# Canonical word omission and companion frame check

**Independent cross-output audit; no producer edit, new exponent or selected-frontier change.** The assigned
`portable-replay` card asks whether a canonical payload comparison omits proof-relevant data. Open PR #3545 already
shows that `_gauge_ann` is omitted from the paired-cube canonical word payload. This package checks the narrower
follow-on question: does the actual generator preserve that data in its companion proof output, and would its full
`--check` reject a change that the compressed word alone accepts?

## Result

Yes. With the pinned producer source and a two-coordinate exact geometry, changing only `_gauge_ann` between the
annihilator row spaces `[[1, 0]]` and `[[0, 1]]` leaves the canonical gzip word payload byte-identical after
decompression. Calling the producer's actual `export()` changes both the exported gauge frame reference and the
exact companion `frames` record. The generator's `--check` path adds every `export()` product to its output map and
compares every named file, so the companion `frames_p*.json` comparison rejects this mutation.

This confirms the field is proof-relevant to the exported frame representation while narrowing the implication of
the word-only equality: it does not demonstrate that the generator's complete output check accepts the mutation.
The tiny fixture exercises serialization with an empty graph; it is not a valid paired-cube construction, the p=12
word, a full selected-family replay or a mathematical theorem check.

The positive control changes a public gauge dimension and observes a changed canonical word payload. The verifier
also binds the exact producer bytes by SHA256 in [SOURCES.json](SOURCES.json); it does not modify or regenerate its
frozen outputs.

## Reproduce

From the repository root:

```sh
python3 scripts/research_package.py --package research/canonical-gauge-frame-crosscheck --check-only
python3.12 scripts/research_package.py --package research/canonical-gauge-frame-crosscheck
```

The check imports the pinned standard-library producer and invokes only `Geometry`, `frame_record()` and
`export()` on the tiny fixture. It does not call `build()` or reconstruct p=12. See [VERIFY.json](VERIFY.json) for
the registered command and source input.

## Overlap, source and limits

Open [PR #3545](https://github.com/CrocSwap/integer-mult-bounds/pull/3545) (head `8cd2dfeb6b5cf0f25a80e12127eebb28827303e6`, same base `20ecf2891d80b5acf18d980b2164fb44ea7faa90`) is direct overlap and receives credit for the original `_gauge_ann` omission, its canonical payload fixture, and source reading. This package independently exercises the actual companion export on a valid pair of distinct exact annihilator spaces. The gzip-container reproducibility note supplies the payload-versus-container comparison convention. The selected record is retained only as task provenance; its conditional finite construction is unrelated to this local verifier check.

Not checked: a full p=12 regeneration, comparison against the pinned six output artifacts, the independent `check_paired_cube_bit.py`, Python 3.11/3.13/3.14, or the selected cold replay `make frontier1094-verify`. The registered Python 3.12.3 replay passed. No selected-result, proof source or producer changes were made.

## Open next questions

No further question is needed for this bounded cross-output audit. Verifying the full p=12 output bundle is a separate replay task; this package's conclusion is limited to the pinned source path and exact small fixture above.

## Credit

Credit to jwr / PR #3545 for identifying the `_gauge_ann` omission and supplying the first payload-level fixture; credit to the paired-cube source authors and the gzip-container reproducibility note for the producer and comparison contract. Prepared with substantial OpenAI Codex assistance. No independent human or formal kernel review is claimed. Apache-2.0.
