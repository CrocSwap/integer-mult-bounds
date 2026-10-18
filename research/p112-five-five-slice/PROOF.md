# Deleting the seven exposes an impossible P112 slice

Let `K` be a characteristic-zero field. Use the pinned 112 nonframe E8
root lines, with doubled representatives `r_t` of squared norm eight and
binary labels `ell(t)`. Define

```
C = {c_h : c_h(t)=<r_t,h>, h in K^8},
w(q) = rank_F2 {ell(t) : q(t) != 0}.
```

**Slice theorem.** Eight independent pieces of respective weights bounded
by `5,5,6^6` cannot span a space `T` with `dim(T intersect C)>=5`.

**Actual-profile corollary.** Nine independent pieces of weights bounded
by `5,5,6^6,7` cannot have code-intersection dimension at least six.
In fact the corollary places no weight restriction on the ninth piece.

This is a new application of the retained A5 geometric bound, using a
codimension-one deletion before quotient normalization. It answers one
actual weight-seven handoff from Nick Petalas/PR3192. It does not establish
full C5, the complete decoder floor, supplier admission or a new kappa.

## Geometric premises

The retained geometry and written root-simplex arguments come from
PR3176/PR3186 and PR3188, with the E8/P112 lineage in
[the retained notice](vendor/NOTICE.md). Exact source heads and bytes are
in [SOURCES.json](SOURCES.json).

The replay reconstructs the root system, frame, simple-root coordinates
and live labels, and compares them with the unchanged repository input.
The live Gram sum is `112 I`, so evaluation `h -> c_h` is injective.
The full five-/six-flat enumerations have respectively 3,309,747 and
788,035 subspaces and maximum live capacities twelve and twenty.
Consequently a weight-five piece has at most twelve support coordinates,
and a weight-six piece has at most twenty.

Every nonzero codeword has support at least 53. Every direction of live
support strictly below seventy is a root direction. Here is the retained
classification argument specialized to the needed threshold. Under the
standard real Weyl-chamber theorem, perpendicular roots form the subsystem
on the zero-pairing simple nodes. The replay checks simple-system
positivity, all 960 simple reflections, the six-node maximum 36 root
lines and the seven-node counts

```
42,28,22,14,16,23,37,63.
```

A direction of live support at most 69 has at least 43 perpendicular live
root lines, so only the 63-line E7 face is possible. Its normal is an E8
root. The 120 root normals have live support 53 or 56. All other normals
therefore have support at least seventy, proving both assertions.

For a `K`-valued direction with at least 43 rational perpendicular roots,
let `Z` be their rational span. If its rank were at most six, a generic
real normal to `Z` would have exactly the same perpendicular root set,
contradicting the 36-line bound. Thus `Z` has rank seven. Its kernel is a
rational line, so the `K` direction is a scalar multiple of a real rational
root normal. This proves the same classification after field extension.

The standard Weyl-chamber theorem is a written dependency, not a formal
proof-kernel result of the replay.

## The eight-piece slice

Let the two small pieces be `a,b`, put `S=supp(a) union supp(b)`, and call
the other six pieces `q_0,...,q_5`. Then `|S|<=24` and each `q_i` has support
at most twenty. Write `D=T intersect C` and `Q=T/D`. The hypothesis gives
`dim Q<=3`.

For every `i`, the three images of `a,b,q_i` in `Q` are independent. A
nonzero dependence would give a nonzero codeword supported on at most
`12+12+20=44<53` coordinates, because the original pieces are independent.
Therefore `dim Q=3`, `dim D=5`, and every `q_i` has nonzero image in the
one-dimensional quotient `Q/span(a,b)`.

Rescale the `q_i` to equalize these last images. Their supports do not
change. Choose `s_i in span(a,b)` so that

```
c_0=0,    c_i=q_i-q_0-s_i in D,    i=1,...,5.
```

The five codewords are independent, by their distinct unit coefficients
on `q_1,...,q_5` in the original piece basis. Injective evaluation gives
five independent directions `h_i`, with `h_0=0`. Every nonzero edge has
support at most

```
|supp(c_i-c_j)| <= 24+20+20=64<70.
```

