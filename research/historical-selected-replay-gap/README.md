# Historical admission gap for the selected-result checker

Audit, not a new κ. The selected conditional exponent stays
**781451/250000000** (0.003125804). Frozen historical inputs are not rewritten
and no live successor is added to an accepted-hash list.

## Result

At upstream `2485805a6d47f36ea83ddde6327d453ac82d44dc`, the exact-head helper
plan and the historical input gate were inspected for the handoff in
[discussion comment 19138624](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19138624).

`scripts/replay_historical_check.py` has one overlay of the selected-record
checker: the `tooling-ledger` input `scripts/verify_selected_result.py`.
Its frozen file
`scripts/historical-ci-inputs/ledger-batch970-verify_selected_result.py`
still hashes to the recorded pin

```text
d7fd929726b326aeeaf0a3996475adec88eee9aac09ae0bebeeaa0bc1fc8f199
```

The only previously accepted live successor is

```text
c0cc23a8534d91c8d272195315c725213f13279815750ffdef055ec3adfbe911
```

The live file hashes to

```text
d6b305eac5b9bdb8172c469ad30a1655a60fa0aceac8b1bf610e1b73f51babd8
```

`authenticated_input` therefore raises
`Unrecognized live source update: scripts/verify_selected_result.py`
before any historical command runs. The same gate rejects 19 CONFIG entries
on seven distinct paths. The other six are `Makefile` (historical prefix),
`scripts/partial_swap/shared.py` (13 aliases),
`certificates/partial-swap-network.json`, `docs/ci-verification.md`,
`scripts/run_isolated_tests.py` and `tests/test_isolated_test_runner.py`.
`docs/ci-verification.md` is the selected-family replay note; its live digest
is `c7d3027e9ad8bcbff68f07aa9576b30fb2f3c76c44d876d40c7fdbf4a3e2228a`.

A session walk of every CONFIG entry admitted 28 inputs and rejected these 19. The committed verifier rechecks the 19 rejections, not those 28 admissions.

The helper plan for `01885346d4e78083b0a41786f977f71c73e3ffa2..2485805a6d47f36ea83ddde6327d453ac82d44dc`
selects nine receipt packages because that commit edits
`docs/research/pr-ledger.json` and `docs/research/pr-intake-decisions.json`.
It does not select `make frontier6030-verify`. Three changed evidence files
match no package input. Those nine packages were not replayed.

## Scope

Task `portable-replay`, refined. The card allows a repair. This package stops
at the reported gap. Admitting the seven live successors would be a review of
those edits, which this session did not do, and the handoff asked not to
repin frozen sources. Selected-record binding orientation returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`. No scientific replay was run.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3 -B research/historical-selected-replay-gap/verify.py
python3 -B scripts/research_package.py --package research/historical-selected-replay-gap
```

The direct command prints `PASS_HISTORICAL_SELECTED_REPLAY_GAP`. A registered
replay prints `PASS_REGISTERED_RESEARCH_PACKAGE`. Both require Git history
containing the two inspected commits and the source and manifest objects at
`2485805a6d47f36ea83ddde6327d453ac82d44dc`. The verifier uses a temporary
sparse checkout of that commit, checks the declared source digests there, and
uses its planner and manifest inventory. The recorded rejections and selection
therefore remain reproducible after later changes to the live Makefile or CI guide.

## Open next questions

Review each of the seven live files against its last accepted or frozen bytes
and either admit that exact successor or revert it. Start with
`scripts/verify_selected_result.py`, whose unreviewed edit adds the explicit
file closure used by the current selected manifest. Do not treat an allowlist
edit as a replay of frontier 6030.

Whether the nine receipt packages selected by this commit's ledger edit still
pass is a separate replay. This package does not run them.

## Credit

The historical replay gate is Dennis's `scripts/replay_historical_check.py`.
The source-history fixture handoff is Clear1nsight's PR #4984. The selected
record is the reviewed #6030 conditional construction. Prepared by unpaidmoon
with substantial Cursor Grok assistance. Apache-2.0.
