# An exact price for the dimension-cut relaxation

Take the standard constant binary field on each public owner. Each nested
upward scalar contact crosses the consecutive thresholds between the two
dimensions. The cut calculation for the literal source shows necessary counts
of 516, 627, 627, 627, 616, 616, 616 and 505 at these eight thresholds.
They sum to 4,750. The original upward contacts attain all eight simultaneously.

Minimize the sum of r^t, 0<t<=1, over multisets of intervals of r consecutive
thresholds that cover those eight demands. The minimum is exactly
505*8^t + 11*7^t + 100*6^t + 11*3^t. This is a solved interval-cover problem.
The original charts, source bits, messages and deadlines are extra constraints
when implementing an actual native word.

For the lower bound, order the dimensions 2,3,4,5,6,7,1,8 by decreasing
demand. Give position j in that order weight j^t - (j-1)^t. Concavity
makes these weights nonnegative and decreasing. The total weight of any
r positions is at most the sum of the first r weights, namely r^t.
Thus every admissible collection pays at least the weighted sum of demands.
For equality take the superlevel sets of the demand vector. The first 505
layers use [1,8], the next 11 use [1,7], the next 100 use [2,7] and the last
11 use [2,4]. Each is an interval and consists exactly of the most valuable
positions for its length. These layers supply each demand exactly and attain
the dual bound. For t=1 any exact cover attains 4,750.

At t=1-0.00389046 the original upward price lies between
4737.618920783137811 and 4737.618920783137812. The exact interval minimum
lies between 4712.558924499539618 and 4712.558924499539619. The resulting
25.059996283598193... difference is slack in a relaxation per native
invocation. Only a causal, endpoint-compatible, paid implementation of a
different roster can realize any part of it. Downward contacts, exterior
caller costs, and other productive requirements have their own prices.

`grade_price.py` authenticates the native gzip graph, recomputes upward
histograms, checks primal coverage and the non-tight dual inequalities by
outward dyadic roots, and encloses the resulting prices.
