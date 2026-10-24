# Independent arithmetic check of #4568 (conditional κ = 0.00302016597)

**Task:** independent-moment (independent source-bound coverage). **Base:** canonical main `f626db5c`. **No new κ** of my own.

hexapode's #4568 (head `b269a729`) raises #4535's conditional κ by 9.7·10⁻¹⁰, to **0.00302016597**. It uses my #4564's outer slack `d = 10^−12` together with the unchanged #4470 profile, #4535's critical-root bracket and #4532's majorant. The new outer point is `z = .996979834024`, with `q, a, b = κ + 3d, 4d, 5d`, `s_C = κ + 6d` and tested saving `κ + 7d`. The frozen word is at `N = 2^(10^14)`. #4568's `RESULT.json` is vendored (blob `540ffb95`, SHA256-pinned).

## Results

All checked claims are confirmed.

- **Outer ledger.** I replayed the exact source that #4535 and #4568 pin (`pr4359-p7-padding/.../endpoint.py`, SHA256-checked) at #4568's parameters, which are confirmed to be exactly `κ + jd`.
  - All 54 strict predicates, the 4 functional guards and the 9 margins above κ pass.
  - The minimum margin is `2996979834027/10^24`, matching #4568's record.
- **Saving order.** `κ < s_C < tested saving = 1 − θ_hi < 1 − θ`. The tested saving equals the bracket endpoint `1 − θ_hi` exactly. It stays strictly below the root's saving only because the certified root lies strictly inside #4535's open bracket, which the bracket certificate guarantees. The absorption gap is `z − θ_hi = 10^−12` exactly.
- **Absorption.** At `N = 2^(10^14)`, my certified margin is 42.94 nats, above #4568's conservative 418/15. The least certified ranks at #4568's κ are:

| majorant | least `K` (`N = 2^K`) | vs #4568's `10^14` |
|---|---|---|
| #4532 witness, #4568's coarse `ln A` | 37,477,695,815,212 | 2.67× smaller |
| #4532 witness, `A`'s own definition | 32,523,485,165,724 | 3.07× smaller |
| **my #4565 retuned witness** (`M = 2^24`, `ℓ0 = 64`, `p = 3/10`, `c = 101`) | **14,562,291,820,122** | **6.87× smaller** |

So #4568's frozen word can be built at a rank exponent at least 6.9× smaller, at the same κ, by combining it with #4565. Each `K` is the least certified one, and the inequality holds monotonically beyond it.

I also replayed #4568's registered package: `PASS_REGISTERED_RESEARCH_PACKAGE research/critical-slack-multiplication outcome=completed` in 8.4 s.

## Verify

```text
python3 -B research/pr4568-arithmetic-check/verify.py
```

This runs in about 3 s with the standard library only.

## Limitations

- **Not covered.** The critical-root bracket, mirror and #4532 gates are #4535's and are not recomputed here; my #4536 and #4569 cover them. Native, physical and outer-cutoff premises are out of scope, as in #4568.
- **Admission.** Whether a κ gain obtained by retuning outer slack against the same raw root counts as a hill-climb step is a maintainer decision. Per #4568 itself, the native paid profile and raw root are unchanged. This package takes no position.

## Open next questions

- None new from the arithmetic. Whether a slack-retuned κ is admitted is for the maintainers.

Credit: hexapode (#4568, #4535), Dillon (#4532), Cinna Davis (#4470), zxv and Jacob Alan Sussman. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
