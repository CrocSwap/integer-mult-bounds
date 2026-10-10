# 365 net-positive supplementary equal-response pair families and the concave-descent retiming on the multi-cut kernel condensation

**Conditional kappa = 355713000638059 / 500000000000000000 = 0.000711426001276118**, +1.25 × 10⁻⁶ (+0.176 %) over PR259's 518-entrance condensation (0.000711029386054035).

This package is [PR259](https://github.com/CrocSwap/integer-mult-bounds/pull/259)'s multi-cut kernel condensation (Dugongue) with two additions and no change to its native checkers:

1. **365 supplementary pivot families (363 after the transform's mod-3 entrance normalization)** (`inputs/candidates-supplementary.json.gz`, consumed by the unchanged `cohort-transform` through its own extra-candidate-file interface). At the first cut (record 676,559) the untouched zero-start helpers that PR259 leaves unused have dirty-response columns of F₂ rank 1,760 among 13,093 helpers, so dependencies are abundant; the binding constraint is geometric. Among the 618 exact equal-response pairs left over, pairs are kept only when the pivot's saving g(r_p) − g(r_p − e) exceeds the donor's extra ascent cost g(e) + g(r_d − e) − g(r_d) under g(r) = r·ln(120/r), with the pivot chosen to minimize that total (earlier drafts of this package admitted every intersecting pair, which prices lower): 365 disjoint net-positive pairs with a nondegenerate common subframe and an admissible prime witness (362 lines, 3 planes), 363 kept by the transform's mod-3 normalization, adding 366 entrance-rank units (raw mass 434,177 → 432,467, 59,184 initial compensation reads removed in total, 881 cohorts, 1,920 distinct helpers). The transform validates each family exactly as it validates PR259's (untouched before its cut, prefix reads only zero-frame dirty reads into targets, exact first-frame containment of the entrance frame, independent entrance basis, nilpotent basis support) and replays all 20,107 formal columns forward and inverse; the independent legality, prefix-kernel (1,643,840 equalities), bank, five-stage column, price and invoice checkers then re-examine the combined word.
2. **The 25-gate concave-descent frame retiming** (`code/descent_retiming.py`, `inputs/descent-selection.json`), re-searched on the 934-family transcript: one local recursive call per helper invocation disappears at unchanged rank mass. The stage rebuilds every MOVE from the retimed gate needs and checks the byte-identical scalar/COPY projection, nested chains, fixed endpoints and COPY lifetimes, nondegenerate endpoint bases, and the exact integer source span of every non-target operand inside its new frame.

Normalized retained profile: stock 173,313, 3,971,320 calls, rank mass 20,762,360, deficit 35,200; literal stock 866,565 over 40 replicas; selector bill 626,937,137,600. `cohort-transform.cpp` uses `stable_sort` for the cut gauges so the transcript is byte-identical across standard libraries; the cohort transcript hash is pinned as `cohort_record_sha256` and the retimed one as `new_record_sha256` in `RESULT.json`.

Prepared by Rohan Arun with Anthropic Claude assistance; Apache-2.0. Everything below is PR259's own description of the inherited construction.

---

# Multi-cut response-kernel condensation

**Conditional kappa = 142205877210807 / 200000000000000000 = 0.000711029386054035.**

This builds on pinned PR249 (`96495746c786d6d0339dbb38c7f553d4af3f88ed`) and extends the earlier 132-pair kernel construction. It raises the previous delivered 0.00071046520063283 by approximately 0.0794%. This is a modest checked exponent gain, not a claim of a huge jump or the latest leaderboard record.

The new mechanism selects simultaneous zero-response helper directions, shares donor lifts, repairs singular common frames with explicit nondegenerate subframes, and places compatible basis changes at four actual cuts. The result has 518 pivot entrances, removes 1344 raw rank units and 27772 initial reads, and pays every added basis gate and inverse. Complete bank stock is 867175.

## Reproduce

Requires Python 3.11+, SymPy 1.14.0, GNU g++ with C++17 and Boost headers. Install `g++ libboost-dev` on Linux, then:

```
python -m pip install -r requirements.txt
python verify.py --output ../multicut-replay
```

MinGW-w64 is supported on Windows. Use `--cxx /path/to/g++` and optionally `--boost-include /path/to/boost-header-parent`. The output directory must be new and outside the package. Allow several minutes and a few GB of RAM. No network, credentials, Lean or GPU is required. New mathematical computation is C++; Python orchestrates it and runs the original upstream emitter.

The default verifier checks hashes, regenerates pinned upstream data, compiles seven native checkers, emits the new word from the frozen candidate selection, and rechecks its complete semantics, geometry, bank assignment, finite invoice and exact exponent. It requires all 20107 local input columns in both directions, 23627 five-stage global columns, 911680 per-cut kernel equalities, all 3317400 bank assignments, exact chart identities, nonvacuous controls and all 47 strict outer inequalities. The bank label and mathematical receipts must match exactly; only elapsed time and runtime paths are excluded from comparisons.

`--snapshots-only` explicitly skips upstream source regeneration and records that weaker provenance mode in its certificate. It still executes all seven native checkers. Discovery scans are not rerun: inputs/candidates.json.gz is the complete frozen final witness, including actual cut positions.

## Scope and source handling

Retains the public all-size compiler, common weighted chart, restored-row, routing, prime, precision/recovery, complex symbolic correctness and analytic interfaces. These foundations are not independently reproved. The actual cancellation is over F2 payload; odd-prime address geometry is separate. This is not an unconditional multiplication theorem, practical benchmark or Lean certificate. The public eight-stage Python command is not claimed to be replayed verbatim on the modified word.

See PROOF.md, KERNEL-PROOF.md, BANK-PROOF.md, COPY-PROOF.md, FINITE-PROOF.md and REVIEW.md. Paths under lead/ or banks/ in research-derived proof notes identify the original evidence roles; the executable package uses code/, inputs/ and expected/. Native output logs can contain your chosen output path; they are not upload files.

Original public sources, licenses and attributions are preserved in vendor/. No personal byline, binaries or local machine configuration is included.
