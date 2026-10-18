# Four restoring transfers force unit coefficients and fixed ports

Status: scoped theorem with a written argument and independent finite checks.
This note has no external review, supplier admission, or new exponent claim.

## Precise statement

Use the PR1682 interface over Q or C. There are independent dirty arrays
x0,x1,x2,y0,y1,y2,z,w of any common positive dimension. The linear maps Ai,Bj
are arbitrary, fixed, and need not commute or be invertible. Sources are immutable;
outputs are never read. Every child restores its scratch and required head positions.
The desired update is yi += sum_j Mij Ai Bj xj, where

```
M = [[1,1,1],[1,1,-1],[1,-1,0]].
```

A finite straight-line word contains exactly twelve ordinary queries, each of form
r += s Bj xj or yi += s Ai r, where r is z or w and s is +1 or -1.
There are exactly four additional transfers z += a_k w with fixed nonzero a_k in Q or C.
The word and its scalar constants are independent of the inputs and chosen maps.
Both roots and all sources restore for every input and every choice of maps.
No other operation, extra root, source mutation, root scaling, or scaled query is permitted.

Then every transfer coefficient is +1 or -1, and every such word has these ports:

```
B0=w, B1=w, B2=z, A0=z, A1=z, A2=w.
```

PR1682 proves this conclusion for unit transfers. This note removes that coefficient
restriction while retaining its other premises. In fact, the enlarged alphabet adds no
valid words: all four coefficients must be units. No bound with more queries or
more transfers follows.

## Pair and height reduction

Each operator occurs at least twice. To see necessity for Bj, set other source
maps to zero and vary xj. A single injection cannot disappear through invertible
root shears. For Ai, a single read leaves a nonzero coefficient of independent
initial root dirt. Each target row and column is nonzero, so no operator can be absent.
Exactly twelve queries therefore give two occurrences of each operator.

Let h be cumulative transfer height. The dirty-root matrix is
U(h)=[[1,h],[0,1]]. Root restoration forces sum_k a_k=0.
In normalized coordinates U(h)^(-1), a source query has direction (1,0)
at z or (-h,1) at w. Two injections cancel only at one common port with
opposite signs; a w pair also needs equal heights. Reader dirt rows are
(1,h) at z and (0,1) at w. Two reads cancel dirt only at one common
port with opposite signs; a z pair also needs equal heights.
These are coefficient identities in independent initial data, not clean-root assumptions.

## The additional coefficient argument

Suppose all three B pairs use w. Write u_j=Bj xj. During the source walk,

```
w = w_initial + q dot u.
```

For each coordinate j, q_j starts at zero, becomes one fixed sign epsilon_j,
and returns to zero. Thus differences of any two visited q vectors have all
coordinates in {-1,0,1}. This fact holds regardless of the interleaved transfers.

Consider a nonzero required row obtained through z. Its reader gaps have equal
height. The consecutive transfers between these gaps must sum to zero.
There cannot be one transfer, because its coefficient is nonzero.
There cannot be three transfers, because the fourth coefficient would be zero.
Zero transfers leave z unchanged. All four transfers also leave z unchanged:
z has no direct source updates, and its full source coefficient must restore.
Therefore the reader gaps enclose exactly two transfers, with coefficients a,-a.
Their source difference in z is a times the difference d of the two visited w vectors,
up to the reader sign. In particular d belongs to {-1,0,1}^3.

Every target row has a nonzero entry equal to +1 or -1.
The equation plus-or-minus a*d=M_i forces a=+1 or -1 by that entry.
Consequently this row is already an ordinary signed difference of two visited w vectors.
A row read directly through w has the same property.
Thus all three target rows would occur as differences in one six-step source walk.

The exact finite lemma below excludes this. Therefore not all B pairs use w.
The argument permits arbitrarily large, irrational, or nonreal transfer coefficients;
the discrete bound concerns the ordinary source queries, not the transfer alphabet.

## A graph proof of the inherited one-root obstruction

Normalize coordinate j by its first sign epsilon_j. The source walk becomes a
closed six-edge walk on the cube {0,1}^3, using each coordinate direction twice.
For each full-support target row, its difference fixes a unique unordered pair
of complementary cube vertices. The rows (1,1,1) and (1,1,-1) together require
all four vertices above one diagonal of the first-two-coordinate square:
those first-two-coordinate corners are opposite, and both third-coordinate heights occur.

The remaining row (1,-1,0) requires the other diagonal of that square, at one
common third-coordinate height t. Thus six distinct cube vertices are mandatory:
four over the first diagonal, and two over the other diagonal at height t.
The two vertices over the first diagonal at height 1-t each have only one
neighbor in this six-vertex set: their vertical neighbor at height t.

A closed six-edge walk has at most six distinct vertices. To visit these six,
it must visit exactly them without any repeated vertex before closing: a simple
six-cycle. A vertex of degree one in the induced graph cannot belong to such
a cycle. This contradiction proves the obstruction without an exhaustive computation.
It also covers a required set omitting the starting vertex: then even the
six-distinct-vertex bound already fails. The argument is independent of first signs.

## Finite corroboration and its coverage

There are 6!=720 orders of B0+,B0-,B1+,B1-,B2+,B2-.
These exhaust every signed source walk with one positive and one negative occurrence
of each Bj. A reader pair exists precisely when two visited coefficient vectors
differ by its target row. Reversing reader signs accounts for the opposite difference.
The event implementation tests all ordered vertex pairs for all 720 walks.
None supplies all three rows of M.

