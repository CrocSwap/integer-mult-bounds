# Three eleven-piece P112 exclusions by quotient selection

Let K have characteristic zero. For the pinned 112 live E8 root lines, put

```
C = {c_h : c_h(t) = <r_t,h>, h in K^8},
w(q) = rank_F2 {ell(t) : q(t) != 0}.
```

Here ell(t) is the pinned nine-bit label. Representatives r_t can be scaled
by the common factor used in the replay without changing supports.

**Theorem.** Eleven independent pieces spanning T with dim(T intersect C)>=5
cannot have weights bounded by any of these multisets:

```
3,3,5,5,5,5,5,5,5,5,5
3,4,4,5,5,5,5,5,5,5,5
4,4,4,4,5,5,5,5,5,5,5.
```

The proof establishes the more general support statement: four pieces with
total support size at most 32 and seven further pieces each supported on
at most twelve coordinates cannot satisfy these independence and
code-intersection hypotheses. No disjointness of supports is assumed.

## Geometric facts and their verification

The following are the exact P112 facts used here, inherited from
Nick Petalas's PR3164/PR3169/PR3171 with their source pins retained:

1. Weight bounds three, four and five give support bounds four, eight and
   twelve, respectively.
2. Every nonzero codeword in C has support at least 53. A nonzero codeword
   supported on fewer than 70 coordinates has a scalar E8 root direction.
3. The evaluation map h -> c_h is injective.
4. Three root lines in a rational root plane form A2: in two normalized
   generating roots the third has coefficient ratio +1 or -1.

The labels have a leading-one bit. A binary d-flat therefore contains at
most 2^(d-1) live labels, giving the first two support bounds in fact 1.
For five-flats, `geometry.py` enumerates all 3,309,747 annihilator spaces
in unique reverse row-echelon form. The largest intersection has size twelve.
Supports of smaller binary rank extend to such a flat.

Fact 2 uses the standard Weyl-chamber theorem for real E8. Move a real
direction to a closed chamber. Its perpendicular root system is generated
by the vanishing simple roots. The replay checks that every six-node
parabolic has at most 36 root lines, and that the eight seven-node
parabolics have counts `42,28,22,14,16,23,37,63`. A support below 70 has
at least 43 perpendicular live lines. Only the last ray can qualify, and
its normal is a root. Root directions have live support 53 or 56, also
excluding every nonzero support below 53. The replay checks simple-system
positivity, all 960 simple reflections, these parabolics and all root supports.

For K-valued directions, their perpendicular rational roots span dimension
at most seven. If the span had dimension at most six, a generic real normal
to it would have exactly the roots in that span as perpendicular roots.
The six-node parabolic bound would permit at most 36, contradicting 43.
Thus at support below 70 the perpendicular span has dimension seven. Its
rational one-dimensional normal supplies the same root classification over K.
The live-root Gram sum is 112 times the identity in the doubled coordinates,
proving fact 3. All 7,140 root-line pairs and all possible third roots are
checked for fact 4. A rational vector in the K-span of two independent
rational roots has rational coefficients, by an invertible rational minor,
so the plane classification also applies over K.

The Weyl-chamber theorem is an explicit mathematical dependency. It is not
proved by the executable checks or a proof kernel in this package.

## A small common support cannot contain a two-dimensional code kernel

No two-dimensional subspace of C can be supported on fewer than 70
coordinates. Otherwise every nonzero vector in it would be proportional
to one of the 120 root directions, by fact 2 and injectivity. For independent
u,v in that subspace, the 121 vectors u+jv, j=0,...,120, lie on distinct
projective lines. Characteristic zero makes the 121 scalars distinct.
There are only 120 root lines, a contradiction.

This auxiliary statement also follows from the stronger inherited generalized
distance bound d_2>=78. It is not a new distance bound. Here it gives the
quotient-selection implication through a self-contained root-rigidity argument.
It uses a common support for the entire kernel. Separate small supports for
selected directions would not prove it.

## Contract four small pieces and select a singleton class

Let D=T intersect C and Q=T/D. The eleven pieces are a basis of T, so
dim Q<=6. Let B be the four small pieces, and let S_B be their support union.
Its size is at most 32. Their quotient images are independent: a dependence
would give a nonzero codeword supported on at most 32<53 coordinates.

The seven remaining piece images in Q/span(B) are all nonzero. A zero
image would give a nonzero codeword supported on S_B plus one twelve-point
support, of size at most 44<53. Independence of the original pieces makes
each such proposed codeword nonzero.

