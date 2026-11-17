# Three-cycle obstruction outside two product loci

This proof was produced by Nick Petalas. Apache-2.0.

## Statement

Let G be any finite simple graph on n >= 3 coordinates. On every edge
{i,k}, i<k, retain both rows e_i+e_k and e_i-e_k, forming a rational
matrix R with v=2|E(G)| rows. Isolated coordinates are permitted. A fitting
binary matrix B has B_ii=1 and B_ik=0 for distinct rows whose rational inner
product is nonzero. The other directed entries are arbitrary, independently.
For rational factors P,Q with P Q^T=R R^T, their algebraic COPY bill is

    C_B(P,Q) = sum_j rank_F2 B[supp(P_j), supp(Q_j)].

Fix distinct a,b,c, rational t,s,u, and set

    M = (I+t E_ab)(I+s E_bc)(I+u E_ca),
    P = R M, Q = R M^(-T), h = tsu.

If h is neither 1 nor -1, then for every common fitting directed B,

    rank_F2 B[supp(P_j),supp(Q_j)] >= degree_G(j) for every j,
    C_B(P,Q) >= 2|E(G)| = v.

The statement includes zero coefficients and arbitrary additional coordinates.
It excludes this ordered coordinate-cycle family away from h=+/-1. It does
not exclude savings on those two loci or for other three-shear patterns.

## Common sign roots and the credited forced minor

For rational vectors p,q and edge {j,k}, the two sign-root products satisfy

    (p_j+p_k)(q_j+q_k) + (p_j-p_k)(q_j-q_k)
        = 2(p_j q_j + p_k q_k).                         (1)

Thus a nonzero right side guarantees at least one sign root in both
supports of R p and R q. For each edge incident to j, choose one such
root as both a row and a column of the support rectangle. Distinct chosen
roots share exactly coordinate j and have inner product +1 or -1. Their
B off-diagonal entries are forced to zero and their diagonals are one.
They therefore form an identity minor of size degree_G(j).

This common-support degree argument is the lemma of JoyboyBrian's #5214,
building on Nick Petalas's #5176. It is cited and restated to make the new
application readable. No new general rank-minor principle is claimed.

## New cycle calculation

Relabel a,b,c as 0,1,2. The affected blocks are exactly

    M = [ 1+h   t   ts ],       M^(-T) = [  1   0   -u ],
        [  su   1    s ]                    [ -t   1   tu ]
        [   u   0    1 ]                    [  0  -s    1 ]

and both matrices are identity on other coordinates. The factors are
reciprocal, so P Q^T=R M M^-1 R^T=R R^T on every input.

For column j, write w_k=M_kj (M^(-T))_kj. These products, not the separate
entries, decide the right side of (1). The three changed columns give

| Column j | w_a | w_b | w_c | All other w_k |
| --- | ---: | ---: | ---: | ---: |
| a | 1+h | -h | 0 | 0 |
| b | 0 | 1 | 0 | 0 |
| c | -h | h | 1 | 0 |

For the a-term, an edge to b has w_a+w_b=1. Any other incident edge has
sum 1+h. For the b-term, every incident edge has sum 1. For the c-term,
an edge to a has sum 1-h, an edge to b has sum 1+h, and every other
incident edge has sum 1. An unchanged coordinate has w_j=1 and all other
w_k=0, so its incident sums are also 1.

All listed sums are nonzero when h is neither 1 nor -1. Equation (1) and
the degree lemma therefore give the asserted termwise bounds. Summing the
degrees counts each edge twice and proves the complete bill floor. The
empty-edge graph has zero bill and satisfies the theorem trivially.

At zero coefficients the coordinate basis and the common pairing B_*
with all-ones 2-by-2 blocks on each sign pair attain v. Hence the joint
minimum over this allowed family and all pairings is v. This is not a
claim that every fixed nonzero M attains its lower bound.

## Why the excluded loci remain open

At t=s=u=1, take the single edge {a,c}. The c-term's P values on its two
roots are (2,0), and its Q values are (0,-2). No common sign root survives.
At t=s=1,u=-1, the same failure occurs on edge {b,c} in the c-term, with
P values (2,0) and Q values (0,-2).

These are failures of this particular degree minor. Neither is a
counterexample to the complete bill floor: other terms and common-pairing
constraints still contribute. In particular the theorem makes no claim
that either exceptional locus supplies an improvement.

## Evidence and limits

The standalone verifier builds M by literal shear multiplication and
obtains its dual by rational Gaussian elimination. It compares both with
the displayed matrices, checks every Gram entry and chosen identity minor,
and enumerates every fitting directed B on the stated three-coordinate
domains. A separate set-of-span oracle checks every small binary rank.
Finite tests corroborate this proof; they are not its universal quantifier.

The proof concerns rational Gram factors, paired sign roots, a fixed square
factor count and one common directed fitting binary pairing. It gives no
physical coefficient arithmetic, native implementation, producer/consumer,
dirty-restoration program, stock, precision, tape or recursive invoice.
No new kappa, supplier admission or complete multiplication theorem follows.
Independent human and formal proof-kernel review are unclaimed.
