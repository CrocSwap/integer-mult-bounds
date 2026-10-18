# NOTICE - attribution and licenses

Contributor: **Aaron Wang**, with help from opencode (substantial AI
assistance in scoping, implementation, verification and writing; no model
named; no independent human review claimed). This package is contributed
under the repository's Apache-2.0 license; see the root `LICENSE` and
`NOTICE` files. The vendored files retain their source licenses and are
reproduced byte-exactly with SHA-256 pins (see `SOURCES.json` and the byte-pin
checks in `test_engine.py` / `verify.py`).

Predecessor credit (every cited PR author verified against current ground
truth with `gh pr view NNN --json author,title` at writing time):

- [PR 943](https://github.com/CrocSwap/integer-mult-bounds/pull/943) by Ross
  Richardson (RossRichardson) - the prefix-walk model and the
  `P + P = F2^n` covering condition this whole question lives in.
- [PR 1185](https://github.com/CrocSwap/integer-mult-bounds/pull/1185) by
  Doug Colkitt (Mister-Meeseeks) - the pinned record `f(5) = 12`,
  `f(6) = 16`, `20 <= f(7) <= 24` and the frozen tier `EXPECTED.json`
  reproduced as an anchor.
- [PR 2542](https://github.com/CrocSwap/integer-mult-bounds/pull/2542) by
  Aaron Wang (navinor) - the length-18 exclusion and the claim "No 17-point
  set covers `F2^7`"; its REPRO tiers and length-18 census are reproduced
  here as anchors.
- [PR 2634](https://github.com/CrocSwap/integer-mult-bounds/pull/2634) by
  Aaron Wang (navinor) - the recorded KB3b state and the bounded-search
  precedent (20-point covers abundant; no 19-point cover in 200 restarts,
  max `124/128`) that this package's class-restricted searches are compared
  against.
- [PR 2773](https://github.com/CrocSwap/integer-mult-bounds/pull/2773) by
  Aaron Wang (navinor) - the split-by-split audit, the Sidon/pair-sum budget
  enumeration (`cover17.py` / `search17.py`, vendored here byte-exact as
  `vendor/agent64_cover17.py` / `vendor/agent64_search17.py`), the census
  floors and the n5 control value `99,200` this package's independent
  `C(32,10)` census reproduces.
- [PR 2870](https://github.com/CrocSwap/integer-mult-bounds/pull/2870) by
  Aaron Wang (navinor) - the odd-coverage Fourier/Parseval identity
  (OBSTRUCTION `696/504/192`, reproduced) and the resumable anchor driver
  `anchors.py` (vendored byte-exact, re-walked from empty receipts).
- [PR 2911](https://github.com/CrocSwap/integer-mult-bounds/pull/2911) by
  Aaron Wang (navinor) - the immediate predecessor: the `(A, D)` reduction
  lemma, the squeeze/deficit bookkeeping, the per-character profile system
  and its no-vanishing sub-case (the vanishing-character restriction this
  package presses), the row remainder `808/501/251/196` and the open
  questions 1-2 that name this step. Its engine `cover18.py` is vendored
  byte-exact as `vendor/cover18.py`.
- [PR 2691](https://github.com/CrocSwap/integer-mult-bounds/pull/2691) by
  Nicholas Stone (NicholasStone, Kimi agent) - the completed `(10,10)`
  simple-20-cycle word census; recorded state only, not re-run here. His
  concurrent repeated-state `L = 20` word claim (discussion 1166 comment
  18954844) is a different (word-level) object and is untouched.

Vendored files (byte-exact, enforced by byte-pin checks):

| Local path | Source | SHA-256 (prefix) |
|---|---|---|
| `vendor/agent64_cover17.py` | PR 2773 `cover17.py` (via PR 2870/2911's pinned vendor/) | `082bc838134cba97...` |
| `vendor/agent64_search17.py` | PR 2773 `search17.py` (via PR 2870/2911's pinned vendor/) | `9eb1bf79ffb99b0e...` |
| `vendor/cover18.py` | PR 2911 `cover18.py` | `24c6a2f4911dc2d5...` |
| `anchors.py` | PR 2870 `anchors.py` | `73d73a9b94539403...` |

Predecessor packages were read byte-exactly from their PR heads with
`agent_tools.py pr-tree-extract` and were never imported at runtime.
