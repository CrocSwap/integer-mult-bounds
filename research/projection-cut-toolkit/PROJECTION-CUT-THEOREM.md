# A rank-one frame move is exactly a minimum-cut problem

This is a constructive optimization theorem for finite compiler frame graphs. It is not a claim that a better kappa exists, or a new theorem about the general maximum-flow problem. The two connections used here are (i) binary domain-wall energies from statistical mechanics / computer vision and (ii) linear projection with rank-nullity from module theory. The gain is a search representation: simultaneous frame rotations and contractions can be optimized as one cut, rather than by independently trying each event.

## Precise input and output

Let G be a finite directed multigraph. Every vertex e carries a subspace F_e of a finite-dimensional vector space over F_2, and every edge u -> w satisfies F_u <= F_w. Parallel edges represent different physical register wires and retain multiplicity. Some vertices are fixed. Let f: {0,...,d} -> R be nondecreasing with f(0)=0. The objective is the sum over edges of f(dim F_w - dim F_u). Constant charges outside this graph remain unchanged.

Fix v and a linear functional lambda with lambda(v)=1. Define P(x)=x+lambda(x)v. For every unfixed vertex choose either F_e or P(F_e); fixed vertices retain F_e. The output is a legal assignment minimizing the stated objective among ALL such binary choices, or the original assignment if it minimizes. A finite directed s-t minimum-cut computes this output. For rational f the entire construction uses rational capacities. For power costs f(r)=r^(1-a), real capacities specify the mathematical theorem; rigorous interval pricing is still required for a numerical improvement claim.

## Projection and mixed-edge lemmas

P is linear, P^2=P, ker(P)=<v>, and im(P)=ker(lambda). Thus

    dim P(F) = dim F - l(F),    l(F) = 1 if v lies in F, else 0.

Call F active if lambda is nonzero on F. Precisely the active frames change under P. For U<=V, activity is upward closed and l(U)<=l(V).

Both unmodified and both projected endpoints of an edge are legal by linearity. For active U,V:

* U<=P(V) is impossible, since P(V)<=ker(lambda) but U is active.
* P(U)<=V holds exactly when v lies in V. If v lies in V, linearity gives the inclusion. Conversely choose u in U with lambda(u)=1; if u+v belongs to V, then v does too.

If U is inactive and V active, U=P(U)<=P(V), and all effective choices are legal. An active U cannot be contained in inactive V. These are all cases, so no geometric condition is omitted.

## Graph construction

Use binary x_e=1 for a projected active frame and x_e=0 otherwise; source-side means1. Inactive frames need no variable. For every active-active edge u->w:

* insert a hard arc w->u (forbid x_u=0,x_w=1);
* additionally insert a hard arc u->w if l(F_w)=0.

Every fixed active vertex has a hard arc to the sink. Inactive vertices are unselected. Let r=dim F_w-dim F_u. Add finite arcs for EACH original edge:

* If l(F_u)=l(F_w)=1, add u->w of capacity f(r+1)-f(r).
* If l(F_u)=0,l(F_w)=1, add source->w of capacity f(r)-f(r-1).
* If both losses are0, add no finite arc.

The impossible loss pattern(1,0) never occurs. In the second case r>=1, so f(r-1) is defined. In the first case r+1<=d. All capacities are nonnegative by monotonicity; concavity is NOT needed for this optimization theorem. A hard capacity greater than the SUM of all finite capacities suffices, since the all-unselected feasible cut has at most that finite sum.

## Exact objective identity

Let C be the sum of all source-arc capacities (counting multiplicity). For any feasible cut, the exact change of objective is

    Delta = cut_capacity - C.

Proof: for losses(1,1), the only nontrivial legal label pair is(1,0), changing rank r to r+1 and crossing its finite arc. Pair(0,1) is forbidden; pairs(0,0),(1,1) leave r unchanged. For losses(0,1), the rank changes to r-1 exactly when w is selected. Its contribution is -(f(r)-f(r-1))*x_w, which equals the source-arc cut charge minus its capacity. Both-zero losses change no rank even if frames rotate. Sum these identities. Hard arcs enforce exactly the mixed-frame inclusions already proved. Therefore minimizing the cut minimizes the exact paid objective, and any cut of capacity<C gives a sufficient strict improvement of that objective.

Fixed boundary frames need not be invariant under P: their label is simply0, and the incident hard arcs enforce legal interaction. This distinction permits local projection moves despite globally fixed endpoints.

## Relation to physical admission

This theorem alone optimizes the finite frame graph, not the entire multiplication claim. The scalar instructions remain fixed, but new Clifford phase charts and endpoint adapters must be reconstructed. Fixed observations, center constraints and target cuts must be represented faithfully; any remaining compiler restriction must be checked separately. The complete local and global emitted transcripts, paid histogram, finite invoice and both exact moment engines must pass before quoting a new kappa. No control is weakened by using this optimizer.

The current word is represented by5,471 event/boundary vertices on728 register chains. Starts, ends, center observations and target cuts are fixed. Each scalar event is a shared vertex for every register it touches; optimizing each wire independently would be wrong. The unchanged center descent charges are outside the graph as constants. The C++ implementation nominates using long-double capacities and exact binary subspace tests. A failed floating screen is not an exact global exclusion certificate, and an apparent success would still need independent rational admission.

## Sources and scope of originality

The cut machinery is standard: Jean-Claude Picard, *Maximal Closure of a Graph and Applications to Combinatorial Problems* (1976), https://doi.org/10.1287/mnsc.22.11.1268; Vladimir Kolmogorov and Ramin Zabih, *What Energy Functions Can Be Minimized via Graph Cuts?*, https://www.cs.cornell.edu/~rdz/Papers/KZ-ECCV02-graphcuts.pdf . The application-specific contribution here is the precise linear-projection move, mixed-edge characterization, objective identity and compiler-boundary contract. This is distinct from asserting global novelty of graph-cut optimization, which has also appeared earlier in this campaign.

Mathlib's Submodule map/ker/range and finite-dimensional rank-nullity APIs guided the linear statement. Source-DAG structural hits were inspected as research pointers, not imported as Lean certificates. No Lean file was created. ROOT-PROJECTION-REVIEW.md contains a separate agent's mathematical check. exact_selftest.py exhaustively checks the edge identity in dimension3 and1,008 finite graph instances with exact integer costs, including fixed boundaries and parallel edges; it supplements rather than replaces the universal argument above.
