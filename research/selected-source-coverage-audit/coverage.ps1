# Coverage map: every source PR in certificates/selected-result.json looked up
# across the central ledger and all audit disposition records.
# Usage (PowerShell 5.1+; no Python required):
#   powershell -NoProfile -ExecutionPolicy Bypass -File research/selected-source-coverage-audit/coverage.ps1
# Exit 0 when every source PR has at least one incorporated-strength record;
# exit 1 otherwise (gap list printed). A human-readable report is written to
# research/selected-source-coverage-audit/COVERAGE.md next to COVERAGE.json.
# Re-run after any ledger, disposition, review or integration change.

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Set-Location $root

function Get-PrRecords($path, $items, $numProp, $dispProp) {
  $out = @()
  foreach ($it in $items) {
    $n = $it.$numProp
    if ($null -eq $n) { continue }
    $out += [pscustomobject]@{ number = [int]$n; disposition = [string]$it.$dispProp; record = $path }
  }
  return $out
}

$all = @()

$led = Get-Content docs/research/pr-ledger.json -Raw | ConvertFrom-Json
$all += Get-PrRecords 'docs/research/pr-ledger.json' $led.pull_requests 'number' 'disposition'

$dispFiles = @(
  'research/community-cold617-audit/DISPOSITIONS.json',
  'research/community-family533-audit/DISPOSITIONS.json',
  'research/community-family588-audit/DISPOSITIONS.json',
  'research/community-frontier741-audit/DISPOSITIONS.json',
  'research/community-frontier799-audit/DISPOSITIONS.json',
  'research/community-hyperplane599-audit/DISPOSITIONS.json',
  'research/community-k492-audit/DISPOSITIONS.json',
  'research/community-queue-20261013/REVIEWS.json',
  'research/supplier-circuit-consolidation/DISPOSITIONS.json'
)
foreach ($f in $dispFiles) {
  if (-not (Test-Path $f)) { Write-Warning "missing $f"; continue }
  $d = Get-Content $f -Raw | ConvertFrom-Json
  $all += Get-PrRecords $f $d.pull_requests 'number' 'disposition'
}

$r9 = Get-Content research/community-round9-audit/review-ledger.json -Raw | ConvertFrom-Json
$all += Get-PrRecords 'research/community-round9-audit/review-ledger.json' $r9.prs 'number' 'disposition'

$o = Get-Content research/overnight-pr-review-20261009/dispositions.json -Raw | ConvertFrom-Json
$all += Get-PrRecords 'research/overnight-pr-review-20261009/dispositions.json' $o 'number' 'disposition'

$w = Get-Content research/community-family588-audit/WORKFLOW-DISPOSITIONS.json -Raw | ConvertFrom-Json
$all += Get-PrRecords 'research/community-family588-audit/WORKFLOW-DISPOSITIONS.json' $w 'pr' 'disposition'

$q12 = Get-Content docs/research/pr-review-queue-20261012.json -Raw | ConvertFrom-Json
$all += Get-PrRecords 'docs/research/pr-review-queue-20261012.json' $q12.pull_requests 'number' 'review_status'

$q11 = Get-Content docs/research/pr-queue-20261011.json -Raw | ConvertFrom-Json
foreach ($e in $q11.prs) {
  $all += [pscustomobject]@{ number = [int]$e.number; disposition = 'open_snapshot_entry'; record = 'docs/research/pr-queue-20261011.json' }
}

# Exact-head integration receipts whose reviewed_heads map is keyed by PR number.
$intFiles = @(
  'docs/research/community-pr531-integration.json',
  'docs/research/community-frontier799-integration.json'
)
foreach ($f in $intFiles) {
  $d = Get-Content $f -Raw | ConvertFrom-Json
  foreach ($k in $d.reviewed_heads.PSObject.Properties.Name) {
    $all += [pscustomobject]@{ number = [int]$k; disposition = 'reviewed_head_in_integration_receipt'; record = $f }
  }
}

