# Validation receipt

Base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.

## Current selected construction inspected

`certificates/selected-result.json` identifies a maintainer-reviewed conditional finite construction with kappa `836330098538459/500000000000000000` (`0.001672660197076918`), complex-binding. The active review is `docs/research/community-batch1099-review.md`; its pinned source manifest is `research/community-frontier1094-audit/SELECTED-SOURCE.json`; its assembly certificate is `research/community-frontier1094-audit/ASSEMBLY.json` with SHA-256 `1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045`; the registered reproduction instruction is `make frontier1094-verify`. This interface package changes none of them and claims no new kappa.

## Checks run

- `python3 -I -O -B research/universal-connector-boundary/verify.py` — `PASS_UNIVERSAL_CONNECTOR_BOUNDARY pairings=945 max_coverage=31 queries=74 leaves=182`.
- `python3 -I -O -B research/two-projection-connector-seed51a5/verify.py` — `PASS_TWO_PROJECTION_CONNECTOR words=945 assignments=30240 full_covers=175 source_calls=10 readouts=62 calls=72 frame_xors=10 children=180 baseline_children=182 saved=2`.
- `python3 -B scripts/research_package.py --package research/two-projection-connector-seed51a5 --check-only` — `PASS_PACKAGE_METADATA_AND_PINS`.

The exact local replay ran under CPython 3.14.7 and uses only standard-library features available from Python 3.10. The registered package runner currently requires Python 3.12, which is not installed in this environment; that runner's mathematical replay was not run. The full selected-result reproduction and repository-wide CI were not run because this package does not alter the selected assembly.

## Scope

The verifier checks the complete 30,240 path/direction census, the explicit 31-row boundary table, the exact arbitrary-dirty formal map, both helper restorations, the shortest 10-XOR frame invoice for the pinned boundary table, the pinned child prices and four failure controls. It does not establish a selected supplier occurrence, a finite-size runtime win, or a bound on the optimal number of frame XORs.
