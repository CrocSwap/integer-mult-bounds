# Exact ternary disjointness repair in every even dimension

Let F be any field of characteristic three. For an integer h >= 2, let
A_h be the matrix indexed by the nonempty proper subsets of [h], with
entry 1 precisely when its row and column subsets are disjoint. Write
B_h = I - A_h, of size v = 2^h - 2.

**Theorem.** For every even h >= 4,

$$
 d_h=2^{h-2}+(-1)^{h/2}2^{h/2-1},\qquad
 \dim_F\ker B_h=d_h-1,
$$
$$
 \operatorname{rank}_F B_h
 =3\cdot2^{h-2}-1-(-1)^{h/2}2^{h/2-1}.
$$

At h=2 the rank is 1. Consequently, the minimum number of arbitrary
additive scalar rank-one terms repairing A_h to I is the displayed rank.

Nick Petalas's [PR #5173](https://github.com/CrocSwap/integer-mult-bounds/pull/5173)
proves the full-rank result for odd h and gives the h=2 boundary example.
This settles its explicitly open even-h >= 4 question. The tensor/deletion
approach follows Ali Romman's binary [PR #4962](https://github.com/CrocSwap/integer-mult-bounds/pull/4962).
The new work is the singular characteristic-three endpoint restriction and
the resulting exact all-even-dimensional formula. The formulas count
algebraic terms, not paid physical operations.

## 1. Full tensor kernel

Include the empty and full subsets, denoted 0 and f. The full disjointness
matrix and its identity repair are

$$
 K=\begin{pmatrix}1&1\\1&0\end{pmatrix},\qquad
 T=K^{\otimes h},\qquad M=I-T.
$$

All entries lie in F3. Rank is preserved by extension of the coefficient
field, as characterized by nonzero minors. Thus it is enough to calculate
over F9; the same rank then holds over F3 and every characteristic-three
field F, whether or not F contains F9.

In F9 choose a root alpha of x^2-x-1. The other root is beta=1-alpha=alpha^3.
The roots are distinct, alpha^4=-1, and alpha has order eight. The two
vectors (alpha,1)^T and (beta,1)^T form an eigenbasis of K. Their tensor
products form an eigenbasis of T. A tensor with k beta factors has
eigenvalue alpha^(h+2k), and hence belongs to ker M exactly when

$$
 h+2k\equiv0\pmod8.
$$

It follows, as an **integer multiplicity count**, that

$$
 d_h=\dim\ker M
 =\sum_{\substack{0\leq k\leq h\\k\equiv-h/2\ (4)}}\binom hk
 \quad(h\text{ even}).
$$

This is not an inference from a trace reduced modulo three. For completeness,
the ordinary complex fourth-root filter evaluates this integer binomial sum.
Set h=2m and take i in C. Then

$$
 d_h=\tfrac14\bigl(2^h+i^m(1+i)^h+(-i)^m(1-i)^h\bigr)
 =2^{h-2}+(-1)^m2^{m-1},
$$

because (1+i)^(2m)=2^m i^m and its conjugate has the same real contribution.
The omitted fourth term is 0^h=0. In particular d_2=0, whereas d_h>0
for every even h>=4.

Every tensor eigenvector of eigenvalue one has coordinate 1 at f and
coordinate alpha^(h+2k)=1 at 0. Therefore

$$
 x_0=x_f\quad\text{for every }x\in\ker M.
$$

For h>=4, evaluation x -> x_0 on ker M is nonzero: any one of those
eigenvectors has value 1. Consequently the subspace of ker M vanishing
at both endpoints has dimension d_h-1. It remains to prove that it is
exactly the kernel of the interior principal block; endpoint deletion
alone does not imply this.

## 2. Singular endpoint restriction

The explicit local powers in characteristic three are

$$
 K^2=\begin{pmatrix}2&1\\1&1\end{pmatrix},\qquad K^4=-I.
$$

For even h, T^4=I. Define two polynomial operators

$$
 P=I+T+T^2+T^3,\qquad G=T^2-T.
$$

They satisfy

$$
 MP=0,\quad P^2=P,\quad MG=GM=I-P.
$$

Indeed P acts as 4=1 on the eigenvalue-one subspace and as zero on
the other eigenspaces. Alternatively the identities follow by polynomial
multiplication using T^4=I and 3=0. In particular P projects onto ker M.

Let E=(0,f). At those endpoints a tensor-power entry is the h-th power
of the corresponding local entry. As h is even,

$$
 T_{EE}=\begin{pmatrix}1&1\\1&0\end{pmatrix},\quad
 (T^2)_{EE}=\begin{pmatrix}1&1\\1&1\end{pmatrix},\quad
 G_{EE}=\begin{pmatrix}0&0\\0&1\end{pmatrix}.
$$

Take y in ker B_h, and extend it to a full vector z with z_0=z_f=0.
The interior coordinates of Mz vanish. Choose a full-kernel eigenvector
x with x_0=x_f=1, which exists for h>=4. Since M is symmetric,

$$
 0=(Mx)^Tz=x^TMz=(Mz)_0+(Mz)_f.
$$

Thus Mz=a(e_0-e_f) for some scalar a. Apply G and the polynomial
identity to obtain

$$
 z=aG(e_0-e_f)+Pz.
$$

Put w=Pz. Since w is in ker M, w_0=w_f. The two endpoint coordinates
of the last display give

$$
 0=w_0,\qquad 0=-a+w_f.
$$

Therefore a=0, and z itself belongs to ker M. Conversely any full-kernel
vector vanishing at E restricts to a vector in ker B_h. Restriction and
zero extension are inverse linear maps between these kernels, proving

$$
 \dim\ker B_h=d_h-1.
$$

Subtracting from 2^h-2 proves the rank formula. The argument establishes
the deletion step without assuming that the singular full matrix has an
inverse or that a principal submatrix keeps its nullity.

## 3. The small boundary and the repair count

For h=2, d_h=0, so the eigenvector used in the deletion proof does not
exist. The literal interior matrix is

$$
 B_2=\begin{pmatrix}1&-1\\-1&1\end{pmatrix},
$$

of rank one. Extending the h>=4 formula to h=2 would incorrectly give
rank three for a two-by-two matrix. This boundary is retained from #5173,
not claimed as a new result.

If A_h+sum_{j=1}^ell u_j v_j^T=I, subadditivity of rank implies
ell>=rank B_h. Conversely every rank-r matrix has a rank factorization
B_h=UV with U having r columns and V having r rows. Expanding this
product gives r rank-one summands. The factorization can be constructed
over F3 and remains valid over every F. Thus the lower bound is attained
in the stated unrestricted additive algebraic model.

## Scope and proof status

This is a written all-even-dimensional proof, corroborated by bounded
exact finite calculations. The finite checks do not prove the universal
quantifier; independent human review and formal proof-kernel acceptance
remain unclaimed.

No native ternary supplier, paid COPY/read count, coefficient-preparation
method, dirty-restoration contract, frame/hosting construction, precision,
fixed-tape/compiler bound, recursive invoice or new multiplication exponent
is supplied. In particular the binary ledger in #4962 is not transferred
to characteristic three, and no nonadditive repair is excluded.

Krzysztof Wojt, with substantial OpenAI Codex assistance. Apache-2.0.
