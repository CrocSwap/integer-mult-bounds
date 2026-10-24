# Five binary shared-header requests have 2,880 threshold headers

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: finite certificate with a scoped algebraic proof and explicit
counterexample.** For five corank-one requests I-U_t on F_2^6 with pairwise
orthogonal rank-one kernel projectors, exactly **2,880** complete GL_6(F_2)
headers pass every leading-principal-minor guard through rank five. Their
exact fraction is **1/6,999,552**.

This answers Open next question 1 of
[#4275](https://github.com/CrocSwap/integer-mult-bounds/pull/4275)
negatively. The proposed threshold pattern 2 k! would give only 240
headers at k = 5. There are 24 unordered five-rectangle decompositions of
J-I_5, rather than the two row-star and column-star decompositions. The
22 other subsets give 2,640 additional headers. Only the k = 5 case and
the counterexample to the all-k pattern are new claims.

[PROOF.md](PROOF.md) gives the exact header/decomposition bijection, proves
that zero and repeated rectangles cannot occur, and explains why the
finite enumeration is exhaustive. An explicit counterexample uses these
source and target support masks, with bit zero denoting coordinate one:

```text
(3,12), (6,17), (9,18), (20,10), (24,5).
```

Every support has size two. These rectangles partition the off-diagonal
cells, so this counterexample can also be checked by hand.

## Evidence and reproduction

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/binary-threshold-five-headers/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/binary-threshold-five-headers/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/binary-threshold-five-headers
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/binary-threshold-five-headers --check-source-history
```

Replace the interpreter path with another CPython 3.12 installation where
needed. The last command requires a publication commit with full history.

Expected marker: `PASS_BINARY_THRESHOLD_FIVE_HEADERS`. The verifier prints
the 24 decompositions, exact counts and fractions, the explicit witness
header, and a receipt bound to all six package-file hashes. It writes no
files. No receipt is handwritten or stored in this package.

The five-request census visits all 180 disjoint-support nonzero binary
rectangles, 16,110 pairs and 955,860 triples. Splitting each sorted
five-element set after its first two indices counts it exactly once.
The verifier completes all 24*120 decompositions to distinct full headers,
inverts them, conjugates every request by ordinary binary matrix
multiplication, and checks every full guard chain by no-pivot elimination.
This supplies 2,880 literal header checks without enumerating all
20,158,709,760 elements of GL_6.

The same new enumerator uses k = 3,4 as small positive controls. They give
12 and 48 headers, matching the cited predecessor observations. They are
not a separate audit deliverable. Five corruptions are rejected: a wrong
rectangle sum, a diagonal rectangle, the identity header's failing guard
chain, a header passing every first guard but failing a later guard, and
a singular header. The explicit nonstar witness must occur,
and a row/column-only enumeration demonstrably undercounts by a factor 12.
Checks use explicit exceptions and also run with Python optimization.

## Scope and credit

The partial-Gram reduction and minimal-dimension argument come from the
counting package produced by Nick Petalas in #4275. The new five-request
enumeration and counterexample answer its open question; no predecessor
code is imported or replayed. Exact Git blob and SHA256 provenance pins
for that proof and question are in [SOURCES.json](SOURCES.json), together
with the original card and selected record. There are no live external
proof inputs or third-party Python dependencies. Cinna Davis supplied the
BIT request context in #4100; source527, commdata2338 and Jose Manuel
retain the normalizer lineage credit.

The original card is `uniform-transfer-audit`, priority revision 7. Its
scope changes to original counting work, as recorded in [TASK.json](TASK.json).
The result addresses a shared-header counting question. A fully paid
producer/consumer protocol would still be needed to turn it into a
physical saving. The family expansion decision is to stop at this finite
result and leave larger classifications as open questions.

Only five orthogonal kernel lines over F_2 in dimension six, with a
complete equally weighted GL header domain, are counted. This gives no
all-k formula, odd-field count, restricted-header guarantee or
nonorthogonal classification. Physical header generation, selection,
emission, dispatch, dirty return, stock, precision and caller costs remain
unknown. There is no supplier admission, new kappa or selected-frontier
change. Independent human and formal proof-kernel review are unclaimed.
The selected cold replay, Lean and Docker were not run.

The verifier uses bounded loops, no recursion and functions below 60
physical lines. The largest subset traversal has 955,860 iterations; the
pair table has 16,110 entries before grouping, and at most 2,880 six-row
headers are retained. CPython dynamic integer/container allocation is a
managed-runtime deviation from fixed allocation, bounded by these finite
domains. Warnings are errors in both registered modes. No shared runtime
or repository-wide diagnostic configuration changes are needed.

## Open next questions

1. Classify the 24 five-request subsets structurally. This would explain
   the first failure of row/column rigidity rather than just count it.
   Start by grouping the emitted support pairs under coordinate
   permutations and transposition. No such orbit classification is
   claimed here.
2. Determine the threshold count at k >= 6, or a family of nonstar
   decompositions for general k. This would replace the refuted 2 k!
   pattern with a useful statement. Start by asking whether the displayed
   five-request partition extends when a coordinate is added. The larger
   census and an all-k argument remain unrun.
3. Find an actual producer whose orthogonal kernel family can use a paid
   shared header. Pin its request and charge selection, emission,
   dispatch, restoration and stock before treating density as a gain.
   No producer or complete physical invoice is supplied.
