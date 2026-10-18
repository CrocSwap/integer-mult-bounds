# Sprint claim: output-borrowed fanout

- Track: recursive interfaces; OS assignment seed **59** (`secrets.randbelow(100)`).
- Exact base: `bbc600db2fc15007b7c914f4f2b2ed55fa909c87`.
- Selected certificate followed: PR942, conditional kappa `1661960547713947/10^18`; U8/T37 owner construction and maintainer batch952 review. Not changed.
- Object: arbitrary-dirty fanout `y_i += A_i B x`, with at least two outputs, where a pending/final output can be borrowed and restored as the connector. Compare with PR889's dedicated-connector star.
- Hypothesis: eliminate the dedicated connector for `4 C(B) + 2 sum_i C(A_i)` complete child calls, preserving arbitrary dirty outputs and noncommutative factor order. Prove a query bound only in an explicit unit-generator alphabet; do not claim general circuit optimality.
- Method: written algebra and restricted lower bound; independent free noncommutative symbolic replay, dense exact noncommuting matrices, literal recursive lowering, complete work/storage recurrence, deliberate failed restorations.
- Seed diversification: seed 59 selects heterogeneous factor lengths and prices and three outputs; not another fixed-space tree or signed-incidence search.
- Expected deliverable: one self-contained research construction with exact certificates, pins, controls, and complete cost recurrence; no new kappa.
- Claimed at: 2026-10-13 15:29 UTC. Expected finish: 2026-10-13 16:04 UTC (40-minute total budget from 15:24; final ten minutes for verification/handoff).
- Coordination: GitHub pinnedIssues returned no pinned issue; local claim per sprint instructions. Queue inspected through PR971, including recursive-interface PR889/822/934/943/944/953/951. Immediate targeted overlap checks recorded in handoff.

## Three candidate tasks and selection

1. Heterogeneous ordered dirty-echo connector reuse: PR730/822 already cover this mechanism; not reopened.
2. Remove cyclic-inverse data connectors with additive filters: active PR951 already directly addresses it; not duplicated.
3. Borrow an output of a multi-output common-factor product shear as the connector: selected. Changes the allowed scratch ownership contract, unlike PR889's dedicated connector and PR822's recursive sibling connector reuse. New complete price, no assumption of a better bound.

## Result and handoff (one claim update)

Submitted [PR982](https://github.com/CrocSwap/integer-mult-bounds/pull/982),
2026-10-13 15:50 UTC. Implementation commit:
`880ba2287427b3c5df6443fd6329ba447c5da47c`.

The exact construction removes the dedicated connector for four B calls plus
two calls per A_i. The seed fixture uses 238 full leaf calls versus 318 for
separate output-borrowed echoes, with three extra rows in both; the dedicated
batch uses 158 calls and four rows. The written restricted-alphabet minimum is
2k+4; all 40,320 two-output equality candidates were completed and 224 pass.
No new kappa or native-supplier integration is claimed.

CPython 3.14.6 and 3.9.6 agree on all 41 fixtures, 123 schedules, 1,550 complete
child boundaries and 369 dense forward/inverse pairs. The default replay,
offline relocation, exact payload/receipt regeneration, mathematical controls,
eight package corruptions, source pins, selected-record check and five existing
tests pass. See VALIDATION.md for exact commands and remaining obligations.

Upstream refreshed to `407d52ff15b2217b6e22bce44728b4c3907b6515`, with unchanged
selected certificate/current status. The final immediate overlap check reached
PR981; no same-scope duplicate appeared. PR889 and PR822 remained at their
pinned heads. No pinned coordination issue exists. Neither requested automation
label exists upstream. Review should focus on exclusive complete-child ownership,
the restricted query alphabet, and the paid extra B pair. No merge performed.
