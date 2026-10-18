# Three-endpoint P112 shortening by singleton capacity

Let K have characteristic zero. Let P be the declared 112 nonframe E8 root
lines, with doubled representatives r_t and binary labels ell(t). Write

```text
C = {c_h : c_h(t) = <r_t,h>, h in K^8},
w(q) = rank_F2 {ell(t) : q(t) != 0}.
```

## Statement

Suppose a_1,...,a_k,q_0,q_1,q_2 are collectively independent in K^112.
Let S be the union of the a_j supports. If |S|<=21 and w(q_i)<=6 for each
of the three endpoints, then

```text
dim(span(a_1,...,a_k,q_0,q_1,q_2) intersect C) <= 1.
```

This is a sufficient uniform threshold, not a sharpness claim. The proof's
lower bound is 62 at support 21, against endpoint allowance 60. At support 22
the same bound equals 60 and does not decide the statement.

The named application excludes the original TWOSIDE `(b,t)=(6,5)` profile
`2^3,5,6^3,7^4`. Four unrestricted pieces are deleted, retaining two code
dimensions on four small pieces and three rank-six endpoints. Its common
support cap is 18, so the contradiction has margin 8.

## Inherited geometry

The source-pinned geometry and proof predecessors supply the following
statements. The replay rechecks their finite ingredients, not the general
Weyl-chamber theorem.

* Evaluation on P is injective. Its Gram sum is 112 times the identity.
* Every nonzero codeword has support at least 53. A nonzero codeword with
  support strictly below 70 is proportional to a root codeword.
* A plane through two different root lines contains two lines or the
  three A2 lines. In the latter case the coefficient ratio of the third
  root line is +1 or -1 in normalized root coordinates.
* A binary five-space contains at most 12 live coordinates, and a binary
  six-space at most 20. A two-space contains at most two because all labels
  have leading bit one.

The chamber classification and its characteristic-zero extension are
inherited from the root-simplex predecessors. Six-node chamber faces have
at most 36 root lines. The seven-node counts are 42,28,22,14,16,23,37,63;
only the last face can supply the perpendicular lines required by support
below 70, and its normal is a root. The extension to K uses the rational
one-dimensional kernel of the perpendicular roots. These are written
mathematical dependencies, not formal-kernel results.

The replay checks 960 simple reflections, 7,140 root planes and every one of
the 3,309,747 five-spaces and 788,035 six-spaces. Frozen geometry is retained
byte-identically and its source/receipt bindings are checked.

## Quotient normalization

Let T be the span of the pieces and D=T intersect C. Suppose dim D>=2.
Then dim(T/D)<=k+1. The images of the k small pieces and any one q_i are
independent. A relation would be a nonzero codeword supported on at most
21+20=41<53 coordinates. Collective independence excludes a zero relation.
Consequently dim(T/D)=k+1 and dim D=2.

Modulo the small images, the three q_i have nonzero images in one dimension.
Rescale them to have equal images. This preserves supports and binary
weights. For combinations s_1,s_2 of the small pieces, put

```text
c_0=0, c_1=q_1-q_0-s_1 in D, c_2=q_2-q_0-s_2 in D.
```

The last two codewords are independent by their separate q_1,q_2
coefficients. Every nonzero edge has support at most 21+20+20=61<70.
Injectivity and the root-plane fact therefore normalize their directions
to `0,z alpha_1,z alpha_2`, with z nonzero and normalized roots satisfying
`<alpha_1,alpha_2>=1`, squared norm two. This is an A2 simplex.

Outside S, the endpoint values are its three evaluations plus one common
coordinate shift. The shift can be arbitrary and nonmodal. No minimum-cost
shift is imposed on the actual pieces.

## Singleton classes and their rank-six capacity

Use doubled roots, with squared norm eight. A representative simplex is

```text
0, (2,2,0,0,0,0,0,0), (2,0,2,0,0,0,0,0).
```

On the full 120 root lines, its three evaluations have the following types:

| Type | Lines |
|---|---:|
| All three equal |36|
| Two equal, one singleton |81|
| All three distinct |3|

Each endpoint has 27 singleton lines. These three classes are disjoint.
Each class's binary labels span seven dimensions. Restricted to that
seven-space, the 127 nonzero linear functionals have kernel intersections

```text
0:1, 11:27, 12:36, 15:36, 16:27.
```

