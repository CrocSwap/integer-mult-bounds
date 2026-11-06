# Exact interval envelope one factor above a power of two

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement and cited premises

Use the balanced dirty word of Chafik Boukhalfa's PR628, with protected
source x, unread target y, and one distinct dirty scratch register at each
depth. A nonleaf with left product B and right product A executes
U,V,U^-1,V^-1 chronologically, where U adds Bx to its connector z and V
adds Az to y. Siblings reuse the same deeper scratch. Cuts are at complete
ideal leaves. Coefficient mass means the sum of absolute integer
coefficients after collecting identical noncommutative monomials.

For every integer h >= 0, the exact largest row coefficient mass over
every ordered pair of cuts, in either orientation, at n=2^h+1 is

    G(h) = floor(h^2/2) + h + 3.

It is also the exact worst joint-register operator norm over contractive
factors. Real scalar factors in {+1,-1} attain it. This is a scoped
ideal-word theorem, conditional on the following credited proof premises.

Write F(j)=floor(j^2/2)+j+2 and H(j)=floor((j+1)^2/2).
Hanson Sun's PR1085 gives unit-monomial entries, protected source/unread
target boundaries, and the 0-or-full-product endpoint rule for prefixes,
inverse prefixes and suffixes. CubeJerry's PR6770 gives the height-uniform
interval bound F(j), and total scratch-row mass at most H(j) for inverse
positive prefixes and positive suffixes. Charles Bethin's PR1278 gives
the chronological phase identities used below. PR6770 retains their
statements and proofs in [the unchanged predecessor proof](prior/6770-PROOF.md).
Arham Tahir's PR1374 supplies the power-of-two attaining family, retained
on main in `research/dirty-interval-coefficient-boundary/README.md`.
Those results are cited premises, not new results of this package.

## The unequal-child estimate

Induct on h. At h=0 there are two factors and four leaves. Directly
multiplying its contiguous leaf shears and their inverses gives maximum
row mass three. For h>=1 the children have sizes

    a=2^(h-1), b=2^(h-1)+1.

There are h deeper shared scratch registers W below the parent connector.
The left child uses h-1 of them; the last one is idle. Hence any left
prefix, inverse prefix or suffix has row mass at most h+1. The sum of its
W-row masses is at most H(h-1)+1 when it is an inverse positive prefix or
a positive suffix. The added one is the idle identity row, not fresh
scratch. The right child has h active scratch registers, giving row
mass at most h+2 and scratch-row sum at most H(h) in those same directions.

Let L act on (x,z,W) and R on (z,y,W). Suppose the rightmost factor is
an inverse positive prefix or a positive suffix. Exactly as in PR6770's
cross-child estimate, but retaining these unequal capacities, the bounds are

    every row of R L: at most 1+(h+1)+(H(h-1)+1) = G(h);
    every row of L R: at most max(H(h)+2,h+2) <= G(h).

For R L, the only potentially largest row is y. It is its own identity
row, at most one monomial multiple of L's z row, and at most one
monomial multiple of each W row of L. Other rows have no larger bill.
For L R, its z row consists of at most one external x term, the
unchanged source row z of R, and weighted W rows of R. W rows have at
most one external x term plus that W-row sum; y is unchanged from R.
The last inequality follows from H(h)<=floor(h^2/2)+h+1.

## Every chronological phase pair

Use positive child prefixes P and Q. Completed child maps are U and V,
and the completed parent is F=I+e_y AB e_x^T. Positive parent prefixes
in the four phases have the credited forms

    0: P;  1: Q U;  2: P U^-1 V U;  3: Q F.

Same-phase intervals are child intervals. Their masses are at most
F(h-1) on the left, and G(h-1) on the right by induction. For the three
adjacent phase pairs, both ordered directions factor as follows.

| Pair | Forward | Reverse |
| --- | --- | --- |
| 0,1 | Q_b (U P_a^-1) | (P_a U^-1) Q_b^-1 |
| 1,2 | (P_b U^-1) (V Q_a^-1) | (Q_a V^-1) (U P_b^-1) |
| 2,3 | (Q_b V^-1) P_a^-1 | P_a (V Q_b^-1) |

