# Restored spectators cannot lower the mixed S4 tariff

**Written all-workspace reduction plus a replayed finite certificate; no new κ.**
The fixed target `diag([2143],[3142],[4231],[2143],1,...)` has exact paid cost
**21**, with any finite number of arbitrary restored dirty spectator registers,
in the formal binary S4 model with adjacent-label prices `(2,1,2)`.

This closes the arbitrary-workspace question of
[PR3888](https://github.com/CrocSwap/integer-mult-bounds/pull/3888), read at
`23057075f4a45fdabdb5c68a206d05306ba61ae3`. Its four- and five-role exclusions,
cut-window method, and direct cost-21 witness remain prior results. The new
result removes every higher-width search for this exact cost-20 question;
it does not enlarge that census or settle arbitrary weighted S4 targets.

[Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2570#discussioncomment-19130776).
Scientific base `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision 7.
The selected conditional κ remains `60403/20000000 = 0.00302015`; the complex
side binds. Only this new package changes.

## The new implication

[PROOF.md](PROOF.md) gives the full argument. A normalized paid factor is
`G=I+([s]+[e])uv^T`, with `v^T u=1` and s one of the three adjacent
transpositions. All dirty inputs and all off-diagonal terms are part of the
formal endpoint. Free binary scalar mixing is absorbed into the normalized
projectors by the inherited augmentation argument.

Use the ordered-pair permutation module and its positive-root half H. Its
crossing rank is the Grassmann distance `φ(P)=d(H,P^(-1)H)`, and a paid simple
factor has `d(H,GH)=1`. If a rightmost written factor can be peeled with
`φ(PG)=φ(P)-1`, the distance triangle is an equality, so

```
H ∩ P^(-1)H  ⊆  G H  ⊆  H + P^(-1)H.
```

When P is an arbitrary active block plus spectator identity, the left-hand
intersection contains every spectator positive-root direction; the right-hand
sum has no spectator negative-root direction. The explicit subspace G H
therefore forces **both** u and v to have zero spectator component. The
factor itself is supported on the active roles in the full formal algebra.
Induction removes spectators from every inversion-tight word.

For the fixed mixed target, the inherited cut values `(inv,c1,c3)=(12,4,4)`
force every cost-at-most-20 word to have counts `(4,4,4)` and exactly twelve
calls. It is inversion-tight, so the new lemma reduces it to four roles.
The complete four-role PR3888 certificate excludes it. Costs are integral,
and the inherited coordinate words cost `4+5+8+4=21`, proving exactness.

This is a **written uniform proof with an explicit finite dependency**. The
finite examples below are implementation controls for the new lemma; they
are not the reason it holds in arbitrary dimension. The four-role exclusion
is indispensable to the final 21 corollary, and is not claimed as a new
analytic or formally verified proof.

## Evidence and reproduction

The standard-library Python checker:

- independently verifies the Grassmann equality inclusions on all 42,875
  triples of two-dimensional subspaces of F2^4;
- checks every one of 20,160 invertible active 4×4 binary matrices, extended
  by one identity spectator, against all 28 rank-one projector peels:
  **564,480 cases** in the two-address, two-active-role, one-spectator
  crossing-pair abstraction, including active maps not diagonal in the address
  basis. This is not a new S4 register-width census;
- distinguishes u-side and v-side dirty coupling, a legal non-tight restored
  word, and a tight endpoint that fails spectator restoration;
- recomputes the S4 cut values, the unique cost-20 count vector, and all four
  direct coordinate words by exact weighted shortest paths;
- validates the source-bound completed independent four-role replay and rejects
  a missing engine, changed results/logs, sources, adapter, arguments and a
  false claim that the stopped primary cross-check completed.

Run from the repository root, Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/s4-tight-word-spectator-elimination
python3.12 -O -B research/s4-tight-word-spectator-elimination/verify.py
```

The registered Python replay **validates the complete C++ receipt; it does
not rerun the C++ exclusion**. To regenerate that finite dependency explicitly:

```sh
python3.12 -B research/s4-tight-word-spectator-elimination/replay_r4.py --output /absolute/new/directory
```

This source-bound command compiles and runs the unchanged independent
`indep.cpp` at four roles, all 360 first factors, without symmetry or early
stopping. It uses one OpenMP thread and a 900-second limit. The completed
cold execution took **855.189 seconds** and obtained
`56,1904,28562,207168,571536,648720,381816,0,0,0,0,0`: **1,839,762 nodes**,
zero full-depth survivors. Source, compiler, command, time and output hashes
are in `finite/REPLAY.json`; raw stdout/stderr are retained alongside it.

This independent engine alone suffices for the finite exclusion. It enumerates
all 360 normalized gates and all recursive choices with counts `(4,4,4)`.
Its natural and ordered-pair representation cut windows are necessary
conditions for a formal word. A nonfaithful representation can admit spurious
candidates, but cannot discard a genuine formal word. No state survives to
depth eight, so the absence of a full formal equality check at depth twelve
cannot affect this exclusion. See [PROOF.md](PROOF.md), section 6.

On this macOS host, GCC14 could not use the installed SDK headers. The
successful independent replay used Apple Clang21 with `-O3 -mcpu=native`,
the Xcode SDK and installed Homebrew libomp. An earlier `-O2` primary attempt
hit its 300-second cap; its timeout message is retained, but that initial
driver did not retain stdout/stderr buffers. No result is inferred from it.
After the independent run finished, a new primary cross-check was stopped
by the coordinator because it was redundant. It completed only 22 of the
56 viable first branches and is **not** counted as a successful replay.
`finite/INITIAL_ATTEMPT.json` and `finite/PRIMARY_STOP.json` retain these
boundaries, with the available raw logs and hashes.

The optional `--include-primary` flag requests that additional sequential
cross-check for a future separately budgeted run. No five-role search or
LP suite is run. `compat/bits/stdc++.h` is only a portable standard-header
list, including `unistd.h`; no predecessor gate, pruning condition, matrix
operation or acceptance code is edited. On other platforms the replay uses
`CXX` or g++ with OpenMP. macOS libomp location can be set with
`S4_LIBOMP_PREFIX`. No script installs a compiler or package. The engines
retain Sagar Thakrar's attribution and source bytes. Direct Python checks
need no Git or network with the declared inputs in an exported package.

The proof and the completed independent engine's sufficiency have separate
Codex review. AI review and distinct implementations are not independent
human or proof-kernel acceptance. No
hosted CI result is asserted by this package.

## Family decision and limits

The named changed obligation is chronological equality with unequal prices
on conjugate simple generators. The retained Coxeter tariff theorem already
settles class-dependent prices; the S4 coordinate and one-copy subspace cut
methods already stop at 20. Their bounds are retained, not rediscovered.
The new elimination lemma closes the higher-workspace branch for this exact
target without any larger census.

Stop here. The argument does not apply automatically to words with inversion
slack, non-simple paid labels, different endpoints, nonlinear gates, unreturned
spectators, or literal unnormalized presentations with interleaved free maps.
Native address realization, frames, scalar charges, routing, hosting, precision,
physical tape and recursive supplier admission remain unknown here, not zero.
No selected construction, complete multiplication theorem or κ changes.
No Lean, Docker, five-role replay or full historical suite was run.

## Open next questions

- **Which changed endpoint or tariff forces inversion slack in every cheapest
  candidate?** That would leave the exact hypothesis used by this elimination
  lemma. First exhibit and price a concrete formal endpoint before starting
  a new word search. The present theorem closes the fixed mixed tuple for
  all finite workspace sizes, so adding spectators is not a reopening reason.
- **Can the remaining active four-role obstruction be proved without a finite
  search?** The current universal corollary explicitly retains that finite
  dependency. A new chronological invariant would replace it; another
  partial replay or a larger register census would not.

## Sources, overlap and credit

`SOURCES.json` pins the exact predecessor code, finite receipt, proof and
orientation documents at the refreshed base; no frozen source is modified.
Live PR3888 and PR2998 heads matched their retained sources before claiming.
The scoped search covered 506 open PRs at 18:49:46 UTC, 3,650 Discussion
records at 18:50:37 UTC and 5,860 local notes on 2026-10-22. No later resolution
of the all-workspace question was identified in that coverage. Closed PR
diffs, arbitrary nested code and unpublished work remain outside it; this is
not a guarantee of novelty.

Credit Sagar Thakrar/#3888 for the cut-window finite exclusion and direct
witness; Arham Tahir/#2998 for the cut-envelope gap and equality handoff;
Nick Petalas/#2583/#3408 for the weighted model and subspace-cut boundary;
Ross Richardson/#1966/#1989 and the permutation-cut work; Adam Gall/#1941;
David Arias/#2738; and the retained register-model lineage. The elementary
Grassmann distance inequality is standard; the application to eliminate
spectators from these tight words is the new proof step.

Prepared for **JoyboyBrian**, with substantial **OpenAI Codex** assistance in
proof, implementation, reproduction and separate agent review. Apache-2.0.
