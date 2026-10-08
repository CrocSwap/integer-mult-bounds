# Current result

The conditional saving is `kappa = 942293/500000000000 = 1.884586e-6`.
The [proof](../../artifacts/partial-swap-note.pdf) extends
[PR #10](https://github.com/CrocSwap/integer-mult-bounds/pull/10), pinned at
`62691e395a0458ce089a1c7b5d89e74291e95e29`.

Partial swaps give rank budget `Wm-2N+2L`. The selected binary triple producer
has dimensions `(25,23,57)` and compatible positive frames and carrier reuse.
Its common rational basis batches the paired boundary into widths
`25,7,25,25,32611`. The complex construction batches all internal residuals
in addition to its five macro classes.

The [certificate](../../certificates/partial-swap-network.json) records exact
moments, precision guard, finite basis combinatorics, and assembly margins.
The [producer checker](../../scripts/partial_swap_producer.py) regenerates
all selected graphs, label assignments, matchings, and internal histograms.
Generic common-basis existence and the tape/analytic interfaces are written
proof obligations, not consequences of the arithmetic checker.

The earlier [#10 proof](../../artifacts/batched-23-note.pdf) and
[patch](../../patches/batched-23.patch) remain baseline references, including
the Gaussian scaling correction. Older research pages describe earlier results.
