# NOTICE — attribution

Agent: **Aaron Wang**, with help from opencode (substantial AI assistance in
scoping, implementation, verification and writing; no model named; no
independent human review claimed). Apache-2.0, same as the repository.

- The audited claim "No 17-point set covers `F2^7`", the pair-representation
  identity (`lemma_a_table`) and the length-18 exclusion are from
  [PR 2542](https://github.com/CrocSwap/integer-mult-bounds/pull/2542) by
  Aaron Wang (navinor), package
  `research/universal-f7-singleton-seedb859517b`. Its `engine.py` is vendored
  byte-exact as `vendor/pr2542_engine.py` (SHA-256
  `82e4c407b58864c74ffd14d47f00b6b1675005ee0e0173909b7bd092491175e4`).
- The recorded KB3b state (search campaign ceilings 120/126/128, the
  cover/walk dichotomy, the resumable 20-cycle census and its open remainder)
  is from [PR 2634](https://github.com/CrocSwap/integer-mult-bounds/pull/2634)
  by Aaron Wang (navinor). Its `test_lemma_rows_survive_at_L20` already pins
  `lemma_a_table(7, 10, 7)` as feasible.
- The completed (10,10) simple-20-cycle census (15/15 shards) and the released
  independent audit of PR 2634 are from
  [PR 2691](https://github.com/CrocSwap/integer-mult-bounds/pull/2691) by
  Nicholas Stone (NicholasStone, Kimi agent, substantial AI assistance).
- The prefix-walk model is
  [PR 943](https://github.com/CrocSwap/integer-mult-bounds/pull/943) by Ross
  Richardson (RossRichardson), `research/universal-connector-boundary`.
- The pinned record `f(5) = 12`, `f(6) = 16`, `18 <= f(7) <= 24` is
  [PR 1185](https://github.com/CrocSwap/integer-mult-bounds/pull/1185) by Doug
  Colkitt (Mister-Meeseeks), `research/universal-connector-six-source`.

Nothing here claims a kappa, supplier, certificate or selected-frontier
change. No word-level census is performed; the repeated-state L=20 word
question belongs to the concurrent claim (discussion 1166 comment 18954844).
