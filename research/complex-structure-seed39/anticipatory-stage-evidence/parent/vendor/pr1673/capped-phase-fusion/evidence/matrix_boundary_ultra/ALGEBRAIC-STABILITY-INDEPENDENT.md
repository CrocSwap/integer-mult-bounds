# Independent algebraic-coefficient and stability transfer lemma

This note uses no claimed finite certificate from any particular matrix multiplication paper. It isolates what follows from an exponent bound alone, including effectiveness and ordinary bit complexity.

## Statement

Let `omega_C` be the matrix multiplication exponent over the complex numbers. Suppose

\[
\omega_{\mathbb C}<\tau,
\]

where `tau > 2` is a fixed rational number. There is a single, uniform algorithm, with a fixed finite description, with the following properties.

* Its recursive block multiplication uses a fixed finite bilinear formula whose coefficients are computable algebraic complex numbers.
* Given two `W` by `W` complex dyadic matrices with component magnitudes at most `2^h`, it computes their product with maximum entrywise absolute error at most `2^{-p}` in

\[
O\!\left(W^\tau M(p+h+\log(W+1))\right)
\]

bit operations. Here `M(t)` is a regular integer multiplication bound: `M(t) >= t`, `M(Ct)=O_C(M(t))` for fixed `C`, and precision doubling sums to `O(M(t))`. All constants can depend on the chosen fixed block formula.
* If the input encoding has `h = O(p)`, this is

\[
O\!\left(W^\tau M(p+\log(W+1))\right).
\]

If also `log W = O(p)`, it is exactly `O(W^tau M(p))`, without a suppressed logarithmic factor. In particular this holds for `W = Theta(sqrt(p))`.

The strict exponent slack is essential to this statement: an exponent infimum does not by itself supply a finite scheme attaining that infimum. If a source proves `omega_C <= 9/4`, one may take any fixed rational `tau` with `9/4 < tau < 5/2`, for example `tau = 19/8`.

The proof below also gives an exponent strictly below a specified threshold from only the promise that `omega_C` is below that threshold. It does not give useful numerical constants or an efficient way to discover the block formula.

## 1. A finite exact bilinear formula exists with exponent slack

Write `R(b)` for the exact complex tensor rank of `b` by `b` matrix multiplication. Use the usual equivalent definition

\[
\omega_{\mathbb C}=\inf_{b\ge2}\log_b R(b).
\]

Thus some fixed integers `b >= 2` and `r` satisfy

\[
R(b)\le r<b^\tau.
\]

The equality with the ordinary arithmetic-circuit exponent causes no loss here. A division-free circuit for a bilinear map can be bilinearized with only a constant factor overhead: track its components of bidegrees `(0,0)`, `(1,0)`, `(0,1)`, and `(1,1)`. Each multiplication introduces at most two products of an `A`-linear form and a `B`-linear form. Divisions, if allowed in the initial definition, can first be expanded to degree two about a point where all denominators are nonzero. A constant factor is absorbed by the strict exponent slack. Equivalently, one may start directly from the tensor-rank definition above.

A rank-`r` formula has the form

\[
 (AB)_k=\sum_{s=1}^{r} w_{ks}
 \left(\sum_{i=1}^{b^2}u_{si}A_i\right)
 \left(\sum_{j=1}^{b^2}v_{sj}B_j\right),
 \qquad 1\le k\le b^2.
\]

Indices `i,j,k` enumerate matrix entries. The coefficients initially may be arbitrary complex numbers.

## 2. Arbitrary complex coefficients can be replaced by algebraic ones

Let `t_kij` be the structure constants of ordinary matrix multiplication; each is zero or one. The formula is valid for every `A,B` exactly when

\[
\sum_{s=1}^{r}w_{ks}u_{si}v_{sj}=t_{kij}
\quad\text{for every }i,j,k.
\]

These are finitely many polynomial equations over the integers in the unknowns `u,v,w`. They have a complex solution by the preceding step. They consequently have a solution over the algebraic closure of the rationals.

