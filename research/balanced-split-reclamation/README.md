# Balanced coarse sums on anchored split frames

The selected finite construction gives the conditional integer-multiplication
bound

\[
T(n)=O\bigl(n(\log n)^{1-\kappa}\bigr),\qquad
\kappa=\frac{12886963972497}{250000000000000000}
=5.1547855889988\times10^{-5}.
\]

This is **0.2590891819% above PR71** at commit
`1bef94fd40a746452548c84a4a8f8834670a3113`. It is a comparison of conditional
asymptotic exponent bounds, with no global-optimality or measured-runtime claim.

The construction combines eumemic's PR69 balanced coarse columns with Chafik
Boukhalfa's PR71 anchored `[1,1,2]` split graph. It uses the inherited joint
reversible frame compiler and compatible pending controls, and orders both
eligible live controls and retired dependency candidates by their actual
profile cost. The latter changes the temporary dependency basis, not just the
choice among the first basis's dependent rows. Pending controls are priced
against their known next use. Every selected clearing expression is emitted
as literal XORs, and all frame moves and final cleanup remain charged.

| Quantity | Pinned PR71 | This construction |
|---|---:|---:|
| Roles at h=23 | 27,455 | 27,338 |
| Roles at h=25 | 36,015 | 35,939 |
| Physical width W | 135,075,665 | 134,671,969 |
| Complete rank mass | 77,666,660,475 | 77,434,535,275 |
| Rank deficit | 1,846,900 | 1,846,900 |

The strict bit-saving witness is `51550513208569/10^18`. The full paid child
list of PR71 has a rigorous moment lower bound above one at this value. The
new list has a rigorous upper bound below one. Its next `10^-18` bit grid
point is rejected, as is the next kappa grid point in the unchanged balanced
assembly. All 47 strict inequalities and seven margins are checked exactly.

## Reproduction

From the repository root, with Python 3.11+ and a C++17 compiler:

```sh
make -C research/balanced-split-reclamation verify
make -j1 verify
```

The first command regenerates both selected words byte-for-byte, independently
replays every input/target/dirty basis vector in both orientations, derives
all physical transitions from literal XOR incidences, recomputes every
fixed-basis profile with the inherited bounded-minor/CRT checks, rebuilds
the complete global profile and exact arithmetic, and runs twelve failure-mode
tests. A second logarithm/exponential evaluation uses a different range
reduction and Taylor degree. This is a second arithmetic implementation,
not independent expert review of the theorem.

`selected/` contains the words, actual profiles, receipts and exact certificate.
`SOURCE.json` freezes consumed sources and deliverables; verification never
rewrites this manifest. `pin.py` is an explicit maintenance operation.
`generate.py --output <directory>` produces fresh artifacts without modifying
the selected witness. The proof is in [paper.tex](paper.tex) and [paper.pdf](paper.pdf).

The selected graph uses columns rather than a three-addition coarse chain,
split vector `[1,1,2]`, and the lowest intact pair first in each common-point
ordering. The h23 region order is `cover-core`; h25 uses `reverse-node`.
The oracle's integer entropy score is only a deterministic search heuristic.
The final complete physical profile, not the score, determines acceptance.

## Proof boundary and attribution

The original-envelope interpretation, all-size residual/frame compiler,
fixed finite-alphabet tape layout, semantic and analytic multiplication
reduction, routing, prime setup and exact recovery remain inherited
assumptions. The complex branch is unchanged. Exact finite checks do not
constitute a complete formal proof of the multiplication theorem.

This composition, cost-ordered dependency basis experiment, independent
reproduction and package were prepared for **huxint with OpenAI Codex
assistance**. Credit eumemic for PR57's reversible region compiler and PR69's
coarse-column identity; Avi Eisenberg for PR62's interval/core-aware graph;
Rohan Garg for PR59's split operation; Rohan Arun for PR65's schedules and
PR67's cost oracle and numerical refinement; Dominik Scholz for PR63's
composition and PR68's compatible pending controls; and Chafik Boukhalfa for
PR60's ranked reclamation and PR71's anchored split/next-use composition.
All prior contributors retain their original notices. See [NOTICE](NOTICE).

The preserved contributor files in `vendor/` are unmodified snapshots, used
for provenance and the complete PR71 comparison. The inherited repository
files are retained unchanged. No endorsement or completed expert review by
those contributors is implied.
