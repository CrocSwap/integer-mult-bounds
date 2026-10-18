# A rank-five cover transfer excludes the P112 profile `5,6^8`

Let `K` be a characteristic-zero field. Use the pinned 112 nonframe E8 root
lines `r_t` and their nine-bit labels `ell(t)`. Put

```
C = {c_h : c_h(t)=<r_t,h>, h in K^8},
w(q) = rank_F2 {ell(t) : q(t) != 0}.
```

**Theorem.** Nine independent pieces spanning `T`, with
`dim(T intersect C)>=6`, cannot have weight upper bounds `5,6^8`.

This is the maximal profile without weight seven in the original TWOSIDE
`(b,t)=(6,3)` cell. The new ingredient is a small affine cover transfer.
It lets the existing weighted A6 theorem of Nick Petalas/PR3186 apply to a
rank-five support. The mixed branch and the geometric classification are
retained from that predecessor. This does not settle the full cell or C5.

## The new affine cover lemma

Every set `A` of at most twelve points of affine `F2^4` is contained in an
affine hyperplane together with at most four extra points.

Choose four distinct points outside `A`. Their affine span has dimension
at most three, so some affine hyperplane `H0` contains all four. Its opposite
half `H1` is another affine hyperplane. Since `H0` has eight points and at
least four are outside `A`, at most four points of `A` lie outside `H1`.
This proves the lemma. The bound four is sharp for any twelve-point `A`,
since a hyperplane has only eight points. A thirteen-point set needs at
least five extras, so the twelve-point hypothesis cannot be increased.

**Odd-label consequence.** Suppose the labels of an actual support `A`
span at most five binary dimensions and `|A|<=12`. A support of rank at
most four already lies in a four-flat. Otherwise let `V` be its
five-dimensional span. All support labels have leading bit one, so
`Q={x in V : x_0=1}` is an affine four-space. Apply the lemma inside `Q`.
The affine three-space `H1` spans a linear four-space `U`, and its odd part
is exactly `H1`. Therefore

```
A subset Lambda(U) union E,    dim_F2 U=4,    |E|<=4.
```

Here `E` consists of actual support coordinates. Missing cube points used
to choose `H0` may be punctured roots or labels that are not roots. Their
absence causes no difficulty. The claim covers only the actual support,
not every root label in its five-dimensional extension. The larger
four-flat may contain extra root coordinates, which is permitted.

`cover_transfer.py` constructs a half-space from four absent points. It
checks all 64,839 subsets of size at most twelve. A separate finite oracle
tries all thirty affine hyperplanes for each of all 65,536 subsets. It
checks the sharp four-point bound and all 560 thirteen-point failure
controls. Each affine hyperplane's eight odd labels have binary rank four.
These finite checks corroborate the written proof; the proof itself is
independent of the enumeration.

## Inherited geometric and support premises

The unchanged [predecessor proof](vendor/PREDECESSOR-PROOF.md) supplies the
following statements with their written arguments and finite inputs:

- The live Gram sum is `112 I`, so `h -> c_h` is injective. A nonzero codeword
  has at least 53 live coordinates.
- A weight-five support has at most twelve live coordinates; weight six
  has at most twenty. The replay checks all 3,309,747 five-flats and all
  788,035 six-flats against the canonical puncture.
- Every nonzero direction of live support at most 72 is a scalar multiple
  of one of 120 root rays or 128 eligible D7-normal rays. This holds over
  every characteristic-zero field by rational-kernel reduction.
- Independent root rays with root-ray differences have a common scale and
  form a root simplex. A6 root stars have one Weyl orbit.
- Weyl transformations act invertibly and linearly on the nine-bit label
  space and preserve its leading-bit functional.

The replay checks root reconstruction against the live input, simple-system
positivity, all 960 simple reflections, all 7,140 root planes, the D7-normal
support spectrum and the complete star stabilizer partitions. The standard
Weyl-chamber theorem remains a written mathematical dependency. These tests
do not formalize it or the original decoder reduction.

## Quotient normalization produces seven endpoints

Choose the weight-five piece and one weight-six piece, denoting their
support union by `S`. Then `|S|<=12+20=32`. The remaining seven pieces
`q_0,...,q_6` have weight at most six. Write `D=T intersect C`.

The quotient `T/D` has dimension at most `9-6=3`. The selected two pieces
together with any `q_i` have total support at most `32+20=52<53`. Their
quotient images are independent. Otherwise a nonzero combination of the
independent original pieces would give a nonzero codeword supported on
fewer than 53 coordinates. Thus `dim(T/D)=3` and `dim D=6`.

