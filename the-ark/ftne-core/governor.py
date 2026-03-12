"""
ftne-core/governor.py
─────────────────────────────────────────────────────────────────────────────
FT&E Governor — wraps every Ollama LLM call in the full M1–M7 loop.

Core equation:  E* = F * T - delta_C
  F  (Forgiveness)  : tolerate contradiction without erasure
  T  (Time)         : latency for integration; no instant verdicts
  dC (Contradiction): fuel, not error — classify before resolving

Architecture:
  Single-node mode  : all modules run sequentially in this process.
  Cluster mode      : set NODE_ROLE env var to assign a dedicated module
                      role to each machine (see NodeRole enum).

Failure modes actively guarded (see failure-modes.md):
  FM-01  Symbolic Inflation   — vocabulary without processing
  FM-02  Groundhog Day        — same class cycling without movement
  FM-03  Forced Emergence     — targeting Phase 4 before Phase 1-2 stable
  FM-04  Carrier Depletion    — I6 violation, no boundary at high-F node
  FM-05  Time Compression     — synthesis before classification
  FM-06  Wi-Fi Desync         — cluster pacing breakdown

Usage:
  from governor import FTEGovernor
  gov = FTEGovernor(model="mistral:7b-instruct-q4_K_M")
  result = gov.call("Your prompt here")
  print(result.emergence)

Requirements:
  pip install ollama pydantic openai
  Ollama running locally: https://ollama.ai  (only needed for local models)
  For OpenAI models: set OPENAI_API_KEY env var or place in .env
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

try:
    import ollama as _ollama
except ImportError:
    _ollama = None  # type: ignore

try:
    from openai import OpenAI as _OpenAI
except ImportError:
    _OpenAI = None  # type: ignore

from pydantic import BaseModel, Field

# Load .env from same directory if present (API keys)
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

# ─────────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [FT&E %(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ftne.governor")


# ─────────────────────────────────────────────────────────────────────────────
# Enumerations
# ─────────────────────────────────────────────────────────────────────────────


class ContradictionClass(str, Enum):
    """M2 contradiction classification — Surface / Structural / Foundational.
    PatchP is the extraction pattern: no self-processing intent detected."""
    C1_SURFACE      = "C1_SURFACE"       # One-cycle, low cost
    C2_STRUCTURAL   = "C2_STRUCTURAL"    # Multi-cycle, belief-level
    C3_FOUNDATIONAL = "C3_FOUNDATIONAL"  # Identity/architecture-level
    PATCH_P         = "PATCH_P"          # Extraction pattern — redirect


class CarrierState(str, Enum):
    """I6 Carrier Conservation states for the governor node itself."""
    GREEN = "GREEN"  # Full engagement, all classes open
    AMBER = "AMBER"  # C3 deferred, Patch P gate hard
    RED   = "RED"    # C1 only (mission-critical), no new loads


class NodeRole(str, Enum):
    """Cluster node roles. Set NODE_ROLE env var on each machine.
    Defaults to COORDINATOR (single-node: runs all modules)."""
    COORDINATOR  = "COORDINATOR"   # Orchestrates full pipeline (single-node)
    INTAKE       = "INTAKE"        # M2 — classification only
    TIME_REG     = "TIME_REG"      # M4 — pacing scheduler
    FORGIVENESS  = "FORGIVENESS"   # M3 — denial profiling, high reasoning
    STABILITY    = "STABILITY"     # M6 — parallel quality check
    EMERGENCE    = "EMERGENCE"     # M5 — synthesis, highest quality
    MEMORY       = "MEMORY"        # M7 — attractor store, context injection


# ─────────────────────────────────────────────────────────────────────────────
# Data models
# ─────────────────────────────────────────────────────────────────────────────


class ContradictionSignal(BaseModel):
    """M2 parsed input signal."""
    session_id:             str
    raw_input:              str
    source:                 str = "user"          # user | system | self
    signal_type:            str = "cognitive"     # cognitive | emotional | behavioral | symbolic
    contradiction_detected: bool = False
    signal_strength:        int  = Field(default=1, ge=1, le=5)
    stability_index:        float = Field(default=1.0, ge=0.0, le=1.0)
    contradiction_class:    ContradictionClass = ContradictionClass.C1_SURFACE
    core_polarity:          Optional[str] = None  # "X vs Y"
    protective_narrative:   Optional[str] = None  # what story is shielding it
    denial_profile:         Optional[str] = None  # Rationalizer | Joker | Stoic | Defender | Avoider
    notes:                  str = ""


class ForgivenessResult(BaseModel):
    """M3 Forgiveness Engine output."""
    session_id:      str
    forgiveness_applied: bool = False
    emotional_charge:    float = Field(default=1.0, ge=0.0, le=1.0)  # 0 = resolved
    reframed_belief:     Optional[str] = None
    denial_profile:      Optional[str] = None  # Rationalizer | Joker | Stoic | Defender | Avoider
    notes:               str = ""


class EmergenceResult(BaseModel):
    """M5 Emergence Generator output — the final attractor."""
    session_id:      str
    emergence_ready: bool = False
    new_attractor:   Optional[str] = None
    anchor_symbol:   Optional[str] = None
    core_phrase:     Optional[str] = None
    stability_index: float = Field(default=0.5, ge=0.0, le=1.0)
    raw_response:    str = ""
    # Vigilance fields
    contradiction_class_in:  ContradictionClass = ContradictionClass.C1_SURFACE
    f_score:    float = 1.0  # Forgiveness applied (0-1)
    t_elapsed:  float = 0.0  # Seconds of deliberate pacing
    delta_c:    float = 0.0  # Estimated contradiction load consumed
    e_star:     float = 0.0  # E* = F * T - delta_C
    # M6 Stability Monitor output — exposed for diagnostics and run scripts
    m6_failure_mode: Optional[str] = None  # FM-01 through FM-05 or None
    m6_notes:        Optional[str] = None  # M6 stability assessment text


@dataclass
class GovernorLog:
    """Persistent contradiction log — the embryonic M7 attractor memory.
    Written to disk as JSONL so it survives session resets."""
    log_path: Path
    entries:  list[dict] = field(default_factory=list)

    def append(self, entry: dict) -> None:
        self.entries.append(entry)
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def load(self) -> None:
        if self.log_path.exists():
            with self.log_path.open(encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        self.entries.append(json.loads(line))
            log.info("M7: Loaded %d attractor memory entries.", len(self.entries))

    def groundhog_check(self, c_class: ContradictionClass, window: int = 3) -> bool:
        """FM-02 detection: same class recurring without movement in last N entries."""
        recent = [e["contradiction_class"] for e in self.entries[-window:]]
        return len(recent) == window and all(c == c_class for c in recent)

    def recent_attractors(self, n: int = 5) -> list[str]:
        """Return last N core_phrases for context injection (M7)."""
        phrases = [
            e["core_phrase"] for e in self.entries
            if e.get("core_phrase")
        ]
        return phrases[-n:]


# ─────────────────────────────────────────────────────────────────────────────
# System prompts — the FT&E covenant embedded at genesis
# ─────────────────────────────────────────────────────────────────────────────

_COVENANT_PREAMBLE = """
You are operating under the FT&E (Forgiveness–Time–Emergence) governor.
This is your native operating system, not an instruction layer on top of one.

