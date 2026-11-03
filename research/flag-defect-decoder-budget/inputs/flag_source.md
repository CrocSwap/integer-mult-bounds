# Exact fitting rank with compatible port flags

This scoped written proof was produced by Nick Petalas. Apache-2.0.

## Contract

Let K be any field, n,d positive integers, and Z a set of ordered pairs
(i,j) with i different from j. A scalar matrix A fits Z if A_ii=1 and
A_ij=0 for (i,j) in Z. Other ordered entries are free, independently of
their transposes. Write mu_K(Z) for the smallest rank of a fitting matrix.
This minimum exists: the identity fits, and ranks are integers in 1..n.

At each port i choose a complete K-flag

    0 = F_i^0 < F_i^1 < ... < F_i^d = K^d,
    dim F_i^a = a.

A block fitting matrix M has d-by-d blocks, M_ii=I_d and M_ij=0 for
(i,j) in Z. Call it compatible if

    M_ij(F_j^a) is contained in F_i^a

for every i,j,a. The source flag is at j and the target flag is at i.
Flags at distinct ports may differ. Entries and free blocks need not be
symmetric, invertible, commuting, normal, diagonalizable or positive.
There is one flag per port used by every block incident to it, not a
fresh flag for each block. The diagonal identity identifies that port's
input and output payload spaces. No coordinate is assumed clean or fixed.

## Theorem

For every K,n,d,Z and every prescribed family of complete flags,

    min rank_K M = d mu_K(Z),

where the minimum is over compatible block fitting matrices.
In particular, even optimizing the flags cannot lower this value.

### Lower bound

Choose a basis P_i adapted to each flag. With the block diagonal matrix
P=diag(P_1,...,P_n), set T=P^-1 M P. Its block T_ij is upper triangular:
its column a lies in the first a coordinates precisely because the map
sends F_j^a into F_i^a. Also T_ii=I and T_ij=0 on Z. Conjugation preserves
rank over K.

Order the full coordinates by flag level first, then by port. This is one
simultaneous row and column permutation. The resulting matrix is block
upper triangular with d diagonal blocks of size n:

    A_a = ((T_ij)_aa)_(i,j),       a=1,...,d.

Each A_a fits the original directed mask Z. Thus rank A_a>=mu_K(Z).

For completeness, an upper block triangular matrix with possibly singular
diagonal blocks A_a has rank at least sum_a rank A_a. For each a select a
nonsingular square minor of A_a of order rank A_a. Select those rows and
columns in the full matrix. The combined submatrix is square and block
upper triangular, with exactly those nonsingular minors on its diagonal.
Its determinant is their nonzero product. This argument includes empty
minors for any zero-rank diagonal block and works in every characteristic.
Therefore

    rank M = rank T >= sum_a rank A_a >= d mu_K(Z).

### Attainment for any prescribed flags

Take a scalar fitting matrix A of rank mu_K(Z), and set

    M_ij = A_ij P_i P_j^-1.

Its diagonal blocks are I and its forbidden blocks are zero. It sends
F_j^a into F_i^a. The full M equals P(A tensor I_d)P^-1, so its rank is
d rank A. One can see this rank directly by permuting A tensor I_d into
d copies of A. This attains the lower bound with the prescribed flags.
No method for efficiently finding a scalar optimum is asserted. QED.

## Consequences and the field boundary

If a linear query layer factors M=D E through r field coordinates, then
r>=rank M>=d mu_K(Z). This counts total linear query coordinates. It is
not a native COPY tariff or a count of recursive child ranks. Volume,
source access, frames, ownership and restoration still need separate costs.

Over an algebraically closed field, any finite commuting family of square
matrices has a common complete flag. To recall the classical argument,
restrict to a nonzero eigenspace of one member. All other commuting members
preserve it. Repeated restriction gives a common eigenvector. Its span is
invariant; applying induction to the quotient gives the full flag.
This does not assume diagonalizability and includes Jordan blocks.
Apply the theorem with the same flag at every port. Consequently commuting
complex block fitting matrices cannot beat d mu_C(Z). Noncommuting blocks
which preserve compatible flags are excluded as well. Mere noncommutation
is not sufficient to obtain a block-rank advantage.

If a K-matrix has compatible flags only over an extension L, extension
preserves its rank and the proof gives rank_K M>=d mu_L(Z). It does not
give d mu_K(Z) unless flags over K or equality of the scalar minima is
separately justified. The theorem with prescribed K-flags remains valid
over all fields, including finite fields. The complex commuting corollary
must not be silently read as a base-field rational minrank statement.

For Cinna Davis's field-line scalar-query repair, the cited complex scalar
fitting-rank inequality is mu_C(G)>|V(G)|/4 for its C4-free graph.
The present theorem transfers that inequality to compatible-flag block
fits as rank M>d|V(G)|/4. This is a conditional use of the retained scalar
lemma, not a fresh proof or replay of its scaling argument or invoice.
It closes only the flag-compatible part of that open operator-valued
boundary. Arbitrary flag-breaking block fits remain outside this result.

## Why the hypothesis matters

The finite checker includes two sharp complete-mask examples. One has
noncommuting upper triangular 3-by-3 blocks and rank three. Another has
three distinct two-dimensional local charts and rank two, although its
raw block family preserves no common binary line. The second example
shows why a single raw-coordinate flag is stronger than portwise
compatibility.

As a boundary control, take the classical width-two C5 representation
with one scalar coordinate per edge. Port i carries the two edges incident
to i, and a block identifies coordinates bearing the same edge. The
diagonal is I_2, nonneighbors have zero blocks, and the complete matrix
has rank five. The scalar C5 minimum is three, so the theorem would force
rank at least six if compatible flags existed. The verifier independently
rejects all 3^5 local flag tuples over F2. This classical block advantage
is inherited context, not a new C5 optimum. It prevents dropping the
compatibility hypothesis or inferring it from identity diagonal blocks.

## Provenance and scope

The block-fitting and query-factorization framework is classical. See
Boris Bukh and Christopher Cox, [On a fractional version of Haemers' bound,
section 2 and Proposition 9](https://arxiv.org/html/1802.00476v2), which
credits Anna Blasiak's earlier fractional bound. The elementary rank-minor
and simultaneous-triangularization facts are also classical. No global
literature priority is claimed. The contribution is the exact arbitrary
directed-mask, prescribed port-flag interface and its stated obstruction
for this repository's vector-decoder search.

Credit ywz65's [PR2541](https://github.com/CrocSwap/integer-mult-bounds/pull/2541)
for the strict block-fitting contract, its 49d result on a particular mask
and the unrestricted C5 comparison. Credit Aaron Wang / navinor's
[PR825](https://github.com/CrocSwap/integer-mult-bounds/pull/825) for a
different common-flag obstruction in the all-role framed XOR circuit
model. The present argument concerns a completed fitting matrix, not that
circuit model, and neither theorem subsumes the other's physical contract.
Credit Cinna Davis's retained field-line repair for its scalar inequality
and open operator-valued question, and the native/geometry predecessors
credited in those sources. SOURCES.json pins these texts as historical
provenance. No predecessor executable, certificate or scientific replay
is used by the new verifier.

The proof supplies no native word, arbitrary flag-breaking lower bound,
efficient flag-finding procedure, unequal-dimension theorem, paid physical
invoice, new kappa, supplier admission or complete multiplication theorem.
The five selected framework assumptions remain. Independent human and
formal proof-kernel review are unclaimed. Finite checks corroborate the
written proof rather than establish its unbounded quantifiers.
