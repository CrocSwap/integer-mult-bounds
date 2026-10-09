# Birth-read reuse on shrunk, saturated frames

Author-checked conditional κ = 11239534209971/10^17 = **1.1239534209971e-4**. Independent review is pending.

This composition applies PR124's birth-read slot reuse (James Chang) to PR125's frames, which are shrunk lifted frames with PR114's saturated placement. The result is 4,706 deferred readouts, 2,108 paid reuses and R = 26,597.

Run from the repository root:

    python3 research/shrunk-birth-reuse/run_checks.py

The checker needs only the Python 3.11+ standard library. The runner first hashes its four base inputs; see `BASE_INPUTS.json`, which pins PR125's DAG, profile and certificate. In a temporary directory it then reconstructs:
- the graph and the matching;
- the shrunk and saturated frames, checked against PR125's complete histogram;
- the birth pairs and the exact readout bill;
- both literal frame directions;
- the exact assembly.

Frozen receipts are compared field by field. On Linux, per-stage CPU and memory caps from PR124 apply; the frame stage is allowed 120 s and 2 GiB. `PROOF.md` states the operation, what changed and the scope.
