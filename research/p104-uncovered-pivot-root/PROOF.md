# An explicit uncovered-pivot root and its transport obstruction

This is root algebra and a scoped carrier theorem, not a new multiplication
bound. The whole-job price is treated separately. All vectors and duals below
are ordinary, data-independent coordinates over a field of characteristic
other than two. Scalar stage parameters commute.

## 1. Family at every even length

Let `L=2g>=2`, choose `0<=p<L`, and use exactly `L` fields
`A,F_0,...,F_(p-1),F_(p+1),...,F_(L-1)`. The productive sites have time order
`0,...,p,p+1,...,L-1`; insert one thin query immediately after site `p`.
At each query put `R=x y^T` and `T(S)=I+(S-1)R`, where `S^2=1`.

For a left site `i<p`, set

```
x_i = A - F_i - 2 sum_(j<i) F_j,
y_i = A* + F_i*,
M_i = {A,F_0,...,F_i}.
```

For a right site `i>p`, set

```
x_i = -A + F_i + 2 sum_(j>i) F_j,
y_i = A* + F_i*,
M_i = {A,F_i,...,F_(L-1)}.
```

At the uncovered pivot,

```
x_p = -sum_(j<p) F_j + sum_(j>p) F_j,
y_p = A*,
M_p = all fields.
```

Write `u=2` if `p` is even and `u=0` if `p` is odd. The single thin query is

```
x_t = -A + 2 sum_(j>p) F_j,
y_t = u A* + (u-1) [sum_(j<p) (-1)^j F_j*
                         + sum_(j>p) (-1)^(L-1-j) F_j*].
```

Every `y_k x_k=0`. The non-A field intervals are exactly `[i,p]` for `i<p`
and `[p,i]` for `i>p`. This extends the minimal uncovered-pivot examples in
pending #6868: its first L4 family has `p=1`, and its first L6 family has `p=2`.
It does not claim that the more expensive full-interval L4 variants are the
same word.

## 2. Endpoint for arbitrary independent inputs

Number all queries, including the thin one, in their chronological order
`0,...,L`. Direct substitution gives

`y_i x_j = sign(i-j)`.

For completeness, between full sites the `A` coefficient is `+1` on the left,
`0` at the pivot and `-1` on the right; the `F_i` coefficient subtracts exactly
the discrepancy from `sign(i-j)`. For a thin column, each earlier full row gives
`-1` and each later full row `+1`. For a thin row, alternating sums give `+1`
on earlier sites and `-1` on later sites. At the pivot this uses
`(epsilon_right-epsilon_left)(u-1)=1`, where epsilon is one for an odd side
length and zero for an even side length. The two side lengths sum to odd
`L-1`, so exactly one epsilon is one. The same formula gives `y_t x_t=0`.

Here is the sign-Gram argument of #6833, included to make the root proof
self-contained. Let `X` have the query columns and `Y` the query dual rows.
Let `G=YX`, let `B` be its strictly lower triangular part, and let `J` be the
all-ones matrix. Then `I+2B=G+J`. The chronological transvection product is

`T_L(-1)...T_0(-1) = I - 2X(I+2B)^(-1)Y`.

For `c=(1,-1,...,1)^T`, `Gc=0`, `Jc=1`, hence `(G+J)^(-1)1=c`.
The full-site dual rows form a basis: the pivot is `A*`, while every other
row is `A*+F_i*`. Their `L` by `L` sign-Gram submatrix is invertible.
Indeed, `Sv=0` implies `v_(i+1)=-v_i` by subtracting adjacent rows; its first
row then implies `v_0=0` because `L` is even. Thus the full-site columns span.
Also `YXc=Gc=0` and the full-site duals span, so `Xc=0`. Consequently

```
X(G+J)^(-1)YX = X(G+J)^(-1)(G+J-J) = X.
```

