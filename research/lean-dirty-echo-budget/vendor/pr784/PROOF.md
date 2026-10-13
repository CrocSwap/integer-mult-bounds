# Ordered dirty-echo trees: cost, capacity and an exact minimum

## 1. Model and retained local identity

A leaf is a source-restoring additive shear. For arbitrary source `x`, target
`y` and fixed external data, it adds a deterministic function `f(x)` to `y`,
independently of `y`'s initial contents. Its negative call subtracts the same
value. The ideal factors are linear maps `A_0,...,A_(n-1)` on equal-length
arrays over an abelian group with linear structure; their required product is
`A_(n-1) ... A_0`. They need not commute.

An internal node has `k >= 2` consecutive, nonempty factor blocks. It reserves
`k-1` distinct dirty arrays `z_1,...,z_(k-1)` throughout the node. A disjoint
deeper pool is reused sequentially by the children. Ancestor sources, targets
and reserved arrays cannot enter that pool. Each child uses one fixed tree
every time it is called, including when its exact inverse is requested.

Let `C` be the ladder of the first `k-1` child shears, from source `x` through
the reserved arrays; let `D` omit the first link of `C`. PR673's word is

```text
C; y += A_last(z_last); C^-1;
D; y -= A_last(z_last); D^-1.
```

Inverses reverse the complete instruction order and negate signs recursively.
The first and last child run twice; every interior child runs four times.
All reserved and deeper arrays are restored. For ideal linear children the
two target inputs differ by the product of the preceding child maps on `x`,
so the target increment is the required ordered product.

The restoration argument also holds for nonlinear rounded leaves. Inverse
ladder calls see the same sources and restored deeper dirt as their forward
mates, and the intervening target update does not change any of those arrays.
Thus each node's net increment is a deterministic function of its source and
initial scratch, independent of its target. Induction preserves this interface.
Only the ideal linear increment is independent of all initial dirt.

This identity and its nonlinear restoration argument are inherited from PR673.
Concurrent PR758 supplies the all-arity optimization principle, including
unequal prices. The distinct result here is the scratch-dependent bound and
attaining family in Section 3; an independent uniform-cost optimizer supplies
finite evidence for the same tree model.

## 2. Exact optimality recurrence

For a tree `T`, let `n(T)`, `N(T)` and `S(T)` count factors, completed leaf
calls and simultaneously borrowed arrays. A leaf has `(1,1,0)`. At an internal
node, with weights `w_1=w_k=2` and all interior `w_i=4`,

```text
n(T) = sum_i n(T_i)
N(T) = sum_i w_i N(T_i)
S(T) = k-1 + max_i S(T_i).
```

Every restoration child is included. Storage takes a maximum because children
execute sequentially and return their deeper pool exactly; the `k-1` parent
arrays remain reserved during each call.

Let `F(n,s)` minimize `N(T)` over this grammar with `n(T)=n` and `S(T)<=s`.
Write `infinity` when no such tree exists. Then

```text
F(1,s) = 1                         (s >= 0)
F(n,0) = infinity                  (n > 1)
F(n,s) = min over k=2,...,min(n,s+1) and n_1+...+n_k=n, n_i>=1:
         2 F(n_1,s-k+1) + 4 sum_(1<i<k) F(n_i,s-k+1)
         + 2 F(n_k,s-k+1).         (n > 1)
```

Any allowed tree appears in this minimum at its root. Replacing each child
by an optimum for the same interval and remaining budget can only reduce
cost and cannot violate storage or factor order. Conversely, concatenating
any minimizing children in the echo realizes that candidate. Induction on
the budget proves equality, including infeasible states.

`plan_table` evaluates this recurrence by min-plus convolution of child costs.
After each position it retains a minimum-cost prefix for each factor total.
All future costs depend only on that total and the common remaining budget,
so discarded prefixes cannot yield a cheaper completion. Ties retain the first
encountered plan; lower-budget plans are considered first. This deterministic
tie rule is not a uniqueness claim.

This optimizes uniform leaf calls. For different per-factor costs the interval
itself, not only its length, would become part of the state. That weighted
optimization is outside this result.

## 3. Capacity and a matching analytic lower bound

**Capacity.** A tree fitting `s` arrays has at most `2^s` factors. At a `k`-ary
root its children have budget `r=s-k+1`, so induction gives at most
`k*2^r <= 2^s`, since `k <= 2^(k-1)`. Balanced binary trees attain every
positive factor count up to `2^s`. Hence feasibility is exactly `n <= 2^s`.

**Lower bound.** Every tree fitting budget `s` satisfies

```text
N(T) >= 2^(s+1) n(T) - 4^s.                         (1)
```

For a leaf the difference between the two sides is `(2^s-1)^2 >= 0`.
At a `k`-ary root put `r=s-k+1`, `p=2^r`, `t=2^(k-1)` and
`C=sum_i w_i=4k-4`. The child induction hypothesis gives

```text
N(T) >= 2p sum_i w_i n_i - C p^2.
```

Subtract the desired right-hand side, `2pt sum_i n_i - t^2 p^2`.
Because `n_i<=p` by capacity and `t>=w_i`, the difference is at least

```text
p^2 (t^2 - 2kt + C)
  = p^2 (t-2)(t-2k+2) >= 0,
```

