Apache-2.0 (see `LICENSE`). Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

Objects of study that are other people's work:
- `data/t7669.json.gz` (sha256 `838da0f9…`) is our replay, in our word-file format, of the P104 native word of PR #7669
  (SYLforge), which builds on the K372-2 word and on PR #7660 (Clear1nsight). The replay reproduces #7669's kappa on
  #7669's own caller exactly; here it is priced under the #7113 caller.
- `data/7113_CALLER.json` (sha256 `255d89f3…`) is the 17-call signed caller of PR #7113 (rohanarun), written in the
  `mixed-root-caller/1` format read by `tools/pricekit.py`.
- The Lean closure contains, unchanged, the earlier P104 Lean library that the crossing statements import, including the
  Bridge7761 modules that encode facts about PR #7761's graph (Clear1nsight), as shipped in our PR #7796.
This package states and checks facts ABOUT those constructions; it does not replace or endorse them.
`data/w_s4.json.gz` (sha256 `fa1a8dad…`) is our own test word (a rebuild stacked on our PR #7623 native).
The Lean sources, generators, PRICEKIT and checks are ours; toolchain and Mathlib pin are those of the earlier Lean packages.
