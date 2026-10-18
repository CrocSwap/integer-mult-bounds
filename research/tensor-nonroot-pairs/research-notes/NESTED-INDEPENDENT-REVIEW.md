# Independent nested-entrance review

Candidate SHA256 f6e176a24f5d53ea372da60dabc55556ab4b6808d4b7081322a39fa4f840eb72.

Conclusion: the nested flag has a sufficient extension of the existing entrance-kernel proof and fits the actual common-frame physical emitter. It does not fit the older kernel-construction function without replacing that function's equal-entrance guard. No unchanged-public verification was repeated.

## What changes

Relative to warm+packet, only A and start differ. Pivot906 changes entrance9={line7} to293={line6,line7}; these lines are2e6,2e7. Its corrections into donors711 and904 occur at293. Donor711 first receives the lower-entrance corrections from749,781,796,823 at9, then906at293. The906correction into904 occurs directly at293. All later visits contain the current frame.

The actual candidate has110pivots and102donors, globally disjoint. Its kernel prefix has103 grouped rows; the source prefix had102. The review recomputed all110 response equations from the actual centre/scatter and B plus the nonkernel A suffix. All equations hold. In particular response906=0x9900000002, response711=0xff00000000 and response904=0x6600000002, so their required XOR identity is exact.

## Sufficient nested-prefix lemma

For each register r let its logical unframed value be h_r, so its physical value at current frame F is T_F h_r. A pivot initially at E merely defines h_p=T_E^-1 times its arbitrary physical initial value; no extra transform is executed or assumed free. A common-frame ADD at F changes donor logical value by h_d<-h_d+h_p. Frame climbs carry T_F h_r to T_G h_r and preserve this logical meaning.

Consequently a sequence of donor corrections can be placed at DIFFERENT nested frames: every correction induces exactly its scalar shear on logical values. Pivot/donor disjointness means these shears commute as logical maps. The chronological frame inclusions checked in the candidate establish legal physical execution of that chosen order. No dirty register is assumed zero; only the source-dependent clean-support component of the entrance correction is zero.

For each pivot the response relation says its direct target contribution equals the XOR of its donor contributions. Hence its omitted zero-frame compensation is canceled by these corrections, independent of its entrance dimension. Full-frame inverse corrections restore the helpers' logical values. The full endpoint on that helper is therefore T_FULL*T_E^-1, with no affine leakage. In the bit supplier, commuting orthogonal projector transforms identify this with the complement transform D_(I-P_E).

For E293 the exact coordinate permutation with row order[6,7,0,1,2,3,4,5] is orthogonal. It sends P_E to diag(1,1,0,0,0,0,0,0), and the residual to identity on the first2 coordinates plus the ordinary rank6 bit transform on the remaining6. The review checked these projector equations over exact rational numbers. A rows-numerator2/denominator2 encoding is exactly this permutation.

## Legacy guard versus actual admission

hosted_kernel.py line26 asserts donor_at.setdefault(d,E)==E. The nested construction violates that old sufficient construction restriction. Packaging must explicitly use the new constructor and lemma above, not assert the old function accepts it.

The actual emitter reads the initial frame of every register, verifies each common-frame ADD and monotone frame edge, derives residual widths as8-dim(start), and validates one residual isometry per initial helper frame. local_audit.py separately checks rational projector nesting and complements. Neither imposes donor-equal-entrance as a semantic condition. Thus the guard is not a hidden hypothesis of those interfaces.

Scope: this is an independent mathematical/interface review plus exact finite relation/projector checks. Root must bind the fresh native records, source hashes, residual isometry table, complete whole-owner packing and final analytic invoice. The review is not a new unconditional multiplication theorem or fresh Lean certification.
