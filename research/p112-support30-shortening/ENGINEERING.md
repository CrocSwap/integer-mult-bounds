# Implementation and verification boundaries

Scope is this package and its three declared immutable inputs. No shared tool,
selected source, frozen input or predecessor module changes. The finite proof
predicate is a complete rank-five mixed minimum of 121 and an orthogonal-frame
root minimum of 122, both greater than the endpoint allowance 120.

## Power of Ten inspection

1. New control flow is structured, without recursion. All loops have bounded
   finite domains. Input/receipt failures raise ValueError; CLI and unittest
   propagate failure. Temporary test copies use scoped cleanup.
2. Primary mixed enumeration uses the inherited 40,000-state bound and checks
   complete rank counts. There are 248 directions, 30,628 line pairs, 58 graph
   vertices, 4,459 four-cliques and 3,136 retained configurations. Direct checking
   enumerates exactly 424,270 quadruples. Frame enumeration has a 2,000,000-state
   limit and a 961-entry stack bound. The separate frame orbit has 2,025 turns,
   each with eight reflections, and fails on capacity overflow or incomplete
   closure. Every vector has eight entries; every configuration has six vertices.
3. Python requires dynamic allocation, so fixed post-initialization allocation
   is a managed-runtime deviation. Live collections are bounded by these fixed
   domains. Inputs are regular files of at most 2,000,000 bytes; there are exactly
   three live input pins. Rank matrices are at most eight by eight, with checked
   128-bit intermediate capacity in the separate integer algorithm. No services,
   solvers, subprocesses or growing output queues are used by direct replay.
4. Functions remain below sixty physical lines after formatting. Separate graph,
   rank, frame and support operations each have one mathematical responsibility.
5. Executable contracts use require/ValueError, not removable Python assertions.
   Tests deliberately use optimized Python. Invariants include exact inventory
   counts, reflection closure, source hashes, integral vertices and strict costs.
6. State is local to replay operations except immutable package/input locations.
   Sources are authenticated before inherited imports; predecessor search order
   follows the package directory, preventing a same-name predecessor checker
   from replacing the local independent implementation. No concurrent writers.
7. Every file read is bounded and checked; hash/JSON mismatches fail. Output uses
   exclusive creation outside the checkout. Exceptions propagate. Standard file
   context managers close output and temporary tests clean up on failure.
8. No eval, generated code, decorators, reflection-based module loading or
   runtime registration. The inherited import path is one explicit fixed package.
9. No unsafe pointers or callback chains. Standard-library dispatch is a Python
   runtime deviation with bounded calls to Counter, Fraction, JSON, itertools
   and unittest. Source identity and exact output are checked, not timing.
10. Ruff plus warnings-as-errors replay and compilation check all new Python.
    The registered manifest runs primary, separate and optimized behavioral
    checks on each relevant change. E402 is narrowly suppressed in verify.py
    because authenticating inherited bytes must precede those imports; the
    strict local lint command enables E402 so unused suppressions also fail.

The standard library allocates internally, and JSON parsing may recurse within
Python's finite recursion limit. Its internals are not instrumented here.
The enclosing two-megabyte bound, fixed semantic inventories and registered
120-second command limits compensate for those runtime deviations. A future
change accepting variable-sized domains must add explicit input/capacity budgets
before extending these routines. No cleanup or warning configuration is changed
in the frozen predecessor to claim compliance.

## Local correction and independent coverage

The first optimized test run caught a real import-precedence error: adding the
predecessor at search index zero selected its same-named independent.py rather
than the new five-row rank checker. The dependency now follows package-local
modules. The witness/rank tests then pass and remain regression coverage.

The separate checker reuses the same E8 reconstruction and written alphabet
classification. Its Gram equations, direct quadruple enumeration, integer rank,
explicit star and reflection frame orbit do not call the primary census
operations. Agreement is additional finite evidence, not independent human
review or proof-kernel verification. The general Weyl-chamber theorem and the
written root/D7 and A2 arguments remain mathematical dependencies.