A second implementation uses the three-dimensional cube graph. A vertex records
which source pairs are open. An edge flips one coordinate. A state stores the
current vertex, three edge-label counts, and the visited vertex set.
Starting at vertex zero, six transitions with each label used exactly twice return
to zero. Dynamic programming merges histories with identical states. It leaves
43 distinct visited cube sets. The eight choices of first-source signs produce
344 distinct signed vertex sets. Every event-model vertex set is present, and
there are no additional sets. This establishes exact coverage agreement without
sharing the event permutation traversal. Neither engine finds all three rows.

The obstruction is the inherited PR944 result, given a graph argument and independently
rechecked here. It is not a new one-root result. The universal reduction above
is a written argument; the finite scripts do not quantify over arbitrary programs.

## Transpose and directed support

Transpose the full linear circuit, reverse event order, exchange input and output
roles, and swap z with w. The shear alphabet again has form z += a w.
The new maps are A'_j=B_j^T and B'_i=A_i^T. Since M is symmetric,
the target is unchanged. Arbitrary maps and independent dirty roots remain arbitrary.
If all original A pairs used z, all transformed B pairs would use w.
The preceding exclusion therefore implies at least one A pair uses w.

A w read cannot see any source injected only into z. A0 and A1 each require
all three sources. If either used w, all B pairs would use w, which is impossible.
Thus A2 uses w and forces B0,B1 to w. B2 must use z. The nonzero B2
coefficients then force A0,A1 to z. These are exactly the six asserted ports.
The attaining unit-coefficient word is credited to Ross Richardson's PR1651.

## Restoration forces the remaining coefficients to be units

The port argument puts B0 on w and A0 on z. Track only the coefficient of
u0=B0 x0 in these roots; other source symbols and initial dirt are independent.
At the four transfer times, that coefficient in w has values q1,q2,q3,q4,
all in {0,epsilon}, for one fixed epsilon in {+1,-1}. No direct z query carries u0.

The two A0 reads have equal dirt height, and their signed u0 difference is 1.
They cannot enclose zero or four transfers: in either case the u0 coefficient
is unchanged, using full root restoration in the four-transfer case.
One or three transfers cannot sum to zero with all four coefficients nonzero
and total height zero. Hence they enclose two consecutive transfers, a,-a.
If the reader orientation is s in {+1,-1}, their u0 equation is

```
s*a*(q_p-q_{p+1}) = 1.
```

Here the chronological orientation can be absorbed into s. A nonzero difference
of two elements of {0,epsilon} is +1 or -1. Thus a is a unit.
Let the other two transfer indices be r<t. Their coefficients must be b,-b,
because all four coefficients sum to zero. Full restoration of the u0 coefficient gives

```
a*(q_p-q_{p+1}) + b*(q_r-q_t) = 0.
```

The first term is +1 or -1. Therefore q_r-q_t is nonzero and equal to +1 or -1,
which forces b to be a unit too. All four coefficients are now units.
Total height zero forces exactly two positive and two negative coefficients.

This also gives a distinct finite linear-model check of the new universal step.
For all 32 choices of a sign and a binary quadruple, each of three consecutive pairs, and both
reader orientations, the checker solves four linear constraints in four unknown
coefficients by generic rational elimination. The constraints are total height zero,
pair height zero, the reader coefficient 1, and final u0 coefficient zero.
All 192 systems either have no solution or have a unique unit solution.
The all-zero quadruple occurs for either sign; these are parameter choices, not 32 distinct q vectors.
There are 48 consistent systems. A separate two-difference formula agrees with
each elimination result. This domain deliberately includes nonchronological q
patterns; it is a superset, so it cannot omit an actual circuit's coefficient case.
Gaussian rank and consistency over Q are unchanged on extension to C.
The check covers unbounded complex coefficients through exact linear elimination,
not through numerical coefficient samples. The written argument supplies the
program-to-system reduction.

## Complete cost boundary

Let q_F,r price both signed invocations of operator F at port r, including child
work, source access, frame changes, scratch restoration, head return, and dispatch.
For any admitted word, the exact additive cost has form

```
I + P + D + 2*t(+1) + 2*t(-1)
 + q_B0,w + q_B1,w + q_B2,z + q_A0,z + q_A1,z + q_A2,w.
```

I,P,D include admission, coefficient preparation, program loading, and remaining
control work. If those costs depend on event order or coefficients, use their
actual values. No constant common overhead is assumed without justification.
Every admissible word pays this fixed sum when the complete tariffs and I,P,D
are common to that class. The PR1651 unit word attains it. Thus this is also
the exact additive tariff optimum over arbitrary nonzero one-way coefficients.
If overhead depends on scheduling, only the forced query/transfer multiset follows.
PR1682's unit-census domain is consequently the entire enlarged source-trace domain;
its reported 80 successful source traces are credited, not independently recounted here.
No selected-supplier seam, physical stock, precision allowance, or contracting
multiplication recurrence has been supplied. Stop before implementation of a supplier.

## Attribution and status

Credit Ross Richardson's PR944 for the signed target and one-root obstruction;
Charles Bethin's PR1637 for the twelve-query two-root interface;
Ross Richardson's PR1651 for the four-transfer witness;
and PR1682 for the unit-transfer port proof and transpose argument.
PR1675 separately excludes shorter bidirectional transfer words.
Exact predecessor commits and proof hashes are in PREDECESSORS.json. Original frozen proofs
remain unchanged. Substantial OpenAI Codex assistance covers this argument and checker.
Apache-2.0, consistent with the predecessor repository.

## Open next questions

Allow more than twelve queries or more than four transfers only with complete tariffs.
The scaled-query and six-transfer controls show why those restrictions matter.
A physical supplier still needs actual compatible ports, frames, ownership, and precision.
First identify a source-bound selected call before pricing any implementation.
Do not repeat the completed unit-shear census or claim selected-supplier savings.
