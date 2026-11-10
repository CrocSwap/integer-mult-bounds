# Proof: first phase-aliasing threshold for tensor widths 2 through k

## Statement

Let `k >= 3`, `0 <= eps <= 2`, and put `alpha = asin(eps/2)/pi`, so
`0 <= alpha <= 1/2`. For unitaries `A, B` of the same positive finite
dimension, write

    R_k(eps) = sup ||A - B||   subject to   ||A^(⊗j) - B^(⊗j)|| <= eps  for j = 2..k,

with operator norms. Define the threshold `alpha*` and jump point `phi*` by

| k | alpha* | phi* | eps* = 2 sin(pi alpha*) | R_k(eps*) = 2 sin(pi phi*) |
|---|---|---|---|---|
| 3 | 1/5 | 2/5 | 2 sin(pi/5) | 2 sin(2pi/5) |
| 4, 5 | 2/7 | 3/7 | 2 sin(2pi/7) | 2 sin(3pi/7) |
| 6, 7 | 1/3 | 4/9 | sqrt(3) | 2 sin(4pi/9) |
| k >= 8 | 1/3 | 1/3 | sqrt(3) | sqrt(3) |

**Theorem.**

1. If `alpha < alpha*`, then `R_k(eps) = 2 sin(pi alpha / k) = 2 sin(asin(eps/2)/k)`.
2. At `alpha = alpha*`, `R_k(eps*) = 2 sin(pi phi*)`.
3. Every value is attained by scalar unitaries `A = I`, `B = exp(2 pi i phi) I`
   in every positive finite dimension.

So the envelope jumps at `eps*` from the left limit `2 sin(pi alpha*/k)` to
`2 sin(pi phi*)`. The row `k = 3` is the equal-budget theorem of PR5916. For
every `k >= 6` the jump happens at the same budget `eps* = sqrt(3)`, and for
`k >= 8` the error after the jump equals the budget.

## 1. Scalar reduction

Let `U = A* B`. It is unitary, and `A^(⊗j)` is unitary, so

    ||A^(⊗j) - B^(⊗j)|| = ||I - U^(⊗j)||,     ||A - B|| = ||I - U||.

`U^(⊗j)` is normal with eigenvalues the products `lambda_{i1} ... lambda_{ij}`
of eigenvalues of `U`. For a normal `N`, `||I - N|| = max |1 - mu|` over its
eigenvalues `mu`. Taking all indices equal, each eigenvalue `lambda` of `U`
satisfies `|1 - lambda^j| <= eps` for `j = 2..k`. Therefore

    ||A - B|| <= max { |1 - lambda| : |lambda| = 1, |1 - lambda^j| <= eps, j = 2..k }.

The scalar pair `A = I, B = lambda I` attains the right-hand side, because then
every product eigenvalue of `U^(⊗j)` equals `lambda^j`.

Write `lambda = exp(2 pi i phi)` and let `||x||` be the distance from `x` to the
nearest integer. Then `|1 - exp(2 pi i x)| = 2 sin(pi ||x||)`, and this is at
most `eps = 2 sin(pi alpha)` exactly when `||x|| <= alpha`. Hence

    R_k(eps) = 2 sin(pi M),   M = max { ||phi|| : phi in S_k(alpha) },
    S_k(alpha) = { phi : ||j phi|| <= alpha for j = 2..k }.

`S_k(alpha)` is closed and symmetric under `phi -> -phi`, so it suffices to
study `phi in [0, 1/2]`, where `||phi|| = phi`.

## 2. The two branches

Fix `phi in [0, 1/2]` in `S_k(alpha)` with `alpha < 1/2`. From `||2 phi|| <= alpha`:
either `phi <= alpha/2` (near branch) or `phi = 1/2 - s` with
`0 <= s <= alpha/2` (far branch).

**Near branch (any `alpha <= 1/3`).** We show `j phi <= alpha` for
`j = 2..k` by induction. The case `j = 2` holds. If `j phi <= alpha` and `j < k`,
then `(j+1) phi <= alpha + alpha/2 <= 1/2`, so `||(j+1) phi|| = (j+1) phi`, and
the hypothesis forces `(j+1) phi <= alpha`. Hence `k phi <= alpha`.
Conversely `phi <= alpha/k` gives `j phi <= alpha` for every `j <= k`. The near
branch is exactly `[0, alpha/k]`.

