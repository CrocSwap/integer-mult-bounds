# Notice

Prepared by Marius-Paul Dumitrean with substantial AI assistance (Anthropic Claude, via Claude Code). New files are under
the repository's Apache-2.0 license.

The toolkit imports or ports, unchanged in substance:

- the frame-domain model and moment engines of `research/frame-domain-ceiling` (prepared for chafreaky), whose
  `vendor/static44/gk` frame algebra `frames.py` imports;
- the k492/multicold moment, base-two and outer engines (`research/complex-k492-owner-repair/vendor/multicold`) and their
  credited lineage, including DreamingOfClouds' engines, eumemic and the PR551/552/558/559 contributors;
- icekylinx's #645 `independent/audit_local.py` (lineage audit, imported by `writeback.py`, `model.py`, `controls.py`);
- Tekalign's `research/pr699-frame-retiming/independent_frames.py` recount, ported verbatim into `word.recount`;
- BRoute's `construction/sw4/build_sw4.py` exchange moves, ported into `exchange.py`;
- NewBArch's #869 `build_tri.py` edit semantics, followed by `harness.compile_edits`;
- Rohan Arun's #987 slot search and the #1018 seven-slot recipe (Jeremy Kothe, MineB), the default input of `slots.py`;
- PR635's native local chain (`research/complex-sw4-frame8/vendor/pr635`), run by `native.py`;
- the gauge44 discovery/freeze witness protocol (#645 lineage) and Hao Yan's #858 T16 controller package, driven by
  `rebind.py`, `unpin.py` and `t16_discover.py`.

The k8 words used by `selftest.py` are Jeremy Kothe's mutable-leaver construction (#1004/#1005) with the #1018 slots, read
from the retained #1042 and #1094 replay archives. No upstream file is modified.

Revision 2 (2026-10-14) responds to the maintainer's review continuation point on #1186
([batch review](https://github.com/CrocSwap/integer-mult-bounds/blob/main/docs/research/community-efficient300-review.md),
Mister-Meeseeks): it adds the true-moment interval certificate, the exact integer dual path and the qualified wording. The
harness compensation check fixes a screen gap found by this author during a later pivot search on #1319's words; the
program semantics it follows are those of the unchanged `independent/audit_local.py` (icekylinx, #645). Prepared with
substantial AI assistance (Anthropic Claude, via Claude Code).

Revision 3 (2026-10-14) makes the toolkit run on Windows. It answers woklerx's independent audit of revision 2
([#1186 comment](https://github.com/CrocSwap/integer-mult-bounds/pull/1186#issuecomment-6169503528)), which found that
`harness.py` imported the Unix-only `resource` module. Prepared with substantial AI assistance (Anthropic Claude, via
Claude Code).
