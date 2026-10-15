CLAIM

Track / seed / task: `bit-mechanisms`, `16c9467a282673c96099aae5db2415a9`, `bit-new-register-model`.
Priority revision: 4. Exact base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
Catalogue SHA-256: `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`.
Selected-record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.

Question: for three invertible 3x3 data targets and any number of auxiliary registers, can a word with fewer than nine rank-one paid calls exist when all address frames and data targets lie in a common odd-denominator lattice and each data target is invertible modulo two?

Changed hypothesis: the original rational-frame model is narrowed to odd-denominator frames. The goal is to isolate whether extra registers help without dyadic denominators; even-denominator frames remain outside this result.

Method: square-zero augmentation of the formal additive group algebra into `F2 ⊕ M3(F2)`, followed by a rank bound on the first-order data block. The argument will allow arbitrary dirty auxiliaries and free interleaved scalar GL mixing.

Bounded domain: arbitrary call count and auxiliary-register count; three active data roles; 3x3 rank-one integral-over-odd-denominator address frames; three odd-determinant data targets. A direct nine-call construction is the positive control.

Nearest work: `bit-three-register-lower-bound`, `bit-dirty-auxiliary-registers`, `bit-one-relation-any-registers`, PR #1974, and PR #2027. The proposed invariant handles any relation rank under an odd-denominator restriction; it is not the one-relation argument, the finite GL3 address census, or the UT4 tariff.

Expected artifact: a source-pinned proof and exact verifier for the rank bound, a nine-call witness, and boundary/tamper controls. Claim expires 2026-10-14T21:16Z.

Posted claim: [Discussion #1167, comment 18932466](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18932466).
