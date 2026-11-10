# The no-edge irreducible bound does not stay 3 in pattern dimension 4

Prepared by unpaidmoon with substantial Cursor Grok assistance. New work is
Apache-2.0. This is a written proof for one explicit pool, checked again by
finite enumeration. **No new κ.** The selected frontier stays
`781451/250000000`.

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

**Theorem.** For every ambient width W ≥ 4 there is a pattern space P of
dimension 4 with e(P) = 0 whose complete pool acts irreducibly on a joint
image of dimension 4. Explicitly, on coordinates Z/4Z,

    N_i = e_i (e_i + e_{i+1} + e_{i+2})^T,    i in Z/4Z,

and P is the span of their four off-diagonal patterns, padded by zero rows
and columns when W > 4. Thus C(P) = {N_0, N_1, N_2, N_3}, dim V(P) = 4, and
the action is irreducible.

Under the same hypotheses used for pattern dimension at most 3 — a complete
noncoordinate rank-one idempotent pool over F2, and no matrix unit — the
irreducible joint-image bound 3 therefore does not remain an upper bound in
pattern dimension 4.

This note does not prove a replacement upper bound. It does not say that
every pattern-dimension-4 pool is irreducible, and it does not say that 4 is
the largest irreducible joint-image dimension. Section 6 recomputes the
width-6 parity pool from #6838: its pattern dimension is 4 and its total
image has dimension 5, but a four-dimensional kernel is invariant, so that
pool does not decide the irreducible question.

#6921 proves that the bound is 3 for pattern dimension at most 3. Its case
split uses the Fano plane of a three-dimensional pattern space and is not
reproved or reused here. The fiber lemma is not an input: membership of
C(P) is settled by the support casework below.

## 2. The four patterns

Index coordinates by Z/4Z. For each i define

    y_i = e_i + e_{i+1} + e_{i+2},    N_i = e_i y_i^T.

Then y_i · e_i = 1, so N_i is a rank-one idempotent. Deleting the diagonal
leaves the pattern

    p_i = E_{i,i+1} + E_{i,i+2}.

These four patterns occupy eight distinct positions, so they are linearly
independent. Let P be their span. A general element is indexed by a subset
A ⊆ Z/4Z,

    p_A = sum_{i in A} p_i.

Row i of p_A is zero when i is not in A. When i is in A, that row has ones
in columns i+1 and i+2 only. Hence p_A has weight 2|A|. Every nonzero
element has weight at least 2, so e(P) = 0 and dim P = 4.

If W > 4, view each p_i as a W-by-W matrix with those two ones and with
every other entry zero. The same weight count holds, and rows and columns
indexed by t ≥ 4 are identically zero throughout P.

The four images e_0, e_1, e_2, e_3 are independent. Once Section 4 shows
that no further pool element exists, V(P) = span(e_0, e_1, e_2, e_3).

## 3. Action on the joint image

Identify V = span(e_0, e_1, e_2, e_3) with F2^4. On this space

    N_i(v) = e_i    if φ_i(v) = 1,    and 0 otherwise,

where φ_i = e_i* + e_{i+1}* + e_{i+2}*. In the basis e_0, e_1, e_2, e_3 the
covector matrix, with rows φ_0 through φ_3, is

    1 1 1 0
    0 1 1 1
    1 0 1 1
    1 1 0 1.

Row operations over F2 produce a permutation of the identity. Add row 0 to
rows 2 and 3; add the new row 2 to rows 1 and 0; add the new row 1 to row 3
and then to row 0; add the resulting row 3 to rows 0 and 2. The rows are
then e_0*, e_2*, e_1*, and e_3*. Swapping the middle two rows gives the
identity. The four functionals are therefore a basis of V*. Their common
kernel on V is zero. Each column of the matrix has weight 3, so each basis
vector e_j is sent to a different basis vector by at least two of the
projectors.

## 4. The pool is exactly the four projectors

