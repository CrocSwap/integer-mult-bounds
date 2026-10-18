# P104 joint endpoint obstruction for the 423-lifetime profile

The named profile in [PR2941][2941], **232 cheap lifetimes, 180 unit-step
lifetimes and 11 lifetimes skipping dimension three**, cannot realize the
frozen X-only monotone correction. The two endpoint systems must use the same
cheap source-to-target flags. A finite necessary-condition certificate then
requires at least 235 distinct flags under the assumed 232-flag budget.

This rejects that profile even though PR2941 reports a passing optimistic
moment and passing separate endpoint screens. It does not correct an error in
PR2941, which explicitly leaves joint realization open. It supplies no new
universal lifetime threshold, feasible correction, supplier or kappa. The
selected result and predecessor packages are unchanged.

## Model and exact question

Use the original 4,058-event P104 `G/2` channel retained by PR1991. The added
correction must implement `I-G/2` on independent immutable X inputs, with
write-only targets Y. Original data-frame paths are fixed. New helpers start
at ZERO with source-independent arbitrary dirty values, move only through
increasing binary subspaces, end at FULL and restore their logical dirt.
Reinitialization starts another lifetime. Same-frame linear operations,
relays, cancellation and singular mixing are allowed. Reading Y or original
helper/private fields, writing X, descending, or source-dependent initial
state is outside this model.

A cheap lifetime has dimension jumps `(1,7,1)`. The other 191 lifetimes have
jumps `(1,1,1,1,1,1,1,1,1)` or `(1,1,2,1,1,1,1,1)`. Call these broad lifetimes.
The proof generously gives every broad endpoint contact its maximum proper
subspace capacity; it does not use the missing dimension-three contact.
Thus replacing that history by a unit-step history does not evade this test
at the same cheap/broad counts.

Scientific base main is `05eee6613f843dd754528c9b2da8049757382ef6`, priority
revision 5. The named pending predecessor is PR2941 at
`df29f70185979e32c73efc5f6e2903652d744ae7`; its price is not recomputed here.
[The canonical claim][claim] records live coordination. [SOURCES.json](SOURCES.json)
pins the original JSON inputs and the reused geometry implementation. No
pending construction is promoted to a reviewed supplier.

## From programs to one shared edge set

Retain the residual sets of PR2896/2909/2920. For target t, `N_t` contains
required source labels absent from every earlier proper Y frame, after
forgiving all direct X-to-final-Y contacts. For source s, `F_s` contains
required target normals for which no later proper X frame lies in that target
hyperplane. The executable reconstructs these sets from the original word,
not a stored endpoint table. Each orientation has 4,656 demands.

The inherited source-support invariant says that a helper's X coefficient
row is supported on labels in its current binary frame. A cheap lifetime
therefore carries at most one designated X source before its direct
line-to-hyperplane transport. After entering a dimension-eight hyperplane,
its only larger frame is FULL. It can reach at most one designated target
hyperplane. Record this source/target pair when both exist. Let E be the set
of distinct such pairs of all cheap lifetimes. Then `|E| <= 232`.

The same E bounds both endpoint systems. A residual arrival that uses a
cheap entrance must use its recorded source and target. A residual departure
that first leaves its source on a cheap lifetime reaches that lifetime's
hyperplane, and cannot subsequently reach a different target hyperplane
without descending. Mixing at a target hyperplane can move broad information
through a cheap helper, but that information is still accounted for at its
broad entrance. Expanding the chronological linear dependency graph handles
relays and cancellation without creating another cheap flag.

At an endpoint let d be its residual demand, b the maximum intersection with
a proper subspace, and u the number of broad contacts. The cheap flags must
cover at least `max(0,d-b*u)` distinct residual demands. The source-side
statement uses the annihilator of the first broad departure. A nested
lifetime has at most one designated source line and one designated target
hyperplane, so the broad counts sum to at most 191 in each orientation.

All endpoints have `b < d <= 2b`. Truncate u at two and, if needed, add
fictitious broad contacts until the sum is 191. This only weakens the
requirements. There are then exactly 17 missing contacts relative to two
per endpoint. This padding is separate in the two orientations and grants
more freedom than a joint physical program.

Choose subsets `E_A, E_D` of E containing exactly the required number of
arrival and departure flags at each endpoint. Their intersection lies in the
mutual residual graph, whose edges satisfy both `s in N_t` and `t in F_s`.
If the total required subset sizes are `L_A,L_D` and their overlap is at most U,

```text
|E| >= |E_A union E_D| >= L_A + L_D - U.
```

This is the new joint condition. Independent endpoint budgets do not impose it.

## Small integer certificate

Classify positive-deficiency endpoints, those with u less than two, as follows.
Each orientation has 12 available P endpoints, 8 Q endpoints and 84 R endpoints.

```text
P: (d,b) = (36,24), first missing-contact price 12
Q: (d,b) = (45,30), first missing-contact price 15
R: d-b >= 16
Every second missing contact costs at least another 24.
```

The reconstructed mutual graph has 4,368 edges. Its only facts needed below are:

- Between the two P classes, every vertex has degree at most four.
- A Q vertex has at most six neighbors in the opposite P class.
- There are no Q-to-Q edges.

Let p,q,r count selected endpoints in those classes, and z count selected
endpoints with u zero. Then `p+q+r+z=17`, and

```text
L >= ell(p,q,r,z) = 12p + 15q + 16r + 24z.
```

A solution with at most 232 cheap flags needs `ell <= 232` in each orientation.
Enumerate `0<=z<=8`, `0<=p<=12`, `0<=q<=8`, set `r=17-z-p-q`, and retain
`0<=r<=84`, `z<=p+q+r`, `ell<=232`. Exactly 34 relaxed states survive.
The relaxation permits unrealizable placements of the second deficiency,
which favors the proposed program.

