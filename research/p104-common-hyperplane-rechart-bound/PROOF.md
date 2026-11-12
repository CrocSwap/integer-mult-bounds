# Common-hyperplane rechart bound

Fix the exact #7334 native word and #7113 signed caller. A component joins role segments that share an ADD or COPY chart. A component is eligible if every role is a public helper, including productive initial and final segments. Main, owned and mixed components stay fixed. Keep scalar sequence and coefficients. Paid edges are the original MOVEs. A helper's productive edge joins its initial and final charts. Require nesting on every edge and positive productive ranks. Grant zero paid rank gaps at zero cost.

For one nonzero normal v in F₂⁹, select any eligible components whose chart W is not already contained in ker(v). Replace each selected W by W∩ker(v). These demotions lower rank by one. The normal is shared among selected charts, while selection is arbitrary.

## Dual reduction

Use the ordinary nondegenerate F₂ dot product. Orthogonal complement reverses containment and takes dimension d to 9−d. The annihilator identity is

```
(W ∩ ker(v))^perp = W^perp + span(v).
```

The right side annihilates W∩ker(v) and has the required dimension by rank-nullity. Thus each permitted primal demotion is an eligible one-vector growth in the dual. An original edge L⊂U becomes U^perp⊂L^perp and keeps the same gap dim(U)−dim(L). The new gap, its paid or productive classification, and productive positivity also agree exactly. No edit to the physical word is inferred from this relaxation.

For a nested dual edge of old gap d, use x,y for growing the lower and upper charts. If v lies in the upper, only x can act and saves c_d on a paid edge or loses c_d on a productive edge. For a productive edge at d=1, forbid x=1. If v lies outside the upper, require x≤y, so y−x charges a paid growth or earns a productive growth at c_(d+1). Here c_r is h(r)−h(r−1), h(r)=r^(1−κ) and h(0)=0. Keep one shared increment vector on all edges. The unchanged signed caller multiplies the native price by 17, preserving its sign.

The lead reconstructs the forward components, computes complements of the given chart bases and solves maximum closure. The independent walk recovers components backward with DFS, rebuilds bases from their primal subspace spans, and independently checks strict reversed nesting and exact gap preservation for all 2,573 incident paid and 193 incident productive edges. It solves direct edge-capacity cuts by shortest augmenting paths with the same exact terminal cancellation proved in #7456. A variable's source and sink arcs have a common minimum which can be subtracted from both and from the offered total. Every cut crosses exactly one, so the optimum saving is unchanged.

## Exact shared envelope

Let a_r,b_r be outward bounds on the nine increments across the exact old crossing bracket at scale S=10^52. At scale 2S the box lies inside the L1 ball centered at m_r=a_r+b_r with radius R=Σ_r(b_r−a_r). Its 18 vertices are m±R e_r. For each fixed normal and feasible selection, price is linear in the shared increments. A nonpositive optimum on every vertex gives an upper on the whole bracket. Both engines give exact maximum zero for all 511 normals × 18 vertices. The empty selection attains zero.

This does not decide selections using distinct normals, mixed growth and demotion, a different scalar or ownership contract, or changed chronology. No new recurrence or operator is claimed.
