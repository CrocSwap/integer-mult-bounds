# The best-quotient staircase of the sharp net splitting tax

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped written proof with finite enclosure certificates; no new κ, no
supplier admission, no selected-frontier change.**

CubeJerry's merged [PR #6769](https://github.com/CrocSwap/integer-mult-bounds/pull/6769)
(`research/sharp-net-splitting-tax`) shows that for `0 < t < 1` and `σ > 1` the
sharp net-tax coefficient `N(t,σ)` is attained at `⌊z⌋` or `⌈z⌉`, where `z`
solves its equation (2). It allows ties, assumes no rounding rule, and lists as
open how the best integer quotient moves as `σ` varies. This package answers
that question for every `t`, with a proof that uses only the facts (I1) to (I3)
quoted from #6769.

## Result

Write `g_σ(q)` for the optimized value of quotient `q` (the maximum over the
remainder of `F_q`), `a = t^(1/(1-t))`, `W(x) = (x+a)^t − a^t` and

    ζ(x) = (x − tW(x)) / (x − W(x)).

`ζ` is a closed-form, strictly decreasing bijection `(0,∞) → (1,∞)`, and
`z(σ) = ζ⁻¹(σ)` (PROOF.md section 1). For `t = 1/2`,
`ζ(x) = 1 + 1/(√(4x+1) − 1)`, so `ζ(n(n+1)) = 1 + 1/(2n)`: the #6769 family.

1. **Ratio monotonicity** (Lemma 1). For integers `1 ≤ q < q'`, the ratio
   `g_σ(q)/g_σ(q')` is strictly increasing in `σ`. The reason is an envelope
   argument: a maximizing remainder is below 1, so the larger quotient is paid at
   a larger `R = q + s`, and a larger `σ` hurts it more.
2. **Staircase** (Theorem 2). Each adjacent pair has exactly one tie threshold
   `τ_q`, with `ζ(q+1) < τ_q < ζ(q)`. The thresholds satisfy
   `τ_1 > τ_2 > … → 1`. For `τ_m < σ < τ_{m−1}` (`τ_0 = ∞`) the unique best
   quotient is `m`; at `σ = τ_m` the best quotients are exactly `m` and `m+1`.
   So the best quotient is nonincreasing, jumps by exactly one, and **every
   positive integer is the unique best quotient on a nonempty open interval of
   `σ`**. #6769's family `σ = 1 + 1/(2n)` only meets the pronic values `n(n+1)`.
3. **Rate** (Corollary 3). `τ_m − 1 ~ (1−t) m^(t−1)`, and the best quotient grows
   like `((1−t)/(σ−1))^(1/(1−t))` as `σ ↓ 1`; for `t = 1/2` this is
   `1/(4(σ−1)²)`.
4. **Shape of `N`** (PROOF.md section 5). `log N(t,·)` is convex and strictly
   decreasing on `(1,∞)`, real analytic between thresholds, with a genuine convex
   kink at every `τ_m` whose slope jump is `log(R_{m+1}/R_m) ∈ (0, log((m+2)/m))`.
   Conditionally on the moment form of `P_x` in #4433/#4480, the left side of
   #6769's strictification test (10) is therefore convex in the free exponent
   `u`, and its minimizer can sit at a kink (a conditional remark, not a result
   about any inventory).

### Certified thresholds

For `t ∈ {1/10, 1/4, 1/2, 3/4, 9/10}` and `q ≤ 30`, `verify.py` certifies a
bracket of half-width at most `1e-12` around `τ_q` (150 pairs), by enclosure
arithmetic with `ρ_q < 1` at its left end and `ρ_q > 1` at its right end. The
thresholds, with `θ_q = z(τ_q) − q`:

| q | τ_q, t = 1/4 | τ_q, t = 1/2 | τ_q, t = 3/4 | θ_q, t = 1/2 |
|---:|---:|---:|---:|---:|
| 1 | 1.4002422608 | 1.6357241325 | 1.8327404694 | 0.405094 |
| 2 | 1.2664553196 | 1.4383632422 | 1.5936908896 | 0.441590 |
| 3 | 1.2074139740 | 1.3507366418 | 1.4876063709 | 0.457824 |
| 5 | 1.1496759204 | 1.2642332618 | 1.3826780029 | 0.472944 |
| 10 | 1.0947642169 | 1.1800795463 | 1.2796676654 | 0.485785 |
| 20 | 1.0593088063 | 1.1233222265 | 1.2085870533 | 0.492734 |
| 30 | 1.0449137612 | 1.0991113903 | 1.1773611067 | 0.495127 |

