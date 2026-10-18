# P104 endpoint-support capacity

The 406-lifetime necessary-screen control in [PR2889][2889] cannot realize the
frozen X-only monotone correction. It can span the endpoint frames, but cannot
carry enough distinct required coefficients. This package proves two further
necessary histogram rows and checks their finite geometric premises.

For each orientation there are **4,656 residual demands**. A proper subspace
of any endpoint contains at most **30** of its residual labels. Consequently
335 histories `(1,7,1)` and 71 unit-step histories can cover at most
`335 + 30*71 = 2465`, strictly below 4,656. The deficit is 2,191 in each row.
This rejects those exact histories, not every network with 406 lifetimes.

A different 400-lifetime profile passes these rows and the earlier numerical
screens, including the declared favorable moment relaxation. Thus this is a
specific compatibility obstruction, not a new universal lifetime floor, a
rejection of the P104 family, a correction circuit or a new exponent.
The selected result and frozen predecessors are unchanged.

## Model and predecessor boundary

Use the frozen 104-port PR1972 paths retained by PR1991. Write the required
added correction as `C = I-G/2`. Its 4,992 nonzero entries have magnitude 1/2.
The sources X are immutable, the targets Y are write-only, and their original
frame paths increase by inclusion. Source lines `ell_s` and final target
hyperplanes `H_t` are distinct in the nine-dimensional binary frame space.

New helpers start at ZERO with source-independent arbitrary dirty values,
follow increasing frame paths, and end at FULL with their logical dirt
restored. Reinitialization counts another lifetime. Added operations are
fixed rational linear combinations within equal frames. Arbitrary relays,
cancellation and even singular same-frame mixing are allowed. The correction
cannot read Y or the original helper/private fields, write X, descend, change
the original paths or use source-dependent initialization. The retained
channel does not write X or read Y, which the replay checks.

These are the same substantive boundaries used by PR2353, PR2614, PR2640,
PR2675 and PR2889. We reuse their source-support/dependence-path reasoning.
The new restriction counts *distinct residual labels*, rather than the binary
dimension of their span or all source-target pairs at an interior cut.

The inspected pending predecessor is Hiroki Kumazaki's PR2889 at
`5cd56602d65c4d0767c86b518a37168d571cf3ba`. Its dimension rows correctly
leave its 406 profile as a necessary-screen control, not a construction.
This package answers its explicit compatible-endpoint handoff without
changing that predecessor. Source pins for every executable input are in
[SOURCES.json](SOURCES.json). No pending supplier is admitted here.

## Endpoint residuals and proper-subspace capacities

Let `q_s` be the nonzero vector of `ell_s`, and `h_t` the unique nonzero
ordinary covector with kernel `H_t`. This does not identify the compressed
root-label pairing with the ordinary binary dot product.

For each target t, remove any demanded source whose label is in any earlier
proper Y_t frame, or whose X_s path visits H_t. Denote the remaining labels
by `N_t`. For each source s, remove any demanded target for which some X_s
frame of dimension greater than one is contained in H_t. Denote the remaining
target normals by `F_s`. These removals grant all possible bypasses without
requiring chronological access, which favors the proposed correction.

The replay reconstructs the root order and all frame paths from the two
pinned JSON inputs, then checks:

- No direct source-to-target contact at H_t, and no target visits a source line.
- The source labels and target normals each lie in an affine odd hyperplane.
- Each N_t spans H_t; each F_s spans `ell_s^ann`, of dimension eight.
- Both `sum_t |N_t|` and `sum_s |F_s|` equal 4,656.
- For every endpoint, the largest intersection of its residual set with any
  proper subspace is 24, 28, 29 or 30. Each orientation has respectively
  12, 24, 24 and 44 endpoints of those types.

It suffices to enumerate the 255 hyperplanes inside each eight-dimensional
endpoint. Every proper subspace extends to one of these hyperplanes.
The primary implementation tests the 510 nontrivial ambient functionals
other than the endpoint annihilator; they represent each proper hyperplane
twice. RESULT.json includes a maximizing functional for every endpoint.
The separate implementation computes all 512 character sums by a nine-stage
integer Walsh-Hadamard transform and recovers the intersections as
`(|N| + character_sum)/2`. It uses bitset frame paths, imports no primary or
predecessor implementation, and agrees on every endpoint and witness.

