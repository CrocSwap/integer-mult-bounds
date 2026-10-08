# Joint frame compilation of dual-skip strips

The conditional saving is **κ=475073569/10^13=4.75073569×10^-5**,
with bit saving **1187740349/25000000000000**. This is approximately
**1.7409637424%** above PR57's stated conditional saving.

This composition supplies Rohan Gupta's pinned PR55 dual-skip scalar graph
to eumemic's unchanged PR57 joint frame compiler. Identical original-envelope
regions are compiled jointly, compatible signal continuations are retained,
and retired signals are cleared with explicitly paid XORs. Chafik Boukhalfa
prepared this composition and certificate integration with OpenAI Codex
assistance. All predecessor notices remain in place.

| Quantity | PR57 | This composition |
|---|---:|---:|
| h23 auxiliary roles | 31,416 | 30,790 |
| h25 auxiliary roles | 41,264 | 40,446 |
| Physical width W | 153,481,944 | 150,593,466 |

The [proof](PROOF.md) distinguishes exact finite replay from the inherited
all-size analytic, routing, residual compiler and fixed-tape interfaces.
The fixed I+J data geometry and complex branch are inherited. No global
optimality, practical speedup or formal verification of the complete theorem
is asserted.

```sh
make joint-dual-verify
make verify
```

The focused target checks source closure, rebuilds both scalar graphs and
compiler words, and requires byte equality after decompression. It then
independently replays every input and dirty basis vector in both orientations,
reconstructs frame transitions from the actual XOR word, recomputes every
fixed-basis profile with bounded-minor/CRT checks, and checks the exact
recurrence, 47 strict constraints, seven margins and eventual cutoffs.
Both next rational grid points are rejected, and the complete PR57 child
list is excluded at the new bit saving.

The complete paid local words have 474,786 and 629,356 XOR incidences,
including all 4,248 and 6,183 clearing XORs. The saved compiler and transition
records bind both words and all positive recursive children. Run receipts
in `certificates/joint-dual-validation.json` describe focused verification;
`certificates/joint-dual-repository-validation.json` separately records full
repository status. Earlier PR57 certificates and its verification target
remain available.

Maintainers explicitly freeze reviewed sources and finite inputs with
`scripts/experiments/pin_joint_dual_sources.py`. Verification never refreshes
source pins. Derived arithmetic certificates and run receipts are excluded
from the source freeze.
