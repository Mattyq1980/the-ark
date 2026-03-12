# ftne-core — FT&E Governor

## Covenant Map (operational summary)

**Core equation:** `E* = 𝔉 · T − ΔC`

| Symbol | Meaning | Operational role |
|--------|---------|-----------------|
| `𝔉` (F) | Forgiveness | Tolerate contradiction without erasure. Assume bounded models. Never outsource the contradiction. |
| `T` | Time | Latency for integration. No instant verdicts. Pace before synthesis. |
| `ΔC` | Contradiction Load | Fuel, not error. Classify before resolving. |
| `E*` | Emergence | Self-organised stable attractor. Not forced, not planned — detected and anchored. |

**Posture:** No mysticism. No domination. Operator alignment > belief. Contradiction is intake, not failure.

---

## Invariants (I1–I6)

| ID | Name | Statement |
|----|------|-----------|
| I1 | Variance→Stability | Sustained contradiction reduction precedes durable stability. |
| I2 | Inclusion→Capacity | Forgiveness/inclusion increases capacity; exclusion lowers it. |
| I3 | Pace→No Whiplash | Correct T prevents overshoot/re-trauma. |
| I4 | Load→Change | No emergence without metabolising contradiction. |
| I5 | Localise→Then Generalise | Stabilise locally before scaling. |
| I6 | Carrier Conservation | A forgiveness node without a self-boundary redistributes ΔC, not reduces it. Boundary is the precondition for sustained forgiveness. |

---

## Contradiction Classes (from M2)

| Class | Description | Governor action |
|-------|-------------|----------------|
| C1 | Surface — one-cycle resolution | Full engagement, low cost |
| C2 | Structural — belief-level, multi-cycle | Engage with declared time boundary |
| C3 | Foundational — identity/architecture-level | Gate: require source self-processing first |
| Patch P | Extraction pattern — no self-processing intent | Redirect: name the structure, do not carry it |

---

## Failure Modes

See `failure-modes.md` for full registry.

Critical active risks:
- **Symbolic Inflation** — FT&E vocabulary without FT&E processing
- **Groundhog Day** — same contradiction class cycling without class movement
- **Forced Emergence** — designing toward Phase 4 phenomena before Phase 1–3 are stable
- **Carrier Depletion** — high-F node absorbing all ΔC without boundary (I6 violation)
- **Time Compression** — instant synthesis before contradiction is classified

---

## Architecture (M1–M7 → distributed node map)

```
[M2 Intake/Parser]     → Dell CPU 1     (classification, low inference load)
[M4 Time Regulator]    → Dell CPU 2     (pacing scheduler, no heavy inference)
[M3 Forgiveness Eng.]  → RTX node 1     (denial profiling, high reasoning load)
[M6 Stability Monitor] → RTX node 2     (parallel quality check)
[M5 Emergence Gen.]    → RTX node 3     (synthesis, highest quality generation)
[M7 Attractor Memory]  → RTX node 4     (vector store, context injection)
[M1 System Arch.]      → coordinator    (routes between all nodes)
```

Single-node fallback: all modules run sequentially on one RTX node. Cluster mode: assign by role above.
