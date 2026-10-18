# Half-stage timing and evacuation on the PR2588 words

Complete finite admission and exact outer arithmetic certify conditional
**κ ≈ 0.001714270081226977**, exceeding
[PR2588](https://github.com/CrocSwap/integer-mult-bounds/pull/2588) by
**1.8041966731709573×10⁻⁸**. The exact rational claim is in `CLAIM.json`;
`evidence/FULL-RESULT.json` records the completed admission.
The maintainer-selected frontier is unchanged.

The contribution combines a new invocation order and complete owner allocation
with Jeremy Kothe's unchanged PR2588 words. For stages `s=0..8`, replicas
`r=0..73`, sort invocations by `(8*s+2*r+int(s==2),s,r)`; PR2588 uses
`(4*s+r,s,r)`. Recompute the original strict windows, realize the fixed whole
helper inventory, then run Philippe Van Velzen's PR2559 evacuation with
`EVMAX=24`, `44`, `48`. The donor/local-word mechanism is upstream work.

PR2588 changes the physical helper labels of two aliases but preserves the
width inventory. A per-provider, width-preserving bijection transfers our
allocation to its helper indices. Each call still supplies each of its 422
helpers exactly once, with unchanged time, owner, port, offset and width. The
original literal checker and full global replay remain acceptance gates.

The final idle profile is
`{1:21829,3:6495,5:612,7:172,8:49,32:31,48:26508}`.
The full paid profile is
`{1:1598251,2:420912,3:218283,4:79920,5:17928,7:5500,8:49,32:31,48:26508}`.
It has the same 4,816,512 rank mass, dimension 73, live stock 66304, physical
stock 66814, 666 calls and 2048 charged prefix bits as its predecessors.

The exact rational moment engine brackets the new complex root between
`0.001714270081226976852108` and `0.001714270081226976852109`.
The modern outer κ is separately admitted below that endpoint; the inherited
supplier's historical κ interface is not the final outer result.
The fixed local profile's coverage-law packing ceiling is between
`0.001743132415391` and `0.001743132415392`; this realizes at least
**98.3442259515%** of that complex ceiling. `packing_cap.py` reproduces the
exact rational relaxation in `evidence/PACKING-CAP.json`, using the existing
ceiling engine with idle ranks at most 51. The modern outer result is checked
separately, without applying the historical `a/(1+a)` map.

## Reproduction

The bounded standard-library verifier checks every whole-helper owner role,
the local words on all independent columns, the exact moment, claim/ledger
bindings and rejecting physical controls:

```powershell
py -3.12 -B scripts/research_package.py --package research/half-stage-evacuation
```

This bounded check uses a fresh temporary workspace on each invocation and
removes it on exit. To retain receipts or failure diagnostics, run
`verify.py --work /fresh/absolute/check` instead. An existing path is refused
without overwriting it. [Workspace regression and evidence](../owner-replay-workspaces/README.md)
cover repeated registered checks; the mathematical checks are unchanged.

Complete fresh admission (Python 3.11; NumPy 1.26.4, SymPy 1.14.0,
SciPy 1.15.3, mpmath 1.3.0), with a fresh work directory:

```powershell
py -3.11 -B research/half-stage-evacuation/full_replay.py --work /fresh/absolute/replay --fill research/half-stage-evacuation/evidence/SWAP-CANDIDATE-FILL.json.gz
```

The actual local run reuses only this session's fully admitted, unchanged
retained parent. Both changed-word native chains are fresh, including phases
and independent warp-recipe checks. `--reuse-from`, `--native-base` and
`--native-extra` validate exact source, status, word and phase bindings.
The changed owner construction, parent lift, rebind, discovery, strict global
admission, geometry controls, outer arithmetic and nineteen outer evidence
replays run freshly. Reuse never covers those changed obligations.

The first discovery stopped because the inherited checker pinned PR2530's
sixteen-target word. The exact PR2588 twenty-target checker was then installed;
discovery and strict admission both passed freshly. The correction and original
failed-stage receipt are retained in `evidence/CHECKER-COMPATIBILITY-REPAIR.json`.
The default full replay installs this matching checker before admission.

Construction search uses the vendored unmodified PR2559 scripts, with
`FILLPKG` pointing at prepared PR2530 inputs carrying the half-stage order.
Starting at `research/source-partner-residual-exchanges/evidence/CANDIDATE-FILL.json.gz`,
run `vendor/evac.py` sequentially with `EVMAX=24`, `44`, `48`, passing the
provider widths/paid-profile adapter described in `TASK.json`. This produces
`evidence/CANDIDATE-FILL.json.gz`. Then:

```powershell
py -3.12 -B research/half-stage-evacuation/reindex.py --source research/half-stage-evacuation/evidence/CANDIDATE-FILL.json.gz --out /fresh/swapped-fill.json.gz
```

Compare regenerated compressed artifacts by decompressed JSON payload.
Compression headers are not mathematical equality checks. The committed
immutable input files retain exact source hashes in the manifests.

## Evidence and limitations

`vendor/pr2588/` contains unchanged word, provider, dispatch and comparison
inputs and its matching independent checker at head
`8cd9dc88e24f062e2ca2fa7f4844a3d3319381fb`; it is not a new
local-word claim. The new allocation is in `evidence/SWAP-CANDIDATE-FILL.json.gz`,
with its complete order, exact profile and interval arithmetic beside it.

All 63 exact outer inequalities are positive. All 17 outer rejecting controls,
six geometry controls and nineteen outer evidence replays passed. Strict global
admission additionally rejected 114 admission controls, twelve bit supplier
controls and eight independent physical owner controls.

This is a conditional finite construction. Inherited all-size/compiler,
common-label/mutable-source realization, whole-call hosting, precision/tape,
exact recovery, analytic transfer, recurrence and bit-side assumptions remain.
No independent human review, complete multiplication theorem or global
packing optimum is claimed.

A follow-up single-helper concentration pass found zero moves on the
pre-reindex allocation. This is a scoped search observation, not a universal
packing barrier. The integer condition for a strict single transfer is
`destination_hole - helper_width < source_hole`; the full-bin evacuation
search can still escape such a local configuration.

## Open next questions

- **Jointly improve invocation priorities and evacuation.** Only the stage-2
  half-step order is fully realized here. First realize the stage-4 half-step
  screen result and rerun complete evacuation; a full literal allocation is
  the missing evidence.
- **Use coupled exchanges after single-transfer descent stops.** First solve
  small exact two-bin or cyclic reallocations under the same strict windows.
  A successful nomination still needs literal/global admission; no optimum
  follows from a failed neighborhood.
- **Improve the local helper assignment further.** First price and audit a
  complete changed word, retaining all new lifted-target and cleanup costs.
  This package inherits PR2588's assignment unchanged.

## Credit

PR2588 and PR2575: Jeremy Kothe (jeremykothe2), with AI assistance, for the
helper-label change, its complete words and the evacuation baseline. PR2559:
Philippe Van Velzen (philippeVV), with Claude assistance, for evacuation and
its search utilities. PR2530: zxv, with OpenAI Codex assistance, for the source
partner aliases and physical-rehosting pipeline. PR2462/PR2435, PR2436
(Tekalign), PR2322 (Vlado Vojdanovski), PR2226 (Cinna Davis) and the retained
native/global/outer authors keep all predecessor notices and attribution.
Douglas Colkitt supplies the exact interval engine used for independent pricing.

The timing order, its global realization, evacuation composition, helper-index
transfer and this certificate were prepared for mcorrigan with substantial
OpenAI Codex assistance. No delegated agents or independent human review.
Apache-2.0.