In every entry the rightmost factor is an inverse positive prefix or
a positive suffix, so the unequal-child estimate applies. Its left
dummy row and the right active scratch rows are exactly the shared W.

For pair 0,2 the new outer y row is its identity plus A times the
target row of the left suffix U P_a^-1. Its mass is at most h+2;
all other rows form a left-child interval. Interchanging the cuts and
negating the new row proves the reverse bound.

For pair 1,3 the parent interval is a right-child interval with an added
external x column. Each new entry has mass at most one by the credited
unit-entry suffix premise. Both orders therefore have mass at most
G(h-1)+1 <= G(h). This also holds at h=1, since G(0)+1=4=G(1).

For pair 0,3 the forward matrix is

    Q_b P_a^-1 + e_y AB e_x^T.

Only y needs more than the cross-child estimate. Write
Q_b[y,z]=e A and P_a^-1[z,x]=-f B, with e,f in {0,1}.
If e=0, its row mass is at most 2+H(h-1)+1 <= G(h).
If e=1, combine the extra ABx with A times the left z row before
bounding. When f=1 the x terms cancel. When f=0 the old x entry is
absent, so adding it leaves at most h+1 occupied entries in that row.
The bound is again 1+(h+1)+(H(h-1)+1)=G(h).
For the reverse matrix P_a Q_b^-1-e_y AB e_x^T, all other rows use
the L R estimate and y has mass at most h+3 <= G(h).

These exhaust six distinct phase pairs and both orders. Final child
boundaries can use either adjacent phase representation. An interval
of the negative word is an interval of the positive word at complementary
cuts in the opposite order. Thus all cuts and orientations are covered.
No formal factor commutation, rounded leaf or new allocation was used.

## Attainment by splitting the last leaf

For h>=1, take PR1374's n0=2^h scalar family, all factors +1 except

    A_(2^h-2^j-1)=-1, 0<=j<=h-2.

Its cuts are a=floor(3*4^(h-1)/5) and b=(4^h+2)/3. The first cut is
in the initial left child and b completes the first execution of the
rightmost factor. Its target row, credited entirely to PR1374, is

    y + (-1)^(h-1)(1+floor(h/2)) x
      + sum_(j=1..h) j*(-1)^(h+j) z_j.

The balanced tree for 2^h+1 factors is obtained from this perfect tree
by splitting precisely its rightmost leaf into two leaves. This follows
inductively because its root sizes are 2^(h-1) and 2^(h-1)+1.
Keep all old factors and append one +1 factor; the old rightmost factor
was +1. Completed occurrences of the replacement implement the same
old shear and restore the added scratch z_(h+1).

Before the first rightmost-factor occurrence, the new word therefore
agrees with the old word and has never used z_(h+1). The initial cut a
is unchanged. Stop the replacement after its first two leaf shears,

    z_(h+1) += z_h;  y += z_(h+1).

Relative to the old first rightmost leaf y+=z_h, its y row acquires
exactly the original z_(h+1) with coefficient +1. Thus the new cut is
b+1=(4^h+5)/3 and the displayed attaining row acquires one new +1 term.
Its mass is F(h)+1=G(h). The h=0 case is the explicit two-factor word.

Each noncommutative monomial has operator norm at most one when every
factor is contractive, so coefficient row mass bounds the joint maximum
norm. The real scalar sign witness attains that bound. For commuting
factors with every subset product bounded by Q>=1, PR1278's separate
squarefree interval premise gives the sufficient bound G(h)Q. Equality
for every chosen Q is not claimed.

## Scope

The result settles one infinite fixed-length family, not every n.
It concerns arbitrary joint disturbances at ideal leaf cuts. Actual
rounded error support, inverse preimages, internal growth, preparation,
precision and tape costs, a complete caller and all five selected
framework assumptions remain separate. There is no new kappa or complete
multiplication theorem. The written induction carries the universal
quantifiers; finite replay corroborates it. Independent human and formal
proof-kernel review are unclaimed.
