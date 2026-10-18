# Cut certificates for exact dirty-output synthesis

Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.
This is a self-contained written argument and executable certificate checker,
not independent human review or formal-kernel verification. The graph algorithm
and dirty-output mechanisms are credited prior work.

## 1. Contract and delta

Retain Ross Richardson's PR3121 contract. There are q>=1 required rows
A_i in F2^w, w>=1, with independent arbitrary initial dirt a_i. A complete
oracle P_i performs A_i ^= p for the same arbitrary p on every invocation.
Its read-only inputs are disjoint from the A rows and preserved. ADD(i,j)
performs A_i ^= A_j for i != j. Required endpoint: A_i=a_i+p for every i.
Words are finite, fixed and straight-line. Every gate is paid; arbitrary
interleavings and repetitions are permitted. No other helper, COPY, CLEAR,
free basis change, adaptive branch or intermediate observation is admitted.

Let mu_i>0 be the complete stationary P_i price and c_ij>0 the complete
stationary ADD(i,j) price. **The directed edge is j -> i.** A physical caller
must supply these prices, including source access, routing, frame adapters,
precision, scratch restoration and head return. No physical tariff or selected
supplier placement is constructed here. The implementation accepts exact
positive rational prices; the certificate soundness argument also applies to
real prices whenever the displayed inequalities are established exactly.

PR3121 proves the optimum is a directed rooted-forest bill using Edmonds'
disjoint-branching theorem. Its executable uses bounded enumeration. This
package supplies a polynomial arithmetic-operation compiler and a small
independent checker. The checker proves a concrete all-word optimum by adding
weighted cut inequalities. It neither calls the optimizer nor invokes the
branching theorem. This does not claim a new graph optimization algorithm,
new forest synthesis identity, replacement of the physical H1-H5 interface,
or a new multiplication kappa.

## 2. The word inequality

For a successful word, let o_i be its number of P_i calls and k_ij its number
of ADD(i,j) gates. For any nonempty row subset S, define

    o(S) = sum_{i in S} o_i,
    k(in S) = sum_{i in S, j not in S} k_ij.

Then

    o(S) + k(in S)/2 >= 1.                                      (1)

If o(S)>=1 this is immediate. Otherwise the predecessor's dirty-span lemma
requires at least two incoming ADD occurrences. For completeness:

* With zero incoming ADDs, the coefficient of p in S remains zero, so it
  cannot become one in every required row. Here p must be arbitrary.
* With exactly one incoming ADD, specialize p=0 and retain all q independent
  dirt columns. Every prefix matrix on dirt is invertible. Before that gate,
  the span of the S rows is the coordinate space W_S; internal ADDs preserve
  it and outgoing ADDs leave those rows unchanged. The incoming source row
  lies outside their span, because all q rows form a basis. Replacing one S
  row by its sum with that source changes the S-row span. With no further
  incoming gate, internal ADDs preserve this changed span. It cannot return
  to W_S at the identity dirt endpoint. Outgoing feedback does not alter the
  argument: prefix invertibility still keeps an outside row independent.

This is PR3121's oracle-free subset argument, itself extending PR3063's
one-row invariant. The new use is the combined inequality (1), which handles
unknown oracle destinations in a single certificate. It does not restrict a
competing word to the compiler's forest shape.

## 3. A directly checkable lower bound

Supply a finite collection of nonempty subsets S and rational prices y_S>=0.
Require

    sum_{S containing i} y_S <= mu_i,                         for every i,
    sum_{S: i in S, j not in S} y_S <= 2 c_ij,                for every i!=j. (2)

Multiply (1) by y_S and sum. Nonnegativity of all gate counts and (2) give

    sum_S y_S
      <= sum_i o_i sum_{S containing i} y_S
           + (1/2) sum_{i!=j} k_ij sum_{S: i in S,j not in S} y_S
      <= sum_i mu_i o_i + sum_{i!=j} c_ij k_ij.                       (3)

