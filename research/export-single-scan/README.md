# Reuse the archive index during offline input checking

This contribution was produced by Nick Petalas.

The complete offline `check --check-inputs` command takes **7.46% less median
wall time** on the recorded 529-file export, from 59.396417 ms to 54.964250 ms.
All 90 complete commands succeed and emit identical output. Each of the nine
paired batches improves. This is a measured tooling improvement with a scoped
equivalence argument and finite conformance evidence. It supplies no new
mathematical theorem, native supplier or kappa.

The smaller 82-file export gives medians of 40.495792 and 40.073833 ms with
overlapping ranges and one losing paired batch. That comparison is inconclusive.
The reported gain applies to the larger workload on this host.

## Change and equivalence argument

The old checker opens the tar, hashes each member and checks the receipt, then
closes it. Declaration checking opens the same path again; `getmember` loads
every header into a second tar index before rereading `VERIFY.json`.

The changed checker keeps the first handle open through declaration checking.
Its completed iteration has already populated the index. `getmember` therefore
uses that index and rereads only the manifest payload. The reread still has to
match the size and SHA256 recorded during integrity checking. All receipt,
path, tree, mode, hash, JSON, declaration and inventory predicates are retained.
The direct `check_declared_inputs(path, receipt, seen)` call still opens and
closes its own handle. A caller-supplied handle is borrowed and remains open.
The outer command owns its handle and closes it on success and exceptions.

For a stable finite archive, the first scan produces the same member sequence,
payload hashes and receipt. Receipt validation is unchanged. The old second
scan and the retained first index describe the same members, so they locate
the same manifest. The exact same payload and declaration predicates then
return the same full receipt or rejection. The changed program removes one
header scan, without caching payload hashes across invocations. This is a
source-level argument, supported by the complete-outcome differential fixtures;
finite tests alone do not prove equivalence for every archive.

Archive mutation during checking is outside this stable-input equivalence
claim. The retained same-handle reread detects an in-place manifest change after
hashing. Reusing one handle also avoids switching to a different file merely
because its pathname is replaced. It does not provide a filesystem snapshot.
There is no new extraction or Git-provenance claim.

## Measurements

The primary fixture is the official committed export of
`research/p104-designer-toolkit-v2` at
`a5bff3bf133e482541c09eba4e773884bdb2b1b7`: 529 payload files, 13,701,120 archive
bytes, and zero external declarations. The command still performs manifest
schema and declaration-coverage validation. The secondary fixture is the
82-file `research/final4610-independent-admission` export, with 51 declarations.
These packages are workload bytes only; their scientific verifiers were not
run or audited for this contribution.

[BENCHMARK-toolkit.json](BENCHMARK-toolkit.json) and
[BENCHMARK-small.json](BENCHMARK-small.json) are generated raw observations.
Each has nine alternating pairs of batches, five fresh complete CLI processes
per side per batch, with the starting side alternating by pair. Timing includes
startup, imports, archive I/O, validation and output capture. Every process has
Git absent from PATH. Output equality, zero errors and unchanged archive hashes
are checked. There are 45 observations per side per fixture, 180 commands total.
No timing assertion is imposed on CI.

The primary before range is 58.337125 to 61.354625 ms; the after range is
53.355958 to 56.586834 ms. Measurements use CPython 3.12.15 on macOS 27.0.1
arm64, with 18 logical CPUs and load averages recorded in each observation.
Concurrent work was present and could not be stopped; alternating pairs expose
both sides to that load. The gap exceeds the observed primary ranges.

An untimed `cProfile` run attributes about 10 ms of its 73 ms total to the old
declaration check, chiefly the second header scan. Profiling overhead is excluded
from the benchmark. Imports, path/tree checks and payload hashing remain costs
of the complete command. Removing that measured stage is consistent with the
4.432167 ms complete-command median reduction; no microbenchmark ratio is used.

## Reproduce

