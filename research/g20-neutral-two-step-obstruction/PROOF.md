# Exact two-step paid-query obstruction

## Proposition

Fix the final G20 word and route table of Ali Romman's #5708, as present at
canonical main `2485805a6d47f36ea83ddde6327d453ac82d44dc` and byte-pinned in
`SOURCES.json`. Choose any of the fourteen neutral longer A2 conjugations
identified in Nick Petalas's #6305 at
`9064cb7abc4d8cbdee1d5d8b04c2992b97547d1e`. Apply that rewrite. On the resulting
scalar word choose **any** syntactically valid second A2 interval, including
zero-contact commuting cancellation. Keep each correction at the contact's
original frame and use only the pinned single-edge routes.

Every such two-step path either fails route emission or has nonnegative
complete local paid-query moment change for every `0<t<1`. Among emitting
paths, the exact minimum is zero for every such exponent. There are 31,719
paths: 28,746 missing-route cases, 2,676 strict losses and 297 neutral cases.
These are rewrite paths, not a count of distinct final programs.

This is an exact finite certificate with a written sign proof. It answers the
immediate second-rewrite part of #6305's open question 1. Its first rewrite is
restricted to those fourteen longer neutral moves. Three or more rewrites,
the six shorter neutral first moves from #6290, other routes, changed
correction frames and changed productive targets are outside this proposition.

## Rewrite and endpoint identities

Remove `Q` and `ZERO_Q` events from the pinned word. This leaves 11,930 scalar
events on 685 roles. Let `G(a,b)` mean `x_a <- x_a + x_b` in characteristic two.
An interval has equal outer gates `G(a,b)`. Between them it has no `INIT` or
`ERASE` of either `a` or `b`, and no reversed gate `G(b,a)`.

Each noncommuting contact has exactly one of the following forms:

| Contact | Condition | Correction after contact |
|---|---|---|
| `G(b,s)` | `s != a` | `G(a,s)` |
| `G(d,a)` | `d != b` | `G(d,b)` |

Delete the two outer gates and append each correction at its contact's frame.
All other events retain their order and frame. This includes zero contacts,
when the operation is commuting cancellation. Direct elementary-matrix
multiplication gives `G C G = C R`, with `C` commuting with its correction `R`.
Noncontacts commute with `G`; destructive events on unrelated roles also do.
Since `G^2=I`, the entire replacement preserves the scalar transformation.
Composing two such replacements preserves arbitrary public and dirty input
columns. This algebraic identity is classical and inherited from #5708.

The verifier additionally propagates all 685 exact input-column coefficients
for each original first candidate and every second candidate. Rows are binary
integer masks. Owned erasure may affect only declared owned roles; INIT
requires a zero row. At return every owned row is zero, every other row is
its input basis row, and output roles 111 through 221 also contain input
roles 0 through 110 respectively. No payload sampling is used.

## Exhaustive coverage

The new enumerator indexes the positions of each ordered gate, each
destination, each source and each destructive event. For every ordered gate
pair `(a,b)` it visits every two increasing occurrences. Sorted index unions
and strict interior slices identify exactly the contacts, reversed gates and
barriers. Therefore it retains every legal interval, independent of its
length or number of contacts. It has no node or contact cutoff.

On the source word, requiring at least four contacts reproduces 1,503 legal
intervals. Exactly fourteen emit with the reference paid histogram. These
are the first-step domain and are reconstructed rather than supplied as an
unchecked list. On each resulting word, the same indexed algorithm permits
zero or more contacts. There are 31 zero-contact second intervals in the
complete 31,719-path domain. Second contact counts run from zero through 33
(not every intermediate count need occur).

`CERTIFICATE.json.gz` contains the complete canonical certificate. Each branch
stores the first interval `[left,right,a,b,contacts]`. Each outcome stores
`[left,right,a,b,contacts,missing_edge,delta]` relative to that branch's scalar
word. `missing_edge` is null exactly for successful emission; `delta` is null
exactly for failed emission. The full decompressed payload is regenerated
and compared byte for byte. Compressed container equality is not used.

An initial, separate interval-scanning implementation was used as an
exploratory cross-check; the deliverable enumerator uses the indexed method.
Both enumerations agree on every path, contact count, missing edge and signed
histogram. This is implementation cross-checking within the AI-assisted
contribution, not independent human or proof-kernel acceptance.

## Complete local paid accounting

