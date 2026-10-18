# Validation record

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Local platform: macOS arm64. All checks below ran on 2026-10-13 UTC.
The result is finite operator evidence, not a full multiplication proof.

## Local checks

| Check | Result |
|---|---|
| `python3 -B research/cold-wrapper-amplitude-audit/verify.py` | PASS on Python 3.15.0; exact receipt |
| Same replay with `-I -O -B` | PASS on Python 3.11.15, 3.13.16 and 3.14.8; identical complete receipt |
| `python3 -I -O -B research/cold-wrapper-amplitude-audit/test_verify.py` | PASS, six tests on Python 3.15.0 |
| Existing `scripts/verify_cold617_interface.py` on both archived PR622 native providers, `--entering 36 --cold 22` | PASS; original scoped interface binding |
| Original `hpe_adapters_local.wrapped_ok` on the 14 good cold recipes and the 14 `R Z_6` mutants | All good recipes accepted; all mutants rejected |
| `actionlint .github/workflows/cold-wrapper-amplitude-audit.yml` | PASS |
| `make selected-record-check` | PASS; selected rational result, source inventory and proof supplement unchanged |

The six harness tests run the public checker in isolated, optimized Python.
They cover the positive replay; a minimal copied input tree in a path with
spaces after changing gzip compression and timestamp; changed source bytes;
a changed adapter phase; a changed expected rejection result; and refusal to
overwrite an existing output. The latter four cases fail as intended. The
mathematical controls are the 70 exact counterexamples in `EXPECTED.json`,
not merely subprocess failure tests.

The optional original-checker comparison is corroboration. It is not used
by the new public checker or to construct its expected matrix kernels. It
confirms that the new zero-column control is already rejected by the full
production predicate; the audit does not allege a production defect.

## Cost and verification boundary

The public amplitude replay uses no third-party package and takes less than
one second in the observed local runs. This is an observation, not a
comparative performance claim. Each full matrix is stored sparsely with
exact Gaussian-integer numerators and a common denominator of 16.

No selected constructor, supplier, global invoice, or accepted artifact was
changed. The repository-wide regenerating `make verify` and cold
`make frontier626-verify` suites were not run for this isolated audit.
Their success, remote Linux execution, and full theorem validation are not
implied by these local checks. The added workflow scopes Linux runs to this
package on Python 3.11 and 3.14; a workflow file alone is not a CI result.
