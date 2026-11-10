# Catalogue assessment versus the selected result

The new contextual task CLI exposes the catalogue's original `selection_context`
as `catalog_selection.context` and compares its κ, source commit and review
pointer with the selected record. It delegates to the unchanged current picker.
This resolves an onboarding discrepancy, not a mathematical claim or a new
research-priority assessment.

At base **`7c49fe32c55de02c2c873655c804b16e4c3fef0a`**, revision 8 of the
catalogue and [priority guide](current-priorities.md) name PR5599. The
[selected record](../../certificates/selected-result.json) and its
[application review](pr-intake-evidence/pr6030-audit/PROOF-REVIEW.md) select
PR6030. The old current CLI emitted the latter under `selected` but omitted the
catalogue's assessment context altogether, while linking the former guide.

| Field | Catalogue assessment | Selected record |
| --- | --- | --- |
| κ | `62009/20000000` = .00310045 | `781451/250000000` = .003125804 |
| Source commit | `09dd0965711ca7eeb169057a420abab1c9052137` | `772dd10a5859a1d15f4851feb371519789213ad8` |
| Review directory | `pr5599-completion` | `pr6030-audit` |

The source comparison uses the original `audited_source_head`, rather than the
separate portability-repair head. It does not infer a primary source from the
order of `source_prs`, nor from a larger number in an open PR title.

## Contract and reproduction

```sh
python3 -B scripts/choose_contextual_research_task.py --task scope-navigation --seed 00000000000000000000000000000063
```

On the pinned inputs, expect `catalog_selection.matches_selected: false`, with
exact old/new values under `differences.kappa`, `differences.source_commit` and
`differences.review`, and no `uncompared_fields`. `selected.reproduce` remains
`make frontier6030-verify`. The 32-digit picker seed is 99 in hexadecimal; it
only makes this explicitly chosen card's output reproducible.

Equal rational representations compare equal. A changed review or source at
the same κ still differs. Missing comparison fields produce `null` (unknown)
when no known difference exists; a known difference still produces `false`.
The exact historical context is retained, including its own dated scope text.

Before comparison, both reread JSON byte strings must match the hashes in the
child picker's receipt. A change between the child and wrapper reads fails
without emitting a successful JSON receipt. This detects mixed snapshots at
that boundary; it is not an atomic filesystem snapshot or authentication of
the full selected construction. A stable checkout remains required.

Both existing pickers, the catalogue, priority guide and selected record retain their
bytes. Existing task choices, methods, scope keys, coverage flags and command
routes are preserved. The contextual CLI adds only `catalog_selection`; existing
consumers can keep their original entry point and output contract. Matching
the three metadata fields establishes neither task novelty nor current coverage.

## Verification and source pins

The following command checks the actual discrepancy fixture and controls for
same-κ provenance changes, rational equivalence, missing context, malformed
metadata, changed-between-reads inputs and the real child/wrapper CLI:

```sh
python3 -B -m unittest discover -s tests -p 'test_research_priority_context.py' -v
```

Expected: **10 tests, OK**. The adjacent command is
`python3 -B -m unittest discover -s tests -p 'test_research_current_assignment*.py' -v`
(15 tests). Both pass normally and with `-O -W error` on Linux, CPython 3.12.14.
The real original/contextual receipt for the command above is identical after removing
the added field. The existing controls preserve all live cards, frozen generic
and historical routes, help/error propagation and sparse-input distinctions.
The 27 onboarding and nine coordination tests also pass. The final replay
dependency plan selects no scientific packages; the new code has no scientific
runtime dependency.

The unchanged #6179 conformance replay also passes with 22 live cards, two
historical route fixtures and seven rejection controls:
`python3 -I -W error -B research/current-picker-lazy-validation/verify.py`.
That replay reconstructs the current picker's exact predecessor source, which
is why this contribution uses a separate entry point. The historical timing
receipt is checked for conformance, not rebenchmarked; no speed claim is made
for the contextual CLI's extra subprocess.

Immutable SHA-256 pins at the exact base above:

| Repository path | SHA-256 |
| --- | --- |
| `docs/research/agent-task-catalog.json` | `ead6cdc9d0af6d58e8a49744d8ec8c7c15e13d2ba93c276c434bcf9b51b93a81` |
| `docs/research/current-priorities.md` | `70f61c8d140ae6e892f2b8f065bba4eae3e76f7a8f55f632fd4e2f9f34039bdc` |
| `certificates/selected-result.json` | `9b8d0eea95b3bf0dfcb7938a732a6439b87a2685dec2a5ab9e525b3b34debbfa` |
| `scripts/choose_research_task.py` | `484f553c488c6f427ca81f19f3ee2720399dcc28ce61a3886d50bdf28ca72d12` |
| `scripts/choose_current_research_task.py` (unchanged) | `04e194b14a1f4157be5be83e8c13995d69c3efe8996773d918acba6bfcabb471` |

Only Python's standard library is used. The selected full cold replay, native
maps, compiler, precision/tape and analytic recovery are outside this metadata
repair. The five selected assumptions and κ remain unchanged.

## Assignment, overlap and open next question

OS randomness (`secrets.randbelow(100)`) yielded assignment seed **99**:
research consolidation. Three candidates were considered: this catalogue/record
discrepancy; source-certificate pointer coverage (current inputs agree, with
the broader predecessor #1864); and ledger/status navigation (nearby work
#3695, #4138 and #6050). The chosen bounded experiment was to reproduce and
expose this exact discrepancy while preserving task selection. Stop after the
three-field comparison and its failure controls; no global survey or search for
a stronger bound is part of this result.

The local claim was recorded at 2026-11-09 17:14:30 UTC, with an expected finish
by 17:47:48 UTC. GitHub reported no pinned issue. The start-here discussion,
last 20 handoff comments, 25 recently active discussions and relevant open and
closed PR searches were inspected before implementation. No matching repair
was found in that bounded coverage; this is not a proof of novelty.

This extends the exact-output boundary in Ali Romman's #5378 and Mihir
Srivastava's #5520, preserving Nick Petalas's #6179 source-bound conformance
and benchmark. The omission of `selection_context` was already observed in
#4906's startup audit; that work repaired the generic command route. This
change adds source/claim reconciliation and unknown-context handling rather
than claiming discovery of the earlier omission. No pending construction is a
dependency.

**Open next question:** should the next maintainer priority assessment revise
the catalogue's tasks as well as its selected context? The comparison now makes
the old assessment visible, but cannot establish whether its advice remains
applicable. First inspect each affected card's current source-specific coverage
and live handoffs; a substantive strategic reassessment and dependent-input
review are required before rewriting frozen catalogue bytes.

Prepared by **Sricharan Vagvala (@theon199)** with substantial **OpenAI Codex**
assistance. Credit Douglas Colkitt, Ali Romman, Mihir Srivastava, Nick Petalas,
ToikY and the
retained picker/test contributors; DreamingOfClouds and the selected source's
[contributor map](community-p1046030-contributors.md) retain all construction
credit. Apache-2.0. No independent human or proof-kernel review is claimed.
