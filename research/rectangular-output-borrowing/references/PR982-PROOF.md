# Exact output borrowing, query lower bound, and complete local price

## Interface and ownership

Let x and y_0,...,y_(k-1) be distinct length-L rows, k >= 2, over a module.
Their initial values are arbitrary and independent. B and the A_i are additive
linear operators; products need not commute and individual operators need not
be invertible. The desired simultaneous update is

```
x -> x,       y_i -> y_i + A_i B x.
```

A complete child `t += F(s)` preserves s and all its private scratch, is
independent of the incoming t, and uses unchanged read-only coefficients.
Its negative invocation is its literal inverse word. Source and target are
distinct. The private pool excludes x and **all** output rows except the
immediate child ports, and it never uses those ports as scratch. Other output
rows are excluded even if already completed or temporarily unused. Coefficient
storage does not overlap data. All calls are sequential, return their heads to
the specified entry positions, and have exclusive access to their mutable rows.

The new permission is narrowly at the top level: an output may be a complete
child's source/target connector. It is not permission to donate an ancestor
target to recursive descendants. The latter invalidates dirty-echo reasoning,
as PR822's explicit nonlinear counterexample illustrates.

## Construction

Choose a pivot q and another output r != q. Write Q for incoming y_q and
v=B x. First execute:

1. For every i != q, `y_i -= A_i y_q`.
2. `y_q += B x`.
3. For every i != q, `y_i += A_i y_q`.
4. `y_q -= B x`.

Each nonpivot increment is `-A_i Q + A_i(Q+v) = A_i v`. The pivot returns to Q.
Let R be the resulting y_r, including its desired increment. Now execute:

5. `y_q -= A_q y_r`.
6. `y_r += B x`.
7. `y_q += A_q y_r`.
8. `y_r -= B x`.

The pivot increment is `-A_q R + A_q(R+v) = A_q v`; y_r returns to its
completed value R. All other outputs retain their completed values. This
uses four B calls and two calls to each A_i, no copies, no zero initialization,
no uncharged source access, and no dedicated length-L connector. Private
scratch is restored at each numbered child boundary. The complete inverse is
the reversed expanded leaf word with every sign negated.

For the seed fixture q=2, r=0, the ten complete calls are:

```
y0 -= A0 y2; y1 -= A1 y2; y2 += B x;
y0 += A0 y2; y1 += A1 y2; y2 -= B x;
y2 -= A2 y0; y0 += B x; y2 += A2 y0; y0 -= B x.
```

This is ordinary dirty-commutator algebra with a changed ownership contract.
No algebraic or literature-priority claim is made.

## Sharp bound in the stated query alphabet

Take the free associative algebra Z<a_0,...,a_(k-1),b> and independent input
symbols X,Y_0,...,Y_(k-1). Permit only unit signed queries

```
Y_j += +/- b X;
Y_i += +/- a_i Y_j,   j != i.
```

There is no additional row. X is read-only. No scalar copies, other coefficient
multiples, combined output queries, direct `a_i b` queries, arithmetic on
coefficients, or writes to X are admitted. The word must work as a free-module
identity, not merely modulo a characteristic or for one specialized matrix.
Queries may read an already modified output, so the bound allows feedback.

Grade formal operator words by degree. At degree one in X, only B queries can
change a row: let h_j be the running integer coefficient of bX in Y_j. A queries
cannot change h_j because they increase degree and no row has a degree-zero X
term. All h_j must end at zero, since the requested outputs contain only
degree-two source increments.

At an A_i query reading Y_j, the change to the coefficient of a_i b X is
`+/- h_j`. If only one row q ever has nonzero h, then A_q cannot read that row
and the required a_q b X coefficient remains zero. Therefore at least two
different rows must have a nonzero B history. Each such history begins and ends
at zero and uses unit signed increments, hence requires at least two B queries.
There must be at least **four B queries**.

The degree-one coefficient of a_i Y_j in output i is exactly the signed count
of A_i queries reading j. Products of other queries have degree at least two
and cannot cancel it. Each count must vanish in the final map. Producing a_i b X
requires some A_i query, so every i needs at least two A_i queries. Therefore
every word in this alphabet has at least **2k+4 queries**. The construction
attains all these bounds simultaneously. It is also optimal for uniform
per-operator positive prices: `4 c_B + 2 sum_i c_Ai`. Port-dependent tape or
layout prices are not covered by that optimality statement.

For k=2, a minimum word has one positive and one negative B query into each
output, and one positive and one negative A_i query from the only other output.
Thus its multiset is exactly the eight signed queries in `verify.py:census`.
All 8! = 40,320 permutations are tested with full noncommutative polynomials;
224 realize the desired map. This is a complete finite classification of
minimum words in this alphabet. The proof of the lower bound is the degree
argument above, not finite search. For k=1 this alphabet has no A query at all;
we assert no general one-output impossibility.

## Recursive lowering and work/scratch recurrence

Factor lists are in application order: `[b0,b1,a0]` denotes a0 b1 b0.
The supplied emitter uses the credited balanced binary dirty commutator.
For a product with first-applied subproduct R and last-applied subproduct Q,
choose one private connector z and emit

```
t -= Q z; z += R s; t += Q z; z -= R s.
```

Descendants get the remaining private rows and exclude both parent ports and
the selected connector except when it is an immediate port. Induction proves
every child boundary is an exact product shear, restoring all other rows.
The verifier checks each such **top-level complete-child** expansion as a free
module identity and forbids access to other outputs anywhere inside it.

Let C(F;L,w) price a complete full-row child, including its source/coefficient
accesses, arithmetic, inverse/cleanup, routing, layout/frame operations and
head returns, at a common sufficient precision w. Both signs use the same upper
price. Let d be paid dispatch/control cost at the indicated interface. Then

