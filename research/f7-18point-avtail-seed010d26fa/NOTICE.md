# NOTICE - vendored engines and attribution

All vendored files under `vendor/` are byte-exact copies, extracted with the
shared toolkit (`agent_tools.py pr-tree-extract`) from PR 2961's package
`research/f7-18point-tight-classes-seed4c1e7b30` at head
`df2eba6c6c3dcc88b49b3b9a9c9c2e710710d7fd` (the head verified stable at
extraction and again before submission). They are read and executed as
vendored copies only; nothing is imported from a predecessor's tree at
runtime. Byte pins are enforced by `verify.py check_pins`.

| File | sha256 | Origin | Credit |
|---|---|---|---|
| vendor/tight.py | 14670ef2d3df9e4ecc9e1db962f4e8cb77545d1c889144352760c1fd14e2273b | PR 2961 (own engine) | Aaron Wang (navinor) |
| vendor/cover18.py | 24c6a2f4911dc2d5de76972eb5ae93dc4e66d8fa1e904443de6d0638e70c0a04 | PR 2911 | Aaron Wang (navinor) |
| vendor/vanish.py | 6c605c54074f725321c5d770d538a652bf7727598a128270831f92fe7b9746d9 | PR 2933 | Aaron Wang (navinor) |
| vendor/agent64_cover17.py | 082bc838134cba9754368cff894d53c729467a689b4cafee8374423688d93654 | PR 2773 | Aaron Wang (navinor) |
| vendor/agent64_search17.py | 9eb1bf79ffb99b0efcdaf57916c493bc781abd4a0096d584dc6bc6ca294bf674 | PR 2773 | Aaron Wang (navinor) |
| vendor/anchors.py | 73d73a9b94539403448d7ff8c914c03711907f75c019c4ccb6843b32c259e8e7 | PR 2870 | Aaron Wang (navinor) |

Model and record credit (read and reproduced, never re-derived):

- PR 943 (Ross Richardson, RossRichardson): the prefix-walk model and the
  `P + P = F2^n` covering condition.
- PR 1185 (Doug Colkitt, Mister-Meeseeks): the pinned `f(5) = 12`,
  `f(6) = 16` record and frozen tier `EXPECTED.json`.
- PR 2542 / 2634 / 2773 / 2870 / 2911 / 2933 / 2961 (Aaron Wang, navinor): the
  complete 17-point exclusion chain, the KB3b search ceilings (118/128 at
  k = 18, 124/128 at k = 19) and the existence of 20-point covers, the
  pair-representation rows, the odd-coverage Fourier/Parseval identity, the
  (A, D) reduction and vanishing-character restriction, the vanishing class
  classification with floors 41/44/45 for the classes decided/classified here,
  and the tight-class decisions whose open question 1 this package executes.
- PR 2691 (Nicholas Stone, NicholasStone, Kimi agent): the completed (10,10)
  simple-20-cycle word census (recorded state only).
- PR 2973 (Nicholas Stone, NicholasStone): the corrected word-census parity
  budgets (its corrected weight-parity census found a false-prune defect in the
  PR 2542/2634/2691 word engines and excludes L=20, recording
  `22 <= f(7) <= 24`) and its explicit scoping of the set-level chain
  PR 2773-2961 as unaffected; corroborated by PR 3005 (Nick Petalas,
  petalas, independent union-support implementation). All word-level work,
  untouched here.

This package is contributed by Aaron Wang with help from opencode (substantial
AI assistance; no model named; no independent human review claimed). Same
repository/source licenses apply; all retained lineage keeps its original
attribution.
