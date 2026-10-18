# Fail-closed selected-record source inventories

An opt-in successor fixes a source-closure gap in
[`scripts/verify_selected_result.py`](../../scripts/verify_selected_result.py).
An unreadable, unlisted subtree can disappear from its inventory, allowing
preflight to pass despite extra supplier sources. This package preserves the
production checker, frozen inputs, pinned consumers and selected kappa.

The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2946)
records coordination. [TASK.json](TASK.json) declares the changed scope from
`portable-replay`, exact base, overlap and remaining adoption work.
[SOURCES.json](SOURCES.json) pins the predecessor, regression suites and selected
record/manifest/certificate by SHA256 and Git blob ID.

## Reproduced failure

On Linux under an unprivileged account, both supported manifest layouts pass
this synthetic record with an extra source:

```text
supplier/
  nested/proof.txt       listed, readable, correct digest
  unlisted/             mode 000, omitted by Path.rglob
    extra.py            not listed in the manifest

retained check(record)  returns 1/1000
successor check(record) raises PermissionError
```

Direct enumeration confirms that `unlisted/` is inaccessible. Restoring its
permissions makes both checkers reject the extra file. Removing that file
restores success. The actual retained and successor CLIs reproduce these
outcomes in minimal checkout fixtures, including both manifest layouts.
This is a source-inventory completeness failure, not evidence of an incorrect
multiplication certificate or an observed bad upstream supplier package.

## Repair and retained coverage

[check.py](check.py) compiles the exact authenticated predecessor source into
a private module and replaces only `package_files`. It uses an iterative
worklist, context-managed `os.scandir` and explicit metadata reads. Opening a
directory, advancing its iterator or reading metadata can fail. Those failures
propagate instead of becoming missing entries. No partial traversal is accepted.

The predecessor still computes every file digest and requires exact inventory
equality. Its certificate, exact arithmetic, primary-proof, supplement,
historical-context and publication-pointer guards are unchanged. No successful
result or digest is cached across invocations.

Contained regular-file symlinks remain supported and independently hashed.
Directory links, dangling/cyclic links and escaping file aliases retain their
rejections. Target EACCES/EIO failures propagate; only ENOENT, ENOTDIR and ELOOP
are translated to the retained invalid-link diagnostic. Nonregular source
entries, such as FIFOs, are now rejected rather than silently ignored. Empty
real directories remain irrelevant to file equality.

An explicit per-package budget allows at most 1,000,000 descendant entries,
including directories. Exhaustion fails before acceptance. The root is not
counted; the bound also limits the iterative worklist. The selected package
inventory has 1,579 files and passes unchanged.

On a stable filesystem, every real directory discovered enters the worklist,
and each is completely enumerated before its handle closes. Every entry either
yields an admitted regular file, adds a real directory, or fails the check.
Directory symlinks cannot add cycles. A successful traversal therefore yields
the complete admissible file inventory, so the retained exact-manifest equality
cannot overlook an extra regular file beneath an unreadable directory.

## Reproduce

From the repository root, standard library only:

```sh
python3.12 -I -B research/selected-inventory-fail-closed/verify.py
python3.13 -I -B research/selected-inventory-fail-closed/verify.py
ruff check research/selected-inventory-fail-closed/*.py
```

Expected marker on a host supporting all fixtures:

```text
PASS_SELECTED_INVENTORY_FAIL_CLOSED tests=59 skipped=0 selected_files=1579 no_new_kappa
```

The complete manual replay authenticates inputs, checks the current selected
source binding with both engines, and runs:

- All 26 unchanged selected-result, primary-proof and inventory-link test groups
  against each engine. The inherited CLI tests still exercise the frozen CLI;
  the new tests separately exercise the successor CLI.
- Seven new groups covering the unreadable unlisted source, actual CLI failure
  and recovery, twelve injected open/iteration/stat failures across both layouts,
  exact entry-budget boundaries, alias-target access failures, special entries
  and rejection of changed predecessor source before execution.

Permission and symlink/FIFO fixtures explicitly skip where unsupported or where
the account bypasses permissions. Injected traversal errors remain mandatory.
The local Linux runs on CPython 3.12.15 and 3.13.5 had no skips. The initial
regression failed in both layouts before the traversal replacement. The retained
false-success control remains part of the passing replay.

The opt-in CLI retains the original options and success marker:

```sh
python3.12 -I -B research/selected-inventory-fail-closed/check.py
python3.12 -I -B research/selected-inventory-fail-closed/check.py \
  --record certificates/checkpoints/frontier1042.json
```

It preserves the original optimized-CLI refusal. Access failures exit nonzero
without printing the success marker. Like the predecessor, errors may include
a traceback. Source-binding preflight is not a construction replay.

## Scope and implementation limits

Inputs must remain stable during each invocation. This is not a filesystem
snapshot or protection against concurrent replacement, mount aliases or a
malicious writer. File sizes and the inherited JSON/parser work remain under
the predecessor's trusted-local-input contract. Python allocations remain
dynamic; the new traversal bounds entry count, not payload byte size.

All new functions are under 60 lines. Traversal is nonrecursive and its entry
budget is checked on every iteration. Directory handles close on success and
on injected failures. The narrowly scoped `S102` lint exceptions execute
explicit local source bytes, with external predecessor/test bytes authenticated
before compilation. They do not introduce an untrusted-code loading interface.
A separately reviewed source-loader API would be needed to remove that mechanism.

No generic CI replay is registered, matching the separate opt-in preflight
prototype's manual deployment boundary. The source manifest already binds the
full selected inventory; this package does not duplicate all 1,579 source pins.
Production adoption and compatibility migration are separate work. No hosted
CI, other operating system, complete cold replay, supplier admission or new
kappa is claimed.

## Open next questions

Should production preflight adopt this traversal? First review the delta and
migrate the explicit source pins in `selected-binding-coverage-seeda342` and
`selected-dependency-heads-audit`, then replay those checks. Maintainer adoption
and compatibility review block that step. A concurrent-writer contract would
need a real snapshot or descriptor-based design and is not supplied here.

## Credit

Douglas Colkitt supplied the selected-record checker. Mihir Srivastava/PR841
supplied the primary-proof guards; yssite/PR959 supplied inventory-link closure.
Their unchanged regression suites are retained. Arham Tahir/PR2793 supplied the
separate path-reuse prototype and its source-pin migration handoff.

Nick Petalas/PR2921 repaired the related generated-payload inventory, a different
consumer. This contribution applies the completeness requirement to selected
source closure while preserving its supported file aliases. Rohan Arun, Jeremy
Kothe and the full selected supplier lineage retain their construction credit.
New work by Nick Petalas, Apache-2.0.
