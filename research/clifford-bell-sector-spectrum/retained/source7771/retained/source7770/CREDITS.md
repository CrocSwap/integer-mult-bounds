# Sources and credit

Ali Romman (@aliromman) prepared the new restriction proof, exact
checker and package with substantial OpenAI Codex assistance.
New material is Apache-2.0. No independent human or formal
proof-kernel acceptance is claimed.

Ali Romman's [PR #7766](https://github.com/CrocSwap/integer-mult-bounds/pull/7766)
supplied the [width-eleven quotient, width-twelve lower bound and open question](https://github.com/aliromman/integer-mult-bounds/blob/d7c2dd1868c70f0addce2c0a4d3220149452f14b/research/clifford-four-qubit-threshold/PROOF.md),
[exact multiplicities and literal gate routines](https://github.com/aliromman/integer-mult-bounds/blob/d7c2dd1868c70f0addce2c0a4d3220149452f14b/research/clifford-four-qubit-threshold/verify.py)
and source closure. All eighteen files remain byte-exact under
`retained/source7766/`. Its complete registered scientific verifier
runs unchanged. The new checker reuses its literal gate and Pauli
conventions and exact quotient multiplicity routine.

Nick Petalas (@petalas) supplied the [width-nine quotient proof](https://github.com/petalas/integer-mult-bounds/blob/ff12ca358d601a21cd4b1f016b8a3a969ac44016/research/clifford-four-qubit-width-nine/README.md),
[81-row projection](https://github.com/petalas/integer-mult-bounds/blob/ff12ca358d601a21cd4b1f016b8a3a969ac44016/research/clifford-four-qubit-width-nine/PROJECTION.json)
and [archive reader and table parser](https://github.com/petalas/integer-mult-bounds/blob/ff12ca358d601a21cd4b1f016b8a3a969ac44016/research/clifford-four-qubit-width-nine/verify.py)
in [PR #7747](https://github.com/CrocSwap/integer-mult-bounds/pull/7747).
The new four-row extractor follows that parser's record and row order,
and reuses its archive authentication. Its original replay remains
in the retained closure.

alephnan (@alephnan) supplied the
[Pauli-sector and quotient framework](https://github.com/alephnan/integer-mult-bounds/blob/f7f32a18dde54e67624a9ed9cc7e1b266d9585c0/research/clifford-three-qubit-threshold/PROOF.md)
in [PR #6714](https://github.com/CrocSwap/integer-mult-bounds/pull/6714),
with the stated OpenAI Codex assistance. All notices and prior credit
remain intact. The full three-qubit suite is not rerun here.

The ordinary S8(2) character table credits the ATLAS. The exact release
is [Thomas Breuer's CTblLib 1.3.11](https://www.math.rwth-aachen.de/~Thomas.Breuer/ctbllib/ctbllib-1.3.11.tar.gz).
`EXTERNAL.json` pins its archive, table member and derived columns.
The table is a mathematical input; authentication and projection do
not reconstruct it from group multiplication. The restriction test
uses classical induction and Frobenius reciprocity. No new general
character theory or global literature priority is claimed.

Source commits are content pins, not ancestry claims. `SOURCES.json`
records canonical main provenance, and `SOURCE-PINS.json` authenticates
all eighteen retained files.
