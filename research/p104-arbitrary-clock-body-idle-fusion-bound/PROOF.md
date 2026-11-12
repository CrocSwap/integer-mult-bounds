# One legal joint body sign excludes each disjoint-mask fusion

Fix the exact #7113 Type A caller at the #7334 comparator. It has 96 ports, 36 roles per port and 30 body-only IDLE_ONE calls. The 14 early masks are nonempty subsets of stages 2 through 8 containing stage 8. The 16 late masks are nonempty subsets of stages 9 through 16 containing stage 9. Two masks from the same side intersect. Every cross-side pair is disjoint, giving exactly 224 cases. The only change considered is deleting both idles and inserting one Type A field multiplication by the whole body product for their union, at any clock. The other actions are fixed.

## One physical specialization

Set q=1, D8=D9=−1, and every other body variable to 1. Each body acts on a disjoint eight-axis block. The binary Gaussian C has eigenvalues 1 and i on the plus and minus Walsh vectors. Choose two minus Walsh bits in each of the stage-8 and stage-9 blocks and plus bits elsewhere. This realizes the same specialization at every positive integral admitted width. Arbitrary role inputs can be supported in this common sector.

Each original idle in the proposed pair acts by −1 on its own role at this profile. A fused union body acts by +1, hence is the identity on its target field. Any placement of that identity gives the same specialized product as deleting both old idles. The result also permits a reversible change of basis around the fused factor with no change to the fixed surrounding action, since conjugation preserves the identity.

## Exact projector comparison

Let G_i denote the old invertible caller prefix before idle i, and E_i the rank-one projector onto that idle's live role at its own clock. The pulled-back projector is P_i=G_i⁻¹E_i G_i. Its reflection R_i=I−2P_i is an involution. Removing a single original idle from the literal word removes its own local reflection. For two removed idles, the new whole product equals the old product multiplied on the input side by the two pulled-back reflections in reverse chronological order. This follows by telescoping the original prefixes, which include all old idles. The product is unchanged exactly when R_j R_i=I, or equivalently P_j=P_i.

The lead maintains exact prefix rows and inverse columns as it reads the tape. The independent replay instead walks forward and reverse sparse basis vectors on its own literal lowering. Both check the old diagonal endpoint and find an unequal matrix entry for every one of the 224 pairs. For the largest priced pair, clocks 1448 and 1763, the stage-mask lengths are 7 and 8, and the first differing projector entry is [1,0], with values −2 and 0. A separate omission replay on all 36 input columns changes the complete output matrix entry [1,0] from 0 to −4. No case survives the specialization.

## Directed price

Write H(r)=r^(1−κ). A hypothetical fusion of body masks with m and n stages pays H(8m+8n) in place of H(8m)+H(8n) at each of 96 ports. The difference is positive by strict concavity. Its gross increases in either rank and has positive mixed partial −H″(8m+8n) in the two ranks up to the positive scale of the stage units. Consequently an optimum disjoint matching pairs the 14 early ranks with the 14 largest late ranks, sorted in the same order. The exchange inequality follows by integrating that positive mixed partial over each rectangle of crossed pairs. All other paid and productive entries are fixed for this quote. Directed exact power bounds over the old crossing certify the combined gross below 238.182 raw. The actual saving in this model is absent because no proposed pair preserves the caller.

The proof makes no claim about changed multi-field operators, changed erased maps, a changed signed interface, or a cancellation of several wrong single-pair edits. No physical rewrite, dirty-restoration proof, or changed recurrence was attempted.
