# Local validation

Validated on macOS arm64, 2026-10-13 UTC, at research base
`2921874911956718fcaaaf9396fe8267b3cfa9f0`.

- CPython **3.14.6** ordinary isolated full replay: complete receipt agrees.
- CPython **3.14.6** and **3.9.6** optimized isolated full replay and package
  tests: all **15 tests** pass on each version, including the complete 963-frame
  Fraction oracle, 16 deliberate rejection mutations and the legal price
  perturbation. No removable assertions are used for verifier rejection.
- Both test runs include a relocated temporary tree containing only this
  package and its declared inputs, invoked by an isolated optimized subprocess.
  No Git, historical workspace, solver, native binary or network is used.
- All **11 immutable source files** match both their SHA256 and Git blob pins
  at the base. Three context-at-base files were separately read from that exact
  Git commit and matched against both recorded identities.
- `make selected-record-check` and all **five** selected-result tests pass;
  selected kappa remains `1661960547713947/10^18`.

The complete deterministic numerical receipt is [RESULT.json](RESULT.json).
The package has no external Python dependencies. The test suite verifies that
an unrelated archive-manifest addition is accepted, while changes to a relevant
alias are rejected.

The GitHub queue was refreshed through **PR1034**. Concurrent PR1024's R714
reconciliation was read and credited; it covers a different word and claim.
Exact commuting-cancellation search returned only the unrelated rational CK
PR719. Neither pending package is a dependency.

Not rerun: native signed/formal replay, historical 39-million-comparison search,
no-gain retiming searches, physical hosting, complete supplier or outer assembly,
or repository-wide `make verify`. No shared generators or selected sources were
changed. A focused Linux workflow is included; no hosted pass is asserted here.
