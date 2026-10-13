# Independent verification of eight PR699 frame changes

This contribution independently reconstructs and checks the conditional bound

**κ = 1661202643272239 / 10^18 = 0.001661202643272239**,

from PR699's κ = 0.001660666354374641. Concurrent
[PR741](https://github.com/CrocSwap/integer-mult-bounds/pull/741), by chafreaky,
published the same eight-frame construction during this investigation. **We do
not claim priority or a bound beyond PR741.** This package adds an independent
checker using explicit subsets of GF(2)^9, an independently discovered recipe,
complete local accounting and a fresh admission replay.

The main checkout base is `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The accepted selected certificate at that base is κ = 0.001635527380375392;
PR699 and PR741 are pending contributions, not selected-frontier updates.
`upstream/` and the selected frontier are unchanged.

## What is checked

Eight phase-B gate frames grow from dimension four to six. Every scalar gate,
entrance, final frame, helper width and physical owner placement stays unchanged.
Each change replaces paid ranks `(2,3)` with `(1,4)`. The complete local profile
is `{1:2556, 2:334, 3:430, 4:194, 5:56, 8:8}`; its rank mass is 5634.
The global profile is
`{1:184033, 2:24048, 3:30961, 4:13968, 5:4032, 8:576, 44:1, 48:2396}`,
with rank mass 520704 and deficit 2560. All 36,288 owner roles are retained.

`independent_frames.py` uses finite point sets, with no constructor, native
row-reduction or optimizer imports. It checks every frame inclusion, all paid
climbs, the eight center descent chains and every residual width. Twelve
negative controls include each omitted frame change, a mass-preserving false
profile, a changed scalar coefficient and changed entrance/final data.

The full replay additionally checks all 728 arbitrary-input columns in both
orientations, native ledgers, exact phases and wrappers, 35 focused frame
controls, 95 inherited end controls, all literal owners, the finite invoice,
69 admission controls, 12 bit-supplier controls, two rational moment engines
and 47 strict outer constraints. An independent owner checker contributes seven
additional corruption controls. See `PROOF.md` and the replay receipts in
`../pr699-frame-retiming-validation/`.

## Reproduce

Use Python 3.11 or newer with assertions enabled; no third-party packages or
optimizer are required. Prepare the immutable dependencies once, from the
repository root:

```sh
git fetch origin 03e8d7ca494a083e5053cd6b1228f66b98414479
git fetch origin a6895a69f8ad98ab45777b03e9e6f48888c39f6f
mkdir -p /tmp/frame8-pr699 /tmp/frame8-pr635
git archive 03e8d7ca494a083e5053cd6b1228f66b98414479 research/gauge44-promo-p6k4sw | tar -x -C /tmp/frame8-pr699
git archive a6895a69f8ad98ab45777b03e9e6f48888c39f6f research/complex-571-cold14-st2 | tar -x -C /tmp/frame8-pr635
```

Then run one command with a new output directory:

```sh
python -B research/pr699-frame-retiming/verify.py \
  --main . --pr635 /tmp/frame8-pr635 \
  --dependency /tmp/frame8-pr699/research/gauge44-promo-p6k4sw \
  --work /tmp/frame8-verified
```

Expected: `PASS_PINNED_INPUT_FRAME_RETIMING_COMPLETE_REPLAY` and
κ `0.001661202643272239`. Allow several minutes for exact phase and mutation
checks. The small frozen PR699 input has decompressed SHA-256
`d232183f233899961bf55cac67a18545ed33548d9a7ca7078990d1a83d557c59`;
it was rebuilt from the pinned PR635→gauge44→no-triangle→p6n→promotion→SW4
chain during this investigation. This command is an incremental replay from
that pinned input, not a fresh ancestral replay. PR699's README gives the full
ancestral reconstruction commands. `SOURCES.json` pins all dependencies;
regenerated compressed files are compared semantically where appropriate.

For the independent frame/cost check alone, first build the changed word with
`construction/build_frame_raises.py`, then run `independent_frames.py --before
inputs/PR699-WORD.json.gz --after NEW_WORD --out RECEIPT` using package-relative
paths. That short check does not establish scalar endpoints, phases or hosting.

## Scope and attribution

The arithmetic certificate is conditional on the inherited all-size compiler,
common-label/mutable-source realization, complete-invocation hosting,
precision/tape, exact recovery, analytic transfer and PR589 bit interfaces.
Finite replay is not a formal proof of the full multiplication theorem.
The complex lower endpoint is `1663966829367501881629/10^24`; PR589's bit
endpoint `1733427039589844234749/10^24` remains nonbinding.

Prepared by **Tekalign (tekuuu)** with substantial **OpenAI Codex** assistance,
including delegated research, implementation and verification. Credit goes to
**chafreaky** for concurrent PR741 and the PR685/660 owner map; **jeremykothe2**
and BRoute for PR699's read exchanges; **icekylinx** for gauge44 and the native
verification lineage; BlockInvert for promotion machinery; Q6Reviewer for
end controls; and the PR589, PR635, PR653, PR658, PR676 and earlier contributors
credited in the pinned packages. See `NOTICE.md`. New work is Apache-2.0.
