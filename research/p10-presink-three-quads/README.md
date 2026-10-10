# Four presink retimings and three rank-two kernels with 300-replica banks

κ = 7.69557449978832e-4

The exact admitted value is `769557449978832/10^18`. It improves the frozen four-retiming successor value `769556690340075/10^18` and PR320 at `1b37957d1520c80b6ea796bf418e52be5109c2d4`, which has `769553898621543/10^18`. This is a conditional finite construction under the same inherited theorem interfaces.

The complete PR320 snapshot is retained in `vendor/pr320`. The frozen four-retiming successor is retained in `vendor/predecessor`, with manifest `32d0bc5569f3bbdcbc488d88f06c688f07b905870db730dd63e1f0920ff627c7`. That predecessor changes four constructed ADD frames after early restoration and then reruns terminal sinks and reorder. The presink stage itself preserves scalar order; the final reordered word differs from PR320 because 24 equal-cost reorder anchors change from rank 18 to rank 19. Its own documentation records this distinction. The new stage in this package acts on that final reordered word and adds three disjoint rank-two quad kernels. Explicit width-100 banks with 300 physical replicas retain all three kernels without an extra rank-balancing entry. Published predecessors remain immutable.

Use Python 3.11 or later, SymPy 1.14.0, a C++17 compiler, and Boost multiprecision headers:

```sh
python -B verify.py --output /tmp/p10-presink-three-quads-proof --boost-include /path/to/boost
```

The output directory must be new and outside this package. The verifier checks the complete manifest before and after the run. It invokes the frozen predecessor's full strict verifier and transparently retains the unchanged return value of its final word stage. Only after all predecessor stages pass does it export and transform that object. It compares its bytes to the predecessor's saved final stream. It then admits the new actual word, both reflected ledgers, all five-stage F2 columns and dirty restoration, exact frame charts, every bank assignment, both independent moment engines with the full fallback, the finite invoice, and all 47 assembly inequalities. Adjacent grid points are rejected. No discovery, repinning, or source mutation occurs during this replay.

The new pivots are 7000, 7234, and 7349, each with three donors recorded in `stages/kernel2-selection.json`. Relative to the retiming predecessor, the local histogram change is `{1: +12, 2: +9, 3: -12}`. The actual word removes 32 compensation ADDs, adds 18 setup/restoration ADDs, and contains 336239 ADDs in 386904 records. All 8223 helpers are dirty and restored. There are 427872 banks per stage, literal stock 3291360, 12334500 enumerated role/replica/stage assignments, and no padding. The literal paid profile has 75078000 children and rank mass 328524000, leaving deficit 612000. The selector charge is 1951324377000; the counted primitive coefficient is 127531482262151501 (57 bits), and the signed payload prefix requires 98 bits.

Prepared with substantial OpenAI Codex assistance. Source authorship, Apache-2.0 notices, and earlier Anthropic Claude and OpenAI disclosures remain in the vendored packages. See `SOURCE.json`, `NOTICE.md`, and `PROOF.md`.
