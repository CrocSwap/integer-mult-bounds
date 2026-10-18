# Discovery tools (not run by verify.sh)

These scripts nominated the frozen plan. The verifier only rebuilds the word from the frozen plan and checks it.

- `planL3.py` (needs ortools): the CP-SAT model for this skeleton. Per 4-frame it chooses each target's partner and
  its d-single keeper line, the D6 that hosts each target's Q-delivery, and the recipient of each free-keeper third
  register. It also sets the quad butterfly extras (d-cell, Q-cell or neither) under the exact d-line parity of every
  target, with a rank proxy for the block nodes.
- `planL3b.py` (needs ortools): iterates that model with random objectives. If `code/gen_l3.py`'s `plan_thirds`
  cannot make some block's 12 Q-delivery needs independent (rank 12), it adds a no-good cut on that block's choices.
  Each solve uses 4 CP-SAT workers, so a new run may return a different plan. The shipped plan is
  `data/plan-l3.json`.
- Hosting selections: `data/selection9-r420.json` came from #442's programme through #510's vendored
  `emit_k.py --discover`, and `data/hosting11-r420.json` from #493's `discovery/host_select.py`. `verify.sh` runs both
  programmes again and compares their output with the frozen files.

```sh
python -I discovery/planL3b.py NEW-plan.json 0                                   # a new plan (ortools)
NODEOPT=2000 python -I code/gen_l3.py data/plan-l3.json OUT.json.gz 0 dead last  # the shipped word
```

`NODEOPT` is the number of randomized LU realizations tried per block node (default 2000, the value the shipped word
uses). The realization with the smallest cancellation-free norm under the literal cleanup is kept; the random
generator is seeded per block, so the result is deterministic.
