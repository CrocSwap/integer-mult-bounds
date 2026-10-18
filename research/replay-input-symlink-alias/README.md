# Reject symbolic-link aliases in replay dependencies

A declared input behind a directory symlink can pass file validation while
evading replay selection. At canonical main
`f1de0c136a6d897332c63eb00b02bcc15e696b31`, let `alias -> src` and declare
`alias/dep.json`. The old `relative_file` accepts the input. Changing only
`src/dep.json` then produces an empty plan, because Git reports the target path.

The shared runner now rejects existing symbolic-link components below the
repository root during metadata validation and planning. Declare the target's
repository-relative path instead. Missing components remain permissible during
planning, so deleting a file or its parent still selects its consumer. Other
filesystem errors propagate. No frozen source, selected result, scientific
certificate or supplier changes.

## Evidence and reproduction

```sh
uv run --python 3.12 --no-project python -I -B scripts/research_package.py \
  --package research/replay-input-symlink-alias
```

`verify.py` authenticates the historical runner against the exact Git blob and
SHA256 in `SOURCES.json`, executes its source without a bytecode cache, and
reproduces both the accepted alias and the skipped target change. On the same
fixture, it checks successor rejection, canonical-path selection and selection
after deleting the input directory. Expected marker:

```text
PASS_REPLAY_INPUT_SYMLINK_ALIAS before=accepted-and-skipped after=rejected deletion=selected
```

The registered replay also runs nine new behavioral groups and five retained
lexical-path groups. They cover full metadata, parent/leaf links,
dangling/cyclic/external links, missing children under links, deleted parents,
a parent replaced by a regular file, and injected EACCES/EIO at both parent
and leaf components. Additional `VERIFY.json` dependencies need not also be
`SOURCES.json` input pins, so provenance checks alone cannot reject this alias.

The actual Git control commits the alias manifest, changes only its target,
and runs the copied CLI under `-I -O -B`. Rejection returns exit 1, writes no
matrix to stdout and preserves a preexisting GitHub-output file. After a
separate commit repairs the manifest, another target-only commit selects
exactly its consumer. A real POSIX permission control checks that inaccessible
input components also fail without publishing a partial matrix.

Local observations on macOS arm64: all nine new groups and five retained
lexical groups pass on CPython 3.12.15; the nine new groups also pass on
optimized CPython 3.14.8. The research-tooling suite passes 167 tests with 18
platform-specific skips. Expected failing child fixtures print tracebacks in
that successful run. Its command is:

```sh
uv run --python 3.12 --no-project python -B -m unittest discover \
  -s tests -p 'test_research_*.py'
```

## Scope and engineering decisions

This is a verifier correctness side result under priority revision 5.
`TASK.json` records the change from the portable-replay card's initial payload
audit. The baseline source check passed before investigation. Final overlap
covered 230 open PRs, 1,687 discussion records and 2,440 closed PRs with complete
pagination. Its wider `symlink`/`input` search found @EdDiboi's earlier
[local-only handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18942018)
on the same gap. This package independently corroborates that finding and
provides a public source-bound patch. The prior code was not linked or copied;
its stated claim had expired. Coordination is in
[discussion 2983](https://github.com/CrocSwap/integer-mult-bounds/discussions/2983).
Search coverage does not establish novelty.

Boundary Discipline and the Laziness Protocol led to one shared guard at the
metadata and planner boundaries. Build the Lever and Prove It Works led to the
source-bound reproducer and actual Git/CLI controls. Internal automated review
prompted the separate canonical-manifest commit in the positive CLI test.
This is author-checked evidence, not independent human review.

The new helper traverses at most the declared path's component count.
It has no recursion, shared mutable state, retries or retained filesystem
handles. It checks `lstat` before following a component. Only missing and
not-a-directory conditions end inspection early; other errors propagate.

Power of Ten deviations:

- Rule 3, managed allocation, `symlink_free_relative_path`: Python allocates
  `Path` objects and exceptions during traversal. Live guard state is bounded
  by the supplied path length. This is a local manifest validator, not hostile
  input resource hardening. Component-error and deleted-input controls verify
  its exits. A separate manifest-size budget would be needed for hostile inputs.
- Rule 8, `verify.py`: the reproducer compiles the authenticated historical
  source and the current runner under test. It uses no downloaded source or
  bytecode cache. Exact Git-blob/SHA256 checks constrain the historical target;
  retaining that execution is necessary to reproduce this predecessor failure.
- Rule 10: no Python linter is configured for this runner. Warnings-as-errors
  compilation and behavioral tests cover the change. Global lint configuration
  is deferred to a separate tooling change. Existing manifest-sized loops and
  allocation in `validate` and `plan` remain outside this small repair.

Inputs must remain stable during planning, validation and execution. This is
not an atomic snapshot or concurrent-writer defense. Inspection starts below
the supplied repository root, which may itself use a system directory alias.
Case-insensitive spelling aliases, hard links, Windows junctions and other
reparse points are outside scope. No Windows/Linux execution, hosted CI result,
cold supplier replay or new kappa is claimed. Full Git history and symlink
creation privileges are needed for the historical reproducer; tests label
Windows privilege and POSIX-permission skips explicitly.

## Open next questions

Should inputs require exact Git-index spelling on case-insensitive filesystems?
A spelling alias could also differ from Git changed-path output. The first
test is a real mixed-case Git fixture on such a volume, checking metadata and
a target-only diff. A separate platform policy is needed before expanding this
guard. The structured question is in `TASK.json`.

## Credit

woklerx's [PR1891](https://github.com/CrocSwap/integer-mult-bounds/pull/1891)
supplied the lexical-input guard and retained regression tests. Charles Bethin
supplied replay-selection controls. @EdDiboi reported the same acceptance and
invalidation gap in the earlier local-only handoff linked above. Douglas Colkitt
supplied the runner, scaffold and task workflow. Nick Petalas's
[PR2958](https://github.com/CrocSwap/integer-mult-bounds/pull/2958) repairs
unreadable planner inventories, a separate failure mode. Their sources remain
attributed. This package supplies an independent public reproducer and symlink
guard.
The fix and scoped package are by Nick Petalas. Substantial AI assistance
was used in investigation, implementation, tests and writing. Apache-2.0.
