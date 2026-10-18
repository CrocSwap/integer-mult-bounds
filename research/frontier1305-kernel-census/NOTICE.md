# Notice

`inputs/BASE-WORD.json.gz`, `inputs/EXTRA-WORD.json.gz` and `inputs/CONTROL-WORD.json.gz` are unmodified copies of
files from PR #1297 (rohanarun, head 4abf710a7f0d2a46f522f3f13c15769d003f9495, research/global-mixed-four-cold-kernels/),
Apache-2.0, with that package's retained ancestry (#1286, #1274 Jeremy Kothe, #1218, #1193 Jeremy Diviney, #1148 Thomas
DiFiore, #1196 chafreaky, #1195, PR564/571/589/645 lineage). The base and extra words are the same Git blobs in PR #1305
(jeremykothe2, head a96a5d959672752026292ba5024664b436879fe7). Exact pins: inputs/PINS.json.

`census.py` is an independent re-implementation of the relation rule of #1297's `search_relations.py`, with its edit
format, extended to pivots never written in B and to a before-first-write restoration. `idle_optimum.py` re-implements
#1305's `idle_overlay.py` group enumeration with exact axis selection; its admissibility class is #1305's
`verify_idle_overlay.py` (adapted there from Gonzalo-Mier's #1252). `price.py`, `deletion.py` and `retime.py` call the
pricing harness of PR #1186 (research/exact-frame-toolkit), which is not vendored here.

New files: Marius-Paul Dumitrean, Apache-2.0, prepared with substantial AI assistance (Anthropic Claude, via Claude Code).

Revision 2 (2026-10-14) answers the maintainer's review continuation point on #1337 (Mister-Meeseeks, [batch review](https://github.com/CrocSwap/integer-mult-bounds/blob/main/docs/research/community-efficient400-review.md)). It re-prices the evidence with PR #1186 revision 2's true-moment interval certificate (head 3855fd41). Prepared with substantial AI assistance (Anthropic Claude, via Claude Code).

Revision 3 (2026-10-14) re-pins `regenerate.py` to PR #1186 revision 3 (head c37dfb07) and moves `deletion.py` to that toolkit's `compat.deadline`; the evidence is unchanged. Prepared with substantial AI assistance (Anthropic Claude, via Claude Code).
