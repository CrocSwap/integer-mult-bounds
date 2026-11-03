# Universal full anchor boxes for positive unit metric triples

This scoped algebraic proof was produced by Nick Petalas. Apache-2.0.

## Theorem

Let D=diag(a,b,c), where a,b,c are positive rational numbers of 2-adic
valuation zero. Residues modulo four use the inverse of the odd denominator.
The following statements are equivalent.

1. Every rational n-by-3 factor P, for every n>=1, with Q=P D,
   nonzero diagonals and nonempty original canonical ties has a full retained
   directed sub-anchor box.
2. a, b and c have the same residue modulo four.

Thus both residue patterns (1,1,1) and (3,3,3) have universal full retention.
Every other unit residue pattern has a rational four-row example with box
exactly three. The example allows the third metric coefficient to vary
independently, removing the repeated-weight restriction of PR5213 in this
unit domain. This is a statement about the supplied factors and their
original anchors, rather than a matrix invariant under arbitrary isometry.

## Definitions and the original anchors

We use the definition of Sagar Thakrar / PR3612, retained by JoyboyBrian /
PR5213. Delete identically zero columns. For each remaining coordinate j,
write m_j=min_i v2(P_ij), n_j=min_i v2(Q_ij), and

    gamma = min_j(m_j+n_j),
    p_ij = 2^(-m_j) P_ij,
    q_ij = 2^(m_j-gamma) Q_ij.

Let A_i and B_i be the odd-coordinate supports of p_i and q_i respectively.
Let T_i=A_i intersect B_i. A box consists of an ordered subset of rows and
binary labels alpha_i subset A_i, beta_i subset B_i, satisfying

    alpha_i dot beta_i = 1,
    i before j and M_ij=0 imply alpha_i dot beta_j=0,

where M=P D P^T and binary dot products are taken over F2. Deleted columns
carry zero labels. Anchors are computed on the whole instance once.

All weights are units, so n_j=m_j. Set m=min_j m_j,
delta_j=m_j-m and R=2^(-m)P. Then gamma=2m and

    p_ij = 2^(-delta_j) R_ij,
    q_ij = 2^(delta_j) d_j R_ij.

The entire R column j is even if delta_j>0. Consequently

    B_i = supp(R_i modulo two),  B_i subset A_i,  T_i=B_i.

Nonempty ties make every R_i primitive at two. These statements include
inactive columns, arbitrary column minima and negative valuations of P.
Reduction of p q^T=2^(-gamma)M modulo two gives the inherited implication

    M_ij=0 implies A_i dot B_j=0.                         (1)

## Sufficiency

Assume all three d_j have the same residue epsilon in {1,-1} modulo four.
In particular d_s d_t=1 modulo four for any pair of distinct coordinates.
Put every odd-sized B_i in a set O. Any remaining B_i has exactly two
coordinates, say {s,t}. Color its row by

    chi_i = R_is R_it modulo four, in {1,-1}.

If two even supports differ, they intersect in exactly one coordinate.
Their weighted inner product is odd, so M_ij is nonzero. If they coincide
and M_ij=0, the product on the remaining coordinate is zero modulo four.
The two supported summands are odd and sum to zero. Their product is -1
modulo four. Because d_s d_t=1, this gives

    chi_i chi_j=-1 modulo four.

Every zero between even-support rows therefore joins different colors.
Let F and L be the two color classes. Neither has an internal zero.
Use the credited directed F/O/L construction of PR3612 and PR5213.
Choose t_i in T_i for i in F or L, order F before O before L, and set

    F: (alpha_i,beta_i)=(A_i,{t_i}),
    O: (alpha_i,beta_i)=(A_i,B_i),
    L: (alpha_i,beta_i)=({t_i},B_i).

Every self-dot is one. Internal F or L pairs have no zero to constrain
them. Within O or between blocks, the relevant dot product equals
A_i dot B_j, so (1) applies. This retains all n rows. No subset is
renormalized. The predecessor supplies the coloring method and label
construction; the new sufficiency observation is that all equal unit
residues, including three independently chosen weights, suffice.

## Necessity and an exact four-row obstruction

If the residues are not all equal, permute coordinates so that a and b
have opposite residues. Thus v2(a+b)>=2. Let c be the remaining positive
unit and take

    P = [(1, 1, 0),
         (b,-a, 2),
         (b,-a,-ab(a+b)/(2c)),
         (1, 0, 1)].

Every column minimum is zero. All metric coefficients are units, so the
same holds in Q=P D. The third coordinate of row two is even. Therefore

    gamma=0,  A=B=(3,3,3,5),

where masks 1,2,4 name the three coordinates and rows are numbered from zero.
All ties are nonempty. Positivity gives nonzero diagonals. The first three
rows are mutually orthogonal, since their weighted products are

    ab-ab=0,  ab-ab=0,
    ab^2+a^2b-ab(a+b)=0.

If a full box existed, restrict its row order and labels to those three
rows. Its binary label-pairing matrix would be triangular with diagonal
one, hence rank three. All its labels lie in the same two-coordinate
plane, so its rank is at most two. This contradiction proves box<=3.
This triangular-rank argument is credited to the existing anchor framework.

Rows (0,1,3) with equal source and target unit labels (1,2,1) attain three.
The only zero between these rows is the first pair; the other two products
are a and ab+2c, which are positive. Hence box=3 exactly.

The formula works for every independent c and every positive unit a,b of
opposite residues. Permuting its coordinates handles every complementary
unit residue pattern. This completes necessity and the classification.

## Scope and credit

JoyboyBrian / PR5213 classifies diag(1,d,1) and explicitly leaves arbitrary
positive triples open. Its original-anchor discipline and unit-domain
argument are inputs. Sagar Thakrar / PR3612 supplies the rational Gram
theorem, modulo-four coloring and F/O/L labels. Nick Petalas / PR5172
supplies the fixed diag(1,3,1) obstruction. The new step is the exact
unit-triple classification and a counterexample family with three
independent metric coefficients. We do not claim the predecessor methods
or their special cases as new.

Credit Aaron Wang/navinor / PR2914, PR2978 and PR3031, DreamingOfClouds's
F-star lineage, and the labeling predecessors credited in PR3612. Exact
proof provenance is pinned in SOURCES.json. The verifier imports no
predecessor code and does not re-run its scientific checks.

Unequal metric valuations are outside the theorem. No unrestricted
asymmetric F-star result, physical decoder, native circuit, productive
target, cost saving or new kappa follows. Physical realization, owners,
dirty restoration, routing, stock, precision, compiler and outer costs
remain caller obligations. Finite checks corroborate this written proof;
independent human and formal proof-kernel review are unclaimed.
