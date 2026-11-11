# Proof: proper helper terminals and the rank bill

**Proof. No new κ.** The selected conditional exponent stays
`363005817/100000000000`. No word is emitted and no cut is declared legal.

## Hypotheses

Fix a real exponent `0 < t < 1` and integers `0 < T < D`. A helper boundary
runs from the zero subspace to a proper terminal of dimension `T`, strictly
inside the ambient `D`-dimensional space. The helper is cut at an intermediate
dimension `x`, using `m ≥ 1` contact-free transport paths. Path `i` has integer
endpoints `0 ≤ a_i ≤ b_i ≤ D` and old charge `(b_i - a_i)^t`. A path with
`b_i > T` leaves the boundary.

Write `h(u) = u^t` for `u > 0` and `h(0) = 0`. On the closed feasible interval
`[A, B]`, with `A = max a_i` and `B = min(T, min b_i)`, every leg length is
nonnegative and the rank bill is

```text
G(x) = h(x) + h(T-x) - h(T)
       - Σ_i ( h(x-a_i) + h(b_i-x) - h(b_i-a_i) ).
```

This is the #7283 formula with the helper dimension `D` replaced by the
terminal `T`. A zero leg is omitted from a physical word; the formula keeps
`h(0) = 0`. The value `G` is the rank-bill factor only. It is not an ordinary
cost, a legality test or a supplier invoice.

The interval endpoints are feasible dimensions. `A` is the largest path start,
and `B` is the terminal when at least one path crosses it, otherwise the
smallest path end. Joins or meets can only shrink `[A, B]`, and the argument
below applies to every closed subinterval on which all legs are nonnegative.

## Lemma 1 (concavity and its derivative)

For `0 < u < v`,

```text
h'(u) = t u^(t-1) > t v^(t-1) = h'(v).
```

Both sides are positive because `0 < t < 1`, and `u^(t-1) > v^(t-1)`
because `u < v` and `t - 1 < 0`. Hence `h` is strictly concave and `h'` is
strictly decreasing on `(0, ∞)`. The verifier checks the equivalent integer
form: for `t = p/q` in lowest terms, `s = q - p > 0`, and `u ≤ v` implies
`u^s ≤ v^s`.

The same strict monotonicity gives the increment form used below. For
`0 ≤ y < z` and `x > 0`,

```text
h(z) - h(z-x) < h(y+x) - h(y)
   if and only if z-x > y,
```

because both increments are `∫_0^x h'(base + s) ds` and `h'` is strictly
decreasing. We use the case `y = T-x`, `z = b` with `b > T`.

## Lemma 2 (subadditivity)

For `u, v ≥ 0`,

```text
h(u+v) ≤ h(u) + h(v).
```

For positive `u, v` this is the strict concavity inequality
`h(u) ≥ h(u+v) + h'(u+v)(u - (u+v))`, together with the symmetric bound for
`h(v)`; the boundary cases follow from `h(0) = 0`. Equality holds only when
`u = 0` or `v = 0`.

## Lemma 3 (the terminal is not a positive bill)

Suppose every path has `a_i ≤ T ≤ b_i`. Then

```text
G(T) = - Σ_i ( h(T-a_i) + h(b_i-T) - h(b_i-a_i) ) ≤ 0.
```

The helper terms vanish because `h(T) - h(T) = 0` and `h(0) = 0`. Each summand
is nonnegative by Lemma 2, applied to `u = T - a_i` and `v = b_i - T` whose sum
is `b_i - a_i`. A summand is zero exactly when `T` equals `a_i` or `b_i`.
Therefore `G(T) ≤ 0`, with equality exactly when `T` is an endpoint of every
path.

## Lemma 4 (no path starts inside the boundary)

Suppose every `a_i = 0`, at least one path crosses (`b_i > T`), and
`0 < x < T`. Then `G(x) < 0`.

Proof. Substitute `a_i = 0`:

