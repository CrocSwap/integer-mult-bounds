# The retained five-bank word has no free monomial-algebra completion

This is an outputs-only exact embedding gate for PR4856 at
`0970de4ec97fc942e6202403ffd7586d19559391`. It applies the group-algebra
projection and all-width faithfulness argument retained in PR4920 at
`7eb4ef5251f7ba96c7e5d78c42fc98e66b7be4ba` to the actual five-bank endpoint.
It is not a circuit search, a new construction, or a new kappa value.
The earlier direct PR4908 binding gate did not allow cross-output ADD;
this argument does, within the fixed finite columnwise Clifford alphabet.

## Exact source word and expansion

Use the source's absolute-phase three-axis Clifford letters. Products act
on a column from right to left. Put

    A=C0, K=C0 C1 C2,
    P=S U S, Q=S V S, S=s_letter(7),
    U=monomial([0,5,2,7,4,1,6,3]),
    V=monomial([0,2,1,3,4,6,5,7]),
    D=Z1 V C2 W C0, W=Z0 Z2,
    B=D(P+2Q)A, F=A(P+2Q)A.

Crucially, at width f these expressions mean
`B_f=D_f(P_f+2Q_f)A_f`, with each pure letter tensor-powered separately.
The scalar 2 stays outside the tensor power. The source's pure identities
include `A^2=X0` and `AD=N K` with a unit-phase monomial N.

The actual retained owner map is

    u0=x0; uj=D xj+B u(j-1), j=1,...,4;
    y0=A^2 x0+F u4; yj=A uj, j=1,...,4.

Consequently its block matrix M has

    M00=A^2+F B^4,
    M0k=F B^(4-k)D, 1<=k<=4,
    Mj0=A B^j, 1<=j<=4,
    Mjk=A B^(j-k)D, 1<=k<=j<=4,
    Mjk=0, j>=1 and k>j.

The executable expands `B=bP+2bQ` and `F=hP+2hQ`, where each b/h is a
single Clifford word. It groups by exact rational-complex 8-by-8 matrices,
retaining absolute phases and integer coefficients. It independently
replays both `five_ports` and `fused_five_ports` in the frozen WORD.json IN
THE EXACT GROUP ALGEBRA and matches all 25 blocks to this recurrence. Group
keys retain absolute one-column matrices, and scalar coefficients remain
outside tensor powers. Ordinary one-column operator equality is only an
additional check. Changing an actual ADD sign or omitting the actual
closing bank0 A gate fails this group-algebra comparison. Thus this is the source endpoint,
not a replacement diagonal-only model. All full matrices, branch labels,
coefficients and grades are retained in RESULT.json.

The entries below list counts of distinct exact group elements by grade
`(rank0,rank1,rank2,rank3)`, after grouping identical pure words:

| row / column | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| 0 | (6,0,26,0) | (0,16,0,0) | (0,0,8,0) | (0,4,0,0) | (0,0,2,0) |
| 1 | (0,0,2,0) | (0,0,0,1) | 0 | 0 | 0 |
| 2 | (0,4,0,0) | (2,0,0,0) | (0,0,0,1) | 0 | 0 |
| 3 | (0,0,8,0) | (0,0,0,4) | (2,0,0,0) | (0,0,0,1) | 0 |
| 4 | (0,16,0,0) | (8,0,0,0) | (0,0,0,4) | (2,0,0,0) | (0,0,0,1) |

In particular M00 has 33 ungrouped terms, 32 exact group elements, and 32
distinct projective classes. Its rank0 and rank2 coefficient masses are 43
and 201. The `A^2=X0` term has coefficient 1 and is the only term in its
projective class, even among all 32 FB^4 branch terms. Therefore its
coefficient remains1 in every central-character quotient: no scalar phase
from another term in that class can cancel it. This alone does not assert
linear independence of different Clifford matrices at small widths.

## All-width algebra, including absolute phases

Let G be a chosen finite-phase group of exact one-column three-axis Clifford
matrices, containing all source letters and the full monomial Clifford
subgroup H in that finite alphabet. Put `Z={z in G : z is scalar}`; H
contains Z. This uses a finite-phase Clifford group, not the normalizer
enlarged by arbitrary U(1) phases. Work over a characteristic-zero splitting
field E. At width f set

    A_f=E[G]/(z-scalar(z)^f : z in Z),
    B_f=E[H]/(z-scalar(z)^f : z in Z).

