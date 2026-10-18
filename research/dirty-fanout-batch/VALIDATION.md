# Validation receipt

Executed on Linux x86_64, CPython 3.12.14. No third-party package is needed.
The exact base is `f567884aeb8851b6e794af1184119a3bfbe1e631`.

| Check | Outcome |
|---|---|
| `python3 -I -B research/dirty-fanout-batch/verify.py` | PASS; complete committed certificate matches |
| Same with `-O` | PASS; checks use explicit exceptions, not assertions |
| `python3 -I -O -B research/dirty-fanout-batch/test_package.py` | PASS outside the checkout in a path with spaces; all six corruption controls rejected |
| Three retained PR628 files vs fetched exact Git objects | Byte-identical; SHA256 and Git blob pins also verified offline |
| `python3 -B scripts/verify_selected_result.py` | PASS, selected κ = 1661634653669567/10^18 |
| `python3 -B -m unittest discover -s tests -p test_selected_result.py -v` | All five existing tests passed |

Completed mathematical coverage: 128 free noncommutative word cases and literal
inverses; 384 nonuniform weighted price cases; integer DP over all binary splits
for n=1..64; 795 dense cases (each compared across three schedules and their
inverses), including integers and moduli 2,3,5,9; one rational noncommuting case;
15 independent closed-form tape-travel cases; 27 rounded-grid cases with exact dirty restoration, inverse and error bound;
all 9,331 signed two-output star words shorter than six queries; and 15 named
algebraic/admission controls. The package test additionally rejects a damaged
source pin, changed certificate, omitted restoration, wrong inverse order and
unpaid child, and unpaid head return. Expected-failure controls are separate from passing examples.

This adds a standalone research package and no production/selected-supplier
changes. The repository-wide regeneration suite and expensive selected-supplier
cold replay were not rerun for this package. No hosted CI, proof-assistant or
human peer-review pass is claimed. Timing is not a contribution claim.

The final public overlap refresh reached #859 (656 open PRs). Targeted searches
covered common factors, fanout, multiple outputs, multi-output, and batch/dirty;
the latter returned 24 PRs, all on one page. Relevant additional comparison:
PR793 at `f9383f324ee86793c5ae7b73f8e39d5827a8aa52` shares JP8 coefficient
preparation while leaving recursive calls unchanged. This package changes the
number of full-row product queries under an explicit multi-output contract.
PR859's public description was a template; no mathematical overlap could be
inferred from that description. We do not claim an exhaustive review of every
open PR or priority over unpublished work.

GitHub API requests returned `Forbidden`, including the repository permissions
read, while HTTPS Git and public web metadata reads worked. No PR or issue
comment was submitted. The local claim, commit and clean patch provide the
handoff requested for unavailable submission access.
