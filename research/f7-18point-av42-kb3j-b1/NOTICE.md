# NOTICE - third-party and predecessor sources in this package

All vendored engines are byte-exact copies (SHA-256 pinned in `SOURCES.json`,
enforced by `verify.py check_pins`). Predecessor work is credited here and in
`README.md`; nothing in this package claims it as new.

- `vendor/tight.py`, `vendor/cover18.py`, `vendor/vanish.py`,
  `vendor/anchors.py` - PR 2961 (Aaron Wang, navinor), extracted byte-exact
  through PR 3023's package via `agent_tools.py pr-tree-extract`. Bitmask
  primitives, the (7,1) Fourier identity, the reduced (A,D) covering model,
  Fourier profiles and squeeze numbers, vanishing-character class tables,
  the L7 Sidon tight-equality lemma, anchor helpers.
- `vendor/agent64_cover17.py`, `vendor/agent64_search17.py` - PR 2773
  (Aaron Wang, navinor), extracted byte-exact through PR 3023's package.
  Pair-representation shape primitives and 17-point search primitives.
- `vendor/parity_census.py`, `vendor/self_obstruction.py`,
  `vendor/split_census.py` - PR 3034 (Aaron Wang, navinor), extracted
  byte-exact with `agent_tools.py pr-tree-extract`. The complete reduced-
  covering census primitives, the (5,5) self-obstruction localization and the
  per-split complete census (m=5 ground truth).
- `PR3023-AVTAIL-PROGRESS.json` - PR 3023 (Aaron Wang, navinor), byte-exact
  copy of its merged walk receipts; the source of the CLASS82/CLASS60/AV51
  heavy-anchor read-backs.

Model and record: the PR943 prefix-walk model is
`research/universal-connector-boundary` (PR 943, Ross Richardson). The
pinned `f(5)=12`, `f(6)=16` record is `research/universal-connector-six-source`
(Doug Colkitt). The concurrent word-level gap `22 <= f(7) <= 24` is PR 2973
(Nicholas Stone, NicholasStone), corroborated by PR 3005 (Nick Petalas,
petalas); this package is set-level only.

Author attributions were verified against current ground truth at writing
with `gh pr view NNN --json author,title`. Prepared by Aaron Wang with help
from opencode (substantial AI assistance; no model named). Apache-2.0, same
as the repository.
