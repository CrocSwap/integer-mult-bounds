# Independent arithmetic check of #4535 (conditional κ = 0.003020165)

**Claim type:** an independent arithmetic check with certified intervals. **No new κ.** It covers hexapode's
[#4535](https://github.com/CrocSwap/integer-mult-bounds/pull/4535) (head `cca1112d`). That PR combines
dillona's #4532 critical-root compiler with #4470's unchanged p16 supplier, and proposes conditional κ
= 0.003020165, up from 0.00302015. #4535's `RESULT.json` is vendored here (SHA256-pinned, `-text`). The p16
profile is read from main.

## What is checked

1. **The critical exponent.** `[θ_lo, θ_hi] = [0.9969798340229, 0.996979834023]` brackets the crossing
   `T_θ = P_θ`, certified on both sides. It equals exactly 1 minus the raw-root bracket
   `(0.0030201659770, 0.0030201659771)` that my #4478 certified for #4470.
2. **The saving order.** κ = 604033/200000000 is below the uniform saving 3775207/1250000000, and
   `t − θ_hi = 377/10¹²` exactly, with `t = 1 − uniform saving`.
3. **The mirror condition at θ.** `E_J(θ_hi) ≤ β·S_J(θ_lo)` holds on every elementary window, with
   `β = 141/250`. The worst ratio is **0.56281**, in the window (1/48, 1/41), matching #4535's maximizing cell.
4. **Absorption.** `A·N^θ(133 + ln N)^{2/5} ≤ N^t`, with `ln A ≤ (1 − θ_lo)·ln(145·1024^{650}) = 13.6223`,
   which is #4535's `logA_upper`:

   | evaluation point | margin (lower) |
   | --- | ---: |
   | `ln N = 10¹²`, #4535's `log_threshold` | 352.33 |
   | the stated `N = 2^{10¹²}` | 236.79 |

   It is monotone beyond both points, since `t − θ > p/(133 + ln N)`.

   **Labelling note.** #4535's `margin_lower`, 352.33, is computed at `ln N = 10¹²`, while its
   `primary_certified_N` is `2^{10¹²}`, which has the smaller `ln N ≈ 6.93·10¹¹`. The inequality still holds
   there, with margin 236.79, so the conclusion is unaffected.
5. **The outer rows.** Seven of the nine rows exceed κ:

   | Row | Formula |
   | --- | --- |
   | main transform | `εq` |
   | global router | `a` |
   | fused Gaussian | `1−ε+qβ` |
   | group bit router | `1−ε+aβ` |
   | group scans | `1−ε+β` |
   | polynomial products | `ε` |
   | micro-box faces | `79−ε−β` |

   The **binding main-transform margin is exactly the reported 29969798347/10²⁰**. The parameters follow the
   schedule `κ + 7d, 6d, 5d, 4d, 3d` and `1 − d`, `1 − 3d`, with `d = 10⁻¹⁰`. The two ξ rows are not recomputed,
   because ξ is not printed among #4535's outer parameters.

6. **The finite envelope.**
   - The height `G = 2⌊log₁₀₂₄⌊N/145⌋⌋` is at most `2·10¹¹` at `N = 2^{10¹²}`.
   - Since `W₀ = 10,928 < 2¹⁴` and `W₀ + P₀ + 1 = 75,549 < 2¹⁷`, the class envelope is
     `C_N < 2^{17G+31} ≤ 2^{3400000000031}`.
   - The episode counts are 144 = 18·8 (centre) and 1,680 = 15·112 (thin queries).

   All of this matches #4535's `finite_envelope`.

## Not covered

- #4532's critical-root theorem: the leaf bound `L(n) ≤ A n^θ(c + log n)^p` and its gate criterion.
- Owned storage, routing, precision, stock and tape bounds, beyond the displayed envelope arithmetic.
- The native and physical premises.
- The two ξ outer rows.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/pr4535-arithmetic-check --check-only
python3.12 -B scripts/research_package.py --package research/pr4535-arithmetic-check
```

The verifier prints `PASS_PR4535_ARITHMETIC_CHECK` in about 10 seconds, using only the standard library.

## Open next questions

1. **Print ξ (`cap_xi`) in #4535's outer parameters, so all nine rows can be recomputed.**
2. **An independent check of #4532's critical-root leaf bound.**

## Credit

- The construction is hexapode's (#4535).
- The critical-root compiler is dillona's (#4532). The profile comes from #4470.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
