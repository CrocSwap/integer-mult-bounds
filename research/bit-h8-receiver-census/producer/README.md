# Producer scripts (provenance only)

These are the resumable drivers that produced `data/`. They ran in a separate working copy with this repository at
`../repo` (or `../../imb-docking`) and wrote JSON lines, which were then converted to the CSV tables. They are not part
of the registered replay; `verify.py` re-derives every claim it makes from `data/` and from main.

- `enumerate_P.py`: admissible puncture sets (same rule as `sets.py`).
- `one.py`, `price.py`: build, export, float price (the dual screen of closed #4633; its first condition is the raw
  root checked by `verify.py`).
- `run_census.py` (stage A, NODEOPT 50), `run_stageB.py` (200 sets × 31 draws, NODEOPT 50), `run_stageC.py` (all 3^9
  receivers of PR589's set, NODEOPT 2000).
- `tune_one.py`, `tune_batch.py`, `pick_c2.py`: tuning of the leading receiver profiles (`data/TUNED.csv`).
