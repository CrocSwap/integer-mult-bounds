# Volume III — Combinatorial certificates and discrete structure

This is an informal mathematical atlas: 90 proved results and 10 explicitly labelled research conjectures, numbered C001–C100. A proof here is an English argument, not a claim of Lean verification. Unless stated otherwise, sets, graphs, matroids and posets are finite; graphs are simple and undirected, fields are arbitrary, and cardinalities count distinct objects. A source hook gives attribution or a connection to an inspected declaration; it does not claim the source formalizes this entire entry. Source hashes, exact declaration excerpts and current-status evidence are in `../sources/03-sources.json`.

The ten conjectures are research targets, not premises used in any proved entry. Their special cases are proved separately inside the entries. Historical conjecture names require care: ordinary cycle double cover and the downset intersecting-family conjecture received proof announcements in 2026, and the unrestricted real sum-product conjecture received a counterexample. We use different, precisely stated targets below.

## 1. Submodularity, certificates and uncrossing

For this section E is finite, f:2^E→R, and f(∅)=0 when normalization is specified. Submodularity means f(A)+f(B)≥f(A∪B)+f(A∩B).

<a id="c001"></a>

### C001 — Diminishing returns characterizes submodularity

**Claim.** Submodularity is equivalent to f(A∪{e})−f(A)≥f(B∪{e})−f(B) whenever A⊆B and e∉B.

**Proof.** Apply the submodular inequality to A∪{e} and B for one direction. Conversely, enumerate A\B as e₁,…,e_k. Compare the marginal of e_i added to (A∩B)∪{e₁,…,e_{i−1}} with its marginal added to B∪{e₁,…,e_{i−1}}. Summing gives f(A)−f(A∩B)≥f(A∪B)−f(B), exactly the required inequality. Empty differences contribute zero.

**Dependencies/source.** Direct proof; classical submodularity. **Use.** Converts a global inequality into local exchange inequalities.

<a id="c002"></a>

### C002 — A greedy vector is a base-polytope certificate

**Claim.** Suppose f is normalized and submodular. For an ordering e₁,…,e_n, put P_i={e₁,…,e_i} and v(e_i)=f(P_i)−f(P_{i−1}). Then v(E)=f(E) and v(S)≤f(S) for every S⊆E.

**Proof.** The first equality telescopes. For each e_i∈S, C001 compares its marginal on P_{i−1} with its marginal on S∩P_{i−1}; the former is no larger. Sum these comparisons over elements of S in order. The latter marginals telescope to f(S)−f(∅)=f(S).

**Dependencies/source.** C001; classical greedy base construction. **Use.** Supplies explicit feasible points for B(f)={x∈R^E:x(E)=f(E), x(S)≤f(S) for all S}.

<a id="c003"></a>

### C003 — Exact support function of a submodular base polytope

**Claim.** Under C002, order any real weights w so w₁≥⋯≥w_n. Then max_{x∈B(f)}w·x=w_n f(E)+Σ_{i<n}(w_i−w_{i+1})f(P_i), attained by C002's vector. For E=∅ the maximum is zero.

**Proof.** Summation by parts gives w·x=w_n x(E)+Σ_{i<n}(w_i−w_{i+1})x(P_i). Each coefficient in the sum is nonnegative, so the defining constraints give the claimed upper bound, even when w_n is negative. The greedy vector satisfies v(P_i)=f(P_i) for every i, so attains every bound simultaneously.

**Dependencies/source.** C002. **Use.** An optimality certificate requiring only a chain of tight constraints.

<a id="c004"></a>

### C004 — Tight sets uncross

**Claim.** If x(S)≤f(S) for all S and f is submodular, then sets A,B satisfying x(A)=f(A), x(B)=f(B) also have tight union and intersection.

**Proof.** Modularity of sums gives x(A)+x(B)=x(A∪B)+x(A∩B). Feasibility and submodularity sandwich the right side between f(A)+f(B) and itself: x(A∪B)+x(A∩B)≤f(A∪B)+f(A∩B)≤f(A)+f(B). Thus both nonnegative feasibility slacks sum to zero, so each is zero.

**Dependencies/source.** Definition of submodularity. **Use.** Replaces crossing certificate constraints by lattice-closed families without losing equality.

<a id="c005"></a>

### C005 — Submodular minimizers form a lattice

**Claim.** The minimizers of a submodular f over all subsets of E are closed under union and intersection. In particular they have a unique inclusion-minimal member and a unique inclusion-maximal member.

**Proof.** Let m be the minimum. For minimizers A,B, submodularity gives f(A∪B)+f(A∩B)≤2m; minimality bounds each term below by m, so both equal m. Finite repeated intersections and unions of all minimizers give the two extreme members, and their defining containment makes them unique.

**Dependencies/source.** Direct uncrossing. **Use.** Canonical choices among multiple optimal solutions.

<a id="c006"></a>

### C006 — Weighted cut submodularity with exact slack

**Claim.** For an undirected graph with nonnegative edge weights, c(S)=w(δS) is submodular, with c(A)+c(B)−c(A∪B)−c(A∩B)=2w(E(A\B,B\A)).

**Proof.** Partition vertices into A∩B, A\B, B\A, and the complement of A∪B. Check the contribution of an edge according to its two parts. Edges between the two difference parts contribute twice on the left; every other edge contributes zero. Summing weighted contributions proves the identity, and nonnegative weights give the inequality.

**Dependencies/source.** Direct edge count. **Use.** Identifies exactly when two minimum-cut constraints can cross tightly.

<a id="c007"></a>

### C007 — Coverage functions are submodular

**Claim.** Given subsets S_e of a finite feature set U with nonnegative feature weights a_u, f(A)=Σ_{u∈∪_{e∈A}S_e}a_u is normalized, monotone and submodular.

**Proof.** Normalization and monotonicity follow from inclusion. The marginal for e is the total weight of S_e's features not already covered. If A⊆B, the uncovered features for B form a subset of those for A, so nonnegativity gives diminishing returns. Apply C001.

**Dependencies/source.** C001. **Use.** Justifies approximation guarantees for selecting experiments, sensors or tests with overlapping benefits.

<a id="c008"></a>

### C008 — Greedy cardinality approximation

**Claim.** If f is normalized, nonnegative, monotone and submodular, and 1≤k≤|E|, repeatedly adding a largest-marginal unused element gives G_k with f(G_k)≥[1−(1−1/k)^k] max_{|S|≤k}f(S).

**Proof.** Let O be optimal and G_i the i-step set. Adding O's elements one at a time and using C001 gives f(O)−f(G_i)≤Σ_{e∈O\G_i}[f(G_i+e)−f(G_i)]. At most k terms occur, each no larger than the next greedy marginal. Thus the remaining gap contracts by a factor at most 1−1/k at each step. Starting with gap f(O), induction and rearrangement prove the formula. If the gap is already zero, monotonicity preserves the conclusion.

**Dependencies/source.** C001; classical greedy analysis. **Use.** A sufficient performance guarantee from verified diminishing returns alone.

<a id="c009"></a>

### C009 — Convexity of the Lovász extension

**Claim.** For normalized submodular f, define L_f(w)=Σ_i w_i[f(P_i)−f(P_{i−1})] using a nonincreasing ordering of the coordinates of w. This is well defined and convex on R^E.

**Proof.** C003 identifies this expression with max_{x∈B(f)}w·x, independently of how equal coordinates are ordered. Every linear functional w↦w·x is convex; their pointwise maximum is convex, since for 0≤t≤1 each x satisfies (tw+(1−t)z)·x≤t max_y w·y+(1−t)max_y z·y. C002 ensures the maximum is attained and finite as explicitly evaluated in C003.

**Dependencies/source.** C002–C003; Lovász extension. **Use.** Passes discrete submodular optimization to a continuous convex certificate.

<a id="c010"></a>

### C010 — Research conjecture: union-closed frequency one half

**Conjecture.** A finite union-closed family F containing a nonempty set has an element belonging to at least |F|/2 members.

**Evidence, not a proof.** For a chain under inclusion, any element of its smallest nonempty member lies in every nonempty member; there are at least half as many nonempty members as members in total. The full power set attains frequency exactly one half. Costa–Sadhu's October 2026 primary preprint proves a smaller universal proportion, not this claim.

**Dependencies/source.** Frankl's union-closed sets conjecture; [Costa–Sadhu, 2026](https://arxiv.org/abs/2610.02295). **Use/approach.** A frequency certificate from closure alone would strengthen selection arguments; possible tools include entropy inequalities and uncrossing. Those tools do not constitute a proof here.

## 2. Matroid rank, exchange and concrete representations

A matroid here is a finite ground set E with a nonempty hereditary family of independent sets satisfying augmentation: if independent I,J have |I|<|J|, some e∈J\I extends I independently. The rank r(A) is the largest size of an independent subset of A. Augmentation implies every maximal independent subset of A has size r(A).

<a id="c011"></a>

### C011 — Rank is submodular

**Claim.** Matroid rank is normalized, integer valued, monotone, bounded by |A|, and submodular.

**Proof.** Only the last assertion needs argument. Extend a basis I of A∩B to a basis J of A, then extend J to a basis K of A∪B. No element of A\J can enter an independent extension of J, so K\J⊆B\A. The independent set I∪(K\J) lies in B. Hence r(A∩B)+r(A∪B)−r(A)=|I|+|K\J|≤r(B), as required. All extensions exist by finite augmentation.

**Dependencies/source.** Matroid axioms; source hook `Mathlib.Combinatorics.Matroid.Basic`. **Use.** Imports the entire first section's certificate toolkit into matroids.

<a id="c012"></a>

### C012 — Rank axioms reconstruct a matroid

**Claim.** Conversely, an integer-valued normalized monotone submodular r with 0≤r(A)≤|A| defines a matroid by declaring I independent exactly when r(I)=|I|; its rank function is r.

**Proof.** Submodularity implies adding one element increases rank by at most one. Therefore, if J⊆I and r(I)=|I|, then r(J)≥r(I)−|I\J|=|J|, proving heredity. If independent I,J with |I|<|J| admitted no extending element from J\I, diminishing returns would make r(I∪J)=r(I), contradicting monotonicity and r(J)>r(I). This proves augmentation. Finally take a maximal independent I⊆A. No remaining element raises r(I), again by the unit-increment bound and maximality; diminishing returns yields r(A)=r(I)=|I|. Thus the reconstructed rank is exactly r.

**Dependencies/source.** C001. **Use.** Certifies a new matroid by inequalities instead of checking all exchanges directly.

<a id="c013"></a>

### C013 — Closure and the exchange law

**Claim.** Define cl(A)={e:r(A+e)=r(A)}. Then closure is monotone and idempotent. If e∈cl(A+f)\cl(A), then f∈cl(A+e).

