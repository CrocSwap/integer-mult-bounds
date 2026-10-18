# Rank cost of sharing phase repairs across independent groups

**Scoped negative result; no new κ or supplier.** PR #3220 leaves cross-group repair sharing open because its per-group allowance does not charge one hypothetical repair once across multiple groups. This package checks the sharpest two-group relaxation for two independent copies of PR #3220's exact rank-two operator defect.

At the live overlap refresh on 2026-10-17 18:34 UTC, the newest reported conditional κ was PR #3200's `0.001734807021726127552033`. This result does not improve that value; it tests one bounded route for lowering the repair bill.

The source defect at character 16 has rank two over `Q(i)`. For two independent groups, the joint error is a direct sum of those matrices and has rank four. Any caller-level phase-child repairs must therefore carry total rank at least four, even if one repair is shared. With child rank capped at 51 and `0 ≤ a ≤ 1/400`, their total raw moment cost is strictly greater than one unit per group. PR #3220's maximum per-group residual-repacking allowance is strictly less than `153/160`; thus even this direct-sum shared repair cannot pay. The proof extends to any number of independent copies of this same defect; details are in [PROOF.md](PROOF.md).

An optional OR-Tools CP-SAT model optimizes the most favorable two-group repair-rank partition while granting arbitrary routing and exact repairability. It selects one rank-4 child. Its integer objective coefficients are exact lower roundings of `r^(399/400)`, so its optimum is a lower bound on the true best repair bill. The standard-library replay independently recalculates those coefficients and verifies the finite optimum with dynamic programming; no optimizer dependency is required for that check. A separate CP-SAT control requiring total repair rank both at least four and at most three is infeasible. The short analytic inequality gives the general result.

This is not a source-bound audit of two distinct T740 groups. It treats two independent direct-sum copies of the pinned PR #3220 port-zero defect and caller-level phase-child repairs. Overlapping inputs, repairs absorbed into original children, edits inside opaque recursive children, changed interactions and the full routing/stock invoice remain open. The retained PR #3220 proof is credited and copied verbatim under `vendor/`.

## Reproduce

The registered standard-library check verifies the pinned witness, exact Gaussian-integer rank, all-parameter cost inequality and solver receipt:

```sh
python3 scripts/research_package.py --package research/shared-phase-repair-rank --check-only
python3.12 scripts/research_package.py --package research/shared-phase-repair-rank
```

Optional optimization, Python 3.10.12 with OR-Tools 9.11.4210:

```sh
python3.10 research/shared-phase-repair-rank/ortools_shared_repair.py
```

The OR-Tools run is outside registered CI. Its result is retained in `ORTOOLS-RESULT.json`; no optimizer dependency is required for the mathematical replay.

## Open next questions

- **Can this rank-additivity bound be bound to two actual T740 groups with disjoint source subspaces?** It would close the direct-sum premise for a real allocation. First select two groups, authenticate their source/stream maps and prove the joint defect has rank four. The current receipt only duplicates the source-derived port-zero defect on independent abstract inputs; no two-group routing ledger is pinned.
- **Can a repair be absorbed into original paid children?** This package does not change original factors or deduct repair rank from the residual inventory. Follow PR #3220's source and derive one literal changed-child identity plus a complete invoice before searching.

## Credit

The exact source defect and per-group allowance are retained from Ross Richardson's [PR #3220](https://github.com/CrocSwap/integer-mult-bounds/pull/3220), prepared with substantial OpenAI Codex assistance. The source proof is copied verbatim; this package adds the independent-group rank argument, exact cost bound and optional OR-Tools relaxation. No independent human or proof-kernel review is claimed. New work is Apache-2.0.
