# Notice

Apache-2.0, as the repository. Prepared by Marius-Paul Dumitrean with substantial AI assistance (Anthropic Claude, via
Claude Code), which ran the searches, wrote the scripts and drafted this text; every reported number was re-checked by
the scripts in this package and by the unchanged predecessor code they call.

## Sources and credit

- **Construction this result modifies:** PR1319 (Rohan Arun), `research/global-mixed-t74-exact-fill`: T74 exact fill of
  the four-kernel construction (owners, dispatch, parent, strict replay, geometry controls). Its owner map, dispatch,
  parent template, construction recipe and idle remainder are reused byte-for-byte; only the two local words change.
- **Local words edited:** PR1297 (Rohan Arun) final words `gauge44-word.json.gz` and `extra-word.json.gz`, vendored in
  PR1319; their lineage includes PR1286 (Rohan Arun), PR1274 (Jeremy Kothe, first helper-donor cold kernel), PR1218,
  PR1193 (Jeremy Diviney, mixed-provider flow), PR1148 (Thomas DiFiore / tomdif, joint entrances), PR1195
  (Marius-Paul Dumitrean, source-holder fusions), PR1196 (chafreaky) and the retained X54, owner and PR589 bit lineage
  named in those packages. (PR1319's credit line groups PR1195/1196 under Thomas DiFiore; GitHub lists their authors as
  above.)
- **Mechanism:** the helper-donor cold kernel of PR1274/PR1286/PR1297 (delete a cold pivot's early read; compensate the
  exact output difference with dyadic windows). This package's kernel uses a helper window restored in the early cleanup
  after the pivot's own restoration, two donor windows and two direct reads.
- **Search and pricing:** PR1186 exact frame toolkit (frames, harness, kappa) and PR1337 census (Marius-Paul Dumitrean),
  extended with feasible-slot screens; PR1431 (Hanson Sun / bbMisk) pivot-440 window analysis informed the scope.
- **Refined assembler (vendored, unchanged):** `vendor/pr1549/code/{assemble.py, fine_mercator.py, fine_moment.py,
  oracle_check.py}` from PR1549 (midhatn) head `f98c217351`, which builds on PR1536 / PR1479 / PR1458 / PR1444 / PR1377
  (Jeremy Kothe) and PR1424 / PR1464 / PR1485 (Rohan Arun); the fine Mercator parity repair follows PR1519 (philippeVV).
  Git blobs: assemble.py ea936f80, fine_mercator.py d42655db, fine_moment.py a81478d0, oracle_check.py 756f370d.
- **Unchanged repository code called:** `research/gauge44-frames-x/independent/audit_local.py` (PR645 lineage
  independent local audit) and the retained multicold moment/outer engines
  (`research/complex-k492-owner-repair/vendor/multicold/engines`).

## Revision 2 (2026-10-14)

Revision 2 answers the maintainer's batch review of this PR
([community-efficient700-review.md](https://github.com/CrocSwap/integer-mult-bounds/blob/main/docs/research/community-efficient700-review.md),
Mister-Meeseeks). It adds `RESTORATION.md`, `kernel_check.py`, `interfaces.py` and the ancestor stages of
`replay_full.py`. The ancestor stages run Rohan Arun's unchanged PR1319 scripts (`reconstruct.py`, `lift_parent.py`,
`replay.py`, `geometry_controls.py`) and PR1297's `verify.py`, binding regenerated containers by payload. PR1319's
package is not modified. `kernel_check.py` follows the program semantics of icekylinx's unchanged #645
`audit_local.py`, reimplemented independently. Prepared with substantial AI assistance (Anthropic Claude, via Claude
Code).
