## Result

This is a **scoped finite negative result** for one asymmetric P112 mechanism. For the exact ten-term shear `D=[X,XU]`, `T=[X(I−VU^T),XV]`, enumerate all ordered pairs of distinct Walsh characters in `U` and `V`, with the identity basis and four elementary unimodular basis shears `U←UM`, `V←VM^{-T}`. The 15,680 parameter tuples preserve `UV^T` and the exact all-pairs identity. Every tuple has the same pairing-rank profile `{8: 8, 9: 2}`, center invoice 82. Replacing the incumbent center invoice 64 gives an exact packing-ceiling upper endpoint `417137082181/500000000000000` (about 0.000834274164362), below the incumbent ceiling and the 5% gate.

No new supplier, κ, selected result, or universal rank-two floor is claimed. Source access, frames, adapters, restoration, hosting, precision and interface costs are waived in the optimistic ceiling. The result covers only the stated Walsh planes and five bases.

## Reproduction

```sh
python3 -I -O -B research/p112-walsh-two-total-seed6ed83d/verify.py
python3 scripts/research_package.py --package research/p112-walsh-two-total-seed6ed83d --check-only
```

Expected verifier marker: `PASS_P112_WALSH_TWO_TOTAL candidates 15680 profiles 1 best_profile {"8": 8, "9": 2} center 82 a_hi 417137082181/500000000000000 gate False`. The generic registered replay targets Python 3.12; local direct verification used CPython 3.14.7 because Python 3.12 is unavailable on this host.

## Overlap and attribution

PR #1197 (merged head `a0935afff6cc5540a582c5881bc8d5f98b587357`) leaves the coupled full-rank overlapping case open. Merged PR #1923 (head `0d33d6020aa50d383067510df78dcc0515bba4f4`) searches a fixed symmetric witness's Householder orbit; this package studies asymmetric Walsh-plane shears and nonorthogonal basis changes, with no claim that the candidate sets are disjoint. Open PR #2022 (head `92ee132d0baf07f7ddf0fbbcd12756be8429bbf7`) gives a broader floor and cost-40 witnesses for its fixed decoder; this package does not claim an optimum. The exact overlap scan at 17:53–17:55 UTC covered 364 open PRs and 680 Discussion records with complete pagination and no warnings; no matching Walsh-shear work appeared.

Assignment seed `6ed83d31ab93b3878e4fc74abdee2988`, track `complex-mechanisms`, priority revision 3; research base `ec8707299e2f40918f5f96cdab99ee49cdbabcf0`; selected-record SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`. Task and source pins are in the package. Prepared by Cinna with substantial OpenAI Codex assistance. Apache-2.0. No independent human review is claimed.
