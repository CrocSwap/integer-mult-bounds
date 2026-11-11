## Change and mathematical scope

The published [source-row index](https://github.com/CubeJerry/integer-mult-bounds/tree/c5bcb6dc792f5fe4d8abe89a2a2854f148b09f2c/research/lockstep-source-row-index)
left source-rank grouping and complement batches open. This supplies an
exact inverse map between its replicated row integers and every whole
complement invocation/input slot in FINITE-PRECOMPILATION section 4.
Sources of rank N receive an explicit no-complement label; no B_0 is invoked.

For true job rank s, freshness simplifies to A*s>N*r_last and unit fit to
A*s<=N*k_i. Shared product tables then supply each class's rank-s source
count in d lookups. Each bucket retains occurrence order and supports exact
rank/unrank. Given the supplied complete smaller-program width B_(N-s),
quotient/remainder of b*S_s+j selects the invocation and its input slot.
The inverse recovers the original replica-major source row.

**No new kappa, width improvement or full assumption discharge.** Selected
conditional kappa remains 0.00363005817.

## Why this is new

#4507 and #5071 already prove the source census, whole-batch divisibility and
least gcd/LCM replication factors. Those results are credited. This adds the
individual source-occurrence/child-port identification without expanding
all replicas, unit ordinals or class paths. Equal true ranks and coincident
products share counts while retaining separate source fields. The complete
deterministic metadata cost includes candidate ranks with zero sources and
a paid serialized-table access model.

## Verification

```sh
python3 -I -W error -B research/source-complement-port-index/verify.py
python3 -I -W error -O -B research/source-complement-port-index/verify.py
```

Normal and optimized receipts agree: 26 literal flows, 755 sources, 1,334
replicated rows, four fitting product-collision classes and 18 rejecting
controls. A source-pinned literal DAG oracle checks every bucket/port inverse.
A height-24 case indexes 216,192,013,559,808 sources per replica with 601
states and 266 candidate ranks. An independent target-minus-incoming census
checks all 206 nonempty rank counts; six large replicated positions round-trip.

A concrete rank-5 width-three complement uses old rows (2,3,6), then
(7,10,11), crossing replica boundaries. Full-rank rows (1,5,9) skip the
complement. Mutations reject incorrect freshness equality, overwritten
product coincidences, merged paid sites and merged replicas.

Canonical base: e54523517d0f03e58352e647c403a5af3e525a57.
Source-index dependency: c5bcb6dc792f5fe4d8abe89a2a2854f148b09f2c.
Occurrence-codec origin: 91246e5131152ccb1f64a969c36706360861f821.
Exact input blobs and byte hashes are recorded in SOURCES.json.

## Limitations and next obligations

This is a logical grouping/dispatch interface. Payload permutation, adapters,
copy/restoration/erasure, actual smaller programs and the selected native
manifest remain supplied obligations. Complement divisibility does not
replace separate chronological exit-cut constraints. No owned bank becomes
an independent productive source. The complete multiplier, five framework
assumptions and all numerical/precision/tape costs remain conditional.

Next: bind one real smaller-program library and whole-field adapter to these
ports, then price actual grouping and return. Separate exit-port indexing
must preserve its chronological cut boundaries.

## Credit

Prepared for Jerry Chen / **@CubeJerry** with substantial OpenAI assistance.
Credit the two published codecs and their separate AI reviews; Jacob Alan
Sussman's integer Pascal flow; zxv's native compiler/literal oracle;
Mihir Srivastava's #4507; JoyboyBrian's #5071; and the cited adaptive-width
predecessors. Original source headers are unchanged. Apache-2.0.

## Independent acceptance checks

The orchestrator read the full proof and implementation, checked the exact
source substitutions, candidate-rank bound, interval inverses and the complete
metadata cost distinction. The separate [peer review](independent/REVIEW.md)
constructs expected sources by literal role-word parent edges without using
the author census, freshness predicate or parent resolver. It passes 22 flows,
328 sources, 3,900 replicated rows, 2,707 whole invocation rectangles, 51
NoComplement rows and 11 rejection controls. Both cross-replica batches are
recovered independently. A minor transient old/new bucket wording correction
was incorporated; the executable files were unchanged.

```sh
python3 -I -W error -B research/source-complement-port-index/independent/check.py
```

Expected: `PASS_SOURCE_GROUPS_PEER_REVIEW cases=22 sources=328 rows=3900 controls=11`.
The exact reviewed hashes and test domain are in `independent/RESULT.json`.
Author normal and optimized replays pass identically from this final package.
These are independent AI checks, not human or formal-kernel acceptance.
The complete proposed PR description is committed in `PR.md`.
