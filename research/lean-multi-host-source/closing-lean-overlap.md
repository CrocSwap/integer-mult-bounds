# Closing overlap review: PR513 and PR511

Read-only review completed 2026-10-11 UTC, following the closing snapshot
at `overlap-closing-refresh.json` in the contribution package. No GitHub
comments, publications or repository mutations were made by this audit.

## Exact evidence boundary

| PR | Inspected head | Changed files | Changed Lean files |
| --- | --- | ---: | ---: |
| [513](https://github.com/CrocSwap/integer-mult-bounds/pull/513) | `005dd3f4e3cba8d1761abc4ab391aaf6d14d6f73` | 20 | 8 |
| [511](https://github.com/CrocSwap/integer-mult-bounds/pull/511) | `79f7c03c7f820ab89955b75ef239cbaccc627e6e` | 17 | 4 |

Both API heads matched the requested pins. Each compare against main
`12a4934d15006e8c10f9b2264f13f8f341be802b` reports one added commit.
Both recursive Git trees are untruncated (162 and 158 Lean files,
respectively). All 37 changed files were fetched from the exact commits;
their Git blob hashes were independently recomputed and matched the tree.
All eight PR513 Lean SHA-256 entries also match its manifest.

The original API responses and fetched files were retained locally during
this audit. The shipped [URL/hash inventory](review-receipts/closing-overlap-fetch-manifest.json)
identifies the inspected files without requiring that local directory.
The review inspected the new theorem statements/proofs and source-binding
definitions, supporting theorem interfaces, README/provenance and manifests.
It did not independently rebuild these Lean 4.21.0 packages or reproduce
their advertised build receipts. Their kernel-check claims remain their
supplied evidence, distinct from this source review.

## PR513: meaningful generic overlap, different concrete target

`SequentialCompleteBank.sequential_complete_bank`
([exact source, line 82](https://github.com/CrocSwap/integer-mult-bounds/blob/005dd3f4e3cba8d1761abc4ab391aaf6d14d6f73/research/lean-sequential-bank-bindings/SequentialCompleteBank.lean#L82))
composes completed local words. Its arguments explicitly include:

- An arbitrary word for each role and an endpoint premise quantified over
  every bank state and every remaining state (lines 84–89).
- One exact common chart and a supplied projector for each role.
- A disjointness premise and a complete partition of the identity
  (lines 90–91).

It proves the full bank swap and chronological evolution of the remaining
state. `completed_words_separate` at line 51 separately proves the product
endpoint composition. The implementation correctly reconciles its two list
orders by reversal. These overlap with the generic completed-word,
arbitrary-dirty-state, common-chart and disjoint-projector principles used
by our abstract framework. The contribution should claim no novelty for
those principles. Five supporting modules are acknowledged as unchanged
reuse; the three additions are this composition adapter and two selected
five-stage source bindings.

The source bindings concern main's `research/five-stage-gen4-banks`, with
dimension 120, local dimension 24, 1,760 ports and 60 physical replicas.
They do not concern the PR442 R747 invocation:

- `CurrentFiveStageBankAddressFactor.address_factor`
  ([line 26](https://github.com/CrocSwap/integer-mult-bounds/blob/005dd3f4e3cba8d1761abc4ab391aaf6d14d6f73/research/lean-sequential-bank-bindings/CurrentFiveStageBankAddressFactor.lean#L26))
  proves the factor-order identity `route (d*tau) N = route d (N*tau^-1)`
  for supplied group laws and normalizers.
- `CurrentFiveStageBankSourceSchedule.lowerStage` accepts the local record
  list as an argument (line 101). `NormalizerFactors` accepts its matrix
  factors (line 162). `chronologicalWord` accepts cover enumeration and all
  local stage/idle/bridge/terminal words (line 191).
- `replica_major_stage_word`
  ([line 204](https://github.com/CrocSwap/integer-mult-bounds/blob/005dd3f4e3cba8d1761abc4ab391aaf6d14d6f73/research/lean-sequential-bank-bindings/CurrentFiveStageBankSourceSchedule.lean#L204))
  connects those supplied words to the literal replica-major stage order.
  It does not supply their physical endpoints or their matrix entries.

The source header explicitly says that no matrix, finite-record digest,
physical endpoint, arbitrary-dirty provider or cost is certified here
(lines 8–11). Its provenance also distinguishes the selected transformed
local record list from the raw producer list and keeps the complete
physical endpoint as a supplier obligation. This is a precise, appropriate
boundary, not evidence of an error in PR513.

No changed file provides the concrete 19,002-event PR442 word, the computed
987-row symbolic endpoint, its chronological nine COPY/nine ERASE guards,
the 944 actual frame matrices, the 747 hosted owner/chart assignments, or
the 172-family original-bank ownership/refinement. Those are precisely the
additional obligations pursued by our Task B. PR513 therefore does not
already discharge that selected concrete target. Its generic algebra can
be cited as overlapping existing work; importing it would not remove the
remaining source-specific proof work.

## PR511: checked counting machinery, no target overlap

`BinaryCountDispatcher.count_run`
([line 249](https://github.com/CrocSwap/integer-mult-bounds/blob/79f7c03c7f820ab89955b75ef239cbaccc627e6e/research/lean-binary-count-dispatcher/BinaryCountDispatcher.lean#L249))
proves termination of an explicit seven-state two-tape binary dispatcher
within the carry-pass read receipt plus `2 * input.length + 1` transitions.
`counter_value` at line 261 gives
`(initial value + input length) mod 2^width`; empty input, zero width and
overflow are within that modular statement. Its four changed Lean files
are `BinaryCarryIncrement`, `BinaryCountDispatcher`, `CarryTape` and
`CarryTapePass`.

The two external foundations are pinned to PR488
`edd3102b415df5b9d6f633ac0a4dedcf69c58525`; their identities are recorded in
`FOUNDATIONS.json`. This audit did not re-fetch/rebuild those unchanged
foundations. The package explicitly leaves actual source prelude/caller,
width allocation and Plan/Budget composition open. It has no frame,
whole-residual hosting, physical owner or PR442 invocation endpoint result.

## Bounded conclusion

Neither of these exact new heads resolves the selected concrete PR442
obligation. PR513 materially reinforces the need to describe the useful
contribution as discharging concrete supplier premises, not discovering
generic conjugation, partition or completed-word composition algebra.
PR511 adds independent compiler-helper work. This conclusion is limited to
the pinned changed files and their exposed interfaces; it is not an
exhaustive novelty claim over historical branches or external repositories.
Neither package establishes a new kappa bound, and neither changes the
unestablished status of PR448's advertised split-stream gain.
