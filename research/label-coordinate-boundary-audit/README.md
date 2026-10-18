# Fractional labels pass checking but change exported geometry

Changing only `lines[0][1]` from `0` to `0.5` in the selected PR589 word passes
the complete symbolic checker and PR2992's simple-scatter boundary. Export then
changes **119 frame descriptions, 77 frame dimensions and 377 record ranks**,
including five COPY ranks. This is a source-to-export acceptance counterexample,
not a failure of the unchanged selected integer input or a new kappa.

## Exact witness and cause

The selected first label is `(2,0,0,0,0,0,0,0)`. The mutant is
`(2,1/2,0,0,0,0,0,0)`. Its norm in the declared form `<x,y>/2` is **17/8**,
not 2. The value 0.5 is exactly representable, so this is not rounding noise.

`Word.__init__` in the pinned `xcheck_p.py` applies `int(a)` to every coordinate.
Thus the checker sees exactly the original labels and accepts the lattice,
frames, all 661 dirty-input columns, H1-H5 and the interface conclusions.
The pinned `export_records.py` instead applies `Fraction(a)` to the raw values
and retains those values in its emitted basis rows. It consumes different geometry.

Frame 267 has rational rank **4 before / 5 after**. Its first affected MOVE,
for register 486 from frame 11 to 267, charges rank 3 before / 4 after:

```text
before: (0, 486, 11, 267, 3, 0)
after:  (0, 486, 11, 267, 4, 0)
```

Both exports still have 27,234 records and 636 frames. The state JSON is
byte-identical. A separate Boolean interpreter still passes all 661 scalar
columns and temporary cleanup in both exports: a scalar-only check cannot
detect this geometry discrepancy. The audit independently computes exact
rational ranks for all 636 raw frames in each fixture. Every changed record
differs only in a MOVE/COPY rank field. [RESULT.json](RESULT.json) records the
deterministic counts, witness and hashes of all three exported artifacts.

As a negative control, changing the same coordinate to the integer 1 passes
the new type guard but fails the full symbolic checker. Integer typing does
not replace E8 geometry validation. No native acceptance or rejection is
inferred here; that boundary has not been replayed.

## Opt-in successor

[boundary.py](boundary.py) applies `integer-labels-v1` before either real entry
mode, then reuses PR2992's authenticated simple-scatter validator:

- `v` is a positive exact integer and `h` is the integer 8.
- `lines` is a list of exactly `v` lists, each of length `h`.
- Every coordinate has Python type `int` after JSON parsing. Booleans, strings,
  fractional numbers and integral float spellings such as `0.0` are rejected.

The schema deliberately follows the selected integer producer. It is a
sufficient contract, not a claim that every rejected encoding changes geometry.
For accepted integers `a`, both `int(a)` and `Fraction(a)` denote the same exact
number. There is no normalization. Other supplier hypotheses remain the
unchanged checker's responsibility; export mode validates schemas only.

The original scripts and predecessor guard are hash-authenticated. Validation
precedes delegation and output creation; the parsed word and delegate script
are snapshotted privately. Replacing the original path after validation cannot
change the delegated word. The valid selected fixture preserves all three
exported artifacts byte for byte. Invalid labels and duplicate scatter rows
reject before existing outputs are touched. Delegate failures retain the
original exporter's behavior; general transactional output is not claimed.

## Reproduce and evidence

From the repository root, standard-library Python only:

```sh
python3.12 scripts/research_package.py --package research/label-coordinate-boundary-audit
python3 -I -O -Werror -B research/label-coordinate-boundary-audit/verify.py
python3 -I -O -Werror -B research/label-coordinate-boundary-audit/test_boundary.py
```

The primary audit covers the actual full symbolic/export paths, both guard
modes, independent rational ranks, scalar columns, byte identity, integer
control and typed receipt. Eight test groups cover coordinate types/shapes,
existing-output preservation, retained scatter rejection, rank controls,
source corruption, snapshot replacement and scalar failure controls.
The registered replay and all eight groups passed locally on Windows with
CPython 3.12.14, with `-I -O -Werror -B` on the audit and tests. This is local
verification; hosted CI is a separate observation.
Each replay command has a 120-second limit; delegated processes have 60 seconds.
Normal replay is read-only. `verify.py --emit` prints a reconstructed receipt.

Use the operational wrapper with any candidate word:

```sh
python3 -I -B research/label-coordinate-boundary-audit/boundary.py check WORD.json.gz
python3 -I -B research/label-coordinate-boundary-audit/boundary.py export WORD.json.gz OUTDIR
```

Scientific base: canonical main `18aacb215fc3717b06be8ceb9fca62aeca0d3e99`,
priority revision 6. [TASK.json](TASK.json) records the refined card, overlap
limitations and handoff. [SOURCES.json](SOURCES.json) pins exact source bytes
and Git blobs, including the selected source manifest. The full selected
inventory/baseline and native cold replay were not run; orientation used the
working PR2992 replay and the relevant selected-source bindings instead.
Canonical main was fetched again before submission and remained at this base;
no guidance or audited-input changes needed reconciliation.

## Open next questions

Should a separately versioned supplier adopt the integer-labels-v1 contract?
It would close this label-interpretation gap at both entry points. First review
the one-coordinate witness, schema and controls, then repin a successor and
run the complete symbolic/export/native chain. Maintainer adoption and that
fresh native/supplier replay are the blockers. Frozen sources and selected
frontier metadata should not be silently repinned to install this opt-in module.

## Credit and limits

Prepared for `josecarlosgonzalezroque-design` with substantial OpenAI Codex
assistance in investigation, implementation, exact verification and writing.
Apache-2.0; no independent human or proof-assistant review is claimed.

Nick Petalas / PR2977 discovered the distinct scatter multiplicity mismatch.
Arham Tahir / PR2992 supplied the simple-support boundary, validator and snapshot
delegation adapted here. kumagi / PR3004 independently characterized the parity
contract. The new result is the fractional-label coercion witness and its
integer-coordinate successor. Credit eumemic for the generator/checker and
PR543/PR555 lineage; DreamingOfClouds for the PR589 bit construction; Dylan Crow
for the exporter/native lineage; and Douglas Colkitt for selected bindings and
guidance. Original notices and sources are retained unchanged.

No native compilation, complete selected replay, hosting/precision or all-size
admission is claimed. This package neither changes the selected exponent nor
establishes a full multiplication theorem.
