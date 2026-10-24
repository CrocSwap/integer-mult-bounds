# Validation record

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Base: `ff3cc58e370d0f678e529246f8c73e8094e18fcf`.
Runtime: CPython 3.12.13, standard library only.

The registered isolated, warning-strict commands passed in normal mode and
with `-O`. Both reproduced `RESULT.json` exactly. The receipt has 160 complete
program comparisons (40 equal, 120 different), 142 independent dense replays,
154 inverse-basis checks, four nested commutators, three nonshortest-word
zero controls, eight dirty-sandwich deletions and 14 rejecting input controls.
The stress case has 2^32 lowest-degree words, 66 states, dimension 33 and a
2,113-point proved grid. Its first trial succeeds. Forced-root examples need
2, 3, 5 and 8 trials. They do not establish a sharp grid bound.

Four code mutations were applied to separate copies. Every copy failed with
`--small`, in both normal and optimized modes, before source-hash or receipt
checks. A wrong lower Cayley sign and a forward-only inverse each failed the
independent dense endpoint comparison. A first-grid-point-only search and a
doubled, nonshortest coefficient word each exhausted the witness search.
The package files were not modified by these mutation tests.

The written proof was checked against the implementation. The critical
boundary is shortestness: a nonzero coefficient alone is insufficient for
the nonlinear substitution. The public negative checker proves the concrete
endpoint discrepancy and does not claim shortestness or least dimension.

No Lean build, independent human proof review, native tape replay, selected
cold admission, Docker replay or complete kappa calculation was run. This is
a local exact theorem/adapter check. The full-history publication wrapper
cannot pass in this shallow checkout. Source pins are retained in an ancestor
commit for a separate direct ancestry check and clean package export.
