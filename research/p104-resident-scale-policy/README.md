# Resident SCALE2 in the complete selected scalar policy

Integrate Nick Petalas's released [PR6608](https://github.com/CrocSwap/integer-mult-bounds/pull/6608)
resident doubling edge into Ali Romman's [PR6530](https://github.com/CrocSwap/integer-mult-bounds/pull/6530)
complete exclusive two-bank scalar policy. For width64 and every integerD>=1,
the exact optimum in the enlarged stated policy class changes from

    800847760D-5118198  to  800328108D-5109750,
    saving519652D-8448 > 0  (511204 operations atD=1).

This is a complete scalar policy operation bill, not a rawADD saving, wall-time
speedup or a full native supplier bill. One additional edge executes SCALE2 only
when its target is already resident, retaining its current physical bank and
owner-head state. All original edges, other coefficients, COPY/ADD premises and
native/reset/final flushes remain. The same four tapes,102272D owner bits,
256D staging bits, one carry and two clean finite-control bits are used. No new
payload stock, prefetch, acquisition or physical bank permutation is free.

[PROOF.md](PROOF.md) states the exact policy and all-D certificate argument.
Source local template correctness/prices remain credited premises. The new
resident route and its component price3284D-2 are6608's result; the new work
binds them to the complete selected event sequence and policy bill.

## Evidence and limits

The primary first full optimality attempt passed. Complete baseline/candidate
graphs have59170/59276 state rows,314133/314589 edges and maximum4/5 states/layer,
respectively, over22805 layers. Every retained affine potential satisfies every
actual edge residualA>=0,A+B>=0, and an actual attaining physical-bank action
path reaches the exact final total. D1/D2 interpolation alone is not acceptance.
[POLICY.json.gz](POLICY.json.gz) retains all layers/actions plus literalD1/D2
resident route words. The independent engine checks actual submitted proof data
after blind firsts; normalized state/edge/potential hashes are supplemental indexes.

The primary literal resident-route checks cover386 basis columns and43 signed
fixtures, complete active bits/head/control/meter and literal inverse. The129
D1 basis columns also match actual pinned source SCALE2 gate data including
unchanged carry. The old template costs are inherited, not re-audited. This does
not physically execute all scalar/native operations throughout the whole word.
Native/reset bodies,7936D reset requests, initial layout, uniform encoded-D
control, precision/stock, complete supplier funding and outer transfer remain
open. No newkappa, frontier change or complete multiplication theorem is claimed.

[RUN-RECORDS.json](RUN-RECORDS.json) and [VALIDATION.md](VALIDATION.md) distinguish
primary execution, independent actual-data comparisons and later transport checks.
Source15objects authenticate before bounded decode; old Python source stays
inert and is never imported/executed. Separate AI review is not independent
human or formal-kernel acceptance.

## Reproduce

From the repository root, CPython3.12, standard library only:

```sh
python3.12 -I -W error -B research/p104-resident-scale-policy/verify.py
python3.12 -I -W error -B research/p104-resident-scale-policy/oracle.py --check-primary research/p104-resident-scale-policy/RESULT.json
python3.12 -W error -B scripts/research_package.py --package research/p104-resident-scale-policy
```

[VERIFY.json](VERIFY.json) registers both commands in normal/optimized modes and
explicitly declares POLICY.json.gz as a runtime input. Direct commands are
read-only and need noGit/network/compiler/Lean/Docker. Regenerated gzip equality
compares complete decompressed canonical values, not container bytes. Combined
caps500000 states/3000000 edges,32MiB per input decode,64MiB combined artifact and
180s per command are predeclared; no pruning meets these caps. New functions are
at most50physical lines and explicit checks remain active under-O. CPython dynamic
allocation, arbitrary-precision integers and bounded recursive JSON comparison
are managed-runtime deviations from fixed allocation/no recursion.

## Open next questions

Structured copies are in [TASK.json](TASK.json).

1. Which other actual SCALE coefficient merits a same-ribbon implementation?
   First bind its exact bit circuit, workspace, no-overflow domain and complete
   policy edge, then compare the resulting full bill. No new edge is reserved.
2. Can one actual native/reset boundary meet the inherited entry/exit contract?
   Name one source body and price its complete tape, stock and precision needs.
   This scalar certificate does not implement the native/grid/reset stubs.
3. Can a uniform encoded-D controller realize this compiled family affordably?
   First specify counters, instruction encoding, access and head-return costs;
   no such uniform implementation or full supplier invoice is supplied.

## Credit

Ali Romman6530/6527/6513/6511 supplies cache, staging, scalar/tape and affine-proof
methods. Nick Petalas6608 supplies resident SCALE2 and its component bill, with
retained scalar-circuit credit. Sagar Thakrar3241, DreamingOfClouds6030 and all
retained native/owner/precision/compiler authors retain credit. ywz65/PR2545
supplies earlier R439 window-residency/restricted-DP context; its route/XOR totals
and weaker intermediate-restoration contract are not transferred. Exact source
notices remain in inputs/; [SOURCE-PINS.json](SOURCE-PINS.json) identifies original
commits, paths, Gitblobs and SHA256s. Classical shortest-path duality, affine
inequalities, adjacent swaps and reversible finite control retain their usual
credit. Prepared for ToikY with substantial OpenAI Codex assistance and separate
AI primary/oracle/static review, Apache-2.0. No frozen predecessor or selected
source is changed.
