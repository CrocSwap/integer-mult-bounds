# Exact persistent stock for minimum-query streams

This contribution was produced by Nick Petalas. Apache-2.0.

For a fixed chronological list of common-query requests, let V_i and W_i
be the scalar row spans of past and future requests at cut i. Put
r=rank(all requests). The exact minimum persistent cache, among protocols
using the minimum r acquisitions, is

```text
b = max_i dim(V_i intersect W_i)
  = max_i (rank(V_i) + rank(W_i) - r).
```

One causal program attains every cut lower bound simultaneously. The
[proof](PROOF.md) allows arbitrary linear cache encodings and legal prefetch
in the lower bound. The upper construction only queries the current
request. [compile.py](compile.py) emits individual scalar ADD, nonzero
SCALE, SWAP and owned CLEAR instructions using b cache fields plus one
response/work field. No second conversion bank is hidden.

Claim type: scoped written proof with exact finite corroboration and a
bounded constructive compiler. This is a new matching stock lower bound
and compiler for the common-query observational interface. Dugongue's
[#5803](https://github.com/CrocSwap/integer-mult-bounds/pull/5803), scheduling
S12-S13, supplies the causal query-basis and one-cut intersection
compression constructions. Those are cited predecessors, not audit targets.
The rank identity and represented-matroid connectivity function are
classical. No claim of worldwide novelty for those ingredients is made.

For example, request e_1,...,e_n and then their sum. Exactly n acquisitions
and one persistent field suffice for every n>=1. Retaining the individually
acquired answers until their last use would use n persistent fields.
This construction changes the retained values. It does not merely reassign
fixed lifetimes to fewer slots.

## Exact boundary

Sources are immutable and arbitrary. Every request is an ordinary scalar
row on that source bank, available at its request time. Answers are
observational outputs, delivered in order and inaccessible after delivery.
All query-dependent state crossing a cut counts toward the cache. A copy
kept by the responder counts too. Ordinary and queried coefficients must
be formally distinguishable. A scalar Q is outside the lower bound.

Queries take only ordinary source combinations. Query feedback,
non-scalar ordinary operator algebras, source mutations, consumer feedback,
different charts and read-access to past outputs have different contracts.
Owned erasure is permitted and charged. Original sources and arbitrary
dirty spectators are preserved. This is not a dirty-return-only workspace
construction. The exact result concerns persistent stock at delivery cuts;
b+1 is an upper bound on total temporary payload fields, not a claimed
minimum for every microstep.

An installation must pay all ordinary instructions, current-source
assembly, initial scrubs, delivery, routing, coefficients, descriptors,
clears and physical access. With h=b+1, the proof gives an ordinary scalar
instruction bound h+m(2h^2+2h+b+1), separately from the r acquisitions.
General field elimination does not automatically give dyadic scalar
recipes. No selected supplier region is installed or repriced here.
No new kappa, selected-frontier change or full multiplication theorem is
claimed. The five selected framework assumptions remain.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/causal-query-cache-stock/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/causal-query-cache-stock/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/causal-query-cache-stock
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/causal-query-cache-stock --check-source-history
```

Another CPython 3.12 may replace the absolute interpreter path. The direct
verifier emits `PASS_CAUSAL_QUERY_CACHE_STOCK` in a generated JSON receipt
bound to SHA256 hashes of all package files. It writes nothing. Registered
replay also prints `PASS_REGISTERED_RESEARCH_PACKAGE`; publication checking
prints `PASS_RESEARCH_COMMIT_BYTES`. No receipt is hand-authored or trusted
as an input. Redirect output into a scratch directory if a saved receipt
is wanted.

The compiler accepts a JSON object with exactly `prime`, `dimension` and
`rows`. Its executable domain is at most 24 requests on 1..8 sources over
F_2, F_3, F_5, F_7 or F_11, with canonical integer residue entries. Empty
streams and zero rows are accepted. For example:

```json
{"prime": 3, "dimension": 2, "rows": [[1,0], [0,1], [1,1]]}
```

Save that object outside the checkout and run:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -B research/causal-query-cache-stock/compile.py /absolute/path/problem.json
```

The result has two acquisitions, persistent width one and a two-field bank.
Its cuts, acquisition decisions and literal ordinary instructions are
included. Compilation chooses a basis from the supplied coefficient rows;
it is offline metadata work, not a free physical source observer.

## Evidence

The independent finite-state oracle enumerates every subspace as a subset
of its finite vector space and tests additive closure. For each capacity,
it tries every available retained subspace and minimizes acquisition count.
It uses no elimination or intersection routine from the compiler.
The complete domains, including zero rows and empty streams, are:

| Field and source dimension | Maximum request length | Streams | Subspaces |
| --- | ---: | ---: | ---: |
| F_2, dimension 2 | 6 | 5,461 | 5 |
| F_2, dimension 3 | 4 | 4,681 | 16 |
| F_3, dimension 2 | 4 | 7,381 | 6 |

All 17,523 oracle optima match the emitted persistent width and minimum
query count. Literal instruction replay checks every delivered formal
answer, each retained basis, entry scrubbing, exit zero and two independent
dirty spectators. Separate complete matrix tests check all 2-by-2 matrices
over F_2,F_3,F_5 and all 3-by-3 matrices over F_2, totaling 1,234 matrices.
Forty running-sum family cases cover all five supported fields and source
dimensions 1..8. Six boundary cases exercise the full 24-request and
nine-field-bank limits, including rank zero.

Twenty-one rejection controls cover invalid domains, deleted acquisition,
missing entry scrub, false query count, destroyed output, a spectator
address, changed cache basis, aliased ADD, zero SCALE, Boolean address and
unknown instruction. The finite oracle restricts acquisitions to the
current request; the written lower proof additionally permits legal
prefetch. Neither finite enumeration nor Python execution proves all-size
physical implementation or formal-kernel acceptance.

## Verification scope and code constraints

Scientific base is canonical main
e54523517d0f03e58352e647c403a5af3e525a57, priority revision 8, with selected
conditional kappa 0.00363005817 from #7000. The first baseline example passed
as source-binding orientation only. [SOURCES.json](SOURCES.json) pins the
selected record, catalogue, priorities and the two predecessor prose files
as historical provenance. No predecessor mathematical suite is imported or
replayed. [TASK.json](TASK.json) records the changed card scope and
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19539387).

