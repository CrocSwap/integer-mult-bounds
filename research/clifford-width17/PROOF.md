# Dyadic interpolation of four-qubit Clifford tensors at width 17

Let `R = Z[i,1/2]`. Choose one Gaussian-dyadic unitary representative
`U_a` of each four-qubit Clifford coset modulo scalar powers of `i`.
Write `c_a = vec(U_a)/4` and let `A_f` have columns `c_a^(tensor f)`.
The convention `vec(U_a^(tensor f))/4^f` differs only by a coordinate
permutation. There are `N = 12,128,668,876,800` columns.

**Theorem.** At every integer width `f >= 17`, the recipe below gives a
matrix `B_f` over `R` such that `B_f A_f = I_N`. Each row of this
specified inverse has squared Euclidean norm `73,190,789,644,335,724`.
Using the reported spectral bounds of #7772, a finite dyadic iteration
gives another exact inverse with operator norm below `3.021`.
The proof also gives the exact complex independence threshold 17 for the
larger alphabet of *all* eight-qubit projective stabilizer states.
The four-qubit Clifford alphabet is a proper subset. Its least dyadic
width remains open between 13 and 17 inclusive, using the reported
complex threshold of [#7766](https://github.com/CrocSwap/integer-mult-bounds/pull/7766).

## 1. Recenter the target over the coefficient ring

Use computational labels `s,r in F_2^4` for the row and column of a
matrix. For a fixed target apply `U_a^* ⊗ I`, then the Bell-basis change

```text
D |s,r> = (1/4) sum_z (-1)^(r·z) |s+r,z>.
```

This is a reversible binary relabeling followed by four Hadamards on the
second register. Their combined coefficient is exactly `1/4`. Thus
`T_a = D(U_a^* ⊗ I)` is unitary, Clifford and Gaussian-dyadic.
It sends `c_a` to `e_0`, since the character sum of `(-1)^(r·z)` over
the sixteen values of `r` vanishes for every nonzero `z`. Each `c_b`
comes from the four Bell pairs `vec(I)/4` by a Clifford on the first
register. Hence `v = T_a c_b` is an eight-qubit stabilizer vector. Its
ray equals that of `e_0` precisely when `U_b` is proportional to `U_a`.
A scalar of modulus one in `R` is a power of `i`: if
`h²+j²=2^(2l)` with `l>0`, reduction modulo four forces both
`h,j` even, and descent gives the four units. Thus the chosen cosets
agree exactly in this case. With `a=b` the recentering gives `e_0`
with coefficient exactly one.

## 2. The phases on a stabilizer support

An eight-qubit stabilizer vector has support an affine subspace of
`V=F_2^8`. If it contains zero, its support is a linear subspace `A`
and the coefficients restricted to any independent directions
`b_1,...,b_k in A` have the form

```text
v_(sum_j t_j b_j) / v_0 = i^q(t),
q(t) = sum_j h_j t_j + 2 sum_(j<l) g_jl t_j t_l  (mod 4).
```

Here `h_j in Z/4`, `g_jl in F_2`, and the bits `t_j` are represented
by zero or one. To see this directly, project the eight-dimensional
binary stabilizer onto its Pauli X-shifts, with image `H` of dimension
`h`. The kernel consists of `8-h` independent diagonal Z constraints.
They restrict nonzero amplitudes to a coset of `H`, because their
labels annihilate `H` by commutation and have dimension `8-h`.
An operator with shift `b` transports every amplitude to its translate
by `b`, with a nonzero phase. The support is nonempty and is therefore
the whole coset. When it contains zero, select a stabilizer element
`i^c X^b Z^z` for each basis direction used above. Moving from zero
along these directions in a fixed order gives the product of the local
phases `i^c` and signs `(-1)^(z·x)` at the previously reached points
`x`. The resulting exponent has the displayed form. This derivation
also permits supports of dimension zero and arbitrary global phases.
The affine quadratic normal form is classical. See [Dehaene and De Moor,
Theorem 5](https://arxiv.org/abs/quant-ph/0304125).

## 3. One ordered monomial per binary subspace

Take the eight rows of a binary length-16 generator matrix `G` for
`RM(1,3) ⊕ RM(1,3)`. In each length-eight block use the evaluations of
`y_1,y_2,y_3,1`, in that order, on the eight binary triples. Each block has rank four.
Each row has weight four or eight and each pair of distinct rows has
even overlap. Distinct blocks have disjoint support.

For each linear subspace `K <= V` choose an ordered basis
`b_1,...,b_k`, for instance its reduced row-echelon basis. Using the
first `k` rows of `G`, form the sixteen coordinate labels

```text
x_t(K) = sum_(j=1)^k G_(j,t) b_j,       1 <= t <= 16,
M_K(v) = product_(t=1)^16 v_(x_t(K)).
```

The labels span `K`, since the selected rows are independent. If
`v_0 != 0` with support `A`, this monomial vanishes unless `K <= A`.
For `K <= A`, sum the phase exponent of Section 2 across the sixteen
columns. Each linear coefficient is multiplied by a row weight divisible
by four; each quadratic coefficient already has a factor of two and
is multiplied by an even overlap. Hence `M_K(v) = v_0^16`. At `k=0`
all sixteen labels are zero, as required.

Put `mu_k = (-1)^k 2^(k(k-1)/2)`, the Möbius coefficient from zero
to a `k`-dimensional binary subspace. Explicitly, if `A` has dimension
`r`, the binary Gaussian binomial identity gives

```text
sum_(K<=A) mu_dim(K) = product_(j=0)^(r-1) (1 - 2^j) = 1[r=0].
```

This identity also follows by induction on `r` from the Gaussian
binomial recursion. For `f >= 17` set

```text
P_f(v) = v_0^(f-16) sum_(K<=V) mu_dim(K) M_K(v).
```

If `v_0=0`, the positive exponent kills every term. Otherwise the
preceding sum gives `P_f(v) = v_0^f 1[A={0}]`. In particular,
`P_f(T_a c_b) = 1[a=b]`.

Use one **ordered** tensor coordinate for each term, consisting of
`f-16` zero labels followed by the listed sixteen labels. Put coefficient
`mu_dim(K)` on that coordinate and zero elsewhere, obtaining a row
`b`. Different `K` produce different words because their labels span
different subspaces. No symmetrization or factorial division occurs.
The row `b T_a^(tensor f)` evaluates the interpolant on the observation
coordinates of the normalized map. This applies the ordered-word lift
in recentered coordinates before the unitary change of basis.
Stacking the rows yields `B_f`
over `R`.

The number of subspaces in dimensions 0 through 8 is
`(1,255,10795,97155,200787,97155,10795,255,1)`. The disjoint tensor
coordinates and the unitarity of the recentering give

```text
||b T_a^(tensor f)||_2² = sum_(k=0)^8 [8 choose k]_2 2^(k(k-1))
                       = 73,190,789,644,335,724.
```

In particular, for Euclidean noise `e` on the normalized observations,
each recovered coefficient has error at most `||b||_2 ||e||_2`, and
`||B_f e||_2 <= sqrt(N) ||b||_2 ||e||_2`.

## 4. Exact dyadic stabilization

Fix `A=A_f` and start with `D_0=B_f`. The following corollary uses
the all-width spectral enclosure of Ali Romman's [#7772, pinned
proof](https://github.com/aliromman/integer-mult-bounds/blob/1398fbdca3536389d8ac3c8b3aaa408f03e8f6c2/research/clifford-threshold-conditioning/PROOF.md);
the interpolation theorem itself is independent of those spectra.
For `G=A* A` its two bounds are `l=470624175/2^32` and
`u=7841980575/2^30`. Apply the classical Landweber (Richardson
normal-equation) iteration with dyadic step:

```text
H = I - G/4,
D_(j+1) = H D_j + A*/4.
```

Every entry remains in `R`. If `D_j A = I`, then `D_(j+1) A = H+G/4=I`,
so each iterate is already an exact left inverse. The complex canonical
inverse `A^+ = G^(-1) A*` is a fixed point. Consequently
`D_j-A^+ = H^j (D_0-A^+)`. Since `1/16 < l <= u < 15/2`,
`||H||_2 < 63/64`. Section 3 and `||A^+||_2 <= 1/sqrt(l)` give
`||D_0-A^+||_2 <= sqrt(N) ||b||_2 + 1/sqrt(l) < 2^50`.
As `(64/63)^64 >= 1 + 64/63 > 2`, the choice `j=8192` yields
`||D_j-A^+||_2 < 2^-78`. For the numerical margin,
`302095² × 470624175 - 100000² × 2^32 = 142959244679375 > 0`.
Thus `||D_j||_2 < 302095/100000 + 2^-78 < 3.021`. This bound applies
to arbitrary Euclidean perturbations of the normalized observations.
The huge Gram multiplication and its precision, storage, movement and
restoration costs have no complete caller invoice here.

## 5. Sharpness for all eight-qubit stabilizer rays

Clifford transitivity sends any target stabilizer ray to that of
`e_0`. For example, reverse a stabilizer preparation circuit; when a
dyadic gate lift is desired, a single Hadamard can be rephased as
`(1+i)/2 * [[1,1],[1,-1]]`. The same polynomial then separates each target
from all other stabilizer rays; rescale its nonzero target value to one.
Thus their tensor columns are independent for `f >= 17`.

Suppose a degree-16 homogeneous polynomial separated `e_0` from every
other stabilizer ray with target value one. Any smaller-degree separator
could be padded by a power of `v_0` to meet this premise. Average the
polynomial over all diagonal Clifford phases `i^q(x)` of Section 2
on the full space `V`. These fix `e_0` and permute stabilizer rays,
so the average is still a separator. The phase generators allow every
linear coefficient modulo four and every cross sign independently.
For a degree-16 monomial with binary coordinate labels `x_1,...,x_16`,
the average survives only if each coordinate row of its `8 × 16`
label matrix has weight divisible by four and each pair overlaps evenly.
These rows and the length-16 all-ones row therefore span a self-orthogonal
binary space of dimension at most eight. The affine dimension of the
sixteen labels is the rank of this augmented matrix minus one. It is
at most seven.

For every nonempty affine subspace `A`, its indicator vector is
proportional to a stabilizer state: prepare a uniform superposition on
independent coordinates, extend its basis by an invertible binary map,
and translate. Evaluating a surviving monomial on this indicator gives
`1[F contained in A]` where `F` is the affine span of its labels.
Thus the averaged polynomial would express `1[A={0}]` as a combination
of these incidence functions with `dim F <= 7`. On the finite poset of
nonempty affine subspaces the full incidence matrix is unit triangular
in any inclusion-respecting order. Its expansion is unique. The
coefficient on `F` in the desired expansion is zero if `0` lies outside
`F` and `mu_dim(F)` otherwise, by the sum in Section 3. In particular
the coefficient on `V` is `2^28`, a contradiction. This proves the
stated threshold for the enlarged alphabet. The diagonal phases in this
argument can move a Clifford Choi ray outside the recentered Choi set.
Consequently this lower bound supplies no obstruction at widths 13–16
for the four-qubit problem.

## Attribution

The zero-quadratic-phase tuple method and its relation to doubly even
codes were developed in the project by Ali Romman and Nick Petalas.
The proof above uses their witness-code idea for an interpolation
problem, together with classical Möbius inversion and the stabilizer
normal form. [Nine-axis proof #5635](https://github.com/CrocSwap/integer-mult-bounds/pull/5635)
and [zero-phase witness lengths #5902](https://github.com/CrocSwap/integer-mult-bounds/pull/5902).

Ali Romman supplied the four-qubit canonical odd-denominator obstruction,
building on the Clifford work of alephnan and the character projections
of Nick Petalas. The earlier dyadic inverse of apoursh provided the
width-256 handoff. Those results retain their respective attribution.
[Canonical decoder #7792](https://github.com/CrocSwap/integer-mult-bounds/pull/7792)
and [prior interpolant #7797](https://github.com/CrocSwap/integer-mult-bounds/pull/7797).
Gross, Nezami and Walter describe the complex span projector for stabilizer
tensor powers in [Theorem 5.6](https://arxiv.org/abs/1712.08628).
Chang, Caro, Larocca and West use the quadratic-phase characters in their
[Eqs. 7–9](https://arxiv.org/html/2609.10974v1), and Nebe, Rains and
Sloane relate Clifford invariants to [self-dual code weight
enumerators](https://arxiv.org/abs/math/0001038).
We make no literature-priority claim for the complex threshold.
Prepared by **apoursh** with substantial OpenAI Codex and separate agent
assistance. Apache-2.0.
