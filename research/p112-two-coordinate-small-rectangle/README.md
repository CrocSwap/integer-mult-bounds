# Two P112 coordinate terms resist a small free rectangle

**Scoped obstruction, with exact finite premises; no new kappa or supplier.**
On the fixed P112 coordinate decoder, mix any two of its eight coordinate
terms with one free rectangular correction by any `M in GL(3,C)`. If the
correction is nonzero and uses at most **23 rows and 23 columns**, at least two of the three
replacement terms have COPY pairing rank at least eight. The whole decoder
therefore retains COPY cost at least **64**, and its separate COPY power bill
cannot improve. Identity mixing attains the bound, including a nonzero odd
singleton correction of matrix rank nine. A second statement covers zero-factor
cases when each support has size at most **11**.

This answers a restricted part of Arham Tahir's [PR1331](https://github.com/CrocSwap/integer-mult-bounds/pull/1331)
/ [Discussion1316](https://github.com/CrocSwap/integer-mult-bounds/discussions/1316)
two-coordinate handoff. PR1331 allows any free rectangle but mixes only one
coordinate. Here two coordinates mix coherently; the rectangle is small.
Neither result subsumes the other. The concurrent
[Discussion1360](https://github.com/CrocSwap/integer-mult-bounds/discussions/1360)
claim by Arham Tahir concerns arbitrary nine-term factorizations of a singleton
completion; our larger-rectangle/two-coordinate domain is complementary.
That claim is provisional and is not a proof dependency.
The initial singleton claim was refined
after the same finite calculation gave erasure distance at least twelve, then
free-compatible erasure distance at least twenty-four.

## Model and quantified statement

Use the pinned PR845/PR717 geometry in [SOURCES.json](SOURCES.json). The 112
live root lines are the E8 lines minus the standard orthogonal eight-frame.
Let `X` be their `112 x 8` coordinate matrix, with entries `0,1,-1` and
`XX^T = 2G` and column rank eight. For binary labels `L_i`, the nondegenerate ambient form satisfies

`B_ij = <L_i,L_j> = (G_ij + 1) mod 2`.

For index sets `A,C`, define `rho(A,C) = rank_F2 B[A,C]`. A scalar term
`d t^T` costs `rho(supp(d),supp(t))`. Coefficients are complex and determine
supports; they are **not** reduced modulo two. This is the inherited
separate-term COPY objective, not a new physical implementation contract.

Choose distinct coordinate columns `x=X[:,k]`, `y=X[:,l]`. Choose arbitrary
complex vectors `u,v`, with supports `U,V`, satisfying

`B[U,V]=0`, and either

- `1 <= |U| <= 23` and `1 <= |V| <= 23`, or
- `|U| <= 11` and `|V| <= 11`, allowing zero vectors.

The pairing condition makes `uv^T` a free correction
on odd entries: it vanishes on all constrained even entries. For arbitrary
`M in GL(3,C)`, form

`D = [x,y,u] M`, `T = [x,y,v] M^(-T)`.

Thus `DT^T = xx^T + yy^T + uv^T`, using **ordinary transpose**.
The other six coordinate terms stay fixed.

**Theorem.** At least two terms of `D T^T` have pairing rank at least eight.
Consequently their sum of ranks is at least sixteen, and the complete
decoder has COPY cost at least sixty-four. This statement includes all
28 coordinate pairs, all such supports and coefficients, every complex
invertible factor change, and the zero-correction boundaries.

## Finite geometry behind the proof

Any nonzero complex combination `a*x+b*y` has exactly one of five support
patterns. The exceptional projective coefficient ratios are `x`, `y`,
`x+y`, `x-y`; every other ratio gives `supp(x) union supp(y)`. Indeed, a row
with two nonzero coordinate entries can cancel only at `a/b = +1` or `-1`.
This exhausts complex coefficients, including nonreal ratios.

For each of the 28 pairs, the exact census is:

| Support stratum | Size | Span dimension | Erasure distance | Free-compatible distance |
|---|---:|---:|---:|---:|
| `x` | 56 | 8 | 24 | 24 |
| `y` | 56 | 8 | 24 | 24 |
| `x+y` | 76 | 9 | 12 | 34 |
| `x-y` | 76 | 9 | 12 | 34 |
| generic union | 88 | 9 | 24 | 40 |

The erasure distance of a support `S` is the minimum **positive** value of
`#{i in S : f(L_i)=1}` over the 511 nonzero ambient binary functionals.
Functionals annihilating the whole support have weight zero and are excluded
from that minimum. The certificate checks their count as well. For the
**free-compatible** distance, additionally require the deletion support
`W={i in S : f(L_i)=1}` to have at least one live common odd neighbor `j`,
meaning `B[W,{j}]=0`. The checker records the complete filtered weight
spectrum as well as its minimum.

All **700 ordered within-pair support pairings** have rank at least eight:
448 have rank eight and 252 have rank nine. The census checks all 71,540
support/functional combinations, not a random sample or a floating-point
rank calculation. Complete supports, weight spectra, pairing matrices and
two boundary witnesses are in [CERTIFICATE.json](CERTIFICATE.json).

**Erasure lemma.** Removing at most eleven indices preserves the label span
of every stratum. If a deletion reduced the span, some ambient functional
would vanish on the retained span but not on the original span. Its positive
weight on the original support would be no greater than the number deleted,
contradicting the minimum of twelve. This is a finite-dimensional linear
algebra argument, so enumeration of all deletion subsets is unnecessary.

**Free-compatible erasure lemma.** Suppose `U,V` are nonempty and
`B[U,V]=0`. If removing `U` from a stratum lowered its span, the same
functional argument would give a nonempty witness `W` contained in `U`.
Every index of `V` is then a common odd neighbor of `W`. Its weight must
therefore be at least the free-compatible distance, which is at least 24.
Consequently `|U|<=23` preserves every stratum span. Transpose for `V`.
Nonemptiness on both sides is essential to this argument. The unconditional
lemma covers the theorem's smaller domain when a factor is zero.

**Boundaries of these premises.** For pair `(0,1)` and the plus stratum, deleting
canonical root indices `100..111` lowers its span from nine to eight. The
primary checker records functional 257 as a witness; the second checker
recomputes the span loss directly from Euclidean pairings. Thus twelve cannot
replace eleven in the universal **span-preservation premise**. This is not
a decoder improvement and does not show that the theorem's eleven bound is
sharp. In fact this twelve-row deletion has **no common odd neighbor**, so it
cannot support a nonzero free rectangle.

The separate `free_boundary` witness uses pair `(0,1)`, the `x` stratum and
24 explicitly listed rows. They have common odd neighbor `{0}`, and deleting
them lowers the span from eight to seven. Thus 24 cannot replace 23 in the
uniform **free-compatible span-preservation premise**. This is a valid free
support rectangle, but no factor-change saving or sharp decoder threshold is
claimed. A 23-by-one subrectangle supplies an additional exact positive fixture.

## Proof over arbitrary complex factor changes

Let `a_j in C^2` be the first two entries of column `j` of `M`, and `b_j in C^2`
the first two entries of column `j` of `M^(-T)`. The top-left block of
`M M^(-1)=I_3` gives

`sum_(j=1..3) a_j b_j^T = I_2`.

Since each summand has complex rank at most one, at least two indices `j`
have **both** `a_j != 0` and `b_j != 0`. This argument does not assume that
`u,v` are nonzero or that either three-column factor has full rank.

Fix such an index. The corresponding left factor is a nonzero combination
of `x,y` plus a multiple of `u`; outside `U` its support contains the
original combination's support. More precisely, if that combination has
support `S`, then `S minus U` is contained in the actual left support.
The same argument gives `C minus V` on the right for one of the five strata
`C`. The applicable erasure lemma, with cap 23 for a nonzero free rectangle or
cap 11 without that nonemptiness assumption, gives

`span(L_(S minus U)) = span(L_S)`,
`span(L_(C minus V)) = span(L_C)`.

Pairing rank depends only on these two spans. Hence the survivor pairing
rank equals `rho(S,C) >= 8`. Enlarging either support cannot decrease rank,
so the actual term costs at least eight. Apply this to the two active indices.
The remaining term has nonnegative cost. The other six original terms each
cost eight. This proves the theorem, including arbitrary cancellations,
triangular changes, nonreal coefficients, and zero-vector cases.

The free-rectangle condition supplies both masked-decoder validity and the
23-per-side strengthening. The unconditional 11-per-side rank argument does
not require it.

## Optimistic complete COPY screen

For `0 <= a < 1`, write `q=1-a > 0`. If the three replacement ranks are `r_j`,
then at least two individually satisfy `r_j>=8`, so

`sum_j r_j^q >= 2 * 8^q`.

Adding the six unchanged terms gives at least `8 * 8^q`, the original COPY
bill. This is stronger than a sum-of-ranks bound: a sum of sixteen alone
would not establish the two-child power inequality. The comparison requires
unchanged width, normalization and common multiplicity for the COPY calls.
It already rejects this family as a COPY-saving route when all extra work
is granted zero cost. It does not price another child histogram, owner layout,
shared-copy convention or a complete supplier; other charges and denominators
cannot be silently cancelled if their contracts change.

## Reproduce and failure controls

Python 3.12, standard library only; from the repository root:

```sh
python3 -I -B research/p112-two-coordinate-small-rectangle/verify.py
python3 -I -B research/p112-two-coordinate-small-rectangle/independent_check.py
python3 scripts/research_package.py --package research/p112-two-coordinate-small-rectangle
```

Expected primary and independent final lines:

```text
PASS_P112_TWO_COORDINATE_SMALL_RECTANGLE pairs=28 strata=140 characters=71540 pairings=700 erasures=11 nonzero_free_erasures=23 fixtures=9 controls=9 copy_floor=64
PASS_P112_SMALL_RECTANGLE_INDEPENDENT strata=140 characters=71540 pairings=700 boundaries=12,24 controls=9
```

The registered replay runs both checkers and verifies historical provenance
and working input pins. Both remain active under `python3 -I -O -B`.
To regenerate the receipt into a **new** path, pass `verify.py --write PATH`;
ordinary verification does not rewrite artifacts.

The primary checker uses the pinned source's exact labels. It replays nine
Gaussian-rational fixtures on all 12,544 entries each: identity/sharpness,
nonsymmetric dense mixing, complex ordinary transpose, a four-by-five free
rectangle, zero-left, zero-right, zero correction, an actual cancellation, and a
23-by-one rectangle. For the sharp singleton it also checks that adjoining
each singleton to all eight coordinate columns has rational rank nine.
Hence `[X,u][X,v]^T` has rank nine: the first factor is injective and the
second transpose is surjective in dimension nine.
Nine controls reject a nonfree correction, singular matrix, inverse without
transpose, out-of-domain twelve-row zero-product and twenty-four-row nonzero corrections,
source drift, omitted input,
a false twelve-erasure extension, and a changed support receipt.

The second checker imports neither the primary checker nor the predecessor
geometry. It independently builds doubled Euclidean E8 roots and the full
binary Gram pairing. Its nine-row basis generates all 511 nonzero dual
**evaluations**, and elimination runs from the opposite bit direction. It
recomputes all supports, both spectra, 700 ranks and both boundary span losses.
Nine corrupt-receipt controls cover pair omission, support changes, incorrect
distance, incorrect pairing rank, repeated boundary deletion, wrong roots and
a false summary, incorrect free-compatible distance and omitted odd neighbor.
The primary checker's factor-change examples and source pins
are separate coverage; the second checker verifies the finite proof premises.
These are two implementations by the same AI-assisted contributor, not human
review or proof-assistant formalization.

## Scope, provenance and credit

Base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`, fetched from main at entry.
Chooser nonce: `44ef721f92930cbeabe2df5c07bc184b`; complex-mechanisms;
`complex-masked-decoder`, scope key `2a6f2c726b78f9ae7d26`, priority revision 2.
[TASK.json](TASK.json) records the local card, refinement, overlap and limits.
PR1331 head `f08b698cc2bd74e2425486728a008e531fc35f0e` is a contextual
predecessor, fetched anonymously; no theorem or code from that PR is imported.

Credit Arham Tahir / PR1331 for the one-coordinate free-rectangle predecessor
and explicit two-coordinate question; DreamingOfClouds / PR717 for the masked
B14 model and PR446/595 for the separate-total lineage; Joel Pulikkan /
GamingPuzzled / PR620 for the coordinate COPY64 decoder; Mihir Srivastava /
PR845 for the exact P112 geometry; themilkman216 / PR968 for the pairing-cost
model; and woklerx / PR1077 for the task's complex-coefficient positive control.
This account's PR1304 studies fixed A8 simplex normals on matching punctures,
which is a different all-pairs family. No predecessor file is modified.
This package and retained inputs are Apache-2.0.

No physical word, gathering, restoration, frame changes, owner admission,
precision bounds, all-size/compiler result or new selected bound is supplied.
The inherited common-label/mutable-source, hosting, precision/tape, analytic
transfer and bit H1-H5 obligations are not checked by this package. The
selected full cold replay is unrelated and was not run. Hosted CI, maintainer
acceptance and independent human review are also not claimed.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

## Open next questions

Can a nonzero free rectangle with at least twenty-four indices on one side
exploit a span-losing coordinate support to reduce the two-coordinate COPY
moment? This is the first size the strengthened proof leaves open. A feasible
first step is to take the recorded 24-row `free_boundary` witness and its
common odd neighbor `{0}`, then solve the actual GL(3,C) cancellation
constraints while pricing every term. The blocker is that a free support
rectangle and span loss do not satisfy the coupled inverse-factor identities
or establish any gain. The twelve-row unrestricted witness is already known
to have no common odd neighbor and should not be used for a nonzero correction.
The zero-factor cases above eleven per side are a separate open branch of this
proof. Larger rectangles, three or more mixed coordinates, other punctures and
shared-copy objectives remain outside scope.
