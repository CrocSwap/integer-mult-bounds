# Joint partial transport and exact scalar-circuit gauges

Prepared for Dugongue with substantial OpenAI Codex assistance. Apache-2.0.

## A sufficient exact transporter theorem

Let V be a finite-dimensional vector space over a field, A and B subspaces of V, L another subspace and f:L→V a specified linear map. There exists an invertible G:V→V such that G(A)=B and G restricted to L equals f if and only if:

1. dim A = dim B;
2. f is injective;
3. f(L ∩ A) = f(L) ∩ B.

This is a complete sufficient construction, not just a necessary incidence test.

Proof. Necessity follows by applying G to intersections. For sufficiency, choose a basis C of L∩A, extend it by D to a basis of L, and extend C by E to a basis of A. Their union C,D,E is independent. The vectors f(C),f(D) are independent, and the last condition says their span intersects B exactly in span f(C). Extend f(C) to a basis f(C),E' of B. Therefore f(C),f(D),E' is independent. Extend C,D,E and f(C),f(D),E' separately to bases of V and send one basis to the other. The resulting invertible G is the required map. This is a finite Gaussian-elimination algorithm; over F₂⁹ it is small exact arithmetic.

If the supplied restrictions are individual pairs a_i→b_i, first check every linear dependence among the a_i is also a dependence among the b_i, and conversely. These checks define an injective f on L=span(a_i). Checking separate line memberships without those relation checks is insufficient. For example a₁=e₁,a₂=e₂,a₃=e₁+e₂ cannot map to b₁=e₁,b₂=e₂,b₃=e₁ under any linear map, although every a_i and b_i is nonzero.

With one nonzero pair a→b, the condition reduces to dim A=dim B and a∈A if and only if b∈B. This recovers the constrained-map predicate already used by Cao Yifan's round-three search. Its multi-pair form allows shared native maps with several freed prelude occurrences to be tested jointly, instead of silently constructing inconsistent maps for different contacts.

## Exact all-column gauge identity

For composable linear maps M₁,…,M_s on the whole persistent/owned state and invertible state-coordinate gauges D₀,…,D_s, define

    M'_j = D_j M_j D_(j-1)^(-1).

Then, on every state, including arbitrary independent helper inputs,

    M'_s … M'_1 = D_s (M_s … M₁) D₀^(-1).

Proof: cancel each adjacent D_j^(-1)D_j. This is an operator identity, so basis-column replay can corroborate it but is not its proof. When initial and final gauges are fixed, the complete semantic endpoint is unchanged. If helper entrance gauges change, the helper endpoint changes by the displayed relative conjugation and must be included as its actual productive interface; it is not initialized scratch and it is not interchangeable with an unrelated Gaussian chart.

For an elementary scalar contact x←x+a y, independent data-coordinate gauges on x and y retain exactly that scalar opcode only when the two data-coordinate maps agree (or when their relative map is explicitly implemented and paid). Thus a search cannot free each scalar incidence independently. Choose one frame per scalar contact, include every paid transition between consecutive contacts, require the same physical native G at all its occurrences, and use the transporter theorem to test the complete joint constraints. The conjugation identity then supplies an all-column proof for the changed gauge schedule. Exact Clifford lifting must retain absolute phases, rather than checking only projective matrix agreement.

## Application to the twelve prelude contracts

The current round-three witness keeps the twelve additional prelude maps fixed. To extend that feasible set, expose their prelude line contacts as shared variables as well as their late source/target subspaces. For each reused G, combine every prescribed pair into one partial f and apply the theorem. A candidate has a positive admission path only after reconstructing the entire chronological word, counting all paid rank changes and owned jobs, retaining main endpoints, authenticating every helper's relative interface, lowering absolute Clifford phases and replaying all independent columns.

This is a constructive search-enabling theorem. It claims no improvement from any candidate not yet emitted and admitted, no global optimality for the finite search, and no resolution of PR #4629's changed-main endpoint objection. Credit Cao Yifan's joint helper/native-map search, Dugongue's transported warp-frame lemma, Cinna Davis's joint-helper circuit and the cumulative Clifford/compiler lineage. The basis extension and gauge cancellation are classical linear algebra, stated here in the concrete sufficient form needed by this contact search.
