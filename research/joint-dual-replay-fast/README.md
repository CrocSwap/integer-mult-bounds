# joint-dual-replay-fast

**Verifier engineering; no kappa, no certificate, supplier or frontier change.**
An opt-in adapter that speeds up the joint-dual serialized-word replay with
identical checks and identical receipts.

Prepared by Aaron Wang, with help from opencode. Apache-2.0.

## Scope and question

Card `replay-runtime` (scope key `b1dd41940c60d240b47a`): can one measured
replay bottleneck be sped up without dropping coverage? The object is the
replay stage of the frozen frame-compiler chain `research/joint-dual`:
`scripts/experiments/binary_frame_replay.py:replay()` on the pinned words
`certificates/joint-dual-word-{23,25}.json.gz` (the words of the PR25-PR58
lineage; source freeze `research/joint-dual/SOURCE.json`, enforced by
`joint_dual_compose.check_sources()`).

Card selection note: the first-choice drawn card `portable-replay` (scope key
`831cc1a3c8f9ff01b197`) matched the fresh claim posted 2026-10-14T11:24Z in
https://github.com/CrocSwap/integer-mult-bounds/discussions/1166 (completed as
https://github.com/CrocSwap/integer-mult-bounds/pull/1834), so per the
pair-collision rule this session took the second-choice card. See TASK.json.

## The measured bottleneck

cProfile of `replay()` on the h=23 word (CPython 3.12, Windows) shows 2.045 s
total, of which **0.84 s** is the per-output full-triple scan

```python
expected = sum(1 << i for i, t in enumerate(triples)
               if common in t and not (set(t) & (set(triple) - {common})))
tt = [i for i, t in enumerate(triples) if common in t]
```

(1,020,119 generator iterations at that line: 5,336 outputs x 1,771 triples).
The rest is the full-basis word simulation and the event loops.

## What this package changes

`fast_replay.py` re-executes the historical replay body with **every assertion,
both full-basis orientations and the receipt kept identical**, replacing only
the scans with containment masks over the same `combinations(range(h), 3)`
enumeration: bit i of `center_mask[c]` is `c in triples[i]`, bit i of
`pair_mask[c][x]` is `{c, x} <= triples[i]`, and

```
expected(common, triple) = center_mask[common]
    & ~pair_mask[common][x] for each x in set(triple) - {common}
```

is exactly the literal condition. `check_word` (including PR64/rfu08's
cancelling-scatter control) and the whole transitions stage
(`binary_frame_profile_prepare.prepare`) are the frozen historical
implementations, loaded unchanged. The historical scripts, certificates and
`tests/test_joint_reclaim.py` are **not modified**; this is the opt-in adapter
pattern of `research/ck-dyadic-replay-fast`.

`shim/binary_frame_replay.py` and `suite_arm.py` exist only for adoption
simulation: preloading the shim routes the *unmodified* frozen test module's
`from binary_frame_replay import replay` to the adapter.

## Evidence

- **Identical receipts.** Historical and adapter replay receipts are equal on
  both pinned words and equal to the recorded receipts in
  `certificates/joint-dual-compiler.json`; the delegated transitions stage
  equals `certificates/joint-dual-transitions-{23,25}.json`.
- **Full cross-check.** On all 12,261 outputs of both words the mask algebra
  equals an independently written literal scan.
- **Oracle matrix.** The exact twelve mutations of the frozen
  `tests/test_joint_reclaim.py` (eleven rejections plus the scatter-reversal
  acceptance) on both words: every accept/reject outcome agrees with the
  historical module in both checkers (24 cases), and the documented rejections
  reject.
- **Failure controls.** A corrupted containment table is detected by the
  cross-check (40/44 mismatching outputs at h=23/25); an unchecked word
  rejects; `-O` entry refuses to run ("Assertions must remain enabled"); the
  source freeze and word pins are re-checked every run.
- **Adoption simulation.** The frozen test module runs unmodified against the
  adapter through the shim and passes all 16 tests.

## Before/after wall time (same fixture, measurements never gates)

Paired alternating runs, CPython 3.12, Windows; see `BENCHMARK.json`:

