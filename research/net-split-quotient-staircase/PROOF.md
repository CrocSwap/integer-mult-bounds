# The best-quotient staircase of the sharp net splitting tax

This proof was produced by Nick Petalas. Apache-2.0.

It answers the open question of CubeJerry's
[PR #6769](https://github.com/CrocSwap/integer-mult-bounds/pull/6769)
(`research/sharp-net-splitting-tax`): how the best integer quotient moves as
sigma varies. Sections 2 to 5 are written proofs. They use only the facts
(I1) to (I3) of section 0, which are quoted from #6769 and not re-proved here.

## 0. Setting and quoted facts

Fix `0 < t < 1`. For real `q > 0`, `sigma >= 1` and `0 <= s <= 1` put

```
A_q(s)       = q + s^t - (q+s)^t,
F_q(s; sigma) = A_q(s) / (q+s)^sigma,
g_sigma(q)    = max_{0<=s<=1} F_q(s; sigma).
```

Let `a = t^(1/(1-t))`, so `a^(1-t) = t` and `t a^(t-1) = 1`, and let
`W(x) = (x+a)^t - a^t` for `x > 0`.

Quoted from #6769 (`PROOF.md` sections 2 to 4):

* **(I1)** For every real `q > 0` and `sigma >= 1`, `F_q(.; sigma)` has a unique
  maximizer `s_q(sigma)` on `[0,1]`, and it lies in `(0,1)`. It is the root of
  `H_q(s) = t q s^(t-1) + (t-sigma) s^t - sigma q + (sigma-t)(q+s)^t`.
* **(I2)** For `sigma > 1` the equation `(sigma-t) W(z) = (sigma-1) z` has a
  unique positive root `z = z(sigma)`. The map `q -> g_sigma(q)` is strictly
  increasing on `(0, z]` and strictly decreasing on `[z, infinity)`.
* **(I3)** `N(t,sigma) = max_{q integer >= 1} g_sigma(q)`, and the integer
  maximizers lie in `{max(1, floor z), max(1, ceil z)}`.

**(I4)** (proved here) For an integer `q >= 1` and `0 < s < 1`, `A_q(s) > 0`.
Indeed `s^t > s`, so `A_q(s) > x - x^t >= 0` with `x = q + s >= 1`. Hence
`F_q(s; sigma) > 0` and `g_sigma(q) > 0`.

## 1. The window function zeta

Since `W(0) = 0` and `W'(x) = t (x+a)^(t-1) < t a^(t-1) = 1`, we have
`0 < W(x) < x`; and `W` is strictly concave, so `W(x)/x` decreases strictly
from `W'(0) = 1` to `0`. Define, for `x > 0`,

```
zeta(x) = (x - t W(x)) / (x - W(x)) = 1 + (1-t) / (x/W(x) - 1).
```

**Lemma 0.** `zeta` is a continuous strictly decreasing bijection from
`(0, infinity)` onto `(1, infinity)`, and `z(sigma) = zeta^(-1)(sigma)`.

*Proof.* `x/W(x)` increases strictly from 1 to infinity, so `x/W - 1`
increases strictly from 0 to infinity and `zeta` decreases strictly from
infinity to 1. The equation of (I2) reads `sigma (W - x) = t W - x`, that is
`sigma = zeta(x)`. By (I2) it has exactly one positive root `z(sigma)`. QED

For `t = 1/2`: `a = 1/4`, and with `w = sqrt(x + 1/4)` one gets
`x - W = (w - 1/2)^2` and `zeta(x) = w/(w - 1/2) = 1 + 1/(sqrt(4x+1) - 1)`.
In particular `zeta(n(n+1)) = 1 + 1/(2n)`, the #6769 family.

## 2. The ratio of two quotients is monotone in sigma

**Lemma 1.** Let `q < q'` be integers with `q >= 1`, and `1 < sigma_1 < sigma_2`.
Then

```
g_{sigma_2}(q) / g_{sigma_2}(q')  >  g_{sigma_1}(q) / g_{sigma_1}(q').
```

*Proof.* Put `Delta = sigma_2 - sigma_1 > 0`, `s = s_q(sigma_1)` and
`s' = s_{q'}(sigma_2)`; both lie in `(0,1)` by (I1). For any `s0`,
`F_r(s0; sigma_2) = F_r(s0; sigma_1) (r + s0)^(-Delta)`. Therefore

```
g_{sigma_2}(q)  >= F_q(s; sigma_2)   = g_{sigma_1}(q) (q+s)^(-Delta),
g_{sigma_2}(q')  = F_{q'}(s'; sigma_2) = F_{q'}(s'; sigma_1) (q'+s')^(-Delta)
                <= g_{sigma_1}(q') (q'+s')^(-Delta).
```

All quantities are positive by (I4). Dividing,

```
g_{sigma_2}(q)/g_{sigma_2}(q') >= [g_{sigma_1}(q)/g_{sigma_1}(q')] ((q'+s')/(q+s))^Delta.
```

Now `q' + s' > q' >= q + 1 > q + s`, because `s' > 0` and `s < 1`. The base of
the power exceeds 1 and `Delta > 0`, so the inequality is strict. QED

The proof does not use uniqueness of the maximizers beyond their location in
`(0,1)`, and it is an envelope argument: the larger quotient is always paid
at a larger `R = q + s`, so a larger sigma hurts it more.

## 3. The staircase

For an integer `q >= 1` put `rho_q(sigma) = g_sigma(q) / g_sigma(q+1)`. The
function `sigma -> g_sigma(q)` is continuous, being a maximum over the compact
interval `[0,1]` of functions continuous in `(s, sigma)`. Hence `rho_q` is
continuous and positive on `(1, infinity)`.

**Theorem 2.** Fix `0 < t < 1`.

1. For every integer `q >= 1` there is exactly one `tau_q > 1` with
   `rho_q(tau_q) = 1`. Moreover `rho_q < 1` for `sigma < tau_q`,
   `rho_q > 1` for `sigma > tau_q`, and
   `zeta(q+1) < tau_q < zeta(q)`.
2. `tau_1 > tau_2 > ...` and `tau_q -> 1`.
3. With `tau_0 = +infinity`: for every integer `m >= 1` and every
   `tau_m < sigma < tau_{m-1}`, the unique best integer quotient at `sigma` is
   `m`. At `sigma = tau_m` the best quotients are exactly `m` and `m + 1`.
   Equivalently, away from the thresholds the best quotient is
   `1 + #{ m >= 1 : tau_m > sigma }`.
4. Hence the best quotient is nonincreasing in sigma, it jumps by exactly one
   at each `tau_m`, and every positive integer is the unique best quotient on
   a nonempty open interval of sigma. For `tau_m <= sigma <= tau_{m-1}`,
   `N(t, sigma) = g_sigma(m)`.

*Proof.* (1) By Lemma 1 (with `q' = q + 1`) `rho_q` is strictly increasing, so
it takes the value 1 at most once. At `sigma = zeta(q+1)` we have
`z = q + 1` (Lemma 0), and by (I2) `g(q) < g(q+1)`, so `rho_q < 1`. At
`sigma = zeta(q)` we have `z = q`, and `g(q+1) < g(q)`, so `rho_q > 1`. By the
intermediate value theorem the root `tau_q` exists and lies strictly between
`zeta(q+1)` and `zeta(q)`, with the stated signs on either side.

(2) By (1) and Lemma 0, `tau_{q+1} < zeta(q+1) < tau_q`. Also
`1 < tau_q < zeta(q) -> 1`.

(3) Let `sigma > 1` and `z = z(sigma)`.

* If `z <= 1`, that is `sigma >= zeta(1) > tau_1`, the candidate set of (I3)
  is `{1}`; the best quotient is 1 and the formula gives 1.
* If `z = m` is an integer, then `sigma = zeta(m)` and `tau_m < zeta(m) < tau_{m-1}`
  by (1); by (I2) `m` is the unique best, matching the formula.
* If `m < z < m + 1` for an integer `m >= 1`, then
  `zeta(m+1) < sigma < zeta(m)` and by (I3) the best quotients lie in
  `{m, m+1}`. By (1), `m` is strictly better iff `sigma > tau_m`, `m + 1` is
  strictly better iff `sigma < tau_m`, and they tie iff `sigma = tau_m`. Since
  `tau_{m+1} < zeta(m+1)` and `zeta(m) < tau_{m-1}`, the sigma between
  `tau_m` and `zeta(m)` lie in `(tau_m, tau_{m-1})` with best quotient `m`,
  and those between `zeta(m+1)` and `tau_m` lie in `(tau_{m+1}, tau_m)` with
  best quotient `m + 1`.

These cases cover every `sigma > 1`, and the tie sets are as stated.

(4) is a restatement: the intervals `(tau_m, tau_{m-1})` are nonempty by (2). QED

**Corollary 3 (rate).** As `x -> infinity`, `W(x) = x^t (1 + O(x^(-t)))`, hence
`zeta(x) - 1 = (1-t) W/(x-W) ~ (1-t) x^(t-1)`. Since `zeta(m+1) < tau_m < zeta(m)`,

```
tau_m - 1  ~  (1-t) m^(t-1)            (m -> infinity),
```

and the best quotient grows like `((1-t)/(sigma-1))^(1/(1-t))` as sigma
decreases to 1. For `t = 1/2` this is `1/(4 (sigma-1)^2)`, and the exact window
is `1 + 1/(sqrt(4m+5) - 1) < tau_m < 1 + 1/(sqrt(4m+1) - 1)`.

## 4. Where in the window the tie sits

Write `theta_m = z(tau_m) - m`; by Theorem 2 (1), `0 < theta_m < 1`. The
nearest-integer rule would correspond to `theta_m = 1/2`. The finite
certificates of `verify.py` show `theta_m < 1/2` for each certified pair
(`t` in {1/10, 1/4, 1/2, 3/4, 9/10}, `m <= 30`); the sampled values of
`theta_m` increase toward `1/2`. They also give concrete witnesses that rounding
`z` to the nearest integer is not the best-quotient rule (at `t = 1/2`,
`z = 1.45` rounds to 1 but quotient 2 is strictly better). **This is not
proved for all `t` and `m`.** It is an open question in the package README.

## 5. Log-convexity and kinks

`log g_sigma(m) = max_s [ log A_m(s) - sigma log(m+s) ]` is a maximum of affine
functions of sigma, so it is convex; by Theorem 2 only finitely many `m`
matter near any sigma, so `log N(t, .) = max_m log g_.(m)` is convex on
`(1, infinity)`. Each branch is strictly decreasing, since `m + s > 1`.

By the implicit function theorem (the same sign computation as (5) of #6769,
with `sigma` in place of `q`), `s_m(sigma)` is `C^1`, and the envelope theorem
gives `d/dsigma log g_sigma(m) = - log R_m(sigma)` with `R_m = m + s_m(sigma)`.
At `sigma = tau_m` the branches `m + 1` (to the left) and `m` (to the right)
meet, with slopes `-log R_{m+1}` and `-log R_m`. Since
`R_{m+1} > m + 1 > R_m`, the slope jumps up by `log(R_{m+1}/R_m) > 0`, and
`R_{m+1}/R_m < (m+2)/m`. So `N(t, .)` is real analytic between consecutive
thresholds and has a genuine convex kink at every `tau_m`; the kinks
accumulate only at `sigma = 1`. `verify.py` spot-checks the slope formula
numerically.

**Remark (conditional, for users of the strictification test).** In the
complete sufficient test (10) of #6769 section 6, with `t`, `v`, the bases and
the histograms fixed, the only summand that depends on `u >= 1 - t` is
`N(t, t+u) gamma(u)^v` with `gamma(u) = P_{t+u} / (c^u T_t)`. If `P_x` is a
positive moment `sum n_r r^x` (the form of the paid moments in #4433 and #4480,
which this package did not re-read), it is log-convex in `u` by Holder's
inequality, `c^(-uv)` is log-linear, and `N(t, t+u)` is log-convex by the
paragraph above. A product of log-convex functions is log-convex, and a
log-convex function is convex. Then the left side of (10) is a convex function
of `u`, any local minimizer is global, the minimizers form an interval, and a
minimizer can sit at a kink `u = tau_m - t`, where a stationary-point solver
would not find it. Whether a real inventory has its optimum at a kink is open.

## 6. What is and is not claimed

Proved (written): Lemma 0, Lemma 1, Theorem 2, Corollary 3 and the section 5
statements, from (I1) to (I3) of #6769. Finite certificates (`verify.py`): the
tie bracket, window and `theta < 1/2` for 150 `(t, m)` pairs, with enclosure
arithmetic described in `README.md`. Not proved: `theta_m < 1/2` for all
`t` and `m`; any statement about an actual supplier.
