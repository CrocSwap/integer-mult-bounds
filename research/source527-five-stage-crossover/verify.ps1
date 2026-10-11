param([string]$Compiler='g++',[string]$TempRoot=$env:TEMP,[string]$PublicResults='')
$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$work=Join-Path $TempRoot ('five527-'+[Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $work,(Join-Path $work 'deps') | Out-Null
function Payload {
 $m=Get-Content -Raw -LiteralPath (Join-Path $root 'FILES.json')|ConvertFrom-Json
 foreach($e in $m.files){if((Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $root $e.path)).Hash.ToLowerInvariant() -ne $e.sha256){throw ('Payload mismatch '+$e.path)}}
}
function Run-Native([string]$Name,[string[]]$Arguments){
 & (Join-Path $work ($Name+'.exe')) @Arguments
 if($LASTEXITCODE -ne 0){throw ('Native check failed '+$Name)}
}
Payload
$public=Join-Path $root 'references/source527'
if($PublicResults -eq ''){
 $PublicResults=Join-Path $work 'public'
 & python -X utf8 -B (Join-Path $public 'verify.py') --output $PublicResults
 if($LASTEXITCODE -ne 0){throw 'Pinned source527 eight-stage verification failed'}
}
$v=Get-Content -Raw -LiteralPath (Join-Path $PublicResults 'verification.json')|ConvertFrom-Json
if($v.status -ne 'PASS_IMMUTABLE_SOURCE527_FIVE_STAGE_BANKED_CONSTRUCTION' -or !$v.inputs_unchanged -or $v.fresh_stages.Count -ne 8){throw 'Public replay incomplete'}
if($v.manifest_sha256 -ne (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $public 'MANIFEST.json')).Hash.ToLowerInvariant()){throw 'Public replay source manifest mismatch'}
& python -X utf8 -B (Join-Path $root 'native/export-prepared527.py') $public $work
if($LASTEXITCODE -ne 0){throw 'Fresh ownership/labels export failed'}
& python -X utf8 -c 'import gzip,sys,shutil; f=gzip.open(sys.argv[1],"rb"); g=open(sys.argv[2],"wb"); shutil.copyfileobj(f,g); f.close(); g.close()' (Join-Path $PublicResults 'records.bin.gz') (Join-Path $work 'records.bin')
if($LASTEXITCODE -ne 0){throw 'Physical stream decompression failed'}
Expand-Archive -LiteralPath (Join-Path $root 'native/native-deps.zip') -DestinationPath (Join-Path $work 'deps')
$inc=Join-Path $work 'deps/include'
foreach($name in @('source527-assembly','independent527','stage-private527-banks','check-stage-private527-banks','route-interface527','extract527-physical-scalar','five-stage527-columns')){
 Write-Host ('Compiling '+$name)
 & $Compiler -O3 -std=c++20 ('-I'+$inc) ('-I'+(Join-Path $root 'native')) (Join-Path $root ('native/'+$name+'.cpp')) -o (Join-Path $work ($name+'.exe'))
 if($LASTEXITCODE -ne 0){throw ('Compile failed '+$name)}
}
$raw=Join-Path $PublicResults 'raw.json'
$nb=Join-Path $work 'NATIVE-BANKS.json'
Run-Native 'stage-private527-banks' @((Join-Path $work 'BANK-INPUTS527.json'),$nb)
Run-Native 'check-stage-private527-banks' @((Join-Path $work 'BANK-INPUTS527.json'),$nb,(Join-Path $work 'BANKS-INDEPENDENT.json'))
Run-Native 'route-interface527' @((Join-Path $work 'LABELS527.json'),$public,(Join-Path $work 'ROUTES.json'))
$events=Join-Path $work 'EVENTS.json'
Run-Native 'extract527-physical-scalar' @((Join-Path $work 'records.bin'),(Join-Path $PublicResults 'physical.json'),$raw,$events)
Run-Native 'five-stage527-columns' @($events,(Join-Path $work 'COLUMNS.json'))
$assembly=Join-Path $work 'ASSEMBLY.json'
Run-Native 'source527-assembly' @($raw,(Join-Path $PublicResults 'banks.json'),(Join-Path $root 'witnesses/complex-native-profile.json'),(Join-Path $PublicResults 'finite.json'),$nb,$assembly)
Run-Native 'independent527' @($assembly,(Join-Path $work 'INDEPENDENT-ARITHMETIC.json'),(Join-Path $PublicResults 'banks.json'),$raw,$nb)
$fresh=Get-Content -Raw -LiteralPath $assembly|ConvertFrom-Json
$frozen=Get-Content -Raw -LiteralPath (Join-Path $root 'certificate.json')|ConvertFrom-Json
if($fresh.kappa -ne $frozen.kappa){throw 'Frozen kappa mismatch'}
Payload
Write-Host ('PASS source-bound conditional kappa='+$fresh.kappa)
Write-Host ('Preserved verification outputs: '+$work)
