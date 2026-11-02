# Implementation bounds

This contribution was produced by Nick Petalas. Apache-2.0.

The executable domain is the two fixed dual pairs, one fixed source word and
one constructed handoff. No discovery search runs during verification.
The two new Python files use structured control flow without recursion.
Boundary programs have at most six events, boundary matrices have at most
five coordinates and inverse checks have at most twelve events. All proof
checks use explicit exceptions and remain enabled with `-O`.

The complete word is bounded below 26,000 events with 744 formal coordinates,
a fixed source-frame catalogue and eight owned slots. The retained engines
enforce their source-specific operation, coordinate, frame and coefficient
contracts. Boundary controls perform eleven omission checks and two order
checks; whole-word controls perform exactly eight replays. Source inventory
has four entries. Both registered commands have 120-second timeouts.

Managed Python and `Fraction` allocate during execution. This is a documented
deviation from fixed allocation; the finite dimensions, event counts and
coefficient domain bound the live state. No fixed-memory implementation or
measured peak allocation is claimed. One mutated word is replayed per control;
the finite input sizes also bound temporary copies.

Authenticated predecessor code is compiled directly from bytes into three
explicit module names. This deliberate dynamic-loading deviation avoids stale
bytecode reads. `completion.py` is loaded the same way. The handoff constructor's
in-memory `basis` function is replaced once with the new explicit program.
The four dependency hashes are checked before any predecessor code executes.
No predecessor file, module source or receipt is changed. Their existing
implementation choices remain source-specific dependencies, not a new claim
of compliance or an unrelated refactoring target.

Each new function is below 60 physical lines. Strong runtime contracts,
warning-strict normal and optimized execution, source compilation and whitespace
checks cover the touched code. Python's standard library supplies no static
type checker; no additional installed linter or proof kernel is assumed.
Receipts are generated on stdout and include hashes of package and input files.
