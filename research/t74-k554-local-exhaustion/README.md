# Local-move exhaustion on the pivot-566+554 T74 supplier, and packing optimality of the 249/417 dispatch (no new κ)

Since PR1800, the outer has been at its ceiling (κ ≈ b(supplier) up to the free slacks). Any real κ gain must lower the T74 supplier's paid cost. This package records an exact, reproducible negative result for the cheap move families on the current supplier words. It also shows that the idle side of the owner packing is already optimal.

The words are the base and extra words carried by PR1839/PR1800 (identical bytes to PR1672's `new/*-word-566.json.gz`; pinned in `inputs/PINS.json`).

## Results (`RESULTS.json`, raw data in `data/`)

1. **Deletion relaxation of every B read.** All 1,797 `add` gates were deleted one at a time and re-solved with exact optimal frames, ignoring exactness and using the base cone caps.
   - 1,002 deletions would save cost; the histogram is in `RESULTS.json`.
   - Exactly 16 reads save one rank-2 split (−4,913 units):
     - the second early reads of pivots 448/450/452/454/585/587/589/591;
     - the early reads of 473/497/521/545/586/588;
     - the two costly reads of the 566/554 kernels themselves (B1 `126 += 554`, B3 `150 += 566`).
   - Every other gain is a delivery read (−8.9k to −26.4k), a first write, or a −3,050/−6,100/−6,763 structural read.
   - Each of the 1,002 deletions moves value into target rows. Compensation must therefore happen inside B (the dirt rule), and none can move to the frame-free cleanup prepends. No early-cleanup gate has only full-end registers.
2. **Frame-cost oracle.** `tools/costorc.py` gives the exact marginal cost of an inserted read from the deleted word's optimal frames: 0 when either register already sits at, or next climbs exactly to, a common frame; otherwise the split cost `c_a + c_(k-a) − c_k`. Calibration on PR1672's pivot-554 kernel (`tools/validate554.py`):
   - the oracle gives `[0, 4913, 0, 0]` for the inserts and 0 for the tail;
   - so the whole kernel cost is one rank-2 split on target 126, against a −6,763 deletion;
   - the cost-aware search (`tools/gencomp2.py`) rediscovers a −1,850 kernel by itself.
3. **Compensation searches: 107 runs, no negative delta.**
   - All 16 one-split reads with budget 4,912, plus a pivot-specific variant (`tools/fc3.py`) with zero-cost inserts in B and in early-cleanup tails: infeasible. The required target-row contributions always cost at least one split.
   - 85 large-gain reads: the source value lives in a single short window, or some effect row has no admissible candidate.
4. **Exact sweep of every single-gate commuting move.** All 1,002 gain-carrying reads were tried at every distinct position in their commutation window (4,461 positions), each priced with the exact frame solver:
   - 2,131 cost-neutral;
   - 2,330 frame-infeasible;
   - **0 gains, 0 losses.**
5. **A section.**
   - A one-in-six sample (327 gates) shows cold-pivot pre-cancels in A (e.g. A1220 `479 −= 527`, −6,763) and data butterflies (−9.8k/−20.8k).
   - Compensation across A, B and tails (`tools/abkernel.py`, full-program exactness plus the dirt rule) fails for the −6,763 cold-pivot pre-cancels, A1220/1226/1232/1238/1244.
   - 91 rewrites of a cancelling read pair into reads of the pivot's writer are all frame-infeasible.
6. **Owner packing is idle-optimal.** `tools/aggT74.py` and `tools/aggmix.py` are an aggregate ILP relaxation over all T74 child windows (caps = 112 × the PLAN window counts by rank).
   - Switching any K = 12, 24, … of the 417 extra calls to base is **infeasible**.
   - Over every mix of the five entrance-demotion variants (W_res 3734–3738), the maximum number of empty rank-48 children is **22,748**, the current value. It is attained by 249 base / 417 extra.

   Supplier-mix or modulo-48 rebalancing cannot add rank-48 idle children.

## Scope

These are finite searches of specific move families on two fixed words, with the PR1186 exact frame model, the dirt rule and cone caps. A two-or-more-gate rewrite outside these families, a new kernel mechanism, or a change of parent or centre interface (for example centre-path sharing, PR1708/1748/1791) is not excluded. No κ is claimed and no construction is changed.

## Reproduce

```sh
python3 -B research/t74-k554-local-exhaustion/verify.py --work /absolute/new/work   # ~6 min on 2 cores: pins, profiles, oracle calibration,
        # 32+32 sampled re-solves, the 16 one-split searches, the packing ILPs, result consistency
python3 -B research/t74-k554-local-exhaustion/verify.py --work /abs/work --full    # re-solves every relaxation and move (CPU hours)
```

This needs Python 3.11+, NumPy and OR-Tools (CP-SAT) for the searches and ILPs. `vendor/exact-frame-toolkit` is PR1186's toolkit, vendored verbatim; it resolves `audit_local.py`, `research/frame-domain-ceiling` and the multicold engines from main.

## Credit

- PR1186 (exact frame toolkit).
- PR1625 (mdumitrean): the pivot-566 kernel.
- PR1672 (jeremykothe2 / LeverRank): the pivot-554 kernel.
- PR1319/PR1297 (Rohan Arun): T74 exact fill and windows.
- PR1193: the mixed-provider flow.
- PR1839/PR1800 (jeremykothe2): the current packages carrying these words.

Prepared by Rohan Arun with substantial AI assistance (Anthropic Claude). Apache-2.0.
