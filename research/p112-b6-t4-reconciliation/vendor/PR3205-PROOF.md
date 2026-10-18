# P112 shortening with thirty common coordinates

Let K be any field of characteristic zero. Let P be the 112 nonframe E8
root lines in the declared P112 data, with doubled representatives r_t of
squared norm eight. Define the evaluation code

```
C = {c_h : c_h(t) = <r_t,h>, h in K^8}.
```

## Theorem

Suppose `a_1,...,a_k,q_0,...,q_5` are collectively linearly independent
vectors in `K^112`. Let S be the union of the supports of the a_j. If
`|S|<=30` and every q_i has support at most twenty, their span T satisfies

```
dim(T intersect C) <= 4.
```

The supports are literal live coordinates. S is one common set, not a
separately chosen set for each edge or endpoint. No bound on k other than
collective independence is required.

This strengthens the support-29 lemma of Nick Petalas/PR3203 at
`f7951d9ca99feb1e54660dbe239941f6187948b1`. The new step retains the orthogonal
puncture in the root case and checks the six-vertex root/D7 case that becomes
possible at support thirty. The complete alphabet and anchored graph are
inherited from Nick Petalas/PR3176 at
`1111a074414c4d2be8b4e230133d873432780814`. This is a scoped code theorem,
not full C5, a decoder-floor proof, a supplier or a new multiplication exponent.

## Geometric dependencies

The declared, unchanged predecessor sources reconstruct all 120 root lines,
the deleted eight-line orthogonal frame and P. They check the following
finite facts. The general classification also uses the standard Weyl-chamber
theorem, an explicit written dependency rather than a proof-kernel result.

* The live Gram sum is `112 I`, so evaluation from `K^8` is injective.
* A subspace of dimension at most six contains at most 36 E8 root lines.
  The eight seven-node chamber faces have `42,28,22,14,16,23,37,63` lines.
  The qualifying 42-line face has a D7 normal; the 63-line face has a root
  normal. Root directions have live supports 53 or 56.
* The 1,080 projective D7 normals, generated as sums and differences of
  perpendicular roots, are Weyl-closed. Their live support distribution is
  `70:128,73:896,76:56`.
* A root plane has two lines, or the three A2 lines. In the latter case the
  third line's coefficients relative to the first two have ratio `+1` or `-1`.

Here is why the complete direction classification, including the field, is
applicable. A nonzero codeword of live support at most seventy has at least
42 perpendicular live root lines. Their rational span has rank at most seven.
If its rank were at most six, a generic real normal in its rational
annihilator would contradict the 36-line bound. Thus their rational kernel
is one-dimensional, and the K-valued direction is a K-scalar multiple of a
rational vector. Move its real rational generator into a closed Weyl chamber.
Only the D7 and E7 faces can have 42 perpendicular lines. The direction is
therefore a root or a Weyl transform of the D7 normal. The retained finite
inventory gives exactly 120 root lines and 128 D7 lines at this cutoff.
The same argument excludes every nonzero codeword of support below 53.

In primitive coordinates each of the 128 eligible D7 lines has exactly one
entry equal to `+1` or `-1` in each pair `(0,1),(2,3),(4,5),(6,7)`, up to
common sign. They form one orbit under even signed permutations preserving
the actual deleted frame. Swap within pairs to move the nonzero entries to
even positions, then change signs to make them positive. An unused zero
position corrects sign parity if necessary. Every line becomes

```
a = (1,0,1,0,1,0,1,0).
```

The replay checks all 128 such symmetries on the roots and frame, all 960
simple reflections and all 7,140 root-plane pairs. It does not silently
transport binary labels through an unrestricted Weyl normalization.

## Quotient normalization

Assume `D=T intersect C` has dimension at least five. Since `dim T=k+6`,
the quotient `T/D` has dimension at most `k+1`. The images of all k small
pieces and any one q_i are independent. Otherwise collective independence
would give a nonzero codeword supported on at most

```
|S| + |supp(q_i)| <= 30+20 = 50 < 53.
```

Consequently `dim(T/D)=k+1` and `dim D=5`. Modulo the small images, all q_i
have nonzero image in one dimension. Rescale them to agree there, without
changing their supports or independence. For suitable small-piece combinations
s_i, put

```
c_0=0,   c_i=q_i-q_0-s_i in D, i=1,...,5.
```

