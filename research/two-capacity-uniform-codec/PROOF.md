# Enumerating and sampling two-capacity completions

## Contract and cited premise

Let V and W have dimension n over a finite field F_q. Fix an injection
h:U→W, and arbitrary subspaces A,B of V and C,D of W. Write

`G(h) = {g:V→W invertible | g|U=h, g(A)⊂C, g(B)⊂D}`.

The inclusions may be equalities and neither pair needs to be nested.
Ali Romman's [PR6539](https://github.com/CrocSwap/integer-mult-bounds/pull/6539),
head `96c63f994af628f574c71dca0d7ed219cbfc70c2`, gives an exact formula
N(h)=|G(h)| from a constant number of subspace calculations and at most n+1
summands. Its proof is retained verbatim in `source/PR6539-PROOF.md`.
The coupled feasibility and common-quotient construction are ToikY's PR6535.
The nested count is Nick Petalas's PR6489. These are cited premises here.
This package does not reprove their count or feasibility theorems.

The new result is an explicit enumerative construction and finite-fair-bit
sampling interface for this coupled contract. Counting-to-sampling reduction,
lexicographic interval coding and binary entropy recycling are classical.
No general literature-priority claim is made for those methods.

## 1. A conditional partition

Choose an ordered basis u_1,...,u_r of U. Extend it deterministically to a
basis of V by greedily adding standard vectors e_1,...,e_n that increase the
span. Denote the added vectors by x_1,...,x_m, where m=n-r. They are fixed
before choosing any images.

Suppose the images of x_1,...,x_i have been specified, giving an injection
h_i on U_i=U+span(x_1,...,x_i). For every y in W define

`w_i(y) = 0` if y belongs to h_i(U_i), and otherwise

`w_i(y) = N(h_i extended by x_(i+1)↦y)`.

The new source vector is independent of U_i. For y outside h_i(U_i), the
extended prescription is again an injection, so PR6539 applies with the
same two capacities. No capacity is discarded, split or replaced by a
separate independent count. In particular, the prescribed-image coupling
in the predecessor's kernel condition persists at every step.

Every g in G(h_i) has exactly one value y=g(x_(i+1)), and that value lies
outside h_i(U_i). Conversely every completion counted by that branch is a
completion of h_i. The branches are disjoint and exhaust G(h_i). Thus

`N(h_i) = sum_(y∈W) w_i(y)`.

At depth m the domain is V. A prescribed invertible map has exactly one
completion if it satisfies the capacities and zero otherwise. Every
positive leaf therefore has weight one.

## 2. Rank and unrank

Order the field elements once, then order vectors y lexicographically.
Assign each child of h_i a consecutive interval of w_i(y) integers, in
this order, starting at zero. Zero-weight children receive empty intervals.
The partition identity makes these intervals a partition of [0,N(h_i)).

Given k in [0,N(h)), choose its containing interval, subtract that
interval's left endpoint and continue. The residual integer is always in
the selected child's interval. After m choices it is zero because the
selected leaf has weight one. The fixed images on the resulting domain
basis determine all standard columns of an invertible map satisfying the
original prescription and both capacities. This is `unrank(k)`.

Conversely, for a supplied admissible map g, follow its successive images
g(x_1),...,g(x_m) and add every left endpoint encountered. This is `rank(g)`.
The same interval partition is used at every level. Induction on the
remaining depth proves

`rank(unrank(k)) = k`, and `unrank(rank(g)) = g`.

Consequently `unrank` is a bijection from [0,N(h)) onto G(h). A uniform rank
gives a uniform admissible completion, including arbitrary nonnormalized
prescribed injections. If N(h)=0, no rank or sample exists. If n=r, there
is either no completion or exactly one; no branch is needed.

The abstract statement works over every finite field with an ordered
element representation and the cited oracle. The executable uses prime
fields only. It does not implement extension-field arithmetic.

## 3. Exact sampling with a finite fair-bit budget

