# A native-first portfolio preserves the better proven route

Prepared for Dugongue with substantial OpenAI Codex assistance. Informal universal theorem; no worldwide novelty claim for dovetailing.

Fix two correct terminating packed-integer multiplication algorithms A and B on the same bounded-word RAM instruction model. Count every input-specific setup, table construction, computation and output operation. Assume their address bounds are polynomial in n and their required word widths are O(log n), with fixed constants. Both logical shifts and word multiplication are allowed; a route using fewer primitives is also an algorithm on this model. Let t_A(x,y) and t_B(x,y) be their actual instruction costs.

There is a uniform portfolio multiplier with total operation cost

    O(min(t_A(x,y), t_B(x,y)) + ceil(n/w))

and no assumption that either route wins. This is an implementable sufficient construction, not a proposed theorem conditioned on an unknown fast gadget.

Construction: retain one readonly packed input, prepare two disjoint virtual machine contexts and private writable memory arenas, and alternate one simulated RAM instruction from each. Every input-dependent preparation instruction is part of that schedule. Stop when either context genuinely halts with its complete packed output. Return that output buffer, or copy it once if the public ABI fixes a separate output buffer.

Correctness follows because each context has the same state evolution as its standalone program; disjoint writable arenas prevent interference. Both algorithms are correct under their explicitly retained premises, so either returned product is exact. Dovetailing does not make an incorrect candidate safe: both correctness contracts are required.

At most 2*min(t_A,t_B) source instructions are scheduled before the first halt. Each is implemented by a constant number of target instructions because the two fixed instruction sets are finite, register contexts are bounded, and memory accesses use explicit disjoint arena offsets. An extra fixed address bit or larger fixed multiplier in w absorbs the sum of the two polynomial address envelopes. If the sources use different fixed word-width constants, emulate each source width by a fixed number of words and mask modular arithmetic at that width. This is constant overhead; no unbounded integer is treated as a word. Program counters, halt tests and code lookup are charged. Each setup allocation is initialized only through its own charged operations. The final copy, if required, costs O(n/w). These facts prove the stated bound.

If A and B both have proven upper bound O(n/(log n)^kappa) with kappa < 1, the portfolio has that same bound because n/w = O(n/log n) is no larger. Thus a native-first experimental backend can be added without abandoning the transferred TM guarantee. This is a positive safe-adoption theorem, not proof that the native backend is faster.

For a stronger asymptotic upper-bound claim, a native proof of O(n/(log n)^(kappa+delta)) for fixed delta > 0 would improve the currently stated comparison envelope by a factor (log n)^delta. It would not prove an actual runtime separation from a baseline known only by an upper bound: the baseline may also run faster than its proved bound. A real runtime-separation theorem needs additional information about the baseline cost.

This theorem concerns the mathematical portfolio construction. Neither complete asymptotic multiplication implementation has been emitted here, so no practical portfolio benchmark is claimed. Credit classical algorithm dovetailing and the bounded-word/dirty-arena compiler precedents described in the preceding native package.
