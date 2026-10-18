# A copy lower bound for Gaussian E8 scalar decoders

**Result.** Every fitting binary scalar-total decoder on the
60 Gaussian E8 lines has copy charge at least **40 Gaussian rank units = 80
rational rank units**, even with asymmetric reader/source sets and arbitrarily
many totals. Every fitting matrix has a row decomposition of charge 60, so the
result leaves the optimal charge in **[40, 60]**. It does not construct a new
supplier or improve the selected multiplication constant.

**Concurrent overlap and the additional result.** The bound 40, the uniform
weight 1/192 on the 640 maximum cliques, closure to flats, the interval
[40,60], and the conditional three-stage consequence are already present in
Sagar Thakrar / thakrarsagar's concurrent
[PR #738](https://github.com/CrocSwap/integer-mult-bounds/pull/738), discovered
during the final overlap refresh. The inspected head is
`9671c5d72f3119ba26f3774f40aa7130c67bcf77`
([proof](https://github.com/CrocSwap/integer-mult-bounds/blob/9671c5d72f3119ba26f3774f40aa7130c67bcf77/research/gaussian-clique-copy-bound/PROOF.md)).
This package supplies an independent replay of that bound, not a priority
claim for it. Its additional theorem is Section 5: **40 is the optimal
certificate value even with arbitrary nonnegative weights on all
inclusion-maximal cliques**. The inspected #738 proof establishes 40 as the
uniform-weight optimum and gives the weaker ceiling 48 for arbitrary
nonnegative clique weights, including non-maximal cliques. Our ceiling 40
does not cover that latter, larger class.

The weighted-clique proof method is adapted from Douglas R. Colkitt /
Mister-Meeseeks' [PR #703](https://github.com/CrocSwap/integer-mult-bounds/pull/703)
on the ten Hurwitz E8 lines. The Gaussian geometry, scalar decoder question,
rank accounting and previously found cost-60 symmetric decoder come from
Joel Pulikkan / GamingPuzzled's
[PR #620](https://github.com/CrocSwap/integer-mult-bounds/pull/620), retained in
[the extension-ring report](../e8-decoder-floors-and-cold14-notes/s1-extension-rings/REPORT.md).
The finite calculations here concern the Gaussian configuration and its full
reader/source pairing ranks. Neither the predecessor's geometry nor the
cost-60 upper bound is claimed as new.

The inspected #703 proof is pinned at commit
`358383e2f1b0f292d4d6eb897c06fd8558a4f5e6`
([source](https://github.com/CrocSwap/integer-mult-bounds/blob/358383e2f1b0f292d4d6eb897c06fd8558a4f5e6/research/hurwitz-asymmetric-copy-floor/PROOF.md)).
The pairing-rank accounting traces to DreamingOfClouds' #446/#595 work as
used by #620; the bound here is explicitly conditional on using that model.

## 1. Geometry and decoder model

Work with the 240 E8 roots in doubled standard coordinates in Q^8:

- vectors with exactly two nonzero coordinates, both in {−2, 2};
- vectors in {−1, 1}^8 with an even number of minus signs.

Let J act on each consecutive coordinate pair by (x, y) -> (−y, x).
Then J^2 = −I, J preserves the roots, and J is orthogonal. It gives Q^8 the
structure of a four-dimensional vector space over K = Q(i). A root r spans
the Gaussian line L_r = span_Q{r, Jr}. The roots partition into 60 distinct
such lines, with four roots on each line. The exact replay checks line
distinctness and the root partition.

Two different lines are called nonorthogonal when either r dot s or
r dot Js is nonzero. Write G for this nonorthogonality graph. Its complement
on distinct vertices is the orthogonality graph; every vertex of that graph
has degree 15. All ranks and orthogonality tests below use exact arithmetic.

A fitting matrix B over F2 has

    B_tt = 1,
    B_ts = 0 whenever t != s and L_t is nonorthogonal to L_s.

Its entries on orthogonal pairs are free and need not be symmetric. An
arbitrary scalar-total decomposition is

    B = sum_j 1_{R_j} 1_{A_j}^T  over F2,

with reader sets R_j and source sets A_j. Any finite number of totals is
allowed; sets may be empty and terms may repeat.

For a set S of lines, let V_S have the rows r and Jr for every representative
r in S. Define the charge of one total by

    q(R,A) = rank_Q(V_R V_A^T) / 2.

Equivalently, this is the rank over K of the restricted Hermitian pairing
between the K-spans of R and A. In particular it is an integer in {0,1,2,3,4}.
The total charge is Q = sum_j q(R_j,A_j). This is the Gaussian form of the
source/reader pairing-rank charge used by the predecessor's Theorem-C
relaxation. It is not the binary rank of the decoder rectangle, and a total
need not have full Gaussian rank four. The factor two is restored whenever
the charge is expressed in rational rank units.

## 2. Reducing all supports to finitely many flats

For a support S, define its closure by

    cl(S) = {t : L_t is contained in span_K(S)}.

A flat is such a closed set, including the empty set and all 60 lines.
Replacing R and A by their closures preserves q(R,A): every appended row of
V_cl(R) or V_cl(A) is a rational linear combination of existing rows. Thus
the Gram-block rank can neither increase nor decrease.

For a clique C of G, put

    a_C(R,A) = 1 if C meets both R and A, and 0 otherwise.

Closing supports can only increase this indicator. Consequently a local
inequality proved for every ordered pair of flats proves the same inequality
for every pair of arbitrary reader/source supports. This reduction concerns
the charge and the local indicator; it does not replace a decoder by a
different decoder or assume its fitting conditions survive closure.

There are exactly 2,272 flats. Their census, together with the number of
maximum cliques meeting each flat, is:

| Gaussian rank | Lines in flat | Number of flats | Maximum cliques meeting each flat |
| ---: | ---: | ---: | ---: |
| 0 | 0 | 1 | 0 |
| 1 | 1 | 60 | 128 |
| 2 | 2 | 360 | 256 |
| 2 | 3 | 320 | 308 |
| 2 | 6 | 30 | 320 |
| 3 | 4 | 960 | 436 |
| 3 | 6 | 480 | 492 |
| 3 | 15 | 60 | 512 |
| 4 | 60 | 1 | 640 |

The closure enumeration is exhaustive: start with the empty flat and the
one-line flats, and extend every rank-r span by every line outside its
closure. Every rank-(r+1) root-spanned subspace has such a basis extension.
Exact row reduction and closure deduplication produce the next level. Rank
four has the unique full flat. This induction proves coverage, rather than
assuming that the displayed census is a complete search domain.

## 3. The finite pairing-rank certificate

Let C be the family of all maximum cliques of G. Exhaustive graph search
gives exactly 640 of them, each of size 12, and proves there is no larger
clique. The key finite certificate is

    sum_{C in C} a_C(F,H) <= 192 q(F,H)                 (1)

for every pair of flats F,H.

The primary replay checks (1) for all 2,582,128 unordered pairs with
repetition; both sides are symmetric in F,H, so this covers all ordered
pairs. It computes the exact pairing rank and the number of maximum cliques
meeting both flats. The result is:

| Pairing rank q | Unordered flat pairs | Largest joint hit count | Allowed count 192q |
| ---: | ---: | ---: | ---: |
| 0 | 4,997 | 0 | 0 |
| 1 | 184,920 | 192 | 192 |
| 2 | 1,316,050 | 384 | 384 |
| 3 | 1,076,160 | 512 | 576 |
| 4 | 1 | 640 | 768 |

Its exact rank calculation reduces to small cases. Empty or full spans and
a one-dimensional side have immediate ranks. Two rank-two sides use their
two-by-two Gaussian Gram determinant and, when that vanishes, their entries.
For ranks two and three, write the hyperplane as n-perp. The pairing rank is
one if n lies in the rank-two span and two otherwise. For two rank-three
hyperplanes, with normals n and m, the rank is two if n and m are orthogonal
and three otherwise. These formulas all follow from

    q(F,H) = dim_K(F) - dim_K(F intersect H-perp).

The real-coordinate replay constructs each normal by exact rational nullspace
calculation. Because its spaces are J-invariant, one nonzero real normal
and its J-translate span the whole Gaussian normal line.

A separate replay uses four Gaussian-integer coordinates, independent flat
generation and exact nonzero minors. For each pair it certifies that q is
at least the ceiling of the joint hit count divided by 192. It may also use
the rigorous bound q(F,H) >= dim_K(F) + dim_K(H) - 4, since the pairing kernel
F intersect H-perp has dimension at most 4 - dim_K(H). This certifies (1)
independently without claiming to recompute the primary rank histogram.
Both exhaustive pair checks pass. They concern the actual source/reader
Gram block, not just the rank of F intersect H, the cardinality of either
support, or an assumed full-rank total.

When q=0 all lines across the two supports are orthogonal, so no clique can
meet both. Such totals are allowed and contribute zero to both sides. The
flat census and its individual hit counts help reproduce the check, but
they are not substitutes for the pairwise inequality (1).

By Section 2, (1) holds for arbitrary supports R,A as well.

## 4. The lower bound, including arbitrary asymmetric decompositions

Every maximum clique C contains only pairwise nonorthogonal lines, so the
fitting conditions imply B[C,C] = I_12. Over F2, the restriction of a
rectangle 1_R 1_A^T to C by C has rank a_C(R,A). Rank subadditivity gives

    12 <= sum_j a_C(R_j,A_j).

Sum this inequality over the 640 maximum cliques and apply (1) to each
total:

    640 * 12
      <= sum_j sum_{C in C} a_C(R_j,A_j)
      <= 192 sum_j q(R_j,A_j).

Therefore

    Q >= (640 * 12) / 192 = 40.

This argument handles every finite number of scalar totals. It requires no
symmetry of B, no minimum-rank assumption on B, no limit on its number of
totals, and no uniform rank assumption on the totals. The extension from the
finite local certificate to all decompositions is the displayed rank
argument, rather than an enumeration of decoders.

For the upper bound, decompose any fitting B into its 60 rows: for row t,
take R_t={t} and A_t equal to the nonzero positions in that row. The diagonal
condition puts t in A_t. Hence the Gram block has Gaussian rank exactly one,
and these 60 totals have total charge 60. In particular this upper bound
holds separately for every fitting matrix. It is an abstract charge bound,
not a claim of a physical supplier realizing it without additional costs.

## 5. Forty is the limit of this maximal-clique method

This section is a separate exact limitation of the proof method. It does not
prove that any actual decoder has charge 40.

For a line t, let H_t be the set of the 15 configuration lines orthogonal to
t. The geometry check verifies that these lines span the whole Gaussian
hyperplane t-perp. If t and u are orthogonal distinct lines, then

    q(H_t,H_u) = 2.

Indeed H_t and H_u both have dimension three, and the kernel of the pairing
on H_t against H_u is H_t intersect span_K(u) = span_K(u), of dimension one.

An inclusion-maximal clique C of G meets H_t exactly when t is not in C.
If t is in C, orthogonality excludes every element of H_t. If t is not in C
and C missed H_t, then t would be nonorthogonal to every element of C and
could be added, contrary to maximality.

Allow arbitrary nonnegative weights w_C on inclusion-maximal cliques. A
proof using only their principal-identity rank inequalities and a local
domination by q would require, for every pair of supports R,A,

    sum_C w_C a_C(R,A) <= q(R,A).                    (2)

Its resulting copy lower bound is sum_C |C| w_C. Apply (2) to the 900 ordered
orthogonal pairs through the rectangles (H_t,H_u), and sum. A clique of size
k contains no orthogonal pair. Among the 900 ordered orthogonal pairs,
exactly 15k have their first endpoint in C and exactly 15k have their second
endpoint in C, with no overlap. It therefore contributes

    900 - 30k

to the sum of the indicators. Since k <= 12,

    900 - 30k >= 45k.

The summed right side of (2) is 900 * 2. Consequently

    45 sum_C |C| w_C
      <= sum_C (900 - 30|C|) w_C
      <= 1800,

and this proof method cannot yield a lower bound exceeding 40. In the
certified uniform construction, the 640 size-12 cliques each have weight
1/192, attaining exactly 40.

This establishes optimality among such nonnegative weighted
**inclusion-maximal-clique** rank certificates. It does not address
certificates using non-maximal cliques, other submatrices or inequalities,
or additional algebraic information about the decoder.

## 6. Consequences and limits

The extension-ring report recorded a computational lower bound of 9 for its
bounded-total searches and a symmetric cost-60 solution. The result here
supplies a lower bound of 40 in the stated all-total asymmetric pairing-rank
model, with normalized charge

    x_K = Q/60 >= 2/3.

The report's approximate charge threshold for beating its bit-E8 comparison
is about 0.71. Since 2/3 is below that value, this bound does **not** exclude
an improved Gaussian construction. The interval [40,60], including the
region near its reported threshold, remains unresolved.

Conditionally applying exactly the report's Dfc accounting, Gaussian rank
scaling k=2 and port count v=60, the rational copy charge is at least 80:

    D/T = (s-1) * 120 - s * cst
        <= (s-1) * 120 - s * 80
         = 40s - 120.

Thus this optimistic accounting has no positive deficit for integer stage
counts s <= 3. It gives no exclusion for s >= 4. Helpers, source access,
restoration and recursive work are not supplied or certified here, and the
conditional accounting is not needed for the finite copy-floor theorem.

The scope is the fixed 60-line Gaussian E8 geometry, binary scalar totals,
the stated fitting pattern, and the source/reader pairing-rank charge.
Other geometries, altered patterns, vector-valued totals, rational sub-line
supports and different supplier formats are outside scope. This is a
finite mathematical argument supported by exact computation, not a
proof-assistant formalization or a proof of the full multiplication theorem.

Prepared for chinmayarvind23 with substantial OpenAI Codex assistance in
proof development, implementation and checking. No independent human review
is claimed.
