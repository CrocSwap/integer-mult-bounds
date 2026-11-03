# Faster complete selected-baseline source authentication

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped implementation-equivalence proof with exact conformance
checks and local performance evidence. The complete captured PR6030 baseline
takes **33.67% less median wall time** through the opt-in adapter. Every one
of the 1,405 manifest files is still opened and hashed. Complete output is
byte-identical to the official command at the recorded main. No new kappa,
mathematical audit, supplier admission or selected-frontier change follows.

The new step reuses directory-prefix validation during one check of a stable
POSIX checkout. It replaces 7,759 component symlink checks by 441 distinct
directory checks and 1,405 separate leaf checks. It removes two redundant
path resolutions per explicit file. All file digests, proof supplements,
inventory comparisons, budget checks and report fields remain. No fact or
digest persists into another invocation. Windows delegates to the original
validator; no Windows speedup or native Windows execution is claimed.

[PROOF.md](PROOF.md) gives the acceptance-predicate argument and scope.
[fast.py](fast.py) is a separate adapter; shared scripts and frozen sources
retain their bytes. [selection.json](selection.json) captures the exact
selected record at main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
The checker and report projection execute from their hash-authenticated
original Python sources. Their scientific claims are cited, not audited here.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/selected-prefix-authentication/fast.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/selected-prefix-authentication/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/selected-prefix-authentication
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/selected-prefix-authentication --check-source-history
```

Other machines may substitute their CPython 3.12 path. The adapter prints the
unchanged `PASS_RESEARCH_BASELINE_BINDINGS_ONLY` report. The verifier prints
`PASS_SELECTED_PREFIX_AUTHENTICATION` in a generated receipt bound to every
package-file hash. It writes no output files. Temporary control trees are
removed on exit. Registered normal and optimized commands run identical checks.

All 1,408 external replay inputs are declared. A Git-free export needs that
roughly 105 MB closure as well as this package. The command reads the scientific
sources for authentication; it does not execute their scientific verifiers.

## Local measurements

The comparison times the actual official command against `fast.py`, including
fresh interpreter startup, complete authentication and JSON output. Both use
`-I -W error -B`, CPython 3.12.15 and the same tree. Five alternating fresh-process
pairs on macOS 27.0.1 arm64 gave:

| Command | Median seconds | Range seconds |
|---|---:|---:|
| Official baseline | 0.191614750 | 0.188641834 to 0.202052708 |
| Prefix adapter | 0.127094625 | 0.126506333 to 0.136955000 |

Official samples are `0.193388625, 0.188641834, 0.191614750, 0.202052708,
0.190051084`. Adapter samples are `0.126886833, 0.127094625, 0.131828959,
0.136955000, 0.126506333` seconds. Zero errors occurred. All ten complete
stdout digests were
`156c34206e1cac9a535d7458ba82c57f9681faad966b45bfda433c0da57b67b8`.
The reduction is `1 - 0.127094625 / 0.191614750`.

The host had 18 logical CPUs and load averages 2.57, 2.28 and 1.87 before
measurement. OS caches were warm; the host was not isolated. These are local
complete-command measurements, not a portable percentage or a multiplication
speedup. The benchmark rejects a changed current selection.

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/selected-prefix-authentication/benchmark.py --rounds 5
```

A separate untimed cProfile run identifies the limiter: 1,405 original
`explicit_file` calls consume 0.217 profiled seconds, including repeated path
resolution and component checks. File reading and SHA256 remain. No timing
threshold is a correctness or CI gate.

## Evidence and limits

The verifier compares complete reports, counts all 1,405 explicit file checks
and 441 unique directory checks, and compares 52 path cases in two traversal
orders. Seven complete-check controls reject corrupted input, certificate,
proof and manifest bytes or newly introduced file/directory aliases. Restoring
each fixture succeeds in a fresh invocation. Three capacity/fallback controls
cover 4,096 calls, depth limits and delegation to the original Windows validator.

The proof assumes a stable filesystem during an invocation. It supplies no
atomic snapshot or protection against concurrent renaming. The optimized POSIX path accepts
only explicit file inventories, at most 4,096 names and depth at most 128.
Its fixture is the captured PR6030 closure. Future selected records and legacy
manifest formats require an explicit successor rather than silent migration.

Independent human and formal proof-kernel review are unclaimed. No selected
scientific cold replay, native suite, Lean or Docker execution was run. All
five selected assumptions remain. Hosted CI evidence belongs in the PR body.

## Credit and overlap

Credit Mihir Srivastava / mihir-s-05 and [PR4463](https://github.com/CrocSwap/integer-mult-bounds/pull/4463)
for the report, Douglas Colkitt and the retained contributors for the source
checker, and the full PR6030/native/caller/compiler lineage for the scientific
files. Prefix memoization and filesystem path facts are classical. The new
contribution is this bounded adapter, equivalence argument, controls and
complete-command improvement. Existing credits remain unchanged.

Arham Tahir / Arham-Tahir64's merged [PR2793](https://github.com/CrocSwap/integer-mult-bounds/pull/2793)
already reuses resolved inventory paths in the later primary-proof membership
pass. That opt-in result is credited prior work. This adapter leaves that
membership pass untouched and instead shares directory checks inside the
explicit-file traversal. No comparison against, composition with or replay
of the earlier candidate is claimed. Its package is cited as prior evidence,
not made into this contribution's deliverable.

The replay-runtime card is refined to this measured authentication bottleneck.
Live PRs, recent handoffs, account work, reservations, merged searches and main
README searches were checked. The overlap helper covered 555 open PRs and
6,596 Discussion records with complete reported pagination; local notes were
sparse. Unpublished work and arbitrary historical diffs remain outside that
coverage. The advance claim is
[here](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19373356).

## Open next questions

- Can a maintained baseline adopt this adapter with a stable-checkout contract
  and matching Windows behavior? Start with full conformance and complete-command
  measurements on Linux and Windows. Portable performance and adoption remain open.
- Can a later selected closure use the same bounded adapter? Capture its exact
  record and complete dependencies, then rerun the controls and benchmark.
  No automatic migration or continuing scope is reserved.

## Verifier constraints

New code has no recursion. Functions are under 60 physical lines. The prefix
map has at most `1 + 4096 * 127` entries; this fixture uses 442 with its root.

Power of Ten rule 3 has a managed-runtime deviation. CPython allocates paths,
dictionaries, integers and JSON during this one-shot check. The fixed input
inventory is 104,799,474 bytes with largest file 7,756,464 bytes; entry and
depth capacities bound new prefix state. The inherited checker reads whole
files and is retained rather than redesigned. A fixed-allocation port would
need a separate implementation. Finite controls and complete normal/optimized
checks exercise these bounds.

Rules 8 and 9 have a bounded adapter deviation. `run_path` executes only pinned
original scripts. Only `explicit_file` is replaced in a fresh checker namespace.
Fallbacks and finite control callables have named local targets and lifetimes.
A static maintained integration could remove this indirection. Warning-strict
normal/optimized runs and in-memory syntax compilation provide available Python
diagnostics; no separate linter or type checker is installed.
