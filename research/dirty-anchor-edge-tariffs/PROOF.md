# Exact edge-dependent price of dirty-output fanout

## Contract and theorem

Let q,w>=1 be finite. There are exactly q required output rows, initially
independent arbitrary a_i in F2^w. A fixed finite straight-line word may use

* ADD(i,j): A_i ^= A_j, i!=j, at finite stationary complete price c_ij>0;
* P_i: A_i ^= p, at finite stationary complete price mu_i>0.

The ordered pair c_ij denotes the arc **j->i**. The same arbitrary value p
comes from preserved read-only sources disjoint from all output rows. The
word must work uniformly for all p and all entry dirt, and finish with
A_i=a_i+p. There is no other row, clean helper, COPY, CLEAR, free basis
change, adaptive control or intermediate caller observation. Every ADD and
every complete oracle is paid, with arbitrary order and multiplicity allowed.

If required, independent arbitrary values t_i have complete calls
T_i: A_i ^= t_i at finite stationary prices nu_i>0; the endpoint then is
A_i=a_i+p+t_i. Those calls may interleave arbitrarily with all others.

For nonempty O, let f(O) be the minimum sum of c_ij over directed spanning
forests rooted exactly at O. Each nonroot has one parent and is reachable
from its component's root; roots have no incoming forest edge. Then

    C* = min_nonempty_O [sum_{i in O} mu_i + 2 f(O)].             (1)

With the private values, add exactly sum_i nu_i. This is the optimum over
**all allowed straight-line words**, not just two-wave words or forest
constructions. The proof uses the finite disjoint-branching theorem stated
below. It establishes an algebraic tariff result, not a physical supplier or
a new multiplication exponent.

## Lemma 1: every oracle-free cut needs two incoming ADD occurrences

Take a successful word and let O be the actual set of P destinations. It is
nonempty because the endpoint depends on arbitrary p. Fix a nonempty S
disjoint from O. An incoming ADD has its destination in S and source outside
S. Outgoing ADDs and feedback are unrestricted.

Zero incoming ADDs are impossible: specialize all private t_i to zero. The
p coefficients in the S rows start at zero. Internal ADDs preserve this
property, outgoing ADDs do not change S rows, and no P occurs in S. They
cannot end with coefficient one on p.

Exactly one incoming ADD is also impossible. For this separate argument,
project every row onto the q independent entry-dirt symbols, equivalently
specialize p and all t_i to zero. The matrix M starts at I. Every prefix is
invertible: row ADDs are elementary invertible operations and all oracle
calls leave M unchanged.

Before the sole incoming gate, the S-row span is the coordinate subspace
W_S=span{e_i:i in S}. Internal ADDs preserve this span; all outgoing gates
leave its rows unchanged. Immediately before j->i, the outside source row
m_j lies outside the span of the S rows because all q rows form a basis.
This remains true even if earlier outgoing gates have given m_j components
from S. Replacing m_i by m_i+m_j changes the S-row span: if the new span
were W_S, both m_i and m_i+m_j would belong to W_S, forcing m_j into W_S.

After that gate, internal ADDs preserve the changed span and outgoing gates
leave it unchanged. There is no further incoming ADD. The final identity
dirt matrix would give span W_S, a contradiction. Hence there are at least
two incoming **occurrences**, for every nonempty S disjoint from O.

The zero-incoming argument uses arbitrary p. The exactly-one argument uses
the zero-p dirt projection. They must not be conflated. A clean-output-only
test would not establish this lemma.

## Lemma 2: cuts force two paid directed forests

Use the following standard finite theorem, credit Jack Edmonds,
*Edge-disjoint branchings*, Combinatorial Algorithms (1973), pp. 91-96:
given nonempty prescribed root sets R_1,...,R_k in a finite directed
multigraph, there are k arc-disjoint spanning branchings with those root
sets if every nonempty S has at least as many incoming arcs as prescribed
root sets disjoint from S. Necessity also holds. A branching is a forest
of outward arborescences. Parallel arcs count separately.

