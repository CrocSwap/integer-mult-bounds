This directory contains the selected retained-total triple producer, adapted
from the October 2026 partial-swap research handoff. The underlying pair and
shared-point modules originate in jacklightChen/integer-mult-bounds commit
6725c6a17b17871a35353fd29157f4ed851bc114 (CrocSwap PR7). Modifications are
copyright 2026 icekylinx, Apache-2.0, made with AI assistance.

Run from the repository root:

```sh
python scripts/partial_swap_producer.py --output certificates/partial-swap-producer-check.json
```

Python 3.10+ and a C++17 compiler are required. `CXX` or `--cxx` selects the
compiler. The default command generates all three selected dimensions
25, 23, 57 and derives the complex h=28 histogram from `paired_complex.py`,
which supplies the selected paired producer in the `complex_circuit.py` interface.
It compares every selected count and every histogram entry to
`certificates/partial-swap-input.json`, raising on disagreement. Successful
stdout (or the specified output file) contains the complete generated results.
Progress and matcher phases go to stderr. Large binary intermediates and
compiled matchers are temporary by default; `--work-dir /tmp/partial-swap`
retains them. `--dimensions 23 --skip-complex` selects a smaller diagnostic run.

`paired.py` parameterizes the weighted pair recursion with base threshold two;
`shared.py` accepts the aligned point order as an ordinary constructor parameter.
There is no runtime source rewriting. `graph.py` retains each common-point total
and its ancestors before pruning the global DAG. The first matcher exports the
original envelope continuation dependencies. `positive.py` propagates output
constraints backward through equal-envelope classes and those dependencies,
then stops after writing the enlarged labels. The research script's alternative
dense-macro candidate is deliberately absent. The second matcher uses enlarged
rank, original rank, and event number to preserve the dependency order.

Both matchers retain the archived deterministic Hopcroft–Karp traversal order:
increasing donor node, first operand before second operand, consumers before
designated outputs. Binary headers and payloads are explicitly little endian
on all supported hosts. No archived binary graphs are needed or stored here.

The complex histogram derives ranks from coordinate-cover sizes for disjoint
sum nodes and independent triple counts for pair stars. It counts producer
transitions and adds three full-rank transitions per center role. Data growth
and outer macro transitions are excluded from this per-invocation histogram.
