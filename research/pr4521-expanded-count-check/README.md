# Independent check of #4521: #4436's expanded rank-mass identity

**Task:** independent-moment (independent source-bound coverage). **Base:** canonical main `f626db5c`. **No new κ.**

Dillon's #4521 (head `d72f2282`) checks the fully expanded counting identity of zxv's #4436, with nested widths:

`B_n·n − P_n = Δ·Q_n`, and `U_n ≤ Q_n ≤ B_n·n/Δ` for positive surplus.

Here `B_n` is the width, `P_n` the number of rank-one leaves, `U_n` the number of raw invocations and `Q_n` their column multiplicity. #4521 retains every source complement, exit and integer batch multiplicity, and publishes SHA256 hashes of the exact big-integer totals.

This package recomputes those totals with **my own** #4436 flow (`flow4436.py`, written for my #4456 checks). Nothing is imported from #4521 or #4436. The recurrence uses `a_n = B_(n−1)` and `B_n = a_n·S_n`, with child batches `a_n S_s / B_(n−s)` (complements) and `a_n E_e / B_e` (exits), which must be integers.

## Results

All checked claims are confirmed.

- **Every rank.** `B_n·n − P_n = Δ·Q_n` and `U_n ≤ Q_n ≤ B_n·n/Δ` hold exactly. All child batches are integral, and ranks strictly descend.
- **Checkpoints.** The exact big integers `B`, `P`, `Q` and `U` match #4521's published SHA256 hashes and bit lengths, **12 of 12**, at:
  - two toy rules at rank 100 (`{2:1,5:1} ← {1:2,4:1}` and `{2:4,3:1} ← {1:6,2:2}`);
  - raw p7 at rank 1000, bound to main's `higher-moment-strictification/RESULT.json`. At rank 1000, `B` has 17,504 bits, `P` 17,514, `Q` 17,497 and `U` 17,497.

`#4521`'s `RESULT.json` is vendored (SHA256-pinned) for the published hashes only. #4521's "routes" count is not recomputed.

## Verify

```text
python3 -B research/pr4521-expanded-count-check/verify.py
```

This runs in about 3 s with the standard library only.

## Limitations

- **Finite ranks.** The checks run through rank 1000. The all-rank induction is #4521's written proof, and this corroborates its finite instances.
- **Out of scope.** Native, physical and precision obligations, as #4521 states.

## Open next questions

- None new. The same recurrence with #4507's chronological widths is covered by my #4519 and #4588.

Credit: Dillon (#4521), zxv (#4436), Jacob Alan Sussman (compiler), Cinna Davis (raw p7). Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