From the repository root, using the standard library and CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/export-single-scan/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/export-single-scan/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/export-single-scan
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/export-single-scan --check-source-history
```

Replace the interpreter path with another CPython 3.12 installation if needed.
The direct verifier authenticates the retained original source, compares full
accepted receipts and rejection type/message, validates recorded timing
arithmetic and checks the generated source-bound [RESULT.json](RESULT.json).
Its 44 finite archives cover receipt position, executable modes, payload counts,
malformed declarations, missing and extra inputs, and corrupted content, with
default and declaration-enabled checking. The registered commands additionally
run the complete exporter regression suite in normal and optimized Python.
The direct comparison has 67 accepted and 21 rejected outcome pairs. Each
exporter suite runs 46 tests, with 45 passes and the existing native-Windows-only
publication test skipped on macOS. Four new tests cover one-open completion,
failure cleanup, borrowed-handle ownership and real post-hash manifest mutation.

To repeat the performance measurement, choose fresh external paths:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/export_research_package.py export --package research/p104-designer-toolkit-v2 --ref a5bff3bf133e482541c09eba4e773884bdb2b1b7 --output /tmp/toolkit-benchmark.tar
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/export-single-scan/benchmark.py --archive /tmp/toolkit-benchmark.tar --output /tmp/toolkit-benchmark.json
```

The baseline directory contains the two exact original scripts needed to run
the old CLI, retaining their notices. [SOURCES.json](SOURCES.json) binds them
to the base Git blobs and SHA256 values. The benchmark never replaces outputs.
Receipt regeneration uses `verify.py --emit-to NEW_EXTERNAL_FILE`; ordinary
verification is read-only apart from private temporary fixtures.

## Scope and credit

Card `replay-runtime`, priority revision 8, is refined to one standard transport
check before replay. The selected binding-only baseline passed. Scientific base
and selected source bindings are pinned in [TASK.json](TASK.json) and
[SOURCES.json](SOURCES.json). The selected frontier and its five assumptions are
unchanged. Lean, Docker, selected scientific replay, mathematical predecessor
audits, native Windows execution and cross-platform timing were not run.
Independent human and formal proof-kernel review are unclaimed.

Credit Tekalign / PR3138 for the exporter; Ali Romman / PR5744 and PR5728 for
declared coverage and typed metadata; roger-sato / PR3629 and PR3641 for path
and tree checks; Mihir Srivastava for portable fixtures;
josecarlosgonzalezroque-design / PR6189 for Windows publication; and Douglas Colkitt and the retained
Git-reader contributors. Original notices and source bytes are unchanged.
The new contribution is archive-index reuse, its lifecycle controls and measured
complete-command effect. New work is Apache-2.0.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19272236)
records the target. Live open and merged PRs, recent account work, handoffs,
local reservations and distinctive main README searches were checked. The
overlap cache had complete remote pagination for 310 open PRs and 5,907
Discussion records, but omitted 8,534 main-tree local notes. Additional targeted
main and merged-PR searches address this object. Unpublished work and arbitrary
historical diffs remain outside coverage. No novelty guarantee is inferred.

## Open next questions

Does the same change improve complete-command time on Linux and Windows, or on
larger real exports? Start with the pinned official export and the same
alternating benchmark. Native host measurements are the missing evidence; the
macOS percentage is not a portable performance guarantee. No further optimization
or follow-on target is reserved.

## Implementation constraints

The changed checker has structured, nonrecursive control flow and functions
under 60 physical lines. It uses one owned archive and one scoped manifest
stream; borrowed handles use `nullcontext`. Returned counts and CLI failures
are checked. Resource ownership, missing inputs, direct-call fallback and
changed-manifest rejection have explicit regressions. Warning-strict normal and
optimized tests and in-memory compilation supply diagnostics; no external
Python linter was available. The package harness is bounded to 44 archives,
at most 31 external files per archive and 20 benchmark pairs of ten processes
per side. Each process has a 60-second timeout.

Power of Ten rules 2 and 3 have a retained finite-file API deviation in the
shared checker. Tar traversal ends at the finite input's EOF, and payload reads
end at each member's declared extent; no new fixed archive-size cap is imposed.
Imposing one would narrow the existing accepted domain. CPython, `tarfile`, JSON
and hashing allocate dynamically. The member inventory is bounded by the finite
archive, while manifest and receipt reads retain their 16 MiB bounds and input
declarations retain their 100,000-entry bound. The changed path retains one tar
index instead of building two sequential indexes. Fixed-capacity operation and
concurrent filesystem mutation require a separately specified interface before
any service with those requirements is built. The finite conformance and full
exporter suites are the compensating checks for this change.
