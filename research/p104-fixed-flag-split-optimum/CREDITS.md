# Sources and credit

Ali Romman (@aliromman) prepared the exact optimization, certificate,
proof and checker with substantial OpenAI Codex assistance. New material
is Apache-2.0. No independent human or formal proof-kernel acceptance
is claimed.

Nick Petalas (@petalas) supplied the signed split witness, compact
geometry, source formula and open optimization question in
[PR #7748](https://github.com/CrocSwap/integer-mult-bounds/pull/7748).
The [source proof](https://github.com/petalas/integer-mult-bounds/blob/5ca92afebe8ed0208c9a1ffbee0424f98a9eff6e/research/p104-c56-split-gather-witness/README.md),
[geometry and flags](https://github.com/petalas/integer-mult-bounds/blob/5ca92afebe8ed0208c9a1ffbee0424f98a9eff6e/research/p104-c56-split-gather-witness/WITNESS.json)
and [checker](https://github.com/petalas/integer-mult-bounds/blob/5ca92afebe8ed0208c9a1ffbee0424f98a9eff6e/research/p104-c56-split-gather-witness/verify.py)
are retained with all six package files at that exact commit. The checker
runs unchanged; the new code uses its authenticated geometry routines.
The shared CI changes in that commit are not copied into this package.

The source credits DreamingOfClouds (@DreamingOfClouds), with Claude Opus
5.5 assistance, for the C=56 flag model, chain configuration and split-gather
question in [PR #7689](https://github.com/CrocSwap/integer-mult-bounds/pull/7689),
at source head `511e7d0852acdca291b50c538b978fb063ae7bac`.
The original notice and geometry provenance remain in the retained source
proof. This package does not replay its global lower-bound or Lean suites.

The new contribution is the exact rational optimum across all 104 columns
of these fixed flags, with integer inconsistency certificates and a full
attaining schedule. `SOURCE-PINS.json` authenticates the six retained files.
`SOURCES.json` records selected-record and catalogue provenance at canonical
main. Content pins do not assert unmerged ancestry.