## Written program-to-histogram implication

Project each helper's logical row onto the independent X inputs. Its source
support lies in its current frame. Initialization has empty support;
equal-frame operations preserve the invariant; increasing transport cannot
violate it. Restored lifetime boundaries have zero X row, so reuse does not
introduce an uncounted source-dependency edge.

Fix target t. Any nonzero coefficient indexed by N_t must reach H_t through
a new helper entering from a proper frame A. It cannot be delivered earlier,
and cannot arrive by direct X read, by the definition of N_t. Expand a finite
linear program into its chronological dependency graph. A nonzero final
coefficient has a nonzero path even with cancellation. That path supplies
an entrance whose A contains its source label. Mixing at H_t cannot create
a source coefficient absent from every entrance.

For an entrance from dimension d, its number of distinct N_t labels is at
most 30 by the checked proper-subspace bound. It is also at most `2^(d-1)`
for d>0, since all source labels are odd under a common nonzero functional.
A ZERO entrance carries none. Define

```text
f(0) = 0
f(d) = min(2^(d-1), 30), for 1 <= d <= 7.
```

The union bound gives `|N_t| <= sum_entrances f(dim A)`. It permits duplicate
labels, unproductive entrances, arbitrary relays and dirty-state compensation;
none makes the bound stronger than justified.

Dually, for source s, each coefficient indexed by F_s must be read at ell_s
and leave on a helper's first departure to B. A later source read reaching
the target would have been removed from F_s. Target reads and source writes
are forbidden, so the dependency cannot bypass that departure. Its target
normal belongs to `B^ann`, a proper subspace of `ell_s^ann`. The same argument
bounds its distinct F_s normals by `f(9-dim B)`.

A nested lifetime visits at most one designated source line and at most one
designated target hyperplane. Thus summing the endpoint inequalities counts
each lifetime at most once in each orientation. For a positive composition
h of nine, define:

```text
a(h) = f(dimension immediately before visiting dimension 8), or 0 if absent
d(h) = f(9 - dimension immediately after leaving dimension 1), or 0 if absent
```

For the complete history histogram x, every permitted correction satisfies

```text
sum_h a(h) x_h >= 4656
sum_h d(h) x_h >= 4656.
```

Visiting dimension eight directly from ZERO, or leaving a line directly for
FULL, contributes zero. Reversing a history exchanges its two weights.
The replay checks all 256 histories, including asymmetric and empty-contact
controls. The universal implication above is a written proof, not finite
network enumeration or a proof-assistant theorem.

## Rejected and surviving profiles

Let c count histories `(1,7,1)` and u count nine unit jumps. Their support
weights are respectively 1 and 30 in both orientations. The earlier
span-dimension weights are 1 and 7.

| c | u | Lifetimes | Span total | Support total | New rows |
|---:|---:|---:|---:|---:|---|
| 329 | 71 | 400 | 826 | 2459 | fail |
| 335 | 71 | 406 | 832 | 2465 | fail |
| 253 | 147 | 400 | 1282 | 4663 | pass |

The last profile also has 9,661 capacity at every old interior cut, 400 proper
arrivals and departures, rank mass 3,600, and 744 ideal idle rank units.
It exceeds the reported mixer lifetime floors, stays in the quoted 387 to
482 investigation window, and passes PR2889's dimension rows.

Reusing Douglas Colkitt's exact rational ceiling engine, the primary replay
certifies its moment upper bound **0.999729278053145** at the selected complex
primitive saving `67018507072324140917/40000000000000000000000`. This is only
the inherited `m=73`, 832-family, nine-stage, centre-56, ideal rank-51-idle
relaxation, including the original channel profile. The original transport
profile is recounted from the literal word. The engine is source-authenticated
but not independently reimplemented. No actual geometry, chronology,
coefficients, dirty restoration word, owners or complete consumer is supplied
for the surviving profile. Unknown additional costs are not zero.

## Reproduce and validation limits

Python 3.12 or later, standard library only:

```sh
python3.12 scripts/research_package.py --package research/p104-endpoint-support-capacity
```

Direct checks, including optimized execution:

