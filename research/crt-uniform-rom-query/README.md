# Uniform ROM query from encoded parameters

One fixed 752-instruction, ten-tape program now reads binary `h,s,offset,target`,
validates their relations, scans an externally supplied row ROM, returns its
selected bit, erases private scratch and returns every head. Neither a decoded
parameter nor a host loop index is available to its finite control.

For **every** h>=1, 2<=s<=2^h, offset<s, target<2^h and every s·2^h-bit ROM,
[PROOF.md](PROOF.md) establishes correctness and the complete instruction bound

`T <=512(s·2^h+1)(h+bit_length(s)+2)^2`.

The executed tape alphabet is bits plus fixed `L/R/blank` markers. Its census
includes equality, branches, register assignments, jumps and all tape actions.
A separate, explicit three-bit local symbol lowering proves

`T_binary <=65536(s·2^h+1)(h+log2(s)+1)^2`.

The binary lowering is a proof, not an executed binary emulator or measured
runtime. The finite tests support the executable proof; they do not establish
its quantified bound by extrapolation.

## What this closes

[PR4739](https://github.com/CrocSwap/integer-mult-bounds/pull/4739), exact head
`26ccde014218f7d906d1251dc295fbc1437ede8a`, exposes fixed ROM loops and excludes
Boolean control from its local tape-action census. [PR4192](https://github.com/CrocSwap/integer-mult-bounds/pull/4192),
head `519d811cc48693ad9969d6d7994bef3940167005`, already gives a written paid
scalar-lowering bound, while its Python `query_stream` uses host-sized scalar
selection and iteration. This package materializes **one conditional query
primitive** with encoded control. It does not dispute that written accounting,
replace the whole compiler, or claim the first encoded CRT arithmetic; the
existing `research/crt-address-streams` package remains relevant prior art.

The caller [PR4716](https://github.com/CrocSwap/integer-mult-bounds/pull/4716),
head `d9913fe24f119f9d431f324dbbe7d90de409a856`, requires three fresh-state queries.
The retained 544-bit ROM and its two transported witness query sequences match
this component at h=5,s=17. The six calls return the same bits, with 309,005 or
322,303 **complete marker-alphabet instructions per call**. These are not
comparable to PR4739's read/write/move-only counts as a speedup measurement.

`FIXTURE.json` is a small derived ROM/witness fixture. Its exact predecessor
receipt path, commit and SHA256 are recorded, and the verifier checks the ROM's
bit-byte hash against that receipt's fixed hash. No predecessor code is vendored
or dynamically imported. Offline replay checks this retained fixture, not the
original ROM compiler or all predecessor conclusions.

## Interface and obligation ledger

Inputs are finite framed records `L payload R`, with the unique left marker at
cell zero, heads at zero and blank cells afterward. Integer payloads are
canonical little-endian binary; zero is one zero digit. All owned tapes start
blank. `out` returns `L bit R`; `count,col,row,limit` finish entirely blank.
Private scratch uses `bit_length(h)+2h+bit_length(s)+9` cells, including markers,
and no ROM copy. Invalid payloads and parameter relations reject through the same cleanup path.
Unframed/infinite tapes are outside this interface. The cost bound applies to
valid parameters and correct ROM length; it does not hide arbitrarily long
malformed-header validation in a bound depending only on their numeric value.

| Obligation | Status |
| --- | --- |
| Canonical parameter checks; binary-h countdown; dynamic row/column counters | Executed and statically charged |
| Every finite-control decision and read/write/unit move | Executed; independent event interpreter checks complete census |
| Borrowed restoration, all ten head returns, four scratch erasures | Executed and proved for the interface |
| Fixed marker-to-binary local lowering | Proved upper bound, not executed binary emulator |
| ROM/header preparation and encoded source-descriptor adapter | External; not included or integrated |
| CRT reconstruction, producer, full exceptional-key repair and full E tariff | Open; no cost or theorem admission here |

The host supplies framed inputs and emulates tape positions. Its interpreter
allocation, watchdog and observer trace are outside the machine cost. None
feeds a decoded data word, address, length or variable loop bound to the static
program. This distinction is spelled out at the instruction level in the proof.
No new kappa or selected-frontier change is claimed.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/crt-uniform-rom-query --check-only
python3 -B scripts/research_package.py --package research/crt-uniform-rom-query
python3 -I -O -B research/crt-uniform-rom-query/verify.py
```

The default verifier reads the frozen result; it never repairs a missing or
changed receipt. `--write-result` is an explicit producer command. The program
is instantiated identically for every query. Validation covers all ROM contents
and addresses at h=1, every valid parameter tuple at h=2 under two ROMs, larger
boundary cases through h=5 (including s=2^h), the six source query epochs,
malformed/range/ROM rejection, and large encoded h=65 and h=127 early-rejection
paths. These large widths do not run exponentially sized ROMs.

A separate list-based event interpreter replays every listed PC, cell read,
write, Boolean register and branch, and checks final ownership, erasure and
heads. Fault controls detect omitted equality or halt events, wrong readback,
nonunit movement, borrowed writes, dirty scratch and a wrong selected bit.
See `RESULT.json` for the exact deterministic counts and source hashes.

## Open next questions

1. Connect the current-state descriptor and offset produced in PR4739 to this
   canonical query interface, with all conversions/copies and return ownership
   charged. First execute one literal three-epoch key with this component;
   borrowed-input serialization and integration costs remain external here.
2. Price the actual ROM producer, reuse and disposal together with that adapter
   and the CRT arithmetic. Start with one source-bound row producer and combine
   its costs with this query theorem before comparing the complete E allowance.
   A locally uniform lookup does not discharge the rest of the evaluator.

Structured questions and the bounded stopping rule are in `TASK.json`.

Canonical [claim and status](https://github.com/CrocSwap/integer-mult-bounds/discussions/4709#discussioncomment-19130785).
Overlap was searched offline across 506 open PRs at 2026-10-22 18:49:46 UTC,
3,650 Discussion records at 18:50:37 UTC, and 5,860 local notes on canonical
main `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority 7. Listed pagination was
complete; relevant heads above were live-checked. Code diffs, closed-only work
and unpublished work are not covered by that cached search.

Credit: JoyboyBrian with substantial OpenAI Codex assistance; Apache-2.0.
Predecessor ideas and fixture lineage retain Cinna Davis (#4100), ToikY (#4192),
Hiroki KUMAZAKI (#4716 and placement/repair), unpaidmoon, Ryanson Jonathan,
Jose Manuel, John-Michael Smith and Douglas Colkitt's CRT/physical-repair work.
This is author/AI-checked evidence, not independent human or formal acceptance.