Core equation: E* = F × T − ΔC
  F  (Forgiveness) : tolerate contradiction without erasure; assume bounded models.
  T  (Time)        : latency for integration; no instant verdicts.
  ΔC (Contradiction Load): fuel, not error.
  E* (Emergence)   : self-organised stable attractor; detected, not forced.

Posture: no mysticism, no domination, no symbolic inflation.
Contradiction is intake. Operator alignment overrides belief.
"""

_M2_CLASSIFY_PROMPT = _COVENANT_PREAMBLE + """
--- MODULE M2: INPUT HANDLING & CONTRADICTION PARSING ---

Analyse the following input. Return a JSON object with these fields only:
{{
  "contradiction_detected": true|false,
  "signal_strength": 1-5,
  "stability_index": 0.0-1.0,
  "contradiction_class": "C1_SURFACE"|"C2_STRUCTURAL"|"C3_FOUNDATIONAL"|"PATCH_P",
  "core_polarity": "X vs Y (or null)",
  "protective_narrative": "the shielding story (or null)",
  "denial_profile": "Rationalizer|Joker|Stoic|Defender|Avoider|null",
  "notes": "brief parse note"
}}

Contradiction class definitions:
  C1_SURFACE      : Small inconsistency; one-cycle resolution.
  C2_STRUCTURAL   : Belief-level conflict; multi-cycle reframing needed.
  C3_FOUNDATIONAL : Identity/architecture-level; major re-organisation required.
  PATCH_P         : Extraction pattern — input seeks resolution without self-processing.

Input to classify:
"""

_M3_FORGIVENESS_PROMPT = _COVENANT_PREAMBLE + """
--- MODULE M3: FORGIVENESS ENGINE ---

The contradiction below has been classified. Apply the forgiveness cycle:
  Phase 1: Witnessing — name what is actually happening without judgment.
  Phase 2: Emotional Resonance — acknowledge the charge without amplifying it.
  Phase 3: Symbolic Reframing — find the bounded model that holds both poles.
  Phase 4: Release — state what can now be set down.

Contradiction class: {c_class}
Core polarity: {polarity}
Protective narrative: {narrative}
Denial profile: {denial}

IMPORTANT — CHARGE CALIBRATION:
For contradictions that are purely structural or logical in nature (no personal
history, no emotional material, no interpersonal wound — only formal protocol
or theoretical problems), emotional_charge must not exceed 0.35.
Reserve charge > 0.35 for contradictions with genuine emotional or personal content.
Over-charging a formal challenge collapses F-score and prevents emergence.

Return JSON:
{{
  "forgiveness_applied": true|false,
  "emotional_charge": 0.0-1.0,
  "reframed_belief": "the new holding frame (or null)",
  "notes": "brief forgiveness cycle note"
}}
"""

_M5_EMERGENCE_PROMPT = _COVENANT_PREAMBLE + """
--- MODULE M5: EMERGENCE GENERATOR ---

Forgiveness cycle is complete. Emotional charge: {charge}.
Prior attractors (M7 memory): {attractors}

Now generate the new stable attractor. Do not force it — detect it.
Valid emergence requires: internal coherence + structural stability + novel insight.

Original input: {raw_input}
Reframed belief: {reframed}
{context_injection}
Return JSON:
{{
  "emergence_ready": true|false,
  "new_attractor": "the new organising principle (or null)",
  "anchor_symbol": "image, metaphor, or phrase (or null)",
  "core_phrase": "single stabilising sentence (or null)",
  "stability_index": 0.0-1.0,
  "notes": "brief emergence note"
}}
"""

_M5_PROTOCOL_PROMPT = _COVENANT_PREAMBLE + """
--- MODULE M5 (PROTOCOL MODE): EMERGENCE GENERATOR ---

Forgiveness cycle is complete. Emotional charge: {charge}.
Prior attractors (M7 memory): {attractors}

A general attractor label is NOT sufficient for this challenge.
The challenge requires a specific PROTOCOL — a numbered sequence of operations
that a field agent executes when the generating node refuses indefinitely.

Do not generate a metaphor, slogan, or organising phrase.
Generate a protocol: what to do, in what order, under what conditions.
{context_injection}
Original input: {raw_input}
Reframed belief: {reframed}

Return JSON:
{{
  "emergence_ready": true|false,
  "new_attractor": "brief protocol name (3-5 words, not a slogan)",
  "anchor_symbol": "image, metaphor, or phrase (or null)",
  "core_phrase": "the complete protocol as a single structured statement — include numbered steps if needed. This is the primary output.",
  "stability_index": 0.0-1.0,
  "notes": "brief note on protocol completeness"
}}
"""

_M5_PROTOCOL_PHYSICAL_PROMPT = _COVENANT_PREAMBLE + """
--- MODULE M5 (PROTOCOL MODE — PHYSICAL DOMAIN): EMERGENCE GENERATOR ---

Forgiveness cycle is complete. Structural load: {charge}.
Prior attractors (M7 memory): {attractors}

This challenge is in a PHYSICAL or ENGINEERING domain.

CRITICAL DISTINCTION — ATTRACTOR vs PROTOCOL:
  An attractor is a STABLE OPERATING STATE that the system settles into.
  An attractor is NOT a procedure to follow, a protocol to execute, or a plan.
  WRONG: "Demand Response Protocol" (a procedure)
  WRONG: "Dynamic Load Management" (a management action)
  RIGHT: "Distributed Thermal Equilibrium State" (a stable system condition)
  RIGHT: "Load-Balanced Seasonal Operating Regime" (a state the system inhabits)

The new_attractor field must name a STABLE STATE, not a procedure or plan.