```text
G(x) = - (h(T) - h(T-x)) + Σ_i ( h(b_i) - h(b_i-x) ) - (m-1) h(x).
```

For a crossing path, `b_i > T`, so `b_i - x > T - x`. Lemma 1 with
`y = T-x`, `z = b_i` gives

```text
h(b_i) - h(b_i-x) < h(T) - h(T-x).
```

Summing over the `m` paths,

```text
Σ_i ( h(b_i) - h(b_i-x) ) < m ( h(T) - h(T-x) ),
```

so

```text
G(x) < (m-1) ( h(T) - h(T-x) ) - (m-1) h(x)
     = -(m-1) ( h(x) + h(T) - h(T-x) ).
```

For `m ≥ 2` the right side is negative because `h(x) > 0` and
`h(T) > h(T-x)`. For `m = 1` the strict increment inequality alone gives
`G(x) < 0` without the last line. At `x = 0` every term vanishes, so
`G(0) = 0` and the maximum is attained only at the left endpoint.

## Theorem 1 (one crossing path)

Suppose `m = 1` and `b > T`. Then `G` is strictly decreasing on `[a, T]`, so
its maximum on the feasible interval is `G(a)`.

Proof. For `a < x < T` the legs are positive and

```text
G'(x) = h'(x) - h'(T-x) - h'(x-a) + h'(b-x)
      = [h'(x) - h'(x-a)] + [h'(b-x) - h'(T-x)].
```

Since `a ≥ 0`, we have `x - a ≤ x`, and Lemma 1 gives
`h'(x-a) ≥ h'(x)`, with equality only if `a = 0`. Since `b > T`, we have
`b - x > T - x`, and Lemma 1 gives `h'(b-x) < h'(T-x)`. The second bracket is
strictly negative, so `G'(x) < 0` on `(a, T)`. A differentiable function with
a strictly negative derivative on an open interval is strictly decreasing
there; `G` is continuous on the closed interval because `h(0) = 0`. Hence the
maximum is `G(a)`. When `a = 0`, Lemma 4 gives `G(x) < 0` on `(0, T)` directly.

Consequently one path that leaves a proper helper boundary can never justify a
new intermediate dimension: the candidate is the path's own lower endpoint,
which is already a boundary dimension. This is the first step requested in
#7283's Open next question 1.

## Proposition (the endpoint maximum fails for four crossing paths)

Take `t = 1/2`, `D = 26`, `T = 24`, and the four paths

```text
(3, 25), (17, 26), (0, 25), (6, 25).
```

Every path starts in `[0, T]` and crosses the terminal, and every endpoint is
in `[0, D]`. The feasible interval is `[A, T] = [17, 24]`. At
`x0 = 3819/160` the exact integer square-root certificate gives

```text
G(17) - G(x0) < 0,      G(24) - G(x0) < 0.
```

The decimal displays are `G(17) = -3.747477...`, `G(24) = -3.734846...` and
`G(x0) = -3.554274...`. Thus `x0` strictly beats both endpoints. The endpoint
maximum of #7283 therefore does not extend to four boundary-crossing paths.

The witness has a negative interior value, so it does not exhibit a profitable
rank bill. It shows that the two-endpoint comparison can understate the
maximum. The sign question is left as an open next question.

## What this does not prove

The proper-terminal bill is a rank-bill factor. This package does not prove a
legal cut, an arbitrary-input identity, a native realization, an ordinary
cost, ownership, restoration or a paid-profile improvement. It does not change
the selected exponent. The two-path and three-path cases are not proved; only
the stated finite grids are censused. The sign of an interior maximum with
nonpositive endpoints is not proved.

## Dependencies

The rank-bill formula, its zero-to-`D` endpoint theorem and the proper-terminal
question are unpaidmoon's #7283. That package credits CubeJerry's shared-native
helper-split exploration and the two-chain word from DreamingOfClouds in #6902.
No part of #7283 is replayed or re-audited here. Prepared by Nick Petalas.
Apache-2.0.
