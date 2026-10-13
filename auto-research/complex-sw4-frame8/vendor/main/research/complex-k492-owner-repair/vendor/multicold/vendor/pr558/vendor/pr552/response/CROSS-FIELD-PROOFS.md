# Two cross-field sufficient constructions

## Temporal observable-state merger

Consider a cut in a finite linear circuit. Let r and s be two background registers that, after the cut, are neither written nor read by background operations. They may be read by target operations, and the target subsystem may have arbitrary subsequent invertible linear operations. Let O_r and O_s be their exact final target-response columns, computed by the backward adjoint of the entire remaining circuit. Suppose O_r = a O_s.

Insert s += a r at the cut, and remove every subsequent target read of r. Since neither background state changes again, the original suffix's contribution is O_r r + O_s s. The changed suffix's contribution is O_s(s+a r), which is identical. The other states' contributions are unchanged by linearity. This argument incorporates target-to-target gates through the adjoint; simply summing coefficients by target would be insufficient.

The added shear is invertible. Retain the stored register r, regenerate inverse background cleanup, and both arbitrary initial dirty values are restored. There is no erasure of an unobserved state. A sufficient native realization requires a common gate frame F containing both current frames and lying in the next frame of s; r needs no later delivery frame after its reads are removed. All remaining target chains and final frames must still be legal. Every extra shear, altered child rank and remainder is charged. Thus an explicit successful frame/column replay plus a lower complete moment suffices for an improved supplier.

This is a causal one-dimensional specialization of state realization using future observations. A general rank factorization O=L R does not by itself prove an implementation: the state transform, extra coordinates, intermediate availability and physical frame schedule still require an explicit invertible circuit. We use the sufficient pair construction above, not a dimension-only claim. On the current witness 308 stable-cut positions yielded no proportional eligible pair; this restricted gate found no improvement.

Source connections: Lall's Realization Theory notes explain reachability/observability and the Hankel operator. Mathlib's LinearRecurrence.toInit gives the explicit equivalence between a trajectory and its initial state, and proves trajectory uniqueness. Neither source supplies the native frame realization automatically.

## Weighted coset decoding of a family of reads

Keep the protected initial coordinates P (data and warm helper dirt) fixed. Cold helper dirt D is the only allowed quotient. At a read gate t += q s, choose another available register r and a coefficient a such that the exact current prefix rows satisfy row(s)|P = a row(r)|P. Replacing the gate by t += q a r changes the current state by a vector supported only on D. Consequently the final protected response is unchanged. Regenerated frame-zero compensation cancels the changed cold response, while literal inverse background cleanup restores all arbitrary background dirt.

The new ingredient is a global cost and its exact update, rather than an isolated quotient identity. Let P_i be the actual prefix matrix before the gate and R_i the actual suffix matrix after it. The elementary-gate difference is e_t v^T, with v^T = q(a e_r^T-e_s^T). Therefore the complete matrix changes by

Delta M = (R_i e_t) (v^T P_i).

After applying the fixed target normalization L, the compensation table changes by the outer product

Delta C = (L R_i e_t) (v^T P_i)|D.

This identity is exact. It permits scoring a candidate by the weighted Hamming cost sum w[j,k] * 1(C[j,k] != 0), using only entries affected by that outer product. If its actual frame profile is preserved, a strict reduction in this cost reduces scalar compensation work. For an accepted family, recompute the prefix, suffix and table after each step; never add gains measured against incompatible original words. Induction proves that every accepted word preserves the protected response and admits the same sufficient compensation/cleanup construction.

This is weighted coset representative selection: all admissible read representatives have the same protected syndrome, while their cold response is optimized against the existing table. Rational coefficients and dyadic compiler restrictions replace the usual finite-field alphabet. The method does not solve general minimum-weight decoding or claim global optimality. The search is a bounded exact greedy family decoder. Every selected representative is proved over the rationals; modular nominations are not certificates.

Mathlib's hammingNorm is exactly the count of nonzero coordinates. Coding theory's coset-leader viewpoint supplies the optimization analogy. The new constructive outer-product update, explicit frame gate, and recomputation between accepted rewrites are proved here.

## Discovery scope

The fixed-frame and frame-interval source-family screens found no paid-rank improvement among 130 single alternatives, 50 lift-family trials and 10 interval-family trials. Two complete response-component retirement modes, across14 components, were sent for joint inventory pricing and were not selected by the complete capacity model. These are bounded negative searches, not universal barriers.

The weighted family decoder's actual saving and complete local replay are recorded separately in weighted-coset/SCREEN.json and weighted-coset-local/. No scalar-operation saving is called a paid-rank improvement. The parent's independently proved collective frame contraction supplies the numerical rank-profile gain.

## Certified concrete family

The frozen twelve-step family reduces the compensation table from 9,756 to 9,132 nonzero entries, saving 624 scalar additions per local invocation. The full scalar program shrinks from 16,890 to 16,266 operations; each oriented emitted program shrinks from 22,107 to 21,483 events. The paid profile remains {1:2300,2:440,3:472,4:184,5:56,6:56,8:8}, with unchanged 504 helpers and all owner widths. Fresh native replay verifies every 728 formal column in both orientations, 2,929 phase edges, 23 residual adapters and 11 mutation controls. This is a scalar-work reduction composed with the separately proved collective-frame numerical gain.
