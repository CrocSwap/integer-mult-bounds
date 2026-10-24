# Repository baseline checks for external review

The baseline repository sweep is **INCOMPLETE_TIMEOUT**; the independently run selected gen4 target is **PASS**. These checks supplement the standalone Lean replay receipts. They do not establish a larger bound or formalize the full multiplication theorem.

Both commands used isolated `git archive` copies of commit `f7330c5f5b1c5e85f91a98c95e8efc0e27c03490`. They did not run in the working repository: the Makefile warns that its verification groups regenerate shared outputs. No generator or mathematical source was edited, and no environment fix was needed. All 20 tracked `upstream/` files in each archive still match their pinned Git blobs.

| Command | Isolated archive | Limit | Elapsed | Result |
| --- | --- | --- | --- | --- |
| `make verify` | Full-sweep archive | 600 s | 600.715 s | INCOMPLETE_TIMEOUT; process exit -15 |
| `make gen4-bank-verify` | Selected-check archive | 600 s | 402.189 s | PASS; process exit 0 |

The full sweep completed `verify-community`, `verify-producers`, `verify-partial-gauge`, `verify-three-stage-cover`, `verify-paired-cube`, then reached `verify-recycled-bit`. A supervisor sent SIGTERM at the agreed ten-minute limit. Any resulting Make “Terminated”/“Error” lines are interruption reports; the unfinished sweep is not a pass. The independent selected check used a second archive and its own ten-minute budget.

The original full-sweep runner automatically attempted a selected-target fallback after interruption. The supervisor cancelled that duplicate promptly; its separate log and process receipt are preserved. It is not the independent selected check reported above.

The selected verifier passed all nine stages: banks, bit, complex, finite, math, primes, raw, scalar, and virtual. Its complete [verification report](review-receipts/external-repository/gen4-verification.json) records unchanged inputs and the stage-omission negative controls.

Selected-target final progress:

```text
00:30:42 UTC  banks PASS 78.3s
00:30:42 UTC  Checking every complex source label and paid child.
00:30:43 UTC  Deriving both complex scalar words and temporary lifetimes.
00:30:47 UTC  Merging scalar events, exact frames and all final climbs.
00:31:30 UTC  Recomputing complex cover, router, precision and row inequalities.
00:31:30 UTC  complex PASS 48.1s
00:31:31 UTC  math PASS 0.7s
00:31:31 UTC  finite PASS 0.2s
```

Environment: Python 3.12.14, SymPy 1.14.0, GNU Make 4.4.1, Git 2.52.0, GCC/G++ 14.2.0, pdfTeX 1.40.26; Linux x86_64. The selected verifier's required Python/SymPy versions were already available.

Evidence: [summary](review-receipts/external-repository/summary.json), [full-run receipt](review-receipts/external-repository/receipt.json), [selected-run receipt](review-receipts/external-repository/selected-receipt.json), [supervisor decisions](review-receipts/external-repository/supervisor-receipt.json), [full log](review-receipts/external-repository/verify.log), and [selected log](review-receipts/external-repository/gen4-bank-verify-isolated.log). The summary records log hashes, generated selected-stage artifacts, and the `upstream/` comparison.

These are historical checks. Commit citations in some evidence copies were
subsequently replaced after the Git identity rewrite. Recorded log hashes still
identify the original bytes; the separate
[historical metadata record](https://github.com/cheesegrader/integer-mult-bounds/blob/377012d9e1d350c29fc47669e82415249429f60c/research/lean-external-review/validation/metadata-reanchor.json)
binds them to the published log copies. No repository checks were rerun for
that metadata correction.
