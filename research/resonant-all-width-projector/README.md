# All-width rank and constructive recovery for the resonant channel

For the exact 256-term coefficient A_f frozen by JoyboyBrian's PR #4797, and every integer f >= 1,

\[
\operatorname{rank} A_f = \frac{3}{256}(8^f+(-8)^f)
 +\frac1{64}(4^f+(-4)^f)-\frac18(2^f+(-2)^f).
\]

In particular the odd-width channel is zero. At even widths its rank is
`3*8^f/128 + 4^f/32 - 2^f/4`, with limiting image density 3/128.
The first even-width ranks are 1, 100, 6256 and 395200.
This answers the general-width rank question left open in Nick Petalas's
[PR #4825](https://github.com/CrocSwap/integer-mult-bounds/pull/4825).
The same certificate gives an explicit fixed-polynomial pseudoinverse and
recovers the accessible input projection from every channel output.

Run `python -I -B verify.py` from this directory, or pass its absolute path.
Python 3.10 or later and its standard library suffice. Also run
`python -I -O -B verify.py`; checks do not depend on assertions.
The verifier does not write files or invoke external programs.
It takes about 3.3 seconds on the development machine; this is replay timing,
not a multiplication benchmark. [PROOF.md](PROOF.md) proves the all-width
and recovery statements from its exact finite algebra certificate.

The result is a partial-channel theorem, not a complete supplier or a new
kappa. A projection of rank 3/128 asymptotically does not supply the omitted
independent target coordinates. A consumer still has to price those coordinates,
physical preparation, routing, ownership, restoration and every Gaussian call.
A free-algebra polynomial is not automatically an exact unit-cost Word RAM
program: fixed rational scalar operations are charged as stated in the proof.

The source TARGET.json is retained byte for byte. [SOURCES.json](SOURCES.json)
pins immutable upstream commits, hashes and predecessor credit.
The receipt [EXPECTED.json](EXPECTED.json) records exact arithmetic rather than
modular evidence or finite-width extrapolation. No Lean or kernel claim is made.

## Concrete scope and relation to κ

This completes the frozen channel's general-width rank and explicit image-recovery question. The session's requested new best κ was not obtained. No independently encoded canonical Gaussian job is inferred from a dimension count. The baseline complex comparison remains the source-bound round-3 profile of PR #4610 and its conditional native transfer #4713; the selected main certificate remains κ = 0.00302015. PR #4814's ordinary BIT saving 0.003475458 is separately scoped. The large finite cascade proposals #4813/#4818/#4819/#4826 require paid-word completion; #4842 audits their evidence, and #4856 emits an actual fused shared-port word with completion still open.

The positive mechanism here is exact finite group-algebra annihilation followed by a fixed polynomial support inverse. It replaces an unknown image recovery oracle with an explicit finite rational monomial program. Its dimension and uniform inverse bound are proved for every positive width. Compiler funding and the missing complement remain separate, priced obligations.

## Independent checks

`python3 -I -O -B independent_tensor.py` builds the actual tensor matrices independently at widths 1, 2 and 3, checks exact rank-one minors at width 2, the nonzero Gram eigenvalue and the inverse scale, and rejects discarded global phase. It does not use the regular-representation certificate to construct those matrices. All default replay is offline, standard-library Python; no C++, GPU, solver or Git is required.

## Open next questions

- Construct a chronological complete consumer for these explicit recoverable image coordinates, retaining arbitrary original owners and the complementary target. Its complete paid moment must improve before another construction round.
- Find fixed native encoders for canonical independent Gaussian jobs within the image; rank alone is insufficient. Charge every preparation, rounded fixed-rational coefficient, routing and restoration pass.
- Fund the actual consumer's source-uniform compiler, precision and outer native ledger. The projector theorem is not a new multiplication theorem or kernel audit.

Prepared by Dugongue with OpenAI Codex and three agents. The existing local MathProof Schur-block elimination and explicit covariance-composition proofs were inspected as algebraic precedents, not imported as unchecked axioms or copied into this package. No Lean formalization or fresh kernel audit is claimed.

Canonical main was pinned through a dedicated ref to 624de9dc66858af0945e5f8a0942488d62280d43. The previous PR #4841 note describing 9e33ecf0 as an advance of canonical main was erroneous: another worker's PR fetch had overwritten shared FETCH_HEAD. Its frozen discovery source was already 624de9dc and is unchanged; this release does not reuse that mutable checkpoint.

Separate optimized subprocess mutation checks rejected a changed TARGET byte, q(0) changed by 1, and a monomial multiplication that discarded all phases. MUTATION-RESULT.json records the exact rejection diagnostics. These are separate executed controls, in addition to the three internal structural checks. CROSS-REVIEW.json binds the independently reviewed original leaf; publication proof prose additionally clarifies three owned Horner buffers, payload-dependent precision and a conservative explicit O(N w) basic-arithmetic fallback. Core certificate and TARGET bytes are unchanged from that review.
