# Verification record

Environment: Python standard library only; no third-party packages.

Commands run from this directory:

```sh
python3 -B replay.py
python3 -O -B replay.py
python3 -B verify.py
python3 -O -B verify.py
python3 -B compact-hall/check.py
python3 -O -B compact-hall/check.py
python3 -B compact-hall/orbit_cut.py
python3 -O -B compact-hall/orbit_cut.py
```

All commands passed. Normal and optimized runs produce identical receipts.
The default replay and checker commands write no files. Both checkers use
explicit `require` checks, so optimized mode does not disable validation.

The checker expands the pinned certificate, enumerates all 3,121 points of
\(S_5\), validates every injection edge using integer arithmetic, enumerates
all error-one output candidates for each of the 1,692 Hall inputs, recomputes
the exact strict-\(\beta\) neighborhood, and checks the signed-permutation
identity. It also exercises certificate-corruption, duplicate-output,
omitted-neighbor, strict-error, and threshold-tie negative controls.

The standalone `compact-hall/check.py` does not read the matching or Hall
certificate. It regenerates the 38 input-orbit representatives from the
closed-form predicate and checks all 9 or 16 error-one candidates at each
representative against \(N_1\). `compact-hall/orbit_cut.py` independently
rebuilds the full quotient graph from the authenticated matching certificate
and exact checker and verifies the flow/min-cut and exact neighborhood.
