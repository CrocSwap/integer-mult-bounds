# Eight signed-root K triangles: 480 helpers

A signed-root reflection extends PR635's four negative K triangles to eight signed triangles, reducing the base from 492 to **480 helpers** with the **unchanged constructor**. This is a structural contribution, not a record improvement.

The included complete conditional witness has κ = **0.001627103256702062**, exact `813551628351031/500000000000000000`; the conservative value is `0.001627103253808713`. It is below PR635's `0.001636241501576388` and the contemporaneous PR638 claim `0.001636456810414854`. Removing helpers also loses some cheap early endings and worsens packing. The failed record attempt is included so that a smaller local word is not mistaken for a stronger global bound.

## What is new

- `nominate_schedule.py` reflects each pair's second root coordinate, normalizes root-line signs, and matches the reflected source rows exactly. It reproduces all 120 positive-triangle reads and checks their multiset against independently enumerated required reads.
- `data/TRI-SCHEDULE.json` schedules both signs of `(0,1), (2,3), (4,5), (6,7)`. Each triangle saves three packet-copy helpers: `504 - 8*3 = 480`.
- Both PR635 provider chains transfer through the new helper map. Each has 48 frame regroupings and 22 inherited hyperplane endings. Cold tails are transported at legal joined frames, original absorption anchors are preserved, and the remaining inverse is rebuilt with exact dyadic elimination.
- `check_schedule.py` reproduces the schedule and rejects 16 damaged schedules: missing reads, duplicated reads, changed sources and targets of the wrong sign. Every rejection comes from an assertion in the unchanged constructor.

All 22 files under `code/` and `verify.py` are byte-identical to PR635 at `a6895a69f8ad98ab45777b03e9e6f48888c39f6f`; see `PROVENANCE.json`. The constructor checks all clean columns and frame chains; the native pipeline separately checks all 704 arbitrary-dirt columns, reflected programs, exact wrappers and phase identities.

## Definition

There are 112 data ports, dimension 9, eight centres, and 72 calls. Dispatch is jp8 ×71 / ck ×1. `data/WITNESS.json` contains declarative inputs and the pinned six-source build graph; `data/EXPECTED.json` contains replay-derived outputs. `check_declarations.py` confirms they reconstruct `data/SPEC.json`. `PLAN.json` and `OWNERS.json.gz` specify all 34,560 literal helper roles.

| Provider | Residual width inventory | Directed phase edges |
|---|---|---:|
| jp8 | 4:24, 5:48, 7:24, 8:122, 9:262 | 3067 |
| ck | 4:24, 5:48, 7:56, 8:102, 9:250 | 3156 |

The exact global profile is `{1:183828,2:33272,3:31230,4:11376,5:3440,6:288,7:78,8:576,16:1,48:2230}`. Live stock is 7168, physical stock is 7658, rank mass is 520704 and deficit is 2560. The owner map was nominated with a restricted pattern/flow model and bipartite edge colouring; no global packing optimality is claimed.

## Reproduction

Python 3 with assertions enabled suffices for verification. Fetch the six source packages at the commits recorded in `data/WITNESS.json`. Put their repository worktrees under `SOURCE_ROOT/pr531`, `pr568`, `pr569`, `pr571`, `pr575` and `pr583`, then run:

```sh
python3 -B research/signed-root-k480/check_declarations.py
research/signed-root-k480/verify.sh /tmp/signed-root-k480-replay SOURCE_ROOT
```

The shell entry point first runs the signed-schedule reproduction and 16 controls, then the unchanged strict 64-stage verifier. The latter rebuilds the baseline and both local providers, without reuse, before literal ownership admission, the finite invoice, both rational moment engines and all inherited controls. A successful run produces `RESULT.json` and `RECEIPT.json`; schedule controls are in the adjacent `.schedule-controls.json` file.

For explicit source paths, call `verify.py --work NEW_DIRECTORY --jobs 2` with the six `--source NAME=PATH` options listed by `verify.sh`, and run `check_schedule.py --hamming PR531/research/direct-delivery504-global/inputs/hamming --out NEW_JSON` separately. On a shared Linux workstation, prefix heavy commands with `nice -n 15 ionice -c 3`.

`SIGNED-ROOT-PROOF.md` explains the transformation, exact checks and limitations. The `history/` directory retains the predecessor's proof notes; their historical counts and bounds describe their named fixtures, not this witness. The sibling audit directory records actual runs separately from the frozen package.

Prepared by Jeremy Diviney with substantial OpenAI Codex assistance; full predecessor attribution is retained in `NOTICE.md`. The inherited all-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape, analytic transfer and bit H1–H5 assumptions remain. This is finite exact evidence, not a full Lean proof or practical multiplication speedup.
