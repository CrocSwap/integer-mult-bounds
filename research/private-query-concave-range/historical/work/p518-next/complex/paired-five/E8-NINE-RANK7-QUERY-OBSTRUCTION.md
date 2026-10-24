# Nine rank-seven private queries cannot span the Gram code

Keep the current retained E8 Gram code W of dimension eight and its binary
source labels in nine coordinates. Suppose nine independent scalar queries
f_0 through f_8 span a space that contains W. Suppose each query support is
contained in a binary source frame F_i of dimension seven. These conditions
are impossible, over Q, R or C.

## Short differences force a root simplex

The exact source census tests all 43,435 rank-seven frames. Each contains
at most 36 retained source labels. The source counts are even. Only a pair
with one 36-port frame and another 34- or 36-port frame could have union
larger than 68. All 1,806,336 such ordered pairs have union at most 66.
Thus every two rank-seven frames have source union at most 68.

No f_i is in W: every nonzero query in W has support at least 53. The
nine-query span modulo W has dimension one. Scale the queries so all have
the same nonzero quotient image. Their nonzero differences are then in W
and have support at most 68.

The support of a non-root real direction in W is at least 70. A complex
direction whose real and imaginary coefficient vectors are independent
has support at least 76, by the dimension-two generalized support bound.
Consequently every difference is a complex scalar multiple of a real E8
root direction.

Write the differences from f_0 as coefficient vectors a_i in eight
dimensions, with a_0=0. They are independent. In a plane through three
noncollinear a_i, the three differences are three distinct E8 root lines.
Such a plane has exactly the three lines of an A2 system. This follows
directly from root norm four and distinct-root inner products zero or
plus or minus two. An orthogonal pair has no third root line. For a pair
r,s with inner product two or minus two, the only third line is
`r-(r dot s)/2*s`. The checker verifies its membership in the literal roots.
To check that it is the only possibility, put g=r dot s, A=t dot r and
B=t dot s for a third root t in the plane. Then A and B are zero or plus
or minus two. The norm equation is
`4*(A^2+B^2)-2*g*A*B=4*(16-g^2)`.
It has no solution when g=0. When g is two or minus two, it forces both
absolute values to be two and the stated third line.

The relation between these three lines forces their scalar multipliers to
agree up to sign. Apply it to a_0,a_1,a_i and choose each root's orientation.
There is one common nonzero scalar lambda such that a_i/lambda is a real
root for each i=1 through 8, and every pair difference is a real root. Their squared pair
distances are four. Thus the nine points form a regular eight-dimensional
simplex. Its 36 edge root lines are ports of the full E8 set.

## Binary labels on the simplex

The eight edge labels incident to one vertex have binary Gram matrix I8.
They are independent. Extend them by their one-dimensional orthogonal
complement to an orthonormal basis in nine coordinates. This gives an
isometry to the following label model, with J the all-ones vector:

```text
p_ab = J + e_a + e_b,   0<=a<b<=8.
```

For each other edge, its pairings with the incident basis give six ones
and two zeros. Its odd self-pairing fixes its last coordinate as one.
Hence this model fixes all 36 labels. The eight labels in the star at j
span the coordinate hyperplane with coordinate j zero. Every nonincident
edge label is outside that full star span.

The eight removed coordinate root ports are mutually orthogonal. Simplex
edge roots are orthogonal exactly when their edges are disjoint. Thus the
removed simplex edges form a matching of at most four edges. Every vertex
retains at least seven incident edge ports, and some vertex j retains all
eight.

## Missing star ports give separating vectors

The rank-seven frame F_j must miss an incident port ja. At that port the
nine scalar query values have three levels: one value at each endpoint
and a common value at the other seven vertices. Relative to the common
value, the endpoint values are `+2t` and `-2t` for nonzero t. Since the
port is outside F_j, its query value f_j is zero. All other eight values
are then nonzero. Therefore p_ja is in every other frame but outside F_j.

For every vertex k other than j and a, the port ja is nonincident. It is
outside the full star span at k and is in F_k. At least seven incident
star ports at k are retained. F_k cannot contain those seven independent
labels and the extra port ja. It therefore misses a retained incident
port. That port's endpoint value is zero, so its label is outside F_k
and inside all other eight frames, by the same three-level calculation.

Thus at least eight vertices have a port label x_v outside their own
frame and inside every other frame. Choose a binary linear functional
l_v that vanishes on F_v and has value one on x_v. Then
`l_v(x_w)=1` for v=w and zero for distinct forced vertices. The forced
port labels are independent. If exactly eight vertices are forced, the
remaining frame contains eight independent labels. If all nine are
forced, each frame contains eight of the nine independent labels. Both
cases contradict frame dimension seven.

## Scope

This excludes the nine independent rank-seven-query profile for the fixed
Gram code and the private support-frame rule. Nonzero diagonal scalar
port scalings and invertible minimal binary factor changes preserve that
rule and the conclusion. It does not by itself exclude every other rank
profile, give a complete lower bound of 64, prove a physical cost bound
for shared carriers, or give a supplier improvement.