```
C([f]) = c_f + d_leaf
C(R followed by Q) = 2 C(R) + 2 C(Q) + d_node
C_borrowed = 4 C(B) + 2 sum_i C(A_i) + d_borrowed
C_separate = 2k C(B) + 2 sum_i C(A_i) + d_separate
C_dedicated = 2 C(B) + 2 sum_i C(A_i) + d_dedicated.
```

Every child and inverse is charged at the same length L, never at L/k. Source
x, all A_i and B coefficients, and layout contracts must remain the same
between the matching calls. Any extra physical frame transition is included in
the actual child price or added explicitly. It cannot be erased by the count.
The exact child-bill saving relative to separate output-borrowed echoes is
`2(k-2) C(B)`; it is zero at k=2. Dispatch differences remain payable.

For a leaf, S=0 private rows; at a binary node,
`S(R,Q)=1+max(S(R),S(Q))`. Balanced n-factor products have S=ceil(log2 n).
Let s=max(S(B),max_i S(A_i)). The new batch and separate-output comparator use
**s extra dirty rows**, besides x and the k outputs. The dedicated batch uses
**s+1**. Thus total data is `(k+1+s)L` or `(k+2+s)L` words. There is no clean
length-L row. A leaf's own private workspace must be added separately.

With unit leaf prices, `N(1)=1` and
`N(n)=2N(floor(n/2))+2N(ceil(n/2))`. Hence N(6)=40, N(5)=28, N(3)=10,
N(1)=1, giving new/separate/dedicated counts 238/318/158 and private rows
3/3/4. These are explicit schedules, not optimal factor-tree claims. Changing
factorization or using higher-arity echoes is outside this comparison.

## Concrete exact dense invoice

For an independently executable finite realization, each factor is a supplied
read-only L-by-L integer matrix and each child leaf is a complete dense
matrix-vector additive update. A single scalar accumulator forms each dot
product; a constant number of scalar load/multiply ports suffice. All factors
are shared read-only by the comparators. If P is the number of distinct factors,
coefficient storage is P L^2 words. Preparing/validating coefficients costs
`Prep(P,L,w)` separately; the fixtures supply exact integers and the finite
input scan costs O(P L^2 w) bits. No factorization/phase oracle is free.

For N leaves the exact reference counts are:

```
N L^2 coefficient reads, N L^2 source reads,
N L target reads and N L target writes,
N L^2 multiplications, N L(L+1) additions,
L sign negations per negative leaf, N emitted instruction records.
```

The tape layout has all data rows first, then all coefficient matrices. For
every dot-product term visit its coefficient then source entry; visit the
destination for its read/update; return to slot zero **after every leaf**.
`verify.py:invoice` sums literal absolute head distances and separately derives
the same sum in closed form. For L=3, the seed receipts are:

| Schedule | Coeff/source reads, each | Multiplications | Additions | Travel in word slots | Data words |
| --- | ---: | ---: | ---: | ---: | ---: |
| Separate | 2862 | 2862 | 3816 | 299448 | 21 |
| Borrowed batch | 2142 | 2142 | 2856 | 245752 | 21 |
| Dedicated batch | 1422 | 1422 | 1896 | 197744 | 24 |

All have 135 coefficient words. These are invoices for the specified tape
trace, not runtime benchmarks. Multiply travel by w, charge O(w) per read/write,
the stated arithmetic counts times M(w)/A(w), and paid instruction dispatch.
The emitter stores N records of O(log(k+s+P)) bits each, with conservative
O(N log(m+1)) record work and O(N log(k+s+P)+m log(P+1)) control bits for total
m factor descriptors; this preparation is additional. Layout/descriptor
validation and exclusive ownership checks are also charged before execution.
Actual implementation on a different tape or physical frame must reprice it.

If input data magnitude is at most D and matrix entries at most H, a leaf shear
has joint infinity norm at most 1+LH. Every prefix of an N-leaf word is bounded
by `max(1,D)(1+LH)^N`. Thus

```
w = 2 + ceil(log2(max(1,D))) + N ceil(log2(1+LH))
```

is a sufficient signed integer width, also covering a scalar dot accumulator
by the same next-shear bound. Use the maximum N among comparators for a common
invoice width. The tests conservatively round upward with integer bit lengths
and check every represented forward and inverse prefix in dimensions 1..3.
Private scalar arithmetic/control bits are not counted as absent scratch.

## Precision boundary and limits

Linearity matters. With x=1, B(t)=A1(t)=t, A0(t)=floor(t/2), q=1, r=0,
incoming y0=y1=0 produces y0=0 and y1=1. Changing only incoming y1 to 1 changes
the y0 increment to 1. Literal reversal still restores all data, but the
update is not the ideal linear A0 B x. A nonlinear or rounded child cannot be
substituted into the exact identity or query theorem. In particular, this
package does not establish target independence for a rounded **batch** child.

A separate sufficient forward-error estimate is available if each ideal leaf
has norm at most K and its actual increment has uniform error at most u on
the whole trajectory: `E_N <= u sum_(j=0)^(N-1)(1+K)^j`.
This is the usual telescoping bound for the literal N shears, not a new
precision improvement. Preparation/coefficient errors, magnitude/overflow,
deterministic inverse recomputation and physical tape realization need their
own budgets before such a numerical implementation is admitted.

The favorable complete-call screen does not beat the dedicated batch's work;
its benefit requires a binding scratch cap or other separately demonstrated
hosting need. No such selected-supplier embedding is provided. The accepted
PR942 construction remains complex-bound on its stated moment endpoints;
this abstract output contract neither changes that profile nor removes any
selected invoice. All-size/compiler, physical frames/owners/common labels,
whole-call hosting, precision/tape and outer analytic obligations remain.
