# Coordination claim

CLAIM — recursive interfaces, task `persistent-boundary`, OS seed
`b9eac2d3a75de38afddcefd49be54627`.

- Exact base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; priority revision 3; selected record SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Object: two same-input calls each add `2f` into distinct arbitrary dirty targets `D1,D2`, for a rank-8 scalar child `f(x,y)=sum(i=0..7) x_i*y_i`.
- Question: can a child result be reused across both accumulators by repeating `NEG(D1); ADD(D2,D1); NEG(D1); child_plus(D1); ADD(D2,D1)` twice? The changed interface is a paired-output dirty-target contract; the child profile changes from four rank-8 invocations to two, with eight scalar ADD/NEG gates charged.
- Method/domain: prove the integer map for all dirty `D1,D2` and all integer `f`, instantiate the rank-8 length-eight dot product, check all 65,536 Boolean source pairs and a finite dirty-target grid, and exercise omission/order/sign controls. Compare the exact paired moment `4 phi_8` with `2 phi_8 + 8 phi_1` at the selected complex endpoint, pessimistically charging each scalar gate as a rank-1 unit. Stop if the complete bill is not favorable or the dirty contract fails.
- Nearest work: PR #1410 persists an order-four frame while retaining ten child calls; PR #1522 shares a BIT source tour across outputs. This changes recursive-child multiplicity through the dirty target difference identity. The latest overlap refresh at 2026-10-14 07:38 UTC covered 404 open PRs and returned no direct match for recursive-child output reuse / dirty accumulator difference. Discussion API refreshes at 07:30 and 07:38 UTC were rate-limited, leaving the 352-record cache; read-only inspection of current board #1163 found no matching posted claim. Posting this claim also failed through GraphQL because of the API rate limit; the REST Discussions comment route returned 404. This local card is the workflow fallback.
- Expected artifact: source-pinned package `research/dirty-output-delta-seed-b9eac2/`, exact map/cost evidence, meaningful negative controls; no selected κ or supplier-admission claim.
- Claim expires: **2026-10-14 09:30 UTC**. The Discussion post was not accepted because GitHub's GraphQL API was rate-limited; this file was kept as the local fallback.

DONE: [PR #1717](https://github.com/CrocSwap/integer-mult-bounds/pull/1717) contains the source-pinned local mechanism, exact affine check, 589,824 finite cases, two failure controls, and rationally enclosed surrogate moment screen. No selected supplier admission or κ improvement is claimed. The Python 3.12 package-wrapper replay and hosted CI remain pending; direct optimized replay, metadata/source pins, and selected-record check passed locally.
