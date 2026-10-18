# A coherent triple escapes the pair-stationary k8 gauge

**Finite scalar construction and exact restricted search closure; no new κ.**
PR1310 leaves the question whether three coupled helper changes can improve its
pair-stationary vector. One common shift does: decrease the exponents of
**L354, L469 and L478 by one** in the forward word (increase them in reverse).
It saves two real-component primitives, then unlocks another two by decreasing
L257 by one. The complete complex saving is **eight primitives per orientation**
beyond PR1310, including every entry/exit scale and coefficient-work operation.

| Complete complex primitive bill | Forward | Backward |
|---|---:|---:|
| Selected-at-base PR1094 | 149,002 | 149,018 |
| PR1310 pair-stationary vector | 135,996 | 136,012 |
| This finite candidate | **135,988** | **136,004** |

The principal evidence is the complete restricted census, rather than the small
saving. Of all **2,190,670 three-helper subsets** of the same 237 eligible
helpers, **exactly one** improves PR1310 under any common integer shift. After
the two strict moves, none improves, and neither does a singleton or a pair
under a common shift. This does **not** cover three independently chosen shifts,
nor prove global optimality. We do not assert that the final vector remains
stationary against the larger arbitrary two-coordinate class of PR1310.

The recursive paid profile remains `{1:2412,2:418,3:432,4:142,5:82,8:8}` per
invocation. Every nonscalar event and its order is unchanged. No new κ,
native/hosted integration or full multiplication theorem follows.

## Scope and complete cost

Sources: PR1310 at `b9ca10f02fca37c8214d880c244ac14ead6bae7a`, PR1263 at
`5fbaca13028846bddbb001e8e07addc2ab8e5816`, PR1214 at
`26162c56ec9c50a80e49949f36d4dd9a137a76a6`, and PR1161 at
`d210969d3158a1e6c505e41f67dd84e555c88564`. These are pending predecessor results,
not newly accepted selected frontiers. Retained used sources are byte-identical;
`PREDECESSORS.json` records their hashes and `SOURCES.json` pins live dependencies.

Eligibility and conjugation are inherited: a helper has cold entry, FULL exit,
no wrapper, no private-center role and no incident COPY/clear. For
`target += q * source`, constant helper gauges multiply q by
`2^(k_target-k_source)`. Uniform register scales commute with the unchanged
linear frame actions. Entry `2^k` and exit `2^-k` restore arbitrary helper dirt.
The inherited source-bound eligibility checks and full 712 formal scalar-column
endpoints run again on the final candidate.

The exact real-component cost dependent on the gauges, up to an unchanged
constant, is

```
F(k) = 2 sum_h |k_h| + sum_ADD (|e+k_t-k_s| - [p=1 and e+k_t-k_s=0]),
```

where `|q| = p * 2^e` with p positive odd. The first term charges both boundary
scales. The point discount comes from Sagar Thakrar's retained copy-init lowerer;
replacing it with plain absolute value would change the search problem.
All other source access, original SCALEs, helpers, COPY/clear, frames and
recursive children remain in the complete invoice. The final 218 nonzero
gauges add 436 scale macros costing **638 real / 1,276 complex primitives**;
this is eight more real boundary primitives than PR1310. It is already paid.

## Why the census covers every common integer shift

For a nonempty helper subset S, put `k'_h=k_h+d` for h in S and leave the other
coordinates fixed. An ADD inside S or outside S is unchanged. A crossing ADD
has valuation `E+d` or `E-d`, with E its valuation at the current vector.
The only breakpoints are therefore `d=-k_h` for h in S and `d=±E` for crossing
ADDs. They are integers. Between them the cost is affine, and moving to a
breakpoint can only introduce additional negative point discounts. The cost is
coercive: each ADD contribution is bounded below and the paid boundary term
grows at infinity. Thus a minimum over all real d, and hence all integer d,
is attained at one of these breakpoints. Including zero and other helpers'
breakpoints cannot invalidate that conclusion.

The primary implementation precomputes singleton curves at this safe global
breakpoint superset. Adding singleton curves double-counts changes to an
internal edge, whose actual coefficient is unchanged. For each internal ADD it
adds the exact correction `2 f(E) - f(E+d) - f(E-d)`, counting multiplicity.
It checks all 237 singletons, all 27,966 pairs and all 49,898 connected triples
in the 2,414-edge helper interaction graph.

Every connected three-vertex graph contains a length-two path; generating all
neighbor pairs at each vertex and deduplicating gives exactly those triples.
At the initial and final vectors, every singleton and common-shift pair has
minimum zero. Each of the remaining 2,140,772 disconnected triples splits into
components of size at most two, and its exact cost change is the sum of those
component changes at the same d. Consequently none can improve there. No
independence between different d values is assumed.

