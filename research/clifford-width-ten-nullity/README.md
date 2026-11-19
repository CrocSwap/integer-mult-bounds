# Exact four-qubit width-ten nullity

The full Gaussian-dyadic four-qubit Clifford Gram matrix at tensor
width ten has exact nullity 193,919,902,208 and exact rank
11,934,748,974,592. Seven minus-type and eight plus-type modules are
absent. Every other module in the required central-character sector
occurs. T(4)=13 is unchanged; no new kappa follows.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json),
[STABILIZERS.json](STABILIZERS.json), [verify.py](verify.py),
[extract.py](extract.py), [SOURCE-PINS.json](SOURCE-PINS.json),
[EXTERNAL.json](EXTERNAL.json) and [CREDITS.md](CREDITS.md).

Run with Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/clifford-width-ten-nullity
```

Both registered modes print `PASS_CLIFFORD_WIDTH_TEN_NULLITY`.
They use the retained projections and need no network access.
To reconstruct the complete data from the authenticated CTblLib
release in EXTERNAL.json, also run:

```sh
python3.12 -B research/clifford-width-ten-nullity/verify.py \
  --ctbllib-archive /path/to/ctbllib-1.3.11.tar.gz
```

This command also prints
`PASS_AUTHENTICATED_STABILIZERS rows=127 inner_products=14650 restrictions=10287`.
It checks the full ordinary character rows, Galois action and class
fusions before comparison with every retained projection and sparse
restriction coefficient. The published tables remain mathematical
inputs; these checks do not rebuild them from group multiplication.

## Open next questions

- Determine exact spectral endpoints at the first independent width.
  Start with all required block eigenvalues; full support alone does
  not give conditioning.
- Determine which parts of the stabilizer calculation extend to more
  qubits without a full ordinary character table.
- Connect the alphabet to native realization and complete caller
  costs. The present algebraic result supplies no physical supplier.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
