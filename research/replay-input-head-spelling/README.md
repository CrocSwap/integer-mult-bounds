# Exact Git spelling for replay inputs

This repairs the shared input-identity boundary requested by Arham Tahir's
[PR2994](https://github.com/CrocSwap/integer-mult-bounds/pull/2994), head
`900ab6c9e1f9cc5dcc1ca93ed7db966e7cf883a5`. That audit reproduced complete
metadata acceptance followed by omitted replay on a native case-insensitive
macOS volume. This contribution supplies the repair and portable Git/CLI
controls, not another native reproduction or a new supplier result.

```diff
 validate input / plan replay
- accept a lexical path, then trust filesystem existence or exact diff matching
+ require exact membership in the current HEAD tree
+ permit exact changed paths in planning so removed inputs still select replay
```

## Contract and correction

`tracked_input_paths` reads `git ls-tree -r --name-only -z HEAD` once per
validation/planning invocation. The immutable set retains exact UTF-8 names,
including embedded whitespace. There is no case folding, Unicode normalization,
filesystem-name scan, index substitution or persistent cache.

- Validation requires every declared `VERIFY.json` input to belong to that set,
  then retains the existing present-file, containment and source-pin checks.
- Planning permits `HEAD` names plus the exact Git-reported changed names.
  If an input was removed or case-only renamed, its old name remains eligible
  and its intersection with the diff selects its consumer.
- Untracked and staged-only inputs must be committed first. The index cannot
  redefine `HEAD` identity. This is an intentional tightening of local usage.
- A stale declaration absent from both `HEAD` and the current diff is an error,
  even during unrelated changes. No incomplete matrix is published. Update or
  remove obsolete declarations before running the selected package.
- These shared boundaries require a valid Git checkout and `HEAD`. Direct
  standalone verifiers keep their existing source-export contracts. Git errors,
  a 30-second listing timeout and invalid UTF-8 propagate as failures.

The planner's `changed` argument remains trusted Git output, as supplied by
its CLI. Arbitrary caller-provided names are not authenticated by set membership.
The checkout and its metadata must remain stable during planning and validation.
This is not a concurrent-writer or hostile-repository security boundary. It does
not establish that two distinct tracked names cannot alias physically on a
particular volume; the repaired failure has a declaration absent from the Git
inventory.

This implements identity at the Git-diff boundary rather than trying to enumerate
filesystem aliases. PR2986's separate symlink-component repair is not imported
or modified. A symlink-parent alias absent from the Git tree is also rejected
by this contract; the other filesystem/permission concerns retain their scope.

## Evidence and reproduction

From the repository root, with Python 3.12 and Git:

```sh
python3.12 -B scripts/research_package.py --package research/replay-input-head-spelling
```

The source-bound reproducer retrieves the original main runner from
`836b19bfa309ceafbc8ee32a15e8c4b10dde7e11`, verifies its Git blob and SHA256,
and runs it and the live runner in disposable Git repositories. Each comparison
uses an actual commit changing only `src/dep.json`.

| Declaration | Authenticated main | Repaired runner |
|---|---|---|
| `SRC/dep.json` | exit 0, empty matrix | exit 1, no matrix |
| `src/DEP.json` | exit 0, empty matrix | exit 1, no matrix |
| `SRC/DEP.json` | exit 0, empty matrix | exit 1, no matrix |
| `src/dep.json` | selects exactly its consumer | selects exactly its consumer |

Expected marker:

```text
PASS_REPLAY_INPUT_HEAD_SPELLING baseline_omissions=3 repaired_rejections=3 canonical_controls=2
```

On this Linux case-sensitive volume, the old planner omission is directly
reproduced. The predecessor's old *full metadata acceptance* on a case-insensitive
volume remains credited to PR2994, not inferred from this run.

The registered replay also runs all nine new behavioral groups and all five
retained lexical-input groups. The new controls cover:

- All three case aliases against the same target-only diff and canonical repair.
- Complete source-pinned metadata with an extra, unpinned VERIFY dependency.
- Canonical inputs, unrelated changes, deleted inputs and deleted parents.
- Both exact consumers of a case-only rename, using a removal/addition diff.
- NFC/NFD spellings without normalization. The positive spelling is read from
  the actual tree, so the fixture does not assume a filesystem's Unicode form.
- Names with spaces, tabs, CR and LF through NUL-delimited Git output.
- Untracked and staged-only rejection, followed by acceptance after commit.
- Missing repository metadata and missing `HEAD`, preserving existing workflow-output bytes.
  The latter reaches `ls-tree` after `ls-files` succeeds.

The regression file failed on unchanged main before the guard was added. The
canonical controls keep the same diff, excluding Git diff construction as the
cause. The surviving mechanism is the lack of a shared Git-spelling check before
filesystem lookup and string intersection.

The original main runner is historical provenance, not a pin that prevents the
live implementation from evolving. No frozen source is copied or changed.

## Verification limits and engineering notes

Local execution uses Linux x86_64/WSL2, CPython 3.12.15 and 3.13.5, Git 2.47.3.
The registered replay passes. The full research-tooling suite runs 167 tests,
with 11 platform-specific skips; the nine new groups also pass under optimized
3.12 and 3.13 with warnings treated as errors. All 1,136 registered package
inventories pass the all-input planner. Selected-record and selected CI
input/trigger checks pass. New test/verifier lint passes. The source-bound
replay also runs with optimization enabled. Native macOS and
Windows execution, hosted CI and a complete selected cold replay are not claimed.
No supplier, selected frontier, source archive, mathematical invoice or kappa
changes. The implementation and evidence are author-checked, not independently
human-reviewed or formally verified.

The two new helpers are nonrecursive and under 20 lines. Loops consume finite
Git/input collections, the Git process has a timeout, and rejection checks do
not depend on assertions. Python allocation remains dynamic for the finite
filename set. There is no adversarial output-memory cap. A future hostile-input
contract would need streaming size limits, not a claim of fixed-capacity memory.
The existing long `validate` function is not split by this repair; an independent
metadata refactor would need the same behavioral suite. Existing shared-runner
lint findings in imports, a regex alias and unrelated native cleanup are retained;
new helper/test/verifier code introduces no additional lint findings.

## Scope and credit

Base main `836b19bfa309ceafbc8ee32a15e8c4b10dde7e11`, priority revision 6.
The picker drew verifier engineering with nonce
`4a19fc67d66cb777341571b198635167`. [TASK.json](TASK.json) records the explicit
scope/method change to this fresh handoff, predecessor heads and overlap limits.
[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2983#discussioncomment-18978476).

Credit Arham Tahir for PR2994's native counterexamples and contract handoff;
Nick Petalas/PR2986 for the distinct symlink repair following EdDiboi's earlier
finding; woklerx/PR1891 for lexical input checks; Charles Bethin for replay
selection controls; Douglas Colkitt and the retained runner/scaffold authors.
The exact predecessor and scientific source notices remain intact. New work by
Nick Petalas, Apache-2.0.

## Open next questions

Run the registered replay on native case-insensitive macOS and Windows to check
platform execution, especially actual Git Unicode spelling and case-only
renames. These tests are already bounded and require no new mathematical work.
Native hosts were unavailable here; Windows intentionally skips filenames its
filesystem forbids. There is no justification for another alias census before
that platform check. Structured details are in [TASK.json](TASK.json).
