# Rank-six P112 star slices and the sharp frame-demand relaxation

## 1. Fixed object and theorem

Use the 120 E8 root lines in the doubled coordinates and order archived in
`inputs/PR1323-MODEL.json`. Remove the standard orthogonal eight-frame F0 to
obtain the fixed 112 live lines. For norm-two representatives, write
`G(i,j) = <r_i,r_j>` and `N(i,j) = (G(i,j)+1) mod 2`.

The 240 tagged supports are `C(alpha)`, the live lines not orthogonal to alpha,
and `N(alpha)`, that support with alpha itself removed. A tag is
`2*normal_line + self_trimmed`. Duplicate tags for punctured normals are retained.
The original support-pair matrix has rank seven for 7,616 ordered tagged pairs
(6,720 distinct support pairs), as in Navinor's PR1226 and David Arias's PR1236.

Here a **rank-six descendant** is any pair of subsets of one of those original
rank-seven parent pairs whose binary pairing matrix has rank exactly six.
Both factors may be trimmed simultaneously. This is a larger support class
than the original exact C/N theorem. Parents of rank eight or nine, descendants
of rank at most five, other punctures and shared-copy contracts are excluded.

The exact census and the domination lemma below establish:

1. Every maximal one-axis nonzero-codeword cut has rank exactly six in this
   fixed model: 127 per tagged parent, 967,232 cases in total.
2. A rank-six descendant meets at most 1,120 of the 1,260 live orthogonal
   eight-frames on both factors. That maximum is attained. The sharp per-parent
   joint maxima are 1,080 for 5,824 tagged parents and 1,120 for 1,792.
3. The averaged frame-demand lower bound for this class is exactly 54.
4. The integer **frame-demand relaxation** over rank-six descendants has sharp
   copy bill 60. Its exact ten-term witness is in `COVERING.json`.

Item 4 concerns supports and necessary rank demand. It does not assert an exact
masked identity, a realized supplier, or any value of kappa.

## 2. Why one-axis codewords cover arbitrary joint rank-six cuts

Let M be a binary matrix of rank r and factor it as `M = A B`, where A has full
column rank r and B has full row rank r. Its column code consists of the
vectors `A z` for `z in F2^r`: B maps its coefficient space onto F2^r.

For a nonzero z, the zero set `Z(z) = {i : (A z)_i = 0}` is the largest row
support lying in that functional's kernel. Deleting the nonzero codeword's
support leaves `M[Z(z), all columns]` with rank at most r-1. For a row
restriction of rank exactly r-1, choose a nonzero z in the one-dimensional
kernel of its A factor. Its retained rows lie in Z(z). Since that restriction already has
rank r-1, the larger maximal restriction also has rank exactly r-1.

Now suppose a simultaneous row and column restriction `A_S B_T` has rank r-1.
Each of A_S and B_T has rank at least r-1. If both had rank r, B_T would still
map onto F2^r and A_S would remain injective, so their product would have rank r.
Thus at least one of the two one-axis restrictions has rank exactly r-1.
Extend that restriction to one of the maximal functional zero sets on its
axis, and restore the other factor to its full parent support. The resulting
one-axis slice:

- contains the joint descendant on both factors;
- still has rank exactly r-1;
- meets every frame that the joint descendant meets.

This proves that the maximum frame coverage over **all** joint rank-six
descendants of a rank-seven parent equals the larger of its maximal row-cut
and maximal column-cut coverages. No bound on the number of deleted labels is
assumed. This argument does not extend an optimization priced at rank five
to one priced at rank six: rank exactly r-1 is essential to the claim.

The two orientations of every tagged parent occur in the ordered census, so
the transposed record supplies the complete column-cut maximum. Every nonzero
word in each seven-dimensional column code is enumerated, not just words of
minimum Hamming weight from PR1323.

## 3. Exact census and averaged bill

Both implementations construct every live orthogonal frame and every original
support-pair rank. They then enumerate all 127 nonzero words for every rank-seven
parent, check the rank of each retained support pair, and count its frame hits.

The primary implementation generates the root lines explicitly, enumerates
column spans, and uses bit-set clique recursion. The separate implementation
validates the roots using simple-root Weyl reflections, enumerates linear
functionals on independently obtained row coordinates, and lists frames using
sets. They agree on every per-parent maximum, witness, minimizer count, and
digest of all 127 `(cut, frame_hits)` records, and on every certificate field.
Both belong to this AI-assisted contribution; this is not an independent human
review or a proof-assistant formalization.

The one-axis per-parent maxima are 1,080 (5,824 pairs), 1,110 (896), and 1,120
(896). Restoring the opposite factor by the lemma and using transposed records
gives the joint maxima in Section 1. There are 23,340 distinct retained row
supports across the full tagged census.