**Proof.** Diminishing returns shows that an element of cl(A) remains in cl(B) when A⊆B. Adding all elements of cl(A) therefore leaves rank unchanged. If e∈cl(cl(A)), monotonicity gives r(A+e)≤r(cl(A)+e)=r(A), so e∈cl(A), proving idempotence. For exchange, r(A+e)=r(A)+1. The hypotheses imply r(A+f+e)=r(A+f); monotonicity forces this common value to be at least r(A)+1 and at most r(A)+1. Hence r(A+e+f)=r(A+e), as claimed.

**Dependencies/source.** C001, C011. **Use.** Turns span calculations into finite rank comparisons.

<a id="c014"></a>

### C014 — Fundamental circuits are unique

**Claim.** If I is independent and I+e is dependent, it has a unique minimal dependent subset C; it contains e. Moreover I−b+e is independent exactly when b∈C\{e}, for b∈I.

**Proof.** Minimal dependent sets exist by finiteness, and each must contain e. If distinct circuits C,D existed, their intersection would be independent. Since each circuit has rank its size minus one, submodularity gives r(C∪D)≤|C∪D|−2. But (C∪D)−e⊆I is independent of size |C∪D|−1, a contradiction. If b∉C, the circuit remains after deleting b. If b∈C and the deletion were dependent, it would contain another circuit of I+e, contradicting uniqueness. This proves the exchange characterization.

**Dependencies/source.** C011. **Use.** Localizes which deletions repair an insertion.

<a id="c015"></a>

### C015 — Symmetric basis exchange

**Claim.** If B,D are bases and b∈B\D, there exists c∈D\B for which both B−b+c and D−c+b are bases.

**Proof.** Let C be the fundamental circuit of b relative to D. If every element of C−b were in cl(B−b), then b, being spanned by C−b, would lie in cl(B−b) by C013. That is impossible since B is independent. Choose c∈C−b outside this closure. Such c is outside B, and B−b+c is independent of full rank. C014 shows D−c+b is also independent of full rank. To justify the span assertion used above, a circuit C has rank |C|−1 while C−b is independent of that size, so b∈cl(C−b).

**Dependencies/source.** C013–C014. **Use.** Preserves feasibility in two configurations simultaneously.

<a id="c016"></a>

### C016 — Weighted matroid greedy optimization

**Claim.** Scanning elements in nonincreasing real weight and retaining an element whenever independence is preserved produces a maximum-weight basis.

**Proof.** In every scanned prefix, the retained elements form a maximal independent subset, hence have the prefix's rank. Any basis has at most that many elements in the prefix. All bases have the same size. Summation by parts, exactly as in C003 but with prefix cardinalities in place of prefix sums, now compares their weights with nonnegative successive weight differences. The greedy basis attains the upper bound. Negative weights cause no problem because the total size is fixed.

**Dependencies/source.** Augmentation and C003's elementary identity. **Use.** A correctness theorem for rank-oracle algorithms, not just an optimal-value bound.

<a id="c017"></a>

### C017 — Contraction has an explicit rank certificate

**Claim.** For A⊆E, the function r_A(X)=r(A∪X)−r(A) on E\A is a matroid rank function. If B is a basis of A, then I is independent in the contraction exactly when B∪I is independent in the original matroid.

**Proof.** Normalization, integrality, monotonicity and submodularity are inherited from r. Adding |X| elements increases rank by at most |X|, giving the size bound; C012 constructs the matroid. Since A⊆cl(B), C013 implies r(A∪I)=r(B∪I). Thus r_A(I)=|I| is equivalent to r(B∪I)=|B|+|I|, exactly independence of B∪I, because B and I are disjoint.

**Dependencies/source.** C011–C013. **Use.** Removes already committed resources while preserving exact feasibility.

<a id="c018"></a>

### C018 — Matchable subsets form a transversal matroid

**Claim.** In a bipartite graph with left ground set L, the subsets of L that can be matched injectively into the right part form a matroid.

**Proof.** Empty-set feasibility and heredity are immediate by restricting a matching. Let matchings cover I and J, with |I|<|J|, and restrict the graph to left vertices I∪J. C022's alternating-path argument gives an augmenting path for the matching of I, since the matching of J is larger. Its initially unmatched left endpoint lies in J\I; toggling the path keeps every previously matched left vertex matched and adds this endpoint. Consequently I gains an element of J and remains matchable, proving augmentation.

**Dependencies/source.** C022, whose proof uses no matroid facts; `Mathlib.Combinatorics.Hall.Basic`. **Use.** Transfers matroid exchange and optimization to assignment problems.

<a id="c019"></a>

### C019 — Forests form a graphic matroid

**Claim.** The acyclic edge subsets of a graph form a matroid.

**Proof.** Deleting edges preserves acyclicity. Let forests I,J satisfy |I|<|J|. If every edge of J joined vertices within a single component of I, the restriction of J to a component with q vertices would have at most q−1 edges. Summing over components gives |J|≤Σ(q−1)=|I|, a contradiction. Thus some edge of J connects distinct I-components, and adding it creates no cycle. The forest edge count used here follows by repeatedly deleting a leaf in each nontrivial tree component, or equivalently by the argument in C041.

**Dependencies/source.** Elementary forest count, proved again in C041 independently. **Use.** Places spanning-tree exchange and greedy minimum spanning trees in the same framework.

<a id="c020"></a>

### C020 — Research conjecture: Rota's basis rearrangement

**Conjecture.** Given n labelled disjoint bases B₁,…,B_n of a rank-n matroid, their union can be partitioned into n bases, each meeting each B_i exactly once. Repeated underlying vectors may be represented by distinct parallel labelled elements.

**Evidence, not a proof.** For n=1 this is immediate. For n=2, apply C015 to any element of B₁; the exchanged pair of bases each contains one element from each original basis. Montgomery–Sauermann obtain asymptotically tight approximate packing and covering, which does not establish the exact n-by-n assertion.

