# Validation and reproducible scope

Research base: canonical main `f9f85c1e4fa1e955ff39f10fca447e3e2a4e4adc`.
Selected record: conditional `23/10000`, unchanged.
Environment: macOS 27.0.1 arm64; registered replay with Python 3.12.15,
secondary isolated optimized checks with Python 3.14.7; standard library only.

## Passed scientific checks

```sh
python3.12 -B scripts/research_package.py --package research/adaptive-gate-existence
python3.12 -I -O -B research/adaptive-gate-existence/verify.py
python3 -B scripts/research_package.py --package research/adaptive-gate-existence --check-only
```

- Exact abstract critical-root witness, covering an entire exponent interval,
  all mirror cells, the base range and the shifted-logarithmic funding guard.
- Exact symbolic checks of the two new mirror-integral identities on square-rank
  fixtures, mirror endpoint conventions and a cell with exits but no source.
- Nine deliberate failures of the abstract witness, plus twelve source-profile
  failures, including false roots, mirror violations and underfunded logarithms.
- Twenty-five rational-root enclosure controls and 48 algebraic controls for the
  separately written fixed-grid logarithm/exponential evaluator.
- Source-bound p7 and p16 root isolation, uniform mirror/mean checks and explicit
  quantitative majorants at the actual roots, with every parameter guard funded.
- p16 compact-consumer and native paid/productive inventories match exactly.

`verify.py` prints a complete deterministic JSON receipt. The displayed U/V/Q
intervals enclose conservative upper estimators; `D_lower` encloses the certified
lower estimator. They need not enclose an actual extremum of the analytic
function. The written proof supplies all-rank and all-parameter arguments.
Finite checks do not substitute for those arguments.

## Mathematical review

Separate author-side agents checked the new crossing implication, the weighted
mirror integrals, the exact fixed-exponent feasibility criterion, the critical
endpoint and complete induction. Another pass checked the interval arithmetic,
source lineage and the unknown-root quantitative certificates. The strengthened
counterexample came from that adversarial review. No unresolved defect was
identified. These are AI-assisted author reviews, not formal-kernel verification
or independent human acceptance.

## Publication checks

After committing, run:

```sh
python3 -B scripts/check_research_commit.py --package research/adaptive-gate-existence --check-source-history
python3 scripts/export_research_package.py export --package research/adaptive-gate-existence --ref HEAD --output /tmp/adaptive-gate-existence.tar
python3 scripts/export_research_package.py check /tmp/adaptive-gate-existence.tar
```

The direct verifier consumes only package files and the six declared inputs;
it requires neither Git nor network access. The generic registered runner
separately needs Git history to authenticate historical card/source provenance.
A 15-file export from scientific commit
`1a623ad2c268b2b23878bc0cc3cf0f67b4b1b5fa` passed integrity and direct
Python 3.12.15 replay with `PATH=/nonexistent` under a macOS per-process
`deny network*` policy. Changed predecessor bytes and an underfunded logarithm
were rejected in copied exports; original inputs stayed unchanged.
Final publication results are recorded in `TASK.json`.

## Remaining obligations

No predecessor native or outer producer suite was rerun. The abstract fixture
is not a native word. Native all-column semantics, owners, whole-job adapters,
restoration, chronological divisible widths, movement, precision, stock,
fixed-tape execution, analytic transfer and exact recovery remain inherited.
The result is a conditional leaf-count theorem with explicit certificates;
there is no new selected κ, materialized winning word or practical threshold.

## Shared hosted-planning limitation

The earlier #4521 [hosted run](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/39716553034/job/119619920401)
stopped before package replay: four shared `test_research_current_status`
failures concerning the CI target, selected decimal formatting and historical
navigation. The affected files are byte-identical on canonical main and both
research branches; six focused local tests reproduce the same four failures.
This was already [reported for #4448](https://github.com/CrocSwap/integer-mult-bounds/discussions/4443#discussioncomment-19109289).
An upstream navigation repair and hosted rerun remain separate obligations.
The local registered pass does not imply a hosted CI pass.
