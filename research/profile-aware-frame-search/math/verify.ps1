param([string]$LeanExecutable = "lean")
$ErrorActionPreference = "Stop"
$taskMathRoot = $PSScriptRoot
$env:LEAN_PATH = $taskMathRoot
$taskModules = @("DirtyComplementSafety", "FreshKernelReclaim", "CoordinateConjugacy", "FiniteRationalChecks", "RankFlowPrice", "ProfileSearchCertificate", "Audit")
foreach ($taskModule in $taskModules) {
  & $LeanExecutable -o (Join-Path $taskMathRoot ($taskModule + ".olean")) (Join-Path $taskMathRoot ($taskModule + ".lean"))
  if ($LASTEXITCODE -ne 0) { throw "Lean compilation failed: $taskModule" }
}
