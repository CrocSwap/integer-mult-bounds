# Independent certified check of #4483's finite gates and arbitrary-height flow

**Claim type:** an independent certified recomputation by separately written code. **No new κ.** It covers
zxv's [#4483](https://github.com/CrocSwap/integer-mult-bounds/pull/4483) (`research/rank-convergence`). That
PR changes the direct flow's stopping height and closes the recursion with a shifted-logarithmic majorant,
reporting the p16 sufficient rank `2^2800000000` instead of `2^558100005581` at κ = 0.00302015. It is a
compiler follow-up in the maintainers' #4470 review plan, and it answers the obstruction my
#4459/#4465/#4467 described.

## What is checked, for all four witnesses in `BENCHMARKS.json`

Each raw profile is read from its pinned source. Everything uses certified interval logarithms and
exponentials (the helpers of my #4455), with exact rational powers for `U^{ℓ₀}` and `V^{ℓ₀}`.

- **The guards (18) on `[t₀, t_hi]`:**
  - `T_{t₀} > P_{t₀}`;
  - `d ≤ μ_T(t₀) − μ_P(t_hi)`, where the μ are tilted log means;
  - the bounds `Q`, `U` and `V`;
  - the ratio ordering `T_{t₀+s}/T_{t₀} ≥ P_{t_hi+s}/P_{t_hi}`;
  - `η_min ≤ t₀m^{t₀−1}` and `c ≥ p/(1−t₀)`;
  - `τ(n₀) ≤ t_hi`.
- **The mirror guard (4)** on every elementary window, for each of the 20 t-slices, in the sufficient form
  `E_J(t_b) ≤ β·S_J(t_a)`.
- **The recurrence inequality (20)** and the **final funding (17)** at `N = 2^H`.

| witness | D (lower) | required | worst mirror ratio | τ(n₀) ≤ t_hi | final margin (lower) |
| --- | ---: | ---: | ---: | --- | ---: |
| p7 | 0.02858992 | 0.02336096 | 0.32091 | 0.9974809363 ≤ .997481 | 0.00003773 |
| native4453 | 0.05448611 | 0.04422604 | 0.57408 | 0.9971361473 ≤ .9971362 | 1.19575350 |
| native4453, matched uniform | 0.05448611 | 0.04422604 | 0.57408 | same | 0.32116914 |
| **p16** | **0.04854643** | **0.04306220** | 0.56287 | 0.9970659832 ≤ .997066 | **0.60862507** |

All match #4483's stated values. Two margins are thin but certified positive:

- p7's final margin of about 3.8·10⁻⁵;
- the `τ(n₀)` covers, with slack of about 2·10⁻⁸ to 7·10⁻⁸.

PROOF.md's rejection control, `t_hi = .9974808` for p7, is rejected.

## Arbitrary-height flow (#4483's open question 1)

On raw p7 at `N = 500, 3000, 20000`, my independent #4436 flow is run with a forced height `G`, at every
`G = 0, …, G₀ + 2`. That range includes heights above the old minimum-target height, where root classes
are empty. Over these 13 cases:

- the exact rank-one identity `Σ S·s − Σ X·e = 608·col` holds;
- every exit stays below `n`;
- the exact mirror identity of #4459 holds.

So PROOF.md §1–2's flow identities do not depend on the old height.

## Not covered

- PROOF.md's theorem itself, including the Chernoff and majorant arguments. Only its finite gates are
  recomputed here.
- The native suppliers and the outer consumer points.
- The stopping heights actually used inside the certificates, beyond `τ(n₀)`.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/rank-convergence-gates --check-only
python3.12 -B scripts/research_package.py --package research/rank-convergence-gates
```

The verifier prints `PASS_RANK_CONVERGENCE_GATES` in about 7 minutes, using only the standard library.

## Open next questions

1. **Can p7's 3.8·10⁻⁵ final margin be widened by a small change of `(t₀, c, ℓ₀)`?**
   - *Why it matters:* it gives a more robust p7 witness.
   - *First step:* scan `ℓ₀` and `c` with this certified checker, holding the consumer saving fixed.

## Credit

- The theorem, the witnesses and the adaptive height are zxv's (#4483).
- The flow is from #4436. The mirror identity is from my #4459.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
