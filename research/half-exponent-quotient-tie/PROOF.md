# The half-exponent adjacent-quotient tie sits before the midpoint

This is a written proof for the exponent `t = 1/2`. It does not change κ, and it
does not claim the same statement for a general exponent.

The net splitting tax on main (`research/sharp-net-splitting-tax`, PR #6769)
leaves the adjacent-quotient transition unclassified. The open staircase note
on PR #7135 defines `θ_m = z(τ_m) - m` for the tie `g(m) = g(m+1)` and proves
`0 < θ_m < 1` for general `t`, but it states explicitly that `θ_m < 1/2` is
not proved for every `t` and `m`. The argument below proves that inequality
for every integer `m ≥ 1` when `t = 1/2`, and records the resulting
best-quotient rule. It uses only the envelope facts quoted in section 0.

## 0. Quoted envelope facts

Fix `t = 1/2`. Then `a = t^(1/(1-t)) = 1/4` and `t a^(t-1) = 1`. For real
`q > 0`, `σ ≥ 1` and `0 ≤ s ≤ 1`,

```
A_q(s) = q + s^(1/2) - (q+s)^(1/2),
F_q(s; σ) = A_q(s) / (q+s)^σ,
g_σ(q) = max_{0≤s≤1} F_q(s; σ).
```

Quoted from #6769, `PROOF.md` sections 2 and 3, specialized to this exponent:

* **(I1)** For every `q > 0` and `σ ≥ 1`, `F_q(·; σ)` has a unique maximizer
  `s_q(σ)` in `(0, 1)`. It is the unique root of

```
H_q(s) = (1/2) q s^(-1/2) + (1/2 - σ) s^(1/2) - σ q + (σ - 1/2) (q+s)^(1/2).
```

  The `s`-derivative of `H_q` is strictly negative, so `s_q(σ)` is `C^1` in
  `(q, σ)`.

* **(I2)** For `σ > 1` the map `q ↦ g_σ(q)` is strictly increasing on `(0, z]`
  and strictly decreasing on `[z, ∞)`, where `z = z(σ) > 0` is the unique
  positive root of `(σ - 1/2) W(z) = (σ - 1) z` and
  `W(x) = (x + 1/4)^(1/2) - 1/2`. Equivalently `s_z(σ) = 1/4`, and
  `g'(q) = (1 - (1/2) s_q^(-1/2)) / (q + s_q)^σ` has the sign of `s_q - 1/4`.

* **(I3)** For an integer quotient, the maximizers of `q ↦ g_σ(q)` lie in
  `{max(1, floor z), max(1, ceil z)}`.

`A_q(s) > 0` on the open square: `(1 + s^(1/2))^2 = 1 + 2 s^(1/2) + s > 1 + s`,
so `1 + s^(1/2) > (1+s)^(1/2)`, and for `q > 1` the same comparison after
replacing `1` by `q` is stricter. Thus `g_σ(q) > 0`.

## 1. The window function at `t = 1/2`

Let `w = (x + 1/4)^(1/2)`, so `x = w^2 - 1/4` and `w > 1/2` for `x > 0`.
Then

```
x - W(x) = (w - 1/2)^2,
x - (1/2) W(x) = w (w - 1/2),
ζ(x) := (x - (1/2) W(x)) / (x - W(x)) = w / (w - 1/2)
       = 1 + 1 / ((4x+1)^(1/2) - 1).
```

The equation in (I2) is `σ = ζ(z)`. Since `(4x+1)^(1/2)` is strictly
increasing, `ζ` is a strictly decreasing bijection from `(0, ∞)` onto
`(1, ∞)`, and `z(σ) = ζ^(-1)(σ)`.

## 2. The explicit critical curve

Let `u = s^(1/2) ∈ (0, 1)` and `v = (q + s)^(1/2) > u`, so `q = v^2 - u^2`.
Stationarity `∂F/∂s = 0` is `(1/A) ∂A/∂s = σ / (q+s)`. Here
`∂A/∂s = (1/2) (1/u - 1/v)` and `A = q + u - v`, so

```
(v - u) v / u = 2 σ (q + u - v).
```

The right-hand side factors as `2 σ (v - u) (v + u - 1)`. For `v ≠ u`,

```
v = 2 σ u (v + u - 1),
v = 2 σ u (1 - u) / (2 σ u - 1),
```

provided `2 σ u ≠ 1`. The numerator `2 σ u (1-u)` is positive for
`u ∈ (0, 1)`, and `v > 0` forces the denominator to be positive, hence
`u > 1/(2σ)`. Then

```
q(u) = v^2 - u^2
     = (2σ - 1) u^2 (2σ + 1 - 4 σ u) / (2 σ u - 1)^2.
```

The numerator factor `2σ + 1 - 4 σ u` is positive exactly for
`u < (2σ + 1)/(4σ)`. Thus, as `u` runs over
`(1/(2σ), (2σ + 1)/(4σ))`, the formula gives every `q > 0` exactly once:
the right endpoint gives `q = 0`, and `q → ∞` as `u ↓ 1/(2σ)`. In
particular `u = 1/2` lies in the interval for every `σ > 1`, because
`1/(2σ) < 1/2 < 1/2 + 1/(4σ)`.

`verify.py` checks the two rational-function identities
`v^2 - u^2 - q(u) = 0` and `H = 0` along this curve, after clearing the
positive denominator `(2 σ u - 1)^2`.

## 3. The critical curve is strictly convex

Write `q(u) = N(u)/D(u)` with the numerator and denominator of section 2.
Differentiating the rational function gives

```
q'(u) = -2 u (2σ - 1) (4 σ^2 u^2 - 6 σ u + 2σ + 1) / (2 σ u - 1)^3,
q''(u) = 2 (2σ - 1) (8 σ^2 u - 8 σ u + 2σ + 1) / (2 σ u - 1)^4.
```

On the interval, `(2 σ u - 1)^3 > 0` and `(2 σ u - 1)^4 > 0`. Also
`2σ - 1 > 0` and `u > 0`. The quadratic
`4 σ^2 u^2 - 6 σ u + 2σ + 1` has discriminant

```
(6σ)^2 - 4 (4 σ^2) (2σ + 1) = 4 σ^2 (5 - 8σ) < 0
```

for `σ > 1`, and its leading coefficient is positive, so the quadratic is
positive. Hence `q'(u) < 0`. The second numerator rewrites as

```
8 σ^2 u - 8 σ u + 2σ + 1 = 8 σ (σ - 1) u + 2σ + 1 > 0,
```

so `q''(u) > 0`. These polynomial identities are the ones `verify.py` checks.

Therefore `u ↦ q(u)` is strictly decreasing and strictly convex, and it is a
bijection onto `(0, ∞)`. Its inverse `q ↦ u(q) = s_q(σ)^(1/2)` is strictly
decreasing. For the second derivative of an inverse, if `f' < 0` and
`f'' > 0`, then

```
(f^(-1))'' = - f'' / (f')^3 > 0,
```

because `(f')^3 < 0`. Thus `u(q)` is strictly convex on `(0, ∞)`. Equivalently,
`u'` is strictly increasing. Strict convexity gives, for every `z > 0` and
every `d ∈ (0, z)`,

```
u(z - d) + u(z + d) > 2 u(z).
```

At the envelope peak, (I2) says `s_z = 1/4`, so `u(z) = 1/2`.

## 4. Values to the right of the peak are strictly larger

Fix `σ > 1` and `z = z(σ)`. The logarithmic derivative of the envelope is

```
λ(q) := g'(q) / g(q) = (1 - (1/2) s^(-1/2)) / A_q(s),
```

with `s = s_q(σ)`, by the quotient of (I2)'s formula for `g'` and the
definition of `g`. The stationarity identity of section 2 is equivalent to

```
(σ - 1/2) A_q(s) / q = (1/2) (s^(-1/2) - 1),
```

which is the `t = 1/2` case of clearing `H_q(s) = 0` (the same algebra as
#6769's passage from `H` to the optimized numerator). Substituting
`s^(-1/2) = 1/u` and `u = u(q)` produces

```
λ(q) = (σ - 1/2) (2 u(q) - 1) / (q (1 - u(q))).
```

In particular `λ(z) = 0`, `λ > 0` on `(0, z)` and `λ < 0` on `(z, ∞)`.

For `d ∈ (0, z)` set `u_L = u(z-d) > 1/2` and `u_R = u(z+d) < 1/2`. Section 3
gives `u_L - 1/2 > 1/2 - u_R > 0`. Both remainders lie in `(0, 1)`, so
`1 - u_L > 0` and `1 - u_R > 0`. Then `λ(z-d) + λ(z+d) > 0` if and only if

```
(u_L - 1/2) / ((z-d) (1 - u_L)) > (1/2 - u_R) / ((z+d) (1 - u_R)).
```

The left numerator is strictly larger, `z - d < z + d`, and
`1 - u_L = 1/2 - (u_L - 1/2) < 1/2 + (1/2 - u_R) = 1 - u_R`. Every comparison
is strict, so the sum of logarithmic derivatives is strictly positive.
Integrating over `d ∈ (0, 1/2)` when `z > 1/2`,

```
log g(z + 1/2) - log g(z - 1/2) = ∫_0^(1/2) (λ(z-u) + λ(z+u)) du > 0.
```

Thus `g(z + 1/2) > g(z - 1/2)`.

## 5. The tie between adjacent integers

**Lemma.** For integers `m ≥ 1` and `1 < σ_1 < σ_2`,

```
g_{σ_2}(m) / g_{σ_2}(m+1) > g_{σ_1}(m) / g_{σ_1}(m+1).
```

*Proof.* Let `Δ = σ_2 - σ_1 > 0`, `s = s_m(σ_1)` and `s' = s_{m+1}(σ_2)`.
For any fixed remainder, `F(·; σ_2) = F(·; σ_1) / (q + s_0)^Δ`. Therefore

```
g_{σ_2}(m) ≥ F_m(s; σ_2) = g_{σ_1}(m) (m + s)^(-Δ),
g_{σ_2}(m+1) = F_{m+1}(s'; σ_2) ≤ g_{σ_1}(m+1) (m + 1 + s')^(-Δ).
```

All four values are positive. Dividing yields a factor
`((m + 1 + s') / (m + s))^Δ > 1`, because `m + 1 + s' > m + 1 > m + s`. The
resulting inequality is strict. QED

The ratio `R(σ) = g_σ(m) / g_σ(m+1)` is continuous on `(1, ∞)` because
`s_q(σ)` is continuous by (I1) and `g` is positive. By the lemma it is
strictly increasing.

**Theorem.** Let `m ≥ 1` be an integer and let `t = 1/2`. There is a unique
`τ_m > 1` with `g_{τ_m}(m) = g_{τ_m}(m+1)`. Its peak
`z(τ_m) = m + θ_m` satisfies `0 < θ_m < 1/2`. For `z ∈ (m, m+1)` the unique
best integer quotient is `m` when `z < m + θ_m`, and `m + 1` when
`z > m + θ_m`. The two integers tie at `z = m + θ_m`.

*Proof.* Let `σ_mid = ζ(m + 1/2)` and `σ_+ = ζ(m)`. Then
`σ_mid < σ_+` because `ζ` is strictly decreasing. At `σ_+` the peak is `z = m`,
so (I2) gives `g(m) > g(m+1)` and `R(σ_+) > 1`. At `σ_mid` the peak is
`z = m + 1/2 > 1/2`, so section 4 gives `g(m+1) > g(m)` and `R(σ_mid) < 1`.
A strictly increasing continuous function crosses `1` exactly once in
`(σ_mid, σ_+)`. Call the root `τ_m`. Applying the decreasing map `ζ^(-1)`
puts `z(τ_m)` in `(m, m + 1/2)`, so `θ_m = z(τ_m) - m` satisfies
`0 < θ_m < 1/2`.

Now take `σ` with `z = z(σ) ∈ (m, m+1)`. By (I3) the only integer candidates
are `m` and `m+1`. The ratio `R(σ)` is `< 1` for `σ < τ_m` and `> 1` for
`σ > τ_m`. Since `ζ` is decreasing, `z > m + θ_m` if and only if `σ < τ_m`,
which is exactly when `g(m+1) > g(m)`. The symmetric statement gives the
winner `m` when `z < m + θ_m`. At `σ = τ_m` the two values are equal. QED

## 6. What is and is not claimed

Proved, for the exponent `t = 1/2` and every integer `m ≥ 1`: the adjacent
tie exists and is unique, the best integer quotient on each interval
`(m, m+1)` switches at `z = m + θ_m`, and `θ_m < 1/2`. The algebraic
derivative identities used in section 3 are checked identically by
`verify.py`.

Not proved: the inequality `θ_m < 1/2` for an exponent other than `1/2`;
the asymptotic coefficient in `1/2 - θ_m` as `m → ∞`; any statement about a
supplier inventory, a paid profile, or κ. The selected frontier is unchanged
at `363005817/100000000000`. A finite numerical sample is not used as a
substitute for the argument above. PR #7135's general-exponent staircase is
not an input; the `t = 1/2` case is derived here from #6769.
