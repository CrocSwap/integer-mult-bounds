# Sources, direct inspirations and attribution

All PR links below refer to CrocSwap/integer-mult-bounds. Upstream author and license notices in bundled source are retained. No submitter name, email or credentials are included intentionally.

- [PR398](https://github.com/CrocSwap/integer-mult-bounds/pull/398), head `c3251c8f33fac9332fb3606c2dc0bd4f32de4615`: the exact R781 signed-prefix input used here, including its 25 target-prefix rewrites and unchanged phase receipts.
- [PR396](https://github.com/CrocSwap/integer-mult-bounds/pull/396), head `b7d56cd87f8e97c3c28cb150dc89995490ba6a0c`: entrance response-kernel gauges and the odd rank-one complement mechanism directly motivate the new entrance-space route. The contribution here is synthesis of larger/even/degenerate spaces, phase-correct two-sided normalization and their actual mixed-rank realization, not a claim to have invented response kernels.
- [PR376](https://github.com/CrocSwap/integer-mult-bounds/pull/376): R781 helper substitutions, frame repairs and bit lifetime reuse. The inherited baseline in PR398 uses its pinned `b07cf2f3fdffcbccca86c88a0c33b32dfce4bfe9` lineage. Latest reviewed head in this sweep is `2205b0973440091770ae2354377d2be8b1ed8790`; that newer head is not silently substituted into the input.
- [PR378](https://github.com/CrocSwap/integer-mult-bounds/pull/378): the far-retimed R783 ancestry (including PR365/374) of the R781 source.
- [PR377](https://github.com/CrocSwap/integer-mult-bounds/pull/377): compressed nine-stage E8 geometry, exact Clifford representatives, routes and finite invoice framework.
- [PR381](https://github.com/CrocSwap/integer-mult-bounds/pull/381): the unsplit nine-stage bit assembly, exact local checkers, paid moments and degree-two halving bridge.
- [PR390](https://github.com/CrocSwap/integer-mult-bounds/pull/390): positive-prefix restoration and full dirty-column replay, extended to signed prefixes in PR398.
- [PR387](https://github.com/CrocSwap/integer-mult-bounds/pull/387), [PR392](https://github.com/CrocSwap/integer-mult-bounds/pull/392), and [PR185](https://github.com/CrocSwap/integer-mult-bounds/pull/185): six-level ordinary bootstrap and slack refinement used in the final assembly.
- [PR384](https://github.com/CrocSwap/integer-mult-bounds/pull/384): carries the exact outer engine used by PR387. Engine ancestry includes PR315, PR144 and PR23; original headers and notices remain.

PR394/395 and [PR399](https://github.com/CrocSwap/integer-mult-bounds/pull/399) were reviewed for the free-sink/prewhitening/padding-fusion route. PR399 at `b974e481efd2f771cda2dcdd71c91f133793558f` is the frozen public benchmark. Its different cleanup bracket is NOT combined with this construction and its gain is not added. PR397 supplies a conditional Lean bridge, not the new finite witness here.

Essential supplier/compiler ancestry also includes PR352, PR363, PR373, PR370, PR375, PR266 and PR234. This package does not claim global optimality or literature-wide novelty. It reports a new finite witness and an explicit sufficient construction relative to the frozen inputs.
