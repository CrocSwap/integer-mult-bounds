# Literal owner repair on PR635

This supplement reconstructs a new literal owner map from **Jeremy Kothe
(`jeremykothe2`)'s PR635**, pinned at
`a6895a69f8ad98ab45777b03e9e6f48888c39f6f`. It preserves both supplier width
arrays and paid profiles, the complete geometry and schedule, and dispatch
71 JP8 / 1 CK. The CK call remains time 5, **stage 2, forward orientation**.
Only owner placement and compacted offsets change.

The selected map's floating nomination is κ ≈ 0.0016362697624404078, exceeding
PR635's 0.001636241501576388. The enclosing package must rebind its actual native
programs, independently check this literal map, and certify the complete exact
invoice, moments and outer assembly. This supplement alone is not a κ certificate.
All inherited conditional assumptions remain.

The actual idle profile is `{1:42,23:1,32:1,39:1,48:2221}`. There are 35,424
hosted roles, paid rank mass 520,704, live count 7,168 and deficit 2,560.

## Reproduce

Python 3.9+ with the standard library:

```sh
python3 research/kappa-packing-pr635-20261013/replay_owner_map.py \
  --base-data /path/to/pr635/research/complex-571-cold14-st2/data \
  --out /tmp/reconstructed-pr635-repair --negative-controls
```

`SOURCE.json` pins the source PLAN and compressed OWNERS artifact. The exporter
applies **6,967** recorded row replacements, validates every helper role, width,
chronology, owner window, physical family, interval, offset, paid profile and
rank mass, and checks canonical decompressed output SHA-256:

```
c329f46ca2674c714644eefb831974cb1fa86702c3a91cb25d4336ee2395f284
```

The published gzip container hash is
`8e752de9e85e9894ca358bc2c25c28d1fdeaf1797dfee6a18a14b372151cb2bb`.
Regenerated gzip hashes are reported only; cross-zlib container differences are
accepted if the canonical payload matches. Ordinary and optimized Python both
pass the exporter and four negative controls (duplicate role, width, offset,
family). `OWNER-TEMPLATE.json` deliberately contains no native hash bindings;
the enclosing package must derive those from its actual programs.

## Search and credit

Two 90-second literal searches used seeds 37 and 97. Seed 37 produced the
selected map after 257,980,001 iterations, six improving moves and 1,092,112
neutral legal moves. Its floating fixed-exponent objective improved by
26.91351729328744. No optimality is claimed. `SEARCH.json` and `search/` retain
both receipts and the nominator. The timing-limited search need not reproduce
the same endpoint; the recorded replacements and exporter reproduce the map.

Prepared by **Chi Zhao**, with **substantial OpenAI Codex assistance**;
**Apache-2.0**. The starting supplier/owner map is credited to Jeremy Kothe's
[PR635](https://github.com/CrocSwap/integer-mult-bounds/pull/635), with
[immutable package source](https://github.com/jeremykothe2/integer-mult-bounds/tree/a6895a69f8ad98ab45777b03e9e6f48888c39f6f/research/complex-571-cold14-st2).
The enclosing combined suppliers retain Jeremy Diviney's PR627 factored-end
credit, Jeremy Kothe's PR629 four-end credit, and all predecessor notices.
Our earlier combined-word reconstruction is independent of PR635's native
program hashes; transfer requires the explicit native rebinding noted above.
No archived source or frozen earlier witness was modified by this supplement.
