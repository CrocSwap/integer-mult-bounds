# Independent review evidence

[REVIEW.md](REVIEW.md) reviews the exact sensitivity theorem and its explicitly conditional precision-to-cost inference. [invariance/REVIEW.md](invariance/REVIEW.md) independently derives the moving-frame delta-zero specialization and checks every actual event. These are separate agent checks within the author process; no independent human or formal proof-kernel acceptance is claimed.

The optional recount uses **NumPy 2.4.5**, tested with CPython3.13.7. It performs exact integer arithmetic on a fixed dyadic grid, checking every division and bounding every product/sum before using signed64-bit integers; this is not floating-point evidence. Its separate single-fault trajectories use Fraction. The moving-frame checker needs only Python's standard library. Neither imports the producer checker or a predecessor evaluator. The primary registered checks do not require NumPy.

From repository root, use fresh output destinations:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B research/two-full-border-paid-precision/independent-review/invariance/check_invariance.py --source research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz --out /fresh/INVARIANCE.json
PYTHONDONTWRITEBYTECODE=1 python3 -B research/two-full-border-paid-precision/independent-review/independent_exact_recount.py --source research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz --receipt research/two-full-border-paid-precision/paid-sensitivity/PAID-SENSITIVITY.json.gz --out /fresh/EXACT-RECOUNT.json
```

Expected markers are `PASS_INDEPENDENT_LOGICAL_ZERO_ADDRESS_AND_FRAMES` and `PASS_INDEPENDENT_EXACT_SENSITIVITY_RECOUNT`. Frozen receipts are included; each checker binds its own source bytes. The NumPy receipt records an input container hash as provenance plus its decompressed payload hash; regenerated gzip bytes do not determine mathematical equality. This review's final source replay and receipt controls used CPython3.14.5 under isolated optimized mode.

`invariance/source/PINS.json` identifies inherited physical definitions read during the audit. They are provenance, not imported runtime dependencies, and their original files remain in the repository. The exact source word is the only live input to the standard-library audit. See [NOTICE.md](NOTICE.md) for attribution.
