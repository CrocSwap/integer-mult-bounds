# Productive-helper baseline orientation

For the current selected productive-helper certificate, run from the repository root:

```sh
python3 -B scripts/research_selected_baseline.py
```

The command first calls the existing selected-record checker on the entire
source closure and proof supplements, then reports the exact budgets recorded
in the certificate. `PASS_RESEARCH_BASELINE_BINDINGS_ONLY` means source binding
and metadata consistency, not a native replay or a proof of the multiplication
theorem. The report follows the live [selected record](../../certificates/selected-result.json)
to its certificate, review and full replay command. It includes the selected
record's SHA256 and conditional scope.

The older `scripts/research_baseline.py` expects `bit_lower` and `complex_lower`.
On canonical main `2a13eb1827784206202db90e5dc8327cf8a250db`, its source-binding
check passes with the complete inputs present, but its summary raises
`KeyError: 'bit_lower'`. #4359's certificate has a different schema and different
budget stages. Treating its uniform-template savings as the older primitive
pair would also apply an unsupported balanced-transfer model.

The successor reports these quantities separately:

| Stage | Source field | Selected #4359 value |
| --- | --- | --- |
| Complex uniform template | `uniform_templates`, family `complex` | `36/15625` |
| BIT uniform template before cover | `uniform_templates`, family `BIT before cover` | `69/25000` |
| Ordinary BIT after conversion | `ordinary_BIT_saving` | `27418653797/10000000000000` |
| Admitted BIT budget | `admitted_BIT_saving` | `27/10000` |
| Binding outer cost row | minimum of `nine_outer_savings` | `main_transform`, `115098849/50000000000` |
| Strict slack over selected `23/10000` | outer minimum minus selected κ | `98849/50000000000` |

These are values from the source certificate, not independently rederived
supplier savings. Every outer row is retained, including rows above one; all
ties for the minimum are reported. Enormous template ranks stay symbolic.
The report does not infer an `a/(1+a)` cap, a limiting primitive, or a target
multiplier from these stages.

The adapter supports `proposed-conditional-integer-multiplication-claim/1`
with the two named template families and nine named outer rows. Unknown schemas,
missing/duplicate families, nonexact or invalid budgets, inverted BIT stages,
missing/extra outer rows, an inconsistent minimum or slack, and nonstrict
endpoints fail with a nonzero exit. Source corruption, omitted source files,
extra package files and proof drift still fail in the existing checker before
a success report can be printed. These are consistency checks; passing them
does not establish the mathematical inequalities that produced the certificate.

## Sparse checkouts

All selected inputs must be materialized. The existing diagnosis command is:

```sh
python3 -B scripts/research_baseline_sparse.py
```

Inspect its suggested sparse-checkout additions and materialize the inputs.
Then run the current command in its `next` field. It uses
`research_selected_baseline.py` for the productive-helper summary. Diagnosis
does not verify the inputs; the successor's source check remains mandatory.

## Compatibility and validation

The historical baseline, bottleneck brief, catalogue and frozen scientific
inputs are unchanged. Existing research packages pin some of those bytes.
[PR #3725](https://github.com/CrocSwap/integer-mult-bounds/pull/3725) documents
the earlier decision to provide sparse diagnosis in a separate helper for
this reason. This successor supplies a migration command without invalidating
those historical receipts. [PR #4436](https://github.com/CrocSwap/integer-mult-bounds/pull/4436)
already contains the separate status/CI navigation repair.

Run the independent synthetic-closure and metadata regression controls with:

```sh
python3 -B -m unittest discover -s tests -p test_research_selected_baseline.py -v
```

The fixtures exercise the real selected-record source checker and the CLI in
ordinary and optimized Python, including a fully hash-authenticated but
internally inconsistent certificate. No Git checkout or native computation is
required for these controls. The source fixture's numeric values are transcribed
from the #4359 claim at the base above; no new scientific result is asserted.
The test filename is included by the existing research onboarding discovery
command. The full selected cold replay is a separate obligation and was not
run for this reporting adapter.

## Current task-picker commands

The current task-picker CLI, `scripts/choose_current_research_task.py`, resolves the exact generic command
`python3 -B scripts/research_baseline.py` to the current selected baseline.
Each affected suggestion retains its complete original entry in
`catalog_first_step` and explains the change in `first_step_resolution`.
Only the command changes. The inspection text, scope, task, method, scope key
and acceptance gate stay the same. Other scientific first-step commands are
not changed. The CLI checks that the current helper exists, or is an exact
HEAD file omitted by a sparse checkout, before it emits the resolved command.
A sparse result names the missing helper for materialization.

The historical `scripts/choose_research_task.py`, catalogue bytes, `select()`
result and package `TASK.json` original-card receipts remain exact. The current
entry point runs the historical CLI with unchanged arguments and resolves its
JSON output. Help and error output keep the child status and text. This separate
entry point is necessary because a frozen package also pins the picker script
as a runtime input. It must not be changed or silently repinned. This distinction is deliberate: the CLI gives current
orientation, while the stored card records the historical assignment. Do not
copy the resolved command into an old package or repin its frozen inputs.
[PR4906](https://github.com/CrocSwap/integer-mult-bounds/pull/4906) found 57
runtime consumers of the catalogue and requested this receipt-preserving
migration. [PR5359](https://github.com/CrocSwap/integer-mult-bounds/pull/5359)
provides the separate authenticated historical complex-ceiling replay.
That scientific command is outside this generic-baseline resolution rule.

The displayed scientific starting points still need a current overlap and
scope check. Command resolution is not a strategic reassessment or scientific
acceptance. Tests cover all 16 generic cards, unchanged other cards, exact
command matching, missing/deleted/sparse helpers and actual CLI output.
Run them with `python3 -B -m unittest discover -s tests -p test_research_current_assignment.py`.
Current CLI resolution and these controls: Ali Romman with substantial OpenAI
Codex assistance; Apache-2.0.

## Open next questions

Future selected certificate schemas need an explicit budget-stage adapter.
Start from the new selected record and reviewed source schema, then add a
positive fixture and rejection controls before enabling it. A generic transfer
formula cannot replace the construction's own outer ledger.

Credit Douglas Colkitt and the retained source-checker contributors for the
orientation and source-binding machinery; zxv, Jacob Alan Sussman and the
[full #4359 contributor map](community-productive4359-contributors.md) for the
scientific inputs; and Mister-Meeseeks / the credited Claude agent in #3725
for the immutable-helper precedent.
Prepared by Mihir Srivastava (@mihir-s-05) with substantial OpenAI Codex
assistance; no subagents. Apache-2.0.
