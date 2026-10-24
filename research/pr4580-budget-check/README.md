# Independent arithmetic check of #4580: the p3 H-branch boundary budget

**Task:** independent-moment (independent source-bound coverage). **Base:** canonical main `f626db5c`. **No new κ.**

Matarener's #4580 (head `62545a03`) prices zxv's p3 H branch at the #4470 frontier, κ = 0.00302015. At most **322** complex and **397** BIT rank-one boundary calls are affordable, and the direct correction (672 and 666 calls) fails even at `s = 0`. #4580 also gives saving roots for one and two shared head conjugations, and checks the native H112's low-rank structure and the distinct query lines.

This package recomputes all of that arithmetic with its **own** certified powers `r^(1−s)`, using atanh logarithms and range-reduced exp series in exact rationals, rounded outward on a `2^−256` grid. It never uses the sources' `h_interval`. The H112 checks use its own exact elimination. Only the signed rank profiles and H112 are read from the same main sources (16 inputs, SHA256-pinned).

## Results

| | complex | BIT |
|---|---:|---:|
| raw surplus | 616 ✓ | 645 ✓ |
| budget at κ = 0.00302015 (budget + 1 certified negative) | **322** ✓ | **397** ✓ |
| direct bill fails at `s = 0` | 672 ✓ | 666 ✓ |
| own certified root, no extra bill | 0.0063799044338 | 0.0079333534813 |
| root, one head (224 / 222) | 0.0040422293244 | 0.0051761597317 |
| root, two heads (448 / 444) | 0.0017248833468 | 0.0024471105557 |

The native H112 has `rank(H − I) = 8`, every one of its 112 rows and 112 columns is nonzero, and `H² = I`. There are 112 distinct complex query lines, and 111 distinct BIT lines up to sign.

**One reporting note, not a defect in the conclusions.** #4580's `RESULT.json` prints its bisection endpoints to 10 decimals. Every printed `positive_at` is certified positive, and every printed `negative_at` lies within #4580's bisection width (`0.02/2^26 ≈ 3·10^−10`) of the root. But two printed `negative_at` values fall **just below** the root, where the moment is still positive:
- complex, no extra bill: printed `0.0063799044`, root `0.00637990443…`;
- BIT, bill 222: printed `0.0051761597`, root `0.00517615973…`.

They are roundings of valid exact endpoints, not certified brackets themselves. The budgets, roots to the stated 7 digits, and the negative result are unaffected.

## Verify

```text
python3 -B research/pr4580-budget-check/verify.py
```

This runs in about 20 s with the standard library only.

## Limitations

- **Not covered.** The decoder lower-bound argument of #4580 §4 (gather decoders need one request per port line) is a written argument, and only its finite inputs (line counts and support) are checked here. The H-branch profiles themselves are the sources'.
- **Raw rank screen.** As #4580 says, these budgets omit outer rows, tails and compiler gates.

## Open next questions

- None new from the arithmetic. #4580's own open question, changing the local family or line structure, is untouched.

Credit: Matarener / Mark (#4580); zxv (#4359 H branch); the #4431, #589 and kappa-rebuild lineage. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
