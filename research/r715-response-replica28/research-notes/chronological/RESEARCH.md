# Chronological rewrite and target-normal-form research

## Outcome and scope

This lane supplies reusable sufficient rewrite constructions and reproducible bounded native searches. It does not supply a third positive optimization for the current deliverable. The existing checked14-factor target interval layer remains unchanged. The two other lanes' positive mechanisms are unaffected.

All experiments used the pinned PR473-derived word or the subsequent source-injection-cancelled word. No current public PR was broadly reverified. No Lean file was changed or newly kernel-checked. No publication or cleanup occurred.

## Structural sources actually retrieved

`SOURCE-HASHES.json` records exact bytes for seven actual source files inspected:

- Mathlib `LinearAlgebra/Matrix/Transvection.lean`: transvection multiplication and matrix row operations; `transvection_mul_transvection_same` derives parameter addition from square-zero matrix units.
- Imported TenProofs `ConnesRigidity.lean`, lines1416-1448: `specialLinear_transvection_commutator` explicitly expands matrix units, proves six zero products, and uses the remaining product to construct the commutator. This is the exact sufficient algebra behind noncommuting transport.
- Our `LiGuanCNOTFallout20260905.lean`: `recorder_comp`, `recorder_square`, `recorder_commute`, `word_map`, and `within_embedding_iff`. The central cross term is explicit; an embedding transports the same generator word and does not automatically improve its cost.
- CSLib `Foundations/Relation/Confluence.lean`: `Diamond.extend` and `Diamond.toConfluent` construct joining reductions. We do not assume that the cost-oriented rewrite system below is confluent; finite witnesses suffice.
- OAI `Topology/ArtinGroups/Quivers/OrthogonalVertices.lean`: normalized commuting twists are reindexed into a common direct-sum carrier, with matching placement and block differential. This motivates checking the complete transformed carrier, not just scalar commutation.
- OAI `Computability/Scheduling/NodeCertificates.lean`: `NodeData.reorder` transports node invariants under `FixedOutside` and `Respects`, retaining explicit boundaries. Our candidate moves separately check frame boundaries; this theorem does not itself license matrix rewrites.
- Hadamard6 `BlockSwapMatrices.lean`: explicit row/column permutations preserve the Hadamard Gram identity and equivalence. Pure permutation conjugation is correctly distinguished from an actual paid improvement.

These are source readings, not new kernel certificates. Historical typed DAG hits include standard-axiom records for LiGuan CNOT generator matrices, but that is not a fresh source-bound audit.

## Coverage

`SOURCE-SEARCH.json` preserves five bounded unified-source queries and three typed-DAG structural symbol queries. The actual registered source catalogue and canonical typed DAG were queried read-only. Searches also traversed installed package sources, project Meta modules, the imported OpenAI Lean tree, and the leanlibs tree for triple-product, transvection, diamond/confluence, and commutation structures. The OpenAI/leanlibs recursive file-content search completed and returned hundreds of matching files. Seven relevant source files were read in detail; several further files were nominated to sibling workers. This is broad structural retrieval, not an assertion that every theorem in the entire registered corpus was read. SQL query result limits are recorded and must not be described as exhaustive retrieval.

## Sufficient construction A: noncommuting transvection transport

Let A update y by x, and B update x by h, where y,x,h are distinct registers over F2. Computing both sides on arbitrary register values gives the exact chronological identity

    A ; B  =  B ; C ; A,       C: y += h.

The source h is unchanged by A and B. This is the elementary commutator correction from the imported SL theorem. Repeating it across an interval moves an existing y+=x instruction across donor writes. Every crossed donor increment must be added to the receiver's increment parity; an existing identical receiver increment may be removed instead. No clean-input assumption is needed for the scalar identity.

To lift the identity to the existing framed program, the executable requires every changed target path to be monotone in the actual rational frame lattice. Each new helper read uses a frame where that same helper was already read. The moved target read uses an existing minimal join of current target frames. Other target reads crossing the two-register interval are excluded in this bounded version. This makes the finite screen conservative. A surviving candidate still requires the complete native signed/formal-column audit and integer operand span audit before admission.

