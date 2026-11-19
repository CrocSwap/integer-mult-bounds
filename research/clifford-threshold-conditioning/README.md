# Four-qubit Clifford threshold conditioning

The normalized full Clifford tensor Gram matrix at width thirteen has
exact condition number 101244/1519. Its least eigenvalue is
470624175/4294967296 and its greatest is 7841980575/1073741824.
All 81 blocks give 52 distinct spectral values.

The normalized tensor map has condition number below 8.165 and
coefficient-recovery norm below 3.021. The same bounds hold at every
larger integer width and for every subalphabet. They are sharp for the
full width-thirteen alphabet. No new kappa or physical supplier follows.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json),
[verify.py](verify.py), [SOURCE-PINS.json](SOURCE-PINS.json) and
[CREDITS.md](CREDITS.md).

Use Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/clifford-threshold-conditioning
```

Both modes print `PASS_CLIFFORD_THRESHOLD_CONDITIONING`. The checks
include the unchanged source verifier, all spectral levels and moments,
and a literal full one-qubit Gram calibration. No network is needed.

## Open next questions

- Specify and price a native decoder that meets this stability contract.
  Include preparation, precision, routing and restoration in the bill.
- Determine sharper constants for a consumer's actual subalphabet.
  First bind that subalphabet and its coefficient norm; do not replace
  the full-alphabet theorem with an unpriced implementation claim.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
