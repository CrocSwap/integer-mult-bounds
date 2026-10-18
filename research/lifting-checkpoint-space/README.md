# Less clean history for the batched lifting core

**Conditional space improvement; same map and time exponent.** Under the
source premises of Jose Manuel's [PR #3109](https://github.com/CrocSwap/integer-mult-bounds/pull/3109),
this construction reduces additional clean workspace from

```
O(N r^(1197203/600000))   ≈ O(N r^1.995338)
```

to

```
O(N r^(1797203/1200000))  ≈ O(N r^1.497669),
```

while preserving its `O(N r^(1199003/600000))` time bound, nonlinear order,
exact inverse and numerical error guarantee. Here `N=2^n`, `n=Theta(r)`
and component width `w=Theta(r)`. This is a standalone core-space result.
It supplies neither a new multiplication κ nor a completed native caller.

The original routine records every transition until its output is copied.
We instead retain a chain of complete configurations and reuse one shorter
history region. Compute-copy-reverse on each segment preserves arbitrary dirty
output XOR targets and clears the checkpoints. For a machine using complete
configuration size S and time T, this costs `O(T+S)` time and
`O(S+sqrt(ST))` clean space. Checkpoints occupy one sequential tape; moving
between adjacent slots costs `O(kS)`, including the backward cleanup.

This is a classical Bennett checkpoint tradeoff. The contribution is its
explicit binding to the inherited C routine's complete configuration,
the sequential tape layout, and its complete consequence for PR #3109.
The configuration audit includes recursive parked arrays, compact rotations,
keyed repair, ordinary-interchange work, control state and mutable compilation.
It gives `S=O(Nw)+F`, not the size of only the visible coefficient array.
The [written proof](PROOF.md) retains the full F-dependent formulas; the
displayed powers fix the inherited compiler/prime. No parameter-uniform bare
`+F` suffix is claimed.

## Reproduce

Exact base: `997e6a9ca7b4f95d50e366f61412fd640d72a88a`.
Python 3.12 standard library, from the repository root:

```sh
python3.12 scripts/research_package.py --package research/lifting-checkpoint-space
```

Expected: `PASS_LIFTING_CHECKPOINT_SPACE`, eight passing control groups,
and a successful package replay. The verifier compares every typed field of
[RESULT.json](RESULT.json). Direct replay also works in a read-only Git-free
export containing this package and the six declared input files:

```sh
python3.12 -I -O -B research/lifting-checkpoint-space/verify.py
```

All six live sources are authenticated by SHA256 and Git blob before execution.
The predecessor model is compiled directly from its authenticated bytes.
Full Git history is needed only by the generic package metadata/provenance
checker. Source pins and credited dependency commits are in
[SOURCES.json](SOURCES.json); scope and finite domains are in [TASK.json](TASK.json).

## Evidence and limits

The completed finite domain includes 2,720 exhaustive source/dirty-target
cases, 32,832 integer planner cases and 40 actual Boolean Gaussian backend
calls. The latter include both orientations, negative values, nonconsecutive
axes and three forward/inverse nonlinear macro pairs through the unchanged
predecessor evaluator. Each Gaussian call executes both schedules on the
same program, input and dirty target. Cleanup, source preservation and
identical outputs are checked.

One rank-three, eight-entry, 16-bit fixture has 30,464 overwrite gates and
518 configuration-payload bits:

| Executed schedule | Peak active/checkpoint/history payload | Forward gates | Reverse gates |
|---|---:|---:|---:|
| Original whole trace | 30,982 bits | 30,464 | 30,464 |
| Checkpoint chain | 7,952 bits | 57,120 | 57,120 |

Both also retain the same 518-bit source adapter and 256-bit target.
The receipt separately charges copies, target XOR, initialization, cleanup
and 18,648 checkpoint-bank moves. These are logical payload counts, not
Python RAM measurements or timings. Program storage and host controller
objects are outside this finite payload comparison. The generated direct
Boolean circuit has no fast physical C tariff; it tests the interface.
The bank-move count covers travel between slot origins; local copy scans
and rewinds are additionally included in the proof's `O(kS)` allowance.

Eight control groups cover information-losing overwrites, omitted cleanup,
corrupt history, a costly reset-to-origin layout, invalid projections/aliases,
removed Gaussian output writes, insufficient headroom, wrong inverse use,
source drift, receipt corruption and read-only optimized export.

The proof is conditional on the named physical source/compiler contracts;
archival merging of those sources is not independent mathematical approval.
Finite replay does not prove the complete source machine. This package
does not execute the enormous selected cover or solve external wrappers,
collector integration, dirty hosting or supplier admission. Its time exponent
is unchanged, with additional constant-factor recomputation. Deeper classical
checkpoint tradeoffs are outside this implemented two-level point.

## Open next questions

1. Lower one complete segment snapshot into the physical C interpreter,
   including heads and control state. This needs the complete source machine
   and independent review of its locality/compilation premises.
2. Price the smaller reserve in an actual native caller's owned-slot census.
   The wrapper/collector scope belongs to separate concurrent work.
3. Derive and test the full depth-dependent invoice before adding checkpoint
   levels; smaller reserve exponents also bring larger recomputation constants.

The question, first step and blocker for each are recorded in TASK.json.

## Credit

Prepared by **Tekalign**, with substantial **OpenAI Codex** assistance in
analysis, implementation, testing and writing. New work is Apache-2.0.
No independent human or formal-kernel review is claimed.

Credit C. H. Bennett's [1973 reversible simulation](https://doi.org/10.1147/rd.176.0525)
and [1989 time/space tradeoff](https://doi.org/10.1137/0218053).
Jose Manuel (`jmbarrancoml`) supplied PR #3109, the exact C layer (PR #2287),
compact monomials (PR #2250) and the ordinary completion (PR #2899), retaining
Douglas Colkitt's source construction and the credited work of Nick Petalas,
David Arias and earlier contributors. Ross Richardson's PR #3072 supplies
the earlier protected evaluation pattern. Tekalign's PR #3033 and PR #3025
provide the residue and blocked-lifting predecessors. Their exact pins and
inherited source manifests remain unchanged.

Related earlier packages [clean-checkpoint](../clean-checkpoint/README.md)
and [reusable-clean-checkpoint](../reusable-clean-checkpoint/README.md) study
dirty product-shear schedules. This package concerns complete computation-state
snapshots for the newer batched lifting backend and uses no code from them.
