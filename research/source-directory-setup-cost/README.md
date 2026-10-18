# Charge repeated exponent reconstruction in source-directory setup

The unchanged PR2569 producer has **cubic**, rather than quadratic, cardinality
setup work in w. Its `high_power` reconstructs the radix exponent m² times,
performing m²w divisions on L-bit words. Each division writes exactly
`3L²+8L+4+(3L+2)*popcount(quotient)`, including allocation and erasure.
Even C=1 therefore gives Omega_q(w³) work.

The corrected conclusion is useful: **complete directory production remains
Theta_q(D)** in the emitted directory size, including its cubic setup and
local cleanup. The actual high cube H=q^(m²(w-1)) absorbs the polynomial.
This producer lemma does not require the root coupling or a complete body
fibre. The separate D=O_q(V) payload statement still needs the predecessor's
h/w/R premises. See [PROOF.md](PROOF.md) for the exact source-loop counts,
upper bound, complete producer contract and limits.

PR2569 is pinned at `0b116cb34f27a4b064f0d8dd65549ea5705cf9c0`.
The specific corrected sentence is its `PROOF.md` claim that computing CH
costs `O_q(w log(C+1)+w²)`. This audit changes no producer code and does not
refute its final volume-based asymptotics. PR2566 at
`bfe8317a38f03a5693470e873b29101f3f7a55e4` is credited for the separate
complete binary primitive and conservative division-preparation bounds.
The present result binds those costs to the new directory producer and proves
their absorption into its actual serialized output.

```sh
python3.12 -I -O -B research/source-directory-setup-cost/verify.py
python3.12 scripts/research_package.py --package research/source-directory-setup-cost
```

The standard-library verifier authenticates all retained SHA256/Git blobs
before compiling source bytes directly. It checks every division's write
bill and full L iterations, independently sums Tape/Arena traffic, verifies
CH and ownership, and directly serializes every output directory in eleven
complete finite cases. Sixteen setup cases include w=32, a 129-bit C and the
m=64/w=1 boundary. Four semantic undercount/multiplicity controls and separate
Git-free/source/typed-receipt tests accompany the written all-size proof.
Default replay is read-only; `--write-result` creates only a missing receipt.

The units are the retained fixed-alphabet Tape/Word meters, not elapsed Python
time or an executed literal fixed-tape compiler. Numerical reserve constants,
controller costs, full selected source/packet/route execution, recursive
hosting and supplier/exponent admission remain open. No human or formal-kernel
verification is claimed. The selected record and frozen sources are unchanged.

## Open next questions

Can one charged encoded exponent traversal be shared across the fixed matrix
coordinates while preserving all state and head contracts? Start with an exact
replacement for `high_power` and its lower/upper invoice; this audit leaves the
original implementation intact.

What numerical directory reserve suffices for the complete selected caller?
Join the full request catalogue and directory lifetimes to its parking schedule,
including descriptor and allocation costs. A source-meter O_q(D) bound alone
does not provide that admission.

Canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
Credit Jose Manuel / PR2569 and PR2501, ywz65 / PR2566 and PR2473, and the
retained source/stream lineage in [NOTICE.md](source/pr2569/NOTICE.md).
Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
Source pins, task refinement, overlap limits and review metadata are retained
in [SOURCES.json](SOURCES.json) and [TASK.json](TASK.json).
