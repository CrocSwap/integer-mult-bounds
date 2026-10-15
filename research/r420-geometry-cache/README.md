# Cache exact E8 geometry across PR543 mutation checks

**Verification tooling; no mathematical construction or kappa change.** This
opt-in adapter speeds up the unmodified PR543 mutation harness by reusing a
previously validated E8 label/frame calculation for exactly matching inputs.
Every word still receives the predecessor's full scalar, frame-path, dirty
restoration and H1–H5/interface checks.

**Status note:** production `research/e8-bit-r420/code/mutants.py` now ships the
same geometry reuse (`research/r420-geometry-cache-production/`). This package
remains the historical opt-in `cached_xcheck.py` adapter; its pairwise-era
`mutants.py` digest is provenance only.

On macOS arm64 / Python 3.12.3, one sequential, same-input A/B took
**8.239 seconds → 1.273 seconds (6.47× faster, 84.5% less wall time)**.
Both runs started separate processes with empty application caches. The original
and cached runs produced byte-identical diagnostics and equal complete JSON
receipts: all nine negative controls reject for the same reasons and the positive
control passes. OS caches were not flushed. This measures only this mutation
suite, not the full supplier pipeline; timings are diagnostic, not test thresholds.

## Reproduce

From the repository root, Python 3.10+ and its standard library:

```sh
python3 -I -B research/r420-geometry-cache/verify.py
```

Expected first result line:

```text
PASS_R420_GEOMETRY_CACHE original_controls=10 supplemental_checks=20
```

The next line reports freshly measured A/B timings. The command runs one
original/cached pair on the exact same word and unchanged mutation harness,
compares receipts and full diagnostics, then checks twenty cache-specific cases.
`--output /absolute/new/directory` retains both logs, receipts and `RESULT.json`;
the directory must not already exist. Without it, scratch outputs are temporary.
The recorded run is in `evidence/RESULT.json` and the adjacent logs/receipts.

Use the adapter directly with the existing harness:

```sh
python3 -I -B research/e8-bit-r420/code/mutants.py \
  research/r420-geometry-cache/cached_xcheck.py \
  research/e8-bit-r420/data/bitE8mut-r420.json.gz
```

The adapter exposes the same `check(word)` and `Reject` API consumed by that
harness. It returns the predecessor's six-item result; as with the original API,
callers must inspect **all hypothesis and conclusion booleans**, not just absence
of an exception. It is an importable adapter, not a standalone verifier CLI.
`GeometryCache(capacity=2)` also permits an explicitly owned cache for a sequence
of checks. The default holds at most two geometry entries, in memory only.

## What is reused, and why it is sound

`cached_xcheck.py` checks the exact SHA-256 of the unchanged predecessor source
before importing it. It refuses source drift; a later checker must be reviewed
for changed data dependencies before changing this pin.

For the pinned implementation, `Word.__init__` and `labels()` read only these
word fields: `h`, `v`, `R`, `form`, `lines`, `frames`. The cache key is their full
JSON serialization, preserving list order, duplicates and numeric representations.
It is **not a digest**, a filename, an object identity, a dimensions-only key or
an assumed E8 catalogue. Equal keys therefore have equal JSON input values for
every cached calculation. This adapter is scoped to ordinary finite JSON data,
as loaded from the word files, and sequential calls in one process.

On a miss, the original exact constructor and label/frame-closure audit run.
Only successful geometry is retained. The cache stores immutable tuples of the
derived geometry and the label receipt. On every call, including a hit, it
creates a fresh original `Word`, supplies the current complete word, copies the
derived geometry into fresh mutable containers and clears per-word nesting
memoization. It then calls the unchanged `full()` and `interface()` methods.
No scalar execution result or successful whole-word verdict is cached.

The label audit covers exact root norms, pair inner products, even-unimodular
lattice rank/determinant and closure of every listed frame. These obligations
have identical inputs on a hit. Every obligation that depends on the current
gates, starts, finals, retained totals or scatter is rerun. Geometry validated
for a word whose later scalar check fails may be retained: the scalar result is
not part of the cached evidence and cannot suppress the next word's replay.

Returned `Word` objects and receipts share no mutable derived data with the
cache. Changing a caller-owned input is detected by the next key computation;
changing a previously returned result cannot poison the next check. Capacity
eviction causes full geometry validation on the next miss. There is no disk
cache, concurrent-call guarantee, approximate arithmetic or trusted old receipt.

These statements are a code-dependency argument for this pinned finite checker,
not a formal proof of the integer-multiplication theorem.

## Verification and boundaries

The original suite checks its valid baseline plus nine negatives and one positive.
Additional checks compare exact outcomes and derived geometry against uncached
execution, including failure reasons:

- Eight cache-hit corruptions: start, final, A, B, C, D, retained totals, scatter.
- Six geometry changes: h, v, R, form, a label, and an unclosed full frame.
- Repeated failed geometry, a valid reflected E8 geometry, returned-result
  mutation, in-place input mutation, capacity-one eviction and source-pin drift.

The two successful geometry variants also compare the full derived geometry and
all predecessor receipts. Source drift is tested by relocating the unchanged
adapter beside altered predecessor bytes; it must refuse to import.
`make selected-record-check` and staged whitespace validation pass.

Only this new research package changes. No existing verifier, manifest, selected
certificate or `upstream/` byte is edited. The complete repository suite, selected
cold replay, hosted invoices, moment engines, Lean and remote CI were not run;
this is an isolated, optional acceleration of one existing finite check.
The inherited all-size, compiler, physical/common-label, hosting, precision,
tape and analytic assumptions remain untouched. No new kappa or end-to-end
supplier speedup is claimed.

## Provenance and credit

Base main: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
PR543 supplier: `2065fe4f72a914d907f1046603f5a36f17018535`.
`SOURCES.json` pins the exact three execution inputs by SHA-256 and Git blob.
The selected PR626 composition still uses conditional
`kappa=51110230636731/31250000000000000`.

**Eumemic** supplied PR543's `xcheck.py`, mutation suite and R420 word, with
substantial Anthropic Claude assistance. The original geometry, construction,
dirty interface and mutation coverage are theirs. Credit also remains with
PR493, Dylan Crow's E8 checker/decoder work, Jacob Sussman's E8 unit, Zhihao
Chen's scalar interface, DreamingOfClouds' supplier/pricing work, and the complete
lineage in [`research/e8-bit-r420/NOTICE.md`](../e8-bit-r420/NOTICE.md).

PR452 (Aman) studies older PR358 prefix and arithmetic reuse; PR662 accelerates
complex Clifford helper checks; PR667/672 concern interval arithmetic. Those
distinct performance contributions are not imported or independently reviewed
here. PR691 is our separate circuit contribution and is not a dependency.
The seed-91 claim and overlap checks are recorded in `CLAIM.md`.

Prepared for **@mtpsl with substantial OpenAI Codex assistance** in implementing
the cache, analyzing dependencies, testing and packaging. No independent human
review is claimed. New files are Apache-2.0 under the repository's LICENSE;
predecessor attribution and files are preserved unchanged.
