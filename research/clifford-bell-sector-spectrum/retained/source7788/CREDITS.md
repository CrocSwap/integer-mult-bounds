# Sources and attribution

Ali Romman's [PR #7766](https://github.com/CrocSwap/integer-mult-bounds/pull/7766),
commit `d7c2dd1868c70f0addce2c0a4d3220149452f14b`, supplied the sharp
four-qubit threshold, Gaussian phase argument, Pauli/Bell checks and
exact table projection. The complete eighteen-file
[source package](https://github.com/aliromman/integer-mult-bounds/tree/d7c2dd1868c70f0addce2c0a4d3220149452f14b/research/clifford-four-qubit-threshold)
is retained byte-exact and its checker runs unchanged in both modes.

Ali Romman's [PR #7772](https://github.com/CrocSwap/integer-mult-bounds/pull/7772),
commit `1398fbdca3536389d8ac3c8b3aaa408f03e8f6c2`, supplied the exact
width-thirteen spectrum and normalization, plus the generic rational
Gaussian matrix operations reused by the literal calibration. Its
[checker](https://github.com/aliromman/integer-mult-bounds/blob/1398fbdca3536389d8ac3c8b3aaa408f03e8f6c2/research/clifford-threshold-conditioning/verify.py),
proof, certificate and credit record are retained. Its full fixed-width
checker is not invoked; the new checker reads its endpoint certificate
and uses the stated generic matrix operations.

Nick Petalas (@petalas) supplied the width-nine quotient calculation and
[exact projection](https://github.com/petalas/integer-mult-bounds/blob/ff12ca358d601a21cd4b1f016b8a3a969ac44016/research/clifford-four-qubit-width-nine/PROJECTION.json)
in [PR #7747](https://github.com/CrocSwap/integer-mult-bounds/pull/7747).
Its six source files remain intact inside the threshold package. They
credit the ATLAS and Thomas Breuer's CTblLib 1.3.11 for the ordinary
character table. That published table remains a mathematical input.

alephnan (@alephnan) supplied the Pauli-sector, projective Gram and
quadratic-character framework in
[PR #6714](https://github.com/CrocSwap/integer-mult-bounds/pull/6714).
The exact [proof](https://github.com/alephnan/integer-mult-bounds/blob/f7f32a18dde54e67624a9ed9cc7e1b266d9585c0/research/clifford-three-qubit-threshold/PROOF.md)
is retained unchanged. Its notices preserve Ali Romman's pointwise
framework, MatShep's small-qubit work, Nick Petalas's lower bound and
the Lee--Yu--Peng--Lai table.

The overlap check identified Hiroki KUMAZAKI's
[PR #5694](https://github.com/CrocSwap/integer-mult-bounds/pull/5694)
and Nick Petalas's
[PR #5939](https://github.com/CrocSwap/integer-mult-bounds/pull/5939).
Those results concern sufficient absolute-row-sum bounds and convergence
as the qubit dimension grows. This package does not reuse or strengthen
those proofs. It proves exact phase-sensitive endpoints at fixed qubit
dimension over all odd widths.

Ali Romman prepared the new all-width derivation, polynomial comparison
certificates and checks with substantial OpenAI Codex assistance in
research, implementation, verification and writing. This is source-aware
computational corroboration of a written proof. No independent human
or proof-kernel acceptance is claimed. Apache-2.0.
