# A strict mixed-cycle column bound

For n=q+3 rows over roots of order 3q^b, where q>=5 is prime and b>=1,
any m orthogonal columns satisfy m^2<d^2(4d-3), with d=n-m.
Thus eight rows permit at most five columns. At 104 rows, the strict
equality obstruction reduces the bound from 91 columns to 90.
These are necessary upper bounds; their attainment is not proved.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json),
[verify.py](verify.py), [SOURCE-PINS.json](SOURCE-PINS.json) and
[CREDITS.md](CREDITS.md). The proof combines a projected star, a
rectangular Hermitian block, paired eigenvalues and a rank bound.
The equality case would require an impossible prime-power row sum.

Run with Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/mixed-cycle-column-defect
```

Both registered modes print `PASS_MIXED_CYCLE_COLUMN_DEFECT`.
The source verifier runs unchanged. No new kappa or physical supplier
follows. The selected frontier and all five assumptions remain.

## Open next questions

- Determine the largest attainable column count for q=5,b=1. Start
  below the upper bound with an exact cyclotomic orthogonality test.
- Determine which block constraints improve the trace bound at large q.
  A necessary spectral condition does not determine the root entries.
- Resolve other row counts or larger powers of three. First check the
  cycle decomposition and triangle phases in that changed scope.
- Connect a valid supplier to a complete physical caller cost. This
  package proves an obstruction and supplies no implementation.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
