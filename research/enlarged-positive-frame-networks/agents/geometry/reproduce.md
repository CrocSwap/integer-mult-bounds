# Geometry branch recovery

Run from the repository root on a little-endian host with Python3.14, a GCC or Clang C++17 compiler supporting unsigned128-bit integers, and Boost multiprecision headers. Promoted fixed/negative witnesses need no NumPy environment. The flag and boundary discovery scripts additionally use the recorded NumPy2.5.3 environment. Keep execution outside Git and set all BLAS/OpenMP thread variables to one. The worker count is a TOTAL native CPU allocation, not a per-task multiplier.

Recover the selected scalar DAG using [the graph branch](../graph/reproduce.md) and its retained parent/clone configurations. Choose the actual DAG whose SHA256 matches the selected axis wrapper; do not substitute a positive carrier matching or its R. Complete selected maps are retained in the wrapper or its complete gzip evidence copy. The geometry recovery driver accepts either form.

```bash
GEOMETRY=research/integer-multiplication-bounds/campaigns/fast-integration-gpu-20261008/agents/geometry
WORK=/path/to/fresh/external/recovery
python3 "$GEOMETRY/code/reproduce_selected_axis.py" \
  --dag /path/to/recovered/dag.bin \
  --expected "$GEOMETRY/results/best-negative-original-axis-23.json" \
  --work "$WORK"
```

Use the size25 wrapper for the other axis. For fixed I+J select `best-fixed-original-axis-23.json` or25. The driver compiles the retained native source from scratch, freshly derives ORIGINAL E(C,M) ranks and maximum matching, applies the recorded actual matrix-moment ordering/exchanges, recomputes every physical local profile with the appropriate fresh CRT bounds, compares every selected use and every histogram entry, creates independent integer envelope labels, and runs both independent scalar/frame and literal original compiler checks. No machine-local executable or foreign modified checkout is used. Four complete recovery runs were exercised: the first selected fixed axes and the best negative axes at both sizes, including fresh compilation and literal compiler review; receipts are in `results/recovery-*.json`.

To recover the negative data certificate, compile `code/negative_basis_classify_pairs.cpp` and run it into a fresh external JSON file. This enumerates the entire4073300-pair Cartesian family and replays whole pairs at alternate primes. Compile and run `code/fixed23_negative25_data_pairs.cpp` for the complete mixed certificate. Never combine prefixes from different primes into one nonvanishing replay.

The both-negative classification's `failures` records contain the exact192596 exceptions. Run `python3 code/build_negative_fixture.py --classification /path/to/classification.json --output /path/to/exceptions.bin` from this worker directory. It checks unique lexical indices and creates the complete fixture. Compile `code/negative_exception_rank_union.cpp` using `c++ -O3 -std=c++17`. Run four disjoint parts, or choose a lower total worker count:

```bash
negative_exception_rank_union /path/to/exceptions.bin 0 4 > /path/to/part0.json
negative_exception_rank_union /path/to/exceptions.bin 1 4 > /path/to/part1.json
negative_exception_rank_union /path/to/exceptions.bin 2 4 > /path/to/part2.json
negative_exception_rank_union /path/to/exceptions.bin 3 4 > /path/to/part3.json
```

Each part must report48149 exact pairs and1011129 field replays. Sum profile counts to192596. Add3880704 regular null profiles (nine singletons plus21,17) and add4073300 central481 blocks. The one-front rank mass must be4073300*528. The two-front distribution doubles the one-front counts. Compare with `results/both-negative-data-histogram.json`. The proof for this procedure is [negative-basis-proof.md](negative-basis-proof.md). The failed uniform19-profile checker is retained as a negative; it is not the certificate used for promotion.

The portable commands above reconstruct changed finite components. The coordinator's exact recurrence, bulk stock, correction calls, scalar bounds and all47 assembly inequalities are separate scripts and certificates. This branch does not claim that local profile recovery alone proves an infinite multiplication theorem.
