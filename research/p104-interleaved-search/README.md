# Exact P104 query construction and complete forward fanout word

**All eight delivery terms now have an exact finite forward construction, but
no κ improvement is certified.** Frame coalescing reduces its local cost;
the concrete owner-window packing still misses the selected result. No global
supplier or improved multiplication bound is claimed.

The starting point is canonical main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. The selected result remains
κ = `836330098538459/500000000000000000`. The requested significant, fully
verified gain (working threshold: 1% relative improvement) is **not achieved**.

## Constructive result

`query_construction.py` derives all sixteen admissible query banks from the
pinned selected word: eight coordinate centres and eight punctured Y roles.
For this decoder, four coordinate banks are ready before B. A dependency
permutation produces the other four after 94, 209, 337 and 507 of 1846 B events.
It preserves every register's incident-event order, all frame inclusions, the
704-column B transformation and its transport profile. Query construction uses
actual public registers; it requires no external pure-query oracle.

`fanout.py`, with the exact rational contacts in `FANOUT-PLANS.json`, realizes
all eight decoder terms in one chronological word:

1. At B prefix 507, copy each actual query at its hyperplane Hb, normalize it,
   and descend through one rank-seven native child to its target line La.
   The eight private copies are sequential; peak occupancy is one.
2. Seed ordinary dirty helpers at La and ascend through their public contacts.
   The joint schedule needs 31 helpers: 28 from the separate contact plans and
   three more to avoid incompatible shared-reader frame promotions.
3. Cancel the helper responses on non-output roles, restore every new helper
   from its actual query bank, perform the old cleanup, and restore the eight
   punctured Y roles. Initial frame-zero compensation removes the remaining
   dirty contribution to live outputs.

The checker replays all **735 independent public input columns**. Every live Y
ends as its initial Y plus its corresponding initial X; all other public roles
return to their initial values. It verifies actual query frames, arbitrary
helper dirt, common charts for scalar additions, monotone public paths, owned
private-copy lifetimes and fixed final boundaries. The word uses 832 initial
compensation additions, 276 helper-response cleanup additions and 911 punctured
Y restoration additions. Four controls change the source coefficient or omit
private initialization, response cleanup or compensation while keeping the
repair word fixed; each is rejected.

`native_checks.py` lowers every literal transport from that verified word using
the pinned predecessor compiler. An independent interpreter checks signed Pauli
actions and exact global phases, 208 rank-zero intrinsic endpoint adapters, and
all 4096 Gaussian basis columns across the eight private paths. A deliberately
wrong global phase is rejected. `verify.py` binds the occurrence lists and paid
profiles to the scalar/frame replay and cost calculation. Counts and recipe
hashes are in `RESULT.json`.

`coalesced.py` improves the same word by changing 339 common scalar frames,
recorded sparsely in `COALESCED-FRAMES.json`. Scalar coefficients and order,
every public boundary frame, and all private Hb/La copy and seed interfaces
stay fixed. Transports are rebuilt and all 735 columns are checked afresh.
The cheaper public histogram is
`2429 H1 + 558 H2 + 389 H3 + 112 H4 + 108 H5 + 16 H6 + 6 H7`,
plus the same `8 H7` private descents. Its native lowering is checked separately;
two additional controls corrupt a contact coefficient or a private seed chart.
The search heuristic is not part of the replay or an optimality claim.

## Complete local cost and remaining admission

Before coalescing, the public histogram is
`2611 H1 + 514 H2 + 378 H3 + 132 H4 + 81 H5 + 15 H6 + 6 H7`;
the eight private descents add `8 H7`. The total local rank mass is 5894.
All eight delivery terms, helper entrances and dirty restoration paths are
included. The 31 new helpers contribute 279 lifetime ranks; existing public
roles add a further 21 ranks compared with the retained punctured baseline.

`fanout_budget.py` checks exact rational interval brackets under the retained
`m=73, W=832, N=9, COPY=56` coverage and balanced-transfer model. It grants all
818 remaining paid ranks the favorable fractional rank-51 idle packing, without
requiring that this packing exist. Even this relaxation gives:

| Scenario | κ upper bound (approx.) | Relative to selected κ |
| --- | ---: | ---: |
| Actual complete forward profile | 0.00165721126536 | −0.92361448% |
| Also grant four unused old gathers' cost credit | 0.00166251958654 | −0.60625646% |

The extra gather credit is deliberately favorable: its joint compatibility with
fanout cleanup is unproved. Both exact moments at the selected κ are strictly
above one. These are **upper bounds**, not achieved exponents. They rule out
this concrete profile within the stated model, not P104 schedules in general.

The coalesced profile has a slightly positive **optimistic** ceiling: at most
+0.05455960% relative to selected κ, or +0.37824205% with the conditional gather
credit. Both exact target moments rule out a 1% gain for these fixed profiles.
A positive upper bound is not an achieved improvement.

`hosting.py` constructs and checks a concrete owner-window packing for all
527 ordinary roles in each of the selected schedule's 144 calls: **75,888
placements**. It uses the actual complete lifetime widths, including the 21
extra ranks on 17 old helpers, 16 reclassified roles and 31 new helpers. It
checks window membership, distinct physical owner families within each call,
exclusion of active data, nonoverlapping offsets and complete role coverage.
The exact residual histogram has mass 117792, or 818 per call. It is reproduced
from pinned schedule and owner inputs; its assignment digest is recorded.

