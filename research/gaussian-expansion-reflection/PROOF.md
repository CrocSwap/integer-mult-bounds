# Exact reflection of the truncated expansion

This scoped implementation-preservation proof was produced by Nick Petalas.
Reflection of an even Gaussian is classical. The new step is an exact
substitution in Mason Hale's PR2313 interval backend, including its finite
truncation, per-summand rounding and outward tail units. The predecessor's
Gaussian transform, recovery theorem and controls are cited premises.

Let positive integers `s<t`, `alpha`, working precision `b`, and integer
radius `r>0` be fixed. The pinned constructor uses

```
c_k = s*k/t
J_k = [floor(c_k)-r, ceil(c_k)+r] intersect Z
E[k,a] = sum_{j in J_k, j mod s = a}
           exp_negative(pi * (j-c_k)^2 / alpha^2) / (2*alpha),
```

then adds one working-grid unit to each upper endpoint. Every expression
above is evaluated by the pinned rational/dyadic implementation. `E` is
the interval matrix, rather than merely the underlying exact real operator.

For `1<=k<t`, put `k'=t-k` and `j'=s-j`. Then

```
c_k' = s-c_k
s-ceil(c_k) = floor(c_k')
s-floor(c_k) = ceil(c_k')
j'-c_k' = -(j-c_k)
j' mod s = (-j) mod s.
```

Thus `j -> s-j` is a bijection from the complete finite interval `J_k`
to `J_k'`. It preserves the exact rational squared argument. Consequently
the interval exponential receives identical integer endpoints and working
precision, and its division by the same positive integer is identical.
The two sums have exactly the same multiset of interval summands in
corresponding cyclic positions.

The pinned interval addition adds lower endpoints and upper endpoints as
integers, without intermediate rescaling. It is therefore exactly associative
and commutative. Reversing the summation order changes neither endpoint.
Both rows receive the same final upper-endpoint unit. Hence

```
E[t-k,a] = E[k,(-a) mod s]
```

as equality of the stored `(lo,hi,bits)` triples. This proves preservation
of the actual computed enclosures, without appealing to floating-point
agreement or assuming that reflected intervals merely overlap.

Compute rows `0,...,floor(t/2)` by the original formula. For every later
row, copy its partner with cyclic column reversal. Row zero is computed
directly. If `t` is even, the self-paired middle row is also computed
directly. This constructs every matrix entry and skips no downstream work.
The proof applies to odd `t` and noncoprime `s,t` too; the retained caller
uses its stricter coprime, power-of-two-target domain.

The replacement allocates a fresh list for every row. It may reuse interval
objects across rows because the pinned `Interval` class is a frozen
dataclass and every arithmetic operation returns a new object. The
unchanged consumers read the expansion matrix and never mutate its
interval objects. All later constructor attributes, norm bounds, operator
certificates, rounded calls, inverse corrections and recovered products
therefore have their original values.

## Exact work reduction

The number of directly evaluated rows falls from `t` to `floor(t/2)+1`.
When `gcd(s,t)=1`, only `c_0` is integral. Its finite sum has `2r+1`
terms, while every other row has `2r+2`. Accordingly,

```
original exponentials = t*(2r+2)-1
reflected exponentials = (floor(t/2)+1)*(2r+2)-1
saved exponentials = (ceil(t/2)-1)*(2r+2).
```

The copy work is `(ceil(t/2)-1)*s` interval references. Matrix storage
remains `s*t` entries; there is no retained cross-invocation cache.
For the first source fixture `(s,t,alpha,b)=(5,8,5,448)`, the original
radius is `r=115`; exactly 696 expansion exponential calls disappear.
The complete retained replay finishes eight constructors and saves 11,470
such calls. Counts from the instrumented complete executions corroborate
these formulas. This is a work-count reduction, not a fixed-tape tariff.

## Binding and evidence

`adapter.py` authenticates twelve live files before loading the captured
Python source bytes. In the reflected mode, one source-bound AST edit
replaces the expansion allocation and its adjacent row loop by the new
builder. The original radius, tail guard, `self.expansion` consumer,
remaining constructor and verifier stay in place. The baseline loads the
original AST without this edit. Both modes count calls through the same
exponential wrapper, execute the complete retained verifier, and require
its original scientific receipt.

`verify.py` checks rational term bijections and literal interval equality
on additional finite fixtures, including odd targets and noncoprime
geometry. Mutation controls distinguish wrong cyclic reversal, wrong row
selection and a missing outward unit. Frozen-object and source-layout
controls check the implementation assumptions. The complete baseline and
replacement commands both execute all 289 predecessor product fixtures.
These are conformance checks of a new substitution, not an independent
audit or a new acceptance claim for the predecessor mathematics.

The universal preservation statement rests on the argument above. It is
not a proof-kernel theorem. Timing evidence is local to the declared
complete command and machine; it supplies no new multiplication exponent,
physical tape implementation, native admission or framework assumption.
