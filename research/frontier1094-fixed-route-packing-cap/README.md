# Selected #1094 fixed-route packing cap

**Scoped exact upper bound, no new κ.** For the selected local word and the selected data-route child inventory, any whole-helper owner reassignment that hosts into those same children has complex primitive saving `a < 0.001682094870065`. Under the retained balanced conversion `κ = a/(1+a)`, this gives the planning cap `κ < 0.001679270178313`, at most **0.395178%** above the selected `0.001672660197076918`. The selected κ is at least 99.606% of this favorable cap. This does not assert an attainable packing or the exact seven-step outer-grid ceiling.

## Fixed inventory and proof

The source-bound route is `research/direct-delivery504-global/inputs/data-base/work/complex-nine-native/DATA-PHASES.json`. It is pinned by the selected `SELECTED-SOURCE.json` and byte-identical to the same member in `selected-replay.tar.gz`. The verifier recomputes GF(2) rank from every `orthogonal_axes` list. Each of the 112 port recipes has two rank-0, six rank-8, four rank-16, four rank-32, and four rank-48 children. Thus **no existing data-route child has rank above 48**. The selected manifest also pins the [parent T16 hosting proof](../gauge44-slots-t16/hosting/PROOF.md): a pending-child group `g=(owner replica, child, port)` has capacity `C_g`, hosting occupies a prefix of total width `U_g`, and its remaining suffix has rank `C_g−U_g`. The selected plan explicitly lifts that eight-replica geometry to sixteen replicas. The verifier checks this premise against the selected sources rather than the proof text alone. All 288 `(owner replica, child)` window entries of the selected `PLAN.json` have capacity equal to the route rank of that child at every port (the two route children of rank 0 have no window). Every one of the 69,120 hosted helpers in the selected `OWNERS.json.gz` lies in its group's window. In each of the 32,256 groups, the hosted offsets tile `[0,U_g)` with `U_g ≤ C_g`. The remainders `C_g−U_g` reproduce the replay's idle profile `{1:2276, 3:377, 7:7, 48:4866}` exactly. Therefore a remainder after whole-helper hosting into one of these fixed children has rank at most `max C_g = 48`. This is the extra premise beyond [the predecessor's rank-51 relaxation](../complex-local-word-ceiling/README.md). Axis transfer or repartitioning across child boundaries can make a rank above 48 without changing the total parent space, and is excluded.

The selected replay's `spec_sha256` binds the T16 `SPEC.json`; its `data.plan_sha256` binds `PLAN.json`. The plan and replay give 144 calls, 14,336 live families and the same complete profile. Subtracting the replay's idle profile and dividing by 144 gives the local profile per call `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`. The complete rank mass is `1,041,408 = 72·14,336 + 64·144`; local mass is `5,586·144`, so idle mass is `237,024 = 4,938·48`.

For `0<a<1`, each idle child of rank `r≤48` costs `(r/73)^(1-a) = r·r^(-a)·73^(a-1) ≥ r·48^(-a)·73^(a-1)`. Consequently the full normalized complex moment is at least

`[144 Σ_r local_r (r/73)^(1-a) + 4938 (48/73)^(1-a)] / 14336`.

This is a favorable mass relaxation; the hypothetical 4,938 rank-48 idle children are not asserted to fit the actual owner windows. The expression increases strictly with `a`. A separately written standard-library rational interval engine encloses logarithms by a reduced-argument atanh series and exponentials by a Taylor series with rational remainder bounds. It certifies the strict root bracket `0.001682094870064 < root < 0.001682094870065`.

The same engine independently reproduces the predecessor's rank-51 bracket `0.001690054109088 < root < 0.001690054109089`; its implied κ cap is `0.001687202645326`. The bit primitive lower exceeds the complex cap, so it does not bind this planning comparison.

Two merged results have narrower or different domains. [PR1276](https://github.com/CrocSwap/integer-mult-bounds/pull/1276) bounds within-group idle-axis repartitions while allowing child ranks up to 51; [PR1387](https://github.com/CrocSwap/integer-mult-bounds/pull/1387) sharpens a selected idle-axis relaxation and gives a counterexample to an inherited admission check. Those analyses do not cover arbitrary whole-helper reassignment among the *unchanged* selected child bins. Their tighter numerical ceilings must not be combined with this cap without satisfying both scopes. The counterexample is also a reason to treat any proposed owner or axis edit as requiring fresh semantic admission. The open [PR1685](https://github.com/CrocSwap/integer-mult-bounds/pull/1685) shows that at `a=0.00169`, at most 1,603 of the 237,024 idle mass units may sit at ranks ≤ 48. It leaves legal residual groups as its next question. This package answers that question for the fixed-route class: every legal remainder has rank ≤ 48, so the fixed route cannot reach `a=0.00169`, consistent with the rank-48 root above. Overlap was refreshed on 2026-10-14 at about 05:50 EDT (446 open PRs, 418 discussions).

## Reproduce

From the repository root:

```sh
python3.12 -I -B research/frontier1094-fixed-route-packing-cap/verify.py
python3.12 scripts/research_package.py --package research/frontier1094-fixed-route-packing-cap
```

The first command takes about 4 seconds on the local macOS host. It checks source hashes; selected record, review and replay paths; manifest, archive, spec, plan and owner-map bindings; all 112 recipes' axes and ranks; window capacities against route ranks; the selected owner map's prefix offsets and idle remainders; profile splitting and the PR1012 coverage identity; exact endpoint signs; `RESULT.json`; and five failure controls, each of which must fail at its intended check. The controls reject a changed rank without matching axes, a rank-49 route child, a mass-preserving change to the local word applied consistently to plan and replay, a window capacity raised to 49, and an overlapping hosted offset. Pinned sources are unchanged, so the selected cold replay is not part of this package check.

## Scope and limitations

- The fixed data-route child boundaries and existing hosting operation are essential. Repartitioning axes across children or a redesigned route making rank-49, 50 or 51 children falls under the predecessor's broader relaxation and is outside this bound. Changed local words, port counts, stage templates, center charges, coverage laws and outer recipes are outside it too.
- The argument allows fractional ownership and ignores timing, capacity and helper indivisibility. These constraints can only worsen the moment inside this fixed-inventory model.
- The selected conditional theorem still inherits all-size/compiler, common-label/mutable-source, whole-call hosting, precision/tape, analytic and bit H1–H5 obligations. This package verifies a narrower arithmetic upper bound, not a multiplication theorem or a new construction.

## Open next questions

1. **Can fixed-inventory capacity sharpen the cap further?** The mass relaxation puts all 237,024 idle units in rank-48 children. A first step is a source-bound linear relaxation using the selected route's per-child capacities and helper-width stock, with every call and owner window explicit. The blocker is a compact, independently replayable capacity model; the selected owner verifier can provide a positive fixture.
2. **Can a redesigned data route create rank-49 through rank-51 idle children without raising other charges?** Such a route would evade this fixed-inventory cap and move toward #1240's rank-51 cap. A first step is one exact route edit with a complete new child inventory and controller invoice. The archived route is fixed in this result.

## Credit

Douglas Colkitt's [complex-local-word-ceiling](../complex-local-word-ceiling/README.md) supplies the rank-51 model and coverage-law application; PR1012 supplies the coverage identity. Rohan Arun's #1094 and Jeremy Kothe's T16 lineage supply the selected word and packing. The selected review credits the underlying data route, controller, bit supplier and outer composition. Prepared by Josie Elliston with substantial AI assistance: drafted by OpenAI Codex (offline session 14 of a donated overnight run), then reviewed, fixed and published by Claude (Anthropic). Claude added the source-bound capacity and offset checks and corrected a control that had been rejected for the wrong reason. No independent human review is claimed. Apache-2.0.
