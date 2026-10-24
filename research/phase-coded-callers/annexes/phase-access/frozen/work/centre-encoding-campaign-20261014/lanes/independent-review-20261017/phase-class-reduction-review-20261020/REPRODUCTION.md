# Reproduction

Run from `/Users/aliromman/Projects/IntegerMultiplicationBounds`.
Use one process at a time. Each output directory must be new.

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/phase-class-reduction-review-20261020/check_review.py --out NEW_NORMAL_DIRECTORY
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/phase-class-reduction-review-20261020/check_review.py --out NEW_OPTIMIZED_DIRECTORY
```

Each command must print:

```text
PASS_INDEPENDENT_PHASE_CLASS_REDUCTION_BASELINE
```

The two `CHECKS.json` files must be equal byte for byte. The final
retained runs are `verified-normal` and `verified-optimized`. The earlier
`normal` and `optimized` directories are draft checks before the literal
active-coordinate factorization and the final source freeze were added.

The checker uses explicit failure conditions. The optimized run does not
remove them. Exact arithmetic uses `fractions.Fraction`.
