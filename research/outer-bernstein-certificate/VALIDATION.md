# Observed validation

2026-10-13, Linux x86_64. Exact base:
`66849e1475c930fd7732b1a0067ffee7e1e95f60`.
These checks were executed with substantial OpenAI Codex assistance; they do
not represent independent human review or a proof-assistant formalization.

## Complete algebra and selected witnesses

The standard-library command reproduces the committed certificate:

```text
PASS_OUTER_BERNSTEIN_CERTIFICATE slacks=47 witnesses=2 coefficient_rows=57 weights=2586 controls=24 kappa=unchanged
```

Coverage is all 47 source rows, both piecewise branch decisions, all seven
minimum-margin comparisons, denominator positivity and the remaining source
identities. The 57 records have 2,586 exact coefficients, 1,268 positive.
Power-to-Bernstein nomination and direct integer-binomial reconstruction agree
coefficient by coefficient. Positivity follows from the written basis lemma,
not from sampling parameter values.

Both retained PR626 witnesses reproduce all 94 fractions exactly. The closed
ordinary-recursion formula matches all 14 recorded exponent/gap/cutoff triples,
and strict grid rounding reproduces both κ values and excludes their next
`10^-18` grid points for these fixed parameters. Supplier endpoints and bridge
meanings are inherited, not re-established by these calculations.

| Invocation | Observed result |
| --- | --- |
| `/usr/bin/python3.12 -B -I verify.py` (3.12.3) | Complete certificate matches; 24 controls reject |
| `/usr/bin/python3.12 -B -I test_verify.py` | All 12 tests pass |
| `/usr/bin/python3.14 -B -I -O verify.py` (3.14.4) | Complete certificate matches; 24 controls reject |
| `/usr/bin/python3.14 -B -I -O test_verify.py` | All 12 tests pass |
| `/usr/bin/python3.12 -B -I -S -O verify.py` | Pass with site packages disabled |
| `python3 -B -I crosscheck_sympy.py` (3.14.4, SymPy 1.14.0) | All 57 coefficient identities and four auxiliary identities match |

Table filenames are relative to this package; the full public commands are
in README.md. The optional SymPy checker imports none of the primary package's
arithmetic or parsing modules. No timing or speedup claim is made.

## Mathematical and packaging controls

The 12 tests include de Casteljau evaluation of every certificate at two
asymmetric rational points, 64 closed-form tensor basis checks, 864 recursion
identities and strict-boundary failures. These finite tests supplement the
universal coefficient certificate. A tightened Gaussian cap is positive at
both selected points yet false inside the admitted domain; its reconstructed
polynomial has a negative Bernstein coefficient.

The test suite copies only this package and the six pinned source files into
a temporary path containing spaces, invokes the verifier from `/tmp` with
`-B -I -O`, and confirms the same receipt. Altering a pinned source byte and
changing an integer certificate weight to `0.0` are rejected.

Additional disposable-copy checks on Python 3.14.4 with `-B -I -O`:

- Incrementing a default certificate weight is rejected by coefficient
  reconstruction, before trusting the receipt's claimed result.
- Writing to an existing output path is refused, preserving its exact bytes.
- Removing the implementation's actual nonnegative-weight guard makes both
  nonsampling regression tests fail with `ValueError not raised`. This checks
  a mathematical failure mode, rather than relying on a checker source hash.

`make selected-record-check` passes with the original source inventory and
κ `51110230636731/31250000000000000`.

## Sources, overlap and remaining obligations

The initial live snapshot covered 611 open PRs through PR791. The packaging
refresh inspected arrivals through PR810 and found no matching universal
Bernstein certificate. Main remained at the exact base. PR183 and PR701 heads
remained at the hashes in SOURCES.json; their written reduction and broader
Gaussian-envelope work retain credit. PR706/678 check moments, PR771 finite
invoice guards, and PR766 mutation sites, each with a distinct scope.

No production or selected-source files change. The complete repository suite,
supplier cold replay, geometry, native phases/wrappers, owner hosting, finite
invoice, and moment enclosures were not rebuilt for this isolated arithmetic
addition. Remote CI is separate. No Lean check or full multiplication-theorem
verification is claimed; the inherited uniform, physical, precision/tape and
analytic assumptions remain.
