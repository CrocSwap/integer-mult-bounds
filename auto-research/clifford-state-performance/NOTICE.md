# Attribution and scope

Prepared for Charles Bethin with substantial OpenAI Codex assistance.
New code, tests, and documentation use the repository's Apache-2.0 license.

The evaluator preserves the Gaussian-dyadic formulas from the pinned `clifford_exact.py`.
It derives the permutation and phase tables from those formulas.
The original source remains unchanged at the path recorded in `SOURCE.json`.
Its enclosing license and notice remain at:

- `research/complex-multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/LICENSE`
- `research/complex-multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/NOTICE.md`

That notice credits icekylinx, OpenAI assistance, and the retained ancestry for the Clifford compiler and scalar routines.
The wrapper adapter credits DreamingOfClouds with Claude assistance and chafreaky's PR458 wrapper construction.
The PR622 native provider artifacts retain Jeremy Kothe's K-triangle lineage and preceding contributor credits.
The unchanged helper checker and selected review retain their original authorship.
This package does not replace any upstream attribution.

PR154, PR367, and PR452 provide related verification performance work.
They are not dependencies of this adapter.
PR581 provides a distinct, scoped Lean identity proof.
This package claims neither a new bound nor a formal multiplication proof.
