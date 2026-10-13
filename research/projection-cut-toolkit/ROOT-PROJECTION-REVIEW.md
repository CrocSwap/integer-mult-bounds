# Independent review: projection moves reduced to a minimum cut

Verdict: the stated reduction is correct for the encoded frame-inclusion problem. It optimizes one fixed rank-one projection's entire binary family, not all frame assignments or all projections. The minimum-cut theorem is standard; the contribution here is the explicit subspace compatibility and paid-edge encoding for this compiler graph.

Let lambda(v)=1 over F2, H=ker(lambda), and P(x)=x+lambda(x)v. Then P squared equals P, its image is H, and its kernel is span(v). A frame F is active exactly when lambda restricted to F is nonzero. Inactive frames satisfy P(F)=F. For active F, dim(P(F))=dim(F)-l(F), where l(F)=1 precisely when v belongs to F. For every edge U contained in V, l(U)<=l(V).

Use x_F=1 for the source side of the cut, meaning choose P(F), and x_F=0 for retaining F. It is sufficient to have variables only for active nodes.

## Exact compatibility table

For two active frames U contained in V:

* (0,0) is legal by the input inclusion.
* (1,1) is legal because linear maps preserve inclusions.
* (0,1) is illegal: U contains a vector of lambda-value one, but P(V) is contained in H.
* (1,0) is legal exactly when v belongs to V. Sufficiency follows from P(u)=u+lambda(u)v. For necessity choose u in U with lambda(u)=1; if P(u) belongs to V then v=P(u)+u belongs to V.

Therefore the hard arc V -> U is always required when both nodes are active, and U -> V is additionally required when l(V)=0. If U is inactive and V active, U=P(U) is contained in both V and P(V), so either choice of V is legal. An active U cannot be contained in an inactive V. Inactive/inactive edges never change.

## Exact cost table

Write r=dim(V)-dim(U). The new edge rank is r+l(U)x_U-l(V)x_V. Let f(0)=0 and f be nondecreasing on all ranks reached by these moves.

When both losses are one, feasibility allows (0,0), (1,0), and (1,1). Only (1,0) changes cost, by A=f(r+1)-f(r)>=0. A directed finite arc U -> V with capacity A gives exactly this cost.

When the losses are (0,1), the cost change is -B*x_V, where B=f(r)-f(r-1)>=0. Here r>=1: v belongs to V but not U. A source -> V arc with capacity B contributes B*(1-x_V). Subtracting the constant B recovers the exact cost change. This applies whether U is active or inactive; only the hard compatibility arcs differ.

When both losses are zero, the cost is unchanged. The loss pattern (1,0) is impossible for an inclusion. Summing these identities over every physical paid edge, including parallel edges with their full multiplicity, proves:

    total new cost - total old cost
      = finite cut capacity - sum of all source-arc capacities.

Thus a minimum feasible cut globally minimizes the exact paid objective over this fixed P's binary choices. The all-old assignment is feasible, so the optimal cost change is nonpositive.

## Fixed arbitrary boundaries

An active fixed node is forced to the sink side by a hard node -> sink arc. It need not be fixed by P. For an incoming edge from a selected active predecessor, the compatibility table requires either v in the old fixed frame or forbids the predecessor's selection. The stated hard arcs enforce exactly that condition. An outgoing edge from a fixed old active predecessor forbids selecting its active successor. Hence arbitrary old boundary frames are handled without assuming P fixes them. Fixed inactive nodes already equal their own projections.

For a literal finite network, a hard capacity strictly greater than the sum of all finite capacities suffices: the all-old cut has finite capacity at most that sum, while any violated hard arc alone costs more. Symbolic infinite capacities avoid numerical ambiguity. Zero finite capacities are harmless.

## Admission and numerical scope

The theorem concerns precisely the constraints encoded by the graph. If two scalar operands must share one frame, they must use the same node or have equality encoded in both directions. Every required fixed entrance, centre, source and final frame, as well as each separate paid register edge, must be represented. Any additional physical-interface obligations must remain fixed, be encoded, or be checked independently. A valid frame cut alone is not a substitute for the changed-word physical audit.

A long-double min-cut is a nomination mechanism, not a certificate of the exact optimum for irrational capacities. Reconstruct the selected subspaces, check all inclusions and fixed values exactly over F2, recount the integer rank histogram, and prove the actual moment inequality with the retained exact pricing engine. The sufficient construction and reduction are valid independently of whether this bounded numerical nomination finds an improving cut.
