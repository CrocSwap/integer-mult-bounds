# Open whole-owner allocator and a delivery-layer map of the complex word

Research note and tools. Prepared by **higherbeing** with Claude Code (Anthropic) assistance. Apache-2.0.

Two things the κ race has so far kept as frozen witnesses or as prose are released here as runnable, checked code:

1. **An open asynchronous whole-owner allocator** (`tools/`): the optimisation that turns a local complex word's
   residual widths and a replica call order into a literal owner map of the kind #505, #508, #512, #514 and #517 ship as
   `ASYNC-OWNERS.json.gz`. Validated: on #505's own call order and widths it returns #505's published remainder profile
   exactly (`results/allocator-validation-pr505.json`), with an optimal rounded aggregate objective; on #507's widths
   under #508's offset-six order it matches the reported timing-free profile, and the resulting profile gives #512's
   complex endpoint `b = 0.001389978441615608` through the pinned moment engine. The latter literal nomination was
   not completed by this package (see the table below).
2. **A map of where the 560 complex helpers go** (`code/`, `results/`): exact symbolic replay of the #433, #484 and #507
   words, classifying every helper by role, duplicate structure and consumer, with the frame-chain structure of the
   targets, a merge-legality test, and one correction to a tempting lower-bound argument.

## 1. The allocator

`tools/aggregate_milp.py` is the aggregate model (CP-SAT): variables `x[t,i,ρ,w]` = number of width-`w` helpers of the
call at time `t` hosted on idle child `i` of owner replica `ρ`, and `y[i,ρ,P]` = number of that child's 120 ports tiled by
the width multiset `P`. Constraints: every call places all its helpers inside the windows of the plan; at most one helper
per call per port (whole owner); the pattern counts cover the 120 ports; Hall conditions for the literal nomination.
Objective: Σ ports `g(remainder)` with `g(r) = r·ln(73/r)`, which is the exact first-order objective because the rank
mass is fixed (`Σ r(73/r)^c = mass + c·Σ r ln(73/r) + O(c²)`).

The implementation rounds each objective coefficient to an integer after scaling by 1000. `OPTIMAL` certifies
the resulting CP-SAT model, not an exact optimum of the logarithmic objective or the full exponential moment.
Matching a reported profile does not independently establish a sharp unrounded ceiling. The aggregate model
is a relaxation of literal nomination; its status alone does not certify an owner map.

`tools/loop.py` adds lazy cuts: after each aggregate solve it tries the literal per-child nomination (a 0/1 model per
child copy) and, for every child that fails, adds the violated top-k Hall cut
`Σ_{t ∈ top-k calls} Σ_{w∈S} x[t,w] ≤ Σ_P y_P · min(k, #S-slots of P)`, then re-solves with the previous solution as hint.
`tools/nominate2.py` writes the literal roles in #505's `ASYNC-OWNERS` format (chronological offsets, whole owners),
`tools/compose_profile.py` recounts the remainders from the roles alone and writes the plan file that #508's
width-generic `emit_async.py` / `audit_async.py` check against.

| run | widths | order | result | note |
| --- | --- | --- | --- | --- |
| validation | #484 `{9:438,8:104,7:14,5:4}` | #505 offset 3 | OPTIMAL 123,686.5; remainders `{1:136,3:3432,5:3501,7:2137,16:1,48:408}` | identical to #505's published profile |
| #507 word | `{9:396,8:146,7:14,5:4}` | #508 offset 6 | 99,625.66 (bound 99,616.7) | aggregate stage with Hall cuts; the literal nomination loop was still adding top-k cuts when #512 published the same endpoint, and was stopped |
| timing-free comparison | same | all windows open | OPTIMAL 99,625.66 | matches the offset-6 profile in this rounded model; #517 separately discusses an exact ceiling |

Requires `ortools` (CP-SAT). Inputs are a plan file in #505's format (`order`, `windows`, `sides`, `pairs`,
`baseline_widths`) and the width histogram; see the docstrings. Solve times on a laptop: 1–10 minutes per aggregate
solve, seconds per child nomination.

These are prototypes for the 120-port, 72-call, 560-helper family with the stated width-73 objective, not generic
allocators for every later supplier. Final acceptance requires literal nomination and the emitter/auditor's
physical checks. The recorded historical results are contributor receipts; the regression below checks solver
failure handling and a small independently recounted allocation, not the full historical optimisations.

Maintainer review fixed an export bug: an `UNKNOWN` aggregate solve could previously write an empty allocation.
Both aggregate entry points now reject statuses other than `FEASIBLE`/`OPTIMAL`, including under `python -O`,
without touching the output. Run `python tools/test_allocator.py` (with `ortools` installed) for the regression.

