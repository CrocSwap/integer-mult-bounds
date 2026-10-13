# Validation record

## Commands (repository root, standard-library Python 3.13.15, Windows x64)

```sh
python -I -B research/r439-block508-schedule/search.py
python -I -B research/r439-block508-schedule/verify.py --record-expected research/r439-block508-schedule/EXPECTED.json
python -I -B research/r439-block508-schedule/verify.py
python -B research/r439-block508-schedule/verify.py
python -O -B research/r439-block508-schedule/verify.py
```

Discovery output: 37 original gates, forward single-write minimum 30,
30-gate witness, candidate sha256
`2947e9d017aabae36f0f196f65417aee18cc45f2485b4dc5e34e9ac20ab0cf82`.

All verify runs print:

```text
PASS_R439_BLOCK508_SCHEDULE gates=37->30 ADDs=24305->24291 saved=14 columns=661 controls=8 minimum=30 rank_mass=5129 no_new_kappa
```

The `--record-expected` run wrote `EXPECTED.json`; subsequent runs compare
the full receipt byte-for-byte (JSON-canonical) and pass, so the receipt is
deterministic across normal, optimized and isolated modes. `search.py` reruns
deterministically to the same candidate hash.

## Coverage in verify.py

- Source pins (word, owning interface checker, record exporter) and base
  commit constant; wrong slice/binding rejected.
- Block certificate: exact forward integer-map equality, reverse-map
  entrywise domination (strict in 20 entries), all 2,048 Boolean tables.
- Optimality: backward Bellman minimum 30 (2,048 states, 11,264
  state/destination pairs, 4,376 feasible edges) agreeing with the forward
  discovery minimum and the 30-gate witness.
- Splice: only `B[205:242]` and `C` change; `C` is the literal reverse;
  identical register frame paths; unchanged paid profile and rank mass 5,129;
  exact F2 endpoint on all 661 columns; inherited H1-H5 and conclusions pass.
- Bills: 24,305 -> 24,291 ADDs; forward bound 49,347 equal; reverse bound
  1,113,070 -> 1,086,054; payload 93 bits (< 104); non-ADD inventory equal;
  9 copies / 9 erasures.
- Eight negative controls rejected, including a stale-cleanup control that
  passes the endpoint but fails literal H4.

## Not run (open obligations)

C++ legality and 5/9/11-stage replays (no C++17/Boost toolchain on this
machine), the hosted invoice, the global assembly, `make verify`, Lean and
remote CI. Forward-map equality plus reverse domination imply the payload
bounds carry over; independent native replay remains to confirm.