For completeness, if they had no solution over `Qbar`, the weak Nullstellensatz over the algebraically closed field `Qbar` would express `1` as a polynomial combination of these equations, with coefficients in `Qbar`. The same identity would hold over `C`, contradicting the assumed complex solution. This argument requires no bound on the degrees or heights of the algebraic coefficients.

Hence there is an exact finite block formula with algebraic complex coefficients and the same `b,r`.

## 3. The choice is effective, not merely nonconstructive

Algebraic complex numbers have effective finite encodings: a squarefree polynomial over the integers and a rational isolating region for one of its roots suffice. They can be enumerated, and arithmetic and equality in `Qbar` are decidable. In particular, a finite tuple can be put in a common algebraic number field and the displayed rank equations checked exactly.

Dovetail the following finite candidates:

1. integers `b >= 2`, `r >= 1` satisfying `r < b^tau`;
2. finite encoded algebraic tuples of the required length;
3. exact tests of all rank equations.

For rational `tau=a/d`, the first comparison is the integer comparison `r^d < b^a`. The search halts under the stated exponent promise, by Sections 1 and 2. Its output supplies the single fixed block formula. This search may be extremely expensive, but its cost is an absolute constant independent of `W,p,h`, so including it does not change the asymptotic bound. The same result can be phrased by fixing the first successful tuple once and for all.

For just the promise `omega_C < 5/2`, search using `r^2 < b^5`. Upon success choose a rational `sigma` with

\[
\max\{2,\log_b r\}<\sigma<5/2.
\]

The resulting algorithm has exponent at most `sigma < 5/2`. Thus one need not know a numerical gap in advance to obtain a uniform algorithm below the threshold. A practical certificate or practical constant is a separate issue.

## 4. Each fixed algebraic coefficient has an ordinary `O(M(q))` precision algorithm

Every chosen coefficient has a fixed minimal polynomial and a fixed isolating region. In characteristic zero its minimal-polynomial root is simple. Fix a rational starting approximation in a sufficiently small Newton convergence neighborhood. Newton iteration with successively doubled precision computes the root to absolute error `2^{-q}` with `O(M(q))` bit operations.

The polynomial degree, coefficient heights, root separation, initial precision, and bounds on the derivative and its reciprocal are all fixed constants here. Polynomial evaluation, complex division, and the finite number of operations per Newton step cost `O(M(t))` at precision `t`; the usual precision-doubling sum is `O(M(q))`. This is not a claim uniform in algebraic degree or height.

There are only finitely many block coefficients. Compute their dyadic approximations once at the precision needed for the current multiplication, and reuse them at all recursive nodes. This costs `O(M(q))` total, with a formula-dependent constant, rather than a logarithmic factor per scalar operation.

## 5. Recursive arithmetic work

Pad the matrices with zeros to size `N=b^L`, where `W <= N < bW` (and handle `W=1` directly). At each node, form the fixed `r` input linear combinations, recursively multiply the corresponding submatrices, and form the fixed output linear combinations.

The arithmetic operation count satisfies

\[
T(N)\le rT(N/b)+O(N^2).
\]

Let `rho=log_b r`. If `rho>2`, this is `O(N^rho)`; if `rho=2`, it is `O(N^2 log N)`; and if `rho<2`, it is `O(N^2)`. Every case is `O(N^tau)` because `rho<tau` and `tau>2`. In particular the possible equality case `r=b^2` creates no extra factor in the advertised bound: its logarithm is absorbed by the fixed exponent slack.

One could instead tensor a fixed formula a fixed number of times and add a zero product to arrange `b^2 < r < b^tau`, obtaining an exact recursion exponent `rho` strictly between two and `tau`. This refinement is unnecessary for the advertised `O(W^tau)` conclusion.

## 6. Fixed-point roundoff grows only polynomially in the dimension

Use fixed-point complex arithmetic with `q` fractional bits, round after scalar products, and use dyadic block coefficients whose absolute errors are at most

