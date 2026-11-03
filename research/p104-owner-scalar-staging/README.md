# Whole-field owner staging for selected P104 scalars

The selected 19288 scalar events now have a four-tape owner-to-circuit
construction. It acquires whole fields, runs PR6513's cached local routes,
and returns every owner value and clean staging buffer. At width 64, the
complete scalar bill is **1236161936D - 5196390** unit moves, reads and writes
for every positive payload dimension D. Native and reset work are separate.

The initial one-coordinate design needs quadratic travel in the same
field-major layout. Whole-field staging saves 822169424 moves at D=1 and
463823251912 at D=17 against that design's exact visit-order optimum. It uses
256D clean staging bits instead of 128. Both use one carry bit, two
finite-control bits and four tapes. The owner backing is 102272D bits.

[PROOF.md](PROOF.md) gives the transfer construction, complete accounting and
all-D optimum over the declared field visit orders. The affine certificate
checks 41232 states and every edge on the whole ray D>=1; interpolation is
not used as proof. [RESULT.json](RESULT.json) gives complete costs and four
finite comparisons. All 43 templates run on literal tapes at D=1,2, with
every untouched owner bit, source, carry, staging bit and head checked.
Five controls reject bad potentials, an incorrect total, source aliasing,
a dirty staging destination and aliased transfer tapes.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/p104-owner-scalar-staging
```

Both registered modes are read-only. `verify.py --write` explicitly rebuilds
the affine certificate and receipt. Exact source, blob and byte pins are
checked before import. No pending branch checkout or Git is needed for
scientific replay. Normal/optimized registered replay, committed bytes/modes
and read-only Git-free export checks are run before publication. The optional
full-history preflight is not run in this shallow checkout.

## Limits

W=64 is fixed. D is arbitrary in the proof, but each emitted controller is
specialized to D. Initial layout construction, uniform control, native calls,
physical reset, full supplier funding and outer admission remain open.
The owner head returns at each external boundary; the external operation
must preserve that field layout and return clean workspace and heads. The
7936D bit-reset requests are explicit and unimplemented. Literal fixtures
cover every template, not the complete physical word. No new kappa, selected
assumption discharge or frontier change is claimed.

## Open next questions

Can two staged fields remain live across adjacent scalar events? Repeated
acquisition and return can cost more than a complete exclusive-owner cache.
The next construction must charge each eviction, acquisition and native
boundary flush. It must restore the full owner tape before external work.
Native and reset bodies still require their own implementations.

## Coordination and credit

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5600#discussioncomment-19364974)
and [explicit workspace scope change](https://github.com/CrocSwap/integer-mult-bounds/discussions/5600#discussioncomment-19365045).
Main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8 and live
handoffs/PRs were refreshed. Cached overlap includes older historical results
and is not a novelty certificate. TASK.json retains the original task card.

Credit Sagar Thakrar / PR3241 for the metered tapes; Nick Petalas's scalar
circuits, PR6511 and PR6513 for all inherited local work; DreamingOfClouds /
PR6030 and the retained native/compiler lineage. David Sanders's QQ16 oriented
scratch sweeps and Nick Petalas / PR2722 provide a distinct prior use of
exact physical sweep scheduling. Clean transfer and dynamic programming
are established methods. Exact inherited notices are retained in inputs.
Ali Romman with substantial OpenAI Codex assistance; no subagents. Apache-2.0.
