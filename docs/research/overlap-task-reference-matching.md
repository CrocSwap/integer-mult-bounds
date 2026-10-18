# Numeric task references in overlap search

Task-card reference `2977` previously matched digits inside unrelated kappa
values and commit hashes. The overlap helper now matches canonical positive
integer card terms as standalone identifiers, including `#2977`, `PR2977`,
`PR #2977` and URL path segments. Explicit positional queries keep their literal
substring behavior, including when the same number comes from `--task`.
Leading-zero word terms such as the census witness `01021323` remain literal.
The JSON report names the identifier-matched terms in `reference_terms`;
the text report prints them as task references.

## Scope and task selection

Base canonical main is `836b19bfa309ceafbc8ee32a15e8c4b10dde7e11`, priority
revision 6. Chooser nonce `4c5a1c825963fc47f3423c2a00a41d2b` suggested the
adversarial-audit cards `supplier-boundary-audit`, `census-pruning-audit` and
`selected-stock-envelope`. Scope is **changed** to a coordination-tool bug
observed during their overlap checks. The scatter successor was already
proposed in Arham Tahir's [PR2992][2992], and a separate corrected-census audit
had an active claim. The stock leads retain their implementation obligations.
This contribution takes over none of those mathematical questions.

The falsifiable predicate is that twenty-one unrelated numeric/hash title
hits cannot hide a genuine `PR2977` body reference below the default
twenty-result limit solely by matching the numeric card term. Before the
repair that fixture has 22 hits; afterwards it has exactly the genuine hit.
This does not alter broad text terms such as `hosting`, the three-to-one
title/body scoring, pagination, cache freshness, path search or source coverage.

## Evidence

A same-corpus comparison on 2026-10-16 used 244 open PRs, 1,706 discussion
records and 3,126 local records. Remote pagination was complete, with PR and
Discussion fetch times `16:44:49.434268+00:00` and
`16:45:20.569634+00:00`. For numeric term `2977` alone, the base helper found
23 hits and identifier matching retained six. The seventeen removed hits
were decimal/hash fragments, including PR1692/1724's long numerical claims,
PR573's commit reference and local references to hash
`81f3b5d12977eba09e06fbff729167d59faabe90`.

The six retained leads were the #2976 discussion, its two result comments,
the #1166 handoff comment, PR2992 and the local review ledger. That comparison
is an observation of the dated cache, not a frozen remote-corpus certificate.
Live counts change. The deterministic CLI regressions reproduce the failure
without network access or that private cache.

The submission refresh at `2026-10-16T16:52:26.547174+00:00` covered 244 open
PRs, 2,440 closed/merged PRs and 1,707 discussion records, with complete
pagination and no warnings. The numeric-reference tooling query found only
this contribution's [claim][claim]. Canonical main remained the base above;
its guidance, priority revision and selected record were unchanged.

Run from the repository root with standard-library Python 3.12:

```sh
python3.12 -Werror -B -m unittest discover -s tests -p 'test_research_overlap*.py'
python3.12 -O -Werror -B -m unittest discover -s tests -p 'test_research_overlap*.py'
python3.12 -Werror -B -m unittest discover -s tests -p 'test_research_*.py'
```

The focused suite covers reference spellings, larger numbers, decimal and
identifier fragments, explicit literal override, all-term conjunction,
title/body scores and excerpts at the actual identifier occurrence. Existing
tests cover open/closed snapshots, pagination and path search. The CLI
fixtures also check that offline cache bytes and coverage metadata survive.
Before implementation, the new tests exposed four assertion failures and a
missing report field. After implementation, all 25 focused tests pass under
optimized Python. The broader workflow suite passes 164 tests, with eighteen
existing environment/platform skips. No scientific replay is needed or claimed.

## Limits and open next questions

Identifier matching is a syntactic filter, not a semantic overlap decision.
Explicit literal queries can still return numeric fragments. Broad text
matches can still fill the result limit, and unpublished work and arbitrary
code diffs remain outside the search. There is no evidence here for changing
the ranking policy or starting a new research family. Investigate ranking
separately only with a concrete missed lead and a defined comparison corpus.

Build the Lever led to reusable CLI regression fixtures. Prove It Works
required the failing base comparison and public CLI checks. Power-of-Ten
inspection keeps new match loops bounded by the existing finite terms,
records and text lengths, with no recursive calls. The matcher adds only
standard-library regular expressions and per-query patterns. Managed Python
allocation and regex dispatch are rules 3 and 9 deviations, limited to the
existing input corpus and covered by the CLI fixtures. The existing long CLI
dispatcher is a rule 4 deviation at `find_overlap.main`, now 121 lines.
Splitting the fetch/report lifecycle would broaden this matching repair;
public CLI tests cover its changed query setup. Extract that setup when next
restructuring the CLI. Existing input/network limits are unchanged; reassess
them before broadening the helper's data sources.

Credit Douglas Colkitt for the overlap helper and its coordination workflow.
Nick Petalas, Apache-2.0. Substantial automated assistance in implementation,
verification and writing; no independent human review claimed. No supplier,
selected source manifest or frontier changes.

[2992]: https://github.com/CrocSwap/integer-mult-bounds/pull/2992
[claim]: https://github.com/CrocSwap/integer-mult-bounds/discussions/3001
