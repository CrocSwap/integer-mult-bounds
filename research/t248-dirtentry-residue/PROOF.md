# Two-copy cold-start residue coalescing

This is a finite construction on the exact PR2833 dirt-entry words and PR2843 T124 allocation. It changes
whole-helper ownership, not either local scalar word. PR2833 is pinned at
`e9307b48d7d1b690939935ecef0f8e524e6d92f4` and PR2839 at
`2fdd289fcd0896f4691f9dd78a8bf1511573e434`. PR2843 is pinned at `47a7227c044cd0cabb1432a06c61dd5d60c07f5a` (Marius-Paul Dumitrean). Their retained notices and contributors
remain authoritative. The PR2839 checker lineage includes Mason Hale, Tekalign,
Jeremy Kothe, Philippe Van Velzen and Marius-Paul Dumitrean.

Take two disjoint copies of PR2843's 124-replica construction. Interleave their
corresponding calls: old time t becomes 2t in copy 0 and 2t+1 in copy 1. Shift
every replica and owner index of the second copy by 124. Each original call's
source progression, pending window, helper width, mask, and physical-family
inequalities are preserved under this order embedding. Every local call and
its children remain paid.

Each copy has exactly one exceptional capacity-16 bin, initially containing
only the width-seven role of helper index 224 (the fill's provider-width
array index) at the first call. The two bin keys are
(owner replica, child, port) = (0,0,0) and (124,0,0). Their exact allowed time
intervals after interleaving are (-1,18] and (-1,19], respectively. Move the
first role from the first bin into the second at offset zero. Move the second
role's offset from zero to seven. Thus both roles fit inside capacity 16 and
have disjoint masks [0,7) and [7,14). They occur at distinct calls, times zero
and one. The first call formerly used only first-copy owner families, so its
new second-copy family does not collide with any existing role. All other
roles are unchanged. The first bin is now empty; the second leaves rank two.

The local words operate correctly for arbitrary dirty helper inputs and return
their specified residual transformations with cleared private work. This is
an inherited source obligation, independently replayed here as a formal free
operator identity in both orientations. The disjoint residual masks and exact
pending windows are the whole-helper hosting premises. Full native/hosting,
precision, physical-stock and outer admission remain separate checks; this
argument alone does not discharge the inherited all-size compiler contracts.

The old two bins left two rank-nine children. The new bins leave one rank-16
child and one rank-two child. Therefore the entire paid profile changes by

    H_2 + H_16 - 2 H_9.

For H_r proportional to r^p with 0 < p < 1, strict concavity at the midpoint
9 = (2+16)/2 gives H_2 + H_16 < 2 H_9. The rank mass is unchanged because
2+16 = 2*9. Live families double from 111104 to 222208, and all other paid
profile entries double exactly. Consequently the normalized moment decreases
strictly at every admissible positive exponent saving. This is a changed
finite owner allocation, not an endpoint-digit refinement.

The literal 910656-role check establishes the proposed T248 allocation. Directed
rational arithmetic brackets its complex root strictly between
0.001718658508304930004819 and 0.001718658508304930004820. The completely admitted outer
target subtracts 10^-46 and 10^-70 from the lower endpoint. It exceeds PR2843's
exact headline by approximately 2.3046321011e-10. The clean source-bound native, global, precision/stock, bootstrap and outer
release passed. Its exact release and source-inventory bindings are retained
in CLAIM.json and evidence/full; the inherited all-size conditions remain.

## Open next questions

1. Independently reproduce the completed T248 release and its source-bound
   PR2839 block-norm premises on the unchanged PR2833 words.
2. Determine whether a different initial allocation can avoid the remaining
   rank-two/rank-16 residue without introducing a larger paid cost elsewhere.
3. The inherited all-size/compiler, source-access, whole-call hosting,
   precision/tape, exact recovery, ordinary recursion, BIT and analytic-transfer
   assumptions remain explicit.
