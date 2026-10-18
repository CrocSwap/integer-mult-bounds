# Replay the current-word optimum and literal review

Use Python 3.12 or later and the standard library. No numerical package, solver, network call or Lean compiler is required by these reviewers. Inputs are read-only and output paths must be fresh. From the package root:

```text
python -B review/review_current.py --package vendor/pr2857 --candidate data --claim CLAIM.json --field kappa --out ../t185-independent-review.json
python -B review/profile_lp_certificate.py --package vendor/pr2857 --candidate-profile data/PROFILE.json --out ../t185-independent-lp
```

Authenticate the complete source first with `python -B tools/verify_package.py --hash-only`, or use its full offline replay to run both reviewers together with construction and the separate root checks. The baseline is the unchanged PR #2857 package at head `0b2e2537b368a0cade07ce3f71452ea018ebe394`; its word, registry, source template and paid profile pins are checked again by the reviewers.

The first command checks every helper descriptor, source-event clock, strict idle window, family exclusion, mask, prefix, current paid profile and exact rational moment. Four malformed inputs are rejected. The second checks rational primal constraints, all 1,163 exact dual inequalities, symbolic objective equality, actual T185 attainment and the locally uniform root bracket. A forged dual price is rejected. Imported helper predicates are compiled directly from authenticated source bytes so stale bytecode is not loaded.

Recorded positive receipts are `REVIEW-FINAL.json` and `lp-final-01/{RESULT,PATTERNS}.json`. These supplementary checks do not replace the enclosing changed-native chains, phase/wrapper audits, generated hosted controller, compiler/precision invoice or complete outer release. Payload remains 2048. No local absolute path is required by these scripts.
