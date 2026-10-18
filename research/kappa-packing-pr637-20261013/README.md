# Literal owner packing after PR637

Chi Zhao, with substantial OpenAI Codex assistance. Apache-2.0.

Starting from Jeremy Kothe's PR637 (`jeremykothe2`, commit `4edb0dda99c495141cc56ae6e8a74e632a74db8a`), this literal packing change consolidates idle ranks `{4:1,32:1,48:2229}` into `{1:1,35:1,48:2229}`. Supplier widths, paid local profiles, and dispatch remain unchanged: 71 JP8 calls and one CK call at time5, stage2, forward orientation.

The construction migrates an empty capacity32 owner through full capacity32 owners whose role times fit the preceding empty owner, performs two neutral swaps that move the rank4 gap to a capacity48 owner, then transfers a rank31 bundle into the empty capacity32 owner. Every moved role retains its helper identity, time, and width. The portable exporter checks every interval, window, physical family, role, and paid profile using integer arithmetic. Search floating-point values are nominations; the enclosing witness supplies native replay and exact moment certification.

PR637's scalar construction and starting packing are credited to Jeremy Kothe. Inherited constructions include Jeremy Diviney's PR627 and Jeremy Kothe's PR629; this supplement claims only the recorded ownership change.

Reconstruct from the immutable PR637 data directory:

```sh
python3 replay_owner_map.py --base-data /path/to/PR637/data --out /tmp/pr637-export --negative-controls
python3 -O replay_owner_map.py --base-data /path/to/PR637/data --out /tmp/pr637-export-opt --negative-controls
```

The admission path is standard-library-only and checks the canonical decompressed payload hash. Published gzip hashes authenticate source bytes; regenerated gzip container bytes may differ across zlib versions. Four corruptions (duplicate role, width, offset, family) must be rejected. `search/relocate_two.py` records the exploratory constructor, with assertions and floating nomination; it is not the admission path. No global packing optimality is claimed.
