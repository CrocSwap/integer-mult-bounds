# The Landau scale of exact Gaussian symmetry-orbit certificates

Base `e54523517d0f03e58352e647c403a5af3e525a57`; orbit-construction
predecessor `8f1a09fb4f696bd5f20e1953210936308571416e` in
CubeJerry/integer-mult-bounds. Exact predecessor object hashes are recorded
in DEPENDENCIES.json. Prepared for @CubeJerry with substantial OpenAI
assistance. The orchestrator proposed this extension; the worker independently
derived the group classification, prime-power correction bound and controls.

## 1. Object, certificate class and claims

Fix integers d>=1, n>=2 and real parameters `0<q<1`, `v>0`. Put
`X={0,...,n-1}^d`, `T=n^d` and

\[
 H_{xy}=q^{\|x-y\|_2^2}v^{\sum_i(x_i-y_i)}.                 \tag{1}
\]

An exact symmetry is any bijection `a:X->X` satisfying
`H_(ax,ay)=H_(x,y)` for every x,y. This quantifies over all T-vertex
permutations, not just an initially selected coordinate-permutation family.
Let c(a) be its number of cycles, including fixed points. The certificate
class studied here concatenates the full cycles of one such symmetry in
successor order and uses its c(a) cycle starts as the boundary set.

Let g(d) be the maximum order of a permutation of d letters. Let
`c_*(d,n,v)=min_a c(a)` over all exact symmetries. We prove

\[
\begin{array}{ll}
 T/g(d)\le c_* <4T/g(d), & v\ne1,\\[2mm]
 T/(2g(d))\le c_* <4T/g(d), & v=1.                         \tag{2}
\end{array}
\]

The strict upper constants can be replaced by
`C=(3/2) exp(8/9)<4`. Thus the best cycle-boundary certificate size in
this class is `Theta(T/g(d))`, uniformly in n and v. The same symmetry
group and bounds hold for H inverse.

This is a lower bound on the number of boundary cycles in this certificate
class. It is **not** a lower bound on displacement rank, generator rank
after compression, arbitrary orderings, partially invariant successors,
implicit generation, arithmetic circuits or integer multiplication.

## 2. Classification of every exact symmetry

**Lemma 1.** The exact symmetry group of (1) is S_d acting by coordinate
permutations if v!=1. If v=1 it is the signed coordinate-permutation group,
where a negative coordinate means `x_i -> n-1-x_i`.

*Proof.* Multiplying an entry and its transpose cancels the shift:

\[
 H_{xy}H_{yx}=q^{2\|x-y\|^2}.
\]

Since `0<q<1`, an exact symmetry preserves every squared Euclidean distance.
Write `z_0=a(0)` and `z_i=a((n-1)e_i)`. Distance preservation shows that
the d vectors `z_i-z_0` have length n-1 and are mutually orthogonal.
Let A have columns `(z_i-z_0)/(n-1)`. Polarization against these vectors
gives, for every x in X,

\[
 (a(x)-z_0)\mathbin{\cdot}(z_i-z_0)=(n-1)x_i.
\]

The orthonormal basis therefore determines `a(x)=Ax+z_0`. This is an affine
Euclidean isometry on the ambient space. Because it maps X onto X, it
maps their convex hull `[0,n-1]^d` onto itself. In particular it maps its
vertices to vertices. Each `z_i` is a cube vertex at distance n-1 from
the vertex `z_0`, and therefore differs from `z_0` in exactly one coordinate.
The columns of A are consequently distinct signed coordinate vectors.
The translation is exactly the one making each negative coordinate the
reflection `x_i -> n-1-x_i`.

These signed coordinate permutations all preserve the distance term. If
v!=1, equality of entries also gives
`sum_i a(x)_i-sum_i a(y)_i=sum_i x_i-sum_i y_i`. The linear coefficient
of each coordinate on the left is its sign. Every sign must therefore be
positive. Conversely ordinary coordinate permutations preserve both factors
in (1), and when v=1 reflections preserve its only remaining factor. This
proves both inclusions. QED.

