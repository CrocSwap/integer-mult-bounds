$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
  lake build
  if ($LASTEXITCODE -ne 0) { throw 'Lean build failed' }
  python verify_phase_endpoint.py
  if ($LASTEXITCODE -ne 0) { throw 'Phase audit failed' }
  python verify_precision_profile.py
  if ($LASTEXITCODE -ne 0) { throw 'Profile audit failed' }
  python verify_mixed_center_image.py --output work/image-audit
  if ($LASTEXITCODE -ne 0) { throw 'Image audit failed' }
  python verify_adapter.py --dag work/image-audit/mixed28.bin
  if ($LASTEXITCODE -ne 0) { throw 'Canonical grid adapter audit failed' }
} finally { Pop-Location }
