# Executed validation and limitations

Environment: Windows, CPython 3.14. Exact research base
`bbc600db2fc15007b7c914f4f2b2ed55fa909c87`. No third-party Python dependency is
required by the new package or its exercised Python checker paths.

## Completed

- Complete bounded discovery replay: PR952 fixed-transfer minimum 12,
  41,235 states / 209,118 edges; reverse-guard shortest-path exhaustion,
  116 paired states / 283 edges. The earlier conjugate selected-word
  exploration is retained and attributed, not claimed as a new minimum.
- Independent first-gate column BFS: minimum 12, 41,203 visited states,
  208,824 examined edges from completed layers 0..11.
- Independent paired-column BFS: reverse-guard minimum 13, 735 states,
  completed layers 0..12. Nine independent controls reject mathematical
  corruption, incorrect lower/upper claims and resource exhaustion.
- All 64 local Boolean inputs, exact forward integer matrix and reported
  reverse matrix; four reverse entries grow, so local domination is explicitly
  false. Complete F/B bounds are recomputed instead of assuming domination.
- Exact whole-word forward and reverse symbolic replay on all 661 arbitrary
  source/target/helper input columns; original E8/frame checker and H1-H5.
- Fresh supplier export followed by a separate set-valued interpretation of
  every actual binary MOVE, ADD, COPY and ERASE record. ADDs 23673->23671,
  records 26602->26600; MOVE/COPY/ERASE costs, frame paths and paid histogram
  unchanged. These are **exported-record checks**, not native C++ execution.
- Exact inherited local and nine-stage scalar prefix expressions: 92 and 174
  bits under 104 and 192. Their respective bounds do not increase. The nine-stage
  expression and bridge count are checked against the pinned source AST.
- Seven additional local/whole-word negative controls: deleted ADD, swapped
  operands, Boolean-neutral positive inflation, omitted cleanup, stale
  nonliteral cleanup, invalid lower frame and missing dirty compensation.
- Source inventory coverage, normalized-text/immutable-gzip hashes, full
  deterministic witness regeneration, and canonical certificate comparison.

The reproducible command is
`python -I -B research/r439-frame281-seed15/verify.py`. Its final output is
recorded in README; `CERTIFICATE.json` contains the exact proof-relevant results.
The verifier uses temporary outputs by default and does not regenerate unrelated
repository artifacts.

## Unavailable or not executed

- `make verify` was attempted once and stopped immediately: **make is not
  installed/on PATH**. The repository-wide suite did not execute.
- `python -I -B research/r439-frame281-seed15/native.py` was attempted and stopped
  at preflight: **no GCC/Clang-compatible C++17 compiler was available**. Existing
  MSVC was detected but the inherited harness uses GCC-style flags. Accessible
  Boost headers were not found in checked common locations and WSL had no
  registered distribution. No tools or system configuration were installed.
- The optional native harness was syntax checked and its prefix arithmetic
  compared with a retained predecessor receipt. That is not a new native run;
  no native certificate is included. Native legality, 883/1327/1549 formal-column
  runs and 96 omitted-bridge controls remain for a suitably provisioned machine.
- Selected cold complex replay, full hosted emitter adoption, global invoices,
  outer reassembly and formal proof of the multiplication theorem were not run.
  The selected pointer and all predecessor sources remain unchanged.

## Development failures retained as limitations of the process

An initial canonical witness comparison failed because in-memory histogram
keys were integers while JSON-loaded keys were strings, leading to different
sort order. The keys are now strings at construction; strict canonical replay
passes without changing circuit results. No failed certificate was edited into
a passing receipt. Duplicate JSON keys and nonfinite values are rejected.

The first selected-word search duplicated a predecessor matrix up to register
permutation. This was detected, credited, and caused the documented single
pivot to PR952's different matrix. The successful finite result does not imply
a new kappa or solve the remaining all-size/compiler and physical obligations.

The sandbox's default Windows temporary directory later refused file writes.
Replays were rerun with the process-local `TMPDIR` pointing to a writable
workspace scratch directory; the default temporary-output path then passed.
This changed no mathematical code or system configuration. Scratch outputs
and failed runs are excluded from the patch.