$pub = Get-Content research/community-frontier799-audit/PUBLICATION.json -Raw | ConvertFrom-Json
foreach ($e in $pub.pull_requests) {
  $pn = $e.number; if ($null -eq $pn) { $pn = $e }
  $all += [pscustomobject]@{ number = [int]$pn; disposition = 'published'; record = 'research/community-frontier799-audit/PUBLICATION.json' }
}

$cc = Get-Content research/community-frontier799-audit/CONTENT-COVERAGE.json -Raw | ConvertFrom-Json
foreach ($k in $cc.pull_requests.PSObject.Properties.Name) {
  $all += [pscustomobject]@{ number = [int]$k; disposition = 'content_coverage_entry'; record = 'research/community-frontier799-audit/CONTENT-COVERAGE.json' }
}

$sel = Get-Content certificates/selected-result.json -Raw | ConvertFrom-Json
$sourceNums = @($sel.source_prs | ForEach-Object { [int]$_ } | Sort-Object -Unique)

$strong = @('incorporated', 'reviewed_head_in_integration_receipt', 'published')
$rows = @()
foreach ($n in $sourceNums) {
  $hits = @($all | Where-Object { $_.number -eq $n })
  $hasStrong = @($hits | Where-Object { $strong -contains $_.disposition }).Count -gt 0
  $rows += [pscustomobject]@{
    number = $n
    records = @($hits | ForEach-Object { "$($_.record)#$($_.disposition)" })
    has_incorporated_record = $hasStrong
  }
}

$outDir = 'research/selected-source-coverage-audit'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$rows | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $outDir 'COVERAGE.json') -Encoding utf8

$noRecord = @($rows | Where-Object { $_.records.Count -eq 0 })
$noStrong = @($rows | Where-Object { -not $_.has_incorporated_record })

$md = @()
$md += '# Selected-source coverage map'
$md += ''
$md += "Base: $(git rev-parse HEAD)"
$md += "Selected record: certificates/selected-result.json (kappa $($sel.decimal))"
$md += "Source PRs checked: $($sourceNums.Count)"
$md += "Record entries indexed: $($all.Count)"
$md += ''
$md += "## PRs with no record in any indexed file ($($noRecord.Count))"
$md += ''
if ($noRecord.Count -eq 0) { $md += 'None.' } else { foreach ($r in $noRecord) { $md += "- #$($r.number)" } }
$md += ''
$md += "## PRs with no incorporated-strength record ($($noStrong.Count))"
$md += ''
if ($noStrong.Count -eq 0) { $md += 'None.' } else { foreach ($r in $noStrong) { $md += "- #$($r.number): $($r.records -join '; ')" } }
$md += ''
$md += '## Full per-PR map'
$md += ''
$md += '| PR | incorporated record? | records |'
$md += '|---|---|---|'
foreach ($r in $rows) { $md += "| #$($r.number) | $($r.has_incorporated_record) | $($r.records -join '<br>') |" }
$md += ''
$md += 'Note: `incorporated` is the central-ledger term for a contribution whose reviewed change is published on the integration path. `reviewed_head_in_integration_receipt` and `published` are the equivalent integration-level bindings. Other dispositions (partially reviewed, unreviewed, scoped review rows, queue snapshot entries) are listed verbatim, not promoted. Vendored-source bindings recorded in package PROVENANCE files and narrative predecessor citations are documented in the accompanying research note, not in this ledger-derived map.'
$md -join "`n" | Set-Content (Join-Path $outDir 'COVERAGE.md') -Encoding utf8

Write-Output "source PRs: $($sourceNums.Count), with no record anywhere: $($noRecord.Count), with no incorporated-strength record: $($noStrong.Count)"
if ($noRecord.Count -gt 0) { Write-Output 'NO-RECORD:'; $noRecord | ForEach-Object { Write-Output "  #$($_.number)" } }
if ($noStrong.Count -gt 0) { Write-Output 'NO-INCORPORATED-STRENGTH:'; $noStrong | ForEach-Object { Write-Output "  #$($_.number): $($_.records -join '; ')" } }
if ($noRecord.Count -gt 0 -or $noStrong.Count -gt 0) { exit 1 } else { exit 0 }
