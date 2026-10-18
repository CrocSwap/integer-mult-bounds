# Equality of row-table and direct matrix products

Fix a dimension d and binary row matrices A, B and C. Encode a row r by
its nonnegative integer with bit j equal to coordinate j. The direct
reference product computes row i of AB as the XOR of rows B[j] for each
set bit j in A[i]. `row_action` computes that same expression: each loop
iteration removes exactly the least significant set bit, and XORs its
corresponding matrix row. The loop terminates after popcount(r) iterations.

`prepare` computes AB for every ordered pair of distinct route indices.
It collects every row of those products in a finite sorted domain D.
For each right factor C and each row r in D it stores row_action(r,C).
Each reversed row list of AB is replaced by its indices in D. Thus every
lookup made by a reduced triple (a,b,c) is defined and equals the
corresponding row of (AB)C. No involution, route uniqueness, sparsity,
or expectation about the eventual relation histogram is used here.

Every output row is less than 2^d, since XOR preserves that range. Starting
with zero and appending the rows in reverse order by
`key = (key << d) | row` is exactly the reference encoding
sum(row[i] * 2^(d*i)). This encoding is injective on d-by-d binary
matrices. It has no truncated fingerprint or probabilistic equality test.
The unsigned integer array stores individual rows; the product key is an
arbitrary-precision Python integer, so its 289 bits are retained for d=17.

The domain a!=b and b!=c is unchanged. Each triple is inserted once, in the
same order as in the original census. Dictionary class membership therefore
agrees exactly. The class histogram, extraction of all pairs of distinct
words, reversal of the second triple and cyclic-reduction test are unchanged.
The returned total, histogram and relation-word set are consequently equal.
This includes duplicate matrices and classes of size greater than two.

Tables are created inside each census and discarded afterwards. No successful
validation is cached between invocations. The adapter checks all live source
pins before loading the predecessor from authenticated source bytes. It then
replaces only that new module's `relation_census` function. Original route
derivation, active/spectator checks, pair uniqueness, relation multiplication,
symmetry, all Fano incidence and labelling searches, and the planted/missing
relation controls run unchanged. The entire canonical receipt must equal the
pinned predecessor receipt byte for byte. Default predecessor commands and
all frozen source bytes are unchanged.

This is an algebraic equivalence argument for an implementation change,
supported by finite differential checks. It is not a proof-assistant theorem
or a formal proof of the multiplication bound. The original observation,
faithful representation and support-bound hypotheses remain inherited.

## Work and storage

For n routes, d rows and U distinct rows of the n(n-1) two-factor products,
preparation costs O(n^2 d^2 + n U d) bit-selection steps and O(n^2 d + n U)
stored row indices/actions. Product-key formation then uses d exact row
lookups per triple, instead of up to d^2 bit-selection steps plus packing.
The same n(n-1)^2 triples and all equality classes remain resident.

For the actual input n=112, d=17 and U=18,388. The 2,059,456 table values
occupy 8,237,824 payload bytes on the measured four-byte unsigned-int array
implementation. Pair/domain dictionaries and the unchanged class dictionary
add overhead. Peak process memory is measured separately; the payload count
alone is not a whole-process memory claim. The method does not make an
unbounded larger-word census feasible and adds no length-eight coverage.
