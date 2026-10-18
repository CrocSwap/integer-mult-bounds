# Literal owner packing after PR643

Chi Zhao, with substantial OpenAI Codex assistance. Apache-2.0.

This supplement starts from Jeremy Kothe's PR643 at `bbfa9fe1d84d5572f4d144c2ee56a3eddc7a83f5` and changes only owner assignments. The idle profile improves from `{12:1,32:1,48:2228}` to `{44:1,48:2228}`. Suppliers, widths, schedule, and dispatch remain unchanged: 71 JP8 calls and one JP8b call. These are the two verified versions used by the upstream twin-supplier package.

A bounded integer CP-SAT model reassigns roles among 123 owners, permitting capacity48 owners to exchange which ones are empty. It leaves one gap of rank 44 and fills the previous empty capacity32 owner. The retained nomination changes 36 literal rows, including compaction offsets. All 35,424 roles pass the independent integer structural validator: complete role inventory, provider width, window eligibility, physical-family exclusions, interval capacity/nonoverlap, compact offsets, paid profile, rank mass 520704, and deficit 2560.

The reproducible admission path needs only the Python standard library:

```sh
python3 -I -O -B replay_owner_map.py --base-data /path/to/PR643/data --out /tmp/pr643-owner-export --negative-controls
```

The exporter checks pinned source bytes, applies the 36 recorded rows, verifies the entire map and canonical decompressed payload, and rejects duplicate-role, width, offset, and family corruptions. Regenerated gzip containers may differ across zlib versions; the decompressed canonical payload is the portability check. The enclosing witness independently rebuilds native suppliers and certifies the global moment and assembly. This supplement alone certifies ownership and the resulting paid profile.

`search_neighborhood.py` is optional nomination provenance, requiring OR-Tools 9.15. The retained solve is trial 11 with 123 owners, seed 123, four workers, and a three-second limit per trial. Its OPTIMAL status certifies feasibility of its constraints. A rerun may find a different map; the recorded changes provide deterministic reproduction.

For these fixed supplier profiles, widths, dispatch and capacity cap48, total idle rank is 106988 = 2228×48 + 44. For every 0 < q < 1, concavity of `r**(1-q)` implies the smallest idle moment under this cap is attained by this maximally concentrated profile. Our literal map attains that relaxed bound and therefore the constrained packing optimum for this fixed setup. This does not bound different suppliers, dispatch or geometry.

PR643's supplier words, twin dispatch, and starting map are credited to Jeremy Kothe (`jeremykothe2`). Inherited constructions include Jeremy Diviney's PR627 and Jeremy Kothe's PR629. This supplement claims the ownership change, by Chi Zhao with substantial OpenAI Codex assistance.
