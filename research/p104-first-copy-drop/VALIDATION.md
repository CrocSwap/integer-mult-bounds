# Validation and handoff

Experimental base: `c0e3631dc24e3c24a861f7d3d79e0608481cccec`.
Environment: Linux, CPython 3.14.7. Only the new scoped package is changed.
Exact source paths, base Git pins and SHA256 values are in SOURCES.json.
All seven copied source/context inputs match their pinned Git bytes.

Commands:

```sh
python3 -I -O -B research/p104-first-copy-drop/test_package.py
python3 -B scripts/verify_selected_result.py
python3 -B -m unittest discover -s tests -p 'test_selected*.py'
git diff --cached --check
```

The focused package passes exact regeneration, read-only relocation to a
path with spaces, and four actual subprocess controls: corrupted threshold,
corrupted COPY invoice, changed predecessor bytes and occupied output
preservation. The primary's pinned predecessor module runs in a child with
assertions enabled. The independent verifier and its mathematical checks
use explicit failure conditions and pass under optimized Python.

Completed finite coverage: 1,260 disjoint frames, 896 admissible frames,
7,168 exact decoders, 28,672 possible unordered terms, 3,655,680 support-cut
incidences and 7,282,688 quotient-cut incidences. The independent checker
reconstructs the model and matches each frame record using a binary column-
code enumeration. The attainment checks all 6,724 surviving scalar pair
coefficients, all eight COPY ranks, 22 individual port restorations, the
support-only counterexample, an invalid decoder and the exact ratio screen.
There are 25 mathematical controls.

The certificate does not enumerate every arbitrary port subset. The written
quotient/hyperplane-cut lemma proves why all rank-losing subsets contain one
of the enumerated cuts, supplying the completeness argument for the threshold.
No failure to find a candidate is treated as a global impossibility theorem.

Selected-record source inventory and proof binding pass, and all 25 related
repository tests pass on the exact base. Staged whitespace and package-only
scope checks pass. The submitted package is also exported from the Git index
for final verification; its exact receipt is in VALIDATION.json.

Repository-wide regeneration, selected-supplier cold replay, physical tape/
hosting execution, remote CI, human peer review and a full formal theorem
are not claimed. No selected supplier or upstream source is edited. The
result concerns an exact geometric COPY price and first-drop threshold;
all source-access, helper, frame, restoration, precision, compiler and analytic
obligations of a future physical supplier remain open or inherited.

The refreshed 790-open-PR inventory through #1178 and targeted all-state
puncture query found no competing preserved-frame P104 threshold. PR1020's
unconstrained pair threshold, PR1125's delivery bound, and PR1171's root-only
star decoder are distinct. PR1171's body explicitly excludes non-star
decoders. No pinned coordination issue exists; the claim and final result
link are recorded locally. See OVERLAP.json and CLAIM.json.

Original contributor/license and AI-assistance notices are retained.
Prepared by Cinna Davis with substantial OpenAI Codex assistance.
