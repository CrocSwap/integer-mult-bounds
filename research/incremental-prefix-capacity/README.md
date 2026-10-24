# Incremental matching capacity in the word census

This package answers the first open question in PR #5033. It replaces the
cube and prefix scans in its opt-in capacity predicate with exact per-depth
counts. The completion inequality, simple-path gate, search order, counters,
report format and defaults are unchanged. The new C source preserves all
predecessor notices. DELTA.diff gives the full source change.

On the complete no-budget n=6, L=14, split (7,7) root shard, seven serialized
alternating runs gave medians 200.42 ms for the pinned enabled predicate,
40.73 ms for the incremental enabled predicate, and 20.68 ms for the new
engine with capacity disabled. The enabled implementation is 4.92 times
faster in this measurement, but still 1.97 times the disabled runtime.
Thus the capacity option remains off by default. TIMINGS.json gives all
samples, compiler, host and reports. These local timings are not CI limits.

Both enabled variants visit exactly 495,919 nodes, find 89,782 restored
leaves, and make 2,922 capacity prunes. Capacity off visits 506,239 nodes
with the same restored leaves. There are no universal hits in this domain.
These results do not establish a seven-label speedup or a new exclusion.
The complete kappa calculation and selected 60403/20000000 are unchanged.

## Exact state invariant

Fix omitted coordinate v. Let f be the functional with coefficient zero
at v and one elsewhere. Each class has 2^(n-1) vertices and 2^(n-2) disjoint
v-matching edges, for n>=2. At prefix depth d, store for each class j:

- a_j: distinct visited vertices;
- e_j: used path edges in coordinate v;
- b_j: matching edges with both endpoints visited.

The caller gate requires a simple path. On insertion of new vertex z,
increment a_f(z). Increment e_f(z) exactly when the new edge uses v.
Increment b_f(z) exactly when z xor 2^v was already visited. Each matching
edge is counted once, on insertion of its second endpoint. The initial
state has a_0=1 and every other count zero. This proves the invariant by
induction for each prefix.

There are a_j-b_j touched matching edges: a matching edge with two visited
endpoints contributes two to a_j and one to b_j. Thus

```text
unused vertices in class j = 2^(n-1) - a_j
fully unused matching pairs = 2^(n-2) - a_j + b_j
crossing path edges = d - e_0 - e_1.
```

The cheap one-vertex matching edges are exactly the unused mates of the
two path endpoints. Two membership tests count them. Distinct endpoints
have distinct mates. An internal vertex cannot take a new edge in a simple
completion. These quantities equal the pinned source's scan results, so
the unchanged even-interval test returns exactly the same split set.
When no new vertices remain, the original closing-edge check still applies.

State is stored by depth. A child copies its parent then updates the three
counts for every omitted coordinate. After return, the parent's row remains
unchanged. A sibling overwrites the child's row. Each new shard clears the
array and sets the initial vertex. Closing edges do not add a vertex and
reach the leaf before a capacity query. The repeat-capable caller bypasses
capacity exactly as before; its arrays are not updated or consumed.

The new state costs 6*n*L C integers, at most 3,696 bytes with the tested
four-byte int and the admitted n<=7, L<=22. Each insertion costs O(n).
Each predicate query keeps the original O(n*L) split loop and removes the
O(n*(L+2^n)) reconstruction scans. This is an implementation of PR #5001's
condition, not a stronger pruning theorem.

## Evidence and reproduction

Use CPython 3.12, the standard library and a C11 compiler that supports
unsigned __int128 and the listed undefined-behavior/bounds sanitizers.
From the repository root:

```sh
python3 -I -W error -B research/incremental-prefix-capacity/verify.py
python3 -I -O -W error -B research/incremental-prefix-capacity/verify.py
python3 -B scripts/research_package.py --package research/incremental-prefix-capacity
python3 -I -B research/incremental-prefix-capacity/verify.py --timings
```

The direct marker is `PASS_INCREMENTAL_PREFIX_CAPACITY`. Normal replay
checks the complete deterministic RESULT.json. The timing command prints
new local measurements and does not update the stored receipt. Each native
process has a fifteen-second limit and fresh output files.

The verifier compares full restored and universal leaf Counters, every
non-timing report field and exact node counts in twenty configurations:
(2,4), (3,6), (4,8), (4,10), (5,12), with capacity on/off and budgets on/off.
Separate checks cover repeat-capable bypass, two disjoint shards and a
17-node cap. A temporary leaf observer is inserted at the actual source
leaf boundary; it does not add a production test hook.

The independent PR #5001 split function checks every one of 1,988
prefix/functional cases at (4,10), with both ordinary and sanitizer builds.
Four actual source mutations fail: missing occupied-pair count, wrong mate,
lost parent state and lost final endpoint. The complete source delta and
all declared input hashes are checked before and after execution.

This equivalence work does not independently prove the predecessor census
traversal or its matching-capacity theorem. Those remain explicit premises.
The new count invariant is proved above. No full seven-label run, selected
cold replay, Lean, Docker, formal-kernel or independent human review is
claimed. Wall time on another compiler or host can differ.

## Open next questions

- Measure a named production simple-split shard under an explicit node and
  time budget. Compare enabled and disabled total time before any default
  change; fewer nodes alone do not justify enablement.
- Derive a repeat-aware completion theorem before expanding the current
  simple-path gate. This implementation supplies no such theorem.

## Sources and credit

SOURCES.json pins every consumed file at canonical main
ff3cc58e370d0f678e529246f8c73e8094e18fcf. The source engine and its notices
are retained from JoyboyBrian's PR #5033 integration. The mathematical
predicate is Ali Romman's PR #5001 result. Credit Nick Petalas's matching
balance and union census, Nicholas Stone's parity correction, Mihir
Srivastava's handoff, Ross Richardson's prefix model, Aaron Wang/opencode,
and the retained contributor notices. Ali Romman prepared this incremental
implementation with substantial OpenAI Codex assistance. Apache-2.0.
