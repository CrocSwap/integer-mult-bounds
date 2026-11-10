# Exact fixed-price nine-query tariff486

Close Nick Petalas's [PR6696 question1](https://github.com/CrocSwap/integer-mult-bounds/pull/6696):
in the five-source path-lowered even-subset class at prices(b,a,x)=(38,2,2),
the minimum at exactly nine queries is486. This is a modest corollary with
independent premise/ABI verification, not a new geometry or counting law.

The credited unrestricted nine-point geometry of apoursh6059 Lemma2 (also
Arham Tahir1340's prior table) givesR>=68. Path-local closure forcesX in
{2,6,10,...}; thereforeX>=6 costs at least490. PR6696's knownX2minimumR70
and credited path(0,1,3,2,6,14,10,26,16,0) attain486. No new witness,
2600-point normalization/census, all-price frontier or physical supplier is claimed.
The six-query tariff436 remains better. See [PROOF.md](PROOF.md).

## Evidence and reproduction

The primary independently enumerates3780coordinate-unlabeled X2forest graphs,
using one three-vertex path plus three paired edges on the nine query positions.
Every graph's actual code, nine prefix slots and31even-subset minima are retained
in [FLOOR.json.gz](FLOOR.json.gz). Repeated prefix values are allowed, not filtered.
All120coordinate labelings preserveR/X, recovering the credited453600walks.
The primary uses512subset states. The independent engine scans five-edge subsets
and uses64(mask,parity) BFS states; actual complete rows are compared after blind
first seals. MinimumR70/classification/count remain credited premises checked
independently, not newly claimed floor or enumeration results.

The submitted actual witness word has9queries,70readouts,2sourceXORs,81root
dispatches and fixture invoice322map leaves+81echo nodes+2XORs+81dispatches=486,
with4borrowed dirty rows. A free noncommuting operator-word interpreter checks
its actual query prefixes, minimum even readout slots, every dirty output/source/
connector/private row, full map and literal inverse. The old model remains inert
text. This checks the abstract ABI and inherited complete-call price fixture;
no physical backend, native multiplier, stock or precision claim follows.

From the repository root, CPython3.12, standard library only:

```sh
python3.12 -I -W error -B research/nine-query-fixed-tariff/verify.py
python3.12 -I -W error -B research/nine-query-fixed-tariff/oracle.py --check-primary research/nine-query-fixed-tariff/RESULT.json
python3.12 -W error -B scripts/research_package.py --package research/nine-query-fixed-tariff
```

[VERIFY.json](VERIFY.json) adds both optimized modes and declaresFLOOR.json.gz as
a runtime input. Direct commands are read-only and need noGit/network/compiler/
Lean/Docker. Source/cases/schema authenticate before computation. Exact typed
retained values, duplicate/nonfinite/float/boolean-alias guards and ten primary
parser/ABI/omission negative controls remain active under-O. Proof artifacts are
bounded at8MiB,4000records and180s per command. New functions stay below50physical
lines. CPython dynamic allocation, arbitrary-precision integers and bounded
recursive JSON comparison are declared managed-runtime deviations. Regenerated
gzip equality compares complete canonical payloads, not container bytes.

[RUN-RECORDS.json](RUN-RECORDS.json) and [VALIDATION.md](VALIDATION.md) retain exact
first timings, subsequent checks, corrections and pending transport stages.
Formal-kernel and independent human acceptance are unclaimed.

## Open next questions

Structured copies are in [TASK.json](TASK.json).

1. What is the full nine-query frontier for arbitrary positive prices? This
   fixed-price closure does not classify the higher-X tradeoffs. First define
   one source-bound price region and its relevant layers before a wider census.
2. Does the fixed nine-query486 tariff extend to non-path restored source-XOR
   programs? Prior projection/geometry already gives the genericR68bound. First
   classify their actualX2source cost; the path-localX=2(S-9)/forest reduction
   does not establish a non-pathX2minimum or fixed486tariff.
3. Can one physical caller implement the inherited price fixture profitably?
   Specify complete calls, access, dirty restoration, routing, coefficient/
   precision/stock and all extra caller charges. None is supplied by this invoice.

## Credit

apoursh6059 supplies the unrestricted geometry; Arham Tahir1340 its prior table
and mutable-source contract. Nick Petalas6696 supplies the question, floor count,
X2minimum and attaining path;6695/5935 retain adjacent support/XOR context.
Wentao Li2677/2686/2643, Arham Tahir1898, ywz652455, Ross Richardson943 and the
retained1370lineage keep predecessor credit. Exact original notices remain in
inputs/ with [SOURCE-PINS.json](SOURCE-PINS.json). Classical incidence rank,
forest counting, subset DP and shortest paths are used. Prepared for ToikY with
substantial OpenAI Codex assistance and separate AI primary/oracle/static review,
Apache-2.0. No predecessor source, κ or selected frontier changes.
