# Independent PR610 replay

κ = 0.00162536523418317, conditional on the inherited framework.
The conservative value is 0.001625365231365566.

This audit pins PR610 to `d9dc50b46b20cb8f769dd85a851f8b31b0f8f695`.
Its jp8×71/ck×1 dispatch and literal owner map improve the independently
replayed PR604 value by about 0.252%. The scalar provider words and all
verifier code are unchanged from PR604; the unused atm3 chain is removed.
This is an independent audit of that construction, not a new construction.

The fresh replay passed all 41 top-level stages plus nine nested baseline
stages in 488.92 seconds, with no reused baseline or local outputs. It checks
all 728 scalar columns per provider, arbitrary dirty-helper restoration,
both native reflected ledgers, wrappers, exact phase edges, physical owners,
a fresh invoice, both exact moment engines, and 47 strict outer inequalities
per model. All 114 assembly controls pass.

The separate audit checked all 36 source-package blobs against the exact
GitHub commit tree, the package manifest and SPEC, 50 stage-log hashes and
49 receipt-artifact hashes. `SOURCE-BLOBS.json` is the package-only subset of
the pinned commit tree. `audit_replay.py` repeats those checks against a
fresh replay directory; it does not replace the upstream verifier.

To reproduce, acquire the exact PR610 commit and the five sources pinned by
its `research/complex-571-cold14/data/SPEC.json`: PR568 (multicold), PR569
(larger_gain), PR571 (structural_gain), PR575 (joint_prefix), and PR583
(frame_coalescing). Run PR610's `verify.py` with a new `--work` directory and
the five `--source NAME=DIR` paths, then run:

```sh
python3 -B certificates/pr610-independent-replay/audit_replay.py \
  --source /path/to/pr610/research/complex-571-cold14 \
  --work /path/to/fresh-replay --out /path/to/new-audit.json
```

The package retains the resulting receipt, assembly, controls, owner audit,
and invoice. Full source packages and intermediate replay logs are not
copied; their hashes are recorded. The PR543 bit profile is cited and
repriced, without rebuilding its bit circuit. The ck provider retains its
pinned PR571 ancestry. No GitHub CI or Lean replay is claimed.

This remains a finite conditional witness. All-size compilation,
common-label/mutable-source realization, whole-call hosting,
precision/tape/exact recovery, analytic transfer, and bit H1–H5 remain
assumptions. It is not an unconditional multiplication theorem or a practical
runtime claim.

PR610 and PR604 credit DreamingOfClouds with Claude Opus 5.5, building on
Jeremy Kothe's hyperplane-end work and the pinned packages by jeremykothe2,
DominikScholz, jon314159, chafreaky, eumemic, icekylinx, rohanarun, and the
contributors credited in the upstream notices and original OpenAI #109
framework. This independent replay, checker, and packaging were prepared
with OpenAI Codex assistance. Previously published heads remain frozen.
