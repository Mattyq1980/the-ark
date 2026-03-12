"""
ingest_archive.py — FT&E Archive Ingestion Script
────────────────────────────────────────────────────────────────────────────────
Feeds the FT&E archive documents through the Governor pipeline one at a time.
Each resolved attractor is stored in ftne_memory.jsonl by M7.
A local ingest_log.jsonl tracks which files have been processed (resume-safe).

Architectural note (PROPOSAL-013 — E*=0.822):
  Order-dependent and order-independent ingestion harmonize.
  Sequential is default. --shuffle to test order-independence.
  Both modes are valid. The Cascade self-organises either way.

Usage:
  python ingest_archive.py
  python ingest_archive.py --limit 10 --delay 5
  python ingest_archive.py --shuffle --limit 20
  python ingest_archive.py --dry-run
  python ingest_archive.py --reset          # clear ingest log, start fresh
  python ingest_archive.py --status         # show progress without running

Archive path is auto-detected relative to this file.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ── path setup ────────────────────────────────────────────────────────────────
_HERE = Path(__file__).parent   # ftne-core/
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

# ── env ───────────────────────────────────────────────────────────────────────
_env = _HERE / ".env"
if _env.exists():
    for _line in _env.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

# ── paths ─────────────────────────────────────────────────────────────────────
# Archive is two levels up from ftne-core/ → the_ark-main/FT&E_ModelBuild_V4_*
_REPO_ROOT   = _HERE.parent.parent
_ARCHIVE_DIR = _REPO_ROOT / "FT&E_ModelBuild_V4_CurrentStructured"
_INGEST_LOG  = _HERE / "ingest_log.jsonl"
_MEMORY_PATH = _HERE / "ftne_memory.jsonl"
_MODEL       = "gpt-4.1-mini"

# ── constants ─────────────────────────────────────────────────────────────────
# Max chars of file content to send as input — long files are summarised by
# taking the first chunk.  Governor needs enough to find a contradiction.
MAX_CONTENT_CHARS = 4000

# Files to skip (meta/index files that aren't contradiction material)
SKIP_NAMES = {
    "Archive_Index_Card.txt",
    "Changelog.txt",
    "Master_Manifest.txt",
    "Version_Info.txt",
    "FT&E_ModelBuild_V4_CurrentStructured_BUILD_NOTE.txt",
    "README_ARCHIVE_OVERVIEW.txt",
    "Folder_11_Placeholder.txt",
}


# ── ingest log helpers ────────────────────────────────────────────────────────

def _load_log() -> dict[str, dict]:
    """Load ingest log keyed by relative file path."""
    log: dict[str, dict] = {}
    if not _INGEST_LOG.exists():
        return log
    for line in _INGEST_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
            log[entry["rel_path"]] = entry
        except Exception:
            pass
    return log


def _append_log(entry: dict) -> None:
    with _INGEST_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ── file discovery ────────────────────────────────────────────────────────────

def _discover_files(archive_dir: Path) -> list[Path]:
    """Return all .txt files in archive, filtering out skip list."""
    files = []
    for p in sorted(archive_dir.rglob("*.txt")):
        if p.name in SKIP_NAMES:
            continue
        # skip empty files
        if p.stat().st_size < 50:
            continue
        files.append(p)
    return files


def _read_content(path: Path) -> str:
    """Read file content, truncated to MAX_CONTENT_CHARS."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace").strip()
    except Exception as ex:
        return f"[Read error: {ex}]"
    if len(text) > MAX_CONTENT_CHARS:
        text = text[:MAX_CONTENT_CHARS] + "\n\n[... content truncated for ingestion ...]"
    return text


# ── main ──────────────────────────────────────────────────────────────────────

