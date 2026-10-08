param([string]$LeanExecutable = "lean")
$ErrorActionPreference = "Stop"
$taskMathRoot = $PSScriptRoot
$env:LEAN_PATH = $taskMathRoot
foreach ($taskModule in @("DirtyComplementSafety", "FreshKernelReclaim", "FiniteRationalChecks", "CircuitToggleSafety", "CurrentRecordCertificate", "Audit")) {
  & $LeanExecutable -o (Join-Path $taskMathRoot ($taskModule + ".olean")) (Join-Path $taskMathRoot ($taskModule + ".lean"))
  if ($LASTEXITCODE -ne 0) { throw "Lean compilation failed: $taskModule" }
}
