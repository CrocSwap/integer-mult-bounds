# Current-source imports in the isolated unittest runner

The isolated test runner now executes current source despite preexisting stale
default-import bytecode. Previously, a matching timestamp or unchecked-hash
cache could make its public CLI report success for a numeric check that fails
from the current source. This is a verification-tooling result. No mathematical
certificate bypass, supplier admission or new kappa is established.

## Result and correction

The source-bound [differential replay](verify.py) retrieves the original runner
at main `b3f3ee0392b71b118fd086a6eaf6b4cab54ef455` and checks its SHA256 against
[SOURCES.json](SOURCES.json). In disposable copies, it compiles a helper with
`VALUE = 2`, then restores equal-length current source `VALUE = 1` with the same
timestamp. The real unittest expects 2. For both cache modes, the original
runner reports `PASS all 1 test modules`; removing only the cache makes that
same source fail with `AssertionError: 1 != 2`. Clean current source with value
2 passes. The successor fails with current value 1 whether the stale cache is
present or absent. Both source and stale-cache bytes remain unchanged by replay.

`scripts/run_isolated_tests.py` now starts each unittest child with `-B` and an
explicit `-X pycache_prefix` under its existing private completion directory.
Historical wrappers receive a separate namespace before importing shared
tooling. Their receipt-producing unittest child uses the same `module_command`
policy. Each namespace is distinct, and the owner removes its entire directory
after workers finish or cancellation cleanup returns. Inherited external cache
prefixes are overridden without modifying the parent environment.

Discovery arguments, sorted receipts, completion checks, scheduling and process
ownership remain intact. The historical tooling-ledger adapter admits the new
runner digest but still restores its authenticated original for that historical
check. Frozen inputs, predecessor evidence and the selected record are unchanged.

## Reproduce

Use a full-history checkout, Git and CPython 3.12. No third-party modules are
required. The registered hook runs the differential and seven public-CLI
regression groups with explicit timeouts:

```sh
python3.12 -B scripts/research_package.py --package research/isolated-test-bytecode --check-only
python3.12 -B scripts/research_package.py --package research/isolated-test-bytecode
```

Expected markers are `PASS_ISOLATED_TEST_BYTECODE_DIFFERENTIAL` and
`PASS_REGISTERED_RESEARCH_PACKAGE research/isolated-test-bytecode`.
To run the new and inherited runner checks directly:

```sh
python3.12 -W error -B -m unittest discover -s tests -p 'test_isolated*.py' -v
python3.12 -W error -B -m unittest discover -s tests -p 'test_historical_check.py' -v
python3.14 -W error -I -O -B tests/test_isolated_test_bytecode.py -v
python3.14 -W error -I -O -B research/isolated-test-bytecode/verify.py
```

The new groups cover timestamp and unchecked-hash false greens, checked-hash
invalidation, inherited external prefixes, distinct concurrent namespaces and
their removal after success/failure, plus both historical interpreter boundaries.
The historical regression uses the real runner routing branch and a small
synthetic wrapper. Existing historical-completion tests exercise the actual
overlay authentication, artifact-mutation and completion checks separately.
Local verification and environment details are recorded in [TASK.json](TASK.json).

## Scope and engineering decisions

This is the `portable-replay` card, priority revision 5, narrowed from the
verifier-engineering picker's two suggestions. The initial runtime profile
identified path resolution already covered by PR2787; that work was not repeated.
The [canonical discussion](https://github.com/CrocSwap/integer-mult-bounds/discussions/2988)
records the concrete claim and final evidence.

Build the Lever led to the rerunnable old/current CLI comparison. Prove It Works
led to observed numerical verdicts and owned-directory cleanup checks. Power of
Ten kept the production change to one direct argument helper and its two callers.
The following deviations remain bounded to this change:

- Rules 2 and 4: the existing `run_modules` function remains longer than 60 lines
  and its worker polls until completion or cancellation. Splitting its shared
  launch/cancellation state or imposing a new test-duration policy would expand
  this import fix. Namespace count is bounded by the input module count; existing
  process ownership and cleanup tests remain the control. Any future worker
  lifecycle refactor must preserve those tests and set its own timeout contract.
- Rule 3: Python and unittest allocate dynamically. The new production state is
  one path per ordinary child, plus one per historical wrapper, under the already
  owned temporary root. `-B` prevents automatic cache writes; marker fixtures
  verify cleanup. A lower-level implementation would need its own memory policy.
- Rules 8 and 9: constant synthetic Python fixtures and unittest dispatch are
  required to reach the actual import boundary. The differential executes only
  the SHA256-authenticated baseline and live runner, with twelve bounded CLI
  calls. It is not a general code-transform or dynamic plugin mechanism.
- Rule 10: local checks use `-W error`, normal and optimized interpreters, and
  syntax compilation. No standalone static analyzer was available. Additional
  platform checks belong to hosted CI; no repository-wide lint change is made.

Fresh imports recompile modules and may increase startup cost. No speedup or
whole-suite runtime claim is made. The guarantee covers default source imports
in the named interpreter boundaries. Separately launched Python processes from
test bodies, custom loaders, explicit bytecode execution, hostile code and
concurrent source mutation remain outside scope. No complete selected cold
replay, native supplier, Lean proof or independent human review is claimed.

## Open next questions

Which actual tests launch source-bound Python descendants without a fresh cache
boundary? Pin one concrete test and child command, then reproduce a benign
numeric source/executed-value difference before changing it. This matters because
the parent's `-X` flag does not automatically protect arbitrary descendants.
The missing input is a named command chain with its own fixture, not a new global
policy. [TASK.json](TASK.json) retains the structured question.

## Credit

PR2553 and its retained
[bytecode-isolation note](../../docs/research/bytecode-replay-isolation.md) supply
the earlier registered-interpreter mechanism and explicit child-process handoff.
The [frame-closure successor](../frame-closure-child-isolation/README.md) closes
a different caller tree; neither result is claimed here as new. Credit ywz65 and
the retained replay/native contributors for that lineage. The original isolated
runner and subsequent scheduling, cancellation, historical-overlay and completion
work retain their contributor credit, including Douglas Colkitt, ywz65 and Dennis.
Prepared by Nick Petalas. Assistance and review limits are recorded in TASK.json.
Apache-2.0.
