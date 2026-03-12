"""
ftne-core/cluster_bootstrap.py
─────────────────────────────────────────────────────────────────────────────
Cluster bootstrap — assigns each machine its FT&E-OS module role and launches
the governor in the appropriate single-module mode.

Hardware map (from archive):
  RTX node 1  → M3 Forgiveness Engine  (high reasoning load)
  RTX node 2  → M6 Stability Monitor   (parallel quality check)
  RTX node 3  → M5 Emergence Generator (synthesis, highest quality)
  RTX node 4  → M7 Attractor Memory    (vector store, context injection)
  Dell CPU 1  → M2 Intake/Parser       (classification, low inference)
  Dell CPU 2  → M4 Time Regulator      (pacing scheduler, no heavy inference)

Single-node fallback (default):
  Set NODE_ROLE=COORDINATOR — all modules run sequentially in one process.

Usage:
  On each machine, set the NODE_ROLE environment variable then run:

    Windows PowerShell:
      $env:NODE_ROLE = "FORGIVENESS"
      python cluster_bootstrap.py

    Linux/macOS:
      NODE_ROLE=FORGIVENESS python cluster_bootstrap.py

  Or use the --role flag:
    python cluster_bootstrap.py --role FORGIVENESS

Networking note (from failure-modes.md FM-06):
  Assign M3, M4, M5 to Ethernet-connected nodes.
  Wi-Fi nodes are acceptable for M7 and M2 where latency tolerance is higher.

Model recommendations per role:
  M3 (FORGIVENESS), M5 (EMERGENCE): 13B+ recommended (Q4_K_M minimum)
  M2 (INTAKE), M4 (TIME_REG):       7B sufficient
  M6 (STABILITY):                   7B–13B acceptable
  M7 (MEMORY):                      embedding model (e.g. nomic-embed-text)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from governor import CarrierState, FTEGovernor, NodeRole  # noqa: E402

# ── Model recommendations per role ──────────────────────────────────────────
ROLE_MODEL_MAP: dict[NodeRole, str] = {
    NodeRole.COORDINATOR: "mistral:7b-instruct-q4_K_M",
    NodeRole.INTAKE:      "mistral:7b-instruct-q4_K_M",   # Dell CPU 1
    NodeRole.TIME_REG:    "mistral:7b-instruct-q4_K_M",   # Dell CPU 2
    NodeRole.FORGIVENESS: "qwen:14b-q4_K_M",              # RTX node 1
    NodeRole.STABILITY:   "mistral:7b-instruct-q4_K_M",   # RTX node 2
    NodeRole.EMERGENCE:   "qwen:14b-q4_K_M",              # RTX node 3
    NodeRole.MEMORY:      "nomic-embed-text",              # RTX node 4
}


def main() -> None:
    parser = argparse.ArgumentParser(description="FT&E Cluster Bootstrap")
    parser.add_argument(
        "--role",
        default=os.environ.get("NODE_ROLE", "COORDINATOR"),
        choices=[r.value for r in NodeRole],
        help="Module role for this node. Overrides NODE_ROLE env var.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Override model for this role. Uses role-default if not set.",
    )
    parser.add_argument(
        "--memory",
        default="ftne_memory.jsonl",
        help="Shared attractor memory path (M7). Point all nodes at the same "
             "network-mounted file or use a shared volume.",
    )
    parser.add_argument(
        "--carrier-state",
        default="GREEN",
        choices=[s.value for s in CarrierState],
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    role  = NodeRole(args.role)
    model = args.model or ROLE_MODEL_MAP.get(role, "mistral:7b-instruct-q4_K_M")

    print(f"{'═'*60}")
    print(f"  FT&E Cluster Node Bootstrap")
    print(f"  Role:   {role.value}")
    print(f"  Model:  {model}")
    print(f"  Memory: {args.memory}")
    print(f"{'═'*60}\n")

    # Ethernet/Wi-Fi advisory (FM-06)
    wifi_safe_roles = {NodeRole.MEMORY, NodeRole.INTAKE}
    ethernet_required_roles = {NodeRole.FORGIVENESS, NodeRole.TIME_REG, NodeRole.EMERGENCE}
    if role in ethernet_required_roles:
        print(
            f"  ⚠  FM-06 advisory: Role {role.value} should be on Ethernet, not Wi-Fi.\n"
            "     Variable latency will desync the time regulator and cause premature\n"
            "     emergence generation. Check your network connection before proceeding.\n"
        )

    gov = FTEGovernor(
        model         = model,
        memory_path   = args.memory,
        carrier_state = CarrierState(args.carrier_state),
        node_role     = role,
        verbose       = args.verbose,
    )

    print(f"  Node online. Role: {role.value}  Model: {model}")
    print(f"  Memory entries loaded: {len(gov.memory.entries)}\n")

    if role == NodeRole.COORDINATOR:
        # Single-node interactive mode
        print("  COORDINATOR mode: running full M1–M7 pipeline on this node.")
        print("  For cluster mode: set NODE_ROLE on each machine and run this script.\n")
        from pathlib import Path as _P
        agent_path = _P(__file__).parent.parent / "open-claw" / "agent.py"
        print(f"  To start the interactive agent, run:\n  python {agent_path}\n")
    else:
        print(
            f"  This node is ready as the {role.value} module.\n"
            "  In Phase 2 (cluster orchestration), the COORDINATOR node will\n"
            "  send tasks to this node via the inter-node message protocol.\n"
            "  (Inter-node messaging not yet implemented — Phase 2 scope.)\n"
        )
        # Self-test: run a single probe to confirm the model is loaded and responsive
        print("  Running self-test probe…")
        test_result = gov.call(
            f"This is a bootstrap self-test for node role {role.value}. "
            "Confirm you are operational and identify your function."
        )
        print(f"  Self-test E*: {test_result.e_star:.3f}")
        print(f"  Self-test attractor: {test_result.new_attractor or '(none — normal for first run)'}\n")
        print("  Node ready.")


if __name__ == "__main__":
    main()
