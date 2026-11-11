# An irreducible no-edge pool of pattern dimension 4 and joint image 5

Prepared by unpaidmoon with substantial Cursor Grok assistance. New work is
Apache-2.0. This is a written existence proof for one explicit pool, checked
again by a finite pattern census and by the subspace lattice of its joint
image. **No new κ.** The selected frontier stays `781451/250000000`.

## 1. Statement

Work over F2. For a matrix N, write off(N) for the matrix obtained by
deleting its diagonal. Let P be a linear space of zero-diagonal W-by-W
matrices, and define the complete noncoordinate pool

    C(P) = {N = x y^T : y^T x = 1, off(N) in P, off(N) != 0}.

The condition y^T x = 1 makes N a rank-one idempotent. Put

    V(P) = sum_{N in C(P)} im(N),

and let e(P) be the number of matrix units E_ab, a != b, contained in P.
A subspace W ⊆ V(P) is invariant when N(W) ⊆ W for every N in C(P). The
action is irreducible when no subspace 0 < W < V(P) is invariant.

**Theorem.** For every ambient width W ≥ 5 there is a pattern space P of
dimension 4 with e(P) = 0 whose complete pool acts irreducibly on a joint
image of dimension 5. Explicitly, on coordinates {0, 1, 2, 3, 4},

    N_v = (e_0 + e_2)(e_1 + e_2)^T,
    N_u = (e_1 + e_2)(e_0 + e_2)^T,
    N_o = (e_0 + e_1 + e_2)(e_0 + e_1 + e_2)^T,
    N_a = (e_2 + e_3)(e_0 + e_1 + e_3)^T,
    N_b = (e_0 + e_2 + e_3 + e_4)(e_1 + e_4)^T,

and P is the span of their off-diagonal patterns, padded by zero rows and
columns when W > 5. Thus C(P) = {N_v, N_u, N_o, N_a, N_b}, dim V(P) = 5,
and the action is irreducible.

The first three projectors are the normal-form triple of #6921. On their
own three-dimensional image that triple is reducible. The two added
projectors are what make the joint image five-dimensional and the action
irreducible. This note does not reprove the pattern-dimension-at-most-3
theorem, and it does not replace the four-cycle of #6962.

The same hypotheses as those two results are in force: a complete
noncoordinate rank-one idempotent pool over F2, and no matrix unit in P.
The result is an existence proof. It is not an upper bound, and it is not
a classification of every pattern-dimension-4 pool.

## 2. The five patterns

Write x_v, y_v for the factors of N_v, and likewise for u, o, a, b. Each
pairing y · x equals 1:

    y_v · x_v = (e_1 + e_2) · (e_0 + e_2) = 1,
    y_u · x_u = (e_0 + e_2) · (e_1 + e_2) = 1,
    y_o · x_o = (e_0 + e_1 + e_2) · (e_0 + e_1 + e_2) = 1,
    y_a · x_a = (e_0 + e_1 + e_3) · (e_2 + e_3) = 1,
    y_b · x_b = (e_1 + e_4) · (e_0 + e_2 + e_3 + e_4) = 1.

The off-diagonal patterns, with every unlisted row zero, are

    p_v:  row 0 = e_1 + e_2,   row 2 = e_1,
    p_u:  row 1 = e_0 + e_2,   row 2 = e_0,
    p_a:  row 2 = e_0 + e_1 + e_3,   row 3 = e_0 + e_1,
    p_b:  row 0 = e_1 + e_4,   row 2 = e_1 + e_4,
          row 3 = e_1 + e_4,   row 4 = e_1.

Their weights are 3, 3, 5 and 7. Adding the displayed rows gives
p_o = p_v + p_u, with

    row 0 = e_1 + e_2,   row 1 = e_0 + e_2,   row 2 = e_0 + e_1,

which is the pattern of N_o. Thus p_o lies in span(p_v, p_u, p_a, p_b).

These four patterns are independent. In a linear relation
α_v p_v + α_u p_u + α_a p_a + α_b p_b = 0, row 4 receives a contribution
only from p_b, and that row is e_1, so α_b = 0. Row 3 then receives a
contribution only from p_a, namely e_0 + e_1, so α_a = 0. Row 1 receives
a contribution only from p_u, so α_u = 0. Row 0 then receives e_1 + e_2
from p_v, so α_v = 0. Hence dim P = 4, where P is the span of the four
patterns, padded by zero outside coordinates {0, 1, 2, 3, 4} when W > 5.

## 3. No matrix unit, and no single-column pattern

Every nonzero element of P is a nonempty sum of {p_v, p_u, p_a, p_b}.

If the coefficient of p_b is 1, row 4 of the sum is e_1, and row 0 is

    (e_1 + e_4) + α_v (e_1 + e_2),

which equals e_1 + e_4 or e_2 + e_4. Both have weight 2, and neither uses
only column 1, so the sum has at least two columns and weight at least 3.

If the coefficient of p_b is 0 and the coefficient of p_a is 1, row 3 of
the sum is e_0 + e_1. That is already two columns and weight 2.

