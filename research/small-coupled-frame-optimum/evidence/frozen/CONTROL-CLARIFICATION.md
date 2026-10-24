# Original control labels

The immutable fixed-C receipt's `dropped_edge_histogram_rejected` label means that deleting one known positive-rank mapped edge changes the recomputed full invoice. The implementation constructs that decremented histogram and checks inequality. It does **not** feed a mutated factor inventory into a separate validator, so the label is stronger than the control performed. REPORT.md describes the actual histogram-change check.

Likewise the map-to-identity control exhibits an actual original edge for which the source subspaces fail containment under identity, although they pass under the retained native map. It tests that containment predicate directly rather than rerunning a mutated optimization. The bad-assignment control does run the full graph validator and requires rejection.

The independent reviewer is adding private-copy factor/inventory mutation controls. These should be identified as independent evidence, without retroactively attributing them to the frozen author run. This clarification changes no source, optimizer, selected assignment, comparison certificate or fixed-C receipt.
