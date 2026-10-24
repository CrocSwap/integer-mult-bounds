# Export one committed replay package

`export_research_package.py` replaces per-package tar recipes with a repeatable
snapshot of the package and its explicit `VERIFY.json` inputs. It reads the
manifest and all file bytes from a resolved commit, including files absent from
a sparse checkout. Working changes, untracked files, smudge filters and
`export-ignore` attributes do not change the snapshot. Executable modes survive;
links, directories used as input files and missing inputs are rejected.

```sh
python3 scripts/export_research_package.py export \
  --package research/guarded-wrapper-refinement \
  --ref d8c0e3e88e501da6c19f858b7debf0c2e3e0be69 \
  --output /tmp/guarded-wrapper.tar
python3 scripts/export_research_package.py check /tmp/guarded-wrapper.tar
```

The example needs that PR3134 commit in the local Git object store. Both
commands print `PASS_RESEARCH_EXPORT` with the resolved commit, package and
file count. An existing output is never replaced. The exporter creates a
regular-file-only, uncompressed PAX tar with sorted paths and fixed owner/time
metadata. Repeating the same export produces the same bytes on the tested
Python 3.12 and 3.14 runtimes. A private temporary file is published only after
Git and archive writing succeed.

The archive includes `.research-export.json`: commit/package labels and the
exact path, mode, byte length and SHA256 of each exported file. `check` streams
payloads, rejects duplicate, unsafe or non-regular members, and requires exact
inventory and hash equality. It never extracts or executes content and does
not invoke Git. Keep this script and `research_package.py` available to run it.

Bundle paths must remain relative under both POSIX and Windows path semantics,
regardless of the machine producing or checking the archive. Drive-qualified
names such as `C:/input.txt` and `C:input.txt` are rejected in declared inputs,
archive members and receipt paths. They are valid relative POSIX names but can
discard an extraction destination on Windows. Other colons, as in
`inputs/part:one.txt`, retain their existing behavior. The generic repository
source-path policy is unchanged. This check does not replace an extractor's
own path filters or promise that every accepted filename is supported by every
filesystem.

This is transport integrity, **not authenticated Git provenance**: an attacker
who replaces both bytes and receipt can create a consistent different bundle.
Obtain the archive/hash or source commit through a trusted channel. Hashing
also does not establish that a verifier or mathematical claim is correct.

After checking an archive from a trusted source, extract it into a fresh
directory and run the package's documented direct verifier. The exporter does
not infer transitive imports, include undeclared external files, install
dependencies or make a Git-dependent checker portable. The generic registered
runner still needs Git history for its provenance checks. The exported manifest
is preserved unchanged; successful export is not a successful registered replay.

## Select a separate input commit

Use `--input-ref COMMIT` when a published package needs its external inputs
from one historical commit. The package files and unchanged `VERIFY.json`
come from `--ref`; all external declared inputs and their executable modes
come from `--input-ref`. Both refs are resolved to exact commits. The receipt
and CLI result add `input_commit`; ordinary exports keep the original format
and bytes. The offline checker validates this optional commit label.

```sh
python3 -B scripts/export_research_package.py export \
  --package research/bit-semidir21-orbit-seed8f89 \
  --ref 1ec1119972c9aefe42525172d07b332fcff81cb4 \
  --input-ref 1c47876ef742ba64bf9140b0527d63acf656a3b4 \
  --output /tmp/semidir21-historical-inputs.tar
python3 -B scripts/export_research_package.py check /tmp/semidir21-historical-inputs.tar
```

The example uses the package's recorded common source base. Both Git trees
must be available. A declared input inside the package is rejected in this
mode because its two source contexts would conflict. Missing, non-regular,
unsafe or directory inputs still fail, and no output is published on failure.
A historical input can be absent from the publication tree and checkout.
Git replacement refs remain disabled for both snapshots.

This option does not select a source base automatically or check mathematical
compatibility. Check the package's exact source pins, then run its unchanged
direct verifier in the checked export. A wrong but well-formed input commit
can produce a valid transport archive whose scientific verifier rejects it.
Inputs from several commits need a separately prepared source archive; this
option selects one common input tree. No frozen file, pin or working-tree
input is changed. The full Git-history and provenance limits above still apply.

New option and regression fixtures: Ali Romman with substantial OpenAI Codex
assistance, Apache-2.0. Tekalign's exporter, roger-sato's path and immutable
object safeguards, Mihir Srivastava's portable fixtures and Dennis's explicit
historical-replay precedent retain credit.

## File and directory conflicts

The regular-file inventory must also form a valid tree: a member cannot be an
ancestor of another member, regardless of archive order. The receipt occupies
`.research-export.json` as a file, so inputs below that path are rejected before
an export is published. Distinct lexical prefixes such as
`.research-export.json.notes/input` remain valid. This prevents a successful
integrity check on a bundle that necessarily fails extraction because a path
would have to be both a file and a directory.

File-tree validation and its CLI/extraction regression tests were prepared for
roger-sato with substantial OpenAI Codex assistance, retaining Tekalign's exporter
and transport-integrity scope. Run them with
`python3.12 -B -m unittest discover -s tests -p 'test_research_export_topology.py' -v`.

