# A 13× smaller certified finite rank for #4535's critical-root compiler (same κ)

**Task:** independent-moment. **Base:** canonical main `f626db5c`. **No new κ.** κ = 0.003020165 is unchanged, as are the parameters, the root bracket, the mirror and the outer ledger.

hexapode's #4535 (head `a6d7237f`) freezes its finite compiler word at `N = 2^(10^12)` and certifies absorption `L(N) < N^z` from #4532's funded majorant `L(n) ≤ A n^θ (c + ln n)^p`. The parameters are `p = 2/5`, `c = 133` and `n0 = 145·1024^650`, with `z − θ_hi = 377/10^12`. Absorption needs only

```text
ln A + p·ln(c + ln N) < (z − θ_hi)·ln N.
```

The left side grows like `ln ln N`. At `ln N ≈ 6.9·10^11` it is about 24 nats, while the right side is about 261. **The rank is therefore about 13× larger, in exponent, than the certificate needs.**

## Result

| Quantity | #4535 | This package |
|---|---|---|
| Frozen rank `N` | `2^(10^12)` | **`2^77,014,944,503`** |
| `ln A` bound used | 13.6223, from `(1−θ_lo) ln n0` | **10.2450**, from #4535's own `A = n0^(1−θ)/(c+ln n0)^p` |
| Height envelope `G_depth` | 2·10^11 | **1.540·10^10** |
| Class-count envelope `log₂ C_N` | 3,400,000,000,031 | **261,850,811,331** |

- **Same `ln A` bound.** With #4535's coarser `ln A` bound, the least certified rank is already `2^90,180,626,561`, an 11.1× smaller exponent.
- **Minimality.** Both ranks are the **least** integers `K` for which the inequality is certified at `N = 2^K`. The verifier also shows that the inequality fails at `K − 1000`, even with the most favourable bounds, so `K` is minimal for these parameters up to 1,000.
- **Larger ranks.** It holds at every larger `N`, because `z − θ_hi > p/(c + ln N)`.
- **Base cutoff.** `N` exceeds `n0`.
- **Consistency.** At `K = 10^12` the margin is 240.17 nats (236.79 with the coarse `ln A`), consistent with #4535 and my #4536.

**Why it matters.** #4535 freezes the finite word at `N` before the multiplication input grows. Its height, class count, divisible widths (`B_N < C_N^N`), record envelopes and, with them, the eventual input cutoff all grow with `N`. A 13× smaller `log N` shrinks the class-count exponent 13× and the width bound `C_N^N` correspondingly. Nothing physical is materialised or claimed here.

All logarithms come from my own certified bounds: atanh series with explicit remainders in exact rationals, with `ln 2` enclosed to `10^−50`. #4535's `RESULT.json` is vendored (blob `1c7af6e3`, SHA256-pinned) for the bracket, gap, saving and κ.

## Verify

```text
python3 -B research/pr4535-smaller-rank/verify.py
```

This runs in about 2 s with the standard library only.

## Limitations

- **Scope.** This uses #4535's certificate as given: its root bracket, gap and #4532's funded majorant. It changes only the frozen rank `N`. Physical constants, the outer cutoff and selection are untouched and not claimed.
- **Not re-optimised here.** `p`, `c`, `n0`, `M` and `g` are not retuned. See the open questions.

## Open next questions

- **Outer slack `d`.** The gap `z − θ_hi = (1 − θ_hi) − κ − 6d` uses `d = 10^−10`. Halving `d` would raise the gap to `6.77·10^−10`, shrinking `K` by a further 1.8×. This needs a fresh 54-predicate outer replay at the new `(a, b, q, ε, β)`. First step: rerun #4535's outer ledger at `d = 5·10^−11`.
- **Majorant retune.** A smaller `ln A`, via a smaller `n0`, or a smaller `p` needs #4532's tail and funding gates rechecked at `θ`. First step: tabulate the gate margins of #4532's p16 witness against `ℓ0` and `p`.

Credit: hexapode (#4535); Dillon (#4532); zxv and Jacob Alan Sussman (#4483 compiler and majorant lineage); Cinna Davis (#4470 supplier). Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
