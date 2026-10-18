# NOTICE — attribution and licenses

Contributor: **Aaron Wang**, with help from opencode (substantial AI assistance
in scoping, implementation, verification and writing; no model named; no
independent human review claimed). Apache-2.0; all source licenses and notices
are retained.

Predecessor credit (authors verified against current ground truth with
`gh pr view NNN --json author,title` at writing time):

- [PR 2542](https://github.com/CrocSwap/integer-mult-bounds/pull/2542) by Aaron
  Wang (navinor): the audited claim "No 17-point set covers `F2^7`", the
  pair-representation identity and the length-18 exclusion.
- [PR 2773](https://github.com/CrocSwap/integer-mult-bounds/pull/2773) by Aaron
  Wang (navinor): the 17-point cover audit, the sharp collision-multiplicity
  rows, the Sidon/near-Sidon census floors and the exact remainder rows
  `(5,1),(6,0)` this package decides. Its `cover17.py` and `search17.py` are
  vendored byte-exact under `vendor/` (SHA-256 pins enforced by
  `test_engine.py`), copied with `agent_tools.py pr-tree-extract`, never
  imported from the predecessor package.
- [PR 2634](https://github.com/CrocSwap/integer-mult-bounds/pull/2634) by Aaron
  Wang (navinor): the recorded KB3b state (REPRO tiers, L=20 campaign and
  census) reproduced here before new work.
- [PR 2691](https://github.com/CrocSwap/integer-mult-bounds/pull/2691) by
  Nicholas Stone (NicholasStone, Kimi agent): the completed `(10,10)`
  simple-20-cycle census (recorded state, not re-run).
- [PR 943](https://github.com/CrocSwap/integer-mult-bounds/pull/943) by Ross
  Richardson (RossRichardson): the prefix-walk model (`S + S = F2^n`
  covering condition).
- [PR 1185](https://github.com/CrocSwap/integer-mult-bounds/pull/1185) by Doug
  Colkitt (Mister-Meeseeks): the pinned record `f(5) = 12`, `f(6) = 16` and the
  `f(7)` gap, plus the frozen tier `EXPECTED.json` reproduced here.
