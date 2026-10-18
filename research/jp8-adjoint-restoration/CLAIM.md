# Sprint claim

- Track: independent verification or formalization. OS assignment seed: **79**, drawn with Python `secrets.randbelow(100)` on 2026-10-13.
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Object: the selected #626 JP8 emitted scalar programs, including target preconditioning, dirty-helper compensation, early cleanup, full cleanup, and private-centre clear/copy operations. Seed 79 chooses index `79 % 2 = 1` in the sorted selected supplier list `[ck, jp8]`.
- Method: independently written exact reverse-mode pullback of every output coordinate in both orientations. No constructor or production replay imports. Mutate compensation, cleanup, copy and clear operations to obtain exact counterexamples.
- Deliverable: one standalone Python verifier, pinned input/certificate data, a scoped mathematical explanation, and validation evidence. No new kappa claim.
- Started: 2026-10-13 04:46 UTC. Expected finish: 2026-10-13 05:26 UTC. Reserve 05:16–05:26 UTC for verification and handoff.
- Coordination: GitHub's pinned-issue query returned no issues. Claim is local as requested; no reservation issue was opened. Open PR metadata was checked through #720 before claiming.

Three candidates were considered: the raw K-triangle read identity, cold-wrapper amplitudes, and the emitted dirty-input restoration identity. #646/#683/#687 cover K-triangle schedules; #702/#712 cover wrapper amplitudes. The chosen check uses a different execution direction from the selected forward state-map replays and includes arbitrary initial private-centre coordinates. #692 concerns weighted-stride structural closures and bilinear duality, not these concrete JP8 programs. Existing source and review attribution will be retained.

Scope is confined to this directory. The construction, selected frontier, `upstream/`, physical frame/wrapper semantics, recursion, cost model, and global assembly remain unchanged. Acceptance requires all output-coordinate identities in both orientations, meaningful rejected semantic mutations, source binding, and a reproducible offline command. This is a finite scalar verification, not a formal proof of the multiplication theorem.

Prepared for Sagar Thakrar (@thakrarsagar) with substantial OpenAI Codex assistance.

## Result update

Completed on 2026-10-13 at 05:03 UTC and submitted as
[PR #745](https://github.com/CrocSwap/integer-mult-bounds/pull/745).
All 724 output functionals pass in both orientations on 724 arbitrary input
coordinates. Six omission controls are rejected. The complete rank-one defect
from deleting backward event 13113 has 107 nonzero persistent outputs while
preserving all 716 ordinary input columns. A separate forward implementation
reproduced every coefficient. No new kappa is claimed.

The final portion of the session covered normal and optimized execution,
Python 3.14.8/3.11.15, minimal relocation, gzip recompression, corruption
rejection, the predecessor comparison, selected-record integrity, and handoff.
The final overlap check reached #743. Concurrent #734's private-input coverage
is explicitly credited; this adds reverse-mode evidence and the exact
clear-omission defect. Full cold/repository-wide and geometric/analytic checks
remain inherited, as recorded in README.md and VALIDATION.json.
