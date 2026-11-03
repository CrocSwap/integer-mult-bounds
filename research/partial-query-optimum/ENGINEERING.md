# Implementation bounds

The exit predicate is a proved exact acquisition reduction, a bounded
constructor and certificate checker agreeing with exhaustive subset optima,
followed by one focused publication. The autonomous local run playbook was
used. Build the Lever led to the reusable optimizer and certificate checker.
Prove It Works led to literal subset and vector-set oracles and actual CLI
replays, rather than inference from certificate self-consistency.

## Code inspection

The scope is optimizer.py and verify.py. All control flow is structured,
without recursion, dynamic code generation, network access, mutable global
caches or background tasks. Optimizer entry points validate width at most
256, at most 4096 queries and 256 target vectors, integer costs in
0..10^12, target inclusion in the query span, and codimension at most four.
Booleans are rejected as integer inputs.

There are at most 67 candidate subspaces. Producer span-extension layers
number at most five and contain at most 67 canonical bases; each tries at
most 15 new vectors. The independent checker enumerates at most 16 pivot
sets and at most 16 free-entry assignments per set. A subspace vector set
has at most 16 elements. Per-candidate elimination retains at most 256 rows.
Dual construction reduces 256 ambient unit vectors. Input and certificate
files are limited to eight million bytes. Certificates retain at most
67*256 selected indices and dual vectors. No search-budget exhaustion is
reported as mathematical infeasibility.

The finite oracle uses at most seven queries, 128 subsets, eight vector
values and 2187 cost assignments. The separate subspace oracle scans at
most 32768 subsets containing zero and tests at most 256 XOR pairs each.
CLI checks launch three serial subprocesses with 30-second timeouts, wait
for their completion and inspect their return codes. Temporary files are
owned by one context-managed directory and removed on every normal or
exceptional exit. Set TMPDIR to the run's scratch directory for local replay.

Explicit exception checks remain active under optimized Python. They check
source hashes, target coverage, dual independence, eligible coverage,
cheapest-basis exchanges, missing-target separators, complete quotient
enumeration and the final minimum. The checker reconstructs actual vectors;
it does not trust a reported rank or price. Malformed input rejects before
optimization. Failed checks propagate; scientific success is never cached.

All application functions fit within approximately sixty physical lines.
Shared helpers operate on small explicit values; certificate verification
does not call the optimizer. Both registered commands use isolated Python,
warnings as errors and disabled bytecode writes. The direct and registered
replays exercise the real optimizer and CLI. No external static analyzer or
proof-kernel verification is claimed.

## Managed-runtime deviation

Rule: Power of Ten rule 3, allocation before steady operation.

Location: optimizer.py and verify.py.

Reason: CPython dynamically allocates arbitrary-precision integers, lists,
sets and dictionaries. This exact one-shot program cannot disable runtime
allocation while retaining its Python interface.

Scope: bounded constructor, checker and finite corroboration only.

Compensating control: enforced input caps, at most 67 candidate certificates,
at most 256 rows per elimination and one current exhaustive instance. No
unbounded queue, recursive stack or persistent cache exists.

Verification: maximum-width/query-count case, maximum-codimension case,
oversize rejection, exhaustive oracles and subprocess timeout checks.

Follow-up: any native steady-operation implementation must allocate fixed
capacity storage before taking over this interface. That implementation is
outside this result.
