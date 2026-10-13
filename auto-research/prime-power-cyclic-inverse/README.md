# Prime-power cyclic inverse bounds

This package proves a uniform conditioning result for the finite
q-Pochhammer kernels used in a Newton factorization of Fourier matrices.
The proof covers all prime-power orders and all primitive root choices.
It includes dyadic orders. The inverse bound does not depend on the
cyclic array length, shift step, or scalar gauge of modulus one.

See [PROOF.md](PROOF.md) for the circle bound, the induced infinity-norm
bound, and the product bound. The contribution removes dependence on
cyclic length from an earlier algebraic-norm estimate. It supplies no
new integer kappa, complex b, BIT c, or paid inversion program.
Efficient preparation, rounding and error propagation, scratch restoration,
and a fast fixed-tape implementation remain open.

## Replay

Python 3.11 or later and the standard library are sufficient:

```sh
python3 -B research/prime-power-cyclic-inverse/verify.py --output /tmp/prime-power-result.json
cmp research/prime-power-cyclic-inverse/EXPECTED.json /tmp/prime-power-result.json
```

The same checks remain active with `python3 -B -I -O`. The verifier uses
exact rational cyclotomic arithmetic. It checks eight cases at orders
3, 4, 5, 7, 8, 9, and 11, with two primitive powers at order 11.
It checks the tail-product kernel, integral coefficients, residue
identities, a nonzero Sylvester determinant, a Bezout identity, and the
nonzero integer norm. Two negative controls catch a unit-circle common
root and omission of complex conjugation. `EXPECTED.json` is a finite
replay record. The written proof establishes the uniform theorem.

[SOURCE.json](SOURCE.json) records exact source pins and the scope of
reused work. [NOTICE.md](NOTICE.md) gives attribution and AI disclosure.

## Independent engine

The optional second engine needs SymPy 1.14.0. It imports no primary
verifier code:

```sh
python3 -B -I -O research/prime-power-cyclic-inverse/independent_verify.py --output /tmp/prime-power-independent.json
```

It checks the same eight input cases and an extra primitive choice at
order eight. It uses SymPy determinants, cofactors, polynomial gcds,
resultants, and inverses modulo `z^L-1` at L=1, 2, 4, and 8. All 36
cyclic inverse products must equal one. All checks remain active with
optimized Python. The primary replay needs no SymPy installation.
