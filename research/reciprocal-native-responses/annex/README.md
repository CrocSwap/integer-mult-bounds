# Low-displacement response supplement

This supplement preserves the completed rank-30 and rank-16 response
results. It gives different response classes from the reciprocal
zero-diagonal family in the main package. The frozen files keep their
original bytes and source pins.

These are matrix constructions, local native words, and two scoped
obstructions. They do not expose a productive centre cohort, remove the
output code, or improve the complete kappa calculation. The moving
section and rational code-service constructions are separate results.

## Exact matrix statements

The [rank-30 response proof](frozen/lanes/new-core-transfer-20261017/low-displacement-20261020/RESPONSE.md)
constructs a dyadic unit `E` on the actual 112 ports, with
`rank(E-I)=30`. Its selected eight-port block is the original `L`,
with `L^2=I/2`, in both `E` and `E^-1`. The full determinant is
`2^25`; the ordinary 104-port determinant is `2^21`. Each literal
common-frame word for `E`, `E^-1`, `E^T`, and `E^-T` costs 3,210
real scalar primitives on arbitrary input fields.

The large 48-port part contributes rank 16. The small part uses eleven
five-cliques and three three-cliques. Fourteen blocks are optimal only
among disjoint rank-one dyadic clique blocks of sizes 2, 3, and 5 on
this fixed small support. This is not a native optimum or a lower bound
for all response matrices. The small inverse has a nonzero diagonal.

The [extension proof](frozen/lanes/new-core-transfer-20261017/low-displacement-20261020/EXTENSIONS.md)
also gives a reciprocal-large response. It replaces the large block by
its inverse transpose and keeps the small response. The backward cross
block uses the large inverse and the original small response. It does
not implement the inverse of the complete 112-port response.

The rank-16 extension is symmetric and has determinant `35^8` and
`rank(E-I)=16`. Its large part is `I-K^T K/2`, where `K K^T=12I`.
Its inverse is `I-K^T K/10`. The small part has eight blocks `I-J_8`,
with inverses `I-J_8/7`. The selected block of `E` is `L`; the
selected block of `E^-1` is `(4I+L)/5`.

Rank 16 relaxes both the inverse-diagonal requirement and the grid
requirement. The inverse diagonal on each six-mode block is `4/5`.
The inverse needs primes 5 and 7 in the stored grid. The ordinary
normalization also needs prime 31: its inverse has denominators 7,
31, and 62. Odd denominators alone do not evade the reciprocal
rank-two theorem. The native data word does not supply or price these
inverse conversions.

## Local native contracts and costs

The [raw native proof](frozen/lanes/new-core-transfer-20261017/low-displacement-20261020/NATIVE.md)
and the extension proof give both directions for both retained
providers. Each local word checks all 640 arbitrary input fields and
leaves the 416 fields outside the two data banks unchanged. Each uses
zero owned fields and zero private fields. There is no clean-field
premise. The following prices are per word.

| Response | Native profile | Children | Rank mass | Real scalar primitives | External endpoint maps |
| --- | --- | ---: | ---: | ---: | ---: |
| Rank 30 | `1036 H1 + 48 H3 + 55 H4 + 55 H5 + 9 H6 + 9 H7` | 1,212 | 1,792 | 5,288 | 224 |
| Reciprocal-large | Same as rank 30 | 1,212 | 1,792 | 5,288 | 224 |
| Rank 16 | `1520 H1 + 64 H2 + 48 H3` | 1,632 | 1,792 | 7,384 | 224 |

The separate upper bound of two side maps per native child is 2,424
for rank 30 and reciprocal-large, and 3,264 for rank 16. These side
maps are additional to the displayed external endpoint maps. The
array prefix bounds are 46 forward and 30 backward for rank 30, 30
forward and 46 backward for reciprocal-large, and 22 in both
directions for rank 16.

The [coded-exit proof](frozen/lanes/new-core-transfer-20261017/low-displacement-20261020/CODED-EXITS.md)
keeps `W=S_e0 C_45 S_e0` on the large 48 ports or on all 112 ports.
On a coded port, the exact output contracts are
`X_p=W F9 x'_p` and `Y_p=W F9 Q_p^-1 y'_p`. The operator order is
literal. The code is not removed and `W` does not commute freely
through `Q_p`. Thus these are changed output contracts.

| Response and output code | Native profile | Children | Rank mass | Real scalar primitives |
| --- | --- | ---: | ---: | ---: |
| Rank 30, `W48_I64` | `988 H1 + 48 H2 + 55 H4 + 55 H5 + 9 H6 + 9 H7` | 1,164 | 1,696 | 5,288 |
| Rank 30, `W112` | `988 H1 + 48 H2 + 55 H5 + 55 H6 + 9 H7 + 9 H8` | 1,164 | 1,824 | 5,288 |
| Rank 16, `W48_I64` | `1472 H1 + 112 H2` | 1,584 | 1,696 | 7,384 |
| Rank 16, `W112` | `1408 H1 + 112 H2 + 64 H3` | 1,584 | 1,824 | 7,384 |

