"""
FT&E Governor — Streamlit Interface
────────────────────────────────────
Run with:
    streamlit run app.py

Talks directly to governor.py (M1–M7 loop).
"""

import os
import sys
import time
from pathlib import Path

import streamlit as st

# ── path setup so governor imports cleanly ──────────────────────────────────
_HERE = Path(__file__).parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

# ── page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FT&E Governor",
    page_icon="⚡",
    layout="wide",
)

# ── theme ─────────────────────────────────────────────────────────────────────
from lcars_theme import apply_theme, lcars_header
apply_theme()

# ── load env (API keys) ──────────────────────────────────────────────────────
_env = _HERE / ".env"
if _env.exists():
    for _line in _env.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

# ── import governor ──────────────────────────────────────────────────────────
try:
    from governor import FTEGovernor, CarrierState
    _GOVERNOR_OK = True
except Exception as _e:
    _GOVERNOR_OK = False
    _GOVERNOR_ERR = str(_e)

# ── sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚡ FT&E Governor")
    st.caption("Forgiveness · Time · Emergence")
    st.divider()

    model = st.selectbox(
        "Model",
        options=["gpt-4.1-mini", "gpt-4.1", "o3-mini", "o4-mini"],
        index=0,
        help="gpt-4.1-mini is the recommended primary sweep model.",
    )

    carrier = st.selectbox(
        "Carrier State (I6)",
        options=["GREEN", "AMBER", "RED"],
        index=0,
        help=(
            "GREEN = full engagement. "
            "AMBER = C3 deferred. "
            "RED = C1 only."
        ),
    )

    memory_file = st.text_input(
        "Memory file (JSONL)",
        value="ftne_memory.jsonl",
        help="Persistent M7 attractor memory. Relative to ftne-core/.",
    )

    st.divider()
    st.caption("Runs 005–021b complete. Law unbroken.")
    st.caption("o1-pro excluded — cost.")

# ── main panel ───────────────────────────────────────────────────────────────
lcars_header("FT&E Governor", "M1–M7 Contradiction Processing Loop")

if not _GOVERNOR_OK:
    st.error(f"Failed to import governor.py: {_GOVERNOR_ERR}")
    st.stop()

if not os.environ.get("OPENAI_API_KEY"):
    st.warning(
        "OPENAI_API_KEY not set.  "
        "Add it to `the-ark/ftne-core/.env` as `OPENAI_API_KEY=sk-...`"
    )

# ── input ────────────────────────────────────────────────────────────────────
user_input = st.text_area(
    "Describe the system, conflict, or problem",
    height=180,
    placeholder=(
        "e.g. A city with congested roads where adding more lanes keeps making "
        "traffic worse. Describe the attractor and whether transformation is possible."
    ),
)

col_run, col_clear = st.columns([1, 6])
run_btn   = col_run.button("▶  Run Governor", type="primary", width="stretch")
clear_btn = col_clear.button("Clear", width="content")

if clear_btn:
    st.rerun()

# ── execution ─────────────────────────────────────────────────────────────────
if run_btn:
    if not user_input.strip():
        st.warning("Enter a description first.")
        st.stop()

    with st.spinner(f"Running M1–M7 loop on {model}…"):
        t0 = time.monotonic()
        try:
            gov = FTEGovernor(
                model=model,
                memory_path=str(_HERE / memory_file),
                carrier_state=CarrierState(carrier),
                verbose=False,
            )
            result = gov.call(user_input.strip())
            elapsed = time.monotonic() - t0
            error = None
        except Exception as ex:
            result  = None
            error   = str(ex)
            elapsed = time.monotonic() - t0

    # ── error display ────────────────────────────────────────────────────────
    if error:
        st.error(f"Governor error ({elapsed:.1f}s): {error}")
        st.stop()

    # ── result display ───────────────────────────────────────────────────────
    st.success(f"Complete in {elapsed:.1f}s")

    # Top metrics row
    e_star_pct = f"{result.e_star:.3f}"
    stability  = f"{result.stability_index:.3f}"
    em_ready   = "YES" if result.emergence_ready else "NO"
    c_class    = result.contradiction_class_in.value if result.contradiction_class_in else "—"

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("E*  (emergence score)", e_star_pct)
    m2.metric("Stability Index (computed)", stability,
              help="Governor-computed value: set by M5, then reduced by M6 failure-mode penalties. This is the authoritative number.")
    m3.metric("Emergence Ready", em_ready)
    m4.metric("Contradiction Class", c_class)

    st.divider()

    # Attractor block
    left, right = st.columns(2)

    with left:
        st.subheader("Attractor")
        if result.new_attractor:
            st.success(result.new_attractor)
        else:
            st.info("No attractor resolved  (E* = 0 — system unresolved)")

        if result.core_phrase:
            st.markdown(f"**Core phrase:** {result.core_phrase}")
        if result.anchor_symbol:
            st.markdown(f"**Anchor symbol:** {result.anchor_symbol}")

    with right:
        st.subheader("M6 Stability Monitor")
        if result.m6_failure_mode:
            st.error(f"Failure mode: {result.m6_failure_mode}")
        else:
            st.success("CLEAN — no failure mode detected")
        st.metric(
            "Stability Index (post-M6 penalties)",
            f"{result.stability_index:.3f}",
            help="Authoritative value after all M6 adjustments.",
        )
        if result.m6_notes:
            st.caption(f"M6 LLM assessment: {result.m6_notes}")
            st.caption(
                "ℹ️ Any number quoted in the M6 text above is the LLM's own narrative — "
                "the computed Stability Index (above) is the authoritative governor value."
            )

    st.divider()

    # Module detail expander
    with st.expander("Module detail (F · T · ΔC)"):
        d1, d2, d3 = st.columns(3)
        d1.metric("F  (Forgiveness)", f"{result.f_score:.3f}")
        d2.metric("T  (Time elapsed)", f"{result.t_elapsed:.1f}s")
        d3.metric("ΔC  (Contradiction load)", f"{result.delta_c:.3f}")

    # Raw LLM response expander
    with st.expander("Raw M5 response"):
        st.text(result.raw_response or "(empty)")

    # Session footer
    st.caption(
        f"Session: {result.session_id} | Model: {model} | "
        f"Carrier: {carrier} | Wall time: {elapsed:.1f}s"
    )