Let x, y in F2^W satisfy y · x = 1 and off(x y^T) in P, with the pattern
nonzero.

First, both vectors are supported on {0, 1, 2, 3}. Suppose some t ≥ 4 has
x_t = 1. Row t of every matrix in P is zero, so the off-diagonal part of
row t of x y^T is zero. That row, with its diagonal entry removed, is y
with coordinate t cleared. Thus y vanishes off t, so y = y_t e_t. Idempotence
gives y_t = x_t = 1. Column t of P is zero, so its off-diagonal entries
x_i y_t = x_i vanish for i ≠ t. Hence x = e_t and the pattern is zero,
which is excluded from C(P). Therefore x_t = 0 for every t ≥ 4.

Suppose instead y_t = 1. Column t then contributes x_i for every i ≠ t, and
those entries must vanish, so x vanishes off t. Combined with x_t = 0 this
gives x = 0, contradicting y · x = 1. Thus y_t = 0 as well.

Now x and y are vectors in F2^4, still with y · x = 1. Let S be the support
of x. For each i in S, row i of the pattern is the off-diagonal part of y,
so the shape of P forces

    y_{i-1} = 0    and    y_{i+1} = y_{i+2}.

In particular y vanishes on S - 1 = {i - 1 : i in S}. Indices are read in
Z/4Z, so i+3 = i-1. Every nonempty S is a rotate of one of the five types
below, and the argument is stated for an arbitrary index, so it covers
every rotate.

**|S| = 4.** Then S - 1 = S, so y = 0 and the pairing is 0.

**|S| = 3.** Let S be the complement of {t}. Then y vanishes off {t-1}. The
pairing is y_{t-1}, so y = e_{t-1}. The constraint at i = t+1, which lies
in S, says y_{t+2} = y_{t-1}. The left side is 0 and the right side is 1.

**|S| = 2, opposite.** Let S = {i, i+2}. The two constraints give
y_{i-1} = y_{i+1} = 0 and y_{i+1} = y_{i+2}, y_{i+3} = y_i. Hence
y_{i+2} = 0. Since y_i = y_{i+3} = y_{i-1} = 0, the covector is zero.

**|S| = 2, adjacent.** Let S = {i, i+1}. The constraints give y_i = 0,
y_{i-1} = 0, y_{i+1} = y_{i+2}, and y_{i+2} = y_{i+3}. The pairing reduces
to y_{i+1} = 1, so y_{i+2} = 1. But y_{i+3} = y_{i-1} = 0, and the last
constraint says those two bits agree.

**|S| = 1.** Let S = {i}. Then y_i = 1, y_{i-1} = 0, and y_{i+1} = y_{i+2}.
If y_{i+1} = 0, then y = e_i and the pattern is zero, which is excluded.
If y_{i+1} = 1, then y = e_i + e_{i+1} + e_{i+2}, and the pattern is p_i.
That projector is N_i.

The empty support is impossible. Therefore C(P) = {N_0, N_1, N_2, N_3} at
every width W ≥ 4, and dim V(P) = 4.

## 5. The action is irreducible

Let A(W) = {i : φ_i does not vanish on W}, for a subspace W ⊆ V. If the
subspace is invariant and φ_i does not vanish on it, the corresponding image
e_i lies in it. The four functionals span V*, so A(W) is nonempty whenever
W is nonzero. They are distinct, so φ_i = ψ has at most one solution i for
a given nonzero functional ψ.

**Lines.** Each i in A(W) puts a distinct basis vector e_i into W, so a line
has |A| ≤ 1. It cannot be 0. If A = {i}, the line is span(e_i), but column
i of the covector matrix has two further ones, so some other φ_k also hits
e_i and |A| ≥ 2.

**Planes.** Three or more basis vectors cannot fit in a plane, so |A| ≤ 2.
The case |A| = 1 would require some e_i in the plane and φ_k(e_i) = 0 for
every k ≠ i, contradicting the column weight. Thus |A| = 2, the plane is
span(e_i, e_j), and the other two functionals vanish on both basis vectors.
All six pairs fail that test:

