# Repository-wide required checks

Both required commands were executed, on unchanged baseline main
`130a7ce63a233e6812b7c037993c721fec827014` and again on refreshed main
`a5b3fc6d931e16af4f0776e4cea58bf3b1b7e099`.

* `make verify`: exit 2. The community arithmetic checks and twelve copied-word
  tests pass, then `research/copied-fixed-reversed/producer.py` fails in
  `scripts/partial_swap/shared.py` while unpacking `t0,t1,t2=target`:
  `ValueError: not enough values to unpack (expected 3, got 1)`. The fixed
  reversed graph retains singleton totals, while the newer digest optimization
  assumes triple-shaped outputs. The new package does not touch these files.
* `make frontier1094-verify`: exit 2. `verify_selected_result.py` first passes
  the selected record's exact kappa and source inventory. The historical-source
  stage then rejects `Selected proof supplement changed:
  scripts/verify_hpe_lean_binding.py`. The expected historical supplement hash
  was not changed or bypassed.

The failures also remain on the final refreshed main; their command logs and
historical-source sub-log are included. They block a claim that the whole
repository's required suite is green. They are separate from the candidate's
complete pinned supplier/outer release, which passes.

The registered new package check passes on Python 3.12. Exact source/commit
byte preflight is recorded separately. No fresh Lean kernel build or hosted
GitHub CI pass is claimed. Main and upstream frozen packages remain unchanged.
