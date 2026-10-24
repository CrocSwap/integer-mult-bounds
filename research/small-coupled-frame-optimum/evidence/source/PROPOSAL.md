# Bounded exact optimization of the 18 small frame components

Prepared 2026-10-23 with OpenAI Codex assistance. **Status: proposal only; optimization and candidate emission are held for the team leader's live ownership and independent-review gate.** The 1,271-variable component will not be enumerated.

## Source and published theorem

The exact source is #4994 head `ef2810fe43829960789f783e44ee6484d0368f09`, package `research/carried-warp-frame-intervals`, retaining #4971 at `0130b196145a43a7d305de41f49e56e8e8556378`. `SOURCE-MANIFEST.json` pins the eight Git-tree snapshots actually used. `inspect_graph.py` reuses only the source's authenticated swap constructor (AST-extracted function, no module-level native replay) and its frame-DAG implementation. This probe is not an independent verification of those source routines or physical phases.

Rina Dechter, **Bucket elimination: A unifying framework for reasoning**, *Artificial Intelligence* 113(1–2), 41–85 (1999), DOI [10.1016/S0004-3702(99)00059-4](https://doi.org/10.1016/S0004-3702(99)00059-4). Publisher metadata and the [author's published PDF](https://ics.uci.edu/~dechter/publications/r76A.pdf) were inspected through the web reader. Section 8, Fig.25 and Theorem 11, journal pp.71–72, give min-sum variable elimination for finite-domain cost networks, with an exact optimum recoverable by stored minimizing choices. Cost factors must be evaluated and compared correctly; complexity is exponential in the induced width after prescribed variables are substituted. The paper does not justify dropping constraints, substituting dimension-only domains, floating-point optimality or physical frame admission.

## Exact mathematical reduction

For every contact v, retain its complete domain

    D_v = { U <= F2^9 : L_v <= U <= H_v }.

The lattice interval is isomorphic to the full subspace lattice of H_v/L_v. Its cardinality is the sum of the Gaussian binomial coefficients for d=dim(H_v)-dim(L_v): for d=0,1,2,3,4,5 the counts are 1,2,5,16,67,374. A domain contains actual subspaces, including every orientation; it is not the integer interval of dimensions and is not limited to the old frame registry.

For each original mapped multiedge e:a→b with its exact invertible binary map G_e, use the binary factor

    phi_e(U_a,U_b) = H_(dim(U_b)-dim(U_a)) if G_e(U_a) <= U_b,
                    M=5328 otherwise,
    H_r = r^(1-C), H_0 = 0.

The finite penalty makes the model meet Dechter's finite nonnegative cost hypothesis directly. For 0<C<1, H_r<=r; the known feasible original schedule has total paid rank 5327 and thus total cost at most 5327. An assignment violating even one mapped edge pays at least 5328, so no global or component minimizer can be infeasible. This remains valid when fixed constants are omitted during a component solve, since that component's source cost is also at most 5327. A symbolic impossible state is an equivalent implementation only if this finite-penalty argument or an extended min-plus proof is retained.

Keep every parallel edge: each corresponds to a live operand's climb. The eight fixed owned-centre calls contribute the separate constant 8H8. Prescribed entrance, exit and owned-contact subspaces remain fixed. A zero-rank edge contributes no paid query. `check_edge_prices.py` audits the factor invoice against the source's original, least and greatest literal paid profiles in both orientations, including the absence of repeated same-operand ADD/COPY contacts that could otherwise cause double counting. `EDGE-PRICE-CHECK.json` records all six exact matches:

| Assignment, identical price in both orientations | Paid histogram |
|---|---|
| Original contacts | {1:2201, 2:412, 3:510, 4:127, 5:40, 8:8} |
| Least | {1:2520, 2:755, 3:225, 4:127, 5:10, 8:8} |
| Greatest | {1:2774, 2:651, 3:301, 4:36, 5:28, 8:8} |

Every profile has rank mass 5327. This price binding reuses the source graph construction; it is separate from an independent physical replay.

Every feasible assignment satisfies the source's complete mapped-containment constraints. #4994's chronological realization theorem then inserts the corresponding ascending climbs while retaining scalar coefficients, swap maps, warp maps and all prescribed boundaries. This is a sufficient binary-frame schedule. Absolute phases and uniform physical implementations of newly introduced frames remain separate obligations.

## Why the small pieces are independent

Substitute every determined contact with L_v=H_v, even when it was not originally prescribed. Its only domain value is that subspace, so each incident binary factor becomes unary (or constant when both endpoints are determined). No factor connects remaining variables across distinct connected components of the resulting undirected graph. Therefore, with the large component held at the original source assignment, optimizing each small component independently gives an exact optimum over that explicitly restricted product of 18 component domains. It is not an optimum over the large component or over broader caller families.

This conclusion uses the complete graph of mapped edge factors, with all original parallel-edge prices. The probe's simple graph is used only for connectivity and elimination ordering; factor evaluation retains the multigraph.

## Measured bounded workload

`GRAPH-STRUCTURE.json` records identical size statistics in forward and backward source orientations:

| Item | Count |
|---|---:|
| All graph nodes / mapped edges | 15,935 / 29,790 |
| Unfixed contacts | 1,339 |
| Domains of sizes 2 / 5 / 16 / 374 | 1,098 / 222 / 16 / 3 |
| Components after fixed substitution | 19 |
| Large component, excluded from search | 1,271 variables |
| Small components searched | 18 components, 68 variables |
| Small component sizes | 15,11,10,9,3,3,3,2,2,2, and eight singletons |
| Sum of small-component bucket assignments under recorded order | 1,095 |
| Largest small bucket / induced width upper bound | 125 assignments / 3 |

The reported bucket workload is a table-size arithmetic bound for that order, before factor-evaluation overhead, exact arithmetic, stored traceback and duplicate/tie handling. It is not a measured optimization runtime. The large component's naive order has a 6.4-billion-assignment maximum bucket; that order is neither a lower bound nor a reason to enumerate it. It remains untouched.

## Objective and evidence proposed for execution

Use C=0.0030217758 as a fixed diagnostic price parameter unless the team leader selects another rational C. This is a comparison parameter inherited from existing conditional research, not a new kappa claim. Store every cost as its exact integer rank histogram (r=1,...,9), including zero/impossible states separately. Compare two histograms using certified rational enclosures of sum_r n_r r^(1-C). Equal histograms are exact ties. If distinct histograms cannot be ordered by the selected enclosure precision, refine the enclosure or retain both; never choose by floating point and label it optimal.

The independent reviewer should check the recurrence, complete quotient-domain enumeration, mapped-edge tables and rank objective before execution. The execution, if authorized by the team leader after ownership clearance, should then:

1. Freeze the 18 component node lists, ordering, original source assignment and exact remaining boundary factors.
2. Enumerate all subspaces in each small domain and verify cardinality, containment, uniqueness and source-value inclusion.
3. Evaluate each original edge factor exactly, keeping maps and multiplicities. Eliminate variables by sum/min with certified histogram comparisons and save the choices needed for traceback.
4. Reconstruct the chosen 68 contact values; leave every large-component and determined contact at its original source value. Run the complete mapped-edge containment check and recompute the exact full native profile from all graph edges plus fixed owned centres.
5. Compare against the full original native profile, report strict interval improvement or no improvement, and record all min-rank-cut differences. Do not assume that improvement at one C implies dominance for every concave price.
6. If a strict improvement exists, hand the exact contact assignment and histogram to a separate priced-event emitter/reviewer. That later stage must materialize the literal schedule, replay all 632 independent inputs, preserve all 408 helper endpoints, verify absolute physical phases/frames, and price any new routing/representation/precision costs. Only after that may the complete p16 P/T, finite compiler reserve and outer transfer be considered.

Stop after this restricted optimization and its independent verification. No large-component search, generic optimality claim, phase compiler reconstruction or kappa digit extraction is part of this proposal. Live ownership and prospective public-claim coordination remain with the team leader.

## Why generic submodular minimization is not substituted

The source-bound probe found a four-assignment counterexample at contacts 9519→9798, keeping every other contact at its original source subspace. Their domains have dimensions 0/1 and 2/3, all four endpoint choices are feasible, and their single connecting edge has cost ranks 1,2,3. All other affected factors are unary in one of these two variables and cancel from the lattice comparison. Thus

    cost(high,low)+cost(low,high)-cost(low,low)-cost(high,high)
      = H1+H3-2H2 < 0

for strictly concave H_r=r^(1-C), 0<C<1. This violates the usual submodular inequality on the actual feasible assignment lattice. It rules out a direct application of a theorem requiring that inequality for this objective. It does not rule out a different lifting, relaxation, discrete-convex formulation or special optimization method.

## Credit and boundaries

#4994's author supplies the sharp frame intervals, feasibility theorem and extremal profiles; Dugongue's #4971 supplies frame-carrying swaps; Cao Yifan and the native/controller/compiler predecessors supply the retained source. Dechter supplies the general exact elimination theorem. This proposal contributes the source-specific finite-domain factorization, graph-size screen, scoped submodularity counterexample and bounded optimization plan. No candidate has been optimized, no productive input has been added, and no scientific admission follows from the graph probe.
