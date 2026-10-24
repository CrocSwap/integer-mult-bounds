# h = 8 BIT words of the PR555/PR589 family: puncture and receiver census (negative result)

Closed #4633 mentions "292 other h = 8 words" next to PR589's BIT word, with no list behind the number. The actual
family is the choice space of PR555's L3 generator (`research/e8-bit-p111/code/gen_p3.py`). You pick nine punctured
lines by the rule of `discovery/choose.py`, and for each punctured line one of three receiver choices. This package
prices the whole family under the current p16 query-thinned BIT invoice, then asks whether any gain survives on the
current BIT supplier (#4760/#4814, compact436 word).

**Result: no new BIT record.** PR589's puncture set is the best of all 17,478 admissible sets. Some receiver choices
of that set do beat PR589's word, by at most **+0.030%** on the old R439 invoice. The best change collides with the
compact436 lineage. The clean half, transferred additively, is at most **+0.023%** over #4760, which is below the 0.1%
improvement gate that #4760's own `certify()` uses. The selected κ (complex side, 0.00302015) is unchanged.

## What was computed

| Stage | Scope | Outcome |
|---|---|---|
| A | all 17,478 admissible puncture sets (plan seed 552), default receivers | PR589's set unique optimum, R 442; next R 446 |
| B | 200 best sets × 31 receiver draws | every other set R ≥ 445, κ < 0.0034493 |
| C | all 3^9 = 19,683 receivers of PR589's set | 252 above PR589 before tuning |
| tuning | 52 leading receiver profiles, PR589's generic tuner passes | best: receivers 51:3, 89:3 |

Prices are raw roots of `Σ T r^(1-κ) = Σ P r^(1-κ)` for the p16 invoice of
`research/query-thinned-controllers/BIT-CONTROLLER.json`. The local profile and helper widths are replaced exactly as
`research/bit-compact-productive-controller/price.py` does. The words are bracketed on a 10^-15 grid with that
package's outward-interval `exact_series.py`.

| Word (PR555 frozen parameters, receivers changed) | Local paid profile | Raw root |
|---|---|---|
| PR589 (control) | {1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19} | 0.003464248972023 |
| 51:3 and 89:3, 1 tuner move | {1:1322, 2:1338, 3:80, 4:47, 5:102, 6:10, 7:19} | 0.003465298185600 |
| 51:3, PR589's 2 moves | {1:1323, 2:1340, 3:79, 4:45, 5:102, 6:11, 7:19} | 0.003465047544055 |
| 89:3, 1 tuner move | {1:1322, 2:1340, 3:80, 4:46, 5:102, 6:10, 7:19} | 0.003464499497158 |

The best word passes PR555's independent checker `xcheck_p.py` (exact replay, interface lemma H1–H5). Every word
keeps R 439 and the generator's mass identity 8R + 63 + 14v.

## Why it does not transfer to the current BIT head

#4760 prices compact436, which is PR589's word after GL464 + public #1043 helper470 deletion (R437), the R438
zero-helper lineage and #4183's delayed retirement of helper469. Its raw root is 0.003475458064076.

- The 89 receiver rewrites section-A gates on helpers **413 and 469**. These are exactly the carrier pair of #4183's
  retirement. PR589's own "sink" move (469 → 413) is no longer legal on that word, so the composed GL464 + 470
  generator rejects it.
- The 51 receiver touches none of 413/464/469/470. The GL464 + 470 generator (`gl464_470` in `verify.py`, the
  generator of `bit-p111-r437-gl464-470-20261018` with only its input hash pins dropped) runs on it with every guard
  and the full D0 restoration check. On PR589 it reproduces the published R437 hash.
- An additive transfer of the profile change onto compact436 gives at most 0.003476514105 for both receivers (not
  realisable) and 0.003476261827 for 51 alone: **+0.0231%**. This is an estimate, not a constructed word. The
  remaining compact436 steps were not ported, because even a perfect transfer stays below the 0.1% gate.

## Reproduce

Python 3.12, numpy (pinned in VERIFY.json), from the repository root:

```sh
python3.12 -B research/bit-h8-receiver-census/verify.py tables   # about 3 minutes
python3.12 -B research/bit-h8-receiver-census/verify.py words    # about 2-5 minutes
python3.12 -B research/bit-h8-receiver-census/test_verify.py     # eight rejecting controls
```

`data/` holds the census tables: per row the set or receivers, R, the float root used during the census and the
local profile. `verify.py tables` recomputes every float root from its profile, checks the set list against
`sets.py`'s enumeration and rebuilds six rows from scratch. `producer/` holds the resumable drivers that produced the
tables (stage A and B with generator effort NODEOPT 50, stage C with 2000). It is provenance only and is not part of
the registered replay; its paths assume a separate working copy.

## Open next questions

- Carry receiver 51:3 through the rest of the compact436 lineage (#4183 retirement, R438 terminals, signed-cold
  compact). Only worth doing if the improvement gate is relaxed or another receiver-independent gain appears; the
  first step is in TASK.json.
- The family is now closed for BIT gain at h = 8 under PR555's generator. A larger gain would need a different
  generator or a different word height, not another receiver choice.
