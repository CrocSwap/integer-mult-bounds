# Independent binary certificate for the Eisenstein scalar copy floor

**Independent verification of PR2017; no new numerical bound.**
A concrete 80-by-80 binary matrix certifies the sharp scalar cost **40**
for every fitting Eisenstein decoder, with any finite number of binary totals.
The verifier checks its pairing-rank domination on **all 595984 ordered pairs**
of the 772 line-spanned flats. Flat closure extends this certificate to every
support pair.

This provides a separate proof route for Jose Manuel's
[PR2017](https://github.com/CrocSwap/integer-mult-bounds/pull/2017).
It uses binary matrix rank and complete finite domination, without importing
the predecessor's Hermitian arithmetic, trace/radical argument, rank routines,
or sample traversal. The pinned geometric coordinate input is shared.
[PROOF.md](PROOF.md) states the model and proves the coverage argument.

## Independent methods and result

The checker enumerates all 10700 generator sets of at most three ports,
then adds zero and the full span. It retains original integer root rows
as each flat's basis. Ranks over the prime 2147483647 are exact rational
ranks because every relevant Gram minor has absolute value at most 16777216.
The binary side uses bit masks and XOR elimination on two-bit port blocks.

All 298378 unordered rational comparisons and both binary orientations pass.
There are **22950 strict rank drops**. A concrete example has rational rank
four and binary rank two, with integer determinant 1024. Rank domination is
valid; equality under reduction is not assumed. The predecessor already uses
the correct inequality.

[CERTIFICATE.json](CERTIFICATE.json) contains the explicit binary witness and
complete flat catalogue. The checker reconstructs both from pinned coordinates.
[EXPECTED.json](EXPECTED.json) records counts and the ordered-input pair digest.
That receipt is a regression aid, not independent evidence by itself.

The diagonal/zero pattern, all pair bounds and rank subadditivity prove the
scalar lower bound. The known row-star decomposition attains 40.
The implementation checks its sharp witness and five semantic controls.
In particular, I_80 has the right fitting pattern but fails the pairing bound;
this detects a missing bridge that pattern checks alone cannot establish.

## Reproduce

From the repository root, with standard-library Python:

```sh
python3 -B research/eisenstein-binary-rank-audit-seed77/verify.py
```

Expected final line: `PASS_EISENSTEIN_BINARY_RANK_AUDIT`.
The JSON output records the interpreter, complete coverage and execution time.
The main research runtime is stable CPython 3.15.0.
The repository manifest keeps its explicit 3.12 compatibility environment.
Exact execution records and limitations are in [VALIDATION.md](VALIDATION.md).

## Scope and decision

This verifies the scalar theorem and its additive pairing-charge model.
It does not independently certify nonlinear encoders, shared physical pricing,
the block-linear extension, a complete supplier, or the multiplication theorem.
No selected kappa changes. No proof assistant or independent human reviewer
has checked this new package.

The newly incorporated PR2017 closes the suggestion in our earlier PR2022
handoff to try more scalar totals or another fitting matrix in the same E8 model.
PR2022's general orthogonal-frame theorem remains valid and has separate scope.
This audit credits PR2017 for the stronger E8 conclusion.

## Open next questions

Can a nonlinear message or a changed physical sharing contract escape the
additive scalar model? Specify that contract and price its complete optimistic
invoice before implementation. Neither adding scalar totals nor changing the
fitting matrix escapes the theorem. No qualifying changed contract is supplied here.

## Attribution

Jose Manuel (@jmbarrancoml), PR2017: sharp theorem and normalized Gram witness.
Jonathan Lam, PR798: geometry, pairing model and row-star construction.
Joel Pulikkan / GamingPuzzled, PR620: order-three construction.
DreamingOfClouds, PR1590: predecessor same-field Schur-rank argument.
Source commits, blobs and hashes are in [SOURCES.json](SOURCES.json).

Charles Bethin, with substantial OpenAI Codex assistance in the independent
model, implementation, proof exposition and verification. New work is Apache-2.0.
All predecessor files and notices remain unchanged.
