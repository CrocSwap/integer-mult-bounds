# The six-point rank-four sojourn is impossible at length 30

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: a scoped written proof with exact finite corroboration.

## Three translates require half the binary group

Let G be an elementary abelian binary group of order 2^r, r >= 2.
If A has three distinct elements and A+B=G, then |B| >= 2^(r-1).

Translate A to {0,a,b}. The nonzero distinct vectors a,b are linearly
independent, so H={0,a,b,a+b} is a subgroup of order four. Addition by A
preserves each H-coset. A coset containing at most one point of B contributes
at most three points to A+B and cannot be covered. Every one of the 2^(r-2)
cosets must therefore contain at least two points of B. This proves the bound.

The bound is sharp. In G=F_2^4, A={0,1,2} and
B={0,1,4,5,8,9,12,13} cover G. Numbers encode binary coordinate vectors.
The argument is elementary additive counting; no literature-wide priority
claim is made for the abstract lemma.

## Apply the lemma separately in eight fibers

Consider a closed singleton source word of length L on the eight coordinate
directions of F_2^8. Let P be its visited prefix set, including its initial
zero state and excluding the duplicate final state. Universality requires
P+P=F_2^8, using Ross Richardson's #943 prefix criterion.

Fix a source alpha that occurs exactly twice. Its two occurrences split P
into alpha-bit-zero and alpha-bit-one layers. Delete coordinate alpha and
call the two resulting sets Q0,Q1. The sets may overlap after projection,
but projection is injective within each layer, so

    |Q0| + |Q1| = |P| <= L.

Every difference with alpha-bit one uses one point from each layer. Thus
universality necessarily implies

    Q0 + Q1 = F_2^7.                                          (1)

This is the sojourn split of unpaidmoon #6943, retained by #7015 and #7093.
Its elementary derivation is included to keep this proof self-contained.

Suppose the steps strictly between the alpha occurrences use exactly four
other coordinate directions. Their span is a four-dimensional space V,
and Q1 lies in an affine V-coset. Translate that layer to arrange Q1 subset V;
this only translates the left side of (1), preserving the covering property.
Choose a complementary three-dimensional space W, so F_2^7=V direct-sum W.
For each w in W write

    F_w = {v in V : v+w belongs to Q0}.

Equation (1) implies F_w+Q1=V for every w. Now impose the separate case
left open in #7093, namely |Q1|=6.

If |F_w| <= 2, then |F_w+Q1| <= 12 < 16. If |F_w|=3, the lemma would require
|Q1| >= 8. Both are impossible. Hence every fiber has at least four points,
and there are eight fibers. Consequently

    |Q0| >= 32,
    L >= |Q0|+|Q1| >= 38.                                    (2)

In particular no universal closed length-30 word has this six-point
rank-four sojourn. This excludes the proposed (|Q0|,|Q1|)=(24,6) boundary.
Repeated prefixes cannot evade (2); they only decrease |P| relative to L.

The cross-layer lower bound |Q0|>=32 is sharp as a set-cover statement.
Take Q1={0,1,2,3,4,8} in V, K={0,4,8,12}, and Q0=K direct-sum W.
The first four points of Q1 form a complement of K in V, so Q0+Q1=F_2^7.
These sets have sizes 32 and 6. Their same-layer sums do not cover F_2^7.
They are not asserted to be a universal prefix set or a length-38 word.

## Exact scope and predecessor credit

The new result closes the explicitly unsearched size-six case of unpaidmoon
#7093 at 94b36d4649b5d29829959409acbc1906ef0b4379. Its sixteen-point census,
#7015's rank-three obstruction, #6943's bent census, and the length-28
results are cited, not replayed or validated by this package. No one else's
reported numerical census is needed for (2). In particular (2) does not
require f(7)=24 or a multiplicity classification of the full word.

The first working example is the six-point Q1 and three-point F={0,1,2}.
The finite checker exhausts every six-point Q1 and every three-point F in V.
Its separate literal-set implementation normalizes F and exhausts Q1 again.
Affine invariance relates the two computations. The all-size statement
rests on the written counting proof, not on the finite checker alone.

Other layer sizes and ranks remain open here. This is no new bound on f(8),
native construction, physical tariff, kappa improvement, or complete
multiplication theorem. No proof assistant or independent human acceptance
is claimed.
