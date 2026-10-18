# Exact interaction and unique fixed-menu optimum

Fix the pinned PR1263 background and, for each of the nineteen helpers, one complete temporal schedule. A chosen schedule includes all of its entry, transition and terminal restoration SCALEs. Omitted schedules have exponent zero throughout. All scales are charged, and each original ADD is retained in order.

For an ADD with coefficient q, destination exponent a and source exponent b, its coefficient is q·2^(a−b). Let c(q) be the attributed exact real-component ADD price, including the unit-coefficient discount. The shared-operation correction is

    c(q·2^(a−b)) − c(q·2^a) − c(q·2^(−b)) + c(q).

An ADD has at most two operands. Transition charges separate by helper. Thus the exact change for any subset S is

    F(S) = Σ[h∈S] single_h + Σ[{h,j}⊆S] cross_hj.

There are no higher-order interactions in this fixed-menu objective. This does not claim convexity: the unit discount makes the price nonconvex.

For the pinned menu, the singleton sum is −973 real primitives in each orientation. The only nonzero accumulated pair corrections are +3 for (348,359) and +4 for (479,515). Full-menu change is therefore −966 real, or −1,932 complex primitives. Other shared ADDs are inspected and can have zero aggregate correction; absence of a nonzero correction is not absence of an ADD.

For each helper h, calculate

    B_h = single_h + Σ[j≠h] max(0, cross_hj).

For any subset omitting h, its exact marginal from adding h is at most B_h. Every B_h is strictly negative; the largest is −11. Consequently every proper subset can be strictly improved by adding any missing coordinate. The full nineteen-helper menu is the unique optimum of this fixed menu. This proof applies separately to each orientation and does not assume their symmetry.

The verifier recomputes the coefficient corrections and all marginal bounds, compares the actual complete invoice with this objective, and confirms the emitted winner on all 712 formal scalar columns. Zero menu identity, direct emitted-word invoices for all sixteen subsets of helpers 348/359/479/515, and deletion of an exactly identified inserted transition SCALE are controls. Optional Gray-code and least-set-bit censuses independently validate all 524,288 subsets per orientation; no word replay is performed for every subset.

For scalar correctness, inserted transitions maintain the current diagonal gauge: each ADD coefficient is conjugated by destination/source exponent difference, original diagonal SCALEs commute, and terminal restoration returns every selected helper to exponent zero. These helpers have no incident COPY/CLEAR and are cold/FULL and unwrapped in the pinned word. Complete formal replay checks all dirty inputs and both separately supplied chronological orientations. It does not replace native interface or global hosting admission.
