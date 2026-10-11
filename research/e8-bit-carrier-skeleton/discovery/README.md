# Discovery tools (not run by verify.sh)

These scripts nominated the frozen inputs. The verifier only replays and checks the frozen files.

- `d4part.py` (needs ortools): enumerates the D4 sub-root systems of E8 and finds, by a CP-SAT exact cover, a
  partition of the 120 lines into 5 orthogonally complementary D4 pairs. The shipped
  `data/skeleton/d4part-pairs.json` came from this search; other partitions exist and would need their own plan.
- `plan.py` (needs ortools): the CP-SAT plan for the quad skeleton on that partition: per-quad butterfly extras
  (d-cell, Q-cell or neither), the single line kept for each cross D6 and which of its two targets reads it. The
  constraints are the exact d-line parity of every target, equal Q-deliveries for the two targets that share a D6,
  and independence of each block's six Q-deliveries. With the matching fixed it is solved to OPTIMAL in seconds
  (4 workers, so a new run may return a different optimal plan); the shipped solution is `data/skeleton/plan-skB.json`. `code/skeleton/gen.py` imports it only when no plan file is given.
- `host_select.py` (needs scipy): PR #442's hosting integer programme (`hosting_core.solve`) on the eleven-stage
  schedule with the eight replicas pooled as in PR #472 and every residual forced onto an idle child. The result is
  `data/eleven/hosting.json`. The programme maximises the saved idle cost r ln(m/r), a proxy for the moment root;
  the selection is not claimed optimal.

Rebuild commands:

```sh
python -I discovery/d4part.py OUT.json                      # optional; any result needs a new plan
PLAN=NEW-plan.json python -I code/skeleton/gen.py OUT.json.gz 0 fresh   # no such file yet: solves and saves a plan
PLAN=data/skeleton/plan-skB.json python -I code/skeleton/gen.py OUT.json.gz 0 fresh   # the shipped word
python -I discovery/host_select.py data/bit/bitE8mut-r489.json.gz OUT_hosting.json
```
