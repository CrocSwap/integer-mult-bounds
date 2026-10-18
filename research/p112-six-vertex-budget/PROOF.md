# Excluding the eleven-piece profile `2,3,4^4,6^5`

Let `K` be any characteristic-zero field. On the pinned 112 nonframe E8
root lines, with representatives `r_t` and nine-bit labels `ell(t)`, put

```
C = {c_h : c_h(t) = <r_t,h>, h in K^8},
w(q) = rank_F2 {ell(t) : q(t) != 0}.
```

The representatives are doubled roots of squared norm eight. Their common
scale affects neither supports nor binary label ranks.

**Theorem.** Eleven independent pieces spanning `T`, with
`dim(T intersect C) >= 5`, cannot have respective weight upper bounds

```
2,3,4,4,4,4,6,6,6,6,6.
```

This excludes one actual profile in the pinned TWOSIDE `(b,t)=(5,6)` residue
of DreamingOfClouds/PR3154. The new ingredient is a six-vertex version of
Nick Petalas/PR3176's mixed-edge simplex calculation. The endpoint support
allowance is 108; both geometric branches require more.

## Geometric premises and finite coverage

The replay reconstructs all 120 E8 root lines and removes the eight fixed
orthogonal frame lines. It checks the data against the unchanged project
input. The live Gram sum is `112 I`, so `h -> c_h` is injective over `K`.
Every live label is odd. Hence weights two, three and four have support
capacities two, four and eight. A complete enumeration of all 788,035 binary
six-flats proves support capacity twenty at weight six.

We retain the written Weyl-chamber argument in
[the predecessor proof](vendor/MIXED-PROOF.md). The replay checks its finite
inputs: positivity of the simple-root coordinates, 960 simple reflections,
the maximum 36 root lines on six-node parabolics, and the seven-node counts
`42,28,22,14,16,23,37,63`. The 63-line face has a root normal and the 42-line
face has a D7 normal. The other faces have too few perpendicular roots.

Consequently every nonzero direction of live support at most 72 is a scalar
multiple of one of 248 rational projective directions. These are the 120
root lines and 128 D7-normal lines of live support seventy. The complete
1,080-line norm-four Weyl orbit has support histogram
`70:128,73:896,76:56`; its reflection closure and the chamber normal's
membership are checked. Root supports have sizes 53 and 56. These facts
also give the minimum nonzero code support 53.

The classification applies over `K`. The rational perpendicular roots of
a field-valued direction span rank at most seven. Rank at most six would
give a generic real normal with the same perpendicular root set, contradicting
the 36-line parabolic cap when support at most 72 leaves at least forty live
zeros. Thus their rational kernel is a line. The field-valued direction is
a `K`-scalar multiple of its rational generator, to which the real argument
applies. Rational matrix ranks are preserved by characteristic-zero extension.

The standard Weyl-chamber theorem is an explicit mathematical dependency.
These finite checks do not formalize it or the complete decoder reduction.

## Quotient normalization gives six independent affine vertices

Set `D=T intersect C`, `Q=T/D`. Then `dim Q <= 6`. Choose five pieces `A`
of weights `2,3,4,4,4`, with common support union `S`. Its size satisfies

```
s = |S| <= 2+4+8+8+8 = 30.
```

Call the remaining six pieces `q_0,...,q_5`; their weights are `4,6^5`.
The selected five pieces together with any one `q_i` have support union
at most `30+20=50<53`. Their images in `Q` are independent. Otherwise a
nonzero combination of those independent original pieces would be a nonzero
codeword of support below 53.

Therefore `dim Q=6`, `dim D=5`, and `Q/span(A)` has dimension one. Every
`q_i` has nonzero image in this last quotient. Rescale these pieces to make
their images equal, preserving every support. There are combinations `a_i`
of the selected pieces such that

```
c_0=0,    c_i=q_i-q_0-a_i in D, i=1,...,5.
```

The five `c_i` are independent because their coefficients on `q_1,...,q_5`
are distinct unit vectors in the original piece basis. Injective evaluation
gives five independent directions `h_i` with `c_i=c_(h_i)`. Put `h_0=0`.
Every edge is nonzero and has support at most

```
|supp(c_i-c_j)| <= s+|supp(q_i)|+|supp(q_j)| <= 30+20+20=70.
```

Thus all edges belong to the complete root/D7 alphabet above. Outside `S`,
the six endpoint values are the six vertex evaluations with the same shift
`q_0(t)` at each coordinate. The total available endpoint support is

```
U = sum_i |supp(q_i)| <= 8+5*20=108.
```

## Mixed-edge branch requires 121 incidences

Suppose some edge is not a root. Translate one endpoint to zero. The
predecessor's 128 checked even signed permutations preserve the actual E8
frame and normalize its D7 line to

