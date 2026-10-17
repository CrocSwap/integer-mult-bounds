# An analytic orthogonal-frame bound for an A5 simplex

Let v_0=0,v_1,...,v_5 be an affine A5 simplex in E8, with norm-two roots
v_i having pairwise inner products one. For each root line r, write
`k(r)=6-max_z #{i:<r,v_i>=z}`. Let F be any orthogonal eight-root frame,
and let c_j count its cost-j coordinates.

**Frame theorem.** Every such frame satisfies `2c_0+c_1>=2`. After removing
F and any thirty further root coordinates, the remaining k-cost is at least
122. This bound is sharp when the frame and further cuts are allowed to vary.

The new contribution is a Parseval proof of this frame theorem. Concurrent
[PR3205](https://github.com/CrocSwap/integer-mult-bounds/pull/3205), at
`49d26a7604686aa77cf88d7280b2e313cb4882f6`, already proves the corresponding
support-thirty shortening theorem using a complete 2,025-frame census.
This proof removes that census as a mathematical dependency. The finite
checks below cover the scalar inequalities, Gram/Parseval identities and
one attaining frame; they do not enumerate all frames.

## The already established shortening corollary

Let K be a field of characteristic zero. Let P be the 112 E8 root lines
outside the fixed orthogonal eight-root frame. With rational representatives
r_t, define the code

```
C = {c_h : c_h(t)=<r_t,h>, h in K^8}.
```

**Corollary, already PR3205.** Suppose a_1,...,a_k,q_0,...,q_5 are collectively independent
vectors in K^112. Let S be the union of the supports of the a_j. If
|S|<=30 and every q_i has support at most twenty, then their span T has
`dim(T intersect C)<=4`.

PR3205 strengthens the support-29 contract of Nick Petalas/PR3203. The
mixed-edge bound is also inherited from PR3188. The corollary is restated
to show exactly which finite dependency the new analytic argument replaces.
No new shortening range or historical TWOSIDE profile is claimed here.

## Inherited geometry and precise dependencies

The source-bound replay reruns PR3188's two implementations in
`research/p112-six-vertex-budget`, unchanged. Its proof establishes these
facts on the fixed P112 geometry over every characteristic-zero field.

1. Evaluation h -> c_h is injective. Every nonzero codeword has support
   at least 53. A direction with support at most 70 is a scalar root
   direction or a scalar D7 direction.
2. Root directions have supports 53 or 56. The complete short D7 alphabet
   has 128 directions, each with support seventy. The full short alphabet
   has 248 projective directions.
3. Six affinely independent vertices with every edge in this alphabet
   and at least one D7 edge require at least 121 endpoint support incidences
   after thirty arbitrary common cuts and arbitrary coordinate shifts.
   The D7-anchor normalization checks all 128 anchors, all 58 possible
   further vertices, 4,459 four-cliques and 3,136 rank-five cliques.
4. If every edge is a root direction, the six vertices are one common
   scalar multiple of an affine A5 root simplex. After signs and translation,
   normalized roots v_1,...,v_5 have squared norms two and pairwise inner
   products one, with v_0=0. The full 120-root minimum-nonzero spectrum is
   `cost 0:4, 1:36, 2:60, 3:20`, of total cost 216.

The inherited proof checks root planes, the complete A5 extension orbits,
the E8 simple system and its reflections. Its direction-completeness proof
uses the standard real Weyl-chamber theorem. A direction of support at most
70 has at least 42 rational perpendicular root lines. Their rank must be
seven: rank at most six would allow a generic real normal with the same
perpendicular roots, contradicting the checked 36-line rank-six bound.
The one-dimensional rational normal space gives the field-extension step.
Rational two-coordinate solves in the mixed-edge census likewise remain
valid after extending scalars to K.

These written root-system facts remain explicit dependencies. The concurrent
frame census corroborates the analytic argument below; neither approach
replaces the standard Weyl-chamber theorem with a formal proof.

## A Parseval bound for the eight punctures

First work with the real, normalized A5 simplex in item 4. For an E8 root
r of squared norm two, set x_i=<r,v_i> and

```
k(r) = 6 - max_z #{i : x_i=z},
V(r) = sum_i (x_i-mean(x))^2 = (1/6) sum_{i<j} (x_i-x_j)^2.
```

All x_i are integers. If k=1 there are five unequal pairs, so V>=5/6.
If k>=2, every equality class has at most four members. The partition 4+2
minimizes the number of unequal pairs at eight; when every class has size
at most three there are at least nine. Thus V>=4/3 whenever k>=2.
These lower bounds hold for any six integers.

Let F be any eight mutually orthogonal E8 root lines, represented by
norm-two roots. Their outer products sum to 2I. The simplex Gram matrix gives

```
sum_i ||v_i||^2 = 10,       ||sum_i v_i||^2 = 30,
sum_{r in F} V(r) = 2*(10-30/6) = 10.
```

Write c_j for the number of frame roots of cost j. The variance lower bounds
imply

```
10 >= (5/6)c_1 + (4/3)(8-c_0-c_1),
8c_0+3c_1 >= 4,             2c_0+c_1 >= 2.
```

For the last implication, c_0>=1 suffices; otherwise the first inequality
forces the integer c_1 to be at least two.

Remove F from the full spectrum. There are 20-c_3 cost-three coordinates
left. Thirty further cuts remove cost at most
`2*30+(20-c_3)=80-c_3`. Therefore the remaining endpoint cost is at least

```
216-(c_1+2c_2+3c_3)-(80-c_3)
    =120+2c_0+c_1 >=122.
```

A Weyl normalization of the simplex may move the original puncture frame.
It remains an orthogonal frame, so the estimate applies. A common nonzero
scalar in K preserves equality classes of the rational evaluations. Hence
the real variance argument bounds the same endpoint supports over K.
No transport of binary labels or actual small-piece supports is assumed.

The bound 122 is sharp in the arbitrary-cut and common-shift relaxation.
The retained attaining frame has costs `0,2,2,2,3,3,3,3`. Remove the sixteen
remaining cost-three coordinates and fourteen cost-two coordinates.
This attains 122. It is not a construction of the original independent pieces.
The sharpness statement here permits the displayed choice of frame. The
stronger fixed-puncture sharpness is already covered by PR3205's frame-orbit
check and is not needed by this analytic lower-bound proof.

## Quotient normalization and the shortening conclusion

Suppose D=T intersect C has dimension at least five, and put Q=T/D.
Then `dim Q<=k+1`. The quotient images of all k small pieces and any
one q_i are independent. A dependence would give a nonzero codeword
supported on S union supp(q_i), of size at most `30+20=50<53`, contrary
to the minimum support. This uses collective independence of the original
pieces, not merely independence of the six endpoints.

It follows that `dim Q=k+1` and `dim D=5`. Modulo the span of the small
images, every endpoint has nonzero image in the remaining one-dimensional
quotient. Rescale the endpoints to make these images equal. Choose s_i in
span(a_1,...,a_k) so that

```
c_0=0,       c_i=q_i-q_0-s_i in D, i=1,...,5.
```

The five codewords c_i are independent because their coefficients on the
original independent endpoints q_1,...,q_5 form the identity. Injective
evaluation gives five independent directions h_i, with h_0=0. Every edge
has support at most `30+20+20=70`, so the complete root/D7 alphabet applies.
The strict root-only cutoff below seventy from PR3203 is insufficient here.

Outside S, the endpoint evaluations equal the six vertex evaluations plus
one common shift at each coordinate. Thus their total support is at least
the sum of the minimum-nonzero coordinate costs outside S.

If there is a D7 edge, inherited item 3 gives support at least 121. If every
edge is a root, the new frame argument gives at least 122. Both exceed the
six endpoints' total allowance `6*20=120`. This is an analytic replacement
for the frame-census step of the known corollary.

## Added scope and stopping boundary

The earlier relaxation removes eight frame coordinates as arbitrary cuts.
Together with thirty common cuts this leaves only cost 120 and gives no
strict contradiction. Orthogonality supplies the missing strict margin.
The known corollary is a general support contract; it needs no binary weight bounds
on the small pieces.

The tempting historical profile `2,4,6^7,7` is already covered by the
[ten-deletion span-four theorem](../p112-ten-deletion-span/PROOF.md).
Choose quotient basis `2,4,6,6`, with support
cap fifty. The remaining five rank-six directions and one unrestricted
direction span at most `4+1=5<6`. It is an overlap control, not a new exclusion.
The other recently published profile exclusions retain their original credit.

At thirty-one common cuts the same root relaxation attains cost 120. The
analytic proof therefore stops at thirty. This is a failed strict inequality,
not a counterexample to a support-31 shortening theorem. We have not matched
this broader contract to a newly open original TWOSIDE profile, settled C5,
proved the complete decoder floor or supplied a better multiplication exponent.
