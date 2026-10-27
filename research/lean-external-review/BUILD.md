# Lean 4.21 reproduction

**Fresh full port validation passed.** These are the normal reproduction
commands; recorded receipts and the conditional CI estimate are in [VALIDATION.md](VALIDATION.md).

Start from a clean checkout of the port commit being reviewed. Record
`git rev-parse HEAD`. Install Git, Python 3.13 and elan using upstream's normal
setup. Each project selects its compiler through `lean-toolchain`; no external
resource settings, special compiler flags or environment overrides are used.
The verifier inherits the host's OS stack limits unchanged and records them
before and after the run. An 8 MiB limit is not assumed: host defaults differ.
The receipt cannot determine whether a caller changed limits before launch;
the reproduction commands and workflow must use their ordinary environment.

From the repository root:

```sh
python3 -m pip install -r research/lean-external-review/requirements.txt
cd research/lean-multi-host-source
lake exe cache get Mathlib.Data.Matrix.Mul \
  Mathlib.Algebra.BigOperators.Fin Mathlib.Tactic.FieldSimp \
  Mathlib.Tactic.Ring Mathlib.Tactic.NormNum
cd ../..
make formal-pr442-verify
```

The Make target defaults to `LAKE=lake`. A local installation can select its
Lake executable with `make formal-pr442-verify LAKE=/path/to/lake`; this is
executable selection only, not a compiler flag or environment override.

These are the commands used by the added `pr442` entry in upstream's existing
formal CI matrix. That job retains its 45-minute limit. The fresh CI-repair
Make run took 16 minutes 58 seconds. Its conservative projection is 34 minutes
9 seconds, qualifying under the revised 35-minute target with the explicit
cache/setup assumptions in [VALIDATION.md](VALIDATION.md). This is a timing
estimate, not an observed GitHub Actions run.

The cache request selects the five imported Mathlib modules and their full
dependency closure; it does not download unrelated Mathlib modules. These are
cache selections, not compiler flags. The ordinary build remains `lake build`.
The official Mathlib cache contains only pinned external dependency artifacts.
It must not supply local contribution artifacts. If the cache is unavailable,
ordinary Lake can compile the dependencies from source; the additional time
must be reported separately and included in any cache-free CI projection.
The current managed environment blocks the official cache endpoint, so local
validation may reuse fingerprinted external dependencies built from source.
That does not establish cold-cache CI runtime.

For a complete local receipt set in a new directory outside the checkout:

```sh
python3 research/lean-external-review/reproduce.py \
  --receipt-dir /tmp/pr442-review-receipts
```

This requires `research/lean-multi-host-source/.lake/build` to be absent or
empty. Use a new clean checkout if local project artifacts already exist.
Pinned external artifacts in `.lake/packages` may be reused and are
fingerprinted. `--lake` optionally selects the Lake executable; it does not
change compilation or resource settings. No resume mode is offered.

The reproduction runs inventory validation, all literal source checks, the
flat-data parser mutation checks, a fresh Lake build and the five separate
axiom inventories. The Task B inventory has 931 declarations and Task A has
21. The nine historical third-party source snapshots are excluded from
compilation and axiom auditing, while their unchanged bytes remain hashed.
The differential test is delegated separately and is not reported here.

The canonical completed-build receipt is `validation/lean421-ci-fix-fresh.json`.
The strict verifier requires its PASS and exact current source bindings. During preparation only,
`verify_package.py --allow-pending-port` checks an unfinished inventory and
reports `PENDING_PORT` when the fresh receipt is absent. With a matching fresh
receipt it performs the normal PASS checks. A reviewer may validate a new local run
using `verify_package.py --build-receipt /tmp/pr442-review-receipts/lean421-fresh.json`.

Historical `replay.py` scripts and Lean 4.33 receipts explain earlier work;
they are not the supported current reproduction route.