| pair | a functional outside the pair that hits the pair |
| --- | --- |
| {0,1} | φ_2(e_0) = 1 |
| {0,2} | φ_1(e_2) = 1 |
| {0,3} | φ_1(e_3) = 1 |
| {1,2} | φ_0(e_1) = 1 |
| {1,3} | φ_0(e_1) = 1 |
| {2,3} | φ_0(e_2) = 1 |

**Hyperplanes.** Let H = ker(ψ) with ψ ≠ 0. For each i outside A(H),
φ_i vanishes on H, so φ_i = ψ. At most one such i exists, hence |A(H)| ≥ 3.
If |A(H)| = 4, then H contains every basis vector and H = V. If
|A(H)| = 3, the three included basis vectors force ψ to be the remaining
coordinate functional e_j*, and the omitted index must be j, so
φ_j = e_j*. But φ_j has weight 3, not 1.

No proper nonzero subspace is invariant. The action on V(P) is irreducible,
and the irreducible joint-image dimension 4 is attained in pattern
dimension 4.

Deleting N_3 leaves the line span(e_0 + e_1 + e_3) in the common kernel of
φ_0, φ_1, and φ_2. That line is invariant for the proper subpool. The
four-projector statement uses the whole pool.

## 6. The parity pool one dimension higher is reducible

#6838 records the even-parity construction moved up one dimension as a scope
control: pattern dimension 4, total joint image 5. It is recomputed here
only to show that it does not already answer the irreducible question. This
is not a new total-image bound.

Use coordinates {0, 1, 2, 3, 4, 5}. Let U be the set of vectors supported
on {1, 2, 3, 4, 5} whose weights are even. Then U is a four-dimensional
subspace and contains no weight-one vector. Set

    P_par = {u e_0^T : u in U},    N_u = (e_0 + u) e_0^T

for each nonzero u in U. Every matrix in P_par is supported in column 0,
and its weight equals the weight of u. Thus e(P_par) = 0 and dim P_par = 4.
Each N_u is a rank-one idempotent with pattern u e_0^T. These 15 patterns
are all the nonzero elements of P_par, so the displayed projectors are the
complete pool. For distinct nonzero u, v in U,

    (e_0 + u) + (e_0 + v) + (e_0 + u + v) = e_0,

so e_0 lies in V(P_par) and then every u does. Hence

    V(P_par) = span(e_0) ⊕ U,    dim V(P_par) = 5.

Every covector is e_0. The subspace U is the kernel of e_0 on V(P_par). It
is nonzero and proper, and every projector kills it. The action is
reducible. The parity construction therefore shows that total image 5
occurs in pattern dimension 4, and it does not show that an irreducible
image of dimension greater than 3 occurs. The four-cycle of Sections 2
through 5 is what shows that the irreducible bound changes.

## 7. What this does not claim

The selected κ and its five framework assumptions are unchanged. The
dimension-at-most-3 theorem of #6921 is cited, not reproved. Nothing here
is a paid-rank accounting for a three-relation word; that is question 1 of
#6921 and is untouched. No upper bound is claimed for irreducible joint
images in pattern dimension 4, and no classification of all such pools is
claimed. The finite scans in `verify.py` cover one 16-element vector space
and widths 4 through 8. They corroborate the width-independent casework;
they are not a search over all four-dimensional pattern spaces. A failed
search would not have been a proof.

The note produces no rational-address word, native primitive, supplier
admission, or multiplication identity.

## Open next questions

The packaged question is whether some complete no-edge pool of pattern
dimension 4 acts irreducibly in joint-image dimension 5 or more. The parity
pool is not an example. A single explicit witness, or a scoped upper bound
with the same hypotheses, would be the next useful step. Absence from a
partial search would not settle it.
