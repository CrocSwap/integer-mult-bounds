# Rank-six endpoints rule out the A3 equality case

Let K have characteristic zero. On the pinned 112 nonframe E8 root lines,
with doubled representatives r_t, write

```
C = {c_h : c_h(t) = <r_t,h>, h in K^8},
w(q) = rank_F2 {ell(t) : q(t) != 0}.
```

The labels are simple-root coordinates modulo two with a leading one.
The new result is the following shortening theorem.

Suppose `a_1,...,a_k,q_0,...,q_3` are collectively independent vectors in
`K^112`. If the union S of the a_j supports has size at most 22 and each
endpoint satisfies `w(q_i)<=6`, their span T obeys

```
dim(T intersect C) <= 2.
```

Unlike a support-only bound, this statement uses the binary rank of each
endpoint. It excludes the actual historical TWOSIDE `(b,t)=(6,3)` profile
`2,6^5,7^3`. No complete C5 or decoder-floor theorem is claimed.

## Retained geometry

The source-bound root and label reconstruction, unchanged from the retained
predecessor, checks these finite premises:

* `C` has dimension eight. Its minimum support is 53.
* Every nonzero codeword supported on fewer than 70 coordinates is a scalar
  multiple of a root codeword.
* A plane through distinct root lines has either two lines or the three
  lines of A2. A third line has coefficient ratio `+1` or `-1` in normalized
  root coordinates.
* A support of binary rank at most 6 contains at most 20 live lines. Rank
  at most 2 gives at most 2 lines because all labels have leading one.

The first two facts use the standard Weyl-chamber theorem and the finite
parabolic counts, not a formal proof kernel. The 28 six-node parabolics
have at most 36 root lines. The eight seven-node faces have line counts
`42,28,22,14,16,23,37,63`. Only the E7 face can have the at least 43
perpendicular live lines required by support below 70; its normal is a root.
Root directions have live supports 53 or 56. The replay checks all 960 simple
reflections, all 7,140 root planes and all 788,035 six-flat annihilators.

These statements hold over K. Rational roots perpendicular to a K-valued
direction have rank at most seven. Rank at most six would admit a generic
real normal contradicting the rank-six root count. Their rational kernel
is therefore one-dimensional whenever the low-support classification is
needed. The direction is proportional over K to a rational normal, to
which the real classification applies. A rational two-by-two minor gives
the same field extension for the A2 plane argument.

## Normalize the four quotient images

Assume `D=T intersect C` has dimension at least three. Then `T/D` has
dimension at most `k+1`. The images of the k small pieces and any q_i are
independent. A nonzero relation would be a nonzero codeword on at most
`22+20=42<53` coordinates; collective independence excludes a zero relation.
Hence the quotient dimension is exactly `k+1` and `dim D=3`.

Modulo the small images, rescale the four nonzero endpoint images to agree
in the one-dimensional quotient. Supports and binary weights do not change.
For suitable small-piece combinations s_i, put

```
c_0=0,    c_i=q_i-q_0-s_i in D, i=1,2,3.
```

The three c_i are independent, by their separate coefficients on the q_i.
Every edge is nonzero and has support at most `22+20+20=62<70`.
Injectivity of evaluation and the root/A2 facts therefore give

```
c_i = c_(z alpha_i),   <alpha_i,alpha_j>=1 for i!=j,
```

for one nonzero field scalar z and norm-two rational roots alpha_i.
Indeed the third root line in each pair plane forces the scalar ratio
to be `+1` or `-1`; absorb signs into the alpha_i. The four vertices
`0,alpha_1,alpha_2,alpha_3` are an affine A3 simplex.

## Complete A3 and puncture coverage

The replay builds every star extension up to the root-reflection action.
Reflections in roots perpendicular to a prefix fix that prefix pointwise.
Their extension sets are single orbits of sizes `240,56,27`, respectively.
Induction therefore moves every ordered A3 star to the retained one. This
is a complete finite orbit argument, not a sample of stars.

Moving the star also moves the deleted orthogonal eight-root frame. All
2025 frames are enumerated as increasing orthogonal eight-cliques, without
recursion. A second level-by-level set-intersection enumeration reproduces
that inventory. Root reflections act invertibly on the root lattice, so
modulo two they preserve binary rank. The leading-one coordinate is fixed.
The executable also checks the explicit nine-bit linear involutions on
all 120 root labels for all eight simple reflections, totaling 960 bindings.
Thus it is legitimate to fix the star and vary the puncture, including
when checking binary ranks.