The original caller/native acceptance gate remains unmet. Native operators,
matched physical ABIs, supported scalar recipes, owned erasure, compiler,
precision/tape, stock and analytic recovery require a separate installation.
Selected cold replay, Lean, Docker, supplier admission, independent human
review and proof-kernel review are unrun and unclaimed.

New code is nonrecursive and functions are shorter than 60 lines. Compiler
inputs bound requests by 24 and source dimension by eight; derived matrices
have at most sixteen unknowns or nine bank rows. Finite oracle spaces have
at most nine elements, so it enumerates at most 512 subsets. All failures
use explicit exceptions that remain active under optimization.

Power of Ten rule 3 has a managed-runtime deviation: Python allocates
lists, dictionaries and integers during these bounded computations.
Streams are checked one at a time and only a digest and counts persist.
Rule 8/9 has a fixed-source loading deviation: the verifier executes only
the package-local compile.py through runpy, with a fixed finite callable
set. No external source or input-provided code is loaded. Warning-strict
normal/optimized replay, in-memory syntax parsing and whitespace checks
supply the available diagnostics. No new external dependency or shared
configuration is introduced.

## Open next questions

1. Does an actual common-ABI source request stream have a smaller b than
   its retained-answer bank? Export its literal immutable source rows and
   delivery cuts first, then price every coefficient conversion, route and
   clear. The missing blocker is an installed physical request stream.
2. What is the exact stock versus reacquisition tradeoff when more than r
   queries are allowed? Start with an independently enumerated small stream
   where capacity b-1 needs additional queries. The theorem fixes the
   minimum query count and supplies no global tradeoff formula.

## Credit

Credit David Ganz / Dugongue and #5803 S12-S13 for causal basis acquisition
and sufficient future-demand intersection compression. Retain that
package's credit to Ali Romman, ToikY, zxv, Cinna Davis, Cao Yifan,
Ryanson Jonathan, Jacob Alan Sussman and the native/ownership/compiler
lineage. Classical span, dimension and Gaussian-elimination methods are
not claimed as new. The matching lower bound, scoped synthesis and finite
checks were produced by Nick Petalas. Predecessor files are unchanged.
