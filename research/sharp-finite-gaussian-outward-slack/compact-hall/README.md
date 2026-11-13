# Compact invariant Hall witness

This folder adds a certificate-independent lower-bound checker for the R5
finite optimum. It defines the 1,809-point input set and 1,777-point output
container by two excluded (W(D_4)) orbits, generates the 38 input-orbit
representatives, and checks every strict-β error-one neighbor of each
representative.

Files:

- `PROOF.md`: the closed-form set, orbit and shell counts, group action, and
  exact neighborhood argument.
- `check.py`: standalone lower-bound checker. It does not read the matching
  certificate or any Hall input list.
- `RESULT.json`: the 38 representative checks and exact counts.
- `orbit_cut.py`: full integer orbit-capacity min-cut reconstruction using
  the certificate and exact verifier in the parent package.
- `ORBIT-FLOW-RESULT.json`: full quotient and min-cut receipt, including
  canonical representatives for all input and output orbits.

Run from this directory with Python 3.10+ and the standard library:

```sh
python3 -B check.py
python3 -O -B check.py
python3 -B orbit_cut.py
python3 -O -B orbit_cut.py
```

The first two commands are standalone and certificate-independent. The
quotient-flow replay reads only pinned sibling files and cross-checks exact
neighborhood equality and the minimum cut. All default runs write no files.
The top-level `CHECKSUMS.sha256` freezes this addition along with the parent
R5 package, excluding itself and Python caches.