No projective proportionality class of the seven images has size three.
If three images were in one class, B together with their three original
pieces would span a seven-dimensional space E whose image in Q had
dimension five. Thus E intersect D would have dimension two, and its entire
support would lie in S_B plus those three twelve-point supports, of size
at most 32+36=68<70. The preceding kernel lemma forbids this.

Consequently dim(Q/span(B))=2. If it were at most one, all seven nonzero
images would belong to one class, violating the class-size bound. Thus
dim Q=6 and dim D=5. Seven points partitioned into classes of size at most
two have a singleton. Adjoin its piece to B, obtaining five pieces A.
Their images are independent and their span contains none of the other
six piece images. Their support union S has size s<=32+12=44.

The executable quotient fixture and all 232 partitions of seven vertices
into singletons and pairs illustrate this step. The argument above proves
it for every permitted K-valued quotient, rather than only the fixture.

## Six remaining pieces yield the retained root A5 contradiction

Write the other pieces q_0,...,q_5. In the one-dimensional quotient
Q/span(A), all have nonzero images. Rescale each to give them equal images;
supports do not change. For i=1,...,5 there is a unique combination a_i
of the selected five pieces such that

```
c_i = q_i - q_0 - a_i belongs to D.
```

Set c_0=0. The five c_i are independent by their distinct unit coefficients
on q_1,...,q_5 in the original eleven-piece basis. Every edge c_i-c_j is
nonzero and supported on S union supp(q_i) union supp(q_j), of size at
most 44+12+12=68<70. Thus the associated directions h_i are independent
and every difference among 0,h_1,...,h_5 is a scalar root direction.

Normalize roots to norm squared two. Write h_i=b_i alpha_i. Fact 4 applied
to h_i-h_j implies b_i/b_j is +1 or -1. Absorb signs into alpha_i to obtain
one common scalar b. Then alpha_i-alpha_j is a root and
<alpha_i,alpha_j>=1. This is the retained affine root A5 simplex argument.

At a live root coordinate, its six integer endpoint levels have pairwise
differences in {-2,-1,0,1,2}. A difference of magnitude two forces that
coordinate to be the corresponding edge root, by equality in Cauchy-Schwarz.
The level multiplicities are then 1,1,4, with nine unequal pairs. Otherwise
there are at most two consecutive levels, with at most 3*3=9 unequal pairs.
The common nonzero K-scalar changes no zero. Each coordinate therefore lies
in at most nine of the fifteen edge supports.

Outside S, the edge values are q_i(t)-q_j(t). If k of the six endpoints are
nonzero, at most k(6-k)+k(k-1)/2<=5k pairs differ. Writing
U=sum_i |supp(q_i)|<=72 and counting all fifteen edge supports gives

```
795 = 15*53 <= 9s + 5U <= 9*44 + 5*72 = 756.
```

This contradiction has margin 39. The coordinate-budget strengthening of
PR3169 is unnecessary; the contribution is the new quotient selection.

## Application binding and prior coverage

Each profile's four smallest support caps sum to 32; the other seven caps
are twelve. Each is an actual survivor of the pinned TWOSIDE `(5,6)` BK/BK7
filters in DreamingOfClouds's PR3154. `beta.py` reconstructs all 77 original
survivors. Each application has deficit one and prefix support caps
`68,80,92,104,116`. A separately implemented filter checks the entire small
multiset domain, including the two-six-flat packing test.

All 462 possible six-piece subsets in each profile have support-cap sum at
least 56. Therefore the old sufficient test `sum caps < 53` certifies no
six-piece quotient basis here. This is a statement about that support-only
certificate, not about the actual unknown support unions. The new selection
argument replaces the missing certificate.

PR3169's ten-piece cases do not directly cover eleven pieces. PR3171's
`4,5^9` theorem needs code-intersection dimension at least five; deleting a
piece here only guarantees four. The initially considered larger-b profiles
`4,5^(b+4)` do follow from PR3171 by deleting pieces, and are deliberately
not counted as new results. The active larger-simplex claim on different
`(6,4)/(7,4)/(8,4)` profiles is separate.

The original decoder reduction and its generalized-distance filters are
inherited, not re-proved here. The exclusions themselves use only the explicit
piece hypotheses and the stated geometry. Full C5, `C(P112)>=64`, complete
suppliers and a new kappa remain open. No scientific admission or selected
frontier change follows from this package alone.
