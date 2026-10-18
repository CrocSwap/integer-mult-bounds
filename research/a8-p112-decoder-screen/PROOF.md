# Sharp copy cost 71 for the A8 simplex on a matching-frame P112 puncture

This is a scoped mathematical proof whose finite lemmas are exhaustively
recomputed by two implementations. It is not a formal multiplication theorem.
The deficiency-space method is due to the P120 predecessor, mightyOil's
[PR1248](https://github.com/CrocSwap/integer-mult-bounds/pull/1248). The one-sided
overcomplete representation comes from joaqcoo's
[PR1224](https://github.com/CrocSwap/integer-mult-bounds/pull/1224). Here the
puncture changes the finite lemmas, and every lemma needed below is recomputed.

## 1. Fixed family and puncture

Work in the sum-zero subspace V of Q^9. Use the 120 oriented E8 root lines

- e_a-e_b for 0 <= a < b <= 8, in lexicographic order (36 lines);
- 1_S-(1/3)1 for three-element subsets S of {0,...,8}, in lexicographic order
  (84 lines).

Puncture the orthogonal frame

    F = { e_(2j)-e_(2j+1),
          e_(2j)+e_(2j+1)+e_8-(1/3)1 : j=0,1,2,3 }.

Its zero-based indices are [0,15,26,33,42,89,112,119]. It is the first
orthogonal eight-frame in the declared root order; the verifier checks this
by complete lexicographic backtracking until the first solution. Let P be
the 112 live lines. They span V (rank eight, checked over Q).

Fix the nine simplex normals b_k=e_k-(1/9)1, and T_ik=r_ik for live roots r_i.
The variable factor D has 112 rows and nine columns. Require

    D T^t = 2G,   G_ij = r_i dot r_j,

on **all** live pairs, with ordinary transpose. Coefficients can be arbitrary
complex numbers. Terms are charged separately by the F2 rank of the pairing
matrix (G_ij+1) mod 2 restricted to their nonzero row and column supports.
Zero terms are allowed, but the sharp witness below has all nine terms active.

Since the live roots span V, the identity is equivalent to

    D_ik = 2r_ik + t_i,   t_i arbitrary in C.

Indeed D_i-2r_i is orthogonal to V and hence is a multiple of the all-ones
vector. This argument is valid over C with the bilinear ordinary transpose;
no positivity or conjugation is invoked.

## 2. Exact reduction to binary deficiency spaces

Use labels in F2^9:

    u_ab = 1+e_a+e_b,    u_S = 1_S.

For every pair of the 120 roots, u_i dot u_j=(G_ij+1) mod 2. This is checked
on all 14,400 entries. For each k, the live labels on the column support
{i:r_ik != 0} span all of F2^9. Thus the pairing rank of term k equals the
dimension of the label span on its row support {i:D_ik != 0}.

Define

    K_k = {w : w dot u_i=0 whenever D_ik != 0},   delta_k=dim K_k.

The total copy cost is exactly 81-sum_k delta_k. It is enough to prove that
the sum of the nine deficiencies is at most ten.

If w in K_j and z in K_k both evaluate to one on u_i, then D_ij=D_ik=0.
Consequently r_ij=r_ik. Call this necessary relation compatibility of the two
functionals at columns j,k. It uses only zero patterns, so it applies to all
complex shifts, including generic shifts that create no zero entries.

## 3. Finite covering of every possible deficiency tuple

If every delta_k <= 1, the sum is at most nine already. Otherwise choose an
anchor j with delta_j >= 2 and a binary plane U contained in K_j. We check
every anchor and every plane; no symmetry assumption enters the primary check.

Each binary plane has a unique representation by 0<a<b<a xor b. There are
511*510/6=43,435 planes. For each k != j, let H_k(U) consist of the functionals
z compatible with both basis vectors of U. Compatibility with a basis is
equivalent to compatibility with all of U: an evaluation of a linear
combination can be nonzero only if some basis evaluation is nonzero. Hence

    K_k subset H_k(U).

H_k(U) is a subspace, being the annihilator of the labels u_i for which
r_ij != r_ik and some member of U evaluates nontrivially. The complete census
checks dim H_k <= 2. Unlike P120, dimension two really occurs: at anchor 0,
U=span(1,508), H_1 has dimension two. The P120 dimension-one lemma cannot be
reused here.

Every subspace L_k of H_k is enumerated: zero, every one-dimensional subspace,
and the whole plane if H_k has dimension two. For a choice (L_k)_(k != j):

1. Reject it if some pair L_k,L_l is incompatible. Checking unions of the
   nonzero evaluation supports of basis vectors checks all elements of each
   subspace, by the same linearity observation.
2. Form Q as the span of labels u_i such that, for some k != j, r_ij != r_ik
   and some z in L_k evaluates nontrivially on u_i.
3. Compatibility with K_j implies K_j subset Q^perp. Therefore this tuple has
   the upper bound

       sum_k delta_k <= 9 - dim Q + sum_(k != j) dim L_k.

The actual tuple L_k=K_k appears in this enumeration, survives the necessary
compatibility tests, and satisfies this upper bound. The enumeration need not
assert that every surviving relaxed tuple is realized by a decoder.

Planes with identical ordered partner spaces are grouped only to avoid
rechecking the identical subspace product. Q and the product depend solely on
those spaces and the anchor. The complete plane-to-space census is still
performed, and multiplicities total 43,435 at each anchor.

## 4. Exhaustive lemma and conclusion

The exact results are:

| Anchor | Planes | Distinct ordered partner-space tuples | Compatible subspace choices | Largest upper bound |
|---|---:|---:|---:|---:|
| Each of 0,...,7 | 43,435 | 2,131 | 52,832 | 10 |
| 8 | 43,435 | 2,251 | 39,485 | 9 |
| Total | 390,915 | 19,299 | 462,141 | 10 |

Thus every possible deficiency tuple has sum at most ten, and **copy cost is
at least 71**. The census is over a finite covering of the zero-pattern
constraints, not over a finite set of sampled complex coefficients.

`verify.py` recomputes the complete table and partner-dimension histograms,
compares every receipt field with `CERTIFICATE.json`, and verifies the model
and witness identities. The separate `independent.py` derives binary labels
from independent columns of the Gram pairing matrix, obtains partner spaces
by row reduction and annihilators, and enumerates Cartesian products without
the primary's incremental compatibility pruning. It tests compatibility by
requiring equal forced coefficient values at each live row. It checks two
anchor representatives and explicitly verifies four puncture-stabilizing
coordinate permutations whose orbits are {0,...,7} and {8}. Its aggregate
counts and upper bounds agree with the primary's nine-anchor census.

Mutual compatibility matters. For anchor 0 and U=span(1,508), dropping it
allows upper bound 11 (the apparent price 70); retaining it gives ten.
This is a failed necessary-condition relaxation, not a price-70 decoder.

## 5. Sharp witness, including nine active terms

Initially set t_i=-2r_i0. Column 0 is zero and the term costs are

    (0,8,9,9,9,9,9,9,9).

For the single live root r=e_0-e_2, change its shift to t_i=-2r_i2. This
preserves the all-pairs identity and makes every term active, with costs

    (1,8,8,9,9,9,9,9,9), total 71.

The primary checks all 12,544 identity entries for each witness using integer
denominator clearing. The separate checker uses rational coefficients and
computes the term costs from the actual binary pairing submatrices, without
the full-column-rank shortcut. The optimum is therefore exactly 71 whether
zero terms are allowed or all nine terms must be active.

## 6. Coordinate-permutation corollary and scope

The fixed simplex family is invariant under all nine-coordinate permutations:
they permute its columns and root lines, with possible sign changes of the
chosen pair-root representatives. These signs preserve supports and the
all-pairs equation after applying the corresponding row signs to D and T.
The pairing is also unchanged modulo two. Hence the same sharp floor holds
for every coordinate-permutation image of F.

These are precisely the frames obtained by choosing a singleton coordinate
and a perfect matching of the other eight coordinates, then taking one pair
root and one triple root (the pair plus the singleton) for each matched pair.
There are 9 * 8!/(2^4*4!) = **945 distinct frames**. The four pair-root lines
identify the matching and the singleton, so no two choices coincide.
The verifier constructs all 945 and checks their orthogonality. No claim is
made for frame punctures outside this orbit or for a different simplex family.

The ratio 71/112 exceeds 64/112. This rules out a copied-information saving
for this family before paying any additional realization costs. It is not a
complete moment invoice or a lower bound for multiplication. Other normals,
other punctures, masked identities, two unrestricted factors, shared-copy
billing and physically different operation contracts remain outside scope.
All selected-supplier all-size/compiler, common-label/mutable-source, hosting,
precision/tape, recovery, analytic-transfer and bit-interface obligations
remain untouched.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
Apache-2.0. No independent human review or Lean proof is claimed.
