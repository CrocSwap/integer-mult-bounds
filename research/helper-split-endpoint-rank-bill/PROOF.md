# Endpoint maximum of one contact-free helper split

**Proof. No new κ.** The selected conditional exponent stays
`363005817/100000000000`. No word is emitted and no cut is declared legal.

## Hypotheses

Fix an integer `D ≥ 1` and a real exponent `0 < t < 1`. A helper whose boundary
runs from the zero subspace to a `D`-dimensional space is cut at an intermediate
dimension `x`, using `m ≥ 1` contact-free transport paths. Path `i` has integer
endpoints `0 ≤ a_i ≤ b_i ≤ D` and a constant old paid-rank charge `c_i`. On the
open interval where every leg length is positive,

```text
G(x) = x^t + (D-x)^t - D^t
       - Σ_i ( (x-a_i)^t + (b_i-x)^t - c_i ).
```

Set `0^t = 0`, so `G` extends continuously to a closed interval on which every
leg length is nonnegative. A zero leg is omitted from a physical word; the
formula still uses `0^t = 0`. The feasible dimensions coming from the paths
alone lie in `[A0, B0]` with `A0 = max a_i` and `B0 = min b_i`, when `A0 ≤ B0`.
A geometric join or meet may shrink that interval to a closed subinterval
`[A, B]`.

This is the rank bill in
`research/p104-shared-native-helper-splits/EXPLORATION.md`. It is not an
ordinary-cost bill, a native legality test, or a supplier invoice.

## Lemma 1

Let `h(u) = u^t` for `u > 0`. Then `h''(u) = t(t-1) u^{t-2} < 0`. For
`0 < u ≤ v`,

```text
h''(u) ≤ h''(v).
```

Write `t = p/q` in lowest terms, `1 ≤ p < q`. Then `t-2 = (p-2q)/q` and
`s = 2q-p > q ≥ 1`. For positive `u, v`,

```text
u^{t-2} ≥ v^{t-2}  ⟺  u^s ≤ v^s,
```

because `x ↦ x^{s/q}` is increasing on the positive reals and taking
reciprocals reverses the inequality. The integer form `u ≤ v ⟹ u^s ≤ v^s`
is the comparison the verifier exhausts. Since `t(t-1) < 0`, the inequality
on `u^{t-2}` reverses when it is multiplied into `h''`.

## Lemma 2

On every open interval where `0 < x < D` and `a_i < x < b_i` for every path,

```text
G''(x) ≥ 0.
```

If `m ≥ 2`, or if `m = 1` and that unique path is not `(a, b) = (0, D)`, the
inequality is strict.

Proof. Differentiate termwise:

```text
G''(x) = h''(x) + h''(D-x)
         - Σ_i ( h''(x-a_i) + h''(b_i-x) ).
```

For each `i`, `x-a_i ≤ x` and `b_i-x ≤ D-x`. Lemma 1 gives

```text
h''(x-a_i) ≤ h''(x),    h''(b_i-x) ≤ h''(D-x),
```

so each path contributes at most `h''(x)+h''(D-x)`. Therefore

```text
G''(x) ≥ (1-m) ( h''(x) + h''(D-x) ).
```

The sum of second derivatives is negative, and `1-m ≤ 0`, so the product is
nonnegative. Equality in a path bound holds if and only if `a_i = 0` and
`b_i = D`. For `m = 1` that is the full-span path. For `m ≥ 2` the factor
`1-m` is at most `-1` and the second-derivative sum is strictly negative, so
`G''` is strictly positive.

## Theorem

Let `[A, B] ⊆ [0, D]` be a closed interval on which every leg length is
nonnegative, with `A ≤ B`. Then

```text
max_{x ∈ [A, B]} G(x) = max( G(A), G(B) ).
```

The identity includes the cases `A = 0` and `B = D`. An interior point of
`[A, B]` is never a separate rank-bill case.

Proof. If `A = B` there is nothing to prove. Assume `A < B`. Every path
satisfying `a_i ≤ A` and `b_i ≥ B` has positive leg lengths on `(A, B)`.
Lemma 2 therefore gives `G'' ≥ 0` on `(A, B)`, so `G` is convex there.
A convex function on an open interval that extends continuously to the
closure remains convex: for endpoints `x, y` and a weight `λ`, approach
`x` and `y` by interior points and pass to the limit. A continuous convex
function on a compact interval attains its maximum at an endpoint.