For a full-root coordinate r, evaluate the four vertices and define

```
v(r) = (0,<r,alpha_1>,<r,alpha_2>,<r,alpha_3>),
k(r) = 4 - max_a #{i : v_i(r)=a}.
```

This is the minimum number of nonzero endpoint values after any common
shift. Nonzero common K-scaling changes no equality. The complete spectrum
is `0:20,1:64,2:36`, with total 136. The eight-root puncture has these exact
cost sums:

| Puncture cost | Number of frames |
|---|---:|
| 8 | 1005 |
| 10 | 960 |
| 12 | 60 |

In each of the sixty maximum-cost frames, two deleted coordinates have
cost zero and six have cost two. No cost-one coordinate is deleted.

Outside S the endpoint values are v(r), scaled by z, plus a common shift.
Consequently their total support is at least

```
136 - puncture_cost - sum_(r in S) k(r) >= 136-12-2*22 = 80.
```

But four binary-rank-six endpoints have total support at most `4*20=80`.
All inequalities must be equalities. In particular, the puncture is one
of the sixty extremal frames, S has exactly 22 cost-two coordinates, and
every remaining coordinate uses a minimum-support common shift. All 64
cost-one live coordinates remain outside S.

## The binary equality obstruction

At a cost-one coordinate, three vertex values agree and the fourth is
different. The unique minimizing shift makes the common value zero, so
the exceptional endpoint must be nonzero. For each extremal frame and
each of the four endpoints, let M_i be its mandatory singleton coordinates.
The following exact facts hold in all `60*4=240` cases:

```
|M_i| = 16,
dim_F2 span ell(M_i) = 6,
{live t : ell(t) in span ell(M_i)} = M_i.
```

The receipt lists all sixty extremal frames and their mandatory/live-closure
bit masks. Bit i refers to full-root index i in the canonical 120-line order;
each mask is thirty hexadecimal digits. Explicit XOR closure checks all
240 cases. Independent Gaussian elimination and an independent root/label
reconstruction repeat them in the test suite. There is no union over different cuts in this step.

Since q_i is nonzero on M_i and has binary rank at most six, the binary
span of its entire support must equal `span ell(M_i)`. Its support is thus
contained in M_i and has at most 16 coordinates. Four such endpoints have
support sum at most 64, contradicting the required 80. This proves the
shortening theorem. The rank-six condition cannot simply be discarded:
the support-only bound is exactly 80 and supplies no contradiction.

## One historical application

Suppose nine independent pieces span T with `dim(T intersect C)>=6` and
weights bounded by `2,6^5,7^3`. Delete the three weight-seven pieces and
let T' be the span of the other six. Projection onto the three deleted
coefficients has rank at most three on `T intersect C`, so

```
dim(T' intersect C) >= 6-3 = 3.
```

Choose the rank-two piece and one rank-six piece as the small pieces.
Their support union has size at most `2+20=22`. The remaining four pieces
have binary rank at most six. The shortening theorem contradicts the three
surviving code dimensions. The deleted pieces may in fact be unrestricted.

The target belongs to the seventeen original `(6,3)` TWOSIDE survivors;
its excess is 35, strictly below 36. The retained original program reproduces
the source table, and a separate filter transcription lists this profile.
This is not a new claim about the completeness of those original filters.

The earlier weight-certified two-six-flat plus two-cut route can choose
basis `2,6,6`, but leaves three rank-six and three rank-seven endpoints.
The retained rank-six direction bound gives only `3+3=6`, not the strict
bound below six needed there. PR3211's five-endpoint theorem requires four
surviving code dimensions and cannot treat the extra remaining rank-seven
endpoint as rank six. The new three-piece deletion argument uses a
different endpoint contract. No complete implication audit of all earlier
work is asserted.

## Limits

The original decoder reduction, standard Weyl-chamber theorem and retained
finite geometric premises remain dependencies. This is a characteristic-zero
piece theorem and one historical profile exclusion. It does not settle full
C5, `C(P112)>=64`, any other original conjecture, a physical supplier or a
new multiplication exponent. Evidence is author-checked, not independent
human or proof-kernel review. The selected frontier is unchanged.
