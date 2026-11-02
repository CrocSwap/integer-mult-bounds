# The minimum-idle mixed root and its limits

The complete conditional result remains kappa **0.00328551**. This note
does not add a new kappa increment. It proves that the ceiling 0.00328554
applies to a larger class than the fixed root in the source package.

Work over a commutative field of characteristic zero, unless stated
otherwise. All ordinary coefficients commute with the central involution
S and with the independent stage variables. There are six arbitrary main
fields, seven rank-one square-zero queries, four full child suppliers,
and at most two extra whole idle jobs at the root. Each child can be any
positive-size binary tree from PR6348, with the PR6353 native source.
There is no initialized extra main field. A full stage acts once on each
field in its projector image. Every field beyond its native two-field
query plane needs one charged whole idle of that same stage product.

**Theorem.** Every such root with an independent Gaussian endpoint has,
up to stage and output names, the output supports

```text
ABCD, AB, CD, empty, B, C.
```

It has two rank-two endpoint stages and two rank-three interior stages.
Thus its complete price is the price of the existing mixed root. No
positive binary child sizes or binary tree shapes reach 0.00328554 under
the fixed PR6353 source and the admitted saving range through 0.0034.

The claim 0.00328551 is less than 0.00000003 below this ceiling. More
idles, more queries, different field counts, different query or source
interfaces, and noncommuting ordinary coefficients are outside this
theorem. In particular, this is not a global optimum for kappa.

## 1. Why the normal form and projector tests apply

Move all invertible constant scalar maps to the final boundary. At stage
variables equal to one, remove their total product there. A full site has
the form

```text
(I+(D_i-1)P_i) (I+(S-1)R_i),
P_i^2=P_i, R_i=u_i v_i, v_i u_i=0, P_i R_i=R_i P_i=R_i.
```

A thin site has only the second factor. At S=-1 put T_i=I-2R_i and
B_i=T_i ... T_0. The complete endpoint at stage variables equal to one
requires T_6 ... T_0=-I_6.

The shortest-query classification in the pinned
`five-call-projector-rigidity/PROOF.md`, section 1, permits the basis

```text
u_i=e_i for i=0,...,5,
u_6=(-1,1,-1,1,-1,1),
(v_i)_j=sign(i-j).
```

It is a complete normal form, not a sampled query tuple. The proof uses
the chronological identity

```text
T_6 ... T_0 = I-2U(I+2L)^(-1)V,
G=VU, and L is the strict lower part of G.
```

The matrix I+2L-G has rank one and diagonal entries one. Rescaling the
query factors gives G_ij=sign(i-j). The same argument applies to n+1
queries on any even n fields.

The independent Gaussian endpoint forces the full P_i to commute.
Indeed, its first derivative in each independent D_i at S=1 and all
D_j=1 identifies P_i with a diagonal zero-one mask in one common basis.
At S=-1 the corresponding derivative is -B_i^(-1)P_i B_i. Equality with
the Gaussian endpoint therefore gives [P_i,B_i]=0. These are necessary
conditions, not extra restrictions introduced for the search. They are
also sufficient for the formal endpoint once the masks and query tuple
are fixed.

## 2. At most two rank-two full stages, in every even dimension n>=4

Any ordered four-site principal Gram matrix has determinant one. Hence
any three query columns are independent, and so are their three rows.
The principal three-site Gram matrix is singular, with rank two.

Commuting idempotents have a common diagonal basis over the original
field: repeatedly split the space into each image and kernel. Suppose
three full projectors have rank two. Their supports are three two-element
sets. Any two supports intersect because each off-diagonal Gram entry
is nonzero.

If their union has at most three coordinates, independence of the three
columns and rows makes their Gram matrix invertible. This contradicts
the preceding rank-two Gram calculation. Otherwise the supports are
three distinct arms of a star, with one common coordinate. Every cross
pairing then passes through that coordinate. The two directed products
around the triple are equal. But in the ordered Gram normal form they are