When `m ≥ 2`, or when `m = 1` and the unique path is not `(0, D)`, Lemma 2
gives `G'' > 0` on `(A, B)`. Then `G` is strictly convex on the open
interval. An interior point cannot attain the maximum of the continuous
extension: if `G(x0)` equalled that maximum for `x0 ∈ (A, B)`, writing
`x0` as a convex combination of two other interior points would put
`G(x0)` strictly below the maximum. Thus every interior dimension is
strictly below `max(G(A), G(B))`. In particular, two or more full-span
paths are strictly convex, not constant. Only the one-path full span is
the constant function in the next section, and only there does every
dimension tie the endpoints.

Thus every interior dimension, including the dimension of a join or meet of
three or four paths, satisfies `G(x) ≤ max(G(A), G(B))` for the interval of
that same path subset. Evaluating the two endpoint dimensions decides the
rank bill. No intermediate subspace can raise it.

## What 0 and D are

A dimension `0` or `D` is an existing boundary chart, not a new intermediate
chart. The theorem still prices it.

- If `A = 0`, every proper dimension `x ∈ (0, B]` satisfies
  `G(x) ≤ max(G(0), G(B))`. When `G(B) ≥ G(0)`, the maximum on the proper
  dimensions is `G(B)`, attained at `B`. When `G(B) ≤ G(0)`, no proper
  dimension beats the existing boundary value `G(0)`.
- If `B = D`, the symmetric statement holds with the candidate `A`.

This is the separate treatment named in `EXPLORATION.md` for an extremum at
`0` or `D`. It collapses to the same endpoint comparison. It does not require
a search over the integers strictly between the endpoints.

## One-path normalization

Specialize to `m = 1`, endpoints `0 ≤ a ≤ b ≤ D`, and the single old charge
`c = (b-a)^t`. Then, for `x ∈ [a, b]`,

```text
G(x) = x^t + (D-x)^t - D^t - (x-a)^t - (b-x)^t + (b-a)^t.
```

At the endpoints the new legs reproduce the old charge:

```text
G(a) = a^t + (D-a)^t - D^t,
G(b) = b^t + (D-b)^t - D^t.
```

Let `k(u) = u^t + (D-u)^t - D^t` for `u ∈ [0, D]`. Then `k(0) = k(D) = 0` and
`k(u) = k(D-u)`. The derivative `k'(u) = t u^{t-1} - t (D-u)^{t-1}` is
positive on `(0, D/2)` and negative on `(D/2, D)`, because `u ↦ u^{t-1}` is
strictly decreasing. Therefore `k(u) > 0` for every `u ∈ (0, D)`.

Consequences, still only for this charge:

- If `0 < a < b < D`, then `G(a) > 0` and `G(b) > 0`. The better rank-bill
  dimension on `[a, b]` is whichever endpoint has the larger `k` value.
- If `a = 0` and `b < D`, then `G(0) = 0 < G(b)`. The unique maximizing
  dimension is the proper endpoint `b`. Every `x ∈ (0, b)` is strictly
  smaller, by the strict-convexity paragraph in the theorem.
- At `t = 1/2` the same sign has an algebraic form. For `u ∈ [0, D]`,
  `(sqrt(u) + sqrt(D-u))^2 = D + 2 sqrt(u(D-u))`, so
  `sqrt(u) + sqrt(D-u) > sqrt(D)` if and only if `u(D-u) > 0`.
- If `b = D` and `a > 0`, the unique maximizing dimension is `a`, and
  `G(D) = 0`.
- If `a = 0` and `b = D`, then `G(x) = 0` for every `x`. The full-span path
  cancels the helper split exactly.

A positive value of `G` is a rank-bill signal under these hypotheses. It is
not a legal kernel cut, not a paid-profile improvement, and not a change in
the selected exponent.

## What this does not prove

The curvature comparison uses a boundary that runs from dimension `0` to
dimension `D`. A proper helper boundary, a path that leaves that boundary, a
paid ordinary bill, ownership, and native legality are outside the argument.
`EXPLORATION.md` already records that limitation. Constants `c_i` other than
`(b_i-a_i)^t` stay inside the theorem and outside the one-path sign
corollary. No finite grid in the verifier is the proof; the proof is the
differentiation above.
