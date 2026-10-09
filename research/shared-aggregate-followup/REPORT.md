# Shared aggregate follow-up: the zero-frame producer frontier costs the saving

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
October 8, 2026. Bounded theoretical diagnostic; no new multiplication exponent.

## Decision

Stop the clean aggregate-producer branch **with the interface specified in
the preceding design session**. A general input-cost bound closes its
optimistic budget, even allowing shared computation, cancellation and
arbitrary internal rational frame matrices.

The proposed producer starts with n distinct rank-one source frames and
delivers its central sums at frame zero. Its paid frame transitions have
total rank at least n. The subsequent, separate output readout already
costs n(h-1). Their sum is at least nh, the entire useful-input rank
capacity. No strictly contracting rank moment remains.

This is not a lower bound on multiplication, every clean-workspace adapter,
or every joint producer. It assumes the declared common-zero central
frontier and its separate readout. Interleaving producer and readout so
their work is genuinely shared, changing the central interface, or changing
the frame/child contract remains outside the conclusion. No such alternative
is supplied here.

Before deriving that bound, we tested one explicit shared-output identity
for adjacent target triples. The scalar identity is correct. Its natural
aggregate frames require two extra rank-one alignments, so its fully
charged readout already reaches the noncontracting boundary. It does not
supply the missing producer.

All previous research and release artifacts are preserved. No wider search,
new goal loop, commit, push or publication is part of this follow-up.

## 1. The proposed contract and its missing budget

The [design session](../hybrid-clean-design/REPORT.md) proposed a one-axis
clean bit-interchange adapter, with n=C(h,3) useful independent source
streams. Work takes place over F2 for scalar payload operations and Q for
frame geometry. The rational form is G=I-J/9, with h not equal to 9, and

    q_T = indicator of triple T,
    P_T = q_T (q_T^T G)/2,
    H_T = I-P_T.

The source frame is P_T. The proposed producer supplies central sums at
frame 0 and aggregate side sums at their target frames H_T. Moving a
central result from 0 to H_T costs rank h-1. The scalar central-plus-side
identity then gives full physical interchange because

    D_(H_T) D_(P_T) = D_I.

These virtual frames do not grant any physical source conversion for free.
The root capacity is nh because only the n original streams are independent
useful inputs. Clean scratch and copied streams add no normalization volume.

For h=23 and n=1771, the earlier hypothetical profile reserved n width-22
output moves and h width-22 center-readout calls. It permitted an additional
1253 singleton children at the 1/511 bit-saving screen. That calculation
was explicitly conditional on an unprovided producer. The following bound
shows that producer cannot fit the stated interface and budget.

## 2. One exact shared-output identity

Choose neighboring target triples

    S={a,b,i}, T={a,b,j}.

Let C be the source triples neighboring both S and T under intersection
size one, U_S those neighboring only S, and U_T those neighboring only T.
These are disjoint sets. With c_S and c_T the central parity sums, write
z_C,z_S,z_T for the three aggregate side sums. The two scalar outputs are

    x_S = c_S + z_C + z_S,
    x_T = c_T + z_C + z_T.

This shares a complete side term across targets rather than separately
merging each target's three point-indexed outputs. Put k=h-4. The exact
support counts are

    |C|=k^2,
    |U_S|=|U_T|=k(k+3)/2.

The common sources consist of a or b together with two outside points,
or i,j together with one outside point. The unique S sources consist of
a,j,r or b,j,r, and i,r,t, with r,t outside S union T; the T version is
symmetric. These descriptions prove the counts and the scalar identity.

### The actual spans, including the previously unbudgeted alignments

Let K be the rational span of the common source labels. For h>=6,

    K = H_S intersect H_T,    dim K=h-2.

The unique S labels span a proper subspace L_S of H_S, also of dimension
h-2. In addition to the equation for H_S, they satisfy

    u_j = u_a + u_b.

Likewise, the unique T labels span a dimension-(h-2) subspace L_T of H_T.
They do **not** span their full target hyperplanes. A check that initially
assumed equality failed and was corrected before any result was promoted.