| Fixture | Historical median | Adapter median | Speedup |
|---|---:|---:|---:|
| `replay()` on both pinned words (5 pairs) | 2.233 s | 1.285 s | **1.74x** |
| frozen `tests/test_joint_reclaim.py`, unmodified (3 pairs) | 41.47 s | 37.72 s | 1.10x |

The unit fixture clears the stated target of at least 25 percent. The suite
fixture improves only 10 percent because most of that module is JSON
deep-copies, mutation rejection paths that never reach the scan, and the
unchanged transitions stage; no coverage was dropped to improve it.

Retained checks: `check_word`, every replay assertion, both full-basis
orientations, the unchanged transitions stage, and the frozen test module as
oracle. Invalidation: the containment tables are rebuilt from the word on
**every call** — there is no persistent cache and no staleness; the source
freeze and word pins are re-verified on every replay.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/joint-dual-replay-fast --check-only
python3.12 scripts/research_package.py --package research/joint-dual-replay-fast
python3.12 -I -B research/joint-dual-replay-fast/benchmark.py   # paired timings
```

Expected: `PASS_JOINT_DUAL_REPLAY_FAST_EQUIVALENCE` (see RESULT.json),
`PASS_REGISTERED_RESEARCH_PACKAGE research/joint-dual-replay-fast outcome=completed`,
and a BENCHMARK.json with the paired timings above (values vary by machine).

## Limitations

- Opt-in only: the historical chain, its frozen pins and the suite default are
  unchanged, so the repository-wide suite wall time benefits only after a
  maintainer adopts the adapter (adoption would require superseding the
  `research/joint-dual/SOURCE.json` freeze, which this PR does not do).
- Domain is exactly the two frozen words at h in {23, 25} (the
  `binary_frame_math.exactness` certified dimensions). The mask identity is
  tested on synthetic shapes up to h=12 but no other word is claimed.
- The adapter mirrors the historical first-match `list.index` semantics with
  explicit `ValueError`s; duplicated frames in a word keep the same behavior.
- No mathematical claim of any kind: no kappa, no bound, no supplier admission,
  no selected-frontier change.

## Open next questions

1. **Sibling skip-frame line.** Can the same identity speed up
   `verify_skip_frame.py`'s replay, which shares the triple-scan shape? First
   step: profile it on its pinned words and measure the scan share. Blocked by:
   that chain's own pin freeze and oracle controls; do not retrofit frozen
   packages.
2. **The remaining simulation.** Is the full-basis word loop (now about 55% of
   the optimized replay) reducible without weakening the two-orientation
   replay? First step: measure limb traffic in the two orientation passes.
   Blocked by: the requirement that every basis row of both orientations is
   executed literally.

## Credit

- The frozen replay, transitions stage and words are the frame-compiler line of
  Chafik Boukhalfa ([PR 25](https://github.com/CrocSwap/integer-mult-bounds/pull/25) by
  Rohan Arun (rohanarun, with OpenAI Codex assistance) through
  [PR 58](https://github.com/CrocSwap/integer-mult-bounds/pull/58) by Chafik Boukhalfa
  (chafreaky, with OpenAI Codex assistance); `scripts/experiments/pin_joint_dual_sources.py`,
  `research/joint-dual`), with the original word/frames checks; PR64 (rfu08) is
  credited in `check_word` for the cancelling-scatter counterexample, which is
  retained verbatim.
- Workflow precedent: `research/ck-dyadic-replay-fast` (opt-in adapter pattern,
  paired benchmark receipts) and `research/git-provenance-stream` (timings as
  measurements, never gates). Both are credited, not modified.
- Task selection, profiling, the adapter, controls and this write-up were
  prepared by Aaron Wang with help from opencode; substantial AI assistance is
  disclosed in TASK.json. No independent human review is claimed.

## Maintainer integration refresh

The package was recertified against main `ec8707299e2f40918f5f96cdab99ee49cdbabcf0`. The original donor base remains recorded in TASK.json. Only the enclosing `research/joint-dual/SOURCE.json` input pin changed: its reclaim-compiler digest was updated by an earlier integration. This adapter does not invoke that compiler; its frozen replay, prepare, test and word inputs are byte-identical. The registered replay is retained in the ninth-batch integration audit. No frozen source or benchmark claim is rewritten.
