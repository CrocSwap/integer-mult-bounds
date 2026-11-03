# A nine-ray obstruction in each F4 coordinate support

Let R consist of the 24 real F4 root rays, represented by the four coordinate
vectors, the twelve vectors e_i +/- e_j with i<j, and the eight vectors
(1,+/-1,+/-1,+/-1). Scaling a representative does not change orthogonality.
For coordinate j let A_j contain the rays with nonzero j-th coordinate.

A fitting matrix over a field K has nonzero diagonal and has B[x,y]=0 for
distinct nonorthogonal real rays x,y. Its orthogonal-pair entries are arbitrary,
independently in the two directions. In particular, symmetry is not assumed.

**Theorem.** Every fitting matrix satisfies rank_K B[A_j,A_j] >= 6 for each
j=0,1,2,3. Consequently, the four fixed coordinate queries have total binary
rank at least 24. For every t>0 their separate rank-power charges total at least
4*6^t. This strengthens the four rank-five bounds in Ali Romman's PR6512.

## The first coordinate

Use the following nine rays, all of which belong to A_0:

| Label | Representative |
| --- | --- |
| c_0 | (1,-1,-1,-1) |
| c_1 | (1,-1,-1,1) |
| c_2 | (1,-1,0,0) |
| c_3 | (1,0,-1,0) |
| c_4 | (1,0,0,0) |
| a | (1,-1,1,-1) |
| b | (1,-1,1,1) |
| u | (1,0,0,-1) |
| v | (1,0,0,1) |

Normalize each diagonal to one by scaling its row. This preserves all required
zeros and the rank. The c_i are pairwise nonorthogonal, so their principal
minor is I_5. Assume for contradiction that the nine-ray matrix has rank at
most five. Its rank is then exactly five. Take a rank factorization
B[x,y]=r_x s_y, with r_x a row of length five and s_y a column of length five.
The I_5 minor permits a change of factor basis with r_c_i=e_i^T and
s_c_i=e_i. This step uses only invertibility over K.

The required zeros against those five rays restrict both r_x and s_x to the
following coordinate sets:

| Ray | Allowed factor coordinates |
| --- | --- |
| a | {1,3} |
| b | {0,3} |
| u | {1} |
| v | {0} |

The diagonal of u is one. Thus its row and column coordinate 1 are both
nonzero. The real inner product a.u is 2, so B[a,u]=B[u,a]=0. These two
equations kill coordinate 1 of both r_a and s_a. Similarly b.v=2 kills
coordinate 0 of both r_b and s_b. The factors of a and b are therefore
supported only at coordinate 3. Their unit diagonals make all four remaining
scalars nonzero. Hence B[a,b] is nonzero. But a.b=2 requires B[a,b]=0, a
contradiction.

The numbers 2 in this argument are real inner products defining the zero
pattern, not elements of K. The proof therefore applies in characteristic two
as well as every other characteristic.

## Every coordinate and the cost consequence

Permute real coordinates 0 and j. The F4 ray set is invariant, up to signs
of its representatives. The nine-ray argument moves into A_j and proves the
same rank bound. Each query matrix is a principal submatrix of its coordinate
block, so the block rank is at least six. Summing the four independent rank
charges gives 24. Monotonicity of r^t for t>0 gives the stated power bound.

## Evidence and limits

The checker constructs the root rays independently and checks every geometric
zero used above on all four coordinate copies. It rejects all 36 possible
binary rank-five factor tuples on a,b,u,v after fixing the I_5 minor.
Separately, it enumerates every binary fitting matrix on the nine rays. There
are 18 independently free directed entries, hence 262,144 matrices. Two rank
engines agree on every matrix. A rank-six witness in that nine-ray domain is
reported. This does not assert a rank-six completion on the full 15-ray
coordinate support, or a common full 24-ray fitting matrix attaining all four
bounds.

The all-field quantifier is supplied by the written argument, not a finite
field census. Arbitrary decoder bases, rectangular factors, shared query
delivery, productive helper credits and complete native/caller invoices remain
outside the theorem. No kappa improvement, global F4 optimality, supplier
admission or complete multiplication theorem is claimed.

This contribution was produced by Nick Petalas. Credit Ali Romman for PR6512's
fixed-coordinate caller question and rank-five minor, DreamingOfClouds for
PR2125's earlier F4 cost-24 search, Aaron Wang for PR2272/2518's distinct fixed
pairing screens, and the retained root-unit, path-caller and productive-recursion
lineage. Rank factorization and zero-pattern arguments are classical.
