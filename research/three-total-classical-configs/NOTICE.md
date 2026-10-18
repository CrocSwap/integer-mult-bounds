# Notice

New work in this package: thakrarsagar, with substantial AI assistance from Claude (Anthropic, Claude Opus 5.5).
Apache-2.0 (`LICENSE`, identical to the repository root licence).

## Vendored files (unchanged copies, Apache-2.0, author DreamingOfClouds)

| path | source | sha256 |
|---|---|---|
| `lib/cr2.py` | PR #2162 head `113a718265c62aec301c5695f4bfb9c421bef7ab`, `research/char2-jets/lib/cr2.py` | `ff3c1bbd072c4d1f47158f903aa3ff4fcd8db5bbc4709c3d15b21a1815eef3bd` |
| `c/enumall.c` | PR #2162 head (identical to PR #2111 head `98da76c2839ba38538b510420dec54546ccabf0b`, `research/three-total-decoders/c/enumall.c`) | `55d864202535c22952e1a9080ad834f1908d18ff857c8dc26211e25a847d1fc8` |
| `data/tied_min.json` | #2111 / #2162 `data/tied_min.json` | `670ed90924b601ade22f0d4adaff46d1667e5449326a0f7ba7b88dd8f5906f93` |
| `data/cex_min_1.json` | #2111 / #2162 `data/cex_min_1.json` | `86064701dde94b4f35427bc3e19275eaf1e40e9e90d4fea28e7857f3564d4dd7` |
| `data/tm_noncr2.json` | #2162 `data/tm_noncr2.json` | `b5aa8ca01a87a898ae27160d5274af7ff08127cf0b27cf372f73a5725cd216a5` |
| `data/cr2_realisations.json` | #2162 `data/cr2_realisations.json` | `2ce114152529d375215f1f64a45072c9b78d1719d156e76bc692eff1fa955666` |

`verify.py` checks these hashes. The #2162 package itself credits #446/#595 (model), #717, #1590 (Lemma B) and #2111.

## Written for this package

`lib/classical.py` (realisations, frames, model re-implementation), `lib/universal.py` (frame-universal char-2 search),
`scripts/*.py`, `verify.py`, `data/universal.json`, `data/instances.json`, `data/special.json`,
`data/special_instances.json`, `README.md`, `MANIFEST.sha256` and the package metadata.
