# Exact weighted all-pair tours

This proof and construction are produced by Nick Petalas. Apache-2.0.

## Boundary and permitted schedules

Fix an integer n >= 2 and positive real toggle prices c_1,...,c_n. All rows
are arbitrary elements of F2^L for any L >= 1. There is one anchor A, n
unchanged source rows B_i, and m_ij >= 1 independent dirty targets X_ij,k
for each unordered pair i<j. The required map preserves A and every B_i and
updates

    X_ij,k <- X_ij,k + A_initial + B_i + B_j.

The permitted gates are anchor toggles A <- A+B_i, at price c_i, and a
single write from A to each assigned target, at a fixed target-specific
price. A target may be written only when A contains its required parity.
There are no other gates. Target prices therefore add the same constant
F to every schedule. We optimize the transition bill. Any mask of the B_i
may be visited; visits and toggles may repeat; A must be restored. There
is no clean-state assumption and no restriction to weight-two intermediate
masks. In particular, this model is narrower than general CNOT synthesis.

Relabel the sources so that c_1 >= ... >= c_n > 0. Ties can be resolved
arbitrarily. The exact minimum transition cost is

    C = 2 c_1 + 2 sum_(i=2)^n (i-1)c_i.                 (1)

The proof permits real prices. The executable accepts exact rational prices
for 2 <= n <= 64 and emits the schedule without numerical rounding.

## Lower bound for every closed walk

Represent the anchor by its mask in F2^n. Toggling bit i has price c_i, so
the shortest distance between masks x,y is their weighted Hamming distance

    d(x,y) = sum_i c_i [x_i != y_i].

Take any legal closed walk from zero. List the N=binom(n,2) required pair
masks in the order of their first designated target visit. Shortcut the
segments between these visits, including the initial and final segments,
by shortest Hamming paths. The triangle inequality gives a tour through
this permutation with cost no greater than the original walk. Extra mask
visits and early visits without a target write do not affect this argument.
Thus it suffices to lower-bound every permutation p_1,...,p_N of the pairs,
with zero before and after it.

For each i let a_i count consecutive pairs p_t,p_(t+1) that both contain i.
Each pair containing i contributes c_i upon entry and c_i upon exit except
that two consecutive such pairs save 2c_i. There are n-1 pairs containing i,
so the shortcut tour costs exactly

    2(n-1) sum_i c_i - 2 sum_i c_i a_i.                (2)

This identity includes disjoint consecutive pairs and both zero endpoints.

For 1 <= k <= n let S_k={1,...,k}, and let V_k be the pair masks containing
at least one member of S_k. Their number is

    v_k = binom(n,2) - binom(n-k,2).

Draw the path with vertices p_1,...,p_N and its N-1 consecutive edges. The
edges counted by sum_(i<=k) a_i lie in the subgraph on V_k. No edge is
counted twice, since two distinct two-element sets share at most one
coordinate. A subgraph of a path is a forest. Since v_k >= 1, it has at
most v_k-1 edges. Hence

    A_k := sum_(i<=k) a_i <= v_k-1.                   (3)

Define b_1=n-2 and b_i=n-i for 2 <= i <= n. Direct summation gives
sum_(i<=k) b_i=v_k-1 for every k, including k=n. Put c_(n+1)=0.
Summation by parts and c_k-c_(k+1)>=0 give

    sum_i c_i a_i
      = sum_(k=1)^n (c_k-c_(k+1)) A_k
     <= sum_(k=1)^n (c_k-c_(k+1)) sum_(i<=k) b_i
      = sum_i c_i b_i.

Substituting into (2) yields (1). This is a bound on every original walk,
including those that repeat required masks or leave the weight-two layer.

## An attaining schedule

In sorted source order, visit pairs in this order:

    {1,n}, {1,n-1}, ..., {1,2},
    {2,n}, {2,n-1}, ..., {2,3},
    ...,
    {n-1,n}.

Use a shortest bit-toggle path between each consecutive pair, from zero to
the first pair, and from the last pair back to zero. At each designated
pair, write its anchor value once to each assigned target. The schedule
visits every pair exactly once as a designated visit. Intervening masks
need not be pairs.

The first row of pairs has n-2 adjacent edges sharing coordinate 1.
For i>=2, the row with first coordinate i has n-i-1 internal edges, when
that number is nonnegative, and one incoming edge from the preceding row.
Thus the consecutive-pair counts are exactly

    (a_1,...,a_n) = (n-2,n-2,n-3,...,1,0) = (b_1,...,b_n).

For n=2 there is one pair and no consecutive edge, giving (0,0) directly.
The lower bound is attained in all cases. Each target receives its
prescribed original-source parity. No B_i changes, and the final mask zero
restores the arbitrary initial A. This proves the full row map for every L.

## Unit-price example and cost limits

When every c_i=1, formula (1) is n(n-1)+2=2N+2. With t targets per pair,
the complete row ADD count is

    t N + n(n-1)+2.

For n=4,t=2 this is 12+14=26. A direct implementation uses three source
ADDs per target, totaling 36. Separately preparing each pair on the anchor
and restoring it costs four transitions per pair plus the same 12 target
writes, also 36. The constructed local improvement is ten row ADDs, with
all source restoration included. At row width L these are 26L versus 36L
bit XORs and 26 versus 36 source-row reads and destination updates. Tape head travel and
frame conversion are outside this aligned row-register tariff.

For prices (7,3,2,1), the exact transition optimum is 34. Independent
prepare/write/restore visits instead cost 2(n-1)sum_i c_i=78 in transitions.
Target prices are additional and identical in both schedules.

## Evidence and obligations

The written forest argument proves the quantified theorem. Independent
Held-Karp permutation optimization and literal hypercube-state Dijkstra
corroborate small rational/integer cases. Complete dirty-state enumeration,
full linear-map columns and wide-row executions corroborate the emitted
circuit. These finite computations do not substitute for the proof.

The general weighted metric and forest inequalities are elementary tools,
not claimed as new methods. The contribution is the exact optimum and
attaining dirty-source circuit in the specified repository interface.
No source-pinned multiplier caller, legal physical layout, native frame
schedule, recursive invoice, supplier admission or multiplication theorem
is supplied. No independent human or formal proof-kernel review is claimed.
