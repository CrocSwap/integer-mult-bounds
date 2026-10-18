# Validation and handoff

Validation date: 2026-10-14, Australia/Melbourne (2026-10-13 UTC).
Environment: macOS arm64, CPython 3.14.6; standard library only.
Original base: `91a2094f2e022930069e8cfdc810a3ea1b81cd09`.
Refreshed submission base: `47481c89fd30a43f8f882eb4b391e89c29273fd0`.
Subject PR889: `e2021d1c9e06948528cbc0a8fd7079b671da981d`.

## Completed checks

```sh
python3 -I -B research/dirty-fanout-star-census/verify.py
python3 -I -O -B research/dirty-fanout-star-census/verify.py
python3 -I -B research/dirty-fanout-star-census/test_package.py
python3 -I -O -B research/dirty-fanout-star-census/test_package.py
make selected-record-check
python3 -m unittest discover -s tests -p 'test_selected_result.py'
git diff --check
```

Normal and optimized verifier output and the deterministic certificate agree:
five complete shortest-word censuses, 60 free-algebra emitter cases with
literal inverse checks, five strict star-admission cases, six built-in controls.
Both package-test modes pass all ten tests. The selected-record check and all
five existing selected-result tests pass, both on the original base and after
incorporating refreshed main. The package is the only changed path relative
to refreshed main; `upstream/` and the selected record match that base.

The ten package tests cover loss of labelled-word multiplicities, a positive
output relabelling, dirty-connector leakage, a wrong integer sign invisible
modulo two, a valid endpoint outside the claimed query alphabet, standalone
relocation to a path with spaces, source drift, omitted source inventory,
wrong source commit, and certificate drift. The relocated default verifier
does not alter any package bytes. Rejected-source tests fail before executing
the emitter. The six algebraic controls are described in README.md.

The independent review checked the proof/state correspondence, weighted
quotient, pruning completeness and all-dirt noncommutative endpoints. It led
to explicit source-inventory completeness and one-connector/port admission
checks. The reviewer reran the final verifier and ten package tests. This
was a delegated AI review; no human-review or hosted-CI pass is claimed.

## Reproduction boundaries

The census covers all signed words of lengths `0..2k+2` for each `k=1..5`
using proved state compression and pruning, not literal enumeration of each
raw word. Certificate rows give the raw domain cardinalities and retained
state counts. The unpruned, unquotiented cross-check covers `k=1,2`.
The chosen finite domain follows seed `79`: `k_max=1+(79 mod 5)=5`.
The experiment stopped after completing this domain and its fixed controls.

No original construction code, selected certificate or shared verifier was
changed. Full repository artifact regeneration (`make verify`) and the
expensive selected-supplier cold replay were not run: neither validates an
additional obligation changed by this standalone research package. The
focused package checks and existing selected-record integrity checks above
are the relevant validation performed; no full-suite success is implied.

No full PR889 invoice, physical layout, rounding analysis, all-size compiler,
supplier integration or complete multiplication theorem was revalidated.
The original-base accepted conditional κ was `1661634653669567/10^18`.
Upstream advanced during verification and selected PR890 at
`1661957774647029/10^18`; this contribution does not change either result.

## Concurrency review

No pinned coordination issue existed at claim or prepublication checks. The
local claim records three candidate tasks and their selection. An initial
inventory inspected all 724 open PRs, including pending independent checks
and negative results. The review ledger and selected PR799 construction/review
were read before choosing this non-frontier subject.

PR889 was refreshed at the same pinned head. PR896 formalizes nonlinear binary
recursion, whereas this package counts exact linear one-source star words.
Concurrent PR934 extends PR889 to a binary multi-source alphabet and supplies
optimal witnesses; this package adds the complete minimizer count for the
one-source alphabet. PR901/PR816 already carry independent scalar/MST evidence
and were not duplicated. No borrowed pending result is promoted to the
selected frontier, and no savings from distinct submissions are combined.
