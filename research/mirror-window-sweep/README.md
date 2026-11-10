# Construct mirror windows with one classification per rank pair

This scoped algorithmic proof and implementation are produced by Nick
Petalas. The opt-in endpoint sweep returns exactly the same ordered mirror
cells, complete integer histograms and funding errors as zxv's PR4483 direct
constructor, while classifying each target/paid rank pair once.

On the retained p16 input, pair classifications fall from 4,550 to 182;
on p7 they fall from 1,296 to 81. The checker enumerates these counts and
compares every output. They are operation counts, not a runtime speedup.
Output copying, counter updates, exact moment evaluation and the rest of a
compiler replay remain payable.

[PROOF.md](PROOF.md) gives the interval invariant, input contract and limits.
[windows.py](windows.py) is a standalone standard-library implementation.
Shared/default code and frozen sources are unchanged. The contribution
adds no compiler theorem, supplier, new κ or selected-frontier update.
Independent human and formal proof-kernel review are unclaimed.

## Reproduction

From the repository root with CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/mirror-window-sweep/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/mirror-window-sweep
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/mirror-window-sweep --check-source-history
```

An equivalent Python 3.12 path may replace the absolute path. Both registered
commands run the complete new certificate in normal and optimized modes.
Expected markers are `PASS_MIRROR_WINDOW_SWEEP`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
Generated receipts bind every package and input file by SHA256 and go to
stdout; no receipt is handwritten or consumed as a proof premise.

The check covers all 6,400 nonempty histogram pairs on ranks 1–4 with counts
0–2, including all 2,712 funding rejections, and complete retained p7/p16
histograms. Twenty boundary, collision, input, capacity and ownership checks
exercise half-open intervals, equal ranks, missing funding, invalid histograms,
independent snapshots and separate invocations. The old direct definition is
used only for implementation conformance. No predecessor scientific suite,
native word, root or multiplication theorem is replayed as the deliverable.

## API and scope

`mirror_windows(targets, paid, stats=None)` accepts positive integer-keyed
histograms. Each has at most 64 entries, with ranks and counts at most
`10**12`. It returns `(left, right, exits, sources)` cells; endpoints are exact
Fractions, and each Counter is independently owned. The optional stats map
records pair classifications, endpoint updates and cell counts.

The new sweep follows the exact original interval semantics. A pair has one
active interval and therefore two boundary events. The proof includes all
product collisions and source-funding errors. Histogram materialization is
still proportional to the returned data. No complete-caller runtime claim
or shared adoption is supplied.

Scientific base is canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8, selected
PR6030. The replay-runtime card changes scope to this originally posed
implementation question. [TASK.json](TASK.json) records the
[claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19380512),
source/overlap coverage and exact scope. Live PRs, the full seven-day account
list, claims, main README searches and merged/general-form searches were
checked. Arbitrary diffs and unpublished work remain outside that coverage.

## Open next questions

- Does adopting the sweep reduce an actual complete compiler replay time?
  First install it in one isolated current caller and benchmark end to end,
  preserving every output and rejection. Exact powers or output copying may
  dominate; this package supplies no such timing result.
- Can an incremental exact moment consumer avoid copying each histogram?
  First specify its endpoint and interval contract and compare complete
  enclosures. Changing the consumer requires a separate proof.

Structured relevance, first steps and blockers are in TASK.json.

## Credit and code constraints

The new implementation and proof are produced by Nick Petalas. Credit zxv
PR4483 for the direct constructor and adaptive compiler, Ryanson Jonathan
PR4459 for the corrected mirror semantics, Jacob Alan Sussman for the
integer compiler, Cinna Davis for the retained p7/p16 inventories and
Dugongue for the compact p16 consumer. Existing source notices remain
unchanged. Endpoint sweeps and difference events are classical. New work
is Apache-2.0.

Build the Lever shaped the standalone opt-in function and rerunnable
certificate. Prove It Works and Test Behavior, Not Implementation shaped
the complete returned-value/error comparison, literal boundary fixture and
ownership checks. The call graph is acyclic, functions fit within 60 lines,
and explicit exceptions survive optimized execution. Both registered modes
make warnings errors; no separate linter is installed.

Power-of-ten rule 3 has a managed-runtime deviation: Python Counters,
Fractions and output lists allocate while running. The API bounds each
support by 64, hence at most 4,096 pair classifications, 8,192 endpoint
updates and 128 elementary cells. The verifier has 6,400 fixed pairs and
two fixed retained profiles, under 120-second per-command limits. Memory
also includes copied output histograms. A long-lived or unbounded-input
implementation needs its own allocation contract. No new dispatch,
recursion, subprocess, network access or file-writing API is introduced.
