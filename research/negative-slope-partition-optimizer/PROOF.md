# Exact maximization for a negative Reading B slope

This scoped proof was produced by Nick Petalas. Apache-2.0.

## Contract and credit

Let R be a positive integer. Let phi be a real-valued function on
{0,...,R}, with phi(0)=0 and differences

```text
delta(j) = phi(j) - phi(j-1),
delta(1) >= ... >= delta(R) >= 0.
```

Fix d<0 and c>=0. For a positive integer partition of R, choose one free
piece and charge c+d phi(r) to each remaining piece. Its credit relative
to the unsplit target is

```text
Delta = phi(free) + sum_charged [phi(r) - c - d phi(r)] - phi(R).
```

Unpaidmoon's [#7299](https://github.com/CrocSwap/integer-mult-bounds/pull/7299)
states this Reading B formula. Its
[#7449](https://github.com/CrocSwap/integer-mult-bounds/pull/7449), head
`180fac9c9797fee6ec44df8d9540f71612d07e1a`, proves an existence test
and explicitly leaves the maximizing partition open. These results are
cited premises, not audit targets. The argument below uses the displayed
definition and elementary discrete concavity. It does not use either
predecessor's existence proof or executable.

## Theorem

For each piece count 2<=k<=R put m=k-1 and n=floor(R/k). For every
1<=s<=n write

```text
R-s = m q + r,    0<=r<m,
F_k(s) = phi(s) + (1-d)[(m-r)phi(q) + r phi(q+1)] - phi(R).
```

Then:

1. The maximum credit among k-piece partitions is
   `max_{1<=s<=n} F_k(s) - m c`. It is attained by a free piece s,
   m-r charged pieces q, and r charged pieces q+1.
2. F_k is a discretely concave sequence. Its forward difference is

   ```text
   D_k(s) = delta(s+1) - (1-d) delta(ceil((R-s)/m)),   1<=s<n.
   ```

3. Its first maximizing s is the first s<n with D_k(s)<=0, or n
   if no such s exists. Bounded binary search uses at most
   `ceil(log2 n)` sign comparisons, with zero comparisons when n=1.
4. Compare these R-1 values and the unsplit credit 0 to obtain the
   exact global maximum and an attaining partition. This takes
   `O(R log R)` arithmetic operations and comparisons in an exact
   tariff-value oracle model. This bound includes constructing one
   returned partition and reading an R+1-entry tariff table. It is
   not a bit-complexity or physical-caller bound.

The theorem applies to real tariffs and parameters with exact comparisons.
The supplied implementation uses rational arithmetic and a rank cap of 4096.
Its exhaustive finite corroboration has smaller, explicitly declared bounds.

## Proof

Write A=1-d>1. For a fixed multiset of pieces, the credit is

```text
A sum_i phi(r_i) + d phi(free) - (k-1)c - phi(R).
```

Since d<0, choose a piece of minimum phi-value as the free piece.
Monotonicity of phi lets us choose a shortest piece s, including when
several distinct ranks have the same tariff. Positivity and the sum R
give 1<=s<=floor(R/k), and every charged piece is at least s.

Fix k and s. If two charged ranks a,b obey b>=a+2, replace them by
a+1,b-1. They stay positive and at least s. The tariff sum changes by

```text
phi(a+1)+phi(b-1)-phi(a)-phi(b) = delta(a+1)-delta(b) >= 0.
```

Multiplication by A preserves the inequality. Repeating the exchange
terminates: the nonnegative integer sum of squares of the charged ranks
strictly decreases at each exchange. At termination those ranks differ
by at most one, hence are exactly q and q+1 with the multiplicities in
the theorem. Conversely this vector is feasible because
`R-s >= (k-1)s`, so q>=s. It has credit F_k(s)-m c. This proves part 1
without asserting uniqueness; a linear tariff can have many other optima.

Let B_m(t) denote the maximum tariff sum of m positive integers totaling
t. The same exchange argument gives its balanced formula. Removing one
unit from a largest balanced piece gives

```text
B_m(t) - B_m(t-1) = delta(ceil(t/m)),    t>=m+1.
```

For completeness, if t=mq+r with r>0, the removed unit changes one
q+1 to q, giving delta(q+1). If r=0, it changes one q to q-1,
giving delta(q). These are exactly the two ceiling cases.

For s<n we have R-s>=m+1, so subtracting adjacent F-values gives

```text
F_k(s+1)-F_k(s) = delta(s+1) - A delta(ceil((R-s)/m)).
```

As s increases, delta(s+1) does not increase. The ceiling index does
not increase, so its delta-value does not decrease. Therefore D_k(s)
does not increase. This proves part 2.

A sequence with nonincreasing forward differences increases strictly
until its first nonpositive difference, then never exceeds that value.
The first such index is the first maximizing index, even if several
zero differences follow it. If no such index exists, every step is
positive and n is the first maximum. This proves the index rule in
part 3. The search maintains an interval [low,high], initially [1,n].
At a midpoint h<high, D_k(h)>0 discards indices <=h; otherwise it
discards indices >h. The remaining interval has at most the ceiling
of half the previous length. Thus ceil(log2 n) comparisons suffice.

Every positive partition has some k between 1 and R. The case k=1
has credit zero. Part 1 covers every other k. Each F-value uses a
constant number of tariff lookups and arithmetic operations, and each
sign test does too. Performing the bounded search for every k and
comparing the values proves part 4. The flat fee affects the choice
of k but cannot change the best s at a fixed k.

## The zero-fee first example

At c=0, the all-singleton partition always attains the global maximum.
Subadditivity, obtained by summing decreasing first differences, gives
`phi(r)<=r phi(1)`. Since the free rank s>=1 also gives phi(s)>=phi(1),

```text
Delta = A sum_i phi(r_i) + d phi(s) - phi(R)
      <= [A R + d] phi(1) - phi(R).
```

All R singleton pieces attain the right-hand side. For the strictly
concave harmonic tariff any piece larger than one makes its subadditive
bound strict, so this is the unique maximizing multiset when R>=2.
This settles the zero-fee harmonic first example asked for in #7449
at every rank. The binary-search theorem also handles nonzero fees.

At R=12, d=-1 and c=0, the first fixed-length optima include

```text
k=2: (4,8),     credit 122407/27720;
k=3: (2,5,5),   credit 41747/5544.
```

The three-piece optimum strictly beats both (4,4,4) and (1,1,10).
The global optimum is twelve ones with credit 23-H_12. These rational
values and strict comparisons are computed by the verifier.

## Boundary of the argument

Concavity is essential to the charged-piece exchange. With the
nondecreasing table phi=(0,0,1,1,4,4,4), R=6, d=-1 and c=0,
the partition (1,1,4) has credit 4, whereas balancing its charged
pieces to (1,2,3) gives credit 0. The verifier computes both.

The sign restriction d<0 chooses a shortest free piece; a positive
slope chooses a largest-tariff piece instead. The supplied optimizer
rejects nonnegative slopes rather than silently using the wrong rule.

This is an accounting theorem under a declared rank-dependent fee.
It supplies no physical adapter, legal split, dirty-state restoration,
native operation, uniform compiler, selected-ledger improvement, new
kappa, or complete multiplication theorem. All five selected framework
assumptions remain. Independent human and formal proof-kernel review
are unclaimed.
