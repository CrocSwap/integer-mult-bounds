# Reuse unchanged pinner bytes in complete pinned-edit scans

This scoped implementation-preservation proof removes duplicate head blob
reads from the repaired pinned-edit scanner of Armin Pourshafeie / apoursh
and ToikY. On the fixed canonical comparison below, it eliminates 123 head
blob requests and 5,882,040 returned payload bytes. The complete 154-row report
is unchanged. This contribution was produced by Nick Petalas.

The result is a tooling work reduction. No new kappa, supplier admission or
multiplication theorem is claimed. Independent human and formal proof-kernel
review are unclaimed.

## The change and proof

Let B be the resolved merge-base commit, H the resolved head commit, and C the
paths returned by the predecessor's `changed_paths(B,H)`. The scanner already
uses an immutable-tree diff with `--no-renames`, keeping modifications,
deletions and type changes. Let P be its merge-base pinners, obtained by the
unchanged full-tree digest search.

Every p in P exists at B. If p is absent from C, it cannot be an addition
relative to B. It also has no modification, deletion or type change. Its
blob bytes at H therefore equal its bytes at B. A move does not evade this
argument, because rename detection is disabled and its old path is a deletion.
The bytes already read at B can replace the second read at H.

The new code reads head bytes only for `P intersect C`. It uses the original
head reader for every changed pinner, including removed and repinned ones.
The base reads, digest search, target multiplicities, classification tests,
row construction, sorting and CLI exit expression are unchanged. Thus every
complete report and default/strict exit agrees on the predecessor's valid
input domain. The proof does not require distinct target digests.

```diff
- read head bytes for every pinner
+ read head bytes for changed pinners
+ reuse base bytes for unchanged pinners
```

The proof assumes valid, stable Git objects and the predecessor's supported
path/encoding contract. It does not preserve failures caused solely by a
redundant read of a corrupt or concurrently removed object. It introduces no
persistent cache, and it never reuses bytes across separate scans.

## Exact evidence

The canonical comparison is
`de5ec2e7a6074068452f45b1a191b5c72832df4a` to
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The scanner resolves the same
merge base, enumerates 39 modified/deleted files, and returns 154 pin rows.
Of these, 153 are stale living-record pins and one is repinned. The frozen
stale count is zero. These classifications are predecessor output preserved
by this change, not a new scientific audit of those records.

The observed `blobs` calls return these payloads:

| Phase | Original requests | Reuse requests | Original payload bytes | Reuse payload bytes |
| --- | ---: | ---: | ---: | ---: |
| Changed files at base | 39 | 39 | 20,664,306 | 20,664,306 |
| Pinners at base | 124 | 124 | 18,445,144 | 18,445,144 |
| Pinners at head | 124 | 1 | 19,620,947 | 13,738,907 |

These are actual requested specifications and returned blob payload bytes.
They exclude Git protocol headers, decompression work, filesystem reads and
process memory. The sole remaining changed pinner still requires a batch
process. The improvement is a reduction of work, not a process-count saving.

`verify.py` compares the complete report and instruments every blob-loading
phase. A separate synthetic Git history exercises unchanged pinners,
changed-but-stale pinners, repinning, removal, LF/CR filenames, two changed
targets with the same digest, an added pinner and an unchanged target. It
checks all twelve expected rows, all three states and both complete CLI
outputs/exit statuses, then the empty diff and three invalid adapter modes.
These tests check the new reuse choice, not the predecessor repair's full
admission obligations. All contracts use explicit exceptions and run under
normal and optimized Python.

## Reproduce

From a full-history checkout at this contribution, use CPython 3.12 and the
standard library. Substitute an installed interpreter path on another host.

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/pinned-edit-read-reuse
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/pinned-edit-read-reuse/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/pinned-edit-read-reuse/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/pinned-edit-read-reuse --check-source-history
```

The direct verifier prints `PASS_PINNED_EDIT_READ_REUSE` in a generated JSON
receipt with the actual counters, complete-report hash and package hashes.
It writes no result files and removes its synthetic repository. Set `TMPDIR`
to an external scratch directory when one is required. Each registered check
has a 300-second limit. Full Git history is needed for the canonical scan;
this is not a Git-free export replay.

The two exact standalone commands are selected through `run.py`:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/pinned-edit-read-reuse/run.py predecessor --base de5ec2e7a6074068452f45b1a191b5c72832df4a --head 7c49fe32c55de02c2c873655c804b16e4c3fef0a --json
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/pinned-edit-read-reuse/run.py optimized --base de5ec2e7a6074068452f45b1a191b5c72832df4a --head 7c49fe32c55de02c2c873655c804b16e4c3fef0a --json
```