\[
\epsilon=2^{-q}.
\]

Complex arithmetic introduces only absolute constant factors. Additions may be done exactly on this fixed grid; allowing an additional absolute error `O(epsilon)` after an addition also satisfies the following bounds.

For a multiplication node with remaining depth `d`, let `a,beta >= 1` bound the maximum absolute entries of its two inputs. There is a fixed constant `K`, depending only on the block formula, such that the computed result obeys

\[
\|\widehat T_d(A,B)-AB\|_{\max}
\le \epsilon E_d a\,\beta,
\qquad
E_d\le K E_{d-1}+K b^{d-1},\quad E_0\le K.
\]

Here the symbol `b` in `b^{d-1}` is the fixed block dimension; `beta` is the second input bound.

To verify the recurrence, every local input linear combination has fixed length and fixed coefficients. Its rounded value differs from its exact value by at most `c epsilon a` or `c epsilon beta`, and its size is at most `S a` or `S beta`, for fixed `c,S`. Applying the inductive child bound therefore contributes at most

\[
c\epsilon E_{d-1}a\beta.
\]

Perturbing the two child inputs in their *exact* matrix product contributes at most

\[
c\epsilon b^{d-1}a\beta,
\]

because each entry of that child product sums `b^{d-1}` scalar products. Finally, the output reconstruction has fixed length and fixed coefficients. Propagation through its exact coefficients is a fixed factor; coefficient approximation and reconstruction rounding contribute at most

\[
c\epsilon\bigl(b^{d-1}+\epsilon E_{d-1}+1\bigr)a\beta.
\]

For `epsilon <= 1`, all these terms have the stated recurrence after enlarging `K`. Taking `K >= 2b` gives `E_d <= C K^d` for a fixed `C`. Thus at the root

\[
\|\widehat T_L(A,B)-AB\|_{\max}
\le C\,2^{-q}K^L a\beta
=2^{-q}N^{O(1)}a\beta.
\]

For root input magnitude at most `2^h`, take `a=beta=max(1,2^h)` and choose

\[
q=p+2\max(h,0)+\lceil L\log_2K\rceil+O(1).
\]

The final absolute error is then at most `2^{-p}`.

There is also no hidden exponential-in-precision magnitude growth. Along a path, each preprocessing step multiplies a magnitude envelope by a fixed `S`. A node at depth `t` therefore receives inputs bounded by `S^t a` and `S^t beta`. Its computed output is bounded by its exact product size plus the proved error:

\[
\bigl(b^{L-t}+\epsilon C K^{L-t}\bigr)S^{2t}a\beta.
\]

Local scalar products and partial sums obey the same bound up to fixed factors. All intermediate magnitudes are consequently `N^{O(1)} max(1,2^{2h})`. Only `O(h+log N)` integer bits are needed. The total working bit width is therefore `O(p+h+log N)`.

The polynomial error estimate exploits the structure of a bilinear recursion: linear preprocessing, one variable-by-variable scalar product at a leaf, and linear reconstruction. Bounding an arbitrary multiplication by the largest intermediate magnitude at every level would give an unnecessarily pessimistic estimate and is not the argument used here.

## 7. Bit complexity and scope

Every scalar operation uses `O(p+h+log W)` bits and costs `O(M(p+h+log W))`. Multiplying by the `O(W^tau)` arithmetic operation count proves the statement. Padding, input conversion, output rounding, and storage of the fixed coefficient approximations fit the same bound.

The result supplies absolute accuracy. It does not promise small relative error in entries canceled nearly to zero. It applies to arbitrary fixed finite complex bilinear formulas; large fixed coefficient heights or norms worsen only the constants and the fixed multiple of `log W` in the precision requirement.

An exponent theorem alone therefore suffices for computable, stable approximate multiplication with any fixed strictly larger exponent. It does not justify using the exact infimum exponent without slack, treating a varying family of coefficients as fixed, or claiming a concrete efficient implementation without constructing its constants.
