# R439 frame 509: 21 ADDs become 20

**Independent finite bit-circuit construction; no new κ.** One Boolean cancellation
shortens Cinna Davis's reviewed PR973 block from 21 to 20 ADDs. Paying the
literal reverse cleanup saves two complete local ADDs beyond PR973, or 22
against the selected PR589 word. No helper, source access, frame adapter,
COPY or recursive child is added. All eleven block inputs, including helper
468, are arbitrary.

Concurrent **PR1208 uses the same local cancellation and also reaches 20**
on the composed PR1122 word. This package independently realizes it on the
reviewed PR973/selected PR589 lineage, preserving the original H1–H5 and
`K_equals_D` without a changed D interface. No priority or ADD-count record
is claimed.

| Complete local quantity | Selected PR589 | Reviewed PR973 | This candidate |
|---|---:|---:|---:|
| Frame-509 B ADDs | 31 | 21 | **20** |
| All ADDs, including D, scatter and C | 24,305 | 24,285 | **24,283** |
| Exported records | 27,234 | 27,214 | **27,212** |
| MOVEs / COPYs / ERASEs | 2,911 / 9 / 9 | same | same |
| Paid rank mass | 5,129 | 5,129 | 5,129 |
| Positive forward envelope F | 49,347 | 49,347 | 49,347 |
| Positive reverse envelope B | 1,113,070 | 1,106,918 | 1,106,918 |
| Sufficient local / nine-stage bits | 93 / 177 | 93 / 177 | 93 / 177 |
| Charged local / nine-stage bits | 104 / 192 | 104 / 192 | 104 / 192 |

The unchanged paid profile is
`{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}`. This is a scalar circuit
saving, with no improvement to the recursive moment. At base
`1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`, the selected conditional κ is
`836330098538459/500000000000000000`; the complex supplier binds.

## Reproduce

From the repository root, Python 3.11+ and the standard library:

```sh
python3 -I -B research/r439-b509-boolean-seed05/verify.py
python3 -I -B research/r439-b509-boolean-seed05/test_package.py -v
```

Expected verifier marker:

```text
PASS_R439_B509_BOOLEAN gates=31/21->20 ADDs=24305/24285->24283 columns=661 truth_table=2048 H1-H5 controls=27 no_new_kappa
```

For the unchanged C++17/Boost legality and 5/9/11-stage column checkers:

```sh
BOOST_INCLUDE=/path/to/boost-headers python3 -I -B research/r439-b509-boolean-seed05/native.py
```

Expected: `PASS_R439_B509_BOOLEAN_NATIVE words=3 columns=883/1327/1549
bridge_controls=144 five_stage_regression=PASS`. `CXX` selects the compiler.
On systems with Boost under `/usr/include`, `BOOST_INCLUDE` can be omitted.
`--output /absolute/new/directory` retains generated words and logs; existing
destinations are refused. `--write-expected` is an explicit development option,
not the reproduction command. Decoded candidate fields and deterministic
receipts are compared, not regenerated gzip container bytes.

## Exact identity and splice

Use the original eleven physical registers
`[17,22,33,38,50,60,67,77,87,92,468]`, all at frame 509 for this block.
In PR973 gates `[7:11]`, set `a=x33`, `b=x38`, `h=x468`, `c=x77`.
Replace the left program by the right:

```text
old (4 ADDs)             new (3 ADDs)
b ^= a                   h ^= b
h ^= a                   b ^= a
c ^= a                   c ^= a
h ^= b
```

Over F₂, both endpoints are exactly

```text
(a, b, h, c) -> (a, b + a, h + b, c + a).
```

This holds for arbitrary incoming values; the old helper update is
`h + a + (b + a) = h + b`. Over the integers, the old block map minus the
new block map is **`2 e_468 e_33^T`**. Integer equality is explicitly false;
the test over F₃ rejects it. The replacement is therefore outside PR973's
integer-map-preserving search class.

Before and after this four-gate window the block is unchanged. The selected
word's `B[283:314]` is replaced by the resulting 20-gate block. C is rebuilt
as the literal reverse of all z-destination A/B gates, at the full frame.
Equality of the F₂ block operators preserves every subsequent observation,
including arbitrary helper dirt. No frame path changes. This argument proves
the local identity; the complete finite checks below bind it to this word.

## Evidence and boundaries

The checker independently executes all eleven block columns and all 2,048
Boolean inputs, checks the exact integer-map difference, and compares all 661
ordered register frame paths. A set-valued interpreter replays all 661 dirty
columns in both directions for the three words. It checks each COPY/ERASE
lifetime and recomputes both positive envelopes. A separate packed-column
replay checks the original exporter's literal stream and complete invoice.
The unchanged E8 checker verifies H1–H5 and all four interface conclusions.
The nine-stage bound `2^18 F^5 B^4` is bound to the pinned compiler expression.

All three words pass fresh native 5/9/11-stage checks, with 883/1,327/1,549
formal columns per stage count and 144 distinct omitted-bridge controls.
The 27 local controls include every single block-ADD omission, a missing
helper restoration, stale cleanup, unpaid frame descent, COPY corruption and
an F₂-identity insertion that exceeds the precision charge. Ten package tests
cover relocated optimized replay, corrupted source, an underbilled receipt,
existing-output preservation and the characteristic-two restriction.
The 14 existing selected-record and finite-bit-contract tests also pass.

This does not establish a minimum circuit, a practical speedup, a new κ,
hosted-supplier admission, or the full multiplication theorem. No selected
cold replay or hosted emission/owner/invoice/assembly is claimed. The
all-size compiler, mutable-source/common-label realization, whole-call
hosting, precision/tape, recovery and analytic assumptions remain inherited.
Remote CI and human independent review are separate from these local checks.

## Provenance and overlap

`SOURCES.json` pins every consumed source by SHA-256 and Git blob, including
PR973 at `c05dc72734c25dd069077157224d4dd30c6e8c19`. The selected bit source
is DreamingOfClouds' PR589 on eumemic's PR555. `CLAIM.json` records OS seed
**5**, the alternatives, bounded experiments and stopping rules.

The broad greedy and pivot-elimination samples each completed 10,000 trials;
both found at best 23 ADDs. They are failed finite searches, not exclusions.
The delivered witness comes from the displayed algebraic identity applied to
PR973. `EXPLORATION.json` records both samples and `CLAIM.json` records the
one count extension and the rejected development prototype.

Aaron Wang's pending PR1127 at `2e9dc9d3356a6b7258ed869ddcee46352907f746`
uses the related triangle identity on the original selected word. Its
frame-509 block has 22 ADDs and the same F₂ map; the extracted comparison is
in `OVERLAP1127.json`. This contribution applies that identity family to the
already factored PR973 block and reaches 20. No full-word composition or
addition of independent PR savings is claimed. PR1015 independently reached
21 for this block; PR1062/1122/1188 change other complete words and remain
separate. The identity family predates this contribution.

The final overlap refresh found ToikY's PR1208 at
`24c45725f7b9ffca4529b46661acf343ce93cee3`. Its sole B rewrite uses the
same three operands `33,38,468`. `OVERLAP1208.json` preserves its 20-gate
block and exact provenance. The two block programs have the same integer
and Boolean endpoints but different literal orders. This independently
corroborates the local mechanism; the additional evidence here covers the
original H1–H5 interface and all three selected/PR973/candidate words.
The composed semantic-D construction's inherited H2/K flags are outside
this package's claims. No PR1208 full-word replay is claimed.

Prepared by **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex
assistance**. New material is Apache-2.0. See `NOTICE.md` for predecessor and
implementation credit.
