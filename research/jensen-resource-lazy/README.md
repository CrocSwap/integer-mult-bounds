# Authenticate the Jensen package without POSIX resource

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped implementation-preservation proof with finite conformance.
No mathematical audit, new bound or new kappa is claimed.

The retained [PR5614](https://github.com/CrocSwap/integer-mult-bounds/pull/5614)
entry imports `resource` before selecting `--integrity-only`. Consequently,
even that file-authentication command fails on a Python installation without
the POSIX module. This adapter moves the import into `child_limits` in memory.
The entire original integrity check then executes without importing `resource`.
Scientific execution still requests the original guarded child.

```diff
-import resource
 def child_limits():
+    import resource
     resource.setrlimit(resource.RLIMIT_AS, (512*1024*1024,512*1024*1024))
```

The source entry and payload inventory must match their exact SHA256 pins
before loading. Every predecessor file remains unchanged. The original
`authenticate` function still checks the complete package inventory, each
member's bytes, the frozen request and receipts, original evidence and scope
fields. Its original complete integrity stdout is preserved.

## Preservation argument

The transformation accepts one exact source file. It removes its sole
top-level `import resource` and inserts that same import as the first statement
of its sole `child_limits` function. An AST comparison checks precisely that
relocation, including every other function and the complete original dispatcher.
The declared entry contains no other use of the resource binding.

The integrity branch calls `authenticate`, checks its own arguments and prints
its original marker. It never invokes `child_limits`. Removing an otherwise
unused import therefore permits this branch to execute when that module is
absent, without deleting any reachable integrity check.

On ordinary POSIX execution, the added local import obtains the resource
module before the retained `setrlimit` call. The call still receives
`RLIMIT_AS` and the same pair of 536870912-byte limits. Its exceptions still
propagate. The original subprocess still names this guard as `preexec_fn`;
its timeout and all subsequent scientific checks are unchanged. If resource
cannot be imported, the guard raises before its remaining statement. No
unguarded scientific fallback is introduced.

This preservation claim concerns ordinary entry behavior and guard arguments.
It excludes module-global inspection, source line numbers, tracebacks, import
timing and externally replacing the old module's global resource binding.
It does not certify OS enforcement of the limit, scientific correctness or
the availability of the full POSIX subprocess API on other platforms.

## Evidence and reproduction

From the repository root, using standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -B research/jensen-resource-lazy/run.py --integrity-only
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/jensen-resource-lazy/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/jensen-resource-lazy/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/jensen-resource-lazy
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/jensen-resource-lazy --check-source-history
```

Another CPython 3.12 executable may replace the displayed interpreter.
The direct checks print `PASS_JENSEN_LAZY_RESOURCE` and a generated receipt
bound to the package hashes. The registered hook executes both normal and
optimized checks. Every one of the 53 retained files is a declared, pinned
live input, so changes select this package for replay.

The executable checks establish the original missing-import failure and the
repaired complete integrity success with the same import blocked. They also
check the exact AST relocation, identical original integrity output, unchanged
guard arguments, rejection when the guard module is missing and propagation
of a denied `setrlimit` call. Five separate custody mutations reject with
their expected reasons: source, inventory and payload byte changes, an extra
member and a missing member. Two unsupported argument lists still reject.
Relocation to a path containing spaces preserves the complete output.

The verifier does not execute the predecessor's numerical checker. The retained
compiler theorem, hypothetical target profile, numerical outputs and mutation
domain remain PR5614's credited evidence. Native Windows execution, physical
supplier admission, the selected cold replay, Lean and Docker are unrun.
Independent human and formal proof-kernel review are unclaimed.

The new reference code uses bounded source text and a fixed import relocation.
Its dynamic compilation is restricted to the hash-authenticated source, with
the AST difference checked in the verifier. Python allocation, bounded callback
dispatch and AST compilation are managed-runtime deviations from Power of Ten;
this is diagnostic software, not a fixed-allocation physical implementation.
The import interceptor has one special module name and restores the original
hook in `finally`. Temporary custody copies are removed by their context
manager, and argument/stdout interception also restores state in `finally`.
Warning-strict normal and optimized execution supply diagnostics. No separate
type checker or linter was run.

## Source and overlap

The base is canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`,
priority revision 8, selected PR6030. The `portable-replay` card is refined
to this missing-module boundary. Its selected-baseline positive control
passed with `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19363539)
records the same scope. Live open/account PRs, current-main and merged searches,
active Discussions and local reservations were checked. The cached overlap
report covered 438 open PRs and 6414 Discussion records with complete remote
pagination and a complete 8917-record local note inventory at the base.
Arbitrary diffs and unpublished work remain outside that coverage. One recent
account PR cites PR5614 for a different invoice result; this contribution does
not pursue that result's follow-up or recheck it.

## Open next questions

Does the same entry pass on native Windows CPython 3.12? First run both committed
VERIFY commands in a Git-free source export. The missing-module control proves
this import boundary, while actual Windows filesystem and interpreter behavior
remain untested. The structured question is in [TASK.json](TASK.json).

## Credit

Credit Chris R / Clear1nsight for PR5614's complete retained authentication
and scientific entry and hypothetical compiler benchmark. Retain Hexapode,
Ali Romman, thu-nmrc, GamingPuzzled, DreamingOfClouds, zxv, Cao Yifan, Jacob
Alan Sussman, Cinna Davis and the native, compiler, geometry, precision and
analytic contributors credited in that source. Their files and credit lines
are unchanged. The new result is the import-boundary repair and its executable
preservation evidence.
