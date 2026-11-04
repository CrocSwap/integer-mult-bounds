# Independent written review of signature completeness and the tensor ABI

**CONDITIONAL PASS: no gap found in the reviewed implications under the
operator, scalar-word, chronology and factorwise-ABI premises below.**
This reviews the mathematical argument in PR6716's evidence/PROOF.md and
COVERAGE.md at outer head `4a40713f10d47da5894d7673eb6d0ab2ebdf0687`.
The separately named inner current-word/compiler pin is
`17c08db090004c1fb54220a6d8463a5095789fa9`; the selected comparison is the
exact retained PR6030 source at canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Those identities must not be
collapsed into a claim that every nested archive belongs to an older Git tree.

I read the pinned proof, coverage, evidence README and source metadata, not
source .py files. No source constructor, compiler, interpreter, matrix census,
scalar replay, scientific program or proof kernel was run for this review.
The review is source-aware: the source proof supplied its intended argument,
and an earlier separately scoped task examined PR6716's cut353 caller at an
older source head. Neither that task nor source-reported numerical receipts
is substituted for evidence about the present native inventory.

## Premises being reviewed conditionally

The compared one-column maps are actual invertible unitary Clifford operators
on the same nine-axis complex space, in the same computational basis and
Pauli phase convention. The complete eighteen signed images really describe
their conjugations on the nine X and nine Z generators; the supplied complex
column really is each map applied to the index0 basis vector. Gaussian-dyadic
encoding of these concrete columns is a source-domain premise, not a claim
that every possible phase convention for an arbitrary Clifford has that form.

Each delivered recipe and helper factorization is an identity of actual
one-column operators, not merely equality of frame IDs, inventory totals,
hash labels or expected tasks. For width f, frame maps, MOVE maps, native
factors and their ordinary normalizers act by the stated factorwise tensor
ABI, including their absolute one-column phases. Scalar ADD/SCALE coefficients
instead act once on the whole payload as exterior complex scalars. The actual
chronological scalar/ownership word satisfies its common-chart and owned-use
contracts and its prescribed endpoint rows.

This note proves the consequences of those premises. It does not establish
their truth by rereading the claimed3184-task,18577-event or800-row censuses.

## Constructive Pauli-commutant proof

Write the computational basis as e_x, x in F2^9, with
`Z_j e_x=(-1)^(x_j)e_x` and `X_j e_x=e_(x+e_j)`.
Suppose A commutes with every Z_j. Its coefficient A_(y,x) satisfies

    ((-1)^(y_j)-(-1)^(x_j))*A_(y,x)=0.

For y!=x, at least one coordinate j differs; the multiplier is then2 or-2,
which is nonzero over C. Thus every off-diagonal coefficient vanishes and
A is diagonal, say A e_x=a_x e_x. Commuting with X_j then gives
`a_(x+e_j)=a_x`. Any two binary strings are joined by coordinate flips, so
all a_x equal one scalar c. Hence A=cI, without relying on an unproved
matrix-algebra generation assertion.

If U and V have identical exact conjugations on the eighteen generators,
then A=V^-1 U commutes with them and equals cI. Equality of their complete
index0 columns gives `c*V e_0=V e_0`. That vector is nonzero because V is
unitary/invertible, so c=1 and U=V. This removes the entire complex global
phase, not only its sign or modulus. Column norm1 alone would not do so.

Three written controls delimit the signature: I and Z_1 have the same
unsigned Pauli labels but opposite X_1 conjugation signs; I and Z_1 also
have the same index0 column, so the column alone is insufficient. Conversely,
U and iU have identical complete signed conjugations and equal column norms,
but their nonzero index0 columns differ. Thus both signed images and the
complete exact column are doing necessary work. These are mathematical
examples, not newly executed source controls.

## Uniqueness of the reduced dyadic column tuple

Represent a column by ordered integer arrays a,b and an integer k>=0, with
entries `(a_j+i*b_j)/2^k`. Let c be the largest integer in0..k such that
2^c divides every real and imaginary numerator. Divide all numerators by
2^c and replace k by k-c. If the resulting denominator exponent is positive,
at least one numerator is odd. If it is zero, no further reduction is allowed.
The valid unit-norm columns are nonzero, so the divisibility condition is
well-defined; an all-zero tuple could also be assigned denominator exponent0.

Suppose two reduced tuples describe the same column, with exponents k<l.
Equality forces every numerator at exponent l to be2^(l-k) times the
corresponding numerator at exponent k. All of the former are therefore even,
contradicting reducedness because l>0. Thus the exponents agree, and equality
of each real and imaginary coordinate forces the arrays to agree exactly.
This proves uniqueness of the full normalized tuple. A SHA256 label can
index it but is not the mathematical equality test.

## Delivered helper normalization and order

From an actual recipe identity `U=L G_r R`, chronological preprocessing must
be R^-1, followed by U, followed by postprocessing L^-1. The resulting map
is `L^-1 U R^-1=G_r` on every arbitrary helper input. No zero input,
correlated output observation or expected-task identity alone establishes
that delivered recipe identity.

