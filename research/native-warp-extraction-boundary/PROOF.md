# Native relations and the fixed two-sided extraction spaces

All coefficient spaces below are over **Q**. This is a finite statement about
the two pinned PR3042 six-skip words, as retained by PR3054. It neither optimizes
all scalar programs nor proves the complete multiplication theorem.

## 1. The exact operator being compared

Use PR2908/2979's non-target forward operator M: execute A after the 84-event
entry prelude, then the B program with its literal warp positions, then restore.
Omit target writes. A target never feeds a non-target register; the checker
rejects that condition if violated. There are 520 non-target registers: 112
sources and 408 helpers. The 72 removed helpers are absent.

Starting with every independent input, `replay` propagates sparse rational rows
with formal noncommuting warp words. Adjacent inverse symbols would cancel.
The final matrix is checked to have only identity terms and **one positive
warp symbol** per other term:

    M = M0 + sum_{j=1}^{72} Mj Xj.

No assertion that arbitrary products of binary G maps preserve the native
phase convention is used. In particular, this proof must be revisited if a
changed word leaves products of warp symbols in M.

Let H be the 207 zero-entry helpers excluding existing restored helpers,
entering helpers and the six initial-correction sources. These exclusions are
exactly the retained paired-extraction input contract. Let C be the literal
zero-frame compensation matrix restricted to H. Its duplicate entries are
summed, not treated as set membership.

Define the right space V and left space L by

    V = {v supported on H: Mv is scalar and Cv = 0},
    L = {alpha: alpha M is scalar and supported on H}.

Here scalar means a rational multiple of the identity native operator in each
matrix entry. The free-symbol versions require every nonidentity coefficient
to vanish separately. We compare these definitions with actual native K_G's.

## 2. Exact native maps, including phase

For a binary invertible 9-by-9 matrix G, use the existing PR2226 convention
implemented by `Kop` and `monomial` at the source pins in SOURCES.json. With

    QG = I + G^(-T) G^(-1) over F2,
    qG(y) = sum_i (QG)_ii y_i + 2 sum_{i<j} (QG)_ij y_i y_j mod 4,

its 512 complex columns are

    K_G |x> = i^(qG(Gx)) |Gx>.

The verifier implements this formula twice: binary Gaussian inversion and
matrix products; separately, inversion of the full permutation and Gram
products of inverse columns. Both must agree on every column, including phase.
These share the credited mathematical formula, not an independently derived
native compiler theorem. No predecessor Python is imported or executed.

The 72 symbols form 58 distinct G maps. The nontrivial equality classes are

    (3,4,29), (8,9), (10,11), (16,17), (18,19),
    (23,24,25), (34,35,36), (38,39,40), (43,45), (71,72).

The identity plus these 58 native matrices are linearly independent over Q.
To certify this, flatten their real and imaginary parts. The verifier selects
59 coordinate equations forming a full-rank minor modulo p=1,000,000,007.
Its entries are integers in {-1,0,1}; a nonzero minor modulo p has a nonzero
integer determinant, proving rational independence. RESULT.json records the
59 selected (input column, output row, real/imaginary component) coordinates
for each provider. The complete native column formulas are regenerated.

Consequently a rational linear combination of the native matrices vanishes
if and only if its coefficients grouped by these equality classes vanish.
There are no additional rational linear relations among the native maps in
this affine-linear M. This does not assert that they freely generate an
operator algebra, nor that they are independent over arbitrary coefficient
fields or under operator-valued coefficients.

## 3. Kernel equality, rather than a modular heuristic

Let AR and AL be the coefficient constraint matrices defining V and L in the
free-symbol model, and BR and BL their grouped/native versions. Grouping
sums old equations, so ker(A) is contained in ker(B).

For each side, rational forward elimination constructs a basis candidate for
ker(A). Its correctness is checked without trusting the elimination:

1. Multiply each vector by every original equation over Q; every result is zero.
2. Its free-coordinate submatrix is the identity, proving independence.
3. Check the same vectors against all grouped equations over Q.
4. Independently eliminate B modulo p, with every denominator required to be
   invertible. If its rank is n minus the number of basis vectors, rational
   rank(B) is at least that large, and its nullity is at most the basis size.

The nullity lower and upper bounds coincide. Inclusion then proves
ker(A)=ker(B), not merely equality of two modular ranks. A bad prime can cause
an inconclusive failure; it cannot silently certify the equality. A test uses
the rational matrix [p], whose rank drops modulo p, to enforce this distinction.

For **both providers**, the exact certificates give:

| Side | Variables | Free/grouped equations | Rank | Nullity |
|---|---:|---:|---:|---:|
| Right, including Cv=0 | 207 | 360 / 288 | 88 | 119 |
| Left | 520 | 561 / 539 | 339 | 181 |

Grouping removes 184 terms from M (12,173 to 11,989), affecting 40 row term
counts. Thus grouping has a real algebraic effect; it simply does not enlarge
these two spaces. No native warp is identity, so M0 is unchanged.

## 4. Consequence for any terminal support and simultaneous extraction

A scalar paired extraction chooses v in V and alpha in L with

    y = Mv = M0 v,    u = alpha M = alpha M0,    alpha y = u v != 0.

For a terminal frame E, the retained construction additionally requires y and
alpha to be supported on registers eligible at E. The spaces V and L, the
scalar map M0 and its pairing are identical before and after native evaluation.
Imposing **any** common support restriction R therefore produces identical
restricted spaces and pairing ranks. This includes every frame E without an
extra finite scan over hyperplanes or rank-seven subspaces. It also includes
multiple simultaneous scalar directions: the entire bilinear pairing, not
just one normalized pair, is unchanged.

Therefore replacing free warp symbols by the actual native maps cannot expose
new scalar paired-extraction directions on these words under this input
contract. This strengthens the interpretation of the prior free-symbol search;
it does not rerun its cost optimization or prove its search complete.

## 5. Boundaries

Changing A/B/restore, the native G/phase convention, the protected input contract,
initial-correction handling, or the use of rational scalar coefficients changes
a hypothesis. Operator-valued preparation/readout, modified consumers and new
geometry remain outside the result. Better synthesis or pricing of an already
available direction is also not excluded.

The original scalar identities, native Clifford realization and supplier
admission are predecessor evidence. This package establishes the stated
finite algebraic implication only. It does not validate all-size/compiler,
physical backing/routing, precision/tape, stock/caller, common-label or analytic
transfer assumptions; it neither changes the selected frontier nor claims κ.
