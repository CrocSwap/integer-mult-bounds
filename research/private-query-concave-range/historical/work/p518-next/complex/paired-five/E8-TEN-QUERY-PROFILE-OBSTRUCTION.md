# The rank profile one, six, seven times eight is impossible

Keep the current eight-dimensional Gram query code W and the 112 binary
source labels. Suppose ten independent queries span a space that contains
W. One query f_s has a rank-one support frame, one query f_6 has a rank-six
frame, and eight queries f_j have rank-seven frames. These conditions are
impossible over Q, R or C.

The analytic capacity proof gives global source capacities one, twenty and
36 at frame ranks one, six and seven. A frame of rank six or seven meets
any root-query support in at most twenty or 32 ports, respectively. Root
queries have support 53 or 56. Every real non-root Gram query has support
at least 70. A complex query that is not a scalar multiple of a real
direction has support at least 76.

## Each triple gives an independent root query

No pair from the triple `f_s,f_6,f_j` can contain a nonzero Gram query.
Pairs with f_s have support below 53. A pair of ranks six and seven has
support at most 56, so any Gram query in it would be a root direction.
Those two frames cover at most twenty plus 32 ports of that root's support,
which is fewer than 53. This also is impossible.

The ten-query span modulo W has dimension two. Each of the three pairs
therefore has independent quotient images. The triple has an exact
one-dimensional intersection with W, and its nonzero vector g_j uses all
three query rows with nonzero coefficients. The eight vectors g_j are
independent: each has a nonzero coefficient of its own f_j and zero
coefficients of the other seven f_j rows.

Each g_j has support at most one plus twenty plus 36, or 57. It is
therefore a root direction. An axis-root direction has retained support
56, but its support is covered by at most one plus twenty plus 32, or 53.
Thus g_j is the direction of a retained nonaxis root alpha_j, with support
exactly 53.

## The self port must be the singleton

The support of g_j is covered by the three frames. Their intersections
with that root support have capacities one, twenty and 32. Their sum
equals 53. Equality therefore forces disjoint frame intersections of
exactly these sizes, covering every support port. Only one query can
supply each such port, and its coefficient in g_j is nonzero. Those
ports are exactly the scalar query supports. The singleton and rank-six
rows have no outside ports, by their global capacities. The rank-seven
row also has no outside ports, because its outside entries could not
cancel against either other row in g_j.

The root's self port alpha_j is in this partition. Its binary label has
self-pairing one. Every other root-support label has pairing zero with it.
If the self port were in the twenty-port part, the other nineteen labels
would span at least six dimensions: a rank-five frame contains at most
twelve source labels. They all lie in `p_alpha_j^perp`. The self label
is outside that hyperplane, so their union would have rank at least seven,
contrary to the rank-six frame.

If the self port were in the 32-port part, the other 31 labels would span
at least seven dimensions: a rank-six frame contains at most twenty labels.
Adding the self label outside their hyperplane would give rank at least
eight, contrary to the rank-seven frame.

Hence alpha_j is the singleton source port s for every j. All eight g_j
would then be multiples of the same root query. This contradicts their
independence.

This excludes this exact rank profile under the private support-frame
rule. It is not a physical circuit or a separate bound on all profiles.
