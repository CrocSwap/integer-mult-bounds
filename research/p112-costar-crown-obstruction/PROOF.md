# A nine-root obstruction for one masked co-star decoder

## Statement and exact model

Let the 120 E8 root lines be represented by doubled coordinates as specified in
[MODEL.json](MODEL.json). First list the 56 integral lines: for each `i<j` in
lexicographic order, put `+2` at coordinate i and `+2`, then `-2`, at coordinate j.
Then list the 64 vectors `(1,s2,...,s8)` with each tail sign in the order `+1,-1`
and an even number of negative signs. Indices start at zero. For representatives
v_r define `G(r,s)=v_r dot v_s / 4`. This is an ordinary bilinear inner product,
not a Hermitian coefficient pairing.

Delete the coordinate frame `e_(2j-1) ± e_(2j)`, j=1,...,4, whose source indices
are `[0,1,26,27,44,45,54,55]`. The remaining set is P112. For each source normal a
let

    S_a = {r in P112 : G(a,r)=0 or r=a}.

The self-line clause includes a live normal in its own co-star. The source label
pairing is `(G(r,s)+1) mod 2`. Its value 1 selects the **ordered even-entry mask**:
all diagonals and both orientations of every orthogonal pair. There are 6,720
such live entries. The target on this mask is `2G`, hence diagonal 4 and
orthogonal off-diagonal 0; no odd-entry equation is assumed.

**Theorem.** Assign at most `[3,2,2,2]` rational rank-one terms to the respective
normal groups `[0,1,56,87]`. Both factors of every term must be supported inside
the co-star of its assigned normal. No such sum equals `2G` on every masked live
entry. This permits arbitrary rational signs, coefficient zeros, repeated
terms, and unequal left and right factors. Nine slots with zero terms allowed
are equivalent to these capacities. No positivity or root-linearity is assumed.

The normals in doubled coordinates are:

| Index | Coordinates | Capacity |
| --- | --- | ---: |
| 0 | (2,2,0,0,0,0,0,0) | 3 |
| 1 | (2,-2,0,0,0,0,0,0) | 2 |
| 56 | (1,1,1,1,1,1,1,1) | 2 |
| 87 | (1,1,-1,-1,-1,-1,-1,-1) | 2 |

## Exclusive-root rank-two crown lemma

Suppose three anchors A and three anchors B are supported by one group only,
whose sum factors as `Z(x,y)=d_x t_y^T` with `d_x,t_x in Q^2`. Assume their
prescribed diagonal entries are a common nonzero scalar and that all
cross-pairs except the three matching pairs are prescribed zero. No equation
is imposed on the matching pairs.

Every anchor has nonzero d and t because its diagonal is nonzero. Any two
A anchors share an orthogonal B neighbour. Their d rows annihilate the same
nonzero t row and therefore belong to its one-dimensional kernel. They span
the same line. This proves all A d rows are collinear; the same reasoning proves
collinearity of all B d rows. Applying the reverse ordered zero equations
proves the corresponding assertions for the t rows.

The A and B d lines are distinct. For a prescribed cross-zero pair a,b,
`d_a t_b^T=0` while `d_b t_b^T` is nonzero, precluding proportional d rows.
Likewise `d_a t_a^T` nonzero and `d_a t_b^T=0` imply distinct A and B t lines.
Thus one row from each side spans Q^2, for d and for t separately.

If another root r has a prescribed zero with an A anchor a and a B anchor b,
and these incident entries receive no contribution from other groups, then

    d_r t_a^T = d_r t_b^T = 0,
    d_a t_r^T = d_b t_r^T = 0.

Independence on both sides forces `d_r=t_r=0`. Individual factor coordinates
may vanish throughout this argument; nonzero anchor rows follow from their
diagonals, not from a full-support premise. A specialization of the group to
rank one or zero cannot escape the distinct-line conclusion.

## Nine-root certificate and application

Write U_j=`e1+ej`, V_j=`e2+ej` for j in `{3,5,7}` in undoubled notation.
These are the exclusive anchors for group 87. All nine roots used below are
live and distinct. The following table gives their exact source indices and
doubled coordinates; the membership column refers to `(S_0,S_1,S_56,S_87)`.

| Role | Index | Coordinates | Membership |
| --- | ---: | --- | --- |
| U3 | 2 | (2,0,2,0,0,0,0,0) | (0,0,0,1) |
| U5 | 6 | (2,0,0,0,2,0,0,0) | (0,0,0,1) |
| U7 | 10 | (2,0,0,0,0,0,2,0) | (0,0,0,1) |
| V3 | 14 | (0,2,2,0,0,0,0,0) | (0,0,0,1) |
| V5 | 18 | (0,2,0,0,2,0,0,0) | (0,0,0,1) |
| V7 | 22 | (0,2,0,0,0,0,2,0) | (0,0,0,1) |
| r0 | 87 | (1,1,-1,-1,-1,-1,-1,-1) | (0,1,0,1) |
| r1 | 80 | (1,1,-1,-1,1,1,1,1) | (0,1,0,1) |
| r2 | 62 | (1,1,1,1,-1,-1,1,1) | (0,1,0,1) |

Let `A=(U3,U5,U7)`, `B=(V3,V5,V7)`, and `R=(r0,r1,r2)`. Direct dot products give

    G[A,B] = I3,
    G[R,R] = 2 I3,
    G[R,A+B] = [[0,0,0,0,0,0],
                [0,1,1,0,1,1],
                [1,0,1,1,0,1]].

An entry incident to an anchor receives contributions only from group 87:
the other groups' left factors vanish when the anchor is the row, and their
right factors vanish when it is the column. The six off-matching cross edges
are orthogonal and masked. Their reverse orientations are also masked.
The matching cross edges have inner product 1 and are not required zero.
Anchor diagonals equal 4. Group 87 has capacity two, so the crown lemma applies.

Both r0 and r1 are orthogonal to U3 and V3; r2 is orthogonal to U5 and V5.
The lemma forces the group-87 factors to vanish at all three roots. Groups 0
and 56 already vanish there by their support envelopes. Thus only group 1
can contribute to `R x R`. This entire 3-by-3 block is masked, so it must be
`4I3`, with determinant 64 and rank 3. But group 1 is a product of a 3-by-2
matrix and a 2-by-3 matrix, hence has rank at most 2. This is a contradiction.

The proof uses 39 ordered masked equations: nine diagonals, twelve oriented
crown-edge equations, twelve oriented anchor-to-residual equations, and six
residual off-diagonals. These exact equations are listed in
[CERTIFICATE.json](CERTIFICATE.json). Inconsistency of this subset excludes a
solution of all 6,720 equations.

## What the program certifies

[verify.py](verify.py) reconstructs the source ordering, puncture, co-stars,
full ordered mask, nine root coordinates, memberships and Gram matrices using
exact integer and rational arithmetic. It checks every finite premise above
and compares the reconstructed certificate and deterministic result with the
bundled data. It does not accept a caller-declared theorem verdict. The model
is fixed by a canonical-content digest embedded in the verifier.

The universal deduction from these premises is the written linear-algebra
argument above. Passing the Python check is **not** a kernel-checked
formalization of that argument or of multiplication. The result is only about
this normal assignment and capacities. It neither constructs a decoder nor
excludes other co-star assignments, different capacities, larger support
alphabets or physical implementations in other domains. It establishes no
physical-budget or kappa claim.
