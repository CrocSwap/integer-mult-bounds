# Replay the PR4470 frame audit through temporary-root aliases

The unchanged [PR4504 frame audit](../pr4470-frame-audit/README.md) rejects a
benign macOS temporary-directory alias before its constructor runs. This
source-bound successor canonicalizes Python's temporary root for the duration
of that audit and restores the prior setting afterward. The entire original
scientific receipt and all eleven semantic rejection controls still pass.
No frozen source, selected record or mathematical claim changes.

The [maintainer review](../../docs/research/pr-intake-evidence/pr4470/PROOF-REVIEW.md)
already identified the failure and the canonical-TMPDIR workaround. This
contribution supplies an executable, source-authenticated application of that
workaround and focused regression controls; it does not claim a new diagnosis.
Its [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4500#discussioncomment-19129412)
continues the existing PR4504 investigation.

## Cause and minimal repair

`emit_source()` resolves each copied destination, but compares it with the
unresolved `Path(directory)` returned by `TemporaryDirectory`. On this host,
`/var/folders/...` resolves to `/private/var/folders/...`; the two spellings fail
the original containment test even when the destination is inside the private
workspace. An explicit directory symlink reproduces the same problem on hosts
whose default temporary root is already canonical.

The successor executes the exact authenticated verifier bytes and sets only:

```python
tempfile.tempdir = str(Path(tempfile.gettempdir()).resolve())
```

The existing caller then creates its fresh private directory under that
canonical root. Its resolved-destination containment guard remains unchanged.
The previous `tempfile.tempdir` value is restored in `finally`, including after
an error. The wrapper accepts no arguments, so it cannot enter the predecessor's
`--write` authoring mode. No whole-package copy or source transformation is
needed.

[SOURCES.json](SOURCES.json) pins the original verifier, constructor launcher,
UPSTREAM map, expected receipt and all nine constructor snapshots. All thirteen
live inputs authenticate before verifier compilation. Compilation uses the
checked bytes directly, so a cached import of the verifier cannot replace them.
The constructor still runs from the original fresh, source-only copied tree.
The base catalogue and selected record are separate historical provenance.

## Evidence and reproduction

Use standard-library Python 3.12 from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/pr4470-temp-root-replay
```

The registered replay runs five regression groups normally and under `-O`,
then executes the complete original audit under isolated optimized Python.
The controls cover:

- Original failure through an explicit directory alias, successor success
  through that alias, and original success through a canonical root.
- Relative, absolute and interior-symlink escapes rejected before any copy or
  constructor call, with the outside directory left empty.
- Changed verifier, constructor launcher, upstream map, expected receipt and
  constructor bytes rejected before verifier compilation.
- Restoration of the temporary-root setting after success or failure, and
  rejection of authoring/unknown arguments before source loading.

The boundary probes mock only the constructor subprocess to keep them tiny.
The separate scientific replay runs the actual constructor and unchanged audit:
both old/new words in both orientations, 499 changed locations, all eight owned
center jobs, all 408 helper fields, complete paid/helper profiles and all eleven
semantic failures. The predecessor itself compares every field of its unchanged
`RESULT.json`; an aggregate pass count is not substituted for that comparison.

Local evidence on macOS 27.0 arm64 with CPython 3.12.2: five regression groups
pass in normal and optimized modes, zero skips; the complete optimized audit
passes in 4.60 seconds. Its statuses are
`PASS_PR4470_CHRONOLOGICAL_FRAME_AUDIT` and `PASS_PR4470_TEMP_ROOT_REPLAY`.
The default native temporary-root spelling reproduces the original failure.
The registered replay, nineteen-file committed-byte/source-history preflight
and export-inventory check pass. The Git-free export also passes both boundary
test modes and the complete audit (4.73 seconds), with all twenty exported
files including its export receipt unchanged.
[TASK.json](TASK.json) records source freshness, overlap limits and the scoped
handoff. Hosted CI and native Windows execution are not claimed.

## Limits

This is a serial replay with stable source files, not protection against a
concurrent filesystem attacker. Directory symlink support is required for the
regression fixture. There is no selected-family cold replay, physical Clifford
phase audit, all-column theorem or new kappa. The inherited audit's full
scientific limits and predecessor credit remain in its README.

## Open next questions

Should a future maintained entry point canonicalize `root` directly? Start
with `root = Path(directory).resolve()` in an explicitly versioned successor,
and retain these escape and complete scientific controls. Direct adoption
requires source-consumer compatibility review; the selected harness already
uses its own canonical temporary-root workaround. This package intentionally
leaves the original frozen entry point unchanged.

## Credit

Mihir Srivastava / mihir-s-05 supplied PR4504's independent frame/invoice audit.
Douglas Colkitt's maintainer review supplied the failure diagnosis and workaround.
Cinna Davis / 1337isnot1337, zxv, Jacob Alan Sussman and the retained
scalar/Clifford/geometry contributors retain construction credit; Ryanson
Jonathan / pinterbanget retains the PR4478 handoff credit. The separate
PR2158 `invoice-realpath-replay` and PR2947 `selected-inventory-native-replay`
provide related path-canonicalization and source-bound replay precedents.

New wrapper, controls and packaging prepared for Brian with substantial OpenAI
Codex assistance, including an independent subagent boundary review.
Apache-2.0. No independent human review or maintainer acceptance is claimed.