The exclusions matter. At q=1,v=1 the matrix is constant and every vertex
permutation is a symmetry. At n=1 the coordinate action is not faithful.
The classification is for the exact matrix; rounding can create additional
exact symmetries and is not covered by simply reusing this argument.

**Lemma 2.** H is invertible, and H and its inverse have the same exact
permutation symmetry group.

For the one-dimensional unshifted factor, write
`B0_ij=q^(i^2) (q^(-2i))^j q^(j^2)`. The middle matrix is a Vandermonde
matrix on distinct positive nodes, and the diagonal factors are nonsingular.
The shifted factor is `Dv B0 Dv^-1`, with `(Dv)_ii=v^i`. Tensoring these
invertible factors proves invertibility. This identity is only used to prove
nonsingularity, not to claim a free or numerically stable gauge operation.
For any permutation matrix P, `P H P^T=H` if and only if
`P H^-1 P^T=H^-1`, by inversion. QED.

## 3. Order bounds and the lower certificate bound

The order of a coordinate permutation with cycle lengths `m_1,...,m_r`
is `lcm(m_1,...,m_r)`, at most g(d). Its action on X is faithful for n>=2.
For a signed coordinate permutation, the product of signs around a
coordinate cycle is positive or negative. That block has order m_i or
2m_i, respectively. Its total order divides
`2 lcm(m_1,...,m_r)`, hence is at most2g(d). This bound on maximum order
is attained by taking a maximum-order coordinate permutation and making
each of its cycles negative.

Every cycle of a finite action has length at most the order of the acting
element. Summing cycle lengths gives

\[
 c(a)\ge T/\operatorname{ord}(a).
\]

Combining this observation with Lemma1 proves the lower bounds in (2).
No statement about entries of the Stein displacement is needed for this
lower bound. In particular, cancellation between boundary generators is
outside what it bounds.

## 4. A maximum-order prime-power construction

Write an integer `M=product_p p^(a_p)` and let
`ell(M)=sum_(a_p>0) p^(a_p)`, with ell(1)=0. The classical finite
characterization of Landau's function is

\[
 g(d)=\max_{\ell(M)\le d} M.                               \tag{3}
\]

For completeness, a permutation of order M has coordinate cycles whose
least common multiple is M. Assign each maximal prime power in M to one
cycle containing it. For any integer m>=2 the sum of its distinct
prime-power factors is at most m: repeatedly use `a+b<=ab` for integers
a,b>=2. Thus the total assigned sum is at most the total coordinate
budget d. Conversely, disjoint cycles of the distinct prime-power lengths
in M, plus unused fixed coordinates, realize order M using ell(M)
coordinates. This proves (3).

Choose a maximizing set of lengths `ell_i=p_i^(a_i)`, with distinct primes
p_i and `sum ell_i<=d`. Rotate these blocks simultaneously and leave the
remaining coordinates fixed. This is an exact symmetry for every v,
without reversal or diagonal conjugation. Its order is
`product ell_i=g(d)`.

For a rotation of one ell-letter coordinate block, the k-th power fixes
`n^gcd(ell,k)` words. Orbit counting gives

\[
 c_\ell={1\over\ell}\sum_{k=0}^{\ell-1}n^{\gcd(\ell,k)},
 \qquad F_\ell(n)={\ell c_\ell\over n^\ell}.
                                                               \tag{4}
\]

Every actual word-period divides ell_i. Periods in different selected blocks
are therefore pairwise coprime. The Cartesian product of one selected cycle
from each block is a single cycle under simultaneous rotation: its period
is the product of the component periods, equal to its cardinality. Hence

\[
 c=n^{d-\sum_i\ell_i}\prod_i c_{\ell_i},\qquad
 {c\over T}={1\over g(d)}\prod_i F_{\ell_i}(n).               \tag{5}
\]

