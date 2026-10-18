# Validation receipt

Scientific base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Local platform: macOS arm64. New package: standard-library Python only.
No Linux CI, Lean, full multiplication theorem, or human peer review is claimed.

The following passed on **CPython 3.9.6** and **CPython 3.12.14**:

- Exact certificate verification, including isolated optimized (`-I -O -B`)
  execution, all 2,246,839 triples, 40 pair/triple hits, four minimum supports,
  both ranks, the 155-port information set, all eight rejection categories,
  and all 20 individual restored-port failures.
- All five independent test groups. These directly solve 45 principal decoder
  systems (four accepted optima, 20 one-port restorations, 20 wrong five-port
  sets, and the full family), check the scope controls, construct all 155
  information-set decoders, and reject four corrupted certificates in
  optimized subprocesses.
- Independent certificate generation gives byte-identical JSON across both
  Python versions. The verifier imports no generator or predecessor module.

`make selected-record-check` passed, checking the current exact κ, original
source inventory, and proof supplements. The selected assembly's SHA-256
matches the selected-result record. The inspected base/source pins are retained
in SOURCES.json. These integrity checks are not a cold supplier replay.

The repository-wide `make verify` was attempted on a **separate detached
checkout of the unchanged base**, protecting the contribution from generated
artifact changes. It did not complete:

1. With system Python 3.9.6, the existing copied-reversed producer uses
   `int.bit_count`, unavailable on that interpreter.
2. After installing Python 3.12.14 inside the task's scratch directory and
   retrying, that existing producer reaches C++ compilation, where the local
   compiler cannot find the standard `<algorithm>` header. It exits from
   `scripts/endpoint_gauge/match_complex_general.cpp` before the later groups.

These are observed baseline/environment failures, not a successful full-suite
run or a finding against the mathematics. The Python-only contribution has no
C++ dependency. No further unrelated toolchain repair or repeated aggregate
suite was attempted. `frontier626-verify` was not run separately because no
selected-construction file changes.

Final clean-package replay, staged whitespace validation and publication
metadata are recorded in the handoff. Only `research/global-star-punctures/`
is added. There are no changes to `upstream/`, existing generators, suppliers,
or the selected-frontier pointer.

All checks and proof review in this contribution used substantial OpenAI
Codex assistance. The separate direct-equation implementation is an algorithmic
cross-check by the same AI-assisted contributor, not a claim of separate human
review or a proof-assistant result.