Thus sum y_S lower-bounds **every successful word**, including repetitions,
feedback and interleaved oracle calls. No linear-programming duality theorem,
integrality theorem or graph theorem is needed for this certificate's validity;
(3) is just a nonnegative weighted sum of proved inequalities.

`check.py` separately verifies all q root capacities and q(q-1) ADD capacities,
positive cut prices, the complete emitted word's symbolic dirt/p endpoint,
literal inverse, actual gate bill, and equality of that bill to sum y_S. Equality
proves the word optimal in this exact contract. Every physical bit position
obeys the same XOR identity, so checking the q dirt symbols and p certifies the
finite word for all widths and arbitrary data, not merely sampled one-bit data.

The parent array is checked as an additional forest/invoice witness; the actual
emitted gates establish the upper bound. The checker does not trust the parent
array instead of replaying those gates. Nor does it require laminar cuts. A
positive control supplies two crossing cuts plus singleton cuts, independent of
the compiler's output, and obtains the same cost-8 valid endpoint.

## 4. Constructing certificates without enumerating forests

Use the classical Chu-Liu/Edmonds minimum-arborescence contraction algorithm.
Add a **graph-only** root s, root edges s->i of weight mu_i, and ordinary edges
j->i of weight 2c_ij. This root is not a physical helper or free oracle.
Deleting s from an outward arborescence gives a directed rooted forest.

The implementation maintains disjoint clusters of original rows and residual
weights. Initially clusters are singletons. At each level:

1. For every nonroot cluster V, choose its cheapest incoming edge, with an
   explicit deterministic tie rule. Subtract its residual weight delta_V
   from every edge entering V, and add delta_V to the certificate price y_V.
2. If chosen edges are acyclic, they form a rooted spanning arborescence;
   every nonroot has one parent, and following parents must reach s.
3. Otherwise contract one chosen-edge cycle to its union cluster, remove
   self edges and continue. Keep original edge identities and each cycle's
   chosen edges for expansion. There are at most q-1 contractions.
4. Expand in reverse. A contracted cluster has exactly one entering selected
   edge. Keep its actual entry vertex, and add the saved cycle edges into all
   other cycle vertices. This breaks the cycle, spans the cluster and leaves
   a rooted tree with exactly one entering edge for every recorded cluster.

Root reachability is guaranteed by the finite root edge to every original
row. The root is never on a selected-parent cycle. All residuals are nonnegative
because delta_V is the cheapest incoming residual; all emitted prices are
nonnegative. The compiler drops zero-price cuts.

For any original edge e, its residual is

    w_e - sum_{recorded S entered by e} y_S.                          (4)

While its endpoints are in different clusters, step 1 updates exactly the
relevant term in (4). Once its endpoints coalesce, no later cluster separates
them, so removed internal edges need no later updates. This proves every
original edge capacity in (2), not merely capacities of the final graph.

Every saved cycle edge is tight when chosen. After its endpoints coalesce,
its residual stays zero. Final acyclic chosen edges are also tight. Expansion
selects only such edges and gives exactly one selected edge entering every
cluster whose price was raised. Summing their original weights via (4) gives

    selected graph weight = sum_S y_S.                               (5)

This proves the constructive certificate property. It is also the standard
primal/dual explanation of contraction, included to make the implementation
reviewable; no priority for that method is claimed. Even a bug in this compiler
cannot establish a false result unless the separate checker also accepts a
false capacity, endpoint or equality. Source/code authentication and ordinary
software correctness remain part of the trusted verification boundary.

The cluster family is laminar: any two are disjoint or one contains the other.
There are at most 2q-1 distinct nonempty clusters (q leaves and at most q-1
unions). The explicit implementation retains at most q^2 original arcs and
uses O(q^3) rational arithmetic operations. Its naive certificate checker also
uses O(q^3) arithmetic operations for these certificates. This is an arithmetic-
operation count, not a uniform unit-cost bit-time or physical tape bound. Exact
rational bit lengths and input/output storage are real costs. The complete
q-by-q tariff matrix must already have been supplied by the caller.

## 5. The restored word and complete price

