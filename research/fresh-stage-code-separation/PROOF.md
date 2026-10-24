# Fresh-stage code products retain a terminal obstruction

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The source code is from Dillon / PR4933 and Dugongue / PR4929.
Cinna Davis / PR5065 supplied the previous two-stage support theorem.

## 1. Statement and source contract

Fix k >= 1, independent of f. The binary address space is the direct sum of a common line E,
with basis vector e, and k private spaces V_s of dimension eight. Each stage
uses E + V_s and acts as the identity on all other private spaces. Each stage
occurs once. Its exponent a_s can be any nonzero integer. Stage order is free.

The 112 signed orthogonal monomial maps K_i and the rational matrix A are
exactly the source data in inputs/. Their binary parts G_i satisfy

    G_i e = q_i,       q_i != q_j for i != j,
    A^2 + 12 A = 13 I,       A_01 = A_10 = -1/2.

All G_i are orthogonal over F2. Define, at positive tensor width f,

    (C_s,f)_ij = A_ij (K_s,i^-1 K_s,j)^(tensor f),
    Q = (1+i) I/2 + (1-i) T_e/2,
    B_f = C_k,f^a_k ... C_1,f^a_1,
    J_f = Q^(-tensor f) B_f Q^(tensor f).

Each owner coefficient is applied once, outside the tensor power. Tensoring
the whole owner matrix would define a different operator.

**Theorem.** Any exact implementation of J_f by scalar ADD/SCALE, monomial
address maps, COPY and CLEAR has an ADD count g with

    g >= max(0, 2f - 24k).

There can be arbitrary mixing between owners and arbitrary owned workspace.
The instruction schedule is linear and does not depend on input values.
The scalar coefficients and monomial maps can depend on f. The bound still
excludes an ADD count that is constant in f. It also applies to B_f^-1,
because inversion reverses the distinct stages and negates their exponents.
It does not bound the minimum number of paid Gaussian calls.

For all sixteen negative-output banks in the saved PR4933 caller, the finite
marker certificates below give the stronger bound

    g >= max(0, 2f - 6).

Some banks have offset three. The previous two-stage offset two is stronger
for its two named banks and remains valid. No new kappa follows from these
bounds. A bound linear in f does not exclude a scalar algorithm with that
cost, an already-paid decoder, or a different recursive target type.

## 2. Ordered local binary maps have a unique factorization

Let H_s be the subgroup of GL(E + direct-sum V_t, F2) obtained by extending
GL(E + V_s, F2) by the identity. If F_s and F'_s belong to H_s and

    F_k ... F_1 = F'_k ... F'_1,

