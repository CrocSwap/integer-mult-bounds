# Verification and implementation limits

Engineering-mode used the hillclimb playbook. The frozen comparison uses the
literal PR3060 and PR3076 providers, unchanged native compiler and explicit
bit-gate tariff. The target was a strict reduction at the same target width,
subject to the written modular, source-preservation and clean-carry predicates.
The two attempts and their different metrics are in `decisions.tsv`.

Build the Lever led to the gate emitter, serialized templates and deterministic
stream receipt. Prove It Works required four fresh native compilations, exact
literal tariff aggregation, exhaustive small-width interpretation and semantic
failure controls. Power of Ten led to bounded inputs, circuit capacities and
child timeouts. These principles did not turn a local circuit into a complete
physical-caller or kappa claim.

## Power of Ten scope

The new executable files are `bitadder.py`, `check_bits.py`, `verify.py` and
`test_bits.py`. All 17 vendored files remain byte-identical to their source
commits. No shared code or selected scientific record changes.

1. Control flow is structured and nonrecursive. Context managers own disposable
   directories. Explicit output paths preserve diagnostics on failure. The
   tests also prove an occupied output directory remains unchanged.
2. Width is at most 256, coefficients have numerator at most 255 and dyadic
   denominator at most 4096, signed expansion takes at most nine iterations,
   and circuit capacity is 20,000 gates. Truth tables contain at most 65,536
   columns, with at most eight bits per register. Native streams have at most
   30,000 events and eight-million-byte decoded inputs under the inherited
   checker. Four source versions and two scripts per version bound compilation;
   each child has a 90-second timeout. Recipe alphabets have at most 384 keys.
3. Python integers, Fractions, dictionaries and lists allocate dynamically.
   This is a managed-runtime deviation from fixed steady-state allocation.
   The capacities above bound retained state. The checker runs as a finite
   batch, and registered replay has a 360-second combined timeout. Its
   subprocesses and temporary directories have explicit owners and cleanup.
4. Every new function is below 60 physical lines after formatting. The largest
   function, the explicit adder emitter, has 46 lines.
5. Executable `require` contracts check coefficient identities, gate ports,
   immutable sources, carry return, exact endpoints, frozen source bytes,
   complete literal tariffs and deterministic receipts. They remain enabled
   with `-O`. Dirty-carry, wrong-sign, omitted-gate and source controls fail.
6. State belongs to one circuit or private replay directory. The only path
   setup selects the package's frozen source modules. No worktree-wide writer,
   network authority or mutable shared registry is introduced.
7. Circuit-template writes check their returned byte counts. Native child
   failures/timeouts propagate. Source files and returned ledgers are consumed.
   The independent scalar-bit interpreter tests observable endpoint/source/
   carry behavior, rather than duplicating the emitter's count formula.
8. No generated Python, dynamic evaluation or hidden runtime registration is
   introduced. JSON templates are data with a fixed two-gate alphabet.
9. Calls and wire access are direct. JSON processing and unittest discovery
   use bounded standard-library dispatch, a runtime deviation from a literal
   C-style indirect-call prohibition. The frozen compiler is not redesigned.
10. New files receive warnings-as-errors, strict Ruff checks, formatting and
    source compilation, normal/optimized tests and registered Python 3.12
    replay. Vendored code is excluded from new style edits to retain source
    identity, while runtime warnings/errors still fail its execution. The four
    E402 suppressions identify imports deliberately placed after selecting the
    frozen module directory; they preserve explicit ordinary imports rather
    than introducing a dynamic loader. Follow-up is a package-native import
    interface only if the predecessor modules adopt one.

The inherited native compiler uses assertions and dynamic allocation. Its
children remove `PYTHONOPTIMIZE` and use fresh private bytecode prefixes. These
are inherited limitations, not a claim of full Power of Ten compliance for
frozen code. The generic registered runner isolates imported bytecode as well.

## Research boundary

This result counts a conditional Boolean ADD layer, with a proof for its
format contract. W=64 circuits are serialized and counted, not exhaustively
tested at that width or placed on a physical machine. The caller's permanent
source alignment, endpoint ranges, clean-space backing, routing and non-ADD
execution remain unknown. The unchanged recursive profile supplies no new
exponent saving. No complete supplier/outer cold replay is relevant to this
unchanged-profile local comparison, and none is claimed.
