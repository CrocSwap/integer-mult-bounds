# Astra independent review — K492 emitter controls

Packaging note: the supporting `astra-*.json` and `astra-run-stdout.txt` files
named below are retained in this package's [`evidence/`](evidence/) directory.
The successful baseline/source-control emissions, command receipts, logs and
patches have also been copied there from the reviewer's temporary output.
References to the original temporary locations remain as execution provenance.
Personal checkout and local evidence directory prefixes in packaged JSON receipts
are normalized as documented in [`PUBLICATION.md`](PUBLICATION.md). Historical
receipt hash values below still identify the original bytes; the package manifest
identifies the published bytes. This review's selected #626 references are relative
to the historical source baseline, not the current upstream frontier.

Independent review on 2026-10-13, repository base `66849e1475c930fd7732b1a0067ffee7e1e95f60`. This reviews the locally authored `research/k492-emitter-independent-controls/independent.py` and `run.py`; it does not endorse any downloaded PR implementation. **Final repaired-code review and a separate harness rerun passed. No remaining blocking finding was identified within the stated eight-site finite structural scope.** The preliminary findings below are retained with their resolution.

## Positive findings

- The eight mutation anchors match exactly once in the pinned original emitter at the expected source lines. They reproduce the eight `emit.*` rows of `PROOF-NOTE-R.md` without duplicating #766's 14 assembly controls.
- Native helper widths are independently calculated by exact integer XOR elimination, checking basis independence and entrance containment. No floating-point arithmetic or production rank function is used.
- Owner families use a separately expressed coordinate formula. Complete `(stage,replica,helper)` coverage, whole-family uniqueness, route/spectator reconstruction, and endpoint-sorted occupied intervals supply useful independent structural evidence.
- Paid profiles are recounted from literal local-program climb/center events and exact idle remainders; scalar, Clifford, phase and theorem proofs remain inherited.
- The selected allocation's serialization order exactly equals call-order then helper-order. Thus the checker's independently generated sigma-stream order agrees with the emitter's allocation-stream order on this fixture. This was verified by directly reading JSON, without executing repository source.
- The donor parent `research/structural-gain/frontier-composition/global-replay/base/split-centres/GLOBAL-TEMPLATE.json.gz` has decompressed SHA-256 `7db047a427a7979d69e163c78a1e32bd445628fb86723e131a3138361355a9c3`, independently verified equal to PR626's archived `HOSTED.json.parent_template_sha256`. It is an exact retained payload, not a synthetic parent.
- The harness's cosmetic control compares the complete template and receipt after normalizing only `GLOBAL-TEMPLATE.version` and its directly derived `HOSTED.template_sha256`. It also compares the sigma artifact. This normalization is appropriately narrow.

## Findings requiring repair or explicit scope limits

1. **Missing proof-input bindings.** In the initially read 305-line checker, `all(...)` over `summary['source_artifacts']` accepts an empty object. Require the exact expected key set (one data-phase file plus seven files per provider), then require each digest. The registry's canonical/program/Clifford/adapter digest fields also need explicit checks. Merely comparing the embedded program does not bind every receipt's claimed input identity.

2. **Incomplete serialized-output coverage.** Initially, changing `recipe`, `exact_data_phase_recipe_sha256`, `adapter_policy`, retained per-call `pair`/`window` fields, async source schedule/call-order/plan links, or hosting limits/banks could survive a refreshed template digest. Compare all retained parent/call fields against their pinned originals, and check explicitly rewritten metadata. Otherwise narrow any “complete emitter semantics” description to the checked contract. Source window feasibility is distinct from checking unchanged expanded event order; it may remain an explicitly inherited obligation.

3. **Overly broad source-failure acceptance.** Initially, the harness accepted any terminal `AssertionError`/`IndexError` mentioning `emit_allcold.py`. This can mistake a different failure for the intended source control. Require the terminal emitter frame, exact source line and exception class, and save the failed source statement. Missing files, import failures, pin failures, or failures at another assertion must never count.

All three findings were repaired and independently re-read before the final run. Exact input inventory/provider links, retained parent/call fields, hosting/async links, and exact failure line/class are now enforced. New regression controls reject erased source inventory, changed input/artifact hashes, a changed retained recipe, an erased call window, and an erased async source schedule. The final version also checks summary call-order digest and bank counts, and validates all 112 port charts before reporting their Gram-entry count.

## Final review checklist