The adapter selects only the two named modules, supplies the repository root,
and imports the same source-pinned `git_source_env` helper for each. It does
not alter the source-read policy. `predecessor.py` is an exact self-contained
export of PR6357's scanner at `170867c0a8f92375dfc489dd090bad5daee7b090`.
`SOURCES.json` records its URL and SHA256. That pending commit is not required
in local history. The exported bytes are committed here; no private object
cache or new Git ref is needed. `optimized.py` differs by the two reuse lines,
their explanation and the new contribution credit. Authentication enforces
that exact delta. Shared source files and frozen evidence are unchanged.

## Timing scope

The complete-command benchmark is `benchmark.py --output /absolute/scratch/path/result.json`.
It starts ten fresh interpreter processes, alternating five runs of each
implementation. Every run includes the full Git search and report output,
requires exit zero, rejects stderr and compares the complete stdout bytes.
The generated receipt binds its source files and records every timing,
platform, CPU count and final load average. It refuses to overwrite a result.
Timing is host-dependent and is not a CI acceptance condition.

The separate profiled baseline took 19.944 seconds. Its three `blobs` calls
consumed 0.189 seconds in total. This bounds the possible benefit from this
change on that run. The tree-wide digest search remains outside the changed
code. Other computations were running on the 18-CPU host; paired timing
therefore needs its measured spread, and no timing result is inferred from
request counts. See the generated `BENCHMARK.json` for the measured verdict.

The five alternating pairs gave overlapping ranges. The original median was
21.064 seconds, range 20.770 to 21.347; the reuse median was 21.403 seconds,
range 20.532 to 21.536. All ten commands completed without errors and produced
identical stdout. Timing is inconclusive. No runtime speedup is claimed.
The verifier authenticates the benchmark's source and complete-output hashes
and recomputes its summaries; it does not try to reproduce host timings in CI.

## Limits and implementation constraints

This package is opt-in. It neither installs the pending scanner in shared
`scripts/` nor adds an intake/CI gate. Digest formats, binary-file treatment,
advisory/frozen policy and the pending predecessor's remaining review status
retain their original scope. The selected frontier and all five framework
assumptions retain their status. No supplier replay, native/ownership,
compiler, precision/tape, analytic-recovery, Lean or Docker check is run.

There is no recursion or new persistent state. New functions fit within 60
physical lines. The verification domain is fixed to the named Git commits
and a fixture of three target files and six merge-base pinners. The benchmark
runs exactly ten commands, each with a 180-second timeout. Registered checks
bound the entire scanner process group through the existing replay launcher.

Power of Ten deviations are explicit. Rules 2 and 3 retain the predecessor's
repository-sized collections and managed-runtime allocations. The fixed
historical domain has 39 changed paths and 124 pinners, and the fixture has
five changed paths and six pinners. A general arbitrary-repository resource
contract would require a separate streaming/cap design before adoption.
Rules 8 and 9 permit loading the two exact source modules and a temporary
blob-observation callback in the checker. Module selection has two targets;
the callback has one target, belongs to one local module instance, and a
`finally` restores it on every exit. A future shared-library adoption should
replace this source-export adapter with a direct import. Rule 10 uses
warning-strict normal/optimized execution and AST function-length inspection;
no separate static analyzer or full native-platform suite is supplied. These
deviations concern this bounded offline package, not a production allocator
or universal scanner guarantee.

## Open next questions

Can the tree-wide digest search avoid decompressing repeated Git objects
while preserving text/binary classification and every substring match?
First specify an immutable blob-ID deduplication algorithm, expand its matches
back to all filenames and compare a complete historical report. Those
semantics remain the blocker; this package supplies no such implementation.
The question and its relevance are also recorded in `TASK.json`.

## Credit and coordination

This contribution was produced by Nick Petalas. Apache-2.0.
Armin Pourshafeie / apoursh, PR6319, supplies the scanner and its classification
policy. ToikY, PR6357, supplies the exact source-read repairs used here. Both
retain their original source notices. Credit Arham Tahir / PR1595 for the
shared batched-source-read lineage, the shared Git-source environment policy's
T74-2530 lineage and Douglas Colkitt, Sagar Thakrar and ywz65 for the credited
source/integrity tooling. No predecessor result is claimed as new.

The original `replay-runtime` card is refined to this new complete-scanner
work reduction. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19361579)
records its scope. Live open/account PRs, active Discussions, local claims,
main README searches and merged searches were checked. The cached scan had
incomplete sparse local-note coverage, so Git searches supplemented it.
These searches do not cover unpublished work and are not proof of novelty.
