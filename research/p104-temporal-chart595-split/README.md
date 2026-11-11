# Conditional κ = 0.003643716168305 from a temporal split at frame 595

This candidate improves [#7145](https://github.com/CrocSwap/integer-mult-bounds/pull/7145)
by **.000000277661886**. Six timed gathers and four later injections split one
rank-nine helper into ranks one and eight, using two explicitly owned buffers.
One paid path changes from rank two to ranks one and one. All three direct CPython 3.14.7 checks passed. Final registered isolated
Python 3.12.16 replay passed all three commands and every frozen receipt field. No admission or selected-frontier change is claimed.

The final constructor also splits four ADD coefficients into two exact summands
each, preserving the existing 24-bit numerator compiler limit and charging all
four extra operations. The normalized word has 76,150 events:815 more ADDs,
4 SCALEs, 1 MOVE, 2 INITs and 2 CLEARs. Ownership is 57 labels / 60 lifetimes / peak 45.
[PROOF.md](PROOF.md) gives the exact identity, path chronology and scalar repair.

Concurrent [draft #7147](https://github.com/CrocSwap/integer-mult-bounds/pull/7147) at `4ca446706d4106176486235b9d7c66bd301b72ff` reports the higher preliminary κ = 0.003643989339627 from a different frame-237 split on the same #7145 source. At the 01:28:59 UTC snapshot, its forward/grid, physical, full caller and registered checks remained pending. This package supplies a distinct complete frame-595 result; it does not claim the strongest open headline. Composition of the two changes has not been tested.

## Sources and reproduction

The complete 33-file #7145 source at
`db8f31c4a1d9e191976e2c92951e6d2dea886a27` and complete 31-file #7143 method
reference at `9ff298bd6547299dc5b263873bf8a400909e5501` are retained with all
nested notices. REUSE.json authenticates six unchanged implementations;
temporal_construct.py is the retained construct.py under an explicit new name.
Candidate native SHA256:
`ecb1f56ba06dbaae424d0f94ad41c6d08f39f5f1f2fec348f2d0c9c9873c657f`.

```sh
git fetch --no-tags https://github.com/CrocSwap/integer-mult-bounds.git main
python3.12 -B scripts/research_package.py --package research/p104-temporal-chart595-split
```

The exact certificate, complete native and full caller commands compare every
frozen receipt. See [VALIDATION.md](VALIDATION.md) for actual status and
[APPLICATION.md](APPLICATION.md) for the complete cost substitutions.
The unchanged BIT cap leaves .000122973831695 headroom. This is one exact
construction; 4,250 of 7,660 paths were tested before the first positive, and the
remaining domain is unprocessed. Its invoice crossing is not a global optimum.

## Credit and remaining obligations

Ali Romman supplied the causal-history identity; CubeJerry the temporal and
verification methods; Matarener the kernels; Rohan Arun the enabling paid
endpoint source and signed caller; ToikY earlier chart 120 and price engines.
Credit Cinna Davis/1337isnot1337, Dugongue, DreamingOfClouds,
Douglas Colkitt/#7000 reviewers and all retained authors. Substantial OpenAI
Codex assistance; no subagents. Apache-2.0.

Five assumptions remain: native_all_columns, owned_erasure, compiler,
precision_tape, analytic_recovery. Independent human/formal review, maintainer
admission and compiled top-level execution remain open.

## Open next questions

Independently replay the timed vectors, long buffer lifetime and scalar-width
repair, then the full bill. Inspect the exact 24-bit assertion retained by the
compiler check. Refresh guidance and overlap before any new optimization.

[Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19520521).
