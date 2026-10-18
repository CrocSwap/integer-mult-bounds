# Verification and handoff

Base `66849e1475c930fd7732b1a0067ffee7e1e95f60`; CPython 3.14.2,
macOS 26.3 arm64, standard library only. The runtime uses Python 3.11+.
Sprint began 2026-10-13 at 05:41 UTC, with a 40-minute budget; the claim was
recorded during the initial selection window. Construction/proof work ended
around 05:55 UTC, with the remaining work dedicated to verification and
handoff, ahead of the reserved final-quarter deadline of 06:11 UTC.

## Final commands

From the repository root:

```sh
python3 -I -B research/dyadic-center-basis-shear/verify.py
python3 -I -O -B research/dyadic-center-basis-shear/verify.py
python3 -I -B research/dyadic-center-basis-shear/test_circuit.py
python3 -I -O -B research/dyadic-center-basis-shear/test_circuit.py
python3 -I -B -m unittest discover -s tests -p test_complex_centers.py -v
make selected-record-check
```

Both full replays match every committed certificate field. All **8 new tests**
pass in both modes. All **4 original center tests** pass. The selected-record
check returns its unchanged conditional kappa
`51110230636731/31250000000000000`.

The primary sparse contraction and independent head/tail implementation
check all **6,760,000** h=26 coefficients and produce identical SHA256
`2f6824bdd4d0a4669e974e7a6087fc7ed329c80c4e9b3afa891d46fee40e8eff`.
The direct **1,300-move** census and independent **16-orbit** census agree on
all admissibility counts, cost histograms and minima. Unit tests cross-check
these two search methods at h=8,10,12,26.

The unchanged full invocation executor checks all 998 formal input columns
at h=8 and all 2,767 at h=10 in each direction: **7,530 column/direction
obligations** including every arbitrary dirty side/center input. The
independent central checker performs **356** exact integer basis executions.
The source worker rebuilds the full h=26 side topology and recounts M,C,J;
it inherits the unchanged full-size side-coefficient and phase proofs.

## Failures detected and final portability

A minimal temporary checkout containing only the **25 pinned inherited
inputs** and this package passes under `-I -O`, with spaces in its path,
an unrelated working directory, a hostile `PYTHONPATH/sitecustomize.py`,
and ambient `PYTHONOPTIMIZE=2`. Its inherited subprocess still runs with
assertions enabled. The observed isolated replay took approximately 5.63s;
this is descriptive, not a performance result or pass threshold.

A fresh `--out` certificate agrees field-for-field. Separate subprocess
controls reject:

- an existing output path, preserving its original bytes;
- altered bytes in the lazily imported `scripts/complex_compression.py`;
- a certificate with scatter charge H reduced by one;
- directly invoking the inherited source worker with assertions disabled.

The mathematical controls detect a gather-only shear, an incorrect sign on
a −2 scatter numerator, omitted inverse gather, and omitted initial dirty
scatter. Invalid alphabet/shape/move inputs and missing/mutated source pins
are rejected. The −2 numerator appears exactly `binom(23,2)=253` times at
h=26 and is charged as a signed unit update. The original factor checker
continues to reject its unsupported alphabet; no original guard is weakened.

Two packaging defects were corrected during verification before submission:
the initial import-time manifest missed lazy imports, so the final manifest
is built from complete runtime coverage and checked against the worker's
reported import inventory; tuple/list representation differences in the
independent counterexamples caused certificate comparison failure, so the
complete result is normalized to exact JSON representations before comparing.
No mathematical field was excluded. Final normal, optimized and relocated
replays pass after both fixes.

All 25 inherited pin hashes were compared against exact Git blobs at the
base. All numeric JSON values are exact integers or rational strings.
A separate Codex worker reviewed the proof, full costs, source-coverage
changes and certificate normalization; no material issue was found. That
is AI-assisted methodological review, not independent human review.

## Overlap refresh and scope

At approximately 05:58 UTC, a fresh query found **621 open PRs through #802**,
compared with 612 through #793 at selection. Main still equaled the base;
the pinned-issues query again returned no nodes. New/changed titles and
full bodies matching the center-basis/dyadic-factor scope were inspected.
No matching historical one-shear contribution was found.

| Related PR | Inspected head | Distinct scope |
|---|---|---|
| #769 | `e891b2b19e3185ec91bcf001e255af87f42389ce` | Selected CK coefficient ladders. |
| #776 | `8bd985fe2842c948a5a4a1554b8e090f2e371afa` | Selected fixed-order A/B frame ceiling. |
| #786 | `c6ae38d9f5a13c53dab623fd6947f08d92173287` | Selected CK/JP8 center quarter scaling and its added-macro cost. |
| #787 | `93ceb65cfbf339d7ca743614d4756a3af1440cd4` | Selected coefficient-lowering/cleanup composition. |
| #793 | `f9383f324ee86793c5ae7b73f8e39d5827a8aa52` | Selected JP8 compensation reordering and batching. |

These contributions are credited as related circuit research; none is a
code dependency or an additive saving here. The source architecture,
operation bill and common-frame grouping in this package are the historical
h-triple construction. The new mechanism changes its scalar factorization,
not a previously closed fixed-factor frame search.

Only `research/dyadic-center-basis-shear/` is added. `upstream/`, original
source files, certificates, selected frontier and unrelated artifacts remain
unchanged. The full repository suite and selected supplier cold replay were
not repeated because this optional historical experiment edits no generator
or selected construction. No remote CI, full-size phase replay, full-tensor
scalar replay, new global admission or Lean proof is claimed. Remaining
conditions are stated in README.md.

Attribution: Curtis Dransfield with substantial OpenAI Codex assistance;
Douglas R. Colkitt's source construction and retained predecessors credited
in README.md. New contribution: Apache-2.0.
