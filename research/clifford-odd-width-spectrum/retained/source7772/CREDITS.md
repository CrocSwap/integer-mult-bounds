# Sources and credit

Ali Romman (@aliromman) prepared the complete spectral calculation,
recovery contract and literal one-qubit calibration with substantial
OpenAI Codex assistance. New material is Apache-2.0. No independent
human or formal proof-kernel acceptance is claimed.

Ali Romman's [PR #7766](https://github.com/CrocSwap/integer-mult-bounds/pull/7766)
supplied the [width-thirteen decomposition](https://github.com/aliromman/integer-mult-bounds/blob/d7c2dd1868c70f0addce2c0a4d3220149452f14b/research/clifford-four-qubit-threshold/PROOF.md),
[all multiplicities](https://github.com/aliromman/integer-mult-bounds/blob/d7c2dd1868c70f0addce2c0a4d3220149452f14b/research/clifford-four-qubit-threshold/RESULT.json)
and [checker](https://github.com/aliromman/integer-mult-bounds/blob/d7c2dd1868c70f0addce2c0a4d3220149452f14b/research/clifford-four-qubit-threshold/verify.py).
All eighteen package files are retained byte-exact. Its full verifier
runs unchanged. Its threshold is not claimed again as a new result.

Nick Petalas (@petalas) supplied the
[ordinary Sp(8,2) projection](https://github.com/petalas/integer-mult-bounds/blob/ff12ca358d601a21cd4b1f016b8a3a969ac44016/research/clifford-four-qubit-width-nine/PROJECTION.json)
and [archive parser](https://github.com/petalas/integer-mult-bounds/blob/ff12ca358d601a21cd4b1f016b8a3a969ac44016/research/clifford-four-qubit-width-nine/verify.py)
in [PR #7747](https://github.com/CrocSwap/integer-mult-bounds/pull/7747).
His full six-file package is retained through the source closure. The
published table credits the ATLAS and Thomas Breuer's CTblLib. Its exact
archive and member pins remain in the source EXTERNAL.json. This result
uses the authenticated projection; it does not repeat archive extraction.

alephnan (@alephnan) supplied the
[projective Gram normalization, odd Pauli sector and Schur propagation](https://github.com/alephnan/integer-mult-bounds/blob/f7f32a18dde54e67624a9ed9cc7e1b266d9585c0/research/clifford-three-qubit-threshold/PROOF.md)
in [PR #6714](https://github.com/CrocSwap/integer-mult-bounds/pull/6714),
with the stated OpenAI Codex assistance and prior credit. That proof is
retained unchanged. Classical character theory, the Schur product
theorem and singular-value recovery bounds are not new general theory.

Related three-qubit conditioning results are
[PR #6794](https://github.com/CrocSwap/integer-mult-bounds/pull/6794),
[PR #6822](https://github.com/CrocSwap/integer-mult-bounds/pull/6822) and
[PR #6826](https://github.com/CrocSwap/integer-mult-bounds/pull/6826).
They concern a different group and are not executable dependencies here.
The full width-ten nullity in
[PR #7771](https://github.com/CrocSwap/integer-mult-bounds/pull/7771)
renewed the conditioning question; its even-sector tables are not used.

SOURCE-PINS.json authenticates the retained source closure. SOURCES.json
records canonical-main provenance. Source pins do not assert ancestry.
All notices remain intact. No global literature priority is claimed.