```sh
python3 -I -O -Werror -B research/p104-endpoint-support-capacity/verify.py
python3 -I -O -Werror -B research/p104-endpoint-support-capacity/independent.py
python3 -I -O -Werror -B research/p104-endpoint-support-capacity/test_verify.py
```

The first command ends with
`PASS_P104_ENDPOINT_SUPPORT required=4656 capacity=30 rejected=406 control=400`.
`--emit` prints a recomputed receipt; normal replay checks RESULT.json and
writes nothing. The tests cover normal/optimized CLIs, all boundary weight
cases, a read-only Git-free export, source corruption before code execution,
a typed receipt fault, the weaker affine-only bound and a phantom endpoint
visit. Deliberately replacing the geometric cap by the old affine bound fails.

Local validation passed on Linux x86_64 / CPython 3.12.15: the registered
three-command replay, five behavioral test groups, Ruff 0.17.1, warning-as-error
source compilation and the selected-result binding check. Direct CPython
3.13.5 optimized primary and independent replays also passed. These checks
were rerun after fast-forwarding the publication branch to canonical main
`a1bfbc677fdcbc2a27a9b3bf6c78cac8fd6da9e2`. The scientific pins, priority
revision, selected record and PR2889 head were unchanged. Final overlap at
08:29 to 08:30 UTC covered 488 open PRs, 2,103 closed PR bodies and 1,558
Discussion records with complete pagination. It found the credited PR2889
handoff; arbitrary code diffs and unpublished work remain outside coverage.

Native phases, full corrected-word execution, rounding, physical hosting,
movement, supplier admission, all-size lifting, the selected cold replay and
the outer multiplication theorem are not checked. No independent human,
formal-kernel or hosted-CI review is claimed.

Engineering limits: Python allocates managed objects during these bounded
finite computations. Frames have at most 512 members, paths at most ten
frames, residual sets at most 48 labels, input JSON files at most 2 MB, and
there are exactly 104 endpoints per orientation and 256 histories. The one
`exec` is limited to the exact SHA256-authenticated, self-contained ceiling
source bytes to avoid source-adjacent bytecode caches. Its narrow static
warning suppression does not apply to untrusted input or any other module.
A static import can replace it if the inherited cost module gains a stable
cache-independent import contract. All changed functions are under 60 lines.

## Open next questions

Does a profile surviving the new rows admit simultaneous endpoint assignments
and chronological reads? Pin the 253/147 profile above as a first finite test,
using the endpoint-specific capacities in RESULT.json rather than the relaxed
uniform maximum. This matters because the seven units of support slack leave
little room for assigning the 24/28/29-capacity endpoints. Interior sharing,
coefficient compatibility and a complete paid consumer remain blockers.

Family decision: stop after this necessary-condition audit. A favorable
surviving screen does not justify a construction campaign or supplier
admission. Reopen only for a named geometric/chronological constraint or a
fully stated changed producer/consumer boundary with its complete cost ledger.

## Credit and task scope

Nick Petalas. Apache-2.0. Task `p104-side-correction`, refined to the explicit
PR2889 endpoint-assignment handoff. The single chooser nonce is
`e5cc9f5989ecea2fa6060e7b440c4314`; scientific base is canonical main
`2b4c46fbb19b2df3685b751965877fa7c7fa34af`, priority revision 5.
[The canonical claim][claim] records coordination and freshness.

Credit Hiroki Kumazaki for PR2889's endpoint-span audit and PR2353's monotone
model; ywz65 for PR2614's later-read-aware source departures; Arham Tahir for
PR2675/2682's coupled screens; Sagar Thakrar for the newer mixer handoff at
`743640530229e1821ae11dc104798871272d6f00`; Philippe Van Velzen for the relay
construction and window bill; Nick Petalas/PR2640/2604 for crossing capacities
and the legal cheap carrier; and Douglas Colkitt for the inherited ceiling
engine. None of those earlier facts or methods is claimed as new here.

Retain the Rohan Arun/PR1972, Chafik Boukhalfa/PR1991, Adam Gall/PR1940,
Josie Elliston/PR1071, Ali Romman/PR1125 and geometry/native/compiler lineage.
No predecessor source is copied or modified. Exact inspected predecessor
heads and the remaining obligations are recorded in TASK.json.

[2889]: https://github.com/CrocSwap/integer-mult-bounds/pull/2889
[claim]: https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18967463
