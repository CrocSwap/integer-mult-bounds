# R480 quad 1: twelve fewer scalar XORs, no new κ

**Finite bit-circuit construction.** The historical #503/#510 R480 word's
quad 1 changes from 18 to 12 XORs, with six further XORs removed from its
literal reverse cleanup. Complete local scalar work is **33,958 → 33,946**.
Every one of the 720 register frame paths, all 480 dirty helpers, nine copied
totals, and the paid recursive histogram are unchanged. This is a small
constant-cost improvement to a historical supplier, not a new selected bound.

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The selected record on that base is #626/#543, with
κ = `51110230636731/31250000000000000`. It is not changed here.
[SOURCES.json](SOURCES.json) pins the actual inputs and predecessor heads;
[CLAIM.json](CLAIM.json) records assignment seed **1**, candidate selection
and the local sprint claim. No coordination issue was found.

During submission refresh, main advanced to
`7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`: the selected result became
#741/#589, κ = `1661202643272239/1000000000000000000`. Its new selected
record and maintainer review were read. All eight consumed input files and
the inherited checker package remain unchanged. This contribution still
targets the historical R480 circuit. The old selected-record hash is retained
as dated context, not imposed as a replay dependency on today's mutable pointer.

## Reproduce

Python 3.9+ and the standard library suffice for the primary certificate:

```sh
python3 -I -B research/r480-quad-seed1/verify.py --out /tmp/r480-quad-seed1
```

Expected final line:

```text
PASS_R480_QUAD_SEED1 quad=1 XORs=33958->33946 saved=12 columns=720 controls=20 kappa=unchanged
```

The command compares all evidence with [EXPECTED.json](EXPECTED.json), and
writes the complete candidate word and receipt to the requested directory.
It imports no producer or inherited checker code. Normal and optimized
Python both enforce its checks.

Independent set-valued replay and exact rational frame checks:

```sh
python3 -I -B research/r480-quad-seed1/independent_check.py \
  --word /tmp/r480-quad-seed1/word.json.gz
```

Expected JSON status: `PASS_INDEPENDENT_SET_VALUED_DIRTY_INPUT_REPLAY`;
720 columns and 16 rejected controls. The implementation uses support sets,
not the primary verifier's packed bit masks.

To reproduce the single completed synthesis attempt:

```sh
python3 -I -B research/r480-quad-seed1/discover.py --output /tmp/r480-recipe.json
cmp /tmp/r480-recipe.json research/r480-quad-seed1/recipe.json
```

There is no solver or network dependency. Discovery started at quad
`seed % 60 = 1` and stopped at the first strict improvement, attempt 0.
Only one attempt on that quad was completed; no other quad was searched.
The original budget allowed up to 60 quads in cyclic order. The replay
deliberately repeats only the completed attempt, with at most 17 subtraction
steps. This is a witness, not an optimality or impossibility claim.

Optional native replay needs a C++17 compiler and Boost headers. It reuses
the unchanged, manifest-pinned predecessor checker chain:

```sh
BOOST_INCLUDE=/path/to/boost python3 -B research/r480-quad-seed1/native_replay.py \
  --work /tmp/r480-native-replay
```

The driver rejects optimized Python because the inherited checkers use
assertions. [NATIVE-EXPECTED.json](NATIVE-EXPECTED.json) contains the compact
semantic receipt. Gzip container bytes are not used to compare regenerated
words: canonical decompressed JSON is checked.

## Exact change and proof

The source is `research/e8-r480-dead-totals/data/bitE8mut-r480.json.gz`.
Replace the zero-based half-open slice `A[621:639]`, frame 303 (rational rank
four). The ordered wires are `[487, 504, 550, 574, 598, 622]`; all are existing
helpers. In local wire indices, the new ordered pairs `(destination, source)`
are:

```text
(2,5) (3,4) (0,1) (0,3) (0,5) (2,3)
(5,2) (3,2) (1,2) (4,0) (5,4) (3,0)
```

Each pair is one XOR, with both operands at frame 303. No temporary register,
source-access operation, preparation or unpriced restoration is added.
`C` is regenerated as the literal reverse of `A` at FULL; `B` writes targets
only. All other fields are byte-for-byte equal as JSON data, including the
dirty compensation `D`, retained totals, scatter, and all initial/final frames.

Replacing XOR by ordinary positive integer addition, both old and new
forward blocks have the complete transfer matrix

```text
1 1 0 1 1 1
0 1 1 1 1 1
0 0 1 1 1 1
1 1 1 3 3 2
1 1 0 1 2 1
1 1 1 2 3 3
```

Thus the maps agree over F₂ on six arbitrary independent inputs, including
all dirty contributions. This is stronger than checking only the source
components present at this particular circuit location. The unchanged rest
of `A/scatter/B` consequently has the same complete scalar action. Each XOR
is an involution over F₂, so the regenerated literal `C` restores every
source/helper. `D` remains exactly the same correction. The full word still
maps `(x,s,y)` to `(x,s,y+x)`; both fresh implementations check all 720 columns.
Literal positive-addition cleanup is **not** asserted to be an inverse over
the integers: the inverse statement here is over F₂. The native signed
inverse checks use their original coefficient-sign convention.

