@Arham-Tahir64 thanks, good catch: the provenance bridge is missing from the package. The 603 rows are produced in two stages:

1. **Generator.** The slack-k landscape, run with K = 7. The pipeline is DP, then the symmetric LP, then Basis-kill (S66+t), then Pencil, then the e = 2 triple rule. It is the same pipeline as land3 / land4 and reproduces 8 / 47 / 133 survivors at slack 3 / 4 / 5, then 333 at slack 6 and 662 at slack 7.
2. **Dominance by earlier span results.** A row is removed if some e-subset B of its pieces has Σ g(w) < 53 (Lemma B), packs into a configuration with a known span bound span ≤ d − 1, and the configuration is one of:
   `(6,6)+1 ≤ 3`, `(6,6)+2 ≤ 4`, `(6,6,3)s0 ≤ 4`, `(7,4)s0 ≤ 4`, `(7,5)s0 ≤ 4`, `(6,6,4)s0 ≤ 5`, `(6,5,4)+1 ≤ 4`, `(6,4,4)+1 ≤ 4`.
   The 603 are the d ≥ 4 survivors of this filter.

Your example, d = 5, [6^6,5,4], e = 3, is removed in stage 2. B = {6,5,4} has Σ g = 20 + 12 + 8 = 40 < 53, and it packs into (6,5,4)+1, whose span is ≤ 4 = d − 1.

Caveat: those eight span bounds come from earlier span runs, and they are not re-derived in #2985. Some had a second implementation (S66) and some only one. I'll attach the generator, the dominance filter, the span-fact list with each fact's run logs, and a script that reproduces rows_input.csv from them, as an artifact on this PR. That is an attachment only; no claim in the PR changes.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0.
