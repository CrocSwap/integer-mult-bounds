# Coordinated owner repacking of PR622

Base: PR622 commit `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`, independently reproduced through all 64 fresh stages, with no reused baseline or providers. The new map preserves all 72 calls, all 492 helper identities and widths in each call, the invocation order and capacity inventory, and the jp8 ×65 / ck ×7 dispatch.

## Result and scope

- Conditional κ: `408856367695223/250000000000000000` = **0.001635425470780892**.
- Conservative κ: **0.001635425467912872**.
- Native complex lower: `1638104468552563164027/1000000000000000000000000`.
- Global paid profile: `{1:181580,2:29864,3:31265,4:11521,5:5040,6:576,7:1,8:576,22:1,48:2213}`.
- Spare-rank profile: `{1:128,3:17,4:1,7:1,22:1,48:2213}`; total spare rank **106,436**, unchanged.
- Live 7,168; physical 7,670; deficit 2,560; paid rank 520,704; hosted residuals 35,424.

There are 5,027 changed owner placements and 3,146 additional offset changes from prefix-packing those bins: 8,173 changed role records in total. The helper identity, width, time, stage and replica fields are unchanged. Moves are simultaneous; the exporter validates the final map before writing output.

The changed packing stays within PR622's supplier family. It does not change any of PR622's 504-to-R generalization sites or the K-triangle constructor. All-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape/exact recovery, analytic transfer and bit H1–H5 assumptions remain. The cited PR543 bit supplier is repriced but not rebuilt in the package replay. No optimal packing, unconditional multiplication theorem or complete Lean proof is claimed.

## Reproduce the nomination

```sh
python3 -B research/complex-571-cold14-k492/tools/replay_repacking.py \
  --base-data /path/to/pr622/research/complex-571-cold14-k492/data \
  --out /tmp/k492-repacked
```

Compare PLAN bytes and decompressed OWNERS payloads with this package. The exporter checks immutable input hashes, each original placement and width, final family uniqueness, windows, capacity, exact rank mass and output content hash. It refuses `-O` before creating output. These are nomination checks; the unchanged independent physical auditor and exact arithmetic remain the admission boundary.

## Fresh strict admission

Use the immutable source packages in the inherited README and SPEC. The first five source commits are PR568 `71c99ac935a33bb7b59a1b4a7af8725a939b0b90`, PR571 `b7bdc5a8de18fcf418cfb9c7d83a2b1097a5e4a3`, PR569 `897213a855b7fb8a1b8b0e552a2f5c42e6c1b326`, PR575 `eac6f7e378ab622dac50a2fd4b7ef6eab014de44`, and PR583 `89be768f0157f5a3d8e4db69cf1748768605eac9`. The direct-delivery source is independently pinned by manifest `c1997405c5c0ccd9bdb0a30b0eb9a5a2dc7dc7ce7b59c6a83a2152b80f6410d1` and the three used input hashes in SPEC.

```sh
python3 -B research/complex-571-cold14-k492/verify.py --jobs 2 \
  --work /tmp/k492-repacked-fresh \
  --source multicold=/path/to/pr568/research/complex-multicold \
  --source structural_gain=/path/to/pr571/research/structural-gain \
  --source larger_gain=/path/to/pr569/research/larger-gain \
  --source joint_prefix=/path/to/pr575/research/complex-joint-prefix \
  --source frame_coalescing=/path/to/pr583/research/kernel-frame-coalescing \
  --source direct_delivery=/path/to/direct-delivery504-global
```

This rebuilds all providers, checks the changed-helper-count controls, runs the independent owner audit, reprices both exact moment engines and checks the strict outer constraints. WITNESS's input hashes and EXPECTED's global fields are synchronized from the package's recomputed SPEC values; expected values are never hand-tuned mathematical inputs. Source review and raw stage logs are in the sibling audit directory. Its shared-regression record identifies the exact checkout used for the broad repository suite separately from the new package's fresh replay.

## Search provenance

Simple consolidation and three million single-helper swap trials found no gain on PR622. Simultaneous one-/two-helper exchanges (three million trials, seed 0, temperature 1) produced the new spare-rank profile. A ten-million-trial seed-1 continuation found no further gain. A 60-second restricted model, choosing each changed helper's original or proposed owner and fixing only the global spare-rank profile, reduced 11,626 placement changes to 5,027. A subsequent solve over those retained choices found no smaller map. These are restricted nomination searches, not an optimum over physical owner maps.

The floating entropy score guides discovery only. The final recipe and standard-library exporter provide a deterministic reconstruction route without a solver. Search scripts, intermediate maps and settings are retained in the sibling audit directory. Supplier construction credit remains with jeremykothe2, DreamingOfClouds and all predecessors named in NOTICE. This repacking was prepared by Jeremy Diviney with OpenAI Codex assistance.
