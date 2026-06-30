# =============================================================================
# Coastal Structures Studio (CSS v1.0) — automated DWG generation
# Workflow:  validated calculations -> parametric DXF -> native AutoCAD DWG
#
#   1. calculations.py  -> canonical_values.json + calculation report
#   2. generate_port.py -> Suez_Port_Masterplan.dxf (R2018, layered, A1/A3)
#   3. accoreconsole    -> Suez_Port_Masterplan.dwg (native AutoCAD)
#   4. qa_check.py       -> consistency gate
#
# Usage:  powershell -ExecutionPolicy Bypass -File make_dwg.ps1
# (Close Suez_Port_Masterplan.dxf/.dwg in AutoCAD first — open files lock.)
# =============================================================================
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$py   = Join-Path $root ".venv\Scripts\python.exe"
$dxf  = Join-Path $root "output\Suez_Port_Masterplan.dxf"
$dwg  = Join-Path $root "output\Suez_Port_Masterplan.dwg"
$scr  = Join-Path $root "dxf_to_dwg.scr"

function Test-Locked($path) {
    if (-not (Test-Path $path)) { return $false }
    try { $h=[System.IO.File]::Open($path,'Open','ReadWrite','None'); $h.Close(); return $false }
    catch { return $true }
}

# Locate the newest installed AutoCAD core console.
$acc = Get-ChildItem "C:\Program Files\Autodesk\AutoCAD *\accoreconsole.exe" -ErrorAction SilentlyContinue |
       Sort-Object FullName -Descending | Select-Object -First 1 -ExpandProperty FullName
if (-not $acc) { throw "accoreconsole.exe not found — install AutoCAD or use ODA File Converter." }

Write-Host "[1/4] Engineering calculations ..." -ForegroundColor Cyan
& $py (Join-Path $root "calculations.py") | Out-Null

if (Test-Locked $dxf) { throw "DXF is open in AutoCAD — close it and re-run." }
Write-Host "[2/4] Parametric CAD (DXF) ..." -ForegroundColor Cyan
& $py (Join-Path $root "generate_port.py") | Select-Object -Last 1

if (Test-Locked $dwg) { throw "DWG is open in AutoCAD — close it and re-run." }
Remove-Item $dwg -ErrorAction SilentlyContinue
Write-Host "[3/4] Native DWG via $acc ..." -ForegroundColor Cyan
& $acc /i $dxf /s $scr | Out-Null
if (-not (Test-Path $dwg)) { throw "DWG was not produced." }
$kb = [math]::Round((Get-Item $dwg).Length/1KB,1)
Write-Host "      -> $dwg ($kb KB)" -ForegroundColor Green

Write-Host "[4/4] QA consistency gate ..." -ForegroundColor Cyan
& $py (Join-Path $root "qa_check.py") | Select-Object -Last 1
Write-Host "DONE — Suez_Port_Masterplan.dwg ready for AutoCAD." -ForegroundColor Green
