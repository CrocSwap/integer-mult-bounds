# No paired-Dn saving from two interacting rational shears

Let G be any finite simple graph on n coordinates, including isolated vertices.
For each edge {i,k}, i<k, put the two rows e_i+e_k and e_i-e_k into R.
There are v=2|E(G)| rows. A directed fitting binary matrix B has diagonal1,
and B_st=0 whenever distinct root rows have nonzero rational inner product.
Every remaining directed entry is free; symmetry is not assumed. For an exact
rational factorization P Q^T=R R^T define its algebraic COPY bill by

    C_B(P,Q)=sum_j rank_F2 B[supp(P_j),supp(Q_j)].

**Theorem.** For any a!=b, c!=d and rational t,s, set

    M=(I+t E_ab)(I+s E_cd), P=R M, Q=R M^(-T).

For every fitting directed B, C_B(P,Q)>=v. Thus optimizing one common pairing
cannot beat the coordinate-basis bill. The zero shears attain v with the common
edge-block pairing described below, so the joint optimum over this entire
family is v. We do NOT assert that every fixed nonzero M has minimum v.

The new boundary is two interacting shears with changing coordinate splits.
Nick Petalas's PR5176 proves equality for any shear matrix supported across one
fixed split; it explicitly asks about two changing-split shears on a paired D5
puncture. The argument below includes both chains and opposite shears. It also
proves a two-coordinate GL2 lemma. ywz65's PR2536 supplies the coordinate model
and open basis question; PR2719's full-Dn fixed-dense pairing model and
DreamingOfClouds's PR3045 full-D4 arbitrary-basis result remain distinct.

## Common-support degree lemma

Write r_j=R e_j and let d_j be the degree of j. If a term has factors R p,R q,
and for every edge incident to j at least one of its two sign roots lies in
BOTH supports, its binary support rectangle contains I_(d_j): choose one such
root for each edge, as both row and column. Distinct chosen roots meet at j,
so their rational inner product is +1 or -1. Fitting forces both off-diagonal
directions to zero; their diagonal entries are one. Submatrix rank gives the
lower bound d_j for every B, regardless of its other entries.

In particular, if p=e_j and q_j!=0, or conversely, the condition holds. On each
incident edge the other factor has values q_j+q_k and q_j-q_k, which cannot
both vanish over Q. Nonzero scalar multiples of a coordinate factor work too.
This is the credited forced-minor mechanism of PR5176, restated for use below.

## Complete classification of two shears

If t or s is zero, the single-shear coordinate anchors suffice. Otherwise:

1. If b!=c and d!=a, the set of source indices {a,c} and target indices {b,d}
   is disjoint. The product is I+tE_ab+sE_cd, with coincident entries added.
   It lies in the fixed-split family. For completeness, each source-coordinate
   column of M is unchanged, and each target-coordinate column of M^(-T) is
   unchanged; diagonal entries in the other column are one. Coordinates outside
   these sets are unchanged. The degree lemma gives every term its d_j.
2. If b=c and d!=a, three indices a,b,d are distinct: the forward chain.
3. If d=a and b!=c, three indices c,a,b are distinct: the reverse chain.
4. If b=c and d=a, the two shears are opposite and affect just {a,b}.

These alternatives are exhaustive even when a=c or b=d: those coincidences
belong to case1, since a!=b and c!=d. Same-oriented repeated shears, all zero
coefficients, and cancellations t+s=0 are therefore included.

## Three-coordinate chains, in both orders

Rename the distinct indices a,b,c. For the forward chain M=S_ab(t)S_bc(s),

    M=I+tE_ab+sE_bc+tsE_ac,
    M^(-T)=I-tE_ba-sE_cb.

All terms except b have a coordinate factor: at a the P factor is r_a; at c
the Q factor is r_c; other coordinates are unchanged. The middle factors are

    P_b=R(e_b+t e_a), Q_b=R(e_b-s e_c).

On an edge {b,k}, k=a makes the Q restriction a coordinate restriction; k=c
makes the P restriction coordinate; and every other k has both coordinate
restrictions. Hence at least one common sign root survives on every incident
edge. The degree lemma gives d_b, even though neither whole factor is a
coordinate column. Summing all terms gives sum d_j=v.

For the reverse order M=S_bc(s)S_ab(t),

    M=I+tE_ab+sE_bc,
    M^(-T)=I-tE_ba-sE_cb+stE_ca.