These are the central-character twisted group algebras on G/Z and H/Z.
Projection pi0 from A_f to B_f discards all nonmonomial projective classes.
Multiplication by H on either side preserves monomial membership and its
complement; hence pi0 is a B_f-bimodule map, entrywise on owner matrices.
The other Fourier-grade projections have the same bimodule property.
Monomial row/column permutations and phases preserve the uniform support
size 2^rank of a pure Clifford matrix, which is the grade used here.

The retained PR4920 independent review proves that the tensor evaluation
of A_f is injective for every f>=|G/Z|-1. Briefly, for each projective
representative v_t choose for every other v_u a linear functional zero at
v_u and nonzero at v_t. Their product isolates v_t in degree |G/Z|-1;
multiplication by a nonvanishing linear functional extends to any larger
degree. Applying this homogeneous polynomial to tensor powers establishes
linear independence. Scalar phases specialize as scalar(z)^f. This
argument permits width-dependent scalar coefficients and free controls
within the same fixed finite alphabet.

The unique X0 class above therefore proves `pi0(M_f) != 0` as an algebra
matrix for every f, and as an evaluated operator matrix for every
sufficiently large f. The all-width endpoint obstruction uses these
sufficiently large widths. It makes no grade-projection claim based only
on accidental relations between one-column matrix sums.

## Stronger rank3 resource bound: linear copy, drop, reset and clean buffers

The parent identified a stronger invariant from the complete grade table.
Let `A_(3),f` be the E-vector space spanned by rank3 projective classes in
A_f. It is a B_f-bimodule. Projection pi3 onto this space is therefore a
B_f-bimodule map. Consider the right-B_f-linear input map

    pi3(M_f): B_f^5 -> A_(3),f^5.

The exact group-algebra checks establish that its entire first row AND
first column vanish. Its lower4-by-4 block is lower triangular with the
single group unit AD, of grade3, on every diagonal position. Thus its
image has E-dimension exactly4*d, where d=dim_E B_f. The zero first input
column gives the upper bound4*d. For the lower bound, a vector in the
kernel of the lower triangular block has `AD*x1=0` in its first row;
multiplication by the group inverse gives x1=0. Successive rows then give
x2=x3=x4=0. This is an injective map from B_f^4 into A_(3),f^4; no domain
or division property for B_f is assumed.

Allow arbitrary rectangular pre/post matrices over B_f, and arbitrary
owned free buffers, saved original inputs, linear copies, dropping and
resets. For this linear alphabet any such pre/post policy, restricted to
the five original independent inputs and the five desired output rows,
has form

    T = L (M_f direct_sum I_s) R + E0,

for some s, where L,R are arbitrary compatible matrices over B_f and
`E0` is a free B_f-valued bypass (which can also be absorbed into a larger
identity summand). No invertibility or scratch restoration is required.
Identity and zero/clean bypass resources have zero pi3. Therefore

    pi3(T) = L (pi3(M_f) direct_sum 0_s) R,
    rank_E pi3(T) <= 4*d.

Here R maps B_f-input modules into B_f intermediate modules, while L acts
E-linearly on the A_(3),f output space. This is not incorrectly treating
pi3(M_f) as a B_f-valued endomorphism. Neither map can increase the image
dimension4*d. Scalar coefficients and the number of buffers may depend on
width; the inequality holds separately at each sufficiently large width.

Five independent pure grade3 target words `diag(g1,...,g5)` instead define
an injective map `B_f^5 -> A_(3),f^5`: each gj is a group unit, including
any allowed monomial boundaries. Their grade3 image dimension is5*d.
This contradicts the bound. Extra discarded or main-dependent garbage
outputs cannot repair the five required output rows. Thus the unchanged
producer has no exact five-target completion by any such free linear
pre/post decoder, even with clean/copy/drop/reset buffers and saved-input
bypass. The all-width applicability is the preceding sufficiently-large-f
faithfulness argument. No accidental small-width equality is ruled out by
this algebraic proof.

## Supporting rank0 proof for invertible controls and restored dirty scratch

