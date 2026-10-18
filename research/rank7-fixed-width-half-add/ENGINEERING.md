# Implementation and verification bounds

The public boundary is `build` plus `pack` or `coarse_call`, or the serialized
program parser in `audit.py`. `verify.py` emits the real gate lists, reads them
back and invokes both interpreters. There is no native/compiler modification.

## Power of Ten inspection

1. Control flow is structured and nonrecursive in the package. Errors propagate
   as exceptions. Default temporary output is scoped by `TemporaryDirectory`;
   an explicit fresh `--work` directory intentionally retains diagnostics.
2. Width is 4 through 256, shift is 1 through 3 and every circuit has at most
   8,192 gates. The largest constructed circuit has 6,640. Validation precedes
   gate execution. Exhaustive loops use only widths 4 through 7. Other widths
   have at most 54 boundary fixtures per circuit. There are 180 programs.
   Source phases are limited to four lists of at most 12,000 gates, and the
   frozen inventory must have exactly four files. Reads and decompression
   are capped at 8,000,000 bytes. Registered commands have 180/60 second limits.
3. Python containers, integers, JSON and the filesystem allocate dynamically.
   This is a managed-runtime deviation, bounded as described below.
4. All package functions are below 60 physical lines after formatting. The
   circuit builder, gate interpreter, source inventory and CLI have separate
   responsibilities. The bit-array interpreter does not import the builder.
5. Executable contracts check source/grid/range, distinct gate wires, clean
   return, the exact result, literal complete invoices, source hashes, readback
   bytes and the final receipt. They remain enabled under `python -O`.
6. Circuits and parsed programs are immutable records. Mutation is local to
   construction or one interpreter call. There is no global mutable registry,
   worker process or concurrent writer. Constants only describe finite bounds.
7. Source bytes and JSON sizes are checked before use. File-write lengths and
   exact readback are checked. Invalid guards, overflow, missing restoration,
   source corruption and existing output paths have behavioral controls.
   Filesystem and decoding exceptions propagate rather than becoming passes.
8. There is no dynamic evaluation, generated Python or runtime registration.
   Emitted data contains only explicitly indexed CX/CCX gates.
9. Ordinary direct calls and shallow records are used. Remaining library
   dispatch is JSON/gzip, dataclasses, argparse and unittest. No externally
   chosen callable or plugin executes. Gate dispatch has exactly two shapes.
10. Validation uses Python warning errors, source compilation, formatting and
    Ruff E,F,I,B,UP,SIM,C4,PIE,RUF checks. The exploratory `--select ALL` pass also
    reported style policies not adopted by this standalone-script repository,
    such as implicit-package, copyright-header and per-test docstring rules.
    No diagnostic suppression or repository-wide configuration is added.
    Registered replay reruns arithmetic and behavioral validation; lint is a
    recorded local check rather than a new mandatory repository build step.

## Managed allocation deviation

Rule: 3, fixed memory after initialization.
Location: all Python modules in this package.
Reason: Python integer/bit operations and standard JSON/gzip execution allocate;
fixed-capacity native allocation would require a different implementation.
Scope: only this bounded offline circuit generator and verifier.
Compensating control: at most three producer circuits and one parsed program
at a time, each within the width/gate/input limits above; 180 sequential program
checks, no worker concurrency, one bit vector of at most 769 bits per interpreter
execution, and external temporary output.
Verification: exhaustive small signed inputs, maximum-width fixtures, oversized
width/gate rejection and registered command time limits. The emitted program
payloads total about 1.33 MB in the recorded run. This is an input/live-data
bound, not an instrumented maximum RSS guarantee for the Python runtime.
Follow-up: an actual native caller must retain these bounds and audit its own
allocator, zero-stock source, routing and precision-output lifetimes.

## Review limits

Build the Lever led to committed gate generators and a deterministic receipt.
Prove It Works required interpreting the emitted bytes, not just checking the
coefficient formula. Test Behavior, Not Implementation led to signed numerical
fixtures and cleanup failures rather than pass-string assertions.

No separate subagent capability was available. The author performed a proof/
resource pass and a source/behavior pass locally. This is not independent human
review, formal verification or scientific supplier admission. The paper cited
in the README credits the MAJ/UMA construction; the package proves and tests
its own particular gates and counts rather than copying that paper's totals.
