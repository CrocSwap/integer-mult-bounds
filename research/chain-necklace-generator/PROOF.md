# Direct generation of valid cyclic chain schedules

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and contribution

Use SHIN09-git's [PR6080](https://github.com/CrocSwap/integer-mult-bounds/pull/6080)
depth-three contract. A word has `m` copies of each of the letters `1,2,3`.
Write `A,B,T` for its scattered subsequence counts `12,23,123`. It is valid
for target `c` when `A=B=0` and `T=c` modulo `m`. In the four-role dirty chain,
these are the complete endpoint conditions, with arbitrary compatible maps
and arbitrary initial data. This endpoint characterization and its rotation
invariance are cited predecessor results. We do not audit or extend them.

We construct exactly the lexicographically smallest word in each valid
rotation class. The new step is a suffix-residue completion test joined to
classical fixed-content necklace generation. The written construction works
for every positive integer `m`. The supplied bounded implementation accepts
only `1<=m<=5`, and `0<=c<m`. At `m=1` this is the predecessor's auxiliary
combinatorial convention, not a ring of characteristic one.

The source's 356 classes at `(m,c)=(5,1)` are credited data. The contribution
is their direct generation, the safe pruning proof, and the complete work
comparison, rather than a new class count. No constant amortized time bound
or improvement of a multiplication exponent is claimed.

## Exact suffix table

For each count vector `r=(r1,r2,r3)` with `0<=ri<=m`, let `D[r]` contain the
triples `(A,B,T)` modulo `m` attained by words with that exact count vector.
Initialize `D[0,0,0]={(0,0,0)}`. Process count vectors in lexicographic order.
For each positive coordinate, append its letter to every state in the cell
with that coordinate decremented. On a predecessor count vector `(a,b,d)`,
the append rules are

```text
append 1: (A,B,T) -> (A,B,T),
append 2: (A,B,T) -> (A+a,B,T),
append 3: (A,B,T) -> (A,B+b,T+A).
```

Reduce each coordinate modulo `m` and take a set union. Every nonempty word
has exactly one last letter. Induction on length therefore proves equality
with the defined `D[r]`, including both existence and exhaustiveness. Every
predecessor cell precedes its successor in the chosen order.

There are `(m+1)^3` cells and at most `m^3` states per cell. There are at most
`3*m^3*(m+1)^3` state transitions. Thus preprocessing needs `O(m^6)` residue
operations and state storage. This is an arithmetic/state bound, not a
worst-case claim about the runtime of a language's hash table.

## Necessary and sufficient completion test

Let a prefix have counts `(a,b,d)` and residues `(A,B,T)`. Its suffix must
have counts `r=(m-a,m-b,m-d)`. Let `(u,v,w)` be the suffix's residues. Split
each counted subsequence at the concatenation boundary. Exactly

```text
A_total = A + u + a*r2,
B_total = B + v + b*r3,
T_total = T + w + A*r3 + a*v.
```

The triple count has four possibilities: all in the prefix, all in the
suffix, its first two letters in the prefix, or only its first letter in
the prefix. No commuting-map assumption enters these integer identities.

Consequently define, modulo `m`,

```text
u0 = -A-a*r2,
v0 = -B-b*r3,
w0 = c-T-A*r3-a*v0.
```

A balanced valid completion exists if and only if `(u0,v0,w0)` belongs to
`D[r]`. Necessity follows by substitution. For sufficiency, the exact table
supplies a suffix word with these residues, and the three concatenation
identities prove validity. This is a completion test among unrestricted
suffix words. It need not certify that a completion is a canonical necklace.
Its use as a rejection test is nevertheless exact and safe.

## Canonical traversal and safe pruning

We use the classical prenecklace extension theorem, not a new necklace
algorithm. A prenecklace is a prefix of a lexicographically least rotation.
Track the length `p` of its longest Lyndon prefix. At the next one-based
position `t`, the permissible symbols are at least `word[t-p]`. Equality
retains `p`; a larger symbol replaces `p` by `t`. At length `n`, such a
prenecklace is a necklace exactly when `p` divides `n`. See Sawada,
[A fast algorithm to generate necklaces with fixed content](https://www.socs.uoguelph.ca/~sawada/papers/alph.pdf),
Theorem 1 and Figure 1, following Fredricksen, Kessler, Maiorana and Ruskey's
necklace-generation lineage. We use the simple extension rule, not Sawada's
constant-amortized-time refinement.

Start with letter `1`, since every balanced necklace contains that least
letter and begins with it. Extend only when the letter count remains at
most `m`. Update the prefix residues and apply the suffix test above.
Reject a prefix only when the test fails. At length `3m`, emit only if
`p` divides `3m`. Use a depth-first explicit stack, exploring the smaller
symbol first.

Every emitted word has the required counts and residues, by the completion
test with an empty suffix. The cited extension theorem makes it canonical.
Conversely, take any valid necklace. Every prefix obeys the extension rule
and count bound. Its actual remaining suffix witnesses table membership,
so no prefix is pruned. Its terminal period divides `3m`, so it is emitted.
Different traversal paths have different words. This proves completeness
and uniqueness, including periodic necklaces. It also gives lexicographic
output order without rotation canonicalization.

The stack has depth at most `3m` and at most `1+6m` pending nodes. Stored
prefix tuples occupy `O(m^2)` space. The result list adds output storage.
The implementation bounds popped nodes by the full ternary-tree size
`(3^(3m+1)-1)/2`; its input cap makes this bound explicit. No output-sensitive
or polynomial total-time theorem is asserted for the traversal.

## First working example and exact comparison

At `(5,1)` the complete suffix table has 216 cells and 9,438 states. Building
it performs 20,912 state transitions. Canonical traversal pops 3,888 nodes,
tries 9,266 symbols, performs 7,007 prefix transitions and 7,007 completion
lookups, rejects 3,120 prefixes, and tests 520 full prenecklaces. The period
test emits 356 words. It performs no rotation tests. All these counts include
the whole table, including cells not subsequently queried.

The separate literal method enumerates all 756,756 balanced words, performs
3,783,780 middle-letter scans, finds 5,340 valid words and canonicalizes
them using 80,100 rotations. Each middle-letter scan computes the numbers
of preceding `1`s and following `3`s. Their product contributes to `T`.
Its set of canonical words agrees exactly with the generator's output.

These counters measure named algorithmic operations. They do not pretend
that a table transition, Python tuple copy, set lookup and integer comparison
have identical cost. `benchmark.py` separately times five alternating calls
to the complete two implementations in fresh child processes. Timed regions
include startup, imports, table construction or literal enumeration,
canonicalization when applicable, JSON serialization of every output word,
and process exit. The parent checks complete returned sets after each pair,
outside timing.

## Scope and credit

This is a scoped constructive proof, exact finite conformance certificate
and local algorithm comparison. It adds no new cyclic-class formula, chain
existence theorem, or generally new necklace method. SHIN09-git supplies
the source question, cyclic contract and period conventions. Nick Petalas's
#6037/#4257/#4281/#4748 supply the credited count/endpoint/rotation background;
their programs and counts are not used to generate the new output. Ross
Richardson's #943/#934 retain the complete-call dirty-chain lineage. The
classical substring-count and dynamic-programming ingredients retain their
usual attribution. Exact source prose pins are in SOURCES.json.

Rotation equivalence does not preserve every physical routing or precision
cost. Native realization, physical selection, ownership, dirty restoration,
precision, tape movement, stock, compiler admission and the full supplier
bill remain separate obligations. No selected assumption, complete
multiplication theorem or new kappa follows. Independent human and formal
proof-kernel review are unclaimed.
