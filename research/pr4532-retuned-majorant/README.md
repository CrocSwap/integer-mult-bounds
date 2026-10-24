# Retuned p16 critical-root majorant: #4535's frozen rank 85× smaller (same κ)

**Task:** independent-moment. **Base:** canonical main `f626db5c`. **No new κ.** κ = 0.003020165 is unchanged, as are the #4470 profile and the isolated critical root.

The frozen compiler rank `N` in hexapode's #4535 is set by absorption:

```text
ln A + p·ln(c + ln N) < (z − θ_hi)·ln N,    A = n0^(1−θ)/(c + ln n0)^p,   n0 = 145·M^ℓ0.
```

My #4563 and #4564 kept Dillon's #4532 p16 majorant (`M = 1024`, `a = b = 1`, `ℓ0 = 650`, `p = 2/5`, `c = 133`) and changed only the rank and the outer slack. Here the majorant itself is retuned. A larger height base lets the tangent cover and the recurrence funding hold at a much smaller base cutoff, which cuts `ln A` from 10.24 to 1.11 and `p` from 2/5 to 3/10.

## Result

**Gates.** #4532's own exact checker, `critical_guards` from `root_application.py` (vendored from #4535 head `a6d7237f`, blob `89d6139b`, SHA256-pinned), passes on the p16 profile (`compact-joint-compiler/arithmetic/RESULT.json`, SHA256-pinned) for:

| | #4532 p16 witness (control) | **retuned** |
|---|---|---|
| geometry | `M = 1024`, `a = b = 1`, `ℓ0 = 650` | **`M = 2^24`, `a = 3`, `b = 2`, `ℓ0 = 64`** |
| tails | `s = 1/20`, `λ = 1/10` | `s = 1/10`, `λ = 1/5` |
| log majorant | `p = 2/5`, `c = 133` | **`p = 3/10`, `c = 101`** |
| guards U, V, Q, d, β | .963, .992, 1.001, 1.03, .564 | .9494, .8776, 1.0015, 1.04, .564 |
| cover exponent | .997067 | .99725 |
| mixed / root tail (upper) | .96237 / .99162 | .94887 / .87703 |
| mirror at cover (upper) | .563147 | .563849 < β |
| tangent exponent (upper) | .997067 | .997237 ≤ .99725 |
| funding: lower vs required | .048546 vs .042809 | .043565 vs .042809 |

Three mutations of the retuned witness are rejected: `ℓ0 = 40` fails the tangent cover, `p = 1/5` fails the funding, and `β = .55` fails a mirror window.

**Ranks.** These are certified with my own logarithms in exact rationals. Each is the least integer `K` at `N = 2^K`, monotone beyond and above `n0`:

| | gap `377/10^12` (`d = 10^−10`) | gap `971/10^12` (`d = 10^−12`, #4564) |
|---|---|---|
| #4535 as published | `K = 10^12` | — |
| #4532 witness (control) | 77,014,944,503, reproduces #4563 | 29,328,002,299, reproduces #4564 |
| **retuned** | **31,585,308,786** | **11,825,387,808** |

At `d = 10^−12` the retuned frozen rank `N = 2^11,825,387,808` is **84.6× smaller in exponent than #4535's `2^(10^12)`**. The word's height envelope is `G_depth ≤ 2.46·10^9`, against 2·10^11. Its class-count envelope is `log₂ C_N ≤ 4.19·10^10`, against 3.4·10^12. Both are recomputed with `g = 5` and `M = 2^24`.

## Verify

```text
python3 -B research/pr4532-retuned-majorant/verify.py
```

This runs in about 4 s with the standard library only.

## Limitations

- **What changes.** Only the critical-root compiler geometry (`M`, `a`, `b`, `ℓ0`), the tail exponents (`s`, `λ`), the majorant (`p`, `c`) and the frozen rank change. The physical bridge of #4535 §4 must apply to the new fixed word just as to the old one. Its envelopes are recomputed here, but no physical constant is computed.
- **Search.** The parameters come from a floating-point search over a coarse grid, and were then certified exactly. Better choices may exist.
- **Gate checker.** The gate certification is #4532's checker, run unchanged. My contribution is the parameter choice and the independent rank certificate.

## Open next questions

- A finer or two-level search, varying `β` and the cover exponent jointly. At the retuned point, `ln A ≈ 1.1` and `p·ln((c+ln N)/(c+ln n0)) ≈ 5` nats, so `p` is now the main lever. First step: maximise the funding margin `a·d/ln M` subject to `u < 1`.

Credit: Dillon (#4532 critical-root theorem and checker), hexapode (#4535), zxv and Jacob Alan Sussman (compiler and majorant lineage), Cinna Davis (#4470). Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
