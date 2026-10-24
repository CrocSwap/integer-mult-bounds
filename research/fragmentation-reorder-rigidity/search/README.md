# Recorded search evidence (not replayed by `verify.py`)

These files document the discovery runs that preceded the exhaustive certificate in `../verify.py`.
They are retained as evidence; their hard-coded paths point at the author's local checkout
(`D:/Math/imb-docking`), and they are **not** part of the registered replay.

| file | content |
|---|---|
| `forced_climbs.py`, `forced_exact.py`, `nested_facts.py`, `dag_windows.py` | the one-field-at-a-time relaxations, nestedness facts and dependency windows of the #4610 word (the numbers in README sections 2–3) |
| `jcr_search4.py` | simulated annealing over joint frame chains and contact frames with an incremental (Pearce–Kelly) acyclicity check, a systematic sweep phase, centre interface pinned |
| `jcr_search5.py` (derived by `make_v5.py`) | the same with the eight centre reads free to move along their source chains |
| `eval_state.py` | prices a saved state's climb profile with the kap-family controller formula |
| `sweep_exact_rules.txt` | sweep under the exact rules: 0 of 2,754 levels dropped (no re-routing 330, every re-routing cyclic 2,196) |
| `sweep_no_centre_pins.txt` | control sweep ignoring the centre interface: 24 levels dropped, Lambda 23.50 |
| `anneal_seed1.txt`, `anneal_seed2.txt`, `anneal_seed3.txt` | three 6-hour / 3-hour annealing runs of `jcr_search5.py` (15.2 M, 14.7 M and 7.1 M moves; moves: drop level, re-route contact, move contact to a new frame): best Lambda 23.8626 = the word in all three; centre reads stayed at dimension 8 |

Earlier annealing versions that ignored the centre interface reached Lambda 23.45 (a model artefact: those
states move contacts across the moments when a field must stand in the frame of a centre read or delivery, so
the exact interpreters of #4610 would reject them). The certificate in `../verify.py` includes that interface.
