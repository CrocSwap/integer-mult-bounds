param(
  [string]$LeanExe = "lean"
)
$ErrorActionPreference = "Stop"
$proofRoot = $PSScriptRoot
$priorLeanPath = $env:LEAN_PATH
try {
  $env:LEAN_PATH = $proofRoot
  Push-Location -LiteralPath $proofRoot
  & $LeanExe --version
  if ($LASTEXITCODE -ne 0) { throw "Lean executable failed" }
  & $LeanExe -o DyadicCertificates.olean DyadicCertificates.lean
  if ($LASTEXITCODE -ne 0) { throw "DyadicCertificates failed kernel checking" }
  if (Test-Path -LiteralPath "GaussianLattice.lean") {
    & $LeanExe -o GaussianLattice.olean GaussianLattice.lean
    if ($LASTEXITCODE -ne 0) { throw "GaussianLattice failed kernel checking" }
  }
  Write-Output "All included Lean modules checked successfully."
} finally {
  Pop-Location
  $env:LEAN_PATH = $priorLeanPath
}
