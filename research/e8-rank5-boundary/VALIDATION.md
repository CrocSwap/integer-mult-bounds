# Validation record

Local checks on 2026-10-13, macOS 27.0.1, arm64, CPython **3.14.7** and
**3.11.15**. These are observed local results, not hosted-CI results.

| Check | Observed result |
|---|---|
| `python3 -B research/e8-rank5-boundary/verify.py` | PASS; complete certificate matches |
| `python3 -I -O -B research/e8-rank5-boundary/verify.py` | PASS with all checks active |
| Independent checker with `--check research/e8-rank5-boundary/CERTIFICATE.json`, ordinary and isolated optimized | PASS; entire independent summary agrees |
| Both scripts, isolated optimized CPython 3.11.15 | PASS |
| `python3 -B research/e8-rank5-boundary/test_package.py` | PASS; relocated isolated replay, byte-identical receipt, cost/orbit mutations rejected, source mutation rejected before changing existing output |
| `python3 -B research/e8-rank5-boundary/sources/pr631/verify.py --negative-controls` | PASS; original thresholds and at-most-35 controls reproduced |
| `make selected-record-check` | PASS; selected κ remains `1661634653669567/10^18` |

The first packaging-test run exposed a mismatch in the test's expected error
substring (`independent summary` versus `independent_summary`); the verifier
correctly rejected the corrupted cost. The expectation was corrected and the
complete packaging test then passed. No mathematical output changed.

The separate mathematical review checked the equality reduction, the distinction
between standard representatives and Weyl orbits, the all-36 exclusion, and the
cost lower-bound wording. An additional scratch calculation used Fraction
elimination on coordinate Gram matrices and verified both rank histograms,
the threshold-span identity and all 72 restorations. These checks were
AI-assisted, not independent human peer review. The reusable independent
checker is included in the package.

The primary verifier checks 130,305 standard-flat/reader pairs across dimensions
zero through seven, including all 28,616 rank-five pairs. It then checks both
511-reader rank tables, an explicit conjugating word and the complete
7,560-mask orbit under eight generators. The independent checker separately
reconstructs the rank-five census and both rank tables, not the full orbit.

Before submission the open-PR inventory was refreshed to **667 open PRs through
#874**. The new Gaussian all-clique note #868 concerns a different geometry
and proof method; #874 concerns X4 gain additivity. Neither overlaps this
root-only rank-five equality classification. The pinned PR631 head remained
`fb893b5ee1317c2da3b297e6fe78eca0857d1a76`, and fetched `main` remained the
original base `f567884aeb8851b6e794af1184119a3bfbe1e631`. There was still no
pinned coordination issue.

The full `make verify`, selected supplier cold reconstruction, Lean builds and
hosted CI were **not run** for this isolated research package. No existing
generator, supplier, selected certificate, `upstream/` file or global workflow
changes. The finite computations and written coverage argument do not prove
the full conditional integer-multiplication theorem.
