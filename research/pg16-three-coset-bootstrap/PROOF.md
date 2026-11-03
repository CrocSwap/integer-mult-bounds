# Exact minimum in eight three-coset queue families

This scoped finite proof and its checkers were produced by Nick Petalas.

## Input and question

Use the fixed graph in Sudarsh Chaturvedi / Sudarsh3301's PR2956,
`research/pg16m-bootstrap-orders/graph16_59.txt`. Its SHA256 is
`6a12ff61f721449228957ea9ab691536fbaa24f45c30bdf3a8fcbf8655f36a6e`.
This is the sole live external input. The interpretation as the Singer
incidence graph PG(2,16) minus an invariant matching is inherited from that
package and Philippe Van Velzen's limits-1/limits-2. We do not reprove that
interpretation or replay either predecessor's scientific checker.

There are 273 points P_i and 273 lines L_i, indexed modulo 273. P_i has
neighbors L_(i+d), for

    d in {39,78,83,89,91,118,125,156,166,178,181,182,199,227,236,250}.

Every vertex has degree 16. For a permutation sigma of all 546 vertices,
let j_v be the number of neighbors earlier than v. Define

    C(sigma) = sum_v max(0, 8-j_v).

This is the bootstrap order objective of the cited source. Its global
minimum and back-arc flow feasibility are separate questions.

For r in {0,1,2} and t in {0,...,90}, put

    p(r,t) = 118(3t+r) modulo 273,
    l(r,t) = p(r,t)+81 modulo 273.

For a phase mask b in {0,...,7}, queue Q_r is the concatenation, in increasing
t, of (P_p(r,t),L_l(r,t)) when bit r of b is zero, and
(L_l(r,t),P_p(r,t)) when that bit is one. Each queue has 182 vertices.
The three queues partition the graph. The point indices form the three
cosets of the index-three subgroup of Z/273Z. The line cosets are translated
by 81.

Let F_b be every stable merge of Q_0,Q_1,Q_2. No order relation is imposed
between different queues. Thus points and lines may each leave the native
cyclic order. PR2956 fixes the entire cyclic point order and cyclic line
order separately. For example, draining Q_0 first starts its point order
with 0,81, whose difference is a nonunit modulo 273. Such an order cannot
be one of that source's unit-multiplier cyclic point sequences. The two
families overlap, and neither full domain is asserted to contain the other.

## New finite theorem

For each b in {0,...,7},

    min_(sigma in F_b) C(sigma) = 784.

Consequently this specified three-coset continuation cannot reach cost 783,
or the imported code dimension 772. This is a scoped finite obstruction,
not a lower bound of 784 on unrestricted Boot. In particular it does not
exclude orders outside these queues, independently reordered points and
lines, other multipliers or offsets, other graph sizes, or changed callers.

## Complete recurrence and coverage proof

A state x=(i,j,k), with 0<=i,j,k<=182, is the union of those three queue
prefixes. Write S(x) for that vertex set. It depends only on x, regardless
of the earlier merge choices. There is one arc x -> x+e_a whenever queue
a is not exhausted. Its appended vertex is v=Q_a[x_a], and its cost is

    w(x,a) = max(0, 8 - |neighbors(v) intersect S(x)|).

Stable merges and monotone paths from (0,0,0) to (182,182,182) are in
bijection: read the chosen queue at each step, or recover it from the next
vertex of a merge. Summing arc costs gives exactly C(sigma), because the
prefix S(x) is precisely the set earlier than each appended vertex.

Define d(0,0,0)=0. At every other state y, set

    d(y) = min_(a with y_a>0) [d(y-e_a) + w(y-e_a,a)].

Induction on i+j+k proves that d(y) is the least cost of every path ending
at y. All admissible last queues occur in this minimum. Thus no candidate
order is omitted by using prefixes instead of enumerating full words.
Lexicographic increasing i,j,k is a valid evaluation order, since every
predecessor is already available. A minimizing predecessor supplies a literal
attaining order. This proves both directions of the finite certificate.

Each phase has 183^3 = 6,128,487 states and
3*182*183^2 = 18,284,994 arcs. The eight complete passes cover
49,027,896 states and 146,279,952 arcs, counted with their phase. These are
state/arc counts, not counts of literal full orders individually enumerated.
The implementation evaluates all incoming arcs at every nonorigin state.

`verify.py` evaluates this entire recurrence in integers, obtains 784 at
all eight terminal states, traces eight tight paths, and independently
recounts their costs from earlier-neighbor membership. It also verifies
that every emitted order is a full permutation and respects its queues.
`--orders` emits the complete eight witnesses. The certificate is executable;
there is no handwritten saved success receipt or opaque solver result.

All prefix counts lie in [0,16]. Every distance is at most 8*546=4368,
since a path has at most 546 arcs each costing at most eight. The unsigned
16-bit table and sentinel 65535 therefore cannot overflow on a reachable
state. Every state is reachable by some merge, so no sentinel enters a
candidate sum. The maximum-distance check and literal traceback guard the
implementation of these facts.

## Separate reverse-order corroboration

The second program imports no primary code. It constructs queue memberships
and neighbor prefix counts by vertex positions instead of the primary's
membership scan. It reverses every queue, then uses a separately written
rolling-slice recurrence, retaining only two 183-by-183 distance slices.

For any complete order on a 16-regular graph, sum_v j_v=|E|=8*546. Hence

    sum_v max(0,8-j_v) = sum_v max(0,j_v-8).

Reversing an order replaces j_v by 16-j_v. Its cost is unchanged. Reversal
is a bijection between merges of the original queues and merges of the
reversed queues. Therefore the reverse-queue optimum equals the original
optimum for each phase. `independent.py` also returns eight values of 784.
This is a separate implementation by the same contributor, not independent
human review or formal proof-kernel verification.

## Verification controls and limits

The primary compares the recurrence and traceback against every literal
queue-label shuffle in forty small regular-graph/phase domains. Three invalid
optimizer contracts are rejected before allocation. The separate checker
recounts the reversal identity on three complete literal orders.
These controls test the new optimizer rather than replay predecessor results.
The runtime checks remain enabled under optimized Python.

No global Boot lower bound, back-arc transportation, schedulability, actual
Hermitian code dimension, native implementation, restored physical caller,
complete supplier invoice, compiler, precision/tape or multiplication theorem
is established. All five selected framework assumptions remain. No selected
cold replay, Lean or Docker build was run. Classical dynamic programming,
regular-graph reversal and the predecessor's objective retain their credit.
