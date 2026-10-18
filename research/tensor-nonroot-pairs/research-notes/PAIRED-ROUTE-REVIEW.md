# Independent review: rational paired whole-owner route

Reviewer lane: complex_control. This is a construction/interface review, not a global runtime or kappa certificate.

## The local sufficient theorem

Let E be the actual source entrance line in Q^8, let P=I-projector_E, and let B_0=P directsum0, B_1=0 directsumP in Q^16. The provided rational orthogonal matrix G satisfies U_j=G B_j G^T, U_0 U_1=0, and U_0+U_1=diag(I14,0_2). Let J interchange the two eight-coordinate blocks. Then sigma_0=G and sigma_1=G J map the SAME source local residual P to U_0 and U_1 respectively. They are distinct complete matrices: their images of the source eight-coordinate space are distinct orthogonal eight-dimensional subspaces. No logical residual is divided between physical owner families.

After embedding these maps into the actual physical family basis, every logical helper owner is (family, d sigma_j^-1). For fixed cover d, equality of two such pairs forces equality of family and sigma by right cancellation. Thus explicitly distinct sigma values give distinct stored array rows within one complete invocation. This is the exact mechanism needed to avoid invalid aliased scalar updates; disjoint coordinate support of the U_j is not necessary.

The source complete local identity is valid for arbitrary values of every source, target, and helper array. It therefore applies to these distinct rows. The whole invocation returns each helper row with only its stated residual endpoint, including identity action on all its spectators. Only after this complete call may another invocation reuse a row. As the cover is swept, d -> d sigma_j^-1 is a bijection. Each residual endpoint therefore lands once at every intended cover row. Orthogonal U_j commute, and (I-2U_0)(I-2U_1)=I-2(U_0+U_1). The remaining pending projector must be included and mutually orthogonal as well. This gives the original pending-child endpoint.

This argument covers temporary overlap of coordinate supports and spectator coordinates precisely because distinct cover owners are used during the full invocation and the intermediate scratch state is never used as another call's premise. It does NOT validate interleaving two invocations before their dirty restoration, duplicate actual owners inside a call, or a local theorem checked only on clean helper inputs.

## Actual gap found and sent to the hosting author

At review time, paired_owner_witness.py defines sigma as placement(output_coordinates)*(G directsum I)*swap(first8,copyj8). But its output_coordinates are offsets in the pending child, starting at0; the actual pending axes depend on window source_level/target_level and the port's rational orthogonal complement. The definition is missing the actual window-adapted ambient basis matrix B_(window,family). The correct physical matrix is

    sigma_j = B_(window,family) placement (G directsum I) J_j.

B must have the actual pending child axes as its first r columns, followed by a fixed orthogonal completion. PR490 wrapper/cover_owner_injection.py already constructs the full port bases and computes the child's actual axes. Reuse those concrete ingredients, not a claim that the first r standard coordinates equal the pending child. The hosting author and parent were notified before a physical admission claim.

## Required checks on the explicit candidate

- Bind every source frame to its actual rational entrance projector; matching a rank or width is insufficient.
- Instantiate both entire 78-by-78 maps, or an unambiguous exact factorization including B, placement, G and J; bind their inverses.
- Check actual owner distinction per complete invocation, including old coordinate routes versus new paired routes; family inequality alone is too strong, projector inequality alone is not the full check.
- Check each family lies in the correct idle window and outside that call's active data families.
- Check the paired and unpaired residual projectors plus the charged remainder sum to the exact physical pending child. Keep both paired source roles; do not price just one of the two seven-dimensional residuals.
- Charge the new literal address-map operations, duplicated address halves, new source-word scalar instructions, and all wrapper passes. A finite q-dependent GL-routing constant must be exposed as such if absorbed by a symbolic cutoff.
- Use the explicit PR490 GL-cover all-size contract and updated row allowance28416 unless an O-cover bad-class proof covering the new non-coordinate residual form is separately supplied. Rational orthogonality of the chosen route is not by itself that counting theorem.

The finite source-word NONROOT-JOINT-AUDIT.json records all955 arbitrary-dirty binary columns and integer operand spans, with local delta {rank1:+84,rank2:-53} for22 new entries on its frozen base. It is useful source evidence but does not replace the physical ownership or full invoice checks above. The updated rank139 source has to be bound to its own audit and hashes.

No achieved global kappa is asserted by this review.


## Final frozen-candidate disposition

The hosting author fixed the ambient-basis gap and the source/window binding checks. The final physical owner audit binds the emitted template's allocation, every role descriptor, actual pending axes, exact entrance basis and both coordinate/rational owner maps. It reports62,920 distinct-per-call whole owners across88 calls.

This lane independently replayed the frozen global-new139-v3 program using independent_paired_invoice.py. PASS:1,733,496 emitted rows including23,040 explicit scalar bridge rows;1,340,856 local additions;792 copy/clear episodes; prefix bound1684bits charged1728; source word c50c9b21f11a8dc0c93c669bbf46e91aa40ac19ddb948397d7e276c3b91a535b; template8c83bb1257df57694e46b056aacc27c1d3ffbf61c4d45a2867de2e16721c25c1. The independent audit also binds the entire frame geometry and all ordinary coordinate residual isometries to the new word; redundant non-coordinate lines in an otherwise coordinate subspace are handled by their geometric span, not rejected by labels.

The complete exact paid profile is {1:222672,2:87431,3:22648,4:27124,5:9944,6:6848,7:4280,8:792,50:1,56:793}. Rank mass745536,live9600,m78,deficit3264. The GL row coefficient is28416. The actual pair G needs at most33 elementary operations per direction; copy-block interchange adds at most8. All selected elementary factors are in {+/-1,+/-2,+/-1/2}; numerator/denominator height is at most2bits. The parent's conservative assembly allowances RES_ISO512 and ROUTE_EXTRA5 dominate these local factors with separately billed placements and port geometry. Hosting's more comprehensive route-factor receipt should accompany the independent local calculation.

INDEPENDENT-PAIRED-INVOICE.json contains the assembly audit keys and exact hashes. Global kappa and all strict outer inequalities belong to the parent's separate final assembly; this review does not assert their result. The retained fixed-GL-routing/all-size compiler contract remains explicit.
