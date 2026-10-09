# Stopped recursion with signed deferred gauges

**Conditional κ = 10954833669241/125000000000000000 = 8.7638669353928e-5.**

This composition applies the stopped whole-rank interface to the existing
h25 rational-frame word and adds signed deferred readouts to the weighted
complex pair-tree word. The new complex schedule selects 14,081 auxiliary
gauges with total dimension 180,444. Every deferred readout, endpoint,
copied center, inverse and larger recursive child is paid.

## Reproduce

```sh
python3 research/stopped-signed-gauges/verify.py
```

Requires Python 3.11+ and a C++17 compiler. Python uses the standard library.
Default verification writes temporary outputs. `--record` additionally writes
a run log and validation receipt without changing mathematical inputs.

The gate regenerates the original and selected complex producers, actual
matching, and h25 bit word. It repeats the full inherited bit dirty replay,
checks every rational projector class and incidence, reconstructs all complex
signed support and gauge choices, and verifies the full forward/reflected
chronology. It independently checks the paid moments, larger precision
constants, all three row reserves, 47 positive constraint slacks and seven
cost margins. Both moment boundaries and the next κ grid are checked.

| Quantity | Exact selected value |
|---|---:|
| Coarse bit saving | 99628619123269/10^18 |
| Stopped ordinary bit saving | 99567450404145731/10^21 |
| Complex saving | 43823175281777/(5·10^17) |
| Complex largest child | 572 |
| Complex halving degree | 100 |
| Complex scalar bound G0 | 5655806159168 |
| Three-stock row coefficient | 3528 |
| Row degree / suffix slope | 10000 / 40000 |

## Proof and credit

See [PROOF.md](PROOF.md), [the bit argument](bit-proof.md), and
[the complex schedule and endpoint argument](complex-proof.md).

Prepared for Thomas DiFiore with substantial OpenAI Codex assistance.
icekylinx supplies PR104's stopped product-ring, opposite-bank and rational-center
interfaces. Swapnil Jain, Zhihao Chen, Paureel and their credited predecessors
supply the deferred-readout, frame, signed-endpoint and two-stage lineage.
Rohan Arun supplies the PR107 comparison and balanced-transfer refinements.
Chafik Boukhalfa, eumemic, Avi Eisenberg, Maxime Fleury, RaD/hipotures,
James Chang, Dominik Scholz and all original contributors retain their
compiler, storage, coordinate, proof and arithmetic credits in the preserved
notices. Douglas Colkitt, OpenAI, David Harvey and Joris van der Hoeven retain
the framework and analytic-work credits.

This is a finite conditional exponent improvement. The all-size common-basis,
normal-form, atom-streaming, exact-grid, analytic, prime and fixed-tape
interfaces remain assumptions. Finite fixtures supplement the written
arbitrary-dirty argument; they do not prove the complete multiplication
theorem. No practical runtime, current-record or human-review claim is made.
