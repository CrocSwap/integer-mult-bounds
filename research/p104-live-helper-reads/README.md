# Actual-frame reads of unfinished P104 helpers retain the relay floor

Allowing **read-only access to every original G/Q/D helper at its actual
chronological frame** still requires at least **208 new monotone correction-helper
lifetimes** in the model below. This includes unfinished helper values whose
source projections lie outside the root code K. It resolves the actual-frame
version of the explicit next question in [PR2383](https://github.com/CrocSwap/integer-mult-bounds/pull/2383).

The number 208 and the original monotone-relay argument are predecessor results
of Philippe Van Velzen and Hiroki Kumazaki / [PR2353](https://github.com/CrocSwap/integer-mult-bounds/pull/2353).
commdata2338 / PR2383 proved the same floor with the whole root code supplied
freely at every frame, but excluded unfinished original G/Q/D rows outside K.
The new implication permits **all actual original helper reads** while keeping
the original word unchanged. It uses a new finite fact: none of the 72 original
G/Q/D helper paths ever visits any of the 104 target endpoint hyperplanes.

This is a written proof with exact finite premises, not a new correction
construction, a simultaneous-register lower bound, an excess-rank invoice,
a favorable completed moment, an admitted supplier or a new kappa. It does not
claim that arbitrary-frame access to the original helper rows is harmless.

## Exact model

The frozen input is PR1972's 4,058-event word retained in PR1991. It has
104 immutable logical sources X, 104 additive targets Y, 32 G helpers,
8 Q helpers, 32 D helpers, and 8 sequential private C lifetimes. Every original
event, value and frame path is retained. Additional correction operations may
read X, G, Q, D and active C, but **cannot write any of those registers**.
The source and original-helper read must occur at that register's actual cut
and frame. Original events preserve their order; arbitrary extra operations
may be inserted between them. Their reads do not change the original trace.

Targets accept additive writes only; they cannot be read, cleared or rescaled.
Every coefficient is an input-independent rational scalar. New helpers can mix,
copy, clear and relay at equal frames. Each new lifetime follows an increasing
binary-subspace path; discard/reinitialization starts another lifetime. Initial
source dependence can be in K, plus independent arbitrary dirt. Grant the whole
K freely at any frame and time. This last permission is favorable and already
belongs to PR2383's model. Dirty restoration is relaxed for the lower bound.

All added operations must use the logical common-frame contract. A physical
operation that mixes different charts requires another argument. Writing new
source information into the original word, changing its paths, introducing new
descending lifetimes, target feedback or arbitrary-frame read oracles is outside
the theorem. The unchanged original private descents are included, with their
actual source rows checked to be in K.

Let R have the doubled integer P104 root columns, in the frozen port order.
Then `R R^T = 104 I`, `G = R^T R/4`, and the additional correction is
`C = I - G/2`. For a binary frame V put

```
K = row_Q(R),
S(V) = {s : initial source label q_s lies in V},
U(V) = span_Q {e_s : s in S(V)}.
```

K and U are spaces of source coefficient rows. The independent source inputs
are not constrained to belong to either space.

## New finite evidence

The independent replay imports no pending predecessor executable. It reconstructs
the P104 roots, executes all 4,058 events over all 280 independent input columns,
and maintains a second representation `source_row = alpha R + local`. At each
changed non-target state and every initial state, it checks this exact equality
and that the local part is supported on S(actual frame). Values do not change
between these checks. The complete private copies are checked to lie in K before
descent; their source projections and independent Q dirt are retained separately.

| Check | Result |
| --- | --- |
| Original G/Q/D helper paths | 72 increasing paths |
| Distinct helper/register-frame pairs, including initial frames | 434 |
| Contacts with any of the 104 target endpoint hyperplanes | **0** |
| Explicit source-decomposition state checks | 2,458 |
| Original private lifetimes | 8, with exact code-valued source rows |
| Complete logical endpoint | original G/2 target map; all 72 dirty inputs restored |

An actual unfinished example occurs at **cut 593**, immediately after event 592:
`G25 = initial_G25 - 2 X1`, in `V = span(8,64,416)`, a proper subspace of Y2's
endpoint. Its source row `-2 e_1` is outside K, as the exact code-projection test
checks. It is nevertheless in U(V). Reading it at V is allowed by the new model;
transporting it freely to ZERO would supply information outside `K + U(ZERO)`
and is not allowed. The dirty term has not been removed by this example.

[RESULT.json](RESULT.json) contains all 72 frame paths, the private rows,
this example, a digest of all source-decomposition certificates, and the
104 target witnesses. [verify.py](verify.py) regenerates every proof-relevant
field from the two frozen JSON inputs and compares the complete canonical payload.

For completeness, the replay also independently checks PR2383's inherited
finite premises: each target endpoint H is a distinct dimension-eight subspace;
`supp(C_t) = S(H)` has size 48; no original source path visits H; and after
granting every possible earlier target-frame contribution, the still-required
labels span H. Eight outside-root columns with nonzero integer determinant
certify `K intersect U(H) = {0}`. These numerical premises and the 208 floor
are credited to their predecessors, not presented as new discoveries.

## Proof

**1. The original read-only word supplies only `K + U(V)` at frame V.**
Initially sources have row e_s at a frame containing q_s; all independent
dirty helpers have zero source projection. Equal-frame additions preserve
the invariant. Every nonprivate original transport increases its frame, so
it preserves the invariant. Each of the eight private copies has a source
row in K before its descent, checked directly over all 104 source columns;
it therefore satisfies the invariant even at the smaller frame. Private
values remain unchanged until discard. This proves the claim at every
original cut, including unfinished captures outside K. The second representation
in the replay checks the induction's exact source binding and excludes accidental
use of a different word or a contaminated private copy.

**2. New helpers obey the same invariant even when reading original helpers.**
At a read from an unchanged original register at frame V, step 1 supplies
an element of `K + U(V)`. This is the new case missing from PR2383's proof.
Initial K dependence, source reads, free code inputs, equal-frame mixing and
increasing new transports preserve the invariant exactly as before. Arbitrary
finite new-helper relay networks, rational cancellation and feedback among
new helpers are permitted. Reads do not modify the original word, so there
is no circular assumption about its future source rows.

**3. Each target still needs at least two new proper-frame arrivals.**
Fix endpoint H. Since `K intersect U(H) = {0}`, every row in `K + U(H)` has
a unique U(H) component. For V contained in H this local component is supported
on S(V). Let E contain all source labels that lie in any proper earlier frame
of this target; grant their contributions for free. The required labels
`N = supp(C_t) minus E` span H by the finite witnesses.

At H, no original source or G/Q/D helper is present: the new path-avoidance
certificate is essential here. An original C read, if available, supplies only
K, as does the free code oracle. A new helper born at H also starts with source
dependence in K. Thus nonzero local information at H can enter only through
a new helper that transports there from some proper subspace V of H.
Mixing at H cannot create missing local support. An increasing lifetime cannot
leave H and return.

If at most one new lifetime entered H, all correction contributions would lie
in `K + span{e_s : s in E} + U(V)` for a single proper V (or no V).
The required correction C_t and the latter two spaces lie in U(H), so
injectivity removes the K component. Consequently every label in N would lie
in V. This contradicts their binary span H, since dim V is at most seven.

**4. The count is 208 distinct new lifetimes.** Distinct dimension-eight
target endpoints are incomparable. One increasing new lifetime can enter at
most one of them. Two per endpoint therefore require at least `2*104 = 208`.
The original 72 helpers are not counted as new lifetimes; step 3 explains why
their additional read permission cannot replace one of the required arrivals.

The argument is about source projections, so allowing arbitrary dirty state
and even relaxing restoration cannot invalidate the lower bound. Finite replay
certifies the pinned geometry and word premises. The written induction proves
the arbitrary-length implication; no enumeration of every correction network
or proof-assistant verification is claimed.

## Reproduction and controls

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -B research/p104-live-helper-reads/verify.py
python3 -I -O -B research/p104-live-helper-reads/verify.py
python3 -I -O -B research/p104-live-helper-reads/test_verify.py
python3 scripts/research_package.py --package research/p104-live-helper-reads
```

Expected marker:
`PASS_P104_LIVE_HELPER_READS original_helpers=72 endpoint_contacts=0 lifetimes=208 controls=8 no_new_kappa`.
Default replay is read-only and Git/network independent. Exact source hashes
are checked before parsing the inputs. The optional `--out NEW.json` writes
a verified receipt exclusively to a new path.

Eight controls cover a wrong transport rank, missing query compensation,
missing dirty cleanup, the actual outside-K but frame-admissible example,
illegal arbitrary-frame access, a changed target creating an original-helper
endpoint contact, a zero-arrival countermodel with the correction row freely
supplied at the endpoint, and invertible code-basis changes for all 104 minors.
The exported-package tests exercise changed/missing sources, receipt drift,
duplicate JSON keys, and a read-only Git-free replay. The scope remains the
finite logical word: no native phase replay, physical scalar lowering, complete
moment, stock reserve, recursive precision, tape or all-size supplier is checked.

## Open next questions

The unchanged original paths have now been tested with all their read-only
helper information. A further escape must change another premise. Can one
original helper visit a target endpoint while preserving its required captures,
query availability and cleanup? First select the helper and endpoint, derive
the new path and price the extra transports; merely re-reading its current
unfinished row is insufficient.

Alternatively, can a new update before an original private descent carry
useful information outside K? Specify the exact source row and legal read
chronology first, then test dirt restoration and a favorable completed bill.
This changes the read-only contract and is not ruled out here. Structured
versions and blockers are in [TASK.json](TASK.json).

## Provenance and credit

Main base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
The task card is explicitly changed from full correction construction to
the concrete PR2383 missing implication. Exact predecessor heads, README blobs
and SHA256s are in [PREDECESSORS.json](PREDECESSORS.json); those documents are
context, not imported code. [SOURCES.json](SOURCES.json) pins the two main-branch
scientific inputs and selected/task provenance. The selected frontier and all
frozen files remain unchanged.

Credit Philippe Van Velzen for the original geometric screen; Hiroki Kumazaki
for PR2353's relay proof; commdata2338 for PR2383's quotient proof and explicit
unfinished-helper handoff; Rohan Arun / PR1972 for the word; Chafik Boukhalfa /
PR1991 for its retained native realization; Adam Gall / PR1940 for the schedule;
Josie Elliston / PR1071 for the fixture; Ali Romman / PR1125 and the retained
geometry/compiler lineage. The new proof extends, and relies on, those ideas.

Prepared for **ywz65**, with substantial OpenAI Codex assistance in derivation,
implementation, checking and writing. Apache-2.0. No independent human review,
formal proof assistant or selected supplier cold replay is claimed.
