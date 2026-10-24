# Attribution and provenance

The unchanged files `vendor/pr4688/verify.py` and `vendor/pr4688/README.md` come from `research/complex-two-image-hook-prefix/` in lee-phys's CrocSwap/integer-mult-bounds PR #4688, commit `264c4b3cb13c82d171de352ecf60486dfb8d2bd4`. Their mathematical construction, model, rank engine, calibrations and seven controls are credited to that work. This package's main checker reuses the engine's sparse Gaussian arithmetic and exterior-power routines.

Jacob Sussman's PR #4628, commit `ee4fd87f064017c23e5a86fc1dcfe0a5237caed3`, and its source repository jacobalansussman/wht-power-saving-lean, commit `86e575e28ed94890872dcff1bb2621d7ff559cbd`, are the sources of the block-3 engine model, the 14W/5 hook bound, the single-image obstruction and the singular-frame subgame motivating the phase repair. The present obstruction uses an explicit joint-target rank and does not depend on an unimplemented singular-frame theorem.

New work in this package: the fresh-input target-deficit obstruction; the explicit S U S / S V S phase repair; the exact joint-rank and four-point-pencil calculations; the higher-width lifted-hook argument; and the independently checked residual interface when included. This work was produced by OpenAI Codex agents acting for Lyy-iiis. No contribution by the predecessors is claimed as new, and no Lean or human verification is claimed.
