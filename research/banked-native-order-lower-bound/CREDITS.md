# Credit and source pins

Ali Romman prepared the universal lower bound, maximal forced-set
characterization, 24-owner certificate and exact single-anchor rank
ceiling with substantial OpenAI Codex assistance in research, code,
verification and writing. New material is Apache-2.0. Reachability,
finite-field rank certificates and information dimension are standard
methods. No new general principle is claimed for them.

Nick Petalas supplied the 2106-bank order, allocation/replay code, graph
export and open all-order question in
[PR #7724](https://github.com/CrocSwap/integer-mult-bounds/pull/7724),
head `ef52676eb20c252f5786f42a70ef0dd814400a03`. Its
[proof and credit](https://github.com/petalas/integer-mult-bounds/blob/ef52676eb20c252f5786f42a70ef0dd814400a03/research/banked-native-row-order/README.md)
and [verifier](https://github.com/petalas/integer-mult-bounds/blob/ef52676eb20c252f5786f42a70ef0dd814400a03/research/banked-native-row-order/verify.py)
are retained unchanged. The graph reader and upper-bound construction/replay
are called directly. The upper bound is prior work, not independently
reimplemented here. All 13 source package files and notices are retained.

Ali Romman's [PR #7674](https://github.com/CrocSwap/integer-mult-bounds/pull/7674),
scientific commit `26b6c469aa6c4aa04322ce25a22150f90e5fb14e`, supplied the
fifteen-pivot graph, banked row semantics and physical model. Its
[proof](https://github.com/aliromman/integer-mult-bounds/blob/26b6c469aa6c4aa04322ce25a22150f90e5fb14e/research/p104-banked-transfer-pivots/PROOF.md)
and [PR #7681's storage contract](https://github.com/aliromman/integer-mult-bounds/blob/1753a3ff56be34b09a217b12b590f51eba15defb/research/banked-native-snapshot-reuse/PROOF.md)
supply the model used here. The latter proof is retained. The integer
coefficient pass follows their exact-grid method. SYLforge supplied the
native word and caller in
[PR #7669](https://github.com/CrocSwap/integer-mult-bounds/pull/7669).

Clear1nsight supplied the comparator encoding and graph digest in
[PR #7682](https://github.com/CrocSwap/integer-mult-bounds/pull/7682).
The [published digest](https://github.com/Clear1nsight/integer-mult-bounds/blob/1b4a4d6f9370b8c93b3f769a6229a9111ef3940e/research/p104-role230-banked/evidence/WIRE-RESULT.json)
identifies the peer graph, distinct from that package's changed role-230
candidate. The retained notices preserve DreamingOfClouds, Clear1nsight,
Rohan Arun, Jerry Chen / CubeJerry, Douglas Colkitt, icekylinx, unpaidmoon,
and all other predecessor credit and assistance disclosures.

SOURCE-PINS.json binds 15 retained files by source commit, path, Git blob
and SHA-256. SOURCES.json binds the canonical-main catalogue and selected
record as provenance. No pending source ancestry is asserted. The source
verifier and graph are not patched. This is source-aware author checking,
not independent human or formal-kernel acceptance.
