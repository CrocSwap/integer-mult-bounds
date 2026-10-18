# Local research claim: jointly time-vary L253 and L254

**CLAIM — Complex mechanisms, OS seed `dee1ed1ab4a97fc6f4249d461a960b25`.**

- Base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; selected-record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Object: the selected PR1263 218-helper static complex word, restricted to gauges L253 and L254.
- Question: does a joint temporal schedule improve the complete scalar invoice after exact pricing of their shared ADD?
- Method/domain: exact dynamic programming over the ordered union of affected ADDs; each offset lies in `[-4,4]`, for both orientations. All transition scales and exit restoration are charged. All other events and gauges stay fixed.
- Predecessors: PR1350 supplies the L253 one-coordinate optimum and explicitly defers L253/L254; PR1376 composes a disjoint pair on the same word; PR1380 jointly prices a different pair on the older PR1094 word; PR1388 prices a different shared-ADD pair on PR1263.
- Expected evidence: complete scalar invoice, exact source pins, all-712-column replay, paid-profile check, and controls; no κ change is expected.
- Claim window: 2026-10-14 07:56–09:56 UTC. Intended experiment stop: 08:36 UTC.

Final pre-submission refresh at 08:10 UTC paginated all 415 open PRs and found no L253/L254 joint temporal match. Fresh public views of Discussions #1163 and #1167 showed no L254 claim; the local complete discussion snapshot also has no match. The overlap helper's network refresh failed because this installed `gh` does not accept its `--slurp` option and the authenticated Discussions API was rate-limited; this local claim is the documented fallback, not a posted claim.

## DONE — bounded construction

The exact `[-4,4]^2` joint program reaches 135,638 forward and 135,654
backward complex primitives, saving 364 in each orientation. It accounts for
all 215 union ADDs and the one shared source ADD at event 19427. The joint
minimum equals the independent composition's complete invoice; both offsets
are zero at the shared ADD. All 712 formal columns replay, the 192-bit charge
and paid profile remain unchanged, and four mutation controls reject. The
registered Python 3.12 replay and package metadata/source-pin validation pass.
The result is submitted in [PR #1732](https://github.com/CrocSwap/integer-mult-bounds/pull/1732).
The initial hosted check observation showed 61 check runs queued; none is reported green.
After a metadata update to the PR branch, its new head had no check runs yet. No global
optimum beyond the box or new κ is claimed. The public Discussion claim update
remains unavailable under the authenticated API rate limit; this local claim
records the same result and PR link.
