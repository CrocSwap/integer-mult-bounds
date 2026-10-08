# Cost-aware reclamation with compatible live controls

The concrete two-axis witness gives

    kappa = 51035127217697/10^18
    bit saving = 51037731934993/10^18
    backoff h = 1/10^12

It exceeds PR #67 at immutable source
`b3745601e947a94316bf25c2c6263d93c06e3364`, whose claimed κ is
10206752116843/200000000000000000, by exactly
683316741/500000000000000000. On the inherited 10^-11 grid, κ=5103512/10^11
also exceeds that pinned bound. This is a conditional finite candidate,
with the verification status below, not a completed theorem formalization.

## Composition

Both words compose Rohan Arun's PR #67 all-rank profile-cost selection
with Dominik Scholz's PR #68 compatible pending-carrier controls. Both use Avi Eisenberg's PR #62
graph and the original region order and matching.

Maintain `pending[slot] = next_use_frame`. An unchanged pending control is
inserted into the temporary dependency basis only when its current frame F,
the current clearing frame E and its scheduled next-use frame G satisfy
F <= E <= G. The two inclusions are the inherited exact envelope checks.
An actual use of that control raises it to E, charging the inherited literal
XOR and frame event. Its signal remains unchanged and its future use at G
remains valid. Pending entries are removed when consumed and added whenever
a preserved or duplicated carrier is assigned a future use.

PR #67's algorithm otherwise remains unchanged: every eligible dependent
retired candidate is examined, its explicit clearing expression is stored,
and an integer score from actual transition profiles chooses a witness.
The entropy/cleanup score remains solely a search heuristic, including for
live controls; no equality between predicted cost and final cost is assumed.
The complete final paid profile determines the exponent.

## Current finite evidence and pending checks

The imported PR #67 baseline was independently checked on both axes: full
dirty basis in both orientations, serialized XOR replay, paid transition
reconstruction, all C++ fixed profiles/CRT, complete profile identity, exact
root bracket and all 47 assembly inequalities/seven margins.

For both new words, the compiler's containment, scalar/scatter, role
uniqueness and total-rank assertions pass. Every paid transition was
reconstructed from the actual word and its full fixed-basis profile rebuilt;
6,049 / 7,997 CRT checks have zero disagreements. The complete two-axis moment has
a strict accepted upper bound and a strict rejected lower bound at adjacent
10^-18 bit grid points. The balanced assembly and eventual arithmetic
cutoffs pass at the displayed κ; its next grid point is rejected.

**At initial handoff, independent complete dirty-basis replay of the new
h=23 and h=25 words and broad repository tests are pending.** `candidate.json` records
`pending_full_replay_axes=[23,25]`. This status is deliberately
explicit so a draft can be published before the remaining validation runs.

## Reproduction

The pinned PR #67 baseline package is preserved at
`research/slot-cost-rank-pair`. To regenerate the concrete candidate:

```sh
python3 research/cost-live-both/experiment.py --h 23
python3 research/cost-live-both/experiment.py --h 25
```

Adding `--full-replay` runs the compiler's complete dirty-basis test and the
independent serialized replay before writing the candidate. The read-only
`python3 research/cost-live-both/validate.py` checks the already serialized
words, profiles and exact arithmetic without changing the selected candidate. On this machine
use the process-scoped environment override
`CXX='c++ -isysroot /Library/Developer/CommandLineTools/SDKs/MacOSX15.2.sdk'`.
`candidate.json` pins the compiler, profile oracle, driver, PR #67 exact
arithmetic source and unchanged graph, and records every complete paid child
multiplicity. `frame-compiler.json` pins each serialized word.

No original-envelope interpretation, data-corner, fixed-alphabet/multitape,
analytic, semantic, routing, recovery or eventual theorem interface is newly
proved. All inherited hypotheses remain explicit dependencies; no global
optimality or practical runtime gain is claimed.

## Attribution

Rohan Arun contributed the PR #67 all-rank fixed-profile-cost selection and
profile oracle, with OpenAI Codex assistance. Dominik Scholz contributed the
PR #68 compatible pending-control extension and this direct composition,
with substantial OpenAI GPT-6 Astra/Codex assistance. Preserve Avi Eisenberg's
PR #62 graph (Claude assistance), eumemic's PR #57 compiler, Chafik Boukhalfa's
PR #60 priority, the PR #63 composition, and all inherited author/license
notices. PR #67's degree-eight directed exact moment bounds and inherited
balanced assembly are used unchanged. Apache-2.0 applies.
