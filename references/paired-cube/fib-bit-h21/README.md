# h = 21 bit word with Fibonacci-oriented strips

Prepared by eumemic with Anthropic Claude assistance. Apache-2.0.

`witness_21.json.gz` and `deferred_21.json.gz` are an h = 21 bit word in PR #97's frozen format. They are read by
PR #97's unchanged `deferred.py`. The word has v = 1330, R = 21526, 8910 deferred readouts, 8590 V-leaf slots,
16628 links and 1120 late nodes. Its lifted frames are M_n = U_n.

- **DAG.** The DAG is a native h = 21 rebuild of the round-seven PR #62 lineage (Swapnil Jain's interval strips,
  #41 order), with Fibonacci-oriented level-zero strips.
- **Compiler.** The B-defer compiler uses weighted links. Every link satisfies span(donor) ⊆ span(user), the
  combinatorial criterion of the round-seven `check_lifted` (enforced inside the matching, `STRICT_LINKS=1`).
- **Reproduction.** `producer/` holds the producer and exporter:
  `STRICT_LINKS=1 BIT_H=21 FIB0='9=2:1,3:2,5:2,8:5' python run_producer.py <dir> dag.json;
  python export97.py dag.json OUT`.
  The matching needs numpy/scipy.
- **Gauge subset.** `selection.json` is the gauge subset in #144's format, in inherited readout order: 7575 gauges
  retained and 1335 omitted.

## Checks run on this word

- **Literal ledger.** `bit-ledger-result.json` is the output of PR #97's `round7_literal_frame_ledger.py` at h = 21.
  It reports complete forward and reflected F2 scalar words, reflected frame continuity, equal frame keys at
  every scalar gate and the external histogram.
- **Round-seven checkers at h = 21.** `check_word` passes: schedule semantics, garbage coefficients, phase one,
  release rule, dirty-scratch replay over F2 and Z, and negative controls.
  - `check_lifted` passes: dirty-scratch replay over F2 and Z, j-monotonicity, link spans, and a chain histogram
    equal to the witness's claim.
  - `check_frames` passes every frame, nesting, nondegeneracy and side-lemma check.
  - Its only failure is the regression pin to round seven's constants.
- **Independent B-defer replay (stages one and two).**
  - Frames hold by exact inclusion.
  - Scalars are checked over F2 on the complete basis: y_T += x_T, and every slot is restored.
  - The paid multisets of the two stages are equal.
