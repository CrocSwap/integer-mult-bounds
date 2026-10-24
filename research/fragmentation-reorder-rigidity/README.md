# The fragmentation of the #4610 word is rigid under free scalar reordering

**Scoped negative result; no new κ.** The selected record is unchanged.

[#5226](../fragmentation-ceiling/README.md) (`fragmentation-ceiling`) prices the whole gap between Cao Yifan's
final [#4610](../kappa-round3-warp-20261022/README.md) word and the +0.05 % bar as fragmentation loss: Λ = 23.86 per
call, where Λ_f = Σ_j rank_j^t − R_f^t sums over the climbs of each field (Theorem B there). Its ship test asks which
scalar-program changes can merge climbs. #4993 and #4610's own MILP re-chose frames at a **fixed chronological
order** and found nothing; #4610 lists "change scalar chronological order" as open; `cao-trace-retiming-20261023`
compresses commuting ADDs at fixed chronology and keeps every climb; `fusion-pair-scalar-rewiring` (#5422) shows
no consecutive pair of rank-1 climbs can be fused by free same-frame rewiring.

This package frees the **order**: scalar operations may be rescheduled anywhere their value dependencies allow,
every field's frame chain and every contact's common frame are re-chosen jointly, and the eight owned-centre
reads may move along their source chains. Under these rules **no intermediate level of any field can be
removed at a gain**: every admissible re-routing of every one of the 2,526 droppable levels is enumerated
(518,315 re-routings) and each is either infeasible or relocates a centre read to the full frame, which raises the
bill by 0.983. The fragmentation of #4610 is a property of its operation set and centre interface, not of its schedule.

## 1. Model (the retained frame contract, order freed)

| rule | statement | source |
|---|---|---|
| chains | a field occupies a nested chain of binary subspaces S_f < F_1 < … < T_f; a climb costs its dimension gap (H1–H2 of #5226) | #4610 contract, #5226 §0 |
| contacts | a two-field ADD/COPY happens at one common frame of both chains, with S_d + S_s ≤ F ≤ T_d ∩ T_s | one common frame per ADD (#5226 H1; `format-limits-2` S1) |
| centre | a COPY C0 ← source may sit at any frame of the source chain of dimension ≥ 1 (the transport to frame 0 then costs that dimension); the 176 deliveries target += C0 at frame 0 are fixed, as are the 8 centre transports' endpoints | `native_extensions.literal_replay` checks the field's frame at every C0 contact |
| order | scalar ops, warps, centre transports and adapters keep their value dependencies (write/read and write/write conflicts; ADDs into one destination commute); the markers `zero_frame_precondition`, `full_frame_cleanup`, `done` are barriers (the second interpreter needs the cleanup block last); every native warp stays anchored between its two frames; along a field, contacts occur in non-decreasing chain order (no descents) | exact interpreters of #4610; `verify_buffers.replay` |
| fixed | operation set, coefficients, native maps, all 632 field endpoints, the 12 fields that revisit a frame | scope |

A **level** is an intermediate frame of a chain that hosts at least one contact. Dropping it means re-routing all
its contacts to other frames of the chain (a frame may be inserted into a partner's chain if nested there) and
merging the two adjacent climbs into one; by strict concavity every merge lowers Λ. Feasibility of a re-routing is
decided exactly: the operation DAG plus the per-field level order must stay acyclic (Pearce–Kelly incremental check).

## 2. Results (`verify.py`, standard library, about 2 minutes)

| # | statement | value |
|---|---|---|
| 1 | word census: 632 fields (224 mains, 408 helpers), 17,453 scalars, 3,290 climbs; profile {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40} + 8 centre; Λ(t₀) at the word's root | **23.8626** (= #5226) |
| 2 | contacts by common-frame dimension: 7,622 at dim 0, 4,808 at dim 9, **3,659 at intermediate dimensions** (these create Λ) | |
| 3 | dependency DAG of the 18,159 operations (with the three barriers): critical path | **694** of 18,159 (order is loose; without barriers 493, median slack ≈ 50 positions) |
| 4 | levels forced by the partners' **endpoints** alone (contact can neither be deferred to the next frame nor advanced to the previous one by endpoint containment) | **12 of 2,754** |
| 5 | levels forced by the partners' **exact chains** (one-field-at-a-time: the next or previous frame of f must appear in the partner's chain) | **2,437 of 2,754** (Λ ≥ 19.1 with partner chains fixed) |
| 6 | **exact rules, joint re-routing enumerated** over the 2,526 droppable levels (the 12 revisiting fields and the warp frames excluded): 518,315 re-routings tried; 322 levels have no admissible re-routing; 2,196 levels: every re-routing closes a cycle; 8 levels: feasible only by moving the centre read to the full frame, bill +0.983 each | **0 bill-improving drops** |
| 7 | control: centre interface ignored (C0 contacts not level-bound) | **51 improving drops** (test is live) |
| 8 | recorded annealing with multi-step moves (insert a frame, re-route, drop), 37 M moves over three runs | best Λ = word; centre reads stay at dimension 8 |

Rows 4–5 say that neither endpoints nor dependencies pin the fragmentation; row 6 says the joint structure does:
the chains of a field and of its partners pin each other, and the centre interface (a source stands in a
dimension-8 frame when C0 copies it, a target at frame 0 when C0 delivers) fixes the moments around which the
rest cannot move. The only feasible drops are the eight centre-read levels themselves, and only by reading the
centre in the full frame (transport rank 9 instead of 8). Row 7 is why earlier searches that forgot the centre
interface reported Λ ≈ 23.45 (+1 % κ): those states are rejected by the exact interpreters.

### What Λ would buy (kap-family controller formula of #5226 `verify.py`, p and a re-optimised)

| per-call profile | κ (best p, a) | κ at p16 a7 |
|---|---|---|
| the word | 0.0030217759 (p16 a7) | 0.0030217759 |
| mains one climb each (rank 8) | 0.0037103 (p13 a6) | 0.0036997 |
| helpers one climb each (rank R_f) | 0.0051074 (p9 a4) | 0.0049744 |
| Λ = 0 | **0.0081386 (p5 a2)** | 0.0071457 |

So the kap family with centre 8 × 8, p − 1 query shears per port, idle at address width and zero fragmentation would
reach 0.0081; the entire distance from 0.00302 to that number is Λ, and this package shows that none of it is
available by rescheduling the #4610 word.

## 3. Reproduce

```sh
python3.12 -I -B research/fragmentation-reorder-rigidity/verify.py
python3.12 -I -B research/fragmentation-reorder-rigidity/test_verify.py
python3.12 -B scripts/research_package.py --package research/fragmentation-reorder-rigidity
```

Expected marker: `PASS_FRAGMENTATION_REORDER_RIGIDITY`. `verify.py` pins both inputs by SHA256, rebuilds the model
from the word, enumerates the re-routings, runs the control and the kap-family table, and compares
[RESULT.json](RESULT.json) exactly. `--write` regenerates `RESULT.json` (authoring only). `test_verify.py` rejects a
drifted input hash, a corrupted climb rank, a contact frame mismatch and a tampered result, and re-runs the live
control. The recorded searches are in [search/](search/README.md).

## 4. Scope and limits

- The claim is about the frozen #4610 word: its operation set, coefficients, native maps and field endpoints.
  A different operation set (for example the ADD-compressed word of `cao-trace-retiming-20261023`), new native
  maps, changed helper endpoints, descents, or a different centre delivery frame are outside it. Warps keep their
  two frames (72 fields carry one), and the 12 fields that revisit a frame are left as in the word.
- "Level drop" is the single-merge move; multi-step moves were explored by annealing only (row 8, RECORDED). The
  exhaustive certificate is for single drops with every admissible re-routing of their contacts, pruned only by
  the necessary condition that an operation which must precede another (value dependency) cannot sit at a higher
  frame of the same field.
- The frame model is the one the exact interpreters of #4610 check (frames at contacts, nested climbs, C0 frames,
  final frames). No physical phase, admission or outer-ledger replay was run, since no word is proposed.
- This is a finite certificate on one word, not a floor for the family: Λ = 0 words are not excluded.

## Open next questions

1. **Skeleton-free floor.** Does every scalar synthesis of the #4610 endpoint identity with one common frame per ADD
   need a stated number of intermediate levels per main field? First step: the chain-cover LP over the contact
   hypergraph with free frames (the one-field relaxations here force nothing, so the floor must use the joint
   structure and the centre interface).
2. **Other operation sets.** Run the same enumeration on the compressed word of `cao-trace-retiming-20261023`
   (151 fewer ADDs, same climbs): removed contacts may unpin levels.
3. **Centre delivery frame.** The deliveries at frame 0 are fixed here because the 22 targets' frames meet the
   source frame only in 0 (`owned-centre-wire-floor`); a changed delivery contract is a changed mechanism.

## Credit

Cao Yifan (intqwq), #4610, the word and its exact interpreters; DreamingOfClouds, #5226, the fragmentation
decomposition and ship test whose kap-family formula is reused; the `cao-trace-retiming-20261023` author (ahrazzle)
and Cinna Davis, #4692, for the fixed-chronology compression line; #4993 for the fixed-order frame search; Dugongue,
#4534, and `owned-centre-wire-floor` (#5060) for the centre wire; the `fusion-pair-scalar-rewiring` package (#5422)
for the pairwise fusion certificate. Prepared by Mark (Matarener) with substantial Claude Code (Claude) assistance.
Apache-2.0.
