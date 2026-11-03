# One reusable clean checkpoint has no unit-price count advantage

This scoped proof was produced by Nick Petalas. Apache-2.0.

## Contract and predecessor results

Use Stephen Shore / nightangelflowerwin-ops's ordered binary,
reserved-connector class from [PR788](https://github.com/CrocSwap/integer-mult-bounds/pull/788).
There are `s >= 1` scratch arrays, exactly one supplied initially zero and
the others arbitrary. A connector remains reserved throughout its node's
invocation. Each child restores its scratch before the next invocation.
Every signed leaf invocation costs one. Factor order is fixed.

A dirty connector invokes its left and right children twice each. A clean
connector invokes its left child twice and its right child once. Reserving
the clean connector leaves only dirty scratch to its children. Reserving
a dirty connector permits both sequential children to reuse the same clean
array. These are the predecessor's interface and restoration identities.
They are premises here, not new identities or newly audited implementations.

Let `D_s(n)` be the minimum with `s` all-dirty arrays. Let `C_s(n)` be the
minimum with one clean and `s-1` dirty arrays. A leaf costs one. A nonleaf
obeys the exact class recurrences

```
D_s(n) = min_(a+b=n) 2 D_(s-1)(a) + 2 D_(s-1)(b),
C_s(n) = min_(a+b=n) {
    2 D_(s-1)(a) + D_(s-1)(b),
    2 C_(s-1)(a) + 2 C_(s-1)(b)    if s >= 2.
}
```

The second line is the extra reuse freedom. PR788 supplies its exact
interval/weighted formulation and a strict weighted improvement. FanPUYen's
[PR714](https://github.com/CrocSwap/integer-mult-bounds/pull/714) supplies the
clean-root formula below with balanced dirty children. The new step proves
that the full reuse freedom cannot improve that formula at unit prices,
for any `n` or admitting scratch cap.

## The theorem

There is no admissible binary tree when `n > 2^s`. Otherwise

```
C_s(1) = 1,
C_s(2) = 3,
C_s(n) = F(n) = 6q(n-2q)       for n >= 3,
```

where `q` is the unique power of two with `3q <= n < 6q`.
The value is independent of `s` throughout the feasible range. A clean
root with balanced all-dirty children attains it using only
`ceil(log2(n))` scratch arrays for `n >= 2`.

This is optimality within this binary grammar. It is neither a general
reversible-program lower bound nor an optimal physical work invoice.

## All-dirty envelope and clean-root lower bound

Write

```
D(n) = p(3n-2p),        p = 2^floor(log2(n)), n >= 1.
```

This is the balanced all-dirty leaf count used by the predecessors.
For completeness, its discrete increment is
`D(j+1)-D(j) = 3*2^floor(log2(j))`, so `D` is discretely convex.
Consequently the minimum of `D(a)+D(n-a)` occurs at the two most balanced
integer arguments. Direct substitution gives
`D(2m)=4D(m)` and `D(2m+1)=2D(m)+2D(m+1)`.
Induction in the dirty recurrence proves that every dirty tree costs at
least `D(n)` and a balanced tree attains it whenever its height fits.

Fix `n >= 3` and its `q`. The affine pieces of the convex function `D`
give supporting lines valid at every positive integer `x`:

```
D(x) >= 3q x - 2q^2,
D(x) >= 6q x - 8q^2.
```

Their equality intervals are `[q,2q]` and `[2q,4q]`, respectively. Thus

```
2D(a) + D(b) >= 6q(a+b) - 12q^2 = F(n).
```

Equality holds for the familiar PR714 interval
`max(q,n-4q) <= a <= min(2q,n-2q)`. In particular choose
`a = min(2q,n-2q)` and `b=n-a`. For `3q <= n <= 4q`, the larger child is
`2q`, half the least power of two admitting `n`. For `4q < n < 6q`, the
larger child is `n-2q < 4q`, also at most half that admitting power.
Balanced dirty children therefore fit in `ceil(log2(n))-1` arrays.
For `n=2`, the two singleton children cost three and fit under one clean
connector. These facts establish an attaining clean-root tree for every
feasible `n >= 2`.

## The new reuse inequality

Extend the notation by `F(1)=1` and `F(2)=3`.
Its first differences are `2,3`, followed by `6q` at every integer
`3q <= j < 6q`. They never decrease. Hence `F` is discretely convex,
and for every positive `a+b=n`,

```
2F(a)+2F(b) >= 2F(floor(n/2))+2F(ceil(n/2)).
```

For `n >= 4`, the right side equals `F(n)`. To see this without an
asymptotic argument, linearly interpolate `F` on `[2,infinity)`.
On `[2,3]` it is `3x-3`, and thereafter its successive pieces are
`6q(x-2q)` on `[3q,6q]`. All breakpoints are integers and doubling an
argument multiplies its interpolated value by four. The interpolation
is affine between the two consecutive integers surrounding `n/2`.
Therefore its doubled midpoint identity is exactly the displayed equality.
The remaining cases give `2F(1)+2F(1)=4>F(2)` and
`2F(1)+2F(2)=8>F(3)`.

It follows for every `a,b >= 1` that

```
2F(a)+2F(b) >= F(a+b).
```

Now induct on factor count in the full one-clean recurrence. A clean
root costs at least `F(n)` by the preceding all-dirty bound. A dirty
root costs at least `2F(a)+2F(b)`, because each child has fewer factors;
the reuse inequality bounds that by `F(n)`. The attaining clean-root
tree proves equality. This includes arbitrarily many opportunities to
reuse the clean array at successive dirty nodes, not only a single
root comparison.

Finally, every root-to-leaf path reserves at most `s` distinct connectors.
Its depth is at most `s`, so a binary tree has at most `2^s` leaves.
This proves infeasibility above capacity independently of prices.

## Evidence and limits

The verifier exhausts the full clean/dirty recurrence for `n <= 256` and
caps `1..10`, and checks both root inequalities at every split through
256. Large exact integer fixtures test scaling, convexity and balanced
identities near dyadic breakpoints. The written proof, not their finite
range, establishes the theorem for all positive factor counts.

An independently written iterative emitter and dense coefficient interpreter
execute attaining words and their literal inverses. Every source, target
and dirty-input column is tracked under noncommuting two-dimensional
integer factors. The clean entry is exactly zero. This checks these new
attaining words; it executes no predecessor code and supplies no new
rounded leaf or physical interface theorem.

Unequal leaf prices are excluded: PR788 already gives a strict weighted
gain. Two clean arrays are excluded: Better-Call-Paul's PR829 treats that
changed resource. Higher arity, nonreserved lifetimes, phase scans,
dispatch, clean provisioning, routing, precision, native implementation,
hosting, all-size compilation and outer admission remain outside the
count optimum. No selected frontier or kappa changes.