using `2^(k-1)>=2k-2` for `k>=2`. This proves (1) for every allowed tree,
independently of the finite dynamic-programming replay. The bound may be
negative and uninformative outside the regime below.

**Attainment.** Let `s>=2` and `q=2^(s-2)`. For every integer
`3q <= n <= 4q`, put `b=n-3q`. Take a full binary top tree of depth `s-2`
whose `q` bottom blocks are `b` four-factor binary trees and `q-b` flat
three-factor echoes. These bottom blocks use two arrays each and cost 16
or 8 calls. Each appears `q` times under the binary top tree. Thus

```text
S = s,
N = q [16b + 8(q-b)] = 2^(s+1)n - 4^s.
```

Together with (1), this proves the exact formula throughout
`3*2^(s-2) <= n <= 2^s`. This sufficient equality interval is not claimed
maximal. For `n=50,s=6`, fourteen three-factor and two four-factor blocks
give `N=128*50-4096=2304`. The pinned balanced binary count is 2752;
the savings are achieved without an extra array or any clean data assumption.

The other reported minima, `F(50,7)=1472` and `F(50,8)=1120`, come from the
exact recurrence and emitted witnesses. They are not instances of (1)'s
attainment formula.

## 4. Complete local cost and approximation recurrence

Let `m_j` be the number of executed occurrences of factor `j`. It is the
product of the endpoint/interior weights along that leaf's path, and
`sum_j m_j=N`. The verifier checks these counts against the emitted word.
For a completed leaf let `L_j` charge its arithmetic, source access,
coefficient/phase access, validation and all source restoration. Let `R_j`
charge any additional routing needed for that leaf. The total bill is

```text
T_total = P_plan(n,s) + P_coefficients_and_phases(n,L,w) + Admission(L,s)
          + sum_j m_j (L_j(L,w) + R_j(L,w)) + O((s+1)N).
```

The abstract recursive executor has node cost `sum_i w_i T_i + O(k)`.
The reference Python generator additionally forwards each yielded leaf through
up to `s` ancestor generator frames, so `O((s+1)N)` charges its dispatch,
including all inverse calls.
There are no implicit copies or clean length-`L` arrays. Live data consists
of source, target and `S(T)` dirty arrays. The reference retains the selected
tree, factor descriptors and `O(s)` active schedule records. Retaining the
tree and computing it are charged preprocessing, not free advice.

The table performs `O(s^3 n^2)` min-plus comparisons, with at most `O(s)`
references copied at each successful update: `O(s^4 n^2)` elementary work
is a conservative bound for this implementation. Stored plan nodes use
`O(s^2 n)` references; integer sizes and arithmetic must also be paid in a
bit model. Precomputation may be shared only when the same schedule is reused.
Every tree has `S(T)<=n-1`, justifying the optimizer's cap on surplus budget.

The pinned PR628 leaf makes three computational passes plus its stability
and grid-validation scans. Inner and outer factors can have different
phase-access costs, so a minimum of `N` need not minimize their weighted
sum. The rounded checks instrument actual phase reads and per-factor calls;
the certificate does not treat dispatch count as free volume-weighted work.
The radix normalization, when present, is paid in a leaf multiplier.
No frame conversion is performed at this array interface. Conversion to a
physical supplier, common-label/tape layout and arbitrary-stride routing are
additional obligations, not free consequences of a valid echo.

For approximation, inherit PR628/PR673's completed-leaf hypotheses. Each ideal
factor has norm at most `K=r/beta`; the rounded leaf error on a source of norm
at most `B` is at most `a(B+1)u`, where

```text
a = 13(r+1)/beta^3,  u=2^-w,  G=2+K,
a*u <= 1,  u <= beta^2/2.
```

If `D` bounds all initial source, target and dirty-array norms, the actual
maximum array norm `M_j` after `j` completed leaves satisfies
`M_j+1 <= G^j(D+1)`. Let `E_j` be the maximum error against the ideal word
after the same `j` leaves. Comparing the full rounded word
with the full ideal word, including all restoration leaves, gives

```text
E_(j+1) <= (1+K) E_j + a*u*G^j(D+1),
E_N <= N*a*(D+1)*u*G^(N-1).
```

Therefore execution error is at most `2^(-p-1)` when

```text
w >= p+1+ceil(log2(N*a*(D+1))) + (N-1)*ceil(log2 G),
```

in addition to the two leaf precision conditions. Source and scratch
restoration remain exact. Initial dirt may affect the rounded target
increment within this bound. The same coefficient/phase preparation theorem
must separately supply at most `2^(-p-1)` operator error scaled for the
original source norm; it is not proved anew or removed here.

Transient integer magnitudes also require bits. The completed-array bound
above contributes `ceil(log2(D+1))+N*ceil(log2 G)` bits; the inherited causal
and closure scalar estimates add `O(log(r/beta))`. With fractional precision
`w`, charge arithmetic at the resulting total width `W` and
`O(L(S(T)+2)W)` mutable data bits, in addition to the plan, descriptors and
the pinned leaf's `O(1)` clean scalar words and the chosen fast-arithmetic
implementation's workspace. No bit-reversible arithmetic compiler is supplied.

This is a complete local array-level recurrence. It is not a complete
integer-multiplication recurrence. The fixed-budget optimization does not
alter the selected bit or complex supplier or any binding assembly constraint.
No improved multiplication exponent, globally optimal reversible program,
practical runtime speedup or fully formalized theorem follows from it.