## Evidence and scope

Base `997e6a9ca7b4f95d50e366f61412fd640d72a88a`; verification-engineering seed 87.
The source example is Tekalign's PR3134, which retains Jose Manuel's PR3131
collector and the predecessor notices. The exporter builds on Douglas Colkitt's
explicit package contract and the retained publication-byte/Git-batch helpers.

```sh
python3 -B -m unittest discover -s tests -p 'test_research_export.py' -v
python3 -B -m unittest discover -s tests -p 'test_research_export_drive_paths.py' -v
```

Nine test methods cover real commits, binary/Unicode/newline/wildcard paths,
Git-free direct replay, deterministic output, dirty/sparse-equivalent missing
working inputs, executable modes, missing/directory/duplicate declarations,
symlinks, overwrite refusal, payload/mode/inventory corruption, duplicate and
escaping tar members, and a late Git failure. No selected construction or
frontier is changed. Further work could define explicit transitive dependency
closures; guessing them from imports is outside this tool's contract.

Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.

The drive-prefix containment check and five regression methods were prepared
for roger-sato with substantial OpenAI Codex assistance. Their two real-Git
fixtures now create blobs, NUL-delimited trees and a commit directly, following
[PR4579](https://github.com/CrocSwap/integer-mult-bounds/pull/4579)'s object-tree
precedent. This retains the literal colon-bearing names without materializing
them on the host filesystem. Both tests run on Windows without platform skips:
drive-qualified inputs fail through the actual CLI before publication, while
nondrive colons retain their names and exact binary/CRLF payloads. The accepted
archive also passes the CLI integrity check with Git absent from `PATH`.

Run the drive-path module with ordinary and optimized Python:

```sh
python -W error -B -m unittest discover -s tests -p 'test_research_export_drive_paths.py' -v
python -O -W error -B -m unittest discover -s tests -p 'test_research_export_drive_paths.py' -v
```

At main base `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, the repair passes all
five methods with no skips on Windows / CPython 3.12.14 and Ubuntu under WSL2 /
CPython 3.12.3, in both modes. This is local test evidence, not hosted CI or a
mathematical replay. These tests do not extract colon-bearing members or promise
that Windows can materialize every accepted archive name. Production exporter
code and source pins are unchanged.

This completes the bounded drive-fixture handoff in
[Discussion #4578](https://github.com/CrocSwap/integer-mult-bounds/discussions/4578);
[Discussion #4675](https://github.com/CrocSwap/integer-mult-bounds/discussions/4675)
records its scope and evidence. Prepared for Mihir Srivastava with substantial
OpenAI Codex assistance; Apache-2.0. The original exporter and its
transport-integrity contract retain Tekalign's attribution, and the boundary
regressions retain roger-sato's attribution.

## Native Windows fixture replay

At main `f626db5c3a3d781d8f7695038776c621651f75e1`, all nine tests in
`test_research_export.py` fail during setup on Windows because the common
fixture name `inputs/a\n雪[*].bin` cannot be materialized there. Substituting a
portable name exposes a second mismatch: the replay prints CRLF on Windows,
while the test expects an LF-only byte string.

The repaired suite uses a portable Unicode filename for extraction and direct
replay. A separate real Git object-tree fixture retains the original newline,
Unicode and wildcard name, without checking it out. It verifies the literal
Git inventory, deterministic repeated export, offline receipt check and exact
binary payload. The symlink rejection uses committed mode `120000`, following
the publication-byte test's existing approach, so OS symlink privileges are
unnecessary. Only console output is read as text; artifact and extracted input
bytes, including CRLF, remain exact.

The command below runs all three exporter test modules; repeat with `-O` to
check optimized Python too:

```sh
python -W error -B -m unittest discover -s tests -p 'test_research_export*.py' -v
```

On Windows 11 / CPython 3.12.0 / Git 2.47.1, normal and optimized runs each
pass 18 tests with the two existing POSIX-colon fixture skips. The repaired
ten-test module has no skips. Ubuntu under WSL2 / CPython 3.12.3 / Git 2.43.0
passes all 20 tests in both modes. This is local test-suite evidence, not a
hosted CI or mathematical cold replay. Production exporter code and immutable
source pins are unchanged.

Open next question: can the two skipped drive-path Git fixtures also be built
from object trees? Start with their existing colon filenames and retain all
CLI rejection and byte-preservation checks; Windows cannot materialize those
names directly. Arbitrary-name extraction support is outside this repair.

Task `portable-replay`, priority revision 7, chooser seed
`78c5bb9d763460ad101abdb809786566`; scope refined to one reproduced environment
failure. Coordination and limitations are recorded in
[Discussion #4578](https://github.com/CrocSwap/integer-mult-bounds/discussions/4578).
Prepared for Mihir Srivastava with substantial OpenAI Codex assistance;
Apache-2.0. Retains Tekalign's #3138 exporter and tests, and roger-sato's
#3629/#3641 path-boundary regressions.
