# Scalar half of `native_all_columns` for the selected #6030 word

**Scoped proof; no new κ.** Every `SCALE`, `ADD` and `COPY` in the selected PR6030 word acts by the same rational matrix at every column multiplicity `f ≥ 1`. The census is 18,404 `ADD`s, 861 `SCALE`s and 23 `COPY`s, each on one common chart. Every `COPY` writes an empty owned logical row. The 3,453 `MOVE`s stay inside assumption `native_all_columns`.

The proof is [PROOF.md](PROOF.md). The width-free cancellation

```text
(C^{(⊗)f})^{-1}(C^{(⊗)f} u + q C^{(⊗)f} v) = u + q v
```

is an induction on `f` for one common invertible chart `C`. If the charts differ by `-I`, the correction is `(-1)^f`: width 2 matches the width-free replay and widths 1 and 3 do not. A finite width does not discharge the statement.

## Scope and evidence

Original card: `uniform-transfer-audit`, refined to assumption ID `native_all_columns` and the scalar-instruction implication on the selected PR6030 caller. The actual question, the reason for the refinement and the stop rule are in [TASK.json](TASK.json). Pins are in [SOURCES.json](SOURCES.json). Base commit `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8. Selected κ remains `781451/250000000`.

Open-PR overlap at 2026-11-03T13:29:40Z covered 572 open PR bodies. No open PR states this census. The discussion refresh returned HTTP 502; comments on #1166 from 2026-10-24 through 2026-11-03 were read directly and do not claim these scalar events.

This is session r92, item 5 of the ordered eligible list. The 19 October handoff index is already delivered. Later structured handoffs are excluded when the post is DONE, a later merged result answers them, or the canonical artifact is an open PR, including the H25 requests on #6321, #6326, #6328, #6332 and #6335 and the 2 November review artifacts #6355, #6357, #6359, #6360, #6361, #6376, #6378 and #6396. Unexpired claims do not cover this word's scalar events. Work already delivered by this account is excluded. The revision-8 next-decision table then supplies six rows, and unnamed catalogue cards follow. Item 5 is the all-size row. Within that row, #5837, #6293 and #6522 are different implications and were not repeated.

The chart walk reports zero common-chart violations and 23 empty-target `COPY`s. Register 778 has three serial lifetimes; the other 28 owned registers have one. Peak simultaneous owned registers: 13.

## Reproduce

Python 3.12 and the standard library, from the repository root:

```sh
python3 -B research/pr6030-scalar-chart-lift/verify.py
python3 -O -B research/pr6030-scalar-chart-lift/verify.py
python3 -B scripts/research_package.py --package research/pr6030-scalar-chart-lift --check-only
python3 -B scripts/research_package.py --package research/pr6030-scalar-chart-lift
```

Expected direct marker:

```text
PASS_PR6030_SCALAR_CHART_LIFT adds=18404 scales=861 copies=23 moves=3453 inits=31 clears=31 common_chart_violations=0 copy_into_empty=23 peak_owned=13 owned_fields=29 public=770 events=22803 phase_width2_only=true no_new_kappa=true
```

The checker rejects a cross-chart synthetic `ADD`, a stale frame tag after `MOVE`, a zero coefficient, a `COPY` into a nonempty owned row, and a one-step retag of the first selected `ADD`. It checks Pauli `X`, a shear and `[[2,3],[5,7]]` at widths 1, 2 and 3. Those widths are controls on the tensor code. The all-`f` argument is the induction in [PROOF.md](PROOF.md).

Not run: `make frontier6030-verify`, the primary native replay, Lean, and any proof of `MOVE` operators.

## Open next questions

1. Do the 3,453 `MOVE`s of this same word equal `(chart_b^{-1} chart_a)^{(⊗)f}` as group elements, including absolute phase `i^{p f}`? #6293 records the phase factor and leaves the joint lowered recipe open. The first step is one lowered recipe with `p ≠ 0` against `U^{(⊗)f}`. Blocked because the primary native payload is not an input here.
2. Does the empty-`COPY` chart identity survive the retained tape and erasure model at width `f`? The first step is one `INIT`/`COPY`/`CLEAR` triple in that model. Blocked by `owned_erasure` and `precision_tape`, which this note does not use.

## Credit

The selected word is DreamingOfClouds' PR #6030. The chart convention and the scalar induction are the ones recorded for the older #5599 word in `research/native-scalar-chart-lift` (unpaidmoon, PR #5837), which explicitly leaves a different word open. #6293 (unpaidmoon) is the `MOVE` phase factor on this word, not the scalar events. The width-1 endpoint replay is `research/p104-6030-independent-audit` (JosieElliston). The selected review is `docs/research/pr-intake-evidence/pr6030-audit/PROOF-REVIEW.md`. #5442 (Mark / Matarener) is the group-algebra half for the older #5413 caller.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
