# Independent finite proof of the P112 root-star cost-64 floor

This is a computer-assisted theorem about one finite support alphabet. It is
not a physical supplier, a formal proof-assistant result, or a multiplication
theorem. The finite premises below are reconstructed by two separate programs.
The result and endpoint argument independently corroborate David Arias'
concurrent PR1236 at `ee8437bd9879272094e20c024cd34a53c4e84cd8`, found during
the submission overlap refresh. The distinct second implementation uses
pivoted maximal-clique enumeration, not PR1236's lattice/quadratic-form
obstruction. No new theorem priority is claimed.

## Model and statement

Use the E8 roots of squared norm two and identify antipodal roots. Remove the
eight lines of the coordinate frame
`f = e_(2a) +/- e_(2a+1)`, `a=0,...,3`, leaving P112. Write
`G_ij = <r_i,r_j>`. The binary label pairing of PR717/PR1226 is

```text
S_ij = (G_ij + 1) mod 2.
```

The E-graph includes the diagonal and the orthogonal pairs. A masked decoder
has finitely many real or complex rank-one terms `d_k t_k^T` whose sum equals
`2G` on that graph. Transpose is ordinary transpose, not conjugate transpose.
In particular, on any eight-line orthogonal frame F the sum is `4 I_8`.

For each of the 120 root-line normals alpha, permit the supports

```text
C(alpha) = {i in P112 : <r_i, alpha> != 0},
N(alpha) = C(alpha) minus alpha's own line, if that line is live.
```

Each positive-cost term must have **exactly** one of these supports on each
side. Its cost is `beta_k = rank_F2 S[supp(d_k), supp(t_k)]`. Arbitrary nonzero
coefficients on those supports are allowed; arbitrary proper sub-supports are
not included. Additional terms of pairing rank zero may have arbitrary
supports. In particular, the free odd-entry singleton corrections in PR717
are allowed. Zero terms can be discarded.

**Theorem.** Every such decoder has `sum beta_k >= 64`. Eight coordinate-star
terms attain 64. This closes the fixed-family assembly window left by
Navinor's PR1226; it does not strengthen the fractional inequality itself.

## Exact finite premises

Both implementations independently generate the 120 lines and the same
punctured frame. Their internal root order differs from PR1226's order; the
certificate specifies this package's order by a hash and explicit witness roots.

1. P112 has exactly **1,260** orthogonal eight-line frames. Every live line is
   in **90** frames. Every orthogonal pair of distinct live lines extends to a
   live frame: 2,856 such pairs belong to ten frames each, and 448 to fifteen.
2. The 240 indexed supports and all **57,600 ordered support pairs** have
   cost histogram `7: 7616`, `8: 37440`, `9: 12544`. Indexing retains the eight
   duplicates `C(f)=N(f)` at punctured normals, as in PR1226.
3. A support misses a live frame precisely when it is `N(alpha)` with alpha
   live and the frame contains alpha. Every cost-seven atom has at least one
   such live trimmed endpoint. There are 1,792 atoms with one and 5,824 with
   two; these meet 1,170 and 1,080 frames respectively.
4. The graph on P112 joining distinct **nonorthogonal** lines has clique
   number **eight**. The complete clique counts, including the empty clique,
   are:

   | Size | Count |
   |---:|---:|
   | 0 | 1 |
   | 1 | 112 |
   | 2 | 2,912 |
   | 3 | 25,088 |
   | 4 | 88,704 |
   | 5 | 161,280 |
   | 6 | 145,152 |
   | 7 | 55,296 |
   | 8 | 4,032 |

   The primary checker visits all **482,577** cliques by increasing-vertex
   recursion, with no size cutoff. The second checker finds all **27,968**
   maximal cliques by pivoted Bron-Kerbosch recursion, then takes the union of
   all their subsets. Every clique of a finite graph extends to a maximal
   clique, so this is a separate complete coverage argument. Both recover the
   entire displayed census and an explicit size-eight witness.

The support/frame assertion in item 3 also has a direct explanation. A frame
is a real basis, so a nonzero root normal cannot be orthogonal to every frame
line. Removing the normal's own line can remove the final intersection only
when that line belongs to the frame. If it does belong, it is orthogonal to
the other seven lines. The programs check this identity on every indexed
support and every frame; no generic-position assumption is used.

## From the premises to the floor

Call a term a *hit* on F when both supports meet F. Its restricted outer
product has rank at most one and vanishes unless it hits F. Since the target
on F is `4 I_8`, at least eight terms must hit every frame. A cost-zero term
cannot hit a frame: every binary pairing between two members of F is one,
whereas a matrix of binary rank zero has all entries zero.

Let n count positive-cost terms. Each costs at least seven, by item 2.
Suppose the total cost were below 64. Then `8 <= n <= 9`.

* If `n=8`, every term must hit every frame. But cost below 64 forces at
  least one cost-seven term. Its live trimmed endpoint belongs to 90 missed
  frames, contradicting the eight-hit requirement.
* If `n=9`, every term must cost seven: the integer total is exactly 63.
  Select one live trimmed endpoint alpha_k from each term, which item 3
  permits. A frame containing alpha_k is missed by that term. No frame can
  contain two selected endpoints, since it would receive at most seven
  hits. Repeated endpoints are therefore impossible. Two orthogonal
  endpoints are also impossible, by item 1. The nine selected endpoints
  would consequently form a nonorthogonality nine-clique, contradicting
  item 4. This holds for any choice when a term has two eligible endpoints.

All finite term counts have been covered. This is an integer compatibility
argument: the averaged coverage bound `784/13` from PR1226 stays valid, but
does not account for two terms missing the same frame.

## Attainment and accounting limits

For the eight removed frame roots f_k take
`d_k(i)=t_k(i)=<r_i,f_k>`. Orthogonality and norm two give

```text
sum_k <r_i,f_k><r_j,f_k> = 2 <r_i,r_j>.
```

All 12,544 entries are checked exactly, and each term costs eight. This is
the existing coordinate decoder, credited to the predecessor lineage; the
result being corroborated is its optimality in the specified mixed-cost root-star family.

The result prevents a reduction of the copied-information constant below 64
within this alphabet, even before charging source access, gather arithmetic,
helper frames, dirty restoration, recursive realization, precision, or
hosting. It does not assert that all other costs are fixed, nor rule out
improvements to them. No complete new invoice, native word, improved moment,
or kappa is claimed. Selected PR1094 and its compiler, all-size, mutable-source,
whole-call hosting, precision/tape, analytic and bit-interface assumptions
are unchanged.

Further trimming, unions of stars, other punctures, different label pairings,
and positive-cost terms outside this alphabet remain outside the theorem.
The assertion is for the displayed coordinate-frame puncture; no unverified
frame-transitivity argument is needed. It covers complex coefficients because
the only coefficient-field fact used is the rank of `4 I_8`.
