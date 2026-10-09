# Nondegenerate readout saturation (research contribution)

This additive package extends **22 readout frames by 25 dimensions** in Swapnil
Jain's pinned round-seven witness. It removes 177,100 singleton children while
preserving rank. The change is a finite, reproducible network improvement;
it is not a measured integer-multiplier runtime result or a global optimality
claim.

## Concrete idea

A readout frame must fit inside its entrance frame and all subsequent target
frames. Their intersection (the admissible cap) may be degenerate under the
required bilinear form. Rather than discard that cap, extend the existing
nondegenerate frame inside it, stopping at the exact rank of the cap's Gram
matrix. A reverse sweep preserves the later target constraints, followed by
an explicit nesting check after sorting the readouts.

For example, slot **22966** grows from dimension 12 to 13 inside a dimension-14
cap whose Gram rank is 13. Per replica, child widths **[507, 1, 1] become [509]**.
Both have total rank 509. For every 0 < tau < 1,
`509^tau < 507^tau + 2`, so this legal regrouping improves the same recurrence.
There are 3,542 replicas. Across all 22 changes:

| Child width | Multiplicity change |
|---|---:|
| 1 | -177100 |
| 507 | -31878 |
| 509 | -24794 |
| 511 | +56672 |

Total rank remains **57,403,754,177**. The certified bit saving used in the local
arithmetic experiment is **3999182181/62500000000000**.

## Reproduce

Python 3.10+; standard library only. Run from any working directory:

```bash
python3 research/nondegenerate-readout-saturation/verify.py
```

This first verifies the immutable package manifest, then runs an independent
rational audit of all 22 changes, the 119 affected target edges, the exact
component histogram delta and the moment enclosure. It writes fresh results
under `verification/`. The expected run time is about one minute on the
original development host.

For the complete finite frame and scalar controls (several minutes):

```bash
python3 research/nondegenerate-readout-saturation/verify.py --full
```

The full mode executes the pinned upstream rational frame/generic-pivot and
negative-control checks against the candidate, then checks the independent
packed-bit scalar word on all data and dirty-scratch basis columns, plus
integer samples and negative controls. It generates new hash-bound receipts;
no historical receipt is accepted as current proof. The wrapper suppresses
only equality to the old published numerical headline, which intentionally
changes; it does not suppress any frame or negative-control check.

The saturation search itself is in
`experiments/round7-review/saturate_readouts.py`. It writes both Z-support and
F2-support candidates. The submitted candidate uses **Z support**. Run the
search in a disposable copy if preserving the byte-level manifest; regenerated
gzip timestamps may change byte hashes even when the decompressed data agrees.
Do not assume an F2-only candidate is compatible with the complex argument.

## Numerical scope and PR97

The earlier A–E transfer experiment gives conditional
**kappa = 63982820832686571/10^21 = 0.000063982820832686571**.
Of its gain over the published round-seven headline, most is numerical
parameter refinement. The physical contribution versus the refined unchanged
baseline is about **3.90116e-9 in kappa**, or 0.00610%.

Separately, the local compatibility experiment with **Zhihao Chen's PR97** at
`f5f9c56e637463cac1e300d1589ccf42838f688a` replays its unchanged reflected/gauged
bit event ledger on the saturated frames and passes its main-compatible
47-condition / seven-margin assembly with
**kappa = 2559149/40000000000 = 0.000063978725**.
That is 1.2912e-8 above PR97's kappa=0.000063965813. PR97 closes actual gauged
endpoint and signed complex phase interfaces; its proof scope must not be
ranked solely by comparing kappa with the alternate A–E number.

The compatibility report and exact parameters are in `historical/`. They are
**bounded evidence from a separate local review**, not a complete combined
138-pin integrated witness. This package's quick verifier does **not** replay
PR97's endpoint/phase controls or assemble the 47 constraints anew. It checks
that the recorded rational slacks are positive, clearly a weaker check.

The all-size finite-alphabet tape compiler, analytic routing, precision,
recovery, prime/denominator arguments and uniform complexity claims retain
upstream proof assumptions. Finite checks do not establish the full theorem.
No global fastest claim, independent human peer review or hosted CI pass is
claimed. The repository-wide `make verify` gate has not been run for this PR.

## Sources, credits and license

All imported code retains its headers. `LICENSE` and the complete upstream
`NOTICE` are preserved. `MANIFEST.json` binds every submitted file; imported
source provenance is pinned separately in `PROVENANCE.json`.

- **Swapnil Jain**, [round7/round6 pinned source](https://github.com/Swapnil-jain/integer-mult-kappa/tree/741e7aa078392553815df7926ee17ac5e25a8c38):
  deferred readouts, V leaves, lifted frames, frozen inputs, flag/staircase
  construction and A–E transfer. Original Claude assistance disclosure retained.
- **Zhihao Chen / jacklightChen**, [PR97](https://github.com/CrocSwap/integer-mult-bounds/pull/97):
  reflected fan scheduling, nonzero auxiliary gauges, signed complex endpoint
  correction and retained-main-assembly integration used in the compatibility
  experiment. That work's Codex assistance disclosure is retained in the report.
- **OpenAI**, *Integer multiplication below n log n*, pinned
  `adc7f1241b42e322a6451854ab7e4b4c146bf78a` in [openai/math](https://github.com/openai/math).
- **Douglas Colkitt / CrocSwap**, [community framework](https://github.com/CrocSwap/integer-mult-bounds).
- **Avi Eisenberg / ikeboy**, [PR62](https://github.com/CrocSwap/integer-mult-bounds/pull/62):
  interval strips and core-aware pair assembly.
- **RaD / hipotures**, [PR41](https://github.com/CrocSwap/integer-mult-bounds/pull/41):
  alternating order and links.
- **Rohan Arun / rohanarun**, [PR44](https://github.com/CrocSwap/integer-mult-bounds/pull/44):
  weighted matching.
- **Aurel Prosz / Paureel**, [two-stage/complement-frame work](https://github.com/Paureel/integer-mult-bounds/tree/c82d09e).
- **icekylinx**, [PR36](https://github.com/CrocSwap/integer-mult-bounds/pull/36):
  copied retained centres; earlier batching, partial swaps and retained assembly.
- Earlier contributors including eumemic, dleen and James Chang are preserved
  in the upstream NOTICE and PR97 review; Harvey–van der Hoeven's multiplier
  and analytic work is inherited background.

The new saturation exploration and package were prepared for **djsmanchanda**
with substantial **OpenAI Codex assistance** in code, checks and drafting.
AI cross-checks are not independent human peer review. Apache-2.0.
