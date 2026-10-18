# Three-shear rewrite

For distinct registers `x`, `s`, and `y`, let `E(t <- u, q)` denote `t += q u`.
When no intervening operation writes `x` or `s`, the selected triples have the form

`E(x <- s, a); E(y <- x, q); E(x <- s, -a)`.

Applied to arbitrary incoming values, the outputs are

- `x' = x`,
- `s' = s`,
- `y' = y + q(x + a s) = y + q x + q a s`.

Therefore the triple equals

`E(y <- x, q); E(y <- s, q a)`.

All four concrete triples use one common frame, so the replacement introduces no
frame transition. `verify.py` checks this identity locally and checks the complete
1,918-event original and 1,914-event candidate B-stage matrices on all 728 arbitrary
input columns. The unchanged selected local emitter and independent frame/wrapper
auditor were also run during validation; both orientations retained the exact paid
profile and 192-bit allowance while saving 52 real-component primitives.

This is a finite local construction. It does not establish that the four rewrites
can improve the selected exponent without rebuilding global hosting and the outer
invoice, and it does not discharge inherited all-size/compiler, physical realization,
precision/tape, exact-recovery or analytic-transfer assumptions.