```text
G_ij G_jk G_ki = 1,
G_ik G_kj G_ji = -1,       i<j<k.
```

This is a contradiction. Thus there are at most two rank-two full sites.
This argument works in every characteristic other than two. The replay
checks the two Gram minors and every set pattern on four coordinates;
three pairwise-intersecting two-sets never need more than four coordinates.

A related filter is useful. Every even principal Gram matrix is invertible:
its ordered entries have the same sign form as the leading matrix in
the normal-form proof. For an odd set of k full sites with k<=n,
the union of their coordinate supports needs at least k+1 coordinates.
The k query columns and rows are independent, while their odd skew Gram
matrix is singular. A union of exactly k coordinates is impossible.
This does not itself construct any of the surviving support patterns.

## 3. Exact image and row-space bounds on six fields

Let P be an idempotent of rank r. Suppose P contains the column space A,
acts as the identity on the row space C, and commutes with specified
operators. Close A and C under those operators. If their dimensions are
a and c, and the pairing C A has rank g, then

```text
r >= a+c-g.
```

On im(P), the row map C has rank c and kernel dimension r-c. The
intersection of im(A) with that kernel has dimension a-g. This proves
the inequality. It explains why column containment alone is insufficient.

Start from A=u_i and C=v_i and close under B_i. Exact rational elimination
gives the following necessary projector ranks:

| Site | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Rank lower bound | 2 | 2 | 4 | 2 | 4 | 2 | 2 |

At sites 1,3,5 the closed column and row dimensions and pairing rank are
all two. A rank-two projector there is therefore unique:
P=A(CA)^(-1)C. Closing each other site's spaces under this P as well as
its own B_j gives:

| Fixed rank-two site | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2 | 2 | 4 | 4 | 6 | 4 | 4 |
| 3 | 4 | 4 | 4 | 2 | 4 | 4 | 4 |
| 5 | 4 | 4 | 6 | 4 | 4 | 2 | 2 |

The replay reconstructs all these spaces from the canonical queries. The
tables hold for every projector, not only for bounded rational entries.

Four full stages and at most two extra idles must have ranks 2,2,3,3.
Section 2 excludes three or more rank-two stages. The table excludes a
rank-two interior site in this configuration. Thus the rank-two sites
are 0 and 6. If these projectors are equal, they are the unique rank-two
projector that contains u_0,u_6 and v_0,v_6. The same closure test gives
interior lower bounds 4,4,6,4,4. Therefore the endpoints must be distinct.
Their common image has dimension one, since disjoint images would make
G_06 zero.

## 4. Retain the free parameter in the endpoint basis

Let a span the common endpoint image and normalize it by a=P_6 e_0.
Then sum(a)=1. Put r=-v_0 a, which is nonzero because v_0 u_6=-1.
There is a vector z in

```text
K={x: x_0=0 and sum(x)=0}
```

such that

```text
a=e_0+r u_6-z,
b=e_0-a=-r u_6+z,
c=e_0-z,
e_0=a+b,       u_6=(a-c)/r.
```

In these coordinates the endpoint masks are {a,b} and {a,c}. Their
common kernel H has dimension three and lies in K. Moreover K is the
direct sum of the line through z and H. This gives the complete endpoint
chart with r free and nonzero. The earlier bounded basis search used
r=-1. Fixing that value would not prove the present classification.

An interior rank-three stage can occur only at 1,3,5 by section 3.
Its image must intersect both endpoint supports. Its possible masks on
the first three coordinates are a, ab, ac, abc, or bc, with the remaining
rank supplied in H. The following tests exclude a, abc and bc.

* For mask a, the vector w=e_0-r u_6=b+c is in the kernel. But
  v_i w=1+r. This forces r=-1. At that value v_i B_i w=2, another
  contradiction because the kernel is invariant under B_i.
* For mask abc, the image contains e_0,u_6,u_i and the row space contains
  v_0,v_6,v_i. Close both under B_i. The rank lower bounds are 4,6,4
  at sites 1,3,5. None permits rank three.
