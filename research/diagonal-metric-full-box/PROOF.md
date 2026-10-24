# Exact classification for diag(1,d,1)

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.

## Theorem and exact domain

For positive rational d write d=2^k u, where k=v2(d) is any integer
and u has odd numerator and odd denominator. The following are equivalent:

1. For every n>=1 and every rational n-by-3 factor P, with Q=P diag(1,d,1),
   nonzero row diagonals and nonempty original canonical ties, the retained
   directed sub-anchor box is n.
2. k is even and u=1 modulo4 in Z_(2).

The congruence uses the inverse of the odd denominator modulo4. In particular
5 satisfies the criterion although it is not a rational square; 2 and 3 fail.
The universal quantifier is over the supplied factors and their original
whole-instance anchors, not an arbitrary rational isometry of their matrix.
Inactive columns and arbitrarily negative valuations are included.

We retain PR3612 (Sagar Thakrar)'s definition. Delete identically zero product
columns. For each active coordinate j let m_j=min_i v2(P_ij), n_j=min_i v2(Q_ij),
and gamma=min_j(m_j+n_j). Define p_ij=2^(-m_j)P_ij and
q_ij=2^(m_j-gamma)Q_ij. A_i and B_i are their odd-coordinate supports and
T_i=A_i intersect B_i. Deleted coordinates carry zero labels. A retained box
orders distinct rows and assigns a_i subset A_i,b_i subset B_i, with binary
a_i dot b_i=1; if i is earlier than j and M_ij=0, it requires a_i dot b_j=0.
No subset of rows is ever renormalized. Reduction modulo2 always gives
M_ij=0 => A_i dot B_j=0, since pq^T=2^(-gamma)M and both factors are integral
at2. Positive definiteness of the metric makes every nonzero row diagonal
positive. Empty ties, even for nonzero rows, are outside this theorem.

## 1. Anchor-preserving valuation reduction

Let S=diag(1,2^h,1), with arbitrary integer h. Set P'=PS, Q'=QS^(-1).
The matrix is unchanged and Q'=P' diag(1,d/2^(2h),1). In coordinate2,
m'_2=m_2+h and n'_2=n_2-h; all m_j+n_j, and hence gamma, are unchanged.
Direct substitution gives p'=p and q'=q exactly. The deleted-column set is
also unchanged. Thus every original anchor, every admissible labeling and the
box value are unchanged. This proves a bijection of entire factor domains.
Choosing h=floor(k/2) reduces the metric to a unit u if k is even, or to2u
if k is odd. This uses only dual column scaling, not a change of row basis
or an unsupported claim that a rational Gram isometry preserves anchors.

## 2. Sufficiency for an odd unit u=1 modulo4

Now all three weights w=(1,u,1) are units congruent to1 modulo4. For active
columns n_j=m_j. Put m=min_j m_j, delta_j=m_j-m>=0, and R=2^(-m)P.
Then gamma=2m, p_ij=2^(-delta_j)R_ij and
q_ij=2^(delta_j)w_j R_ij. If delta_j>0, both R's column and q's column are
even; if delta_j=0, their odd supports agree. Consequently
B_i=supp(R_i mod2) subset A_i and T_i=B_i, including deleted columns.
Nonempty ties make every row R_i primitive at2.

Odd-sized ties are assigned to O. Every other row has exactly two odd
coordinates, a support S_i={s,t}. Give it color chi_i=R_is R_it modulo4,
which is +1 or -1. If two such supports differ they intersect in exactly
one coordinate, so the weighted product R_i diag(w) R_j^T is odd and not
zero. If they agree and that product is zero, the unsupported-coordinate
product is zero modulo4. The two supported summands are odd, sum to zero,
and thus have product -1 modulo4. Since w_s w_t=1 modulo4 this says
chi_i chi_j=-1. Every actual zero between even-tied rows therefore joins
opposite colors. Neither color class has an internal scalar zero.

Let F be the +1 class and L the -1 class. Choose c_i in T_i for F and L.
Order F, then O, then L, with arbitrary internal orders, and assign

- F: (a_i,b_i)=(A_i,{c_i});
- O: (a_i,b_i)=(A_i,B_i);
- L: (a_i,b_i)=({c_i},B_i).

Every self-dot is1. Internal F/L zeros do not occur. For internal O or any
forward pair across distinct blocks, the binary dot is A_i dot B_j and the
original scalar-to-anchor implication applies. This verifies all directed
conditions, including empty blocks, and retains all n rows. This is PR3612's
credited coloring/two-block construction applied to the new weighted domain;
no finite enumeration is used to establish the universal statement.

## 3. Necessity for odd valuation: a three-row family

After section1 let d=2u with u any positive unit. Take

P=((1,0,1),(1,1,-1),(1,-2/d,-1)), Q=P diag(1,d,1).

All column minima of P are0. Those of Q are(0,1,0), and gamma=0. Since
-2/d=-1/u is a unit, the original anchors are A=(5,7,7), B=(5,5,5), using
masks1,2,4. Thus every tie is the two-coordinate support5.
All three off-diagonal weighted products vanish: the first row gives1-1;
the other pair gives1+d*(-2/d)+1=0. Their diagonal entries are
2,2+d,2+4/d, all positive. If all three rows were kept, their ordered binary
pairing matrix would be triangular with diagonal1, hence have rank3 overF2.
Every target label is confined to coordinates1 and3, so the pairing has
rank at most2, a contradiction. Keeping rows0,1 with equal source/target
unit masks1,4 attains2. Therefore box=2 for every member of this family.
Section1 transports the obstruction to every positive rational d of odd
valuation, preserving the original anchors exactly.

## 4. Necessity for even valuation with u=3 modulo4

After section1 take the positive unit d=u=3 modulo4 and put

P=((1,1,0),(u,-1,2),(u,-1,-u(u+1)/2),(1,0,1)), Q=P diag(1,u,1).

Because v2(u+1)>=2, the third coordinates of the first three rows are even.
The appended row makes the third-column minimum0; the other minima are
already0. Thus gamma=0 and A=B=(3,3,3,5). The first three rows are mutually
orthogonal: their products are u-u, u-u, and
u^2+u-u(u+1)=0. Positivity gives nonzero diagonals. A full box would restrict
to a triangular rank3 pairing on these three rows, but all their labels lie
in the same two-coordinate plane, impossible. Rows0,1,3 with unit masks1,2,1
in that order form a box: the first pair is zero with distinct labels;
the other scalar products are1 and u+2, both nonzero. Hence box=3.

This is a rational family extending Nick Petalas PR5172's exact u=3 example,
not a new triangular-rank argument. Section1 transports it to every even
valuation whose unit part is3 modulo4. Every odd rational unit is1 or3
modulo4, so sections2–4 exhaust all positive rational d and prove the iff.

## Scope and credit

PR5172 contributes the fixed positive-metric obstruction and asks this
classification question. PR3612 contributes the rational Gram theorem,
original-anchor caution, modulo-four coloring and directed F/O/L construction.
The anchor framework and rank obstruction retain Aaron Wang/navinor's
PR2914/2978/3031 and DreamingOfClouds's F-star lineage and the labeling
predecessors credited by PR3612. This contribution supplies the exact metric
criterion, its anchor-preserving reduction, weighted sufficiency and complete
complementary counterexample families. It is a scoped algebraic theorem,
not unrestricted asymmetric F-star, native supplier admission, a physical
algorithm, new kappa or a selected-frontier change. No routing, COPY, storage,
precision or tape-cost improvement is claimed; independent human and formal
proof-kernel acceptance are unclaimed.
