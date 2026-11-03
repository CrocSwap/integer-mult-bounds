# Prefix-balanced native coarsening

This is a scoped mathematical proof of a changed numerical interface. The new
step is the compatibility of cumulative stochastic rounding with the native
coarse-period codec, including simultaneous optimal prefix variances and the
extra scan cost. It is not a complete multiplication theorem.

## Premises and credit

Use Ali Romman's [PR6540](https://github.com/CrocSwap/integer-mult-bounds/pull/6540)
at `5f7c893b6af9a75cb19ad22c6db06ed22eea6f54` for the Gaussian operator and
quotient premises below. Its exact proof is retained in
[inputs/PR6540-PROOF.md](inputs/PR6540-PROOF.md), with origin and hash in
[ORIGIN.json](ORIGIN.json). Its scientific executable is not invoked. Gaussian
Smith coordinates and the earlier native/compiler lineage keep their credit.

Cumulative rounding is classical. Knuth's
[two-way rounding](https://arxiv.org/abs/math/9504228) and Doerr, Friedrich,
Klein and Osbild's [unbiased matrix rounding](https://arxiv.org/abs/cs/0604068)
give broader controlled-rounding context. Neither cumulative rounding nor the
scalar unbiased-variance inequality is claimed as new here.

Let A=L C_r R be the predecessor's Gaussian-unit monomial native recipe at
tensor width f>=1. Write N=512^f, a=r*f, d=ceil(a/2), m=2^k, k>=d and
D=2^(k+d). Its central pair is

```text
C = [[1+i,1-i],[1-i,1+i]]/2.
```

For every x in Z[i]^N the vector n=2^d A x is integral Gaussian, and
B=m A^-1 is integral Gaussian. The lattice quotient Z[i]^N / B Z[i]^N
has exactly 2^(2kN) elements. The predecessor supplies a label ell(x) with
2kN bits and a representative x0(ell), with x-x0 in B Z[i]^N. These are cited
premises, not new quotient or source-admission claims.

Fix an order of the 2N real components after applying A. The input and order
are fixed before drawing a fresh uniform u in {0,...,D-1}, conditionally on
the entire incoming state and history. Physical values use input unit h/m
and output unit h, for h>0. No initial component of x is assumed zero.

## The new quantizer

Flatten n into n_1,...,n_t, t=2N. Set S_j=sum_(i<=j) n_i, S_0=0, and

```text
q_j = floor((S_j+u)/D) - floor((S_(j-1)+u)/D).
```

Equivalently, keep c_0=u and compute

```text
(q_j,c_j) = divmod(n_j+c_(j-1),D),   0 <= c_j < D.
```

The invariant D*sum_(i<=j) q_i+c_j=S_j+u proves the equivalence even for
negative inputs. For a fixed j, c_(j-1)=(S_(j-1)+u) mod D is uniform on the
D residues. Consequently q_j is an adjacent-integer unbiased rounding of
n_j/D. Every individual coordinate retains the predecessor's pointwise
minimum mean squared error. In particular the total Euclidean mean squared
error remains at most N*h^2/2.

More strongly, each prefix sum is exactly floor((S_j+u)/D). If
t_j=S_j mod D, then

```text
E[h*sum_(i<=j) q_i | x] = h*S_j/D,
Var[h*sum_(i<=j) q_i | x] = h^2*t_j*(D-t_j)/D^2 <= h^2/4.
```

Its absolute error is less than h for every seed, and it is exact whenever
S_j/D is integral. All these statements hold simultaneously for every prefix
in the fixed order. For any integer-valued unbiased output with mean b+p,
0<=p<1, the inequality (Z-b)*(Z-b-1)>=0 gives Var(Z)>=p*(1-p).
Thus each displayed prefix variance is the least possible among all unbiased
grid-valued vector outputs, without any reversibility assumption.

## Translation and the exact inverse

For any integer real vector z, replacing n by n+D*z increases q_j by z_j
and leaves every carry unchanged. In Gaussian coordinates this proves

```text
Q_u(x+B*z) = Q_u(x)+z.
```

Use exactly the cited label ell. Encode x as (Q_u(x),ell(x)). Given any
coarse q and label ell, compute

```text
x0 = x0(ell),
z = q-Q_u(x0),
x = x0+B*z.
```

Translation gives Q_u(x)=q, and addition of B*z preserves ell. Conversely,
an original x differs from its representative by a unique B*z, and this
formula recovers it. Hence this is a two-sided bijection for each retained
seed. It changes neither the 2kN-bit label nor the k+d-bit uniform seed.
The predecessor's full-grid capacity and fixed-fair-bit lower bounds apply
to the same input domain and means. No better capacity bound is claimed.

The finite reference instantiates the canonical C axes and their Gaussian
Smith coordinates. The written translation proof applies also to the cited
L,R phases/permutations and arbitrary tensor widths. The finite program's
size/payload guards are not an all-width physical implementation.

## A strict native improvement and sharpness

For the canonical unphased native operator at N=512, r=8, k=5, take every
Gaussian input component equal to 16+16i. C and all its tensor powers fix
constant vectors, so all 1024 real output means are 1/2. The predecessor's
common-coordinate threshold makes the entire sum either 0 or 1024 with equal
probability. Its error variance is 512^2*h^2=262144*h^2.

The new total is identically 512, so its error variance is zero on this same
input. Both constructions have the same coordinate marginals, 5120-bit
residue capacity and nine-bit seed. This is a comparison for this fixed
reader and input, not a new Euclidean-error optimum or caller kappa.

The new uniform quarter-variance bound is sharp for this native family.
Take x_0=16 and every other Gaussian input zero. Column sums of C and its
tensor powers are one, so the full real-component sum has ideal value 1/2.
Its rounded sum is an unbiased Bernoulli output and has variance h^2/4.

## Complete cost change and remaining obligations

Keep the predecessor's native evaluations, Gaussian quotient transforms,
digit extraction/reconstruction, routing and retained-label costs. Each of
the two quantizer passes in an encode/decode round trip visits 2N real
coordinates. Each visit still adds one offset and takes a floor quotient,
and now also computes its remainder modulo D. The added work is exactly
4N remainder extractions, plus two carry initializations from the retained
seed. The carry has k+d bits and can be reused between the sequential passes.
It introduces a serial dependence along the chosen output order.

Because D is a power of two, a remainder is the low k+d bits, including for
negative integers under floor division. The carry never grows with N. If a
numerator has magnitude below 2^W, adding c<D needs at most max(W,k+d)+2
signed bits. There is no full prefix-sum accumulator in this implementation.
The added indexed bit work is O(N*(W+k+d)) and the added live carry capacity
is k+d bits. These are ordinary integer-reference costs. No reversible gate,
dirty-temporary cleanup, seed sampler, fixed-tape schedule or recursive
tariff is supplied by calling a remainder extraction free.

A selected consumer must actually use the declared ordered prefix readers
before this numerical bound can improve its precision budget. An arbitrary
later linear reader need not benefit. Adaptive seed reuse, a changed order
chosen after seeing u, whole-word accumulated errors, native supplier admission,
precision/stock/tape/compiler/outer closure and all five selected framework
assumptions remain unresolved. No new kappa or frontier change follows.
