# Validation receipt

Research base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Final integration base: `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`.
Environment and mathematical execution receipts are in `EVIDENCE.json`.

The unmodified later PR279 verifier completed all nine mandatory stages in
1,096.765 seconds. It passed its target-prefix omitted-setup control, 11 scalar
controls, six prime controls and nine mandatory-stage omission controls.
The exact command actually executed is recorded in `EVIDENCE.json`; the
public `--replay` wrapper reconstructs the same source before invoking it.

After rebasing, the source package, workflow and immutable context consumed
by this contribution were compared across both bases; there were no changes.
The executed source, the wrapper's extracted source, and the current
reconstruction all contain the same 115 files byte for byte. The completed
replay's 723,357 instruction sextuples match the stored canonical fingerprint.
This verifies that the completed replay applies to the final integration.

The following checks passed on the final integration base:

```sh
python -X utf8 -B research/pr279-target-prefix-reconciliation/verify.py
python -X utf8 -B -I -O research/pr279-target-prefix-reconciliation/verify.py
python -X utf8 -B research/pr279-target-prefix-reconciliation/test_verify.py
python -X utf8 -B -I -O research/pr279-target-prefix-reconciliation/test_verify.py
python -X utf8 -B -m unittest discover -s tests -p test_pr_reconciliation.py
python -X utf8 -B scripts/verify_pr_reconciliation.py
python -X utf8 -B scripts/verify_selected_result.py
```

- Companion source/evidence checks and 13 tests pass, including under `-I -O`.
- All 14 repository reconciliation unit tests pass.
- The reconciliation checker validates all 535 ledger entries.
- The selected-result checker validates
  `1661202643272239/1000000000000000000` (#741 with #589).
- Source extraction to a new directory outside the repository succeeds.

No selected construction was changed, and no cold selected-frontier replay,
Lean build, repository-wide `make verify`, or new remote CI execution is
claimed. Historical source CI is identified separately in `SOURCE-CI.json`.
Maintainer acceptance and the disposition of PR279 remain pending.
