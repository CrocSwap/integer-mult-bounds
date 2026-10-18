# Vendored files

Byte-for-byte copies; nothing here is modified. The sha256 and git blob ids are pinned in
`../deletion_ladder.py` (`VENDOR`) and checked before any use.

- `pr2423/verify_rehost.py`: Sagar Thakrar (@thakrarsagar), PR2423 head
  `13cd273dc13c98244b1f9bcf588b6e828cbc0347`, `research/bit-r438-transport-rehost/verify_rehost.py`.
  Apache-2.0. Prepared with Claude Code assistance. Its DP (`topk_dp`, `certify_optimum`), exhaustive
  enumerator (`exhaustive_topk`), Hall test, independent placement audit and `main` are imported, not rewritten.
- `pr2423/vendor/pr1043/`: Ali Romman (@aliromman), PR1043 head `e309e17f83f5759b1ea1fa24a76f24838784cb4d`,
  `research/bit-boundary-persistence/CERTIFICATE.json` and its `NOTICE.md`, copied unchanged via PR2423's
  `vendor/pr1043/` (where `verify_rehost.main` expects it). Apache-2.0; its notice states substantial OpenAI Codex
  assistance.

Main-tree inputs (PR1023 packing.py and engines, seed72 windows, seed14 placement, PR442 hosting_core, PR589 record
and selection) are read from `--repo` through PR2423's `PINS` (sha256 and git blob at canonical main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`).
