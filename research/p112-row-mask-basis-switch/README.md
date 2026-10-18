# Arbitrary row masks cannot make two-coordinate P112 basis switching cheaper

**Scoped proof with exact finite premises; no new kappa or physical supplier.**
For any two of the eight P112 coordinates, any invertible complex 2-by-2
basis change, and any subset of the 112 source rows, switch to the dual
basis only on that subset. The complete separate COPY rank sum stays at
least **64**. More strongly, for every `0 < theta <= 1`, its COPY power
bill is at least **8 * 8^theta**. Both bounds are attained by the empty mask.

This handles **every one of the 2^112 masks**, without enumerating them.
It narrows the coupled rank-two opening of Philipp / mightyOil's
[PR1197](https://github.com/CrocSwap/integer-mult-bounds/pull/1197).
The two added sources need not belong to the root code: an exact fixture has
`rank([X Z])=10`, hence two independent outside-code source directions.
This does not settle arbitrary two-total sources.

## Model and endpoint

Use the pinned PR845 P112 geometry. `X` is the real 112-by-8 coordinate
matrix with entries in `{0,1,-1}`, `X^T X=56I`, and `XX^T=2G`.
The binary pairing is `P_ij = 1 + G_ij (mod 2)`. Define

```
beta(d,t) = rank_F2 P[support(d), support(t)].
```

The eight coordinate terms each cost eight. Fix `p<q`, put `C=[x_p x_q]`,
choose `A in GL(2,C)`, and let `M` be any diagonal 0/1 row selector.
Replace the two coordinate terms by four separate terms with readers and sources

```
old readers: C              old sources: (I-M) C
new readers: C A            new sources: M C A^{-T}.
```

All transposes are ordinary transposes. Direct multiplication gives

```
C ((I-M)C)^T + (CA) (M C A^{-T})^T
  = CC^T(I-M) + CC^T M = CC^T.
```

The six other coordinate terms remain. Every nonempty old/new term is
charged; a zero source costs zero. There is one fixed basis `A` on the
selected rows and the original basis on the complementary rows.

## Proof

### 1. Eleven support cases cover all complex bases

For a nonzero direction `(a,b)`, the support of `a x_p+b x_q` depends only
on which of these five projective classes it occupies:

| Class | Representative | Condition |
|---|---|---|
| p axis | `(1,0)` | `b=0` |
| q axis | `(0,1)` | `a=0` |
| plus | `(1,1)` | `a=b!=0` |
| minus | `(1,-1)` | `a=-b!=0` |
| generic | `(1,2)` | all other nonzero directions |

This is exhaustive over **complex** coefficients: with both row entries
nonzero, cancellation requires `a/b=+1` or `-1`; with exactly one nonzero
entry it requires the corresponding coefficient to vanish. Rows with both
entries zero vanish in every class.

Write the columns of `A` as `a=(a0,a1)` and `b=(b0,b1)`. Up to their common
nonzero determinant, the columns of `A^{-T}` are `(b1,-b0)` and
`(-a1,a0)`. Thus their supports also depend only on the two reader classes,
not on coefficient magnitudes or phases. Column order and nonzero column
rescalings do not change the bill. Two columns in the same nongeneric
class would make `A` singular. There are therefore ten unordered distinct
class pairs and one generic/generic pair; the latter is represented by
`(1,2),(1,3)`. This reduces all `GL(2,C)` bases to **11 support cases**.

### 2. Balanced common independent-set certificates

For each of the 28 coordinate pairs and 11 support cases,
[CERTIFICATE.json](CERTIFICATE.json) gives sixteen units `(i,j,k)`, where
`i` is a source-row index and `j,k in {0,1}` select an old and a new term.
Each unit satisfies:

1. The old unmasked source `C_ij` and new unmasked source
   `(C A^{-T})_ik` are nonzero.
2. For each old term `j`, exactly eight assigned units have linearly
   independent binary columns `P[support(C_j), i]`.
3. For each new term `k`, exactly eight assigned units have linearly
   independent binary columns `P[support((CA)_k), i]`.

There are 308 certificates, 4,928 units and 1,232 independent eight-column
groups. A port may occur in different groups. Repeated/dependent columns
within a group are rejected. These are explicit finite facts, checked
both by nine-bit label projections and by independently reconstructed
full binary pairing columns.

Now fix an **arbitrary** mask. Route each unit to its old term when
`i` is outside the mask, and to its new term when `i` is inside. The chosen
column occurs in that term's actual source support by condition 1.
Any subset of an independent group is independent. Consequently the four
actual ranks `r_t` dominate four integer routed counts `c_t` satisfying

```
r_t >= c_t,       0 <= c_t <= 8,       sum_t c_t = 16.
```

Every unit is routed exactly once. If several units have the same row,
the same mask decision routes them all; the proof does not assign separate
masks to different occurrences of one row. It follows that `sum r_t>=16`.
Adding the six unchanged rank-eight terms proves the COPY floor 64.

### 3. The same certificates prove the power floor

For `0<theta<=1`, monotonicity and the chord below the concave function
`x^theta` on `[0,8]` give

```
sum_t r_t^theta >= sum_t c_t^theta
                   >= 8^(theta-1) sum_t c_t = 2 * 8^theta.
```

Add the other six terms. This proves `sum_all r_t^theta >= 8 * 8^theta`.
Taking the empty mask gives ranks `(8,8,0,0)` on the replaced block, so
both bounds are sharp. No classification of every equality case is claimed.

The balance condition is essential for this argument: a rank-sum floor
alone permits `(9,7,0,0)`, whose square-root sum is less than `2sqrt(8)`
because `9*7=63<64`. That is an arithmetic failure control, not a decoder.
The general certificate-routing/chord argument uses ordinary linear
algebra and concavity; the contribution is its source-bound application
and complete witnesses for this decoder family.

## Verification and reproduction

Python 3.12, standard library, from the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/p112-row-mask-basis-switch
```

The explicit [VERIFY.json](VERIFY.json) replay runs:

- `verify.py`: all 308 certificates and 12,544 geometry pairings, 42 exact
  integer/Gaussian-integer endpoint fixtures (526,848 changed-block entries),
  489 balanced count vectors, and ten controls/boundary checks.
- `independent_check.py`: a separate 120-root enumeration and 112-root
  pairing matrix from Euclidean products, full-column set elimination for
  every group, 17,472 Gaussian-coefficient support controls, three controls.
  It imports no primary or predecessor code. It shares the pinned row
  ordering and certificate witnesses; it does not independently prove the
  all-complex support reduction or universal routing argument.
- `test_package.py`: five groups covering missing strata, duplicate and
  dependent units, support incidence, balance, Boolean/numeric aliases,
  receipt/source corruption, no-overwrite behavior, deterministic certificate
  regeneration, and optimized execution from a renamed read-only copy.

The primary pass marker is `PASS_P112_ROW_MASK_BASIS_SWITCH`.
The separate replay prints `PASS_P112_MASK_INDEPENDENT`.
[RESULT.json](RESULT.json) is compared in full with type-sensitive canonical
JSON. Both checkers keep their guards under Python `-O`.
To reconstruct the witness certificate in a new file:

```sh
python3.12 -I -B research/p112-row-mask-basis-switch/build_certificate.py --output /tmp/new-mask-certificate.json
```

The generator tries only two deterministic shuffled greedy orders per
case; every candidate is then checked exactly. Discovery is not an
exhaustive optimizer and supplies no exclusion claim. The proof uses the
positive certificates, not a failed search. `verify.py --write NEW_PATH`
creates a new receipt without overwriting an existing one.

## Budget and limitations

At the same width and normalization, take `theta=1-a`, `0<=a<1`.
This COPY component cannot improve even if all preparation, frame changes,
restoration, hosting and precision costs are granted zero. Any added
nonnegative costs only increase that bill. This is a completed algebraic
screen, **not** a complete physical invoice or a proof that every other
component of a new implementation cannot improve.

The scope requires the two old coordinate readers, one fixed new basis,
the exact dual new sources on one common row mask, six unchanged coordinate
terms, and the inherited separate-total COPY interpretation. Independent
source masks, arbitrary source corrections, more than two mixed coordinates,
multiple new bases, changed labels, masked-only equality and interacting
delivery circuits are outside it. Physical arbitrary-dirty restoration is
not supplied by this scalar identity.

No new kappa, supplier admission, native/hosting replay, selected cold
replay, all-size/compiler result, precision/tape or analytic transfer,
Lean proof or independent human review is claimed. The selected record
and all frozen predecessors are unchanged. The original revision-3
5% physical block-climb acceptance gate is **not satisfied**.

## Assignment, provenance and overlap

Base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`, selected #1094 at
`0.001672660197076918`. One OS draw
`b753af53242f8a79a9032531c8f15c54` selected complex mechanisms.
[TASK.json](TASK.json) declares the changed scope and one bounded narrowing
from arbitrary four-ray sources to this common-mask family. The original
arbitrary-source question remains open. Coordination is
[Discussion1737](https://github.com/CrocSwap/integer-mult-bounds/discussions/1737).
[SOURCES.json](SOURCES.json) binds the selected/catalogue provenance and
the live geometry and predecessor proof bytes by Git blob and SHA256.

The initial complete remote snapshot covered 415 open PRs including drafts
and 365 Discussion records; the pivot refresh covered 418 and 371.
Local top-level package notes and the PR ledger were also searched.
This coverage excludes arbitrary nested code and is not a novelty certificate.
Final refresh details belong to the validation receipt.

Nearest scopes: PR1197 leaves arbitrary coupled rank-two sources open;
this settles one such family. Denis / just-mn's
[PR1689](https://github.com/CrocSwap/integer-mult-bounds/pull/1689), exact head
`f87724057cc5fc5192fe2904675a563273612851`, uses complementary Walsh masks
and arbitrary real reader coefficients. Here a common arbitrary mask uses
the exact dual sources and arbitrary complex bases; neither contains the
other. Sagar Thakrar's PR1327 changes both factors in a parity-lift family.
PR1180 requires both factors in the root code; the rank-ten fixture here
shows that restriction need not hold. PR1633 gives general excess-rank
constraints, not this support-cost bound.

## Open next questions

- **Independent masks or arbitrary sources for the fixed four rays.** This
  would address more of PR1197's residual class. Start from
  `T=C-Z A^T` with fixed sum/difference readers and test source supports
  that do not equal a common mask of `C A^{-T}`. The blocker is finding
  support certificates or a cheaper exact identity without the unit-routing
  partition used here. A new word still needs a complete physical invoice.
- **Three-coordinate basis switching.** This is outside the finite support
  classification here. First enumerate attainable support strata for one
  concrete 3-by-3 basis family and attempt balanced 24-unit certificates.
  The blocker is the larger complex cancellation arrangement; increasing
  mask samples alone would not prove the universal statement.

## Credit and license

Mihir Srivastava / mihir-s-05, PR845
`125ce25bdae421627b56077adc14940c2d0aa52f`, supplies the exact geometry and
single-lift model. Woklerx, PR998
`66b777bf2b0160ed926572ff8714ac7b7bba0859`, supplies the complex extension.
Philipp / mightyOil, PR1197
`a0935afff6cc5540a582c5881bc8d5f98b587357`, supplies the coupled two-total
question and basis-change cost warning. Their proof files are pinned
context; no predecessor theorem or executable is needed by this proof
beyond the rechecked geometry.

Credit DreamingOfClouds (PR717/PR446) for the decoder/COPY interface,
Joel Pulikkan / GamingPuzzled (PR620) for the coordinate baseline,
themilkman216 (PR968), woklerx (PR1077/PR1180), joaqcoo (PR1224), Hanson Sun
(PR1633), Denis (PR1689), Sagar Thakrar (PR1327), and Douglas Colkitt
(PR1240) for adjacent constraints and planning context. The selected
construction retains Rohan Arun, Jeremy Kothe, Hao Yan and its full lineage.

Prepared for **Ross Richardson with substantial OpenAI Codex assistance**
in mathematics, implementation, both checker algorithms, testing and prose.
No subagents or independent human proof review. New material is Apache-2.0;
the unchanged predecessor sources retain their notices and license.
