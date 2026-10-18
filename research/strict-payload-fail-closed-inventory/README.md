# Fail-closed inventories for strict payload comparison

This opt-in successor repairs a filesystem coverage gap in commdata2338's
[PR2040 comparator](../strict-replay-payload-comparison/README.md). It changes
only directory inventory in a private, source-authenticated module. Frozen
predecessors, selected evidence and immutable source hashes remain unchanged.
No supplier execution or new kappa is claimed.

## Reproduced failure

On Linux, CPython 3.12.15 and 3.13.5, an unprivileged account can place different
`certificate.json` files under `reference/private/` and `run/private/`, then
remove both subdirectories' permissions. The retained CLI exits 0 and prints:

```json
{"counts": {}, "equivalent": true}
```

`Path.rglob` omits inaccessible subtrees. The files are absent from both
inventories, so complete payload comparison never reaches them. With only one
subtree inaccessible, the retained CLI reports missing/extra files instead of
an access error. Restoring permissions exposes the differing certificate.
These are synthetic filesystem fixtures, not evidence of a bad supplier result.

The new CLI exits 2 on every such access failure, prints `INVALID_COMPARISON`
to stderr, and creates no `--out` report. After permissions are restored, it
still distinguishes changed proofs from equivalent JSON formatting.

## Change and verification

[compare.py](compare.py) compiles the exact SHA256/Git-blob-authenticated
predecessor source and replaces only `inventory`. It uses an iterative worklist,
context-managed `os.scandir`, and `entry.stat(follow_symlinks=False)`. Opening,
iterating and reading metadata may each fail; all those errors propagate to the
retained CLI's input-error handler. It does not infer absence from an I/O error.

Accepted trees contain real directories and regular files. Symlinks, dangling
links and special files are rejected. Rejecting special files tightens the
predecessor, which silently ignored them. Empty directories remain irrelevant
to regular-file equivalence. An explicit budget permits at most 1,000,000
descendant entries per input tree, including directories; exhaustion is an input
error, never partial success. The root is not counted. This also bounds the
worklist without recursion.

The parser, typed numbers, complete gzip payloads, relocation rules, timing
policy and difference diagnostics are unchanged. The successor does not import
the separate paired-walk or large-integer adapters.

[verify.py](verify.py) checks all 12 external inputs, replays the complete
retained audit and requires its full canonical receipt to match. It additionally
materializes both complete 105-file corpus trees and requires exactly 105
`bytes` results from both inventories. Six new test groups and all nine retained
groups cover:

- Actual optimized CLI processes with one or both nested directories unreadable,
  no partial report, a readable proof difference and an equivalent-format control.
- Twelve injected failure cases across reference/run, open/iteration/stat and
  EACCES/EIO. Iteration fails after a real entry, and opened handles must close.
- Exact entry-budget acceptance/exhaustion, missing/extra/changed files,
  invalid roots, symlinks, FIFOs and changed-source rejection before execution.

The real permission fixture skips only where POSIX permissions are unavailable
or the account bypasses them. Injected errors remain mandatory. On the local
Linux account, no tests skipped. The inherited corpus audit retains its 39
adverse witnesses and 22 deleted-timing controls. Its small retained CLI test
still invokes the frozen CLI; the new filesystem CLI controls invoke this
successor directly.

## Reproduce

From the repository root, Python 3.12 standard library:

```sh
python3.12 -B scripts/research_package.py --package research/strict-payload-fail-closed-inventory
python3.12 -I -O -B research/strict-payload-fail-closed-inventory/verify.py
ruff check research/strict-payload-fail-closed-inventory/*.py
```

Expected marker:

```text
PASS_STRICT_PAYLOAD_FAIL_CLOSED_INVENTORY files=105 retained_false_equivalences=39 timing_rejections=22 test_groups=15 no_new_kappa
```

The standalone CLI retains the predecessor's options:

```sh
python3.12 -I -B research/strict-payload-fail-closed-inventory/compare.py REF_DIR RUN_DIR --out /tmp/comparison.json
```

Exit 0 means equivalent under the explicit payload policy, 1 means a payload or
inventory difference, and 2 means configuration/input-access failure. Source
pin failures stop before comparison. Use this only for generated payloads,
never to relax immutable source authentication.

## Scope and credit

The inputs must remain stable during enumeration and file reads. This is not an
atomic filesystem snapshot or protection against concurrent replacement,
symlink races, mount aliases or a malicious writer. It does not bound payload
sizes, repair inherited parser recursion/resource limits, integrate the other
successors, or establish replay execution authenticity. No Windows/macOS or
hosted CI execution is claimed. No selected cold replay was needed or run.

The inventory itself is nonrecursive and entry-bounded. Python allocations
remain dynamic, bounded here by the entry budget and filesystem path lengths;
complete payload parsing retains the predecessor's resource contract. The two
specific `S102` lint exceptions cover only execution of authenticated retained
source bytes, avoiding stale bytecode. Replacing this mechanism requires a
reviewed source-loading interface, not a normal cached import. No general
untrusted-code loader is introduced.

Base canonical main is `5a0dc2c0f4685b02bef7776bc196c7c1231cbac1`, priority
revision 5. The task is `portable-replay`, refined to directory-enumeration
coverage. [TASK.json](TASK.json) records assignment, overlap and next questions;
[SOURCES.json](SOURCES.json) pins exact dependencies. The canonical thread is
[Discussion 2919](https://github.com/CrocSwap/integer-mult-bounds/discussions/2919).

Credit commdata2338 for PR2040 and its full audit, Josie Elliston for PR1824's
portability comparator, Maxime Fleury and Antoine Olivier for the gzip/payload
convention, and Rohan Arun, Jeremy Kothe, Douglas Colkitt and the retained
supplier/archive lineage. ywz65's PR2693 addresses paired payload traversal;
Arham Tahir's PR2803 addresses large integers. Neither repairs this inventory
boundary or is imported here. New work by Nick Petalas, Apache-2.0.

## Open next questions

Should a future replay wrapper adopt this inventory boundary together with its
chosen strict comparator? First specify stable-tree ownership and run the same
CLI failure controls against that wrapper. Adoption needs caller/source-pin
review and is outside this opt-in contribution. A concurrent-writer contract
would additionally require a real snapshot or descriptor-based design; this
package does not claim to supply one.
