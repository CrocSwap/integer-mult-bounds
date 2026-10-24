# The full shared-arena CRT batch fits from p = 3

Scoped counting proof, with exact finite corroboration. No new kappa.

For the explicit one-axis bill `U` in unpaidmoon's PR4650, repeat its complete
CRT and four-network charge on all `8(p+2)` axes. Retain its schoolbook product
beside every tape action. [PROOF.md](PROOF.md) proves that this full batch is
strictly below `E = 2^(4ell)(p+2)^16` for all integers `p>=3` and
`1<=h<=ell<=p`. The three admissible `p=2` cases are exhausted explicitly.
Exactly `(p,ell,h)=(2,1,1)` and `(2,2,2)` exceed `E`.

The least uniform constant in `8(p+2)U <= C E` is
`C = 9702312163/8589934592`, attained at `(2,2,2)`. A majorant exceeding an
allowance does not prove an actual machine lower bound. The new conclusion is
that no scalar-inventory change is needed for the large-parameter batch under
this particular allowance, despite the previously displayed small failure.

## Evidence and reproduction

The quantified result comes from the written proof. [verify.py](verify.py)
independently forms the full batch, compares a second polynomial expansion,
and checks all 45,759 triples with `2<=p<=64`. The generated, hash-bound
[RESULT.json](RESULT.json) records the exact exceptions, the sharp witness,
63 height inequalities, 64 extension steps and eight rejection controls.
No predecessor executable is run. The verifier authenticates its one live
proof input by SHA256 and Git blob identity. [SOURCES.json](SOURCES.json)
pins the canonical base, catalogue, selected record and inherited bill.

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/crt-arena-batch-threshold/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/crt-arena-batch-threshold/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/crt-arena-batch-threshold
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/crt-arena-batch-threshold --check-source-history
```

The direct verifier prints `PASS_CRT_ARENA_BATCH_THRESHOLD`. Its checker has
an explicit finite domain; the proof has no `p<=64` restriction. Normal and
optimized checks retain all checks through explicit exceptions. Default replay
does not rewrite the receipt; `--write-result` generates it deliberately.

## Scope and credit

Base is canonical main `624de9dc66858af0945e5f8a0942488d62280d43`, priority
revision 7. [TASK.json](TASK.json) changes `uniform-transfer-audit` into an
original analytic extension of another contributor's open batch question.
The [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19133323)
states the proposed threshold and the first-result stopping rule.

This contribution was produced by Nick Petalas. Credit unpaidmoon for
[PR4650](https://github.com/CrocSwap/integer-mult-bounds/pull/4650)'s one-axis
bill, its majorant lemmas and the batch question, and
[PR4377](https://github.com/CrocSwap/integer-mult-bounds/pull/4377)'s CRT and
rotation tariffs. Credit ToikY for
[PR4192](https://github.com/CrocSwap/integer-mult-bounds/pull/4192)'s arena
census and Cinna Davis for
[PR4100](https://github.com/CrocSwap/integer-mult-bounds/pull/4100)'s CRT
construction. Their claims are cited premises, not new verification deliverables.
Predecessor files and attribution are unchanged. New work is Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

The arena and reconstruction tariffs remain inherited. This does not execute
an arena, implement a tighter scalar inventory, compose reservoir placement or
exceptional repair, admit a supplier, or prove the multiplication theorem.
No Lean, Docker, native replay or full historical suite is required or run.
The selected frontier is unchanged. Python's managed allocation is bounded by
the fixed 64-parameter checker domain; no recursion or unbounded search is used.

## Open next questions

1. Can the actual word-level scalar inventory fit constant one at the two
   excluded `p=2` corners? Start with the per-record comparisons in PR4192
   section 2. The present majorant excess does not settle that question.
2. Can this full-batch allowance be composed with reservoir placement and the
   actual paid repair-key service of PR4795? Begin with one complete entry,
   call and exit program, retaining all source-state queries and restoration
   charges. Physical movement and all-size caller premises remain external.

The [structured questions](TASK.json) record relevance, first steps and blockers.