then F_s = F'_s for every s. To prove this, move the last factors to one side:

    (F'_k)^-1 F_k = F'_(k-1) ... F'_1 F_1^-1 ... F_(k-1)^-1.

The left side is supported on E + V_k. The right side is supported on E plus
the earlier private spaces. Their intersection is GL(E,F2). This group is
trivial because E is a binary line. The last factors are equal. Remove them
and repeat. This argument does not assume that the stages commute.

Fix an input owner j_0 and an output owner j_k. A path j_0,...,j_k has binary
map

    G_path = product_(s=k,...,1) (G_s,j_s^-1 G_s,j_(s-1)).

If two paths have the same map, the local factors are equal by the lemma.
At the last stage the output owner is fixed, so equality forces the two
previous G matrices to be equal. Their central images q_i are distinct,
so the previous owner is the same. Repeat backwards. Thus every owner path
has a different complete binary map, including paths with zero coefficients.
Signed monomial terms therefore cannot cancel after collection.

This is a statement about this ordered fresh-stage domain. It is not a
unique-factorization claim for arbitrary words in the generated groups.

## 3. A nonzero path survives every integer power

The polynomial for A gives, for every integer a,

    A^a = alpha_a A + (1-alpha_a) I,
    alpha_a = (1-(-13)^a)/14.

This follows by evaluating at the two distinct eigenvalues 1 and -13. It is
valid for negative a because both eigenvalues are nonzero. Alpha_a is nonzero
when a is nonzero. The same formula holds for C_s,f, since it is a block
monomial conjugate of A tensored with the identity on the address space.

Take the path j_s = s mod 2, starting at owner zero. Its coefficient is

    c = (-1/2)^k product_s alpha_a_s != 0.

At its first stage the map G_1,1^-1 G_1,0 sends e to a vector different from
e. The vector is nonzero. It therefore has a nonzero component in V_1.
Later stages cannot change that component. The complete G_path e differs
from e. This path has a unique binary map by Section 2.

The argument works for either parity of k. For even k the witness is in
owner block (0,0); for odd k it is in block (1,0). It need not use the same
owner block as the two-stage predecessor.

## 4. Four nonzero entries after central conjugation

Let M|x> = s(x)|Gx>, where s(x) is +1 or -1, and let G e != e. Direct expansion
gives

    2 Q^-1 M Q |x>
      = s(x)|Gx> - i s(x+e)|Gx+Ge>
        + i s(x)|Gx+e> + s(x+e)|Gx+Ge+e>.

The four destinations are distinct because e and Ge are independent.
Every coefficient has absolute value 1/2. The inverse map also moves e,
so application of this argument to the adjoint proves that each row has
four nonzero entries. This is the source's one-stage support argument.

Write N_path = Q^-1 M_path Q. In one fixed owner block,

    J_f = sum_path c_path N_path^(tensor f).

This is a finite sum for fixed k. There can be exponentially many paths.
The next step isolates one path without assuming that this sum is a tensor
power of its width-one value.

## 5. A coordinate contraction isolates a path

All binary maps G_path are orthogonal. Two such maps that agree on the
n-1 private basis vectors also agree on e, where n=8k+1. Indeed, the image
of e is the unique nonzero vector in the orthogonal complement of the
other n-1 orthonormal columns.

Let G_* be the selected path in Section 3. For each private basis vector
x_l, put y_l=G_* x_l and define a linear functional on base matrices by

    ell_l(N) = (Q N Q^-1)[y_l,x_l].

There are m=8k functionals. For each path, ell_l(N_path) is its signed
monomial entry M_path[y_l,x_l]. The selected path has value +1 or -1 at
every marker. Every other path has a zero marker. Contract the first m
tensor factors of J_f with these functionals. For f>=m the result is

    c_* eta N_*^(tensor (f-m)),       eta in {+1,-1}.

This is a proof operation. It is not a free physical projector or an
instruction that the caller can execute without charge.

Each ell_l is a sum of four entries of N, using at most two output indices
and two input indices. Fix any output row in the remaining factors. The
contraction uses at most 2^m actual rows of J_f. If each actual row has at
most S nonzero input coordinates, the contracted row has at most 2^m S
nonzero remaining input coordinates. Summing over marker input indices
cannot increase this union beyond S for each fixed actual row.

The isolated row has exactly 4^(f-m) nonzero entries. Consequently

    S >= 4^(f-m) / 2^m = 2^(2f-3m).

Every initial role row depends on at most one independent input coordinate.
A monomial map, SCALE, COPY or CLEAR cannot increase the maximum support.
Each binary scalar ADD increases it by at most a factor two. Thus S<=2^g,
and g>=2f-3m=2f-24k. For f<m the stated nonnegative bound is automatic.
This proves the theorem. It permits arbitrary cross-owner scalar work;
no source-preserving or two-read restriction was imposed.

## 6. Short certificates for the actual caller

A marker need not be a basis vector. Any inputs x_1,...,x_m that isolate the
selected path give the same bound g>=max(0,2f-3m). MARKERS.json records such
addresses. They were found by a deterministic bounded search; their validity
does not depend on the search or its seed.

The checker counts every surviving owner path by dynamic programming. At a
stage boundary its state is the current owner and the m central bits. Each
private input block is already fixed by the marker input. The stage must
produce the prescribed private output block. Those bits never change again.
The state then records the new owner and central bits. There are at most
112*2^m states per layer. Counts are exact nonnegative integers.

The transition domain includes every nonzero A edge and every diagonal edge.
It therefore contains the nonzero paths of every nonzero integer power,
regardless of signs. A final count of one proves that only the selected path
survives. A second computation runs backwards, using separately composed
inverse matrices instead of the forward literal K lookup tables. The small
complete path censuses check the coordinate contraction directly.

Every bank length in the source endpoint has a certificate with m<=2.
The longest negative bank has eighteen distinct stages. The source specifies
its endpoint as E_i=Q^-1 B_i D_i and its required Gaussian job as Q^-1 D_i.
Its unique postdecoder is Q^-1 B_i^-1 Q, which is covered by the theorem.
The saved endpoint and its source lineage remain premises: this package does
not replay or admit the full producer, compiler, or outer construction.

The theorem concerns decoding from the emitted bank and independent extra
inputs. Additional retained histories correlated with the original main
inputs can change that interface. Their complete charged consumer is outside
this theorem and remains an active research route.

## 7. Two explicit boundaries of the result

Repeated stages can cancel: C_s C_s^-1=I. Their factors do not have distinct
private supports, so Section 2 does not apply. This is an exact positive
control, not a claim that a profitable repeated-stage caller exists.

Two common axes also change the lemma. On four coordinates, let the common
space have axes 0,1, and let the two private spaces have axes 2 and 3. Put

    H=(0 1),       L=(0 3),       R=(0 2).

Here permutations denote binary permutation matrices. Both factorizations

    L R = (L H)(H R)

use the correct two local supports, but their local factors differ. More
concretely, choose K_t,0=K_s,1=I, K_t,2=L, K_s,2=R, and
K_t,98=L H, K_s,98=R H. The two intermediate-owner paths 2 and 98 have the
same signed monomial L R. Their port images are distinct within each named
stage. In the actual scalar code,

    A_02 A_21 = 1/4,       A_0,98 A_98,1 = -1/4.

These two terms cancel exactly, at every tensor width, even after conjugation
by Q. Each term alone is nonmonomial after that conjugation. The control uses
permutation lifts with sign +1, so it also checks absolute phase.

This is a concrete two-path cancellation under a changed interface. It is
not a completed 112-owner provider, a replacement for all the source port
normalizers, or a favorable paid invoice. The additional shared axis and its
producer, targets, restoration, and routing must all be charged. It identifies
an algebraic mechanism that the one-line theorem excludes, rather than a
new kappa improvement.
