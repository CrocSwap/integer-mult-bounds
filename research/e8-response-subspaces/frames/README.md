# Portable exact entrance reconstruction

Requires Python3.11+; uses only its standard library.

Run with the frozen base candidate and a fresh output directory:

```text
python -B reconstruct.py BASE_CANDIDATE.json FRESH_OUTPUT_DIRECTORY selection.json
```

The selection argument defaults to `selection.json` beside the script. The
script verifies source and selection SHA256 values, reconstructs the exact
119-gauge candidate, independently checks all1021 rational columns and every
nested register frame path, and requires the frozen output hash. It writes
`candidate.json`, the explicit changed dirty response `K.json`, and `RECEIPT.json`.
It also checks an omitted-gate negative control. Existing outputs are preserved:
the output directory must not already exist.

`PROOF.md` states the sufficient response identity and the additional scalar/
phase/banking premises. This package is the exact response reconstruction
component; the final supplier package must include its independently admitted
normalization, phase, bank, invoice and outer-assembly artifacts.
