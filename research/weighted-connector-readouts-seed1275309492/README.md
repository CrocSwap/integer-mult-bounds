# Exact weighted optimum for a five-source dirty connector

**Completed finite weighted interface construction; no selected κ change is claimed.**

## Result

Use the fixed five-source interface from [universal-connector-boundary](../universal-connector-boundary/README.md). There are five arbitrary dirty source bits `x0..x4`, one arbitrary dirty connector bit `z`, and 31 arbitrary dirty target bits `ym`, one for every nonzero mask in `F2^5`. A source call `Bj` performs `z ^= xj`; a target call `Am` performs `ym ^= z`. Every call preserves its non-target data, the connector and targets must be restored to their required endpoints, and a legal schedule cannot depend on the bit values.

The complete leaf prices are the pinned fixture's nonuniform vector

\[
  c(B_0,\ldots,B_4)=(1,4,10,16,28),\qquad c(A_m)=1\quad(1\le m\le31).
\]

The exact minimum weighted leaf bill is **182**. The pinned predecessor's displayed 12-source-call universal word repeats `B2`, so its invoice is `2+8+40+32+56+62=200`. Swap labels 0 and 2 throughout that word. Prefix-difference coverage remains all of `F2^5`, but the repeated pair now belongs to cheapest `B0`: the source invoice becomes `4+8+20+32+56=120`, and the 31 targets still use 62 calls, for a total of 182. The root word still has 74 fixed-width query records, the same five source and 31 target operators, and the same peak borrowed-row depth. Thus the leaf saving is exactly 18, with no uncharged new primitive or free source broadcast.

There is a second schedule at the same optimum. The 10-source-call word in the predecessor certificate covers every mask except 21. All five source operators occur twice, costing 118. Every target except `A21` is read twice; `A21` is read four times at boundary slots `[0, 1, 6, 8]`, for a target invoice of 64. Its full invoice is also 182. This exposes the trade directly: one can pay an extra pair of cheap source calls or an extra pair of unit-price target readouts.

## Exact lower bound in the stated model

For an arbitrary dirty connector, every used `Bj` has an even call count; because the requested set contains all 31 nonzero masks, every `Bj` is used at least twice. Every target `Am` likewise has an even count of at least two. Therefore the baseline invoice is

\[
  2(1+4+10+16+28)+2\cdot31=118+62=180.
\]

The source-call count is even. It cannot be below ten, and eleven is impossible. In the **10-call** case, each `Bj` occurs exactly twice. The pinned complete census of 945 canonical five-source paths has maximum prefix-difference coverage 31 of 32 masks. Since zero is always covered and the output set contains every nonzero mask, at least one requested nonzero mask is absent. Two readouts cannot realize it, so that target needs at least four `Am` calls. At unit target price this adds at least two, giving 182.

In the **12-or-more-call** case, after the mandatory two calls per source, any extra restored source work costs at least `2 * min_j c(Bj) = 2`. Target work is at least 62, so this case also costs at least 182. The relabelled 12-call word attains the bound. These cases exhaust legal source lengths, proving the exact optimum for this fixed mask family and price vector. The inherited 945-path computation is rerun before this package verifier; its two enumeration methods and dirty-input controls are pinned and attributed in `SOURCES.json`.

The 10-call and relabelled 12-call schedules are each replayed on all 37 basis coordinates of the complete dirty state. Since the circuit is linear over `F2`, equality of those columns proves the requested linear transformation for every choice of dirty source, connector, and target bits. The tests also reject an under-read mask-21 output, a removed `B0` call that leaves the connector unrestored, and the valid but over-budget repeated-`B2` control.

## Cost boundary and relation to the selected result

The prices are the complete leaf-call prices in the exact five-source fixture; preparation of all 46 primitive operators is unchanged. All schedules use 74 root records with the same fixed-width role labels, all five sources and all 31 targets, and the same maximum factor depth, so input admission, coefficient preparation, tape capacity, instruction reads, root dispatch, and borrowed-row capacity are unchanged in the model. The only invoice change is replacing two price-10 `B2` calls by two price-1 `B0` calls. The resulting 182 bill also beats the fixture's separate column-star and row-star bills (278 and 1950). These are complete abstract interface bills under the pinned fixture, not physical runtime measurements.

This refines selector card `connector-alphabet-change` with `scope_status=changed`: the operation alphabet and source count remain fixed, and the changed hypothesis is heterogeneous complete call prices. The full 09:17 UTC Discussion refresh returned #1579, an expired claim for the all-n minimum-query/readout bill with unequal readout prices. It explicitly leaves the global unequal-price optimum open; this package gives one exact five-source optimum under unequal complete **source leaf** prices and unit target-readout prices. Open PR #1526 is the closest price-sensitive circuit result, but treats paid root scaling in a signed characteristic-zero 3x3 connector. The other nearby scopes are #1707's common-A broadcast, #1708's centre-path fanout, #1739's rank-one source transition, #1155's batch restoration coalescing, and #1522's dyadic BIT source tour. Their exact states, heads, and scope distinctions are recorded in `SOURCES.json`; the live weighted-path phrase scan found no matching open PR.

The current selected record has SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32` and conditional `kappa=836330098538459/500000000000000000`. Its maintainer review is `docs/research/community-batch1099-review.md`, selected source manifest is `research/community-frontier1094-audit/SELECTED-SOURCE.json`, assembly certificate is `research/community-frontier1094-audit/ASSEMBLY.json` (SHA-256 `1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045`), and reproduction command is `make frontier1094-verify`. The review retains the inherited finite construction assumptions and does not claim a full Lean multiplication theorem. No occurrence of this weighted five-source interface in that selected supplier, nor a transfer to its recursive moment, is established here; the selected κ is unchanged.

## Reproduce

From the repository root with Python 3.12:

```sh
python3.12 -I -O -B research/universal-connector-boundary/verify.py
python3 scripts/research_package.py --package research/weighted-connector-readouts-seed1275309492 --check-only
python3.12 scripts/research_package.py --package research/weighted-connector-readouts-seed1275309492
python3.12 -I -O -B research/weighted-connector-readouts-seed1275309492/verify.py
```

Expected final lines:

```text
PASS_UNIVERSAL_CONNECTOR_BOUNDARY pairings=945 max_coverage=31 queries=74 leaves=182
PASS_WEIGHTED_CONNECTOR_READOUTS optimum=182 old_repeated_B2=200 saved=18 schedules=2 dirty_bits=37 root_queries=74 controls=3
```

## Open next questions

Does any source-bound selected supplier expose this same five-source all-mask interface with these complete heterogeneous call prices, or an analogous price vector? A useful next step is to inspect one pinned call family, extract every source and target call's complete price, then apply the same 10-versus-12 lower-bound split. Until such a supplier occurrence and moment transfer are shown, this remains a local interface improvement.

## Credit

Prepared by Cinna Davis. Substantial OpenAI Codex assistance was used for overlap review, scope refinement, weighted lower-bound derivation, schedule construction, exact replay, packaging, and writing. No subagents or independent human review are claimed. New work is Apache-2.0; predecessor attribution and source-specific notices remain pinned in `SOURCES.json`.