If both of those coefficients are 0 and the sum is nonzero, the sum is
p_v, p_u, or p_v + p_u. The first has columns 1 and 2, the second has
columns 0 and 2, and the third has columns 0, 1 and 2. Each has weight
at least 3.

Every nonzero pattern therefore has weight at least 2 and at least two
columns, so e(P) = 0. The same column count is the input to the
realizability argument in the next section.

## 4. The pool is exactly the five projectors

First let t ≥ 5, and suppose some pool element has image bit x_t = 1.
Row t of every matrix in P is zero, so the off-diagonal part of row t of
x y^T is zero. That row, with its diagonal entry removed, is y with
coordinate t cleared. Thus y = e_t. Idempotence gives the remaining bit
1. Column t of P is zero, so x vanishes off t. The pattern is zero,
which is excluded from C(P). If instead y_t = 1 and x_t = 0, column t
equals x and must vanish, so x = 0, contradicting the pairing. Every
pool element is therefore supported on {0, 1, 2, 3, 4}. It is enough to
classify patterns inside that coordinate block. The block is
five-dimensional as a vector space of coordinate masks, and P meets it
in the four-dimensional space already described. There are exactly
fifteen nonzero patterns.

A nonzero pattern M = off(x y^T) can have a zero row on the support of
x only in one situation. If x_i = 1 and row i of M is zero, then y
vanishes off i. The pairing forces y = e_i, and M is supported in column
i. Section 3 says P contains no such nonzero pattern. Consequently every
realizable pattern in P has nonzero rows exactly on the support of x.
Each of those rows equals y with its own diagonal bit removed, so the
rows determine every off-support bit of y. A disagreement between two
rows on such a bit means that M has no rank-one idempotent lift.

The fifteen patterns fall into two lists.

**Realizable.** The rows force one covector, and the pairing equals 1.

| pattern | forced image | forced covector | projector |
| --- | --- | --- | --- |
| p_v | e_0 + e_2 | e_1 + e_2 | N_v |
| p_u | e_1 + e_2 | e_0 + e_2 | N_u |
| p_v + p_u | e_0 + e_1 + e_2 | e_0 + e_1 + e_2 | N_o |
| p_a | e_2 + e_3 | e_0 + e_1 + e_3 | N_a |
| p_b | e_0 + e_2 + e_3 + e_4 | e_1 + e_4 | N_b |

For p_v, row 0 forces y_1 = y_2 = 1 and y_3 = y_4 = 0, while row 2 forces
y_0 = 0. For p_u, row 1 forces y_0 = y_2 = 1 and y_3 = y_4 = 0, while row 2
forces y_1 = 0. For p_v + p_u the three nonzero rows are e_1 + e_2,
e_0 + e_2 and e_0 + e_1; together they force every bit of
y = e_0 + e_1 + e_2, including y_3 = y_4 = 0. For p_a, row 2 forces
y_0 = y_1 = y_3 = 1 and y_4 = 0, while row 3 forces y_2 = 0. For p_b, row 4
forces y_0 = y_2 = y_3 = 0 and y_1 = 1, while row 0 forces y_4 = 1. In each
case every covector bit is fixed by a row, so the pairing has one solution.

**Unrealizable.** Two nonzero rows require opposite values of one
covector bit. The bit is off both row indices, so both rows constrain it.

| sum | rows | bit | values |
| --- | --- | --- | --- |
| p_v + p_a | 0, 2 | y_1 | 1, 0 |
| p_u + p_a | 1, 2 | y_0 | 1, 0 |
| p_v + p_u + p_a | 1, 2 | y_0 | 1, 0 |
| p_v + p_b | 2, 3 | y_1 | 0, 1 |
| p_u + p_b | 0, 1 | y_2 | 0, 1 |
| p_v + p_u + p_b | 0, 1 | y_4 | 1, 0 |
| p_a + p_b | 0, 2 | y_1 | 1, 0 |
| p_v + p_a + p_b | 0, 2 | y_1 | 0, 1 |
| p_u + p_a + p_b | 0, 1 | y_2 | 0, 1 |
| p_v + p_u + p_a + p_b | 0, 1 | y_4 | 1, 0 |

Each row of a sum is the sum of the corresponding basis rows from Section
2. For instance row 0 of p_v + p_a is e_1 + e_2, so it requires y_1 = 1,
while row 2 is e_1 + (e_0 + e_1 + e_3) = e_0 + e_3, so it requires y_1 = 0.
The other nine lines are the same one-bit comparison. None of these ten
patterns has a lift.

Therefore C(P) = {N_v, N_u, N_o, N_a, N_b} at every width W ≥ 5.

## 5. The joint image and the covectors

The five images are

    x_v = e_0 + e_2,
    x_u = e_1 + e_2,
    x_o = e_0 + e_1 + e_2,
    x_a = e_2 + e_3,
    x_b = e_0 + e_2 + e_3 + e_4.