* For mask bc, the image contains w,u_i and their B_i images. At site 3
  the four columns [w,u_i,B_i w,B_i u_i] have the minor -4r on rows
  0,1,3,4. It is nonzero. At sites 1 and 5 their invariant span has
  dimension three for every nonzero r. Take A=[w,u_i,B_i w]. A minor
  is 2r^2 at site 1 and 2 at site 5. The replay checks B_i A=A M_i(r)
  as an identity in Q[r,r^-1]. It also checks v_i A equals row 0 of A.
  Since b=e_0-a is in this image, v_i a=a_0=1-r. The mask kills a,
  so v_i a=0 and r=1. At this exceptional value
  e_0=(w-B_i w)/2 lies in the image. Thus a=e_0-b lies in the image
  as well as the kernel. This contradicts sum(a)=1.

This leaves only masks ab+h and ac+h, where h is one line in H.
Call them L and R. The exceptional value r=1 is explicitly checked;
generic elimination without that check would leave a gap.

## 5. Only one L and one R are possible

Write w_0=e_0+u_6. Column containment and the endpoint coordinates give
the required H lines at a rank-three site i:

```text
L: d_i=e_i-w_0+z/r,       v_i z=1,
R: d_i=e_i-w_0+z,         v_i z=-r.
```

These lines are nonzero. The rank-one projectors on H commute. Any two
are either equal or have zero product.

Two equal L lines give the same rank-three projector. It would contain
three query columns and rows from sites 0,i,j, which section 2 excludes
in dimension three. Equal R lines fail in the same way with site 6.
For two distinct L lines, cross pairing must vanish in both directions.
The sum of those two equations is 2/r=0, which is impossible. For two
distinct R lines the sum is -2r=0. Thus there is at most one of each type.

An L line and an R line cannot be equal either. Apply their two query
rows to their two required H vectors. If the L site is earlier, the
determinant of this two-by-two pairing matrix is -1. If it is later,
the determinant is 3. Both are nonzero in characteristic zero. Thus the
lines are independent. Cross pairing then requires the L site to precede
the R site; the opposite order gives a forbidden entry 2.

Consequently, the four-full, two-idle root has the masks

```text
site 0: {a,b},
earlier rank-three site: {a,b,h_L},
later rank-three site: {a,c,h_R},
site 6: {a,c}.
```

The two H lines are distinct and leave one unused H coordinate. This is
exactly the six output supports in the theorem. Different allowable site
locations, the free parameter r, and different scalar bases cannot change
this price pattern.

The free parameter is real, not just a redundant case in the exclusion.
There is an explicit positive algebraic family for every r!=0. With
w_0=e_0+u_6, set

```text
z=(r+1)w_0-r e_1-e_5+e_2-e_3,
F=[a,b,c,e_3-e_4,d_R,d_L],
d_L=e_1-w_0+z/r,       d_R=e_5-w_0+z.
```

Use the same four masks at sites 0,1,5,6. The replay checks a displayed
inverse of F, every projector identity, all pairwise commutators and
the prefix commutators as exact Laurent identities for all r!=0. Thus
the entire parameter family has the same endpoint and price pattern.
This supplies an algebraic positive control outside r=-1. It does not
replace the physical caller at the published source basis or certify
one uniform ordinary-cost bound over unbounded parameter values.

The same proof excludes three rank-three interiors whenever both
endpoints have rank two. Combining this fact, section 2 and the exact
rank tables gives the following lower bounds. The replay enumerates all
site rank assignments from {thin,2,3,4,5,6}; this is a complete finite
list of rank possibilities, not a coefficient search.

| Number of full stages | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Required extra whole idles, at least | 0 | 0 | 0 | 1 | 2 | 4 | 6 | 8 |

The existing four-full root attains its two-idle bound. The table does not
claim constructions that attain the other entries.

## 6. Transfer of the exact price ceiling

Let H(r)=r^(1-kappa), let L be the complete PR6353 paid-minus-helper
moment per port, and let C(n) be the minimum cost of all binary trees
with n native leaves. The separately registered composition replay uses

