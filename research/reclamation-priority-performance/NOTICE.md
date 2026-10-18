# Attribution and license

Prepared for **Peter Carpenter (PeterCarp320)** with substantial assistance
from **OpenAI Codex (GPT-6 Astra)**, including experiment selection,
implementation, equivalence argument, testing, measurements and documentation.
No independent human mathematical review is claimed. New material is supplied
under the repository's Apache-2.0 license.

The original source files and their notices remain unchanged:

- **eumemic** supplied the PR57 joint compiler and identified repeated sorting
  in `acquire` as an unchanged bottleneck in PR154.
- **Chafik Boukhalfa (chafreaky)** supplied descending-rank reclamation and its
  exact integration, with OpenAI Codex assistance. His **PR175** already
  replaced whole-set sorting with ordered per-rank lists and correctly moved
  retired anchors when clearing changes their frames. That contribution is
  incorporated in an archived prerequisite, as the review ledger records.
  This package does not claim that ordering optimization as new.
- `reference-pr175.py` preserves the exact compiler bytes from PR175 commit
  `f1081fabbfadaaaaf7292a40d428dbbb865ce920`, SHA256
  `f0696953d057239ed5a75e28d857b814d43ca43deaaf7b7b8fd191aa115112ff`.
  Its original compiler credits and the root Apache-2.0 license apply.
- **Rohan Gupta** supplied the PR55 dual-skip producer. The PR48 fixed-basis
  geometry and preceding compiler/graph contributors retain their existing
  attribution in `research/joint-dual/` and `references/frame-compiler/`.
- **rfu08's PR64 audit** identified the cancelling-scatter failure covered by
  the retained independent replay and regression controls.

The new contribution is exact coordinate-membership filtering before ordered
iteration, its equivalence argument and complete same-input comparison against
both the base compiler and PR175. PR367/452/662/667/672/707/709/721/727 address
other verification workloads and are not dependencies.

The accepted selected result at the base commit is #626/#543, conditional
κ = 51110230636731/31250000000000000. This package concerns the historical
joint-dual verifier; neither the selected frontier nor `upstream/` is edited.