Allow any number s of dirty scratch owners returned unchanged. Grant
arbitrary invertible pre- and postcontrollers L,R over B_f on all 5+s
owners, with unrestricted scalar coefficients, cross-owner ADD and full
monomial Clifford boundaries. This is a relaxation of a finite native
free controller; all its Gaussian calls remain those in M. Suppose

    L (M_f direct_sum I_s) R = diag(g1,...,g5,I_s),

where each gj is a single pure rank3 Gaussian Clifford, with arbitrary
monomial input/output boundaries. Each target gj has zero pi0 projection.
Applying the bimodule projection gives

    L (pi0(M_f) direct_sum I_s) R = diag(0,0,0,0,0,I_s).

Let d=dim_E B_f. Regard these matrices as E-linear maps on the regular
right module B_f^(5+s), using left multiplication for their entries.
A nonzero B_f entry gives a nonzero linear map (apply it to1), even though
B_f can have zero divisors. Thus `rank_E pi0(M_f)>=1`. The left side has
rank at least `s*d+1`, since the two blocks act on separate summands and
L,R are invertible. The right side has rank exactly `s*d`, a contradiction.
Equivalently the respective nullities are at most5*d-1 and exactly5*d.
No domain assumption, determinant argument or positivity assumption is
used. The argument holds for each sufficiently large f, so an all-width
completion of this form is impossible.

Without scratch, the nonzero grade component and invertibility suffice
immediately. With scratch, the rank argument prevents moving that component
into an identity scratch block. Arbitrary scratch count and width-dependent
free coefficients do not change the contradiction.

## Complete invoice and stop gate

The actual fused source bill remains `2H1+4H3`,24 monomial passes and10
ADD passes. Five independent rank3 rewards would give optimistic recursive
moment `3^(1-C)-2`, but the required free completion is now excluded in the
declared alphabet. One additional ordinary rank1 Gaussian already changes
this upper bound to `3^(1-C)-3<=0` for 0<=C<1. Thus that completion cannot
fund a positive moment before any finite/compiler reserve.

There is also no profitable downgrade to five independent pure Gaussian
targets of ranks at most3. If k of them have rank3, the target pi3 map
has image dimension k*d, so the resource bound forces k<=4. Put t=1-C,
with0<=t<=1. The other targets have rank at most2; granting all five jobs
and zero finite bill gives

    reward <= 4*3^t + 2^t,
    paid recursive cost = 4*3^t + 2,
    moment <= 2^t - 2 <= 0.

This bound is strict for0<=t<1, equivalently positive C, and only reaches
zero at C=0. If k<4, monotonicity `3^t>=2^t` gives the same upper bound.
An empty/rank0 job can only reduce reward under the convention h(0)=0.
Thus no five-target census with ranks at most3 can make this unchanged
paid profile profitable through a free linear pre/post decoder in scope.

This closes the zero-extra-Gaussian pre/post completion question for the
unchanged five-bank word under arbitrary free linear full-monomial Clifford
ADD controllers, including owned clean/copy/drop/reset buffers and saved
original-input bypass. The rank0 proof separately covers arbitrary restored
dirty identity scratch with invertible controls. It also includes
any PR4908 inverse representable by such controllers if it were bound to
this actual endpoint. No new decoder, precision schedule or kappa is
supplied or needed for this negative gate.

Open next questions require a changed premise: another paid word/profile,
transformed nonmonomial helper resources with a complete invoice, another
target census, or a non-columnwise address grammar. Arbitrary width-specific
address permutations outside the fixed finite tensor alphabet and changed
main sizes are outside this claim. The same applies to prefix taps, saving
intermediate producer states, and inserting free gates inside the retained
producer word. The model grants one invocation of that complete fixed
producer plus pre/post controls and saved original-input bypass. These are
scope limits, not proposed successes.

Sources retain their original authorship and Apache-2.0 notices. The
five-bank construction and invoice are PR4856's; the projection and
phase-aware faithfulness argument are reused with credit from PR4920 and
its independent review. The parent research agent proposed the stronger
maximal-grade resource bound removing controller invertibility and scratch
restoration assumptions. New expansion and application: OpenAI Codex
gpt-6.1-sol/high, outputs-only work for the parent research session.
