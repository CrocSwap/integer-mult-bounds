# The line cut fixes the terminal rank for a cover-only response

This result concerns a port-diagonal response that changes only the
orthogonal cover label. It does not concern all monomial responses or
all supplier circuits.

Let q be an odd binary vector. Let v be an odd vector with q^T v=0.
Suppose the first native transfer reads a source in frame C_q and writes
a target in frame C_v. Let the common response be

    (E f)(h)=f(h L),

where L is orthogonal and the logical payload action is the identity.
Exact matching of the line spaces requires

    L q=v.                                           (1)

An affine translation can correct a phase. It does not change (1).

The raw common-response controller has preterminal state
(-F E^-1 y,F Q^-1 E x). To return FULL of the original raw input (Qx,y),
its X branch must apply Q F E^-1 F^-1 Q to the old Y branch. The FULL
conjugate F E^-1 F^-1 is a cover permutation and a translation: an
orthogonal matrix changes the full Z4 weight phase by an even linear
phase. Thus the terminal X branch, after its cover permutation and
translation are removed, is

    C_q C_w,  where w=L^-1 q.                         (2)

From orthogonality and (1),

    q^T w=(L q)^T q=v^T q=0.

Both q and w have norm one. They are therefore distinct and independent.
The binary upper-right Clifford block of (2) is

    q q^T+w w^T.

It has rank two. One positive rank-two native child implements it. A
one-field Clifford word with monomial views has total native rank at
least two, because the rank of a product is at most the sum of the
factor ranks and monomial views preserve rank.

This conclusion holds for every orthogonal extension L of the initial
line map. Later flag choices cannot reduce this standalone terminal
rank. For 112 ports and four pairs, the terminal rank is at least 896.
The finite recipe in `../common-monomial-terminal-20261018/` attains
that rank for the actual ten-cycle extension.

The result does not rule out an earlier native operation that absorbs
part of the terminal, a circuit that mixes fields, a logical response
with a nontrivial payload map, or a different initial native cut. It
does not prove a lower bound for multiplication algorithms.

The proof is symbolic in L, q, and v. The checker separately enumerates
all orthogonal binary matrices in dimensions three and five and all
odd q that satisfy q^T Lq=0. It checks the FULL phase identity on every
character in those dimensions and checks the rank-two conclusion. It
also binds all 112 actual port cycles. These finite checks support the
proof; they are not the basis of the universal claim.

No PR, commit, push, or publication is part of this work. Before any
future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
