# Exact unequal-width capacity of theta(2,3,3)

JoyboyBrian, with substantial OpenAI Codex assistance; Apache-2.0. Credit the
query-factor contract of Tekalign #3362, Nick Petalas #4909, JoyboyBrian #5023,
and the classical Tutte–Berge matching theorem. No literature-priority claim
is made for matching duality or index-coding methods.

## Contract

The seven vertices, in implementation order, are (u,v,a,b,c,d,e). Edges are
ua,av,ub,bc,cv,ud,de,ev: three internally disjoint paths of lengths2,3,3.
For arbitrary nonnegative integers d_i and any field F, let M have diagonal
blocks I_(d_i), zero ordered blocks on every distinct nonedge, and arbitrary
rectangular ordered edge blocks. Symmetry, invertibility of edge blocks,
commutation and simultaneous scalar-coordinate decomposition are NOT assumed.
Put S=sum d_i and

    nu_b(d)=max {sum_edges x_ij : x_ij nonnegative integers,
                               sum_(j adjacent i) x_ij <= d_i}.

Then the exact minimum rank is S−nu_b(d). In particular arbitrary block
mixing cannot outperform integral edge/private coordinate sharing on this
specified overlapping-cycle mask. This is an exact linear-query dimension
contract, not a physical COPY tariff, native supplier or multiplication bound.

## 1. A half-total bound, including zero widths

Factor an arbitrary fit M=AB through r=rank M coordinates. Write B_i for
its column block, A_i for its row block, and U_i=im B_i. The identity diagonal
makes B_i injective, dim U_i=d_i, and A_i injective on U_i. For each nonedge ij,
A_i annihilates U_j. In particular an independent vertex set has a direct sum
of column spaces: apply the separate A_i to any putative relation.

Set L={u,c,e} and R={v,b,d}. Each is independent. The induced graph on L union
{a} is just the edge ua plus isolated vertices c,e. Applying A_c and A_e to
a relation shows their spaces are independent of U_u+U_a and each other.
Consequently

    r >= sum_(i in L) d_i + d_a − t_u,
    t_u=dim(U_a intersect U_u).

The same argument on R union{a} gives r>=sum_R d_i+d_a−t_v, with
 t_v=dim(U_a intersect U_v). Vertices u,v are nonadjacent, so U_u intersect
U_v=0. Therefore the two intersections inside U_a are disjoint, and
 t_u+t_v<=d_a. Adding yields 2r>=S+d_a−t_u−t_v>=S.
Thus r>=ceil(S/2). This argument is unchanged when any widths are zero.
It does not count the two C5 subgraphs independently or assume their shared
path can be used twice without an invoice.

## 2. Every induced coordinate restriction

Form the finite independent-copy blowup H(d): its vertices are individual
payload coordinates (i,t), 1<=t<=d_i. All copies of a fixed vertex are pairwise
nonadjacent; between different groups all edges are present precisely on
an edge of theta. M, viewed in scalar coordinates, fits H(d): its diagonal
blocks are identity, including off-diagonal zeros inside a group.

Delete ANY subset Z of scalar coordinates. Within each original group keep
its remaining coordinates in their original order. The resulting principal
submatrix has exactly the same block contract with reduced widths d'_i.
Section1 applies. More particularly, restrict to one connected component C
of H(d)−Z: retain only the coordinates in C, set all other widths to zero,
and apply Section1 again. Its rank is at least ceil(|C|/2).

This does not assume arbitrary matrices preserve coordinate subspaces.
Only principal submatrices and the originally imposed identity blocks are
used. Distinct components have both ordered off-diagonal blocks zero, so
r>=rank M[V\Z,V\Z] is at least the sum of these component bounds.

## 3. Matching duality supplies the complete lower bound

We use the classical Tutte–Berge formula as a cited theorem, not a new result:
for a finite graph H on S vertices, with o(H−Z) odd components,

    nu(H)=min_Z (S+|Z|−o(H−Z))/2.

A standard proof is available in Alexander Schrijver's
[The Tutte–Berge formula](https://homepages.cwi.nl/~lex/files/tutteb.pdf);
original attribution is Tutte1947 and Berge1958. This standard graph theorem
is the only external matching premise, and is not formalized here.

Choose a set Z attaining that minimum. Section2 gives

    rank M >= sum_C ceil(|C|/2)
           = (S−|Z|+o(H−Z))/2 = S−nu(H).

A matching in H assigns disjoint coordinate pairs to original edges and hence
integer counts feasible for nu_b. Conversely any feasible counts can be
realized by selecting distinct coordinates at each incident edge: the capacity
inequalities ensure enough coordinates. Thus nu(H)=nu_b(d), proving the
required lower bound, including S=0, disconnected supports and partial copies.

## 4. Attainment and finite constructive algorithm

For each matched coordinate pair put the rank-one2-by2 all-ones block on
that pair. On every unmatched coordinate put a scalar1. The resulting direct
sum has rank exactly S−nu_b over EVERY field (including characteristic2),
identity diagonal groups and zeros on every forbidden ordered pair. This
provides a full matrix, not merely a dimension count.

The implementation computes counts without materializing H. For a residual
width tuple w, choose its first positive entry i. One selected copy of i is
either unmatched or paired to some neighbor j with w_j>0. Thus

    f(w)=max(f(w−e_i), max_j [1+f(w−e_i−e_j)]), f(0)=0.

Conversely each option gives a legal matching, proving equality by induction
on total width. Store a deterministic maximizing choice and backtrack to
produce all edge counts and private counts. The code uses an explicit stack,
so there is no recursion-depth cap masquerading as a width restriction.
There are at most P=product_i(d_i+1) states and at most4 successors per state.
The deliberately elementary constructor uses O(P) seven-integer records,
O(P) transitions, and O(S) backtracking steps. Integer bit costs and matrix
expansion are additional; it is not polynomial in encoded width length.
No physical efficiency or compressed-polylogarithmic implementation is claimed.

## Scope and stopping boundary

The half-total argument is the new mask-specific ingredient; Tutte–Berge
promotes it to the entire unequal-width endpoint, rather than only uniform
widths. #5023's single-cycle rotating proof does not establish this shared-path
bound. #5180's equality classification concerns one cycle, not this mask.
The theorem stops at theta(2,3,3). No classification of minimizers, wider theta
families or arbitrary triangle-free graphs follows. Source preparation,
physical reads/copies, frames, dirty restoration, ownership, finite precision,
fixed tapes, compiler and outer transfer remain unpriced and outside scope.