This is an exact identity, including all shorter cycles. Repeated primes
would invalidate the product-of-cycle-counts inference.

## 5. Uniform correction for every prime power

**Lemma 3.** For every prime p, a>=1 and n>=2,

\[
 1\le F_{p^a}(n)\le1+(p-1)n^{1-p}.                         \tag{6}
\]

For a=1, exactly n words are constant and all other words have period p,
giving equality on the right. Suppose a>=2, put ell=p^a and m=ell/p.
Every nonidentity power of the block rotation has at most ell/p cycles, so

\[
 F_\ell(n)-1\le(\ell-1)n^{-\ell+\ell/p}.                  \tag{7}
\]

Except for p=2,a=2, the following elementary inequality holds:

\[
 {pm-1\over p-1}\le2^{(p-1)(m-1)}\le n^{(p-1)(m-1)}.       \tag{8}
\]

Indeed, if m>=4 the left side is at most `2m-1`, which is at most
`2^(m-1)` by induction from m=4; the displayed power is at least this.
The only remaining m>=3 case is m=3,p=3, where the left side is4 and the
power is16. Combining (7) and (8) gives the desired bound (6).

The exceptional ell=4 case is essential to handle exactly, because (7)
alone is too loose at n=2. Its exact correction is

\[
 F_4(n)-1=n^{-2}+2n^{-3}\le n^{-1},
\]

equivalent to `n+2<=n^2`, valid for n>=2. This completes the proof.

The p=2 factor is at most3/2. For all distinct odd primes,

\[
 \log\prod_{p\text{ odd}}(1+(p-1)n^{1-p})
 \le\sum_{j\ge1}{2j\over4^j}={8\over9}.
\]

Therefore

\[
 \prod_iF_{\ell_i}(n)\le C={3\over2}e^{8/9}<4.              \tag{9}
\]

For a wholly rational check of the last comparison, the exponential series
and `k!>=2*3^(k-2)` for k>=2 give
`e^x<=1+x+(x^2/2)/(1-x/3)` for0<=x<3. At x=8/9 this is419/171;
thus `C<=419/114<4`. Equations(5) and(9) prove both upper bounds in (2).

Maximal order need not minimize c at a finite dimension. For n=2,d=5,
coordinate cycles2+3 have order6=g(5) and `c=3*4=12`; one5-cycle has
order5 and `c=(32+4*2)/5=8`. The construction proves a uniform constant
factor, not a finite optimizer.

## 6. Classical asymptotic and exact certificate interpretation

The classical Landau asymptotic is

\[
 \log g(d)\sim\sqrt{d\log d}.                              \tag{10}
\]

