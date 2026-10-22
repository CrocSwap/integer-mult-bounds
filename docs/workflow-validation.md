# Validate workflows before publishing a branch

GitHub parses every workflow on a new head, including manual-only workflows and
jobs disabled by a repository condition. A syntax or expression-context error can
therefore produce a failed run with **zero jobs**. A rerun of the same head does
not repair the YAML. Workflow validation is a tooling check, not a scientific
replay, ledger reconciliation, certificate verification, or theorem approval.

## One-time tool installation and everyday checks

Python 3.10+ and Git are needed. The standard-library installer downloads
[actionlint 1.7.12](https://github.com/rhysd/actionlint/releases/tag/v1.7.12)
from its official release and verifies the platform-specific SHA-256 pinned in
`.github/actionlint.json` before writing the executable. Linux and macOS on
amd64/arm64 are supported. It only writes to the directory explicitly supplied;
it does not change shell profiles, Git settings, or existing hooks.

```sh
python3 scripts/install_actionlint.py --directory "$HOME/.local/bin"
export PATH="$HOME/.local/bin:$PATH"
# Includes uncommitted changes, and every .yml/.yaml workflow, not just a diff.
python3 -B scripts/check_workflows.py
# Validate the actual committed tree before publication.
python3 -B scripts/check_workflows.py --ref HEAD
python3 -B -m unittest discover -s tests -p test_workflow_validation.py -v
```

An existing exact-version binary can be supplied with `--actionlint /path/to/actionlint`.
For other operating systems, install the same version using its official
[installation guide](https://github.com/rhysd/actionlint/blob/v1.7.12/docs/install.md).
A missing/wrong-version linter, missing workflow directory, Git read failure,
invalid YAML, invalid expression or disallowed expression context fails closed.
The validator copies workflow and local-action metadata into an isolated temporary
project. Worktree mode uses tracked and non-ignored untracked source files; it does
not import ignored build/dependency trees or Git/worktree administrative files.
Symlink source paths are rejected explicitly rather than silently bypassing
local-action metadata checks. For local JS/Docker actions, empty placeholders preserve regular-resource
file existence without reading or executing their contents. Reusable-workflow
inputs and local-action metadata are checked in this project context. It never
runs workflow commands, changes the checked-out branch, or loads repository-specific
ignore rules. Exact-object reads disable Git replacement refs, so a local object
replacement cannot disguise the tree that will actually be published. Native actionlint checks remain enabled without error suppression.
The optional external ShellCheck/Pyflakes integrations are disabled deliberately:
this gate covers workflow syntax and semantics independently of those tools.

`Workflow validation / workflow-lint` runs on every push and pull request, with
no branch, path, or repository-name filters, and can also be dispatched manually.
It validates the complete checked-out Git tree and runs real-linter regression
tests, including the original P112 job-level `env.TMPDIR: ${{ runner.temp }}`
failure. A push run identifies the exact published head; a pull-request run may
validate GitHub's synthetic merge commit, so record which one was tested.
No branch protection, repository permissions, or existing replay triggers are
changed by this tooling. Maintainers may separately decide whether to require
this check. Always confirm that a real job ran at the expected head; an absent,
skipped, pending, or zero-job run is not a lint pass.

## Opt-in pre-push guard

No hook is activated automatically. First inspect any existing hook configuration
and hook file; do not overwrite an existing hook or bypass it. A configured
`core.hooksPath` replaces Git's default hook directory for **all** hook types.
If an existing hook framework is in use, add the validator to its existing
pre-push chain while preserving the same four-column stdin for every consumer.

```sh
git config --show-origin --get core.hooksPath || true
git rev-parse --git-path hooks/pre-push
```

For a repository without existing hooks, opt in with an **absolute path** to a
stable tooling checkout containing `.githooks`, `scripts/check_workflows.py`, and
`.github/actionlint.json`. Keep that tooling checkout at a reviewed commit and
make the pinned actionlint binary available on PATH. For example:

```sh
# Run in the repository whose pushes should be checked.
tooling=/absolute/path/to/reviewed-tooling-checkout
git config --local core.hooksPath "$tooling/.githooks"
```

This is an explicit user choice, not a command run by the installer or CI. It
changes only that repository's configuration (shared by its worktrees), not
other repositories or global Git configuration. Keep the tooling checkout
separate when research branches predate the guard; a relative `.githooks` path
would disappear when switching to such a branch. Do not remove or move the
tooling checkout while it is configured. To remove this opt-in, inspect the
current value first, then unset that value and restore any previous setup.

The hook validates the local object IDs Git actually intends to push, even when
a different branch is checked out or a worktree has an uncommitted fix. It checks
all non-deletion updates, including new branches and annotated commit tags, and
fails the push if any fail. Deletion-only pushes have no new tree to lint. Tags
pointing to non-commit objects are rejected. Hooks can be bypassed by `--no-verify`
and are not invoked by GitHub/API writes; those publication paths must run the
same validator against the exact prepared tree and then verify remote CI.

## New research branches from an intentionally frozen base

Refresh and read canonical guidance using the
[agent checkpoint procedure](research/agent-procedure.md#looping-agents-refresh-upstream-at-each-research-checkpoint).
Do not reset, rebase, or edit another worker's in-progress branch. Create a new
isolated worktree, pin the scientific starting commit, and record any separate
tooling overlay in the PR. Fetching a corrected fork main does not automatically
correct a new branch created from an older upstream commit.

```sh
git fetch --no-tags https://github.com/CrocSwap/integer-mult-bounds.git main
research_base=$(git rev-parse FETCH_HEAD)
# Read the fetched guidance and compare priorities before choosing the base.
git show "$research_base:AGENTS.md"
git show "$research_base:autoresearch.md"
git show "$research_base:CONTRIBUTING.md"
# Use a new branch name and an unused worktree path.
git worktree add -b audit/your-scoped-task ../your-scoped-task "$research_base"
cd ../your-scoped-task
python3 "$tooling/scripts/check_workflows.py" --repo "$PWD" --ref HEAD
```

As of 2026-10-19, canonical main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`
still contains the invalid P112 job-level runner context. The workflow-only
correction is reviewed commit `89031d21f01f8b676f87c76443f5afc41457a17c`,
merged in [fork PR #8](https://github.com/Clear1nsight/integer-mult-bounds/pull/8)
and proposed in [upstream PR #3885](https://github.com/CrocSwap/integer-mult-bounds/pull/3885).
It writes `TMPDIR` from `$RUNNER_TEMP` into `$GITHUB_ENV` in the first step.
Check the current tree and PR state; do not assume this temporary overlay remains
necessary forever. When it is missing and CI changes are within the branch's
approved scope, inspect and apply that **single** reviewed commit:

```sh
p112_fix=89031d21f01f8b676f87c76443f5afc41457a17c
git fetch --no-tags https://github.com/Clear1nsight/integer-mult-bounds.git "$p112_fix"
git show --stat "$p112_fix"
git show "$p112_fix" -- .github/workflows/p112-common-slice.yml
git cherry-pick -x "$p112_fix"
python3 "$tooling/scripts/check_workflows.py" --repo "$PWD" --ref HEAD
```

If the correction is already present, skip it. If it conflicts, stop and review
the actual difference; do not overwrite the workflow wholesale or repin research
inputs. The same rule applies to adopting this safeguard: cherry-pick only the
reviewed guard commit(s) if the branch's scope permits tooling changes. Otherwise
run the validator from the separate tooling checkout and report the blocker for
a separate tooling PR. In particular, branches explicitly excluding CI changes
must remain untouched until their owners approve a scope change.

Keep `research_base`, selected-result pins, `upstream/`, frozen source archives,
original intake history, historical receipts and contributor credits unchanged.
A tooling overlay is a separate commit, not an update to scientific evidence.
Before pushing, validate the final committed tree. After pushing, verify the
remote SHA and successful nonzero-job workflow-lint run for that SHA. Report
workflow lint separately from any scientific replay, including failed or unrun
replay stages. Do not alter evidence or relax mathematical checks to make CI green.

## Updating the linter

Review the official release notes and asset digests; update the version and all
supported checksums together. Run the full workflow lint and guard regression
suite, including negative controls, before publishing the update. A green check
at an older head is not verification of the update.

## Current integration repair (2026-10-22)

The upstream PR #4548 planning failure came from four selected-result navigation
checks after integration with main at
`f626db5c3a3d781d8f7695038776c621651f75e1`. The current CI guide now follows the
selected record's #4359 command and evidence links. The status page separates
the selected decimal from its fraction and places the history banner before
the first historical checkpoint. Neither the selected record nor its evidence
is changed.

These documentation edits select four registered packages. This branch reuses
the historical adapter, source-role repairs and six rejecting/positive tests
from [PR #4542](https://github.com/CrocSwap/integer-mult-bounds/pull/4542), exact
predecessor head `af86fb28f4fe039d4bb8419850af99a6fc474587`:

- D8 assignment and navigation documents retain their original blob and SHA256
  authentication as provenance; the mathematical reference remains a live input.
- PR3563's #1042 finding runs the original verifier, tests and receipt against
  its authenticated historical snapshot. Its previous-record assertion applies
  to that snapshot. The current status tests separately check current navigation.
- The locale replay authenticates the historical status text as provenance and
  still executes its full declared checks against the current documentation.

All original invalidation paths remain declared. Original verifiers, result
receipts, mathematical inputs and source hashes are retained. The fourth
package, `k8-three-coordinate-temporal-seed21`, is replayed without changes.
Upstream execution exposed one fork-only publication reference in the reused
adapter. It now reads the byte-identical manifest at canonical upstream
introduction `d11655a9fd1c7eedc52e0e9720158bd17d29192a`; the original manifest
blob guard is unchanged. An additional test requires this pin to be reachable
from HEAD, preventing an unrelated cached fork object from hiding missing
upstream history.
Report hosted workflow outcomes against the final pushed SHA; these repairs
do not establish a new scientific result.

Prepared with OpenAI assistance. Apache-2.0.
