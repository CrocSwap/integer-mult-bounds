# Eleven scalar centres cannot reduce E8 bit copy rank below 72

This proof uses the definitions and the ten-centre theorem in `TEN-PROOF.md`.
Write `rho(w)` for the rational rank of the root support of a binary word.
Write `e_S` for the indicator of a set of root lines, and write `k_q` for
row `q` of the binary corrector matrix `K`. Root vectors have squared length
4. A sign change in a root vector does not change any binary word.

## Statement and scope

Every binary factorization `K=A B^T` with at most eleven scalar terms has
source-reader pairing-rank sum at least 72. The drop-pricing theorem of
PR #446 therefore excludes a copy-rank improvement in this retained-total
model with at most eleven centres.

The result does not bound twelve or more centres, or a different model of
totals and gates. It does not give a positive improvement to the bit bound.

The factor-rank cases other than `(9,11)` and `(11,9)` were proved in
`TEN-PROOF.md`. It remains to prove the following statement:

> If a binary space `U` of dimension eleven contains `C`, then every basis
> of `U` has rational support-rank sum at least 72.

For factor ranks `(9,11)`, a zero column on the rank-nine side removes a
term and reduces to the ten-centre theorem. Otherwise its columns are
nonzero words in `C`, so their support spaces are all eight-dimensional.
Each pairing rank is then the support rank of the opposite column. Those
eleven columns form a basis of their column space `U`, which contains `C`.
The transpose case is identical.

The quotient `U/C` has dimension two. It has three nonzero cosets. All
nonzero vectors in `C` have support rank eight.

## Finite facts and their verification

The following exact facts concern only the 120 pinned E8 root lines.

1. `C` has dimension nine. Its word-weight distribution is
   `0:1, 56:255, 64:255, 120:1`. Every nonzero word has support rank eight.
2. The eight Weyl classes of root hyperplanes, the sets `D_H`, and their
   outside support spans have the descriptions in `TEN-PROOF.md`. In particular,
   a non-E7 hyperplane has at most 42 root lines.
3. In an E7 hyperplane `H=n^perp`, the outside weights of the 512 words of
   `C` have distribution
   `0:1, 1:1, 24:63, 25:63, 28:128, 29:128, 32:63, 33:63, 56:1, 57:1`.
   The unique outside-weight-one word is `k_n`, with support `H union {n}`.
4. The seven maximal proper E7 root-flat types have 16, 21, 13, 10, 36, 21,
   and 30 root lines. Each complement spans all seven dimensions. Thus a
   proper root span in E7 has at most 36 lines, and the complement of every
   proper root span has rank seven.
5. In E7, the nonperpendicular neighbors of any root line span seven
   dimensions. Every pair of distinct root lines has 16 common
   nonperpendicular neighbors, distinct from the pair.
6. Distinct root lines have inner product 0 or plus or minus 2. All root
   vectors have squared length 4.

`parabolic_check.py` verifies items 1, 2, 5, and 6, including reflection
closure. `e7_complements.py` verifies item 4 by all seven simple-root
deletions of E7. `eleven_facts.py` verifies item 3. The same Weyl-chamber
argument used for E8 in `TEN-PROOF.md` shows that these seven E7 deletions cover
all maximal proper E7 root flats. Thus the checks cover every proper root
span, not sampled flats. All rank decisions below full rank use exact
rational arithmetic.

## Every coset has a star description

For every coset `V` other than `C` that has a word of rank at most seven,
there is a centre `a` in `V` and a set `Q` of root lines with these properties:

- The lines in `Q` belong to the support of `a`.
- Each `q in Q` is perpendicular to every other line in the support of `a`.
  In particular, the lines in `Q` are pairwise perpendicular.
- The low-rank words in `V` are exactly the satellites `a+k_q`, for `q in Q`,
  together with `a` itself if `rho(a)<=7`.
- Every satellite has rank seven. The centre can have rank eight; in that
  case the centre is not a low-rank word.

To prove this, choose a low-rank word `v` and a root hyperplane `H` that
contains its support. If `H` is not E7, the proof in `TEN-PROOF.md` gives precisely
this description with centre `a=v` and with the isolated support roots as
`Q`.

