# Ranked reclamation in joint dual-skip frames

The conditional saving is **κ=4764513337/10^14=4.764513337×10^-5**,
with bit saving **2382370177/50000000000000**. This is approximately
**0.2900108%** above PR58's conditional saving.

The dedicated compiler considers retired physical slots in descending current
frame rank, using slot ID to break ties. It retains PR58's pinned PR55 scalar
graph, matching, frame-containment and signal-span checks, and explicitly paid
clearing XORs. The original shared PR57 compiler remains byte-identical.
Rohan Gupta supplied PR55's producer; eumemic supplied PR57's joint compiler.
Chafik Boukhalfa prepared this priority change and exact integration with
OpenAI Codex assistance. All predecessor notices remain in place.

| Quantity | PR58 | Ranked reclamation |
|---|---:|---:|
| h23 auxiliary roles | 30,790 | 30,688 |
| h25 auxiliary roles | 40,446 | 40,338 |
| Physical width W | 150,593,466 | 150,167,598 |

The [proof](PROOF.md) distinguishes exact finite replay from the inherited
all-size analytic, routing, residual compiler and fixed-tape interfaces.
The fixed I+J data geometry and complex branch are inherited. No global
optimality, practical speedup or formal verification of the complete theorem
is asserted.

```sh
make joint-dual-verify
make verify
```

The focused target checks the source closure, rebuilds both scalar graphs and
compiler words, and requires byte equality after decompression. It then
independently replays every input and dirty basis vector in both orientations,
reconstructs frame transitions from the actual XOR word, recomputes every
fixed-basis profile with bounded-minor/CRT checks, and checks the exact
recurrence, 47 strict constraints, seven margins and eventual cutoffs.
Both next rational grid points are rejected. The complete pinned PR57 and
PR58 child lists fail at the new bit saving. Ten focused test methods include
physical-word tampering, missing paid transitions and centers, understated
width, and rejection of optimized Python at all four new entry points.

The complete local words have 474,930 and 627,480 XOR incidences,
including all 4,284 and 5,714 clearing XORs. Compiler and transition records
bind both words and all positive recursive children. Run receipts in
`certificates/joint-dual-validation.json` describe focused verification;
`certificates/joint-dual-repository-validation.json` separately records full
repository status. The PR57 baseline and its verification target remain
available. The complete PR58 comparison certificate and source/proof
provenance are frozen under `references/frame-compiler/pr58`; its complete
historical source and word closure remains available at the pinned ancestor
commit.

Maintainers explicitly freeze reviewed sources and finite inputs with
`scripts/experiments/pin_joint_dual_sources.py`. Verification never refreshes
source pins. Derived arithmetic certificates and run receipts are excluded
from the source freeze.
