# Three rank-five endpoints after one common cut

Fix the 112 live E8 root lines and nine-bit labels reconstructed by the pinned
`research/p112-root-simplex-exclusion/geometry.py`. Roots use doubled Euclidean
coordinates. If `r_t` represents a line, its label is the leading bit one
together with its eight simple-root coordinates modulo two. Signs do not
change labels or supports. Work over any characteristic-zero field `K`.

Let `C = {(r_t dot h)_t : h in K^8}`. For a set `S` of live coordinates, let
`pi_S` delete those coordinates. For a piece `q`, write `w(q)` for the binary
rank of the labels in its support.

**Theorem.** If `|S| <= 44` and `w(q_i) <= 5` for three pieces, then

```
dim_K( pi_S(C) intersect span_K(pi_S(q_1), pi_S(q_2), pi_S(q_3)) ) <= 1.
```

The pieces need not be independent. They may have arbitrary characteristic-zero
coefficients. The same conclusion holds if each piece has rank at most five
only after deletion of `S`. The theorem uses one common set `S`.

This is a sufficient threshold. No counterexample at 45, sharp global threshold,
TWOSIDE profile exclusion, complete decoder floor, physical supplier or improved
multiplication exponent is claimed.

## 1. The finite geometric premises

The verifier rebuilds the source geometry and checks the following facts.

1. A set of live labels of binary rank at most five has at most 12 elements.
   All 3,309,747 five-dimensional subspaces of `F2^9` are represented by their
   unique four-dimensional reverse-echelon annihilators. Lower-dimensional
   sets extend to a five-space, so this also covers them.
2. Among the 28 parabolic subsystems on six simple nodes, exactly one has
   36 root lines. Every other has at most 30. The unique 36-line subsystem is
   E6. Its orthogonal complement contains exactly three root lines forming
   an A2 plane. All parabolics on fewer nodes embed in one on six nodes.
3. There are exactly 1,120 A2 root planes. Applying the eight simple
   reflections reaches all of them from one plane. On the fixed P112, their
   nonzero evaluation unions have sizes 78 and 80, with multiplicities
   896 and 224. In particular every such union has size at least 78.
4. Fix one A2 plane and any rational basis of it. Partition all 120 E8 root
   lines by the projective value of their two evaluations. The nonzero
   fibers have sizes `27,27,27,1,1,1`. In each 27-line fiber, every subset
   of binary label rank at most five has at most ten elements. Each fiber
   spans seven binary dimensions. The verifier checks all 2,667
   codimension-two subspaces of that span. A literal ten-line rank-five
   subset in every fiber attains the bound.

The last capacity bound holds for every A2 plane. A simple reflection is an
invertible integral linear map on the E8 root lattice. Reducing modulo two,
and leaving the leading label bit fixed, gives an invertible linear map on
the nine-bit labels. It preserves binary ranks. The checked transitive
reflection orbit transfers the bound to every A2 plane. A change of basis in
the plane only renames the projective fibers. Removing the eight frame lines
cannot increase any fiber's capacity. A singleton fiber also has capacity
at most ten.

The standard Weyl-chamber theorem for a finite real root system is a written
dependency. The executable checks the finite parabolic inventories and
reflection actions. It does not constitute a proof-kernel formalization of
that theorem or of the argument below.

## 2. Any putative two-dimensional intersection is an A2 code

Suppose two independent restricted codewords lie in the displayed span.
Choose lifts `c_h,c_k` in `C`. Their directions `h,k` are independent over
`K`, since their restrictions are independent. Let `U` be the union of
their full supports. Both codewords vanish outside

```
S union supp(pi_S(q_1)) union supp(pi_S(q_2)) union supp(pi_S(q_3)).
```

Premise 1 gives `|U| <= 44+3*12 = 80`. Thus at least 32 live roots are
orthogonal to both directions. Include also any omitted frame roots
orthogonal to both, and let `Z` be this full set of perpendicular root lines.
Its rational span has rank at most six. Indeed its matrix has rational
entries and has the two independent vectors `h,k` in its kernel over `K`.
Matrix rank does not change upon extending a characteristic-zero field.

Choose a generic real vector perpendicular to the rational span of `Z`.
It has exactly the root lines of `Z` perpendicular to it: any additional
such root would already lie in that span and hence be perpendicular to
`h,k`. Finitely many proper hyperplanes exclude the other coincidences.
The Weyl-chamber theorem makes this root subsystem conjugate to a parabolic
subsystem. It has rank at most six and at least 32 lines. Premise 2 therefore
forces rank six and type E6. Its two-dimensional normal space is an A2
plane by premises 2 and 3.

Consequently `span_K(h,k)` is the scalar extension of an A2 plane. Replace
`h,k` by a rational root basis of that plane. This leaves the code subspace
and its union `U` unchanged. Premise 3 now gives `|U| >= 78`.

## 3. Singleton coordinates improve the support bound

Write the two restricted root codewords as combinations of the three
restricted pieces. This gives a fixed `2 by 3` coefficient matrix `A`.
For each `t` outside `S`,

```
(r_t dot h, r_t dot k)^T = A * (q_1(t), q_2(t), q_3(t))^T.
```

Put `N=|U minus S|`, so `N >= 78-44 = 34`. Count only sites in `U minus S`.
A singleton site has exactly one nonzero piece. If that piece is `q_i`,
the nonzero evaluation pair is proportional to column `i` of `A`.
Thus all singleton sites assigned to one piece lie in one projective A2
fiber. They form a subset of that piece's support, of binary rank at most
five. Premise 4 bounds their number by ten. A zero column admits no such
singleton site. Summing over three pieces gives at most `L=30` singleton
sites.

Every other site in `U minus S` uses at least two piece incidences. Let `M`
be the total number of piece incidences at these sites. Premise 1 gives
`M <= 36`. Hence

```
2*N <= M+L <= 36+30 = 66,
```

contradicting `N >= 34`. The putative two-dimensional intersection cannot
exist.

The argument allows extra piece incidences outside `U`: ignoring those
only weakens the upper bound on `M`. It allows zero pieces, dependent pieces,
zero coefficient columns, and arbitrary cancellations at nonsingleton sites.

## 4. Boundary and contribution

Using only the union capacity `3*12=36` and the A2 minimum union 78 excludes
common supports through 41. The projective-fiber incidence bound extends
this sufficient threshold through 44. At 45 the inequalities give
`N >= 33` and `2*N <= 66`, which are compatible. The verifier checks this
losing counting control. It is not an actual piece construction.

The sharp finite statement is the ten-line rank-five capacity of a full E8
A2 projective fiber. The global shortening threshold is not proved sharp.
An application to a remaining decoder profile must separately establish its
three endpoint ranks, its one common support and the required intersection
dimension. This package makes no such profile claim.

The root/label model, five-flat capacity method and chamber machinery follow
Nick Petalas's PR3164/PR3174 root-simplex lineage. DreamingOfClouds's PR3154
motivates the current decoder/shortening question. The E8/P112 lineage,
including joaqcoo's model, retains its attribution. No predecessor is modified.
