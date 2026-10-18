# Four row-local certificates for two known class exclusions

Aaron Wang's PR891 already proves that the original R439 phase-B blocks at
frames 509 and 521 have no whole-block single-write program in its specified
class. Its forward/backward dynamic programs establish that conclusion.
Its simpler coordinate donor-supply test finds no witness for these blocks;
the note describes them as global order obstructions. Here four small linear
inequalities show that realization order is unnecessary to exclude them:
individual rows fail even a relaxation that lets every donor independently
choose its entry or completed value. The exclusion is prior work; this is a
strictly simpler source-bound explanation and independent certificate.

## Model and standard separating inequality

Let M be the exact nonnegative integer transfer matrix of one original block.
In the single-write class, a destination d starts with e_d and receives at
most one addition from each distinct donor j != d. Depending on realization
order, donor j is either its entry row e_j or its completed row M_j. Partial
intermediate rows, repeated use of one donor, subtraction, new registers,
changes of factor cut, and arbitrary F2-only synthesis are outside this class.

Set g=M_d-e_d. A donor row v with any coordinate greater than g cannot occur:
all additions are nonnegative, so that overshoot could never be removed.
Let V_j contain the fitting rows among {e_j,M_j}. A necessary condition,
even when all ordering constraints are discarded, is

    g = sum_(j != d) v_j,       v_j in {0} union V_j.

For any integer weight vector w, every such representation satisfies

    w dot g <= sum_(j != d) max({0} union {w dot v : v in V_j}).

This follows by applying the linear functional to the sum and bounding each
independently chosen summand. It remains valid when w has negative entries.
It is the standard support-function bound for a sum of finite choice sets;
no new convex-separation theorem is claimed. A strict reverse inequality is
a complete, order-independent certificate of nonrepresentation. Mutually
exclusive alternatives are bounded by a maximum, not added together.

The predecessor coordinate test instead sums both fitting versions of each
donor. That is a valid, looser overestimate. Our certificate does not falsify
its computation or the existing exclusion, and does not require editing it.

## Source-derived witnesses

Both matrices are reconstructed from immutable PR589's original B records.
The slices are B[283:314] at frame 509 (31 gates, 11 registers) and
B[314:361] at frame 521 (47 gates, 12 registers). Their matrices and register
lists equal PR891's pinned hashes and lists. Coefficients below refer to the
entry value of the indicated physical wire, not an intermediate live value.

| Frame | Destination wire | Functional on a row | Required | Maximum supply |
|---|---:|---|---:|---:|
| 509 | 468 | coefficient(33) | 3 | 2 |
| 521 | 32 | coefficient(42) - coefficient(10) | 2 | 1 |
| 521 | 34 | coefficient(34) - coefficient(10) | 1 | 0 |
| 521 | 107 | coefficient(13) - coefficient(10) | 2 | 1 |

For frame 509, the old coordinate bound can count both the entry and final
version of wire 33, although a single-write destination can consume it only
once. Taking their maximum removes that false supply. Frame 521 needs a
two-coordinate functional; the negative term records an unavoidable coupled
coefficient that a coordinate-only comparison loses. All allowed donor rows,
their fitting decisions and every per-donor cap are in EXPECTED.json, so each
strict inequality can be checked without a search or any order enumeration.

One row suffices to exclude each block; the other two frame-521 rows are
independent corroborating witnesses. Every one-coordinate sign and every
two-coordinate +/-1 functional is checked for all 23 rows: 6,118 functionals.
The four rows above are precisely those separated in this finite class.
The independent grouped donor enumeration finds no representation in exactly
those four rows and at least one in each of the other 19. A per-row positive
representation does not establish a consistent whole-block realization order.
There is no claim that one/two-coordinate separation decides every block or
every donor problem. For these four witnesses the support size is minimal:
the three frame-521 rows have no one-coordinate separator, and scaling any
one-coordinate real functional gives one of the two checked signs.

## Verification and scope

The primary engine uses integer row updates and direct functional maxima.
It imports none of PR891's search or verifier code. Its complete source-pin
inventory includes the baseline archive and the original statement/receipts.
The separate engine propagates individual columns through the literal source
records and exhausts each donor's unused/entry/final choice, pruning only
nonnegative overshoot. For the four negative rows it independently evaluates
all 58,320 combinations of individually fitting choices to reproduce the
claimed maxima. Duplicate equal entry/final vectors retain distinct choices;
this affects representation counts but cannot remove a valid representation.

This certifies a local obstruction to the same positive integer single-write
class. It is not an unrestricted XOR lower bound or an obstruction to known
multi-write programs (including PR843/884/1015 and PR1062's composition).
No program, gate invoice, geometry, frame, copied total, helper, boundary,
prefix guard, native stream, selected source or kappa is changed. No full
R439/H1-H5, native 5/9/11-stage replay, hosted invoice or multiplication
theorem is asserted. The useful output is four short integer inequalities
that replace reliance on dynamic programming for these known exclusions.
