# Four-primitive X4 precondition pairs (no new kappa)

The 56 disjoint zero-frame target pairs at the start of the selected PR799
X4 complex program each admit a four-primitive implementation, in both
orientations. This replaces the retained emitter's eleven primitives per
real component and saves **784 real-component primitives per orientation**.
Against optimal *separate* compilation of the three old macros in the stated
two-register alphabet (six primitives), fusion still saves **224** per orientation.

This is a finite scalar circuit construction and a scoped optimality result.
It changes only this research package. The selected construction, certificates,
production emitter, paid recursive profile, and conditional
`kappa = 0.001661634653669567` remain unchanged.

## Reproduce

From the repository root, using only Python 3.9+ and its standard library:

```sh
python3 -B research/x4-precondition-seed22/check.py
```

Expected final line: `PASS_X4_PRECONDITION_PACKAGE no_new_kappa`.
The command checks both exact certificates, the full forward/backward scalar
programs, the independent pair proof/search, and seven source/interface tests.
It writes no repository files. `-I -O` also works. The frozen source archive
already exists in the repository; there is no download or solver dependency.

## Construction and accounting

Writing the two original registers as `(x,y)`, the forward triple is
`x *= -1/2; x += y/2; y -= x`. It maps `(u,v)` to
`((-u+v)/2,(u+v)/2)`. Replace it with:

```text
x -= y; NEG x; HALF x; y -= x.
```

The backward triple computes the inverse transpose: `(u,v) -> (-u+v,u+v)`.
Our integration replay uses:

```text
x -= y; NEG x; DOUBLE y; y -= x.
```

The independent checker uses a different four-letter backward realization
obtained by letterwise inverse transposition, and verifies the same matrix.

| Complete local scalar program | Retained Horner real primitives | Replacement | Saving |
|---|---:|---:|---:|
| Forward | 193,162 | 192,378 | 784 |
| Backward | 193,210 | 192,426 | 784 |

Each ADD reads one other register and writes its target; each NEG/HALF/DOUBLE
is charged once. Both real components are counted. The replacement needs no
copy, new helper, coefficient scratch, frame change, restoration instruction,
or recursive child. Both live targets reach their original pair endpoint, so
the later compensation, adapters, centers, frame changes, wrappers, B word and
cleanup use exactly the same inputs. Each replacement interval uses exactly
its two native target registers. All 112 registers have entrance frame zero.

The retained comparison is implemented literally, including every coefficient
work clear, signed accumulation and shift. Its count agrees with the archived
`LOCAL-CHECKS.json` in both orientations. The six-operation comparison uses
two operations for the signed scale, three for a half-add by target dilation,
and one unit add; the independent BFS proves each separate macro minimum.
No additivity with other pending lowering proposals is assumed.

## Proof, completed search and verification scope

[PAIR-PROOF.md](PAIR-PROOF.md) gives an elementary four-operation lower bound:
the negative dyadic determinant requires a NEG and a scale, and the dense
matrix requires at least two ADDs. Its scope is exactly two live registers,
unit-cost signed unit ADD, NEG, HALF and DOUBLE, without scratch or a free swap.
It is not a lower bound for other instruction sets or the full supplier.

`independent_checker.py` uses a separately written dense Fraction-matrix engine,
imports no integration code, and verifies every word through length four in
the ten-instruction alphabet: **11,111 words**, no coefficient pruning, exactly
eight shortest words per orientation. A separate state-deduplicated BFS agrees.
Seed 22 was drawn from OS randomness; the exhaustive search itself is deterministic.
The stopping rule is length four, where explicit witnesses meet the analytic bound.

`verify.py` independently expands the retained Horner macros and the replacement
into real primitives, then replays both complete local scalar projections with
exact sparse rational rows. It checks **737 formal columns per orientation**:
728 native registers (including arbitrary dirty helpers), eight independently
dirty center cells and one dirty coefficient-work cell. It verifies every pair's
native endpoints, the complete program endpoints, and final clearing of all
private cells. The fused pair does not use the work cell and can leave its old
dirt untouched; the unchanged suffix clears it before use. Pair-boundary equality
is asserted on native registers, not on that eliminated private scratch cell.