For cancellation-free bounds, the reversed positive transfer matrices in
[recipe.json](recipe.json) satisfy `N_new <= N_old` entrywise, with 13 strict
entries. Their row sums are respectively `[9,2,7,5,2,3]` and
`[39,26,13,5,2,5]`. The forward positive matrix is equal. All intermediate
bounds in either replacement block only increase, so each is bounded by
that block's endpoint. At corresponding endpoints the new nonnegative
bound is equal or smaller. Multiplying by the unchanged nonnegative maps
before/after the blocks preserves this order. This proves nonincrease of
the maximum-norm bound, including the reverse word; it does not assume that
fewer gates alone imply a smaller bound. Native replay checks the actual
COPY/erase and stage conventions separately.

Each of the six wires is touched at the same frame, and the preceding and
following frame visits are unchanged. Therefore each full frame path is
unchanged. Exact rational nesting is independently checked. No altered
delivery model, helper lifetime or boundary interface is introduced.

## Complete accounting and scope

| Scalar XOR terms | Original | Candidate |
|---|---:|---:|
| Dirty compensation D | 26,298 | 26,298 |
| A, including all source reads | 3,246 | 3,240 |
| Scatter | 568 | 568 |
| B | 600 | 600 |
| Complete literal cleanup C | 3,246 | 3,240 |
| Total | 33,958 | 33,946 |

The complete local paid profile remains
`H={1:1200, 2:1440, 4:180, 6:120, 8:9}`, rank mass 5,592.
The last term charges all nine full-rank copied totals. Native replay also
checks their nine erasures. No recursive child is removed. The native
record count is 36,916 → 36,904, with all 2,940 MOVEs unchanged.

In the inherited nine-stage/32-replica layout there are 288 local calls.
The scalar delta would therefore be 3,456 additions in the corresponding
emitted program. This is an accounting consequence, **not a freshly emitted
or hosted global receipt**. Under exactly the old ownership/interface
assumptions, the recursive recurrence is unchanged: its complete historical
profile is
`P={1:345600,2:430080,4:67200,6:49920,7:23040,8:2592}`, with `m=64`,
`W=30720`. This profile includes the idle work. The inherited moment test is

```text
M(c) = sum_r [r P_r / (m W)] (m/r)^c
       + [32 m sum_r P_r / (10^16 W)] m^c.
```

Every term, including the bad-branch allowance, is unchanged. The reduced
scalar work affects only a finite overhead constant, so this package claims
neither a higher bit saving nor a higher κ. These historical global numbers
are source-pinned context, not a newly checked global invoice. The selected
#543 word at the original base and the new #741/#589 suppliers are not
replaced or reassembled.

Native finite checks pass for both words: 960 five-stage, 1,440 nine-stage,
and 1,680 eleven-stage columns, with 6/18/24 omitted-bridge controls.
Forward prefix is unchanged at 176,135; reverse prefix decreases from
3,751,204 to 3,751,140. Both payload bounds occupy 102 bits, below the
inherited 104-bit limit. The detailed validation and failed repository-wide
check are recorded in [VALIDATION.json](VALIDATION.json).

Remaining obligations are the inherited all-size compiler, common-label and
mutable-basis realization, whole-call correlated-helper hosting, normalized
residuals, compressed windows/restored work, common grid, precision/tape,
exact recovery and analytic transfer. Full global hosting, the 47 outer
inequalities, remote CI and Lean were not replayed here. Finite certificates
are not a formal proof of the multiplication theorem or a practical-runtime
speedup measurement.

## Provenance and overlap

DreamingOfClouds supplied #503's R480 adaptation and #510's nine-stage
pipeline; eumemic supplied #493's carrier skeleton, generator, mutable-source
checks and frozen plan. Retain their [#503 notice](../e8-r480-dead-totals/NOTICE.md)
and [#493 notice](../e8-bit-carrier-skeleton/NOTICE.md), including Zhihao Chen
(#425/#386), Dylan Crow (#370), DaysSky (#442/#381), chafreaky
(#445/#451/#472/#458), icekylinx, Dugongue, Jacob Sussman and the cumulative
lineage. All original bytes and notices remain unchanged.

@mtpsl’s pending [#691](https://github.com/CrocSwap/integer-mult-bounds/pull/691)
uses the related positive-integer/reverse-domination criterion for **R420
quad 13**. This package independently instantiates that criterion on **R480
quad 1**, with a distinct source, dirty-input map, circuit and receipt.
[#754](https://github.com/CrocSwap/integer-mult-bounds/pull/754) synthesizes
R420 cleanup windows; #789/#790/#810 change R420 phase-B blocks. No pending
implementation is imported or combined here. The ledger marks #503/#510
incorporated and the base-selected #543 bit supplier incorporated;
unreviewed PR titles do not change the selected frontier.

Prepared for **Hao Yan (@FanPUYen)** with substantial **OpenAI Codex**
assistance in synthesis, implementation, independent checking and writing.
The separate implementations were produced by cooperating AI workers;
no independent human peer review is claimed. New work is Apache-2.0.
