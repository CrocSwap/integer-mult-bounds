# Repeatable owner-verifier workspaces

The registered checks for `half-stage-evacuation` and
`source-partner-residual-exchanges` now use a fresh temporary workspace on every
invocation. Previously, each passed once and then failed with `FileExistsError`
because its registration reused `{package}/_work/registered-check`.

This implements item 2 of [kumagi's released handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18978663).
The [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18978999)
records the scoped override of the `replay-runtime` card. This is a reliability
fix, not a speedup, supplier admission or new kappa.

## Change and evidence

Only the two CLI adapters/imports, their registered argument lists and
reproduction instructions change. Unused imports are removed. Both
`verify(work)` function bodies are byte-for-byte unchanged. Their input pins,
literal owner checks, exact moment calculations, three rejecting physical
controls and bindings to stored outer receipts remain.
The shared launcher, source archives, scientific inputs, pinned evidence and
selected record are unchanged.

Without `--work`, each CLI allocates a private temporary parent, passes a fresh
`check` child to the existing verifier, and removes the parent on success,
exception or catchable interruption. Explicit `--work /fresh/path` still retains
receipts and partial diagnostics. Existing directories, files and dangling
symlinks receive an argparse error with exit code 2, without invoking the proof
body or overwriting their contents. No existing workspace is deleted or reused.

At baseline `d8e0f83f00191df62174b641e9fff055c357f641`, two consecutive calls to
each unchanged registered command produced:

| Package | First call | Second call |
| --- | --- | --- |
| `half-stage-evacuation` | exit 0, 19.41 seconds | exit 1, `FileExistsError` |
| `source-partner-residual-exchanges` | exit 0, 17.35 seconds | exit 1, `FileExistsError` |

After the patch, both commands passed twice in the same checkout, with identical
stdout between repeats. The old in-package work directories from the baseline
were left in place. The full regression also gives each replay an isolated
temporary root containing preexisting sentinel data; after each run only that
unchanged sentinel remains. All four actual replays retain
`PASS_LITERAL_OWNERS_AND_EXACT_MOMENT` and the registered-package success marker.

Seven quick behavioral groups test both actual CLI entry points with only the
expensive proof body substituted. They cover repeated success, failure cleanup,
`KeyboardInterrupt` cleanup, explicit result retention, explicit failure
retention, existing-path refusal and registration arguments. These are lifecycle
tests, not independent implementations of the mathematics. Optional `--full`
executes both actual registered proof checks twice, without substitutions.

## Reproduce

From the repository root, using Python 3.12 and its standard library:

```sh
# Quick lifecycle regression and exact provenance/input checks.
python3.12 -B scripts/research_package.py --package research/owner-replay-workspaces

# Quick controls plus four real registered owner/moment replays.
python3.12 -I -Werror -B research/owner-replay-workspaces/verify.py --full

# Retain a real replay's diagnostics instead of deleting its temporary output.
python3.12 -B research/half-stage-evacuation/verify.py --work /fresh/absolute/check
```

The full mode normally takes about a minute on this host. It gives each child
command a 310-second timeout. The registered quick hook has a 60-second timeout;
the original registered verifiers retain their 300-second limits. The full mode
is separate because its transitive scientific inputs and checks are owned by
the two existing registrations, not inferred by the quick hook.

To reproduce the original failure, use a separate clean checkout at the pinned
baseline and run each original registered command twice. No special input or
search seed is needed. Historical CLI/manifest blobs and the selected-record
context are pinned as provenance in [SOURCES.json](SOURCES.json). Three unchanged
imported modules are live input pins. The four changed CLI/manifest files are
current declared inputs, not falsely bound to their old bytes.

Local checks used CPython 3.12.15 on Linux x86_64, WSL2. The seven quick groups
also passed on CPython 3.13.5. Ruff passed for the new regression; the replay
selection suite passed nine tests and onboarding passed 26. Both original
package metadata/source-pin checks passed after the change.

## Limits and engineering choices

Temporary mode deliberately discards diagnostics, including on proof failure.
Use explicit `--work` when retaining them matters. A hard kill, power loss or
process detachment can bypass Python cleanup. This is not a durable crash-recovery
or hostile-filesystem guarantee. Racing writers to an explicit path still meet
the existing exclusive `mkdir`; the friendly precheck is not a locking protocol.

No full native/global/outer cold replay, new arithmetic result, independent human
review, proof-assistant verification, native Windows run or hosted CI success is
claimed. The existing checks compare arithmetic bindings to stored full receipts;
that is not a fresh execution of those entire supplier chains.

Build the Lever produced the retained quick and full regression commands.
Prove It Works required the actual registered checks twice, not only mocked CLI
tests. Make Operations Idempotent led to fresh state per run instead of deleting
or trusting old workspaces.

Power-of-Ten inspection found the new CLI adapters are 12 lines each and the
new regression functions are at most 30 lines. Loops cover exactly two packages,
two repeats or three existing-path kinds. Explicit errors and unittest checks
remain active under optimization. The original proof bodies rely on assertions
and still refuse optimized execution.

Rules 3, 8 and 9 have managed-runtime/testing deviations in the regression:
Python allocates temporary objects, `runpy` loads two fixed local modules, and
`unittest.mock` substitutes one proof callback for lifecycle controls. The target
set is fixed, the seven external quick-test dependencies are declared, and
context managers release temporary state. The full mode uses four bounded
subprocess calls and no substitutions. Existing long proof functions and dynamic
source recovery are unchanged, outside this lifecycle repair. Reassess their
bounds separately before extending the scientific verifiers; no broader rewrite
is justified by this defect. Ruff's existing body-only `C408`/`I001` style and
`PLW1510` subprocess-default findings remain, without suppression. Those
subprocess return codes are checked immediately; inner subprocess deadlines
require a separate hardening change. This patch removes unused imports and
sorts top-level imports without changing either proof body.

## Open next questions

Run the same `--full` command on native Windows to check temporary-directory
cleanup with that platform's file-handle behavior. Symlink creation may require
privileges; the quick suite reports an unavailable symlink fixture as a skip,
not passed coverage. Linux execution cannot establish that platform result.
Structured scope, overlap and remaining work are in [TASK.json](TASK.json).

## Credit

Credit kumagi for discovering and releasing the handoff. The original packages
retain credit for mcorrigan, zxv, Jeremy Kothe, Philippe Van Velzen, Douglas
Colkitt and their predecessor chain. Their mathematics and source notices remain
unchanged. Nick Petalas. Apache-2.0. Assistance and review limits are recorded in
TASK.json.