All phase/event boundaries outside the first 168 scalar macros are retained.
The unchanged suffix is hashed. The retained paid profile is
`{1:2548,2:338,3:430,4:194,5:56,8:8}`. All 672 instruction-deletion/sign mutants
across 56 pairs and two orientations fail the exact pair identity. Separate
tests reject altered coefficients, nonzero entrance frames, overlapping or
missing pairs, changed source bytes and omission of a dirty-work clear.

## Precision: local increase, unchanged complete scalar budgets

Every shortest forward realization raises the isolated prefix row-l1 maximum
from **1 to 2**. This is an actual intermediate growth requirement, not a
rounding-free implementation claim. The backward isolated maximum stays 2.
The full literal primitive replays give:

| Exact scalar prefix metric | Retained | Replacement |
|---|---:|---:|
| Forward maximum row-l1 | 525,312 | 525,312 |
| Backward maximum row-l1 | 5,338,828 | 5,338,828 |
| Forward maximum binary denominator exponent | 3 | 3 |
| Backward maximum binary denominator exponent | 19 | 19 |

These metrics include private scalar rows and every primitive prefix. They
bound exact linear growth and exact grid representability in the scalar
projection. They do **not** evaluate physical phase/frame/recursive operations,
roundoff accumulation or the full inherited precision/tape theorem. Those
obligations, all-size compilation, common-label/mutable-source realization,
whole-call hosting and analytic transfer remain inherited. No full Lean
multiplication theorem, practical runtime improvement or new kappa is claimed.

## Provenance and nearby work

Base commit: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
The selected record points to Jeremy Kothe's PR799, pinned at
`80e6463157cfc80b85af09e7e2f14748fe2dac60`, with Chafik Boukhalfa's PR741
(`e516b1463606840a15f80aac1995d64ce0092e89`) and DreamingOfClouds' PR589 bit
supplier on eumemic's PR555. The consumed input is the **actual integrated X4
replay**, not the historical 492-helper `evidence/local` copy retained inside
the package. Archive/member hashes and contextual source pins are in
[SOURCES.json](SOURCES.json); [RESULT.json](RESULT.json) records consumed payloads.
The entire source archive is an immutable input; generated result JSON is
compared structurally, independent of compressed container bytes.

Credit icekylinx's PR425 target-butterfly/emitter lineage, Jeremy Kothe and the
X4/SW4 contributors, Chafik Boukhalfa, DreamingOfClouds, Rohan Arun, eumemic and
the predecessor notices retained in the repository. This work makes no
priority claim for the elementary butterfly or scale-commutation identities.

Related pending work was checked at pinned heads:

- [Sagar Thakrar's PR750](https://github.com/CrocSwap/integer-mult-bounds/pull/750),
  `b6d6934092c063ab2575ebee00f48bbc7b1c9d82`: historical CK cleanup scale relocation.
  This package synthesizes the selected X4 zero-frame three-macro blocks.
- [Gareth Davidson's PR837](https://github.com/CrocSwap/integer-mult-bounds/pull/837),
  `0a2977195efc8fb2a918fbfb694ec8d294387f08`: within-macro Horner lowering,
  following Sagar Thakrar's PR696/723 and Chris Pagolu's PR734. Our factorization
  crosses three macro boundaries and does not import their pending implementation.
- [PR866](https://github.com/CrocSwap/integer-mult-bounds/pull/866),
  `5ae580bf68516f1cbe3b2dd3cb646be55170288f`: exact fractional-grid audit motivating
  an explicit check of intermediate denominators as well as endpoints.
- PR840 concerns native BIT query fusion; PR864 fixes the X4 scalar word while
  optimizing frames. Neither analyzes this scalar pair factorization.

Prepared by **Philipp (@mightyOil)** with substantial **OpenAI Codex assistance**,
including separately implemented AI-assisted pair verification and review.
This is not independent human peer review. New files are Apache-2.0 under the
repository license. No predecessor files, source archives or notices are edited.
