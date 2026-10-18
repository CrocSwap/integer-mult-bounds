# Verification design and bounds

Build the Lever led to a replayable full census and weight-cover certificate.
Prove It Works led to checking actual cuts, rational direction ranks and the
complete orbit transcript, including a new signed-Gram symmetry obligation.

The C++ code is derived from the pinned PR3161 implementation, rather than a
claimed code-disjoint census. Its original finite RREF enumeration, merge sort,
union-find and dual-code oracle are retained with explicit capacities. The new
rank path uses structured loops and checked 64-bit integer elimination. No
recursion is introduced. All exceptions propagate to a nonzero CLI status.

The native limits are 112 live lines, 248 directions, twelve generators,
788,035 RREF matrices, 776,805 nonempty masks, 159 representatives, 511
nonzero characters, at most three independent restricted character words,
and eight rational pivots. A rank reduction bounds stored coordinates by
10^9 before another multiplication. Intermediate absolute values are at most
2*10^18. Exhaustion fails. The two census budgets are exactly eight and ten;
orbit prefixes are allowed only as diagnostics and rejected by the acceptance
parser. The rank CLI accepts at most eight catalogue indices.

Python bounds are fixed by these same inventories: at most 1,200 Weyl rays,
eight reflections per ray, 28 six-node parabolics, 512 binary-span members,
4,795 weight multisets and at most 126 quotient subsets with 81 assignments
each. Public weight arguments are validated. The only open-ended path is a
caller-chosen filesystem location; replay work must use a new external directory.
Source reads have a two-megabyte capacity. Native subprocesses have explicit
timeouts. The generic replay additionally bounds command and process-group lifetime.

Rule 3 deviation, managed allocation: Python and the C++ standard-library sort
and initialization allocate objects. Fixed-capacity native arrays and reserved
flat vectors bound scientific work; Python collections have the finite limits
above. Files/processes are scoped to the external work directory and exceptions
close their streams. There is no sustained service phase. A move to a fixed-memory
embedded runtime would require replacing these managed collections.

Rule 9 deviation, language/runtime dispatch: Python arithmetic uses the standard
Fraction and collection implementations. Targets are fixed standard-library
operations and the source-bound local modules. There are no plugin callbacks,
dynamic code generation, eval or exec. The independent rational oracle and
malformed-input controls check this boundary; a native replacement would need
the same literal semantic controls.

Diagnostics use the native compiler's Wall, Wextra, Wpedantic, Wconversion,
Wsign-conversion and Wshadow warnings, all as errors, on every build. Python
replay uses warnings as errors and Ruff's functional, import, upgrade, complexity
and path checks. Ruff's optional documentation/annotation/package-layout policies
are outside this standalone-script contract, as are its preference for assigning
exception strings to temporary variables and its heuristic warning on a
checked argument-array subprocess call. No local suppression is added to code.
Exact commands and environment are recorded in CHECKS.json.

All functions stay within sixty physical lines in their repository formatting.
Python assertions are not used for acceptance, so optimized execution retains
every check. Imported vendor files are immutable provenance and are not executed
by the mathematical verifier. The repository's generic metadata and byte
publication checks are separate from the mathematical replay.
