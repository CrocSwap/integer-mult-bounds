# Executed validation

Linux x86_64, CPython 3.12.15. Scientific commit:
`5bad501f85c453dc84bdd79affcf39de17f6150b`.

- Registered replay and metadata/source pins: PASS.
- Direct isolated optimized (`-I -O -B`) replay: PASS.
- Committed-byte and source-history preflight: PASS, 61 files; the scientific
  base b58ad9ef4d4e861b0eaa5dba41742bdc072dca51 is an ancestor.
- Committed package export and archive integrity: PASS, 61 files.
- Fresh extracted export, outside Git, `PATH=/nonexistent`, isolated optimized
  CPython 3.12.15: PASS in both orientations.
- Whitespace check: PASS.

Two retained interpreters agree on all 632 arbitrary input columns in each
orientation, paid profiles and scalar allowance. Registered replay includes
commutation, correction-sign and actual wrong-paid-rank controls. It does not
run a new compiler/outer/selected cold replay or independently re-prove the
retained all-column/physical native theorem. No independent human acceptance
is claimed. The complete moment is unchanged, so no new K is claimed.

Initial authoring attempts caught and corrected an integer-key versus JSON
string-key receipt comparison. The final normal registered replay, rather than
only receipt generation, passes. The first export launch named a nonexistent
system Python path; the successful run used the resolved CPython path.
