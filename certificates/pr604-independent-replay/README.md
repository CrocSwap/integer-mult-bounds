# Independent PR604 replay

Pinned upstream head: `1b795c5d7dea746ba310572585c0ef067574b4a6`.

The PR604 cold-end construction was independently replayed from its exact
head. The fresh run passed 55/55 top-level stages in 601.33 seconds, with
provider dispatch ck×44, atm3×22 and jp8×6. The resulting conditional rate is
κ = 0.00162128508944984, with conservative κ = 0.001621285086572193.

The audit checked all 55 stage log hashes and all 54 receipt-artifact hashes,
then rechecked the package manifest and SPEC hash. The exact final profile is
`{1:185792, 2:32576, 3:23600, 4:14128, 5:5040, 6:2016, 8:576, 32:1, 48:2094}`.
The run includes actual scalar words, arbitrary dirty restoration in both
orientations, both reflected ledgers, native frames, wrappers, all phase edges,
physical owners, a fresh invoice, both moment engines, assembly and negative
controls. The separate audit receipt records the source and output hashes.

The construction is a new cold-end architecture relative to PR601: fourteen
factory-scratch helpers per provider call finish at dimension-four frames after
an exact premix and guarded multi-gate cleanup. This is finite exact evidence,
not an unconditional theorem or practical speedup. The inherited all-size
compiler, common-label/mutable-source realization, whole-call hosting,
precision/tape/exact recovery, analytic transfer and bit H1–H5 assumptions
remain conditional; no Lean replay is claimed.

Sources are pinned to PR568, PR569, PR571, PR575 and PR583 as recorded in the
upstream receipt. The full source package is intentionally not copied here;
this directory preserves the independent audit outputs and hashes. Existing
published heads remain frozen. PR604 credits DreamingOfClouds and Claude
Opus 5.5; this independent replay and packaging used OpenAI Codex assistance.