Order cannot be silently exchanged. A written Gaussian-dyadic example uses
`c=(1+i)/2`, `K=c*[[1,1],[1,-1]]`, L=X and R=diag(1,i). These are unitary;
L and R are signed monomial matrices. With U=L K R, the correct product is
K, whereas the reversed normalizer product is

    R^-1 U L^-1 = c*[[-i,1],[1,-i]],

which differs from K already in its first column. Embedding these factors
in one of the nine axes preserves the discrepancy. This demonstrates the
order requirement without claiming that this toy is an actual paid helper.

At width f the same equation lifts as

    (L^-1)^(tensor f) U^(tensor f) (R^-1)^(tensor f)
       = G_r^(tensor f).

It relies on the factorwise normalizer ABI, not on applying a width-one
scalar phase only once. For example U=iI,L=iI,G=R=I gives the correct
normalizer phase(-i)^f. Substituting an exterior -i instead gives iI at f=2,
not I. The source explicitly distinguishes one-column phases from exterior
scalar coefficients; that distinction must remain an implementation premise.

## Arbitrary-width common-chart induction

Let H be the one-column space. For each public input j in initial frame a_j,
set `z_j=(T_(a_j)^(tensor f))^-1 x_j`. This is an invertible change of
variables on each original input, so the z_j remain arbitrary independent
vectors in H^(tensor f). They are not assumed pure tensors or equal inputs.
For each active field r the proposed invariant is

    payload_r=T_(c_r)^(tensor f) * sum_j s_(r,j)*z_j.

An exact one-column MOVE from frame a to b has the corresponding factorwise
map `T_b^(tensor f)*(T_a^(tensor f))^-1`, so it changes the frame label and
leaves its exterior scalar row unchanged. For a common-frame ADD,
linearity of T_c gives the scalar-row update exactly; SCALE by a coefficient
acts on that row once. INIT's admitted zero state has the zero row. COPY is
valid only under the actual checked frame/owned contract and copies the same
row dependence; it does not create a new independent productive input.
CLEAR retires an owned field only under the retained erasure/chronology
contract. A zero formal row is not by itself a physical-erasure certificate.

Induction through the actual admissible chronological word therefore gives
the invariant for every f>=1. Its exact scalar exit rows, together with the
specified final frames/adapters, yield the prescribed endpoint on every
arbitrary input vector. Equality of the individual operator products lifts
because `(AB)^(tensor f)=A^(tensor f) B^(tensor f)` in the same order. This
operator identity holds on a pure-tensor basis and hence by linearity on the
entire space, including vectors correlated across columns. Tensoring each
map with an identity on a spectator space preserves the same induction.

Two boundaries are essential. First, a raw ADD between different frames is
not a scalar-row ADD in one common chart: with destination frame I, source
frame Z, destination0 and source chart vector e_1, the actual result is-e_1
while the naive common-frame row predicts e_1. Second, an exterior SCALE2
remains2 at every width, not2^f. A one-column phase i^a inside a frame instead
becomes i^(af). For example I+(-I)=0 at width1, but tensoring the two operator
terms separately gives2I at width2. Thus no arbitrary width-one sum identity
is lifted by this argument; the eventwise chart/scalar invariant is necessary.

## Scope, verdict and credit

The signature-completeness, dyadic-uniqueness, correctly ordered helper and
factorwise common-chart implications pass this written review under their
explicit premises. Actual source custody, tuple extraction, emitted recipe
correctness, paid Gaussian ranks,3184 tasks,39 unmatched operators, five
helper normalizations,18577 events,800 exits, lifetime counts and current
physical implementation were not independently checked here. Source-reported
counts remain source-reported. No complete supplier, fixed-tape allocator,
stock/layout/precision/callback/compiler/outer result or discharge of the
five retained framework assumptions follows. There is no changed word,
invoice, kappa, selected frontier, human acceptance or proof-kernel result.

DreamingOfClouds/PR6030 and its maintainer repair retain exact selected-source
credit; Matarener retains scalar/inventory machinery; Clear1nsight retains
the dense Gaussian-dyadic interpreter; Charles Bethin and the retained lineage
retain compiler/literal semantics credit; Ali Romman retains the prefix
evaluator and PR6702 lineage. thu-nmrc's source comparison/application delta
and existing common-chart method remain credited rather than claimed as new
general mathematics. Pauli commutants, dyadic reduction and tensor linearity
are classical. This external source-aware written AI review was prepared
with substantial OpenAI Codex assistance. Apache-2.0.

## Post-draft consistency check

The core review above was completed before reading the coordinator's REVIEW.md.
I then read that draft and found no inconsistency with this conditional result,
including its Gaussian-dyadic matrix-order and common-chart controls. Its
selected-review-specific counts and COPY/residual discussion were not separately
reaudited by me. This later comparison is disclosed rather than presented as
blind agreement or another actual-source replay.
