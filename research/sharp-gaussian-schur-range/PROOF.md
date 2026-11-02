# The sharp uniform Gaussian minor range

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement and predecessor boundary

Let b>=1 and n>=1 be integers, and let t>0 be real. On indices 0,...,n-1 put

```text
G[i,j] = t^((i-j)^2) if |i-j|<=b, and 0 otherwise.
```

The largest parameter interval on which the following criterion holds for
every n and b is exactly **0<t<=1/2**. For any equally long increasing row
and column lists R and C,

```text
det G[R,C] > 0  iff  |R_l-C_l|<=b for every l;
det G[R,C] = 0  otherwise.
```

The empty minor is one. Consequently all principal pivots are positive.
For any eliminated set E and surviving i<j, the Schur entry is nonzero
exactly when the chain from i to j through E intersect (i,j) has every
successive gap at most b. Its sign is (-1)^|E intersect (i,j)|. Diagonal
Schur entries are positive. Independent positive row and column gauges
preserve these conclusions.

PR5207 proves these implications from a positive bidiagonal factorization
of the finite Gaussian polynomial and establishes the sufficient range
0<t<=1/3. That theorem and its classical path argument are cited premises,
not audit targets. The new steps are a sharper alternating-sign estimate,
the exceptional repeated-root endpoint, and an obstruction at every t>1/2.
They answer its Open next question 2. A short account of the inherited
factorization implication below makes the dependency explicit.

## 1. The alternating tail

For L>=0 define A_L(t)=sum_(r=1)^L (-1)^r t^(r^2). For 0<t<1,

```text
A_0=0,  A_1=-t,  A_L>-t for every L>=2.
```

Indeed, after the first term, pair the terms of indices 2,3, then 4,5,
and so on. Each pair t^((2k)^2)-t^((2k+1)^2) is strictly positive.
An unpaired last even term is also strictly positive. This works for
each finite tail and does not replace it by an absolute-value bound.

Define the degree-2b polynomial

```text
P_b(z) = sum_(h=-b)^b t^(h^2) z^(h+b).
```

At z_j=-t^(-2j), for -b<=j<=b, division by its jth summand gives

```text
P_b(z_j) / [(-1)^(j+b) t^(-j^2-2jb)]
    = 1 + A_(b+j)(t) + A_(b-j)(t).
```

If one tail is empty, this is at least 1-t>0. If both are nonempty,
it is at least 1-2t. Thus it is strictly positive for t<1/2.
At t=1/2 and b>=2, the two lengths sum to 2b>=4, so at least one is
at least two. Its strict tail inequality again gives strict positivity.

The 2b+1 negative evaluation points are distinct, and the displayed
signs alternate. The intermediate value theorem supplies a root in
each consecutive interval. The degree is 2b, so all roots are negative
and simple in these cases. Write them as -lambda_r with lambda_r>0.

The only omitted case is b=1, t=1/2. Here

```text
P_1(z) = (z+1)^2/2.
```

Its repeated root is still negative. Repeated roots do not remove the
strict minor criterion: its path weights remain strictly positive.
For every 0<t<=1/2 and every b>=1 we have therefore proved

```text
P_b(z) = t^(b^2) product_(r=1)^(2b) (z+lambda_r),  lambda_r>0.
```

## 2. The factorization implication

As in PR5207, let T[i,j]=1 if i=j+1. The formal Laurent expression
for the doubly infinite band kernel is

```text
G = t^(b^2) T^(-b) product_r (lambda_r I+T).
```

This is a finite path identity with 2b steps, so there is no convergence
issue. A path from column c to row r+b stays put or advances by one at
each step. Its weight is positive, including when some lambdas coincide.
The classical determinant path cancellation leaves precisely the
nonintersecting, order-preserving path families. Such a family requires
|R_l-C_l|<=b. When those inequalities hold, positions

```text
x_l(s) = max(C_l, R_l+b-(2b-s)),  0<=s<=2b,
```

give a family explicitly: each increment is zero or one, and positions
strictly increase with l at every time. The minor is then strictly
positive. If an inequality fails, there is no surviving family and
the minor is zero. This proves that the new factorization satisfies
exactly the premise used by PR5207; simplicity of roots is unnecessary.

For the Schur conclusion, the block determinant formula expresses S[i,j]
as the minor with row list (E,i) and column list (E,j), divided by the
positive principal minor on E. Sorting the appended lists gives sign
(-1)^|E intersect (i,j)|. The ordered-minor criterion becomes the stated
chain-gap criterion. For i=j it is a principal numerator. Positive
diagonal gauges multiply the Schur entry by the corresponding positive
row and column factors.

## 3. Every larger t fails

Set b=1 and let D_n be the full n-by-n principal determinant. Expansion
along the last row of this tridiagonal matrix gives

```text
D_0=1, D_1=1, D_n=D_(n-1)-t^2 D_(n-2).
```

At t=1/2 this recurrence gives D_n=(n+1)/2^n>0, consistent with
the included repeated-root endpoint.

For any t>1/2 put theta=arccos(1/(2t)). Then 0<theta<pi/2.
The same initial values and sine addition identity prove

```text
D_n = t^n sin((n+1)theta)/sin(theta).
```

Choose n=floor(pi/theta). Then

```text
pi < (n+1)theta <= pi+theta < 3pi/2,
```

so D_n<0. Its row and column lists agree, hence every matched distance
is zero. The asserted strict positivity criterion therefore fails.
An earlier determinant may vanish; that also contradicts positivity
of every principal pivot and does not affect this negative witness.
This excludes every t>1/2, not merely a finite sample above the endpoint.

## Scope

This is a scoped algebraic proof, with exact finite corroboration in
verify.py. It proves the maximal uniform parameter interval, not a
maximal interval at a fixed bandwidth or matrix size. Classical
alternating sums, polynomial separation, determinant paths and the
tridiagonal recurrence retain their usual credit. No literature-priority
claim is made for those methods or for general total-positivity theory.

No concrete retained Gaussian caller has been shown to meet the real,
linear-path and positive-gauge hypotheses. Periodic or complex kernels,
conditioning, rounding, tape execution, routing, native implementation,
stock, compiler admission and exact recovery remain separate obligations.
No new kappa, selected-frontier change or complete multiplication theorem
is claimed. Independent human and formal proof-kernel review are unclaimed.