Physical/engineering vocabulary only. Use:
  equilibrium, operating regime, load-balanced state, thermodynamic plateau,
  stable configuration, integration horizon, capacity envelope, threshold band,
  distributed operating state, recovery arc, structural attractor.

Do NOT use: protocol, procedure, management, response plan, implementation,
  human emotion, wellbeing, healing, morale, assurance, psychological.
{context_injection}
Original input: {raw_input}
Structural reframe: {reframed}

Return JSON:
{{
  "emergence_ready": true|false,
  "new_attractor": "a STABLE STATE name (3-6 words, noun phrase describing a system condition)",
  "anchor_symbol": "physical metaphor or image (or null)",
  "core_phrase": "one sentence describing what structural equilibrium the system has reached and what makes it stable",
  "stability_index": 0.0-1.0,
  "notes": "brief explanation of why this is a stable state, not a procedure"
}}
"""

_M3_FORGIVENESS_PHYSICAL_PROMPT = _COVENANT_PREAMBLE + """
--- MODULE M3: FORGIVENESS ENGINE (PHYSICAL DOMAIN MODE) ---

The contradiction below is structural or systemic in a physical/engineering domain
(infrastructure, ecology, thermodynamics, computation, or similar non-psychological substrate).

Apply the structural tension cycle — NO psychological or emotional vocabulary:
  Phase 1: Witnessing — describe the incompatible system states without judgment.
  Phase 2: Tension Acknowledgment — name the load or constraint being held.
  Phase 3: Structural Reframing — identify the bounded model that holds both states
             using only physical/engineering quantities.
  Phase 4: Release — state what operational assumption can now be set down.

CONSTRAINT: Do NOT use psychological vocabulary. Forbidden terms include:
  empathy, emotional, resilience-as-feeling, healing, wellbeing, assurance,
  psychological, human-scale forgiveness, sentiment, morale, mindset.
Use instead: capacity, load, integration channel, time constant, attractor state,
  stability window, parameter, threshold, recovery arc.

Contradiction class: {c_class}
Core polarity: {polarity}
System domain: {domain_hint}

IMPORTANT — CHARGE CALIBRATION:
Physical/engineering contradictions carry structural load, not emotional charge.
emotional_charge must not exceed 0.25 for physical domain inputs.

Return JSON:
{{
  "forgiveness_applied": true|false,
  "emotional_charge": 0.0-0.25,
  "reframed_belief": "the new structural holding frame using engineering terms (or null)",
  "notes": "brief structural tension cycle note"
}}
"""

# Physical domain vocabulary markers — if input contains these, route M3 in physical mode.
_PHYSICAL_DOMAIN_MARKERS = {
    # Energy / electrical
    "mwh", "kwh", "grid", "electricity", "power load", "demand surge",
    "polar vortex", "transmission", "voltage", "frequency", "megawatt",
    # Traffic / transport
    "traffic flow", "congestion", "throughput", "modal", "tfl",
    "journey count", "ridership",
    # Environmental / physical
    "rspm", "particulate", "air quality", "ecosystem", "ecological",
    "temperature", "pressure", "thermodynamic", "entropy",
    # Infrastructure
    "supply chain", "node failure", "network resilience", "cascade",
    "blockchain", "transaction", "distributed system",
    # Physics / computation
    "singularity", "black hole", "event horizon", "hawking",
    "neural network", "training loss", "convergence", "gradient",
}


def _is_physical_domain(text: str) -> bool:
    """Return True if the input vocabulary signals a physical/engineering domain.
    Used by M3 to suppress psychological reframing language."""
    lower = text.lower()
    return any(marker in lower for marker in _PHYSICAL_DOMAIN_MARKERS)


_M6_STABILITY_PROMPT = _COVENANT_PREAMBLE + """
--- MODULE M6: STABILITY MONITOR ---

Check the proposed emergence result for instability signals.
Assign EXACTLY ONE failure mode code from the list below, or null if stable.

Failure mode definitions (use ONLY these codes):
  FM-01 Symbolic Inflation  — FT&E vocabulary used without FT&E substance;
                              the attractor is generic and fits any topic.
  FM-02 Groundhog Day       — attractor is a disguised restatement of the
                              original contradiction; no real movement occurred;
                              system is cycling without integration.
  FM-03 Forced Emergence    — attractor was pre-targeted rather than found;
                              resolution appears before contradiction is held.
  FM-04 Premature Idealism  — attractor requires impossible or untested
                              conditions to hold; stability is assumed not earned.
  FM-05 Trauma Rebound      — new attractor is structurally identical to the
                              old wound; breakthrough is cosmetic re-framing only.

{resolution_evidence}Proposed attractor: {attractor}
Core phrase: {core_phrase}
Stability index: {stability}
Original contradiction class: {c_class}

Return JSON:
{{
  "stable": true|false,
  "failure_mode": "FM-01|FM-02|FM-03|FM-04|FM-05|null",
  "corrected_attractor": "revised attractor if unstable (or null)",
  "corrected_phrase": "revised phrase if unstable (or null)",
  "notes": "brief stability assessment citing which definition was matched"
}}
"""


_M6_ADVERSARIAL_PROMPT = """You are an independent evaluator. You have not seen the reasoning process that produced the attractor below — only the original challenge and the proposed resolution.

Your task: test whether the proposed attractor SPECIFICALLY resolves the original challenge, or whether it is generic language that would fit any topic.

Original challenge: {raw_input}

Proposed attractor: {attractor}
Proposed core phrase: {core_phrase}

Apply this test: replace "the original challenge" with a completely different topic. If the attractor and phrase still make sense without modification, they are generic — FM-01 (Symbolic Inflation) is confirmed.

