# Hybrid movement and a clean one-axis adapter: design session

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
October 8, 2026. Conditional research context; no improved exponent.

## Decision

Neither concrete implementation tested here earns a larger construction
run. The two proposals change real assumptions of the previous diagnostics,
but their specified implementations still fail:

| Proposal | Changed assumption | Screening result |
|---|---|---|
| Retain one noncoordinate chart and recurse within smaller common blocks | Allows noncoordinate movement instead of eliminating it through coordinate Fourier kernels | The retained triple-projector families have no nontrivial common invariant block decomposition |
| Compute one useful output bank with clean workspace, using a one-axis code | Drops arbitrary-scratch restoration, the second tensor stage, and the all-role output obligation | Independent addition-tree readout of the retained central and three side outputs already costs at least the entire useful rank budget |

The clean adapter leaves a more specific missing mechanism: a **joint
producer of the complete side sums in their target frames**. Combining the
three existing side outputs separately for each target cannot provide it.
There is optimistic arithmetic headroom for a genuinely different producer,
but neither such a producer nor a compatible complex construction is supplied.
This is a replacement specification, not a newly surviving finite network.

The selected release, reviewed PR82 research baseline, and previous results
are unchanged. No goal loop, broad search, merge, push, or publication was
started. Historical notes cited below retain their original headline values;
only their mathematical contracts are used here.

## Starting constraints

The [mechanism brief](../mechanism-prep/REPORT.md) records the retained
target requirements: bit saving greater than 1/511 for kappa greater than
1/512, plus a separate complex saving exceeding 20/9709 at the cited
assembly parameters. Changing a primitive also changes its transfer and
precision obligations; those requirements are not supplied by a finite
rank calculation.

The [latest Fourier diagnostic](../fourier-boundary-fusion/REPORT.md)
extends the coordinate-only obstruction to rectangular copying/deletion
and spectator-volume splits. The earlier
[fused-block audit](../../docs/research/fused-block-audit.md) already
established the equal-volume coordinate-child obstruction. Neither result
excludes noncoordinate movement or a different root contract.

Two accounting rules guide this session:

* A fixed-factor reduction in the number of calls to the existing movement
  oracle does not improve that oracle's certified exponent. Keeping a
  positive constant-volume, linear-width movement call at the root leaves
  an O(V e^tau) term in the available recurrence estimate. This is a limit
  of the supplied upper-bound analysis, not a lower bound on actual runtime.
* Clean scratch and copies carry no new independent input volume. In a
  clean code with n useful source streams, normalize by n, even if it
  allocates many additional streams. Their initialization, reads, writes,
  parking and deletion must still be implemented and charged.

## Design A: persistent charts with smaller invariant blocks

### Operation and proposed payoff

Choose a common invertible linear address chart once for a complete
complex-network invocation. Preserve it through aligned scalar gates.
Evaluate residual phase kernels in that chart; restore the original chart
at the output. Every original input remains arbitrary and the complete
output operator is unchanged. Entry, exit and any changes between charts
are physical operations, not free reinterpretations.

The proposed recursive simplification is to split the address space into
smaller fixed invariant blocks, so every retained residual projector acts
inside those blocks. This could have concentrated the noncoordinate work
into a genuinely smaller family of recursive problems. Unlike the preceding
Fourier proposal, it explicitly retains noncoordinate address movement.

Before implementing a tape schedule, test the necessary simultaneous-block
condition. The rank-one endpoint projectors alone rule it out for the
current triple family. No ordering or gate search is needed for this test.

### Common-chart obstruction

Let q_S be the indicator of a triple. On the rational side use

    G = I - J/9,
    P_S = q_S (q_S^T G)/2.

For h not equal to 9, G is nondegenerate; q_S^T G q_S=2. Over F2, the
complex phase labels use P_S=q_S q_S^T because q_S^T q_S=3=1.
Both families consist of rank-one idempotents.

The triple vectors span the ambient space. Differences of two triples
sharing two points give coordinate differences; adjoining one triple
supplies the missing direction because 3 is nonzero over Q and F2.

Their nonorthogonality graph is connected in the retained regimes:

* Over Q, triples meeting in two points have pairing 1. These edges already
  form the connected triple-replacement graph.
* Over F2, triples meeting in one point have pairing 1. For h>=6, any
  two triples sharing two points can be connected by two such edges:
  take one of their common points and two points outside their union.

Now suppose a matrix A commutes with every P_S. Each q_S is its eigenvector,
say A q_S=lambda_S q_S, and the associated dual functional has the same
left eigenvalue. Whenever two labels have nonzero pairing, these eigenvalues
are equal. Connectivity and spanning therefore imply

    A = lambda I.

