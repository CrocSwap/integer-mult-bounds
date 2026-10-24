# POSIX ownership of shared Git blob readers

A response deadline that kills only `git cat-file` does not bound a pipe read
when an ordinary descendant retains stdout after Git exits. The pre-change
reader reproduced this with actual processes: a controlled Git launcher exited,
its ready child retained the response pipe, and the read remained blocked after
a 0.7-second deadline until the outer 2-second test guard intervened. A launcher
without that child rejected promptly. This is a process-boundary reproduction,
not evidence that an installed Git version spontaneously exhibits this behavior.

The shared `git_blobs` reader now starts each POSIX batch process in its own
session. Its response watchdog and generator finalizer share an idempotent stop
operation that sends SIGKILL to that process group, including after leader exit.
An exited leader is reaped before signaling; this avoids macOS EPERM for a group
containing only its unreaped zombie. The watchdog is cancelled and joined before
control returns to the caller, so the finalizer and watchdog do not race their
stop operations. Finalization stops the group before closing buffered streams.
Normal completion, malformed responses and early generator close use the same
ownership path. Non-POSIX retains its existing direct-child behavior.

The stop action does not alter authenticated bytes, source roles or Git
repository selection. Streaming still retains one blob, and the deadline ends
before yielding it: a slow or suspended consumer is not charged as a slow Git
response. The unsupported-NUL fallback still requires the first request, no
response and exit 129; it retains the original request and exact legacy framing.
Live-input drift continues to reject, including old research packages whose
historical helper pins differ from today's shared code. This repair neither
repins those artifacts nor makes their historical replay green.

## Actual consumers

All production calls share this one reader:

| Consumer | Blob use | Compatibility checks |
| --- | --- | --- |
| `research_package.validate` | Source-pin objects | Git compatibility, replacements, root-binding suites |
| `research_package.planning_manifests` | Sparse HEAD manifest objects | Sparse-planning suite |
| `new_research_package.create` | New package source pins | Scaffold-batch suite |
| `check_research_commit.check` | Committed package/input bytes | Commit-bytes suite |
| `export_research_package.inventory/export` | Committed manifest and archive bodies | Export suite |

The older `git_source_rows` helper, individual `git()` calls, HEAD inventory
commands and history-helper subprocesses are separate boundaries. This change
does not silently extend their deadlines. No frozen historical runner is edited.

## Validation

The dedicated test module launches the actual shared reader in an independently
bounded worker. A real child writes its PID/readiness file before the simulated
Git leader exits or responds. Tests inspect that readiness and stopped process
state before fallback fixture cleanup. An adopted zombie counts as stopped,
not as a running descendant. The direct-child-only semantic mutant still blocks
past the external guard with the descendant alive, so teardown cannot manufacture
a passing cleanup result.

Six test methods cover header, partial-payload, terminator and blocked-write
stalls; successful and malformed responses; early generator close with a live
leader; consumer suspension longer than the response deadline; exact binary
legacy fallback; and the direct-child-only mutant. The existing closed-stdin
fixture models the new POSIX operation while retaining native-Windows-compatible
simulation; it does not pretend to test Windows process groups.

Local validation uses CPython 3.12.7 on macOS arm64, with warnings as errors:

```sh
python3.12 -W error -B -m unittest discover -s tests -p 'test_research_git_*.py' -v
python3.12 -W error -B -O -m unittest discover -s tests -p 'test_research_git_*.py' -v
```

Also run each of `test_research_scaffold_batch.py`,
`test_research_commit_bytes.py`, `test_research_sparse_planning.py` and
`test_research_export.py` with the same normal/optimized discovery commands.
All 57 Git-reader tests passed normally (19.963s) and optimized (21.260s),
and all 35 caller tests passed in each mode. A fresh committed three-file source
snapshot, without `.git` and with only the `ps` observer on PATH, passed all six
descendant tests normally (9.589s) and optimized (10.767s); every source hash
remained unchanged. This is a focused tooling snapshot, not a registered research
package export. An earlier sandboxed optimized attempt denied the `ps` observer;
the final optimized run used process-observation permission. That denied attempt
is not counted as passing evidence.

These real-Git checks cover exact binary transport, drift rejection, linked
worktrees, retained source authority, sparse planning, immutable publication
bytes and Git-free export integrity. They are tooling checks, not mathematical
replays. No full selected, historical all-suite or heavy scientific run is used.

## Boundaries and open next questions

The contract covers ordinary POSIX descendants that remain in the owned process
group and retain the caller's signal permissions. It does not contain escaped
sessions/groups, privileged children, uninterruptible kernel operations, or an
abruptly killed outer Python process. Windows descendant ownership and native
Linux execution are unverified here. Individual Git commands and the legacy
reader still need separate bounded ownership work if their concrete callers
require it. A platform-specific ownership implementation must preserve the
streamed protocol and consumer-suspension boundary before extending this claim.

This takes the explicitly deferred descendant boundary in
[the shared blob-response deadline handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/4681#discussioncomment-19130292).
The source reader, immutable-object policy, fallback and deadline work retain
their original attribution, including Douglas Colkitt, Nick Petalas, Arham Tahir,
Woklerx and Mihir Srivastava. The process ownership repair and regression evidence
were prepared by JoyboyBrian with substantial OpenAI Codex assistance;
Apache-2.0. No independent human or formal proof-kernel review is claimed.