Why release it: every published asynchronous result ships only its frozen witness. Anyone changing the local word
(new gauges, new kernels, new factories) needs a fresh allocation; these tools provide a starting point for that search.

## 2. Where the complex helpers go

`code/delivery_layer.py` replays phases precondition+A over Q and classifies the 560 helpers. All three words agree on
the packet layer; they differ in how packets reach the targets.

| class (after phase A) | #433 | #484 | #507 |
| --- | ---: | ---: | ---: |
| single-source copies (feed the block shears 476×, packet builders 343–371×, centres 21×) | 84 | 84 | 84 |
| 4-source packets (span 3) | 269 | 269 | 269 |
| 8-source packets (span 5) | 204 | 204 | 204 |
| 56-source centre sums | 3 | 3 | 3 |
| identical copies of a packet (same support, same coefficients) | 90 | 90 | 90 |
| sign variants of a packet | 84 | 84 | 84 |
| helpers whose first gate copies a source | 389 | 380 | 283 |
| helpers built only from other helpers | 171 | 171 | 255 |
| identical pairs each read by exactly one target, mergeable post hoc at the readers' shared 7-frame | 0 of 45 | 0 of 22 | 0 of 22 |

Coefficients are ±1 and ±1/2 only. The duplicates are not waste in the packet algebra; they exist because the same packet
is read by two targets whose caps `u_t^⊥` are different 8-dimensional frames, so one register cannot serve both at the
cap. Merging a pair at the readers' shared 7-dimensional frame `u_t^⊥ ∩ u_e^⊥` fails for every pair in all three words
for the same reason: each reader has other pre-cap reads at frames that do not lie inside that meet. The merge would
have to be designed together with the readers' frame chains, not applied afterwards.

`code/plane_cover.py` records the chain structure that governs this (`results/plane-cover-*.json`):

- every target's cap is exactly `u_t^⊥`, and the sources it can be served are exactly the 56 with `u_s·u_t = 0`;
- in #433 and #484 every target reads along `0 → F₅ → F₆ → cap`; its 5-frame is private (112 distinct 5-frames for 112
  targets) and its 6-frame is shared with exactly one other target (56 pairs). #507 shifts this to `0 → F₆ → F₇ → cap`
  with the same private/paired pattern;
- so a packet is delivered either once per target (private frame or cap) or once per pair (shared 6-frame). No frame
  below the cap is shared by more than two targets in any of the three words.

**A correction.** One might try to bound carriers by plane sections: a register of `s` above its line sits on a plane
`span(u_s, v)` and can serve the readers with `u_t·v = 0`; the largest such section has 32 of the 56 readers. But two
sections always cover all 56: every port has odd weight, so the all-ones functional is 1 on every port and the planes
spanned with `v` and `v+1` are complementary on the readers. Plane sections therefore give no bound (we had written one
down privately and withdraw it). The binding structure is the nested frame chains above: a delivery frame must be a
chain frame of every target it serves.

## 3. The direction this points to

The complex word's cost is 72 % helpers, and the helpers are mostly delivery: the same 269 + 204 packets as #425, copied
and re-signed until every target can read them inside its own chain. The chain design in use shares frames only in
pairs. A design that groups `k` targets on a shared `(9−k)`-dimensional frame delivers a packet once per group instead
of once per pair, at the price of one extra climb step per target per shared level (≈ 3 Φ at `m = 73`, against ≈ 25 Φ
per helper removed). The question is combinatorial and exact: choose chains `0 ⊂ G₁ ⊂ … ⊂ u_t^⊥` for the 120 targets
and frames for the 473 packets so that every packet's port span lies in the chain frame of each of its readers, and
minimise paid climbs. Nothing in #446's rigidity results (labelling, caps, copy loss, m) constrains this layer. We have
not solved it; the data above is what a solver would have to beat.

## Credits

#425 (jacklightChen / Zhihao Chen) and #433 (icekylinx) for the packet word; #484 for the gauge/kernel word; #507 (eumemic) for the partial-own
factory; #505 and #508 (Dugongue) for the asynchronous schedule and the width-generic emitter/audit used to check the
emitted maps; #512 and #517 (chafreaky) for the independently published endpoint and ceiling that the allocator
reproduces; #446 (DreamingOfClouds) for the rigidity results; #496 (eumemic) and #442 (DaysSky) for whole-owner hosting.
All scripts here were written by higherbeing with Claude Code assistance.
