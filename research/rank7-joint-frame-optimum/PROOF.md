# Fixed-interface frame optimality proof

## 1. The finite constraint problem

A scalar event has one variable subspace common to its one or two operands.
For each register, split the chronological event sequence at its fixed warp
interfaces. Initial, terminal and centre-interface frames are constants.
Consecutive events in each segment give containment edges `U ⊆ V` and charge
`H_(dim V − dim U)`. A zero difference costs zero. Warp actions connect fixed
interfaces and introduce no variable transition. The eight centre descents
contribute the fixed profile `{8:8}`.

`graph.build` reconstructs these edges from the literal words, without using
the source profile to define costs. Its subsequent recount must equal the
source's complete local profile and helper inventory. All 72 removed helpers
are checked to have no scalar or warp events. They introduce no free variables.

The original source frames satisfy every edge. For any feasible assignment,
induction in chronological order bounds each scalar frame below by the join
of the preceding operand bounds. Reverse induction bounds it above by the
intersection of following operand bounds. Every legal frame is therefore in
one computed interval `[L,U]`. A gate's bounds may cross A/B/restore section
boundaries; no restore entrance is held artificially fixed.

All nontrivial quotients `U/L` have dimension at most three. Begin with `L`
and repeatedly adjoin one vector of `U` in at most `dim U − dim L` rounds.
Every intermediate subspace is spanned by such a sequence, so `spaces.domain`
exhausts the interval. Dimension three gives sixteen subspaces, including
all rotated lines and planes. Forced variables are constants. Join remaining
variables when an edge connects them. No constraint or tariff term crosses
between the resulting components.

## 2. Exact variable elimination

An edge factor stores its tariff vector for every contained endpoint pair.
For each component, eliminate one variable at a time. Multiply the incident
factors by adding their profile vectors. For each assignment to the remaining
boundary variables, keep the least profile over the eliminated variable.
Keep the number of assignments attaining it and, separately, the number of
all feasible assignments. Counts multiply when factors join and add when
choices of the eliminated variable are summed.

Every eliminated variable belongs to exactly one generated factor. Thus factors
never count the same eliminated choice independently. Induction proves that
each table entry is exactly the minimum over all eliminated assignments
consistent with that entry, and both counts are exact. At the final empty
scope this is the complete component minimum. Components then multiply their
counts independently.

The elimination order affects computational cost but not the result. The
published order chooses the smallest next domain product, then degree, then
event index. No table is truncated. Capacity exhaustion or an unproved tariff
comparison raises an error. The largest actual domain product is 2,560.

## 3. Uniform exact tariff comparisons

Write a difference of two candidate profiles as integer coefficients `d_r`.
For any fixed boundary assignment, the rank mass of the eliminated internal
transitions telescopes. The checker explicitly verifies

`Σ_(r=1)^9 r d_r = 0`.

A comparison ignores the common positive factor `73^b` and compares
`F(b) = Σ d_r r^(1−b)`. There are no floating-point decisions. Every retained
comparison is proved uniformly for `0 < b <= B`, where `B=1/100`, by one of
these two sufficient tests. Failure of both directions aborts the replay.

### Discrete concavity

For `k=1,...,8`, put `c_k = −Σ_(r>k) (r−k)d_r`. The rank-mass identity gives

`F(b) = Σ_(k=1)^8 c_k [2 k^(1−b) − (k−1)^(1−b) − (k+1)^(1−b)]`.

The function `x^(1−b)` is strictly concave on nonnegative x for `0<b<1`.
If every `c_k >= 0` and some is positive, the difference is strictly positive.
An identically zero profile difference is an exact tie.

### Rational logarithm and Taylor bound

Put `L_r=ln r`,

```text
D = −Σ d_r r L_r,
S =  Σ d_r r L_r²,
P =  Σ_(d_r>0) d_r r L_r³.
```

For x nonnegative, Taylor's remainder gives

`1−x+x²/2−x³/6 <= exp(−x) <= 1−x+x²/2`.

Apply the lower polynomial to positive coefficients and the upper polynomial
to negative coefficients. The constant term cancels by rank mass, giving

`F(b)/b >= D + b S/2 − b² P/6`.

The positive factor `73^b` remains irrelevant. If rational interval arithmetic
gives lower bounds `Dlo,Slo` and an upper bound `Phi`, then

`Dlo − B max(0,−Slo)/2 − B² Phi/6 > 0`

proves strict positivity throughout `0<b<=B`.

For each integer `1<=r<=9`, use `z=(r−1)/(r+1)` and the exact series

```text
ln r = 2 Σ_(j>=0) z^(2j+1)/(2j+1).
```

The first 96 terms give a rational lower bound. Its omitted positive tail is
at most `2 z^193 / [193(1−z²)]`, giving the rational upper bound. Every power
and signed sum uses the correct interval endpoint. Fifteen distinct comparison
vectors need this test; their certified lower margins after dividing by b
are all positive, the smallest exceeding 0.182917. Forty-one others use
concavity, and one is equality. The complete vectors and rounded-down positive
margin bounds are recomputed into RESULT.json.

## 4. Conclusion and limits

All 210 components have a minimum profile exactly equal to their source
profile. All fixed edges and centre descents are unchanged. Therefore the
complete source local profile is optimal for every `0<b<=1/100` in this
relaxation. Both provider instances have the same exact graph result.

This proves a finite frame-cost statement. It does not assert that every
relaxed assignment is a legal native program. It leaves changed scalar words,
warp/centre interfaces, endpoints, nonmonotone transformations and different
helper/consumer contracts outside the theorem. No multiplication theorem or
new κ follows from this optimality result alone.
