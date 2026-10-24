# Windows junctions in replay input paths

The registered replay planner now rejects Windows directory junctions below
the repository root, using the same component walk that rejects symbolic
links. This fixes a case where metadata validation accepted an input alias and
a real target change produced an empty replay matrix. It changes tooling
coverage, not a scientific result or the selected frontier.

## Reproduced failure

Source: canonical main `7c472563474e60185e6ca101a17622133d047e56`.
The original `scripts/research_package.py` has Git blob
`ef9b52c392323362621baf6ee188a26fc5122bf9` and SHA256
`8e07ddee4d8e1c70a278538b2758d423a298b96d5d1a18233dc29925696fc96f`.

1. Commit two ordinary files, `src/dep.json` and `alias/dep.json`, with identical
   bytes, and register a package with `alias/dep.json` as its input.
2. Replace the working directory `alias` with a native Windows junction to
   `src`. Keep the checkout stable for each validation/planning call.
3. Change `src/dep.json` from `{"proof":1}` to `{"proof":2}` and commit only that
   canonical path. The declared alias spelling still exists in `HEAD`.
4. Validate the package and plan from the earlier commit.

On Windows 11 build 26300, CPython 3.12.0 and Git 2.47.1.windows.1, the original
validator accepts the package. Reading its input returns `{"proof":2}`, but
the actual Git diff names only `src/dep.json`. The CLI exits zero, prints
`{"include": []}`, and appends `count=0` to the workflow-output file.

This does not require an immutable source pin to accept changed bytes. Explicit
replay inputs may be dependencies without a `SOURCES.json` pin; the planner
must still reject an alias that cannot match Git's changed paths.

## Repair and evidence

A junction reports directory mode, so `stat.S_ISLNK(info.st_mode)` is false.
Its `lstat` result instead carries `IO_REPARSE_TAG_MOUNT_POINT`. The component
walk now rejects that tag before looking up descendants, including for a
dangling junction. It keeps the existing symlink diagnostic and propagates I/O
errors. Python exposes [the reparse tag in `os.lstat` results](https://docs.python.org/3.12/library/os.html#os.stat_result.st_reparse_tag)
and [the corresponding `stat` constant](https://docs.python.org/3.12/library/stat.html#stat.IO_REPARSE_TAG_MOUNT_POINT)
since 3.8; the fix does not require the newer `Path.is_junction()` API.

The five added regression groups cover the tag/lookup boundary on every host
and four native Windows cases: metadata/resolution/planning, a dangling
junction, an actual-Git CLI omission, and a checkout reached through a junction
at its root. The CLI rejection leaves stdout empty and an existing workflow
output unchanged; declaring `src/dep.json` instead selects the package.

The same five new groups were run against the unchanged original runner in a
separate source snapshot: four fail, and the root-junction positive control
passes. With the fix, the complete alias module passes normally and optimized:

```sh
python -B tests/test_research_symlink_inputs.py
python -O -B tests/test_research_symlink_inputs.py
```

Each runs 14 tests, with one existing POSIX-permission test skipped on Windows.
All four native junction groups execute; none depends on symbolic-link
privileges. Existing regular-file, deleted-parent, symbolic-link, permission
error and canonical-selection controls remain in that module. Adjacent input
spelling, pin-path, replay-selection, sparse-planning and publication-byte
regressions are part of the focused validation recorded in the PR. The existing
Git-spelling module needs `PYTHONIOENCODING=utf-8` on this host: its Unicode
diagnostic assertion fails under default CP1252 on both the original and fixed
runner. That [previously reported fixture mismatch](https://github.com/CrocSwap/integer-mult-bounds/discussions/2983#discussioncomment-18981956)
is not changed here. Replay-selection tests were run after materializing their
workflow-file dependency omitted by the sparse checkout.

## Scope, selection and attribution

Task `portable-replay`, priority revision 7, chooser nonce
`59d790bcbb44891de2b3ea502e8df5eb`. Scope is **changed** from container comparison
to a platform-specific dependency boundary: silently omitting a required
replay is a verification failure. The selected source/metadata baseline passed.
Handoffs were checked before the picker; the current temporary-root issue had
already been addressed, so this takes the distinct repository-input boundary.
The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2983#discussioncomment-19152881)
records overlap, the bounded method and the stop rule. Stop after this component
boundary and its relevant regression tests; no construction search follows.

This extends Nick Petalas's [PR2986](https://github.com/CrocSwap/integer-mult-bounds/pull/2986),
which explicitly left Windows reparse points outside its scope and preserved
[EdDiboi's earlier finding](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18942018),
woklerx's lexical path guard, Charles Bethin's replay-selection work and Douglas
Colkitt's runner. Exact Git spelling remains the separate PR3007 boundary.
[PR4730's native Windows corroboration](https://github.com/CrocSwap/integer-mult-bounds/discussions/4500#discussioncomment-19136617)
concerns temporary-root aliases and is not this input-dependency fix.

Only existing components below the repository root are checked. The root may
itself be a junction. The patch is not a general reparse-point ban, hard-link
detector, atomic snapshot, concurrent-writer defense or transitive dependency
analysis. Frozen packages, source pins and selected records are unchanged.
No selected cold replay or complete multiplication-theorem check is claimed.
Evidence is author-checked, not independent human or proof-kernel acceptance.

Prepared for Mihir Srivastava with substantial OpenAI Codex assistance.
Apache-2.0; predecessor attribution is retained.

## Open next questions

Cross-platform CI should retain the platform-neutral tag control and existing
POSIX symlink/permission coverage; actual junction behavior requires a Windows
runner. Any broader alias policy needs a named failure and an explicit contract
before expanding this check. No additional mathematical question follows from
this tooling repair.
