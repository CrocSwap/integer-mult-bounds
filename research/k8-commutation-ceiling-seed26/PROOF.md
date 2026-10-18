# Why the bound is valid

The argument below is written by hand. Every computational step it relies on is checked by `verify.py`.

## Class and cost

**The class.** It is the set of words W′ = A′·B′·T′ obtained as follows:
- each segment of the selected k8 word (A, B and the 116-gate tail T) is replaced by a linear extension of its dependency order;
- in that order, an earlier gate g precedes a later gate h on a shared register whenever g and h do not commute as elementary row operations;
- coefficients are unchanged, and intermediate words need not be legal.

**Commutation.** For row operations, ADD t ← t + c·s and ADD t′ ← t′ + c′·s′ commute exactly when t ≠ s′ and t′ ≠ s. Two SCALEs commute. Any other pair commutes exactly when it shares no register; no SCALE in this word has factor 1. `verify.py` checks this rule against exact rational composition, in both orders, on all 109,388 same-register pairs.

**Frames.** For each member, PR1671's contract applies:
- one frame per gate, shared by its operands;
- nesting along every register in the member's order;
- fixed starts and ends;
- pins at the A/B boundary entered by charged climbs;
- the 101 cone caps;
- eight fixed rank-8 centre descents.

The local cost is the sum of c(Δdim) over consecutive distinct frames on each register. The idle term is constant, because rank mass telescopes per register, so the bill is as in PR1671.

## Intervals

The DAG has nodes S_q, G_i, P_q, X_q and E_q. Its edges:
- join gates that are dependent in every member (the non-commuting same-segment pairs and all cross-segment same-register pairs);
- join starts, pins, the end-of-B cap node X_q and ends to the gates on their register.

Every edge joins two nodes on one register whose relative order is the same in every member. Frames nest along each register, so l(x) ⊆ F(x) ⊆ h(x) for every member and every legal assignment, where:
- lo2 is the join of the fixed frames over ancestors;
- hi2 is the meet of the fixed frames and the caps over descendants.

Two implementations agree on all 5,413 gates: propagation, and a closed form over ancestor and descendant closures. In chronological mode both reduce to PR1671's intervals.

## Stage 1: the order-free stabbing bound

For register q, take items x (its gates, plus its pin) with intervals [l_x, h_x]. Let D_q be the cheapest chain S_q = V_0 ⊊ V_1 ⊊ … ⊊ V_m = E_q, with each V_j a subspace inside some item's interval. The chain may use no arc on which an item is first entered (l_x ⊄ V_{j−1}, l_x ⊆ V_j) outside its upper end (V_j ⊄ h_x).

**It is a lower bound.** Take any member and any legal assignment. The distinct frames on q, in the member's order, form such a chain:
- every frame lies in its item's interval;
- at an item's first entry, the current frame is ⊆ F_x ⊆ h_x.

The chain's cost is exactly q's paid climbs. The bound uses the lower enclosures of `child_cost`. These lie on the 2⁻²⁵⁶ grid (`ceiling.py`), so the arithmetic is exact integer arithmetic.

**Adding precedence does not help.** Constraining the per-register DP by precedence cannot raise this bound. lo2 and hi2 are monotone along every DAG edge, so the first-entry points of any stabbing chain already respect every precedence.

## Stage 2: dimension-linear Lagrangian coupling

**Setup.** Each free ADD gate g appears on two registers, t and s. Give its t-copy the multiplier +λ_g and its s-copy −λ_g, priced linearly in the dimension of the frame:
- a copy with κ > 0 is charged κ·dim at its entry point;
- a copy with κ < 0 is charged κ·dim at its exit point (the last chain point inside h_x).

Define L(λ) = Σ_q D_q(λ).

**Validity.** Take any member and assignment.
- The operands agree, so Σ_g (λ_g − λ_g)·dim F_g = 0.
- On q's true chain, the entry point of x has the minimum dimension of any chain point inside x's interval, and the exit point has the maximum.
- For κ > 0, charging at entry gives at most κ·dim F_x. For κ < 0, charging at exit gives at most κ·dim F_x.
- So D_q(λ) ≤ chain_q + Σ_x κ_x·dim F_x on every register.
- Summing over q gives L(λ) ≤ the true local cost, for every λ.

The bound ignores precedence and acyclicity across registers, which only weakens it.

**Why the charging rule matters.** Charging negative multipliers at the entry point would be invalid. The toy check in `toy.py` catches that mutation.

**Exactness.** The multipliers are k/2⁴⁰ with integer k. Combined with the 2⁻²⁵⁶ cost grid, the whole DP is exact integer arithmetic. The certificate is the stored k (`LAMBDA.json`), and `verify.py` recomputes L(λ) and the bill exactly.

## Conclusion

At a* = (21/20)·a_hi, with the stored multipliers, the exact lower bill is 1 + 2.146289×10⁻⁴ > 1. So no member of the class, under any legal frame assignment, has bill ≤ 1 at a*. The packing ceiling of every member is below a*, so no member lifts it by 5%.

At (1007/1000)·a_hi a second certificate gives 1 + 4.86×10⁻⁶ > 1, so no member lifts it by 0.7%. By monotonicity of the bill in a, the same holds at every larger exponent.

A smaller lift, below 0.7%, is neither shown nor excluded.

## What the class excludes

- Moves across segment boundaries: across the cut between A and B, or into and out of the tail.
- Coefficient-rescaling rewrites.
- Changes to the cut, precondition, cleanup, compensation, pins or endpoints.
- New child interfaces (fanout or gather children) and other words.
