# Cached physical controls for selected P104 scalars

All 43 width-64 scalar templates from PR6511 now have literal three-tape routes
with two reusable finite-control bits. The complete source-weighted local bill
falls from 153820224 to 117253520 physical operations per complex coordinate.
The saving is 36566704 operations: 31347396 unit moves and 5219308 reads.
All 15227252 target writes remain. One carry bit, two scratch bits and all
heads return to their entry state. Multiply the bill by payload dimension D.

The optimality claim is precise: all allowed no-prefetch two-bit cache routes
for each fixed template. It does not cover different circuits, arbitrary
physical compilers or weighted operation tariffs. [PROOF.md](PROOF.md) states
the policy and proves the cache invariant and potential certificate rule.
[RESULT.json](RESULT.json) gives every template, source weight and both bills.
The compressed certificates contain all 83619 reachable layer states and an
attaining path. The largest layer has 127 states.

The checker authenticates the selected source WORD, unchanged PR3241 Tape
implementation and byte-exact PR6511 circuits before use. It checks every
certificate edge and route instruction, then executes 473 paired physical
fixtures through both compilers. A direct Boolean interpreter and aligned
Fraction fixtures check the outputs. Six controls reject changed potentials,
a missing reachable state, omitted cache cleanup, incorrect head return,
a wrong control mask and a stale cached target.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/p104-cached-control-routes
```

Both registered modes are read-only. To regenerate the exact finite
certificates and receipt, run `verify.py --write` explicitly. Normal and
optimized CPython 3.12 replay, committed bytes/modes and read-only Git-free
source export are checked before publication. Full-history preflight is not
run in this shallow checkout. Hosted checks and independent mathematical
acceptance are separate from these local checks.

## Scope and open obligations

Both operand ribbons must already be supplied at their local origins. This
compiled fixed-width route does not provide an encoded-width controller,
global owner access, coordinate dispatch, a native child, physical reset,
or a complete supplier invoice. The 7936 bit-reset requests remain explicit
and unimplemented. Arithmetic alignment and range are the PR6511/PR6499
contracts. No new kappa, selected assumption discharge or frontier change.

## Open next questions

Construct a fixed-tape owner layout that supplies these local ribbons and
returns them at the actual selected events. This is the next cost boundary:
a local saving can be lost in global field acquisition. Native children and
physical reset also need separate implementations. Recheck current claims
before taking any of these scopes.

## Coordination and credit

Canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, revision 8 and live
handoffs/PRs were checked before work and submission. The cached search covers
local notes, open PRs, Discussions and older closed PRs; it is not a novelty
certificate. [Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5600#discussioncomment-19364256).
TASK.json preserves the original card and the physical-interface scope change.
SOURCES.json binds live main inputs; ORIGINS.json binds the self-contained
PR6511 circuit snapshot. No side-branch checkout is needed for replay.

Credit Sagar Thakrar / thakrarsagar / PR3241 for the metered tape model;
Nick Petalas / PR3152/3159 and PR6511 for the logical circuits; DreamingOfClouds
/ PR6030 and all retained P104/native/compiler work. See [NOTICE](NOTICE).
Ali Romman with substantial OpenAI Codex assistance; no subagents. Apache-2.0.
