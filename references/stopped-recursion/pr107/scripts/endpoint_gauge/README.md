# Endpoint-gauge finite producers

Copyright 2026 icekylinx, Apache-2.0. Adapted with OpenAI GPT-6 Astra and
Codex assistance from the endpoint-gauge research handoff. The retained
pair/triple circuit modules carry the previous contributors' attribution;
see the repository `NOTICE` and `SOURCES.json`.

From the repository root run:

```sh
python3 scripts/endpoint_gauge_producer.py
```

This regenerates both selected producer families for dimensions 32, 30,
and 40, compiles the deterministic matchers, and compares every producer
count and histogram entry with the two endpoint-gauge input certificates.
`--work-dir PATH` keeps intermediate files; by default they are temporary.
`--output PATH` writes the complete JSON report. Python assertions must be
enabled. Only standard-library Python and a C++17 compiler are required.

The bit producer uses the ordinary paired base threshold **four** and
reuses the partial-swap binary exporter, exact support verifier, initial
matching, dependency-preserving positive labels, and final matching.
The complex producer uses paired triple base **two**, complete ordinary
supports, retained doubled point centers and a global total. It checks
ordinary support partitions, exact center coefficients, the Gaussian-dyadic
scalar correction identity, and binary frame nesting before export.

The complex matcher is the selected deterministic research matcher with
portable little-endian reads and standard integer population counts.
Its binary DAG layout is the same as the bit layout. The separate `.labels`
file contains one little-endian uint32 rank per node, then one uint8 label
type per node (1 = triple-star span, 2 = coordinate space, 3 = point-center
hyperplane). Node zero is unused. No raw DAG or compiled executable is a
source dependency. These finite checks do not implement the complete
recursive multiplication machine.