For source state `(p,q,r,z)` and target state `(a,b,c,w)`, write
`k=p+q+r`, `h=a+b+c`. Allow every possible edge touching R. The mutual-edge
upper bound is

```text
U = k*c + h*r - r*c + 4*min(p,a) + 6*(q+b).
```

All 1,156 state pairs satisfy `ell_source + ell_target - U >= 235`.
The minimum occurs at `(p,q,r,z)=(10,0,7,0)` on both sides, with lower costs
232 each and overlap allowance 229. Consequently `|E| >= 235 > 232`, a
contradiction. [RESULT.json](RESULT.json) retains every state and the full
geometric census.

**The 235 is conditional on the assumed 232 budget.** It is a contradiction
certificate, not the optimum cheap count when a larger budget is allowed.
The independently implemented six-type check retains the exact endpoint
prices and block degree maxima. Its 337 squared state pairs give the stronger
conditional bound 300 under the same budget. The smaller proof above suffices.
Neither computation optimizes actual correction circuits.

## Reproduce and evidence

Python 3.12 or later, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-joint-endpoint-obstruction
```

Direct read-only checks also work in a Git-free source export:

```sh
python3.12 -I -O -Werror -B research/p104-joint-endpoint-obstruction/verify.py
python3.12 -I -O -Werror -B research/p104-joint-endpoint-obstruction/independent.py
python3.12 -I -O -Werror -B research/p104-joint-endpoint-obstruction/test_verify.py
```

The primary marker is
`PASS_P104_JOINT_ENDPOINT cheap=232 broad=191 bound=235 states=34 pairs=1156`.
`verify.py --emit` recomputes the complete receipt without writing files.
The primary checker reuses the authenticated PR2909 geometry module. Its
loader compiles those authenticated bytes directly, so a preexisting bytecode
cache cannot replace that module. The independent checker imports no
predecessor implementation and computes capacities using integer character
transforms instead of direct functional intersections.

The tests exercise the actual CLI, Git-free read-only replay, false P-P and
Q-Q graph premises, a weakened degree bound that no longer excludes the
profile, a false class gap, input corruption before code execution, poisoned
bytecode, duplicate keys and typed receipt corruption. An exploratory CP-SAT
run returned UNKNOWN after 45 seconds; no solver status or solver dependency
is used as evidence. The two finite implementations and a separate internal
mathematical review support the result. The program-to-edge implication is a
written proof, not a formal-kernel theorem or independent human review.

Native identities, precision, full-word execution, physical routing/hosting,
complete consumer costs, all-size lifting and the selected cold replay are
unrun. They are unnecessary for this exclusion within the stated model, and
remain obligations for a changed candidate. Local commands and environments
are recorded in [TASK.json](TASK.json). Hosted CI is separate.

## Open next questions

A changed candidate must pass a **joint** endpoint flag test before further
scalar or native implementation. One feasible next test is to name a different
cheap/broad histogram and check actual residual-edge subsets in both
orientations, retaining the same flags, or to change a stated source/consumer
contract. This result does not supply a new optimum or authorize treating
unknown acquisition, coefficient, restoration and physical costs as zero.

Family decision: finish this named-profile obstruction and stop. No additional
threshold search or construction expansion is included. The structured next
question in TASK.json preserves that boundary.

## Credit and engineering notes

Nick Petalas. Apache-2.0. Substantial automated assistance was used in the
mathematics, code, independent implementation, review and writing. No independent
human review is claimed.

Credit Nick Petalas/PR2941 for the named three-history profile and handoff,
Sudarsh Chaturvedi/PR2924 for the two-history floor screen, Nick Petalas/PR2920,
PR2909 and PR2896 for separate covers, endpoint prices and residual capacities,
Hiroki Kumazaki/PR2889 and PR2353 for endpoint spans and the monotone model,
Arham Tahir/PR2675 and PR2682 for the coupled price model, ywz65/PR2614 for
later-read-aware departures, Sagar Thakrar's mixer handoff and Philippe Van
Velzen's relay work. Retain Rohan Arun/PR1972, Chafik Boukhalfa/PR1991,
Adam Gall/PR1940, Josie Elliston/PR1071, Ali Romman/PR1125 and their retained
geometry/native/compiler lineage. No predecessor construction or earlier
one-sided bound is claimed as new.

Build the Lever led to the replayable integer certificate. Prove It Works
required original-input reconstruction and a separate implementation. Test
Behavior, Not Implementation led to CLI and semantic fault tests. Unslop guided
the prose. The finite domains are 104 endpoints per orientation, 512 labels,
4,058 source events, 34 squared primary pairs and 337 squared independent pairs.
All changed functions are below 60 lines. Explicit checks remain enabled under
optimized Python.

Power of Ten rule 3 deviation: these bounded Python computations allocate
managed objects. Source files are capped at 2 MB, spans at 512 members, and
the independent staged state list at one million entries. A resident or
untrusted general-purpose checker would need a fixed-capacity implementation.
Rule 8/9 deviation: the primary loader uses Python module dispatch for one
SHA256-authenticated geometry source. Its code path bypasses bytecode-cache
reads, with a valid poisoned-cache control. The test runner has one explicit
module import and bounded subprocesses with 30-second timeouts and scoped
temporary cleanup. A standalone static geometry API with source binding could
remove that loader in a separate change. Registered warnings-as-errors, lint
and source compilation cover the changed code. Shared repository configuration
and frozen sources are unchanged.

[2941]: https://github.com/CrocSwap/integer-mult-bounds/blob/df29f70185979e32c73efc5f6e2903652d744ae7/research/p104-three-history-threshold/README.md
[claim]: https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18975014
