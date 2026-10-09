# Partial-gauge reproduction

This extension inherits PR #104 at
`948ce1510df750f4c18b96bdaef436a86f8bf834` and gives the conditional saving
`7237/78125000 = 9.26336e-5`. Proofs are supplied as LaTeX source.

From the repository root, with Python 3.11+ and a C++17 compiler:

```sh
make partial-gauge-verify
```

CI runs this extension in its own `partial-gauge` matrix group. The
incremental target performs three checks:

- `partial_gauge_bit.py` checks pinned PR #97 source hashes, reconstructs
  auxiliary and data ranks from its actual frozen paths, matches the physical
  ledger receipt, and rebuilds the whole-projector child list. The unchanged
  upstream complete-basis scalar and rational frame audits are inherited.
- `partial_gauge_producer.py` rebuilds the selected h24 interval/cube DAG,
  compatible matching, backward enlarged frames, physical word and partial
  source gauges. Independent checks cover exact supports and signed decoder,
  frame nondegeneracy and nesting, center closure, untouched source roles,
  reverse readout order and every positive-rank transition. The deterministic
  construction also reproduces the complete histogram, including zero-rank
  no-ops; see [the producer guide](../scripts/partial_gauge/README.md).
- `partial_gauge_network.py` certifies both strict moments, the stopped
  ordinary-bit saving, denominator-21 semantic charge, product row stock,
  all 47 strict constraints and seven assembly margins. It writes the
  deterministic, source-bound `certificates/partial-gauge-network.json`.

For arithmetic and the pinned bit profile alone:

```sh
make partial-gauge-certificate
```

Generated complex graphs are temporary by default. To retain them and a
compact report outside the repository:

```sh
python3 scripts/partial_gauge_producer.py --work-dir /tmp/partial-gauge-work --output /tmp/partial-gauge-verification.json
```

The selected proof is [partial-gauge-note.tex](../notes/partial-gauge-note.tex).
The source notices and compact PR #97 witness remain under
`references/partial-gauge/`. Unselected experiments, large generated graphs,
recursive handoff copies and PDFs are excluded.

## Shared source bindings

The joint-dual manifest also binds `Makefile`, `README.md` and `NOTICE`.
This round refreshes those three digests and the two derived certificate
digests. Its producer, physical words, frame profiles and mathematical
certificate fields are unchanged from PR #104's successful local replay.
Incremental validation checks that equality and reruns the joint arithmetic;
it does not repeat the unchanged graph and complete-basis suites.

After reviewing changes to those shared files, the explicit manifest refresh
is `python3 scripts/experiments/pin_joint_dual_sources.py`. Its derived
`joint-dual-kappa.json` and `joint-dual-validation.json` must also be updated.
The full affected replay command, when needed, is `make verify-joint`.
CI checks the committed source bindings and requires deterministic output;
it never silently repins sources. Stage the final artifacts before the
reproducibility check and require `git diff --exit-code` to remain clean.
