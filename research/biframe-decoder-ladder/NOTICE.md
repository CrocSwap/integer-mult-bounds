# Notice and credits

Apache-2.0, as the repository.

Submitted from the GitHub account of Josie Elliston (@JosieElliston), who started the session and approved
the submission. The research, proofs, code and write-up were produced by Claude Opus 5.5 (Anthropic) via
Claude Code. No independent human review or formal proof is claimed.

Predecessor and concurrent work:

- **themilkman216, #968** (merged 2026-10-13):
  - the frame-pair explanation of #717's decoders;
  - the exact 8-term floor, with attainment at every p ≤ 24;
  - the 896-of-1260 family;
  - the favorable budget on T37 (+5.51% b; bit-cap margin about 1.33%).

  Section 5 of the README is an independent re-derivation of that result and is credited to #968.
  Sections 2–4 address #968's open construction question and use its budget figures.
- **DreamingOfClouds, #717** (format limits part 2):
  - the B14 complex decoder model and the D1–D3 floors and walks;
  - the 11 decoder files vendored under `inputs/pr717-hits/`;
  - the center semantics of S4;
  - the helper exchange rates (P3) cited in §4.

  The D3 decoders, and the observation that P104 reaches 56, belong to #717.
- **DreamingOfClouds, #595** (merged; `research/format-limits-corrected/`): the certified ceiling code
  (`cert.py`, `skel.py`, imported in place) and the pairing-rank decoder formulation.
- **DreamingOfClouds, #446**: Theorem C, the pairing-rank price of a copy tree.
- **Joel Pulikkan / GamingPuzzled, #620**: the E8 decoder floors and the P112 frame decoder of cost 64.
- **The hub's E8 complex unit lineage and the selected supplier chain** that #968's budget is priced on.
- **The original OpenAI #109 framework**, unchanged under `upstream/`.