`coalesced_budget.py` also prices that actual residual histogram. The resulting
fixed-invoice κ upper bound is **1.21466947% below selected κ**, or **0.89916793%
below** after additionally granting the conditional gather credit. Thus this
available packing does not turn the cheaper finite word into a gain. A better
packing is not excluded by that calculation.

The owner certificate is conditional on the retained schedule windows. It does
not generate or admit a changed 104-port global emitter, backward supplier,
route/wrapper proof or recursive precision/reserve account. Those remaining
obligations cannot establish a gain for the rejected invoice. A cheaper local
word or packing must first pass the full cost screen. The selected frontier is
not modified.

## Earlier checkpoints and scope

The package retains its useful predecessor checkpoints separately.
`actual_queries.py` checks an eight-query 704-column scalar identity whose 302
scatter additions are explicitly unframed. `natural_delivery.py` and
`NATIVE-CHAIN.json` check one actual-source rank-one increment through 16
contacts; `natural_budget.py` prices it with the seven other deliveries mostly
free. `scalar_surgery.py` is the older pure-query-cut identity; `delivery.py`
and `CHAINS.json` check two externally supplied query fragments; `budget.py`
prices those fragments. None of their optimistic ceilings is promoted to a
supplier or substituted for the complete fanout invoice.

The native fixture removes selected port positions
`3, 14, 21, 34, 39, 61, 76, 93`. This differs from the puncture in the selected
port adapter package. The aggregate checker binds the exact port set, decoder,
query rows and normalizations rather than conflating the fixtures.

## Reproduce

From the repository root, with Python 3.12 and the standard library:

```sh
python3 -I -O -B research/p104-interleaved-search/verify.py
python3 scripts/research_package.py --package research/p104-interleaved-search
```

The registered replay is read-only: it checks pinned source hashes, recomputes
the receipt, compares it with `RESULT.json`, and runs the rejecting controls.
`--write-result` explicitly regenerates the receipt. The registered replay
passed on CPython 3.12.14 with assertions disabled. A separate CPython 3.14.7
replay passed from a source-only export of the 23 package files and 13 declared
inputs, without changing the export. Both ran on macOS 27.0.1, arm64. Exact
commands and the receipt hash are recorded in `TASK.json`. Search optimizers are not
needed for replay. The exact contacts are checked evidence; unsuccessful route,
decoder, helper-reuse and frame-coalescing searches are not impossibility proofs.

## Open next questions

- **Can existing helper lifetimes replace new fanout helpers?** The full local
  identity now exists, but its helper and small-rank transport costs exceed the
  useful budget. Replace one complete lifetime, replay every input column and
  the joint frame chronology, then reprice. Existing helpers acquire old scalar
  payloads after B prefix 507, so they cannot simply be treated as persistent
  query-plus-dirt storage.
- **Can a different contact schedule reduce small-rank children?** The separate
  flow plans minimize helper count without optimizing the joint native invoice.
  Optimize the actual moment while preserving query-bank access and all dirty
  restoration. Total rank mass alone does not measure the expense.
- **Can a favorable local word satisfy full admission?** Only after a complete
  local profile passes the necessary cost screen, construct its backward dual,
  actual owner windows, residual children, precision/reserves and both exact
  moment checks. Physical register capacity alone is not a hosting proof.

## Provenance

This follows the native P104 channel in PR1991 (Chafik Boukhalfa), the scalar
channel in PR1972 (Rohan Arun), and the chronological gather schedule in PR1940
(Adam Gall). The P104 geometry and decoder work originate in PR1071 (Josie
Elliston), PR1125 (Ali Romman), PR717 and PR968. The selected scalar architecture
and Hamming packet construction retain their predecessor attribution, including
icekylinx's frame-sa504 work and the selected PR1042/PR1094 lineage. The packing
ceiling engine is Douglas Colkitt's existing work, not a new theorem here.
The native compiler and independent interpreter retain the notices pinned in
`SOURCES.json`. The inherited T16 owner schedule is Rohan Arun's
`complex-t16-rare-pattern-exchanges` package, following PR1087 and earlier
packing work by jeremykothe2, FanPUYen's PR858 and the retained
PR1018/PR1005 lineage. The archive and its notices remain unchanged.

PR2082's earlier temporal-cut result concerns a frozen native schedule; this
construction changes that hypothesis. PR2090 and PR2083/PR2089 cover distinct
cut and terminal-correction questions. PR2139 (Jose Manuel, Discussion2121) independently publishes a distinct
836-register delayed-query word based on full120/PR697. This construction
instead rebuilds the selected P112 word on P104 and checks 735 public registers. Discussion2131 (Hope7Happiness) explores
dirty carriers starting from the native 72-helper G/2 channel; this package
uses the selected 480-helper word plus 16 reclassified roles. Discussion2123
and PR2127 constrain retained transports; the changed paths here do not satisfy
that premise. PR2148 extends the retained-obligation obstruction to subdivided
intervals; this word replaces and coalesces original obligations. Discussion
proposals remain provisional evidence. Source blobs,
hashes and overlap snapshots are recorded in `SOURCES.json` and `TASK.json`.

Prepared for David Arias with substantial OpenAI Codex assistance, including
parallel construction and checking. Apache-2.0. No formal proof assistant or
human independent review is claimed.