`transport.cpp` checked29,464 placements,22,198 legal frame paths,zero strict paid-moment improvements. `transport_neutral.cpp` also sought lower scalar instruction count at nonincreasing moment and found zero. These results do not rule out simultaneous transport through further target-read barriers.

## Sufficient construction B: simultaneous GL3 target basis

For three arbitrary target values x and a prefix increment vector V, choose an invertible matrix M over F2. Apply M at entry, replace V by M V, then restore M^-1 at exit. The exact endpoint is

    M^-1 (M x + M V) = x + V.

Each original helper read contributes one coordinate unit to V. The transformed read multiplicities are the corresponding column of M, reduced by parity. This is a full invertible basis change, not an assumed gadget. A matrix can be emitted by Gaussian row operations (transvections); all 168 elements of GL3(F2) have explicit short words. Our screen used a common recovery frame and only pre-existing helper read frames, requiring exact monotone target paths. No large matrix or exponential tensor is materialized.

`gl3.cpp` tested62,999,748 matrix-window cases during its150-second bounded run;68,136 met the complete target frame constraints;zero improved the recursive moment. This is not an exhaustive proof about GL3 rewrites, since placement of helper reads and recovery frames was restricted.

## Sufficient construction C: chronological affine normal form

For a connected three-target prefix containing target reads, compute its exact affine map

    x_out = M x_in + N h,

where h is the vector of immutable helper values during B. Synthesize M by breadth-first search on the168-element GL3(F2), using the six elementary target CNOTs. Then emit N h as parity-reduced helper contributions. Either earliest or latest inherited occurrence of each helper supplies the bounded candidate placement. Preserve all remaining gates. Equality of M and N proves scalar equality for all initial target and helper values.

Frame legality must still be checked on every target and helper. The search keeps targets disjoint from outside target dependencies within the prefix. It counts scalar instructions as well as recursive transforms. `affine3.cpp` screened28 connected triples and252 legal forms, finding neither lower paid moment nor a scalar-count reduction at equal moment.

## Sufficient construction D: central-response packet deletion

At a helper-to-target read, propagate a unit target injection through the remaining target network to obtain its exact final response vector. A collection of reads of the same immutable helper may be removed together when those response vectors sum to zero. This equality is sufficient for the full final target map to remain identical; helpers are not written during B. Final native signed semantics and frame constraints remain required for any implementation claim.

`central_cancel.cpp` tested all343 helper groups in the word. No group exceeded the22-read enumeration bound, and no nonempty zero-response packet existed. This route is closely related to the algebra worker's response-kernel method, and must not be counted as an independent positive mechanism merely by changing phases.

## Cleanup checks and signed-semantic limitation

Every cleanup instruction is at FULL frame. Exact simplification of its complete operator would preserve the recursive frame invoice and could reduce scalar work.

`cleanup.cpp` implements a finite F2 trace/diamond contraction screen. Identical elementary gates cancel if all intervening gates commute with them. If exactly one dependent gate is crossed, the elementary commutator contracts A U B V A to U B C V, when A commutes with U,V and C is its explicit matrix-unit commutator with B. The2,904-gate cleanup had zero applicable contractions.

`resynthesize.cpp` reconstructs the full955-column binary cleanup operator and resynthesizes it using30 sparse Gaussian elimination orders. All resulting circuits were longer: best14,347 gates versus2,904. No candidate was saved.

Crucial restriction: the repository's signed integer/formal cleanup semantics may require the integer inverse of A, not merely a binary-equivalent CNOT word. Therefore a future positive F2-only cleanup rewrite must be checked against the actual signed compiler and, where necessary, synthesized over the integers with the permitted signs. The negative exploratory screens above establish no signed optimization. There is no hidden unproved bridge in the delivered candidate: no cleanup rewrite was admitted.

## Reproduction

C++ sources are under the same directory as this note. JSON results and executables are under F:/proof/kappa-library-three-20261011/order. They depend on the existing pinned nlohmann header directory and, for rank-aware screens, rational.hpp from the earlier scheduling lane. `SOURCE-HASHES.json` and `SOURCE-SEARCH.json` retain the evidence provenance. `SEARCH-RESULTS.json` records the source-bound results and hashes of each experimental input/output available at finalization. These are discovery artifacts, not a standalone publication certificate.
