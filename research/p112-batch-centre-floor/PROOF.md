# A direct-sum P112 copy-rank theorem

## 1. Fixed geometry and cost model

Let X be the 112-by-8 live P112 root matrix in norm-four, frame-adapted
Hamming coordinates. The full set has eight coordinate lines `2 e_j` and
112 signed affine-plane root lines; P112 deletes the coordinate lines.
One representative of each line is chosen. The checker gives an explicit
scaled orthogonal map from standard doubled E8 roots and their deleted
frame, checking `2 h(q) dot h(q') = q dot q'` before line-sign normalization.
The normalized Gram pairing is preserved.

For the full 120-line set define

    B_ij = 1 + (x_i dot x_j)/2  (mod 2).

All dot products are even. B is symmetric of rank nine. Its rows define
labels ell_i in a nine-dimensional binary space V, with a well-defined
nondegenerate symmetric pairing `b(ell_i,ell_j)=B_ij`. Indeed symmetry makes
row dependencies column dependencies, and a label pairing to zero with all
generators is the zero row. An arbitrary chosen nine-bit coordinate chart
need not make b the standard dot product.

For live index sets S,T let `rho(S,T)=rank_F2 B[S,T]`. This depends only on
their label spans and cannot decrease on enlarging either set. Every call
uses this **same** puncture, chart and pairing.

For p output blocks, q input blocks and `C in C^(p x q)`, require the
all-pairs matrix `G_C=C tensor (X X^T)`. Let `X_p=I_p tensor X` and similarly
X_q. A root-code factorization satisfies

    D T^T = G_C,
    col(D) subset col(X_p),   col(T) subset col(X_q).

Coefficients are arbitrary complex numbers and transpose is **ordinary**
transpose. Discard a term if either column is zero. For each active term j,
S_j and T_j are the unions of its nonzero live rows over all output and
input blocks, respectively. Charge the term `rho(S_j,T_j)`, once, regardless
of how many calls it touches. The total charge is their sum.

This is an explicit algebraic objective that forgets call identity.
Interpreting it as a physical lower bound requires a corresponding
separate-total copy/delivery interface; no assertion about arbitrary
interacting circuits is built into the definition. Inputs in different
blocks are independent variables, even if the requested C is singular.

## 2. Finite support lemma, with predecessor credit

The fixed P112 support classification is due to Mihir Srivastava's PR845;
Adam Gall's PR1098 independently certifies it with Gram spectra. Our two
checkers re-establish the following finite premises without importing those
executables or invoking a Weyl-flat classification theorem.

For each of all 511 nonzero linear functionals h on V, form the matrix of
live roots with `h(ell_i)=1`. Exactly 503 matrices have rational rank eight.
The other eight have rank seven with kernels the eight coordinate lines,
each once. Write E_j for the live support of `X e_j`. Each E_j contains
56 roots and spans eight label dimensions. All 64 ordered pairs satisfy
`rho(E_i,E_j)=8`.

The rank statements use exact witnesses. Nonzero rational minors remain
nonzero over C, and rational null vectors remain null vectors. Thus all
ranks and one-dimensional kernels hold over C. This enumerates binary
hyperplanes of the **label space**, not all complex coefficient directions.

**Support lemma.** For any nonzero `a in C^8`, the support of Xa has full
label span V or is exactly E_j for some j.

X has rank eight, so Xa is nonzero. If its support span is proper, choose
a nonzero h vanishing on it. Every live root outside ker(h) annihilates a.
A rank-eight complement would imply a=0. Hence this is one of the eight
rank-seven cases, so `a=c e_j` with c nonzero and its support is E_j.
This includes complex isotropic a; positivity or nonisotropy is not used.

**Pair lemma.** Any two nonzero complex root-code supports pair with rank
at least eight. If both are exceptional this is the 64-entry check. If one
spans V, nondegeneracy of b gives rank equal to the dimension of the other
span, which is eight or nine.

## 3. All-batch lower bound

A nonzero column of col(X_p) has a nonzero block Xa. Its union support
contains that block's support. Choose a nonzero block Xc in the other
factor. The two block-support pairing matrix is a submatrix of the two
union-support pairing matrix. The pair lemma and rank monotonicity show
that **every active term costs at least eight**, even when the chosen
blocks have different call indices.

Exact geometry gives `X^T X=56 I_8`, hence `rank(XX^T)=8` over C. For
r=rank(C), the Kronecker-product rank identity yields `rank(G_C)=8r`.
Equivalently, use the full-rank left/right inverses of X_p and X_q on
`G_C=X_p (C tensor I_8) X_q^T`. A sum of m rank-one outer products has
rank at most m. Thus

    m >= 8r,        total charge >= 8m >= 64r.               (1)

