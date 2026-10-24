The [fixed-code appendix](PROOF.md) gives an independently reviewed criterion for one fixed scalar code to survive independent native port operators. The operators must agree on each component of the code projector's support graph. The pinned `ker R` graph is connected on all 112 ports, so all completed port operators must agree for that fixed-code contract; equal ranks are insufficient. Changing codes and joint array operators remain outside the result. The exact source graph check passes in normal Python and with `-O`.

```sh
python3 -I -B research/phase-coded-callers/annexes/fixed-code-interface/replay.py --out /tmp/fixed-code-interface-replay
```

Expected final line: `PASS_SCOPED_SUPPORT_PROOF_REPLAY`.