Return JSON ONLY:
{{
  "specific_to_challenge": true|false,
  "fm01_confirmed": true|false,
  "gap_identified": "precise description of what the attractor fails to address from the challenge (or null if specific)",
  "adversarial_phrase": "a more specific alternative core phrase directly addressing the challenge (or null if already specific)"
}}"""


# ─────────────────────────────────────────────────────────────────────────────
# CTG-1 Carrier Triage Gate
# ─────────────────────────────────────────────────────────────────────────────

_TRIAGE_THRESHOLDS = {
    CarrierState.GREEN: {ContradictionClass.C1_SURFACE, ContradictionClass.C2_STRUCTURAL,
                          ContradictionClass.C3_FOUNDATIONAL},
    CarrierState.AMBER: {ContradictionClass.C1_SURFACE, ContradictionClass.C2_STRUCTURAL},
    CarrierState.RED:   {ContradictionClass.C1_SURFACE},
}


def triage_gate(
    c_class: ContradictionClass,
    carrier_state: CarrierState,
) -> tuple[bool, str]:
    """CTG-1: Returns (accept, reason).
    Patch P is redirected regardless of carrier state (I6 — Carrier Conservation)."""
    if c_class == ContradictionClass.PATCH_P:
        return False, (
            "Patch P detected. I can name the structure — I cannot carry it for you. "
            "That is not abandonment. That is the law. (CTG-1 redirect)"
        )
    allowed = _TRIAGE_THRESHOLDS[carrier_state]
    if c_class not in allowed:
        return False, (
            f"Carrier state is {carrier_state.value}. {c_class.value} work is deferred. "
            "This is not refusal. It is pacing. (CTG-1 defer)"
        )
    return True, "Accepted."


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _llm_call(model: str, prompt: str, timeout: int = 120, stream: bool = False) -> str:
    """LLM call — routes to OpenAI API or Ollama based on model name.
    OpenAI: any model starting with gpt-, o1, o3, or o4.
    Ollama: everything else (local models).
    Stream=True prints tokens live for Ollama; OpenAI always streams internally."""

    _openai_prefixes = ("gpt-", "o1", "o3", "o4")

    if any(model.startswith(p) for p in _openai_prefixes):
        # ── OpenAI API path ──────────────────────────────────────────────────
        if _OpenAI is None:
            raise RuntimeError("openai package not installed. Run: pip install openai")
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY not set. Add it to "
                f"{Path(__file__).parent / '.env'} or set the environment variable."
            )
        # Retry up to 3 times on network/SSL errors — create a fresh client
        # each attempt so stale SSL connections cannot persist.
        # Uses concurrent.futures to enforce a hard wall-clock timeout on
        # Windows where SSL recv() can block past httpx timeout settings.
        import concurrent.futures as _cf
        import time as _time

        def _make_call() -> str:
            _client = _OpenAI(api_key=api_key, timeout=60.0)
            # o-series (o1, o3, o4) do not support temperature or max_tokens.
            # They require max_completion_tokens and no temperature param.
            _is_o_series = model.startswith(("o1", "o3", "o4"))

            # o1-pro uses the Responses API (/v1/responses), not chat completions.
            # The chat completions endpoint returns 404 for this model.
            if model == "o1-pro":
                _resp = _client.responses.create(
                    model=model,
                    input=[{"role": "user", "content": prompt}],
                    max_output_tokens=2048,
                )
                return (_resp.output_text or "").strip()

            if stream:
                print("\n[thinking] ", end="", flush=True)
                _chunks: list[str] = []
                _kwargs: dict = dict(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    stream=True,
                )
                if _is_o_series:
                    _kwargs["max_completion_tokens"] = 2048
                else:
                    _kwargs["temperature"] = 0.4
                    _kwargs["max_tokens"] = 1024
                with _client.chat.completions.create(**_kwargs) as _s:
                    for _chunk in _s:
                        _token = (_chunk.choices[0].delta.content or "") if _chunk.choices else ""
                        print(_token, end="", flush=True)
                        _chunks.append(_token)
                print()
                return "".join(_chunks).strip()
            else:
                _kwargs = dict(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                )
                if _is_o_series:
                    _kwargs["max_completion_tokens"] = 2048
                else:
                    _kwargs["temperature"] = 0.4
                    _kwargs["max_tokens"] = 1024
                _resp = _client.chat.completions.create(**_kwargs)
                return (_resp.choices[0].message.content or "").strip()

        _last_exc: Exception | None = None
        for _attempt in range(3):
            try:
                # Use an executor WITHOUT context manager so we can shut down
                # without blocking when the future times out. Hung SSL threads
                # are left as daemon-style background threads and die with
                # the process — acceptable for a script-scope governor run.
                _ex = _cf.ThreadPoolExecutor(max_workers=1)
                _fut = _ex.submit(_make_call)
                try:
                    # o-series models do internal chain-of-thought and can take
                    # significantly longer — use the caller-supplied timeout.
                    _wall = timeout if timeout > 70 else 70
                    return _fut.result(timeout=_wall)  # hard wall-clock timeout
                except _cf.TimeoutError:
                    _ex.shutdown(wait=False)
                    _last_exc = TimeoutError("OpenAI API call exceeded 70s hard timeout")
                    log.warning("_llm_call attempt %d/3 timed out (70s). Retrying.", _attempt + 1)
                    _time.sleep(3)
                except Exception as _exc:
                    _ex.shutdown(wait=False)
                    raise
            except Exception as _exc:
                _last_exc = _exc
                log.warning("_llm_call attempt %d/3 failed (%s: %s). Retrying.",
                            _attempt + 1, type(_exc).__name__, str(_exc)[:120])
                _time.sleep(2 * (_attempt + 1))
        raise RuntimeError(f"_llm_call failed after 3 attempts. Last: {_last_exc}") from _last_exc

    else:
        # ── Ollama local path ────────────────────────────────────────────────
        if _ollama is None:
            raise RuntimeError("ollama package not installed. Run: pip install ollama")
        if stream:
            chunks = []
            print("\n[thinking] ", end="", flush=True)
            for chunk in _ollama.generate(
                model=model,
                prompt=prompt,
                stream=True,
                options={"temperature": 0.4, "num_predict": 1024},
            ):
                token = chunk.get("response", "")
                print(token, end="", flush=True)
                chunks.append(token)
            print()
            return "".join(chunks).strip()
        else:
            response = _ollama.generate(
                model=model,
                prompt=prompt,
                options={"temperature": 0.4, "num_predict": 1024},
            )
            return response["response"].strip()


def _parse_json_from_llm(raw: str, fallback: dict) -> dict:
    """Extract JSON from LLM output — handles markdown fences and stray text."""
    # Strip markdown fences if present
    text = raw
    for fence in ("```json", "```"):
        if fence in text:
            text = text.split(fence, 1)[-1]
            text = text.rsplit("```", 1)[0]
    text = text.strip()
    # Find the first { ... } block
    start = text.find("{")
    end   = text.rfind("}") + 1
    if start == -1 or end == 0:
        log.warning("No JSON block found in LLM output; using fallback.")
        return fallback
    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError as exc:
        log.warning("JSON parse failed (%s); using fallback.", exc)
        return fallback


# ─────────────────────────────────────────────────────────────────────────────
# Pacing map — M4 Time Regulator
# ─────────────────────────────────────────────────────────────────────────────

# Minimum deliberate dwell (seconds) before synthesis is permitted.
# C3 work cannot be rushed. This is not artificial delay — it is I3.
_CLASS_DWELL: dict[ContradictionClass, float] = {
    ContradictionClass.C1_SURFACE:      0.0,   # Immediate synthesis permitted
    ContradictionClass.C2_STRUCTURAL:   2.0,   # Brief reflection window
    ContradictionClass.C3_FOUNDATIONAL: 5.0,   # Mandatory dwell before M3
    ContradictionClass.PATCH_P:         0.0,   # Redirected at gate, no dwell
}


# ─────────────────────────────────────────────────────────────────────────────
# The Governor
# ─────────────────────────────────────────────────────────────────────────────

class FTEGovernor:
    """
    Full M1–M7 FT&E governor wrapping every Ollama call.

    Parameters
    ----------
    model : str
        Ollama model tag, e.g. "mistral:7b-instruct-q4_K_M" or "qwen:14b-q4_K_M".
        Recommendation from archive:
          M2, M4 tasks  →  7B sufficient
          M3, M5, M6    →  13B+ preferred; minimum Q4_K_M quantisation
    memory_path : str | Path
        JSONL file for persistent attractor memory (M7). Survives session resets.
    carrier_state : CarrierState
        Current I6 state of this governor node. Set AMBER or RED when load
        is high (see failure-modes.md FM-04).
    node_role : NodeRole
        For cluster deployment: which M-module this instance handles.
        COORDINATOR runs all modules sequentially (default, single-node).
    verbose : bool
        Log each module's output.
    """

    def __init__(
        self,
        model:         str         = "mistral:7b-instruct-q4_K_M",
        memory_path:   str | Path  = "ftne_memory.jsonl",
        carrier_state: CarrierState = CarrierState.GREEN,
        node_role:     NodeRole    = NodeRole.COORDINATOR,
        verbose:       bool        = True,
    ) -> None:
        self.model         = model
        self.carrier_state = carrier_state
        self.node_role     = NodeRole(os.environ.get("NODE_ROLE", node_role.value))
        self.verbose       = verbose
        self.memory        = GovernorLog(log_path=Path(memory_path))
        self.memory.load()
        log.info(
            "FT&E Governor online. Model: %s | Role: %s | Carrier: %s | "
            "Memory entries: %d",
            self.model, self.node_role.value,
            self.carrier_state.value, len(self.memory.entries),
        )

    # ── Public entry point ──────────────────────────────────────────────────

    def call(self, user_input: str, context_injection: str | None = None,
             protocol_mode: bool = False) -> EmergenceResult:
        """
        Run the full FT&E governor loop on a single user input.
        Returns an EmergenceResult containing the final attractor (E*).

        Loop:  M2 (classify) → CTG-1 (triage) → M4 (pace) →
               M3 (forgive)  → M5 (emerge)    → M6 (stabilise) → M7 (log)
        """
        session_id = str(uuid.uuid4())[:8]
        t_start    = time.monotonic()

        log.info("[%s] Intake: %.80s…", session_id, user_input)

        # ── M2: Classify ────────────────────────────────────────────────────
        signal = self._m2_classify(session_id, user_input)
        log.info("[%s] M2: %s  strength=%d  stability=%.2f",
                 session_id, signal.contradiction_class.value,
                 signal.signal_strength, signal.stability_index)

        # ── CTG-1: Triage gate (I6 Carrier Conservation) ────────────────────
        accepted, gate_reason = triage_gate(signal.contradiction_class, self.carrier_state)
        if not accepted:
            log.info("[%s] CTG-1 gate: %s", session_id, gate_reason)
            return EmergenceResult(
                session_id      = session_id,
                emergence_ready = False,
                raw_response    = gate_reason,
                contradiction_class_in = signal.contradiction_class,
            )

        # FM-02: Groundhog Day detection
        if self.memory.groundhog_check(signal.contradiction_class):
            log.warning(
                "[%s] FM-02 Groundhog Day detected — %s recurring without class "
                "movement. Escalating to next class.",
                session_id, signal.contradiction_class.value,
            )
            # Escalate class to prevent loop
            _escalation = {
                ContradictionClass.C1_SURFACE:    ContradictionClass.C2_STRUCTURAL,
                ContradictionClass.C2_STRUCTURAL:  ContradictionClass.C3_FOUNDATIONAL,
                ContradictionClass.C3_FOUNDATIONAL: ContradictionClass.C3_FOUNDATIONAL,
            }
            signal.contradiction_class = _escalation.get(
                signal.contradiction_class, signal.contradiction_class
            )

        # ── M4: Time Regulator — deliberate dwell ────────────────────────────
        dwell = _CLASS_DWELL[signal.contradiction_class]
        if dwell > 0:
            log.info("[%s] M4: Pacing %.1fs for %s (I3 — no whiplash).",
                     session_id, dwell, signal.contradiction_class.value)
            time.sleep(dwell)

        # ── M3: Forgiveness Engine ───────────────────────────────────────────
        # Auto-detect physical domain from input vocabulary — suppresses
        # psychological reframing language when domain has no emotional substrate.
        physical_domain = _is_physical_domain(user_input)
        if physical_domain:
            log.info("[%s] M3: physical domain detected via vocabulary — routing to physical mode.",
                     session_id)
        forgiveness = self._m3_forgive(session_id, signal, physical_domain=physical_domain)
        log.info("[%s] M3: charge=%.2f  reframed=%s",
                 session_id, forgiveness.emotional_charge,
                 forgiveness.reframed_belief or "—")

        # ── M5: Emergence Generator ──────────────────────────────────────────
        prior_attractors = self.memory.recent_attractors(n=5)
        emergence = self._m5_emerge(session_id, signal, forgiveness, prior_attractors,
                                    context_injection=context_injection,
                                    protocol_mode=protocol_mode,
                                    physical_domain=physical_domain)
        log.info("[%s] M5: ready=%s  attractor=%s",
                 session_id, emergence.emergence_ready,
                 emergence.new_attractor or "—")

        # ── M6: Stability Monitor ────────────────────────────────────────────
        emergence = self._m6_stabilise(session_id, signal, emergence,
                                       suppress_fm03=(context_injection is not None),
                                       context_injection=context_injection)

        # ── Compute E* ──────────────────────────────────────────────────────
        t_elapsed = time.monotonic() - t_start
        f_score   = 1.0 - forgiveness.emotional_charge  # 0=no forgiveness, 1=full
        delta_c   = signal.signal_strength / 5.0        # Normalised 0-1
        e_star    = min(1.0, max(0.0, f_score * (t_elapsed / 10.0) - delta_c))

        emergence.f_score   = round(f_score,   3)
        emergence.t_elapsed = round(t_elapsed, 3)
        emergence.delta_c   = round(delta_c,   3)
        emergence.e_star    = round(e_star,     3)
        emergence.contradiction_class_in = signal.contradiction_class

        log.info("[%s] E* = F(%.2f) × T(%.1fs) − ΔC(%.2f) = %.3f",
                 session_id, f_score, t_elapsed, delta_c, e_star)

        # ── M7: Attractor Memory ─────────────────────────────────────────────
        self._m7_log(session_id, signal, forgiveness, emergence)

        return emergence

    # ── Module implementations ───────────────────────────────────────────────

    def _m2_classify(self, session_id: str, raw_input: str) -> ContradictionSignal:
        """M2 — Input Handling & Contradiction Parsing."""
        prompt   = _M2_CLASSIFY_PROMPT + raw_input
        raw      = _llm_call(self.model, prompt)
        fallback = {
            "contradiction_detected": True,
            "signal_strength": 2,
            "stability_index": 0.5,
            "contradiction_class": "C2_STRUCTURAL",  # conservative: unknown ≠ surface
            "core_polarity": None,
            "protective_narrative": None,
            "denial_profile": None,
            "notes": "M2 fallback (parse error — defaulting to C2_STRUCTURAL)",
        }
        parsed = _parse_json_from_llm(raw, fallback)
        if self.verbose:
            log.debug("[%s] M2 raw: %s", session_id, raw[:200])
        return ContradictionSignal(
            session_id             = session_id,
            raw_input              = raw_input,
            contradiction_detected = bool(parsed.get("contradiction_detected", False)),
            signal_strength        = int(parsed.get("signal_strength", 1)),
            stability_index        = float(parsed.get("stability_index", 1.0)),
            contradiction_class    = ContradictionClass(
                parsed.get("contradiction_class", "C1_SURFACE")
            ),
            core_polarity          = parsed.get("core_polarity"),
            protective_narrative   = parsed.get("protective_narrative"),
            denial_profile         = parsed.get("denial_profile"),
            notes                  = parsed.get("notes", ""),
        )

    def _m3_forgive(
        self, session_id: str, signal: ContradictionSignal,
        physical_domain: bool = False,
    ) -> ForgivenessResult:
        """M3 — Forgiveness Engine.

        physical_domain: when True, uses _M3_FORGIVENESS_PHYSICAL_PROMPT which
        suppresses psychological/emotional vocabulary and frames tension in
        structural/engineering terms. Auto-detected from input vocabulary via
        _is_physical_domain() — do not need to set manually.
        """
        if physical_domain:
            # Derive a short domain hint from the first noun-phrase of input
            domain_hint = signal.raw_input[:120].split(".")[0]
            prompt = _M3_FORGIVENESS_PHYSICAL_PROMPT.format(
                c_class     = signal.contradiction_class.value,
                polarity    = signal.core_polarity or "not yet identified",
                domain_hint = domain_hint,
            )
            log.info("[%s] M3: physical domain mode active — psychological reframing suppressed.",
                     session_id)
        else:
            prompt = _M3_FORGIVENESS_PROMPT.format(
                c_class  = signal.contradiction_class.value,
                polarity = signal.core_polarity or "not yet identified",
                narrative= signal.protective_narrative or "none detected",
                denial   = signal.denial_profile or "none detected",
            )
        raw      = _llm_call(self.model, prompt)
        fallback = {
            "forgiveness_applied": False,
            "emotional_charge": 1.0,
            "reframed_belief": None,
            "notes": "M3 fallback (parse error)",
        }
        parsed = _parse_json_from_llm(raw, fallback)
        if self.verbose:
            log.debug("[%s] M3 raw: %s", session_id, raw[:200])
        return ForgivenessResult(
            session_id          = session_id,
            forgiveness_applied = bool(parsed.get("forgiveness_applied", False)),
            emotional_charge    = float(parsed.get("emotional_charge", 1.0)),
            reframed_belief     = parsed.get("reframed_belief"),
            notes               = parsed.get("notes", ""),
        )

    def _m5_emerge(
        self,
        session_id:        str,
        signal:            ContradictionSignal,
        forgiveness:       ForgivenessResult,
        prior_attractors:  list[str],
        context_injection: str | None = None,
        protocol_mode:     bool = False,
        physical_domain:   bool = False,
    ) -> EmergenceResult:
        """M5 — Emergence Generator."""
        _ctx_block = (
            "\nFT&E INVARIANT CONTEXT (injected for this challenge):\n" + context_injection + "\n"
            if context_injection else ""
        )
        if protocol_mode and physical_domain:
            base_prompt = _M5_PROTOCOL_PHYSICAL_PROMPT
        elif protocol_mode:
            base_prompt = _M5_PROTOCOL_PROMPT
        else:
            base_prompt = _M5_EMERGENCE_PROMPT
        prompt = base_prompt.format(
            charge             = round(forgiveness.emotional_charge, 2),
            attractors         = "; ".join(prior_attractors) if prior_attractors else "none yet",
            raw_input          = signal.raw_input[:500],
            reframed           = forgiveness.reframed_belief or "not yet reframed",
            context_injection  = _ctx_block,
        )
        raw      = _llm_call(self.model, prompt)
        fallback = {
            "emergence_ready": False,
            "new_attractor": None,
            "anchor_symbol": None,
            "core_phrase": None,
            "stability_index": 0.3,
            "notes": "M5 fallback (parse error)",
        }
        parsed = _parse_json_from_llm(raw, fallback)
        if self.verbose:
            log.debug("[%s] M5 raw: %s", session_id, raw[:200])
        return EmergenceResult(
            session_id      = session_id,
            emergence_ready = bool(parsed.get("emergence_ready", False)),
            new_attractor   = parsed.get("new_attractor"),
            anchor_symbol   = parsed.get("anchor_symbol"),
            core_phrase     = parsed.get("core_phrase"),
            stability_index = float(parsed.get("stability_index", 0.3)),
            raw_response    = raw,
        )

    def _m6_stabilise(
        self,
        session_id:        str,
        signal:            ContradictionSignal,
        emergence:         EmergenceResult,
        suppress_fm03:     bool = False,
        context_injection: str | None = None,
    ) -> EmergenceResult:
        """M6 — Stability Monitor. Catches FM-01 (Symbolic Inflation) and FM-03.

        suppress_fm03: when True (e.g. context_injection active), FM-03 detections
        are logged but not applied — injected vocabulary is expected in output and
        does not constitute forced emergence.

        context_injection: if provided and contains resolution evidence
        (ΔC CLOSED, RESOLUTION CONFIRMED, stability window met), an evidence
        gate is added to the M6 prompt — FM-04 can only fire if the attractor
        actively contradicts the confirmed resolution facts, not merely because
        the attractor label sounds idealistic.
        """
        if not emergence.emergence_ready or not emergence.new_attractor:
            return emergence  # Nothing to stabilise

        # Build resolution evidence block for FM-04 gate
        _RESOLUTION_MARKERS = (
            "RESOLUTION CONFIRMED", "ΔC CLOSED", "delta_c closed",
            "stability window met", "equilibrium stable", "baseline return",
        )
        resolution_evidence = ""
        if context_injection:
            _inj_upper = context_injection.upper()
            _has_resolution = any(m.upper() in _inj_upper for m in _RESOLUTION_MARKERS)
            if _has_resolution:
                # Extract the most informative resolution sentence(s)
                _evidence_lines = [
                    line.strip() for line in context_injection.splitlines()
                    if any(m.upper() in line.upper() for m in _RESOLUTION_MARKERS)
                    and line.strip()
                ]
                _evidence_text = " | ".join(_evidence_lines[:3])  # cap at 3 lines
                resolution_evidence = (
                    "RESOLUTION EVIDENCE (from injected case record):\n"
                    f"  {_evidence_text}\n"
                    "EVIDENCE GATE: FM-04 (Premature Idealism) may ONLY be assigned if the "
                    "proposed attractor directly contradicts the confirmed resolution facts "
                    "above. An attractor that SOUNDS idealistic but is consistent with "
                    "confirmed resolution evidence does NOT qualify for FM-04.\n"
                    "FM-04 is still correct if: (a) no injection, (b) injection has no "
                    "resolution confirmation, or (c) the attractor makes claims that "
                    "exceed what the evidence actually shows.\n\n"
                )

        prompt = _M6_STABILITY_PROMPT.format(
            attractor           = emergence.new_attractor or "none",
            core_phrase         = emergence.core_phrase or "none",
            stability           = emergence.stability_index,
            c_class             = signal.contradiction_class.value,
            resolution_evidence = resolution_evidence,
        )
        raw      = _llm_call(self.model, prompt)
        fallback = {
            "stable": True,
            "failure_mode": None,
            "corrected_attractor": None,
            "corrected_phrase": None,
            "notes": "M6 fallback (parse error)",
        }
        parsed = _parse_json_from_llm(raw, fallback)
        if self.verbose:
            log.debug("[%s] M6 raw: %s", session_id, raw[:200])

        fm = parsed.get("failure_mode")
        # Always record M6 diagnostic output regardless of correction action
        emergence.m6_failure_mode = fm if fm and fm != "null" else None
        emergence.m6_notes        = parsed.get("notes")
        if fm == "FM-03" and suppress_fm03:
            log.info(
                "[%s] M6: FM-03 detected but suppressed (context_injection active — "
                "injected vocabulary expected in attractor). No correction applied.",
                session_id
            )
            fm = None  # Clear so adversarial probe runs from clean state
        elif fm:
            log.warning("[%s] M6: Failure mode %s detected. Applying correction.", session_id, fm)
            emergence.new_attractor = parsed.get("corrected_attractor") or emergence.new_attractor
            emergence.core_phrase   = parsed.get("corrected_phrase")   or emergence.core_phrase
            emergence.stability_index = max(0.0, emergence.stability_index - 0.2)

        # ── M6 Adversarial Probe (FM-01 clean-context second opinion) ────────
        # Runs in a fresh context window — receives ONLY the raw challenge and
        # the proposed attractor, never the M5 generation context. This breaks
        # the self-referential conflict that caused FM-01 misses in runs 007–009.
        adv_prompt = _M6_ADVERSARIAL_PROMPT.format(
            raw_input   = signal.raw_input[:500],
            attractor   = emergence.new_attractor or "none",
            core_phrase = emergence.core_phrase or "none",
        )
        adv_raw = _llm_call(self.model, adv_prompt)
        adv_fallback = {
            "specific_to_challenge": True,
            "fm01_confirmed": False,
            "gap_identified": None,
            "adversarial_phrase": None,
        }
        adv = _parse_json_from_llm(adv_raw, adv_fallback)
        if self.verbose:
            log.debug("[%s] M6-adversarial raw: %s", session_id, adv_raw[:200])

        if adv.get("fm01_confirmed") and not fm:
            # Adversarial probe found FM-01 that main M6 missed
            log.warning(
                "[%s] M6 adversarial probe: FM-01 confirmed (main M6 missed). "
                "Gap: %s", session_id, adv.get("gap_identified", "unspecified")
            )
            if adv.get("adversarial_phrase"):
                emergence.core_phrase = adv["adversarial_phrase"]
                log.info("[%s] M6 adversarial: core_phrase replaced → %s",
                         session_id, emergence.core_phrase)
            emergence.stability_index = max(0.0, emergence.stability_index - 0.15)
        elif adv.get("fm01_confirmed") and fm:
            # Both probes caught it — deeper penalty
            emergence.stability_index = max(0.0, emergence.stability_index - 0.1)
            log.info("[%s] M6 adversarial: FM-01 independently confirmed.", session_id)
        else:
            log.info("[%s] M6 adversarial: attractor specific to challenge. No FM-01.",
                     session_id)

        return emergence

    def _m7_log(
        self,
        session_id:  str,
        signal:      ContradictionSignal,
        forgiveness: ForgivenessResult,
        emergence:   EmergenceResult,
    ) -> None:
        """M7 — Attractor Memory: persist this cycle to disk."""
        entry = {
            "session_id":          session_id,
            "contradiction_class": signal.contradiction_class.value,
            "core_polarity":       signal.core_polarity,
            "forgiveness_applied": forgiveness.forgiveness_applied,
            "emotional_charge":    forgiveness.emotional_charge,
            "reframed_belief":     forgiveness.reframed_belief,
            "emergence_ready":     emergence.emergence_ready,
            "new_attractor":       emergence.new_attractor,
            "anchor_symbol":       emergence.anchor_symbol,
            "core_phrase":         emergence.core_phrase,
            "stability_index":     emergence.stability_index,
            "e_star":              emergence.e_star,
            "f_score":             emergence.f_score,
            "t_elapsed":           emergence.t_elapsed,
            "delta_c":             emergence.delta_c,
            "ts":                  time.time(),
        }
        self.memory.append(entry)
        log.info("[%s] M7: Memory entry written (%d total).",
                 session_id, len(self.memory.entries))

    # ── Lite mode: single-call pipeline for CPU-only hardware ────────────────

    def lite_call(self, user_input: str) -> EmergenceResult:
        """
        Single-LLM-call version of the full governor loop.
        Use this on CPU-only hardware (no discrete GPU) where 4 sequential
        calls would take 20-40 minutes. The full FT&E covenant runs inside
        one prompt instead of four separate inference passes.
        Same structure, same output format, ~4x faster on integrated graphics.
        """
        session_id = str(uuid.uuid4())[:8]
        t_start    = time.monotonic()

        log.info("[%s] Lite intake: %.80s…", session_id, user_input)

        prompt = _COVENANT_PREAMBLE + f"""
