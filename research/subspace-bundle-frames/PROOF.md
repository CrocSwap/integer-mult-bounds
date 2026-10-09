# Coordinated frame moves on the fixed physical word

The underlying scalar word, aliases, compensation deadlines, source labels,
root readouts and endpoint frames are fixed. Only operation frames change.
For operation i, its frame F_i must contain the full recursively computed
source span S_i. Each physical register, including a spliced donor/recipient
chain, must have nested frames from its prescribed start to its endpoint.
These are checked by the retained full physical verifier.

## Expansion by one binary direction

Fix a binary vector v. Each operation not already containing v may either
keep F_i or replace it by F_i + <v>. Fixed start, gauge, root and full frames
are never variables. Expansion preserves source containment.

For a chain edge U contained in V, write d=dim(V)-dim(U). If neither frame
contains v, an expansion of U requires expansion of V. For the feasible
states (0,0), (0,1), (1,1), the rank increments are d, d+1, d respectively.
If only U misses v, expanding U changes the increment from d to d-1.
If U contains v then V does too, so there is no variable change on that edge.

Let c(d)=d^(1-a)-d, with c(0)=0. Total rank mass is constant on every complete
nested register chain, so minimizing the sum of c is equivalent to minimizing
the positive-rank moment. When both ends miss v, the feasible edge cost
change is

    [c(d+1)-c(d)] (x_V-x_U), with x_U <= x_V.

This is a pair of unary weights and an implication. When the successor
already contains v, the unary weight on U is c(d-1)-c(d). A fixed successor
missing v prohibits expansion of its predecessor. Thus the global move is
a minimum-weight closed subset problem on operation variables.

The search converts unary weights to integer capacities and solves an s-t
cut. The hard-constraint capacity exceeds the sum of all finite absolute
weights. This optimizes a rounded discovery objective only. Every accepted
move must also improve the unrounded discovery score, and all output frames
must pass exact containment and nesting checks. Neither rounded capacities
nor floating scores are used as evidence for the final exponent.

## Hyperplane contraction by duality

Reverse every chain and replace U by its orthogonal complement U-perp.
Inclusion is preserved in the reversed order, as are all rank increments.
An expansion U-perp + <v> corresponds to the primal contraction

    U -> U intersect v-perp.

For each operation, this is permitted only if v is orthogonal to its entire
required source span S_i. The solver adds a prohibition otherwise. The dual
fixed endpoints stay fixed, so starts, gauges, root frames and endpoints
are all preserved in the primal interpretation as well.

The same closure construction therefore finds simultaneous admissible
contractions. Source containment and all physical chains are rechecked after
every accepted move.

## Local endpoints and equal-frame groups

For one operation, the join of its source span and predecessor frames is a
feasible lower endpoint; the meet of its successor frames is a feasible
upper endpoint. The search tries both. Connected equal-frame groups can
move together: their internal edges remain rank zero, and every external
boundary edge is charged with its full multiplicity. These are additional
discovery moves, with the same final acceptance requirements.

## Complete accounting

All rank increments are derived again from actual candidate frames by the
original physical checker. The terminal-sink compiler is rerun, since changed
sink prefixes alter local and target histograms separately. The complete
combined histogram is then passed to the original rational interval moment
routine and the retained 47-constraint balanced assembly.

The full physical word and every formal source, target and arbitrary dirty
column are replayed under both shear signs. Scalar and routing bills and
the complete polynomial row-stock charge are checked against the baseline.
If a maximum child changes, the bridge formulas reprice its halving and
semantic induction obligations before the assembly is accepted.

This establishes a conditional finite-witness improvement only after that
full verifier passes. It does not establish global frame optimality or prove
the original analytic and finite-to-all-size compiler interfaces.

# Fixed-subspace closure moves

For U contained in W, fix a subspace V and let t_U=dim(U+V)-dim(U),
t_W=dim(W+V)-dim(W), d=dim(W)-dim(U). Then t_U>=t_W.
If both t values are positive, expanding U to U+V while keeping W is
infeasible because V is not contained in W. Thus x_U<=x_W. The three
feasible states 00,01,11 have increments d,d+t_W,d+t_W-t_U. Their
cost relative to 00 equals

  [c(d+t_W)-c(d)] x_W + [c(d+t_W-t_U)-c(d+t_W)] x_U.

If t_W=0, expanding U alone gives c(d-t_U)-c(d). If t_U=0 both
are zero. Fixed endpoints are handled as in single-direction closure.
This proves the same exact minimum-weight closure reduction for adding
a whole subspace. Reversed orthogonal-complement chains give contraction
by V-perp, permitted only if the entire source span is orthogonal to V.
The search tests two-coordinate planes and frequent two/three-dimensional
annihilator subspaces. It can jump over configurations that improve only
after several directions change together. This is a possible benefit,
not an assertion that the particular search gains over the single-direction
method. A candidate must pass the complete original exact verifier.

## Relationship to PR195 and retained hypotheses

PR195 by huxint at d3e6b83af33c3aad940e737776937706e25b0b19 already
implements arbitrary-subspace joins/intersections in Cut.step(L, mode).
Our primal bundle is its join with L=V; the dual bundle is its meet with
L=V-perp. This is an independent implementation and a different finite
proposal catalogue, not a new move family or a novelty claim for cuts.

The starting seed is the exact selected frame list of that commit, recorded
in SOURCE.json. The parent scalar graph, word, aliases, frame endpoints and
base profile were checked byte-identical to the reviewed PR186 package.
New frames are independently derived and admitted by the original physical
checker. The original complete-column bound, terminal compiler, bit supplier,
finite bridge and assembly remain the proof dependencies. Every terminal
prefix is regenerated; no old prefix is retained after changing its frame.

All numerical cost obligations are recomputed. The method stays inside the
retained parameter domain and does not change the bit supplier or its ceiling.
The parent bank scheduling supplement remains applicable to the unchanged
bit word. It supplies the explicit low-residue schedule and finite extra prime
exclusions; none of its hypotheses is discharged anew here.

The all-size analytic, compiler, common-chart, routing, restored-row,
precision/recovery, prime supply, uniform setup and fixed-tape interfaces
remain conditional. Finite certificate success is not formal verification
of the complete multiplication theorem.
