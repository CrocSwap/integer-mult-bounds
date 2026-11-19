# The sharp four-qubit Clifford tensor threshold is thirteen

The full Gaussian-dyadic four-qubit Clifford alphabet is pointwise
tensor-independent exactly at widths **f>=13**. Thus **T(4)=13**.
Width eleven has exact nullity **2,733,412,864**. Two inflated modules
still give nullity at least **10,677,394** at width twelve. Every quotient
row occurs at width thirteen.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json), [verify.py](verify.py),
[SOURCE-PINS.json](SOURCE-PINS.json), [EXTERNAL.json](EXTERNAL.json) and
[CREDITS.md](CREDITS.md). The package also proves a table-independent
Dickson-block obstruction: **T(n)>=2n+3** for positive n divisible by four.
It gives a degree-120 missing block and explicit null coefficients at
four-qubit width ten.

Use Python 3.12 and its standard library from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/clifford-four-qubit-threshold
```

Both modes print `PASS_CLIFFORD_FOUR_QUBIT_THRESHOLD`. The registered
replay uses the exact retained quotient projection. To rederive that
projection, download the CTblLib 1.3.11 archive linked in `EXTERNAL.json`,
then run:

```sh
python3.12 -W error -B research/clifford-four-qubit-threshold/verify.py --ctbllib-archive /path/to/ctbllib-1.3.11.tar.gz
```

The archive and exact table member are authenticated before use.
The published ordinary table is a mathematical input, not a table
reconstructed from group multiplication. No new kappa or physical
supplier follows; all five assumptions remain.

## Open next questions

- Determine the full width-ten and width-twelve nullities. The reported
  missing blocks need not be the only ones in those even sectors.
- Test other qubit counts or exact conditioning. Retain the Gaussian
  phase and the correct natural or conjugate odd sector. No physical
  caller price follows from a tensor-alphabet threshold alone.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
