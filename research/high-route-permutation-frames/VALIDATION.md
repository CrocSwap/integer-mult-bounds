# Verification record

Base: `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
Executable/certificate freeze: `14a8d05bd4215c451de7f62ce161ec36ffe12348`.
Linux x86_64, standard-library CPython 3.12.14 and 3.14.7.

## Completed checks

- The complete registered Python 3.12 replay passed all four suites at the
  frozen commit. It verified 840 seeded and 341 exhaustive words, 2,246 exact
  oriented source maps, 1,123 compiled low/carry programs, six complete
  physical before/after pairs and optimized failure controls. Both per-chart
  and summary certificate files match their generated typed receipts.
- `check_research_commit.py` passed all 49 package/input byte comparisons at
  that commit. The source proof pin also matches the exact PR3301 Git blob.
- A committed, read-only, Git-free export passed algebra, controls and all
  six physical comparisons under Python 3.14.7 with `-I -O -B`. Every one
  of its 50 exported files remained unchanged. The export did not repeat
  the full catalogue suite; that suite had also passed under Python 3.14.7
  during generation, and passed again in the registered Python 3.12 run.
- The final amendments add this completed record and BENCHMARK.json only.
  All executable, source manifest, proof and mathematical certificate bytes
  remain identical to the successful frozen replay. Final publication and
  export bytes are compared separately before pushing.

## Same-input measurements

[BENCHMARK.json](BENCHMARK.json) records three alternating fresh-process
pairs under Python 3.12.14, with the same 486-bit, nine-reverse-ADD fixture.
The physical and independent-column checks are enabled in both variants.
All six receipt hashes match the corresponding full physical-suite receipt.

| Interval | Baseline median | Scheduled median | Ratio |
| --- | ---: | ---: | ---: |
| Instrumented route entry/return | 3.671683727 s | 1.772377791 s | 2.072x |
| Whole fresh process | 4.004344101 s | 2.107719357 s | 1.900x |

Reproduce individual sides with `python3.12 -I -B
research/high-route-permutation-frames/benchmark.py`, adding `--optimized`
for the new schedule. The deterministic tape bill is 5,691,269 versus
2,808,517 operations; native calls are 72 versus 8. Timings include the
instrumentation/provenance overhead and establish no selected GL64 or
multiplication runtime ratio. They are not mathematical pass predicates.

## Scope and superseded exploration

The final acceptance policy includes the paid setup guard. The exploratory
native-count-only census (30.93% reduction) is superseded by the committed
29.64% result, which retains the conditional complete upper bound per chart.
The scripts do not search all permutation schedules or prove optimality.

No selected cold replay, fitted selected GL64 payload, full supplier audit,
proof-assistant verification or independent human review was performed.
The initial selected baseline-binding utility could not finish in the sparse
checkout because unrelated selected package roots were absent. The selected
record, review and manifest were read; this package's complete declared
input closure is independently authenticated. This does not stand in for
that unrelated full selected check. Hosted CI status is separate.
