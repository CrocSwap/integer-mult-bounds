# CopyCheck: do RankLaw's COPY / SCALE-0 caveats bite on #7623? No.
Lane LEAN-NEXT10, Nov 16. Data check, exact Python (Nov15/copycheck.py, ~8 s, stdlib Fractions). No Lean needed.
Word: cards/WILD/BIG/LOANBUILD/hit_loan_14.json.gz (#7623): 1501 public, 68 owned fields, 77,277 events
(ADD 66,930, SCALE 3,729, MOVE 6,257, INIT 180, CLEAR 180, COPY 1).

**COPY semantics (source: official replay).**
- SODDPKG `native.py` replay (the repo's native verifier):
  - `COPY r s q f` requires r owned and `rows[r]` empty (`need(r in owned and not rows[r], 'COPY zero')`);
  - then it does `rows[r] += q*rows[s]`, the same as ADD.
- PRICEKIT `replay` (used by accx2.py) is the same add, and flags `copy-nonzero` as a problem. accx2 demands 0 problems.
- `physical_exact.py` overwrites. On a zero row, overwrite and add agree.
- So the official COPY is "ADD into a zero row" (i.e. TokenCancel `copy` then `scale q`).
  - A zero row lies in span(other rows), so an official COPY is never `Lossy`.
  - RankLaw's `copy_lossy_example` (COPY over a live row) is illegal under the official verifier.

**SCALE 0.** native.py requires `q != 0` for every SCALE/ADD/COPY scalar. So SCALE by 0 is illegal, and RankLaw's `NZ` hypothesis is a verifier rule.

**Exact counts on #7623.**
| check | count |
|---|---|
| COPY events | 1 |
| COPY into a nonzero row (the only way a COPY can be lossy) | 0 |
| SCALE events / SCALE by 0 | 3,729 / 0 |
| CLEAR of a nonzero row | 177 (of 180) |

**The 177 nonzero CLEARs are not lossy either.**
- The final rows of the full word have rank 1501 = number of tokens (public start registers; an owned INIT is 0, so it adds no token).
- Certificate: mod-p rank with p = 2^61−1. That is a lower bound on the rank over Q, and no denominator is divisible by p.
- By `RankLaw.rank_run` a lossy step leaves the final rank ≤ |tokens| − 1. So the full #7623 word has no lossy CLEAR or COPY.
- Scope: this is the full word. RankLaw is applied to the run with the V-hub ops deleted, which is a different list. Its CLEARs are a subset of these; their lossiness there is not covered by this certificate.
  - The COPY / SCALE-0 statements above hold for every sublist.

**Verdict.** RankLaw's hypotheses `NZ` and "no lossy COPY" hold on #7623 by legality (official verifier), and also by exact count.
RankLaw Finding 1 ("every op except CLEAR is invertible" is false with COPY) is a model-level caveat only. It does not affect #7623.
