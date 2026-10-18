# E8 prefix restoration: kappa = 0.001000220222889528

This package supplies a new finite conditional construction for the Beyond n log n framework. Its assembled exponent is

    kappa = 125027527861191 / 125000000000000000
    complex b = 40048866680681 / 40000000000000000
    bit c = 255384852701747 / 250000000000000000

This is about 0.1981% above PR382's 0.000998243154231047, the strongest benchmark in our frozen sweep through PR383. It exceeds 0.001. The claim is conditional on the inherited multiplication/compiler/precision interfaces; it is not an unconditional integer-multiplication theorem or a Lean certificate.

## What changes

1. Eighteen disjoint target-prefix difference/recovery rewrites remove paid target frame visits while preserving the entire raw rational operator, including arbitrary initial helper and target values. These introduce target-to-target additions, so the dirty decoder explicitly freezes the source response network rather than assuming the old compiler accepts them.
2. Two helpers are restored at rank-eight endpoints. Explicit initial dirty cancellation and helper preconditioning permit those heterogeneous endpoints without requiring clean helpers. The final program includes the scalar inverse, every donor advance, the full endpoint Clifford phases and actual inverse bank routes.
3. Thirty-two replicas pack the rank-eight residuals with rank-nine residuals into width73 banks. There are3131 banks per stage, including all paid padding. The new finite scalar work is charged, not hidden as an oracle.

The bit side composes PR376's helper reuse with PR381's nine-stage unsplit construction. That composition is useful headroom, not the new mathematical mechanism. The complex source is PR378's far-retimed word inside PR377's compressed nine-stage construction.

| Construction | Assembled kappa |
|---|---:|
| PR381 public benchmark | 0.000995656966441037 |
| PR382 public benchmark / old complex cap | 0.000998243154231047 |
| Helper reuse plus far retiming | 0.000998634656132003 |
| Add eighteen target-prefix rewrites | 0.001000197726610570 |
| Add two early restorations and heterogeneous banks | **0.001000220222889528** |

These are sequential exact compositions, not sums of percentage gains. No claim is made that elementary linear preconditioning itself is a new mathematical discovery; the new contribution is this explicit legal construction and its paid recurrence improvement.

## Reproduce

Requirements: Python3.11 or newer, NumPy2.4.6, SymPy1.14.0, mpmath1.3.0, g++ with C++17 (GNU headers/builtins), and Boost multiprecision headers. On Linux install g++ and libboost-dev; on Windows set CXX to your g++.exe and BOOST_INCLUDE to the directory containing boost/. No network is used during replay.

    python -m pip install -r research/e8-prefix-restoration/requirements.txt
    python -B research/e8-prefix-restoration/verify.py /absolute/path/to/new-empty-output

The output path must not exist and must be outside this package. Do not use python -O. The replay validates the manifest, reconstructs the changed word, checks both dirty orientations, Clifford phases and banks, emits the global template, reconstructs the changed bit component, and checks all47 outer strict inequalities with exact rational moment engines. It does not run unchanged public PR verification pipelines. Source inputs are never modified.

See PROOF.md for the sufficient construction, VALIDATION.md for evidence and limits, SOURCE-PINS.json and NOTICE.md for provenance, and research-notes/ROUND.md for the screened alternatives. Generated binaries and large replay logs remain in your output directory.
