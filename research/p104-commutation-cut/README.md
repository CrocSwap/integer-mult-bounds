# The P104 eight-array cut survives arbitrary interleaving of its frame paths

Reordering the PR1972/PR1991 P104 channel and redesigning all its scalar
operations cannot make its side correction free while its per-register frame
paths and private lifetimes are retained. Even with arbitrary common-frame linear
operations, the source-to-target transfer has rank at most **8d**, where d is
the dimension of one array. The 104-port identity requires **104d**. The
original `G/2` channel attains the bound.

The new quantifier is **every interleaving of the per-register transport chains**,
with **all original scalar reads/writes discarded and freely redesigned**, rather
than one chronological event list. This
closes a restricted version of the retiming question left open by
[PR2082](https://github.com/CrocSwap/integer-mult-bounds/pull/2082) and
[PR2090](https://github.com/CrocSwap/integer-mult-bounds/pull/2090). Changing a
register's frame path, replacing/fusing transports,
new storage lifetimes and non-common-chart operations remain outside the result.
There is **no new supplier or kappa**.

## Exact domain

Start with the pinned 4,058-event word, its 104 X sources, 104 Y targets,
72 arbitrary dirty helpers and eight owned C lifetimes. The input witness is
SHA256 `0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e`.

Delete all 2,624 original ADDs and eight COPY instructions, including all
their cross-register ordering dependencies. Only the 1,410 transports and
eight private allocation/disposal pairs remain. Retain their order separately
for each register, including the order of C's eight lifetimes. Admit every
interleaving of these chains as whole transport events. No access inside a
recursive child is granted. Between events, grant any finite linear program
on existing live registers in exactly the same canonical frame, including
singular operations if desired. Original scalar coefficients, source choices
and access order need not be retained. Requiring restoration of borrowed
inputs only restricts this favorable class further.

Retain the original frame transports and C allocation/disposal lifetimes.
Each role ends at its original frame. We do not grant arbitrary storage at
unoccupied frames or identify frames merely because they have equal rank.
The theorem concerns linear maps, not adaptive or nonlinear programs.

## A union graph for all retimings

A wire node is one register's interval between successive retained transport
or lifetime events, labelled by its canonical frame. Separate C lifetimes
have separate nodes. Each transport supplies a directed wire edge from its
input interval to its output interval; initialization has no predecessor and
disposal has no successor.

For every pair of intervals on different registers with exactly equal frames,
add both directed communication edges. After the original scalar dependencies
are discarded, different registers' transport chains are independent, so each
such pair can overlap in some interleaving. More importantly, every actual
common-frame operation in every admitted execution is represented by an edge.

The graph deliberately permits incompatible choices from different schedules
and even cycles. We do **not** claim that all its edges can occur together.
Every actual data dependency maps to a walk in this enlarged graph. Extra
operations may repeatedly change a row inside one interval without changing
its frame, and are therefore still covered. Same-role intervals are connected
only by their directed transport chains, not by free access to past values.

The implementation also computes interval overlap from the event partial
order, and checks that granting *every* cross-register equal-frame pair gives
exactly the same graph. This prevents accidentally retaining an original
scalar-order restriction.

Delete the eight C-descending transport edges at original zero-based event
indices

```
2463, 2472, 2479, 2487, 2495, 2503, 2510, 2518.
```

Each is one rank-seven native descent, and each carries **one array**. Native
child rank seven is not seven independent array wires. Exact reachability
in the enlarged graph finds no X-input to Y-output path.

## Rank implication and attainment

Fix any admitted retiming and inserted linear program. Replace the values
at those eight transport outputs by eight independent array variables. In
the resulting broken program, no X input influences a Y output except via
these variables: otherwise its actual dependency path would appear in the
union graph after the same eight edges were removed.

With all other independent inputs set to zero, the original X-to-Y map
therefore factors through the eight original edge values. These values may
depend on previous such values; evaluating them in their actual chronological
order still gives a linear map from X into an 8d-dimensional space. The
transfer rank is at most 8d. Arbitrary dirty inputs and scalar/address mixing
within frames do not increase this dimension.

For sharpness, the original word is an admitted ordering. The checker
reconstructs its 280-input rational map and verifies all source and helper
endpoints, including query compensation and cleanup. Its transfer is `G/2`.
The independently reconstructed roots satisfy `G²=26G` and `trace(G)=208`.
Thus `G/26` is an idempotent of trace eight over Q, so G has rank eight; the
array-valued transfer has rank 8d. This replays the inherited scalar channel,
not a new native compilation.

## Evidence and reproduction

Two separately implemented exact graph checkers agree:

* 1,698 wire intervals in 444 binary subspaces;
* 1,402 retained transport edges after removing the eight descents;
* 71,224 directed potential common-frame edges;
* 853 reachable intervals and zero reachable final targets;
* restoring any one omitted descent reaches 52 targets; restoring all reaches 104.

The primary implementation uses forward ancestor bitsets and complete XOR
spans. The second builds per-role traces, reverse descendant sets and reduced
binary bases; it imports no primary graph code. Both were written with Codex
assistance, so this is not independent human review.

A deterministic legal retiming moves 3,989 event positions. The full rational
280-input endpoint replay and independent union-graph invariants still pass.
Controls restore each omitted edge, inject a forbidden cross-frame bypass,
remove dirty compensation or cleanup, and reverse frame-basis presentation.
The complete regenerated receipt is compared with `RESULT.json`.

```sh
python3 -I -O -B research/p104-commutation-cut/verify.py
python3 scripts/research_package.py --package research/p104-commutation-cut --check-only
python3.12 scripts/research_package.py --package research/p104-commutation-cut
```

The direct check is read-only, standard-library only, and needs no network,
Git or predecessor executable imports. `--write` deliberately regenerates
only this package's receipt. Source pins authenticate before calculation.
The unchanged local profile has mass 2368: 2312 persistent boundary progress
plus COPY56. No new correction tariff, global owner assignment, precision,
all-size theorem, selected cold replay or native phase recompilation is
claimed. In particular, the 96 missing array directions are **not** a
96-child lower bound for changed frame paths.

## Relation to current work

PR2082 (`60f4e337ffba470e09727dd435b1f1be3b67d03d`) and PR2090
(`dff116efc2c4ddd7236020ad8316db5c98aa693e`) establish the sharp rank-eight cut
for the frozen chronological itinerary. Their graph/cut idea and distinction
between array dimension and child rank are retained here. The new result is
the union over arbitrary interleavings of the fixed frame paths, after
discarding all scalar-event dependencies, and its exact certificate. Their terminal-excursion budget arguments are not new claims
of this package. PR2083 treats the completed terminal cut; PR2089 constructs
a paid tail correction. Both change the transport list and are outside this
theorem.

The investigation began as an attempted constructive retiming, after local
log-reuse and additive-access screens failed. Those exploratory finite-field
searches are not used to prove this result and are not presented as native
lower bounds. The public package contains the exact successful certificate,
not a claim of a successful identity construction.

## Open next questions

Change at least one actual frame path, storage lifetime or permitted
cross-chart interface. A concrete first experiment is
to replace one gather or delivery transport so that a source-bearing helper
can meet a target-bearing helper at a new intermediate frame. Rebuild the
union graph and require a bypass of this eight-edge cut, then verify dirty
restoration and a complete native invoice. A bypass alone is not identity
completion. Retiming or scalar resynthesis along the original per-role frame paths is
no longer the open case identified here.

## Credit

Rohan Arun / PR1972 (`fd82d172f46933fd253c2c6de4bd5eaff5429cfd`) supplies the
scalar/frame channel; Chafik Boukhalfa / PR1991
(`6e222517e182e98499239bc9a4009f540e1c5520`) supplies its native realization;
Adam Gall / PR1940 supplies the 32-chain schedule. Retain Josie Elliston /
PR1071, Ali Romman / PR1125, and the PR968/717/446/595/620 geometry and decoder
lineage. David Arias / PR2082 and Adam Gall / PR2090 supply the immediate
frozen-itinerary obstructions. No predecessor source is modified or copied.

New work by Jeremy Diviney with substantial OpenAI Codex assistance in
mathematics, code, verification and prose. Apache-2.0. No formal-kernel proof,
independent human review or exhaustive novelty guarantee is claimed.