A nontrivial simultaneous block decomposition would give a nontrivial
block projection commuting with every P_S. None exists. The same argument
applies to all tensor endpoint lines q_S tensor q_T: they span the tensor
space, and their nonorthogonality graph is connected by changing one factor
at a time. Thus the bit 23-by-25 and complex 28-by-28 endpoint families
already obstruct this common invariant-block proposal.

Exact small controls compute the full commutant over Q and F2 at h=4,5,6.
They include a useful exception: at h=4 the four binary triple vectors are
an orthonormal basis, and the commutant has dimension four, not one. A
coordinate-projector family is a second positive control. These checks
support, rather than replace, the general argument at the retained sizes.

### Recurrence decision and scope

In this proposal there are no proper common blocks to serve as smaller
children. Treating the entire block as an unresolved recursive call does
not create contraction. Keeping existing costly chart changes and merely
reducing their number retains their inherited exponent in the available
recurrence estimate. These facts stop the specified implementation before
a larger search.

This does not exclude different charts on different segments, a new
implementation of a directional kernel with full physical support, a
multitype family without common invariant blocks, or changing the endpoint
geometry. Nor does it say that the complex phase operators fail to commute:
they are jointly diagonal in the full Fourier basis. The obstruction here
concerns a common *linear address chart and projector blocks*. Full Fourier
entry/exit costs belong to the already tested, different proposal.

**Smallest success test for a successor:** exhibit one complete noncoordinate
operator with a cheaper implementation or a closed, contracting family of
children. Naming a new child type or leaving its basis transport unspecified
does not meet that test. No such implementation was found in this session.

## Design B: clean workspace and one tensor axis

### Exact useful-output contract

Take n=C(h,3) independent source streams, one for each triple. Allow clean
scratch and discard obsolete streams. Require full bit interchange on all
n useful sources at the output. Auxiliary data need not be restored because
it was initialized as workspace, but no extra original input is counted for it.

For target S, define the central and side forms over F2 by

    c_S = sum_T (|S intersect T| mod 2) x_T,
    s_(S,i) = sum_(T intersect S = {i}) x_T,     i in S.

Then c_S + sum_(i in S) s_(S,i) = x_S. This is the inherited triple
identity used by the [shared producer](../../docs/research/shared-computation.md),
now proposed as a clean, one-axis code rather than an all-role shear.

Let the input's virtual frame be P_T, and the output's virtual frame be
H_S=I-P_S. If D_P denotes partial interchange, their physical composition
on the diagonal is

    D_(I-P_S) D_(P_S) = D_I.

Thus a correctly framed clean implementation of the scalar identity would
perform the required full interchange. Giving a source a virtual frame
does not physically transform it for free; every subsequent alignment
edge is charged. This proposal changes both the two-axis adapter and the
arbitrary-workspace contract, so the existing all-role transfer cannot be
invoked unchanged.

### Retained readout interface

Grant the producer for free to screen its readout alone. It supplies c_S
at frame 0 and s_(S,i) at the projector onto

    U_(S,i) = span_Q {q_T : T intersect S = {i}}.

For h>=6 these nondegenerate subspaces have dimension h-3. They lie in
H_S, which has dimension h-1. Their common subspace is

    D_S = {u : u_j=0 for j in S, sum_(j outside S) u_j=0},

of dimension h-4. Any pair of the three U spaces intersects exactly in D_S.
Their orthogonal projectors therefore have the following rank distances:

    dist(0,H_S)=h-1,
    dist(0,U_i)=h-3,
    dist(H_S,U_i)=2,
    dist(U_i,U_j)=2 for i != j.

These are projector rank distances, not dimension differences between
arbitrary nonnested spaces. The code constructs all projectors using exact
Gram inverses and checks the formulas. The retained h values avoid the
degenerate ambient h=9 case.

The central form and the three side forms are independent for a fixed S:
the source x_S occurs in the central form and no side form, and each of
the disjoint side groups is nonempty. Hence none of these four terms can
be dropped as zero. This does not declare the forms for *all* targets to
be independent: sharing across targets remains an explicit escape.

### Any independent tree readout exhausts the budget

Consider any per-target addition tree. Its four input terminals have frames
0,U_1,U_2,U_3, and its output has frame H_S. Internal gates have common
frames, and a physical edge is charged at least the rank distance of its
endpoint frames. Grant arbitrary rational internal matrices as an optimistic
relaxation of legal frame choices. This covers arbitrary regrouping into
addition trees, not just one common alignment gate.

A tree of total edge cost L admits a doubled traversal of cost 2L. By
shortcutting between successive terminals and using the rank triangle
inequality, this yields a terminal Hamiltonian tour of rank-distance cost
at most 2L. The shortest terminal tour for the five distances above has
length 2h: tours with H_S adjacent to 0 have length 2h+2; the other tours
have length 2h. Consequently

    L >= h.

