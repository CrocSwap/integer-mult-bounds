# R439 column zero needs at least six scatter taps

This finite exclusion was produced by Nick Petalas. Apache-2.0.

For the fixed `ideal303` target undo order and kept gates `{31,51,52}` of
[Sagar Thakrar's PR2440](https://github.com/CrocSwap/integer-mult-bounds/pull/2440),
retained column 0 cannot be synthesized with at most five scatter taps,
even when every target port and every cut are available. It therefore needs
at least **six** taps, improving the predecessor's lower bound of five.

Together with PR2440's cited bounds for the other eight columns, this raises
the complete scatter lower bound from **44 to 45**. That corollary uses the
predecessor bounds as premises; they are not replayed here. The known upper
bound remains 84. No exact optimum, native implementation, new kappa or
selected-frontier change is claimed.

The claim type is a **finite exclusion certificate**, supported by the
written reduction in [PROOF.md](PROOF.md) and an exhaustive exact search.
Repeated taps, different COPY intervals and arbitrary interleaving within
this frozen order are covered by a relaxation allowing all responses at once.

## Evidence and reproduction

The checker reconstructs all 33,744 cut/port responses from the authenticated
PR1062 word. A separately written literal bit-state interpreter executes
each injected basis vector through its remaining suffix and agrees at every
cut and port. The complete dictionary has 412 distinct responses.

An exact two-plus-three search stores all 82,435 distinct sums of at most
two responses. It then tests every subset of at most three responses:
1 empty subset, 412 singletons, 84,666 pairs and 11,571,020 triples. None has
the required complementary pair sum for column 0. Exact integer equality
decides membership; hashes bind artifacts and do not decide mathematics.

The independent small-domain subset oracle, an actual-dictionary positive
fixture and invalid-domain/source-corruption controls exercise acceptance
and rejection. Every check remains active under optimized Python.

Both warning-strict CPython 3.12.15 modes pass with identical receipts.
The independent oracle checks 128 targets against all 256 source subsets,
with 125 accepted and three rejected targets. Eleven rejection controls pass.
The direct commands each took about 1.15 seconds locally; the registered
two-command replay took 2.75 seconds. These are timeout-headroom observations,
not performance comparisons. An external Python linter was unavailable.

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/r439-column0-six-tap-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/r439-column0-six-tap-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/r439-column0-six-tap-floor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/r439-column0-six-tap-floor --check-source-history --check-modes
```

Another CPython 3.12 path may replace the local interpreter path. The direct
marker is `PASS_R439_COLUMN0_SIX_TAP_FLOOR`. Standard output is a generated
receipt bound to the source input and every package file. No receipt is
handwritten or committed, and the verifier writes no files. The committed
export includes the one declared compressed source input and runs without Git.

## Contract, credit and limits

There are 111 binary target coordinates and nine independent retained source
columns. The only target transport is the fixed 303-gate undo. A scatter tap
adds one copied source column to one target at a cut. COPY lifetime restrictions
can only remove available combinations. Mixing copied source columns, changing
the target basis or undo order, adding a new paid operation, or altering the
retained source contract changes this model.

Credit Sagar Thakrar / thakrarsagar, PR2440, for the one-slot multi-column
model, the 84-tap upper bound and the explicit remaining optimality question;
Ross Richardson, PR2407, for the ten-tap column-zero construction and live-COPY
interface; Sricharan Vagvala, PR2356, for the suffix-response reduction;
Charles Bethin, PR2279, for the split-ideal accounting; Sagar Thakrar, PR1062
and PR2115, for the word and deferred split; and Gareth Davidson, commdata2338,
Scott Woolsey Biggart, Aaron Wang, DreamingOfClouds, eumemic, Zhihao Chen,
woklerx, Arham Tahir and Dylan Crow for the retained R439/exporter lineage.
Meet-in-the-middle enumeration and linear superposition are classical.
The new claim is only the column-zero five-tap exclusion and its stated
lower-bound consequence. No predecessor executable is imported or replayed.

[SOURCES.json](SOURCES.json) pins the actual word, source question and task
provenance at main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
[TASK.json](TASK.json) records the changed card scope and overlap coverage.
The advance [CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19370159)
precedes the search. Complete remote pagination covered 505 open PRs and
6,496 Discussion records; sparse local notes, arbitrary historical diffs
and unpublished work remain coverage limits.

This is a historical scalar-interface side result. Every recursive rank
charge is unchanged. Native/parser admission, physical COPY/ERASE costs,
dirty ownership, hosting, precision/tapes, compiler closure and outer
assembly are not established. The five selected framework assumptions
remain. Independent human and formal proof-kernel review are unclaimed.
Selected cold replay, Lean and Docker were not run.

## Open next questions

Can a structural or exact method narrow the remaining 45 to 84 tap gap for
this fixed order? First choose one unresolved column weight or an explicit
chronological interval constraint, preserving all independent source columns.
Higher-weight exclusions and a complete lifetime lower bound remain missing.
The present certificate does not justify declaring 84 optimal.

## Verifier bounds

All functions are below 60 physical lines. Control flow is nonrecursive.
The source has fewer than 20,000 D records, 111 target coordinates and 303
retained undo gates. The two response engines each emit exactly 33,744
vectors. The generic bounded search accepts at most 412 distinct nonzero
111-bit responses, stores at most 85,079 pair values and performs at most
11,656,099 right-subset membership tests. Every loop has a finite bound.

Python allocation is a Power of Ten rule 3 deviation confined to this finite
command and these explicit capacities. No steady service, shared mutable
cache, subprocess or generated code is introduced. Warning-strict normal
and optimized replay provide the available interpreter diagnostics.
