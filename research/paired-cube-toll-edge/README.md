# Re-instantiated atom exponent at the toll edge on the searched pair module: conditional κ = 5.557315e-4

Under #157's retained interfaces this package certifies

    T(n) = O(n (log n)^(1 - kappa)),   kappa = 1111463/2000000000 = 5.557315e-4

This is #157's construction unchanged — eumemic's paired cubes at p = 11 with
the searched (annealed) pair module, physical frames, late-read reuse and the
paired-cube bit word — with one assembly instantiation constant re-chosen: the
atom exponent `theta`, from the merged value `1/1000` to its exact toll edge
`556349912/10^12`.

The atom exponent is a free positive constant of #144's retained assembly: it
enters only through `ab = (1-theta)*COARSE + theta*OLD` and the strict toll
`ab < theta < 1-ab`. #157's bit side binds (coarse saving 5566382/10^10 below
the complex saving 5622769/10^10), so raising `ab` onto the binding face moves
kappa directly. `ab` is strictly increasing in theta while kappa is strictly
decreasing across the acceptance window, so the grid-maximal instantiation is
the first 10^-12-grid point at which the strict toll holds: exactly one step
above `theta* = COARSE/(1+COARSE-OLD)`.

| | atom exponent | kappa |
|---|---:|---:|
| #157 (inherited) | 1/1000 | 5555021/10^10 |
| this branch | 556349912/10^12 | **1111463/2*10^9** (+2294 grid points) |

The phase-stop (1/10^6) is left at #157's inherited value: it is slack here,
because the binding bit face sits below the `(1-beta)*AC - 10^-10` ceiling.

No word, frame, pair, certificate or interface changes. Every inherited
interface remains an assumption exactly as in #157. Conditional, as in #157:
no unconditional multiplication theorem is claimed.

Failed next-grid upper-enclosure tests mean only the failure of that
certificate, not a mathematical optimality result.

## Verify

From the repository root (Python 3.10+ stdlib; a couple of minutes; do not
use `-O`):

    python3 research/paired-cube-toll-edge/verify.py

The script reproduces #157's published kappa = 5555021/10^10 exactly at the
inherited constants (#157's own producer, certificates, bridge and assembly),
checks that one 10^-12 step below the re-instantiated theta violates the
strict toll, then re-runs the same 47-constraint assembly at
theta = 556349912/10^12 and asserts kappa = 1111463/2000000000 with the next
10^-10 grid point rejected.

## Credits

- eumemic: #157 (searched pair module, physical frames, the certificates this
  branch re-prices), #152, #117, with Anthropic Claude assistance.
- gupt1156: #148 (the tightened adapter toll lineage this constant belongs to).
- icekylinx: #144/#130 (paired cubes, shared cores, the retained assembly).
- Zhihao Chen (#97), Swapnil Jain (round-seven checkers), an664 (#128),
  DaysSky (#150), hpst3r (#147), jamesyc (#124), SovereignSteak (#122).
- The re-instantiation and this package: Abhinav Ramachandran with Hermes
  (Nous Research) assistance.

## Scope

All inherited written proof dependencies (paired source scheduling, shared-core
execution, word-frame nesting, uniformity, analytic and tape contracts) remain
explicit assumptions, exactly as stated in #157.