These five codewords are independent by their unit coefficients on the
original independent q_1,...,q_5. Injectivity gives five independent direction
vectors h_i with `c_i=c_{h_i}`, and set h_0=0. Every nonzero edge has support
at most `30+20+20=70`. Thus each edge lies in the complete root/D7 alphabet.
Outside S the six endpoint values are the six vertex evaluations plus one
common coordinate shift.

For six values v_i define `k(v)=6-max_z #{i:v_i=z}`. Any common shift leaves
at least k(v) nonzero values, and choosing the largest equality class to
become zero attains this bound. Therefore the six endpoints must have at
least the sum of these costs outside S support incidences. Their entire
support sum, including S, is at most `6*20=120`.

## Mixed branch, at least one D7 edge

Translate a D7 edge to `0,a` using the puncture-preserving symmetry and one
common nonzero K-scaling. Every other vertex x lies on a rational allowed
line u, and `a-x` lies on a different allowed line v. Affine independence
excludes collinearity. Thus `a=s*u+t*v` with s,t nonzero. Solving one
nonsingular rational two-by-two minor determines s,t rationally even over K.
Checking all eight coordinates on all `binomial(248,2)=30,628` pairs gives
exactly 58 candidates. All are half-integral; the replay doubles vertices.

Join two candidates when their difference is in the allowed alphabet. The
inherited graph has 595 edges. A six-vertex mixed simplex gives four mutually
adjacent candidates whose rows together with a have rank five. Complete
four-clique enumeration gives

| Rank including a | Four-cliques |
|---|---:|
| 3 | 63 |
| 4 | 1,260 |
| 5 | 3,136 |

For every rank-five configuration, evaluate all 112 coordinate costs and
remove its thirty largest costs. This relaxes S to any thirty coordinates
and allows an independently chosen common shift at each retained coordinate.
The surviving support sums are

| Lower bound | Configurations |
|---|---:|
| 121 | 448 |
| 122 | 112 |
| 123 | 560 |
| 124 | 560 |
| 125 | 560 |
| 133 | 784 |
| 134 | 112 |

Every mixed configuration therefore requires at least 121 incidences,
contradicting 120. RESULT.json retains a rank-five witness attaining 121 in
this relaxed cost problem, including its thirty deleted coordinates. It is
not a realization by the independent pieces of the theorem.

The separate checker rebuilds the candidates with Gram-system equations,
checks all 424,270 index quadruples directly, uses fraction-free integer
rank and accumulates costs by multiplicity rather than sorting them. It
agrees on every rank and support histogram.

## All-root branch

If all edges are root directions, the retained A2 fact forces a common
scale after absorbing signs. In norm-two root coordinates the h_i are
scaled roots with every pairwise inner product one. They form an affine
A5 root simplex. The argument holds over K by solving rational coordinate
minors; it requires no positive-definite norm on K itself.

Extend an ordered star by every compatible root and retain every orbit under
reflections perpendicular to its current prefix. This subgroup fixes the
prefix pointwise; using a smaller stabilizer cannot omit an extension orbit.
The extension sizes are `240,56,27,16,10`, leaving one A5 representative.
Its full 120-line coordinate-cost spectrum is

```
0:4, 1:36, 2:60, 3:20; total cost 216.
```

A Weyl normalization may move the puncture, but it remains an eight-line
orthogonal frame. The predecessor's relaxation to arbitrary 38 cuts gives
only 120 and cannot contradict the endpoint allowance. Retain orthogonality
instead. Exhaustively enumerate all 2,025 frames, then delete the thirty
largest remaining live costs. The resulting histogram is

```
122:720, 123:720, 124:585.
```

Thus this branch requires at least 122 incidences, again contradicting 120.
A separate explicit star `0,e0+e1,...,e0+e5` and the orbit of the actual
puncture under the eight simple reflections reproduce the same histogram.
The reflection orbit's 2,025 frames equal the complete primary inventory.
This closes both branches and proves the theorem.

## Scope and next boundary

The new result is the support-thirty shortening contract, not a claim of
complete current profile disposition. No additional TWOSIDE profile is
counted as a new exclusion here. A later application must establish literal
collective independence and the retained code dimension, then check existing
profile exclusions and the complete decoder reduction.

At thirty-one cuts the relaxed root minimum is 120 and mixed minimum 119.
These are failed sufficient bounds, not counterexamples to shortening or
proof that thirty is optimal. The minima 121 and 122 are attained only in
the stated coordinate-deletion/common-shift relaxations. Full C5, the decoder
floor, physical interfaces, supplier admission and kappa remain open or
unchanged. The standard Weyl-chamber theorem and retained alphabet/star
arguments are mathematical dependencies, not formalized theorems here.
