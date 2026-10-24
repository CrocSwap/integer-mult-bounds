# Exact scope of Matarener's PR #4610 scalar-order comment

**No corrective construction or replay is required to resolve this comment.**
It reports useful negative evidence within a bounded, explicitly stated family.
The appropriate response is to acknowledge it and narrow open question (3) to
changed native maps/interfaces or other constructions outside that family.

Source: [Matarener, comment 6342665165](https://github.com/CrocSwap/integer-mult-bounds/pull/4610#issuecomment-6342665165),
created and last updated 2026-10-22 14:02:04 UTC. The root's API capture was
retrieved at 2026-10-22 15:43:28 UTC. This assessment reads that captured comment;
it does not independently reproduce the author's unpublished scripts or solver
results.

| Source word | Reported experiment | What it establishes within the report |
| --- | --- | --- |
| `4b4c75bc0fd64d3eee54029e8d2fab834251fca6`, kappa 0.00302152 | Eight exact MILP variants, one commuting pair per group | Zero gain in those solved instances; tie swaps occur |
| Same old word | Three plateau chains, 16 solved steps | No improvement along those chains |
| Same old word | All acyclic permutations in commuting-run windows through K=8 | No improvement in that bounded window family |
| `1eb8da6cfb35512c0cc2533413e5ca42f48e13c6`, kappa 0.00302176 | Window screen at K=3,5,6,7,8, about 1.6M permutations | No improvement in those bounded windows; identity-order control clean |

The current word was **not** reported to receive the old exact MILP or plateau
replays. Neither revision receives a global optimality claim over arbitrary
chronological scalar words. Warp input/output frames remain fixed; scalar
frames are reselected and climbs priced by `d^(1-kappa)`. Moving warps, changing
their maps or gauges, and redesigning scalar/owned interfaces are expressly
outside the comment's scope.

The comment's old profile `2201/412/506/135/36` omits the unchanged eight rank-8
owned-center charges in its shorthand. The current full local profile is
`{1:2201,2:412,3:510,4:127,5:40,8:8}`. These refer to distinct source words and
must not be conflated.

Suggested factual resolution: acknowledge Matarener's bounded no-gain result,
credit the experiment, and record that subsequent work targets changed physical
phase/native interfaces. Any external response is the parent's responsibility.

This note supplies no new native proof, paid-profile improvement, or kappa.