We cite this result rather than claim a new proof. A primary research
reference stating (3) and (10) explicitly is Deléglise, Nicolas and
Zimmermann, *Landau's function for one million billions*, Journal de Théorie
des Nombres de Bordeaux20(2008),625--671,
[DOI10.5802/jtnb.644](https://doi.org/10.5802/jtnb.644), equations(2) and(6),
[full text](https://www.numdam.org/article/JTNB_2008__20_3_625_0.pdf).
The finite characterization, classical orbit counting and cube symmetries
are background mathematics; no global priority claim is made for them.

Equation(2) gives, uniformly in n>=2 and v>0,

\[
 \log(T/c_*)=\log g(d)+O(1)
            =(1+o(1))\sqrt{d\log d}.                       \tag{11}
\]

Here the O(1) is an absolute bound. In particular, for fixed n the best
cycle count in this certificate class is `T^(1-o(1))`. This strengthens the
predecessor's elementary distinct-prime family, whose guaranteed saving had
logarithm of order `(log d)^2`, to the optimal scale for all global exact
symmetry-orbit certificates of the stated Gaussian matrix.

To make the connection to generators precise, put the cycles of a in
successor order and let S be their c starts. Except at starts, simultaneous
predecessors are obtained by `a^-1`. Thus for the ordinary lower shift Z,
`E=M-Z M Z^T` vanishes when both indices are outside S. The same applies
to the inverse, by Lemma2. If D selects rows in S, then

\[
 E=DE+(I-D)ED
   =\sum_{s\in S}e_sE_{s,:}
    +\sum_{s\in S}(I-D)E_{:,s}e_s^T.                      \tag{12}
\]

This is the specified at-most2c boundary decomposition, with known unit
vectors and2c nontrivial length-T vectors. The nilpotent identity
`M=sum_(k=0)^(T-1) Z^k E (Z^T)^k` converts each outer product into the
usual lower-times-upper Toeplitz generator term. This restates the relevant
predecessor interface so the precise scope of the count is visible.

Some displayed vectors may vanish or be dependent. The lower bound on c
does not prevent removing them, changing the generator basis, or finding a
different low-rank representation. It does not apply to an arbitrary order
whose successor need not extend to a global matrix symmetry.

## 7. Full construction and dense-materialization boundary

### 7.1 A uniform, paid construction

The prime-power lengths in (3) can be selected by a finite dynamic program.
Process primes p<=d. For each capacity t<=d, retain the largest product
using processed primes; at prime p compare the previous value with
`p^a` times the previous value at `t-p^a`, for all `p^a<=t`. The old
table is retained during a prime's update, so at most one power of that
prime is selected. Store predecessor choices to reconstruct the lengths.
This is the classical grouped-knapsack recurrence, not a new algorithm.

There are at most `O(d^2 log(d+2))` updates and all products have
`O(d log(d+2))` bits by the crude bound d!. Even scanning the entire
table for every access, and using schoolbook arithmetic, gives a
conservative fixed-tape bit budget
`C_select=O(d^4 log^3(d+2))`; prime generation by trial division and
reconstruction fit inside this deliberately loose polynomial envelope.
No random-access or unit-cost large-integer operation is required by this
upper bound. No efficient native repository controller is asserted.

Let `b_label=d ceil(log_2 n)`. For each lexicographic vertex, follow the
selected coordinate permutation until its first return, at most g(d)
steps. Output that cycle only if the initial vertex was its least label.
Comparing and permuting digit fields can be done by paid scans; a
conservative bound is `O(d b_label)` per successor without indexed tape
access. This explicit uniform enumeration therefore costs

\[
 C_{\rm enum}=O(C_{\rm select}+Tg(d)d\,b_{\rm label}).        \tag{13}
\]

One may improve this enumeration, but no improved bound is needed here.
Its scratch is polynomial in d and log n, apart from its charged output.
Pairing emitted labels with their orbit-order indices and performing
sequential merge-sort joins transports b-bit records in each direction
with the additional upper bound
`O(T(b+b_label) log T)`. Both ingress and restoration are charged. These
are general uniform bit-operation budgets, not proof of source-local
physical ownership, head placement, or an admitted native program.

### 7.2 The specified dense format still costs almost quadratically

Consider explicit dense materialization of the2c length-T scalar vectors
in (12), with their prescribed zeros occupying slots. Its size is exactly
`2cT` scalar slots. If each slot is written as a b-bit record, the writes
alone cost `Omega(bcT)`. The two unit-vector families are already implicit;
this count does not charge them as additional dense input.

Over **every exact symmetry** in Lemma1, equations(2) give

\[
 \min_a 2c(a)T=\Theta(T^2/g(d)).                            \tag{14}
\]

For fixed n>=2, equation(10) implies

\[
 T^2/g(d)=T^{2-o(1)}.                                     \tag{15}
\]

Even with optimistic unit-cost scalars, this specified materialization
eventually exceeds the direct dense axis-application bill `O(dTn)`, since

\[
 {T^2/g(d)\over dTn}={n^d\over dn\,g(d)}\longrightarrow\infty.
\]

The same scalar comparison applies to the homogeneous inverse factors.
This compares scalar slots with scalar arithmetic operations. It does not
infer a bit-time comparison for an arbitrary growth regime of the precision
b; an actual implementation must price both arithmetic and writes at its
own precision.
It is a scoped obstruction to this *dense boundary-vector representation*;
it is not a proof that orbit ordering, implicit generators, structured
access, compressed linear combinations or a different transform cannot
improve actual computation. Precision, coefficient construction, arithmetic,
accumulation and source access can only add to this explicit write bill.

## 8. Source boundary and verification boundary

Every factor here has the same n,q,v. Common shifts already commute with
coordinate rotations, so the prime-power construction needs no conversion
to an unshifted kernel. If source factors differ within a block, exact
commutation must be proved separately. If diagonal conjugation is introduced
to match them, its magnitude/condition range, rounding transfer and physical
transport remain paid; the identity proving Lemma2 supplies no such service.
Physical gaps, periodic tails, actual phase permutations and the complete
three-transform/all-axis bill have not been absorbed into H.

The classification in Sections1--7 is for the exact homogeneous matrix.
An entrywise rounded table might gain additional symmetries. Section9 gives
explicit sufficient separation conditions that transfer symmetry containment
and the certificate bound. Structure-preserving rounding alone supplies no
such separation. An approximate symmetry is outside the certificate class.

The standalone verifier cross-checks direct finite orbits, independent
Burnside averages, prime-power product counts, two finite methods of computing
g(d), and exact small matrix automorphisms. It includes the exceptional
4-cycle estimate, repeated-prime failure, composite-as-prime failure,
non-symmetry and shift controls, and the d5 counterexample to finite
max-order optimality. All finite coverage is recorded in the output.
These checks corroborate the proof; they do not prove (10) or any universal
statement by extrapolation. No selected frontier or foundational assumption
changes, and there is no new kappa.

## 9. A finite-precision extension by preserved grid adjacency

This section concerns exact symmetries of a perturbed table, not approximate
symmetries of the ideal matrix. Let `Htilde` be any real or complex T-by-T
table with `|Htilde_xy-H_xy|<=delta` entrywise. Arbitrary perturbations can
destroy symmetries; only containment is automatic from the conditions below.

**Lemma 4 (grid graph).** Every automorphism of the nearest-neighbor grid
graph on X is a signed coordinate permutation.

The graph degree is `d + number of interior coordinates`, so its
minimum-degree vertices are precisely the2^d corners. This includes n=2,
when every vertex is a corner. Graph distances between corners are n-1
times Hamming distance, hence determine their squared Euclidean distances.
The corner action is therefore a signed coordinate permutation by the
affine-cube argument of Lemma1. Compose its inverse so that all corners
are fixed. For any x, the distances to the corners0 and `(n-1)e_i` give

\[
 x_i={\operatorname{dist}(x,0)+(n-1)
             -\operatorname{dist}(x,(n-1)e_i)\over2}.
\]

Thus every coordinate of x is fixed, proving the lemma.

**Unshifted separation.** If v=1 and

\[
                         2\delta<q-q^2,                     \tag{16}
\]

every exact symmetry of Htilde is a signed coordinate permutation. Indeed,
the entries for adjacent distinct vertices equal q, and every other
off-diagonal entry is at most q^2. Under (16), an adjacent entry and a
nonadjacent entry cannot become equal after two errors of size delta.
An exact table symmetry consequently preserves grid adjacency; apply
Lemma4. Its order is at most2g(d), so its orbit count is at least
`T/(2g(d))`.

**Shifted separation.** Suppose `|log v|<=-log q`. Each exact entry of H
is at most1: for an integer difference k, `k^2>=|k|`, so
`q^(k^2)v^k<=1`, and the tensor product preserves the inequality. Hence

\[
 |\widetilde H_{xy}\widetilde H_{yx}-H_{xy}H_{yx}|
                         \le2\delta+\delta^2.
\]

Adjacent ideal pair products are q^2, whereas other distinct pair products
are at most q^4. Therefore the sufficient condition

\[
                       4\delta+2\delta^2<q^2-q^4             \tag{17}
\]

forces every exact symmetry of Htilde to preserve adjacency and to be a
signed coordinate permutation. Its cycles again satisfy `c>=T/(2g(d))`.
This conclusion does not need a lower bound on the size of the shift.

If v!=1 and in addition

\[
                       2\delta<q|v-v^{-1}|,                  \tag{18}
\]

all reflected coordinates are excluded. To see this, choose a pair with
`x-y=e_i` in a reflected coordinate. A signed permutation sends its
difference to `-e_j`. The ideal directed entries are respectively qv and
q/v. Under (18), they cannot become equal after two delta perturbations.
Thus every exact symmetry is an ordinary coordinate permutation and
`c>=T/g(d)`.

These conditions prove containment even for arbitrary complex errors.
They do not imply that a nonidentity symmetry survives. For example,
arbitrarily small distinct perturbations of all diagonal entries force
the symmetry group to be the identity, because every diagonal value then
identifies its vertex. Consequently the constructive upper bound in (2)
does not follow from an error bound alone.

For a *common deterministic scalar rounding rule* applied to every ideal
entry, each original symmetry survives exactly. Therefore (16) gives the
full signed group in the unshifted case, and (17)--(18) give the full
coordinate group in the shifted case. Even (17) without (18) suffices for
the same `Theta(T/g(d))` certificate scale: coordinate permutations survive,
and the whole symmetry group is contained in signed coordinate permutations.
The possible factor-two difference does not change that scale.

Common factorwise rounding has the same useful implication once its global
error is paid. If every one-dimensional entry has magnitude at most1 and
each rounded factor entry has error at most epsilon, telescoping a product
of d entries gives

\[
          \delta\le d\epsilon(1+\epsilon)^{d-1}.             \tag{19}
\]

The proof replaces one factor at a time, bounding each remaining rounded
factor by1+epsilon. Equal rounded factors preserve coordinate permutations;
in the unshifted case their inherited reversal symmetry also survives.
Substituting (19) into (16) or (17), and optionally(18), therefore extends
the corresponding bounds to this precise factorwise rounding model. For
nearest dyadic rounding at b fractional bits one may use
`epsilon=2^(-b-1)`. Neither a per-factor error nor a symmetry-preserving
rule should be silently confused with the required global bound.

**Polynomial-range corollary.** Let P tend to infinity and fix positive
constants A,B,C,c. Suppose

\[
 d\le P^A,\qquad P^{-B}\le q\le1-P^{-C},\qquad
 |\log v|\le-\log q,\qquad b\ge cP.
\]

With common nearest factorwise rounding at b fractional bits, equation(19)
gives `delta<=d 2^(-b)` eventually: `d epsilon` tends to zero, so
`(1+epsilon)^(d-1)<=2` eventually. Meanwhile
`q^2-q^4>=q^2(1-q)>=P^(-(2B+C))`. Exponential decay beats this polynomial
gap, and (17) therefore holds eventually. Coordinate symmetries survive and
all exact rounded symmetries lie in the signed group, yielding the same
`Theta(T/g(d))` certificate scale without any lower bound on a nonzero
shift. This is a parameter-regime consequence of the matrix theorem; it does
not assert that the actual source supplies these matched factors or its
coefficient-production service. No inverse-stability assertion is added.

The dense slot conclusion (14)--(15) transfers whenever these containment
and surviving-construction conditions hold. For arbitrary perturbations
only its lower bound transfers. If Htilde is nonsingular, its exact inverse
has the same symmetry group by inversion; these separation conditions do
not themselves guarantee nonsingularity, conditioning or stable inverse
rounding. The actual source must still supply matched factors, admitted
precision, transport and the complete caller. This is a robust scoped
matrix certificate theorem, not source admission or a multiplication result.
