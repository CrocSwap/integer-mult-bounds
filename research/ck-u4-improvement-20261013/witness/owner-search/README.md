# CK four-end owner reconstruction

Chi Zhao, with substantial OpenAI Codex assistance. Apache-2.0.

Start from pinned PR638 data. Four CK widths at time 5 shrink from 9 to 8,
and a 21-owner integer neighborhood consolidates the released space into
idle ranks {40:1,48:2229}. The recorded replacement contains 38 changed
literal rows, including width changes and interval compaction. Supplier and
scalar claims are independently checked by the enclosing witness.

```
python3 replay_owner_map.py --base-data /path/to/PR638/data --out /tmp/ck-owner-export --negative-controls
python3 -I -O -B replay_owner_map.py --base-data /path/to/PR638/data --out /tmp/ck-owner-export-opt --negative-controls
```

The standard-library exporter verifies pinned base inputs, every literal role,
width, time window, physical family, compact interval and paid profile. Four
corruptions must reject. It checks the canonical decompressed output hash;
regenerated gzip container bytes may differ across zlib versions. The original
compressed hash authenticates the pinned publication. SEARCH.json records the
nomination method; no solver is required for reconstruction.