On each live frame F, the constrained masked identity has right side `4 I_8`.
Each paid outer product has rank at most one, so at least eight terms must meet
F on both factors. A cost-zero term has a zero binary pairing matrix on its
support rectangle. Since N is one everywhere on F-by-F, such a term cannot
meet F on both factors and cannot supply any of those eight ranks.

Summing the required hits over 1,260 frames gives 10,080. A rank-six term supplies
at most 1,120 hits. Thus the uniform averaged inequality gives

```
copy bill >= 10080 * (6/1120) = 54.
```

The maximum-hit witness attains the per-term efficiency in this calculation.
This is a sharp single-term capacity bound; it is weaker than the simultaneous
integer frame constraint.

## 4. At least ten rank-six terms

The rank-seven parent classification says both supports are self-trimmed
(or identical C/N supports for a punctured normal), with the two normals having
odd inner product. Two punctured normals are orthogonal, so at least one normal
of each parent is live. Choose one such live normal a for each descendant.

The parent's support N(a) avoids every live frame containing a. Every subset of
that support also avoids those frames. Thus a descendant misses all 90 frames
through its chosen live normal.

Seven or fewer terms cannot satisfy the rank-eight demand. Eight terms would each have to
meet every frame; none of these descendants does. Suppose nine terms were
feasible. A frame could then be missed by at most one term. The nine chosen
live normals must be distinct, and no two can be orthogonal: every orthogonal
live pair belongs to a live eight-frame, as recounted by PR1236/PR1242 and the
frame enumeration. We would have nine pairwise odd root lines.

For completeness, the predecessor's integer-dependence proof excludes those
nine lines. Nine rational norm-two roots in eight dimensions have a primitive
integer dependence `sum c_i v_i = 0`, with some c_i odd. Their Gram matrix
modulo two is J+I of size nine; its kernel consists of the constant vectors.
Hence every c_i is odd. But

```
(1/2) ||sum c_i v_i||^2
  = sum c_i^2 + sum_(i<j) c_i c_j <v_i,v_j>
  = 9 + 36 = 1 mod 2,
```

contradicting the zero dependence. This obstruction is credited to David
Arias's PR1236 and independently corroborated by Hanson Sun's PR1242. Trimming
more support cannot undo the inherited misses.

Consequently any feasible all-rank-six frame cover has at least ten terms and
copy bill at least 60. `COVERING.json` attains ten terms: both exact checkers
recompute each parent rank, each cut's code membership, the actual rank six,
and all 1,260 frame hit counts. This proves the relaxation's optimum is 60.

## 5. Search and limits

The complete capacity census is exhaustive. The optional MILP proposal search
is narrower: 5,376 distinct maximum-hit frame patterns, sorted by their missing
frame masks, with pattern index 20 forced by the assignment seed, and ten
distinct patterns chosen. It stops after a feasible incumbent or a 120-second
solver limit. The search receipts record the runtime, versions, candidate hash
and explicit terms. A floating-point proposal is accepted only after exact
standard-library checking. Search failure would not be an impossibility theorem.

The recorded first witness has frame-hit counts 8 (376 frames), 9 (648), and
10 (236), but leaves 21 live diagonals outside all ten support rectangles.
That is a concrete obstruction to this particular witness being a decoder:
its diagonal sum is zero there for every possible coefficient choice, whereas
the required diagonal is four. Cost-zero odd corrections cannot touch those
diagonals. This distinguishes the sharp frame relaxation from masked exactness.
One bounded refinement added coverage of every live diagonal to the same
5,376-pattern search. It timed out after 120 seconds without a feasible
incumbent; the finite coverage class was not exhausted and no infeasibility
conclusion is drawn. See `DIAGONAL-SEARCH.json`.
The refinement retained the first enumerated support representative of each
frame pattern. Deduplicating by frame pattern preserves the frame-only
problem, but does not preserve diagonal-coverage possibilities. The failed
refinement is therefore also restricted by this representative choice.

The complete supplier cost has not been realized. For this optimistic screen,
all helper endpoints, source access, frame changes, extra copied information,
dirty restoration, hosting and recursive overhead are assigned zero cost;
only the separate-term copied rank is priced. Even this favorable screen does
not supply coefficient exactness. Necessary frame coverage is not sufficient
for the diagonal and orthogonal-entry equations. Free odd-entry corrections
cannot repair a wrong diagonal. A complete decoder would have to satisfy
`sum d_k(i) t_k(j) = 2 G(i,j)` on all N(i,j)=1 entries with these actual supports,
then pay every physical and recursive charge. No such decoder is claimed.
