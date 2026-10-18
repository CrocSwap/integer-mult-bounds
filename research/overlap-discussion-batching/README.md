# Batch Discussion reads without losing overlap coverage

## Maintainer integration, 2026-10-16

The original PR #2493 implemented 50/5/5 initial page sizes. Main already
incorporates the same batching mechanism from Nick Petalas's #2514 with
10/25/10 initial page sizes. Integration retains that current implementation,
including later PR-file pagination and query handling, and adds Arham Garg's
six independent pagination/cache controls. The 51-small-thread request test
therefore expects six listing requests; complete ordered records are unchanged.
The original tests and implementation are retained at PR head
`a459ee34fad0488691beba8441e0a31e103b91a5` and in the review archive.

All benchmark numbers and the original validation/integration narrative below
are historical author evidence for the original 50/5/5 implementation, not
fresh measurements of main's 10/25/10 implementation. The opt-in benchmark
records the code actually run and must write a new output; keep BENCHMARK.json
and its source/fixture pins unchanged. The integration does not modify the
shared overlap helper or onboarding test, so it introduces no further drift
in either older package named below. Their historical pin failures are not
reported as successful replays. Current maintainer execution is recorded in
`research/community-efficient1800-audit/checks/check-2493.json`.

`scripts/find_overlap.py` now fetches the first five comments and the first
five replies with each 50-Discussion listing. It follows every remaining
comment and reply cursor in 100-item pages. Small threads no longer require
one extra API request each. Record fields, order, search rules, cache lifetime,
and replacement only after a complete fetch remain unchanged.