```text
C(1)=0,
C(n)=min_a [C(a)+C(n-a)+2H(8n)+1-2H(8n+1)],
G(n)=max_b [H(8n+1)-nL-C(n-b)-C(b)+H(8b+1)-H(8b)].
```

The complete margin for any root in the classified family is

```text
H(8(x+y)+1)+G(x)+G(y)-2.
```

This includes every native target debit, every binary-node job, the
three root thin queries and both individual whole idles. The proof above
shows why the formula applies to every root in the family, not just the
displayed source basis.

At 0.00328554, the composition replay checks 4,851 rational interval
binary splits and 4,656 root pair choices below total size 100. All fail.
For every larger size f, concavity gives the upper bound

```text
H(8f+1)+2H(4f+1)-f(L-1)+2(H(9)-H(8))-6.
```

Its value and derivative at 100 are strictly negative, and its derivative
decreases. The native deficit derivative is positive through the admitted
cap 0.0034. Thus the full infinite size range is excluded. The headroom
replay authenticates that numerical receipt; the composition replay
recomputes its interval bounds. Neither substitutes a numerical optimizer
for a proof.

## 7. The normalization is a whole-field identity at every width

The native phase checker gives q^2=X and X^2=I, with X an ordinary binary
translation. Define

```text
lambda=((1+i)I+(1-i)X)/2,
lambda^-1=((1-i)I+(1+i)X)/2,
S=lambda q.
```

Polynomial multiplication gives lambda^2=X, lambda^-1 lambda=I,
S^2=I and lambda^-1 S=q. These are identities for any operator with
the stated relations. They therefore hold at every tensor width after
the native q and the global X have been formed. Scalar coefficients stay
outside the tensor power. The proof does not infer an all-width statement
from a bounded collection of dense matrices.

On a nonzero binary translation x -> x xor t, choose one nonzero bit of
t. The addresses with that bit zero give exactly one representative per
pair. On each pair the four operations in the root proof implement
[[a,b],[b,a]], with a=(1+i)/2 and b=(1-i)/2. Conjugating the coefficients
implements the inverse. No field is initialized or copied. The map is
unitary; each scalar operation has maximum-norm growth at most two.
Address generation and scalar operations remain in the inherited route
and ordinary-work bill. This is not a new precision-tape admission.

There is a simple reason to keep the global rule. On two one-column
characters q=-i, the separate normalized characters are both +1. The
two-column q is -1, whose global normalized character is -1. Tensoring
the one-column normalization would therefore implement the wrong operator.

## Verification scope

`verify.py` uses only rational arithmetic and finite Laurent polynomials.
It rebuilds the query tuples, Gram identities, invariant image and row
spaces, free-parameter identities, exceptional case, line constraints,
rank floors and normalization identities. Its normal and optimized runs
must reproduce `RESULT.json`. The source root is a positive construction
at the lower bound. Removing the three-interior restriction lowers the
five-full bound to three, which checks that this restriction is needed.

These are author checks and a written proof. They are not independent
human review or formal-kernel acceptance. The complete conditional kappa
still has five inherited framework assumptions. No selected-frontier
change or general impossibility statement follows.

`caller_reverse.py` supplies an additional author implementation of the
actual 570-event caller. It propagates one output functional backward at
each of Q=1,-1,i,-i, with exact rational complex coefficients and formal
independent stage monomials. The source checker instead propagates a
matrix forward in the quotient Q^4=1. Since Q^4-1 has four distinct roots
over Q(i), the four character checks establish the full quotient-ring
identity. Every one of the 1,156 matrix entries is checked at all four
characters. Six omitted-operation controls and a nonzero off-diagonal
output are rejected. This is not independent human review and does not
replace the physical, native, price or compiler checks.

Prepared by Ali Romman with substantial OpenAI Codex assistance. The
shortest-query normal form, native word, binary module, source contraction,
and compiler retain their source attribution. Apache-2.0.
