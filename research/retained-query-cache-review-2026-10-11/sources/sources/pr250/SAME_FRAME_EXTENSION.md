# Exact same-frame rational maps: critic extension

For k role streams carrying the **identical exact** frame representative F, every scalar map A on their role index commutes with the common transform:

    (I_k ⊗ F)(A ⊗ I) = A ⊗ F = (A ⊗ I)(I_k ⊗ F).

This identity does not require invertibility. Invertibility of A is required to undo the operation on arbitrary dirty registers. Thus a rational scale, swap, or full invertible local flow map is a valid same-frame telescope step. Both orientations are available because A^{-T} is again a scalar role map at those same representatives. Equality of rank, binary support, or symplectic action alone is insufficient: relative phase mismatch can break the identity.

`same_frame_controls.py` checks exact rational examples and rejects a relative-sign mismatch. This is a finite illustration of the tensor identity, not its only justification.

## Physical and arithmetic obligations

- Every gate's participating roles must be at the literal common F at that event. A future frame or matching rank does not suffice.
- The global allocator must retain every dirty coordinate and give a once-only invertible map; zero-fresh is not zero-dirty. No discard/reinitialization is permitted for dirty roles.
- Swaps can be charged as three additions and a sign change. A scale can use one disjoint coefficient stream: copy the original, apply its literal arithmetic, replace the destination, and clear the coefficient stream. Both real components must be charged. This temporary has a bounded overlapping lifetime; it is not a new free role or random-access operation.
- Exact inspected local inverse coefficients in the actual lift are ±1, ±1/2, ±2, with inverse operations of the same bounded type. Center scatter retains division by3 or6. These do not introduce new denominator primes beyond the retained2/3 grid, but every multiplication/division step contributes to grid exponent, height, and rounding/recovery bounds.
- Replacing an add-only primitive grammar requires a written lowering argument. Existing Lean proofs for a different literal word are not claimed to check these new gates.
- The old-response tableau must include all center responses, and inverse cleanup must use the new local maps. Terminal-center pivots preserve the old single-cut interface but change the dirty map.

## Current admission status

The composition worker's finite bill is an explicit conservative arithmetic overcharge, not an emitted primitive transcript. Its large retained guards have room, but correctness of numerical guard inequalities is distinct from proving every macro lowers within its assigned bound and storage. The same-frame lemma discharges the mathematical gate-compatibility issue; the exact slot allocator and local invertibility discharge corresponding finite structural issues. A complete conditional construction can be justified by these compositional proofs plus exact global fresh-response and dirty-lifting identities, without a dense global matrix replay or rebuilding the entire old theorem. It still needs an auditable mapping from every flow read, source correction, terminal center and slot event into that argument, and justified primitive/precision charges. Until that mapping is delivered, the new five-stage profile is a prospective construction, not an admitted supplier merely because its moment passes.
