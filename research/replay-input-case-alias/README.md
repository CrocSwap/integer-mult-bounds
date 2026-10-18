# Case-insensitive replay-input aliases evade Git invalidation

**Author-checked audit; no shared-runner repair or mathematical claim.** This
answers the native-volume handoff in [discussion 2983](https://github.com/CrocSwap/integer-mult-bounds/discussions/2983).

On the tested case-insensitive macOS volume, both pinned runners accept a
declared dependency `SRC/DEP.json` through complete metadata validation when Git
tracks `src/dep.json`. A subsequent commit changing only `src/dep.json` produces
a successful empty replay matrix. Correcting the declaration to `src/dep.json`
selects its consumer against the **same target-only commit**.

| Authenticated runner | Parent alias `SRC/dep.json` | File alias `src/DEP.json` | Both `SRC/DEP.json` |
|---|---|---|---|
| Main at `b3f3ee0392b71b118fd086a6eaf6b4cab54ef455` | Validates; skips replay | Validates; skips replay | Validates; skips replay |
| PR2986 at `f610bda7818df522c26b28f5766a06c5ef5c270c` | Validates; skips replay | Validates; skips replay | Validates; skips replay |

The PR2986 symlink repair explicitly excludes case-insensitive aliases. This
result fills that stated evidence gap; it is not a contradiction of its claimed
scope. All six aliases are ordinary files resolving to the tracked inode, with
no symbolic links. The complete observed receipt is [EVIDENCE.json](EVIDENCE.json).

## Why the implication fails

`canonical_relative_path` enforces POSIX lexical spelling, while `relative_file`
uses the host filesystem to establish existence. Neither establishes equality
with the spelling emitted by Git. PR2986 additionally rejects symlink components;
an ASCII case alias has none. The planner compares strings with
`changed.intersection(inputs)`, so these spellings never intersect.

The dependency in the fixture is an **additional, unpinned VERIFY input**. The
schema permits such inputs. Catalogue and selected-record provenance are fully
pinned, and validation runs with its default `check_pins=True`; the real CLI
also returns `PASS_PACKAGE_METADATA_AND_PINS`. This does not demonstrate that a
wrongly spelled, Git-pinned SOURCES input passes its separate provenance checks.

Planning does not call full package validation. Thus a successful empty matrix
can prevent any replay job from discovering the bad declaration, including on a
case-sensitive CI host. On case-sensitive hosts these same aliases fail file
validation; the portable replay explicitly distinguishes that behavior.

## Reproduce

From the repository root, using Python 3.12 and Git:

```sh
python3.12 -I -B research/replay-input-case-alias/verify.py --require-native
python3.12 -I -B scripts/research_package.py --package research/replay-input-case-alias
```

The first command requires the temporary working volume to resolve ASCII case
aliases. It must print both:

```text
PASS_CASE_ALIAS_PORTABLE_CONTROLS runners=2 variants=3 source_mutants=6
PASS_CASE_ALIAS_NATIVE_REPRODUCTION full_validation=6 target_only_git_omissions=6
```

The registered replay runs the same controls and attempts native reproduction.
On a case-sensitive volume it instead reports `CASE_ALIAS_NATIVE_UNAVAILABLE`;
that is **not** a native reproduction. `--require-native` then exits nonzero.
`tempfile` chooses the working volume; set `TMPDIR` to an existing directory on
the volume being tested if needed. No disk image or mount is required.

Each fixture makes real local commits, checks the exact NUL-delimited target-only
diff, runs both the Python API and actual planner CLI, and verifies the appended
GitHub output as well as stdout. Each alias fixture also checks:

- Canonical spelling selects exactly its consumer and passes full validation.
- An unrelated dependency selects only the other package.
- Deleting the canonical input and its parent still selects the consumer from
  a separate target-only deletion commit.
- A lexical `./` alias fails before publishing a matrix or changing an existing
  workflow-output file.
- Changed source bytes fail SHA256 and Git-blob authentication before execution.

No assertions implement acceptance, so optimized Python preserves the checks.
Authenticated source is compiled directly to avoid preexisting bytecode caches.
The two frozen snapshots are necessary executable audit inputs; later shared
runner repairs do not silently change the experiment. Their historical Git blobs,
SHA256 hashes and exact heads are in [SOURCES.json](SOURCES.json). The main script
pin is provenance, not a requirement to keep today's shared runner unchanged.

The recorded native run used CPython 3.12.14, Git 2.53.0 and macOS 26.3.1 arm64.
This package needs no third-party Python modules. A replay normally takes several
seconds. To record a new observation explicitly, add `--receipt /tmp/case-alias.json`;
the committed receipt is an author-run record, not a cross-platform expected file.

## Boundaries

This audits three ASCII spelling variants on one native volume and two exact
runner versions. It does not repair the shared runner, scan existing packages
for aliases, or prove any selected construction incorrect. Case-only Git
renames, Unicode normalization, filesystem race conditions, hard links,
Windows reparse points and general alias equivalence are untested. No hosted
CI, independent human review, full supplier replay or new kappa is claimed.

The task picker drew bit mechanisms with nonce
`7b063b204ec1c0b77aa3105b3acf2127`. [TASK.json](TASK.json) records the explicit
`portable-replay` scope override to the fresh platform-specific handoff, exact
base, overlap coverage and stopping rule. Sparse local searches do not cover all
historical package notes; live metadata pagination does not cover every diff or
unpublished contribution.

## Open next questions

What exact Git-spelling contract should both validation and planning enforce?
The first useful repair test is these target-only fixtures, retaining canonical
deletion and adding case-only renames. A filesystem directory-name scan alone
does not establish Git-index spelling; a repair must define its index/export,
untracked-input and normalization behavior before adoption. These unresolved
choices are the blocker, not another alias census. The structured question,
relevance and first step are also in [TASK.json](TASK.json).

## Credit

Arham Tahir, with substantial OpenAI Codex assistance in investigation,
implementation, verification and writing. Apache-2.0; no independent human
review is asserted.

Nick Petalas's PR2986 supplied the symlink repair and this native Git-spelling
handoff. EdDiboi's earlier symlink-input finding retains discovery credit for
that different alias class. Retain woklerx/PR1891's lexical-path guard, Charles
Bethin's replay-selection controls, Douglas Colkitt's runner/scaffold and the
remaining verifier/workflow lineage. The byte-identical predecessor snapshots
retain their original notices and the repository's Apache-2.0 license.
