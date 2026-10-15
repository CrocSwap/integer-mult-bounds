Task ID / proposed scope key: `bit-new-register-model` / `odd-denominator-augmentation-three-data-any-aux`

Cycle seed: `16c9467a282673c96099aae5db2415a9`; track `bit-mechanisms`; priority revision 4. Exact base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. Catalogue SHA-256: `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`. Selected-record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.

Concrete object and question: three active data roles with 3x3 address targets and any number of auxiliary registers. Can one extra-register construction use fewer than nine rank-one paid calls when every paid address frame and each data target lie in one common odd-denominator lattice, with each target invertible modulo two?

Scope status: refined. Change from the broad `bit-new-register-model` card: restrict the additive address frames to a common odd-denominator lattice and the three data targets to matrices whose odd-denominator-cleared reductions are invertible modulo two. This isolates an exact larger-register model and makes the excluded mechanism explicit: any improvement here must use even-denominator frames or a target singular modulo two.

Predecessors and differences: the three-register abelian theorem proves nine calls without auxiliaries; `bit-dirty-auxiliary-registers` treats two data targets with up to two dirty auxiliaries and leaves three data targets plus an auxiliary open; `bit-one-relation-any-registers` handles arbitrary register counts only when the frame relation rank is at most one. PR #1974 is a finite GL3(F2) address census, and PR #2027 is a UT4(F2) tariff; both use different address groups. The fresh complete cached overlap (366 open PRs; 749 discussions, 2026-10-14 19:16Z/19:12Z) found no exact odd-denominator augmentation claim.

Method and domain: map the formal group algebra into the square-zero extension `F2 ⊕ M3(F2)` by `[A] -> 1 + qA mod 2`, where odd `q` clears the common denominator. The first-order coefficient of a k-call word is a sum of k matrices of rank at most one on the combined register/address space. The data target coefficient has rank nine. Prove this uniformly for any number of auxiliary roles and free interleaved GL mixing. Build an exact nine-call positive control for `C1=I`, `C2=I+E21`, `C3=I+E32`.

Optimistic full cost: give all auxiliary storage and free scalar mixing away. The lower bound still requires nine paid calls, equal to the direct construction, so this submodel has no call saving. This says nothing about even-denominator frames or physical supplier costs.

Success/falsification: a written uniform rank proof, exact formal replay of the nine-call construction, and controls for a deleted call, a perturbed endpoint, and an even-determinant target outside the nine-call premise. Stop when the proof and receipt are independently reproducible; no search over larger alphabets is needed.

Expected deliverable: exact theorem and bounded interface result, with predecessor attribution, source pins, registered replay, meaningful controls, and no new kappa/supplier claim. No PR unless the written result adds evidence beyond the existing scoped register bounds.
