# One rejected dyadic pair is a local helper target

**Scoped local handoff. No new κ.**

On the pinned PR5580 word, cut 13762 and frame 1053 admit a dyadic dual pair
with no unit coordinate in the row. The unit-pivot constructor in
`research/p104-coupled-helper-bases/construct.py` rejects both the source-chart
pair and the cut-chart pair with `Dyadic basis pivot`. The Euclidean compiler
in `research/dyadic-helper-basis-completion/basis.py` emits a legal ADD and
dyadic-unit SCALE schedule. Substituting that schedule into the existing
coupled handoff adds one public helper field and splits one rank-9 helper.

The local replay then records:

| | PR5580 word | After this handoff |
|---|---:|---:|
| Events | 25140 | 25280 |
| Public fields | 735 | 736 |
| Paid MOVE histogram | `{1:2211, 2:459, 5:164, 4:94, 3:494, 7:14, 6:18}` | unchanged |
| Helper ranks | `{9:424, 4:83, 5:5, 8:15}` | `{9:423, 4:84, 5:6, 8:15}` |
| Scalar allowance | 217428 | 218564 (+1136) |

Register 596 keeps initial frame 3 and finishes at frame 1053, a rank-5
lifetime. The new register 735 runs from frame 1053 to frame 127, a rank-4
lifetime. Together they replace that register's old rank-9 lifetime from
frame 3 to frame 127. Endpoint identity, peak owned fields 1, and all eight
owned copy lifetimes hold under `local.replay`. The fixed operation ceiling
in that replay is 26000 events; this word uses 25280.

This answers the open question in
[research/dyadic-helper-basis-completion](../dyadic-helper-basis-completion/TASK.json):
a newly admitted dyadic pair can be an additional physical helper target on
this word. The local paid profile does not improve. The scalar allowance
increases. Complete κ is unchanged, and the selected record is not updated.

## The pair

Normalized so both pairings equal 1:

- `v = a = {592: 5/16, 593: 5/16, 594: 5/8, 596: 3/8}`
- `u = {592: -1, 593: 1, 594: 1, 596: 1}`
- `b = {188: -1, 592: -1, 593: 1, 594: 1, 596: 1}`

The four cut registers sit at frame 1053. Their prefix rows also touch
registers 595 and 597; those coefficients cancel, so `a` equals `v` and lands
in the helper group with frames `(3, 127)`. The suffix columns also touch
193, 199 and 204; those cancel, leaving the extra group register 188. No
owned field is live at the cut. The helper group has 424 members. The frame
spans are strictly nested: span(frame 3) < span(frame 1053) < span(frame 127).

Every coordinate of `a` and `v` has an odd numerator, so the old pivot test
fails. A nearby row `{596: 1, 592: 5/16}` with column `{596: 1}` still passes
that test, which isolates the rejection to the missing unit coordinate.

The Euclidean schedule has 36 operations at frame 3 and 34 at frame 1053.
Its coefficients are in `{±1, ±5, ±10, ±1/16, 16}`. Each satisfies
`abs(q)+1 < 2^16`, and every SCALE coefficient is a dyadic unit. The handoff
inserts each schedule and its inverse, 140 events. Their scalar allowance is
exactly the observed +1136. This schedule is a feasible witness. It is not
claimed to be coefficient-minimal. The direct matrix check is `a R = e_p^T`
and `R e_p = b` for both pairs, with pivot 596.

## What was not run

Native chart maps, the physical caller, the PR5545 capsule, the compiler
closure and the outer ledger were not run. The nine published handoffs in
`WITNESS.json` were not replayed here; #5611 already checks those unit-pivot
interfaces. Other pivots at this cut were not replayed. A locating search
outside this verifier saw another coefficient-box hit at frame 597; that hit
is not part of the receipt. No census of other cuts is claimed. Unknown
delivery, restoration and native costs are not zero.

`certificates/selected-result.json` on this base records κ = 781451/250000000.
`docs/research/current-priorities.md` still describes the earlier #5599
checkpoint. This package leaves both files unchanged.

## Reproduce

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/dyadic-rejected-dual-target --check-only
python3 -B scripts/research_package.py --package research/dyadic-rejected-dual-target
```

Both registered commands must print `PASS_DYADIC_REJECTED_DUAL_TARGET`. The
launcher must print `PASS_REGISTERED_RESEARCH_PACKAGE`. The verifier checks
pinned SHA256 values and does not call Git or the network. A direct run is
`python3 -B research/dyadic-rejected-dual-target/verify.py`.

## Scope and credit

Base: canonical `CrocSwap/integer-mult-bounds` main
`2485805a6d47f36ea83ddde6327d453ac82d44dc`, priority revision 8. The catalogue
card is `p104-side-correction`. Scope status is **changed**: the card asks for
a complete-invoice improvement on uncovered #5599 work, while this result is
the #5611 physical-target question on the PR5580 constructor word. The
overlap helper's offline local search matches many other
`p104-side-correction` packages by card id. The predecessor that leaves this
question open is #5611
(`research/dyadic-helper-basis-completion`), whose discussion claim is
[#5125 comment 19184390](https://github.com/CrocSwap/integer-mult-bounds/discussions/5125#discussioncomment-19184390).
That claim records the constructor and no new physical channel. #5615 asks a
different capacity question and is not answered here. Remote PR and discussion
coverage was not refreshed for this note.

Ali Romman's [PR #5611](https://github.com/CrocSwap/integer-mult-bounds/pull/5611)
and [PR #5602](https://github.com/CrocSwap/integer-mult-bounds/pull/5602)
supply the Euclidean compiler and the coupled handoff. [PR #5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599)
is the reviewed helper-subspace construction named by the priority prose.
Nick Petalas's [PR #5115](https://github.com/CrocSwap/integer-mult-bounds/pull/5115)
uses Euclidean row preparation for a different single-hub contract. The PR5580
word and `local.py` retain David Arias, Cinna Davis, Gareth Davidson and
Ali Romman's source credit. Prepared by unpaidmoon with substantial Cursor
Grok assistance. Apache-2.0. No independent human or formal-kernel acceptance
is claimed.

## Open next questions

1. Does this rank-9 to rank-5-plus-rank-4 split improve the complete signed
   moment once the scalar allowance, native maps and physical caller are
   charged? The local paid histogram is unchanged and the scalar allowance
   rises by 1136, so a helper-rank credit alone is not a κ improvement.
   First step: replay the coupled caller and native maps on this one-step
   word and charge the +1136 allowance. Blocked by the PR5545 capsule and
   outer predicates, which were not run. Unknown costs are not zero.

2. Is there a shorter ADD and dyadic-unit SCALE schedule than the Euclidean
   compiler's 36 source-chart operations and 34 cut-chart operations? The
   +1136 allowance is the cost of this feasible schedule. First step: search
   for a shorter factorization of the same two matrices inside the growth
   bound. Blocked by the absence of a coefficient-minimal compiler here.

3. Does another pivot at cut 13762, or another legal rejected pair on this
   word, produce a lower local scalar allowance? Only pivot 596 was replayed.
   First step: recompile the co-located pivots `{592, 593, 594, 596}` and
   compare local allowances. The frame-597 locating hit is not a packaged
   witness.
