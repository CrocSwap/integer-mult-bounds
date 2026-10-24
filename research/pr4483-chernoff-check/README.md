# Independent check of #4483 §2–3 on actual flows: identity (2) and Chernoff bounds (7)–(9)

**Task:** independent-moment (independent source-bound coverage). **Base:** canonical main `f626db5c`. **No new κ.**

zxv's #4483, `research/rank-convergence/PROOF.md` (pinned), controls the arbitrary-height flow with three results:
- the exact potential identity `I_t + R_t = B_t + F_t + (T−P)H_t`, eq. (2);
- the two Chernoff bounds, (7) `(T−P)H_t ≥ (1−u_t^ℓ)P^(G+1)(q^(aℓ+1)−1)` and (8) `R_t ≤ q M^λ v_t^ℓ P^(G+1)`;
- their consequence (9), `A_t ≥ D_ℓ(t) P^(G+1)`.

#4532's critical-root funding inherits these, and with it #4535 and #4568. My #4529 checked #4483's gates and its rank-one identity at `t = 1`. This package checks (2), (7), (8) and (9) **on actual flows** at real exponents.

## Method

My own flow code builds the arbitrary-height flow at #4483's height `G = (a+b)·⌊log_M ⌊N/m⌋⌋` and computes, from the flow's classes, five potentials:
- the unit-column potential `H_t`;
- root sources `R_t`;
- inner sources `I_t`;
- boundary exits `B_t`;
- leaf exits `F_t`.

`u_t`, `v_t` and `q` follow #4483's (6). There are two cases:
- **raw p7** with #4483's p7 geometry: `M = 256`, `a = b = 1`, `s = λ = 1/10`;
- **p16** (#4470) with #4532's p16 geometry: `M = 1024`, `a = b = 1`, `s = 1/20`, `λ = 1/10`.

Both profiles are read from main (SHA256-pinned). The exponents lie above each profile's moment crossing, since `T > P` is (7)'s premise: the guard exponents `t0` and `t_upper`, plus `0.999`.

## Results

All 15 cases pass:
- **Identity (2), exactly.** At every rank checked, both sides are compared as **formal power sums** `Σ_x c_x·x^t` with integer coefficients, from 245 up to 16,252 distinct bases `x`. They are identical, so (2) holds **exactly, for every exponent `t` at once**. A rejection control drops one root source and is detected. Numerically it also holds to `10^−9` at each tested `t`.
- **Ratio ordering.** It holds, as does `q > 1`.
- **(7), (8), (9).** They hold with the following slack:

| profile | ranks `N` (height `G`) | `(T−P)H_t / rhs(7)` | `R_t / rhs(8)` |
|---|---|---|---|
| p7 | 10^5 (2), 10^7 (4), 3·10^9 (6) | 28.0 → 13.5 → 9.97 | 0.304 → 0.123 → 0.096 |
| p16 | 2·10^5 (2), 2·10^8 (4) | 25.2 → 16.1 | 0.267 → 0.237 |

So (7) holds with a factor of at least 9.97, and (8) with at most 0.31 of the bound. The (7) slack shrinks as the height grows, as expected for a Chernoff tail bound, and stays well above 1 at every tested height. (9) follows, and is checked directly.

**Scope note.** Below the moment crossing, where `T < P` (for example `t = 0.9` for p7), both sides of (7) are negative and the inequality is not claimed. #4483 states it only for `T > P`.

## Verify

```text
python3 -B research/pr4483-chernoff-check/verify.py
```

This runs in about 30 s with the standard library only.

## Limitations

- **Finite heights.** These are finite heights (`G ≤ 6`) and finitely many exponents. #4483's (7)–(9) are proved for all heights by the written Chernoff argument, which these checks corroborate on actual flows. The asymptotic ranks of #4535 (`N = 2^(10^12)` and beyond) are far outside direct computation.
- **Floating point.** Comparisons use floats. The margins (≥ 9.97 and ≤ 0.31) far exceed rounding.

## Open next questions

- Certified (interval) versions of (7) and (8). (2) is now exact. First step: certified powers `r^t` at `t = t0`, as in my #4580 check.

Credit: zxv (#4483), Dillon (#4532), Cinna Davis (#4470), Jacob Alan Sussman (Pascal matching). Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
