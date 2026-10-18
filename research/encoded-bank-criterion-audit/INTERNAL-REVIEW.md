# Internal review and resolution

Two focused native Codex subagents supported this audit. This is separate AI
checking under shared model assumptions, not independent human review, maintainer
acceptance or formal-kernel verification.

The verifier derived the criterion, weighted dimension argument and C5 exclusion
from the explicit model before inspecting PR2872's proof. Its derivation is in
AUDIT.md. It then implemented the rational centralizer witness without importing
predecessor code. The lead authenticated the input tree and replayed all three
predecessor command bodies; exact pins/output are in SOURCE-REPLAY.json.

The skeptical reviewer read a frozen package and the exact source proof. It found
no substantive mathematical or executable defect. It independently enumerated
all labeled paired words through four columns, using swap-connected components
and recursive deletion rather than the new piling routine. Its portable
`review_words.py` retains that oracle, comparing 162,014 cases with the new checker
and its receipt. It is now a registered command. The reviewer also independently
authenticated all 13 source Git bindings and both provenance files and checked
the centralizer fixture via matrix-unit commutators, exact kernel membership and
ranks modulo 101/103. Those finite-field ranks were used only with exact rational
nullspace witnesses; none is a statement about all complex representations.

Two low-severity wording issues were resolved:

1. The main census uses canonical paired words up to global relabeling. README
   and VERIFY.json now say this explicitly; the all-graph census and independent
   fully labeled check support the symmetry reduction.
2. The empty-schedule rejection in AUDIT.md belongs to the source package's
   `verify.py`; the new checker deliberately includes the empty word. The text
   now names the source package explicitly.

Neither finding required changing the two mathematical checker implementations.
The portable reviewer script changes only location/output plumbing from the
reviewer's scratch version and omits its separate local-Git authentication stage.
The final narrow review confirmed AST identity of all six retained functions
and unchanged hashes for the first two checkers. The lead then completed the
final three-command replay and relocated/read-only check of the third script.
The tested environment is Linux; the reviewer script uses Unix resource metrics.
It imports this package's checker only for comparison; its rewrite oracle does
not use that checker's piling, crossings or word enumeration.

Reproduction:

```sh
python3.12 scripts/research_package.py --package research/encoded-bank-criterion-audit
```

The lead additionally ran both receipt corruptions (expected nonzero exits),
optimized relocated Git-free/read-only replay, source-byte preflight, and final
upstream/overlap checks. Validation scope and results are recorded in
VALIDATION.json. Native costs, physical caller implementation, the full selected
cold replay and the complete multiplication theorem remain unreviewed.
