Apache-2.0 (see `LICENSE`). Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

The Lean sources are new. They formalise Lemma G of PR #484 (DreamingOfClouds), which reduces to PR #425's common-frame
conjugation lemma (jacklightChen / Zhihao Chen, OpenAI Codex), PR #458's one-helper rule and paid wrappers (chafreaky) and
PR #471's virtual entrance (Dugongue). The toolchain and Mathlib pin are those of `formal/lean` on main; the package layout
and axiom reporting follow PRs #487/#488 (jamesyc). `code/check_extended_labels.py` imports PR #484's
`research/e8-complex-gauge-kernel/code/lemmaG/lg_lib.py` (read-only) to load the emitted artefacts.
