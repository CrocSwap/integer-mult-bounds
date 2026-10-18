# Attribution and scope of authorship

The banked pricing model, geometry inputs, rank-mass identities, packing
hypotheses, and original interval implementation belong to Dominik Scholz's
PR606 and its retained predecessors, with the disclosed OpenAI GPT-6 Astra
assistance in T3 Code. The engine is inherited from PR598. The full upstream
Niemeier and Leech attribution texts are preserved in `notices/`; they were
transferred from the pinned public NOTICE text, not represented as newly
authored research or as separately hash-authenticated upstream files.

The H6 interpretation and six originally quoted helper thresholds belong to
DreamingOfClouds / PR1590, prepared with Claude Opus 5.5 via Claude Code. The
subsequent public pricing supplement at commit
`b496aed769dd724cd1ff6b921cade626562be27b` belongs to the same author and is
cited as a later source clarification, not as this audit's implementation.

This new, bounded arithmetic audit and proof were prepared for Andrey Mas,
with GPT-6 Astra Pro research through ChatGPT. Codex selected/coordinated the
source input and is designated for later local mechanical replay. No Codex
mathematical derivation, independent human review, or formal verification is
claimed. Tests actually performed in this ChatGPT runtime are listed in
`RUN_LOG.txt`; later replay is not represented as already completed.

New work is limited to the twelve exact comparisons, a source-bound replay,
strict-threshold and maximality analysis, rational evidence, and rejection
controls. No new geometry, pricing model, compensation construction, physical
helper-capacity theorem, admitted supplier, or multiplication exponent is
claimed. The four files under `vendor/` have their original full-file bytes;
all other Python files are newly assembled narrow audit code, with the
interval method explicitly credited to the upstream authors.

The redistributed upstream source is Apache-2.0. A copy of that license is
included in `LICENSE`. Retain these attributions with derivative use.