All 150 pairs also certify the window `ζ(q+1) < τ_q < ζ(q)` and
`ζ(q+½) < τ_q`, that is `θ_q < 1/2`. **The inequality `θ_q < 1/2` is a finite
observation, not a theorem**; it is the first open question below. It shows that
rounding `z` to the nearest integer is not the best-quotient rule: at `t = 1/2`,
`σ = 1.62201395897…` has `z = 1.45`, which rounds to 1, yet quotient 2 is
strictly better (certified, `ρ_1 < 0.9925`).

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/net-split-quotient-staircase/verify.py
python3.12 -I -O -W error -B research/net-split-quotient-staircase/verify.py
python3.12 -B scripts/research_package.py --package research/net-split-quotient-staircase
python3.12 -B scripts/check_research_commit.py --package research/net-split-quotient-staircase --check-source-history
```

The direct commands print a JSON receipt ending in
`PASS_NET_SPLIT_QUOTIENT_STAIRCASE`; each takes about 10 to 25 seconds. They read
and write no files. The checks are:

- **A.** The `t = 1/2` closed form of `ζ` and `ζ(n(n+1)) = 1 + 1/(2n)` for
  `n ≤ 16`.
- **B.** 400 ratio evaluations on a grid (`t` in five values, eight quotient
  pairs, ten `σ`): the ratio increases. 48 envelope-slope comparisons against
  `−log(q + s_q)`, 12 one-sided slope pairs at thresholds showing the convex
  kink, and 261 second differences of `log N`.
- **C.** The 150 enclosure-certified brackets, windows and `θ < 1/2` tests.
  Enclosures widen every `exp`/`ln` result by a relative `4e-70` and treat the
  100-digit rounding of `+ − × ÷` as exact. The smallest certified relative
  margin is `3.2e-14`, so that omitted rounding (relative `1e-98`) cannot change a
  verdict. The enclosure relies on the documented correct rounding of
  `Decimal.exp` and `Decimal.ln`. The maximizing remainder is bracketed by a
  certified sign change of `H_q`, and the upper bound on `g` uses that bracket.
- **D.** A float brute force over integer quotients `1..200` at 300 values of `σ`
  (five `t`, 60 each, `z ≤ 35`) agrees with the staircase read from the
  thresholds.
- **E.** Eight rejection controls (the false claim `τ_q < ζ(q+½)` and a bracket
  outside its window fail the enclosure test for `t = 1/2`, `q ∈ {1,2,5,12}`),
  the nearest-integer witness at `t = 1/2` and `t = 1/4`, and a control that the
  inverse ratio is decreasing.

## Scope and limits

- **Claim type.** Lemma 1 and Theorem 2 are written proofs, from (I1) to (I3) of
  #6769, which are quoted and not re-proved. The tie brackets, windows and
  `θ < 1/2` are finite certificates at the listed `(t, q)`; the brute force and
  the slope checks are float corroboration. This is not a complete multiplication
  theorem and not a statement about any supplier.
- No new κ and no selected-frontier change. The five selected framework
  assumptions are untouched.
- `t` ranges over five exact decimals; `t = 1/3` and `2/3` are not exact decimals
  and were not certified. Nothing here covers the full split charge of #6390.
- No independent human or proof-kernel review is claimed.

## Open next questions

The structured versions are in [TASK.json](TASK.json).

1. **Half-window.** Is `θ_q < 1/2` for every `0 < t < 1` and every `q ≥ 1`, and
   what is `c_t` in `1/2 − θ_q ~ c_t/q`? The certified table has
   `(1/2 − θ_q) q ≈ 0.15` at `q = 30`. First step: prove `g(z+½) > g(z−½)` at
   fixed `σ`, for example by comparing `F_{q+1}` at the remainder `s_q` with
   `g(q)` at `z = q + ½`. Blocker: no closed form for `s_q`.
2. **Kinks in the strictification test.** For the selected #6030 joint
   application linked from #6769, does the minimizing `u` of test (10) sit at a
   threshold `u = τ_m − t`? First step: scan `u` over its exact moment intervals.
   Blocker: those exact moments and the moment form of `P_x`.
3. **Monotone in `t`.** Is `τ_m(t)` increasing in `t` for each `m`? The table
   suggests it. First step: differentiate `ρ_m(σ; t) = 1` in `t`. Blocker: the
   `t`-derivative of `s_q`.

These are suggestions, not reservations or novelty guarantees.

## Credit

CubeJerry's #6769 supplies the coefficient `N`, the maximizer equation (3), the
unimodality in `q` and the question; it is quoted, not replayed. The envelope
argument and `ζ` are new here. Source pins are in [SOURCES.json](SOURCES.json),
and the scope record is in [TASK.json](TASK.json).