**Dependencies/source.** [Montgomery–Sauermann, 2025](https://arxiv.org/abs/2508.05601). **Use/approach.** Simultaneous independent scheduling; exchange graphs and absorption might bridge approximation to exactness, but no such bridge is proved here.

## 3. Matching and assignment certificates

A bipartite graph has designated disjoint parts L,R; N(S) denotes the right neighbors of S⊆L. Matching edges have disjoint endpoints.

<a id="c021"></a>

### C021 — Hall's theorem, including the equality split

**Claim.** A matching saturating L exists if and only if |N(S)|≥|S| for all S⊆L.

**Proof.** Necessity follows by restricting the matching. For sufficiency induct on |L|. If a nonempty proper S has equality, match S into N(S) inductively. For T⊆L\S, Hall on S∪T gives |N(T)\N(S)|≥|T|, so the remaining graph also has a saturating matching. Otherwise every nonempty proper S has |N(S)|≥|S|+1. Choose any edge xy with x∈L, delete its endpoints, and apply induction: each nonempty remaining left subset loses at most one neighbor, so still satisfies Hall. The case |L|=1 follows directly, and the empty case is vacuous.

**Dependencies/source.** Direct induction; inspected Hall source declarations. **Use.** A universal sufficient assignment condition with constructive decomposition at tight sets.

<a id="c022"></a>

### C022 — Berge's augmenting-path criterion

**Claim.** A matching M has maximum size exactly when no path alternates between edges outside and inside M and has both endpoints unmatched by M.

**Proof.** Toggling the edges of such a path increases size by one. Conversely, if N is a larger matching, the graph with edge set M△N has maximum degree two. Its components are alternating paths, alternating even cycles, or isolated vertices. Cycles and equal-length alternating paths contribute equally to both matchings. Since |N|>|M|, one path has one more N-edge; its endpoints are unmatched by M. It is the required augmenting path.

**Dependencies/source.** Elementary symmetric difference. **Use.** Gives a falsifier and a repair for any nonmaximum matching.

<a id="c023"></a>

### C023 — König's matching–cover equality

**Claim.** In a bipartite graph, the maximum matching size equals the minimum vertex-cover size.

**Proof.** A cover must meet every edge of a matching, so its size is at least the matching size. Take a maximum matching M. From unmatched left vertices, follow nonmatching edges left-to-right and matching edges right-to-left; call the reachable sets Z_L,Z_R. There is no reachable unmatched right vertex by C022. The set (L\Z_L)∪Z_R covers every edge: an uncovered edge would go from reachable left to unreachable right, impossible by the traversal rule, including for a matching edge. Every vertex in this cover is matched, and each matching edge contributes exactly one endpoint because reachability is equivalent for its two endpoints. Its size is |M|.

**Dependencies/source.** C022. **Use.** A primal–dual optimality certificate with integral witnesses.

<a id="c024"></a>

### C024 — Regular bipartite graphs have perfect matchings

**Claim.** A bipartite graph or multigraph with every vertex of degree d>0 has a perfect matching.

**Proof.** Counting edges gives d|L|=d|R|, hence equal part sizes. For S⊆L, its d|S| incident edges all end in N(S), which has at most d|N(S)| incident edges. Thus Hall's condition holds. C021 yields a matching of L, and equal part sizes make it perfect. Parallel edges do not affect the neighbor sets or the counting argument.

**Dependencies/source.** C021. **Use.** Extracts balanced one-to-one schedules from degree balance alone.

<a id="c025"></a>

### C025 — Bipartite edge coloring uses exactly Δ colors

**Claim.** The edges of a bipartite multigraph of maximum degree Δ can be partitioned into Δ matchings; no fewer suffice when Δ>0.

**Proof.** Pad the two parts with isolated vertices until their sizes are equal. Add edges, allowing parallel edges, between pairs of vertices with positive degree deficits until all degrees equal Δ. Total deficits on the two sides are equal, so this finishes. C024 supplies a perfect matching; deleting it leaves a (Δ−1)-regular graph. Inductively decompose into Δ perfect matchings, then restrict to the original edges. A vertex of degree Δ requires Δ distinct colors, proving optimality. The empty graph uses zero colors.

**Dependencies/source.** C024. **Use.** Converts resource degrees into exact time-slot requirements.

<a id="c026"></a>

### C026 — Hall's theorem with demands and capacities

**Claim.** For integer demands b_l≥0 and capacities c_r≥0, assigning b_l distinct units from each l to adjacent right vertices without exceeding c_r is possible exactly when Σ_{l∈S}b_l≤Σ_{r∈N(S)}c_r for every S⊆L. Multiple units may use the same original edge.

**Proof.** Necessity is counting. Replace l by b_l identical clones and r by c_r identical clones, joining all corresponding pairs. For any subset T of left clones, let S be their original vertices. Its size is at most Σ_S b_l, and its neighbors are precisely all clones of N(S), so Hall holds. A matching of all clones yields the required assignment. Conversely an assignment can be realized with distinct right clones because the capacity inequalities hold.

**Dependencies/source.** C021. **Use.** Exact feasibility for indivisible but repeatable capacity units.

<a id="c027"></a>

### C027 — The deficiency formula

**Claim.** Put d=max_{S⊆L}(|S|−|N(S)|). Then a maximum matching has size |L|−d.

**Proof.** Every matching leaves at least |S|−|N(S)| vertices of S unmatched, giving the upper bound. Since ∅ is permitted, d≥0. Add d new right vertices adjacent to all left vertices. Every nonempty S now has |N(S)|+d≥|S| neighbors. Hall gives a matching saturating L in the augmented graph. Deleting its at most d dummy edges leaves a matching of size at least |L|−d, attaining the bound.

**Dependencies/source.** C021. **Use.** Measures the exact shortfall, not merely whether a perfect assignment fails.

<a id="c028"></a>

### C028 — Doubly stochastic matrices decompose into permutations

**Claim.** Every nonnegative n×n real matrix with all row and column sums one is a convex combination of permutation matrices.

**Proof.** In the support graph, rows S send total mass |S| into neighboring columns, each of total mass one, so Hall holds. Choose a supported permutation P and let ε be the smallest selected entry. If ε=1 the matrix is P. Otherwise (A−εP)/(1−ε) is doubly stochastic with strictly fewer positive entries. Induct on the number of positive entries, and write A=εP+(1−ε)A'. The base case has one positive entry per row and is a permutation. For n=0 the unique empty matrix is itself the unique permutation matrix.

**Dependencies/source.** C021; Birkhoff–von Neumann theorem. **Use.** Realizes fractional assignments as lotteries over integral assignments.

<a id="c029"></a>

### C029 — Unique bipartite perfect matchings admit forced-edge peeling

**Claim.** A nonempty bipartite graph with a unique perfect matching has a left vertex of degree one. Recursively deleting its forced edge and endpoints characterizes uniqueness.

**Proof.** Label matched pairs (l_i,r_i). Make a directed graph on pairs with arc i→j whenever i≠j and l_i r_j is an edge. A directed cycle would give an alternating cycle, whose toggle gives a second perfect matching. Thus this directed graph is acyclic and has a sink; its left vertex has only its matched neighbor. Deleting this pair leaves a unique perfect matching, or a different one would extend to the original graph. Conversely a degree-one edge must lie in every perfect matching, so recursive success ending at the empty graph forces uniqueness.

**Dependencies/source.** Alternating cycles as in C022. **Use.** A short certificate that an allocation is forced.

<a id="c030"></a>

### C030 — Research conjecture: odd Latin squares have transversals

**Conjecture.** Every Latin square of odd order n has n cells meeting each row, each column and each symbol exactly once.

**Evidence, not a proof.** For the cyclic square L(i,j)=i+j modulo odd n, the diagonal cells (i,i) have distinct symbols 2i because multiplication by two is invertible. Near-transversals of size n−1, and the even-order variant of Ryser's conjecture, must not be confused with this full odd-order assertion.

**Dependencies/source.** Ryser's transversal conjecture; [historical formulation](https://arxiv.org/abs/1801.02893), [2026 near-spanning matching work](https://arxiv.org/abs/2609.11006). **Use/approach.** Three simultaneous uniqueness constraints exceed ordinary Hall matching; rainbow matching absorption is a possible route, not a proved completion.

## 4. Flows, cuts, orientation and transport

Directed networks are finite; capacities and lower bounds are nonnegative unless specified. A flow obeys conservation at internal vertices. Its value is net outflow at s. Residual edges include reverse edges with the negative of the original cost when costs are present.

<a id="c031"></a>

### C031 — Flow decomposes into paths and cycles

**Claim.** A nonnegative s–t flow with no edges into s or out of t is a nonnegative sum of s–t path flows and directed cycle flows. Integer flows admit integer coefficients. A nonnegative circulation decomposes into cycles.

**Proof.** Starting at a positive edge from s, follow positive edges. Conservation prevents stopping internally; reaching t gives a path, and repeating a vertex gives a cycle. Subtract the minimum flow along the obtained path or cycle. At least one positive edge disappears, so finitely many subtractions suffice. Once no positive edge leaves s, any remaining positive edge lies in a balanced circulation; the same traversal yields cycles. Each subtraction preserves conservation. If flows are integers, each minimum is an integer.

**Dependencies/source.** Direct finite elimination. **Use.** Converts algebraic transport into explicit routes and identifies cyclic waste.

<a id="c032"></a>

### C032 — Residual reachability certifies maximum flow

**Claim.** A feasible s–t flow is maximum if and only if its residual graph has no positive-capacity s–t path.

**Proof.** A residual path permits a positive bottleneck augmentation, so a maximum has none. Conversely let S be the vertices reachable from s residually when t is unreachable. Every original edge leaving S is saturated, and every original edge entering S has zero flow, because otherwise its reverse would allow reachability. Conservation gives flow value equal to the capacity leaving S. Every flow value is at most that cut capacity, so the given flow is maximum. This argument uses no termination assertion for real-capacity augmentation.

**Dependencies/source.** Flow conservation. **Use.** A sufficient cut certificate valid for real as well as integer data.

<a id="c033"></a>

### C033 — Integral max-flow/min-cut

**Claim.** With integer capacities, a maximum integer flow exists and its value equals the minimum cut capacity.

**Proof.** Start with zero flow. While a residual s–t path exists, augment by its integer bottleneck, increasing value by at least one. Value is bounded by the total capacity out of s, so this process terminates. The terminal flow is integral, and C032 supplies a cut of equal capacity. Every cut bounds every flow, proving both optimality statements.

**Dependencies/source.** C032. **Use.** Integer certificates for routing and packing.

<a id="c034"></a>

### C034 — Directed vertex Menger theorem

**Claim.** For distinct vertices s,t with no edge s→t, the maximum number of internally vertex-disjoint directed s–t paths equals the minimum number of internal vertices whose removal separates s from t.

**Proof.** First delete edges into s and out of t; they cannot belong to a simple s–t path, and their deletion does not change separation by internal vertices. Split each internal vertex v into v_in→v_out of capacity one. Replace original arcs by arcs between the appropriate split endpoints of capacity n, where n is the original vertex count. Removing all n−2 internal vertices separates s,t, so the minimum cut has capacity at most n−2 and uses no capacity-n arc. Such a cut consists of unit split arcs and gives a separating vertex set. Conversely any separating vertex set gives a cut of at most its size by removing its split arcs. C033 gives an integral maximum flow; C031 decomposes it into paths. Unit split capacities force distinct paths to use disjoint internal vertices. The reverse inequality follows because each path must meet any separator.

**Dependencies/source.** C031, C033. **Use.** Converts node-disjoint routing into ordinary capacity flow.

<a id="c035"></a>

### C035 — Lower-bounded circulation criterion

**Claim.** For integer bounds 0≤l_e≤u_e, a circulation with l_e≤f_e≤u_e exists exactly when l(δ⁻S)≤u(δ⁺S) for every vertex set S.

**Proof.** Necessity follows by summing conservation on S. For sufficiency put d(v)=l(δ⁻v)−l(δ⁺v), add a source edge of capacity d(v) when d(v)>0 and a sink edge of capacity −d(v) when d(v)<0, and give each original edge capacity u_e−l_e. Let D=Σ_{d>0}d. For a cut with original source-side vertices S, its capacity minus D equals u(δ⁺S)−l(δ⁻S), hence is nonnegative by hypothesis. C033 gives a flow saturating all added source edges and all sink edges. Its restriction g satisfies out(g)−in(g)=d, so f=l+g is the required integral circulation.

**Dependencies/source.** C033; Hoffman circulation criterion. **Use.** Exact feasibility with mandatory shipments as well as upper capacities.

<a id="c036"></a>

### C036 — Directed incidence matrices are totally unimodular

**Claim.** Every square submatrix of an oriented vertex–edge incidence matrix has determinant 0, 1 or −1.

**Proof.** Induct on its size. If a column has zero entries, the determinant is zero. If some column has exactly one nonzero entry, that entry is ±1 and cofactor expansion reduces to a smaller submatrix. Otherwise every column has both its original +1 and −1 entries among the selected rows; all row sums, viewed as a row-vector sum, are zero. The rows are dependent, so the determinant vanishes. The empty determinant is one.

**Dependencies/source.** Elementary determinant expansion. **Use.** Explains integrality of many network linear programs through a checkable matrix property.

<a id="c037"></a>

### C037 — Negative-cycle optimality for fixed-value flow

**Claim.** A feasible flow of fixed value and finite edge bounds has minimum linear cost exactly when its residual graph has no directed cycle of negative total cost.

**Proof.** A negative residual cycle permits a small feasible circulation augmentation that strictly lowers cost. Conversely compare with another feasible flow of the same value. On each edge, route the positive difference forward or the negative difference backward; the result is a nonnegative residual circulation, with exactly the cost difference. By the circulation part of C031 it is a nonnegative sum of directed cycles. If every such cycle has nonnegative cost, the comparison flow cannot be cheaper. Capacities ensure each difference uses an available residual edge.

**Dependencies/source.** C031. **Use.** Certifies minimum-cost routing without re-solving an optimization problem.

<a id="c038"></a>

### C038 — Tree metrics are sums of cut metrics

**Claim.** In a tree with nonnegative edge lengths, choose either component S_e of each edge deletion. Then d(x,y)=Σ_e l_e |1_{S_e}(x)−1_{S_e}(y)|. Thus, with positive lengths the tree metric embeds isometrically in a weighted ℓ¹ space; with zero lengths allowed the same holds for the metric quotient identifying points at zero distance.

**Proof.** There is one simple x–y path. An edge lies on it exactly when deleting that edge separates x from y, which is exactly when the displayed indicators differ. Summing the lengths of precisely those edges gives the identity. The coordinate map x↦(1_{S_e}(x))_e with coordinate weights l_e is the claimed embedding; zero-length edges yield a pseudometric unless they are contracted.

**Dependencies/source.** Unique-path tree property, independently proved in C041. **Use.** Reduces transport inequalities on trees to one-dimensional cuts.

<a id="c039"></a>

### C039 — Prescribed outdegrees have a cut criterion

**Claim.** An undirected graph admits an orientation with specified integer outdegrees d(v)≥0 exactly when Σ_v d(v)=|E| and Σ_{v∈S}d(v)≥|E(S)| for every S⊆V.

**Proof.** Necessity counts tails of edges internal to S. For sufficiency make a bipartite graph whose left objects are original edges and whose right objects are vertices, joining each edge to its endpoints. Demand one for every edge and capacity d(v) at v. For any edge family F with endpoint set S, |F|≤|E(S)|≤Σ_S d(v); thus C026 applies. Assign each edge a tail at its chosen endpoint. Since total capacity equals the number of assigned edges, every capacity is filled, giving exactly the prescribed outdegrees.

**Dependencies/source.** C026; Hakimi's orientation theorem. **Use.** A sufficient condition for balanced discrete load distribution.

<a id="c040"></a>

### C040 — Research conjecture: five even subgraphs double-cover edges

**Conjecture.** Every bridgeless graph has five, possibly empty or disconnected, even-degree spanning subgraphs such that each edge occurs in exactly two of them. “Even subgraph” does not mean a single simple cycle.

**Evidence, not a proof.** In a three-edge-colorable cubic graph, each color class is a perfect matching. The complements of the three classes are even 2-factors, and every edge belongs to exactly two; add two empty subgraphs. This proves that substantial special case. The ordinary cycle-double-cover assertion had proof announcements in July 2026; the bounded-five assertion is a stronger target, discussed as such in Zerafa's September work.

**Dependencies/source.** [Oum, 2026 exposition](https://arxiv.org/abs/2607.16356), [Zerafa, 2026](https://arxiv.org/abs/2609.28118). **Use/approach.** A bounded family of parity certificates for every bridgeless graph; perfect-matching and parity-flow methods are candidates, not a proof here.

## 5. Trees, cycle spaces and structural decompositions

<a id="c041"></a>

### C041 — Three equivalent tree certificates

**Claim.** For a nonempty graph on n vertices, being connected and acyclic, having a unique simple path between every pair, and being connected with n−1 edges are equivalent.

**Proof.** Connectivity gives paths, and two distinct simple paths produce a cycle by following them between their first divergence and next meeting. Conversely a cycle supplies two distinct paths. An acyclic connected graph with at least two vertices has a leaf: a longest simple path cannot be extended at an endpoint, and another neighbor there would produce a cycle. Deleting a leaf preserves connectivity and acyclicity, proving the n−1 count inductively. Finally a connected graph contains a spanning tree, obtained by deleting cycle edges while preserving connectivity. If it has only n−1 edges, the spanning tree uses all its edges and it is acyclic.

**Dependencies/source.** Elementary tree theory. **Use.** Interchange a structural, routing or cardinality certificate.

<a id="c042"></a>

### C042 — Fundamental cycles form a cycle-space basis

**Claim.** Over F₂, the even-degree edge subsets of a graph with n vertices, m edges and c components form a vector space of dimension m−n+c. For any spanning forest, the fundamental cycles of its nonforest edges are a basis.

**Proof.** Symmetric difference preserves parity, giving a vector space. Each nonforest edge closes one unique path in its forest component. Its fundamental cycle contains that nonforest edge and no other, proving independence. Given any even edge subset, add these cycles to cancel all its nonforest edges. The remainder is an even edge subset of a forest; if nonempty, its own forest has a degree-one vertex, contradicting evenness. Thus the cycles span. The spanning forest has n−c edges by C041, giving the dimension.

**Dependencies/source.** C041. **Use.** A complete independent set of parity constraints and cycle coordinates.

<a id="c043"></a>

### C043 — Cut and cycle spaces are orthogonal complements

**Claim.** In F₂^E, the cut space is the orthogonal complement of the even-degree cycle space. Its dimension is n−c.

**Proof.** Every even-degree edge subset meets every cut evenly, by summing degrees on one side; hence the spaces are orthogonal. Vertex cuts generate all cuts because δS is the symmetric sum of the singleton cuts for vertices in S. Their only linear relations are sums over whole connected components: a sum indexed by S is zero exactly when no edge crosses S. Therefore their span has dimension n−c. C042 gives cycle-space dimension m−n+c; the dimensions sum to m, so orthogonal containment is equality.

**Dependencies/source.** C042. **Use.** Converts all cycle-parity tests into a cut representation.

<a id="c044"></a>

### C044 — Euler tours from parity

**Claim.** A graph with at least one edge has a closed trail using every edge once exactly when all nonisolated vertices lie in one component and all degrees are even.

**Proof.** A closed edge-using trail enters and leaves every vertex equally often, proving necessity. For sufficiency follow unused edges until unable to continue. Even degree prevents stopping away from the starting vertex, so this produces a closed trail. If unused edges remain, connectivity of the nonisolated part provides a vertex of the current trail incident to an unused edge: take the first unused edge on a path from the trail to an unused edge. Starting there gives another closed trail, which can be spliced into the first. Each splice uses additional edges, so finiteness yields an Euler tour.

**Dependencies/source.** Direct Hierholzer construction. **Use.** Turns local parity into one global traversal.

<a id="c045"></a>

### C045 — Every tree has a balanced separator vertex

**Claim.** A tree on n≥1 vertices has a vertex whose deletion leaves components of size at most n/2.

**Proof.** Choose a vertex v minimizing Φ(v)=Σ_x d(v,x), with unweighted distances. If a component C of T−v attached through neighbor u has more than n/2 vertices, moving from v to u decreases each distance to C by one and increases each other distance by one. Thus Φ(u)−Φ(v)=n−2|C|<0, contradicting minimality. Hence no component is too large.

**Dependencies/source.** C041. **Use.** A recursive divide-and-conquer separator with a guaranteed balance ratio.

<a id="c046"></a>

### C046 — Diameter determines the radius of a tree

**Claim.** A tree of diameter D has radius ⌈D/2⌉, attained by either middle vertex of a diametral path.

**Proof.** Any vertex has maximum distance to the two diametral endpoints at least ⌈D/2⌉ by the triangle inequality. Write the endpoints a,b as positions 0,D on their path, and choose middle position m=⌊D/2⌋. A vertex v reaches the path first at position x, with off-path distance h. Since neither d(v,a) nor d(v,b) exceeds D, h≤min(x,D−x). Therefore h+|x−m|≤max(m,D−m)=⌈D/2⌉. This bounds every distance from m and proves equality. Reflecting the path gives the other middle vertex when D is odd.

**Dependencies/source.** C041. **Use.** Exact worst-case access points for tree transport.

<a id="c047"></a>

### C047 — Prüfer coding and Cayley's count

**Claim.** Labelled trees on {1,…,n}, n≥2, correspond bijectively to words of length n−2 over these labels; consequently there are n^{n−2} trees.

**Proof.** Repeatedly delete the smallest labelled leaf and record its neighbor, stopping with two vertices. To decode a word, repeatedly select the smallest currently available label absent from the remaining word, join it to the first word symbol, delete that label and symbol, then join the final two labels. Such an absent label always exists because the number of available labels exceeds the word length by two. In the decoding tree, a label's degree equals one plus its number of remaining occurrences: each occurrence supplies one incident edge, and its final removal or final join supplies the last. Thus the selected absent label is exactly the smallest leaf. Encoding and decoding reverse each step, proving bijectivity and the count.

**Dependencies/source.** C041; Prüfer's classical code. **Use.** Uniform tree generation and exact counting.

<a id="c048"></a>

### C048 — The matrix-tree determinant

**Claim.** For a connected graph, deleting any row and corresponding column of its Laplacian gives a determinant equal to its number of spanning trees.

**Proof.** Orient edges arbitrarily, form the incidence matrix B and delete the chosen vertex row, obtaining B'. The reduced Laplacian is B'B'ᵀ. The Cauchy–Binet expansion gives det(B'B'ᵀ)=Σ_{|S|=n−1}det(B'_S)²: this identity follows by multilinearly expanding the determinant in columns, with repeated selected columns cancelling by alternation and the distinct selections grouping into the two determinants. If S is a tree, successive leaf expansion, leaving the deleted vertex as root, gives determinant ±1. If S contains a cycle, its incidence columns are dependent; if it is disconnected, the component row sums give deficient rank. By C041 these exhaust the non-trees of size n−1. Thus each tree contributes one and each other subset zero.

**Dependencies/source.** C041, elementary determinant algebra. **Use.** Counts global connected structures by one local matrix determinant.

<a id="c049"></a>

### C049 — Degeneracy yields a forest decomposition

**Claim.** If every nonempty subgraph has a vertex of degree at most k, the edge set can be partitioned into k forests.

**Proof.** Repeatedly delete a vertex of current degree at most k. In this deletion order each vertex has at most k later neighbors. Orient edges from earlier to later and assign distinct colors 1,…,k to the outgoing edges of each vertex. A monochromatic cycle would have an earliest vertex; both its cycle edges would be outgoing and have the same color, contradicting the assignment. Thus every color class is acyclic. For k=0 the graph has no edges and the partition is empty.

**Dependencies/source.** Direct ordering construction. **Use.** Decomposes sparse interactions into independently routable acyclic layers.

<a id="c050"></a>

### C050 — Research conjecture: every tree is graceful

**Conjecture.** Every tree with m edges admits a bijective vertex labeling by {0,…,m} for which its edge absolute differences are {1,…,m}.

**Evidence, not a proof.** A star is labelled with center zero and leaf labels 1,…,m. For a path, label consecutive vertices 0,m,1,m−1,2,m−2,…; consecutive absolute differences are m,m−1,…,1. Thus stars and paths satisfy the conjecture. Approximate results giving almost all distinct differences do not prove the exact labeling assertion.

**Dependencies/source.** Graceful tree conjecture; [Letzter–Pokrovskiy–Williams, 2025](https://arxiv.org/abs/2511.11331). **Use/approach.** Exact difference decompositions and graph embeddings; an approach must preserve both the permutation constraint and all distinct differences.

## 6. Extremal graph and incidence tools

<a id="c051"></a>

### C051 — Mantel's triangle-free bound

**Claim.** A triangle-free graph on n vertices has at most n²/4 edges.

**Proof.** For an edge uv, the neighborhoods N(u),N(v) are disjoint, so d(u)+d(v)≤n. Sum over edges to obtain Σ_v d(v)²≤ne. Cauchy–Schwarz and Σ_v d(v)=2e give 4e²≤nΣ_v d(v)²≤n²e. If e>0, divide by e; the zero-edge case is immediate. Balanced complete bipartite graphs show the integer-rounded bound is sharp.

**Dependencies/source.** Degree counting. **Use.** A local forbidden pattern forces a global sparsity certificate.

<a id="c052"></a>

### C052 — Motzkin–Straus weighted clique bound

**Claim.** If a nonempty graph has clique number at most r≥1 and x_v≥0 with Σ_v x_v=1, then Σ_{uv∈E}x_u x_v≤(r−1)/(2r).

**Proof.** Choose a maximizing vector on the compact simplex with minimum support. If two support vertices u,v are nonadjacent, their mutual product does not occur. Holding x_u+x_v fixed makes the objective linear in x_u, so moving all their mass to one endpoint can only increase the objective and reduces support, a contradiction. The support is therefore a clique of size q≤r. On that clique the objective equals (1−Σ_v x_v²)/2≤(1−1/q)/2≤(r−1)/(2r). This also covers q=1.

**Dependencies/source.** Direct mass transfer; Motzkin–Straus theorem. **Use.** A continuous certificate for forbidden-clique edge bounds and relaxations.

<a id="c053"></a>

### C053 — Caro–Wei independent-set bound

**Claim.** Every graph has an independent set of size at least Σ_v 1/(d(v)+1).

**Proof.** Choose a uniform random ordering of the vertices. Retain v if it precedes all its neighbors. Two adjacent vertices cannot both be retained, so the retained set is independent. Each vertex is first in its closed neighborhood with probability 1/(d(v)+1). Linearity of expectation gives the displayed expected size, so at least one ordering attains it or more.

**Dependencies/source.** Finite averaging. **Use.** Degree-sensitive packing beyond a maximum-degree estimate.

<a id="c054"></a>

### C054 — A quantitative triangle supersaturation bound

**Claim.** A graph on n>0 vertices with e edges has at least e(4e−n²)/(3n) triangles. A negative right side is merely a vacuous lower bound.

**Proof.** Every edge uv has at least d(u)+d(v)−n common neighbors by inclusion–exclusion. Summing common-neighbor counts over edges counts each triangle three times, so 3t≥Σ_v d(v)²−ne. Cauchy–Schwarz bounds the first term below by 4e²/n. Rearrangement yields the claim.

**Dependencies/source.** Same degree identity as C051, now retaining the defect. **Use.** Turns excess density into a guaranteed supply of witnesses.

<a id="c055"></a>

### C055 — A K₂,t incidence bound

**Claim.** For n≥1, if no two distinct vertices have t common neighbors, where t≥1, then e≤(n/4)[1+√(1+4(t−1)(n−1))].

**Proof.** Count pairs of neighbors centered at each vertex. Each unordered pair can occur as neighbors of at most t−1 centers, so Σ_v binom(d(v),2)≤(t−1)binom(n,2). Meanwhile Σ d(v)²≥4e²/n for n>0. Thus 4e²/n−2e≤(t−1)n(n−1), a quadratic whose nonnegative root gives the formula. The empty graph on zero vertices satisfies it separately.

**Dependencies/source.** Double counting and Cauchy–Schwarz. **Use.** Controls dense incidence systems with bounded pair multiplicity.

<a id="c056"></a>

### C056 — Dependent random choice with explicit parameters

**Claim.** In a bipartite graph with |A|=N>0, |B|=M>0 and average degree d on A, for positive integers t,r,m there is U⊆A of size at least N(d/M)^t−binom(N,r)(m/M)^t such that every r-subset of U has at least m common neighbors in B.

**Proof.** Choose t independent uniform vertices of B, allowing repetition, and let X be their common neighborhood in A. Then E|X|=Σ_a(deg(a)/M)^t≥N(d/M)^t by convexity. An r-set with fewer than m common neighbors lies in X with probability at most (m/M)^t. Hence the expected number Y of such bad r-sets in X is at most the second term. Some sample has |X|−Y at least the claimed difference. Delete one vertex from each bad set still present. At most Y deletions occur and no new bad subset is created, giving U.

**Dependencies/source.** Finite expectation and convex power inequality. **Use.** Produces a large subset with uniform common-neighborhood guarantees.

<a id="c057"></a>

### C057 — Erdős–Szekeres monotone subsequences

**Claim.** For positive integers r,s, any sequence of rs+1 distinct real numbers has an increasing subsequence of length r+1 or a decreasing subsequence of length s+1.

**Proof.** At each position i record the pair (a_i,b_i), the largest lengths of increasing and decreasing subsequences ending there. For i<j, either the value at i is smaller, implying a_j>a_i, or larger, implying b_j>b_i. Thus all pairs are distinct. If neither claimed subsequence existed, all pairs would lie in {1,…,r}×{1,…,s}, which has only rs elements, a contradiction.

**Dependencies/source.** Pigeonhole principle. **Use.** Extracts ordered structure from arbitrary data without probabilistic hypotheses.

<a id="c058"></a>

### C058 — The binomial Ramsey bound

**Claim.** Every graph with at least binom(s+t−2,s−1) vertices contains a clique of size s or an independent set of size t, for s,t≥1.

**Proof.** The case s=1 or t=1 is immediate. At a vertex v, if it has at least binom(s+t−3,s−2) neighbors, induction on (s−1,t) gives either an independent t-set or a clique of size s−1 which extends by v. Otherwise Pascal's identity shows v has at least binom(s+t−3,s−1) nonneighbors. Induction on (s,t−1) gives either a clique of size s or an independent set of size t−1 extending by v. This proves the bound inductively.

**Dependencies/source.** Elementary Ramsey recursion. **Use.** An explicit finite threshold for homogeneous substructures.

<a id="c059"></a>

### C059 — Packing supplies a hitting-set certificate

**Claim.** In an r-uniform hypergraph with r≥1, if ν is the largest disjoint-edge packing and τ the smallest vertex set meeting every edge, then ν≤τ≤rν.

**Proof.** Every hitting set must meet each edge of a disjoint packing in a different vertex, proving the first inequality. Choose a maximum packing and take the union of its edges, of size rν. An edge missing that union could be added disjointly, contradicting maximality. The union therefore hits all edges and proves the upper bound. The same construction works with any maximal packing, although its size need not be ν.

**Dependencies/source.** Direct certificate construction. **Use.** A universal approximation guarantee; applied to triangle edges it gives τ≤3ν.

<a id="c060"></a>

### C060 — Research conjecture: Tuza's factor two

**Conjecture.** In every graph, the minimum number τ of edges meeting all triangles is at most twice the maximum number ν of edge-disjoint triangles.

**Evidence, not a proof.** C059 gives the weaker factor three by viewing triangles as a 3-uniform hypergraph on graph edges. In K₄ any two triangles share an edge, so ν=1. Two opposite edges hit all four triangles, while one edge misses a triangle; hence τ=2 and the proposed factor is sharp. Dense-graph partial results and the 2026 claimed universal bound 165/59 do not imply the factor-two assertion.

**Dependencies/source.** [Chahua–Gutiérrez, 2024](https://arxiv.org/abs/2405.11409), [Wang, September 2026](https://arxiv.org/abs/2609.13831). **Use/approach.** Sharper removal certificates for triangles; exploiting the overlap geometry of graph triangles is necessary beyond arbitrary 3-uniform hitting sets.

## 7. Set families, compression and order

<a id="c061"></a>

### C061 — The LYM inequality for antichains

**Claim.** If F⊆2^[n] contains no two distinct comparable sets, then Σ_{A∈F}1/binom(n,|A|)≤1.

**Proof.** A uniform random permutation generates the maximal chain of its successive initial sets. A given k-set occurs on this chain with probability k!(n−k)!/n!=1/binom(n,k). A chain meets an antichain at most once. Taking the expected number of F-members on the random chain proves the inequality. The empty ground set has one possible chain and satisfies the same formula.

**Dependencies/source.** Inspected `Mathlib.Combinatorics.SetFamily.LYM`; Lubell–Yamamoto–Meshalkin inequality. **Use.** A level-sensitive counting certificate stronger than a single maximum-layer bound.

<a id="c062"></a>

### C062 — Bollobás's set-pairs inequality

**Claim.** Suppose finite pairs (A_i,B_i) satisfy A_i∩B_i=∅ and A_i∩B_j≠∅ for all distinct i,j. Then Σ_i 1/binom(|A_i|+|B_i|,|A_i|)≤1.

**Proof.** Uniformly order the union of all sets. Let E_i be the event that every member of A_i precedes every member of B_i. Its probability is the displayed reciprocal. For i≠j choose x∈A_i∩B_j and y∈A_j∩B_i. These are distinct because A_i and B_i are disjoint. Event E_i forces x before y, whereas E_j forces y before x. Hence the events are disjoint, and their probabilities sum to at most one. Empty individual sets create no problem: the cross-intersection hypothesis then permits at most one pair.

**Dependencies/source.** Direct permutation proof; Bollobás's inequality. **Use.** Bounds irredundant witnesses with crossed incompatibility conditions.

<a id="c063"></a>

### C063 — Sauer–Shelah counting

**Claim.** If F⊆2^[n] shatters no set larger than d≥0, then |F|≤Σ_{i=0}^{min(d,n)}binom(n,i). Shattering Y means every subset of Y occurs as A∩Y for some A∈F.

**Proof.** Split F at coordinate n, writing its two trace families as F₀,F₁ on [n−1]. Put U=F₀∪F₁ and I=F₀∩F₁. Then |F|=|U|+|I|. Every set shattered by U is shattered by F, while a set Y shattered by I yields Y∪{n} shattered by F. Thus their dimensions are at most d and d−1. Apply induction and Pascal's identity. For d=0, I is empty because any nonempty family shatters ∅; the same recurrence works with the bound for dimension −1 defined as zero. The n=0 base is immediate.

**Dependencies/source.** Inspected `SetFamily.Shatter`, especially `card_le_card_shatterer`; Sauer–Shelah lemma. **Use.** Converts a local pattern restriction into a global sample-space bound.

<a id="c064"></a>

### C064 — Down-compression preserves size without creating shattered sets

**Claim.** At coordinate i, replace A containing i by A−i only when A−i is absent. This preserves family size and creates no new shattered set. Repeated coordinate compressions eventually produce a downset of the same size and no larger VC dimension.

**Proof.** Partition the cube into pairs (B,B+i). Compression changes only a singleton upper member to the lower member, preserving cardinality. For Y not containing i, traces on Y are unchanged. If Y contains i and is shattered after compression, every upper trace on Y is witnessed by an upper set that survived; survival means its lower partner was also originally present. These partners witness both traces in the original family for every trace on Y−i. Thus original shattering follows. Every nontrivial compression strictly decreases the sum of member sizes, so the process terminates; stability at every coordinate is exactly downward closure.

**Dependencies/source.** Inspected `Shatters.of_compression`. **Use.** Simplifies a family while preserving an upper-bound obstruction.

<a id="c065"></a>

### C065 — The factorial sunflower bound

**Claim.** For integers k≥1,r≥2, a family of distinct k-sets of size greater than k!(r−1)^k contains r sets whose pairwise intersections all equal one common core.

**Proof.** Induct on k. For k=1 any r distinct singletons suffice. Choose a maximal disjoint subfamily. If it has at least r members, take r with empty core. Otherwise its union U has at most k(r−1) elements and meets every family member. Some x∈U belongs to at least |F|/[k(r−1)]>(k−1)!(r−1)^{k−1} members. Deleting x from those members gives that many distinct (k−1)-sets. Induction supplies r with a common pairwise-intersection core; restoring x adjoins x to that core. The k=1 case avoids invoking zero-uniform families.

**Dependencies/source.** Erdős–Rado sunflower lemma; [Rao's primary survey](https://arxiv.org/abs/2509.14790). **Use.** Extracts repeated overlap structure from a large uniform family, without relying on any stronger sunflower conjecture.

<a id="c066"></a>

### C066 — Erdős–Ko–Rado via cyclic intervals

**Claim.** If n≥2k≥2 and an intersecting family F consists of k-subsets of [n], then |F|≤binom(n−1,k−1).

**Proof.** First, in a fixed cyclic order at most k pairwise-intersecting intervals of length k can occur. If any occurs, rotate so one ends at position n. Intervals ending at k,…,n−k are disjoint from it and excluded. The remaining candidates, besides the chosen interval, pair as endpoints i and i+n−k for i=1,…,k−1; the intervals in each pair are disjoint, so at most one can be selected. This proves the interval bound. In a uniform random cyclic order, each fixed k-set is an interval with probability n/binom(n,k), by symmetry and the n distinct intervals. Expected interval members of F are therefore |F|n/binom(n,k)≤k. Rearranging gives the claim.

**Dependencies/source.** Katona's circle method; inspected `SetFamily.Intersecting` as a source hook, not a replay. **Use.** Sharp packing under pairwise intersection.

<a id="c067"></a>

### C067 — Dilworth's chain decomposition

**Claim.** A finite poset's largest antichain size equals the least number of chains partitioning its elements.

**Proof.** For n elements form two copies of the poset with edge x_L y_R when x<y. A matching of size k links elements into directed paths: each vertex has at most one successor and predecessor, and strict order forbids cycles. These paths partition the poset into n−k chains. Conversely any partition into q chains gives n−q matching edges by joining consecutive elements. Let k be maximum. By C023 a vertex cover of size k exists. Elements neither of whose copies lies in that cover form an antichain, since a comparable pair would yield an uncovered edge; at least n−k elements remain. Every antichain meets each chain at most once, so its size is also at most n−k. Equality follows.

**Dependencies/source.** C023. **Use.** Exact equivalence between parallel decomposition and obstruction size.

<a id="c068"></a>

### C068 — Mirsky's antichain decomposition

**Claim.** A finite poset of maximum chain size h can be partitioned into h antichains, and fewer are impossible.

**Proof.** Assign to each element x the maximum size ρ(x) of a chain ending at x. If x<y, a longest chain ending at x extends by y, so ρ(y)>ρ(x). Each level {x:ρ(x)=i} is therefore an antichain. Ranks lie between one and h, giving the partition. A chain of size h requires h distinct antichain parts, proving minimality. The empty poset uses zero parts.

**Dependencies/source.** Direct rank construction. **Use.** A layering certificate complementary to C067's chain partition.

<a id="c069"></a>

### C069 — Harris positive correlation

**Claim.** For independent Bernoulli coordinates and increasing real functions f,g on their finite product cube, E(fg)≥Ef·Eg.

**Proof.** Induct on the coordinate count. Condition on the final coordinate Z. The conditional covariance is nonnegative by induction. The functions F(z)=E(f|Z=z), G(z)=E(g|Z=z) are increasing because the remaining coordinates have the same distribution in both conditions. Their covariance is p(1−p)[F(1)−F(0)][G(1)−G(0)]≥0. Expanding E(fg)−EfEg into expected conditional covariance plus Cov(F(Z),G(Z)) proves the claim. The zero-coordinate case has constant functions.

**Dependencies/source.** Direct conditioning proof; Harris inequality. **Use.** Justifies correlation lower bounds without assuming independent events.

<a id="c070"></a>

### C070 — Research conjecture: a sharp inertia certificate for every downset

**Conjecture.** Let D⊆2^[n] be a downset containing a nonempty set, and s=max_i |{A∈D:i∈A}|. There exists a real symmetric matrix M indexed by D, with M_AB=0 whenever A∩B≠∅, having exactly s nonnegative eigenvalues, counted with multiplicity. Negative and zero entries on allowed disjoint pairs are permitted; the empty-set diagonal is allowed.

**Evidence, not a proof.** For D=2^[n], n≥1, take the complement-permutation matrix M_AB=1 if B=[n]\A and zero otherwise. Complementation has disjoint two-element orbits; each block has eigenvalues +1,−1. Thus exactly 2^{n−1}=s eigenvalues are nonnegative. The authors report many further tested downsets. This is their new spectral Conjecture I, not the older downset intersecting-family conjecture for which their paper gives a proof.

**Dependencies/source.** [Ellis–Filmus–Friedgut, 2026, §4](https://arxiv.org/html/2609.28404v1). **Use/approach.** Sharp spectral upper certificates for intersecting families; construct disjointness-supported matrices with controlled inertia. No general construction is supplied here.

## 8. Polynomial grids and finite-field existence

<a id="c071"></a>

### C071 — Root counting over a field

**Claim.** A nonzero univariate polynomial of degree d over a field has at most d distinct roots.

**Proof.** Induct on d. A nonzero constant has none. If a is a root, division by X−a gives P=(X−a)Q with deg Q=d−1. Every different root b satisfies (b−a)Q(b)=0, hence Q(b)=0 in a field. Induction bounds the other roots by d−1. If P has no root there is nothing to show.

**Dependencies/source.** Polynomial division; classical root bound. **Use.** The induction base behind finite-grid interpolation and randomized identity tests.

<a id="c072"></a>

### C072 — Lagrange interpolation with its leading coefficient

**Claim.** For distinct field elements S, |S|=t+1, every polynomial of degree at most t satisfies P(X)=Σ_{a∈S}P(a)∏_{b∈S−a}(X−b)/(a−b). In particular [X^t]P=Σ_{a∈S}P(a)/∏_{b≠a}(a−b).

**Proof.** Each displayed basis polynomial equals one at its designated point and zero at all others. The difference between the two sides has degree at most t and at least t+1 roots, so is zero by C071. Taking the coefficient of X^t yields the formula. Nonzero denominators are invertible because the points are distinct.

**Dependencies/source.** C071; Lagrange interpolation. **Use.** Explicit coefficient certificates from finite evaluation tables.

<a id="c073"></a>

### C073 — Product-grid unisolvence

**Claim.** Let nonempty finite subsets S_i of a field be given. A multivariate polynomial with individual degree in X_i less than |S_i| that vanishes on ∏S_i is the zero polynomial.

**Proof.** Induct on the number of variables. Write the polynomial as a polynomial in its last variable with coefficient polynomials in the others. For every fixed choice of the first variables from their grids, the resulting last-variable polynomial has too many roots by C071, so all its coefficients evaluate to zero. Each coefficient obeys the remaining individual degree bounds, and induction makes every coefficient polynomial zero. With zero variables, the grid is a singleton and the assertion concerns a constant.

**Dependencies/source.** C071; inspected `MvPolynomial.eq_zero_of_eval_zero_at_prod_finset`. **Use.** A finite deterministic identity certificate when individual degree bounds are known.

<a id="c074"></a>

### C074 — Coefficient formula and combinatorial Nullstellensatz

**Claim.** If deg P≤Σ_i t_i and |S_i|=t_i+1, then [∏X_i^{t_i}]P=Σ_{x∈∏S_i}P(x)/∏_i∏_{a∈S_i−x_i}(x_i−a). Thus a nonzero indicated coefficient forces a nonzero grid evaluation.

**Proof.** Both sides are linear in P, so check a monomial X^k with total degree at most Σt_i. The right side factors into univariate evaluation functionals from C072. If k=t, every factor equals one. Otherwise some k_i<t_i, unless all coordinates are at least their targets, which would violate the total degree bound. For that coordinate C072 says its functional is zero; hence the product is zero, as is the target coefficient. This proves the identity for every monomial and therefore P. If all grid evaluations vanished, its right side would be zero.

**Dependencies/source.** C072; [Alon's combinatorial Nullstellensatz](https://www.tau.ac.il/~nogaa/PDFS/null2.pdf), inspected `combinatorial_nullstellensatz_exists_eval_nonzero`. **Use.** Converts an explicit coefficient into a universal finite existence certificate.

<a id="c075"></a>

### C075 — Schwartz–Zippel identity testing

**Claim.** For a nonzero polynomial P of total degree d and independent uniform variables in a nonempty field subset S of size q, Pr(P=0)≤d/q.

**Proof.** Induct on variable count. Let k be the degree in the last variable and Q its nonzero leading coefficient; deg Q≤d−k. The induction hypothesis bounds the probability Q vanishes at the other variables by (d−k)/q. Conditional on a specialization with Q nonzero, C071 bounds the final-variable zero probability by k/q. The total probability is at most their sum; bounds above one remain valid upper bounds. A nonzero constant has zero failure probability.

**Dependencies/source.** C071. **Use.** Quantified soundness for randomized polynomial checks.

<a id="c076"></a>

### C076 — Minimum support on a product grid

**Claim.** If P≠0 has individual degrees at most d_i<|S_i|, then it is nonzero at at least ∏_i(|S_i|−d_i) grid points.

**Proof.** Induct on variables. The leading coefficient in the last variable, of actual degree k≤d_n, is a nonzero polynomial obeying the other individual bounds. By induction it is nonzero on at least ∏_{i<n}(|S_i|−d_i) choices. At each such choice, C071 leaves at least |S_n|−k≥|S_n|−d_n nonzero evaluations. Multiplying gives the bound. A nonzero constant on a zero-variable grid has support one, the empty product.

**Dependencies/source.** C071. **Use.** Robustness: a bounded-degree nonzero polynomial cannot hide at just a few grid points.

<a id="c077"></a>

### C077 — Chevalley–Warning divisibility

**Claim.** For polynomials f₁,…,f_r over F_p with Σ_j deg f_j<n, the number of their common zeros in F_p^n is divisible by p. Zero polynomials may be omitted.

**Proof.** Modulo p, the zero count equals Σ_{x∈F_p^n}∏_j(1−f_j(x)^{p−1}), since each factor is one exactly when its value is zero. Here c^{p−1}=1 for c≠0 follows by multiplying all elements of F_p^×: multiplication by c permutes them, so cancelling their nonzero product proves the identity. Every expanded monomial has total degree less than n(p−1), so some coordinate exponent is less than p−1. Summing that coordinate gives zero in F_p: exponent zero sums p ones; for 1≤a<p−1, choose c∈F_p^× with c^a≠1, which exists by C071, and scaling the power sum forces it to vanish. Thus each monomial's full sum is zero. The zero count is zero modulo p.

**Dependencies/source.** C071 and Fermat's theorem in F_p. **Use.** Produces nontrivial solutions when a known trivial solution prevents a zero count.

<a id="c078"></a>

### C078 — Hyperplanes cannot cheaply cover a punctured grid

**Claim.** Let nonempty field subsets S_i and a distinguished x*∈∏S_i be given. If affine hyperplanes cover every grid point except x* and none contains x*, their number is at least Σ_i(|S_i|−1).

**Proof.** Multiply their defining nonzero affine linear forms to get P. It is zero at all grid points except x*, and P(x*)≠0. If fewer hyperplanes than the claimed lower bound occurred, deg P<Σ_i t_i for t_i=|S_i|−1, so its target coefficient in C074 would be zero. But that formula's sum has just one nonzero term, at x*, with nonzero denominator, a contradiction. For a singleton grid the lower bound zero is automatic.

**Dependencies/source.** C074. **Use.** Lower bounds for affine obstruction covers from one exceptional feasible point.

<a id="c079"></a>

### C079 — Prime-order Erdős–Ginzburg–Ziv

**Claim.** Among any 2p−1 integers, p prime, there are p whose sum is divisible by p.

**Proof.** Reduce the integers to a_i∈F_p. On 2p−1 variables impose Σ_i X_i^{p−1}=0 and Σ_i a_i X_i^{p−1}=0. The degree sum is at most 2(p−1)<2p−1, so C077 makes the common-zero count divisible by p. A solution's support size is a multiple of p and lies between zero and 2p−1, so is either zero or p. For each p-subset of indices with zero coefficient sum, exactly (p−1)^p solutions have that support. Thus the count is 1+(p−1)^p N, where N is the number of desired subsets. Since (p−1)^p≡−1 mod p, including p=2, divisibility gives N≡1 mod p. Hence N>0.

**Dependencies/source.** C077. **Use.** An exact-size zero-sum selection theorem.

<a id="c080"></a>

### C080 — Research conjecture: Alon–Tarsi Latin parity

**Conjecture.** For every positive even n, the signed sum over all Latin squares of order n is nonzero, where a square's sign is the product of the signs of all its row permutations and all its column permutations, using fixed ordered row, column and symbol labels.

**Evidence, not a proof.** At n=2 there are exactly two Latin squares. In either square the product of row signs is −1 and the product of column signs is −1, so both have sign +1 and the sum is two. C074 illustrates why nonzero combinatorial coefficients are useful; it does not prove this particular coefficient is nonzero. Asymptotic cancellation estimates also do not settle the required nonvanishing.

**Dependencies/source.** [Alpoge's primary parity work](https://arxiv.org/abs/1412.7574), [2026 seminar on the conjecture](https://math.ucsd.edu/seminar/alon-tarsi-conjecture-sun-matrix-integrals). **Use/approach.** Exact signed enumeration, potentially via matrix integrals or coefficient identities. No general parity computation is supplied.

## 9. Enumeration, incidence symmetries and spectral counting

This section combines exact enumeration under partial orders and group actions with incidence, orthogonality and Fourier certificates. In C084 blocks are actual subsets, rather than duplicate labels.

<a id="c081"></a>

### C081 — Möbius inversion on a finite poset

**Claim.** For a finite poset P define μ(x,x)=1 and, for x<y, μ(x,y)=−Σ_{x<z≤y}μ(z,y). If f(x)=Σ_{y≤x}g(y), then g(x)=Σ_{y≤x}μ(y,x)f(y). These two transformations are inverse over any commutative coefficient ring.

**Proof.** The recursion is well founded on interval size and implies Σ_{x≤z≤y}μ(z,y)=1 when x=y and zero otherwise. Substituting f into the proposed recovered value gives Σ_{z≤x}g(z)Σ_{z≤y≤x}μ(y,x)=g(x). Thus the proposed transformation is a left inverse. Independently, summation f(x)=Σ_{y≤x}g(y) has a unique solution for any f: choose a linear extension of the finite poset and set g(x)=f(x)−Σ_{y<x}g(y). Hence the left inverse is the actual inverse, proving both directions without division.

**Dependencies/source.** [Rota's incidence-algebra foundations](https://webhomes.maths.ed.ac.uk/~v1ranick/papers/rota1.pdf). **Use.** Recovers exact-type counts from cumulative counts, including inclusion–exclusion on a subset poset.

<a id="c082"></a>

### C082 — Cauchy–Frobenius orbit counting

**Claim.** If a finite group G acts on a finite set X, the number of orbits is |G|⁻¹Σ_{g∈G}|Fix(g)|.

**Proof.** Count pairs (g,x) with gx=x first by g, giving the numerator, and then by x, giving Σ_x |Stab(x)|. For an orbit O, the map G→O sending g to gx is surjective, and its fibers are cosets of Stab(x), all of equal size. Thus |O||Stab(x)|=|G|. Stabilizer sizes are constant along the orbit by conjugation, so its contribution to the second count is exactly |G|. Summing over orbits and dividing proves the formula. The group is nonempty even if X is empty, in which case both counts are zero.

**Dependencies/source.** Classical Cauchy–Frobenius–Burnside lemma; the same weighted counting underlies [Pólya's primary enumeration paper](https://doi.org/10.1007/BF02546665). **Use.** Counts symmetry classes by fixed configurations without choosing representatives.

<a id="c083"></a>

### C083 — Pólya's weighted cycle-index formula

**Claim.** Let a finite group G permute a finite position set Ω and let colors be 1,…,k with k≥1. For each orbit O of colorings c:Ω→{1,…,k}, assign its invariant monomial w(O)=∏_{u∈Ω}t_{c(u)}. Then Σ_O w(O)=|G|⁻¹Σ_{g∈G}∏_{cycles C of g}(Σ_{a=1}^k t_a^{|C|}), as a polynomial with rational coefficients.

**Proof.** A coloring fixed by g is constant on each cycle of g. Summing its monomial over fixed colorings therefore factors as the product on the right. Average these fixed-coloring monomials over G and interchange the finite sums. For one coloring orbit, its monomial is constant and its total multiplicity is Σ_{c∈O}|Stab(c)|=|G| by C082's orbit–stabilizer calculation. Dividing by |G| leaves exactly one copy of that monomial, proving the polynomial identity. Consequently each coefficient counts coloring orbits with prescribed color multiplicities, not merely the total number of orbits.

**Dependencies/source.** C082; [Pólya, 1937](https://doi.org/10.1007/BF02546665). **Use.** Enumerates unlabeled patterns while retaining exact composition data through the full cycle index.

<a id="c084"></a>

### C084 — Incidence automorphisms are determined by their point action

**Claim.** If blocks are actual subsets of the point set, every incidence-preserving pair of point and block permutations is uniquely determined by its point permutation. A point permutation extends exactly when it permutes the block family.

**Proof.** Let σ be the point permutation and τ the block permutation. Incidence preservation says σ(x)∈τ(B) exactly when x∈B. Because σ is bijective, this forces τ(B)=σ[B] as subsets, proving uniqueness. Conversely if B↦σ[B] permutes the family, use this map for τ; the displayed incidence equivalence follows immediately, and its inverse is induced by σ⁻¹. Distinct labelled copies of the same subset would invalidate uniqueness, so the actual-subset hypothesis is essential.

**Dependencies/source.** Inspected project declarations `pointHom_injective`, `pointHom_surjective`, `incidenceMulEquivPointAut` in `Mathproof/IncidenceDesignAutomorphisms.lean`. **Use.** Removes a redundant symmetry coordinate without assuming a faithful labelled-block representation.

<a id="c085"></a>

### C085 — Necessary orders of Hadamard matrices

**Claim.** If an n×n matrix H with entries ±1 satisfies HHᵀ=nI and n>0, then n=1, n=2, or 4 divides n.

**Proof.** Multiply columns and then rows by signs to make the first row and first column all +1, preserving orthogonality. For n>1, the second row has equal numbers of +1 and −1, so n is even. If n>2 use a third row. Partition columns according to the second row's sign; each part has size n/2. The third row sums to zero by orthogonality with the first and has equal sums on these two parts by orthogonality with the second. Thus each part's sum is zero, so n/2 is even. Hence 4 divides n.

**Dependencies/source.** Direct orthogonality count. **Use.** Rejects impossible exact orthogonal sign designs.

<a id="c086"></a>

### C086 — Kronecker multiplication constructs Hadamard matrices

**Claim.** If H and K are Hadamard matrices of orders m and n, then H⊗K is Hadamard of order mn. In particular such matrices exist for every order 2^a, a≥0.

**Proof.** Entries of H⊗K are products of signs and hence signs. For row pairs (i,a),(j,b), their inner product factors as (Σ_l H_il H_jl)(Σ_c K_ac K_bc)=mn δ_ij δ_ab. This is precisely the required orthogonality. Starting with the order-one matrix (1) and the order-two matrix with rows (1,1),(1,−1), repeated tensor multiplication yields all powers of two.

**Dependencies/source.** Elementary tensor-product entry calculation; Sylvester construction. **Use.** A compositional exact construction, not just an approximate norm estimate.

<a id="c087"></a>

### C087 — Finite Fourier orthogonality, inversion and Parseval

**Claim.** On G=F_p^d, define χ_γ(x)=exp(2πi γ·x/p) and f̂(γ)=|G|⁻¹Σ_x f(x)overline(χ_γ(x)). Then the characters are an orthonormal basis under the uniform inner product; f(x)=Σ_γ f̂(γ)χ_γ(x) and Σ_γ|f̂(γ)|²=|G|⁻¹Σ_x|f(x)|².

**Proof.** The inner product of χ_γ and χ_η factors into coordinate geometric sums. It is one when γ=η; otherwise some coordinate has a nontrivial pth root of unity whose geometric sum is zero. There are |G| mutually orthonormal characters in a |G|-dimensional function space, so they form a basis. Expansion in this basis yields inversion; multiplying the expansion by its conjugate and averaging eliminates cross terms and gives Parseval. The d=0 case is the one-dimensional constant space.

**Dependencies/source.** Geometric sums and finite-dimensional orthogonal expansion. **Use.** Exact diagonal coordinates for convolution and additive counting.

<a id="c088"></a>

### C088 — Biregular expander mixing with specified norm

**Claim.** For a bipartite incidence matrix M with row degree a and column degree b, let σ be the operator norm of M on the zero-sum subspace of R^R into R^L. Then for S⊆L,T⊆R,

|e(S,T)−a|S||T|/|R||≤σ√(|S|(1−|S|/|L|)|T|(1−|T|/|R|)), assuming both parts are nonempty.

**Proof.** Write 1_S=(|S|/|L|)1_L+s and 1_T=(|T|/|R|)1_R+t, with s,t zero-sum. Biregularity makes the mixed constant–centered terms vanish, and the constant–constant term is the displayed expected count, since a|L|=b|R|. The discrepancy is sᵀMt, bounded by ||s||₂ σ||t||₂. Expanding the two centered-indicator squared norms gives exactly the claimed expression. σ is a defined norm of the actual matrix, not an assumed spectral gap.

**Dependencies/source.** Cauchy–Schwarz. **Use.** Certifies incidence pseudorandomness once a concrete norm bound is supplied.

<a id="c089"></a>

### C089 — The binary Plotkin bound

**Claim.** A binary code of length n with M≥1 distinct words and minimum Hamming distance δ>n/2 satisfies M≤⌊2δ/(2δ−n)⌋.

**Proof.** In a coordinate with a ones and M−a zeros, the number of unordered pairs differing there is a(M−a)≤M²/4. Sum over coordinates: the total pairwise distance is at most nM²/4. On the other hand it is at least δM(M−1)/2. Divide by M>0 and rearrange to obtain (2δ−n)M≤2δ. The denominator is positive by hypothesis, and integrality gives the floor. For M=1 the same inequality remains valid with the usual vacuous minimum-distance hypothesis interpreted as a stated pairwise lower bound.

**Dependencies/source.** Coordinate double counting; Plotkin bound. **Use.** Bounds the size of highly separated binary certificate families.

<a id="c090"></a>

### C090 — Research conjecture: all admissible Hadamard orders

**Conjecture.** For every positive integer m there is a Hadamard matrix of order 4m.

**Evidence, not a proof.** C085 proves divisibility is necessary for orders above two. C086 constructs all orders that are powers of two and all products of known orders, but multiplication cannot by itself fill every 4m. Approximate orthogonal sign matrices do not satisfy this exact identity and do not resolve the conjecture.

**Dependencies/source.** [Steinerberger, primary discussion of approximate versus exact matrices](https://arxiv.org/abs/2402.13202); [2025 exact constructions](https://arxiv.org/abs/2510.12315). **Use/approach.** Exact orthogonal test systems and designs; further finite-field or difference-set constructions are potential routes, not general solutions here.

## 10. Additive structure, covering and zero sums

All additive sets in C091–C099 are finite and nonempty when cardinality ratios are used. Ambient groups are abelian. For subsets, A+B={a+b}, A−B={a−b}; kB denotes a k-fold sumset, with 0B={0}.

<a id="c091"></a>

### C091 — Cauchy–Davenport in prime order

**Claim.** For nonempty A,B⊆F_p, |A+B|≥min(p,|A|+|B|−1).

**Proof.** Write a=|A|, b=|B|. If a+b>p, every x has A∩(x−B) nonempty by counting, so A+B=F_p. Otherwise, if |A+B|≤a+b−2, enlarge it to C of exactly a+b−2 elements. The polynomial P(X,Y)=∏_{c∈C}(X+Y−c) vanishes on A×B and has total degree a+b−2. Its coefficient of X^{a−1}Y^{b−1} is binom(a+b−2,a−1), nonzero modulo p because all factorial arguments are below p. C074 contradicts vanishing. If a=b=1, the contradictory upper bound is zero and is already impossible because A+B is nonempty.

**Dependencies/source.** C074; inspected `ZMod.cauchy_davenport`. **Use.** A sharp expansion guarantee with no structural hypotheses on the summands.

<a id="c092"></a>

### C092 — Ordered sumsets have linear growth

**Claim.** For nonempty finite subsets A,B of R, |A+B|≥|A|+|B|−1.

**Proof.** List A as a₁<⋯<a_r and B as b₁<⋯<b_s. The chain a₁+b₁<⋯<a_r+b₁<a_r+b₂<⋯<a_r+b_s consists of r+s−1 distinct elements of A+B. This proves the inequality, including singleton cases. The same argument works in every linearly ordered abelian group with translation-invariant order.

**Dependencies/source.** Direct monotonicity; source hook in the torsion-free part of the inspected Cauchy–Davenport file. **Use.** A characteristic-free expansion certificate from order alone.

<a id="c093"></a>

### C093 — Ruzsa's triangle inequality

**Claim.** Nonempty finite additive sets satisfy |A−C||B|≤|A−B||B−C|.

**Proof.** For each d∈A−C fix one representation d=a_d−c_d. Map (d,b) to (a_d−b,b−c_d). Its image lies in (A−B)×(B−C). The sum of the two output coordinates recovers d; the fixed a_d and the first coordinate then recover b. Hence the map is injective, proving the cardinality inequality.

**Dependencies/source.** Explicit injection; Ruzsa triangle inequality. **Use.** Transfers a small difference-set estimate through an intermediate set.

<a id="c094"></a>

### C094 — Ruzsa's covering lemma

**Claim.** If |A+B|≤K|B| with B nonempty, there is X⊆A, |X|≤K, such that A⊆X+(B−B).

**Proof.** Choose X maximal with the translates x+B pairwise disjoint. Their union lies in A+B, so |X||B|≤|A+B| and |X|≤K. For any a∈A, maximality makes a+B intersect x+B for some x∈X, unless a was already in X, where the intersection also holds. Thus a+b=x+b' for some b,b'∈B, so a=x+b'−b. This proves the cover.

**Dependencies/source.** Inspected `Finset.ruzsa_covering_mul` and its additive counterpart. **Use.** Converts a cardinality bound into an explicit bounded-translate cover.

<a id="c095"></a>

### C095 — Additive energy and its maximal case

**Claim.** For finite nonempty A, E(A)=#{(a,b,c,d)∈A⁴:a+b=c+d} satisfies |A|⁴/|A+A|≤E(A)≤|A|³. Equality in the upper bound holds exactly when A is a coset of a finite subgroup.

**Proof.** With r(s)=#{(a,b)∈A²:a+b=s}, E=Σr(s)² and Σr(s)=|A|². Cauchy–Schwarz proves the lower bound. Each triple (a,b,c) determines at most one d, proving the upper bound. Equality means a+b−c∈A for every triple. Fix a₀∈A and put H=A−a₀. Then 0∈H and H+H−H⊆H, so H is closed under subtraction and is a finite subgroup; A=a₀+H. Conversely any such coset admits every determined fourth element, attaining equality.

**Dependencies/source.** Direct counting. **Use.** Distinguishes exact subgroup structure from merely high collision counts.

<a id="c096"></a>

### C096 — Petridis growth lemma and iterated sumsets

**Claim.** Choose nonempty X⊆A minimizing K=|X+B|/|X|. Then |X+B+C|≤K|X+C| for every finite nonempty C, and |X+kB|≤K^k|X| for all k≥0.

**Proof.** Enumerate C as c₁,…,c_m. Let X_i={x∈X:x+c_i is not in the earlier translates of X}; then Σ|X_i|=|X+C|. Any x∈X\X_i has x+c_i in an earlier translate, so (X\X_i)+B+c_i is already in the earlier translates of X+B. The new contribution at step i is therefore at most |X+B|−|(X\X_i)+B|≤K|X_i|. The last inequality is the minimizing property for the nonempty subset X\X_i, and is also true when that subset is empty. Summing proves the first assertion. Set C=(k−1)B and induct, starting at k=0, to prove the second.

**Dependencies/source.** [Petridis's elementary proof of Plünnecke growth](https://arxiv.org/abs/1101.3507); no unproved packing assumption. **Use.** A single small-growth subset controls all higher sumsets.

<a id="c097"></a>

### C097 — Bogolyubov's subspace certificate

**Claim.** If A⊆F_p^d has density α>0, then 2A−2A contains a linear subspace of codimension at most ⌈2/α²⌉.

**Proof.** Use normalized convolution and the Fourier normalization of C087. For f=1_A, let Γ={γ:|f̂(γ)|≥α^{3/2}/√2}. Parseval gives |Γ|≤2/α². Let W be the common kernels γ·x=0 for γ∈Γ; its codimension is at most |Γ|. Put f̃(x)=f(−x). The function f*f*f̃*f̃ has Fourier coefficients |f̂(γ)|⁴, by substitution in the convolution sum and Fourier inversion. For w∈W, every Γ character equals one, and the zero frequency contributes α⁴. The absolute contribution outside Γ is at most (α³/2)Σ_γ|f̂(γ)|²=α⁴/2. Thus the convolution at w is positive, which means w=a₁+a₂−a₃−a₄ with a_i∈A. Hence W⊆2A−2A.

**Dependencies/source.** C087; classical Bogolyubov argument. **Use.** Produces an actual subspace inside a bounded additive combination.

<a id="c098"></a>

### C098 — Schur's finite monochromatic equation

**Claim.** Define m₁=3 and m_r=r(m_{r−1}−1)+2 for r≥2. Every coloring of {1,…,m_r−1} with r colors has same-colored positive integers x,y,z with x+y=z; x=y is allowed.

**Proof.** First show every r-edge-coloring of K_{m_r} has a monochromatic triangle. For r=1 use three vertices. At a chosen vertex, some color occurs on at least m_{r−1} incident edges, since otherwise at most r(m_{r−1}−1) neighbors would exist. Among those neighbors, an edge of that color gives a triangle through the chosen vertex; if none exists, their complete graph uses only r−1 colors and induction gives a triangle. Now label vertices 0,…,m_r−1 and color each edge by the color of its positive endpoint difference. A monochromatic triangle a<b<c yields x=b−a, y=c−b, z=c−a in the original color class and x+y=z.

**Dependencies/source.** Elementary multicolor Ramsey recursion. **Use.** Guarantees additive relations in arbitrary finite partitions.

<a id="c099"></a>

### C099 — A zero-sum subsequence in an elementary abelian group

**Claim.** Every sequence of d(p−1)+1 vectors in F_p^d has a nonempty subsequence summing to zero. Repetitions are allowed and subsequence means a subset of positions.

**Proof.** Let its length be n and its vectors v_i. In n variables impose, for each coordinate j, Σ_i v_{ij}X_i^{p−1}=0. The sum of degrees of the nonzero equations is at most d(p−1)<n. C077 says the common-zero count is divisible by p. The all-zero solution exists, so it cannot be the sole solution. At a nonzero solution the nonempty support has X_i^{p−1}=1 at every selected position, and the equations say exactly that the corresponding vectors sum to zero. For d=0 the one available vector is already zero.

**Dependencies/source.** C077. **Use.** Exact zero-sum selection with a dimension-dependent universal length.

<a id="c100"></a>

### C100 — Research conjecture: Erdős–Turán additive bases

**Conjecture.** If A⊆N₀ and every sufficiently large integer is a sum of two elements of A, then r_A(n)=#{(a,b)∈A²:a≤b, a+b=n} is unbounded as n→∞, meaning limsup r_A(n)=∞.

**Evidence, not a proof.** If A has positive upper density, choose arbitrarily large N with |A∩[0,N]|≥δN for a fixed δ>0. The unordered pairs from this set give at least δ²N²/2 representations spread among 2N+1 sums. Thus some r_A(n) grows without bound; since each fixed n has finitely many representations, these witnesses must have unbounded n. This proves the positive-upper-density case, even without the basis assumption. It leaves the thin-basis case unresolved.

**Dependencies/source.** [Nathanson's primary formulation](https://arxiv.org/abs/math/0302155), [Ding–Wang, 2026, introduction](https://www.sciencedirect.com/science/article/pii/S0012365X26002670). **Use/approach.** Understands necessary redundancy of additive coverage; density amplification or representation-energy arguments would need a new input in the thin regime. This is distinct from the unrestricted real sum-product conjecture, counterexamples to which appeared in [Bloom–Sawin–Schildkraut–Zhelezov, 2026](https://arxiv.org/abs/2605.28781).

## How to use the volume

Select a proved entry whose hypotheses describe the intended object, verify those hypotheses, and compose the stated conclusions through the named dependencies. C010,C020,C030,C040,C050,C060,C070,C080,C090,C100 are never available as proved leaves. The principal sufficient routes are: local diminishing returns → greedy certificates; local capacity inequalities → integral assignments and flows; polynomial coefficients → finite witnesses; additive growth → covers and subspaces. This volume supplies reusable classical tools and precise research questions, not claims of new solutions to the listed conjectures.