Again every term except b has a coordinate factor. Its middle factors are the
same R(e_b+t e_a), R(e_b-s e_c). The identical edgewise argument applies.
Renaming the three coordinates covers case3 above. No condition on nonzero
values t,s, nor an assumption excluding +/-1 cancellations, enters this proof.

## Arbitrary invertible mixing on two coordinates

In fact any rational GL2 block on coordinates a,b has no saving. Write its
block and dual block as

    H=[u v; w z], delta=uz-vw !=0,
    H^(-T)=[z -w; -v u]/delta.

For the a-term take p=(u,w), q=(z,-v)/delta, and for the b-term
p=(v,z), q=(-w,u)/delta, in the ordered coordinates a,b. Each satisfies
p dot q=1. All other terms are unchanged coordinate terms.

Suppose uz and vw are both nonzero. In each changed term both a-coordinate
factors are nonzero and both b-coordinate factors are nonzero. On an edge
{a,k} with k!=b, both restrictions are nonzero multiples of e_a, so both sign
roots survive. The same applies to edges {b,k}, k!=a. If {a,b} itself is an
edge, its two sign-root products have sum

    (p_a+p_b)(q_a+q_b)+(p_a-p_b)(q_a-q_b)=2(p dot q)=2.

Thus at least one product is nonzero and supplies a common sign root. Each
changed term separately has both a degree-a minor and a degree-b minor, and
therefore costs at least max(d_a,d_b). We do not add the ranks of these two
possibly overlapping minors. The pair costs at least 2max(d_a,d_b)>=d_a+d_b.

If vw=0, then uz!=0. If v=0, the a-term has a coordinate Q factor at a and
the b-term a coordinate P factor at b; if w=0 the roles are reversed. The
other factor's matching coordinate is nonzero. The pair costs at least d_a+d_b.
If uz=0, then vw!=0. If u=0, the a-term has coordinate P at b and the b-term
coordinate Q at a; if z=0, the a-term has coordinate Q at b and the b-term
coordinate P at a. The matching coordinates are again nonzero. The bounds
are swapped, still totaling d_a+d_b. These branches also cover a diagonal or
antidiagonal H; simultaneous uz=vw=0 is excluded by invertibility.

Adding the unchanged terms proves the GL2 lemma. Opposite shears have
H=[1+ts t; s 1], determinant1, so case4 follows, including the cancellation
locus 1+ts=0. This completes the theorem.

## Complete pairing bill and first actual D5 fixture

B_* has an all-ones2-by2 block on each edge's two signs and zero entries between
edges. It is fitting because the two sign roots of one edge are orthogonal.
In any support rectangle each edge contributes rank1 exactly when both factor
supports contain a sign on that edge, otherwise rank0. Thus its complete bill
is easy to compute without optimizing pairing entries. At M=I the jth term
has one block for each incident edge, giving sum d_j=v and the claimed joint
attainment. This is one common B for all terms, not termwise pairing choices.

Use exactly PR5176's D5 graph

    E={(0,1),(0,2),(0,4),(1,2),(2,3),(3,4)}; v=12.

The complete rational factors and all144 Gram entries are checked. For
S_01(1)S_12(1), the B_* bill is (3,3,3,2,2), total13. For opposite
S_01(1)S_10(1) it is (4,4,3,2,2), total15. For S_01(1)S_10(-1) it is
(2,3,3,2,2), total12. These are complete common-pairing invoices, not assertions
that the first two bills are optimal. The theorem bounds every fitting B.

## Scope and open next questions

The proof concerns algebraic support cost over rational factors and binary
pairings. Paired sign roots and characteristic different from2 for the factor
identities matter; the stated theorem is over Q only. Directed pairing freedom
is fully included. It does not cover single-sign deletions, three or more
interacting shears, arbitrary basis changes on larger blocks, extra factor
terms or factors outside the root code. Physical coefficient evaluation,
producer/consumer access, dirty restoration, tape movement, precision, native
and outer multiplication costs remain unpriced. No new exponent, physical
supplier, independent human review or formal proof-kernel acceptance is claimed.

The next changed boundary is three interacting shears on three coordinates.
First ask whether an actual paired D5 graph loses the edgewise common-support
condition in a way that lowers the COMPLETE common-pairing bill. A missing
minor alone is not a saving. Any construction needs exact full Gram equality,
one fitting pairing and all term ranks before a physical expansion is justified.