Put M=N(h)>0. If M=1, return rank zero without reading a bit. Otherwise
start with an interval width v=1 and value c=0. For each supplied fair bit b,
replace `(v,c)` by `(2v,2c+b)`. If v≥M and c<M, return c. If v≥M and c≥M,
subtract M from both v and c and continue. If the supplied bit budget ends,
report exhaustion. A rejected interval is recycled before another bit is
read; no candidate matrix is constructed and rejected.

For M>1, after any surviving prefix one has `0≤c<v<M`. Doubling gives
v<2M, so at most one subtraction is needed per bit. At every depth j,
the surviving bit prefixes are in bijection with

`{0,...,r_j-1}`, where `r_j = 2^j mod M`.

This follows by induction. Doubling the previous residual interval gives
every new integer once. If its size reaches M, the first M integers accept
one occurrence of every rank, and the residual interval has size
`2r_(j-1) mod M`. Previously accepted prefixes contribute the same number
of length-j extensions to every rank. Therefore, with exactly b independent
fair bits available, every rank has exactly

`(2^b-r_b)/M`

successful length-b bit strings, and exactly r_b strings exhaust the budget.
In particular,

`P(exhaustion) = (2^b mod M)/2^b`,

and every admissible map has probability

`(1-P(exhaustion))/M`.

Conditional on success, the distribution is exactly uniform whenever the
success event has positive probability. No approximate rounding or modulo
bias is introduced. The caller must supply independent unbiased bits; this
is a sampling interface, not a physical random-bit generator.

For an unlimited fair stream, write T for the number of bits used and
t=ceil(log_2 M). The tail identity gives

`E[T] = sum_(j≥0) (2^j mod M)/2^j < t+2`.

Indeed the first t summands are at most one, and the remaining sum is
strictly below `sum_(j≥t) M/2^j = 2M/2^t ≤ 2`.
Exhaustion probability tends to zero. For a power of two, exactly log_2 M
bits suffice. The executable takes at most 4,096 bits and returns exhaustion
explicitly. The infinite-stream statement is a mathematical consequence,
not an unbounded executable loop.

## 4. Exact operation bounds and limits

An encoding or decoding path has m=n-r levels and at most q^n candidate
image vectors at each level. At most one call of the cited count oracle is
made per candidate. Including initialization, either operation needs at most

`1 + (n-r) q^n`

count-oracle calls. No collection of complete matrices is generated. The
baseline literal universe has q^(n^2) matrices. These are exact candidate
bounds, not measured runtime comparisons or a polynomial-time sampler.
The algorithm remains exponential in n.

Our direct oracle implementation uses O(n^4) field operations for basis
calculations and O(n^2) integer products/divisions in the formula. The
field-operation bound allows a separate linear solve for every mapped basis
vector. It is not a bit-complexity bound. Every count is at most
|GL_n(F_q)|≤q^(n^2), with equality in the latter bound only at n=0, where
there is one empty isomorphism. For n≥1 the zero matrix is singular, so the
inequality is strict. Count integers therefore have O(1+n^2 log q) bits,
recovering O(n^2 log q) for n≥1. At n=0, the unique rank is zero and the
M=1 sampling case in Sections 2 and 3 already applies. Reconstruction of
standard columns takes O(n^4) further field operations. The fair-bit
recurrence uses O(b) arithmetic steps on integers smaller than 2M, followed
by one unrank call on success.

The executable enforces n≤12, prime q≤31, q^n≤4,096 and b≤4,096. It keeps
one partial prescription and bounded row-reduction workspaces, rather than
a tree of all completions. Python allocates managed integers and containers;
no allocation-free execution or physical storage tariff is claimed. Functions
use bounded loops, normal input errors and invariant checks that remain
enabled under optimization. The finite verifier's enumerations have separate
explicit dimension and field bounds.

This is unrestricted GL construction. It does not preserve a symplectic form
or signed phases, construct an actual native contact, price scalar basis
changes or establish caller access, dirty restoration, physical routing,
precision, stock, tapes, compiler or outer closure. All five selected
framework assumptions remain. No new kappa or selected-frontier change follows.
