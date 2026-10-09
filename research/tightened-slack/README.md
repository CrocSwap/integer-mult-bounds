# Tightened slack constants on the conservative paired scratch-reuse candidate

Conditional finite arithmetic candidate, in exactly the status of PR #135
(this branch's parent): the shared-scratch execution theorem and the
inherited all-size analytic/tape contracts remain written proof
dependencies, and the paired physical replay is not rerun here.

T(n) = O(n (log n)^(1-kappa)) with

kappa = 362108584810/10^15 = 3.62108584810e-4,

361,856 grid points (denominator 10^15) above PR #135's
181054111477/500000000000000 = 3.62108222954e-4, the furthest published
value at the time of this branch. The next 10^-15 kappa grid point is
rejected by PR #135's own check.

## What changed

One instantiation choice, nothing structural: no word, role, frame,
matching, gauge, histogram penalty, bridge, router, reserve or bit-side
change. The complex saving, the physical role counts, the compensated
birth-cut aliases, the data-wire moment penalty and the stopped bit
supplier are byte-identical to PR #135.

PR #135 (like #104, #110, #117, #128 and #134 in this lineage) instantiates
the retained 47-constraint assembly with the loose legacy slack constants
STOP = beta = 10^-6 and a 10^-14 declared leaf-over-bit backoff. In this
lineage these are declared free positive instantiation parameters, not
derived constants:

- PR #97 used beta = 1/4; the batched assembly used beta = 1/1000; PR #104
  used beta = 10^-6; the assembly machinery is unchanged across all three.
- Of the 47 strict constraints, beta enters only through positivity and
  leaf-ordering margins, all checked at exact rationals.
- The complex side binds, so the assembly bit saving is exactly
  (1-beta) * ac - backoff; the slack directly depresses the ceiling.

This package sets beta = 10^-15 and backoff = 10^-17 and re-runs PR #135's
own certificate chain end to end from its pinned inputs: the stopped bit
supplier reproduction, the finite bridge with the reflection-audit charge
checks, the paired histogram and telescoping identity, the rational
log/exp moment penalty enclosures, the kappa bracket with next-grid
rejection, the +3%-over-PR132 target, and all 47 strict constraints and 7
margins. The chain passes at the refined constants and yields the kappa
above.

## Reproduction

    python3 research/tightened-slack/certificate-tight.py

(same venv as the repository; the pinned inputs are those of PR #135,
verified by SHA-256 in SOURCE.json)

## Credit and scope

All construction credit belongs to the inherited lineage as recorded in
the repository's NOTICE and SOURCES: the conservative PR131 physical word
with compensated scratch reuse, PR130's three-stage Cayley cover, PR132's
orthogonal first-stage lockstep pairing, and their combined PR #135 by
DanieleCorso, plus every earlier interface those PRs attribute. The only
change here is the value of two declared slack constants. This is an
instantiation refinement in the genre of #61, #100 and #107; it claims no
new producer, no new physical execution, and no global optimality.
