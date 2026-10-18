# Exact target unions for the historical disjoint-tensor audit

This opt-in adapter replaces repeated reachable-target enumeration with exact
union propagation in `DisjointTensor.frame_data`. At h=26 it preserves all three
maps on **60,372 active nodes**, including **9,206,600 reachable-target
memberships**, and reproduces the **entire original historical certificate byte
for byte**. The complete audit still checks integer coefficients, reversible
embedding, both physical frame orientations, exact small residual bases,
operation invoices, rational inequalities, guard slack and its original finite
parameter screens.

This is verification tooling: no new construction, kappa, search result, or
multiplication runtime claim. The selected conditional result at the pinned base
is PR942's **0.001661960547713947**. Historical bound strings in the reproduced
certificate describe an earlier supplier.

Five sequential alternating fresh-process pairs on macOS arm64 / Python 3.14.4
measured median complete-audit wall time **5.014369 s → 3.492928 s (1.435577×)**.
Every one of the ten runs reproduced the same full certificate. The measurement
includes source admission, construction, scalar/frame checks, accounting and
receipt comparison. BENCHMARK.json retains all samples, environment and code
hashes. Timings describe this historical audit, not the selected frontier replay;
there is no performance pass threshold. No other task-local tests or benchmarks
were running during the measurement.

## Reproduce

Python 3.11+ and the standard library suffice. From the repository root:

```sh
python3 -I -B research/disjoint-frame-unions/verify.py
```

Expected status: `PASS_DISJOINT_FRAME_UNIONS`, with
`scope: complete_historical_audit` and receipt SHA256
`3f2b37542f9581f9d3238cccfce19fd3e2964c89ec4af4ff047fb8041f5c3cd1`.
This compares the complete original certificate, including every source hash,
against the committed fixture; no fields are removed or normalized away.

Additional reproducible checks:

```sh
python3 -I -B research/disjoint-frame-unions/test_unions.py
python3 -I -O -B research/disjoint-frame-unions/test_unions.py
python3 -I -B research/disjoint-frame-unions/test_replay.py
python3 -I -B research/disjoint-frame-unions/verify.py --engine baseline
python3 -I -B research/disjoint-frame-unions/benchmark.py --pairs 5 --output /tmp/disjoint-frame-unions.json
```

Use a new benchmark output path. Full inherited audit replay rejects `-O` to
preserve inherited assertions. The new graph kernel and its independent tests
also pass with assertions disabled; this is a distinct, narrower claim.

## Equivalence argument

For a node v let D(v) be its set of reachable output indices. If output i has
ground-coordinate mask T_i, the old loop computes

```
U(v) = OR_{i in D(v)} T_i.
```

Define F(A) as the OR of T_i over indices in A. Then F(empty)=0 and
F(A union B)=F(A) OR F(B). The original reverse topological pass initializes
D at output nodes, then unions each child's D into each parent. The adapter
initializes U at those same output nodes and propagates it alongside D.
Induction in the identical reverse topological order gives U(v)=F(D(v)) at
every node. Multiple outputs on one node and multiple paths to one output are
handled by OR's idempotence. Target masks are actual output keys, not the
positions of those keys in the sorted output list.

The reachable-target bitsets are retained in full: later `bit_count` calls
still see exactly the same D. Source unions and the nonempty/disjoint rectangle
checks are unchanged. All three dictionaries preserve the original insertion
order. The adapter assumes exactly the original graph contract: active nodes
are closed under parents and topologically numbered. It is not a new DAG
validator; the original full audit's acyclicity, support, coefficient and
embedding checks remain in place.

The old loop performs one target-mask lookup for every reachable-target
membership (9,206,600 at h26). The replacement does one ground-mask OR per
active parent edge. Python integers are unbounded; no hash, floating estimate,
truncated bitmap or probabilistic acceptance is substituted for the exact sets.
The full descendant bitset propagation and all later frame checks remain.

This is a written equivalence argument plus finite independent controls, not a
formal proof of the full multiplication theorem.

## Coverage and failures

`test_unions.py` contains eight tests, including five original historical tests
run under a scoped adapter installation. It compares ordered contents of all
three maps at h26, both full physical orientations, and exact small residual
bases. A separately implemented breadth-first graph oracle checks 88 seeded
arbitrary DAGs plus explicit small controls. Cases include aliased outputs,
multiple-coordinate target masks, output insertion permutations, repeated
children, an empty graph, and a 300-input graph with gaps in its active set.
The BFS oracle is intentionally confined to small graphs; the h26 comparison
uses the unmodified original implementation over every map entry.

Four graph corruptions must retain the original explicit failure: source/target
overlap, zero target union, an active node without an output path, and an alias
that introduces overlap. The historical tests additionally cover corrupted
coefficients/supports and all independent dirty inputs under both signed
invocation directions.

`test_replay.py` checks altered/missing source files, changed adapter bytes,
changed or incomplete result fields, restoration after an audit exception,
rejection of optimized full replay, and preservation of an existing output.
The finite test domain and seed are fixed; no search or impossibility claim is
made. The stopping rule is those tests plus five alternating benchmark pairs.

## Pins and scope

Exact base: `2921874911956718fcaaaf9396fe8267b3cfa9f0`.
`SOURCES.json` binds 40 inherited files, including the original construction,
all imported audit modules, fixture, tests, proof references and upstream files.
Each inherited file hash was compared to its Git blob at that base. It also
binds the new executable adapter, replay, tests and benchmark. Source admission
precedes repository imports; unexpected imported repository scripts are rejected.

The wrapper temporarily changes only `DisjointTensor.frame_data` and restores
it even if the audit fails. No original source, certificate, source manifest,
`upstream/` file or selected record is edited. This avoids invalidating existing
consumers' immutable source pins, including the related PR950 package. Running
the default repository commands does not automatically opt into this adapter.

All inherited all-size/compiler, common-label/mutable-source, hosting,
precision/tape, analytic and bit-interface assumptions remain. See NOTICE.md
for predecessor attribution and AI disclosure, CLAIM.md for scope selection,
and VALIDATION.md for the exact completed checks and remaining limitations.
