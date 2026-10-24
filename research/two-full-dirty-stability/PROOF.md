# Identity scratch and joint main-owner routing do not rescue two native FULLs

This is a scoped obstruction, not a new multiplier, native caller, or kappa
improvement. It extends the full-monomial **two-owner** Fourier-grade theorem
of [PR4920](https://github.com/CrocSwap/integer-mult-bounds/pull/4920) to
arbitrarily many simultaneous main pairs under joint owner control, together
with arbitrarily many independent dirty scratch owners returned unchanged.
In particular, the declared main interface permits joint control of all
224 original main owners in a native 112-pair bank. The additional argument
uses the intermediate grades, regular-module rank, and a zero-column block.
It answers the identity-scratch question released in
[Discussion4902 comment19144315](https://github.com/CrocSwap/integer-mult-bounds/discussions/4902#discussioncomment-19144315).

The source interface, grade facts, and all-width separation lemma are inherited
from PR4920. The finite regular-module method and the warning against silently
combining different resource scopes are credited to
[PR4928](https://github.com/CrocSwap/integer-mult-bounds/pull/4928).
Native operators and raw phase conventions are credited to the upstream
contributors. The new argument is the forced main/scratch decoupling and its
simultaneous block extension below.

## Exact algebra and endpoint

Let G be a fixed finite-phase, one-column Clifford group on 17 address axes,
Z its scalar subgroup, and H its **full monomial subgroup**, containing Z.
In particular, H includes monomial central/fresh coordinate mixing and
controlled quadratic phases; it is not the separated subgroup in PR4928.
At column width f, let A_f be the central-character twisted group algebra
on G/Z, specializing z=ζI to ζ^f over a characteristic-zero splitting field K.
Let B_f be its subgroup algebra on H/Z. No domain assumption is made.

Fourier grade is unchanged by left or right monomial multiplication. Thus
projection onto any chosen set of grades is a B_f-bimodule map. Products of
pure words satisfy grade(uv) <= grade(u)+grade(v). These are exactly the grade
facts used by PR4920; scalar cocycles change coefficients, not grades.

There are 2m main owners, m>=1, and s>=0 further independent arbitrary dirty
scratch owners. The real native helper jobs remain autonomous, unchanged,
and unavailable for mixing. On the main index set, choose two partitions

    C disjoint-union Cbar = {1,...,2m},  |C|=|Cbar|=m,
    U disjoint-union Ubar = {1,...,2m},  |U|=|Ubar|=m.

The first stage's query block has destination rows C and source columns Cbar;
the second stage's query block has destination rows Ubar and source columns U.
These two partitions and the pairings within them need not agree. Write

    T1 = diag(A1,...,A_(2m),I_s) E1,
    T2 = diag(B1,...,B_(2m),I_s) E2,
    E1 = I + N1,  support(N1) contained in C x Cbar,
    E2 = I + N2,  support(N2) contained in Ubar x U.

Products act on columns from right to left. Each Ai and Bi is a pure Clifford
group unit of Fourier grade eight, including role-dependent raw translations
and phases. The actual disjoint native shears have one query per paired
destination/source. We grant the stronger relaxation in which

    Q1 = (N1)_(C,Cbar),  Q2 = (N2)_(Ubar,U)

are arbitrary m-by-m matrices over A_f. Their entries may differ and need not
commute with each other or any Ai/Bi; signs and inverses are retained. Since
N1^2=N2^2=0, these relaxed shear blocks are still invertible. This is the source
factor order `diag(D) E`; no rank-eight factor is absorbed into a free control.

Allow arbitrary L,W,R in GL_{2m+s}(B_f). They may jointly mix every main and
scratch owner, including different original ports. Their entries may be sums
of monomial words, not just pure words, pairwise controls, or owner permutations.
Suppose

    L T2 W T1 R = J = diag(g1,...,g_(2m),I_s),

where each gi is one pure Clifford group word of grade 17, up to arbitrary
monomial boundaries and with its actual phase. We prove this impossible for
every m>=1 and s>=0. Disjoint native pair shears, with arbitrary orientations
and free port permutations at either stage, satisfy these hypotheses without
having to align their destination/source halves across stages.

## Intermediate grades force the interstage control to decouple

Put rho=pi_{1,...,16}. Since rho(J)=0, the bimodule property and invertibility
of L,R imply

    rho(M)=0,  where M=T2 W T1.                         (1)

This retains the grade-zero scratch endpoint. It does **not** make the
incorrect inference pi_{<=16}(M)=0 while scratch is present.

The first shear leaves all input columns c in C untouched; the second leaves
all output rows r in U untouched. For m=1 these are exactly the four orientations:

| First shear | Second shear | Untouched column c | Untouched row r |
| --- | --- | --- | --- |
| E12 | E12 | 1 | 2 |
| E12 | E21 | 1 | 1 |
| E21 | E12 | 2 | 2 |
| E21 | E21 | 2 | 1 |

For every scratch index a, c in C, and r in U, direct multiplication gives

    M[a,c] = W[a,c] A_c,
    M[r,a] = B_r W[r,a].                               (2)

Each entry is supported wholly in grade eight: W entries lie in B_f and
monomial multiplication preserves grade. Consequently rho is the identity
on these entries. By (1) they vanish. Ai,Bi are group units, so

    W[a,C]=0,  W[U,a]=0.                               (3)

Before using (3), the remaining cross entries, for j in Cbar and i in Ubar, are

    M[a,j] = W[a,j] A_j + sum_(c in C) W[a,c] A_c Q1[c,j],
    M[i,a] = B_i (W[i,a] + sum_(r in U) Q2[i,r] W[r,a]). (4)

The query terms vanish by (3), without moving a query through any D factor.
The remaining terms are again entirely grade eight, so (1) implies

    W[a,Cbar]=0,  W[Ubar,a]=0.                         (5)

Equations (3),(5), for all a, say

    W=diag(Wm,Ws),       M=diag(Mm,Ws),
    Mm=T2_main Wm T1_main.                             (6)

Both Wm and Ws are invertible over B_f. Indeed, multiplying a two-sided
inverse of the block diagonal W on either side gives a two-sided inverse
for each diagonal block. This works for every finite s, including s=0.

## The scratch block already uses the entire projected rank

Let Pi=pi_{0,...,16} and P=diag(0_(2m),I_s). The endpoint equation gives

    Pi(M) = L^-1 P R^-1.                               (7)

The right side lies in Mat_{2m+s}(B_f). Independently, (1) implies
Pi(Mm)=pi_0(Mm), so the left side of (7) also lies in that matrix algebra.
Thus the following rank comparison is on B_f^{2m+s}, rather than an
unjustified restriction of an A_f-valued map to B_f.

Put d=dim_K(B_f). Act by left multiplication on columns in the right regular
module B_f^{2m+s}; its K-dimension is (2m+s)d. L and R are invertible on that
space. The right side of (7) therefore has K-rank sd. By (6), its left side is

    diag(Pi(Mm), Ws).

The invertible Ws block already has rank sd. Rank additivity for this block
diagonal K-linear map forces Pi(Mm) to have rank zero on B_f^{2m}. Left regular
multiplication is faithful: a nonzero entry acts nontrivially on the column
having 1 in its input position. Consequently

    Pi(Mm)=0                                          (8)

as an algebra element. This is not an accidental small-width operator
identity, and it does not use an integral-domain or division-ring property.

## A whole block of untouched main columns must vanish

For every r in U and c in C, directly,

    Mm[r,c] = B_r Wm[r,c] A_c.

Every word here has grade at most 8+0+8=16. Hence it is its own Pi projection;
(8) makes it zero and the group-unit factors give Wm[U,C]=0. For i in Ubar,
the other entries of these same input columns are

    Mm[i,c] = B_i (Wm[i,c] + sum_(r in U) Q2[i,r] Wm[r,c]) A_c
            = B_i Wm[i,c] A_c.

The same grade bound and (8) give Wm[Ubar,C]=0. Thus all m columns indexed
by C vanish in Wm, contradicting invertibility because m>=1. This is the block
extension of PR4920's direct zero-column step. It needs no reduced outer
main-only L/R, presumes no such reduced matrices invertible, and does not
assume matching orientation or pairing between the stages.

## Why this is an all-width obstruction

The argument above holds in A_f for every central character. To pass from
literal tensor operators to A_f, use PR4920/PR4928's separating-polynomial
lemma, recalled here to make the hypothesis explicit. Choose one matrix
representative v_t per projective class G/Z, and put h=|G/Z|. For each t and
u!=t, choose a linear functional that vanishes on v_u and not on v_t. Their
product isolates v_t in degree h-1. Multiplication by powers of a functional
nonzero on v_t extends this to every degree f>=h-1. Applied to tensor powers,
these functionals prove the v_t^{tensor f} linearly independent for every
such f. The central-character tensor representation of A_f is then injective.

Therefore a literal endpoint at every positive column width would give the
forbidden algebra identity at every sufficiently large width. Coefficients,
controls, query blocks, and the finite owner counts m,s may depend on f within
the same fixed finite one-column alphabet. The argument is applied separately
at each sufficiently large f, so width-dependent coefficients do not help.
The finite checker corroborates formulas and grade supports; it does not
replace this all-width proof by a width-one matrix experiment.

## Exact advance and remaining boundary

PR4920's full-monomial grade theorem had exactly two owners and explicitly
excluded scratch mixing. PR4928 allowed identity scratch and simultaneously
transformed helper jobs, but only in a separated central/transverse algebra.
Neither result alone establishes this full-monomial joint-main-bank and
identity-scratch extension.
The new ingredient is (2)-(5), forcing decoupling via grades 1 through 16,
followed by the rank budget (7)-(8) and the simultaneous zero-column block.

The theorem includes arbitrary main/scratch owner mixing by L,W,R, all full
monomial central/fresh routes, all disjoint native shear orientations and
pairings, arbitrary joint mixing of all 2m original main owners, role-dependent
rank-eight raw factors, and arbitrary restored identity scratch. In particular,
m=112 permits joint control of the full 224-main-owner bank under the declared
native main interface. It excludes mixing the
productive native helper operations, native prefixes, altered FULLs, additional
paid nonmonomial calls, discarded main-dependent garbage, noninvertible global
owner controls without a reversible restored extension, and non-columnwise or
arbitrary width-specific address operations outside the fixed finite alphabet.
Already transformed helper input/output contracts cannot be replaced by the
identity-scratch contract without justification.

No new endpoint, invoice improvement, kappa, complete compiler replay, formal
proof-kernel verification, or independent human review is claimed.