Thus any binary space of dimension at most six meets a singleton class
in at most 16 labels. Indeed, its intersection with the class's seven-space
is contained in a hyperplane of that seven-space. This elementary dimension
argument replaces a new all-six-flat census with 127 exact restrictions.
All 511 ambient nonzero functionals are evaluated and equal restrictions are
combined; all 127 restrictions are retained.

The separate checker enumerates every six-label subset of each 27-label
class. It obtains 3,189 distinct generated spans per class, with maximum
intersection 16 and the same 27 attaining intersections. This is complete
for a putative larger intersection: select a basis of its span and extend
it to six distinct labels from that intersection. Their generated span
would contain the entire intersection. There are 296,010 such subsets per
class. Both methods authenticate all attaining intersections through their
canonical digests; the independent method imports no executable predecessor
or primary code.

These facts cover every A2 simplex, not just the representative. The primary
check enumerates the orbit of an ordered pair under eight simple reflections.
It reaches all 13,440 signed ordered root pairs with inner product four.
For each generator it checks the corresponding invertible binary action
on all 240 signed roots. A reflection acts linearly on lattice coordinates
modulo two and fixes the leading label bit. Canonical root-line sign does
not change the label or evaluation equality classes. Therefore transport
preserves binary support ranks and singleton capacities. This proof uses
all checked pairs; transitivity is not assumed from a single example.

## Arbitrary-shift inequality

At a singleton coordinate belonging to endpoint i, let x_j indicate whether
q_j is nonzero. Its two nonsingleton values remain equal after any common
shift. If x_i=0, those two values are nonzero. If x_i=1, the total support
is at least one. In both cases

```text
x_0+x_1+x_2 >= 2-x_i.
```

At a three-distinct coordinate the total support is at least two. This
includes every nonmodal shift. Replacing the actual shift by a modal shift
would wrongly force a particular endpoint to be nonzero.

There are 84 positive-cost coordinates on the full root set. Removing the
eight frame lines and at most s=|S| live coordinates leaves at least 76-s.
For each endpoint, at most 16 of its own singleton labels can belong to its
support because its support has binary rank at most six. Sum the pointwise
inequality on the surviving positive-cost coordinates:

```text
sum_i |supp(q_i)| >= 2*(76-s) - 3*16 = 104-2s.
```

At s<=21 this is at least 62, strictly above the three endpoint capacities
20+20+20=60. The contradiction proves the shortening theorem. Using any
eight removed root lines is a favorable relaxation; orthogonality is not
needed in this new counting step.

## Actual caller and deletion

The original PR3154 program contains the profile

```text
2,2,2,5,6,6,6,7,7,7,7
```

among its 174 historical `(6,5)` survivors. Its excess is 35<36. The unchanged
program confirms feasibility and failure of the earlier basis-kill filter.
An independent transcription reproduces the complete 174-profile cell.

Suppose the eleven independent pieces span T with dim(T intersect C)>=6.
Delete the four weight-seven pieces and let T' be the span of the other
seven. Projection onto the four deleted coefficients has rank at most four
on T intersect C, so dim(T' intersect C)>=2. The deleted weights and supports
are unused in this projection argument and may be arbitrary.

The three weight-two pieces and weight-five piece have common support at
most 2+2+2+12=18. The remaining three endpoints have binary weight at most six.
Their quotient-basis union has at most 38 lines and each edge at most 58.
The shortening inequality gives required support 68 against allowance 60.
The named profile is therefore impossible over K.

The original caller's 112 root lines and labels are also bound directly to
PR3154's copied `bx_data.json`. Matching root lines, the computed invertible
binary map has columns

```text
1,52,278,138,492,418,346,154,350.
```

Its rank is nine and it maps all 112 original labels to the declared labels.
Both implementations check it. This preserves the caller's support weights;
matching root sets alone would not establish that fact.

Deleting only three pieces leaves a weight-seven endpoint. The earlier
four-endpoint rank-six theorem therefore does not directly apply. The
five- and six-endpoint support-twenty theorems likewise do not directly apply
to the two- or one-deletion controls. This is not a complete survey of every
logical implication of earlier exclusions.

## Scope

This proves the stated three-endpoint lemma and one historical profile
exclusion. Full C5, the other PR3154 conjectures, `C(P112)>=64`, physical
COPY/native realization, suppliers, all-size multiplication and kappa remain
unproved or unchanged here. No sharp common-support threshold, independent
human review, formal-kernel proof or supplier admission is claimed.
