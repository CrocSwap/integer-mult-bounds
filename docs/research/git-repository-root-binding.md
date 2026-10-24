# Repository-local Git reads for research publication

The shared source and publication tools now remove inherited Git repository,
index, object-directory and command-line configuration overrides from their
**Git subprocesses**. Git discovers the repository from the supplied working
directory, including an ordinary linked worktree's `.git` file. Existing
stored-object checks still disable replacement refs. Parent-process and
package-verifier environments are unchanged.

## Hosted validation limitation

PR #5102 introduces working-source drift for the frozen
`research/isolated-descendant-bytecode` package: its `SOURCES.json` still pins
`scripts/check_research_commit.py` as an input, while this change updates that
checker. The current package's `--check-only` therefore rejects with
`working source drift: scripts/check_research_commit.py`. This is introduced
by this PR, not a pre-existing failure. Its frozen package, pins and replay
policy remain unchanged; this tooling repair does not establish a green
historical scientific replay.

The first hosted plan run (39932040857, job120342425789) reported eight test
failures. One standalone cp1252 overlap fixture omitted the new shared-helper
dependency; it now copies that dependency. Seven source-role assertions were
masked by the unrelated checker drift. Their disposable fixture now restores
the exact manifest-pinned checker blob, so they continue to test the intended
`research_package.py` and source-history-test role transitions, including
corrupt pins and unrelated input drift. This test setup correction does not
change the actual frozen package's rejection described above.

The affected 37 tests pass under normal and optimized Python after this fixture
follow-up (10 descendant-role and 27 onboarding methods in each mode). The
hosted planner command completes with 2,939 packages in 12 batches. The entire
408-test hosted suite and those scientific replay batches were not rerun
locally; hosted results remain separate from this targeted validation.

## Reproduced failure

At canonical base `81e9bd69e4a5b00ba9c713a1620e36d576d5522e`, two real
repositories suffice:

1. The intended repository has one checker committed at HEAD. Modify its
   working bytes without committing them.
2. A second repository has those modified bytes committed. Set inherited
   `GIT_DIR` to its Git directory (also reproduced with `GIT_WORK_TREE`).
3. Call the publication checker with the **intended** repository as `root`.

Without the environment override, the checker rejects the dirty bytes. With
it, Git resolves the foreign HEAD while Python reads the intended working
files. Their equality produces an incorrect publication success. Export also
resolves and exports the foreign HEAD. This is observable repository
misselection, not a hypothetical hostile verifier or a compressed-byte change.

The regression additionally constructs foreign live source pins in the
intended checkout. Those pins previously validated against the foreign object
store. After the fix they cannot pass as sources of the intended repository.
The original eight-method suite failed with five assertion failures and four
errors at the unchanged base; all eight pass after the repair. Subtests account
for multiple failures within a method.

## Policy and callers

`research_package.git_source_env()` returns a copy, removing:

- `GIT_DIR`, `GIT_WORK_TREE`, `GIT_COMMON_DIR`, `GIT_INDEX_FILE`;
- `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_NAMESPACE`,
  `GIT_CEILING_DIRECTORIES`;
- `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_COUNT`, and the
  `GIT_CONFIG_KEY_` / `GIT_CONFIG_VALUE_` families.

It retains the existing `GIT_NO_REPLACE_OBJECTS=1` policy. It does not rewrite
repository configuration, objects, refs, the caller's environment, or the
separate environment used to launch a package's verifier. Normal repository
configuration and on-disk linked-worktree/alternate-object topology remain
Git's responsibility. This is not a sandbox for an untrusted Git executable,
repository configuration, or concurrent repository modification.

The shared helper reaches:

| Consumer | Covered operations |
| --- | --- |
| Package scaffolding and catalogue lookup | Base resolution, pinned catalogue and input reads |
| Metadata validation | HEAD spelling, exact pinned blobs and working-byte comparison |
| Replay planning | HEAD/index inventories, sparse manifest reads and changed paths |
| Publication preflight | Commit resolution, file inventory, committed bytes |
| Package export | Committed manifest, inventory and payload objects |
| Source-history preflight | Committed source metadata and ancestry; its existing graft/shallow guards remain |
| Overlap local coverage | HEAD and note-tree inventory; its no-lazy-fetch setting remains |

The legacy line reader and the NUL reader/fallback use the same policy.
`find_overlap.py` imports the helper from its adjacent `research_package.py`,
including direct invocation under `-I`. Standalone copies of that tool need
both files; the helper has standard-library dependencies only. Existing CLI
fixtures now copy that closure.

Package-local workflows that intentionally use an external Git object store
inside their verifier remain unchanged. The shared publication/source APIs
use the repository provided as their root; inherited shell selection is no
longer an alternate way to override that argument.

## Validation

Environment: macOS/Darwin 27.0 arm64, CPython 3.12.7, Git 2.44.0. The eight new
real-Git methods cover dirty-publication rejection, foreign-pin rejection,
exported payload/commit identity, source history, all blob readers, scaffolding,
HEAD inventory, planning, overlap coverage, a real linked worktree, other
inherited selection channels, and unchanged parent/verifier environments.
They observe results before disposable fixture cleanup.

```sh
python3.12 -W error -B -m unittest discover -s tests \
  -p 'test_research_git_root_binding.py' -v
python3.12 -O -W error -B -m unittest discover -s tests \
  -p 'test_research_git_root_binding.py' -v
```

Targeted compatibility passes 143 methods in each mode: `test_research_git*`,
`test_research_source_history.py`, `test_research_commit_bytes.py`,
`test_research_export*`, `test_research_overlap*`,
`test_research_sparse_planning.py` and `test_research_plan_explanations.py`.
The normal run was split into 132 plus 11 methods; the optimized run was one
143-method run. No platform skips occurred on this host. Existing replacement
ref, binary/newline object, source-history, export, sparse-index and standalone
CLI checks remain intact. No scientific package replay or full archive suite
was run. Native Windows execution remains untested for this change.

The scoped committed source closure can run the new regression and standalone
overlap tests from a directory without `.git`; their temporary real-Git
repositories still require a Git executable. This is a Git-free **source
checkout**, not a claim of Git-absent tests. The registered research-package
exporter is not applicable to this shared-tooling change, which has no
`research/<package>/VERIFY.json`; use the exact committed files and record their
hashes. The final handoff records the actual archive and cold-run evidence.

## Open next questions

Native Windows can run the same real-Git controls without a POSIX-only fixture;
record that platform separately. General isolation of user/system Git config,
untrusted executables, concurrent writers, and package-specific external-Git
contracts is outside this repair. No further construction or mathematical
replay follows from a publication transport fix.

## Credit

Prepared by JoyboyBrian with substantial OpenAI Codex assistance; Apache-2.0.
The environment policy is adapted from the existing package-local
`research/t74-2530-source-partner-audit/audit_common.py` (introduced at
`feb727ba471b5dc3f057f867804aa70ae58b2e71`); that prior isolation technique is
not new here. Retains Douglas Colkitt's shared runner/scaffold, Tekalign's
exporter, Nick Petalas's PR3304 source-history checks, and roger-sato's
stored-object policy at `1a885a3546cd68995be448e2ca91f28cc23ec155`.
The new contribution is the shared explicit-root failure reproduction,
consistent caller repair and compatibility evidence.
