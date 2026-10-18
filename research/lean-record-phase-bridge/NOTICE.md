# Attribution

Gareth Davidson (`bitplane`) prepared `RecordBridge.lean`, the new finite oracle,
verification harness, controls and documentation with substantial OpenAI Codex
assistance. New material is Apache-2.0. No independent human review is claimed.

AAAmirinu, with Codex, supplied PR2378 at
`5816f94741709e8082e06a2cc9a114ff87411f3d`: the unchanged signed-word and
selected monomial coordinate proofs, source binding and existing packed tests.
`PREDECESSOR.json` records exact commit, source path, Git blob and SHA256 for
every retained file. The active lakefile only adds the RecordBridge target;
the original is retained under `sources/pr2378/`.

Jose Manuel (`jmbarrancoml`), with OpenAI Codex, supplied PR2250 at
`d404b48a1e7b147556b309497d55089c837dddb2`: the unchanged Python streams,
Compact and monomial implementation, proof and notice. The selected recipe
retains the original source and contributor lineage recorded by those notices.

Our PR2341 at `f448ce821ba32001bf1ec13f7088450d2edcd112` supplied the unchanged
common-label tensor lift. DreamingOfClouds supplied the unchanged Lemma G Lean
source, with Claude assistance and its retained notice. That notice credits
Zhihao Chen, chafreaky, Dugongue, jamesyc and the surrounding contributor chain.
Mathlib and Lean retain their upstream licenses and exact dependency pins.

The kernel harness and nine control groups adapt our PR2404 at
`d7db77c9e3f19fd1196393c045e597539fdcfc8a`, itself following PR2341/2295.
Most-negative, repeated-constant and inverse-order witnesses were already
identified by the predecessors; this package applies them to the composed
all-field boundary. It does not claim those observations as new defects.