At the initial vector the only improving triple is `(354,469,478)`, only at
shift -1 forward / +1 backward, with delta -2 real. Every proper subset is
nonimproving. The deterministic descent chooses the lexicographically first
best strictly improving tested block, ordered by delta, block size, helper
list, absolute shift and signed shift; it permits at most 25 iterations. The
actual trace is that triple, then singleton L257, then termination. The
intermediate vector has an improving singleton, so the disconnected-triple
reduction is **not** asserted there; the descent need not be globally best over
all disconnected triples. At termination the reduction is valid again. This
is a complete closure in the stated move class, not a claim about search paths
or other coupled directions.

## Verification

From the repository root, Python 3.12, standard library only:

```sh
python3.12 scripts/research_package.py --package research/k8-coherent-triples
```

Expected final marker:
`PASS_REGISTERED_RESEARCH_PACKAGE research/k8-coherent-triples outcome=completed`.
The exact trace, all-curve/minimum hashes, gauges, invoices and formal endpoint
receipt are in `CERTIFICATE.json`. Every recorded census is recomputed.

`independent.py` uses a different direct edge-cut method: it visits every
labeled triple to classify graph connectivity, gathers its literal crossing
ADDs, and prices every integer shift in an enclosing interval using the actual
PR696 lowerer. It does not call the primary `f`, singleton/correction curves,
triple generator, census, transform or invoice. Initial and final minima for
all connected triples and all pairs agree in both orientations; the extreme
integer points also have strictly outward costs. It separately reconstructs
the final word by rational register-scale ratios, counts all literal
primitives, and runs three arbitrary-dirty exact-rational fixtures per
orientation including dirty coefficient work. `INDEPENDENT.json` records
this second calculation. Its source reader and primitive interpreter are
explicitly reused from PR1263, not presented as new independent implementations.
Both implementations are AI-assisted, not independent human review.

Seven test groups include 60 synthetic signed-incidence graphs, every subset
of size one to three, dense bounded integer checks; proper-subset controls;
unit-discount and boundary-price checks; eight rejected dirty-endpoint faults;
four corrupted-census controls; and two actual corrupted predecessor files.
Full formal-column replay and literal dirty fixtures serve different purposes.
Local positive-prefix bounds remain 52/68 bits within the inherited 192-bit
charge; these are local envelopes, not a new global precision invoice.

## Selection, provenance and credit

OS-random seed **37** assigns the donor's complex-supplier track. Three narrow
candidates were considered: phase-varying composition already overlaps
PR1259/1270; coherent triples are selected by seed modulo three; full native
admission exceeds the bounded session. Initial complete live overlap search
covered 804 open PRs and 55 discussions, plus package notes and the review
ledger. No pinned sprint issue existed; the claim was posted in discussion1166.
The observed unlocked singleton justified one bounded refinement to descent
and final closure; the original frozen-vector census is retained.

Base: **bce54fb3f895cbe5cd4c0eb477c3afeed100190f**. The selected certificate,
actual reconstruction source and maintainer review were followed: accepted
conditional κ there is 0.001672660197076918. No selected file, frozen source,
`upstream/` file or existing package is changed. This is an explicitly scoped
scalar side result, not fulfillment of the newer helper-inventory task card.

Credit **Hanson Sun / @bbMisk** (PR1214 eligibility and exact pair method),
**@woklerx** (PR1161 gauge mechanism/source engine), **Sagar Thakrar** (PR696
literal copy-init lowering, PR1259), **Philipp / @mightyOil** (PR1263 simultaneous
gauges, PR1310 coupled-pair result), Jeremy Kothe, Rohan Arun, Hao Yan /
icekylinx, Douglas Colkitt and the retained supplier lineage. PR1259/1270
varying gauges and PR1170 scale merging are not composed here. No priority
claim is made for general block-coordinate search.

Prepared for **Philipp (@mightyOil)** with substantial **OpenAI Codex / GPT-6
Astra** assistance in mathematics, code, verification and writing. New material
is Apache-2.0; predecessor notices are retained. No proof assistant, independent
human review, hosted CI success, complete selected cold replay, full controller,
physical admission or discharged all-size/compiler/precision/tape/analytic
assumptions is claimed.

## Open next questions

1. Can unequal shifts on three helpers, or a larger coherent block, improve
   this final vector? Start with the retained graph and literal objective.
   Common-shift closure says nothing about those larger classes; arbitrary
   pair stationarity at this new vector must also be checked before using it.
2. Can the fully priced scalar candidate pass native and complete
   hosted/controller admission? Start by carrying all 436 boundary scales into
   the pinned emitter. No native artifact or global precision invoice is
   supplied; those remain blockers to supplier integration. Structured entries
   are in `TASK.json`.