The precise finite statement and multigraph conventions are recorded in
Attila Joo, [Edmonds' Branching Theorem in Digraphs without Forward-infinite
Paths](https://arxiv.org/pdf/1705.00471v1), printed pp. 1-2. Only the finite
theorem is used. Its proof is an external mathematical dependency; it has
not been formalized or replaced by the finite checker here.

Build the directed occurrence multigraph of the word: every ADD(i,j) gives
one distinct arc j->i of weight c_ij. Use k=2 and R_1=R_2=O. Lemma 1 supplies
the theorem's cut condition for S disjoint from O; for S meeting O the
required lower bound is zero. Thus there are two occurrence-disjoint
spanning forests B_1,B_2 rooted exactly at O.

Their occurrences are disjoint and prices are positive, so

    ADD bill >= cost(B_1)+cost(B_2) >= 2 f(O).

Each i in O receives at least one P call, costing at least mu_i. Extra
calls can cancel in the common-value map but still cost positively. Every
successful word therefore costs at least the bracket in (1) for its actual
O, and hence at least its minimum. This packing is a lower-bound witness;
the forests need not occur as chronological subwords.

If independent private values are required, every t_i must be inserted by
at least one T_i. Setting t=0 leaves the preceding lower bound valid and
the actual private-call costs add at least sum_i nu_i.

## Lemma 3: an exact attaining word and its inverse

Choose any directed rooted forest F and roots O. Execute the forest ADDs
in children-before-parents order, for example by decreasing depth. Call
P once on each root. Execute the preparation ADDs in literal reverse
order. If needed, finish with one T_i on every row.

When a parent is used during preparation, it still holds its original
a_parent: its own ADD, if any, occurs later. Thus preparation maps each
nonroot i to a_i+a_parent(i), and leaves every root unchanged. Root calls
give a_root+p. The reverse pass visits parents before children; induction
then gives

    (a_i+a_parent)+(a_parent+p) = a_i+p.

Every row has its own entry dirt plus the common value, and private calls
give the t_i endpoint. Each edge has been paid twice at its same directed
price; no scratch or oracle uncompute is hidden. The total equals the
bracket in (1), plus the private bill. Minimize over forests to prove (1).

Every admitted gate is an involution, including a complete P or T because
its read-only sources are preserved. The exact inverse reverses the entire
word, including the private calls, and has the same bill. If a caller
requires this inverse as another stage, it must pay that stage too.

## Exact graph optimizer and earlier special cases

Add a graph-only vertex s, arcs s->i of weight mu_i, and arcs j->i of weight
2c_ij. Spanning outward arborescences rooted at s correspond exactly to
the forests in (1): delete s and its outgoing arcs to get the component
roots. Thus the optimum is also the minimum directed spanning-arborescence
weight in this augmented graph. The graph-only vertex is not a free
physical helper. Standard graph algorithms can optimize it; this package's
executable uses bounded enumeration and makes no all-size tape-runtime
claim for an optimizer.

When c_ij=alpha_i independently of j, f(O)=sum_{i notin O}alpha_i:
every nonroot needs one incoming edge and a star from any root attains it.
Equation (1) recovers PR3063's destination-only subset formula. With uniform
prices and exactly r root calls, it gives r*mu+2(q-r)*alpha. Hence the old
homogeneous endpoint comparison remains intact.

General edge prices can make a deep forest much cheaper than all stars.
For q=3, let mu=(1,100,100), c_10=c_21=1, and every other c_ij=100. The word

    ADD(2,1), ADD(1,0), P_0, ADD(1,0), ADD(2,1)

uses 0->1->2 and costs 5. It is optimal: any other root costs at least 100;
with O={0}, any forest needs two edges of price at least one. Direct calls
cost 201; the cheapest single-root star costs 203; even allowing several
root stars, the best height-one forest costs 103. The strict gap tests
routing structure under declared complete prices, not measured hardware.

## Scope, scientific decision and remaining obligations

This all-q, all-w statement is a written proof using Edmonds' finite theorem.
The executable finite domains corroborate its ingredients and test defects;
they do not supply the all-parameter quantifiers or a formal-kernel proof.
An independent automated specialist rederived the argument; no independent
human review is claimed.

Complete stationary tariffs must include legal operand/source access, frame
adapters, routing, precision, scratch restoration, dispatch and physical head
return, as applicable. Prices cannot be reused when path, time, aliasing or
frame state changes them. This result permits only the exact XOR alphabet
and uniform arbitrary p and independent dirt. Extra helpers, correlated
private values, changing sources, adaptive words, other coefficient rings,
intermediate observations or relaxed output frames change the model.

If the c_ij(n), mu_i(n), nu_i(n) are proven complete costs for one legal
recursive caller at width n, (1) applies pointwise. A supplier or exponent
comparison still requires all changed child ranks, helper/idle stock,
precision, hosting and both supplier moments in their actual outer contract.
No such physical mapping is asserted; scalar savings or the tariff witness
alone do not establish a kappa improvement.

Stop after this completed local theorem and its source-bound checks. The
next useful experiment is a named operand-compatible caller with legal
unobserved target lifetimes and a complete directed tariff matrix. Do not
start another abstract fanout census in lieu of that physical obligation.

## Attribution

PR3063, Ross Richardson, head 3f384b8b7daccb2c8e12013fd81a738202ce0f8d,
provides the one-row dirt projection and destination-only optimum. It builds
on Cinna Davis/PR1944's single-common-child echo; PR1968 retains credit for
several different common terms accumulated before fanout. Anthony/PR774 and
Oscar Fennell/PR759 give earlier forest compensation synthesis, with the
tree-synthesis literature credited in their sources. This is not a priority
claim for forest synthesis or graph optimization. The added implication is
the subset cut plus branching lower bound for unrestricted edge-priced
words in this narrower single-common-value contract.

New proof/checker by Ross Richardson with substantial OpenAI Codex
assistance (GPT-6.1 Sol, Max), Apache-2.0. Exact repository source pins are
in SOURCES.json. The external graph theorem and original sources retain
their authors' attribution; no third-party code is copied.
