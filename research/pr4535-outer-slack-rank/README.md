# #4535 at outer slack `d = 10^−12`: same κ, a 34× smaller certified finite rank

**Task:** independent-moment. **Base:** canonical main `f626db5c`. **No new κ.** κ = 0.003020165 is unchanged, as are the root bracket, the mirror, the majorant parameters and the native supplier.

hexapode's #4535 (head `a6d7237f`) sets every outer parameter from κ and a slack `d = 10^−10`:
- `b, a, q = κ + 5d, 4d, 3d`;
- `ε = 1−d` and `β = 1−3d`;
- `r0 = d/10`, `stop = layout = d`;
- tested saving `κ+7d` and complex uniform saving `s_C = κ+6d`.

The frozen compiler word must satisfy absorption with gap `z − θ_hi = (1−θ_hi) − κ − 6d`. My #4563 showed that the least certified rank at `d = 10^−10` is `2^77,014,944,503`. A smaller `d` widens the gap.

## Result

The verifier runs **the exact outer-ledger source #4535 pins**, `research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py` (SHA256 `d097e55f…`), with the ordinary BIT admission from `research/compact-joint-compiler/arithmetic/RESULT.json`, as #4535's `verify.py` does.

| | `d = 10^−10` (#4535) | `d = 10^−12` |
|---|---|---|
| 54 strict predicates, 4 functional guards, 9 margins `> κ` | pass | **pass** |
| minimum outer margin above κ | `29969798347/10^20` (control, exact) | `2996979834997/10^24` |
| absorption gap `z − θ_hi` | `377/10^12` | **`971/10^12`** |
| least certified rank `K` (`N = 2^K`) | 77,014,944,503 (#4563) | **29,328,002,299** |
| `log₂` class envelope `17·G_depth + 31` | 2.62·10^11 | **9.97·10^10** |

- **Control.** At `d = 10^−10` the ledger reproduces #4535's recorded minimum margin and its full `outer_parameters` exactly.
- **Rank exponent.** At `d = 10^−12` the frozen rank's exponent is **34.1× smaller than #4535's `10^12`**.
- **Certification.** The rank comes from my own certified logarithms (exact rationals): it is minimal, it holds monotonically beyond, and it uses the same `A`, `p = 2/5`, `c = 133` and `n0`.
- **Smaller `d`.** Smaller `d` only moves the gap toward its limit `(1−θ_hi) − κ ≈ 9.77·10^−10`; `d = 10^−12` already reaches 99.4% of it.

## The trade-off

A smaller `d` shrinks the outer power gaps, which are of order `3d`. #4535 absorbs the frozen word's fixed constants into the eventual input cutoff through those gaps, so the cutoff's logarithm scales roughly like `log(constants)/d`.

The frozen word's constants grow with `N = 2^K`; for example, #4535's width envelope is `B_N < C_N^N`. Their logarithms therefore scale at least like `2^K`. Going from `d = 10^−10` to `10^−12` multiplies `1/d` by 100 but divides `2^K` by `2^(4.77·10^10)`, so the net effect on that crude cutoff estimate is overwhelmingly favourable. This is a heuristic comparison of envelopes, not a computed cutoff. #4535 computes no explicit cutoff, and neither does this package.

## Verify

```text
python3 -B research/pr4535-outer-slack-rank/verify.py
```

This runs in about 2 s with the standard library only.

## Limitations

- **Scope.** This changes only `d`, and with it the derived outer parameters and the frozen rank. It does not re-certify the root bracket, mirror or majorant; it uses #4535's certificate.
- **Unchanged.** Physical constants, the outer input cutoff and selection are untouched.
- **Cutoff comparison.** The comparison above is heuristic.

## Open next questions

- A majorant retune, a smaller `n0` or `p`, needs #4532's gates rechecked at `θ`. At the new gap, `ln A ≈ 10.24` and `p·ln(c+ln N) ≈ 9.4` contribute comparably to `K`. First step: tabulate #4532's p16 gate margins against `ℓ0` and `p`.

Credit: hexapode (#4535); Dillon (#4532); zxv and Jacob Alan Sussman (compiler and majorant lineage); Cinna Davis (#4470); the outer-ledger lineage in `pr4359-p7-padding`. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
