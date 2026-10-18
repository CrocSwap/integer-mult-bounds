# Validation and limits

Author checks on macOS 26.3.1, arm64, CPython 3.12.14 and 3.14.7, 2026-10-16.
Standard library only. No independent human review or proof assistant was used.

| Command from repository root | Observed result |
|---|---|
| `python3.12 scripts/research_package.py --package research/p104-retimed-error-recovery --check-only` | Metadata and all Git/SHA256 pins pass |
| `python3.12 -Werror -B scripts/research_package.py --package research/p104-retimed-error-recovery` | All three registered commands pass under the refreshed runner, including its private bytecode namespace |
| `python3.14 -I -O -B research/p104-retimed-error-recovery/verify.py` | Same complete receipt passes |
| `python3.12 -I -O -B research/p104-retimed-error-recovery/test_verify.py` | All six behavioral groups pass optimized |
| Source compilation with `compile(..., 'exec')` under CPython 3.12 `-Werror` | All four new Python files pass without writing bytecode |
| `python3.12 -I -B research/p104-dual-add-retiming/independent_check.py` | Retained predecessor dense/native audit passes; not a fresh full native ancestry cold replay |
| `python3 -B scripts/research_baseline.py` | Selected bindings/arithmetic pass; complex side binds, unchanged selected kappa |

Primary evidence checks all 70,311 nonzero final input/error coefficients against
reverse adjoints, plus private/peak rows. Forward and independently recomputed
reverse scores agree at all 5,252 non-lifetime cuts; the digest is
`d955464a6515d25592e34f85e2892237bea0da1ba87a6c0f9f3dfdc2881fafa9`.
The reverse full-cut pass took about six seconds in the first local run;
this is not a portable performance claim.

Tests reject omitted cleanup, an incompatible ADD chart, a changed late ADD
coefficient, source-byte mutation and a changed result coefficient. Eight
nonzero private residuals recover inside the strict radius. Half-grid ties
reject; outside the radius recovery can return the wrong lattice point.
An injected private error is independently seen in a retained public output.
The relocated optimized replay uses only declared inputs, runs without Git or
network, and leaves every file byte unchanged. No source executable is imported.

The submission refresh advanced main from
`4b82082f901945f8d0314f143576c7ad31e021fc` to
`c7df0bb890cae0cc393cdd32dad19c3facc80992`. The isolated contribution branch was
fast-forwarded before final registered replay. AGENTS.md, autoresearch.md,
priority revision 5, selected record and all five live scientific/doc inputs
were unchanged. The changed package-guide bytecode policy was read; new runner
behavior was included in validation. Exact overlap/freshness data is in TASK.json.

No Linux or hosted-CI success is claimed here. A linter was not available.
No all-size physical implementation, rounded recursive child, precision/tape
reserve, recovery scan/movement cost, ownership/idle bill, full selected cold
replay or formal multiplication proof was run or supplied. The conditional
tensor-grid argument is inherited and written, not extrapolated from fixtures.
The new result is the scoped completed-error/recovery implication in README.md.
