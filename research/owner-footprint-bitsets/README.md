# Exact owner-footprint bitsets

**Tooling improvement; no new κ.** Replace the occupied-cell Python sets in
PR626's independent owner checker with exact integer bit masks. On the same
frozen inputs, final local 31-pair runs measured **12.9–18.7% less wall time
for the complete checker**. Every result receipt is byte-identical.

The scope is one supplemental check of 35,424 helper roles. This does not
change a supplier, owner map, mathematical bound, selected pointer or default
verification command. The original source packages and `upstream/` stay intact.

## Reproduce

From the repository root, with Python 3.11+ and its standard library:

```sh
python3 -I -B research/owner-footprint-bitsets/verify.py
```

Expected final line:

```text
PASS_OWNER_FOOTPRINT_MASKS baseline_runs=6 negative_controls=19 positive_controls=1
```

The command uses the immutable archived PR622 native artifacts already in the
repository. It copies only its 12 pinned execution inputs into a temporary
path containing spaces, replays the original direct CLI and both adapter
engines (including optimized Python), then checks repinned corruptions and a
valid row permutation. Temporary files are removed; repository inputs are
unchanged. This is not a fresh reconstruction of the native suppliers.

Additional arithmetic-oracle tests and reproducible timing:

```sh
python3 -I -B research/owner-footprint-bitsets/test_masks.py
python3 -I -B -O research/owner-footprint-bitsets/test_masks.py
python3 -I -B research/owner-footprint-bitsets/benchmark.py --pairs 31 --out /tmp/owner-mask-benchmark.json
```

Expected: five tests pass in each test invocation, followed by
`PASS_OWNER_FOOTPRINT_BENCHMARK` for the benchmark. Choose a fresh output path;
it is never overwritten. Timing has no pass/fail speed threshold. The
benchmark checks every complete receipt, including the exact moment fractions.

To use the adapter with the pinned checker on a separately prepared work
directory, pass its original arguments to `adapter.py`, for example
`--work /path/to/work --out /path/to/new-result.json`. The inherited provider
defaults are `work/ck-local` and `work/jp8-local`; original `--provider PID=DIR`
overrides are supported. The default engine is `masks`; `--engine sets` runs
the reference code through the same adapter. Source drift is rejected.
Input changes must satisfy the original checker's plan, owner and native
bindings. The standalone adapter does not claim an audit of a changed supplier.

## What changes, and why coverage is retained

The adapter pins the original checker and rational-interval source, then
makes four counted substitutions: empty set to zero, interval to bit mask,
compact-prefix set equality to a binary predicate, and cardinality to
`int.bit_count()`. Intersection and union continue to use `&` and `|`.
Every original `need` statement and the complete moment arithmetic execute
unchanged. The [equivalence argument](PROOF.md) proves these finite-set
operations agree for nonnegative integer cells, including empty intervals.
No accepted result or geometry is cached.

Validation covers:

- 18,943 exhaustive subset/interval comparisons for capacities 0 through 8,
  2,000 seed-91 larger cases through capacity 4,096, and sparse/boundary cases
  through bit 8,192. The oracle uses Python sets and integer powers.
- Five actual adapter-source mutations caught by the independent set oracle:
  omitted offset, off-by-one interval, displaced interval, and two incorrect
  compact-prefix predicates.
- Fifteen whole-check mathematical/data controls: overlap, an interior gap,
  negative offset, capacity overflow, width, duplicate helper, physical family,
  copy, stage, missing role, paid profile, both failed moment thresholds,
  native forward/backward disagreement, and changed inherited geometry.
- Two inherited input-pin and two adapter source-pin controls. Changes are
  repinned where necessary to reach the stated predicate; the native-program
  control also updates its immutable-hash declaration intentionally. These are
  invalid-input controls, not defects alleged against the accepted construction.
- Exact matching rejection diagnostics for both adapter engines. A shuffled
  valid role list and the six baseline invocations retain the full original
  receipt, including idle remainders and both rational moment brackets.

The final full-control receipts agree on Python 3.14.6 and 3.12.11. Normal and
optimized unit suites pass on 3.14.6; normal unit tests also pass on 3.12.11.
The selected-record binding check and staged whitespace check pass. A separate
minimal relocated package replay is recorded in `evidence/SUMMARY.json`.
A scoped Linux workflow is supplied as `workflow.example.yml` for maintainer
installation. It is not enabled: the publishing credential lacks GitHub
`workflow` scope. Local evidence is not a remote CI claim.

## Measured result

All samples start a fresh interpreter. The reference is the **unchanged direct
CLI**; the candidate includes adapter import, source hashing and transformation.
The same archived inputs are used for every sample, with alternating order
starting with the reference (seed 91). OS caches were not flushed, and other
system activity was not controlled. The raw samples, child CPU times and code
hashes are retained in `evidence/benchmark-*.json`.

| Interpreter, macOS arm64 | Pairs | Original median | Masks median | Wall reduction | Masks faster |
| --- | ---: | ---: | ---: | ---: | ---: |
| CPython 3.14.6 | 31 | 0.5620 s | 0.4571 s | 18.7% | 27/31 |
| CPython 3.12.11 | 31 | 0.5108 s | 0.4447 s | 12.9% | 28/31 |

An earlier 31-pair 3.14 run measured 21.1%; the seven-pair inline-mask pilot
measured 14.0%. Both are retained, not substituted for the final measurements.
The adapter kernel is unchanged between the 31-pair runs. `verify.py` was
strengthened before the final runs: the physical-family control now reaches
that exact formula guard, and failure strings must match exactly. The older
`validation.json` records the earlier, weaker diagnostic check; the two
`validation-final-*.json` files are the final evidence.

No full-frontier wall-time, memory reduction, practical multiplication speedup
or universal performance guarantee is claimed.

## Provenance and remaining scope

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Selected conditional κ remains `51110230636731/31250000000000000`, or
`0.001635527380375392`: #626 with #543, as specified by
`certificates/selected-result.json` and its actual #626 assembly/review.
[ORIGINS.json](ORIGINS.json) pins all 12 execution inputs by SHA-256 and Git blob,
and records the immutable #626/#622/#623 source commits. Native files are
original archived compressed inputs; the inherited exact-byte native check is
retained. No claim about regenerated gzip container equality is added.

OS assignment seed **91**, verification-engineering track. Three narrow
candidates, the local claim, seed use and overlap review are in
[CLAIM.json](CLAIM.json). No open sprint issue was available. The final refresh
covered 539 open PRs through #720. PR672 optimizes exponential intervals in the
same checker; this work changes footprint representation and does not compose
its kernel. PR667/662/707/709/367/452 address other costs. Their descriptions
were considered for overlap, not independently verified here.

Repository-wide `make verify`, selected supplier cold replay, full controller
and 47-inequality assembly, and Lean were not rerun for this isolated opt-in
adapter. All-size/compiler/common-label/mutable-basis, whole-call hosting,
residual, precision/tape/exact-recovery and analytic-transfer obligations remain
inherited. Finite equivalence tests are not a formal proof of the multiplication
theorem. Original sources and contributor notices are retained; see
[NOTICE.md](NOTICE.md) for attribution and substantial AI-assistance disclosure.
