# Exact closure bound for one common vector

Fix #7334's literal 76,466-event word and #7113's signed caller. A segment is a role's lifetime between consecutive frame-changing events or endpoints. Form common-chart components by joining segments that share a literal ADD or COPY. Uncontacted segments are singleton components. An eligible component contains only public helper segments and touches neither endpoint. Main roles, owned roles, boundaries, scalar words and productive targets are fixed.

Choose one nonzero vector v in F₂⁹. Any subset of eligible components that do not already contain v may add v to their common frame. Each selected frame grows by one rank. All unselected frames stay fixed. If a recomputed MOVE gap vanishes, the price grants H(0)=0. This only enlarges the search relative to requiring every literal paid position to stay positive.

For a literal paid edge L⊂U of old gap d, write x for whether L grows and y for whether U grows. An inactive component has indicator zero.

- If v lies in U, then y=0. Growing L keeps containment and saves H(d)−H(d−1). Use the directed upper endpoint for that benefit.
- If v lies outside U, containment requires x≤y. A selected L forces U, or is forbidden when U cannot grow. Growing U alone changes the gap to d+1 and pays H(d+1)−H(d). Use the directed lower endpoint for that penalty. Growing both leaves the gap unchanged.

This identity accounts for every touched edge exactly once. The raw total for 17 copies has the same sign as the one-copy sum. The lead collects linear weights and hard implications and solves maximum closure. The independent verifier instead sends an edge from source to L for each benefit, an edge from U to L for each finite penalty, and an infinite edge from L to U for the containment implication. When one endpoint is fixed at zero, the appropriate edge terminates at the sink. Use total offered benefit plus one integer unit for an infinite capacity. Cutting no variable gives a cut with capacity equal to the total offered benefit. Every cut using a hard edge costs more, so no such cut minimizes.

The upper saving equals the offered benefit minus the minimum cut. Exact augmenting-path flow saturates all source benefits for all 511 choices. Thus the upper saving is zero and the empty selection attains it. Outward price bounds cover the entire old crossing bracket. Any positive improvement in the tested model would require a positive upper saving and is excluded.

The lead uses a forward union-find and a maximum-closure flow implementation. The independent engine walks backward from final charts, reconstructs lifetimes, joins by DFS and tests the direct edge-capacity cut with shortest augmenting paths. Both recover 1,517 total components, 482 eligible components and 2,292 incident paid edges. They agree on the active component and hard implication counts for every vector and on the exact rational directed price intervals.

This argument leaves vector-dependent growth across components, shrinking a frame, endpoint changes, retiming, or changed scalar and owner actions open. It does not assert a lower bound for a different model.
