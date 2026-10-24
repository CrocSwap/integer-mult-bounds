# Reproduction

Run from `/Users/aliromman/Projects/IntegerMultiplicationBounds`.
Use one process at a time. Each output directory must be new.

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/row-involution-review-20261020/check_review.py --out NEW_NORMAL_DIRECTORY
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/row-involution-review-20261020/check_review.py --out NEW_OPTIMIZED_DIRECTORY
```

Both runs must print:

```text
PASS_INDEPENDENT_ROW_INVOLUTION
```

The retained final runs are `verified-normal` and `verified-optimized`. Their
`CHECKS.json` files must be equal byte for byte. The checker uses
exact rational arithmetic and explicit failure conditions.

The earlier `normal` and `optimized` directories contain the complete
base review before the symmetric and metric addendum was bound.

The old native response and physical pair geometry are pinned inputs.
No producer function is imported or replayed. The imported helper is
a frozen earlier independent matrix checker; its hash is in the
receipt. The new review derives its response matrices from the signed
blocks and uses reverse output propagation for the literal words.