This is coordination tooling, with no supplier, frontier, or mathematical
replay change. The picker assigned verifier engineering, `replay-runtime`,
with nonce `515f2593bdf7181fc9c591fa525a923a`.
[TASK.json](TASK.json) declares the change in scope to the required overlap
step. Contributors reported stalled Discussion scans, including
[this report](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18927573).
The canonical claim and completion are in
[Discussion 2264](https://github.com/CrocSwap/integer-mult-bounds/discussions/2264).

## Coverage and failure controls

The six tests in
[`test_research_discussion_batching.py`](../../tests/test_research_discussion_batching.py)
use distinct cursors for every connection. The larger fixture has 51
Discussions, a 207-comment hub, and two 207-reply comments. Tests compare every
ordered record with a direct traversal of the fixed graph. The CLI test
finds the final reply and checks its persisted cache and coverage report.

The small-thread test fails on the base with `53 != 2` requests, then passes
with two requests and identical records. Later Discussion, comment, and reply
page failures preserve the previous complete source. A failed first scan
publishes no partial Discussion source. Empty boards remain complete empty
results. The existing pagination test retains its five records and now makes
four requests instead of five. Manual mutation controls that stop comment
or reply pagination early both fail the CLI coverage test.

The listing requests at most `50 + 50*5 + 50*5*5 = 1,550` connection nodes.
Using 100 at both nested levels would request 505,050 nodes, exceeding
[GitHub's 500,000-node query limit](https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api#node-limit).
Small initial pages also limit response size.

## Measured evidence

[BENCHMARK.json](BENCHMARK.json) contains all six runs, source hashes,
environment, request counts, and record hashes. Three pairs alternate order
on the same twenty public Discussion IDs in [FIXTURE.json](FIXTURE.json).
Every run makes fresh GitHub requests and reproduces all 77 ordered records,
including exact text, URLs, timestamps, and record kinds. No overlap cache,
errors, or skipped work contributes to these timings.

| Version | Requests per run | Median seconds | Minimum to maximum |
|---|---:|---:|---:|
| Base `0fdd7d82` | 21 | 18.442 | 17.644 to 18.521 |
| Batched | 2 | 2.628 | 2.585 to 3.247 |

The local median ratio is 7.02. Wall times include network latency, GitHub
processing, and local `gh` startup on macOS 27.0.1 arm64, Python 3.12.13,
and `gh` 2.102.0. The benchmark replaces only the listing connection with
`nodes(ids:)` to fix the roster. It preserves each implementation's field
selection and runs its unmodified comment/reply traversal. The request
reduction is deterministic on this corpus; the timing ratio depends on the
host, network, and thread sizes.

The earlier 67-record capture remains in [FIXTURE-initial.json](FIXTURE-initial.json).
During a nine-hour interruption, Discussions 1267 and 1317 acquired ten
comments and new update timestamps. The stale hash correctly rejected.
After inspecting those changes, the new fixture pinned 77 records on the
same twenty IDs. No timing from a mismatched corpus is accepted.

A complete live candidate scan used the actual repository listing: 975
records in 19 requests, 27.86 seconds. Compared with the earlier 973-record
scan, it retained every record and added the new claim and one handoff
comment; the handoff thread's timestamp also changed. These unequal snapshots
are smoke evidence, not a timing comparison. A resume scan covered 679 open
PRs and 1,197 Discussion records. The submission scan at 12:35 UTC covered
687 open PRs and 1,199 Discussion records with complete pagination and no
warnings. Canonical main remained at `0fdd7d82`.

## Reproduce

The registered replay is offline. It runs the six coverage tests normally
and with Python optimization enabled. [SOURCES.json](SOURCES.json) pins the
unchanged base as provenance. The working helper and test are declared CI inputs.

```sh
uv run --python 3.12 --no-project python -B scripts/research_package.py --package research/overlap-discussion-batching --check-only
uv run --python 3.12 --no-project python -B scripts/research_package.py --package research/overlap-discussion-batching
uv run --python 3.12 --no-project python -B -m unittest discover -s tests -p 'test_research_*.py'
```

The live benchmark needs authenticated `gh`, the pinned Git commit, and an
explicit opt-in. It refuses changed live records. Write a new output file
to preserve the recorded measurements.

```sh
uv run --python 3.12 --no-project python -B research/overlap-discussion-batching/benchmark.py --live > /tmp/overlap-benchmark.json
```

No full supplier cold replay or Linux timing is claimed. GitHub pagination
does not provide an atomic snapshot of a board that changes during a scan;
this change retains that limitation. Extremely busy threads can need an
extra continuation request after the five-item initial page. Any GitHub
error still produces a refresh warning and retains old evidence only with
its original timestamp.

## Verification and integration status

The three offline commands above pass on Python 3.12.13. The package replay
runs six tests normally and six under `-O`. The full research-workflow suite
runs 71 tests in 10.480 seconds: 68 pass and three Linux `/proc` process-tree
tests skip on macOS. `git diff --check` passes. The assigned first step,
`python3 -B scripts/research_baseline.py`, passes selected source bindings
and arithmetic only.

Two older registered packages also declare the edited files as inputs.
Their metadata checks fail on both an untouched `0fdd7d82` worktree and this
patch, with the same first error:

| Package | Metadata error on base and candidate |
|---|---|
| `overlap-path-index` | `source blob provenance mismatch: scripts/find_overlap.py` |
| `research-package-pin-batching` | `working source drift: tests/test_research_onboarding.py` |

Reproduce either rejection with the package launcher:

```sh
uv run --python 3.12 --no-project python -B scripts/research_package.py --package research/overlap-path-index --check-only
uv run --python 3.12 --no-project python -B scripts/research_package.py --package research/research-package-pin-batching --check-only
```

This patch also changes the onboarding test bytes that `overlap-path-index`
pins, so resolving its older provenance error alone will not admit this
patch. Frozen package files and pins remain unchanged, as repository guidance
requires. Their replays have not passed; integration needs a maintainer's
source-binding decision. Aaron Wang's broader
[live-pin drift audit, PR 2255](https://github.com/CrocSwap/integer-mult-bounds/pull/2255),
head `15836362a3cf17d245db8a01d930a12868c043bd`, records the same class of
existing limitation. This package does not import or repeat that audit.

## Open next questions

No further change is justified by this scoped result. Larger page sizes or
incremental caching would need separate coverage and request-limit evidence.
TASK.json records the empty question list and reason.

## Credit and overlap

Douglas Colkitt and the overlap-tool contributors supplied the record schema,
complete pagination, cache behavior, and original tests. Nick Petalas's
pagination compatibility repair at `9c2fdd89e553751e40ef8011716a249e8385d284`
is retained. Neighboring
[PR 2154](https://github.com/CrocSwap/integer-mult-bounds/pull/2154), head
`5984d9999bceaeb7d1ce9a3f4edfbfcd0b70c118`, changes task-term extraction.
This patch changes Discussion acquisition and does not depend on that PR.
Entry, resume, and submission checks found stall reports but no competing batching claim.
Their coverage and limits are recorded in TASK.json.

Prepared by Arham Garg, `@arhamgarg`, with substantial OpenAI Codex assistance,
GPT-6 Astra, for diagnosis, implementation, verification, and writing.
No independent human review is claimed. New work is Apache-2.0.