Each coded word has 48 explicit inline monomial exits. `W48_I64`
retains 176 external endpoint maps; `W112` retains 112. The side-map
upper bound is twice the child count. These counts do not pay for
future code removal, terminal access, or a recursive caller.

## Two scoped limits

The [cross-Gram proof](frozen/lanes/new-core-transfer-20261017/low-displacement-20261020/EVEN-CLIQUE-GRAM.md)
shows that the current rank-16 factor cannot support a section-swap
code that requires an everywhere invertible `V Q^2 U`. Its ranks on
all 512 characters are 0, 4, 8, 14, and 16, with counts 32, 96, 12,
256, and 116. A change of minimal scalar factor basis cannot remove
the obstruction. This does not rule out a different encoding method.

The [paired-line proof](frozen/lanes/new-core-transfer-20261017/low-displacement-20261020/PAIRED-LINE-TENSOR-SCOPE.md)
proves that the scalar two-field identity retains a tensor-width
cost. A word with arbitrary monomial views and no native calls needs
at least `f` scalar ADDs to implement `Q_f` or
`diag(Q_f,Q_f^-1)`. A separate one-call determinant obstruction
requires translation-only views. It does not apply to general native
views. The finite checks cover widths 1 through 6.

The paired-line freeze retains its historical status
`FROZEN_PRODUCER_NOTE_INDEPENDENT_REVIEW_NOT_RUN`. The new publication
proof review is separate evidence and does not rewrite that status.

## Evidence and replay

[SOURCES.json](SOURCES.json) pins 59 additional frozen files and 14
shared files from the main package. It retains the exact proofs,
payloads, checks, and five historical independent reviews:

- [Rank-30 matrix and scalar review](frozen/lanes/independent-review-20261017/rank-thirty-review-20261020/REVIEW.md).
- [Extension matrix review](frozen/lanes/independent-review-20261017/response-extensions-review-20261020/REVIEW.md).
- [Rank-30 native review](frozen/lanes/new-native-recipes-20261017/low-displacement-review-20261020/REVIEW.md) and [extension native review](../frozen/lanes/new-native-recipes-20261017/low-displacement-review-20261020/EXTENSIONS-REVIEW.md).
- [Coded-exit review](frozen/lanes/new-native-recipes-20261017/low-displacement-coded-review-20261020/REVIEW.md).

The historical raw native review checks 1,141 native recipes and 224
endpoint adapters with complete spatial columns. The extension review
inherits the unchanged reciprocal-large paths and checks 876 new
rank-16 phases, with 685 exact inherited recipes. The coded review
checks 352 changed exits: 48 exact inherited exits and 304 complete
spatial checks. These historical spatial replays are not repeated by
the four frozen matrix and scope checks below.

The new [publication checker](check_native.py) uses separate rational
arithmetic from [its review helper](check_publication_review.py). It
checks all 12 raw words, 16 coded words, the exact changed output
order, and all 352 changed-exit phases with the retained exact phase
engine. It also checks the three matrix models and all 512 cross-Gram
ranks. Raw phase and endpoint inheritance remains tied to the historical
reviews. [PUBLICATION-CHECKS.json](PUBLICATION-CHECKS.json) pins the
unchanged checkers and [their accepted receipt](NATIVE-CHECKS.json).

From the main package directory, use Python 3.10 or later:

```sh
python3 -I -B replay_annex.py --out /tmp/reciprocal-response-annex-replay
```

The output directory must not exist. The runner copies the two frozen
trees into a new directory and checks every source hash. It runs the
two independent matrix checks, the cross-Gram checker, and the
paired-line checker in normal Python and with `-O`. It compares all
eight receipts byte for byte with their frozen values. It also runs
the new publication checker in both modes. For those two receipts,
it compares every field except Python version and elapsed time. The
expected final line is:

```text
PASS_LOW_DISPLACEMENT_RESPONSE_ANNEX
```

[VALIDATION.json](VALIDATION.json) records the ten completed checks,
commands, source-manifest hashes, and receipt hashes.

The main package replay remains separate. Source credits, retained
licenses, and the AI-assistance disclosure are in
[the source notice](../SOURCE-NOTICE.md). This supplement makes no
claim of independent human review.

## Open next questions

- Can a paid code expose and restore the rank-16 or rank-30 records
  at an actual caller cut? A displacement factor alone gives no such
  interface.
- Can a caller retain `W` with a complete endpoint and terminal
  calculation? The coded words leave this operator present.
- Can the rank-16 inverse use an admitted odd grid, including its
  selected normalization, with every conversion and precision cost?
  The raw native response does not settle that task.
