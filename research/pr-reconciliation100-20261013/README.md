# Frozen 100-PR reconciliation

**Scope:** 100 historical open, non-draft PRs selected before this round,
not a current queue census and not 100 completed mathematical audits.
The [review](../../docs/research/community-reconciliation100-review.md) records
three completed dispositions and 97 explicit carry-forwards. No new κ.

- `STARTING-SNAPSHOT.json`: contributors, exact heads, GitHub base/count/state
  refresh, and preceding scoped review references.
- `COVERAGE.json.gz`: complete original changed-file inventory for each PR,
  compared with main `49b3157d1d89adcef16df8be98445451672be5ba` and the checked
  PR181 archive. Resolution maps appear only for completed reviews.
- `SHARED-CONTENT.json.gz`: unmatched blobs with every PR/path occurrence;
  a comparison worklist, never automatic mathematical acceptance.
- `DISPOSITIONS.json`: authoritative per-PR status, evidence, attribution,
  integration, remaining task, publication and closure.
- `NEXT-ACTIONS.json`: grouped dependency work and individual starting paths.
- `pr3-original.tar.gz`: all 14 changed files from eumemic's PR3 at
  `dfe5b818aad4d386cb5dd7d76df108088107765d`. Old release wrappers are historical.
  Original copyright, notices and assistance disclosures are retained.
- `pr3-tests.txt`, `pr183-tests.txt`: local Python 3.12 execution receipts.
- `CLOSURES.json`: verified GitHub merge/closure states, exact heads and explanation links.
- `MANIFEST.json`: evidence byte pins; this is not a mathematical certificate.

Reproduce the integrated focused checks and offline receipt integrity:

```sh
python3.12 -B -m unittest discover -s tests -p test_complex_network.py -v
python3.12 -B -m unittest discover -s tests -p test_assembly_ceiling.py -v
python3 scripts/verify_pr_reconciliation.py
```

The receipt checker accepts `--git` to recompute all 100 raw original diffs
and merge bases if their pinned Git objects are available. Fetch missing
`pull/<number>/head` objects from the origin, and verify they still equal the
snapshot before using them. That flag is optional for normal offline CI;
receipt byte pins and integrated sources are always checked. Neither mode
performs a live GitHub check. To inspect one PR's full path-level coverage:

```sh
python3 - <<'PY'
import gzip, json
from pathlib import Path
p = Path('research/pr-reconciliation100-20261013/COVERAGE.json.gz')
rows = json.loads(gzip.decompress(p.read_bytes()))['pull_requests']
print(json.dumps(next(row for row in rows if row['number'] == 154), indent=2))
PY
```

## Open next questions

1. Can the early circuit/geometry remainder (#2/#4/#8/#9/#12) be retained in
   complete historical packages without modifying immutable dependencies?
   Begin with each decision's explicit unmatched scientific files, then inspect
   old root wrapper edits. Existing attribution is not a full scope check.
2. Which frame-compiler residuals are reusable exact-source work, and which
   contain alternate schedules or proof claims? Start with the shared-content
   index and preserve each contextual use before granting replay reuse.
3. Can #154's concurrency and algebra optimizations be integrated safely?
   Start with invalid-job rejection, failure propagation and isolated generation;
   reuse the prior scoped frame comparisons only where inputs are unchanged.

Do not infer that an unmatched blob is an incorrect contribution, that all
matched files are actively executed, or that these remaining tasks are author
revision requests. Research notes and parallel alternatives remain in scope.
