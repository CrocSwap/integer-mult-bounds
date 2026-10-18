# Conditional dirty-host cut-rank audit

In the stated scalar common-frame transport model, the [history-span proof](PROOF.md) gives

`paid mass >= sum_alpha |initial host height - final host height| + q * rank_K(S)`.

This independently audits [ctoth's dirty-host implication](https://github.com/CrocSwap/integer-mult-bounds/discussions/1516#discussioncomment-18913724). It permits mixing, cancellation, feedback, cycles and reuse. The required contract has independent ordinary inputs and zero private work at entry, carriers initially at height at least `q`, clean scatter `Y + SX` observed at height zero, restored disjoint hosts, and a complete bill for all transports. Actual observations may occur at different times. The proof uses their joint rank modulo the complete initial span on each side of a cut; it needs no reduction to trees.

A [separate GPT-6 Pro review](REVIEW.md) corroborates the conditional argument and audited the complete original checker. Its one wording correction is applied verbatim in Section 5.3: the prefix must be invertible on the ordinary boundary state. Reversibility only on ordinary-plus-private registers is insufficient. The two-gate example `P += X; X -= P`, from `X=x, P=0`, leaves `X=0, P=x`. This violates the clean-entry hypotheses, not the theorem.

The useful hosting credit must still be bound to the proved endpoint term, exact gauges and a fully charged preparation/cleanup interval. The inherited private-centre checker does not establish that extended contract. No selected rank-8/64 calculation, production admission, new kappa or universal obstruction to hosting is claimed. The [literal branching-tree proof](https://github.com/CrocSwap/integer-mult-bounds/discussions/1516#discussioncomment-18913740) is a separate source control; [Dennis's selected-word tree audit, PR1643](https://github.com/CrocSwap/integer-mult-bounds/pull/1643) is complementary work. Its reported geometry and attainment are not rechecked here.

## Evidence and reproduction

From this directory, using Python 3.12 with no external dependencies:

```sh
python3.12 -I -B check.py
python3.12 -I -O -B check.py
python3.12 -I -B boundary_checks.py
python3.12 -I -O -B boundary_checks.py
```

All four local Python 3.12.14 runs passed; normal and optimized output agree byte-for-byte for each checker. Both use explicit exceptions, so acceptance does not depend on assertions.

- `check.py`: six rational logical-row fixtures, all 16 subspaces of F2^3, 66 nested edge constructions, 256 two-leaf trees, a tight three-leaf example and 11 rejection controls. One deliberately outside-contract fixture illustrates pre-positioned dirt.
- `boundary_checks.py`: six fixed Q/F2/F3 traces with both host directions, nonuniform heights, target feedback and simultaneous or strictly noncoincident clean observations; also the ordinary/private prefix distinction in each field.

[REPLAY.json](REPLAY.json) and [REVIEW_REPLAY.json](REVIEW_REPLAY.json) record local commands, timings and hashes. Saved outputs are `check-normal.json`, `check-optimized.json` and `boundary-results.json`. [VERIFY.json](VERIFY.json) registers these finite checks. They do not machine-certify the universal proof, physical Clifford/owner/wrapper/phase conditions or a global invoice.

[SOURCES.json](SOURCES.json) pins authenticated source bytes, exact original artifact hashes and the single review amendment. The original `execution.json` records the producer's Python 3.13.5/Linux runs separately. Its `source_manifest.json` and report retain the historical failed raw downloads; the operator subsequently authenticated the pinned repository bytes. The compact review is included, not the full reviewer report. Source files were recovered with canonical hashes verified; no transport ZIP is used as evidence.

The Section 6 endpoint-height comparison is a Pro-authored deduction from the gauge conventions. The source's ascent-plus-tail calculation concerns its prescribed nested ascent, not arbitrary nonnested routes. Package base is `c24fb5e6537d19d79c62265e4a12781aef9309cb`, priority revision 3; historical source and claim bases remain separately pinned.

## Open next questions

[TASK.json](TASK.json) gives first steps and blockers:

- Bind each claimed hosting credit to exact host endpoints and logical gauges.
- Provide the complete charged preparation/cleanup interval and independent entry state.
- Bind one extended dirty-host implementation to the physical and production admission contracts.

## Credit

Credit ctoth and his disclosed GPT-6/Codex, Gemini 3.8 Flash/Antigravity and Claude Opus 5.5 reviewers; icekylinx's frame/emitter/auditor work; DreamingOfClouds's gauge-kernel and PR595 lineage; jeremykothe2's PR635 source package; DaysSky's idle-axis hosting and retained notices; rohanarun's selected PR1094; and Dennis / @antunishdPursuit's complementary tree audit. Exact roles are in SOURCES.json.

Prepared by Andrey Mas (an664). GPT-6 Pro through ChatGPT authored the audit and both checkers, with a separate Pro conversation providing the adversarial review. Codex collected sources, coordinated, inspected code for execution effects, replayed it and packaged the result. No human or proof-assistant review is claimed. Apache-2.0.
