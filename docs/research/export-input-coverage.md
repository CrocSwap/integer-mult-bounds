# Check an export's declared input coverage

Use this optional check before a Git-free package replay:

```sh
python3 -B scripts/export_research_package.py check bundle.tar --check-inputs
```

The default command checks receipt inventory, modes and payload hashes. Consistent
hashes alone do not prove that a bundle contains each input named by its manifest.
The option also reads the bundled `VERIFY.json` and checks these declarations:

- `inputs` is a list of unique canonical file paths.
- Each declared input is present in the checked bundle.
- Files outside the package are declared inputs.
- The export receipt is not named as an input.

A successful console receipt includes `declared_inputs_checked`, with the number
of declarations checked. Zero is valid for a self-contained package. The command
uses no Git process and does not extract files or run the verifier. The manifest's
second read reuses the open archive and its checked member index, and must match
its checked payload hash. The command closes the archive on success or failure.
Manifest bytes are limited to
16 MiB and input declarations to 100,000 entries.

This is a declaration-coverage check, not full `VERIFY.json` schema validation or
proof that the declared list covers every import and runtime dependency. It does
not authenticate the labelled commit, reconstruct source history, install an
environment or verify a mathematical claim. Run the package's stated replay and
retain its source pins and omitted obligations.

The default byte-integrity check and export format remain unchanged. Credit
Tekalign and the retained exporter contributors. Input-coverage work was prepared
for aliromman with OpenAI Codex assistance. Apache-2.0.
