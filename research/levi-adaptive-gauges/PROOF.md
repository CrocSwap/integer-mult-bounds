# Support, adaptive gauges and the Levi inverse dual

## 1. Exact ingredients taken from the TI_SP proof

The inspected canonical module Mathproof.SymplecticTI contains:

- `map_eq_of_eqOn_msupp`: maps agreeing on the intrinsic mode support of a tensor act identically on it.
- `levi_isSymplectic`: P ↦ diag(P,P^−T) preserves the hyperbolic form Ω((x,α),(y,β))=β(x)−α(y).
- `levi_trans`: the Levi lift respects composition.

These declarations were also retrieved from the authoritative shared DAG. The source hash is in PRECEDENTS.json. This is source/provenance reuse, not a new Lean import or fresh kernel audit. The source itself attributes the Levi embedding to classical prior art; its exact-orbit support-reflection theorem is a separate part of the TI_SP argument.

For a row contribution q supported on source coordinates I and target y, the coefficient tensor is e_y ⊗ q. Its output-mode support lies in span(e_y). A diagonal gauge that scales e_y by 2^b acts on this coefficient tensor by exactly 2^b; its extension outside that support is irrelevant to this contribution by the support-substitution lemma. This concerns **coefficient support**, not a claim that arbitrary input data vanish outside I. The dirty initial y is scaled and restored explicitly. The useful algorithmic change is to let b vary between support groups rather than fix one b across the whole row.

## 2. Native dyadic pricing

For q=o 2^v ≠ 0 with signed odd integer o, the retained ADD price is

A(q)=c(o)+2|v|,  c(o)=2(2+bit_length(|o|)+popcount(|o|)).

A positive SCALE by 2^e costs 2|e|. Proof: shifting the numerator by a positive power of two increases only its bit length; a negative exponent contributes the denominator bit length. Popcount is unchanged. These are exactly the two branches of the authenticated native formula. ∎

## Theorem 1: a dirty-target adaptive gauge schedule is exact

Suppose X_i are unchanged source fields, Y is a disjoint target and q_i are dyadic. Maintain an integer gauge b, initially 0, representing the current stored target as 2^b times its logical partial sum. To change b to b', SCALE Y by 2^(b'−b). At level b, execute an original row contribution with adjusted ADD coefficient 2^b q_i. Execute every original nonzero contribution exactly once, in any order, then return b to 0.

The final target is its arbitrary initial value plus Σ_i q_i X_i; every source and exterior field is unchanged. No clean entry or scratch field is needed.

Proof. SCALE changes the representation factor while preserving the logical partial sum. ADD contributes (2^b q_i)X_i to the stored target and hence q_i X_i to its logical value. Induction gives the invariant throughout, including the arbitrary dirty initial Y. Returning to b=0 yields the claimed exact map. All coefficients are dyadic and every scale is a native unit. ∎

## Theorem 2: a finite interval formula gives the optimum in this family

Let s_i=−v(q_i), C=Σ_i c(odd(q_i)). Allow arbitrary ADD order, each original nonzero ADD once, and arbitrary integer target-gauge schedules starting and ending at 0. The optimal allowance equals

C + min_(L≤0≤H) [4(H−L)+2 Σ_i dist(s_i,[L,H])].

A minimizer exists with L and H drawn from {0,s_i}, subject to their signs.

Proof, lower bound. Any such schedule visits some minimum L and maximum H. Its closed total variation is at least 2(H−L), so SCALE cost is at least 4(H−L). An ADD performed at b∈[L,H] costs c_i+2|s_i−b|, at least c_i+2 dist(s_i,[L,H]). Sum these inequalities.

Construction attaining the bound. Assign contribution i to b_i=clamp(s_i,L,H). Walk 0 → L → H → 0 and serve each group at b_i in increasing order during the L → H leg. Its total variation is exactly 2(H−L); every contribution attains its minimum allowed valuation cost. Theorem 1 proves the exact dirty-target map.

Finite optimization. Between consecutive breakpoints among {0,s_i}, the objective is affine in each endpoint. A minimizer can be moved to a breakpoint without increasing cost. Beyond all breakpoints, increasing interval width strictly increases cost without further reducing ADD costs. Thus the finite candidate set suffices. Ties use minimum width, then endpoint order. The zero interval is available, so this compiler never exceeds the direct coalesced row bill. ∎

The implementation enumerates endpoint pairs and emits the attaining schedule. It uses polynomial work in row length and coefficient bit length; the simple cost enumeration is O(n³) per row. This is a restricted-family optimum, not a lower bound for arbitrary circuits, shared temporaries, non-diagonal gauges or cross-row factoring.

## Theorem 3: Levi dualization preserves order, correctness and scalar bill

For the invertible elementary scalar maps of a schedule, let P be their product in execution order. The Levi lift gives diag(P,P^−T), preserving Ω. Its homomorphism property implies that the inverse-dual program uses the **same execution order**, with

ADD t ← t+q s  replaced by ADD s* ← s*−q t*,

SCALE t ← 2^e t replaced by SCALE t* ← 2^−e t*.

Proof. For an elementary transvection, inverse transpose swaps its off-diagonal indices and negates q. A diagonal scale inverts. The map P ↦ P^−T is a homomorphism because (AB)^−T=A^−T B^−T. Hence elementwise dualization in the same execution order gives the complete inverse transpose. This is the coordinate instance of `levi_trans` and `levi_isSymplectic`. ADD pricing ignores sign and SCALE pricing is symmetric in e, so every primitive has the same allowance. ∎

A bipartite shear Y←Y+MX therefore has inverse-dual shear X*←X*−MᵀY*. The backward physical role binding is checked independently against the actual source window. No second physical copy of the registers is allocated; the doubled symplectic space supplies the proof relating the two separately executed interfaces.

## 4. Source specialization and measured consequences

Row-wise schedules are composable because sources and targets are disjoint and every row uses unchanged sources. The two repeated-input windows keep #4502's cheaper 42-cost borrowed adapters. The other windows use the adaptive compiler, producing 316 and 216 instead of 358 and 224. Thus the four-window cost is 316+42+42+216=616 in each orientation, versus 666 previously and 766 in the original word.

The 1 × 38 row chooses interval [0,2]. Its increasing-level schedule serves integer/large coefficients before half coefficients and then quarter coefficients; it ends by unscaling the dirty target. Its cost is 316. A decreasing traversal has the same scalar price but a worse measured backward suffix factor; the chosen increasing traversal gives 4,871 instead of 4,885. This demonstrates why endpoint/cost equality alone does not imply equal error propagation.

Eight exact source windows are checked on all local columns and installed into both complete native words. The original non-scalar events and field inventory are retained exactly. The full independent literal/prefix replays verify the identity-shear endpoint on all 632 arbitrary persistent inputs plus the original dirty owned C field, restoration of all 408 helpers, C=0 at exit, scalar frame correctness and the retained paid profile. Scalar totals become 157,970 forward and 158,018 backward, a saving of 150 over the original or 50 over #4505 per orientation.

The exact ideal prefix maxima remain unchanged. Applying #4510's suffix certificate gives uniform entire-field ADD/SCALE defect factors 1,328 forward and 4,871 backward in its explicit logical isometry model. This improves the previous backward sufficient factor 4,879 by 8; it does not imply coordinatewise domination for every unequal physical error budget. Physical phase-receipt consumption, actual rounding/recursive defect contracts and the complete all-size induction remain separate obligations. No new κ or measured runtime speedup is established.
