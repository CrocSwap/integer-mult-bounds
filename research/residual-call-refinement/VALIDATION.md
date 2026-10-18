# Local validation

Checked 2026-10-16 on macOS 27.0.1 arm64, CPython 3.12.15, Clang 23.1.3.
Canonical main was refreshed before publication and remained
`d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.
The selected source record and caller inputs were unchanged.

The direct verifier passed its typed RESULT comparison in 41.85 seconds.
The observed maximum resident set was 267,239,424 bytes. These are finite
checker measurements on this host, not bounds for the multiplication algorithm.

Commands completed successfully:

```sh
uv run --python 3.12 --no-project python -B -Werror \
  research/residual-call-refinement/verify.py
uv run --python 3.12 --no-project python -B -Werror \
  research/residual-call-refinement/test_verify.py
uv run --python 3.12 --no-project python -B -O -Werror \
  research/residual-call-refinement/test_verify.py
uv run --python 3.12 --no-project python -B -Werror scripts/research_package.py \
  --package research/residual-call-refinement
uvx --from ruff==0.17.1 ruff check --no-cache research/residual-call-refinement
uvx --from ruff==0.17.1 ruff format --no-cache --check research/residual-call-refinement
```

The registered replay reported `PASS_REGISTERED_RESEARCH_PACKAGE`. Both
behavioral runs passed six groups. An optimized, read-only Git-free export
also passed all six groups with unchanged exported bytes. Source pins and
package metadata passed.
`RESULT.json` retains all mathematical/checker quantities and control labels.
Publication bytes are compared after committing with
`scripts/check_research_commit.py --package research/residual-call-refinement`.
That read-only preflight does not replay the mathematics.

Two separate internal reviews inspected the proof and code. The code review
identified missing child source/directory byte assertions. Both exact
comparisons, loss controls and root program checks were added before the
passing final replay. A final delta review found that objection resolved.
These are internal reviews, not independent human or formal-kernel checks.

The final metadata overlap refresh covered 282 open PRs and 1,775 Discussion
records with complete pagination, at 20:12 UTC. Relevant matches were the
credited PR2989 and this claim; no competing completion was found in that
coverage. Closed work was represented through retained notes and the ledger.
Arbitrary diffs and unpublished work were not searched. No scientific novelty
or universal absence follows from a no-match result.

No selected-supplier cold replay, full GL64 packet, native build, Lean proof,
whole-caller closure, H2 time/space proof or hosted CI result is claimed.
The intentionally reduced fallback cutoff and opaque payload are documented
in the README and the typed receipt.
