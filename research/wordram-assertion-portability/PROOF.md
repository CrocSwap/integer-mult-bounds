# Preservation of the fixed bounded-kernel checklist

The claim is a scoped implementation-preservation proof. It concerns the exact
source closure in SOURCES.json, CPython 3.12, and the normal and `-O` commands
in VERIFY.json. It supplies no new arithmetic theorem or independent scientific
acceptance of the predecessor.

## Assertion lowering

For each parsed statement `assert test, message`, replace just that statement by

```python
if not test:
    raise _imb_certificate_assertion_error(message)
```

Omit the constructor argument when the assertion has no message. The injected
name denotes the built-in AssertionError class. The parser rejects source that
already contains the reserved name, so source code cannot capture the injected
binding. The fixed sources contain no operation that mutates that binding.

The replacement evaluates the predicate once and tests its truth value in the
same position. A true predicate skips the message. A false predicate evaluates
the message once, then raises the same exception class with the same arguments.
An exception from evaluating either expression propagates in the same way.
In particular, no-message and explicit-None-message assertions stay distinct.
Surrounding loops, handlers, functions and statement order are unchanged.
Ordinary Python assertion execution therefore agrees with this replacement.
The compiler retains an explicit conditional raise under `-O`.

The transformation iterates over the parsed tree and replaces statement-list
members of type Assert. It rejects a result containing any remaining Assert.
The receipt records each source line and column, including multiple assertions
on a line. The authenticated closure contains exactly 55 sites. No assertion
is removed without its explicit replacement.

## Entry and import boundary

The original entry point has one capability guard that rejects optimized
Python before any scientific work. The adapter recognizes its exact syntax
and error message and replaces its condition by False. It requires exactly
one `__debug__` reference in that entry and none in imported source modules.
This removes only that refusal. All nine entry-point certificate assertions
receive the transformation above.

Before execution, read and authenticate every original package file against
both the publication source pins and the original MANIFEST.json. The closure
has 33 files, including that manifest. The original entry's own inventory,
hash and retained-result checks still execute. Frozen bytes remain unchanged.

Every imported source module uses a loader that compiles its authenticated
bytes directly after assertion lowering. The loader does not read bytecode
caches. A clean-interpreter guard rejects preloaded source modules. The final
module-inventory check requires every Python source except the separate NTT
test module, which the unchanged subprocess checklist executes. The NTT
implementation and test module have no bare assertions; their unittest checks
remain method calls under optimization.

The entry's single NTT subprocess is intercepted at its explicit run boundary.
The wrapper checks the exact original argument list, working directory and
check=True contract. It propagates the requested optimization level, removes
inherited optimization/path overrides, supplies a fresh bytecode-cache prefix,
adds a 180-second limit and requires the complete eight-test success report.
It runs the same unittest discovery domain. No test is filtered or replaced.
Unexpected commands fail. Nonzero exit, timeout or an incomplete report fails.

## Complete preservation check

Each invocation first runs the original normal entry point with a fresh
bytecode-cache prefix. It then runs the adapted entry at the invoking
interpreter's optimization level. Compare the entire parsed output object
after removing just the `seconds` clock field. This includes all reported
check counts and the full instruction histogram. The original whole-program
result comparison also remains active inside the adapted entry.

Normal and optimized executions perform the same complete checklist. Finite
evidence compares eight assertion-evaluation fixtures at compiler levels
0, 1 and 2. Those 24 comparisons include lazy messages, side effects,
missing versus explicit None messages, loop failure, nested functions and
exception handlers. Five boundary controls reject changed source bytes,
oversized input, a reserved binding, an unexpected guard and a missing guard.
Four additional controls introduce wrong results into actual loaded components
and require their retained assertions to fail. They exercise the RAM residue,
circuit, complete-program digit and fixed-point recovery paths. They do not
claim that every assertion has a separately falsifying fixture.

All controls finish with the original module bindings restored. Finally,
reauthenticate the complete original source closure. A generated stdout receipt
binds the new package files and therefore the source manifest by SHA256.

## Limits and implementation constraints

The equivalence argument concerns the fixed code, its executed checklist and
ordinary assertion effects. Traceback formatting, debugger/coverage line events,
code-object identity, frame introspection, AST layout and timing are outside
the claim. It is not a general Python source transformer or an execution
sandbox. The AST guard and import inventory deliberately reject changed sources.
Only full normal and `-O` source replays are registered; level 2 has synthetic
assertion-semantic coverage, not a claimed complete source replay.

New functions are below 60 physical lines. Inputs are limited to 64 source
rows, one MiB per source and 30,000 AST nodes at depth at most 64. The original
fixed numerical domains and interpreter budgets stay unchanged. Subprocesses
have 180-second limits and each registered invocation has a 240-second limit.
There are no new retries or background jobs. The CLI accepts only an existing
scratch-directory path. Temporary cache directories are scoped and removed;
import hooks, search paths and newly imported source modules are restored on
success or failure.

Power of Ten deviations are explicit. Python allocates managed ASTs, integers,
fractions and containers. The source whitelist and finite bounds constrain
these live objects; no fixed-allocation or allocator-internals claim is made.
The AST compiler and import protocol are required metaprogramming here. Their
inputs are hash-bound, transformation sites are enumerated, and execution
targets are the fixed module closure. Standard AST location/compiler routines
use bounded library recursion after the depth check. The retained predecessor
circuit evaluator has its existing fixed small-tree recursion; frozen source
is not rewritten beyond the stated assertion transformation. This adapter
does not expand its circuit domain. Callback dispatch is limited to the import
loader, one checked subprocess boundary and four local fault controls. Warning-
strict normal and optimized replays supply interpreter diagnostics. No external
static analyzer or proof kernel was run.
