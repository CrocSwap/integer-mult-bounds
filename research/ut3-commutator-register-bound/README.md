# Two UT3 commutators require eight paid calls with at most one dirty extra

**Scoped computer-assisted result; no new kappa.** In the formal model below,
the exact cost of `diag([c],[c])` and `diag([c],[c],1)` is eight. Free scalar
register mixing and one arbitrary restored dirty register do not improve the
direct four-plus-four construction. This answers one three-dimensional instance
of the restricted-coordinate-alphabet question in Gareth Davidson's
[PR1333](https://github.com/CrocSwap/integer-mult-bounds/pull/1333) and the second
open question of commdata2338's
[PR1414](https://github.com/CrocSwap/integer-mult-bounds/pull/1414).

This is a finite formal-algebra boundary result, not an admitted multiplication
supplier. The address alphabet is different from the rational additive frames
of the root three-register theorem. No rational frame entry is reduced modulo two.

## Model and complete bill

Let `G=UT_3(F2)` consist of upper unitriangular three-by-three binary matrices.
Write an element as `(x,y,z)` for entries `01,12,02`. Its product is
`(x,y,z)(X,Y,Z)=(x+X,y+Y,z+Z+xY)` over F2. Set

```text
a = I+E01, b = I+E12, c = abab = I+E02.
```

The group has eight elements; a and b are involutions and c is a central
involution. Work in the **full formal group algebra** `R=F2[G]`. For exactly
`r=2` or `r=3` registers, each paid unit is

```text
D_N(g) = I + ([g]+1)N,  g in {a,b},
N = xy^T over F2, x,y nonzero, y^T x = 1.
```

All scalar `GL_r(F2)` changes are free. There are no additional free address
maps, clean allocations, copies, erasures, higher-rank paid calls or free undo
operations. The endpoint is equality of every formal coefficient to
`T_r=diag([c],[c],1,...,1)` on arbitrary inputs; the third role, when present,
must be returned identically. The direct word uses `(a,b,a,b)` on the first
coordinate projector followed by the same four labels on the second. Its
complete bill is eight paid calls, two data roles and zero or one dirty extra,
with no scalar mixing needed. Both engines check this word exactly.

Free scalar normalization uses PR1333's augmentation argument: move all scalar
maps to one end, conjugating each projector as necessary. Augmentation sends
every paid factor and the target to I, so the remaining scalar map must be I.
Conversely, every binary rank-one idempotent is conjugate to a coordinate
projector (use its image and kernel as a basis). Thus the enumerated alphabet
covers all allowed interleaved scalar mixing.

## Lower-bound argument and exhaustive coverage

**Parity lemma (any finite register count).** The character `chi(x,y,z)=x+y`
is a homomorphism `G -> C2`, with a,b sent to its generator t and c to 1.
In `F2[C2]=F2[epsilon]/(epsilon^2)`, t=1+epsilon. The image of a paid factor
is `I+epsilon N`. By the rank-one determinant lemma its determinant is
`1+epsilon trace(N)=1+epsilon`, since `trace(xy^T)=y^T x=1`.
The target's image is I, so `(1+epsilon)^k=1`; k is even. This excludes every
odd length, including seven. This parity statement alone is not an eight-call
lower bound for arbitrary register count.

**Finite even-length exclusion (r=2,3 only).** Every generator is involutory,
because `N^2=N` and `g^2=1`. Enumerate the exact radius-three ball `B3` from I,
deduplicating by the complete formal matrix and retaining minimum distance.
Any word of length at most six can be split as `PQ` with both lengths at most
three. If `PQ=T_r`, then `P=T_r Q^{-1}` and hence `B3 intersect T_r B3` is
nonempty. Both enumerations find that intersection empty. Together with parity,
this excludes every length below eight. The direct word attains eight.

| r | Dirty extras | Generators | Distance layers 0,1,2,3 | Ball size | Target intersection |
|---|---|---|---|---|---|
| 2 | 0 | 12 | 1, 12, 80, 472 | 565 | 0 |
| 3 | 1 | 56 | 1, 56, 1750, 45424 | 47231 | 0 |

The first implementation enumerates all outer products with `y^T x=1`, stores
eight formal coefficients per entry and right-multiplies using the triple
group law. `independent.py` imports none of that implementation: it constructs
three-by-three address matrices, enumerates every binary scalar matrix to find
rank-one idempotents, and multiplies ordinary binary matrices of dimensions 16
and 24 in the faithful right regular representation. **Entire state sets and
minimum distances agree**, including all 1,116 and 101,192 transition attempts
in the second engine. Faithful decoding also reconstructs each complete regular
matrix, rather than comparing only a natural three-dimensional image.

`EXPECTED.json` records deterministic receipts. Hashes concatenate the sorted
formal states, each encoded as r*r bytes in row-major order, one eight-bit
coefficient mask per entry; group index is `x+2y+4z`. The hash is a compact
receipt, not a substitute for the full state-by-state comparison.

The 37 controls include all eight single-call omissions for both register counts,
wrong labels, invalid scalar projectors and expanded address labels, involution
and quotient checks, dirty leakage/restoration faults, and a nonregular matrix
mutation. Identity and a single-commutator target have independently recovered
minima zero and four. A nonzero formal sum of all eight group elements vanishes
in the natural three-by-three representation but survives the regular one:
natural matrix equality cannot certify formal equality here.

## Reproduce and observed verification

Python 3.12+ and the standard library suffice. From the repository root:

```sh
python3 -I -B research/ut3-commutator-register-bound/verify.py
python3 scripts/research_package.py --package research/ut3-commutator-register-bound --check-only
# The registered hook requires Python 3.12:
python3.12 scripts/research_package.py --package research/ut3-commutator-register-bound
```

Expected final line:

```text
PASS_UT3_COMMUTATOR_REGISTER_BOUND minimum=8 registers=2,3 dirty_extras=0,1 no_new_kappa
```

`--emit` prints a fresh receipt without modifying files. The replay is read-only
and uses explicit checks under Python's optimized mode. `VALIDATION.md` records
the measured runs, environment, relocation and corruption controls. The generic
hook runs the complete bounded census, with no skipped larger census.

## Task, sources, overlap and limitations

Base main: `410026dc5513b87db92ae98571d1d5984c69a983`; task
`bit-new-register-model`, scope key `7084092dd726e7ba1f2f`, priority revision 2,
chooser nonce `d556c3c1fbf3d1a397fbb6604c6f5772`. The broad assignment is refined
to this fixed group, alphabet, target and register count. Claim and updates:
[Discussion1317](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-18912406).
`TASK.json` preserves the original card and structured next questions;
`SOURCES.json` pins the base and contextual input.

Immediate research leads: Gareth Davidson (@bitplane), PR1333 head
`7f25b6d0e1d7e995d4d2840f231d98b1a1a9fec2`; commdata2338, PR1414 head
`9e1640094f649ba6db9742796825a8d6c238989b`. Their S3 coordinate-swap model and
this D8 central-commutator model have different groups and targets. No pending
implementation is imported. The local overlap helper searched 326 records,
with two contextual matches and no usable remote snapshot. Live PR and
Discussion searches were checked at entry and before submission; coverage is
incomplete and no novelty or literature-priority claim is made.

This does not exclude improvements with two or more extra dirty registers,
different targets, a larger address alphabet, or other primitive prices. It does
not prove a rational-frame identity, physical compiler/hosting feasibility,
precision/tape or analytic transfer, or a new kappa. The full selected-supplier
cold replay was not run. The prescribed orientation baseline was attempted but
could not validate its complete source inventory in this sparse checkout;
large archived supplier inputs are absent. This package consumes no supplier
data and makes no selected-source acceptance claim. The result is not Lean
verification or independent human proof review.

## Open next questions

1. **Two additional dirty registers.** Does r=4 admit a six-call word for the
   same two targets, or is eight still minimal? This would test whether the
   obstruction scales with workspace. First enumerate the 120 rank-one
   idempotents and a radius-three ball with packed formal states. The blocker
   is a substantially larger census; the present r=3 proof does not imply r=4.
2. **An all-register coefficient obstruction.** Can six paid a/b factors be
   excluded without fixing r? This would replace the finite register boundary
   with a structural theorem. First classify the 64 length-six label patterns
   and derive rank constraints on the c coefficient under the identity of all
   other coefficients. Noncommuting scalar products and cancellations are the
   blocker; parity alone is insufficient.

## Credit and license

Prepared for @juper997 with substantial OpenAI Codex assistance (research,
implementation, checking and writing). No subagents were used. Credit Gareth
Davidson for the affine/restricted-alphabet question and augmentation
normalization; commdata2338 for the adjacent coordinate-swap investigation and
faithful-census approach; eumemic (PR288), Ali Romman (PR468) and David Govea
(PR720) for the register-model lineage. The root abelian bound and all source
notices remain unchanged. New work is licensed Apache-2.0.
