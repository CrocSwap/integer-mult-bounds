# R715 kernel, target mixing and eight-replica whole hosting

Conditional κ = **0.001292099559442278**, or
`646049779721139 / 500000000000000000`.
This is 1.4180932604% above PR458. The bit supplier binds:

- bit c = `0.001293771240692396056124`;
- unchanged paid-adapter complex b = `0.001297203880559577927527`.

Starting from PR463's published R715 word, this package reconstructs 109
shared-donor pivots of total entrance rank 120, 56 disjoint target mixes,
60 single-gate frame changes and the 14 paired retimings from PR467.
A frozen selection pools eight replicas. All 62,920 helper occurrences stay
whole on one idle physical family; there are no helper banks or residual
splits across physical families. The live stock is 9,600, with 9,609 physical
families including the private-centre reserve.

The larger physical-family growth bound is charged explicitly: 804 prefix
bits are charged at 832, and the 2,468-bit three-level coefficient at 2,496.
The complete bit row coefficient remains 19,431, below the retained 20,161
contract. Both rational moment engines, six bootstrap steps, all 47 strict
outer inequalities and next-grid/invalid-parameter controls are mandatory.

## Reproduce

Install the unchanged `research/e8-r740-replica32/parent436/requirements.txt`
and a C++17 compiler with Boost headers, then run:

```sh
E8_REPLAY_PHASES=1 python -B research/e8-r715-whole-hosted/verify.py /absolute/new/output
```

Set `BOOST_INCLUDE` if Boost is outside the compiler's include paths.
The default rebuilds the full corrected PR458 composition before all new
checks. `--quick` only skips the inherited PR443 exhaustive controls.
`--parent-output /absolute/completed/pr458-output` explicitly reuses a
completed, manifest-matching parent and emits a different receipt status;
it does not claim a fresh full parent replay.

New checks include the exact frozen reconstruction; all 955 local columns;
independent C++ legality and 1,915 eleven-stage formal columns; record and
mixing mutants; 958 positive Gram frames; exact shared target labels; 11
residual isometries; 3,396 nested/reflected projector pairs; all 9,065 unbanked
global columns; 1,320 data routes; every whole owner/window/slot/remainder;
1,726,296 renamed instructions; a separate physical-prefix traversal;
22 global mutations and 24 omitted-bridge controls. Source inventories,
package hashes and exact expected results are enforced.

## Scope

This remains conditional on the inherited bit/Gaussian compiler,
common-frame mutable-basis and target-label realization, whole-call
correlated-helper hosting, compressed-window, restored-work, common-grid
and tape, precision, row and analytic contracts. The paid two-sided complex
adapters from PR458 are retained and fully charged. No cross-family residual
factorization, unconditional multiplication theorem, new Lean theorem or
κ = 1 result is claimed. The selected kernel and pooling are not claimed
optimal. The two/four/eight-replica screen selected eight for its exact rate.

See PROOF.md, SOURCE.json and NOTICE.md for the argument and attribution.
