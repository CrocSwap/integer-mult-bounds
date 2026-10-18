# Combined h4a and factored cold ends

The conditional finite-construction saving is
**κ = 0.001636269762440408**, exactly
`204533720305051/125000000000000000`; the conservative calculation gives
`0.001636269759573274`. This exceeds pinned PR635's
`0.001636241501576388` by `0.000000028260864020`.
No latest-frontier or global optimality claim is made.

The JP8 word combines PR629's four dimension-eight cold ends with both of
PR627's dimension-seven factored cold ends. Simple concatenation fails. One
additional same-frame absorption and ten rank-zero basis corrections resolve
the exact compatibility defects, after which an exact FULL-frame remainder
restores all other registers. [PROOF-COMPOSITION.md](PROOF-COMPOSITION.md)
explains the repair and its independent Fraction proof.

The literal dispatch is **71 JP8 / 1 CK**, with CK at chronological call 5.
Both suppliers retain 492 helpers; there are 35,424 hosted roles, 7,168 live
rows and 7,670 physical rows. Rank mass remains 520,704 and deficit 2,560.
The whole profile, including the simultaneous owner packing, is recomputed by
strict exact engines. Search objectives and integrality guesses are not used
as certificates. The map exporter and search settings are retained in
[owner-search/](owner-search/README.md). Retained `data/cand.json` and
`data/search/` describe PR629's historical search, not the new owner nomination.

All core files in `code/` and `verify.py` are byte-identical to pinned PR629
`9f3b92d06ba876ce7101238882d35565993eca57`. The six pinned external sources
are vendored; their original manifests and notices are preserved. The exact
source roles and hashes are recorded in [PROVENANCE.json](PROVENANCE.json).

## Reproduce

Python 3.10 or newer is required; the Python checks use only the standard
library. The frozen baseline also requires a C++ compiler and Boost headers.
Run from the repository root, choosing a new output directory:

```sh
PYTHON=python3 sh research/combined-cold-ends-20261013/witness635/verify.sh /tmp/combined-cold-ends-fresh
```

The wrapper checks declarations, builds the frozen baseline and both provider
chains, replays arbitrary dirt and both orientations, checks wrappers and
exact phases, then admits the physical owner controller, finite invoice, two
moment engines and strict outer inequalities. It also runs the independent
composition proof, a positive control and twelve repair corruptions, both
nomination exporters, and the separate native-width/owner/rational-moment
checker with five rejection controls under isolated optimized Python.

`MANIFEST.json` binds this complete input package. The complete fresh replay
passed all **64 stages**, with no reused baseline or local supplier results,
and confirmed the bound above. Independent proof, twelve composition mutations,
five owner mutations, declaration reconstruction and both exact nomination
exporters also passed. [Retained validation](../validation635/README.md) includes
the complete replay archive, receipts and environment details.

The validation preserves the executed commit, manifest and README. This README
was subsequently updated only to report completion; all other 320 manifested
inputs remain byte-identical. The [documentation update record](../DOCUMENTATION-UPDATE.json)
binds both manifests and verifies that distinction.

The package-specific
SPEC verifier is authoritative for this replay; the input-only WITNESS and
output-only EXPECTED declarations independently reconstruct SPEC exactly.

## Scope and credits

This is a conditional finite certificate. All-size compilation, common-label
and mutable-source realization, whole-call hosting, precision/tape/exact
recovery, analytic transfer and bit H1–H5 remain inherited assumptions. PR543's
bit supplier is cited and repriced, not rebuilt. This is not a full theorem
formalization, a practical speedup or an optimality proof.

Chi Zhao prepared the combination, exact compatibility repair, owner
nomination and validation with substantial OpenAI Codex assistance. Jeremy
Diviney contributed PR627's factored ends; Jeremy Kothe contributed PR629's
h4a construction and the K-triangle lineage; DreamingOfClouds contributed the
cold-end framework; Chafik Boukhalfa contributed PR632's packing baseline and
PR626's separate rational interval engine; Jeremy Kothe supplied PR635's stronger owner nomination, independently transferred to this native word and further repaired; eumemic contributed the unchanged
PR543 bit supplier. All cumulative attribution and licenses in
[NOTICE.md](NOTICE.md) remain.
