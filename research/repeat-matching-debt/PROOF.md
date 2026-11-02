# Matching balance with repeated visits

This scoped proof was produced by Nick Petalas. Apache-2.0.

## Statement

Let n>=2, choose a coordinate v, and put

    f(x) = sum_{i != v} x_i mod 2.

Let q_0,...,q_L=q_0 be a closed walk in Q_n. Every step flips exactly
one coordinate. Repeated vertices and repeated edges are permitted. Count
the L positions q_0,...,q_(L-1), excluding the final closing occurrence.
Let V be their distinct support. Assume V meets at least two pairs of
the coordinate-v matching. No universality assumption is needed.

For j=0,1, let s_j be the number of vertices of V with f(x)=j, m_j the
number of coordinate-v edges whose two endpoints both lie in that class
of V, and R_j the number of occurrences in that class beyond its s_j
distinct vertices. Put c_j=s_j-m_j. Then

    R_0 >= max(0, c_1-s_0),
    R_1 >= max(0, c_0-s_1).                         (1)

Consequently, with D the sum of the two right sides,

    L-|V| >= D,
    L-|V| == |V| mod 2.                            (2)

The congruence uses the fact that Q_n is bipartite, so L is even. Thus
one may round D upward to the next integer of the parity of |V|.
These are necessary conditions and need not imply a completion.

## Proof of the bounds

Contract every coordinate-v matching edge in the entire cube. Each pair
becomes one quotient vertex. Its color f is well defined, and every
remaining edge changes that color. An occupied quotient vertex contains
one or two vertices of V. A fully occupied pair saves one quotient vertex
relative to s_j, so there are exactly c_j occupied quotient vertices of
color j.

Delete the stationary steps from the projected closed walk. Since V
meets at least two matching pairs, the resulting closed walk has a
positive number C of edges and visits every occupied quotient vertex.
Every visited vertex of a nonempty closed walk has at least one arrival
and one departure, counting edge multiplicity. Each crossing edge has
exactly one endpoint of each color. Therefore

    C >= 2c_0,    C >= 2c_1.

In the original walk there are a_j=s_j+R_j occurrences of color j.
Each contributes two incident edge occurrences. Every projected edge
uses one incidence in each color, whereas a stationary step contributes
no crossing incidence. Hence

    C <= 2a_0,    C <= 2a_1.

Combining the lower bound from the opposite color with these upper
bounds gives c_1<=s_0+R_0 and c_0<=s_1+R_1. This proves (1).
Summing proves the inequality in (2). Bipartiteness proves its congruence.

The two-pair hypothesis matters. A two-step walk on a single matching
edge has s_0=2,m_0=1,s_1=0 and no repetitions, contrary to the proposed
bound if that hypothesis were removed. Such a support is rejected by
the executable interface rather than silently treated by the formula.

For a simple cycle R_0=R_1=0, so (1) implies c_0<=s_1 and c_1<=s_0.
Since m_j<=floor(s_j/2), this includes the familiar s_0<=2s_1 and
s_1<=2s_0 simple matching balance. The new bounds retain actual occupied
pairs and quantify how repeats pay for imbalance.

## Prefix corollary with a prescribed final support

Fix V, L and a prefix q_0,...,q_(k-1) contained in V. It may repeat.
Let r_j be the prefix's occurrence count in class j minus its distinct
count in that class. For any completion visiting exactly V,

    ell_0 = max(r_0, 0, c_1-s_0),
    ell_1 = max(r_1, 0, c_0-s_1),
    ell_0 <= R_0 <= L-|V|-ell_1.                    (3)

Each repeated occurrence already in the prefix remains a repeated
occurrence in any extension. Apply (1) as well, then use
R_0+R_1=L-|V|. An empty interval in (3) rejects that specified completion
support. A nonempty interval leaves all other walk conditions open.
The support V must be prescribed or independently bounded. Substituting
the current partial support for an unknown final support is unjustified.

## An unbounded attaining family

For k>=1 use coordinates 0,1,...,k and omit coordinate 0. Set

    V_k = {0,e_0} union {e_i,e_i+e_0 : 1<=i<=k}.

This is a book of k squares sharing edge {0,e_0}. Its distinct size is
2k+2. Class zero consists of the two hubs, so s_0=2,m_0=1,c_0=1.
Class one consists of the leaf pairs, so s_1=2k,m_1=k,c_1=k. For k>=2,
the bound is R_0>=k-2 and R_1>=0. For k=1 both right sides are zero.
Since |V_k| is even, the minimum permitted repetition total is

    0                       if k=1,
    k-2+(k mod 2)            if k>=2.

Traverse the k paths

    0 -> e_i -> e_i+e_0 -> e_0

in alternating orientations. If k is odd, close by the shared hub edge.
For even k the last path already returns to zero. The resulting walk
visits exactly V_k and has length 3k+(k mod 2). It attains the rounded
bound in every k>=1. Thus the minimum length among closed walks with
exactly this support is 3k+(k mod 2). Embedding the support in a larger
cube preserves the argument if the visited support remains V_k.

No universal prefix-cover property is asserted for this family. Its role
is to show that the repeat-aware bound has sharp, arbitrarily large debt.
The contribution stops at this lemma and prefix corollary; it supplies
neither an unknown-support completion algorithm nor a census integration.