For independent calls C=I_k, this is m>=8k and charge at least 64k.
This is an all-size proof after a fixed finite premise; finite fixtures do
not substitute for the quantified argument.

## 4. Attainment and exact coupling-rank law

Choose a rank factorization `C=sum_(l=1..r) u_l v_l^T`. For every l and
j=1,...,8 take

    d_(l,j) = u_l tensor (X e_j),
    t_(l,j) = v_l tensor (X e_j).

Their outer products sum to G_C. Each u_l and v_l is nonzero, so both union
supports are exactly E_j. Each term costs eight. These 8r terms attain 64r;
for C=0 the empty factorization attains zero. Therefore

    minimum copied-pairing-rank charge = 64 rank(C).          (2)

**Exact charge and equality cases.** Call a nonzero block-root-code column
coordinate-aligned if it is `u tensor (X e_j)` for some nonzero call vector u
and one root coordinate j. The support lemma and injectivity of X show that
its union support spans an exceptional hyperplane exactly in this case.
Otherwise some block has full span V, or two blocks have distinct
exceptional hyperplanes, whose union spans V. The eight hyperplanes are
distinct because the finite census identifies each with a distinct nonzero
functional. Taking unions does not cancel coefficients across calls.

The complete pairing table is therefore 8 for exceptional/exceptional or
exceptional/full, and 9 for full/full. For any factorization in the stated
root-code model, let b count active terms where **neither** factor column
is coordinate-aligned. Its exact cost is

    total charge = 8m + b.                                  (2a)

Among exact factorizations of G_C with r>0, optimum 64r holds if and only if
`m=8r` and b=0. Either side may supply the aligned column term by term;
both sides need not align. Alignment is not a substitute for checking the
full endpoint identity. The fixture with one two-sided nonaligned term
has exact cost 65, while a mixed two-call equality fixture still costs 128.

This is algebraic attainment only. Arbitrary complex call coefficients do
not come with free preparation, arithmetic, routing or restoration.

For C=I_2 the outputs request `XX^T x_0` and `XX^T x_1`, separately, and
require 128. For the two-by-two all-ones C, both request `XX^T(x_0+x_1)`,
and the minimum is 64. Substituting the latter for the former introduces
nonzero off-diagonal blocks; the verifier rejects this endpoint mutation.

## 5. Minimum-term factors are automatically in the code

Suppose r>0 and an unrestricted exact factorization of G_C has exactly 8r
columns. Both factors have rank 8r. Since `col(G_C) subset col(D)` and
their dimensions coincide, the two spaces are equal; likewise
`col(G_C^T)=col(T)`. These spaces lie in col(X_p), col(X_q), respectively.
Both code hypotheses follow, with no conjugate transpose argument needed.

Thus (1) covers every minimum-term factorization, including arbitrary
cross-call basis changes. This implication fails for overcomplete factors;
their two code hypotheses remain explicit.

## 6. Moment consequence and necessary escape invoice

For independent calls, under a one-child-per-total interface at its pairing
rank, every nonnegative increasing per-child function f obeys

    sum_j f(rho_j) >= m f(8) >= 8k f(8).

This includes `f(s)=(s/M)^(1-a)` for fixed parent width M and a<1. Changing
the root-code factorization cannot improve the centre-only moment. Changes
to volume, other local children, coverage or the physical contract require
separate pricing; positive added interface costs cannot rescue this route.

An unrestricted independent-call decoder with charge at most 64k-1 must
have m>=8k+1, at least one column outside its respective block-root code,
and

    sum_j (8-rho_j) >= 8(m-8k)+1.                             (3)

The last line just rearranges `sum rho_j <=64k-1`. At least one term has
rank at most seven; ranks above eight count against the savings. For k=2,
m=17 requires at least nine net units. These are necessary conditions,
not sufficient ones, and do not exclude general outside-code factorizations.

## 7. Limits

The fixed P112 puncture, common chart, all-pairs endpoint and separate-total
union price are material. Masked identities, changed charts, temporal
source relations, interacting delivery, arbitrary frames and outside-code
overcomplete factors are not covered. Singular C changes the requested
map; it does not merge independent endpoint obligations for free.

The finite premises have exact executable witnesses and separate checks.
This all-size argument is a written proof, not a Lean theorem or human
peer review. No selected global schedule or frontier is modified. Source
and predecessor credit are in README.md and SOURCES.json.
