# Exact maximal-mask setup for the four-flat decoder checker

**Tooling improvement with a scoped equivalence proof.** The four-flat search
constructs, for each active direction and first flat, the inclusion-maximal
masks `Off(h) \ X1` intersected with candidate 7-flats. Its original setup tests
every candidate against every other candidate. This adapter uses cardinality
buckets and compares only against already retained, strictly larger maxima.
It restores the original ascending mask order before the search resumes.

This answers a separate setup bottleneck in
[Discussion2954](https://github.com/CrocSwap/integer-mult-bounds/discussions/2954#discussioncomment-18977655).
It composes with PR2975's faster requirement enumeration. Both benchmark builds
use that same predecessor option generator; the only mathematical computation
changed here is maximal-mask filtering. No new pruning of pairs or directions,
new decoder exclusion, supplier, or kappa is claimed.

## Result and evidence

| Same-input workload | Reference | Accelerated | Speedup |
| --- | ---: | ---: | ---: |
| Maximal-mask filtering, both representatives | 104.85 s | 11.26 s | 9.31x |
| Complete per-representative setup | 107.28 s | 13.55 s | 7.92x |
| Full bounded run, shared catalogue/orbits included | 156.74 s | 61.42 s | 2.55x |

Final registered Python 3.12 replay passes. The earlier complete serial trial
measured 9.14x filtering and 2.58x total speedup, with identical exact outputs.

See [RESULT.json](RESULT.json) for the serial same-input measurements and exact
receipt hashes. The benchmark runs complete setup for representatives **46 and
94** of the source's `a=4,b=6,c=4,d=5` configuration, and the predecessor's fixed
12 pairs for representative 46. The second representative is selected by OS
assignment seed 94. An additional `a=b=6,c=4,d=0` case preserves the known relaxed
span-five witness at representative 82, V2 index 103676.

The comparisons cover every active-direction index, residual mask, cap, maximal
mask and its order, all eleven downstream requirement records, the complete output/histogram
reporting 5,509 closure leaves, and the positive witness.
Temporary binary setup records contain the complete arrays, not a sampled
checksum. The verifier compares their bytes; only compact hashes/counts are
committed. The timings measure this verifier on the recorded host, not integer
multiplication or the entire class-C campaign. Benchmark wall time includes
setup-state serialization and requirement exports, excludes compilation and
additional controls. Filter/setup phase times use process CPU time and exclude
setup-state serialization. A speed threshold is deliberately not a correctness
predicate.

Independent explicit-set controls cover all **65,536** families of subsets of a
four-point universe, 2,000 deterministic wide-mask families, and 128 cases covering
every bit position. Six implementation mutants must fail, including wrong bucket
order, reversed containment, omitted high bits and lost canonical order. The
same cases run under undefined-behavior/bounds sanitizer traps. Source-byte and
missing/ambiguous adapter controls fail closed. This is a representation-level
argument and finite replay, not a second independent proof of the outer decoder
search or a formal multiplication theorem.

## Reproduce

From a checkout containing the seven declared predecessor files:

```sh
python3 -I -B research/four-flat-maximal-masks/verify.py --work /tmp/four-flat-masks
```

Use a fresh output directory, Python 3.12+ and a `cc` supporting GNU C11,
unsigned 128-bit integers, `-fsanitize=undefined,bounds` and
`-fsanitize-undefined-trap-on-error`. No Python third-party dependencies, network,
Git metadata or cached scientific results are needed by this command.
Expected: `PASS_MAXIMAL_MASK_CONTROLS` and `PASS_MAXIMAL_MASK_FULL`.
`--controls-only` and `--full-only` select the separately bounded obligations.
The registered command is:

```sh
python3.12 scripts/research_package.py --package research/four-flat-maximal-masks
```

Both builds authenticate all external inputs by SHA256. Source adapter anchors
must occur exactly once. Source files and the inherited circuit/checker remain
unchanged; generated C, executables and large records live only in the work
directory. `SOURCES.json` pins the baseline main commit, exact predecessor and
all live bytes; `VERIFY.json` declares those inputs for CI selection.

## Equivalence proof

Let `F` be a finite collection of **distinct** bit masks, ordered by set
inclusion. The frozen source sorts and deduplicates `tmp` immediately before
the replaced block. Its output is the ascending list

`Max(F) = {x in F : there is no y != x in F with x subset y}`.

Process masks in descending cardinality, with an arbitrary order within each
bucket. Maintain the retained maxima of the already processed, larger buckets.
For a candidate `x`, any proper superset has strictly larger cardinality and has
already been processed. If such a superset was discarded, it was contained in
an earlier retained mask. By transitivity that retained mask also contains `x`.
Consequently `x` is nonmaximal if and only if a retained larger mask contains it.
Distinct masks of equal cardinality cannot contain one another, so comparisons
within a bucket are unnecessary. No future smaller mask can invalidate an
accepted maximum. This proves the invariant and exact maximal-set equality by
induction over the buckets. Empty input returns the empty list; the zero mask
is handled by the same argument. Sorting the retained masks with the original
integer comparator gives the **same ordered array** as the predecessor.

The C implementation uses all 128 bits for cardinality and containment. Bucket
indices lie in 0..128, their sizes sum to the input count, and the permutation
contains each input index exactly once. At the start of a bucket, `larger` fixes
the count of earlier maxima; newly appended equal-size masks are intentionally
not tested. Input and output buffers are distinct and each holds at least the
input count, as provided by the original `tmp`/`mx` allocation. Additional space
is one integer index per input mask and three 129-element arrays. Worst-case
containment work remains quadratic; the claim is the measured reduction on the
named workload, not a universal subquadratic bound.

Every other setup calculation is unchanged. Thus identical `mx` implies
identical `LG`, `LGn`, `capr`, `act` and `R1` for each direction. The unchanged
outer search receives exactly the same arrays and order; its branch sequence,
requirements, closure and reports are preserved, conditional on the inherited
implementation. Source authentication and exact-once replacement prevent silently
applying this argument to an unrelated future source version.

## Scope, provenance and credit

Scientific base: `b3f3ee0392b71b118fd086a6eaf6b4cab54ef455` (priority revision 5).
Submission refresh: `836b19bfa309ceafbc8ee32a15e8c4b10dde7e11` (revision 6).
The revised guidance, family record and priority log were read; the replay-runtime
card, selected record and all runtime inputs are unchanged. This is bounded
replay acceleration, not a larger static-cover census.
Predecessor PR2975: `1d7b491c9efad451d49dbfd36a3be7443999bf17`.
Original DreamingOfClouds help package:
`1b25759bff5486293a9083ebbe0097b5f6642e08`, `research/k2-class-c-help`.
The selected maintainer-reviewed conditional kappa remains
`0.001672660197076918`; merged archive status does not certify newer claims.

Credit **DreamingOfClouds** for the four-flat engine, original maximal-mask
construction, help request and #2816/#2826/#2862 lineage, and Tekalign's PR2975 for
the separately retained requirement-enumeration improvement. PR2985's newer
residue-closure work is complementary; its claims are not prerequisites of this
filter equivalence. Prepared by **Tekalign (@tekuuu)** with substantial **OpenAI
Codex assistance** in analysis, implementation, checking and writing.
Apache-2.0, as the repository and predecessors. No independent human review is
claimed.

The direction catalogue, group/orbit reduction, real-rank arithmetic, RRC,
complete decoder floor, native/supplier admission and all-size multiplication
interfaces remain inherited or unresolved. This package does not audit or
silently accept those obligations. The seeded finite fixtures are performance
measurements, not a new impossibility theorem. It does not launch a larger
construction/search campaign or alter the selected frontier.

## Open next questions

- A stronger common-flat gate or exact orbit reduction is still needed before
  the full campaign is affordable. First profile the transformed search, then
  prove any proposed reduction cannot discard a possible span witness.
- Measure other representatives/configurations with the same complete setup
  comparison. The present timing evidence covers only the named inputs and host.

Structured questions, stopping rule and the three candidate tasks considered
are retained in [TASK.json](TASK.json).
