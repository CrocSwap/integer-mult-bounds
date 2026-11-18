# Validation record

Author checks used CPython 3.12.16 on macOS arm64 with the standard library.
The normal and optimized registered commands passed, with warnings treated
as errors. Syntax and indentation checks passed for the three new modules.
No test relies on Python assertions for its scientific checks.

```sh
python3.12 -B scripts/research_package.py --package research/owned-canonical-row-producer
```

Expected final line:

```text
PASS_REGISTERED_RESEARCH_PACKAGE research/owned-canonical-row-producer outcome=completed
```

`RESULT.json` records the fixed graph digest and exact transition/history
counts. Both instruction paths check complete owner states and head returns.
The canonical compiler checks all small rows; the closed formula checks the
larger rows. These mathematical oracles share predecessor definitions but
do not drive the physical program. All eighteen retained source files and
all 3,237 embedded point instructions are checked exactly.

Release checks use the committed package and source history, an exported
archive, and both registered commands in a read-only directory without Git
or tools on PATH. The PR and canonical Discussion record report the actual
release and hosted-CI outcomes. Export integrity and source hashes do not
establish the mathematical theorem by themselves.

No full historical scientific suite, selected cold replay, Lean or Docker
was run. The two instruction paths share the same emitted graph and fixture
boundary. No independent human or formal-kernel acceptance is claimed.
The program operates on supplied descriptors and blank owner windows;
actual CRT descriptor production, transport, payload use and output disposal
are not part of its local transition count. No fragile source patch, runtime
callback or host-generated query address is used.
