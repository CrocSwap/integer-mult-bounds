# Fixed-cut seam condition and exact exclusion

Use the original 4,783-event caller and the cut before event 1741, whose first post-cut event is `A ADD 10 0 2`. Keep all paid positions, their itinerary, and the Type A central factors. The tape splits into an early prefix containing body stages 1–8 and four Type A QUERYs and a suffix containing body stages 9–17 and zero Type A QUERYs. Each idle wrapper references only bodies from its side. Denote the two disjoint body-variable sets by b and c.

Write P(q,b) for the prefix and S(q,c) for the suffix on the full 36-role Type A space. The published arbitrary-input diagonal endpoint is

\[
 S(q,c) P(q,b) = q^{-1}D_l(c) D_e(b),
\]

where D_e and D_l encode the early and late masks. The bodies commute under the retained caller contract. Setting the opposite set of body variables to identity gives P(q,b)=G(q)D_e(b) and S(q,c)=q^{-1}D_l(c)G(q)^{-1}, with G(q)=P(q,1). For this necessary condition it suffices to specialize every body to the identity sector and retain all 36 arbitrary role coordinates.

For one swap X, the reassignment exchanges late masks and the final order of the two outputs. A seam W must satisfy

\[
 X S(q,c) W(q) P(q,b) = q^{-1} X D_l(c) X D_e(b).
\]

At unit bodies, every displayed factor other than W is invertible and the equation uniquely forces W(q)=G(q)XG(q)^{-1}. Substitution then gives the requested action for every early and late body setting on which the seam can be realized. A fixed phase-even seam would have W(+1)=W(−1). Both signs are available in the physical #7113 gate. Its C has Walsh eigenvectors (1,1) and (1,−1) with respective eigenvalues 1 and i. At width two, taking zero or two minus factors in the central copies supplies signs +1 and −1 while keeping all body factors in their identity eigenspaces. The signed direction is preserved by the retained routing and the body axes are disjoint from the central block. The necessary equality therefore applies on legal physical input sectors, with arbitrary amplitudes independently placed in all 36 roles.

There are two exact ways to test the equality. If d=e_a−e_b, X=I−dd^T gives W−I=−(Gd)(d^T G^{-1}), the forward test. With H=G(−1)^{-1}G(+1), multiplying the equality on the left by G(−1)^{-1} and on the right by G(+1) gives XH=HX, the reverse test. Each computation works over the rationals. The latter derives G by reverse covector action and uses exact elimination to obtain H, independent of the forward inverse-event action.

For each unordered pair the two old and new productive ranks have the same sum. A root with e early and l late active bodies contributes rank 1+8(e+l). At fixed rank sum, strict concavity of r^(1−κ) for 0<κ<1 makes the combined productive weight increase exactly when the difference between the ranks decreases. The 570 other pairs cannot give a strict improvement at unchanged paid stock even if the inserted seam were free. Both exact tests reject the other 60 at q=±1. This settles the full fixed-cut profitable single-swap scope without building a new caller or deriving a new complete exponent.

The single-pair replay imposes a fixed action on the two signed sectors and retains the old itinerary and final ordinary output swap.

## Bound for all late-mask permutations at the same cut

Let Π be any permutation matrix. The output reorder is Π^-1 and the desired late diagonal is Π^-1 D_l Π. The unit-body equation now uniquely forces W(q)=G(q)ΠG(q)^-1. Consequently every phase-even feasible Π commutes with H=G(−1)^-1G(+1). Such a permutation preserves every directed matrix entry under simultaneous row and column permutation. It also preserves the diagonal entries.

Start with one class of 36 roots. Refine each class by the signature comprising its diagonal entry and, for every current class, the multiset of pairs (H_ij,H_ji) incident to that class. A permutation commuting with H preserves each class at every iteration by induction. Exact refinement gives invariant classes of sizes 2, 16, 10 and 8. Every commuting permutation therefore belongs to the relaxation allowing arbitrary permutations within those classes.

Within each class, opposite-sort the early and late body counts. For any early counts e≤e′ and late counts l≤l′, the pair (e+l′,e′+l) has the same sum and weakly smaller spread than (e+l,e′+l′). Each such exchange weakly increases the concave productive moment. Repeated exchanges prove opposite sorting maximizes the relaxed within-class objective for every 0<κ<1. The exact opposite-sorted productive rank histogram equals the old one. Therefore the gross gain is at most zero even before charging the seam or output reorder. The exact upper bound settles the whole class without enumerating any permutations.

The replay also checks that one body count is constant in each invariant class. This proves every class-preserving permutation keeps the exact rank histogram. Other cuts, phase-sensitive seams and changed paid itineraries remain open.