At every nonzero-source ADD, move the destination and then the source to
that ADD's frame. A nonzero moved row incurs the published route rank.
A zero moved row still requires a published route, but incurs no paid query.
An uninitialized owned zero row may enter its first frame. A zero-source ADD
is omitted completely, including its frame visits. Every public role is
returned to its prescribed final frame; owned roles must be zero at return.
This is the row-sensitive contract in the pinned `construct.py`, which is
authenticated for provenance but never imported by the verifier.

The complete reference histogram is
`{1:1281,2:1338,3:58,4:57,5:102,6:10}`. Each successful second word has its
entire histogram reconstructed from start through return. No query is
subtracted merely because it was in a removed scalar interval. Missing-route
records give the first required ordered pair absent from the table; they
are rejections under this table, not geometric impossibility certificates.

Write `H_r=r^t`. The complete emitting classification is:

| New minus reference | Paths | Sign for `0<t<1` |
|---|---:|---|
| `2H1-H2` | 2,326 | Strict loss |
| `3H1+2H2` | 140 | Strict loss |
| `2H2-H4` | 70 | Strict loss |
| `2H1+H2+H3` | 56 | Strict loss |
| `H1+3H2` | 28 | Strict loss |
| `H1+2H2-H5` | 28 | Strict loss |
| `H1+H2+H4` | 14 | Strict loss |
| `H1+H3-H4` | 14 | Strict loss |
| `0` | 297 | Neutral |

For a positive-coefficient shape, the sign is immediate. Each other nonzero
shape replaces one rank `R` by at least two positive ranks summing to `R`.
Strict subadditivity `(u+v)^t<u^t+v^t` for `u,v>0` and `0<t<1`, iterated if
necessary, gives the strict sign. Hence the classification applies to the
entire exponent interval without floating-point samples or root searches.
The presence of 297 zero shapes establishes sharpness of the minimum.

## Stronger finite trace statement

For all fourteen first words and all 297 neutral second paths, the **ordered
paid-route sequence on each individual role** equals the source sequence.
This is stronger than histogram equality: every role retains the same ordered
triples `(origin_frame, target_frame, rank)` for its paid queries. Zero-row
transports and ordinary scalar events are not part of this paid trace.

`trace_audit.py` checks this finite statement without importing the primary
checker or any predecessor executable. It scans each named interval directly,
reconstructs the corrections, walks the whole scalar program, materializes
the per-role paid traces and compares them with the source. It also checks
the complete scalar endpoint. The decompressed full two-step certificate is
bound to SHA256 `b0d62e1faa9aaa7bdde5aac5b55b5d226272461238fa960cc0ad0df0b054bb47`
before it supplies the neutral subset. The audit supplies a separate replay
method for those paths, not independent enumeration of the whole domain.

The source, fourteen first words and neutral second successors contain 221
distinct scalar words, with lengths from 11,930 to 11,942. Their counts by
length and the exact reference-trace digest are in `TRACE-SUMMARY.json`.
Distinctness uses canonical exact event lists; no semantic quotient or
finite all-depth closure is inferred. Two actual toy programs with equal
endpoints and equal paid histograms but different per-role traces are
rejection controls: one swaps which roles visit two frames, and the other
reverses the frame-visit order. Thus the stronger predicate is tested beyond
the weaker histogram comparison.

## Exact limits

This is a statement about the paid-query component on a fixed source word.
The scalar endpoint and original productive boundary are retained, but no
global supplier caller, native address action, coefficient allowance,
stock/precision prescription, physical tape/storage bound or outer ledger is
newly admitted. Ordinary scalar work can change in a neutral rewrite; this
result is not an optimum for that work. No new κ is claimed. All five
selected assumptions remain: `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape` and `analytic_recovery`.

No theorem excludes an arbitrary sequence of neutral transformations. Long
neutral rewrites can increase scalar length, so finiteness of an all-depth
word graph does not follow from the finite two-step census. A missing route
does not prove that a new native route is impossible. These boundaries are
essential to the proposition.

## Attribution

Prepared for @CubeJerry with substantial OpenAI Codex assistance, Apache-2.0.
Nick Petalas supplied #6305's longer-contact census and neutral-neighbor
question; unpaidmoon supplied #6290's short-contact screen and question.
Ali Romman supplied #5708's word, A2 construction and row-sensitive emitter,
following Dugongue, ai-nanachi and the retained G20 native/controller/helper,
ordinary-cost and stock lineage. Those predecessors retain their credit.
