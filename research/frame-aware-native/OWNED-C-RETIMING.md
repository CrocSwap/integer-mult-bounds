# Sufficient theorem: exact retiming of the complete owned-C wire

## Statement

Let V be a vector space over a field containing the rational scalar coefficients. For every permitted coordinate chart f let C_f be a specified invertible linear operator on V, including its exact absolute phase. A register with chart tag f and decoded logical value x physically contains C_f x. Assume a paid native implementation is supplied for every newly used transition

T_(a,b) = C_b C_a^(-1),

including its exact scalar phase and a correct tariff. Let an existing finite program use persistent arbitrary-input registers and one owned scratch register C, with the following operations: scalar ADD between registers in a common chart; scalar multiplication; owned COPY in a common chart; owned CLEAR; pure coordinate transitions; and specified physical warp operations with fixed source and target chart references.

Then one may replace the coordinate chart at any scalar contact, including contacts involving the owned C register, provided all of the following are done:

1. Preserve the chronological scalar operands and coefficients, apart from separately proved exact monomial replacements.
2. Give every live register, including owned C, a consistent chart at every event. Before a scalar ADD/COPY, all participating registers must occupy the declared common chart.
3. Insert and pay the actual transition T_(a,b) between consecutive incompatible live contacts on each register, in either direction. Do not keep a fixed charge of eight for the owned-C path.
4. After a CLEAR, choose any chart for the now-zero C register without a Fourier transition; CLEAR itself retains its original scalar charge. A later COPY must still have a common chart with its source.
5. Preserve each fixed physical warp, its exact absolute phase, and its declared input/output charts. Insert any required transitions before and after it.
6. Restore the prescribed final persistent ABI charts, ownership labels and field order. Preserve the final CLEAR of C.

Under these sufficient conditions the retimed program has exactly the same decoded logical endpoint on every arbitrary persistent input and on an arbitrary initial C value. It uses the same one owned field and gives C no productive output credit. Every productive helper retains its original whole input/output operator when its original endpoint charts and logical identity are preserved.

The theorem permits more than eight C transports if necessary. It permits fewer or lower-rank C transports only after those actual edges have been emitted and priced. Internal frame retiming alone does not establish a multiplication exponent.

## Proof

Maintain the invariant that the physical content of every live tagged register r is C_(f_r) x_r, where x_r is the corresponding decoded logical value.

For a transition, T_(a,b) C_a x = C_b x. Thus its decoded value is unchanged, in either direction, and no nestedness assumption is needed for the algebraic equality.

For a common-chart ADD with coefficient q, linearity gives C_f x + q C_f y = C_f(x + q y). Scalar multiplication similarly gives q C_f x = C_f(q x). COPY reproduces C_f x in the owned register, hence its decoded value is x. CLEAR produces physical zero, and C_f 0 = 0 for every chart f; consequently a cleared register may be tagged by any chart without an additional physical Fourier operation. Its arbitrary old input has already been erased by the explicitly charged CLEAR, rather than silently assumed zero.

At a retained warp with physical operator W and fixed input/output references a,b, the decoded action is C_b^(-1) W C_a. This is unchanged because the same W, a and b, including W's absolute phase, are retained. Required changes to reach a are paid separately.

Apply these identities by induction over all emitted events. The scalar logical program is unchanged, so its endpoint agrees with the original on every input. The final ABI and erasure clauses give the actual persistent endpoint and zero owned field. Whole-helper productive widths depend only on their unchanged original endpoint operators and independent input roles; no intermediate C contents create an extra helper. This proves the theorem.

For a two-role monomial replacement, the same induction uses the already proved unequal-chart swap identity: registers E x and G y can be swapped and scaled to G(a y), E(b x), with exchanged chart tags. Coefficients and signs must be emitted; merely changing a role permutation is not enough.

## Why the original eight rank-8 centers qualify

This argument applies to the original full-identity native center transports, not to every operation named a center in neighboring packages. The authenticated `full_identity_rebuild.py` function `split_centers` explicitly defines an original center operator as

`canonical_frame(9, frames[old]).adjoint().then(canonical_frame(9, frames[new]))`.

In the library's `then` convention this is C_new C_old^(-1). Backward orientation uses its explicitly computed complex-conjugate operator. The function splits the eight-dimensional transport through an intermediate chart and checks that the two exact Clifford pieces reproduce the whole, including absolute phase. Therefore these eight center events are pure coordinate transports and fit the theorem.

The retained literal native evaluators likewise change only the owned register's chart at a center event; its decoded logical row is preserved. The physical definition above is essential: logical-row replay alone would not establish that no phase or hidden logical operator was omitted.

The extra rank-1 external H112 completion in `rebuild_native.h_child_recipes` has different external endpoint references and an explicit warning about phase adapters. It is not being identified with these rank-8 center events, and this argument does not erase its cost.

## Actual pricing and verification requirements

For a newly used nested pair of canonical subspace charts, the claimed rank may be the absolute difference of their dimensions only after exact Clifford lowering confirms it. For a nonnested pair, compute the actual Fourier/B-block rank of C_b C_a^(-1); dimensions alone are insufficient. All normalizers and global phases must be serialized and decoded in both orientations.

The C wire must be included in the contact graph. CLEAR breaks its dependence on the previous C content and gives a free zero-chart reset. COPY and every ADD involving C couple it to the persistent contact's chart. Any transport between these contacts is a paid C edge. An optimizer that changes those contact charts independently while retaining an unchanged rank-8 center invoice is invalid.

A completed candidate still needs all-column logical/physical endpoint replay, exact paid profile, all changed edge phase certificates, scalar allowance, prefix/conditioning bounds and the retained outer compiler premises. No new kappa is asserted by this theorem alone.

## Source and credit

The source anchor, canonical main commit and SHA-256 are in `owned-C-source.json`; an exact source copy is preserved beside it. The original full-identity supplier, owned-center reuse and exact center factorization are predecessor work from the repository's credited #4359, #4440, #4441, #4447 and #4470 lineage, including zxv, Jacob Alan Sussman, Cinna Davis and the native/scalar/Clifford contributors retained by those packages. The new contribution is the explicit complete owned-wire retiming theorem and its use as a sufficient replacement rule. Prepared for Dugongue with substantial OpenAI assistance. Apache-2.0.