Since the columns span, `X(G+J)^(-1)Y=I`, proving the endpoint `-I`.
At `S=1` every query is identity. Decomposing by the central idempotents
`(1+S)/2` and `(1-S)/2` therefore gives endpoint `S I` for arbitrary `S^2=1`.
No input is identified with another input.

## 3. Arbitrary stage parameters

At full site `i`, let `P_i` be the coordinate projector on `M_i` and
`Delta_i=I+(D_i-1)P_i`. The site is `Delta_i T_i`; the thin query has no Delta.
All `x_i,y_i` are in `M_i`, so `P_i R_i=R_i P_i=R_i`.

Let `V_i` be the product of queries strictly after site `i`. Then
`P_i V_i=V_i P_i`:

- For a right site every later query is supported in `M_i`.
- At the pivot `P_p=I`.
- For a left site every query up to that site is supported in `M_i`.
  Its prefix therefore commutes with `P_i`. The scalar root endpoint implies
  that `V_i` is the inverse of that prefix times `S`, so it also commutes.

Reverse induction now factors the literal stage product. If the suffix has
already become the product of its diagonal Deltas times `V_i`, commuting
`Delta_i` past `V_i` gives the next induction step. The diagonal Deltas commute
with each other. Hence the complete operator is

`S product_i Delta_i`.

On every independent input field its scalar is therefore

- `A -> S product_(i=0)^(L-1) D_i`;
- `F_i -> S product_(j=i)^p D_j`, for `i<p`;
- `F_i -> S product_(j=p)^i D_j`, for `i>p`.

This is a polynomial identity in all independent `D_i`, not a test at chosen
numeric inputs. The checker also multiplies the literal matrices as sparse
multilinear polynomials, independently of this proof.

## 4. No idle line transports from a left site to a right site

This assertion includes conjugation by every intervening literal query,
including the pivot query and the thin query. It does not assume a constant
projector throughout that interval.

Fix full sites `i<p<j` and work in the `S=-1` sector. Let `U_i` be the product
of queries strictly before `i`, `V_j` the product strictly after `j`, and `H`
the product strictly between them, all in their literal order. The endpoint is

`V_j T_j H T_i U_i = -I`.

Suppose `v` is a source idle vector: `v in M_i` and `y_i v=0`. If its transported
vector `Hv` lies in `M_j`, then `T_i v=v`, so

`-U_i^(-1)v = V_j T_j H v in M_j`.

The inclusion holds because `V_j` and `T_j` preserve `M_j`. Every earlier
query preserves `M_i`, so `U_i^(-1)v` also lies in `M_i`. As
`M_i intersect M_j = span{A}`, it follows that `v=c U_i A`.

Earlier left queries have no `F_i` component, while the `A` coefficient of
`U_i A` is `(-1)^i`: each earlier left query flips that coefficient, since
its host has not appeared in the earlier prefix. Therefore

`y_i U_i A = (-1)^i != 0`.

The source neutrality gives `c=0`, so `v=0`. In the `S=1` sector the claim is
immediate from `H=I`, `M_i intersect M_j=span{A}` and `y_i A=1`.

Thus no nonzero native-neutral source line can reach the coordinate support
of a right site through the literal query transport. The target need not even
be neutral; support alone rules it out. A positive-rank transported idle
subspace contains a nonzero vector and is excluded as well.

For a transparent, data-independent whole-idle carrier in the arbitrary-D
word, specialize all `D_i=1`. Its intermediate evolution becomes exactly the
query transport just analyzed, making this obstruction necessary. The theorem
does not cover data-dependent frames that vanish or become singular at that
specialization, extra paid maps, altered masks, or a word with changed queries.
The complete invoice must declare its job contract separately.

## 5. What the uncovered-pivot proxy actually counts

For the masks above, define `f(x)=x log x`, with `f(0)=0`, and
`c(m)=f(8m+1)-f(8m-8)`. The field formula in #6868 assigns the root proxy

