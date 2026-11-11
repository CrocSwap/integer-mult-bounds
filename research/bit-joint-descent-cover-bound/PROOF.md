# Owned BIT descents through lower-rank catalogue transports

The exact selected #7001 native has nine owned rank-seven
descents to chart zero, roles 770 through 778. Each gathers
three source rows and supplies a later fanout to main outputs.
One uncharged descent would exceed the required native gain
of about 1.67 rank-one equivalents. The test retains all
other descents and allows one summary to be rebuilt with
arbitrary timing, XORs and any number of lower-rank existing
catalogue transports in the fixed monotone source flow.

Project each normalized scalar row onto the first 111
independent main coordinates. Label those coordinates by
their initial rank-one rational chart lines. Along a public
MOVE the set of contained initial lines can only increase.
An ADD uses a common chart, a SWAP exchanges chart and row,
and owned INIT contributes zero. Thus the main support of
a live row is confined to lines contained in its chart,
modulo the span of the retained owned descents already
introduced at chart zero. No other downward MOVE occurs.
The exact replay checks line-set monotonicity on every
public MOVE. It also checks that the selected summary is
outside the span of all other live chart-zero rows at its
first read, granting the other eight summaries.

The nine descent rows projected onto the main coordinates
generate 512 distinct codewords. The minimum nonzero weight
is 48. Even granting all other eight descents from the
start, every representative of the selected descent's
coset has weight at least 48.

The existing rational catalogue contains at most 0, 1, 2,
12 and 30 initial main lines at ranks 0, 1, 2, 4 and 6
respectively. Those are all available ranks below seven.
An exact integer capacity bound gives at most 30 distinct
lines in a union of charts of total rank at most six. For
`f(r)=r^(1−κ)`, 0<κ<1, the sum of paid powers is at least
the power of the total transported rank. A cheaper
replacement for one rank-seven descent must therefore
use total rank at most six. Its main support modulo the
retained descents can cover only 30 lines, below 48.
This rules out a strict saving by this replacement, even
with any number of asynchronous lower-rank accumulators.

# Up to four simultaneous descents

Use the same literal nine projected summary rows, catalogue and
monotone source-flow contract as the one-descent proof. Select k
of the nine summaries and retain the other 9−k. Allow any number
of new catalogue accumulators, arbitrary timing and arbitrary
XOR recovery after their descents. At each new descent the
monotone source-flow invariant confines the row to its source
chart's lines modulo the retained and already completed
descent rows. Subtract a combination of those earlier rows
to get a supported representative. In chronological order
this elimination preserves the span after every descent, so
recovery can use the representatives even when a later
accumulator uses an earlier descended value.

Order positive-rank new transports from largest to smallest.
The selected k target rows are independent modulo the retained
span. Consider the k recovery coefficient vectors on the new
transports. Some nonzero linear combination of the target rows
has a recovery expression whose coefficients on the k−1 largest
transports vanish, by the dimension of a homogeneous linear
system with k variables and at most k−1 equations. The result
is a nonzero codeword even after adding any retained summaries.
It has weight at least 48. Thus the union of the source supports
of the remaining transports must have capacity at least 48.
Zero-rank transports have no such support and can be omitted.

Let r be the largest remaining rank, and p=1−κ in (0,1).
Each of the removed k−1 ranks costs at least r^p. The possible
values of r are 1, 2, 4, 6, 7 and 8. Lower bounds for the
remaining cost, in multiples of r^p, are 48, 24, 4, 2, 1
and 1 respectively:

- At r=1 or 2, each available chart covers at most its rank.
  Thus the sum of remaining ranks is at least 48.
- At r=4, the capacity is at most three times rank. Thus the
  sum of remaining ranks is at least 16. In all three cases
  use s^p ≥ s r^(p−1) for 0<s≤r.
- At r=6, either there are two rank-six transports, or one
  covers at most 30 and the remaining ranks ≤4 must cover at
  least 18 more. They have total rank at least six and cost
  at least 6·4^(p−1) ≥ 6^p.
- At r=7 or 8, count the largest remaining transport.

The total cost is therefore at least (k−1+b_r)r^p, where
b_r is the bound above. For k≤4 and r≤6 the integer
mass inequality (k−1+b_r)r ≥ 7k holds, so the cost is
at least 7k·r^(p−1) ≥ k·7^p. For r≥7, b_r=1 and
monotonicity gives the same result. Consequently any joint
change of up to four summaries has at least the original
paid moment for every 0<κ<1 under this contract.

This proof grants all retained summaries at the start and
overcounts union capacity. Timing or overlapping lines cannot
improve the lower bound. A possible cheaper monotone route
must change at least five summaries at once. The bound also
leaves new chart spaces, new nonmonotone source transports
and changes to the supplied target span open.
# Five summaries at the fixed moonshot price

Let p=1−κ* at κ*=0.0040075385047236. Demand at least
5/3 net paid units per native copy, a relaxation of the target's
60.1038992-unit raw deficit across 36 copies. If R is total
new rank, subadditivity gives a new cost of at least R^p.
We have 34^p ≥ 34(1−4κ*) > 35−5/3 ≥ 5·7^p−5/3,
using log 34 < 4. Thus R≤33.

Cancel the four largest transports as in the joint proof.
The tail must cover at least 48 lines. A tail maximum of
rank at most two costs at least 48 total tail rank. A tail
maximum of six needs at least 12 tail rank and four earlier
ranks of at least six, hence R≥36. A tail maximum of seven
or eight gives R≥35. The remaining possibility is rank four.
It needs at least 16 tail rank and four earlier ranks ≥4.
Those earlier ranks must all be four, since a six would
force R≥34. If the tail has at most three rank-four rows,
its capacity is at most 17+8·3=41, using a tail rank budget
of 17 and capacity at most one per rank below four. Thus
the only possible profile is eight rank-four transports and
at most one rank-one transport.

Cancel any four of the eight rank-four transports. The
remaining four rank-four charts must cover at least 47 lines
because the optional transport contributes at most one. Every
one of the eight charts must contain at least 11 lines.
The union of any pair must contain at least 23. These are
necessary conditions even with free, arbitrarily timed
recovery and unrestricted use of the optional line.

The exact catalogue contains 70 rank-four charts and 51
distinct eligible line supports. A depth-first search checks
the pair and four-chart conditions, rejecting paths with too
few remaining charts to reach eight. It exhausts after 59
visited states, with no eight-set and no unresolved cases.
Thus changing five summaries cannot supply the full required
BIT gap under this fixed catalogue and monotone source flow.
This leaves sub-target savings on five summaries, joint
changes to six through nine, and changed source interfaces
open.
