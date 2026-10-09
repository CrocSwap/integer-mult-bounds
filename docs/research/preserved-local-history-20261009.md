# Preserved local research and review history

Douglas Colkitt, with OpenAI Codex assistance. Preservation date: 2026-10-09.

This checkpoint versions 117 previously untracked files (7,332,551 bytes)
from earlier research and community-review rounds. Their original bytes,
source notices, assistance disclosures, experimental certificates and dated
status statements are preserved. None of these files was present at a local
branch tip when the inventory was taken; that check does not claim they never
appeared in older commits or external repositories.

**This is an archival checkpoint, not a new multiplication result or a new
mathematical review.** For the current conditional witness and accepted
construction, use [current status](current-status.md) and the
[selected result record](../../certificates/selected-result.json).
Statements such as “main remains,” “current,” “pending,” and “next experiment”
inside the files below refer to their original snapshots. They do not assign
work or change the current PR queue.

## Research record

| Location | Historical subject and disposition |
|---|---|
| [kappa-nine](../../research/kappa-nine/ASSESSMENT.md) | Earlier target budgets, block-label and rank diagnostics, baseline sources and follow-ups. Read the later reports in the directory as well as its initial assessment; its proposed next experiments are historical. |
| [architecture-nine](../../research/architecture-nine/REPORT.md) | Scoped screens for auxiliary-bank reuse and retained cube geometry; no improved exponent. |
| [computation-fusion-nine](../../research/computation-fusion-nine/REPORT.md) | Two specified whole-stage fusion designs rejected by paid readout costs. |
| [direct-selected-xor](../../research/direct-selected-xor/REPORT.md) | Exact phase identity and its recursive-cost diagnostic; no faster tape algorithm established. |
| [fourier-boundary-fusion](../../research/fourier-boundary-fusion/REPORT.md) | Copied-center Fourier fusion and boundary-cost obstruction in the tested schedule. |
| [geometry-circuit-discovery](../../research/geometry-circuit-discovery/REPORT.md) | Support-weighted central-factor searches and scoped negative findings. |
| [shared-center-feasibility](../../research/shared-center-feasibility/REPORT.md) | Joint changes to center forms and maps within specified E8 families; no admitted construction. |
| [mechanism-prep](../../research/mechanism-prep/REPORT.md) | Two-field mechanism and circuit/geometry requirements at the earlier checkpoint. |
| [hybrid-clean-design](../../research/hybrid-clean-design/REPORT.md) | Common-chart and clean-readout design screens. Its remaining aggregate proposal was subsequently closed by the follow-up below. |
| [shared-aggregate-followup](../../research/shared-aggregate-followup/STATUS.md) | **Retired at the maintainer's direction.** Preserving its report does not reopen the search. The unchanged separate producer/readout contract remains excluded by its scoped obstruction. |

These directories contain useful failed approaches as well as exact identities
and narrow obstruction arguments. Their conclusions apply to the models stated
in each report, not to every finite network or multiplication algorithm.
They are not added as dependencies of the selected production verifier.

## Review and publication history

- [Round-three review](community-round3-review.md),
  [validation](community-round3-validation.json), and
  [Lean audit](community-round3-lean-audit.json).
- [Round-four review](community-round4-review.md) and
  [validation](community-round4-validation.json).
- [Round-five review](community-round5-review.md),
  [validation](community-round5-validation.json), and
  [queue snapshot](community-round5-queue.json).
- The [PR144 integration receipt](../../research/pr-review-20261009/pr144-integration-status.json)
  and [historical patch](../../research/pr-review-20261009/pr144-integration.patch).
  The patch targets the PR head identified by its receipt, not today's main.
  It is retained as evidence and has not been applied again.

These reviews preserve contribution attribution and the evidence available at
their respective dates. Their old pending/accepted dispositions are historical;
later integration records and the selected result determine current inclusion.

## Preservation checks

The [inventory](preserved-local-history-20261009.json) records the original
byte count and SHA-256 of every preserved file, against base commit
`efaa57eb626a3a48bdb8ac17f4344d0298126b87`.

This pass checked Python syntax for 39 files, JSON parsing for 55 files,
and local Markdown link targets. The PR144 patch matches its recorded size
and SHA-256 and parses as a patch. No historical experiments were rerun and
no mathematical claims were revalidated by those packaging checks.

To verify that the archived files still match the captured originals:

```sh
python3 - <<'PY'
import hashlib, json
from pathlib import Path
record = json.loads(Path('docs/research/preserved-local-history-20261009.json').read_text())
for name, expected in record['files'].items():
    raw = Path(name).read_bytes()
    if len(raw) != expected['bytes'] or hashlib.sha256(raw).hexdigest() != expected['sha256']:
        raise SystemExit('Changed preserved file: ' + name)
print('PASS all', record['file_count'], 'preserved files')
PY
```

The manifest is a snapshot of the original evidence, not a reason to rewrite
that evidence whenever the project advances. Later corrections should be
separate, dated records that identify the affected claim and source.