**Far branch, width three.** Since `s <= alpha/2 <= 1/6`, `3 s <= 1/2` and
`||3 phi|| = ||3/2 - 3 s|| = 1/2 - 3 s`. Hence `s >= (1/2 - alpha)/3`. (F3)

**Far branch, width four.** `||4 phi|| = ||4 s||` with `0 <= 4 s <= 2 alpha <= 2/3`.
For `alpha <= 1/3`, `||4 s|| <= alpha` means `4 s <= alpha` or `4 s >= 1 - alpha`.
The second case needs `2 alpha >= 1 - alpha`, so it occurs only at `alpha = 1/3`,
`s = 1/6`. (F4)

**Far branch, width six.** If `(1/2 - alpha)/3 <= s <= alpha/4` and
`alpha <= 1/3`, then `6 s` lies in `[1 - 2 alpha, 3 alpha/2]`, a subset of
`[1/3, 1/2]`. So `||6 phi|| = ||6 s|| = 6 s >= 1 - 2 alpha`, and the hypothesis
forces `1 - 2 alpha <= alpha`, that is `alpha >= 1/3`, with equality only when
`6 s = 1/3`. (F6)

## 3. Proof of the theorem

All thresholds satisfy `alpha* <= 1/3`, so the near branch is `[0, alpha/k]`
throughout. It remains to locate the far branch.

**k = 3.** (F3) and `s <= alpha/2` need `(1/2 - alpha)/3 <= alpha/2`, that is
`alpha >= 1/5`. At `alpha = 1/5`, `s = 1/10` and `phi = 2/5`. This is PR5916.

**k = 4, 5.** For `alpha < 1/3`, (F4) gives `s <= alpha/4`. With (F3),
`(1/2 - alpha)/3 <= alpha/4` gives `alpha >= 2/7`. So the far branch is empty for
`alpha < 2/7`. At `alpha = 2/7` the two bounds meet at `s = 1/14`, so the far
branch is at most `{3/7}`. The point `3/7` is feasible: `||6/7|| = 1/7`,
`||9/7|| = 2/7`, `||12/7|| = 2/7` and `||15/7|| = 1/7`.

**k >= 6, alpha < 1/3.** (F4) gives `s <= alpha/4`, (F3) gives the lower bound,
and (F6) then contradicts `alpha < 1/3`. The far branch is empty.

**k >= 6, alpha = 1/3.** (F3) gives `s >= 1/18`. By (F4), either `s = 1/6` or
`s <= 1/12`. If `s = 1/6`, then `phi = 1/3`, and `||j/3|| <= 1/3` for every `j`, so
`1/3` is feasible for every `k`. If `1/18 <= s <= 1/12`, (F6) forces `s = 1/18`,
`phi = 4/9`. For `k = 6, 7` this point is feasible:
`||8/9|| = 1/9`, `||12/9|| = 1/3`, `||16/9|| = 2/9`, `||20/9|| = 2/9`,
`||24/9|| = 1/3`, `||28/9|| = 1/9`. For `k >= 8`, `||32/9|| = 4/9 > 1/3`, so
it is excluded. The far branch is `{1/3, 4/9}` for `k = 6, 7` and `{1/3}` for
`k >= 8`.

In each case the maximum of `||phi||` over `S_k(alpha)` is `alpha/k` below the
threshold, and `phi*` at the threshold, because `phi* > alpha*/k`. Section 1
converts these maxima into the stated operator-norm values, with scalar
attainment. ∎

## Remarks

- The threshold is not monotone in a simple way: adding the width-four test
  moves it from `1/5` to `2/7`, width six moves it to `1/3`, and width eight
  changes only the jump point. For `k >= 6` the threshold `alpha = 1/3` cannot
  move further, because `phi = 1/3` passes every width.
- Width two alone (`k = 2`) admits `phi = 1/2` for every budget, so
  `R_2 = 2` and no small branch exists.
- The theorem covers `eps <= eps*` only. Above the threshold the envelope
  continues piecewise, and the remaining pieces depend on `k`.
- The proof uses only the scalar reduction and elementary inequalities.
  It makes no literature-priority claim. Spectral theory and trigonometry are
  classical.
