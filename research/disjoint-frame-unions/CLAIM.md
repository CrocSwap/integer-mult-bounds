# Verification engineering, seed 88

- OS assignment: `secrets.randbelow(100)` returned **88** on 2026-10-13.
- Base: `2921874911956718fcaaaf9396fe8267b3cfa9f0` (freshly fetched main).
- Claim: 2026-10-13 16:44 UTC. Expected finish: 17:20 UTC (13:20 Eastern),
  reserving the final quarter for verification and handoff.
- Object: the historical `DisjointTensor.frame_data` target-coordinate unions.
- Method: propagate exact unions along the same reverse DAG traversal as the
  unchanged reachable-target bitsets. Compare all three returned maps with
  the original, run both frame orientations, and compare complete certificates.
- Deliverable: additive opt-in adapter, differential/negative controls, pinned
  sources, paired fresh-process timings, and one focused tooling PR; no new kappa.
- No pinned issues existed; the two open issues were unrelated. Claim is local.

Initial narrow candidates were Fano-completion reachability, subset-core ledger
replay, and point-cancellation neighbor checks. Their complete certificates all
finished below 0.25 seconds, so none justified optimization. One evidence-driven
pivot selected the disjoint-tensor frame traversal: profiling the actual complete
historical h=26 audit spent 2.34 of 8.53 instrumented seconds in `frame_data`.
These exploratory instrumented timings are not the benchmark result.

Seed 88 also fixes randomized topological-DAG cases, output permutations and
mutation positions. The object and mechanism distinguish this contribution from
existing optimizations; the seed is not itself a novelty claim.

Overlap review read the 714-open-PR snapshot through #1019, the review ledger,
selected #942 certificate/review/construction, local claims and relevant negative
results. #950 considered and declined this traversal, choosing central-factor
packing instead. #863 and #981 change historical root contraction/traversal
choices; neither changes `frame_data`. #756 changes balanced-Fano enumeration,
#778 changes single-intersection Gram construction, #976 changes historical
rational rank, and #1006 changes T37 occupancy. None supplies this code.
No closed mathematical search is reopened.

Current selected conditional kappa at this base is 0.001661960547713947 from
#942, with #890/#869/#870/#858 ancestry and unchanged #589 on #555. This tooling
contribution concerns an older finite supplier and does not alter that frontier
or its inherited all-size/compiler, realization, hosting, precision/tape,
analytic or bit-interface assumptions.

## Result

Completed: the complete historical audit is 1.435577x faster in five alternating
fresh-process pairs, with byte-identical complete receipts in all ten runs.
All map entries/order, two physical orientations, independent BFS graph cases,
and failure controls pass. `make verify-tests` passes 661 tests in 96 modules
plus 20 patch checks. See README.md, BENCHMARK.json and VALIDATION.md.
Final review found no competing frame-union implementation among 737 open PRs
through #1042; #1029/#1041 are distinct U8 phase-recipe tools. No coordination
issue was pinned. Source exploration ended before the final verification and
handoff phase. The only additions are this optional package.

Submitted contribution: [PR #1044](https://github.com/CrocSwap/integer-mult-bounds/pull/1044).