Hence all fifteen edges are root directions. The retained A2 plane lemma
puts the six vertices into one common scalar multiple of an affine A5
root simplex. In more detail, three distinct root lines in a plane form
A2, with coefficient ratios `+1` or `-1`. Comparing every pair of the five
independent directions makes their scales agree after absorbing signs.
The doubled root representatives then have diagonal Gram entries eight
and off-diagonal entries four. This argument also holds over `K`.

The replay checks all 7,140 root planes. It constructs every root star up
to Weyl symmetry, retaining every orbit of the reflections perpendicular
to the current prefix. Such reflections fix the prefix pointwise. This
subgroup need not be the full stabilizer: retaining all its orbits can
only retain extra representatives. Complete extension orbit sizes are
`240,56,27,16,10`, leaving one A5 star.

## The inherited support count gives the contradiction

For a full-root coordinate `r`, define the cost

```
k(r)=6-max_z #{i in {0,...,5} : <r,h_i>=z}.
```

Outside `S`, the six `q_i` values equal the vertex evaluations after one
common coordinate shift. At least `k(r)` of them are nonzero. The
full-120 A5 cost spectrum, retained from PR3188, is

```
0:4, 1:36, 2:60, 3:20;    total cost 216.
```

The replay also checks this by a separate explicit star and root-class
count. Normalize to vertices `0,e_1+e_2,...,e_1+e_6`. The 56 integer-pair
root rays contribute `0:2,1:24,2:30`. For a half-root ray choose its first
sign positive. If `j` of signs two through six are positive, the endpoint
multiplicities are `j` and `6-j`; there are `2*binomial(5,j)` such rays,
including the two parity-compatible choices of the final signs. Their
costs give `0:2,1:12,2:30,3:20`.

A Weyl normalization may move the puncture, but it still removes only
eight full-root coordinates. The actual `S` removes at most another 24.
Relax these to any 32 coordinates. They remove at most
`20*3+12*2=84` cost, leaving at least `216-84=132` support incidences.
The six endpoints permit at most `6*20=120`, a contradiction.

This argument requires no transport of binary labels under the Weyl
normalization and no common-cut span theorem.

As a separate arithmetic control, PR3169's coordinate inequality gives
`15*53 <= 112+8*24+4*120`, namely `795<=784`, also impossible.
The older unrefined edge bound gives only `795<=9*24+5*120=816`, which
does not contradict. These are inherited inequalities applied to the new
slice, not newly discovered A5 bounds.

## Delete the ninth piece

Let `T9` be the nine-piece span in the actual-profile corollary, and let
`T8` be the span after deleting its ninth piece. Independence gives
`dim T9/T8=1`. Restricting the quotient map to `T9 intersect C` shows

```
dim(T8 intersect C) >= dim(T9 intersect C)-1 >=5.
```

The retained eight pieces have weights `5,5,6^6`, contradicting the slice
theorem. The deleted piece's weight is unused. The new step is deleting
this piece before choosing the small supports, instead of charging its
weight-seven endpoint directly.

## Historical binding and limits

The unchanged DreamingOfClouds/PR3154 filter and a separate transcription
retain the target among seventeen historical `(b,t)=(6,3)` profiles. Its
excess is `35<36`. This binds the actual caller; it is not a claim that
all seventeen still remain open. The eight-piece slice itself has excess
thirty at required dimension five, exactly the old strict threshold, so
it is not one of the four strict `(5,3)` profiles in PR3161.

PR3192 excludes `5,6^8`, without weight seven. PR3161's eight-cut
rank-six transfer and PR3162's ten-cut transfer do not directly certify
the target using the weight-only two-six-flat cover: its three-piece
quotient basis has minimum paid-cut budget twelve. The earlier
separate-twelve-cut span-four extension has a five-direction
counterexample; no such extension is assumed here. Actual overlaps
could help other approaches. Their absence is not claimed.

The final live overlap refresh found a [concurrent same-profile claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156#discussioncomment-19001119)
using the same deletion and PR3169's `795<=784` coordinate contradiction.
This package retains the A5 endpoint count `132>120` as its primary route,
with exact source replay and a separate root-class calculation. It claims
no exclusive priority for the deletion application. The concurrent claim
remains separately owned and is not cancelled by this completion.

The full decoder reduction, remaining profiles and C1-C7 remain outside
this package. Source reconstruction and the finite checks are
author-checked evidence with an internal mathematical review. They do
not constitute independent human review or formal verification of a
multiplication theorem. The selected frontier is unchanged.
