# A fixed independent idle family reduces to coordinates

## Contract

Let F be any field, V=F^n with named coordinate basis e_1,...,e_n,
and let stages s=1,...,m have coordinate masks M_s contained in {1,...,n}.
Write U_s=span{e_i : i in M_s}. Fix integers 0<=q_s<=|M_s|.

Choose one basis v_1,...,v_n of V for the entire schedule. A feasible
allocation chooses J_s contained in {1,...,n}, with |J_s|=q_s and
v_j in U_s for every j in J_s. Put I_j={s:j in J_s} and d_j=|I_j|.
Directions are independent globally, not merely separately at each stage.
A direction's scalar multiple represents the same line. No direction changes
between its uses. Choosing a different basis for a different allocation is
allowed. All basis setup, scalar mixing and transport costs are optimistically
zero. Eligibility uses only the output direction's support, so imposing
additional right-vector or physical restrictions can only shrink this model.

The coordinate model is the special case v_j=e_j. Its schedules have exactly
q_s distinct idle coordinates in M_s at each stage. Neither model preserves
a prescribed HOST action or imposes chronological barriers on coalescing.

## Theorem

For every feasible fixed-basis allocation there is a coordinate allocation
and a permutation pi of {1,...,n} with

    I'_{pi(j)} = I_j for every j.

In particular, the two models have exactly the same feasible multisets of
idle stage sets, and exactly the same feasible idle-degree multisets.
They have the same minimum sum_j f(d_j) for every real-valued function
f on {0,...,m}. No concavity or monotonicity assumption is needed for
this equality. More generally any objective invariant under relabeling the
directions has the same attainable values in both models.

The same reduction holds for a globally independent family of at most n
directions. Extend the family to a basis and give every added direction
the empty stage set. The permutation argument then applies to the original
family as an injection into the coordinate indices.

## Proof

Let B have columns v_j in the coordinate basis. Since det B is nonzero,
the determinant expansion has a nonzero summand. There is a permutation pi
such that B_{pi(j),j} is nonzero for every j. A nonzero sum must have a
nonzero summand over every field, including characteristic two. Thus pi(j)
belongs to the support of v_j.

If j belongs to J_s, all coordinates in the support of v_j belong to M_s,
because v_j belongs to U_s. Hence pi(j) belongs to M_s. Set
J'_s={pi(j):j in J_s}. The permutation is injective, so |J'_s|=q_s,
and J'_s is contained in M_s. This is a feasible coordinate allocation.
Moreover pi(j) belongs to J'_s exactly when j belongs to J_s, proving
the equality of stage sets and of degrees.

This constructs one inclusion of feasible multiset collections. The reverse
inclusion holds because the coordinate basis is itself an allowed fixed
basis. Objective equality follows by relabeling. All allocation domains are
finite at the stage-set level, even when F is infinite, so every nonempty
set of attainable objective values has a minimum. Coordinate feasibility
also follows directly from 0<=q_s<=|M_s|. This proves the theorem.

The support-matching fact is classical. Equivalently, every subset of the
independent columns has support union of size at least its cardinality,
and Hall's marriage theorem supplies the injection. The new contribution
is the degree-preserving reduction for this idle-coalescing question.

## Application to the connected eighteen-stage root

CubeJerry's [#7002](https://github.com/CrocSwap/integer-mult-bounds/pull/7002)
defines a coordinate-role relaxation in
[IDLE-COALESCING.md](../connected-l18-root-caller/IDLE-COALESCING.md).
It optimistically allows any two eligible coordinates to be hosted at a stage,
leaves the other mask coordinates idle, and coalesces all occurrences of a
coordinate for free. Its costs depend on idle degrees alone. Set
q_s=|M_s|-2 in the theorem.

Consequently, allowing an arbitrary fixed common basis, or a fixed globally
independent subset, cannot lower that relaxation's optimum. The predecessor's
stated coordinate optimum and fixed-profile failure therefore apply to this
larger subclass as a corollary. This is a new applicability step. The
predecessor's numerical optimum, transcendental bounds and complete invoice
are cited premises; this package does not recompute or certify them.

The proof maps optimistic allocations, not physical operators. It need not
map the HOSTs or retain a source's original endpoint. This causes no gap in
the lower-bound use: every admitted fixed-basis allocation maps to a feasible
member of the already optimistic coordinate relaxation. A map in the other
direction with physical HOSTs would require a separate construction.

## Boundary

Three directions e_1,e_2,e_1+e_2 in F_2^2 are dependent and cannot receive
distinct coordinate anchors. The matching proof therefore cannot cover
arbitrary dependent families, even if every individual stage uses independent
directions. This observation does not prove that dependent directions save
cost. A basis that changes between stages, changing a direction's identity,
also falls outside the contract. No theorem about either extension is claimed.

Noncoordinate common bases are thus insufficient on their own. A route
around this obstruction must change at least one premise, for example use
dependent directions across the complete schedule, rotate the basis, or
change masks, idle counts, native profile or the degree-only tariff.
