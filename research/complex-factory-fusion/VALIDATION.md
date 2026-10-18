# Executed validation

The base is `8bddbee377e2f3ce1f1247196c4b290d55767d20`. Checks ran on
2026-10-13 with CPython 3.14.7, NumPy 2.5.4 and macOS 26.6.1 arm64.
BLAS and OpenMP worker counts were one. The final checks used the existing
project virtual environment. No dependency was installed. The exact interpreter
path and source hashes are in `VALIDATION.json`.

The final source passed the following commands with that interpreter:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python3 -I -B research/complex-factory-fusion/verify.py
python3 -I -B research/complex-factory-fusion/test_package.py
make selected-record-check
```

All three commands returned zero. The primary command matched every field
of `EXPECTED.json`. It took 31.139 seconds in this environment. The maximum
child resident set was 412,450,816 bytes. These are verification resources,
not a multiplication runtime benchmark.

Coverage:

- Exact integer lower-bound certificate and four complete factory maps,
  compared with both the original 87-macro map and PR924.
- Strong 44-operation comparison and all 39,424 one-scale magnitude
  placements in each orientation under the declared source-version policy.
  Small-integer routes are applied outside the factories in both programs.
- Fresh raw constructor extraction, all fourteen window bindings, native
  frame/compensation audit and unchanged emitted-word checks.
- Exact phase lowering of 1,879 fresh edges; 1,231 edge certificates and
  224 endpoint adapters reused from pinned sources, with global phase.
- Ten complete primitive streams, 725 arbitrary columns in each, 492
  restored logical helper columns and all private columns erased.
- Every call and field in five complete 72-call host schedules, data-port
  and endpoint-frame binding, disjoint bank footprints and complements.
- All scalar, operand-read, helper, stock, source/interface, adapter, wrapper,
  bridge, idle, precision, tape and routing terms in the fixed host invoice.
- All ten strict finite guards and the unchanged selected record.

There are 168 new mathematical rejection cases: all 152 single-primitive
omissions, four certificate controls, a climb moved across a live register
use, a primitive with a wrong frame, and ten host defects. The host defects
include a missing call, an alias, a wrong complement, an unbound program,
a missing bridge, stale bank coverage, an unpaid translation, a wrong
bridge sign, a private-family alias and a changed data-port order. The
unchanged native auditor also runs its four retained rejection controls.

The package command took 31.166 seconds. It passes a full `-I -O -B` replay in a minimal path with
spaces, outside the source checkout. It copies only declared sources and
this package. It then rejects two corruptions and preserves two existing
output locations. The inherited assertion-based scripts run in separate
`-I -B` subprocesses, so top-level optimization does not disable their checks.
Generated gzip headers and temporary paths are absent from expected identities.
The committed phase-baseline container retains its original exact certificate.

An initial run with the system Python stopped because NumPy was absent.
The final checks used the existing project virtual environment and passed.
An earlier `/usr/bin/time -l` wrapper returned status one because the sandbox
refused `kern.clockrate`, after the package checks printed PASS. A direct
rerun passed. The final time and memory use Python's `time` and `resource`
APIs. These environment failures are retained in the lane archive.

Not executed: a full cold phase replay of reused edges, the current selected
supplier's cold replay, repository-wide `make verify`, Linux/remote CI, Lean,
or a physical integer-multiplication runtime benchmark. The dedicated-bank
host is the historical raw supplier's host. No optimized-provider transport,
owner search or outer exponent assembly is claimed.
