# Sources and credit

Ali Romman (@aliromman) prepared the new full sector calculation,
exact extractor, checker and package with substantial OpenAI Codex
assistance. New material is Apache-2.0. No independent human or
formal proof-kernel acceptance is claimed.

Nick Petalas (@petalas) supplied the
[width-nine quotient and question](https://github.com/petalas/integer-mult-bounds/blob/ff12ca358d601a21cd4b1f016b8a3a969ac44016/research/clifford-four-qubit-width-nine/README.md),
[81-row projection](https://github.com/petalas/integer-mult-bounds/blob/ff12ca358d601a21cd4b1f016b8a3a969ac44016/research/clifford-four-qubit-width-nine/PROJECTION.json)
and [archive reader and table parser](https://github.com/petalas/integer-mult-bounds/blob/ff12ca358d601a21cd4b1f016b8a3a969ac44016/research/clifford-four-qubit-width-nine/verify.py)
in [PR #7747](https://github.com/CrocSwap/integer-mult-bounds/pull/7747).
The new extractor follows its MOT record selection and published row
order, then adds the complete ordinary orthogonal tables, class
fusions, tensor rows and exact Galois arithmetic.

Ali Romman's [PR #7766](https://github.com/CrocSwap/integer-mult-bounds/pull/7766)
supplied the [actual Bell-line extension and Dickson obstruction](https://github.com/aliromman/integer-mult-bounds/blob/d7c2dd1868c70f0addce2c0a4d3220149452f14b/research/clifford-four-qubit-threshold/PROOF.md)
and [literal gate and Pauli routines](https://github.com/aliromman/integer-mult-bounds/blob/d7c2dd1868c70f0addce2c0a4d3220149452f14b/research/clifford-four-qubit-threshold/verify.py).
All eighteen package files remain byte-exact and its complete verifier
runs unchanged. Its source closure retains Nick's six-file package
and alephnan's proof.

Ali Romman's [PR #7770](https://github.com/CrocSwap/integer-mult-bounds/pull/7770)
supplied the [restriction argument and remaining width-ten question](https://github.com/aliromman/integer-mult-bounds/blob/ff9bdc0e82e75ab5ed39f3ff034ac8ddb3ea06d2/research/clifford-width-twelve-nullity/PROOF.md)
and [all symplectic class columns used to check the fusions](https://github.com/aliromman/integer-mult-bounds/blob/ff9bdc0e82e75ab5ed39f3ff034ac8ddb3ea06d2/research/clifford-width-twelve-nullity/CHARACTER-COLUMNS.json).
Five notes and data files are retained. Its full width-twelve suite
is not rerun as part of this package.

alephnan (@alephnan) supplied the
[Pauli/quadratic-sector framework](https://github.com/alephnan/integer-mult-bounds/blob/f7f32a18dde54e67624a9ed9cc7e1b266d9585c0/research/clifford-three-qubit-threshold/PROOF.md)
in [PR #6714](https://github.com/CrocSwap/integer-mult-bounds/pull/6714),
with the stated OpenAI Codex assistance. All earlier notices and
credit remain intact. The full three-qubit suite is not rerun.

The ordinary tables and class fusions credit the ATLAS and
[Thomas Breuer's CTblLib 1.3.11](https://www.math.rwth-aachen.de/~Thomas.Breuer/ctbllib/ctbllib-1.3.11.tar.gz).
The complete ordinary tables are external mathematical inputs;
`STABILIZERS.json` retains derived sums and restriction coefficients.
The exact archive and three member hashes are in `EXTERNAL.json`.
The independent tuple count uses
[D. E. Taylor's Witt extension theorem, Theorem 7.4](https://www.maths.usyd.edu.au/u/don/papers/gcg.pdf#page=65).
Character induction, reciprocity and quadratic-space theory are
classical inputs, not claimed as new general theory.

Source commits are content pins, not ancestry claims. `SOURCES.json`
records canonical main provenance, and `SOURCE-PINS.json` authenticates
all twenty-three retained files. No global literature priority is claimed.
