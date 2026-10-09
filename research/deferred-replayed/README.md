# Deferred readouts on the replayed h24 complex network

Conditional κ = 1363953833/(1.25·10¹³) = 1.0911630664 × 10⁻⁴, complex-bound.

PR #110 showed that Swapnil Jain's deferred readouts also pay on the complex network under PR #104's
one-child-per-residual rule. Here that construction runs on the replayed h24 complex DAG already shipped by
PR #117 (`certificates/deferred-product-complex-dag.json.gz`, R = 28,705), with PR #114's saturated placement:
a degenerate target-chain intersection is refined to a nondegenerate subspace instead of being discarded.

| | #117 (not deferred) | this |
|---|---:|---:|
| deferred roles | 0 | 4,560 |
| complex saving (binding) | 1.0451600e-4 | **1.09140237e-4** |
| κ | 1.044939e-4 | **1.0911630664e-4** |

The bit side is #117's, unchanged: Swapnil Jain's round-seven deferred word under #104's rule.

Files:
- `complex_deferred.py`: #110's script with #114's `saturated_placement`, reading the shipped DAG. It checks root
  values, replays the deferred stage-one word with arbitrary scratch over Z/(2^61−1), checks exact F2 nesting and
  nondegeneracy on every role chain and target chain, and the rank mass W m − N + L.
- `network.py`: #117's bit side and bridge, this complex profile, #114's conservative literal charge for expanded
  readouts, 47 strict constraints and 7 margins, next grid points rejected.
- `scripts/deferred_product/deferred_word.py`: independent two-stage check of the exported word. Stage two is
  expanded explicitly as the complement time reversal with banks exchanged: 277,799 events per invocation per
  stage, 0 violations, reflection continuous, paid histogram equal to the profile. Five mutation controls are
  rejected. Alternating residuals of ranks 2, 4, 6 and 8 occur; each is one child under the general normal form of
  `notes/endpoint-gauge-complex.tex`.

```sh
make verify-deferred-replayed
```

Credits: Avi Eisenberg (#110 deferral construction), eumemic #114 (saturated placement, expanded-readout charge),
Swapnil Jain (deferred readouts, lifted frames, round-seven bit word), icekylinx (#104), Zhihao Chen (#97), and all
predecessors in #104's NOTICE and SOURCES. Prepared by eumemic with Anthropic Claude assistance.
