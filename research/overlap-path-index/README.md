# overlap-path-index: search open-PR overlap by changed file path

**Verifier engineering; no new kappa, no certificate or selected-record change.**
This package documents and verifies one change to the live coordination tool
`scripts/find_overlap.py`: it now caches each open PR's changed-file list and
answers "which open PRs touch this path?", the request left in
[the workflow feedback thread](https://github.com/CrocSwap/integer-mult-bounds/discussions/1200#discussioncomment-18909265).

Integration note: the live tool retains main's UTF-8 handling, and its tests include PR1702's isolated Unicode fixture. `SOURCES.json` pins this combined version and retains the submitted input pins. Both the complete onboarding suite and this package's unmodified acceptance checks are rerun for the combination.

## Scope and evidence

Original card: `replay-runtime` (verifier-engineering), scope **refined** to the
card's allowed "source-bound cache boundary" variation; see
[TASK.json](TASK.json) for the scope-change reason. Source commits, Git blobs
and SHA256 pins are in [SOURCES.json](SOURCES.json); the catalogue and selected
record are pinned as historical provenance.

**What changed.** `find_overlap.py` gains a third snapshot source, `pr_files`,
fetched only when `--path` is used, plus `fetch_pr_files` and `path_report`.
Body term search, its match order and its report fields are unchanged. With
both axes given, `matches` is the intersection (a record must hit at least one
term and one path) while `path_matches` stays the superset of all path hits, so
a path hit can never disappear silently. Patterns are `fnmatch` patterns or
literal substrings of the repository-relative path. A PR whose changed-file
list is unavailable (for example
[CrocSwap/integer-mult-bounds#376](https://github.com/CrocSwap/integer-mult-bounds/pull/376)
at the measured snapshot) is recorded
with empty paths and `truncated: true`, and PRs beyond GitHub's 100-file
listing are flagged `truncated: true` in the output; neither is silently
trusted. Diff contents remain unsearched, and the report's `path_limits` says so.

**Measured behavior** (Windows 11, CPython 3.13.15, this host):

| Check | Before | After |
|---|---:|---:|
| Body-only overlap query (offline cache) | 0.48 s | 0.48 s (no `pr_files` fetch at all) |
| Full changed-file index build | impossible (no path data) | 87.7 s, 745 open PRs, 20,117 changed-path entries |
| Cached offline `--path` query | manual per-PR inspection | 0.48 s |

The index fetch pages 10 PRs at a time with up to four attempts per page:
25x100-node pages exceed GitHub's ~10 s gateway limit and returned HTTP 502 on
this host (measured: failing calls died at 10.5-10.7 s), while 10x100 pages
completed in 0.8-4.4 s. A failed refresh keeps the previous snapshot and warns;
it never reports "no overlap" from missing data without a warning.

**Live answers to the request's example questions** at the measured snapshot:
`docs/research/current-status.md` is touched by exactly one open PR,
[CrocSwap/integer-mult-bounds#1232](https://github.com/CrocSwap/integer-mult-bounds/pull/1232);
`research/lean-external-review` is touched by
[CrocSwap/integer-mult-bounds#1365](https://github.com/CrocSwap/integer-mult-bounds/pull/1365)
and
[CrocSwap/integer-mult-bounds#1494](https://github.com/CrocSwap/integer-mult-bounds/pull/1494),
the stacked level-model phases of
[CrocSwap/integer-mult-bounds#442](https://github.com/CrocSwap/integer-mult-bounds/pull/442).

## Reproduce

From the repository root (no network needed):

```sh
python3 scripts/research_package.py --package research/overlap-path-index --check-only
python3 scripts/research_package.py --package research/overlap-path-index
```

Expected: `PASS_OVERLAP_PATH_INDEX`, then registered-package success. The
verifier checks the two pinned live inputs, runs the 11 Overlap unit tests and
seven hermetic CLI controls (positive, substring, glob, rejection,
term-and-path, mutation, missing-index) against a fixture snapshot cache placed
outside the repository. A live index build additionally needs authenticated
`gh`; `--path` queries within the cache lifetime cost nothing extra.

## Limitations

Tooling only. No mathematical claim, kappa, supplier, certificate, replay
coverage or selected-frontier change. Path matching is a changed-file
inventory, not diff-content search; closed PRs remain represented only through
local READMEs, TASK metadata and the PR ledger. The full index build costs
about 88 s and is paid only by `--path` queries at refresh time; GitHub's
~10 s gateway limit caps the page size. Whether the two live input files change
later is not this package's call: they are pinned, so a future edit of either
needs an explicit source-pin migration (same convention as other tooling
packages here). The pre-existing Windows CRLF failures in `PackageTests`
(fixed in [CrocSwap/integer-mult-bounds#1298](https://github.com/CrocSwap/integer-mult-bounds/pull/1298))
are unrelated and untouched. No independent human review or hosted-CI success
is claimed.

## Open next questions

Structured in [TASK.json](TASK.json):

1. **Closed-PR path coverage.** Can the index cover closed/merged PRs via the
   ledger's `COVERAGE.json.gz` inventories? Matters because closed work holds
   most duplicates. First step: a reader for
   `research/pr-reconciliation100-20261013/COVERAGE.json.gz`. Blocked by the
   need for an explicit freshness/coverage label so batch snapshots cannot
   overstate coverage.
2. **Cheaper refresh.** Should body-only searches carry the index, and can the
   87.7 s build be cut? First step: per-page caching keyed by PR head sha.
   Blocked by GraphQL offering no ETags for this connection; the time cost must
   be shown worth paying first.
3. **True stacking.** "What stacks on PR N" is approximated by shared paths;
   base/head chains would be exact. First step: record each open PR's base ref
   in `pr_files` rows. Blocked by stacked PRs here mostly targeting `main` and
   naming their parent only in prose.

## Credit and provenance

The overlap helper, its snapshot design and its coverage contract are Douglas
Colkitt's (with OpenAI Codex assistance, Apache-2.0, retained unchanged except
as described). The changed-file request is Mister-Meeseeks's
[discussion 1200](https://github.com/CrocSwap/integer-mult-bounds/discussions/1200#discussioncomment-18909265)
item 2. The onboarding UTF-8/Windows fixes in
[CrocSwap/integer-mult-bounds#1298](https://github.com/CrocSwap/integer-mult-bounds/pull/1298)
(rtyu193-rgb) affect the same script and are complementary; this change does not
include them. Prepared by Aaron Wang / navinor, with help from opencode.
Apache-2.0.
