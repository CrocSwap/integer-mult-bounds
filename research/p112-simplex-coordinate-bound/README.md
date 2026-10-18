# Six new P112 simplex exclusions

For `b=6,7,8`, independent P112 pieces with weights bounded by either
`3,5^3,6^b` or `4^2,5^2,6^b` cannot have code-intersection dimension at least
`b`, over any characteristic-zero field. These are six named profiles in
the pinned TWOSIDE `(6,4),(7,4),(8,4)` residues, not complete cell closures.

The new coordinate count for an `n`-vertex root simplex is

```
53*n*(n-1)/2 <= 112 + (M_n-1)*s + (n-2)*U,
M_n = max(2*n-3, floor(n^2/4)).
```

It gives contradiction margins **33,40,60** for both profiles, where the
older endpoint count gives negative margins. It generalizes PR3169's
six-vertex count to PR3170's larger simplices. [PROOF.md](PROOF.md) states
the exact hypotheses and characteristic-zero proof.

[RESULT.json](RESULT.json) records exact geometry, original survivor counts,
all six exclusions and the prior weight-cover boundary. The replay checks
4,097,782 five/six-flat kernels, 7,140 root planes, 960 reflections and
142,139 coordinate equality patterns. Sixteen behavioral test groups include
separate algebraic and subset-cover oracles, losing single-bound controls,
threshold failures and source/receipt mutations. This is author-checked
proof and finite evidence, not independent human or proof-kernel review.

## Reproduce

From the repository root, with Python 3.12+ and no third-party dependencies:

```sh
python3.12 -B scripts/research_package.py --package research/p112-simplex-coordinate-bound --check-only
python3.12 -B scripts/research_package.py --package research/p112-simplex-coordinate-bound
```

To keep the runner's temporary files external, set `TMPDIR` to a writable
session directory. Direct commands also work without Git:

```sh
python3.12 -W error -B research/p112-simplex-coordinate-bound/verify.py
python3.12 -O -W error -B research/p112-simplex-coordinate-bound/test_verify.py
```

`verify.py --output /NEW/EXTERNAL/RESULT.json` writes a fresh receipt and
refuses an existing file or output inside the checkout. A Git-free export
needs this package and the single declared P112 data input. Equality is on
proof-relevant JSON fields, not compressed-container bytes or timings.
[CHECKS.json](CHECKS.json) records commands and verification limits.

## Scope and source credit

Nick Petalas. Apache-2.0. DreamingOfClouds's PR3154 at
`708f0ad8928c383de8294aea3c126e9461d2066d` supplies TWOSIDE, its original
weight filters and the retained E8/P112 decoder lineage. Nick Petalas's
PR3164 at `857384079ab640a949fb7618b7909664d3e737e5` supplies the unchanged
geometry implementation and root-simplex proof. PR3170 at
`182168c4a7af570902b231aa6d35bbf4139098f2` supplies the larger-simplex
argument. PR3169 at `2dbbd3004b70772cef200e341037c7c05b094fbc` supplies the
six-vertex coordinate count. Its existing result is not counted as new.

Only the required frozen premises, original filter and notices are retained
under `vendor/`. [SOURCES.json](SOURCES.json) pins their original commits,
paths, Git blobs and SHA256 digests. Replay authenticates the bytes; source
origin was separately checked against those Git objects. The generic source
pins resolve at main, so replay does not need unrelated unmerged PR history.

The smallest cut allowance certified solely by the weight-cover capacities
is sixteen for every profile. A rank-four nonbasis anchor is absent or has
a certified allowance of twenty, beyond PR3167's twelve-cut hypothesis.
These are not lower bounds on actual geometric deletion sets; support
overlaps may reduce them. The audit concerns only that earlier weight-only
cover route. The separate
`4,5^9` quotient-independence result in PR3171 is outside this scope.

The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156)
and [TASK.json](TASK.json) record the handoff and changed scope. No full C5,
`C(P112)>=64`, decoder, supplier admission or new kappa is established.
The selected frontier stays unchanged. Development and local checking used
substantial automated assistance. Native, outer, all-size and analytic
obligations were not replayed or discharged.

## Open next questions

Bind a remaining actual profile to a valid quotient and its endpoint support
budget before expanding this method. The new inequality can reject some
budgets the older count could not, but a nonpositive margin is not a
construction. PR3171's separate `4,5^9` independence repair should not be
duplicated. [TASK.json](TASK.json) gives the next
question, feasible first step and blocker. No further supplier construction
is justified by these six local exclusions alone.