The root has only h rank units of useful capacity per original stream.
Thus these separate readouts already have total rank at least nh, even
before charging the producer, copying, or any other boundary operation.
For children of width at most h, their normalized moment at exponent
sigma<1 is at least their normalized rank mass, hence at least one.
This interface cannot produce a contracting recurrence.

For comparison, an explicit legal nested-frame readout costs h+1:
move the central term from 0 to D_S; move side terms 2 and 3 to D_S and
add them; move the accumulator to U_1 and add side term 1; move it to H_S.
Its widths are

    h-4, 1, 1, 1, 2.

The exact minimum lies between h and h+1; it is not determined here.
The lower endpoint already suffices for rejection. All intermediate
transitions in the displayed upper construction are nested, so their
widths use the existing residual rule without an unproved batching lemma.

This is a restriction on the retained *separate-target tree readouts* and
their rank-distance compiler. It does not exclude cancellation DAGs,
joint readouts with work shared between targets, a different producer
interface, or a separately faster implementation of the composite operator.
Initializing scratch to zero alone does not change this readout bound.

## The remaining design specification: aggregate outputs in target frames

To avoid repeating the rejected readout, a clean producer would need to
deliver the full side sum

    s_S = sum_(|S intersect T|=1) x_T

directly at frame H_S, with its cost shared and charged across the whole
family of targets. Central c_S at frame 0 then moves to H_S in width h-1
and adds to s_S. Simply appending a separate merger to the existing three
side outputs reinstates the tree obstruction; it is not the missing compiler.

Here is a **hypothetical scorecard**, not a circuit. At h=23 and n=1771,
reserve n width-22 children for the central-to-output moves and h width-22
children for copied-center readout. Charge every remaining source alignment,
central gather, side computation, output preparation and recursive operation
to an additional profile G. Normalize all children by the n useful inputs.
These listed calls are proposed obligations; their sufficiency is unproved.

At exponent one the remaining rank mass must be strictly less than

    n - h(h-1) = 1265.

At the 1/511 bit-saving screen, the exact moment for an additional g
width-one calls is

    ((n+h)/n)*(22/23)^(510/511) + (g/n)*(1/23)^(510/511).

Exact rational root enclosures give:

| Additional singleton calls | Moment, approximate display | Screen |
|---|---:|---|
| 1253 | 0.999979021942092 | Pass |
| 1254 | 1.000003723163713 | Fail |

These are limits for the stated hypothetical profile, not a count of an
existing producer. Other width distributions need their own exact moments.
In particular, the usual n width-one input unframings already exceed this
allowance, before side computation. The missing mechanism must jointly
avoid that bill and the separate readout bill; it is not merely removal
of cleanup from the existing dirty-workspace circuit.

This arithmetic is useful as a falsifiable specification. It does not
increase our confidence that such a compiler exists. The entire clean
finite-transfer proof, precision and row-stock accounting, and a complex
companion are still missing. Even a successful bit construction here would
not by itself establish kappa greater than 1/512.

## What should happen next

Do not expand the common-chart search or optimize independent clean readout
trees. Both have already failed necessary conditions. Do not treat a fixed
number of saved movement calls as an exponent gain.

If this direction is revisited, the concrete proposal to request is a joint
side/central producer that creates aggregate side outputs in their target
frames and avoids per-source unframing. Before a large search, it should
show an exact local saving after *all* frame transitions, explain how it
shares across targets, and score its full profile against useful input
volume. A small success need not reach the headline, but needs a plausible
scaling mechanism. No current candidate meets those requirements.

This session narrows the opening and supplies rejection tests. It does not
select a viable construction or justify another unattended search loop yet.

## Reproduction and verification

```sh
python3 research/hybrid-clean-design/design.py --output research/hybrid-clean-design/certificate.json
python3 -m unittest discover -s research/hybrid-clean-design -p 'test_*.py' -v
```

Six tests cover the common-chart obstruction and positive exceptions, clean
scalar cancellation, projector and terminal-tour calculations, physical
partial-swap endpoints, every path of the explicit readout tree, and the
distinction between hypothetical profile headroom and a construction.
All acceptance decisions use exact arithmetic. Small tests accompany the
written general proofs; there is no Lean formalization or new upstream
theorem audit. The [certificate](certificate.json) pins dependencies and
[validation](validation.json) records execution and preservation checks.

Provenance: the scalar triple identity, producer frames and side groups
come from the repository's earlier shared-computation and retained-center
work. Paureel's copying/two-stage adapter, icekylinx's producers and copied
centers, and Zhihao Chen's compatible transfer remain inherited context.
This session supplies scoped design screens and a missing-producer budget,
not a claim to rediscover those ingredients.
