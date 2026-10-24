# Full-mask attainment with separated-port excess

This is a scoped algebraic proof over every field. The finite checks corroborate
the new constructions. No physical tariff or multiplication theorem is proved.

## Contract and credited premises

Use the 112 ports, matching and strict ordered mask of Sagar Thakrar's
PR2484, retained in `paired-plane-block-rank`. If port i lies in plane E_i,
a fitting matrix has diagonal block I_(n_i), and its ordered (i,j) block is
zero for i != j unless E_i and E_j are orthogonal. Permitted rectangular
blocks are arbitrary. They need not be symmetric or commute.

The credited premises are:

1. PR2484's 49 supports partition the ports, and distinct ports within a
   support are permitted pairs.
2. Its 22-plane set Q is pairwise nonorthogonal and nonorthogonal to the
   five planes C=(13,23,35,16,34). The induced permitted graph on C is C5.
   Both ports within a plane have forced off-diagonal zeros.
3. The all-field C5 block lemma in `paired-plane-block-rank` gives rank at
   least 5d when each cycle plane has total width 2d.

These are predecessor results, cited as dependencies. This package does not
claim to discover their geometry, partition or uniform rank 49d, and does
not replay their verification suites. Source bytes and proofs are pinned.
Tekalign's PR3362 extends the C5 lower bound to unequal widths and explicitly
leaves full unequal-mask attainment open. We settle one restricted family.

## Theorem

Let T be the 44 ports in the planes of Q. Choose an integer d>=1 and
arbitrary integers e_p>=0 for p in T. Set

    n_p = d+e_p for p in T, and n_p=d otherwise.
    E = sum_(p in T) e_p.

The exact minimum rank of a fitting matrix on the complete 112-port mask is

    49d + E.

Equivalently this is the exact minimum intermediate field-coordinate
dimension for a linear factorization M=A B of such a fitting matrix.
This is a full-mask result for this family, not just a principal-mask bound.

## Lower bound

Restrict any fitting matrix to the 44 Q ports and the ten C ports. All
ordered cross blocks between those two sets vanish. The Q part is the
identity of dimension 44d+E. The cycle part, grouping the two ports within
each plane, has five diagonal blocks I_(2d) and forbidden nonneighbor
blocks. The credited C5 lemma bounds its rank below by 5d over every field.
The principal submatrix therefore has rank at least 49d+E, as does the
full matrix. This applies to all arbitrary ordered free blocks.

## Attaining construction

No two distinct Q ports can occur in the same partition support: Q ports
are mutually forbidden, whereas each support consists of permitted pairs.
Thus exactly 44 of the 49 supports contain a Q port, each containing one.

For each support S allocate a query vector of dimension

    c_S = max_(p in S) n_p.

At port p in S, embed its n_p coordinates as the first n_p coordinates
of this vector. Sum these embeddings to encode the query. Decode at p by
projection onto its first n_p coordinates. The self-block is I_(n_p).
Blocks between distinct supports vanish. Blocks within a support are
rectangular initial-coordinate overlaps, which the mask permits. This
constructs an actual full-mask factorization over every field using only
zero and one coefficients.

For a support containing Q port p, c_S=d+e_p. For the other five supports,
c_S=d. Consequently total query dimension is exactly 49d+E, attaining
the lower bound. The construction is independent of the characteristic.

One can also see its exact rank directly. For each support and local
coordinate, the associated expanded matrix is a nonempty all-ones block
on the ports that possess that coordinate. These blocks use disjoint row
and column sets. Each has rank one over every field, so their total rank
is sum_S c_S. Arbitrary independent invertible port charts preserve the
identity/zero mask and rank, though they do not reduce the universal floor.

## First instance and scope

Set d=1 and add one coordinate at Q port 0. The full matrix has 113 rows
and columns and exact minimum rank 50. No assertion is made that every
unequal vector satisfies a formula based only on total excess. Allowing
excess at other ports changes the family and can change both bounds.

The compressed recipe stores 112 widths and 49 capacities. It does not
expand enormous payload matrices or implement the queries on a physical
machine. Native copies, access, frame changes, dirty restoration, numerical
precision, hosting and complete supplier costs remain outside the theorem.

This contribution is produced by Nick Petalas. Credit Sagar Thakrar/PR2484,
Tekalign/PR3362, ywz65/PR2541 and PR2471, Cinna Davis/PR1825,
Adam Gall/PR1889, ctoth, Philippe Van Velzen and the retained P112 lineage.
The support embedding and rank arguments use elementary linear algebra;
no claim of literature priority for those methods is made. Apache-2.0.
