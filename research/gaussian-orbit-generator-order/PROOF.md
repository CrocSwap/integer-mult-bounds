# Ordinary Toeplitz generators after ordering invariant kernels by orbits

This is an all-size representation upper bound and an explicit scope correction
to a lexicographic lower bound. It is not a fast multiplication algorithm, an
all-order minimum, or an assumption discharge. All matrices below are finite.
The field may be R or C; transpose means algebraic transpose. The concrete
Gaussian claims use real `0<q<1`.

Sections 1--2 also support the stronger prime-block family proved in
[PRIME-ORBITS.md](PRIME-ORBITS.md). Sections 3--7 below concern complemented
rotation. Prime rotations do not require even n or centrosymmetry and
directly preserve already matched shifted factors.

## 1. Invariant kernels and ordinary shifts

Let X be a set of T labels, let a be a permutation of X with c cycles, and let
K be a matrix indexed by X satisfying

\[
                 K(ax,ay)=K(x,y) \qquad(x,y\in X).                 \tag{1}
\]

Choose one representative per cycle, list each entire cycle successively by
applying a, and concatenate the lists. Call the resulting order
`v_0,...,v_(T-1)`. Let S be the c positions at which cycles start; in
particular `0 in S`. Set `M_ij=K(v_i,v_j)`. Let Z be the ordinary strict lower
shift of size T, with `Z_(i,i-1)=1` for `1<=i<T`, and put

\[
                         E=M-ZMZ^{\mathsf T}.                     \tag{2}
\]

**Theorem 1 (orbit-start support).** E is zero outside the rows and columns
indexed by S. Hence

\[
                \operatorname{rank}E\le\min(T,2c).               \tag{3}
\]

**Proof.** If `i,j not in S`, both are positive and their predecessors stay
inside their respective cycles. Thus `v_i=a v_(i-1)` and
`v_j=a v_(j-1)`. By (1), `M_ij=M_(i-1,j-1)`, exactly the entry subtracted
in (2). A matrix supported on c rows and c columns has rank at most 2c:
with `Q=sum_(s in S) e_s e_s^T`, its exact decomposition is

\[
 E=QE+(I-Q)EQ
  =\sum_{s\in S} e_s E_{s,:}
    +\sum_{s\in S} ((I-Q)E_{:,s})e_s^{\mathsf T}.                 \tag{4}
\]

Each summand has rank at most one. This does not require equal cycle lengths,
symmetry, positivity, Toeplitz factors, or an efficient method for obtaining
the entries. It counts a start even when its actual displacement happens to
vanish, so equality in (3) is not claimed. QED.

**Inverse target.** If K is invertible, its inverse also satisfies (1).
Indeed the permutation matrix A of a obeys `A K A^T=K`; invert this identity
using `A^-1=A^T`. Apply Theorem 1 to `K^-1`, in the same order. Consequently

\[
 \operatorname{rank}(M^{-1}-ZM^{-1}Z^{\mathsf T})\le2c.            \tag{5}
\]

No inverse-displacement orientation transfer or tensor persymmetry is needed
for (5); it follows from the same actual permutation symmetry.

## 2. Explicit ordinary Toeplitz generators

For column vectors u,v of length T, let L(u) be lower triangular Toeplitz
with first column u and U(v) be upper triangular Toeplitz with first row
`v^T`. Direct matrix multiplication gives

\[
 L(u)U(v)=\sum_{k=0}^{T-1} Z^k u v^{\mathsf T}(Z^{\mathsf T})^k,
 \qquad E(L(u)U(v))=uv^{\mathsf T}.                              \tag{6}
\]

The inverse of the linear map `E(X)=X-ZXZ^T` is the finite sum in (6),
because the T-th power of Z is zero. Substitute each rank-one term of (4)
into (6). This gives M as a
sum of at most 2c ordinary `L(u)U(v)` products, with generators read directly
from its displacement's start rows and columns. The same holds for `M^-1`.

The familiar equality between minimum generator count and rank E follows as
well: (6) proves every k-term representation has displacement rank at most k;
an exact rank factorization of E and the finite inverse sum give a rank(E)-term
representation. The package uses the concrete 2c-term construction (4), not
an uncharged numerical rank factorization.

In (4), one vector of each pair is a coordinate vector. Thus one triangular
Toeplitz factor of each term is a shift, which may be stored implicitly. The
other 2c vectors still have length T; section 6 charges their representation.

## 3. Even-dimensional centrosymmetric tensor blocks

Let n be even and at least 2. Write `j*=n-1-j` for label reversal, and let B
be any n-by-n centrosymmetric matrix:

