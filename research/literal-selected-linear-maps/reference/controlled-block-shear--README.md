# Controlled block reversal

## Question

When does reversing each aligned block of length `2^width`, on the blocks whose start has a chosen bit set, equal XORing those low bits on every index where the same bit is set?

## Result

Through dimension 16, the two maps agree exactly when the control bit is at least the block width. There are 680 such pairs. The other 680 pairs, where the control bit varies inside a block, disagree. The selected κ is unchanged.

## Boundary

This checks the reversal against the controlled XOR. It does not price a bit-free supplier, choose a tape count, or run a layout schedule. The stop rule is to record this equality.

## Reproduce

```bash
python3.12 -B research/controlled-block-shear/verify.py
python3.12 -B research/controlled-block-shear/test_verify.py
```

## Open next questions

None. The dimensions and control bits are finite. A supplier pricing would leave this package.

## Credit

Matarener recorded the controlled reversal in PR #3825. The checker compares both maps on every pair through dimension 16. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
