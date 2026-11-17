# Executable bounds and inspection

Produced by Nick Petalas. Apache-2.0.

The executable validates supplied dyadic Smith charts. It computes no Smith
form and imports no predecessor algorithm. The only external input is the
pinned proof text, read for authentication. Scientific checks use no subprocess,
network, floating-point arithmetic, recursion or source-file mutation.

## Bounds

Input matrices have one through six rows/columns. Each reduced numerator and
denominator has at most 256 bits. Entries must be dyadic; U,V must be square
with dyadic-unit determinant. The full Smith identity and positive odd
chain are checked. Odd factors/budgets are at most 2^20-1. Matrix loops have
at most six iterations, products at most 6^3 terms and elimination six pivots.
Intermediate exact arithmetic is bounded by these input sizes.

Trial division visits at most 511 odd candidates through the factor's square
root, with at most twenty divisions per candidate. Budget products are below
2^40; the valuation loop has forty-one slots. The common-denominator function
accepts at most six factors. Production functions are below sixty physical
lines. Contract failures raise explicit exceptions and remain active with -O.

The independent modulo-nine oracle visits at most 9^4 right factors and 9^2
left rows per two-channel system; the one-channel bounds are 9^2 each. The
largest live image has 81 tuples. The scalar oracle has at most 125^2 pairs
per system. Every verifier domain is a literal bounded range or finite product.
Each registered command has a 120-second timeout. Local timings are in the PR.

## Managed-runtime deviations

Rule: Power of Ten 3, fixed allocation.
Location: both Python files during exact arithmetic and exhaustive checks.
Reason: CPython integers, Fractions and tuple construction allocate dynamically;
fixed-allocation execution is unavailable in this runtime.
Scope: this bounded single-process certificate command.
Compensating control: explicit matrix, bit, factor, budget and enumeration caps;
no growing work queue or retained candidate-factorization list. Sources are the
eight committed files and one hash-authenticated declared proof.
Verification: normal/optimized checks exercise input-capacity rejection, complete
residue domains and witness contracts.
Follow-up: larger constants require a fresh arithmetic/memory analysis; a
fixed-allocation deployment needs a separate backend.

Rule: Power of Ten 9, indirect calls.
Location: verify.py expect_rejection.
Reason: this bounded test helper receives three explicit candidate functions.
Scope: invalid-input controls only, with no externally supplied call target.
Compensating control: each site names construct, matrix or common_denominator.
Verification: every control must raise; a positive boundary must pass.
Follow-up: inspect any added call target explicitly.

Rule: Power of Ten 10, diagnostics.
Location: the two standalone Python files and package commands.
Reason: this standard-library package has no compiled backend or required
separate project Python type-checker.
Scope: these new files only.
Compensating control: warning-strict normal/optimized runtime, source compilation,
available static diagnostics, source pins and committed-byte/history checks.
Verification: exact commands and outcomes are in the PR body.
Follow-up: keep these checks; any native backend needs its own analyzers.
