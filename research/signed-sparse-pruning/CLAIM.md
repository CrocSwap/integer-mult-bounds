# Sprint claim

- Track: verification engineering; OS-random assignment seed: **92**.
- Base: `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`.
- Object: `scripts/experiments/signed_sparse_core.py::coefficient_terms`.
- Hypothesis: prune prefixes of coordinate choices once their minimum degree
  exceeds q-1, preserving every exact coefficient and its iteration order.
- Deliverable: focused optimization, exhaustive before/after stream comparison
  for all 13 valid (h,q) pairs with 2 <= q <= h <= 8 and q a power of two,
  full historical audit equivalence, failure controls and same-input timings.
- Candidates considered: this enumeration; triple-core incidence elimination;
  prime-subset partial-output support reconstruction. Seed 92 chooses index
  92 modulo 3 = 2 from [triple-core, prime-subset, signed-sparse].
- Scope excludes selected suppliers and any new mathematical search or bound.
- Coordination: GitHub reports no pinned issues; the only open issue was #650
  (Discussions). Open PR titles and the review ledger were checked; existing
  stage-pair, single-intersection, quadratic-affine and cyclic optimizations
  concern different objects. No overlapping signed-sparse enumeration found.
- Expected finish: within 25 minutes of claim, final quarter reserved for
  verification and submission. No delegated workers.

## Result / final handoff

Completed: all 13 ordered streams and the full historical certificate agree;
14 relevant tests pass, including two factor-identity negative controls.
Enumeration improves; no full-audit speedup or new κ is claimed. Exact timings,
pins, reproduction command and inherited limits are in README.md / RESULT.json.
Final overlap refresh found no competing change to this routine.
Submitted: https://github.com/CrocSwap/integer-mult-bounds/pull/833
