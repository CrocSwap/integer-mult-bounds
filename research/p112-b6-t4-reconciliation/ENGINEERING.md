# Bounded implementation and checks

Separate Before Serializing Shared State kept this package, branch, cache,
claim and status file separate from sibling work. Only short shared Git
metadata and claim transactions use the common OS locks.

Prove It Works required the actual registered three-command replay, the
separate partition implementation, actual source hashes and committed
read-only Git-free export before the peer brief. Receipt equality checks
every field instead of trusting the status line.

Power of Ten inspections cover binding.py, model.py, verify.py,
independent.py and test_verify.py. They use direct calls and no recursion.
Each function is below60physical lines. Explicit ValueError checks remain
active under optimization. JSON objects reject duplicate keys. Every new
loop is bounded by8sources,6rules,69rows,7,546multisets,10pieceindices,
1,024subset masks or finite combinations thereof. The frozen filter has
24sequential cells and lengths at most14, at most37,044candidate multisets
per cell and at most64two-bin assignments. It is retained unchanged.

Rule3 deviation: Python necessarily allocates managed objects during
iteration. Live memory is bounded by the finite domain,69receipt rows,
one partition witness per rule/row and counters, not all assignments.
Each source payload is limited to100,000bytes, inventory JSON to16,384bytes
and the receipt to2,000,000bytes before parsing. Source copies in controls
use the fixed eight-path inventory. Temporary directories have context
cleanup and the one child replay has a20second timeout. Follow-up: revisit
these capacities before enlarging the domain.

Rule8/9 deviation: the standard Python module loader runs exactly the
authenticated retained vendor.bk2b filter after source checking, and
unittest dispatches twelve named tests. There is no arbitrary module or
code argument. The registered runner supplies a private bytecode namespace;
direct export checks use source-only bytes. The frozen source is neither
rewritten nor claimed fully compliant with these new-path rules.

Rule10 uses warning-strict Python3.12 replay and Ruff0.17.1 with
E,F,I,B,UP,RUF plus formatting checks on all five new Python files.
The frozen predecessor is excluded from formatting and cleanup. The
registered CI manifest reruns all three checks when the package changes.
The exact theorem premises and their historical proof suites remain
inherited and unrun, as stated in PROOF.md.
