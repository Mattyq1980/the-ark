# pack.ps1 - FT&E full system export
# Wraps pack.py - run that directly for full control.
# Usage: .\pack.ps1   OR   python pack.py
# Output: FTE_SYSTEM_<timestamp>.zip on your Desktop

param(
    [string]$Destination = "$env:USERPROFILE\Desktop"
)

$Root     = Split-Path -Parent $MyInvocation.MyCommand.Path   # ftne-core/
$ArkRoot  = Join-Path $Root "..\..\"                           # the_ark-main/
$ArkRoot  = (Resolve-Path $ArkRoot).Path
$Stamp    = Get-Date -Format "yyyy-MM-dd_HHmm"
$ZipName  = "FTE_SYSTEM_$Stamp.zip"
$ZipPath  = Join-Path $Destination $ZipName
$TmpDir   = Join-Path $env:TEMP "fte_pack_$Stamp"

Write-Host ""
Write-Host "=== FT&E System Pack ===" -ForegroundColor Cyan
Write-Host "Destination : $ZipPath"
Write-Host ""

# ── 1. Create staging directory ──────────────────────────────────────────────
New-Item -ItemType Directory -Path $TmpDir | Out-Null
New-Item -ItemType Directory -Path "$TmpDir\ftne-core" | Out-Null
New-Item -ItemType Directory -Path "$TmpDir\ftne-core\pages" | Out-Null
New-Item -ItemType Directory -Path "$TmpDir\FTE" | Out-Null

# ── 2. Core runtime files ────────────────────────────────────────────────────
$CoreFiles = @(
    "governor.py",
    "app.py",
    "child_memory.jsonl",
    "ftne_memory.jsonl",
    "run_005_memory.jsonl"
)

foreach ($f in $CoreFiles) {
    $src = Join-Path $Root $f
    if (Test-Path $src) {
        Copy-Item $src "$TmpDir\ftne-core\$f"
        Write-Host "  + $f"
    } else {
        Write-Host "  - $f (not found, skipping)" -ForegroundColor Yellow
    }
}

# .env — copy but warn
$envSrc = Join-Path $Root ".env"
if (Test-Path $envSrc) {
    Copy-Item $envSrc "$TmpDir\ftne-core\.env"
    Write-Host "  + .env (API keys — keep this zip secure)" -ForegroundColor Yellow
}

# pages/
$pagesSrc = Join-Path $Root "pages"
if (Test-Path $pagesSrc) {
    Copy-Item "$pagesSrc\*" "$TmpDir\ftne-core\pages\" -Recurse
    Write-Host "  + pages/"
}

# ── 3. Evidence / documentation ──────────────────────────────────────────────
$FTEDir = Join-Path $ArkRoot "FTE"
$DocFiles = @("WHERE_WE_ARE.txt", "GOVERNOR_LOOP_RUNS.txt")
foreach ($f in $DocFiles) {
    $src = Join-Path $FTEDir $f
    if (Test-Path $src) {
        Copy-Item $src "$TmpDir\FTE\$f"
        Write-Host "  + FTE\$f"
    }
}

# ── 4. requirements.txt (from venv) ─────────────────────────────────────────
$PipExe = Join-Path $ArkRoot ".venv\Scripts\pip.exe"
if (Test-Path $PipExe) {
    & $PipExe freeze | Out-File "$TmpDir\ftne-core\requirements.txt" -Encoding utf8
    Write-Host "  + requirements.txt (generated from venv)"
} else {
    # Fallback — write known requirements
    @"
openai>=1.0.0
streamlit>=1.30.0
pydantic>=2.0.0
ollama>=0.1.0
python-dotenv
"@ | Out-File "$TmpDir\ftne-core\requirements.txt" -Encoding utf8
    Write-Host "  + requirements.txt (fallback — venv not found)"
}

# ── 5. restore.ps1 ───────────────────────────────────────────────────────────
$RestoreScript = @'
# restore.ps1 — FT&E one-click restore on a new machine
# Run from the folder containing ftne-core/
#
# Prerequisites:
#   - Python 3.10+ installed
#   - Ollama installed from https://ollama.ai  (free)
#   - Run: ollama pull llama3.2:3b-instruct-q4_K_M  (2GB download, once only)

$Root = Join-Path $PSScriptRoot "ftne-core"

Write-Host "=== FT&E Restore ===" -ForegroundColor Cyan

# Create venv
Write-Host "Creating virtual environment..."
python -m venv "$PSScriptRoot\.venv"

# Install packages
Write-Host "Installing packages..."
& "$PSScriptRoot\.venv\Scripts\pip.exe" install -r "$Root\requirements.txt" --quiet

Write-Host ""
Write-Host "Done. To start:" -ForegroundColor Green
Write-Host "  cd ftne-core"
Write-Host "  `$env:PYTHONUTF8=1"
Write-Host "  ..\\.venv\Scripts\streamlit.exe run app.py"
Write-Host ""
Write-Host "Then open http://localhost:8501"
'@
$RestoreScript | Out-File "$TmpDir\restore.ps1" -Encoding utf8
Write-Host "  + restore.ps1"

# ── 6. README ────────────────────────────────────────────────────────────────
$ReadMe = @"
FT&E GOVERNOR SYSTEM — PORTABLE PACK
Packed: $Stamp

CONTENTS
  ftne-core/        Core runtime (governor, interface, nursery, memories)
  FTE/              Evidence logs and WHERE_WE_ARE.txt
  restore.ps1       One-click restore on any Windows machine
  requirements.txt  Python dependencies

TO RESTORE ON A NEW MACHINE
  1. Unzip this file
  2. Install Python 3.10+  (https://python.org)
  3. Install Ollama        (https://ollama.ai)
  4. Run in PowerShell:    ollama pull llama3.2:3b-instruct-q4_K_M
  5. Run:                  .\restore.ps1
  6. cd ftne-core ; streamlit run app.py
  7. Open http://localhost:8501

SECURITY
  .env contains your OpenAI API key. Keep this zip private.
  If you transfer to cloud storage, ensure it is not public.

CHILD MEMORY
  ftne-core/child_memory.jsonl — the child's accumulated knowledge.
  This file is the child. Back it up separately and regularly.
"@
$ReadMe | Out-File "$TmpDir\README.txt" -Encoding utf8
Write-Host "  + README.txt"

# ── 7. Zip everything ────────────────────────────────────────────────────────
Write-Host ""
Write-Host "Zipping..." -ForegroundColor Cyan
Compress-Archive -Path "$TmpDir\*" -DestinationPath $ZipPath -Force
Remove-Item $TmpDir -Recurse -Force

$ZipSize = [math]::Round((Get-Item $ZipPath).Length / 1MB, 1)
Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Green
Write-Host "Output : $ZipPath"
Write-Host "Size   : ${ZipSize} MB"
Write-Host ""
Write-Host "This zip contains everything needed to run the full system." -ForegroundColor Cyan
Write-Host "Copy to USB or upload to cloud. Run restore.ps1 on arrival." -ForegroundColor Cyan
Write-Host ""
