# Attribution and exact source pins

Ali Romman prepared the finite-iterate optimum, shifted annular assembly,
proof and checks with substantial OpenAI Codex assistance. New work is
Apache-2.0. It is author-checked, not independent review of its sources.

Jerry Chen / CubeJerry's
[PR #7570](https://github.com/CrocSwap/integer-mult-bounds/pull/7570), head
`053c42c68165cf24fd4e8bc33c2b20d6ac3d399b`, supplies the
[half-grid framework, annular matching and sharp square-to-swap theorem](https://github.com/CubeJerry/integer-mult-bounds/blob/053c42c68165cf24fd4e8bc33c2b20d6ac3d399b/research/sharp-order-four-gaussian-rounding/proof/PROOF.md).
That full proof was read. The annular construction and connector cycle
are adapted here to arbitrary odd starting radii and prescribed iterate
identities. Its m=4 optimum is retained, not claimed as new. No CubeJerry
source code is copied; the local partner rule and separate arc generator
implement the cited mathematical construction.

Ali Romman's [PR #7699](https://github.com/CrocSwap/integer-mult-bounds/pull/7699),
head `2a5dcb314ccdfeed24bd86ec1f56f519eead56c1`, supplies the
[forced ring classification and finite-order lower framework](https://github.com/aliromman/integer-mult-bounds/blob/2a5dcb314ccdfeed24bd86ec1f56f519eead56c1/research/gaussian-radial-order-classification/PROOF.md)
and [exact coordinate, cycle and radical-comparison routines](https://github.com/aliromman/integer-mult-bounds/blob/2a5dcb314ccdfeed24bd86ec1f56f519eead56c1/research/gaussian-radial-order-classification/verify.py)
adapted in this package. The proof is source-relative and the checker
is not blind to that source. No predecessor module is imported.
The new step selects the first incompatible odd radius, handles the
central exception, and assembles a total map that attains its lower bound.

The [retained source credits](https://github.com/aliromman/integer-mult-bounds/blob/2a5dcb314ccdfeed24bd86ec1f56f519eead56c1/research/gaussian-radial-order-classification/CREDITS.md)
identify Ali Romman's global optimum and ring construction in
[PR #7696](https://github.com/CrocSwap/integer-mult-bounds/pull/7696),
the provider question in
[PR #7698](https://github.com/CrocSwap/integer-mult-bounds/pull/7698),
the earlier Gaussian contract in
[PR #6509](https://github.com/CrocSwap/integer-mult-bounds/pull/6509),
and Nick Petalas's exact-sum question in
[PR #7652](https://github.com/CrocSwap/integer-mult-bounds/pull/7652).
The present result does not count those prior bounds, contracts or
constructions as new. The source notices retain the earlier native and
tensor lineage, including its known limitations.

Douglas Colkitt and the repository contributors supplied the research
framework, task catalogue and package tools. SOURCES.json pins the
main-branch provenance at `e54523517d0f03e58352e647c403a5af3e525a57`.
The consumed unmerged proof and code commits are pinned above and are
not represented as ancestors of main. Full predecessor suites were not run.
