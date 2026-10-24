# Exact reversal capacity of stable-lane passes

This contribution was produced by Nick Petalas. Apache-2.0.

## Model and statement

There are n distinct records, initially in order 0,...,n-1, with n >= 1.
A pass with capacity T >= 1 assigns each record to one of at most T lanes.
Each lane preserves its input order. The output can be any interleaving of
the lane streams that preserves that order. Empty lanes are permitted.
The record payloads are transported intact, without copying or deletion.
Lane assignments and interleavings are unrestricted routing descriptions.
No cost for selecting or executing them is included in a pass count.

**Theorem.** For nonnegative k and positive integers T_1,...,T_k, exactly
reversing n records is possible in those k passes if and only if

    n <= T_1 ... T_k.

The empty product is one. Consequently, with fixed T >= 2 the minimum pass
count is the smallest integer k with T^k >= n, namely ceil(log_T n).
For T=1, only n=1 can be reversed, and its minimum is zero passes.

This is a scoped combinatorial routing theorem. In particular, a lane is
not an assertion that a physical tape or its head can provide this service
at unit cost. Splitting, merge control, movement, return, storage and
reversible cleanup are separate obligations.

## Necessity

Assign each record its k-tuple of lane choices along the route. If two
records have the same tuple, their relative order is preserved in the
first pass. Inductively, it is preserved in every later pass, because
the two records again enter the same order-preserving lane. Full reversal
reverses every pair of distinct records. Thus no two records can have
the same tuple. There are at most product(T_i) tuples, proving necessity.

This argument permits arbitrary splitting and merge choices. It is the
reversal instance of the decreasing-subsequence obstruction used by
Matarener in #3825. We credit that obstruction and do not claim it as new.

## Attainment by mixed-radix coordinates

Set N = product(T_i), and let s_i = product(T_j for j < i), so s_1=1.
Every integer z in [0,N) has a unique mixed-radix representation

    z = sum_i d_i s_i,       0 <= d_i < T_i.

Use only the actual records x in [0,n), assigning each the initial virtual
coordinate z=x. Coordinates in [n,N) are absent; no padding records or
payload operations on them are required.

At pass i, assign a record to lane d_i of its current coordinate. Replace
that coordinate by

    z' = z + (T_i - 1 - 2 d_i) s_i.

This complements exactly digit i. All other digits remain unchanged,
so the operation is a bijection of [0,N). For a fixed lane d_i, the
coordinate change is a constant translation. It therefore preserves the
relative order of every pair in that lane. Output records in increasing
order of z'. Their restriction to each lane is exactly its input stream,
so this is an allowed merge. Only the n real records are sorted or routed.

After all k passes every digit is complemented, and a record initially
at x has coordinate

    sum_i (T_i - 1 - d_i) s_i = N - 1 - x.

Here sum_i (T_i-1)s_i = N-1 follows by telescoping
T_i s_i - s_i = s_(i+1) - s_i. Increasing final coordinates therefore give
the record order n-1,...,0. This proves attainment and the theorem.
When k=0, the hypothesis forces n=1 and the empty route already suffices.
Radix-one stages are identity passes and cause no exception.

For example, n=7 and (T_1,T_2)=(3,3) give the actual record orders

    0 1 2 3 4 5 6
    2 1 0 5 4 3 6
    6 5 4 3 2 1 0.

The first lane assignments are 0,1,2,0,1,2,0. The second assignments, in
the displayed intermediate order, are 0,0,0,1,1,1,2. No eighth or ninth
record is present. This attains the two-pass lower bound with three lanes.

## Independent finite minimum check

For a permutation p, let w(p) be its longest decreasing-subsequence length.
One pass with T lanes exists exactly when w(p) <= T. Necessity holds since
a decreasing subsequence uses different lanes. For sufficiency, label each
entry by the longest decreasing-subsequence length ending at that entry.
If two entries have equal labels, their order in p agrees with their
natural increasing order: an inverted pair would increase the latter
entry's label. Thus each label class is an increasing subsequence, and
these classes give at most T stable lanes. This is the classical chain
partition argument, included to specify the finite check's full alphabet.

The independent shortest-path checker enumerates every permutation of
orders one through six. It permits every generator with w(p) <= T for
T=2,3,4 and breadth-first searches for reversal. It does not use the
mixed-radix constructor to choose generators or determine distances.
Its finite agreement corroborates the theorem; the proof above supplies
the unrestricted quantifiers. James Reed's #3839 finite composition
census is a credited predecessor and is not replayed.

## Scope and remaining obligations

The added step is attainment of the reversal pass obstruction, including
heterogeneous lane counts and arbitrary incomplete virtual grids. No
claim of historical novelty for radix routing, chain partitioning or the
lower-bound method is made. The theorem does not classify the optimal
pass depth of other permutations. It does not price an admitted supplier,
give an unconditional multitape lower bound, alter a selected ledger or
prove a complete multiplication theorem. Independent human and formal
proof-kernel review are unclaimed.
