# Independent review of the current249 cohort rewrite

## Outcome

The final `cohort-transform.cpp` was copied, freshly compiled and replayed independently. Final source SHA256:

    5c59929f8691582fd54aa7568145851ea21818965b055b8eba4e46580ebd18fc

The five outputs (record stream, extra frames, initial frames, selection and replay receipt) are byte-identical to the parent lane's outputs. Fresh replay proves all 20,107 F2 formal columns in each direction, with nonvacuous omitted-Q and omitted-Q-inverse controls. It chooses 132 disjoint pairs and reduces the literal raw rank mass from 434,177 to 434,045. This review does not assert bank completion or a final exponent.

## Independent mathematical and geometric checks

A separately written chronological checker inspected the actual rewritten stream, not just the transform's assertions:

- 264 chosen helpers are distinct, are genuine helper indices, and have zero intersection with the 527 source-owner keys or the 1,760 concrete donor keys.
- All 132 new rank-one bases have cleared H0 Gram value 36 and annihilator rows orthogonal to the basis; each is contained in both helpers' first frames.
- New frame identifiers do not collide with the inherited inventory (largest inherited ID 150,370).
- Every one of 786,359 ADD events has both actual operands in its stated common frame.
- Every one of 98,689 MOVE events starts at its recorded frame, follows exact nesting, and charges exactly the dimension difference.
- All 24 concrete COPY/ERASE lifecycles remain balanced, with the same temporary and endpoints; no chosen helper is a copied-center source.
- Every final frame matches the required final state.
- Exactly 81,591 distinct containment pairs were checked using integer dot products. The largest inherited integer coordinate has absolute value 7, so the 128-bit accumulation is safely exact.

Receipt: `INDEPENDENT-LEGALITY.json`; source: `cohort-legality-independent.cpp`.

A second native checker recomputed the concrete prefix response at the actual current249 cut from the old record stream. For every selected pair, its two response columns agree at all 1,760 targets: **232,320 exact F2 equalities**, including 543 nonzero common target responses. Every original-source/helper row is unchanged at the cut. This independently verifies the cancellation condition instead of assuming the synthesized candidate's `new_targets` metadata.

Receipt: `INDEPENDENT-PREFIX.json`; source: `cohort-prefix-independent.cpp`.

## Why the rewrite is sufficient

The selected helpers are untouched independent dirt before the cut, except for already-observed target corrections. A new common rank-one entrance E is contained in both first frames. The paid shear adds the first helper to the second at E, after removing the first helper's initial correction reads. Their identical target response means the added helper contribution cancels over F2. Exact nested transport allows this common entrance component to be carried into either first frame. After the full computation, both helpers reach the common full frame and the inverse shear restores their original independent dirt. The fresh whole-word columns confirm this composition on the actual transcript, while the independent prefix and chronological tests establish the relevant cancellation and frame preconditions.

The cancellation argument is **for F2 payload**. The address field is the separate odd-characteristic field used by the original compiler. Equal responses do not justify the same global rewrite over the integers; no such claim is made. The illustrative signed cohort example elsewhere has a separate signed response pattern and must not be confused with this actual bit-word theorem.

## Code review findings

No functional defect was found in the final source. The former tautological final-frame check was corrected by the parent before the final source was frozen; the independent checker verifies the full final-state condition again. The transform assumes the fixed six-integer event layout and trusted pinned candidate/export schemas. The independent audit checks the role ranges, frame IDs, common ADD frames, source-owner exclusion, copied-temporary lifecycle and final states that matter for this concrete instance. Source/frozen-input hashes are saved in `SHA256.json`.

Completion of the copied-gauge bank geometry, finite toll and exact outer assembly are assigned to the other lanes. Those are not silently included in the claims above. No files in another worker's lane were edited and nothing was published.
