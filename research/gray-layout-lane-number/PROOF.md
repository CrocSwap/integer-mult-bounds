# Exact stable lanes for the reflected Gray layout

This scoped written proof was produced by Nick Petalas. It uses the classical
reflected Gray order and increasing-chain characterization of stable lanes.
No historical novelty is claimed for those general tools.

## Contract

There are N=2^n distinct records, initially in order 0,...,N-1, for n>=0.
Record IDs describe positions and do not restrict payloads. One stable-lane
pass splits the input into T ordered streams, then arbitrarily interleaves
those streams while preserving each stream's order. Every record enters
exactly one stream and leaves it exactly once. There are no copies, deletions,
or reversals within a stream. Empty streams are permitted.

Define g_n(x)=x XOR floor(x/2), and let G_n be its values in increasing x.
The requested output record order is G_n. The alternative convention that
record x moves to position g_n(x) has output order g_n^{-1}; it has the same
answer below. Lane selection and merge decisions depend only on positions.
Their physical preparation, storage, access and cleanup are not free costs
certified by this abstract contract.

Write F_0=0, F_1=1 and F_{j+2}=F_{j+1}+F_j.

**Theorem.** The exact one-pass lane requirement of G_n and its inverse is
F_{n+1}. Its longest increasing subsequence has length F_{n+2}, and its longest
decreasing subsequence has length F_{n+1}. Consequently any realization using
k stable-lane passes of capacities T_1,...,T_k must satisfy

    product_i T_i >= F_{n+1}.

For fixed T>=2, at least the smallest k with T^k>=F_{n+1} passes are necessary.
This statement does not assert that this lower bound is attainable in multiple
passes. The one-pass minimum is attained.

## Reflection gives both extremal subsequences

For n=0, G_0=(0), and both subsequence lengths are one. Directly from the
binary formula, with h=2^{n-1},

    G_n = G_{n-1} followed by h + reverse(G_{n-1}).        (1)

The n=1 identity is immediate. For n>=2, put x=h+y in the second half and
let z=h-1-y. In the low
n-1 bits, complementing y to z preserves adjacent-bit XORs and flips the top
low bit. These are exactly the low bits of g_n(h+y). Thus
g_n(h+y)=h+g_{n-1}(h-1-y), proving (1).

Let L_n and D_n be the longest increasing and decreasing lengths. Every value
in the first block of (1) is less than every value in the second block.
An increasing subsequence can concatenate independently optimal subsequences
of both blocks. Reversal interchanges increasing and decreasing lengths.
A decreasing subsequence cannot use both blocks. Therefore exactly

    L_n = L_{n-1} + D_{n-1},
    D_n = max(D_{n-1}, L_{n-1}).                         (2)

Starting at L_0=D_0=1, induction in (2) gives
L_n=F_{n+2} and D_n=F_{n+1}. The argument supplies both the upper bounds and
attaining subsequences, rather than just bounding the recurrence.

For any permutation, transposing the points (i,pi(i)) preserves increasing
subsequence lengths. A decreasing subsequence becomes another decreasing
subsequence after reversing its indexing order. Applying this twice proves
that a permutation and its inverse have equal L and D. This establishes the
alternative position-map convention.

## Stable lanes attain the decreasing-subsequence lower bound

Consider any output permutation pi of distinct initially increasing IDs.
Every stream in a stable-lane pass is increasing in those IDs. A decreasing
subsequence can take at most one record from each stream, so T>=D(pi).

For the converse, process pi in its output order. Label each record by the
length of a longest decreasing subsequence ending there. The labels lie in
1,...,D(pi). If an earlier record a and a later record b have the same label,
then a>b is impossible: a decreasing subsequence ending at a could extend
by b and increase b's label. Distinctness implies a<b. Each label class is
therefore increasing.

Assign that label to the record's input position. Split the original input
into those classes in input order. Merge by following pi's label sequence.
The next requested record is the next item in its stream because every
class is increasing. Every item is consumed once. This attains D(pi) lanes
and works for arbitrary payloads. In the verifier, patience sorting constructs
these labels, and a separate stream interpreter checks the literal split and
merge. The proof of attainability does not depend on that implementation.

Applying this fact to (2) proves the exact F_{n+1} lane requirement. For
example, n=16 needs exactly F_17=1597 one-pass lanes.

## Composition and its scope

Give each record the tuple of its lane choices in all k passes. Two records
with the same tuple preserve their relative order in the first pass and,
inductively, in every subsequent pass. Each tuple class is increasing in
original IDs at the final output. There are at most product_i T_i classes.
The decreasing-subsequence lower bound proves the displayed product bound.
This reasoning permits arbitrary position-dependent splits and merges and
does not assume consecutive lane ranges.

The Gray address map itself is a product of n-1 adjacent binary shears for
n>=1: for bit j from low to high, update x_j by XOR with the still-original
x_{j+1}. The resulting bit j is x_j XOR x_{j+1}. This small algebraic factor
count therefore does not bound one-pass stable-lane requirements by a constant
or by n. A physical implementation can use more passes, another memory model,
or additional channels. The theorem excludes none of those alternatives.

This is a layout-interface result. It does not establish a caller occurrence,
an unconditional multitape lower bound, a paid native operator, a supplier
admission, a new kappa or a complete multiplication theorem. All five selected
framework assumptions remain. Independent human and formal proof-kernel
review are unclaimed.