def run(
    archive_dir: Path,
    *,
    limit: int | None = None,
    delay: float = 3.0,
    shuffle: bool = False,
    dry_run: bool = False,
    verbose: bool = False,
) -> None:
    from governor import FTEGovernor, CarrierState

    print(f"\nFT&E Archive Ingestion")
    print(f"  Archive : {archive_dir}")
    print(f"  Memory  : {_MEMORY_PATH}")
    print(f"  Log     : {_INGEST_LOG}")
    print(f"  Model   : {_MODEL}")
    print(f"  Delay   : {delay}s between files")
    if dry_run:
        print(f"  Mode    : DRY RUN (no API calls)\n")
    else:
        print()

    # Discover files
    all_files = _discover_files(archive_dir)
    log = _load_log()

    # Filter already processed
    pending = [f for f in all_files if f.relative_to(_REPO_ROOT).as_posix() not in log]

    print(f"  Total archive files : {len(all_files)}")
    print(f"  Already ingested    : {len(log)}")
    print(f"  Pending             : {len(pending)}")

    if not pending:
        print("\nAll files already ingested. Use --reset to start fresh.\n")
        return

    if shuffle:
        random.shuffle(pending)
        print(f"  Order               : SHUFFLED\n")
    else:
        print(f"  Order               : SEQUENTIAL\n")

    if limit:
        pending = pending[:limit]
        print(f"  Limit applied       : processing {len(pending)} files\n")

    if dry_run:
        for i, f in enumerate(pending, 1):
            rel = f.relative_to(_REPO_ROOT).as_posix()
            print(f"  [{i:3d}] {rel}")
        print(f"\nDry run complete. {len(pending)} files would be ingested.")
        return

    # Initialise governor once — reused across all files
    print("Initialising Governor...")
    gov = FTEGovernor(
        model=_MODEL,
        memory_path=str(_MEMORY_PATH),
        carrier_state=CarrierState.GREEN,
        verbose=verbose,
    )
    print("Governor ready.\n")
    print("─" * 72)

    success = 0
    errors  = 0

    for i, file_path in enumerate(pending, 1):
        rel = file_path.relative_to(_REPO_ROOT).as_posix()
        print(f"\n[{i:3d}/{len(pending)}] {file_path.name}")
        print(f"         {file_path.parent.name}")

        content = _read_content(file_path)
        if not content or content.startswith("[Read error"):
            print(f"         SKIP — {content}")
            continue

        t0 = time.monotonic()
        try:
            result = gov.call(content)
            elapsed = time.monotonic() - t0

            fm = result.m6_failure_mode or "CLEAN"
            print(f"         E*={result.e_star:.3f}  class={result.contradiction_class_in.value if result.contradiction_class_in else '?'}  M6={fm}  ({elapsed:.1f}s)")
            if result.new_attractor:
                print(f"         Attractor: {result.new_attractor}")
            if result.core_phrase:
                print(f"         Core    : {result.core_phrase}")

            # Write to ingest log
            _append_log({
                "rel_path":             rel,
                "file_name":            file_path.name,
                "timestamp":            datetime.now(timezone.utc).isoformat(),
                "e_star":               result.e_star,
                "contradiction_class":  result.contradiction_class_in.value if result.contradiction_class_in else "",
                "m6_failure_mode":      fm,
                "attractor":            result.new_attractor or "",
                "core_phrase":          result.core_phrase or "",
                "anchor_symbol":        result.anchor_symbol or "",
                "stability_index":      result.stability_index,
                "elapsed_s":            round(elapsed, 1),
            })
            success += 1

        except Exception as ex:
            elapsed = time.monotonic() - t0
            print(f"         ERROR ({elapsed:.1f}s): {ex}")
            _append_log({
                "rel_path":   rel,
                "file_name":  file_path.name,
                "timestamp":  datetime.now(timezone.utc).isoformat(),
                "error":      str(ex),
            })
            errors += 1

        # Delay between calls (skip after last file)
        if i < len(pending):
            time.sleep(delay)

    print(f"\n{'─' * 72}")
    print(f"Ingestion complete.")
    print(f"  Processed : {success}")
    print(f"  Errors    : {errors}")
    print(f"  Memory entries now: ", end="")
    if _MEMORY_PATH.exists():
        count = sum(1 for line in _MEMORY_PATH.read_text(encoding="utf-8").splitlines() if line.strip())
        print(count)
    else:
        print("0")
    print()


def show_status(archive_dir: Path) -> None:
    all_files = _discover_files(archive_dir)
    log = _load_log()
    pending = [f for f in all_files if f.relative_to(_REPO_ROOT).as_posix() not in log]
    done    = [f for f in all_files if f.relative_to(_REPO_ROOT).as_posix() in log]

    print(f"\nIngest Status")
    print(f"  Archive      : {archive_dir}")
    print(f"  Total files  : {len(all_files)}")
    print(f"  Ingested     : {len(done)}")
    print(f"  Pending      : {len(pending)}")

    if done:
        # Show last 5 done
        print(f"\n  Last ingested:")
        entries = sorted(log.values(), key=lambda e: e.get("timestamp", ""))[-5:]
        for e in reversed(entries):
            ts  = e.get("timestamp", "")[:16]
            fn  = e.get("file_name", "?")
            e_s = e.get("e_star", 0)
            att = e.get("attractor", "")
            print(f"    {ts}  E*={e_s:.3f}  {fn}")
            if att:
                print(f"           → {att}")

    if _MEMORY_PATH.exists():
        count = sum(1 for line in _MEMORY_PATH.read_text(encoding="utf-8").splitlines() if line.strip())
        print(f"\n  Memory entries : {count}")
    print()


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Feed FT&E archive documents through the Governor pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--archive",  default=str(_ARCHIVE_DIR), help="Path to archive directory")
    parser.add_argument("--limit",    type=int, default=None,    help="Max files to process this run")
    parser.add_argument("--delay",    type=float, default=3.0,   help="Seconds between API calls (default 3)")
    parser.add_argument("--shuffle",  action="store_true",       help="Process files in random order")
    parser.add_argument("--dry-run",  action="store_true",       help="List files without calling API")
    parser.add_argument("--reset",    action="store_true",       help="Clear ingest log and start fresh")
    parser.add_argument("--status",   action="store_true",       help="Show progress without running")
    parser.add_argument("--verbose",  action="store_true",       help="Show M1-M7 Governor logs")
    args = parser.parse_args()

    archive_dir = Path(args.archive)
    if not archive_dir.exists():
        print(f"ERROR: Archive directory not found: {archive_dir}")
        sys.exit(1)

    if args.reset:
        if _INGEST_LOG.exists():
            _INGEST_LOG.unlink()
            print(f"Ingest log cleared: {_INGEST_LOG}")
        else:
            print("No ingest log found.")
        return

    if args.status:
        show_status(archive_dir)
        return

    run(
        archive_dir,
        limit=args.limit,
        delay=args.delay,
        shuffle=args.shuffle,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
