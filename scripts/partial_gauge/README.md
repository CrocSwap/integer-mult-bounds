# Selected partial-gauge complex producer

Run `python3 scripts/partial_gauge_producer.py` from the repository root.
Python's standard library and a C++17 compiler are required. The command
regenerates the selected h = 24 scalar DAG, compatible carrier matching,
backward lifted frames, physical word and partial source gauges. It compares
every field of `certificates/partial-gauge-complex-input.json` and performs
independent finite checks. Intermediate graphs are temporary unless
`--work-dir DIRECTORY` is supplied; `--output FILE` saves the compact report.

The selected counts are 146,284 additions, 120,097 matched carriers,
34,307 auxiliary roles and 6,341 selected partial source gauges.

`interval.py` extends the existing `PairedTriple` and
`PairedExclusionCircuit` implementations. `cube.py` overrides the triple
assembly with the selected pair-first cube. `scalar.py` retains only the
selected h = d = 24 rational-center construction. `match.cpp`, `lift.py`,
`word.py` and `select.py` build the actual finite program. The superseded
whole-birth selection is omitted: the physical word supplies only operations,
sources, root roles and the retained-center closure. Final readouts use
`selection.json` in **reverse selection order**.

`verify.py` independently checks every scalar DAG addition and output support,
the signed coefficient identity and divisor 21, nondegeneracy and old-frame
containment, dependency and carrier nesting, an exact support replay of M,
the center-phase closure and selected untouched roles. It executes the reverse
readout order, checks actual subspace containment and recounts target-data
transitions. It also recounts every positive-rank internal transition directly
from the physical word. Zero-rank no-ops have different literal multiplicities
in the per-role replay; the complete selected histogram, including its zero
bin, is reproduced by the deterministic construction and compared to the
certificate. Partial first transitions retain rank r minus dim(sigma), and
the selected source exterior is m minus h plus dim(sigma).

Boolean readout support is the conservative support of the exact rational
matrix C = J M; it is used only to impose sufficient frame constraints.
The scalar identity is checked from exact root supports, not inferred from
Boolean cancellation. These finite checks do not establish the inherited
analytic, semantic-precision or fixed-tape interfaces.

Adapted from `round6_work/complex_{interval,cube}_experiment.py`,
`complex_terminal_counts.cpp`, `complex_maximal_lift.py`,
`complex_deferred_readouts.py`, `complex_partial_deferred_readouts.py`, and
the preceding `round5_complex_rational_centers.py` in the round-six handoff.
The cube override derives from the retained `scripts/paired_triple_circuit.py`.
Copyright 2026 icekylinx, Apache-2.0; see the repository NOTICE and source registry.
