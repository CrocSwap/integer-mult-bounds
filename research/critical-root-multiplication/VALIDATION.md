# Validation and limits

Environment: Python 3.12 on macOS. This package was prepared on exact PR4532 head `644607ba59ebe401ac7ecd627ae7f331f924d1b0`; canonical main was `f9f85c1e4fa1e955ff39f10fca447e3e2a4e4adc`.

Completed:

- PR4532's exact registered arithmetic witness, including the p16 root application; all pinned source bytes matched and its p16 invoice matched PR4470.
- Fresh PR4470 `verify.py --part dependencies`: retained native query interfaces and ordinary BIT admission 0.0034 passed.
- Fresh PR4470 `verify.py --part native`: both 632-column arbitrary-input replays and all 423 new/helper physical frame pairs passed.
- `scripts/research_package.py --package research/critical-root-multiplication --check-only`: metadata and pins passed.
- The complete registered package command: dependency, native and new arithmetic gates passed in sequence, ending `PASS_REGISTERED_RESEARCH_PACKAGE research/critical-root-multiplication outcome=completed`.
- New arithmetic authoring/default comparison under `-I -O -B`; explicit rejection checks remain active with assertions disabled.
- Separate author-side agents checked the source-bound moment, finite logarithmic absorption, full outer ledger and conditional finite-template proof. This is AI-assisted cross-checking, not independent human review.

A final source-manifest strengthening and explicit finite-envelope arithmetic were added after the full replay. They do not change the native word or dependency implementation. The final metadata and arithmetic checks are repeated; the unchanged heavy gates are not rerun merely for those additions.

The finite arithmetic does not prove PR4532's theorem, the general finite-template closure theorem or the inherited native, physical, analytic and recovery premises. The proof explicitly assumes those contracts. The winning finite word and its enormous constants are algorithmically specified rather than materialized. No overall numerical multiplication threshold, practical speedup, formal proof or selected-frontier admission is claimed.

Hosted CI has not been asserted to pass. Predecessor submissions report upstream navigation/planning failures; local replay results must not be confused with hosted replay or scientific acceptance.

Published-head follow-up: hosted run 39721672717 failed on four unchanged current-status/navigation tests before research replay. The 77-file committed export, archive validation and extracted isolated arithmetic check passed. PR4536 independently reproduced its checked arithmetic and noted the different evaluation points of the two absorption margins. The reporting-only follow-up adds explicit cutoff labels, with unchanged numerical values and proof. Metadata/pins and isolated optimized arithmetic checks are repeated for this clarification; the unchanged native/dependency gates are not rerun.
