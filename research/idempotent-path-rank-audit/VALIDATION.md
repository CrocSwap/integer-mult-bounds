# Validation and handoff

Validated on 2026-10-13 with CPython 3.14.2, macOS 26.3 arm64, using only the
standard library. Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The audit began at 05:18 UTC; selection/claim completed at 05:21 UTC.
Implementation and proof were complete by 05:33 UTC, when work moved to
verification and handoff, earlier than the reserved final quarter of the
40-minute budget. No larger search was launched.

## Commands and observed results

Run from the repository root:

```sh
python3 -I -B research/idempotent-path-rank-audit/verify.py
python3 -I -O -B research/idempotent-path-rank-audit/verify.py
python3 -I -B research/idempotent-path-rank-audit/test_audit.py
python3 -I -O -B research/idempotent-path-rank-audit/test_audit.py
python3 -I -B -m unittest discover -s tests -p test_cancellation.py -v
python3 -I -B -m unittest discover -s tests -p test_block_core.py -v
make selected-record-check
```

Both full package replays exactly matched the committed certificate. Both
unit-test modes passed all **12 tests**, including 113 rational/rectangular
rank comparisons against permutation determinants. The existing cancellation
suite passed **10 tests** and existing block-core suite passed **5 tests**.
The selected-record check passed with the unchanged exact conditional kappa
`51110230636731/31250000000000000`.

The main replay checks 10 named witnesses, the independent 1936-pair census,
30 generated pairs, all 400 original h=6 triple pairs, four original guard
rejections and 24 actual compiler endpoint pairs. The endpoint examples
expand two 144-gate control networks solely to obtain their actual matrices;
this package does not claim a full circuit certificate for those examples.

The proof and implementation were also reviewed by a separate Codex worker.
That worker independently reran the main replay successfully in about 1.60s
and found no material proof or scope error. This is AI-assisted review, not
independent human review or proof-assistant verification.

## Isolated replay and meaningful failures

A temporary checkout containing **only** the 23 pinned inputs plus this new
package passed from an unrelated working directory, with spaces in its path
and a hostile `PYTHONPATH/sitecustomize.py`, using `python3 -I -B`.
The observed replay time was approximately 1.73s; this is descriptive, not a
performance claim or acceptance threshold. A fresh `--out` certificate
matched every committed field. These subprocess controls also passed:

- Existing `--out` target: rejected with `FileExistsError`; its bytes unchanged.
- Appending a comment to the copied `rank_product_core.py`: rejected with
  `Source pin mismatch` before inherited imports.
- Replacing the copied certificate's one-sided excess `1` with `2`: rejected
  with `Recomputed certificate differs from committed evidence`.

The unit tests reproduce mutated/missing source-pin rejection, non-idempotent
input rejection, wrong dimensions and inexact-input rejection under normal
and optimized Python. The mathematical controls separately refute one-sided
`2 rank(PQ)`/`2 rank(QP)` bounds, a blanket `2ell` block bound, the converse
common-form claim, removal of idempotence, a trace proxy, and unrestricted
common-offset transfer. These are explicit counterexamples to those stronger
statements. No failed search is being described as an impossibility proof.

## Final overlap and review scope

The pre-submission refresh at approximately 05:35 UTC found **607 open PRs**
through **#788**, up from 583 through #764 at selection. Main remained the
exact base above; the pinned-issues query again returned no nodes. The
snapshot was searched across titles and full bodies for the claimed
idempotent/path-excess/common-form/mutual-annihilation scope. All new/changed
titles were reviewed. In particular:

| PR | Inspected head | Relation |
|---|---|---|
| #717 | `67e9e846d9e8814b2dd01133251bb83fafa8f5b6` | Non-projection sink-interface questions, distinct from this endpoint identity. |
| #778 | `f015b04c74801fa330f818d178e809c760fb5469` | Historical Gram replay performance, distinct from this rank-path proof. |
| #785 | `83e78085ae9c110a34bff87e71387292d85e47c0` | Fixed-support nonlinear message floor, a different model. |

Earlier source-frame translations (#13, #14, #21) and orthogonal-idempotent
composition (#455) were also checked for overlap; none is imported. No
matching concurrent endpoint audit was identified. This is a bounded review
of public metadata and retained sources, not a guarantee that no similar
work exists elsewhere.

Only `research/idempotent-path-rank-audit/` is added. Original source files,
`upstream/`, selected frontier and unrelated artifacts remain unchanged.
The selected-supplier cold replay and expensive repository-wide `make verify`
were not repeated because no supplier, generator or original checker changed.
Relevant original tests and selected-record integrity were run as above.
No CI pass or full multiplication-theorem audit is claimed. All construction,
recursive, precision and asymptotic assumptions remain inherited.

Contributor: Curtis Dransfield; substantial OpenAI Codex assistance in proof,
implementation, independent determinant replay, review and writing.
Apache-2.0; predecessor attribution is in README.md and the pinned sources.
