# Deadlines for direct Git blob responses

The shared `git_blobs` reader now gives each complete request/response 90 seconds.
Previously its synchronous header, payload and terminating-newline reads could
block forever; the process-exit timeout was reached only after those reads.
The bound includes writing/flushing the request and the initial unsupported-option
decision. It ends before yielding the blob, so time spent by the consumer is
excluded. This is a tooling repair, not mathematical verification or a new κ.

One short-lived watchdog kills the direct Git process on expiry. The main thread
cancels and joins the watchdog, checks its expiry flag, and raises
`subprocess.TimeoutExpired` before any expired response can be yielded. It then
reaps the child through the existing cleanup. Normal malformed replies retain
their existing errors. The first-request/no-response/exit-129 fallback gate,
exact object IDs and payload framing, one-blob memory use, source pins and
selection policy are unchanged. There is no source cache or dependency change.

The reader serves package validation, catalogue reads, package scaffolding,
publication preflight and committed exports. This repair only covers their
`git_blobs` batch request/response boundary. It does not give those entire
commands a deadline. The separate `git()` helper (including legacy CR/LF-path
resolution), the older `git_source_rows`, and descendant processes retaining
pipe handles remain outside this bound. A direct-child kill cannot close a
descendant's inherited stdout. Partial-clone/promisor helpers and full process-tree
containment therefore need separate treatment. The 90-second bound is total
response time, not an inactivity timer; an unusually slow valid response can time
out even if it makes progress.

## Evidence and reproduction

Base and original reader: canonical main
`b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision 7;
`scripts/research_package.py` Git blob
`ad2f94e3d38c3167feb66b07cbe6c52192284d39`.
[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4681#discussioncomment-19130292).

The new tests substitute controlled real Python subprocesses at the Git launch
boundary; they do not claim an observed production Git hang. On the unchanged
reader, the no-header, partial-payload and missing-terminator controls all wait
for the fixture's independent three-second safety kill, then raise framing
errors instead of the required timeout. The original run fails all three
controls; the delayed exact binary response and suspended-consumer control passes.
After the repair all three bounded stalls raise `TimeoutExpired`, start no
fallback, consume no later object specification, and reap the direct child.
Files written after the fixture emits its chosen prefix establish that the
intended response boundary was reached rather than merely timing out at startup.

Further controls cover blocked request writes, a partial payload in the legacy
line protocol, delayed binary responses, and pausing the consumer longer than
the test deadline. A real Git process streams 128 small blobs with exact bytes
and no live watchdog thread at any yield or after completion. Existing tests
retain unsupported-option fallback, binary/empty/Unicode/CR-LF inputs, SHA256
object IDs, invalid/missing/non-blob requests, bounded retry, early close,
replacement-object rejection and exact path selection.

Run the focused tests normally and with Python assertions disabled:

```sh
python3.12 -B -W error::ResourceWarning -m unittest discover -s tests -p 'test_research_git_*.py' -v
python3.12 -O -B -W error::ResourceWarning -m unittest discover -s tests -p 'test_research_git_*.py' -v
```

All 37 focused tests pass normally (8.970 seconds) and under `-O` (8.983 seconds)
on macOS 27 arm64, Python 3.12.2 and Git 2.44.0, with resource warnings treated
as errors. The finite fixtures shorten the response deadline to 0.5 seconds (0.3 for the
delayed positive control); production keeps 90 seconds. Their three-second
independent safety kill bounds regression runs against the old code. The tests
require Git and the Python standard library. This is not a native Windows or
hosted CI claim. No full selected
replay, broad historical suite, Lean or Docker run is included.

An independent Codex agent reviewed the cancellation/yield ordering and protocol
scope. Its readiness-evidence recommendation is included in the tests. This is
AI-assisted review, not independent human acceptance.

## Open next questions

- Can the same boundary remain bounded when a descendant retains stdout? Start
  with a controlled child that spawns a pipe-holding descendant, then design
  process-tree containment without weakening one-blob streaming or early-close
  cleanup. POSIX groups and native Windows lifetime ownership need separate
  evidence; this patch does not supply it.
- Does composing this deadline with the pending Windows closed-pipe repair
  preserve `TimeoutExpired` at all native Windows cleanup boundaries? Apply
  both changes and run the real-process and closed-stdin controls on Windows.
  Native Windows access is required; no additional closed-pipe fix is claimed here.

## Source lineage and overlap

[PR #4686](https://github.com/CrocSwap/integer-mult-bounds/pull/4686), exact head
`de93ebd044d0b00a8647a9f47f86939a6b18b9aa`, repairs Windows closed-stdin errors
and explicitly leaves synchronous read deadlines separate. This patch is based
on main and does not copy that repair. Both touch adjacent lines of
`_git_blob_batch`; integration should retain its Windows error classification
and this deadline's cancel/join boundary.

Initial overlap covered 498 open PRs, 3,641 Discussion records and 5,860 local
notes. Only the older compatibility work and its explicit remaining deadline
limitation matched this question. Closed PR diffs and unpublished work were not
searched; these counts are search coverage, not proof of novelty.

Credit Nick Petalas for Git-version compatibility, Arham Tahir for pin batching,
Woklerx for streamed provenance and cleanup checks, Mihir Srivastava for the
Windows closed-pipe analysis, and Douglas Colkitt for the package contracts.
Their frozen evidence is unchanged. Prepared for Brian (JoyboyBrian) with
substantial OpenAI Codex assistance; Apache-2.0.
