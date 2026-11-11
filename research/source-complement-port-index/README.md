# Map every source row to its whole complement invocation and child input slot

**Scoped constructive compiler interface; no new kappa.** This package
provides a direct, invertible map from each published replicated source-row
integer to the exact smaller-program invocation and input slot that completes
its complementary coordinates. It does so without enumerating the replicated
source arrays or the chronological class tree. A source already of full rank
N receives an explicit `NoComplement` label; no B_0 program is introduced.

The result follows the [published source-row index](https://github.com/CubeJerry/integer-mult-bounds/tree/c5bcb6dc792f5fe4d8abe89a2a2854f148b09f2c/research/lockstep-source-row-index)
and its [occurrence/owner codec](https://github.com/CubeJerry/integer-mult-bounds/tree/91246e5131152ccb1f64a969c36706360861f821/research/pascal-occurrence-codec).
Its target is the actual pre-flow complement phase in
[FINITE-PRECOMPILATION.md](reference/FINITE-PRECOMPILATION.md), section 4.
Counting the histogram or clearing its denominators was already solved;
the new result resolves the individual real occurrences into those batches.

## Exact result

The true source-job rank of role i in a unit is
`s=rho(path)*c(alpha)*k_i`. At a fixed s, the missing-parent condition becomes
`h=0 or A*s>N*r_last`, and the unit-fit condition becomes `A*s<=N*k_i`.
Shared ordered-word product counts therefore compute each class's rank-s
source count in d lookups, without scanning all multiindex profiles at every
state. Product coincidences add counts; physical fields remain distinct.

Each true-rank bucket has an exact rank/unrank in the preceding source
order. If j is that bucket index, b the replica and S_s its size, then
`x=b*S_s+j`. For a nonzero complement e=N-s, the supplied width B_e must
divide a*S_s, and `divmod(x,B_e)` is exactly its invocation and input slot.
The inverse recovers b,j and the old row. Rank N skips this division and
supplies no complement call.

The metadata construction has a deterministic polynomial bound for fixed
native rank alphabets. It uses sorted product/count tables and retains only
one active rank-bucket DP. The full cost includes predecessor indexing,
candidate ranks that turn out empty, large integer arithmetic, queries that
change buckets, and the supplied width/replication bit lengths. A separate
conservative serialized-table simulation charges scans, cursor returns,
updates and erasure. See [PROOF.md](PROOF.md), section 6.

## A batch that crosses replica boundaries

For productive roles (small,2),(large,5), paid sites (1,small),(1,bank),
A=5,N=10, the four unreplicated source ranks in the fixed row order are
4,10,5,5. At three replicas, the rank-5 bucket has six arrays. With a
supplied complement rank-5 program of width three, its invocations use:

| Complement invocation | Existing source-row integers |
| --- | --- |
| 0 | 2, 3, 6 |
| 1 | 7, 10, 11 |
| No complement, source rank 10 | 1, 5, 9 |

The first invocation crosses from replica zero into replica one. Dividing
the old source-row integer directly by three would give the wrong fields.
The rank-4 sources use the separately supplied rank-6 width-one program.
This example specifies addresses; executing the gathering and restoration
still has its physical cost.

## Reproduction and evidence

After placing the package at `research/source-complement-port-index/`, run:

```sh
python3 -I -W error -B research/source-complement-port-index/verify.py
python3 -I -W error -O -B research/source-complement-port-index/verify.py
```

Both standard-library commands print `PASS_TRUE_SOURCE_COMPLEMENT_PORTS`;
the executed normal and optimized outputs agree exactly. The unchanged
literal DAG oracle supplies **26 flows, 755 source fields and 1,334 replicated
rows**. Every bucket order, class-local/subtree count and whole-complement
port inverse agrees. Four fitting classes contain distinct multiindices
with the same column product. Eighteen rejecting controls cover wrong
freshness equality, dropped product multiplicity, repeated paid sites,
replica merging, zero complements, divisibility, namespaces and bounds.

A height-24 example uses **601 count states** and **266 candidate source
ranks**, with 206 nonempty buckets, to index
**216,192,013,559,808 source arrays per replica**. Its chronological tree
would have 423,644,304,721 classes. A separate method verifies every rank
count by subtracting actual incoming paid jobs from the full target census;
it uses no rank-bucket freshness test or subtree DP. Six replicated row
positions round-trip. Finite checks corroborate the written theorem; they
are not an asymptotic experiment or formal-kernel proof.

[SOURCES.json](SOURCES.json) pins all reused code and reference bytes.
[VALIDATION.json](VALIDATION.json) records the executed receipt. Namespace,
actual occurrence, true job rank and integer row position remain distinct.

## Prior work and limits

[#4507](https://github.com/CrocSwap/integer-mult-bounds/pull/4507) and
[#5071](https://github.com/CrocSwap/integer-mult-bounds/pull/5071) already prove
the source/complement census, least gcd/LCM factors and the need to preserve
individual chronological exit cuts. [#4638](https://github.com/CrocSwap/integer-mult-bounds/pull/4638)
extends batching to adaptive-height forests. [#6086](https://github.com/CrocSwap/integer-mult-bounds/pull/6086)
and [#6612](https://github.com/CrocSwap/integer-mult-bounds/pull/6612) improve
different width bounds; this contribution claims no width improvement.
The new work is the individual source-occurrence/child-port map and its
costed true-rank counting interface.

The supplied a is checked only against complement divisibility. The full
compiler must also clear every separate ordered exit batch. All smaller
programs and their whole-job adapters remain supplied premises. The map
does not execute a payload permutation, copy inputs, create a source from an
owned bank, construct the selected astronomical native manifest, or price
the complete native/tape/numerical caller. The selected conditional
**kappa=0.00363005817** and all five foundational assumptions remain.

Next work should join one real smaller-program library and its explicit
whole-field adapter to these ports, then price the actual grouping/return
permutation. Separate chronological exit-port indexing is another remaining
emitter obligation; source grouping does not authorize pooling those exits.

## Credit

Prepared for **Jerry Chen / @CubeJerry**, with substantial OpenAI assistance.
The preceding two published codecs retain their proof and independent AI
review credit. Jacob Alan Sussman supplies the Pascal/lockstep flow; zxv its
native finite compiler and literal DAG audit; Mihir Srivastava supplies
#4507's chronological gcd/LCM policy; JoyboyBrian supplies #5071's exact
separated batch/bit-size formulation. codyw912 and the other cited authors
retain the adaptive-width and native lineage. All reused headers remain.
Apache-2.0; see [NOTICE.md](NOTICE.md).

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