The proposed readout takes c_S and c_T at frame zero, z_C at K, and the
unique aggregates at L_S and L_T. Move both central terms to K, add the
shared term to each there, then move the two accumulators to H_S and H_T.
Finally align and add the unique terms. Its complete recursive widths are

    h-2, h-2, 1, 1, 1, 1.

Their sum is 2h. The common-term portion costs 2(h-1), but the two unique
terms each need one more rank unit. Those charges can instead be put into
the producer; moving their location does not remove them from the budget.

The five scalar forms c_S,c_T,z_C,z_S,z_T are independent for a fixed pair.
The original inputs x_S,x_T supply two independent central directions;
one source in each of the three side groups supplies the other three.
Thus the unique-term alignments cannot be omitted because their values
are zero or determined by the central terms alone.

There is a finite-geometry exception: L_S is degenerate at h=10, so its
orthogonal projector is not available there. If r is the coefficient vector
of u_j-u_a-u_b, the normal Gram determinant for q_S and G^(-1)r is

    2(10-h)/(9-h).

The ambient h=9 case is already excluded. The proposed projector schedule
is therefore restricted to h>=6 with h not in {9,10}. Exact controls use
h=6,7,11, and separately check the h=10 degeneracy. The retained h=23
case is nondegenerate; the general rank and span formulas apply to it.

This is a complete readout identity with its own aggregate-input contract,
not a complete producer. Its score is not a claimed improvement over the
modern shared producer. Even granting its producer for free, this particular
readout has no strict rank contraction when repeated across the output bank.

## 3. A forest bound that permits shared paths and cancellation

The stronger finding concerns the input side, independently of the tested
pair identity.

### Metric statement

Consider a finite directed acyclic graph whose vertices have rational frame
matrices M_v. Each paid edge e=(u,v) has rank charge at least

    dist(M_u,M_v) = rank_Q(M_v-M_u).

There are n source terminals with frames P_1,...,P_n, satisfying

    dist(P_i,P_j) >= 2 for i != j.

Every source can reach a designated frontier terminal. Every frontier frame
is at distance at least one from every source frame. Then the total paid
edge rank is at least n.

The graph may branch, share intermediate values and have arbitrary gate
arity. Internal matrices need not be projections, symmetric, or nested.
The statement concerns a rank-charged frame graph; a different edge
implementation not subject to these charges is a different contract.

### Proof

Restrict to vertices that can reach the frontier. Stop paths when they first
reach a frontier terminal. At every other relevant vertex choose one outgoing
edge leading toward the frontier. Keep the selected paths from all n sources.

The resulting graph has outdegree at most one and is acyclic. Its underlying
undirected graph is a forest. Its components share no edges; each contains
one frontier root and some k source terminals. This selection does not charge
a shared edge once per source.

Double the edges of one component and traverse it. The resulting walk visits
the k sources and its root with cost twice the component's edge-rank sum.
Shortcut between these terminals using the rank triangle inequality. A
terminal tour contains k-1 source-to-source steps, each of distance at least
two, and two source-to-root steps, each of distance at least one. Its cost
is at least

    2(k-1)+1+1 = 2k.

Thus the component's edge-rank sum is at least k. Summing over components
gives n. The forest uses a subset of paid edges, so the same lower bound
holds for the full graph.

### Why cancellation and zero workspace do not invalidate the application

Apply the bound to the finite scalar producer graph after deleting streams
that are identically zero. A nonzero scalar linear form in the independent
logical input arrays ranges over an arbitrary complete array, so its frame
transition is still charged by the retained interface. Zero initialization
does not give that nonzero value a free frame conversion.

If an original input has a nonzero coefficient in a required frontier sum,
there is a path from that input to the frontier through nonzero streams.
One can follow predecessors with nonzero coefficients backward to the input.
Cancellations on other paths do not change this fact. No claim that graph
reachability implies a nonzero coefficient is needed.

