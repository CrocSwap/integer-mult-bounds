# Independent receiver-window floor and peer-certificate comparison

This package independently corroborates the concurrent all-length results in
[#4581](https://github.com/CrocSwap/integer-mult-bounds/pull/4581) and
[#4582](https://github.com/CrocSwap/integer-mult-bounds/pull/4582), and supplies
an executable comparison of their pinned receipts. All three implementations
agree on every window boundary, incumbent bill and terminal rank partition.
The contribution adds a separate three-ancestry model and exhaustive small
geometric inclusion controls, with no exclusive novelty or priority claim.

**Every eligible window has zero paid-cost headroom for any finite shear word
on the same three fields, with the same monotone frame boundaries.** There is
no word-length or coefficient cap. The incumbent minimizes every increasing
concave rank cost `f`, with `f(0)=0`; in particular `f(r)=r^(1-C)` for
`0 <= C < 1`. No new kappa or selected-frontier change is claimed.

This closes the length/coefficient direction left by [#4546](https://github.com/CrocSwap/integer-mult-bounds/pull/4546)
and [#4567](https://github.com/CrocSwap/integer-mult-bounds/pull/4567), within their
fixed three-field monotone contract. Those packages enumerate bounded scalar
words. This package discards scalar coefficients and the exact endpoint after
retaining necessary temporal ancestry, then exhausts a finite acyclic frame
relaxation. It is a scoped exclusion, not a general barrier to better suppliers.

## Contract and theorem

The three persistent fields are `(a,b,x)`, with arbitrary initial values. Their
entrance and exit frames `S_i <= E_i` are binary subspaces of `F_2^9`. Each
constant-coefficient shear `y_i += c*y_j` requires a common frame for its two
operands. Each field's frame only grows by inclusion. Every positive movement
of dimension `r` is charged `f(r)`, including the final movement to `E_i`.
The required endpoint is `a += ca*x; b += cb*x`, with `ca,cb` in `{+1,-1}` and
`x` restored. Replacement coefficients can be arbitrary constants; the proof
does not bound their magnitudes or charge their scalar cost.

For each of the 128 eligible adjacent pairs freshly extracted from main's
PR4470 constructor (123 phase-B and 5 cleanup-tail), every such replacement
has cost at least the incumbent's. The incumbent itself satisfies the boundary
contract, so the minimum is attained. The proof has four parts.

### 1. Temporal ancestry is necessary

Initially give field `i` the marker set `{i}`. At a contact of `i,j`, replace
both marker sets by their union. This is deliberately generous: a shear moves
information in only one direction and cancellations may remove information.
Induction on gates shows that every actual nonzero input dependency remains in
the marker set. Since both receiver outputs depend nontrivially on the original
`x`, their final marker sets must contain marker 2 (bit 4 in the checker).
Restoring `x` and cancelling unwanted dependencies are additional constraints
that the relaxation omits.

Each current frame also contains the sum of the entrance subspaces associated
with its markers. Initially this is equality. A common contact frame contains
both previous frames, so their union of markers preserves this property.
This geometric induction is valid even when a scalar coefficient cancels.

### 2. A finite graph contains every legal path

A state consists of three marker bitmasks `M_i` and three current contact
dimensions `d_i`. For contact `i,j`, put `M=M_i union M_j`. Its frame must contain
`L=sum(S_k : k in M)` and be contained in `U=E_i intersection E_j`. Reject the
transition if `L` is not contained in `U`. Otherwise permit every integer

`max(d_i,d_j,dim L) <= d <= dim U`.

Set both operand dimensions to `d`, both marker sets to `M`, and charge each
positive gap `d-d_i`, `d-d_j`. We forget incidence constraints on the unknown
current frames, so this can admit extra paths, never exclude an actual one.
Once both receivers contain the source marker, termination charges every
positive gap `dim(E_i)-d_i`.

A state-changing transition strictly increases
`sum(d_i) + sum(|M_i|)`, bounded by 36. A transition leaving the state unchanged
has zero frame cost and can be deleted: the relaxed endpoint depends only on
the markers. Thus all finite words, however long, map into this finite DAG.
The checker retains every attainable rank partition, not just a heuristic
minimum. The sum of its ranks must equal `sum(dim E_i - dim S_i)`.

Extra monotone movements between contacts are compressed into one jump. This
cannot raise cost: for an increasing concave `f` with `f(0)=0`,
`f(u+v) <= f(u)+f(v)`. To see this for integer ranks, the first `v` discrete
slopes dominate the `v` slopes starting at `u`. This also covers split terminal
movements. Consequently the relaxed cost is a lower bound on actual cost.

### 3. Integer capped-rank sums certify all concave tariffs

For each relaxed partition `p` and incumbent partition `o`, the checker proves
equal rank mass and, for every `k=1,...,9`,

`sum(min(r,k) for r in o) <= sum(min(r,k) for r in p)`.

Let `s_k=f(k)-f(k-1)`. Concavity and monotonicity give
`s_1 >= ... >= s_9 >= 0`. The exact identity

`f(r) = s_9*r + sum((s_k-s_(k+1))*min(r,k), k=1,...,8)`

proves the cost order by nonnegative linear combination. Thus the certificate
uses integers only, with no root rounding or sampled exponents. It includes
the predecessors' `C=0.00302015` and every `0 <= C < 1`.

### 4. Source-bound application and attainment

[SOURCES.json](SOURCES.json) authenticates all seven constructor inputs before
execution. The constructor supplies candidate frames and the forward program;
its acceptance engine is not invoked. The new extractor uses chronological
entrances and per-role next-use lists for exits (including warp pre-frames).
It independently checks the incumbent's actual subspace containment and ranks.

[RESULT.json](RESULT.json) records all 128 window indices, roles, signs,
canonical entrance/contact/exit bases, incumbent partitions and relaxed
partitions. In total there are **1,603 states and 239 window/partition pairs**;
the largest individual graph has 45 states. Every incumbent is admitted and
every integer comparison passes. Partition-count frequencies are
`{1:93, 2:9, 3:6, 4:2, 5:13, 7:4, 9:1}`. Different windows may overlap;
their gains or costs must not be summed as disjoint modifications.

## Verification

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/receiver-all-length-floor
```

The registered replay freshly extracts the windows and compares every receipt
field without rewriting it. Both registered Python commands use isolated mode;
the constructor child also gets a fresh bytecode cache namespace. The second
command runs semantic controls under `-O` with explicit checks/unittest:

- A separate forward traversal over actual `F_2^2` subspaces covers all 1,728
  triples of comparable entrance/exit pairs (664 have a terminal path).
  Every actual geometric partition is admitted by the dimension relaxation.
- The shape of window 10557 rejects the tempting cheaper partition `(1,2)`
  when the old bill is `(1,1,1)`. Forgetting temporal source ancestry admits
  it. Connectedness alone can contact `a,b` before `x` arrives, leaving `a`
  without the required source contribution.
- Omitting an exit payment fails rank mass; incompatible equal-dimensional
  frames and shrinking boundaries fail; zero-dimensional source propagation
  and a next-use/warp extraction fixture pass.
- All 220 decreasing nine-step slope sequences over `{0,1/3,2/3,1}` satisfy
  the exact cost expansion. A corrupted constructor input is rejected before
  execution.

The finite controls support the implementation; the all-length statement
rests on the inductions and finite-state reduction above. No formal-kernel or
independent human verification is claimed. `--write` is an authoring option,
not part of the registered replay.

Local validation on Windows with CPython 3.12.0 passed the metadata/source-pin
check, full registered replay and all six optimized controls. A one-time
development cross-check matched all 128 indices, roles, signs, complete
subspaces and incumbent bills against #4567's separately loaded extractor at
the pinned head. That comparison is corroboration, not a replay dependency.

## Executable comparison with concurrent certificates

The submission refresh found [#4572](https://github.com/CrocSwap/integer-mult-bounds/discussions/4572),
[#4577](https://github.com/CrocSwap/integer-mult-bounds/discussions/4577) and the
static-contact proof in [#4574](https://github.com/CrocSwap/integer-mult-bounds/discussions/4574).
They are concurrent investigations of the same conclusion. This package was
already implemented when discovered and is offered as independent corroboration.
It does not claim to have independently audited their proof code.

[PEERS.json](PEERS.json) pins the exact source Git blobs and SHA256 payloads for
two committed receipts, retained as unchanged gzip-compressed inputs under
`peers/`. [compare_peers.py](compare_peers.py) authenticates those bytes, expands
bases to complete binary subspaces (basis order may differ), and compares all
128 identities, phases, roles, signs, entrances, contacts, exits, incumbent
bills and 239 terminal partitions with this package's freshly verified receipt.
It executes no peer code. This is the third registered command, also runnable
directly with `python -I -O -B research/receiver-all-length-floor/compare_peers.py`.

| Certificate | Exact head | Reported states | Matched window/partition pairs |
|---|---|---:|---:|
| #4581, directed source dependence | `b154350fbf1e7d49118851ab899a733727483289` | 1,303 | 239 |
| #4582, bidirectional source dependence | `23c515a3c071a6bfdd1fe80bc67cea55f6d43643` | 1,496 | 239 |
| This package, all three entrance-ancestry masks | See this PR head | 1,603 | 239 |

State counts are representation-dependent, not an improvement measure. The
executable comparison certifies the common projected data, not equivalence of
all intermediate states or peer tests. The peer receipts are package-local
immutable inputs; the generic runner includes them in package invalidation and
export, while their external-origin Git blob checks are explicit in the
comparison code. They do not add pending source-history dependencies.

## Scope, overlap, and credit

Canonical base: `f626db5c3a3d781d8f7695038776c621651f75e1`, priority revision 7.
Coordination: [Discussion #4573](https://github.com/CrocSwap/integer-mult-bounds/discussions/4573).
The handoff-first selection and exact predecessor heads are in [TASK.json](TASK.json).
The initial overlap refresh covered 355 open PR bodies and 3,470 Discussion
records; all 5,860 tracked top-level package README/TASK notes were then
materialized and searched. The 08:08-08:09 UTC submission refresh covered 358
open PRs and 3,493 Discussion records and revealed the concurrent work above.
Canonical main and the priority revision were unchanged. Coverage is a dated
search, not proof of novelty. #4567's head `58695721e3cf9d5101440dd53a3ea5bbcc0e9313`
adds nonadjacent and contact-retiming checks outside this fixed adjacent scope.
The older R420 all-length cleanup floor and P111 receiver census concern
different targets and tariffs; neither covers these PR4470 frame contracts.

The historical baseline helper was attempted but stopped at absent source
packages in the sparse checkout. It is not reported as a pass. The selected
record, review, source manifest, claim and reproduction entry point were read;
the selected full cold replay is outside this local result. The selected record
remains `23/10000`. Native all-column correctness, physical lowering, stock,
precision, fixed tape, compiler and outer transfer are not reverified here.
There is no conclusion about extra fields, nonmonotone frames, changed
boundaries, nonadjacent windows, or simultaneous overlapping rewrites.

Credit Chris R / Clear1nsight's #4546 fixed-window relaxation; Ryanson
Jonathan's #4567 broader finite census and explanation motivating this
all-length question; Cinna Davis's #4470 construction and retiming lineage;
zxv's receiver-sharing/productive-helper work; Jacob Alan Sussman and the
retained native, Clifford, geometry and outer contributors. Predecessor code
was read during development; a local probe reused #4567's extraction for
comparison. The committed extractor, state graph and cost checker are new,
and import no #4546/#4567 acceptance code. This is a separate implementation,
not a separately launched audit team. Prepared for mihir-s-05 with substantial
OpenAI Codex assistance. Apache-2.0; retained source notices are unchanged.
Credit the concurrent #4572/#4582, #4577/#4581 and #4574 investigations as well;
the compressed peer receipts retain their exact authored payloads and origin.

## Open next questions

Further word-length or coefficient sweeps in these fixed contracts have no
headroom under the stated tariff. A useful follow-up must explicitly change
the contract: for example, one additional field with fully charged entry,
exit, restoration and consumer work. Derive that optimistic complete budget
before implementing a search. This certificate does not decide that changed
model. [TASK.json](TASK.json) records the first step and blockers.