Now let `H=n^perp` be E7 and put `t=k_n`. Define `A` and `B` as in `TEN-PROOF.md`:
`A` consists of the isolated roots in the support of `v`, and `B` consists of
the isolated roots in its complement within `H`. The only possible low-rank
words are `v`, `v+t`, `v+k_q` for `q in A`, and `v+t+k_q` for `q in B`.
The last two groups have rank seven. The sets `A` and `B` cannot both be
nonempty, by the common-neighbor fact.

Put `d=rho(v)` and let `e` be the rank of its complementary support in `H`.
If `d<=6`, the E7 complement fact gives `e=7`, and the neighbor-rank fact
gives `B` empty. If `e<=6`, then `d=7` and `A` is empty.
If `B` is nonempty or `e<=6`, take `a=v+t` and `Q=B union {n}`. The support
of `a` is `{n}` together with the complementary support in `H`, so every
line in `Q` is isolated there. Its rank is `1+e`. Its satellite at `n` is
`v`; its other satellites are the listed words indexed by `B`.
Otherwise `B` is empty and `e=7`; take `a=v` and `Q=A`.
This proves the description in every case.

## Small changes to a codeword

Suppose `0!=c in C`, `|S|<=11`, and `rho(c+e_S)<=7`. Then for some root `n`,

\[
 c=k_n,\qquad n\in S,\qquad S\setminus\{n\}\subset n^\perp,
 \qquad \rho(c+e_S)=7.                                      \tag{2}
\]

Choose a root hyperplane `H` containing the support of `c+e_S`. If `H` is
not E7, the support of `c` outside `H` has at least `56-42=14` lines. Those
lines would all have to belong to `S`, a contradiction. Thus `H=n^perp`
is E7. The outside-weight distribution shows that `c=k_n`: every other
nonzero word has at least 24 outside lines. Since `k_n` has just the root
`n` outside `H`, cancellation requires `S outside H={n}`. Inside `H`, the
remaining support is `H\S`, with at least 53 lines. It cannot lie in a
proper E7 root span, which has at most 36 lines. Its rank is therefore seven.

## The basis defect

Let a basis of `U` be given. The defect of a vector is `8-rho(w)`. Suppose,
for contradiction, that its total defect `D` is at least 17. The coset bound
in `TEN-PROOF.md` gives at most eight defects in any one nonzero quotient coset.
Hence all three cosets contain selected low-rank basis vectors.

Give these cosets star descriptions with centres `a_1,a_2,a_3`. Put
`d_i=rho(a_i)`. Let `Q_i` be the roots of the satellites selected in the
basis, and let `n_i=|Q_i|`. Say that a centre is selected when the centre
itself belongs to the basis. We may count a selected rank-eight centre as
well; it contributes zero defect. There are no other positive-defect words.
Thus, if `delta` centres are selected and `n=n_1+n_2+n_3`,

\[
 \delta+n\leq11,\qquad
 D=\sum_{i:\ a_i\text{ selected}}(8-d_i)+n.                \tag{3}
\]

Remove the selected isolated roots from each centre:

\[
 u_i=a_i+e_{Q_i},\qquad \rho(u_i)=d_i-n_i.
\]

The rank equality follows because each removed root is perpendicular to
all remaining support roots. The quotient images of the three centres sum
to zero, so `c=a_1+a_2+a_3` belongs to `C`. Set
`S=Q_1 triangle Q_2 triangle Q_3`, the symmetric difference. Then

\[
 u_1+u_2+u_3=c+e_S,\qquad |S|\leq n\leq11,
\]

and

\[
 \sum_i\rho(u_i)
 =24-D-\sum_{i:\ a_i\text{ not selected}}(8-d_i)
 \leq7.                                                   \tag{4}
\]

Two distinct roots cannot belong to both `Q_i` and `Q_j`: the four
corresponding satellites would sum to zero. Therefore

\[
 |Q_i\cap Q_j|\leq1\quad(i\ne j).                         \tag{5}
\]

### Independent centres: `c!=0`

Equation (2) applies. Write `c=k_n` as there. The sum `u_1+u_2+u_3` has
support rank seven, while (4) bounds the sum of their support ranks by
seven. Its support spans `n^perp`. Consequently each `u_i` is supported in
`n^perp`, `D=17`, and every unselected centre has rank eight.

