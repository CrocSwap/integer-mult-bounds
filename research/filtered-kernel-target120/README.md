# Frame-filtered collective kernels and target-prefix sharing

**Conditional kappa = 712074434532274423885827/1000000000000000000000000000 = 0.000712074434532274423885827.**

This combines a new frame-filtered response-kernel construction with PR266's early response pairs, PR268's target-prefix compression, PR263's 25 gate retimings and PR261's fixed-prime finite-level arithmetic. It improves PR266's 0.000711403723709732 by approximately 0.0943%. No gain is added as an estimate: the complete composed word is rebuilt and priced.

Our physical contribution is a 925-pivot kernel selection of total entrance rank 1762, versus PR266's 851 pivots and rank 1677. Instead of finding scalar relations first and hoping they share a frame, filter helpers by a common nondegenerate address frame first, then choose a response basis and expose its simultaneous dependent directions. Basis exchange and chronological donor sharing retain compatible alternatives. One selected collective kernel has eight pivots on 18 helpers in a common rank-11 frame; it is not a single-donor nine-helper star. The selection is a bounded search result, not an optimality claim.

All 217 target-prefix groups are rebound to the actual new word and their 246 dependencies rechecked. This removes 218 local recursive children and pays 275 additional scalar ADDs. The 25 subsequent retimings remove one further child. All charts, stages, selectors, payload bounds and costs are included.

## Reproduce offline

Requires Python 3.11+, SymPy 1.14.0, GNU-compatible C++17 and Boost headers:

```sh
python -m pip install -r requirements.txt
python verify.py --output ../filtered-kernel-target120-replay
```

Use a fresh output directory outside this package. On Windows use --cxx and --boost-include if necessary. The default regenerates pinned upstream sources, compiles nine native checkers and executes the exact rational retiming audit. Allow several minutes; no network, credentials, Lean or GPU is needed. The --snapshots-only option explicitly records weaker baseline provenance and is not the default.

Checks include every local formal column forward and inverse, all 23627 five-stage columns, selected prefix relations, actual chronological frames and COPY lifetimes, 1142 exact charts, all 9952200 bank assignments, the full finite invoice, two rational moment engines, eight ordinary levels, 47 strict assembly inequalities and adjacent-grid rejection. Saved expected receipts are compared only after execution. All three transformation word hashes and the complete package manifest are pinned.

Literal stock: 2599435. Selector cost: 1882890856800. Counted primitive coefficient: 188158356456648601 (58 bits). Payload: 98 bits. Row swaps cost four elementary operations; the largest newly checked chart uses 236 factors, below the retained 548 allowance. The complete normalizer ceiling remains 787.

## Scope

This is a finite construction and conditional exponent improvement under the retained public all-size compiler, common weighted chart, restored rows, routing, prime supply, precision/recovery, complex correctness and analytic interfaces. It does not independently prove those interfaces, an unconditional multiplication theorem, practical speedups or Lean certification. The displayed finite coefficient counts this recipe; larger inherited all-size constants enter the supplied cutoff formula.

See PROOF.md, DISCOVERY.md, REPLICATION-PROOF.md, REVIEW.md and NOTICE.md. Historical predecessor notes are preserved with their original counts; RESULT.json and fresh expected receipts describe this final composition. No personal byline, local machine paths or executable binaries are included.
