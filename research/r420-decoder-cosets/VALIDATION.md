# Validation receipt

2026-10-13, Linux, Python 3.14.7, standard-library Python only.
Base `66849e1475c930fd7732b1a0067ffee7e1e95f60`.

Passed after implementation:

1. `python -B research/r420-decoder-cosets/verify.py`
   reproduces the frozen 32-trial search, five moves, 2,997 candidate scores,
   exact certificate and 244-XOR saving. All 660 columns, 672 closed frames,
   original H1–H5, unchanged per-register paths and six negative controls pass.
2. Original exporter, baseline and candidate: 29,874 / 29,630 native records;
   copy-aware forward/reverse integer bounds and 100-bit local envelopes pass.
3. Minimal `git archive` containing this package plus only its three input files,
   extracted into a fresh `/tmp/` directory and invoked from outside the repo:
   same PASS line, no untracked dependencies.
4. `python -O -B research/r420-decoder-cosets/verify.py` exits nonzero with
   `Assertions required: do not use python -O`.
5. Appending corruption to the archived input gzip: verifier rejects its source
   hash before search. This is an immutable source pin; candidate gzip output
   is compared through canonical JSON instead.
6. `git diff --check origin/main` passed; `git diff --exit-code origin/main --
   upstream certificates/selected-result.json` passed.
7. `make selected-record-check` passed with exact selected κ
   `51110230636731/31250000000000000`.

A separate AI reviewer checked the mathematical direction and cost formula,
not execution, and prompted explicit source-kernel, downstream-host, changed
D/C, frame-path and positive-growth checks. A second final static AI review
read the completed code, recipe and receipts and reported no issues; it did
not rerun commands or review a committed-range diff. This is not human peer review.

Not run: repository-wide `make verify`, selected `frontier626-verify`, C++
multistage replay, hosted-parent rebuild/global invoice, changed outer assembly,
Lean or remote CI. Boost headers and NumPy are absent in this environment;
the scoped stdlib verifier and unmodified exporter do not require either.
No full theorem, stronger κ, global optimality or practical runtime speedup is
inferred from these finite checks.
