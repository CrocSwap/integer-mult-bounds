# Implementation decisions and verification limits

The accepted predicate is one exact exclusion of `4,5^2,6^8`, with a written
characteristic-zero implication and independently reconstructed finite evidence.
No source, selected frontier, shared verifier or predecessor package is edited.

Build the Lever changed the deliverable from a one-off calculation to the
committed `verify.py`, `bound.py` and separate `independent.py` replay.
Prove It Works required exact receipt comparison, a different flat generator,
all-frame cross-checks, optimized rejection controls and publication-byte checks.
These are the two engineering principles applied to this package.

## Power of Ten inspection

1. New code uses structured loops and direct calls, with no recursion or background
   process. CLI exceptions propagate nonzero; output files use exclusive creation
   inside a context manager. The original filter subprocess is read-only and checked.
2. Inventories are fixed: 120 roots, 112 live lines, 248 allowed rays, 58 graph
   vertices, 9,737 six-cliques and 2,025 frames. The primary frame stack allows
   at most 961 pending states and 2,000,000 visits, with fail-closed exhaustion;
   the actual complete traversal uses 352,877 loop visits. RREF enumeration has
   exactly 3,309,747 cases. The independent generator uses `35 choose 5` and
   `35 choose 4` subsets, at most 511 extensions per retained four-flat, and
   a 400,000-space capacity. It actually retains 5,124 candidate spaces.
   Each binary basis has at most five nine-bit rows. Each rational/integer rank
   problem has at most eight rows and columns. Registered commands and the
   original filter subprocess have 120-second timeouts.
3. Python allocates during execution. See the scoped deviation below.
4. All new functions fit within 60 physical lines after formatting. The longest
   is the independent CLI orchestration at 57 lines. Frozen library formatting
   and original filter style are not changed.
5. Mathematical invariants use `require`, which raises `ValueError` even under
   optimization. Checks cover inventory counts, rank/support spectra, complete
   frame orbits, candidate capacities, source hashes and the exact receipt.
   The optimized tests exercise changed graph edges and a planted large cover.
6. State is local or immutable module constants. No shared mutable cache, solver,
   service or worker is introduced. Runtime outputs are external and opt-in.
7. Inputs are regular, nonlinked files of at most 2 MB. The live data is checked
   against its hash and independently reconstructed root/label order. Retained
   files are checked against both SHA256 and Git blob identities. Subprocess
   status, stderr, output size and shape are checked. Output overwrite fails.
8. There is no dynamic evaluation, code generation, reflection or runtime
   registration in new proof code. The two registered checks use explicit imports.
9. New proof paths use direct calls and shallow immutable rows/bitmasks.
   Standard-library unittest dispatch is the scoped exception below.
10. `-W error`, Ruff correctness/import/modern-Python classes and warning-as-error
    compilation cover new Python. The optional `ruff --select ALL` exploratory
    audit also reported documentation, annotation, package-name and literal-style
    preferences. Those are not this repository's coding contract, and include
    mutually incompatible styles; no diagnostic suppression or shared config
    change was added. The applicable final selection is `E4,E7,E9,F,B,I,UP`.

The retained libraries are byte-identical sources, not a new reusable general
API. Their unused historical entry points remain for source integrity. No new
code depends on those historical entry points. Resource bounds cover only the
fixed finite problem in this package, not arbitrary caller inputs.

## Scoped deviations

Rule: 3, allocation-free steady operation.
Location: all new Python replay files and standard-library arithmetic.
Reason: the Python runtime and exact integer/rational arithmetic allocate.
Scope: this fixed, sequential finite verifier only.
Compensating control: finite inventories, bounded bitmasks, matrices, stacks,
file sizes and registered timeouts; no concurrent writers or unbounded stream.
Verification: complete primary/independent replay and capacity/rejection controls.
Follow-up: a fixed-capacity native port is needed only if this becomes a
resource-constrained runtime component, not for its current offline proof role.

Rule: 9, indirect calls.
Location: `test_verify.py` through the standard-library unittest framework.
Reason: unittest discovers and dispatches test methods by its supported API.
Scope: the sixteen explicit behavioral groups, not the mathematical verifier.
Compensating control: fixed test class, no user-supplied callback or plugin.
Verification: registered optimized run executes all sixteen groups.
Follow-up: retain the fixed test inventory if adding another behavioral group.

## Evidence limits

The primary census proves the full120 five-flat capacity twelve. The separate
flat generator uses that premise to obtain completeness by high-cost root
subsets; it independently reconstructs the selected masks, not that capacity
proof. Both algorithms share retained root geometry. The standard Weyl-chamber
theorem and original decoder reduction remain written dependencies. Local
checks are neither independent human review nor a proof-kernel theorem.

An early receipt comparator incorrectly compared JSON text with numeric versus
string key sorting. It now compares the canonical JSON data model, with a
numeric-key regression control. No mathematical receipt quantity changed.
