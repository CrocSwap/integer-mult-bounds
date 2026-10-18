# Local validation

Base and final refreshed main: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
PR1255 remained OPEN at exact head `add1e2673ef000c097ec0fd70058e644af048d6b` in the pre-submission refresh.
The selected record and live gate input did not change.

- CPython 3.12.13: complete registered package passed, including seven test groups.
- CPython 3.14.7: verifier, optimized package tests and relocated execution passed.
- `python3 scripts/research_package.py --package research/orthogonal-phase-defect-spectrum --check-only`: metadata and Git/source pins passed.
- `python3 scripts/verify_selected_result.py`: selected record, exact kappa, original source inventory and proof supplement passed.
- `python3 -B -m unittest discover -s tests -p 'test_research_*.py'`: 20 tests, one existing skip.
- `python3 -B -m unittest discover -s tests -p 'test_selected_result.py'`: five tests passed.
- `git diff --check`: passed; upstream and selected artifacts unchanged.

Mathematical receipt SHA256: `4e97f70ff42338630cea337a6d6231925cabbd6a063d5473dfc14ca9ed0a0ff7`.

The seven package test groups include five real on-disk rejection cases: incorrect fiber size, Boolean substituted for an integer count, a missing defect fiber, modified predecessor receipt and modified inherited gate source. The optimized verifier retains explicit `require` checks. The certificate is compared as canonical JSON text, so JSON numeric-type substitutions cannot pass via Python's `True == 1` behavior.

Finite coverage: 23,817 complete matrices in dimensions1–6; all 271 attainable defects in dimensions1–9; 187,868 literal Gaussian-integer coefficient comparisons across both signs; 1,022 direct Gaussian character sums; 2,804 cocycle pairs. The companion brute-force oracle admits all binary matrices through dimension4, without the transversal recurrence. Larger exact counts follow from the written proof, not a larger matrix enumeration.

Final live overlap search: 792 open PR bodies and 21 Discussion threads with up to five recent comments each, all returned in the requested limits. Exact predecessor and latest main heads were refreshed. No matching defect-spectrum or transvection-factorization claim was found. Literal search is bounded overlap evidence, not a novelty certificate. The local claim is the donor-authorized fallback because no pinned coordination issue exists.

Not run or claimed: full selected cold replay, native supplier/controller admission, physical cost model, Lean, external human review or hosted CI success. This package makes no selected construction change.