\[
                      B_{i^*,j^*}=B_{ij}.                       \tag{7}
\]

Let ell be a positive power of two. On the ell selected coordinates define

\[
 a(x_1,\ldots,x_\ell)=(x_2,\ldots,x_\ell,x_1^*).               \tag{8}
\]

It fixes all spectator labels. We allow

\[
                         K=B^{\otimes\ell}\otimes C,            \tag{9}
\]

where C is any square matrix on a finite spectator label set of size m.
Put `T=n^ell m`. There need not be a tensor structure or a reversal symmetry
on C. Formula (8) preserves (9): rotate the equal B factors and use (7) on
the wrapped factor. Therefore (1) holds.

**Lemma 2 (cycle length).** Every cycle of (8) has length `2ell`.

**Proof.** Applying a ell times reverses every selected label, and applying
it `2ell` times is the identity. Thus every cycle length divides `2ell`.
Since `2ell` is a power of two, each proper divisor divides ell. A point of
shorter period would therefore be fixed by `a^ell`. But n is even, so label
reversal has no fixed label, and `a^ell` has no fixed point. Contradiction.
The argument also covers ell=1. Spectators do not change the period. QED.

There are exactly `c=T/(2ell)` cycles. Theorems 1 and (6) prove:

**Corollary 3.** The orbit order gives ordinary Stein rank and ordinary
Toeplitz generator count at most `T/ell` for K, and also for `K^-1` if K is
invertible. This is an explicit order, the same for forward and inverse.