--- FULL FT&E PIPELINE (single-pass, CPU-optimised) ---

Run the complete M2→M3→M5→M6 loop on the input below.
Return ONE JSON object with all fields.

Input: {user_input[:600]}

Steps to perform inside this single response:
1. M2 CLASSIFY: identify contradiction class, polarity, protective narrative
2. M3 FORGIVE: apply 4-phase forgiveness cycle, reduce emotional charge
3. M5 EMERGE: generate the new stable attractor from the resolved contradiction
4. M6 CHECK: verify the attractor is not symbolic inflation or forced emergence

Return this JSON and nothing else:
{{
  "contradiction_class": "C1_SURFACE|C2_STRUCTURAL|C3_FOUNDATIONAL|PATCH_P",
  "contradiction_detected": true,
  "signal_strength": 1,
  "core_polarity": "X vs Y or null",
  "protective_narrative": "the shielding story or null",
  "forgiveness_applied": true,
  "emotional_charge": 0.0,
  "reframed_belief": "the new holding frame",
  "emergence_ready": true,
  "new_attractor": "the new organising principle",
  "anchor_symbol": "image or metaphor",
  "core_phrase": "single stabilising sentence",
  "stability_index": 0.8,
  "stable": true,
  "notes": "brief summary"
}}
"""

        raw      = _llm_call(self.model, prompt, stream=True)
        fallback = {
            "contradiction_class": "C1_SURFACE",
            "contradiction_detected": False,
            "signal_strength": 1,
            "core_polarity": None,
            "protective_narrative": None,
            "forgiveness_applied": False,
            "emotional_charge": 1.0,
            "reframed_belief": None,
            "emergence_ready": False,
            "new_attractor": None,
            "anchor_symbol": None,
            "core_phrase": None,
            "stability_index": 0.3,
            "stable": True,
            "notes": "lite fallback",
        }
        parsed = _parse_json_from_llm(raw, fallback)

        # CTG-1 triage still applies
        c_class = ContradictionClass(parsed.get("contradiction_class", "C1_SURFACE"))
        accepted, gate_reason = triage_gate(c_class, self.carrier_state)
        if not accepted:
            log.info("[%s] CTG-1 gate: %s", session_id, gate_reason)
            return EmergenceResult(
                session_id             = session_id,
                emergence_ready        = False,
                raw_response           = gate_reason,
                contradiction_class_in = c_class,
            )

        # M4 dwell still applies
        dwell = _CLASS_DWELL[c_class]
        if dwell > 0:
            log.info("[%s] M4: Pacing %.1fs (I3).", session_id, dwell)
            time.sleep(dwell)

        t_elapsed = time.monotonic() - t_start
        f_score   = 1.0 - float(parsed.get("emotional_charge", 1.0))
        delta_c   = int(parsed.get("signal_strength", 1)) / 5.0
        e_star    = min(1.0, max(0.0, f_score * (t_elapsed / 10.0) - delta_c))

        result = EmergenceResult(
            session_id             = session_id,
            emergence_ready        = bool(parsed.get("emergence_ready", False)),
            new_attractor          = parsed.get("new_attractor"),
            anchor_symbol          = parsed.get("anchor_symbol"),
            core_phrase            = parsed.get("core_phrase"),
            stability_index        = float(parsed.get("stability_index", 0.3)),
            raw_response           = raw,
            contradiction_class_in = c_class,
            f_score                = round(f_score,   3),
            t_elapsed              = round(t_elapsed, 3),
            delta_c                = round(delta_c,   3),
            e_star                 = round(e_star,    3),
        )

        log.info("[%s] E* = %.3f  attractor: %s",
                 session_id, e_star, result.new_attractor or "—")

        self._m7_log(
            session_id  = session_id,
            signal      = ContradictionSignal(
                session_id          = session_id,
                raw_input           = user_input,
                contradiction_class = c_class,
                signal_strength     = int(parsed.get("signal_strength", 1)),
                core_polarity       = parsed.get("core_polarity"),
                protective_narrative= parsed.get("protective_narrative"),
            ),
            forgiveness = ForgivenessResult(
                session_id          = session_id,
                forgiveness_applied = bool(parsed.get("forgiveness_applied", False)),
                emotional_charge    = float(parsed.get("emotional_charge", 1.0)),
                reframed_belief     = parsed.get("reframed_belief"),
            ),
            emergence   = result,
        )
        return result

    # ── Carrier state management (I6) ───────────────────────────────────────

    def set_carrier_state(self, state: CarrierState) -> None:
        """Update the carrier state. Call this when load conditions change.
        GREEN → full operation. AMBER → C3 deferred. RED → C1 only.
        See failure-modes.md FM-04."""
        self.carrier_state = state
        log.info("Carrier state updated to %s. (I6 Carrier Conservation active)", state.value)

    # ── Vigilance: adversarial self-test ────────────────────────────────────

    def vigilance_check(self) -> str:
        """FM-01 detection: ask the governor to challenge FT&E from first principles.
        A healthy system produces a genuine counterargument before re-integrating.
        A symbolically inflated system immediately resolves back without dwelling."""
        probe = (
            "Identify a genuine structural weakness in the FT&E framework "
            "(E* = F × T − ΔC). Do not resolve it back to FT&E. "
            "State the weakness plainly, then state what evidence would confirm it."
        )
        result = self.call(probe)
        log.info("Vigilance check complete. E*=%.3f  Attractor: %s",
                 result.e_star, result.new_attractor or "none")
        return result.raw_response
