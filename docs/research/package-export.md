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

## Evidence and scope

Base `997e6a9ca7b4f95d50e366f61412fd640d72a88a`; verification-engineering seed 87.
The source example is Tekalign's PR3134, which retains Jose Manuel's PR3131
collector and the predecessor notices. The exporter builds on Douglas Colkitt's
explicit package contract and the retained publication-byte/Git-batch helpers.

```sh
python3 -B -m unittest discover -s tests -p 'test_research_export.py' -v
```

Nine test methods cover real commits, binary/Unicode/newline/wildcard paths,
Git-free direct replay, deterministic output, dirty/sparse-equivalent missing
working inputs, executable modes, missing/directory/duplicate declarations,
symlinks, overwrite refusal, payload/mode/inventory corruption, duplicate and
escaping tar members, and a late Git failure. No selected construction or
frontier is changed. Further work could define explicit transitive dependency
closures; guessing them from imports is outside this tool's contract.

Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.
