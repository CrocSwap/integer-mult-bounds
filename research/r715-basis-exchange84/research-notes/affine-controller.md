# Bit algebra lane: bounded screens and sufficient affine-controller theorem

Date:2026-10-11. No improved kappa is claimed by this lane in this sweep. The root has a separate concrete17-pair improvement and should not wait on this new global interface.

## Frozen inputs and bounded screens

Current screened PR470 word SHA256:
2b91cf95df15d9c32d830f15cfa3f2b74b89c439f40ebbe2f04c8235cfb1b49b.
Source: parent-pinned PR470@281a0fbded64209e51964bfe4bf19b1da37a6f5b.

The native C++ screens in this directory tested:
1. Source-assisted initial response kernels: for source i, test whether its unit response lies in the response span of helpers admitting a common initial line i.
2. Timed source assistance between point-copy deliveries, requiring a virgin pivot and compatible current/next-use frames.
3. Timed assistance at the source's actual larger frame, with current-frame and next-use containment checks.

All three found zero candidates on470. The first two also found zero on the previous rank151 word. These are finite restricted screens, not impossibility theorems. The third screen uses one Gaussian-elimination representative and does not exhaust alternative dependent representations. No expensive constructor or price was pursued after these gates failed. Sources and empty candidate receipts are preserved, total lane storage under1MiB.

The sufficient local identity behind the source-assisted screen is valid: if an uncancelled helper response B_j equals e_i plus a sum of other eligible helper responses, write the pivot into source i and those donors at a common frame and undo the non-target updates at FULL. The target's pivot column cancels, while inverse cleanup restores sources/helpers. Common-frame feasibility and the paid profile must still be checked on any actual witness. This sweep produced no such witness.

## Universal common-affine-offset cancellation theorem

Let V be any vector space over F2, let K>=1, and let X_1,Y_1,...,X_K,Y_K belong to V. Fix ANY b in V. Consider the following2K+1-stage controller. Every local forward shear adds X_p+b into Y_p; every local backward shear adds Y_p+b into X_p.

The stages are F_1,G_1,F_1,G_2,F_2,...,G_K,F_K. For each p>=2, after G_(p-1) apply X_(p-1)+=X_p and Y_p+=Y_(p-1); after F_(p-1) apply Y_p+=Y_(p-1) and X_(p-1)+=X_p. After the last stage, for p=K down to2, apply Y_(p-1)+=Y_p and X_p+=X_(p-1). Finally exchange X_p and Y_p in every pair.

THEOREM: the final output is exactly the same as for b=0, for every K, every initial data tuple and every b. In particular, whenever the clean controller is identity, the common-affine controller is identity too.

PROOF: subtract the clean execution from the affine execution. Because every bridge/shear is linear apart from the added constant, it suffices to follow the offset coefficients of b; all start zero. F_1 sets the Y_1 offset to1. G_1 makes the X_1 offset0, since it adds1+1. If K>=2, the first bridge copies the Y_1 offset1 into Y_2; its X bridge changes nothing. F_1 then resets Y_1 to0, and the following bridge leaves Y_2 at1. Inductively, just before G_p the only nonzero offset is Y_p=1. G_p sets X_p to0; the next pair's first bridge copies Y_p=1 to Y_(p+1), when that pair exists; F_p resets Y_p to0; the second bridge leaves only Y_(p+1)=1. At p=K, F_K resets the last offset. All offsets are now zero, so terminal bridges and swaps leave them zero. For K=1 this is the familiar three-shear cancellation. This proves the theorem for arbitrary vectors, not merely observed tests.

This theorem permits a common DIRTY offset b=C(h), with h arbitrary, including unknown or correlated data. It does not require a clean helper or a zero response C=0. The scalar compensation demand can therefore, at the abstract controller level, be weakened from individually zero dirty responses to a common coherent dirty response.

## Sufficient physical realization criterion (not instantiated here)

Let actual helper state evolve by H_(s+1)=R_s H_s after complete invocation s, including all Fourier residuals and owner routing. Let the actual data offset in invocation s be K_s H_s. A sufficient intertwining identity is

    K_(s+1) R_s = K_s

for every consecutive pair of calls, with explicitly compatible actual owner spaces. Then every invocation's data offset equals the same b=K_0 H_0, and the theorem applies. Any helper/data cross-block leakage, external bridge action on helpers, or independent fresh helper input must be included in R_s or separately proved absent. All transforms implementing K_s or its coordinates must be priced; a formal matrix representation is not a free algorithm.

Equivalently one may supply explicit cheap coordinate maps J_s with J_(s+1)R_s=J_s and K_s=CJ_s. Those maps must be executable under the existing interface with their actual costs. They cannot silently contain recursive Fourier calls.

The current hosted provider does NOT automatically satisfy this criterion: helper endpoints are nontrivial block-diagonal residual operators, and owners can change between idle families. Equality of raw scalar response columns is insufficient. In particular, scalar rows tensored with the identity generally do not intertwine a nontrivial Fourier block merely because the helper index is reused. This is the precise unresolved implementation step, and no reduction of compensation/entrance cost is claimed.

## Structural sources read

Problem18AnchorInvariantCoordinates20261001.lean, conjugated_gram_blocks, is an actual project instance of exposing an invariant block and its cross terms in adapted coordinates. TIGroupLevi20260902.lean, hypLift_isIsometry, supplies the primal/dual lift analogy for coherent source/response changes. These are discovery analogues only; neither asserts the present physical intertwining relation. Source-only retrieval is not fresh kernel verification.

Next bounded action: look for an ACTUAL response observable fixed or coherently transported by the whole residual/owner operator; compute its exact paid implementation. If none exists cheaply, abandon this route rather than assuming the transport condition. Preserve the frozen17-pair deliverable independently.

Additional exact diagnostic: the larger-frame timed screen has583 source-response memberships, but ZERO of those sites has an eligible virgin helper with nonzero response. Consequently the zero-candidate result there is not caused solely by choosing an unfavorable Gaussian-elimination representation. Helpers already used before the insertion cannot be given the proposed new entrance without an additional earlier-frame reconstruction. This diagnostic still concerns only the stated virgin-pivot protocol, not all source-assisted transformations.
