# Tightened slack constants on paid padded triple covers

Conditional

T(n) = O(n (log n)^(1-kappa)),  kappa = 206798323483/500000000000000
= 4.13596646966e-4,

413,264 grid points (denominator 10^15) above PR #137's
206798116851/500000000000000 = 4.13596233702e-4, the furthest published
value at the time of this branch. The next 10^-15 kappa grid point is
rejected by PR #137's own check.

## What changed

One instantiation choice, nothing structural. PR #137 (like #104, #110,
#117, #128, #134 and #135 in this lineage) instantiates the retained
47-constraint assembly with the loose legacy slack constants beta =
10^-6 (STOP) and a 10^-14 declared leaf-over-bit backoff. In this lineage
these are declared free positive instantiation parameters, not derived
constants: PR #97 used beta = 1/4; the batched assembly used beta = 1/1000;
PR #104 used beta = 10^-6; the assembly machinery is unchanged across all
three, and of the 47 strict constraints beta enters only through
positivity and leaf-ordering margins, all checked at exact rationals.

This package re-instantiates with beta = 10^-12 and backoff = 10^-16, and
re-runs PR #137's own certificate chain end to end from its pinned inputs
(SHA-256 pins in SOURCE.json): the padded bit provider with paid padding
deltas, the padded cover geometry checks, the weighted local-ring
compilation, the finite bridge, the kappa bracket with next-grid
rejection, and all 47 strict constraints and 7 margins. Everything else is
byte-identical to PR #137: no word, frame, matching, gauge, bridge,
router, reserve, bit-side or geometry change.

## Reproduction

    python3 research/tightened-slack/certificate-tight.py --write

(same venv as the repository; runs in minutes; the frozen certificate is
regenerated from the pinned sources)

## Credit and scope

All construction credit belongs to the inherited lineage as recorded in
the repository's NOTICE and SOURCES: PR #131's physical word and
cover-local reuse, PR #137's paid padded triple covers (eumemic), and
every earlier interface those PRs attribute. The only change here is the
value of two declared slack constants. This is an instantiation
refinement in the genre of #61, #100 and #107. It claims no new producer
and no global optimality; the inherited analytic, fixed-tape, uniform
batching and borrowed-row interfaces remain written proof dependencies
exactly as in PR #137.
