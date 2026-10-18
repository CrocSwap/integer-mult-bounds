# Executed validation

Base: `1f327c6f3e3a35271c5c141d381b540bab8ad005`.
Primary environment: macOS arm64, CPython 3.12.13 (Clang 22.1.3).
Cross-version environment: CPython 3.14.5 (Clang 21.0.0).
Standard library only; no dependency installation or predecessor executable import.

## Passing checks

- `python3.12 -B scripts/research_package.py --package research/shear-equivariant-rounding-seed70`
  checks historical Git provenance, all mathematical receipt fields, and eight
  focused tests under isolated optimized Python. Its final marker is
  `PASS_REGISTERED_RESEARCH_PACKAGE research/shear-equivariant-rounding-seed70 outcome=negative-result`.
- `python3 -I -O -B research/shear-equivariant-rounding-seed70/verify.py`
  also passes under CPython 3.14.5. The complete parsed receipt matches CPython 3.12 exactly; only deterministic JSON layout is used.
- `python3.12 -B -m unittest discover -s tests -p test_research_onboarding.py`:
  all 12 repository workflow tests pass.
- `python3.12 -B -m unittest discover -s tests -p test_selected_result.py`:
  all five selected-record tests pass.
- `python3 scripts/research_baseline.py`:
  `PASS_RESEARCH_BASELINE_BINDINGS_ONLY` for the selected PR1094 certificate;
  this is explicitly not a cold replay.
- `python3 scripts/research_package.py --package research/shear-equivariant-rounding-seed70 --check-only`:
  source/provenance and metadata validation pass.

## Mathematical coverage

The deterministic receipt SHA256 is
`cbf43fd9b3741d914936e0f83dd9826227274c2e535d052dbb6caf279978284b`.
It records 357,522 candidate seed outputs across 161 horizons, 402 attaining
orbits, 2,093 signed-power cases, 15,288 quantitative defect cases,
5,000 exact echoes, 5,000 rounded echoes (2,344 eager/carried disagreements),
10,000 literal group inverse cases, 931 compatible restricted-grid cases,
133 finite-order controls and ten named semantic controls.

The census includes every integer seed output that could beat its explicit
incumbent. Outputs outside that entrance box cannot improve the radius.
The written proof establishes all spacings, all finite error allowances and
all horizons; these finite checks are corroboration, not proof-assistant
verification or an impossibility extrapolated from failed search.

Focused tests reject deleted output alignment, deleted workspace/output returns,
missing source unload, a false 17-unit K70 radius, modified reference bytes,
a false source head and duplicate JSON keys. A relocated isolated optimized
replay from a path containing spaces passes with all input files read-only and
identical bytes before and after.

## Omissions and inherited boundary

No full selected supplier cold replay, actual PR1537 fixture replay, Lean build,
physical supplier/owner admission, numerical child implementation, complete
cost/precision/tape recurrence, hosted CI success or independent human review
is claimed. The retained exact rational construction is not refuted. The
conditional all-size/compiler, common-label/mutable-source, hosting,
precision/tape, exact-recovery, analytic and bit H1-H5 obligations remain.

Only this new research directory is changed. Source reference bytes,
`upstream/`, selected frontier, frozen packages and review ledger are preserved.
Contribution by Sricharan Vagvala (@theon199), with substantial OpenAI Codex
assistance; Apache-2.0.

## Publication refresh

Refreshed main `81e81af67714bdc8d1693b0bf5c29468b92f62ff` has byte-identical
selected-result.json (SHA256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`).
The final complete overlap snapshot covered 741 open PRs and 245 Discussion,
comment and reply records without warnings. PR1537 remains at the exact pinned
head. No matching rounding-orbit audit was found in that covered domain. This
is an overlap check, not a literature-priority claim.
