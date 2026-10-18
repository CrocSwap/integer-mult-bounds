# Validation receipt

Validated locally on macOS on 2026-10-13, based on
`66849e1475c930fd7732b1a0067ffee7e1e95f60`.

| Command | Result |
| --- | --- |
| `python3 -B research/complex-dyadic-lowering/verify.py` | PASS on Python 3.14.8 |
| `python3.11 -B -O research/complex-dyadic-lowering/verify.py` | PASS on Python 3.11.15, all checks remain active without assertions |
| `make selected-record-check` | PASS, selected source inventory and exact κ unchanged |
| `git diff --cached --check` | PASS, only this research package is added |

The deterministic evidence is in [EXPECTED.json](EXPECTED.json). Both Python
runs match it, including all four primitive-word hashes. The package makes no
wall-clock performance claim. The original and replacement primitive counts
refer to the same pinned complete scalar inputs.

A minimal committed archive of the seven package files and nine pinned source
files also passes under Python 3.11.15 with `-O`, invoked by absolute script path
from an unrelated working directory. This checks that no untracked file, local
dependency, repository import or original checkout path is required.

An additional scoped AI worker reviewed the algebra, operation vocabulary,
source binding and written scope. That review identified the need to compare
prefixes per register, including the initial dirty-work row. The implementation
now performs that exact comparison. This is AI review, not independent human
peer review or a formal proof assistant result.

The final overlap refresh inspected 513 open PRs through #693 and fetched
`origin/main`, which remained at the base commit. PR681 changes a factory's
scalar word; this package changes primitive lowering beneath unchanged scalar
words. Historical PR411 is credited for its coefficient microcircuits. PR667
checks logarithm intervals, PR688 composes bit circuits, and PR693 audits signed
block extraction. None is a dependency of this result. No pinned sprint issue
was present at either coordination check.

Not run: repository-wide `make verify`, cold selected-construction replay,
Linux CI or Lean. This standalone research package does not modify generators
or selected certificates. The focused primitive replay and selected-record
check cover its changed behavior without regenerating unrelated artifacts.
The geometric, compiler, hosting, rounding and tape contracts remain inherited.
