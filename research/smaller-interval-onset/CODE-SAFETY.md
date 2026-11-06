# Verifier bounds and inspection

The verifier only checks the new rational gates and hashes its own package.
It does not implement, import, fetch or replay the cited probability law.

- Control flow has no recursion. Failed gates raise `ValueError`; file errors
  propagate after the context manager closes the file.
- The Taylor sum has five terms. The gate loop has thirteen entries, the
  rejecting-control loop has two inputs, and the file loop has seven paths.
  There are no unbounded searches, queues, subprocesses or network calls.
- The exponent is bounded by `10^12` and is never used as a power exponent.
  Computed powers have exponents at most 80. The supplied rational numerators
  and denominators stay below 256 bits. Every file read is capped at 65537
  bytes and rejects lengths above 65536. Files close before the next read.
- Every function is below 60 physical lines. `require` calls enforce the
  arithmetic conditions in both ordinary and optimized execution. All mutable
  collections are local, and returned gate results and file bytes are used.
- No dynamic code, decorators, registration or callback chain is introduced.
  `sum`, the context manager and JSON encoding use normal Python dispatch.
  Imported calls have explicit standard-library targets.
- Registered checks enable warnings as errors. Development mode is also run
  locally. The repository's existing package workflow runs both registered
  normal and optimized commands. No shared workflow or analyzer is changed.

## Managed-runtime deviation

Rule: 3, fix memory capacity before steady operation.

Location: `verify.py`, rational arithmetic, dictionaries and JSON output.

Reason: CPython and `Fraction` allocate objects during arithmetic; they do not
provide an allocation-free execution mode.

Scope: one bounded verifier invocation, including seven bounded file reads.

Compensating control: fixed loop sizes, bounded exact integers, a 64 KiB cap
per file and sequential file lifetimes. No retained probability distribution
or enormous onset integer is allocated.

Verification: the two registered commands, the local development-mode run,
and static inspection of the bounded domains above.

Follow-up: reassess these bounds before adding inputs, adjustable numerical
domains or another package file to the receipt inventory.
