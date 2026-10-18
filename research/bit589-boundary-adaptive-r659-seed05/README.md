# PR589 jointly boundary-adaptive pair at register 659 (seed 5)

**Status: scoped negative-result audit. No new kappa or stronger bound is claimed.**

## Scope and result

The assigned OS-random seed was `5` (bit supplier). The three candidates and
selection rule are recorded in [SELECTION.md](SELECTION.md). Seed mapping chose
the third register among the top three ranked by `dim(firstB)-dim(lastA)` and
then register ID descending: shared register `r=659`, with A[2071]
`(frame 501, target 290, source 659)` and B[820]
`(frame 598, target 184, source 659)`.

This extends the exact fixed-option pair census in PR #1382 by restoring the
reciprocal boundary dependency for these two moves. For every exact commutation
slot region, the enumerator first relaxes the opposite-stage boundary to form a
finite candidate superset, then recomputes B's lower frame from the moved A
schedule, recomputes A's upper frame from the moved B schedule, and checks COPY
retention and the full D/A/B/C frame chain for registers 184, 290 and 659.

The exact census produced 20 candidate frame assignments. Eight fail the
reciprocal A upper boundary. Twelve are legal: 8 preserve the complete paid
profile and 4 are strictly worse; none improve and none remain unresolved. The
fixed-original-boundary control also yields 12 legal pairs, so the census found
no joint-only pair for this cut. All 12 legal pairs are replayed literally through `wlib.rebuild_C` and
`wlib.paid`; the baseline/home control reproduces the pinned word's paid
profile. Destination slots are gaps before original operation indices; the
literal replayer adjusts the insertion index after a pop for later moves. Exact witnesses and rational interval deltas
are in [EXPECTED.json](EXPECTED.json).

This is evidence only for one pair of operations in the pinned PR589 word. It
does not establish that boundary-adaptive options are redundant for other cuts,
other words, larger move sets or recursive constructions. The accepted selected
result remains #1094 and the current assembly remains complex-limited; this
result changes neither the selected certificate nor its inherited assumptions.

## Reproduce

From repository root, with Python 3.12 and the pinned source files in
[SOURCES.json](SOURCES.json), run the package verifier:

```sh
python3 research/bit589-boundary-adaptive-r659-seed05/verify.py
```

Expected result:

```text
PASS_BIT589_BOUNDARY_ADAPTIVE_R659 seed=5 candidates=20 valid=12 joint_only=0
```

For registered package metadata and source-pin validation:

```sh
python3 scripts/research_package.py --package research/bit589-boundary-adaptive-r659-seed05 --check-only
```

Expected result:

```text
PASS_PACKAGE_METADATA_AND_PINS (not a mathematical acceptance check)
```

The verifier takes about 15 seconds on the recorded environment. It uses only
the standard library and pinned PR589 word, `wlib.py`, and exact base-two moment
engine; `C=1733427039589844234749/10^24`. The atlas checks a deliberately
relaxed candidate rejected by the restored A boundary and confirms the
fixed-boundary domain is contained in the jointly legal set. The finite replay
is not a proof for unenumerated moves or other registers.

## Open next questions

The next scoped question is whether the same reciprocal-boundary enumeration
finds joint-only choices for the next seed-ranked high-gap register (r=660 or
r=67). First recheck overlap and derive its exact boundary operations. This
extension is not included here.

## Provenance and assumptions

The selected source is the PR589 bit supplier on PR #555, within the accepted
#1094 result. The exact move/price method follows the transport audit in
[PR #1345](https://github.com/CrocSwap/integer-mult-bounds/pull/1345); this
scoped extension follows the open next question recorded by
[PR #1382](https://github.com/CrocSwap/integer-mult-bounds/pull/1382). The
selection, current state and source pins are recorded in [TASK.json](TASK.json)
and [SOURCES.json](SOURCES.json). The selected certificate and task catalogue
are provenance; the listed word, `wlib.py`, and moment engine are live pinned
inputs.


## Credit and license

Prepared by Cinna Davis with substantial OpenAI Codex assistance. The verifier
adapts and credits the exact transport infrastructure developed in PR #1345
(Qwen3.8-Flash) and extends the fixed-option census contributed in PR #1382
(OpenAI Codex assisted). PR #589/#555 supply the bit word and its construction;
the selected #1094 result and the word's inherited assumptions remain unchanged.
New package material is Apache-2.0, consistent with repository policy.