The binary version of (8) and its equal-cycle fact are classical: Gregor,
Merino and Mütze, *The Hamilton Compression of Highly Symmetric Graphs*,
[DOI 10.1007/s00026-023-00674-y](https://doi.org/10.1007/s00026-023-00674-y),
section 3.3, equation (13), Lemma 3.4. Their use concerns symmetric Hamilton
cycles. We credit that construction; our orbit-concatenated order need not
be a Hamilton path of the cube. The contribution here is its ordinary
generator consequence, even-n/spectator scope, and cost boundary.

## 4. Gaussian specialization and comparison with lexicographic order

Let

\[
                 B_{ij}=q^{(i-j)^2},\quad 0<q<1,\quad0\le i,j<n.\tag{10}
\]

This is centrosymmetric and invertible. For a direct proof of invertibility,
write `B=D V D`, with `D_ii=q^(i^2)` and `V_ij=(q^(-2i))^j`.
The nodes `q^(-2i)` are distinct, so the Vandermonde determinant is nonzero.
This uses exact coefficients and no truncation or numerical test.

For `H=B^tensor d`, take ell to be the largest power of two at most d and
put the remaining factors into C. Then `T=n^d` and Corollary 3 gives

\[
 \min_{P\ \mathrm{permutation}}
 \operatorname{rank}(PHP^{\mathsf T}-ZPHP^{\mathsf T}Z^{\mathsf T})
       \le {T\over\ell},                                       \tag{11}
\]

and the same upper bound for the inverse target. The exact lexicographic
rank from the [predecessor at 326844a](https://github.com/CubeJerry/integer-mult-bounds/tree/326844a3e0c570fdafa4f3737095cd37154743a6/research/tensor-gaussian-displacement-rank)
is `2T/n` in every axis order. Consequently the available bounds are
`min(2T/n,T/ell)`; when `2ell>n`, the second one certifies a strictly smaller
generator representation. Its guaranteed improvement factor over the
lexicographic minimum is at least `2ell/n`, unbounded when `d/n` grows.
This compares different physical orders, not the same displacement operator.

For n=2, (10) is the Hamming kernel `H_d(x,y)=q^dist_H(x,y)`. At d=4, the
explicit lexicographically chosen orbit representatives give the order

```
0, 1, 3, 7, 15, 14, 12, 8,  2, 5, 11, 6, 13, 10, 4, 9
```

with starts 0 and 8. Its forward and inverse ranks are at most 4 for every
`0<q<1`; at q=1/2 exact rational elimination certifies equality. The
lexicographic rank is 16. The verifier also checks q=2/3 and q=4/5, but those
finite cases do not assert equality for every real q.

The [rounding-margin predecessor at 575491d](https://github.com/CubeJerry/integer-mult-bounds/tree/575491d5fc353eac26010e45e9ced60fc9870017/research/gaussian-generator-rounding-margin)
concerns the fixed lexicographic shift. Equation (11) does not contradict its
robust lower bound: a general P does not commute with Z.

**Structured rounding.** Replacing every selected B by one common
centrosymmetric table preserves (7)--(11), for the forward target even if
the table is singular. For the inverse, nonsingularity must be proved
separately. Applying a deterministic scalar rounding rule to the equal
entries of B, then reusing that one table on all selected axes, preserves
centrosymmetry exactly. Independent unequal factor tables or arbitrary
unstructured perturbations of the full tensor need not preserve it.

## 5. Complemented rotation on shifted kernels: a paid factorization

The source's normalized shifted Gaussian is
`B(v)_ij=q^((i-j)^2) v^(i-j)`. With
`D(v)=diag(1,v,...,v^(n-1))`, `v>0`, direct entry multiplication gives

\[
 B(v)=D(v)B(1)D(v)^{-1},\qquad
 H_{\boldsymbol v}=D H_{\boldsymbol1}D^{-1},\quad
 D=\bigotimes_i D(v_i).                                         \tag{12}
\]

Let P be the orbit permutation for the common unshifted factors and set
`M=P H_1 P^T`. Then

\[
 H_{\boldsymbol v}=D P^{\mathsf T} M P D^{-1},\qquad
 H_{\boldsymbol v}^{-1}=D P^{\mathsf T} M^{-1}P D^{-1}.           \tag{13}
\]

This allows different shifts on otherwise matched factors as an algebraic
factorization. It does not assert a small ordinary displacement for the
shifted H itself. Its diagonal factors are separate operators; their
precision, physical access and intermediate magnitudes must be paid.

For positive diagonal parameters v_i, their exact spectral condition number is

\[
 \log\operatorname{cond}_2(D)
       =\sum_i(n_i-1)|\log v_i|.                                \tag{14}
\]

Indeed the largest and smallest diagonal entries independently choose the
appropriate endpoint of each tensor factor. Centering the diagonal by a
scalar changes neither the condition number nor (14).
If the unshifted core error F satisfies `||F||_2<=eta`, (13) gives external
error at most `cond_2(D) eta`. This amplification is sharp for arbitrary
norm-bounded errors: choose a matrix unit between a maximal and minimal
diagonal position. Thus a black-box normwise error guarantee must budget
`log_2 cond_2(D)` additional bits. This is not a lower bound for methods
that exploit a smaller structured error class.

For the normalized form
`exp(-gamma u^2+2 gamma s u)`, one has `v=exp(2 gamma s)` (up to the harmless
choice of orientation u=i-j or j-i), and

\[
 \log\operatorname{cond}_2(D)
            =2\sum_i\gamma_i|s_i|(n_i-1).                      \tag{15}
\]

For example, suppose ell matched factors have common n, `|s_i|>=s_0>0`,
and `gamma_i>=c/log p`, with fixed positive c,s_0. Then a linear-in-p
black-box normwise precision budget requires
`ell(n-1)/log p=O(p)`. A strict improvement from the displayed rank upper
bound over the lexicographic value requires `ell>n/2`. Together, these
necessary conditions imply `n(n-1)/log p=O(p)`. If `n` grows like `p^xi`
with fixed `xi>1/2`, that implication fails as p tends to infinity.
This excludes that specific fixed-shift, normwise diagonal-conversion
argument at the displayed cap; it does not exclude other layouts, other
error models, or stable algorithms without that conversion.

The matched nonzero-shift premise in this example is explicit and is not
asserted to hold for every source block. The retained
`GAUGEFREE-INTERIORS.md`, sections 0, 2 and 5, deliberately absorbs the linear
gauge into a shifted kernel and retains a smaller chirp range. Returning to
(12) must not silently reintroduce that discarded linear range for free.
The current package establishes no source-faithful restoration of all shifted
blocks at the original Cp precision.

## 6. Constructibility and the complete costs left to pay

### 6.1 Uniform enumeration and reversible transport

An explicit order does not require an oracle for cycle representatives.
For `X={0,...,n-1}^d`, enumerate each label x in lexicographic order. Compute
`x,a x,...,a^(2ell-1)x`; accept x precisely when it is the least of those
labels. For each accepted x, output its entire orbit in that sequence.
Lemma 2 proves that exactly one representative per orbit is accepted and
that no output label repeats. This is uniform in n,d.

Labels occupy `b_label=d ceil(log_2 n)` bits, which is within a constant
factor of `log_2 T` for n>=2. Rotating one label, subtracting its wrapped
digit from n-1, and comparing two labels can each be done by sequential
scans in `O(b_label)` bit steps on a fixed number of work tapes. Testing
all `2ell` powers for every label and then writing the accepted orbits
therefore takes `O(T ell b_label)` bit steps, with `O(b_label)` scratch
besides its output. It does not use a T-entry random-access visited array.
The verifier compares this direct-power construction with a separate
visited-set orbit enumeration only as a bounded correctness control.

For records carrying b payload bits, one conservative transport construction
is as follows. Emit `(old_label,new_position)` for every label in orbit order;
sort by old_label; merge with the lexicographic input stream; then sort the
resulting `(new_position,payload)` records by new_position. The inverse uses
the inverse pair of labels in the same way. A bottom-up merge sort on a fixed
number of tapes has `O(log T)` passes. Each pass reads and writes
`O(T(b+b_label))` bits and performs O(T) comparisons of `O(b_label)`-bit
keys, with sequential rewinds charged at the same order. Thus either
direction has a straightforward bound

\[
 C_{\rm perm}=O(T\ell b_{\rm label}
                 +T(b+b_{\rm label})\log T)                    \tag{16}
\]

and `O(T(b+b_label))` occupied cells if the map is generated afresh. The map
can instead be retained at its storage cost. Copying, return scans and
clearing temporary record streams add linear passes already covered in
(16). This elementary tape sorting account is an existence upper bound,
not a repository-native controller or an admission of its ownership ABI.
No permutation is declared free, in-place, ancilla-free, or source-local.

### 6.2 Generator materialization and application

Equation (4) asks for c start rows and c start columns of E. With the
coordinate-vector partners stored implicitly, the displayed representation
still stores `2cT=T^2/ell` scalar slots (including its prescribed zero slots).
Writing it explicitly at b bits per slot takes `Omega(cTb)` bit work and
cells if all vectors are retained. This is a cost of this materialization
format, not a lower bound on every compressed representation.

For an exact tensor given by available factor entries, each needed kernel
entry is a product of d factor entries. Thus the simple generator assembly
uses `O(cTd)` factor accesses and scalar arithmetic operations. For the
inverse tensor, its inverse factor entries must first be computed and made
available. These are arithmetic counts; they do not make bounded-time bit
access, precision, rational coefficient size or factor inversion free.

Let `C_setup` be the paid assembly bill and `A(T,b)` the paid bill of one
triangular Toeplitz matrix-vector service with its length-T coefficients
already supplied. Each term of (4) has one shift factor and one such
service. A direct one-transform implementation therefore requires the sum
of the following charged components:

\[
 2C_{\rm perm}+C_{\rm setup}
       +2c A(T,b)+O(cTb),                                      \tag{17}
\]

plus the precision-dependent diagonal operations in (13), if used. The last
term includes record movement, shifts, accumulation and clearing for this
simple implementation. It is not a claim that this implementation fits the
source's native gate or ownership interface. A source algorithm with three
transforms must pay the corresponding three application bills, and must also
pay source generation, retained helper work, changes of frame, restoration,
recursive children and its actual interfaces. None is removed by (3).

Even in an optimistic unit-cost arithmetic model, for fixed n and d tending
to infinity the displayed generator materialization has size
`Theta(T^2/d)`, while direct dense axis application uses `O(d T n)` scalar
operations. Their ratio grows at least as `T/(d^2 n)`. Thus this explicit
materialization does not give an asymptotic application improvement in that
regime. A useful fast route would need further compression, fast implicit
generation, or a different circuit, together with its full bit-model bill.

## 7. Exact limits and falsification controls

The theorem does not make any of the following claims.

- Odd n has fixed reversal labels. For n=3, ell=2 the cycle lengths are
  4,4,1, so the uniform `2ell` count is false.
- If ell is not a power of two, its proper periods need not divide ell.
  For n=2, ell=3 there is a 2-cycle as well as a 6-cycle.
- A shifted factor need not be centrosymmetric, and different q parameters
  inside the rotated block need not be invariant. Exact rational controls
  detect displacement outside the complemented-rotation support in both cases. Equations
  (12)--(15) state the separate, paid scope of shift removal.
- A singular factor has no inverse target. An arbitrary perturbation of the
  full ordered matrix can break the support property, even at size `2^-20`.
- The rank is not asserted to equal `T/ell` for all invariant kernels. For
  example an identity kernel has ordinary Stein rank one in every order.
- No all-order lower bound, bounded-rank order, or optimality of this order
  has been proved. In particular, (11) is not an unbounded lower bound.

The verifier checks 15 exact rational fixtures (30 forward/inverse targets),
including cube dimensions 1--6, even local dimensions 4 and 6, a nonsymmetric
centrosymmetric factor, an arbitrary nonsymmetric spectator, and a common
four-bit rounded factor table. It checks the support decomposition in every
case and literal triangular Toeplitz reconstruction in 22 targets. Eight
failure controls include deliberate rank-bound forgery and remain active
under Python optimization. These are finite verification aids; sections
1--6 supply the quantified arguments and state their separate model limits.
