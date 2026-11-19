# Exact four-qubit width-twelve nullity

The full Gaussian-dyadic four-qubit Clifford Gram matrix at tensor
width twelve has exact nullity 10,677,394 and exact rank
12,128,658,199,406. Only inflated Sp(8,2) rows 9 and 22 are absent.
Every nonzero Pauli-character sector occurs. The threshold T(4)=13
is unchanged; no new kappa follows.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json),
[CHARACTER-COLUMNS.json](CHARACTER-COLUMNS.json), [verify.py](verify.py),
[SOURCE-PINS.json](SOURCE-PINS.json), [EXTERNAL.json](EXTERNAL.json)
and [CREDITS.md](CREDITS.md). The proof also gives an implicit
orthogonal projector onto the complete nullspace.

Run with Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/clifford-width-twelve-nullity
```

Both registered modes print `PASS_CLIFFORD_WIDTH_TWELVE_NULLITY`.
To reproduce the new columns from the authenticated release archive,
run this additional command after obtaining the file in EXTERNAL.json:

```sh
python3.12 -B research/clifford-width-twelve-nullity/verify.py \
  --ctbllib-archive /path/to/ctbllib-1.3.11.tar.gz
```

That command also prints
`PASS_AUTHENTICATED_CTBL_COLUMNS classes=81 rational_rows=4`.
It authenticates and replays the source projection. The registered
commands use the retained columns and need no network access.

## Open next questions

- Determine the full nullity at width ten. Its quadratic Pauli orbits
  need a different restriction calculation from the linear orbit here.
- Determine exact spectral endpoints or a useful conditioning bound
  at width thirteen. Support alone does not give those quantities.
- Connect the alphabet to native operations and complete caller costs.
  This package gives an algebraic dependence result, not a supplier.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
