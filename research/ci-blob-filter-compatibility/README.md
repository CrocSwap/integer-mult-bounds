# Full-history blob-filter source-reader compatibility probe

The unchanged source reader successfully hydrated a genuinely old, deleted
provenance blob in a controlled local partial-fetch fixture. Full refs, raw
commit/tree history and current HEAD bytes/modes matched the unfiltered client.
The separate offline client rejected that source before hydration and passed
metadata/history/mode checks after explicit hydration. This is a local transport
compatibility result; no hosted speedup or production adoption is claimed.

Actual `.github` workflows are unchanged. `PROPOSED-NOT-APPLIED.patch` contains
only the prospective two `filter: blob:none` input lines as data. Current
checkout uses full history/all heads/all tags and no explicit filter or sparse
checkout. The pinned action applies filtering only when requested, so the
proposal would change acquisition. Changing either live workflow would select
all registered packages through the existing shared-control planner; adoption
is therefore a separate review and CI-budget decision.

## Exact scope and evidence

`SOURCE-PINS.json` authenticates 12 source objects from canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a` and pinned official
`actions/checkout` commit `3d3c42e5aac5ba805825da76410c181273ba90b1`.
The experiment executes the exact unchanged `research_package.py` and
`check_research_commit.py` copies in synthetic repositories. Other retained
source files document the workflow, checkout ref/filter mapping and existing
regression guarantees. It does not execute predecessor scientific packages.

Each client starts with `git init`, then a real `file://` fetch of all heads,
all tags and the exact event commit, followed by full HEAD checkout. The local
upload-pack server permits filtering and SHA wants. No shallow depth, alternate
object store, external service or project clone is used. A 257-byte old source
and 65,536-byte unused obsolete blob are deleted before HEAD. A separate branch,
annotated tag and event ref must remain present. The fixture also contains a
32,768-byte side-branch blob. Total observed primary fixture size was below
0.5 MB, against a frozen 50 MiB ceiling.

Before any named old-blob lookup, resident inventory uses `cat-file
--batch-all-objects`. The first filtered client then runs the UNCHANGED metadata
validator while the old source is still absent. This reader actually fetches
that old source in the tested environment. The two online outcome fields were
unknown until execution and were allowed to report a useful negative. A second
filtered client separately tests offline failure, explicit old-source hydration,
then offline metadata, publication ancestry and executable-mode validation.
Working-byte, owner-execute, staged/unstaged drift, shallow-history and
foreign-source controls require their intended failures. No source-history
acceptance check is weakened.

`RESULT.json` contains 17 strict semantic booleans, source/case hashes and primary
code hash. `ORACLE.json` contains the independent fixture's result; its command
compares every common field against actual primary data. Temporary paths, Git
IDs, pack details, versions and timings are excluded from portable semantic
comparison. Raw first attempts and diagnostics are retained in the session
handoff, with public status described in VALIDATION.md.

The primary environment was managed CPython 3.12.14 and Git 2.50.1 (Apple
Git-155). First complete execution and four strict modes took about 2.5–2.9 s
locally. These are complete fixture times, not matched filtered/unfiltered
acquisition timings and not evidence of a hosted speedup. Registered commands,
export integrity and any cold replay status are reported separately.

## Reproduce

From the repository root with Python 3.12 and Git on POSIX:

```sh
python3.12 -I -W error -B research/ci-blob-filter-compatibility/verify.py
python3.12 -I -O -W error -B research/ci-blob-filter-compatibility/verify.py
python3.12 -I -W error -B research/ci-blob-filter-compatibility/oracle.py --check-primary research/ci-blob-filter-compatibility/RESULT.json
python3.12 -I -W error -B -O research/ci-blob-filter-compatibility/oracle.py --check-primary research/ci-blob-filter-compatibility/RESULT.json
python3.12 -I -W error -B research/ci-blob-filter-compatibility/verify.py --emit /absolute/new/RESULT.json
python3.12 -B scripts/research_package.py --package research/ci-blob-filter-compatibility
```

Git is an explicit runtime dependency; a cold Git-only PATH is meaningful,
whereas Git-free replay is not claimed. Each Git command is bounded at 30 s,
helper Python command at 60 s, and the enclosing registered command at 180 s.
Only local file transport is allowed. Each new wrapper bounds its launched
process group on timeout; separately detached children of the unchanged helpers
retain those helpers' existing lifecycle responsibility. No universal process-tree
cleanup is claimed. Automatic maintenance is disabled in owned fixtures. Python containers, arbitrary-size
integers, exceptions and recursive exact-type JSON comparison are declared
managed-code deviations from low-level Power-of-Ten style. Primary functions
remain below 60 lines and acceptance does not use `assert`.

## Failure provenance

The original first fixture attempt exited 1 because its launcher used Python
`-I` for a frozen helper that imports an adjacent module. Its raw code and trace
are retained. The actual first online source-reader probe had already succeeded;
the later history-checker import failed. The corrected launcher uses `-E -s`
to retain the documented sibling import while ignoring Python environment and
user-site injection; rejection controls additionally require intended diagnostics.
Source helpers, cases and common schema were unchanged. The first complete
receipt is labeled separately from that original failed attempt. An original
manually written BEFORE timestamp mistakenly read 20:43 while the run completed
at 20:42; the original file remains retained with an explicit correction.
Pre-execution ordering rests on the recorded sequential code-copy/hash/subprocess
operations, not the erroneous future timestamp. No failure is relabeled as success.

## Open next questions

- Test the declared online hydration phase on an actual hosted Git/public-origin
  environment with `persist-credentials:false`. Start with one authorized
  controlled job; authentication, availability, versions and throughput remain
  external to this local file transport result.
- Audit one actual replay's old-source inventory before an offline gate. Start
  from SOURCES and actual Git reads, including script/archive references;
  undeclared transitive refs and external dependencies remain blockers.
- Measure acquisition bytes and complete matched job times before proposing
  production adoption. Hold HEAD, source demand and coverage fixed; current
  fixture timings and canceled checkout jobs do not establish a speedup.

Full history does not imply all historical blobs are offline. Later lazy fetches
require access to the public origin after checkout removes credentials; this
prototype grants an online acquisition/validation phase, followed by explicit
offline checks. It does not establish immediate post-checkout offline equivalence,
private-repository compatibility, an exporter theorem, arbitrary registered
command equivalence, a new kappa or a selected-frontier change.
