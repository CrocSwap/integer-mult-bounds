# Independent certified check of #4532: adaptive gates at a moment crossing

**Claim type:** an independent certified recomputation of the finite figures. **No new κ.** It covers
dillona's [#4532](https://github.com/CrocSwap/integer-mult-bounds/pull/4532) (head `644607ba`). That PR gives
a sufficient criterion for #4483's gates at the exact moment crossing, together with the critical-root
majorant `L(n) ≤ A n^θ (c + log n)^p`. #4535's κ = 0.003020165 (checked in my #4536) rests on it.

The code is separately written, using the certified interval helpers of my #4529. All figures match
#4532's tables.

## A. The abstract witness

The profile is `W_16 = 1, W_256 = 4; P_1 = 59, P_81 = 1`, with exact crossing `T(1/2) = P(1/2) = 68`.
Parameters: `a = b = 1`, `M = 4096`, `s = λ = 1/4`, `p = 12`, `c = 24`, `ℓ₀ = 128`, `n₀ = 2^{1544}`.

| guard on [1/2, 33/64] | certified | #4532 |
| --- | ---: | ---: |
| mean gap `μ_T(1/2) − μ_P(33/64)` | 4.7649 | ≥ 4 |
| mixed tail `U` | 0.6223559 | < .622356 |
| root tail `V` | 0.6603487 | < .660349 |
| mirror, worst `E_J(33/64)/S_J(1/2)` | 0.010664 | ≤ 1/80 |
| capacity `t·m^{t−1}` | 1/32 (exact) | 1/32 |
| tangent cover `τ(n₀)` | 0.510967 | ≤ 33/64 |
| recurrence lower bound | 272.8579195 | > 272.857919 |
| required `(1−η)/(η−β)` | 155/3 | 155/3 |

The ratio ordering also holds.

## B. The counterexample

The profile is `W_4 = 4, W_64 = 17; P_1 = 4, P_16 = 1`, at `t = 1/2`:

- `T = 144 > P = 8`;
- the mirror ratio is exactly `1/17 < 1/16` (the capacity);
- `μ_P(1/2) = 2 ln 2`, and exactly `T(1/2 − λ)·e^{λμ_P} = 8 + 136·16^{−λ} > 8 = P(1/2)` for every `λ > 0`.

So #4532's tail criterion fails for every `λ`, as it states.

## C. Root applications, with #4483's geometry

| | crossing bracket | mean gap | mirror (bracket) | capacity | mirror (cover) | D | required |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| p7 | (.997313, .997314) | 1.723542 | 0.320851 | 0.984544 | 0.321177 ≤ .322 | 0.028590 | 0.023329 |
| p16 | (.996979, .996980) | 1.042285 | 0.562814 | 0.982102 | 0.563147 ≤ .564 | 0.048546 | 0.042808 |

The crossing in each bracket is certified by opposite moment signs, and uniqueness by a positive mean gap.
The U, V, Q, d and ordering guards hold on the critical covers `[root, .997483]` and `[root, .997067]`.
The concavity and tangent-cover conditions hold, and so does the funding `D ≥ (1−η)/(η−β)`.

## Not covered

- #4532's theorem: the integral identities, the existence argument and the critical-endpoint majorant
  proof.
- The criterion's "only if" direction, beyond the counterexample.
- The native premises.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gate-existence-check --check-only
python3.12 -B scripts/research_package.py --package research/gate-existence-check
```

The verifier prints `PASS_GATE_EXISTENCE_CHECK` in about 25 seconds, using only the standard library.

## Open next questions

1. **Combine #4532's critical endpoint with my #4533 retuned geometry.**
   - *Why it matters:* at the crossing exponent, a smaller `n₀` also shrinks the finite cutoff in #4535's
     absorption.
   - *First step:* rerun section C with #4533's p16 witness (`M = 768`, `ℓ₀ = 140`, `p = 3/5`, `c = 400`).

## Credit

- The theorem, the witness and the counterexample are dillona's (#4532), building on #4483.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
