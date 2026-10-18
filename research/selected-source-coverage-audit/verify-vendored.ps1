# Independent re-verification of the vendored-source binding behind the
# selected construction's #635-#699 predecessor block.
#
# For each of the 298 rows in
# research/complex-sw4-frame8/provenance/SOURCE-FILES.json this script checks
# two independent equalities:
#   (a) SHA256(working-tree file) == recorded sha256  (manifest fidelity), and
#   (b) git-blob-sha1(working-tree file) == git-blob-sha1(<commit>:<upstream_path>)
#       (the vendored bytes are byte-identical to the named Git object).
# Arm (b) uses only git object ids, so no binary content crosses the shell.
#
# Usage (PowerShell 5.1+; no Python required):
#   powershell -NoProfile -ExecutionPolicy Bypass -File research/selected-source-coverage-audit/verify-vendored.ps1
# Exit 0 iff all rows pass both arms. Results go to VENDORED-CHECK.json.
#
# Required commits must resolve locally. The two pins used here are CrocSwap
# main 17ce0c79b7b51c2634b439ea5a2b754f09909693 and PR635
# a6895a69f8ad98ab45777b03e9e6f48888c39f6f; fetch them first if needed:
#   git fetch origin <sha>

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Set-Location $root

$manifest = 'research/complex-sw4-frame8/provenance/SOURCE-FILES.json'
$entries = Get-Content $manifest -Raw | ConvertFrom-Json

$pass = 0; $fails = @()
foreach ($e in $entries) {
  $wt = Join-Path 'research/complex-sw4-frame8' ($e.path -replace '/', [IO.Path]::DirectorySeparatorChar)
  $row = [pscustomobject]@{ path = $e.path; commit = $e.commit; ok_manifest = $false; ok_object = $false; detail = '' }
  if (-not (Test-Path $wt)) { $row.detail = 'working-tree file missing'; $fails += $row; continue }
  $h = (Get-FileHash $wt -Algorithm SHA256).Hash.ToLower()
  if ($h -ne $e.sha256) { $row.detail = "sha256 mismatch tree=$h manifest=$($e.sha256)"; $fails += $row; continue }
  $row.ok_manifest = $true
  $blobTree = (git hash-object $wt 2>&1).Trim()
  $blobObj = (git rev-parse "$($e.commit):$($e.upstream_path)" 2>&1).Trim()
  if ($blobTree -eq $blobObj -and $blobTree -match '^[0-9a-f]{40}$') {
    $row.ok_object = $true; $row.detail = "blob $blobTree"; $pass++
  } else {
    $row.detail = "blob mismatch tree=$blobTree object=$blobObj"; $fails += $row
  }
}

$out = [pscustomobject]@{
  base = (git rev-parse HEAD).Trim()
  manifest = $manifest
  total = $entries.Count
  passed = $pass
  failed = $fails.Count
  failures = $fails
}
$out | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $PSScriptRoot 'VENDORED-CHECK.json') -Encoding utf8
Write-Output "VENDORED-CHECK total=$($entries.Count) passed=$pass failed=$($fails.Count)"
foreach ($f in $fails) { Write-Output "  FAIL $($f.path): $($f.detail)" }
if ($fails.Count -gt 0) { exit 1 } else { exit 0 }
