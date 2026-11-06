# Local overlap inventory runtime

The overlap checker now filters Git tree path strings before parsing matching
entries' metadata. Git supplies canonical slash-separated tree paths, so this
avoids constructing a `PurePosixPath` for every nested evidence or vendor file.
The inventory still includes only regular `research/*/README.md`,
`research/*/TASK.json` and `docs/research/pr-ledger.md` blobs at the pinned HEAD.
Both regular modes, 100644 and 100755, remain accepted. Symlinks remain excluded.

## Scope and evidence

Task `replay-runtime`, chooser nonce `2f902f02bc90b13cafed87d51f51b71d`,
priority revision 8, base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
`scope_status=changed`: this optimizes coordination-tool runtime rather than
scientific replay runtime. Checking overlap is required for research sessions;
this removes measured overhead without adding a cache or weakening coverage.

The selected-baseline command passed its source-binding checks. Live handoffs,
the start-here post and recent open PRs were read before selection. The overlap
refresh completed with 760 open PR bodies and 6,881 discussion records, fetched
2026-11-06 at 20:03:19 UTC and 20:05:44 UTC respectively. Targeted searches for
`local_coverage`, `HEAD note inventory` and `inventory parsing` found no direct
competing optimization in that coverage. Code diffs and unpublished work were
not searched. Canonical main remained the base above at the final fetch.

On Linux WSL2, CPython 3.10.12, seven alternating before/after trials gave these
median wall times on the same working tree:

| Measurement | Before | After |
|---|---:|---:|
| `local_coverage` with preloaded records | 0.512789 s | 0.178231 s |
| `local_records` plus `local_coverage` | 1.673241 s | 1.350239 s |

The tree query returned 129,156 entries; both versions searched the same 8,917
local records. Every trial compared the complete records, coverage dictionary
and warning list for equality. This is a local timing observation, not a claim
about network refresh time or scientific replay speed. Profiling the original
local scan attributed 1.086 s of its 3.289 s profiled duration to `local_coverage`.

To repeat the comparison from the repository root, use the base implementation
and the working implementation against the same checkout:

```sh
python3 -B - <<'PY'
from pathlib import Path
import statistics, subprocess, time, types
root = Path.cwd()
sources = [subprocess.check_output([
    'git', 'show', '7c49fe32c55de02c2c873655c804b16e4c3fef0a:scripts/find_overlap.py']),
    (root / 'scripts/find_overlap.py').read_bytes()]
modules = []
for source in sources:
    module = types.ModuleType('benchmark_overlap')
    module.__file__ = str(root / 'scripts/find_overlap.py')
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    modules.append(module)
records = modules[0].local_records(root)
expected = modules[0].local_coverage(root, records)
for full_scan in (False, True):
    samples = [[], []]
    for trial in range(7):
        for i in ((0, 1) if trial % 2 == 0 else (1, 0)):
            start = time.perf_counter()
            current = modules[i].local_records(root) if full_scan else records
            actual = modules[i].local_coverage(root, current)
            samples[i].append(time.perf_counter() - start)
            assert current == records and actual == expected
    print('full_scan', full_scan, 'seconds', samples,
          'medians', [statistics.median(s) for s in samples])
PY
```

## Verification and remaining scope

Run `python3 -B -m unittest discover -s tests -p 'test_research_overlap*.py'`
and the same command with `-O`. Both passed 38 tests. The added Git fixture
checks Unicode, spaces, tabs and newlines in package names, executable and
ordinary notes, a committed symlink, nested exclusions and a deleted executable
note. Existing tests retain sparse omission, ordinary deletion, unknown Git
coverage, working edits, untracked notes, cache, pagination and search checks.
No immutable input, source pin or selected-frontier file changes.

All 17 `test_research_*.py` modules containing `find_overlap` also passed
serially through `run_isolated_tests.run_modules`, with `workers=1` and
`module_timeout=60`. This includes Git-root binding, local aliases, Unicode
excerpts and onboarding. Initial attempts waited on inherited GPG signing for
temporary fixture commits and were stopped. The completed run prepended a
temporary PATH wrapper executing `/usr/bin/git -c commit.gpgsign=false "$@"`;
the user's Git configuration was unchanged. An environment-only config override
was insufficient because the source helpers intentionally scrub Git injection
variables. No native/operator replay was run for this coordination-only edit.

## Open next questions

The larger remaining local cost is reading and validating working-tree notes.
Any future optimization should first measure that stage and retain alias
rejection, untracked notes and changed working bytes. Caching solely by HEAD
would fail those obligations. No broader scan or cache change is proposed here.

Credit Douglas Colkitt and the retained overlap-helper contributors for the
existing search and coverage contracts. Prepared with substantial OpenAI Codex
assistance. Apache-2.0. Timings and test results are local executions; no
independent scientific review or multiplication-theorem claim is made.