Suppose a linear combination vanishes. Coordinate 4 appears only in x_b,
so that coefficient is 0. Coordinate 3 then appears only in x_a, so that
coefficient is 0. Coordinate 1 leaves the relation α_u + α_o = 0, and
coordinate 0 leaves α_v + α_o = 0. Coordinate 2 then reads
α_v + α_u + α_o = α_o = 0. The five images are independent. They lie in
E = span(e_0, e_1, e_2, e_3, e_4), so they are a basis of E. Section 4
puts every image in E, and V(P) = E has dimension 5.

The five covectors are

    y_v = e_1 + e_2,
    y_u = e_0 + e_2,
    y_o = e_0 + e_1 + e_2,
    y_a = e_0 + e_1 + e_3,
    y_b = e_1 + e_4.

The same coordinate chase shows they are independent: coordinate 4 fixes
the coefficient of y_b, coordinate 3 fixes the coefficient of y_a,
coordinate 0 leaves β_u + β_o = 0, coordinate 1 leaves β_v + β_o = 0, and
coordinate 2 gives β_o = 0. Restricted to E they are a basis of E*. Their
common kernel on V(P) is zero.

## 6. The hit digraph

Draw a directed edge j → i, for distinct labels, when y_j · x_i = 1. The
six edges used below are

    a → v:  (e_0 + e_1 + e_3) · (e_0 + e_2) = 1,
    v → b:  (e_1 + e_2) · (e_0 + e_2 + e_3 + e_4) = 1,
    b → o:  (e_1 + e_4) · (e_0 + e_1 + e_2) = 1,
    o → a:  (e_0 + e_1 + e_2) · (e_2 + e_3) = 1,
    a → u:  (e_0 + e_1 + e_3) · (e_1 + e_2) = 1,
    u → a:  (e_0 + e_2) · (e_2 + e_3) = 1.

Thus (a → v → b → o → a) is a directed 4-cycle and (a → u → a) is a
directed 2-cycle. Each of v, b and o lies on the 4-cycle, and u lies on
the 2-cycle, so every vertex reaches a and is reached from a. The digraph
on {v, u, o, a, b} is strongly connected.

**Cut lemma.** In a strongly connected digraph, every nonempty proper
vertex subset A has an edge into A from its complement. Indeed, take a
vertex p in A and a vertex q outside A. A directed path from q to p has
a last vertex outside A, and the next vertex of the path lies in A.

Applied here: for every nonempty proper subset A of the five projectors,
some j outside A and some i in A satisfy y_j · x_i = 1.

## 7. The action is irreducible

Let W ⊆ V(P) be invariant, and let A be the set of pool labels whose
covector does not vanish on W.

If i is in A, some vector of W is sent to x_i, so x_i lies in W. The span
of {x_i : i in A} is therefore contained in W. If j is outside A, then
y_j vanishes on W, so W is contained in the intersection of those kernels.

The empty active set forces W into the common kernel, which Section 5
shows is zero. The full active set forces W to contain every image, hence
W = V(P). Suppose A is nonempty and proper. The cut lemma supplies
y_j · x_i = 1 with i in A and j outside A. Then x_i lies in the span of
the active images and outside ker(y_j), so that span is not contained in
the complementary intersection. This contradicts the containment forced
by invariance.

No proper nonzero subspace is invariant. The action on the
five-dimensional joint image is irreducible.

The same three projectors without N_a and N_b are the normal-form triple.
On their image, the line span(x_u) is invariant: y_u · x_u = 1 with image
x_u, while y_v · x_u = 0 and y_o · x_u = 0. The two added projectors are
what breaks that line. y_b · x_u = 1 and the image x_b is outside the
line, so N_b carries x_u out of span(x_u).

## 8. Evidence class and scope

The argument above is a proof for one explicit pool, valid at every width
W ≥ 5. The fifteen-pattern list is the complete set of nonzero vectors in
this four-dimensional P; it is not a census of all four-dimensional pattern
spaces. The verifier repeats those fifteen weights and lifts, scans every
rank-one idempotent at widths 5, 6 and 7, checks the six digraph edges,
and enumerates every subspace of the joint image. The number of subspaces
of F2^5 is the sum of the Gaussian binomial coefficients, 374, including
the zero subspace and the whole space. That lattice check is corroboration.
The written argument does not depend on it.

This existence result does not give a replacement upper bound. Dimension
6 and higher, at the same pattern dimension, stay open. A search that
finds no further example would not decide them: nothing here bounds the
ambient support of an arbitrary pattern space. The four-cycle of #6962
remains the example that irreducible dimension 4 occurs, and the
dimension-at-most-3 theorem of #6921 is cited rather than reproved. The
parity pool of #6838 still shows that total dimension 5 can be reducible;
the pool in this note is a different one.

The selected κ and its five framework assumptions are unchanged. The note
produces no rational-address word, native primitive, supplier admission,
or multiplication identity.

## Open next questions

The packaged question is whether some complete no-edge pool of pattern
dimension 4 acts irreducibly in joint-image dimension 6 or more. The pool
above attains 5, so any upper bound is at least 5. One explicit witness
with a written invariant-subspace check, or a scoped upper bound under
the same hypotheses, would be the next useful step.
