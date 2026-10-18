# A checkable paired-diagonal lattice filter for dyadic Borel words

This is a decision interface for the obstruction in Sagar Thakrar's
[PR2613](https://github.com/CrocSwap/integer-mult-bounds/pull/2613), head
`ea9b811636934a4e5a4a81c1b292619ba6d9f2c9`. The first-order lattice method
already appears in eumemic's PR288 section1.4(a), and the rank functional is
credited there and in PR2613 to Swapnil Jain's P1. Neither the invariant nor
the difference-constraint algorithm is new here. The addition is an exact
certificate interface for one explicitly bounded class of analytic gauges,
with positive dyadic words and source-compatible failure boundaries.

## Decision theorem

Fix m>=1 and a finite list of rational 2m-by-2m matrices g_k, with H before D.
For a in Z^m put D_a=diag(2^a_0,...,2^a_(m-1)) and B_a=diag(D_a,D_a).
For every nonzero entry g_k[i,j] add the directed edge

    j mod m -> i mod m, weight v2(g_k[i,j]).

The entry's matrix index, row and column are retained. Multiple edges and
self loops are allowed. Zero entries impose no constraint. Then exactly one
of the following holds:

1. There is an integer potential a satisfying every edge inequality
   a_(i mod m)-a_(j mod m)<=v2(g_k[i,j]). Every B_a^-1 g_k B_a is 2-integral.
2. There is a directed cycle of strictly negative total weight. No such
   common paired-diagonal gauge exists.

These alternatives are exhaustive **only in this gauge class**.

Proof: the transformed entry is g_k[i,j]*2^(a_(j mod m)-a_(i mod m)). Its
valuation is nonnegative exactly when the displayed inequality holds.
Adding inequalities around a negative cycle gives 0<0, a contradiction.
Conversely, adjoin a source with a zero-weight edge to every vertex. If
there is no negative cycle, a minimum-weight path to each vertex exists:
any repeated-vertex cycle can be removed without increasing its weight,
so a simple path suffices. Its integer distances obey every edge inequality.
Subtracting a_0 from every distance fixes a_0=0 without changing any entry.
This proves feasibility and completeness. Bellman-Ford constructs a potential
or a predecessor cycle; the separate checker verifies the returned evidence
directly, without trusting the search. The certificate contains m integers or
at most m entry indices. With E nonzero entries the standard graph procedure
uses O(mE) relaxations and O(m+E) storage, apart from exact integer bit costs.

## Applying the existing floor

Use the exact PR2613 formal model: R scalar roles over F2[G], arbitrary
free GL_R(F2) mixing, rational invertible block-lower register maps, and paid
I+xy^T([n_A]-1), where n_A=[[I,A],[0,I]], at cost rank_Q(A).
Only a designated W-by-W data block at the final endpoint is required to
be a block-permutation of single group elements. Auxiliary blocks may be
unconstrained as in that source. A dirty-restored auxiliary claim would
require its additional endpoint identity and is not silently assumed.

Apply the same B_a to every role. Conjugation is a group automorphism of
the rational matrix group, hence gives an automorphism of its F2 group
algebra and of the role matrix algebra. It commutes with scalar mixing.
It preserves block-lower free maps and maps each paid shear to
n_(D_a^-1 A D_a), with exactly the same rational rank. Every matrix actually
applied, including an inverse if it occurs, must appear in the constraint
list. Inverses that are never applied need not be integral.

Consequently a feasible potential puts this complete word in PR2613's
2-integral monoid algebra. Entrywise natural reduction to F2 and the rank
of the all-H/all-D block give

    sum_paid rank_Q(A_j) >= sum_data rank_F2((B_a^-1 g_w B_a)_HD).

For clarity, the argument is self-contained: reduction is multiplicative
on the monoid of integral applied matrices; the HD block of a product is
Y_HH Z_HD+Y_HD Z_DD, whose rank is at most the sum of the two HD ranks.
Free factors have zero HD block. A paid factor has HD block xy^T tensor Abar,
of rank at most rank_Q(A). The final data submatrix gives the lower bound
regardless of the other auxiliary entries. Reduction can be singular on a
free matrix; invertibility after reduction is not required.

In particular B_a^-1 n_I B_a=n_I, so W n_I targets force the sharp mW floor.
More generally, a data target with HD block C becomes D_a^-1 C D_a. Its
determinant is unchanged. Once the transformed entries are integral, it
is a unit block precisely when v2(det C)=0. **Feasible integrality alone
does not imply the target-unit condition.** The paid moment consequence
is the existing one: for 0<=s<=1 and ranks 1<=r<=m,
(r/m)^(1-s)>=r/m, so (1/W)sum n_r(r/m)^(1-s)>=1 on unit targets.

B_a is an analytic basis change in this argument. We do not execute it,
declare it a free native operation, or provide a physical implementation.
The consumer of a certificate is the lower-bound test on a proposed word,
not a compiler that can omit a physical cost. Complete endpoint equality,
model membership and target admission are separate required inputs.

## A nontrivial admitted dyadic word

Let m=2 and

    A1=[[1,-1/2],[0,0]], A2=[[0,1/2],[0,1]],
    K=[[0,1/2],[2,0]], L=[[I,0],[K,I]], J=diag(2I,I).

A1,A2 each have rank one and sum to I. They are the two conjugated
coordinate projectors for S=[[1,1/2],[0,1]]. The gauge a=(0,1), equivalent
up to a common shift to (-1,0), makes all five applied matrices
n_A1,n_A2,L,L^-1,J integral. Both upper paid frames and the lower-left
free update genuinely contain even denominators in the original basis.

On two data roles and one arbitrary auxiliary role, start with the free
scalar XOR role0+=role1. Apply L to both data roles, n_A1 then n_A2 to each,
then L^-1 to both, and undo that scalar XOR. Finally apply J to the auxiliary.
Chronological left multiplication gives diag(g,g,J), where g=L^-1 n_I L.
The scalar XOR cancels because both data operators are the same. The HD
block of g is I. There are four paid rank-one calls, attaining mW=4.
J is rationally invertible but singular modulo two after conjugation,
exercising the source's allowed singular-free boundary. Its auxiliary
output is unconstrained, not claimed restored.

The checker expands the entire three-role formal group-algebra map,
checks every off-diagonal entry is zero, checks the auxiliary map, and
compares the original and conjugated endpoints. It does not infer a formal
identity from an unfaithful finite address representation.

## Rejected shortcuts and exact limits

The source's half frame n_(1/2) and its commutator using
d=diag(2,1), d^-1=diag(1/2,1) each have a negative self loop. Their exact
source formulas are retained and checked; the negative answer is specific
to paired gauges. A two-coordinate example n_(E01/2), n_(E10/2) has a
negative two-cycle although each matrix separately admits a paired gauge.
One common potential is essential for scalar mixing between roles.

Allowing unrelated H/D scalings can clear n_(1/2): B=diag(1/2,1) sends it
to n_1. But it also sends the required n_1 target to n_2, which has zero
HD rank modulo two. This cannot justify a unit-target floor. Likewise,
entrywise clearing of even denominators changes rank-one
[[1,1/2],[2,1]] to the rank-two matrix [[1,1],[2,1]]; it is not similarity.
The integral target n_(2I) is another control: a potential exists, while
its reduced HD block is zero. No mW admission is returned for it.

Negative cycles do not exclude non-diagonal lattices, more general paired
changes of basis, or other first-order representations. They imply neither
a saving nor an impossibility outside this class. This package neither
maps the selected supplier into the model nor searches for a new supplier.
It is a local analytic filter for the PR2613 dyadic handoff.
