# Independent endpoint-sweep check of PR727 owner masks

**Independent verification and scoped tooling evidence; no new κ or new optimization claim.** This checks Agastya Sondhi / TMM2009’s concurrent [PR727](https://github.com/CrocSwap/integer-mult-bounds/pull/727) at `71ba94c981477b3527ef21dd0f8140e795a7664d`. Its exact adapter and provenance/notice/proof are vendored byte for byte. The complete original PR626 checker, PR727’s transformed checker and a separately implemented **sorted interval-endpoint oracle** agree on the selected owner allocation.

The endpoint oracle uses neither bit masks nor per-coordinate occupancy sets. It sorts each owner’s nonempty intervals, rejects overlaps, sums lengths and checks that the final endpoint equals the occupied length. It reconstructs all **16,128** owner bins, the **280,592** occupied coordinates and the complete idle histogram for **35,424** helper roles. This independently corroborates PR727’s most important representation obligation using a different algorithm, rather than presenting another copy of the same optimization.

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. The accepted selected conditional bound is `51110230636731/31250000000000000 = 0.001635527380375392`, from #626 with #543. The selected record, actual assembly, source manifest and [maintainer review](../../docs/research/community-k492-review.md) were followed. Pending PR titles are not accepted frontiers. Existing suppliers, selected metadata and `upstream/` are unchanged.

## Reproduce

Python 3.11 or later, standard library only, from the repository root:

```sh
python3 -I -B research/owner-footprint-crosscheck/verify.py
```

Expected:

```text
PASS_OWNER_FOOTPRINT_CROSSCHECK roles=35424 owners=16128 exhaustive=21500 sequence_steps=6000 checker_controls=9 kernel_mutations=5 pin_controls=4 sweep_owners=16128
```

This verifies source pins before importing the vendored adapter, runs both complete checkers, compares their entire outputs against `OWNER-CHECK.json`, compares every internal occupied-cell mask with the original set, independently recounts every owner via endpoints, and runs the controls below. `-I -O -B` also passes: explicit exceptions preserve rejection logic. This does not authorize disabling assertions in the inherited construction pipeline.

For fresh complete-check timings on macOS or Linux:

```sh
python3 -I -B research/owner-footprint-crosscheck/benchmark.py --pairs 15 --out /tmp/pr727-independent-benchmark.json
```

Use a fresh output path. Both timed modes include the same source-admission harness. The candidate uses the **unmodified PR727 transformation and helper functions**; the reference executes the original PR626 source. Every complete receipt and diagnostic must match. See `VALIDATION.md` for results and limits. No timing threshold is imposed and no endpoint-oracle speedup is claimed.

## Different method and exact argument

For each owner, let the original checker admit integer intervals `[a_i,b_i)` within `[0,C]`. Ignore empty intervals because they contribute no cells. Sort by the left endpoint. Maintaining the last right endpoint `e`, an interval overlaps an earlier interval exactly when `a_i < e`, provided earlier intervals were disjoint. Otherwise add its length and set `e=b_i`. This determines the same union cardinality as a set of all occupied coordinates, without enumerating those coordinates.

With bounds and disjointness established, all intervals lie in `[0,e)`. Their total length equals `e` exactly when there are no initial or internal gaps. Thus `count == end` is equivalent to the original compact-prefix condition, including the empty case `0 == 0`. Its idle contribution is then exactly `C-count`. This is an all-finite-interval argument; tests verify its implementation and its agreement with the pinned checker on the stated finite domains.

The oracle is independent only for **footprint accounting**. It receives the same owner roles and capacity windows; it does not prove those windows physically legal or independently derive the helper widths. Chronology, physical families, native profiles and exact moments are still checked by the inherited complete checker. Finite replay does not prove the multiplication theorem.

## Completed coverage and controls

- Complete map: all 35,424 roles, all 16,128 owner bins (13,913 nonempty), 280,592 occupied coordinates, exact idle histogram, native-width/profile data, helper/family sets, paid profile and both rational moment endpoints. The full exact receipt and relevant internal state match. Rank mass remains 520,704.
- **21,500** exhaustive cases: every occupancy subset at capacities 0–7; every integer offset and width from -1 through capacity+1; every compact-prefix decision. A coordinate-enumeration oracle, actual transformed PR727 expressions and endpoint sweep agree on interval acceptance, rejection reason and cardinality/compactness. Invalid intervals are included, unlike a test restricted to legal intervals.
- **6,000** seed-89 sequential operations compare the actual set and PR727 expressions across capacities 48, 63, 64, 65, 127, 128, 129, 256 and 1024. Both accepted and rejected operations preserve identical states. This tests stateful sequences rather than isolated masks.
- Nine full-map perturbations: overlap, gap, negative offset, overflow, wrong width, family, copy or stage, and a missing role. The complete engines reject with identical diagnostics before receipt output. The endpoint oracle independently rejects the four footprint perturbations. Decoded roles are changed after parsing so these tests reach mathematical guards instead of stopping at input hashes.
- Five corrupted implementations are detected: wrong interval width, shifted origin, skipped overlap rejection, skipped prefix rejection and wrong idle remainder. Four input/source corruptions fail source admission. Output-path reuse fails without overwriting the receipt.

PR727 already supplied set/mask identities and its own controls. This contribution specifically adds a third endpoint-sort implementation, every-owner internal-state comparisons, invalid interval enumeration and sequential state tests, plus fresh complete-check measurements on two local Python versions. No exclusive priority or independent human review is claimed.

## Sources, coordination and scope

`SOURCES.json` pins all 17 original source/context files with SHA-256 and Git blob IDs; gzip inputs also have payload hashes. Four exact PR727 source/provenance files are separately pinned, including their remote Git blob IDs. These hashes identify immutable archived inputs; regenerated gzip container equality is not used as a mathematical identity. The original adapter, proof and notices are unchanged in `vendor/pr727/`.

Reviewed construction heads: #543 `2065fe4f72a914d907f1046603f5a36f17018535`, #622 `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`, #623 `e39a615ca601ce5d62abeb24f3fcdb8644ca1005`, #626 `660de893d27bb7abd1d5b01b1640207528a5c851`. No cold supplier reconstruction is claimed; archived PR622 native artifacts are reused.

OS assignment seed **89** selected verification engineering. Three candidate tasks, initial local claim and one evidence-driven pivot are recorded in `CLAIM.json`. No pinned coordination issue existed. PR727 arrived just after the initial queue snapshot through #725; the pre-submission refresh found it. The overlapping optimization was retired locally, and this package uses a distinct path and credits/replays PR727 directly. A pilot endpoint implementation was slower and is not promoted as a performance improvement. It remains useful as an independent oracle. Related #672 changes exact exponential arithmetic in the same checker; #662/#707/#709/#721 optimize different workloads. #675 and #724 audit different owner/accounting obligations. None is imported or claimed as independently verified here.

The full repository suite, supplier cold replay, controller/full 47-inequality assembly and Lean are outside this new package’s scope. Native algebra, common-label/mutable-source realization, pooled hosting/normalized residuals, uniform compiler, precision/tape/exact recovery and analytic transfer remain inherited assumptions. Source hashes and finite checks do not discharge them.

## Attribution and license

The mask optimization belongs to **Agastya Sondhi / TMM2009**, with the substantial OpenAI Codex assistance disclosed in the unmodified [PR727 notice](vendor/pr727/NOTICE.md). **Chafik Boukhalfa / chafreaky** supplied the PR626 independent owner checker and exact interval engine. **Jeremy Kothe / jeremykothe2** and the credited Claude Code contributors supplied the PR622 K-triangle construction and PR623 dispatch. **DreamingOfClouds**, **Rohan Arun**, **icekylinx**, **eumemic** and the cumulative supplier lineage retain credit through [the original notice](../complex-k492-owner-repair/NOTICE.md). Douglas Colkitt’s selected-source/review infrastructure supplies the accepted context.

This independent endpoint oracle, differential harness and replay evidence were prepared by **Brian / JoyboyBrian**, with substantial **OpenAI Codex assistance**. No delegated or independent human review was used. Apache-2.0; predecessor notices and AI disclosures are preserved.
