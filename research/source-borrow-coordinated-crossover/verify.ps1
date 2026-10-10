param([string]$Compiler='g++',[string]$TempRoot=$env:TEMP)
$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$work=Join-Path $TempRoot ('source-borrow-crossover-'+[Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $work,(Join-Path $work 'inputs'),(Join-Path $work 'deps'),(Join-Path $work 'results'),(Join-Path $work 'reference')|Out-Null
$manifest=Get-Content -Raw -LiteralPath (Join-Path $root 'FILES.json')|ConvertFrom-Json
function Check-Payload {
 foreach($entry in $manifest.files){
  $actual=(Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $root $entry.path)).Hash.ToLowerInvariant()
  if($actual -ne $entry.sha256){throw ('Source hash mismatch: '+$entry.path)}
 }
}
Check-Payload
Expand-Archive -LiteralPath (Join-Path $root 'native-inputs.zip') -DestinationPath (Join-Path $work 'inputs')
Expand-Archive -LiteralPath (Join-Path $root 'native/native-deps.zip') -DestinationPath (Join-Path $work 'deps')
$include=Join-Path $work 'deps/include'
foreach($name in @('source440-frame-admission','source-frame-admission','source-entrances','bit-columns','joint-banks','source-boundary','actual-signals','native-pricing','independent-pricing','frozen-result','all-active-primes')){
 Write-Host ('Compiling '+$name)
 & $Compiler -O3 -std=c++20 ('-I'+$include) (Join-Path $root ('native/'+$name+'.cpp')) -o (Join-Path $work ($name+'.exe'))
 if($LASTEXITCODE -ne 0){throw ('Compile failed: '+$name)}
}
$taskInput=Join-Path $work 'inputs/combined'
$reference=Join-Path $work 'inputs/reference'
$out=Join-Path $work 'results'
$anchor=Join-Path $reference 'packed-baseline.json'
& (Join-Path $work 'source440-frame-admission.exe') $reference (Join-Path $work 'reference') (Join-Path $root 'witnesses/empty-bases.json') $anchor
if($LASTEXITCODE -ne 0){throw 'Predecessor82 reference graph failed'}
$source440=Join-Path $work 'inputs/source440'
$prior=Join-Path $work 'source440-reference'
New-Item -ItemType Directory -Path $prior|Out-Null
& (Join-Path $work 'source440-frame-admission.exe') $source440 $prior (Join-Path $root 'witnesses/source440-candidate-bases.json') $anchor replace-all (Join-Path $work 'reference/FRAME-ADMISSION.json')
if($LASTEXITCODE -ne 0){throw 'Actual source440 plus73-cut reference failed'}
$sourceAnchor=Join-Path $root 'witnesses/source469-packed-reference.json'
& (Join-Path $work 'source-frame-admission.exe') $taskInput $out (Join-Path $root 'witnesses/candidate-bases.json') $sourceAnchor replace-all (Join-Path $prior 'FRAME-ADMISSION.json')
if($LASTEXITCODE -ne 0){throw 'Latest469 frame/path/profile relative recount failed'}
Copy-Item -LiteralPath (Join-Path $out 'merged-bases.json') -Destination (Join-Path $taskInput 'current-bases.json')
& (Join-Path $work 'all-active-primes.exe') $taskInput (Join-Path $out 'merged-bases.json') (Join-Path $out 'ALL-ACTIVE-PRIMES.json')
if($LASTEXITCODE -ne 0){throw 'Fresh retained-prime admission of every active frame failed'}
& (Join-Path $work 'actual-signals.exe') $taskInput (Join-Path $out 'ACTUAL-SIGNALS.json')
if($LASTEXITCODE -ne 0){throw 'True physical intermediate source-support replay failed'}
& (Join-Path $work 'source-entrances.exe') $taskInput (Join-Path $out 'SOURCE-ENTRANCES.json')
if($LASTEXITCODE -ne 0){throw 'New29 correlated source-gauge histories and target chronology failed'}
& (Join-Path $work 'source-boundary.exe') $taskInput (Join-Path $out 'SOURCE-BOUNDARY.json')
if($LASTEXITCODE -ne 0){throw 'Complete original source/alias/mix paths failed'}
& (Join-Path $work 'bit-columns.exe') $taskInput (Join-Path $out 'ALL-COLUMNS.json')
if($LASTEXITCODE -ne 0){throw 'Actual scalar columns or hostile controls failed'}
& (Join-Path $work 'joint-banks.exe') $taskInput (Join-Path $out 'BANKS.json')
if($LASTEXITCODE -ne 0){throw 'Charts/banks/normalizers/invoice failed'}
& (Join-Path $work 'native-pricing.exe') price (Join-Path $out 'new-profile.json') (Join-Path $root 'witnesses/complex-profile.json') (Join-Path $out 'ASSEMBLY.json') 4 (Join-Path $taskInput 'public-complex-and-bridge.json')
if($LASTEXITCODE -ne 0){throw 'Outward exact moment/assembly replay failed'}
& (Join-Path $work 'independent-pricing.exe') (Join-Path $out 'ASSEMBLY.json') (Join-Path $out 'INDEPENDENT-ARITHMETIC.json') (Join-Path $out 'BANKS.json') $anchor
if($LASTEXITCODE -ne 0){throw 'Independent rational assembly/actual selector/normalization audit failed'}
& (Join-Path $work 'frozen-result.exe') (Join-Path $out 'ASSEMBLY.json') (Join-Path $root 'certificate.json')
if($LASTEXITCODE -ne 0){throw 'Complete frozen result differs from fresh replay'}
$frozen=Get-Content -Raw -LiteralPath (Join-Path $root 'certificate.json')|ConvertFrom-Json
$fresh=Get-Content -Raw -LiteralPath (Join-Path $out 'ASSEMBLY.json')|ConvertFrom-Json
if($fresh.kappa -ne $frozen.kappa){throw 'Final kappa differs from frozen certificate'}
foreach($name in @('m','W','total_rank','maxchild')){
 if($fresh.bit_profile.$name -ne $frozen.bit_profile.$name){throw ('Profile mismatch: '+$name)}
}
if(($fresh.bit_profile.child_multiplicities|ConvertTo-Json -Compress) -ne ($frozen.bit_profile.child_multiplicities|ConvertTo-Json -Compress)){throw 'Profile child histogram mismatch'}
Check-Payload
Write-Host ('PASS fresh offline replay; kappa='+$fresh.kappa)
Write-Host ('Temporary outputs preserved: '+$work)