# Concentrating cold-start residues into one paid child of rank 32

Status: actual literal T372 owner allocation, separate directed finite-moment checks and complete fresh native/global/physical/outer release passed. The binding receipts are in `evidence/`; this improves the pinned PR #2848 target and remains below the newer PR #2853 claim. All inherited compiler, source-access, hosting, precision/tape, recovery, ordinary-recursion, BIT and analytic-transfer assumptions remain.

## Construction from immutable sources

Use three disjoint copies of the exact PR2843 T124 allocation, with the unchanged PR2833 dirt-entry words. Interleave corresponding calls: source time t in copy g becomes 3t+g, for g=0,1,2, and add 124g to replica/owner indices. Each replica retains its complete source-stage and event progression. Every inherited helper is still executed once, with its unchanged width and native provider.

In the first copy, the ordinary owner bin (replica,child,port)=(0,4,0) has capacity 32 and contains three roles of width 9 at successive offsets 0, 9 and 18, leaving remainder 5. Each copy also has a capacity 16 exceptional bin (124g,0,0) containing only helper 224 of width 7, leaving remainder 9. Make precisely these edits in the three-copy lifted fill:

| Before: time,helper,owner,child,port,offset | After |
|---|---|
|0,190,0,4,0,0|0,190,124,0,0,7|
|3,63,0,4,0,9|3,63,0,0,0,7|
|6,0,0,4,0,18|6,0,248,0,0,7|

Thus the donor bin is empty, leaving rank 32. Each exceptional bin now holds its original mask of width 7 [0,7) and one mask of width 9 [7,16), leaving no child. The source-event windows and physical-family inequalities are checked on the complete literal fill, not inferred from its cardinalities. In particular the transfers occur in distinct calls from the pre-existing role of width 7 in each receiving family; one transfer crosses copies, one stays within the first copy, and one crosses into the third. Native words and dispatch are unchanged.

## Universal sufficient cost argument

Write H_r for the cost of a paid rank-r child. Relative to three untouched T124 copies, the entire profile changes by H_32−H_5−3H_9. Rank mass is unchanged because 32=5+3×9. There is no unpriced helper, tail or additional call in this identity.

For H_r=r^p with 0<p<1, the two-copy rank 23 construction has per-copy change (H_23−H_5−2H_9)/2; the three-copy construction has (H_32−H_5−3H_9)/3. The latter minus the former is [2H_32+H_5−3H_23]/6. Since 23=(2×32+5)/3, strict concavity gives 3H_23>2H_32+H_5. Hence the actual three-copy allocation improves the normalized full paid moment over that two-copy construction at every positive saving parameter in range, independently of decimal computation. This is the concave secant/decreasing-marginal principle of atlas C001 and D021–D023 applied to a physically checked allocation.

For the C001 connection explicitly, the cost screen g(S)=(5+9|S|)^p−5^p is submodular on a set of candidate equal-width moves: its marginal is (x+9)^p−x^p with x=5+9|S|, and this decreases with x because p x^(p−1) decreases. Subtracting the modular term |S|H_9 preserves submodularity. This is a statement about the actual residual-cost score; feasibility is still supplied by the source-event and owner checks, not by submodularity.

Compared with PR2848's two-copy rank 2 / rank 16 construction, two untouched T124 copies change by H_2+H_16−2H_9. After normalization per T124 copy, our cost difference is [2H_32−2H_5−3H_2−3H_16]/6. This is universally negative as well: strict subadditivity gives H_32<2H_16 and H_32<H_16+2H_5+3H_2, using 32=16+5+5+2+2+2. Add the two inequalities. Strict subadditivity itself follows because (a/(a+b))^p+(b/(a+b))^p>1 for positive a,b and 0<p<1. Thus the complete normalized cost improves for every allowed exponent, while the directed moment comparison below supplies its certified numerical size.

## Finite evidence

The owned producer/checker recounts all 1,365,984 literal roles, 3,348 calls and 372 replica source projections. It verifies strict expanded source-event windows, complete helper coverage, one physical family per call, integer ranges, finite capacity, disjoint masks, contiguous used prefixes, the full paid profile and rank mass 24,212,736. Five invalid-owner cases are rejected. The final profile is:

    {1:8061984,2:2176200,3:923379,4:428544,
     5:135035,8:26784,32:1,48:133845}.

Its live stock is 333,312 and charged physical stock 333,802. The exact directed rational moment root lies strictly between 0.001718659357407250209979 and 0.001718659357407250209980. The admitted conditional outer target is the lower endpoint minus 10^-46 and 10^-70. Its exact difference from the full pinned PR2848 target is 21227558005129/25000000000000000000000, about 8.4910232020516e-10. This comparison uses the full rational PR2848 claim, not a truncated title. Six invalid moment cases are rejected. The arithmetic receipt reuses the authenticated PR2848 interval implementation, so root's separately implemented arithmetic check is required for independent verification.

Stable candidate: `T372-concentrate32/`. Its FILL SHA-256 is b6339f5bd30d334d4a6b74276951cf9e87a68aef7b0878ab38b0d2a9102f91c9; profile SHA-256 is 868cfdbcb73413f43b2d834d296f5cca261ed863a5ac54a69d08527f24a13ce7. Exact source and output bindings are in the receipts. The T248 rank 23 intermediate is preserved separately and is not represented as an already admitted release.

## Attribution and scope

Jeremy Kothe's PR2833 supplies the dirt-entry native rewrite and its retained words; Marius-Paul Dumitrean's PR2843 supplies the actual T124 allocation; Yiyang (@Lyy-iiis), with substantial OpenAI Codex assistance, supplied PR2848's two-copy interleaving/residue-exchange construction and independent audits. Dugongue's PR2839 supplies the tensor-block replica contract. Tekalign, DavidAriasC, Philippe Van Velzen, Mason Hale and all retained provider, owner, native/admission/outer contributors keep their upstream credit and licenses. New here is the literal three-role transfer through the ordinary capacity 32 donor, its paid comparison, and the complete checks described above. No broad mathematical novelty or independent human review is claimed.

The broader search retained its failed checkpoints. An old-word T124 CP-SAT attempt stopped within 120 seconds after 65 Hall cuts without a witness, and its projected tiny gain was superseded by actual new upstream words. A proposed higher-way direct merge of only exceptional capacity 16 bins is infeasible for k>2; the successful construction uses a different larger donor. Rank 3 residual donors first occur far after the strict cold-start windows, so their tempting local concavity saving was rejected by actual chronology rather than reported as feasible.
