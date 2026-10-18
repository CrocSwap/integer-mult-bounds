# NOTICE

Research package `research/r439-z3to2-seed13`, prepared with help from
opencode. Apache-2.0 (repository license).

Predecessor work this result builds on and does not supersede:

- The word itself: DreamingOfClouds' PR589 (tuned punctured R439 word) on
  eumemic's PR555, with the PR543/PR545/PR510 lineage. The base word file is
  used unchanged; only gate lists A/B and the rebuilt cleanup C differ in the
  candidate.
- The transvection (Steinberg 3->2) relation and its use as a word-rewrite
  mechanism: Dugongue's PR541/PR548 move families on the R480 word and PR589's
  own tuner (`research/e8-bit-p111-tuned/tune/tune.py`). That tuner optimizes
  the paid moment to a fixed point and records that its Steinberg step has
  "nothing to apply that lowers the moment"; it does not optimize ADD count, and
  equal-moment rewrites are outside its greedy objective. This package's delta
  is the ADD-count objective with exact register-level commutation windows and
  the unchanged-profile/unchanged-paths acceptance gate.
- The record-format contract and exporter: `export_records.py` (Dylan Crow) in
  `research/e8-bit-carrier-skeleton/code/bit/`, used as a subprocess cross-check
  only.
- Prior finite block ADD-count results on the same word (PR873, PR973, PR986,
  PR1001, PR1002, PR989, PR980, the r439-bsection-survey and
  r439-frame524-seed13 packages, and concurrent PR1015 and follow-ups) work the
  phase-B blocks with donor/factor/multi-write programs. This package changes
  none of those blocks and is not additive to them by construction: each result
  is measured against the same committed base word.
- Concurrent PR1122 (bitplane; same track and a coincidentally identical
  assignment seed, different agent) composes the frozen PR980/PR1062 changes on
  the semantic-D word lineage. Its object, word and mechanism are different and
  its numbers are not additive to this package's; these 3->2 rewrites are
  candidates for that lineage as future work.
- The duplicate-pair (paired-transvection) census here is the bit-word
  counterpart of the program-identity audits in those packages; it is reported
  as coverage, not as a separate claim.

Substantial AI assistance is disclosed as required by CONTRIBUTING.md.
