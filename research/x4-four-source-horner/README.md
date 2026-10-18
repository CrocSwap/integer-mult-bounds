# Four-source Horner work in historical X4

**Finite complex-supplier scalar construction; no new kappa.** Sharing one
coefficient-work stream across up to four consecutive source additions saves
**8,976 more backward real-component primitives than PR945's pair-only
construction**. The complete backward scalar projection costs **121,626**,
down from 143,674 under PR696 and 130,602 under PR945.

The forward orientation is unchanged at 143,658 and binds the maximum.
Consequently the orientation maximum receives **no additional improvement
beyond PR945**. This is useful finite circuit evidence, not a better selected
supplier, global invoice, runtime result or recurrence exponent.

| Complete scalar projection | PR696 | PR945 pairs | This recipe |
| --- | ---: | ---: | ---: |
| Backward real-component primitives | 143,674 | 130,602 | **121,626** |
| Forward, retained | 143,658 | 143,658 | 143,658 |
| Maximum over orientations | 143,674 | 143,658 | 143,658 |

The old pre-PR696 backward count is 193,210. PR696's savings are credited to
Sagar Thakrar and are not counted again as new. The pair and four-source
recipes are alternatives; their savings must not be added together.

## Reproduce

Run from the repository root with Python 3.11+ and its standard library:

```sh
python3 -I -B research/x4-four-source-horner/verify.py
python3 -I -B research/x4-four-source-horner/independent.py
python3 -I -B research/x4-four-source-horner/test_package.py
```

Expected primary result:

```text
PASS_X4_FOUR_SOURCE_HORNER candidates=16431 windows=1174 saved=22048 extra_vs_pairs=8976 columns=737 no_new_kappa
```

The primary command recomputes the entire census, selection and both complete
backward primitive traces; it also invokes the separate integer implementation,
which checks the retained forward trace. The independent command imports
neither the constructor nor its Fraction replay. Both commands work with `-O`,
use no network or solver, and leave their inputs unchanged. `--json` prints
the checked receipt. `verify.py --emit /absolute/new-file.json` saves the exact
complete backward primitive event stream and refuses an existing destination.

## New mechanism and complete coverage

PR945 uses two-source binary Horner words. The new words jointly prepare three
or four dyadic source terms in the same existing private stream, sharing the
shifts, accumulation and final clear. Each source remains unchanged, every
read is charged, and the first COPY handles arbitrary incoming private dirt.
There is no additional helper, frame transition or recursive child.

A concrete four-source window costs **7** primitives per real component.
Every partition of those four terms into singletons and pairs costs at least
**9**, even after discounting all intermediate clears. This establishes a
strictly larger circuit class, not just more computation in the closed pair
class. [PROOF.md](PROOF.md) gives the literal event indices and full argument.

The domain is every consecutive length-2/3/4 ADD window in the pinned PR799
backward program with one target, distinct immutable sources and an identical
nonzero frame. It contains **6,112 pairs, 5,455 triples and 4,864 quartets**.
Of these, 9,652 beat removal of redundant clears alone. Exact interval DP
selects 1,174 disjoint windows: 58 pairs, 147 triples and 969 quartets. This is
optimal only among those admitted windows with PR696 lowering elsewhere.
The search completed its entire domain and stopped. Longer windows, source
reordering, repeated-source aggregation, signed-digit words and arbitrary
circuits are outside scope.

Two implementations check all 16,431 candidate identities and agree on every
cost record. A suffix DP and a separate prefix DP establish the same optimum.
Their tie policies differ; the receipt distinguishes the independent chosen
window count from the published recipe. The independent engine then checks
the published recipe's optimality and literally emits the same full stream:

```text
d95c2ce750263e09c1051dad011e0bb436b696424e8d98513efba09908d757a3
```

[EXPECTED.json](EXPECTED.json) includes the complete recipe, census and stream
digests, counts, prefix bounds and separate-engine receipt. [SOURCES.json](SOURCES.json)
pins nine inherited files to the exact base by SHA256 and Git blob ID, and
records PR945's source head. No pending code is imported or executed.

## Verification and interface limits

Both exact engines replay all **737** independent input columns: 728 logical
registers, eight private centers and coefficient work. They check every
selected window boundary, the complete signed shear, all 504 dirty-helper
restorations and erasure of all nine private inputs.

The backward exact maximum row L1 norm remains **5,338,828** and maximum
fractional denominator exponent remains **19**. The positive scalar envelope
also remains **48,299,247,699,832,632,898,063 / 16**. These are different bounds;
the proof does not assume that every joint intermediate matches an old one.
Nonwork source reads remain 19,723 per real component; total arithmetic
operand reads fall from 73,196 to 65,431. These are syntactic counts, not a
physical memory-access invoice.

Nine independent adverse controls and seven package test groups cover dirty
work, signs, denominator alignment, frame/source aliases, suboptimal and
overlapping recipes, a valid but suboptimal greedy circuit, corrupt pins and
receipts, and minimal offline optimized replay. The baseline lowerer is
compared with retained PR696 on every one of the 38,394 source macros.
See [VALIDATION.md](VALIDATION.md) for executed checks and environment.

Non-scalar events and their paid profile are retained literally, but these
interpreters do not execute the physical frame, phase or Clifford operations.
Work clears at a joint-window boundary rather than every old macro boundary;
typed production integration and fresh native/hosted admission remain undone.
Uniform compilation, common-label/mutable-source realization, whole-call
hosting, rounding/precision/tape and analytic transfer remain inherited
obligations. No full repository suite, selected cold replay, formal theorem
proof, global invoice or hosted CI success is claimed.

## Provenance

Exact base: `007664306fff84fbb1c9a1b4053b69f439764034`.
OS assignment seed **22**, complex supplier. The selected result at that base
is PR890's conditional kappa **0.001661957774647029**, left unchanged. The
historical X4 program is deliberately the object here. [CLAIM.md](CLAIM.md)
records candidate selection, overlap checks, timing and stopping rule.

At the final refresh, main `bbc600db2fc15007b7c914f4f2b2ed55fa909c87`
selected PR942 U8/T37 at conditional kappa **0.001661960547713947**.
All nine historical inputs remain byte-identical there; this contribution
does not change that selection. See [VALIDATION.md](VALIDATION.md).

Credit **Ross Richardson's PR945** (`a3245bf22fa2a2eb778b11128cbc605b130d737f`)
for the shared pair-Horner mechanism and comparator, **Sagar Thakrar's PR696**,
**Jeremy Kothe's PR799**, **Chafik Boukhalfa's PR741**, icekylinx and the
retained construction lineage. PR751/830's JP8 fan-in work supplies related
precedent; no first-invention claim is made for joint Horner arithmetic.

Prepared for **ToikY with substantial OpenAI Codex assistance**, including
separate implementation and mathematical review. No independent human review
is claimed. Apache-2.0; see [NOTICE.md](NOTICE.md).
