# Exact bitmaps speed up the complete T37 owner audit

**Verification tooling; no new kappa or circuit.** This opt-in adapter makes
the selected T37 independent owner audit **1.17–1.19× faster** on the measured
Linux host, with about **22% lower peak resident memory**. It represents each
occupied residual-cell set by an exact nonnegative integer bitmap. Every
original predicate, all 167,832 helper roles and the complete original receipt
are retained. The original checker, T37 wrapper and default commands are
unchanged on disk.

Five alternating fresh-process pairs per interpreter measured:

| CPython | Reference wall median | Bitmap wall median | Speedup | Reference / bitmap peak RSS median, KiB |
|---|---:|---:|---:|---:|
| 3.12.3 | 5.179287 s | 4.351544 s | 1.190× | 296,612 / 230,396 |
| 3.14.4 | 3.915432 s | 3.339163 s | 1.173× | 301,832 / 235,136 |

Each timed process includes imports, exact source admission, immutable archive
input preparation, input reading, the full original wrapper, its six original
negative controls and eight omitted-edit controls, complete receipt comparison,
output and serialization. All 20 timed processes match the original maintainer
receipt. Timings are descriptive, not a pass threshold or a whole-frontier
speed claim. The host was not isolated and OS caches were not flushed. Raw
samples, child CPU time, process peak RSS and source/code hashes are in
`evidence/benchmark-python312.json` and `evidence/benchmark-python314.json`.
The preliminary in-process pilot is excluded from those measurements.

## Reproduce

From the repository root, using Python 3.11+ and its standard library:

```sh
python3 -I -B research/t37-slice-bitmaps/verify.py
```

Expected: `PASS_T37_EXACT_OCCUPANCY_BITMAPS: complete original receipt; 167832 roles; 14 inherited controls; no new kappa`.
This runs both complete engines, compares every original receipt field,
replays the occupied-set representation, exercises the additional differential
controls, and compares the complete new verification receipt to EXPECTED.json.
`--output /new/path --receipt /new/receipt.json` retains all evidence. The
source T37 wrapper uses assertions and rejects `-O`; that behavior is retained.
No network, C++ build or third-party Python module is required for this stage.

```sh
python3 -I -B research/t37-slice-bitmaps/test_package.py
python3 -I -B research/t37-slice-bitmaps/adapter.py --output /tmp/new-t37-audit
python3 -I -B research/t37-slice-bitmaps/benchmark.py --pairs 5 \
  --output /tmp/new-t37-benchmark.json
```

The package tests contain eleven admission/failure controls. The adapter
defaults to bitmaps; add `--engine reference` for the unchanged set engine.
Both arms use identical pinned inputs. `--inputs /prepared/path` accepts a
previously materialized copy only after checking all five immutable input
hashes again. The benchmark requires POSIX process resource accounting and
refuses more than five pairs. Fresh outputs are required. Its expected marker
is `PASS_IDENTICAL_T37_OWNER_AUDITS`, followed by the measured ratio.

## What is preserved

Only three blocks inside the pinned `check_roles` function change: the empty
occupied-set representation, disjoint interval union, and final prefix/count
test. The original range construction is retained to preserve malformed-input
behavior. Capacity checks precede integer shifts. Empty sets, overlaps,
arbitrary interval placement, gaps and cardinalities have exact bitwise
counterparts; see PROOF.md for the induction argument.

Whole-helper widths, physical family identities, strict bridge-aware windows,
active-pair exclusions, duplicate helper/family checks, all 73-axis charts,
permutations, pending-axis binding, inventories, idle profile, rank deficit,
prefix reserve and row reserve execute through the original code. There is
no acceptance cache, skipped role, floating approximation or random fingerprint.
The temporary import hook is confined to an isolated single-threaded process
and is restored after the wrapper returns or raises.

The complete receipt covers **333 calls, 167,832 roles, 9,628 distinct charts,
74,592 slice-prefix checks, 779 prefix bits and row coefficient 17,495**.
All fourteen original controls retain their original reasons. Only the eight
machine-specific input-path keys are normalized to fixed logical names, after
their complete exact hash inventory is checked; no receipt field is omitted.
Saved runs retain the raw original receipt and a separate adapter identity.

Additional evidence includes:

- A separate set/bitmap occupancy replay at all **167,832 role boundaries**,
  with **1,258,074 cell insertions** and all 74,592 final prefix checks. Actual
  masks need at most 48 bits. A deterministic stream digest records the result.
- **Sixteen** changed owner inputs rejected by both engines with identical
  exception type and message, including negative/huge/float offsets, invalid
  widths, early/middle/late capacity failures, overlaps and a prefix gap that
  leaves the occupied-cell count unchanged.
- **Four** equivalent inputs accepted with identical complete receipts:
  original, reverse and seed-94 shuffled role orders, plus a Boolean zero
  offset accepted by the original checker. The adapter does not silently
  strengthen that original input behavior.
- All **51,190** bounded interval cases and **65,536** sixteen-position masks
  for independent prefix equivalence. A deliberately weakened cardinality-only
  prefix check accepts an invalid shifted prefix, which the proper checker
  rejects.

## Provenance and boundaries

OS assignment seed **94**, verification-engineering track, drawn at
2026-10-13T15:48:37.259894+00:00. It fixes the differential permutation and first
benchmark ordering. Research base:
**407d52ff15b2217b6e22bce44728b4c3907b6515**. Refreshed upstream
**8bddbee377e2f3ce1f1247196c4b290d55767d20** has identical bytes for all ten
consumed source inputs and retains selected PR942's conditional
`1661960547713947 / 10^18`.

SOURCES.json pins the source checker/wrapper, original witnesses/notices,
retained receipt and two replay archives, plus five implementation files.
Five individually pinned data members are read without extracting archive
paths or executing archive content. Exact archive/input bytes remain immutable
provenance inputs. This pass does not regenerate those archives. The native
local word and its original replay come from the accepted T37 archive; the
original eight-replica parent and phase data come from the accepted PR799
archive. No prior completed replay directory is required on the caller's disk.

This is one independent admission stage. Fresh native supplier construction,
whole-hosted emission, global invoice, exact moments, outer assembly, selected
cold replay and full `make verify` are outside its executed or measured scope.
The archived native replay is hash-bound evidence, not a claim of a new native
run. All inherited all-size/compiler, realization, hosting, precision/tape,
analytic and bit H1-H5 obligations remain. Finite verifier success does not
formally prove the multiplication theorem or establish a new kappa.

See VALIDATION.md for executed checks, CLAIM.json for scope selection and
NOTICE.md for contributor attribution and substantial OpenAI Codex assistance.
