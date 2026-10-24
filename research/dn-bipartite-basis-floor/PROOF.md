# Exact floor under a bipartite change of factor basis

Let G be any finite simple graph on vertices 1,...,n. Isolated vertices
are allowed. For every edge {i,k}, i<k, retain both rational root rows
e_i+e_k and e_i-e_k. Let R be their matrix and v=2|E(G)| their number.
Scaling all roots by two gives the convention of PR2536 and changes no
support or binary pairing condition.

A fitting pairing B is a v-by-v matrix over F2. It has B_ss=1, and
B_st=0 whenever distinct root rows s,t have nonzero rational inner
product. The other directed entries are independent. In particular,
symmetry is not required. The cost of an exact factorization P Q^T=R R^T
is

    C_B(P,Q) = sum_j rank_F2 B[supp(P_j), supp(Q_j)].

Only this algebraic support cost is considered. A pairing is not a
physical implementation or a statement about its full recursive bill.

## Theorem

Partition the coordinates as A disjoint-union D. Choose any rational
matrix N whose nonzero entries have row in A and column in D. Put

    M=I+N,    P=R M,    Q=R M^(-T)=R(I-N^T).

For every such N and every graph G,

    min_(fitting directed B) C_B(P,Q) = 2|E(G)| = v.

The same minimum holds if B is required symmetric. In fact one fixed
symmetric pairing attains it for every N. Every single elementary
rational shear I+t E_ab, a!=b, is included, as is any finite product of
shears with all sources/targets in this same fixed bipartition.

## Exactness and anchoring

There cannot be two consecutive nonzero entries N_ik N_kj, since k would
belong to both D and A. Thus N^2=0, and (I+N)^(-1)=I-N. It follows that
P Q^T=R(I+N)(I-N)R^T=R R^T.

For j in A, the jth column of M is e_j, so P_j=R e_j. The jth column
of I-N^T has jth entry one. For j in D, the jth column of I-N^T is e_j,
so Q_j=R e_j, and the jth column of M has jth entry one. Thus each term
has one coordinate factor R e_j; its other factor is R z with z_j=1.

For an edge {i,k} incident to j, the two values of R z are z_i+z_k and
z_i-z_k. They cannot both vanish: adding and subtracting would force
z_i=z_k=0 over Q, contradicting z_j=1. Consequently the two factor
supports intersect in at least one root on every edge incident to j.

## A forced identity minor

Let d_j be the degree of vertex j. Select one surviving common-support
root for each of its incident edges. Two selected roots from distinct
edges have inner product +1 or -1, since their edges meet exactly at j.
Both directed pairing entries between them must therefore be zero.
Their diagonal entries are one. These selected rows and columns form
I_(d_j), a principal submatrix inside the term's support rectangle.
Hence that term costs at least d_j for every fitting B.

Summing gives C_B(P,Q)>=sum_j d_j=2|E(G)|. This argument permits
arbitrary entries at disjoint edges, arbitrary mate entries and asymmetric
B. It neither assumes rank is monotone under entry deletion nor uses a
predecessor's dense-pairing rank formula.

## One pairing attains every bound

Let B_* be block diagonal by graph edge, with a 2-by-2 all-ones block
on its two sign roots. It is fitting: the two signs on one edge are
orthogonal, and zero is allowed at every pair of distinct edges. B_* is
symmetric.

For term j, its coordinate factor contains exactly the two roots on each
edge incident to j. The other factor contains at least one root on each
such edge. The support rectangle of B_* therefore has one nonempty
all-ones block for every incident edge, and no other nonzero blocks.
Each block has binary rank one, so its total rank is d_j. All terms
simultaneously attain their lower bounds. The empty graph and isolated
vertices contribute zero and need no separate construction.

Finally, if N_1 and N_2 have this same bipartite support, N_1 N_2=0.
Products of their elementary shears equal I+sum N_i. This proves the
finite-product assertion without extending it to changing bipartitions.

## What is new and what remains

ywz65's PR2536 establishes the coordinate-basis optimum for arbitrary
Dn punctures and fitting pairings. Its first open question asks about a
basis change, beginning with an elementary shear. Here both signs on
every retained edge are required, but the basis is allowed every rational
bipartite shear. PR2719 permits arbitrary root-code factors for the full
Dn configuration with one fixed dense pairing. It does not optimize the
pairing after deleting paired edges. These are different quantified models.

DreamingOfClouds's PR3045 already proves a stronger arbitrary-basis
variable-pairing floor for full D4. That special case is credited prior
work, rather than an original claim of this theorem. The new coverage
is arbitrary paired graphs and dimensions in the bipartite basis family.

The result excludes a gain throughout the stated basis family. It does
not cover sequential shears with changing bipartitions, arbitrary
invertible bases, single-sign punctures, extra factor terms, factors
outside the root code, changed targets or physical realization. The
proof over Q also uses division by two; no characteristic-two extension
is asserted. Finite checks corroborate this written proof and do not
supply its universal quantifiers. No formal proof kernel was run.
