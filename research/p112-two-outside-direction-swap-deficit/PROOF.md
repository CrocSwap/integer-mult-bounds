# Two outside directions remove the RDEP2 swap deficit

This is a source-level theorem about the two-sided K1 accounting in
DreamingOfClouds' PR3154, pinned at
708f0ad8928c383de8294aea3c126e9461d2066d, checks/RDEP2/NOTES.md.
It does not prove K1, C(P112)>=64, or a multiplication bound. The one-sided
K2 ledger subsequently closed by C6/C7 is a different problem.

## Exact premises and source boundary

Let T be the finite set of distinct swap root lines used in RDEP2 §1:
T_D union T_X, counting a line once. Let lambda_1,lambda_2 be the two
outside directions, over the source coefficient field K. Put
P(v)=(lambda_1(v),lambda_2(v)) and S_a={v:lambda_a(v)!=0}.
The proof works over any field K, independently of the binary label field.
We require:

1. P(v) is nonzero for every v in T.
2. For every v in T, there is a linear functional f_v:K^2->K such that
   f_v(P(v))!=0 and f_v(P(w))=0 for every w in T orthogonal to v.
3. A pairwise nonorthogonal subset of T has independent binary labels.

Premises 1 and 2 are stronger than merely requiring different classes on
adjacent roots. RDEP2 supplies them explicitly: §1 constructs
 o_j=p_j-C'x_j=sum_a omega_j[a] lambda_a
with o_j(v)!=0; §2 states supp(o_j) intersect O_{u_v}={v} and
v^perp subset O_{u_v} minus {v}. Taking f_v(z)=sum_a omega_j[a]z_a
proves 2. We retain the original source's hypotheses for these swap
identities. In particular this does not audit all imported catalogue,
normal-form, SU, or pivot claims.

Premise 3 can be verified directly for the actual pinned P112 geometry,
without importing Pay(a) as an additional theorem. The 112 raw E8 roots
r_v have squared norm 8. Its nine-bit labels ell_v and dual labels d_v obey
 d_v dot ell_w = 1 + (r_v dot r_w)/4 (mod 2).
For distinct nonorthogonal root lines, the scalar quotient is +1 or -1,
so this binary pairing is zero; on the diagonal it is one. Consequently
for a pairwise nonorthogonal V, the matrix (d_v dot ell_w)_(v,w in V)
is the identity. Applying each d_v to a linear dependence proves every
coefficient zero. The checker validates all 12544 pairings against the
pinned actual geometry. The finite identity supports this implication;
it is not a finite search for the theorem below.

## Separator graph lemma

Construct the simple undirected graph G on T whose edges are orthogonal
pairs. Projective equality means nonzero scalar proportionality in K^2.
For any vertex v with a neighbor, f_v is nonzero and its kernel is a
one-dimensional subspace. All neighbors of v lie on that same projective
line, which differs from the class of v because f_v(P(v))!=0.
Thus every walk of length two has endpoints in the same projective class,
and adjacent vertices have distinct classes.

There is no odd cycle: following length-two steps around an odd cycle
would identify the classes of adjacent vertices. Each nontrivial connected
component is therefore bipartite. Choose either bipartition (A,B).
Every two vertices in A are joined by an even path, so all of A has one
projective class p; similarly B has one class q, with p!=q. The component
need not be complete bipartite. The same class may occur in several
components, which can be oriented independently.

## Membership-compatible partition

Define L(v)={a in {1,2}:P(v)_a!=0}. Each class has a constant nonempty
list. The only class with list {1} is [1:0]; the only class with list {2}
is [0:1]. In a nontrivial component with distinct side classes p,q,
choose different colors 1 and 2 for its sides within their lists:

- if both lists are singletons, they differ;
- if one is a singleton, give its required color and the other side the
  other color, which is allowed;
- if neither is a singleton, either orientation works.

The impossible pattern is two distinct classes with the same singleton
list. Isolated vertices receive any color in their nonempty list.
Let V_a be all vertices of color a. Then T=V_1 disjoint-union V_2,
V_a subset T intersect S_a, and V_a contains no orthogonal pair.
The latter holds both within components by bipartiteness and across
components by the definition of a connected component. By premise 3,
 rank_ell(T intersect S_1)+rank_ell(T intersect S_2)
 >= |V_1|+|V_2| = |T|.
Therefore delta_row=0 in RDEP2, for the entire s=2 class, with no bound
on the number of projective classes, coefficient sizes, or |T|.
The empty T case is immediate. The same argument with the original
column-side symbols proves delta_col=0 when t=2.

## Consequence and limits

In the source's DR-prime inequality, set delta_row=0 when s=2 and
set delta_col=0 when t=2. If s=t=2 both disappear. All F_row,F_col,
O,O-prime, XM and SH debits remain. SU on both sides, disjoint pivot
sets and every other original DR-prime import remain required. No
extension to s>=3 is claimed: a nonzero functional on K^s then has a
higher-dimensional kernel, so the single-neighbor-class step fails.

This strengthens RDEP2's sufficient coloring of the graph of whole
projective classes: a class may now split between colors in disconnected
root-graph components. The source-derived six-root control uses indices
0..5, labels 161,97,177,113,185,121 and actual frame-coordinate rows
X_0..X_5. Its orthogonality graph has edges 01,23,45. Giving these vertices
classes e1,e2,e2,e1+e2,e1+e2,e1 makes the whole-class graph a triangle,
while the component partition is valid. This is a root-geometry control
for the implication, not a complete decoder realizing prescribed lambdas.

Prepared by JoyboyBrian with substantial OpenAI Codex (Astra) assistance.
Source attribution: DreamingOfClouds for PR3154 and PR717; Mihir Srivastava
for the exact retained p112-single-lift geometry package. No proof-assistant
or independent human verification is claimed.