Modulo the two selected images, all seven remaining quotient images are
nonzero in a one-dimensional space. Rescale them to have equal images.
Subtract suitable combinations `s_i` of the selected two pieces and set

```
c_0=0,    c_i=q_i-q_0-s_i in D,    i=1,...,6.
```

The six codewords are independent by their distinct coefficients on
`q_1,...,q_6`. Injective evaluation gives seven affinely independent
vertices `h_0=0,h_1,...,h_6` in `K^8`. Each nonzero edge has support at most
`32+20+20=72`, so its direction is in the complete root/D7 alphabet.

At a coordinate outside `S`, the seven endpoint evaluations equal the
seven vertex evaluations after one common shift. Consequently at least

```
7 - maximum equality multiplicity
```

endpoints are nonzero there. Their total support allowance is `7*20=140`.

## The two inherited geometric branches

If an edge has a D7 direction, the pinned predecessor normalizes it to
`a=(1,0,1,0,1,0,1,0)` by a frame-preserving signed permutation and scaling.
All other vertices belong to its exact 58-vertex anchored graph. Among
all 7,350 five-cliques, exactly 3,360 have the required rank six. Removing
the 32 largest coordinate costs leaves at least 142 support incidences
in every such case. The unchanged `vendor/endpoint.py: mixed_six` replays
that census, including its complete rank and support histograms.
Thus this branch exceeds the allowance 140.

If all edges are root directions, the vertices are one scaled A6 root
simplex. Its full120 minimum-nonzero cost spectrum is

```
0:1, 1:21, 2:63, 3:35,    total 252.
```

Arbitrary removal of forty full-root coordinates leaves only 137. That
relaxation fails to contradict 140 and is retained as a losing control.
A Weyl normalization maps the actual puncture to an orthogonal eight-line
frame `F`, while preserving all binary support ranks.

PR3186 proves the following weighted cover statement for the A6 cost `c`:
for every such frame, binary six-flat `V`, binary four-flat `U` and at most
four extra root coordinates `E`,

```
sum_{r outside F union Lambda(V) union Lambda(U) union E} c(r) >= 141.
```

The unchanged `vendor/cover.py: weighted_cover` replays its finite proof.
It covers all 2,025 orthogonal frames and all 788,035 six-flats. The
63 six-flat masks with cost at least 55 give 7,140 relevant frame prefixes.
A potentially violating four-flat must contain at least seven cost-three
labels; all 135 such masks are tested, giving 963,900 residual tests.
The removed cost is at most 111, so at least `252-111=141` remains.
The retained proof explains the threshold pruning and completeness.

Apply the new odd-label consequence to the actual weight-five support
after Weyl normalization. Its size is still at most twelve, and it lies
inside a four-flat plus four extra coordinates. The other selected support
lies in a six-flat. The inherited weighted cover therefore applies to a
set containing the actual small-support union. At least 141 endpoint
incidences remain outside `S`, exceeding 140. This closes the root branch
and proves the theorem over every characteristic-zero field.

## Actual residue, overlap and limits

The original unmodified `vendor/bk2b.py` and a separate transcription
both retain this excess-35 profile among seventeen historical `(6,3)`
survivors. Exactly six have maximum weight at most six, and each is
componentwise bounded by `5,6^8`. This theorem excludes all six original
profiles as a corollary. Four smaller profiles already follow from PR3162
with at most eight cuts.
The fifth, `5,5,6^7`, permits only 132 endpoint incidences, below both the
inherited mixed bound 142 and arbitrary-cut root bound 137. Six is not a
claim of six newly resolved profiles or a complete current residue count.
The eleven historical profiles containing weight seven are outside this
theorem.

The earlier root cover accepted rank four plus four arbitrary coordinates.
It did not state the rank-five transfer above or this maximal profile
application. The earlier two-six-flat, ten-cut theorem does not accept the
rank-five support's twelve paid cuts, and the twelve-cut anchor theorem
requires a rank-four nonbasis piece, absent here. These are checks of
named sufficient routes, not a universal novelty claim. The active
fourteen-common-cut question on `2,3,4,6^8` is separate.

No full C5, `C(P112)>=64`, supplier admission, complete multiplication
theorem or new kappa is proved. The selected frontier remains unchanged.
The source classification, standard Weyl-chamber theorem and original
decoder reduction remain explicit dependencies. This is an author-checked
written proof and finite replay, not independent human or proof-kernel
review.
