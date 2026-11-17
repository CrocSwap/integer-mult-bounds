# Executable bounds

The verifier is read-only and uses Python 3.12's standard library. No source
module from another package is imported. Every mathematical acceptance check
uses an explicit exception and survives optimized execution.

- There is no recursion, subprocess, network request, dynamic evaluation or
  callback registration. The normal exit prints one generated JSON receipt;
  any failed invariant raises an exception and fails the command.
- Every matrix has exactly four rows and columns. Every word has exactly
  three stages. All products use fixed loops of length four or three.
- Each census has twelve orientations and exactly 65,536 inputs per
  orientation. It streams the inputs and stores twelve ten-bin histograms,
  twelve witnesses and one hash state. It does not retain the input corpus.
- The primary public evaluator checks exactly four integer inputs, with
  absolute values below 2^128, and distinct integer indices in 0..3. Booleans
  are rejected. Internal census calls have the stronger fixed domain 0..15.
- The independent interpreter is a fixed-corpus executable, not a public
  arbitrary-matrix API. Its matrices are constructed locally from twelve
  fixed index pairs. Its Fraction oracle has 256 inputs per pair.
- Receipt hashing reads exactly eight package files and one declared context
  input, each guarded at one MiB. All filesystem read failures propagate.
  The primary checks the context's pinned SHA256 before its census.
- All functions are below sixty physical lines. Warning-strict normal and
  optimized runs, source compilation and AST inspection are the available
  local diagnostics. No separate linter or type checker is configured here.

Power of Ten rule 3 has a managed-runtime deviation in both Python files.
Python allocates integers, tuples, Fraction values and hash/JSON buffers
dynamically. The fixed matrix/corpus sizes, streaming census, input bit bound
and one-MiB receipt-input limits bound live state. These are certificate
programs, not fixed-allocation runtime kernels. A fixed-capacity rewrite is
required before deploying them in a setting that prohibits allocation.

Python has no exposed raw-pointer dereference or compiler-preprocessing step
on these paths. Direct local function calls and shallow immutable matrix rows
are the corresponding inspected mechanisms. The only file writes are stdout
receipts; callers put them outside the checkout.