`f(8L+1) + sum_(m=2)^(p+1)c(m) + sum_(m=2)^(L-p)c(m)`.

For fixed even `L=2g`, the smallest value occurs at `p=g-1` or `p=g` because
`c` is strictly increasing. Relative to `chain(g|g)`, its delta is exactly

`c(g+1)-2c(1)`.

This is negative at L4 and L6, reproducing the source's `-3.439566326...` and
`-0.438584792...`, but is positive at every even L>=8. The signs at L4, L6,
L8 are the exact integer comparisons

```
25^25 < 16^16 9^18,
33^33 < 24^24 9^18,
41^41 > 32^32 9^18.
```

Monotonicity of `c` extends the last sign to every larger g. At L18 the delta
is `+8.4803785672596...` per port. Decimal values are diagnostics; the formula,
monotonicity and integer comparisons establish the signs.

These minimal masks are forced within the singleton-host sign-Gram setting.
Normalize `y_p=A*` and `y_i=a_i A*+F_i*` for `i!=p`. The full-site sign Gram
forces

`x_(j,A)=sign(p-j)` and
`x_(j,F_i)=sign(i-j)-a_i sign(p-j)`.

The coefficient at `j=p` is nonzero, and the host belongs to its own mask, so
any interval mask must contain `[min(i,p),max(i,p)]`. Taking `a_i=1` realizes
exactly that interval. A larger interval cannot improve this field proxy. With l idle sites before
the host and r after it, write
`C(l,r)=f(8(l+r+1)+1)-f(8l)-f(8r)`. Extending the left end by delta>0 changes
C by `[f(x+8delta)-f(x)]-[f(y+8delta)-f(y)]`, where
`x=8(l+r+1)+1>y=8l`. This is strictly positive because f is strictly convex
and its increments of a fixed positive length strictly increase with their
starting point. The right end is identical with l and r exchanged. Extending
both ends is the sum of two positive one-end extensions. This paragraph concerns that proxy only; it is not
a theorem that enlarged masks cannot improve a complete physical invoice.
Dense y, repeated hosts and more than one uncovered site are outside this
normal form.

The proxy is not a legal rank-two-stage invoice at the pivot. It discounts
all `L-1` non-A fields there, but the native active plane has rank two inside
`|M_p|=L`, leaving at most `L-2` idle dimensions. More explicitly, the usual
side carrier with primal `F_i` and dual `F_i*+2A*` has dual pairing `-1` with
`x_p` for `i<p`, and `+1` for `i>p`; it does not annihilate the pivot query.
Counting all those lines across the pivot overstates the idle rank by one.
At L18 its outer rank surplus is 297, whereas any complete rank-two-stage
invoice for this shortest root has surplus

`n-t+16L = (L-1)+16L = 17L-1 = 305`.

The missing eight units must be repaired before a kappa claim is considered.
Neither the proxy comparison nor this rank discrepancy alone decides whether
a different legal idle decomposition has a better complete recurrence.

## 6. Evidence and scope

`check.py` uses only integer operations for its root, commutation, polynomial
identity and transport checks. It checks every pivot of every even L from 2
through 20, and directly tests the cross-side nullspace without invoking the
endpoint argument. Wrong thin coefficients, a deleted thin query, an omitted
pivot D action are rejected. A legal enlarged-mask positive control is accepted. These tests supplement
the general proofs; they do not turn finite evidence into a universal theorem.

The parameter family answers the realizability part of #6868 OQ1. The
D_root saving is not constant for this natural minimal singleton-host family.
No claim is made about all roots outside that setting, no full native/compiler
replay is supplied here, and no selected frontier or framework assumption is
changed.

Prepared for @CubeJerry with substantial OpenAI GPT-6 assistance. Credit
DreamingOfClouds for #6833's sign-Gram root framework and #6868's uncovered-pivot
examples; the wider native/caller lineage is retained by the full invoice.
Apache-2.0.