```
a=(1,0,1,0,1,0,1,0).
```

A common nonzero scalar makes the second endpoint exactly `a`. Translation,
coordinate permutation, coordinate sign and common scaling preserve equality
multiplicities and support after allowing an arbitrary common shift.

Every other vertex `x` lies on a projective alphabet line `u`, and `a-x`
lies on another line `v`. These lines are distinct because the vertices
are affinely independent. Solve `a=s*u+t*v`, with `s,t` nonzero. A nonzero
rational two-coordinate minor gives a unique rational solution even over `K`.
Checking all 30,628 unordered direction pairs gives exactly 58 possible
vertices. All their coordinates are half-integral. Two vertices are joined
when their difference is in the alphabet. The graph has 595 edges.

The four further vertices of our six-vertex simplex form a four-clique.
Complete enumeration gives 4,459 cliques. Their ranks together with `a` are
`3:63,4:1260,5:3136`. Only the 3,136 rank-five cases can occur here.

For six values at coordinate `t`, an arbitrary common shift leaves at least

```
k_t = 6 - max_z #{i : <r_t,h_i>=z}
```

nonzeros. Choosing the most frequent value as the new zero attains this
coordinate bound. Removing up to thirty common coordinates can remove at
most the thirty largest `k_t`. Across all independent cliques, the remaining
support-sum histogram is

```
121:448,122:112,123:560,124:560,125:560,133:784,134:112.
```

Hence `U>=121`, contradicting `U<=108`. `RESULT.json` retains an attaining
simplex and one thirty-line cut. Its cost spectrum is `0:6,1:31,2:46,3:29`.
Delete the 29 costs of three and one cost of two. The remaining sum is
`31+45*2=121`. This is attainment in the arbitrary-cut/common-shift
relaxation, not a realization of the small-piece supports.

The separate checker reconstructs intersections using Gram systems, joins
two disjoint ordered edges to enumerate four-cliques, and uses integer
elimination for ranks and explicit equality counts for costs. It reproduces
all vertices, edges, cliques, rank counts and the histogram. The two
implementations share the root reconstruction and written classification.

## All-root branch requires 120 incidences

If every edge is a root direction, the retained A2 plane argument puts the
vertices into a common scalar multiple of an affine A5 root simplex. The
root-plane check covers all 7,140 pairs. Three rational root lines in a plane
form A2 when there is a third line; its coefficient ratios are `+1` or `-1`.
Applying this to each pair of the independent root directions makes their
scales agree up to sign. After absorbing signs, the five doubled roots
have pairwise inner product four.

The replay builds every ordered star up to Weyl symmetry. At each step it
uses all reflection orbits perpendicular to the current prefix. That subgroup
fixes the prefix pointwise, so retaining all its orbits covers every extension.
The successive orbit sizes are `240,56,27,16,10`, leaving one rank-five star.
An independently constructed explicit star has the same spectrum.

On all 120 root lines, the minimum-nonzero cost spectrum is

```
0:4,1:36,2:60,3:20.
```

Relax the eight missing frame lines and the thirty common small-support
lines to any 38 deleted full-root coordinates. The 82 smallest surviving
costs sum to `4*0+36*1+42*2=120`. Thus `U>=120>108`, a contradiction.
No claim of sharpness for the actual fixed frame and actual small supports
is needed.

Both branches are impossible, proving the theorem.

## Actual residue and prior coverage

The unchanged pinned `bk2b.py` reproduces all 24 original cell counts. A
separate transcription reproduces the 77 historical `(5,6)` survivors and
checks this profile. Its raw excess is `29<30`, with prefix support caps
`58,78,98,118,138`. This is a historical binding, not a claim that the other
76 profiles still remain unresolved.

Every weight-certified six-piece quotient basis and every partition into
two weight-six bins plus paid cuts is checked. The minimum paid-cut budget
is twenty. Thus the earlier eight-/ten-cut and twelve-cut anchor theorems
do not certify this profile through that sufficient weight-only route.
Actual unknown support overlaps might improve such covers; their absence
is not claimed. PR3169/PR3171 concern shorter families at the same required
code dimension; deleting a piece here guarantees only dimension four.
PR3174/PR3177's eleven-piece profiles have all weights at most five and
do not directly dominate this profile's five weight-six pieces.

Fresh overlap was checked in PR bodies and Discussion comments. The active
fourteen-common-cut claim on `2,3,4,6^8` is separate. A zero exact-text match
is not a novelty certificate; the explicit mathematical premise and prior
applicability checks above state the added scope.

No full C5, `C(P112)>=64`, physical supplier, complete multiplication theorem
or new kappa is established. The original decoder reduction and the written
Weyl-chamber argument remain dependencies. The selected frontier is unchanged.
