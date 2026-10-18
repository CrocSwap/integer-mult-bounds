# Research claim and handoff

**Track:** `recursive-interfaces`

**Seed:** `1275309492f09fbd834a77649e96ad73`

**Selector card:** `connector-alphabet-change`; refined scope status `changed`

**Priority revision:** 3; catalogue SHA-256 `6686ad58f1fbdbc87134a78901b60fd53a20d3984355e91defbbebc9e9fa8075`

**Exact base:** `0b1cccf86e2f5132ed286a26ef0a681a495740ea`

**Selected-record SHA-256:** `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`

**Claim expiry:** `2026-10-14T11:06:51Z` (two hours from the UTC cycle start).

**Claim board:** posted in [Discussion #1167](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18920274) at `2026-10-14T09:07Z`.

## Question and bounded scope

For the fixed five-source dirty connector with all 31 nonzero output masks, use the complete leaf-price vector from the universal-connector fixture: source calls `B0..B4` cost `[1, 4, 10, 16, 28]`, and every target readout `Am` costs 1. Is the minimum weighted leaf bill exactly 182? This changes the assigned card's cost premise from adding an operation to heterogeneous complete call prices; the alphabet, five sources, target set, arbitrary dirty inputs, restoration rules, frames, and schedule-size model remain fixed.

The construction candidates are (i) relabel the known 12-source-call universal path so its extra source pair repeats cheapest `B0`, or (ii) use the 10-source-call path whose prefix-difference set omits only mask 21 and read `A21` four times. Each should cost 182. The proof domain is all legal source-word lengths: fewer than 10 calls cannot restore and use all five sources; 11 is parity-forbidden; a 10-call path uses each source twice and the pinned complete 945-path result forces one nonzero output mask to require at least four readouts; 12 or more source calls add at least the cheapest two-call price. The verifier will replay both candidate schedules on the full 37-bit dirty state and price every source and target call. It will compare the result with the pinned 200-leaf 12-call schedule and 278/1950 leaf-star controls.

This refines the existing fixed-alphabet five-source interface. The latest complete Discussion snapshot (`2026-10-14T09:17:23Z`, 400 records) surfaced #1579, Arham Tahir's expired claim (05:35Z) on the all-n minimum-query/readout bill for a common-B connector with unequal readout prices. That claim explicitly disclaims a global unequal-price optimum. This package instead proves one fixed five-source optimum under unequal complete **source leaf** prices and unit target-readout prices; it minimizes the weighted total over the 10-versus-at-least-12 source-call cases. Also nearby is open PR #1526, head `1fb85dc6813b88483f4f0a359ccd722376acd292`, on paid root scaling for a signed characteristic-zero 3x3 connector; its alphabet, field, and target differ. Other adjacent scopes are #1707's identical-map broadcast, #1708's shared centre path for two panels, #1739's rank-one connector update, #1155's restoration coalescing across recursion batches, and #1522's dyadic BIT outputs. The predecessor is PR #934, head `f3100aec6ce6a7b061987875d5e9a8b93801ac0b`, whose three-source query result underlies the later universal-connector package. The snapshot had no literal match for the exact weighted-path search terms; the live REST scan found no open PR on this binary source-price objective.

## Result

The registered package replay passes. The relabelled 12-call word and the 10-call word with four `A21` readouts both cost 182 and agree with the desired transformation on all 37 dirty-state basis columns. The two-case lower bound gives the same value. The pinned repeated-`B2` schedule costs 200, so the relabelled schedule saves 18 leaf calls without changing root-record count or the fixed alphabet. This is a source-local weighted interface optimum; no selected supplier occurrence or recursive moment transfer is claimed, and selected κ is unchanged.
