# Positive half-integral Gram decoders cannot save port-space cost

## Statement

Let each scalar port i carry a nondegenerate subspace E_i of a finite binary
space with a symmetric bilinear form. Write d_i = dim E_i. The ambient form may
be degenerate. A scalar fitting matrix K has diagonal one and K_ij = 0 whenever
i != j and E_i is not orthogonal to E_j.

Suppose

    K = sum_t c_t v_t v_t^T,

where the factor vectors are integral and every coefficient is a positive
multiple of 1/2. Discard zero terms. Charge term t the binary pairing rank of
S_t against itself, where S_t is the sum of the **complete** E_i for which
v_it is nonzero. There is no bound on the number of terms or support size.

**Theorem.** The total charge is at least sum_i d_i. Unit-weight singleton
factors attain equality. The statement is normalized to K_ii = 1; rescaling an
unnormalized diagonal also rescales its coefficient alphabet.

## 1. The diagonal forces a sparse incidence structure

Positivity and K_ii = 1 imply that every active coefficient is 1/2 or 1, and
that every nonzero factor entry is +1 or -1. Each row therefore occurs either
in exactly one unit-weight column, or in exactly two half-weight columns.
The two kinds of rows never share columns.

Within one unit-weight column, every pair of distinct rows has nonzero scalar
inner product. The fitting condition forces their complete port spaces to be
pairwise orthogonal. Those spaces are nondegenerate, so the column's charge is
exactly the sum of their dimensions.

## 2. Half-weight rows form edges

Identify each half-weight row with the unordered pair of factor columns in
which it occurs: an edge of a multigraph on column indices. Rows on distinct
edges sharing a vertex have exactly one common column and scalar inner product
+1/2 or -1/2. Consequently their complete port spaces are orthogonal.

On a fixed edge, divide its rows into the two sign classes proportional to
(1,1) and (1,-1). Two rows in the same class have scalar inner product +1 or -1.
Their port spaces are pairwise orthogonal and span a nondegenerate space.
Let A_e and B_e be the dimensions of the two class spaces, equal to the sums of
the individual row dimensions in each class. An empty class has dimension zero.

Let H_e be the sum of the two class spaces, and let r_e be its restricted
binary pairing rank. It contains each nondegenerate class space, so

    r_e >= max(A_e, B_e) >= (A_e + B_e)/2.

## 3. The complete tariff adds at each column

At a column vertex, the H_e of its incident edges are pairwise orthogonal by
section 2. The rank of their sum is the sum of their restricted ranks, **even
if degenerate summands intersect**. To see this, pull the form back along the
surjection from the external direct sum of those spaces. The pullback matrix
is block diagonal. Pullback along a surjection preserves bilinear rank: choose
lifts of a basis in the range and then a basis of the kernel.

Every edge has two endpoints. Summing the column invoices therefore gives

    half-column charge = 2 sum_e r_e
                       >= sum_e (A_e + B_e).

The right side is the sum of d_i over all half-weight rows. Add the unit-column
bill from section 1 to prove the theorem.

## Consequence and limits

Under the retained favorable s-stage coverage law, the available deficit is
proportional to `(s-1)/s * tau - C`, where tau = sum_i d_i and C is the decoder
charge. The theorem gives an upper bound `-tau/s`, strictly negative for
positive tau and finite s. Further native, routing, restoration or hosting
charges cannot repair that unfavorable budget. This application retains the
stated coverage law; it is not an all-architecture multiplication lower bound.

Positivity and the coefficient lattice are essential. The exact E8 fixtures
in algebra.py give cost 72 on 120 line ports with positive quarter weights,
and cost 81 with eight positive and one negative half weight. Both use integral
factors, diagonal one and the same type of full-space tariff. Their binary
pairings have rank nine; quotienting by the radical produces a nine-dimensional
nondegenerate ambient model without changing any charge. They are algebraic
controls, not new native suppliers.

Asymmetric factors, other coefficients, changed endpoint masks and alternative
physical tariffs remain open. The separate finite C5 census covers only its
explicit 120-root menu. Neither a finite replay nor this handwritten proof is
a formal verification of the full multiplication theorem.

## Credit

New proof by Tekalign (`tekuuu`) with substantial OpenAI Codex assistance.
The strict masked endpoint, complete-port-space tariff and 2-integral benchmark
are credited to Adam Gall, Jeremy Diviney, Philippe Van Velzen and their cited
predecessors. This proof addresses a positive half-integral Gram class outside
the 2-integral coefficient hypothesis, with additional symmetry and positivity
restrictions. Known E8 geometry supplies the escape controls. See README and
SOURCES for exact pins and retained construction credit. Apache-2.0.
