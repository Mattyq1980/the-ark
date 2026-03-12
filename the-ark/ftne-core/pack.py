"""
pack.py - FT&E full system export
Creates a portable zip containing everything needed to run the Governor + Nursery.

Usage:
    python pack.py
    python pack.py --dest E:\\MyUSB

Output: FTE_SYSTEM_<timestamp>.zip  (default: Desktop)
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

HERE     = Path(__file__).parent                          # ftne-core/
ARK_ROOT = (HERE / "../..").resolve()                     # the_ark-main/
DESKTOP  = Path.home() / "Desktop"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", default=str(DESKTOP))
    args = parser.parse_args()

    dest     = Path(args.dest)
    stamp    = datetime.now().strftime("%Y-%m-%d_%H%M")
    zip_name = f"FTE_SYSTEM_{stamp}.zip"
    zip_path = dest / zip_name

    print()
    print("=== FT&E System Pack ===")
    print(f"Output: {zip_path}")
    print()

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "ftne-core" / "pages").mkdir(parents=True)
        (tmp / "FTE").mkdir()

        # Core runtime files
        core_files = [
            "governor.py",
            "app.py",
            "child_memory.jsonl",
            "ftne_memory.jsonl",
            "run_005_memory.jsonl",
            "architect_dialogue.jsonl",
            "architect_propose.py",
            "pack.py",
        ]
        for f in core_files:
            src = HERE / f
            if src.exists():
                shutil.copy2(src, tmp / "ftne-core" / f)
                print(f"  + {f}")
            else:
                print(f"  - {f} (not found, skipping)")

        # .env (API keys)
        env_src = HERE / ".env"
        if env_src.exists():
            shutil.copy2(env_src, tmp / "ftne-core" / ".env")
            print("  + .env  *** KEEP THIS ZIP SECURE - contains API key ***")

        # pages/
        pages_src = HERE / "pages"
        if pages_src.exists():
            for f in pages_src.iterdir():
                shutil.copy2(f, tmp / "ftne-core" / "pages" / f.name)
            print("  + pages/")

        # Evidence docs
        fte_dir = ARK_ROOT / "FTE"
        for f in ["WHERE_WE_ARE.txt", "GOVERNOR_LOOP_RUNS.txt"]:
            src = fte_dir / f
            if src.exists():
                shutil.copy2(src, tmp / "FTE" / f)
                print(f"  + FTE/{f}")

        # requirements.txt
        pip_exe = ARK_ROOT / ".venv" / "Scripts" / "pip.exe"
        req_path = tmp / "ftne-core" / "requirements.txt"
        if pip_exe.exists():
            result = subprocess.run(
                [str(pip_exe), "freeze"],
                capture_output=True, text=True
            )
            req_path.write_text(result.stdout, encoding="utf-8")
            print("  + requirements.txt (from venv)")
        else:
            req_path.write_text(
                "openai>=1.0.0\nstreamlit>=1.30.0\npydantic>=2.0.0\nollama>=0.1.0\n",
                encoding="utf-8"
            )
            print("  + requirements.txt (fallback)")

        # restore.ps1
        restore = (
            "# restore.ps1 - FT&E one-click restore on a new machine\n"
            "# Prerequisites: Python 3.10+  https://python.org\n"
            "#                Ollama         https://ollama.ai\n"
            "# Then run: ollama pull llama3.2:3b-instruct-q4_K_M\n"
            "\n"
            "$Root = Join-Path $PSScriptRoot 'ftne-core'\n"
            "Write-Host '=== FT&E Restore ===' -ForegroundColor Cyan\n"
            "python -m venv \"$PSScriptRoot\\.venv\"\n"
            "& \"$PSScriptRoot\\.venv\\Scripts\\pip.exe\" install -r "
            "\"$Root\\requirements.txt\" --quiet\n"
            "Write-Host 'Done.' -ForegroundColor Green\n"
            "Write-Host 'Run: cd ftne-core ; ..`\\.venv\\Scripts\\streamlit.exe run app.py'\n"
        )
        (tmp / "restore.ps1").write_text(restore, encoding="utf-8")
        print("  + restore.ps1")

        # README
        readme = (
            f"FT&E GOVERNOR SYSTEM - PORTABLE PACK\n"
            f"Packed: {stamp}\n\n"
            f"CONTENTS\n"
            f"  ftne-core/   runtime (governor, interface, nursery, memories)\n"
            f"  FTE/         evidence logs + WHERE_WE_ARE.txt\n"
            f"  restore.ps1  one-click restore on any Windows machine\n\n"
            f"TO RESTORE\n"
            f"  1. Unzip\n"
            f"  2. Install Python 3.10+  https://python.org\n"
            f"  3. Install Ollama        https://ollama.ai\n"
            f"  4. Run: ollama pull llama3.2:3b-instruct-q4_K_M\n"
            f"  5. Run: .\\restore.ps1\n"
            f"  6. cd ftne-core\n"
            f"  7. streamlit run app.py\n"
            f"  8. Open http://localhost:8501\n\n"
            f"SECURITY\n"
            f"  .env contains your OpenAI API key. Keep this zip private.\n\n"
            f"CHILD MEMORY\n"
            f"  ftne-core/child_memory.jsonl IS the child.\n"
            f"  Back it up separately and regularly.\n"
        )
        (tmp / "README.txt").write_text(readme, encoding="utf-8")
        print("  + README.txt")

        # Zip
        print()
        print("Zipping...")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in tmp.rglob("*"):
                if file.is_file():
                    zf.write(file, file.relative_to(tmp))

    size_mb = round(zip_path.stat().st_size / 1024 / 1024, 1)
    print()
    print(f"=== Done ===")
    print(f"Output : {zip_path}")
    print(f"Size   : {size_mb} MB")
    print()
    print("Copy to USB or upload to cloud. Run restore.ps1 on arrival.")
    print()

if __name__ == "__main__":
    main()
