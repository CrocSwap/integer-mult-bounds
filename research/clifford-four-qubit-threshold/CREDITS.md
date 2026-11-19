# Sources and credit

Ali Romman (@aliromman) prepared the sharp four-qubit threshold proof, the missing-block
argument, explicit character relation and checker with substantial OpenAI Codex assistance.
New material is Apache-2.0. Independent human and formal proof-kernel
acceptance are not claimed.

Nick Petalas (@petalas) supplied the width-nine four-qubit quotient,
rank calculation and released width-ten question in
[PR #7747](https://github.com/CrocSwap/integer-mult-bounds/pull/7747).
All six files of the [source package](https://github.com/petalas/integer-mult-bounds/tree/ff12ca358d601a21cd4b1f016b8a3a969ac44016/research/clifford-four-qubit-width-nine)
are retained byte-exact. The [source proof](https://github.com/petalas/integer-mult-bounds/blob/ff12ca358d601a21cd4b1f016b8a3a969ac44016/research/clifford-four-qubit-width-nine/README.md)
supplies the tuple identification. Its [projection](https://github.com/petalas/integer-mult-bounds/blob/ff12ca358d601a21cd4b1f016b8a3a969ac44016/research/clifford-four-qubit-width-nine/PROJECTION.json)
and [checker](https://github.com/petalas/integer-mult-bounds/blob/ff12ca358d601a21cd4b1f016b8a3a969ac44016/research/clifford-four-qubit-width-nine/verify.py)
supply the separate signed-sum check and unchanged source replay. Their
notices credit the ATLAS and Thomas Breuer's CTblLib 1.3.11 for the ordinary
character table. The release archive and exact table member were authenticated, and the
unchanged source extractor rederived the retained projection.

alephnan (@alephnan) supplied the odd-sector and quadratic-character
framework in [PR #6714](https://github.com/CrocSwap/integer-mult-bounds/pull/6714),
whose [proof](https://github.com/alephnan/integer-mult-bounds/blob/f7f32a18dde54e67624a9ed9cc7e1b266d9585c0/research/clifford-three-qubit-threshold/PROOF.md)
is retained byte-exact. That package reports substantial OpenAI Codex
assistance. Its notices retain the pointwise framework from Ali Romman's
[PR #5526](https://github.com/CrocSwap/integer-mult-bounds/pull/5526),
MatShep's small-qubit results, Nick Petalas's lower bound and the
Lee--Yu--Peng--Lai table. Those earlier numerical suites are not replayed here.

The Dickson sign homomorphism is classical, not a new result. The proof
uses D. E. Taylor, *The Geometry of the Classical Groups*, Theorem 11.43,
printed page 160, which credits Dye (1977).
[Author's text](https://www.maths.usyd.edu.au/u/don/papers/gcg.pdf#page=168)
No book content is copied into the package. `EXTERNAL.json` records this
mathematical input.

The new contribution is the sharp threshold T(4)=13, the complete
width-eleven quotient support, the width-twelve inflated-block obstruction,
and the complete width-thirteen support. The additional Dickson proof
gives the absent width-ten module, explicit character coefficients and
the result for qubit counts divisible by four. Seven retained source
files have exact Git blob and SHA-256 pins in `SOURCE-PINS.json`.
`SOURCES.json` records canonical selected-record and catalogue provenance.
Content pins do not assert unmerged ancestry.