For each forest edge parent(i)->i, execute ADD(i,parent(i)) in child-before-
parent order. Call P once on each forest root. Execute the preparation ADDs
in literal reverse order. During preparation each parent still has its original
dirt when read. Each nonroot therefore holds a_i+a_parent. On the return pass,
parents have already become a_parent+p, so that row becomes a_i+p. Roots get
that endpoint from their P calls. No extra row or oracle uncompute is hidden.

The complete price is exactly

    sum_roots mu_i + 2 sum_edges c_ij.                               (6)

Together, (3), (5) and the executed endpoint prove optimality. The exact inverse
reverses all gates and has the same bill; a caller needing it as another stage
must pay again. An arbitrary path-dependent or time-dependent tariff cannot
be substituted into (6). The package does not price independent private oracles;
their fixed additive bill is handled separately by the credited predecessor.

The chain fixture from PR3121 has cost 5. A constructed cheap-cycle control
has mu=(1,100,100), c_12=c_21=1, c_10=c_20=50 and c_01=c_02=100.
Choosing each row's cheapest incoming augmented edge gives 1+2+2=5 but has
an unrooted cycle. The certificate assigns y_{0}=1, y_{1}=y_{2}=2 and
**y_{1,2}=98**, proving 103. Two roots and one twice-paid edge attain 103.
The extra cut records the missing root connection instead of trusting a
cycle-free label or enumerating all competing words.

## 6. Coverage and remaining obligations

`RESULT.json` records complete q<=3 tariff cubes with every mu_i,c_ij in
{1,5}: 530 cases compared to unrestricted shortest paths on exact affine
states, with 394 strict sharing wins and 240 mixed-root certificates. These
comparisons optimize over arbitrary gate interleavings at the stated tiny
sizes, not over a full physical model.
The separate parent-function implementation checks 48 seeded positive rational
instances through q=6 (145,984 forests across those repetitions). Larger
constructed instances have q=8,16,31,64,112. These domains are corroboration;
the word inequality and certificate argument supply the all-word conclusion.

The q=112 example is an explicitly **synthetic** stationary tariff matrix.
It has a 223-gate word (one oracle, 222 ADDs), 216 positive cuts, and 12,544
capacity inequalities. Its exact declared optimum is 1,539. This is a compiler
stress case with nested cycles, not a selected supplier invoice or a claimed
physical saving. All named certificates are committed in compact JSON.

Negative controls cover missing restoration/oracle calls, wrong edge direction,
undercharged edge capacity, inflated/negative/duplicate cuts, cyclic parents,
typed values, wrong cost, source/receipt corruption, duplicate input keys and
operation under `-O`. An export executes the checker after physically removing
the compiler file. A nonlaminar positive certificate tests acceptance beyond
what the contraction generator emits.

An actual physical caller with legal unobserved target lifetimes and complete
stationary prices remains missing. The contribution removes an exhaustive
synthesis/certificate-checking obstacle; it does not solve the predecessor's
physical caller, frame, clean/dirty hosting, precision or complete supplier
recurrence obligations. No selected record, upstream source or kappa changes.

## Credit

Ross Richardson's PR3121 (`eea0861aff47df568be4bb4a4db43c2da390d351`) supplies
the subset dirty-span lemma, exact edge-price theorem and forest tariff model;
PR3063 (`3f384b8b7daccb2c8e12013fd81a738202ce0f8d`) supplies the destination
tradeoff. Cinna Davis/PR1944 supplies the original dirty echo; PR1968's multiple
common-term accumulation is separate. Anthony/PR774, Oscar Fennell/PR759 and
the retained synthesis literature keep their forest-construction credit.

Credit Y. J. Chu and T. H. Liu, *On the shortest arborescence of a directed
graph*, Scientia Sinica 14 (1965), 1396-1400, and Jack Edmonds, *Optimum
branchings*, J. Res. NBS 71B (1967), 233-240, DOI 10.6028/jres.071B.032.
The code is newly written; no third-party implementation is copied. The general
contraction and primal/dual method are classical. This result is their explicit
word-level certificate application and reusable scoped implementation.