| Control | Intended observed outcome |
|---|---|
| `emit.R_from_providers` | `IndexError`, original emitter line 42 |
| `emit.roles_72R` | `AssertionError`, line 48; 35,424 differs from 36,288 |
| `emit.widths_range` | `IndexError`, line 42 |
| `emit.all_helpers_owned` | `AssertionError`, line 77 |
| `emit.physical` | Emitter succeeds; independent `emit.physical` rejection of 7,682 vs 7,670 |
| `emit.reserved_tableau` | Emitter succeeds; independent `emit.reserved_tableau` rejection of end 7,680 vs 7,668 |
| `emit.parent_R0` | `AssertionError`, line 93; retained parent stock gap 514 differs from 502 |
| `emit.version_label` | Accepted; only label and derived template digest differ |

The final review pinned repaired checker/harness hashes, reviewed exact input inventory and donor provenance, ran the final harness once into a fresh separate directory, and compared deterministic mathematical receipts with the implementation agent's run. The baseline `HOSTED.json` equals its archived counterpart; all eight original source mutations reach their intended result; the added semantic corruptions are rejected after output hashes are refreshed; cosmetic/recompression positives pass.

## Final execution and comparison

Command: `python3 -B research/k492-emitter-independent-controls/run.py --out /tmp/k492-emitter-astra-review-20261013`.

Observed UTC interval: `2026-10-13T06:14:35.026077+00:00` through `2026-10-13T06:15:18.676077+00:00`; wall time 43.65 seconds; CPython 3.13; exit 0; output `PASS_COMPLETE_EIGHT_EMITTER_SITE_SLICE`.

Reviewed and executed source SHA-256 values, checked unchanged after execution:

- `run.py`: `fbb04bc8c097b82db4a09af69ae62c1b7ab07f522a9726ff573ea64e485a9aa8`
- `independent.py`: `755f2c39697d33f2f2c431605dcdc59c7753e4cfae497d40482ab40b7d0f9016`

Results:

- Eight documented source controls: five failures at the exact original source line/class, two successful emissions rejected by the independent output-geometry oracle, one accepted changed-label control.
- Twenty additional semantic controls: 18 intended rejections after hash refresh, one accepted cosmetic label, and one accepted actual gzip recompression with identical payload semantics.
- Selected structural recount: 984 provider helper-frame pairs, 35,424 roles, 7,670 physical rows, 7,672 sigma charts, 596,848 exact Gram entries, 2,339 idle remainders, rank mass 520,704 and deficit 2,560.
- Fresh complete `HOSTED.json` equals the archived receipt as JSON. The template decompressed SHA-256 is `22b41c45fdac1dcc7495311fe701f4697219654843558785ed72fae91df531b0`, matching its receipt.
- Against `/tmp/k492-emitter-final`, `BASELINE.json`, `RESULT.json`, `SEMANTIC-CONTROLS.json`, and `INPUT-PINS.json` are byte-identical. `SOURCE-REVERTS.json` mathematical records are identical after excluding only each run's command object, which contains different absolute output paths, wall times and path-dependent stderr hashes.

Supporting evidence: `astra-run-command.json`, `astra-run-stdout.txt`, and `astra-receipt-review.json` in this directory; complete command, mutation patches, stderr/stdout and emitted outputs remain in `/tmp/k492-emitter-astra-review-20261013` for packaging by the implementation agent. `RESULT.json` SHA-256: `2ece1e706252c810df6e8a73d09dd66ae6c9b2b940c83049a7c7767aec6856e9`.

Keep these distinctions in the handoff:

- The maintainer already recorded a generalized R504 compatibility replay. This contribution does not reproduce the unavailable original `GlobalR/run504b` scratch fixture or its full 32-site reversion report.
- Eight emitter controls do not discharge the other 24 documented source sites. Related invoice/accounting evidence from #724 is credited; the R/R0 prose discrepancy is not new here.
- Complete source emission and finite structural checking do not independently re-prove native scalar/Clifford/phase identities, source allocation window feasibility, invoice/assembly inequalities, all-size compilation, physical hosting, precision/tape or analytic transfer.
- No selected-record change, new κ, full theorem proof, or human peer review is claimed.

No verifier source was edited by this reviewer. The final rerun executed the reviewed local harness, the pinned primary repository emitter and witness loader in temporary copies, and the separate independent checker. No pending-PR code was executed. No external publication, PR, issue, claim, or message to contributors was made.