Consider an unselected centre `a_i`. Its remaining support and its selected
isolated roots give an orthogonal direct sum of all eight dimensions.
Since `u_i` is supported in `n^perp`, the root `n` belongs to the span of
`Q_i`. If its line is not itself in `Q_i`, expand it in these pairwise
perpendicular roots. Every nonzero coefficient is plus or minus one half:
this follows from the root inner products and squared lengths. Its squared
length then forces exactly four nonzero coefficients. Thus four roots of
`Q_i` are not perpendicular to `n`.

By (2), every one of these four roots must occur an even number of times
among the three sets `Q_i`; otherwise it would belong to `S` outside
`n^perp`. Each therefore belongs to one of the other two sets. This
contradicts (5). We conclude that `n` belongs to `Q_i` for every unselected
centre.

If no centre is unselected, all three centres belong to the basis and
`k_n=c` is their sum. The root `n` belongs to at least one `Q_i`, so its
satellite and that centre give a basis dependence.

If one centre is unselected, its selected satellite at `n`, together with
the other two selected centres, sums to `c+k_n=0`.

If two centres are unselected, their two sets `Q_i` both contain `n`.
Since `n in S`, the third set must also contain `n`. The three selected
satellites at `n` sum to `c+3k_n=0` over the binary field.

If all three centres are unselected, the same three-satellite dependence
holds. Each case contradicts basis independence.

### Dependent centres: `c=0`

Any two centres are independent, because their quotient images are distinct
nonzero elements of `U/C`. We use the following elementary real-linear
bound. If `a_3=a_1+a_2`, every root in their supports occurs in exactly two
of the supports. Lift such a root `q` to

\[
 (q,0),\quad(0,q),\quad\text{or }(q,q)
\]

according as it belongs only to `a_1`, only to `a_2`, or to both. These
vectors lie in the direct sum of the two rational support spaces.
For a root isolated in `a_1`, the dual vector `(q,0)` pairs to zero with
every other lifted root. For a root isolated in `a_2`, use `(0,q)`; for a
root isolated in `a_3`, use `(q,-q)`. Each self-pairing is nonzero.
Hence all distinct selected satellite roots have independent lifts. If
there are `N` such roots, then

\[
 N\leq\min(d_1+d_2,d_1+d_3,d_2+d_3).                       \tag{6}
\]

At most two centres can be selected.
If none is selected, `D=n<=11`, a contradiction.
If two are selected, all three centres lie in their span. A repeated root
among the selected satellites would give a dependence with these centres.
Thus `n=N`. If the selected centres are `a_1,a_2`, equations (3) and (6)
give `D<=16-d_1-d_2+d_1+d_2=16`.

It remains to consider exactly one selected centre, say `a_1`. A root
cannot occur in both `Q_2` and `Q_3`: those two satellites would sum to
`a_1`. Each of the other pairwise intersections has at most one root by
(5). They cannot both be nonempty: the four satellites from these two
intersections, together with `a_1`, would sum to zero. Therefore there is
at most one repeated root in the full list of selected satellites. Using
(6),

\[
 n\leq N+1\leq d_1+\min(d_2,d_3)+1,
 \qquad D\leq8+\min(d_2,d_3)+1\leq17.
\]

Equality `D=17` requires `d_2=d_3=8`, exactly one repeated root, and
`N=d_1+8`. The selected-vector count is then at least
`1+n=d_1+10`, so `d_1<=1`. A centre in a nonzero coset is nonzero, hence
`d_1=1`. Only one root line lies in a one-dimensional support, so
`a_1=e_r` for one root `r`. The repeated root must be `r`, since the only
allowed repetition involves `Q_1`.

But `a_2+a_3=e_r`. If `r` is isolated in the rank-eight centre `a_2`,
removing it gives `a_3` rank seven, a contradiction. The same argument
applies with `a_2,a_3` exchanged. Thus equality 17 is impossible here too.

Both centre cases give `D<=16`. Every basis therefore has rank sum at least
`11*8-16=72`. This closes factor ranks `(9,11)` and `(11,9)`, and completes
the eleven-centre obstruction.
