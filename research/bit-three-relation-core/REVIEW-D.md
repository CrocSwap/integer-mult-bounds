# Independent review of the five-dimensional binary core

Jerry Chen (@CubeJerry), with substantial OpenAI Codex assistance. Independent worker-D review,2026-11-06 at10:28UTC. Reviewed worker-c/research/bit-three-relation-core/PROOF.md, SHA25619ea0115a0d4939bf0bbac8cb6263b1cb38b2cfa49724f6a436fa7fc423cf5e1. Primary scope:Sections4–5 and7. Sections2–3/6 receive a separate worker-A audit. Human/proof-kernel acceptance is unclaimed.

**PASS in the stated scope.** The unique irreducible five-dimensional pool and explicit witness are correct. The full-rank lattice argument justifies removing free coordinate-call generators under its hypotheses. It does not produce a diagonal rank-saving word or paid-rank inequality.

In Section4, E is a coordinate subspace contained in V, so subtracting its component produces w supported outside E. The edge lifts become four coordinate projectors after the stated shear. Their disjoint-edge sum is unrealizable because the two forced entries imply an unwanted cross entry. Remaining projectors have common off-block column and row. If either vanishes, w or E is invariant. Otherwise binary rank-one factorization forces both fifth-coordinate factors to equal1 and determines one remaining restriction. Irreducibility forces every entry of the two off-block vectors to be1. The basis-generation argument proves irreducibility without enumeration.

In Section5, B=(e1+e3+e4)(e0+e2+e4)^T is idempotent. The fixed nonzero outside row and column in its pattern coset force x4=y4=1 and determine all other entries; only B lifts that coset. The two edges supply exactly their four lifts. The involutory shear sends these to E00,E11,E22,E33 and B to J5.

The standalone independent check_bit_core.py enumerates all496 binary rank-one idempotents, recovers exactly the five-projector pool, verifies exactly two edges and joint-image dimension5, checks the shear, and exhausts all372 nonzero proper subspaces in both bases. Neither alphabet has a proper invariant subspace. Deleting B restores the four-coordinate invariant subspace; a changed covector is rejected. Normal and optimized isolated Python outputs agree. This finite evidence verifies the fixture, not the universal-width theorem.

In Section7, saturation and rankL0=rankL=3 imply L0=L. Full pattern dimension3 makes first-order coefficient rows span L/2L. Their zero coordinate-call entries force every relation entry there to be even. Cube entries are−1,0,1, so they must be0; the cube rational span then forces all lattice entries there to be0. This proves the free-generator split. The rankL0≤2 cube-fiber lift preserves coefficient fibers and uses the retained two-relation theorem.

After free coordinate calls are removed, the pool joint image is invariant and the quotient word is identity. Monomial independence decomposes each invariant space by equal endpoint labels. Applying this at every invariant-flag term keeps the endpoint diagonal while giving block-upper-triangular subquotients. Each rank-one idempotent has one active diagonal block. The warning that the later five-projector shear can spoil endpoint diagonality is essential and correct; it is not a free physical operation.

Three clarifications were incorporated before this pin: exclusion of the disjoint-edge sum, equal-label basis adaptation at every flag term, and removal of the erroneous fixed number of coordinate-call generators. No remaining objection was found in the assigned scope.

Inherited context read:#6777 head e62a9d0d4143e11c190fcb4d81d83dc1662da782, sources/research/bit-two-relation-any-registers/PROOF.md. No predecessor executable was imported by the independent checker. Exact script/report hashes can be bound in the final package manifest.

## Final proof and general quotient-bound addendum

Final proof SHA256:1fad3fa92b26bcd290b179ee3b714c3d25017bc63fa2439124e2e10ddb2c374c. The inherited citation-prefix edits are presentation-only. I independently checked the new general corollary in Section3 and the corresponding word-relevance update.

Let E be exactly the coordinate span of the endpoints of all e edge patterns, and P0 their e-dimensional span. Within each nonzero coset of P/P0, off-pattern differences are supported inside E. Two independent image classes modulo E would, by the quotient observation, produce a single-edge pattern in P with both endpoints outside E, contradicting E's definition. Over F2, pairwise-dependent image classes span at most one dimension. The zero coset contributes only inside E, and the edge lifts imply E⊆V. Summing the 2^(r−e)−1 nonzero cosets proves dimV≤dimE+2^(r−e)−1.

The required coordinate-span wording has been made explicit. Since dimE≤2e and f(e)=2e+2^(r−e)−1 is convex on[0,r], f(e) is at most max(f(0),f(r))=max(2^r−1,2r). Thus every r=3 pool has joint image at most7; the e=1 bound is5. These are upper bounds without new sharpness claims. The unique irreducible five-dimensional classification remains specific to e=2, as correctly stated in the final table and Section7. The extension is sound; no additional finite enumeration is needed to prove it.
