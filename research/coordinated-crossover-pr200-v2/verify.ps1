param([string]$Compiler='g++')
$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$work=Join-Path $root ('.work-'+[Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $work,(Join-Path $work 'inputs'),(Join-Path $work 'deps'),(Join-Path $work 'results') | Out-Null
$manifest=Get-Content -Raw -LiteralPath (Join-Path $root 'FILES.json') | ConvertFrom-Json
foreach($file in $manifest.files){
 $actual=(Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $root $file.path)).Hash.ToLowerInvariant()
 if($actual -ne $file.sha256){throw "Source hash mismatch: $($file.path)"}
}
Expand-Archive -LiteralPath (Join-Path $root 'native-inputs.zip') -DestinationPath (Join-Path $work 'inputs')
Expand-Archive -LiteralPath (Join-Path $root 'native/native-deps.zip') -DestinationPath (Join-Path $work 'deps')
$include=Join-Path $work 'deps/include'
foreach($name in @('frame-admission','bit-columns','native-pricing')){
 & $Compiler -O3 -std=c++20 ("-I"+$include) (Join-Path $root ('native/'+$name+'.cpp')) -o (Join-Path $work ($name+'.exe'))
 if($LASTEXITCODE -ne 0){throw "Compilation failed: $name"}
}
$inputs=Join-Path $work 'inputs'
$results=Join-Path $work 'results'
& (Join-Path $work 'frame-admission.exe') $inputs $results (Join-Path $root 'witnesses/additional-bases.json') (Join-Path $inputs 'packed-baseline.json')
if($LASTEXITCODE -ne 0){throw 'Frame/prime/path admission failed'}
& (Join-Path $work 'bit-columns.exe') $inputs (Join-Path $results 'ALL-COLUMNS.json')
if($LASTEXITCODE -ne 0){throw 'Formal column replay failed'}
& (Join-Path $work 'native-pricing.exe') price (Join-Path $results 'new-profile.json') (Join-Path $root 'witnesses/complex-profile.json') (Join-Path $results 'ASSEMBLY.json') 4 (Join-Path $inputs 'public-complex-and-bridge.json')
if($LASTEXITCODE -ne 0){throw 'Exact arithmetic assembly failed'}
$actual=Get-Content -Raw -LiteralPath (Join-Path $results 'ASSEMBLY.json') | ConvertFrom-Json
if($actual.kappa -ne '427415195711/625000000000000'){throw 'Unexpected kappa'}
if(-not $actual.adjacent_kappa_rejected){throw 'Missing adjacent-grid negative control'}
foreach($file in $manifest.files){
 $hash=(Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $root $file.path)).Hash.ToLowerInvariant()
 if($hash -ne $file.sha256){throw "Source changed during replay: $($file.path)"}
}
Write-Output ('PASS: kappa = '+$actual.kappa+'; all source hashes, frames, primes, columns and47constraints.')
Write-Output ('Fresh replay receipts: '+$results)