# Searches after the fourteen target factors

All three searches use the repaired110-pivot/rank119 factored word with source hash7721fa65c554b99e739b775e0015a46bb31d9afedd2172b0ad807e7cbf160757. Each completed exact955-column/rational-frame replay, and none found an improving move. They differ from older searches on the unfactored word.

- Existing-frame descent:6324 mutable operations, then11684 connected pairs,32426 triples,106758 groups of four and391424 groups of five; no positive nominees.
- Extreme-frame descent: allow newly generated smallest/largest legal root-spanned frames,6324 operations and11684 connected pairs; no gains. This does not enumerate every intermediate subspace or all block sizes.
- Dependency-preserving delivery reordering:434 noncommuting pairs and1900 legal candidate frame choices; no gains. Target clean-operand support is included in nominations and checked in exact final replay.

[All exact results and source hashes](RESULTS.json). Scripts preserve the recipe but require the original inherited source packages and workspace layout. Do not repeat these same neighborhoods without a changed word, larger blocks, different ordering mechanism or objective.

The initial reordering attempt completed its local checks but failed writing its summary because an operand-loop variable shadowed the source Path. [Original failure](INITIAL-REORDERING-FAILURE.log) is retained; a fresh output run with the variable renamed completed. This is an execution/reporting failure, not an extra mathematical trial or infeasibility certificate.
