# Validation

Executed on 2026-10-13 using CPython 3.12.15 on Linux in the official image
`python@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1`.
Containers had no network, a read-only checkout and root filesystem, no Linux
capabilities, no privilege escalation, two CPUs, 1 GiB memory and 64 PIDs.
Temporary test files used a bounded writable `/tmp`.

- The verifier reproduced all 13 fields and the complete expected receipt.
- All 13 tests passed normally and with `-I -O -B`. They contain 33 distinct
  negative cases: six historical false positives, one checked-literal change,
  14 source-grammar cases, seven order/multiplicity cases and five JSON cases.
- Each historical false positive runs the original R420 portion of the
  maintainer script with only three local path substitutions. Its assertions
  are explicitly retained even in optimized Python. A separate rejected
  literal mutation confirms that those assertions run.
- Source-expression controls bypass hash admission, so their rejection
  exercises the parser and exact comparison. They do not claim the changed
  Lean modules compile or evade the formal package's source hashes.
- Unchanged sources, nested comments and a different gzip encoding of the
  identical payload pass. Every consumed file matches its base Git blob.
- A minimal relocated tree, without Git or the original absolute paths,
  passes. Six release corruptions fail: changed Lean source, expected receipt,
  manifest provenance, omitted source pin, historical checker and gzip payload.
  Restoring the minimal tree passes again.
- The selected-record integrity check passed at this base for
  `1661202643272239/1000000000000000000`. Staged files match working bytes
  exactly, and `git diff --cached --check` passes.

Review caught and corrected a lexer issue and an initially permissive
list/tuple conversion before the final runs. Explicit Fin constructors and
gate tuples now have rejection controls. Separate automated review found no
remaining blocking issue; this is not human peer review.

No fresh Lean kernel build, supplier cold replay, repository-wide `make verify`,
remote CI result or full multiplication theorem is claimed. All changes are
standalone additions; no historical source, frontier or `upstream/` file changes.
