# Attribution and license

Prepared by **Ross Richardson (@RossRichardson)** with substantial
**OpenAI Codex assistance**, including design, implementation, mathematical
analysis, tests, documentation and automated verification. No independent human
peer review is claimed. This contribution is under the repository's
Apache-2.0 license; see the root `LICENSE`.

The original dyadic factor, structural validation, receipt schema, side circuit,
phase argument and cost ledger are by **Douglas R. Colkitt**, retained at
`d55bcd62ceb8f322bcf311a5a66e94c3ac7724f0`. The structural/charge checks in
`packed.py` are adapted from his `scripts/experiments/complex_centers.py`;
the baseline and proof sources are retained unchanged and pinned in
`SOURCES.json`. Upstream material retains its own source notices and license.

Related exact integer-packing verification work, inspected before this change:

- Curtis Dransfield / @Curtis-D,
  [PR752](https://github.com/CrocSwap/integer-mult-bounds/pull/752),
  `3603d8d9184995ae1cc67c0f5e01f02f3a1d634e`: quadratic-affine witness replay.
- @merramil, [PR778](https://github.com/CrocSwap/integer-mult-bounds/pull/778),
  `f015b04c74801fa330f818d178e809c760fb5469`: single-intersection Gram replay.
- @CubeJerry, [PR898](https://github.com/CrocSwap/integer-mult-bounds/pull/898),
  `521c86e7fd4d0fbd1ed4e0524aa26a1e45861477`: Leech-minor byte lanes.

This contribution applies the related injective-encoding principle to a
different exact obligation: the complete rectangular sparse gather/scatter
product against triple incidence, with an input-dependent signed radix.
No pending PR implementation is imported and no novelty claim is made for
integer packing itself.

Curtis Dransfield's [PR809](https://github.com/CrocSwap/integer-mult-bounds/pull/809),
`66cabb478385fbaa1a8060123cd57545d703d84e`, researches a basis shear of the same
historical center. It is a construction contribution; this verifier retains
the baseline factor and does not import or certify that PR's changed invoice.
The final overlap check also inspected Ross Richardson's
[PR937](https://github.com/CrocSwap/integer-mult-bounds/pull/937)
(`b303fed6dfe2066dcd78c0d8ed74d2a3b153ba72`) and
[PR947](https://github.com/CrocSwap/integer-mult-bounds/pull/947)
(`b6f6418bdcae748b267cea72a5949d551feb7bb2`). These change the historical
factor and classify a shear family, respectively; their construction/proof
code is not imported or replayed here.

The accepted frontier is credited in `community-frontier890-review.md`:
Chafik Boukhalfa's T21 composition, Jeremy Kothe's U8 work, Hao Yan's T16
mechanism, DreamingOfClouds' PR589 on eumemic's PR555, and their predecessors.
This package does not alter their result or establish new source priority.
