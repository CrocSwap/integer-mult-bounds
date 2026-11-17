# Different epoch prices defeat the same-tree dirty echo

A three-row dirty fanout costs exactly **7**, while every same-tree echo
costs **9**, under the complete two-epoch prices below. This is a scoped
written proof with exact finite corroboration, produced by Nick Petalas.
It is a negative result for extending the stationary forest normal form.
It changes no supplier or selected kappa.

Ross Richardson's [PR3121](https://github.com/CrocSwap/integer-mult-bounds/pull/3121)
proves an exact forest tariff under stationary directed prices, and
explicitly leaves changing prices outside its contract. Here exactly one
common-value call on row zero separates two price epochs. The three rows
have arbitrary independent dirt, the common source is preserved, and every
row must finish with its original dirt XOR the common value. No helper or
free basis change is supplied. The only changed hypothesis is the ADD price
across the cut. The predecessor theorem is a cited result, not a replay
deliverable.

## Result and word

Before the call, ADD(1,0) and ADD(2,1) cost one. After the call, ADD(2,0)
and ADD(1,2) cost one. All other ADDs cost M in their respective epoch.
The complete common call P0 costs one. For every real M>=3 and every
positive row width, the unrestricted optimum is **7** and every same-tree
echo costs **2M+3**. Three is the smallest row count for this separation in
the declared exactly-one-call model.

The chronological attaining word is

```text
ADD(2,1), ADD(1,0), ADD(2,1),
P0,
ADD(1,2), ADD(2,0), ADD(1,2).
```

Both three-ADD words realize the same involution S, which adds row zero
to each other row. Their different spellings use only cheap directions
in their respective epochs. Every gate and the single oracle are paid.
The usual three-ADD identity is classical. The new result is the sharp
two-epoch tariff and its complete comparison with every rooted-tree echo.

[PROOF.md](PROOF.md) gives the all-word proof. Every successful program
needs at least four ADDs by the inherited one-row dirt invariant. A program
using an expensive ADD therefore pays at least M+3>=6 in ADDs. If it uses
only cheap ADDs, restoration forces both cut matrices to equal S, and each
epoch needs at least three ADDs. The three possible rooted trees each pay
2M+2 for ADDs. The ratio of their total bill to seven is unbounded as M grows.

The scope is the same-tree echo, including its children-before-parents
preparation and literal reversal. This does not contradict the stationary
theorem, forbid other useful forests, or settle changing-source scheduling.
An optimizer for changed epoch prices must allow different words for the
same cut map.

## Exact evidence and reproduction

From the repository root with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -X dev -W error -B research/two-epoch-dirty-fanout/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -X dev -W error -B research/two-epoch-dirty-fanout/independent.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/two-epoch-dirty-fanout
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/two-epoch-dirty-fanout --check-source-history
```

An equivalent CPython 3.12 path works. The registered replay runs both
checkers normally and under optimization. Direct execution is read-only.

The primary prints `PASS_TWO_EPOCH_DIRTY_FANOUT` in a generated JSON
receipt bound to every package file's SHA256. It enumerates all 168 matrices
in GL(3,2) and all 24 legal cut maps at M=1,2,3,6,11. For each price it
checks every attaining path and all 2,016 directed Bellman inequalities.
It enumerates all three trees, runs all 4,368 literal input assignments at
widths one through three, and passes thirteen boundary and semantic controls.
The M=1 stationary control has four ADDs, as expected. The M=2 computation
is corroboration, not an extension of the stated M>=3 proof.

The separate [independent.py](independent.py) prints
`PASS_INDEPENDENT_TWO_EPOCH_FANOUT`. It exhausts the full 1,344-state
two-epoch graph using sixteen-entry Boolean truth tables, including the
single paid oracle transition. Its 8,232 transitions give exact total seven
at M=3. It imports no primary or predecessor code. These are two separate
implementations by the same contributor. Independent human and formal
proof-kernel review are unclaimed.

[SOURCES.json](SOURCES.json) pins the unchanged predecessor documents as
live inputs and the catalogue/selected record as historical provenance in
reachable base history. No predecessor scientific executable is run.

## Limits and implementation bounds

These are declared complete tariffs. No selected caller is shown to have
them. Physical access, frames, routing, precision/storage, owned lifetimes,
restoration and head return remain unpriced. No native implementation,
complete recursive invoice, selected cold replay, Lean or Docker execution,
new kappa or complete multiplication theorem is claimed. All five selected
framework assumptions remain. The family decision is to stop at this
tariff counterexample until an actual caller makes the changed contract useful.

The primary has a fixed three-row domain. Its price evaluator accepts only
integer M in [1,1000]; these are checker limits, not theorem restrictions.
All loops have explicit finite bounds. The two Cayley searches each retain
at most 168 states, with at most 1,009 queue insertions. The separate search
retains 1,344 states, each with three sixteen-bit tables, and has at most
9,409 queue insertions. The independent main function is under sixty lines.
There is no recursion, dynamic evaluation, network access or subprocess.

Power-of-Ten rule 3 needs a managed-runtime deviation for Python's integer,
tuple and dictionary allocation. The fixed domains bound all live objects;
receipt hashing reads at most twelve package files and two pinned input
documents. Python runtime/library allocation is not a physical fixed-capacity
implementation. Warning-strict normal/optimized runs, AST parsing and
compilation provide diagnostics. A separate static type checker is unrun.

## Open next questions

1. Bind one actual caller whose legal frame or routing change induces two
   different complete epoch tariffs. First identify the owner/cut and price
   both realizations of S, including source access and restoration. No such
   physical price assignment is supplied here.
2. Characterize two-epoch price matrices for which one same-tree echo is
   still optimal. First compare the exact cut-matrix optimization with the
   combined-edge tree bill for a fixed small caller. The unrestricted number
   of cut matrices and the physical meaning of a price change remain blockers.

[TASK.json](TASK.json) records these questions and the scope change.

## Credit

The new tariff proof, example and checkers were produced by Nick Petalas.
Credit Ross Richardson #3121 for the stationary directed tariff theorem,
the boundary excluding changing prices and its one-row dirt argument;
Ross Richardson #3063 and Cinna Davis #1944/#1968 for dirty-output echo and
common-value lineage. Anthony #774 and Oscar Fennell #759 retain the earlier
forest-compensation credit preserved by #3121. No priority is claimed for
elementary XOR identities, forest synthesis or shortest-path algorithms.
Predecessor files and credit lines are unchanged. Apache-2.0.