Consequently the bound permits cancellation DAGs and dependent copies. Its
assumptions exclude an address-restricted payload representation for which
a nonzero stream has a separately cheaper frame transition. Such a new
representation would need a different implementation and cost proof.

## 4. Application to the aggregate-producer proposal

Distinct triple lines give rank-one idempotents P_T. Their differences have
rank two: the two column vectors are independent, and their two dual vectors
are independent because G is nonsingular. Every P_T is at distance one
from frame zero.

The central point sums

    G_i = sum_(T contains i) x_T

use every original source. Therefore a producer delivering them at frame
zero satisfies the forest bound. The same conclusion holds if it instead
delivers all central output sums c_S at zero: their coefficient matrix has
nonzero diagonal, so every input participates. The scalar map need not have
full rank; mere participation is sufficient for this geometric bound.

Hence the producer costs at least n rank units, whatever sharing or
cancellation it uses internally. This includes its center readout calls;
they must not be charged a second time in the following sum.

With the separately specified n output moves of rank h-1,

    producer rank + output-readout rank >= n + n(h-1) = nh.

At an exponent sigma<1, for child width t<=h,

    (t/h)^sigma >= t/h.

So the normalized recursive moment is at least one. Ideal regrouping of
the same charged rank cannot make it strictly contracting. A new analysis
would need to change the interface or the underlying cost accounting.

At h=23 the n=1771 producer floor includes the previously reserved
h(h-1)=506 center rank units. The remaining producer work is therefore
at least 1265 rank units. The optimistic singleton profile allowed only
1253: it is short by 12. Even the rank-saturating profile with 1265
singletons has an exact moment greater than one at the 1/511 screen.
The proof is stronger than that particular profile comparison: any profile
respecting the stated rank charges saturates or exceeds capacity.

## 5. What has been closed, and what has not

This closes the proposed sequence:

1. Start from the retained distinct rank-one source frames.
2. Build a separate producer whose central outputs are in frame zero,
   potentially sharing all side computation and using clean scratch.
3. Apply the separately charged n rank-(h-1) central-to-output moves.

The producer edges and the subsequent output edges are disjoint parts of
this contract. If readout operations feed later producer work and are
genuinely shared, that separation must be rederived; their costs must not
be added twice. The current theorem does not exclude such an interleaved
operation graph. Nor does it exclude different central frames, different
source geometry, or a new noncoordinate primitive.

The older [cancellation audit](../../docs/research/cancellation-audit.md)
used edge-disjoint private diagonal paths in different all-role networks.
The new application does not assume such paths: its selected forest counts
shared edges only once, and its capacity is the useful clean input volume.
The difference in contract is essential to both the proof and the scope.

**Recommendation:** do not search for a better producer behind this unchanged
frontier. The next proposal would have to eliminate the common-zero central
frontier together with its separate output transport, or give a concrete
interleaving that shares their physical work. No example is presently
supplied, so this follow-up does not justify another broad search loop.

## 6. Reproduction, checks and provenance

```sh
python3 research/shared-aggregate-followup/audit.py --output research/shared-aggregate-followup/certificate.json
python3 -m unittest discover -s research/shared-aggregate-followup -p 'test_*.py' -v
```

Seven exact tests cover the paired scalar identity and physical frame paths,
the unique-span charge and degeneracy, source separation, a sharp star,
a genuinely shared cancelling DAG, and failures when source separation,
frontier separation or full source participation is omitted. Exact rational
root bounds check the old hypothetical profile against the new floor.

The [certificate](certificate.json) contains source hashes and finite controls;
[validation](validation.json) records reproduction and preservation. The
general forest and geometric arguments are written proofs supported by
those finite checks, not Lean formalizations or an independent audit of
the upstream multiplication theorem.

The triple scalar identity, rational metric, source frames, and shared
producer context are inherited from the repository's earlier work, including
the sources credited in the preceding design report. This follow-up supplies
the scoped forest application and the fully charged paired-readout diagnostic.
