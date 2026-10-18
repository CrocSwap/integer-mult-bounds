# Engineering decisions and limits

The exit predicate is a source-bound, clean-return Boolean caller for all
9,992 prelude/A scalars per provider/orientation, with a fully charged local
comparison. It does not require or assert supplier admission.

Build the Lever shaped the deterministic circuit generator, stream binding
and cold replay. Prove It Works shaped the serialized truth-column and
independent bit-array checks, rather than relying only on real-arithmetic
endpoints. Power of Ten shaped explicit input, width, recipe, source and
verification bounds. No shared or frozen predecessor source is changed.

## Power of Ten inspection

1. New call paths have no recursion. Circuit construction and evaluation use
   bounded loops and structured exceptions; external temporary outputs have
   explicit ownership and either caller retention or scoped cleanup.
2. Width is at most 256; each recipe has at most 32 instructions; the scalar
   alphabet has at most 32 templates; the full native stream has at most
   30,000 events and exactly 9,992 covered scalars. A circuit has at most
   50,000 gates. Truth-column batches have at most 16,384 cases. The native
   subprocess limit is 90 seconds each. Registered commands have 300/60-second
   bounds and inherit the runner's process-group cleanup.
3. Python allocates dynamically. This is the managed-runtime deviation below.
4. Every new function is at most 60 physical lines after formatting. Frozen
   source formatting and existing longer functions remain byte-identical.
5. Runtime contracts check inventories, exact rows, guard bounds, source/carry
   return, complete writes and the positive cost saving. They use explicit
   exceptions and remain enabled under `-O`.
6. Native work, circuits and logs use one external session directory. A local
   source search path is added only to load the pinned predecessor replay;
   all source files are included and authenticated. No external posting
   capability is present in the research implementation.
7. File writes and subprocess outcomes are checked. Invalid grid, signed
   range, clean stock and gate ports have behavioral rejection controls.
8. There is no generated/evaluated Python. Gate lists are ordinary JSON data,
   with two fixed gate types and four explicit wire banks. The inherited
   compiler is a fixed pinned subprocess, not an arbitrary command input.
9. Calls and data access are direct, except for fixed Python import dispatch
   and the two explicit Boolean gate variants. Wire ports are bank/index
   pairs with validated ownership. The source bank is never a target.
10. New Python passes Ruff correctness diagnostics `E4,E7,E9,F,B` for Python
    3.12, formatting and warning-as-error execution. Frozen dependencies are
    preserved; this is not a repository-wide lint/configuration change.

The two frozen native compiler scripts retain their original CRLF bytes.
Their exact paths declare Git `whitespace=cr-at-eol`; ordinary trailing spaces
remain diagnosed. No source normalization or pin change is used to pass the
publication check.

Rule: 3, fixed memory capacity.
Location: caller.py, replay.py, check_bits.py and the pinned Python replay.
Reason: Python integers, dictionaries and JSON decoding allocate dynamically.
Scope: this finite command, not a long-lived service.
Compensating control: enforced bounds above, input files at most 8 MB each,
bounded decompression in the predecessor, sequential provider compilation,
private external outputs and finite registered timeouts.
Verification: full cold replay and recorded maximum resident memory in
CHECKS.json, exhaustive capacity-limited bit batches and invalid-width tests.
Follow-up: use fixed-capacity storage if this verifier becomes a persistent
service; do not reuse these bounds as a production-memory guarantee.

The common 84-bit figure is an arithmetic capacity. The direct caller also
needs 83 owned clean carry bits, and the comparison needs one 84-bit scratch
field. Their physical production, routing and allocation remain explicit
caller obligations. The logical gate saving does not price those operations.

## Internal review

A separate read-only reviewer inspected the circuit identities, native guard
composition, reverse cleanup and decision trail. It independently checked
source/scale-prefix bounds on existing compiled streams and 4,088 unary cases
at widths 2 through 10. No arithmetic defect was found. This is internal
review, not independent human scientific approval. The exact probe result is
summarized in CHECKS.json. The main replay independently records every reached
guard and all published tariff values.
