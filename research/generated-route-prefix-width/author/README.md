# Structural prefix widths for generated routes

This separate supplement certifies the denominator and maximum column-sum
norm of every forward/inverse prefix of #8092's actual recipe emitter.
Tensor and guard copies act on disjoint coordinates, so their bounds follow
the compact recipe instead of its expanded gate count. The certificate also
covers ordered-addition and signed-scale-atom lowering.

A certificate (d,e) gives fixed carry denominator 2^d and d+e+9 signed work
bits. Updates combine the entire numerator before exact power-of-two
division. A concrete d=0,s=1 example rejects separate summand division.

The retained eight-dimensional `actual_relative` base has certificate (2,4).
Its r-fold tensor power has certificate (2r,4r) and width 6r+9. At r=20,
N=8^20 and width is 129; the prior 6m+5 bound is 293994983674745978885.
This large family is computed symbolically, not materialized. Arbitrary
recipes have no claimed logarithmic-depth bound.

```
python3 -B check_prefix.py --output /tmp/prefix-width.json
python3 -O -B check_prefix.py --output /tmp/prefix-width-opt.json
```

The checker authenticates source bytes, verifies native and lowered words
in both directions, checks all tested matrix prefixes, compares rational
low/carry results, and rejects nine shortcuts. See PROOF.md and the receipts.

#5841 supplies the generic carry and column-denominator identities. The new
content is the source grammar's complete prefix certificate, including
partial copies and lowered microsteps, and its fixed-denominator producer.
Complete selected-expression widths, native private-H precision, payload
ordering and owner return remain open. All canonical assumptions and kappa
are unchanged.
