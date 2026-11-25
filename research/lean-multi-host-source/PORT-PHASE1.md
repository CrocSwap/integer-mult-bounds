# Lean 4.21 compatibility probe (Phase 1 only)

This branch probes 12 existing modules and their 39 new generated node modules.
**Phase 1 passed:** a clean checkout freshly compiled all 51 local modules in
291.242 seconds and audited all 567 listed declarations in 17.800 seconds, with
only standard axioms. See the [receipt and integrity checks](phase1-results/README.md)
and [complete timing comparison](phase1-results/TIMINGS.md).

It does **not** port or verify the complete Task A / Task B package. The original
4.33 receipts, full-package manifests, replay scripts and PR description retain
their historical meaning; they are not 4.21 validation receipts. Full-package
manifest updates and the 931-declaration audit belong to the approval-gated next
phase. No changes have been pushed to PR #540.

## Exact sources and external settings

- Review base: `c4b1560a569f54064608bf88440f9e492c03fba3` on
  `lean/pr442-invocation-review` (unchanged).
- Probe branch: `lean/pr442-lean421-probe`.
- Upstream source: `db0e57bc7f36b5ac0fc844ad7ce1396165ee6647`.
- `formal/lean/lean-toolchain`: `leanprover/lean4:v4.21.0`.
- Lean compiler commit: `6741444a63eec253a7eae7a83f1beb3de015023d`.
- `formal/lean/lake-manifest.json` Mathlib revision:
  `308445d7985027f538e281e18df29ca16ede2ba3`.
- The new Lake manifest pins the same dependency commits as upstream. Its root
  package name is `InvocationProbe`; its Mathlib input revision is the exact
  commit rather than a tag.

Existing source `set_option maxHeartbeats` and `maxRecDepth` lines remain.
Verification must use the ordinary inherited OS stack (8 MiB on the measured
Linux host), no raised Lean stack, no extra compilation flags and no environment
overrides. Lake's own automatically supplied dependency search path is part of
normal Lake execution. Selecting an installed Lake executable is toolchain
selection, not a resource or proof setting.

## Representation changes

The original monolithic `MatrixData` overflowed the default stack. A diagnostic
with raised OS/Lean stack succeeded, but **does not count as a compatibility
pass**. Splitting only event lists into 16-event named suffixes was insufficient:
a temporary progress diagnostic reached approximately 3,500 tree-node
declarations before the overflow, before any event chunk was elaborated.

The final representation splits the 21,655 matrix node declarations across 22
modules and the 16,195 frame-trace node declarations across 17 modules, at most
1,000 per module. Every node declaration keeps its original name, type and body.
Event lists use named suffixes of at most 16 literal events. The public 96 chunk
names and boundaries remain unchanged (95 chunks of 200 events, then 2 events).
All 19,002 events remain in the original order. No theorem statement is changed.

`PortGeometry` needed three proof-only compatibility edits: explicit beta
reduction before each of the two `Matrix.map_mul` rewrites, and a final `simp`
to close a disjunction left by the older `field_simp`/`ring` combination. Its
successful bounded probe took 10.366 seconds (4.33 baseline: 6.584 seconds).
The failed initial attempt is recorded separately and is not counted as a pass.

`check_sources.py` independently expands the named event-list suffixes, rejects
missing/cyclic/cross-chunk/unused suffixes and checks the original input hashes,
event order, chunk boundaries and byte-reproducible generated modules.
`test_flat_data.py` supplies negative controls for this changed parser.

## Reproduction

Use a new checkout of the probe commit, Python 3.11+, elan and the Python
dependencies pinned in `requirements-probe.txt` (SymPy 1.14.0 and mpmath 1.3.0).
These support source regeneration; Lean checks the resulting witnesses.
From the repository root:

```sh
cd research/lean-multi-host-source
python3 -m pip install -r requirements-probe.txt
lake exe cache get
python3 check_sources.py
python3 test_flat_data.py
python3 verify.py --receipt phase1-receipt.json
```

`verify.py` checks `probe-manifest.json`, runs `lake build` with no compilation
options, and runs `lake env lean ProbeAxioms.lean`. The audit covers the 567
existing declarations in the bounded probe, allowing only `propext`,
`Classical.choice` and `Quot.sound`. It records whether local build artifacts were
absent initially, compiler identity, bundled-library hashes, exact dependency
revisions, dependency source/artifact fingerprints and local artifact hashes.
Run it in a new checkout to obtain a fresh local build. It has no resume mode.
It also supports normal incremental Lake builds, explicitly recording
`fresh_local_build: false` in that case. A fresh receipt requires all 51 local
modules to appear as newly compiled and none as replayed. The verifier imposes
a 45-minute outer command deadline; the separate per-module timing probes used
three times each module's 4.33 baseline as their stop limit. The clean aggregate
build is a reproduction check, not a second per-module performance measurement.

The optional `--lake /path/to/lake` argument selects an installed executable;
it does not alter the child process's environment, stack or Lean options.
`--receipt` only chooses an output file. The package does not require either
option to build.

The initial cache download was denied by this environment's HTTP proxy. A cache
is optional: ordinary Lake can compile the pinned dependency sources instead.
Dependency setup time is reported separately from local-module timings.

At the pinned upstream commit, `.github/workflows/verify.yml` runs the formal
matrix `historical`, `gaussian`, `matrix`, using `lake exe cache get` and
`make formal-<package>-verify`. The Makefile targets use ordinary `lake build`
and `lake env lean` axiom checks. The Phase 1 clean-checkout validation uses those
same underlying build/audit commands for this bounded package. This new package
is not yet wired into that workflow, and no claim is made that the entire
upstream matrix or complete Task B package passed. The formal job currently has
a 45-minute timeout; the full-port estimate must be assessed against that limit.

## Interpretation and next phase

Per-module 4.33 baselines come from the committed fresh Task B receipt. They used
direct Lean invocations; 4.21 measurements use Lake and include its startup cost.
The data-module times include all newly introduced node modules. This is an
approximate performance comparison, especially for subsecond modules.

Checkpoint ratios estimate only the likely computation time of `FrameData`.
They cannot establish that its data representation, proofs, or dependencies will
build on 4.21. The full port may need further same-content data partitioning.
No whole-call theorem, ownership fact, scheduling result, cost result, all-size
compilation theorem or kappa claim is added by this compatibility probe.

The differential-test patch was explicitly deferred by the user and is not
included or run in this phase. Phase 2 and publication require further approval.
