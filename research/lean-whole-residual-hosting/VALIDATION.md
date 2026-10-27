# Recorded validation

The new package passed a fresh offline build with the official Lean 4.33.0
Linux executable (compiler commit
`d8b18978322de05a8f3dba51ef03cf5461676c17`). All eight modules compiled with
trust level zero; all 47 theorem axiom reports passed. Seventeen have no
axioms; the rest use only `propext`, `Quot.sound`, or both. The precise source
hashes and per-theorem closures are in proof-manifest.json and replay-result.json.

The official release archive SHA-256 was checked against its GitHub release:
`4b3fb03c29a1e0a253fb1d11f9bae3725f19a0dc6fc09b3ea16d2c9df3349e2c`.
The build has no Mathlib dependency. Jacob Sussman's larger project was
inspected as source; no complete rebuild of that project is claimed.

Lean rejected six false finite instances: host preservation implies
commutation; overlapping residuals combine by union; a hosted residual may
lie outside the pending child; independently changed charts commute;
omitting the selected four-coordinate residual preserves coverage; and
retaining the whole pending child after hosting preserves its action.
The runner requires mathematical rejection by `decide`, not a generic
compiler error. BoundaryExamples also proves explicit negations, and
PhysicalExample checks a nonempty interface instance with changing banks.

The separate source check passed for the five pinned PR442 files and the
freshly emitted template. It verifies the selected slots, exact single-family
owners, schedule, coverage, and matching literal masks. Its source-check
receipt is separate from the Lean result. This is finite Python validation,
not an additional Lean theorem.

PR442's full `research/idle-axis-hosting/verify.py` replay completed with
`PASS_FULL_IDLE_AXIS_HOSTING_COMPOSITION`, including the parent construction,
bit/complex generation, independent hosting audit, and exact assembly.
repository-checks.json records the command, exit status, and original receipt
hash. Its reported numerical bounds retain all upstream assumptions; this
package does not independently certify those bounds.

The preceding session ran the repository-required `make gen4-bank-verify`:
all nine stages passed and all 112 inherited inputs were unchanged. The broad
`make verify` run was stopped after its `joint-dual-verify` prerequisite failed
with `AssertionError: Makefile`, independently reproduced on clean pinned
main. That broad suite did not pass. These unchanged baseline results are
recorded in repository-checks.json; no inherited implementation was changed
and those expensive baseline checks were not repeated for this additive proof.

Review snapshots and final upstream checks are recorded separately. The
final replay covers the exact packaged sources, including any later editorial
changes to comments. Nothing was pushed, published, or sent to maintainers.
