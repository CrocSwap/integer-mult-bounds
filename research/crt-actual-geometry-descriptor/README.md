# PR4174's production layout has no split-axis same-color pair

The requested first caller for a seven-unary-descriptor frontend does not exist in PR4174's exact `production_census` layout. Across all sixteen tree levels and both partitions, no bit of an active axis split by a placement cut shares a color with any bit of another axis in the same batch. This is stronger than excluding full guards: there is no same-color pair even before guard admission or the synchronized Beneš layer restriction. Consequently there is no exactly-two-target color subbatch containing such an axis in this layout.

This is a finite, exact source-bound incompatibility result, not a universal statement about CRT layouts or PR4990's seven-descriptor interface. It does not exclude pairs without split axes, other admissible layouts, or changed batching. The package stops at the assigned caller-selection gate and implements no binary-to-unary frontend. The production payload is never materialized, and no child coordinate value or control function is evaluated.

## Source and coverage

The canonical base is `4c0a359d88f22f05189d51f48387750b801a45d4`, priority revision 7. [SOURCES.json](SOURCES.json) binds the owning PR4174 allocator and production fixture, PR4100's coloring rule, and PR4990's unary consumer. The verifier extracts and executes only the assignments preceding and including `layout = allocator.Layout(...)` in the original `production_census`; it does not run that census. The resulting values are:

| Parameter | Value |
| --- | ---: |
| `d`, `ell`, `p` | `65536`, `24`, `9240576` |
| Widths in logical order | `24,23` repeated |
| `L`, `G`, `K` | `1540096`, `3072`, `196608` |
| `r_max`, `H` | `5`, `15360` |

The immutable receipt [RESULT.json](RESULT.json) lists all 26 `(level, partition, batch, cut)` candidates. Their split axes are exactly `653`, `64228`, and `64882`. Each row gives the exact union of inclusive positive-distance intervals between every possible bit of that split axis and every possible bit of the other active axes. None contains a positive multiple of `K`. All source-position pairs are also compared independently with that interval union. [PROOF.md](PROOF.md) explains why these candidates cover every relevant caller, including root and nonroot reservoirs.

## Verification

Run from the repository root with Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/crt-actual-geometry-descriptor --check-only
python3.12 -B scripts/research_package.py --package research/crt-actual-geometry-descriptor
```

Author verification on Python 3.12.14 / Darwin 27.0.0 arm64 passed metadata/source pins (0.67 s) and the registered ordinary plus optimized replays (0.75 s combined), each reporting `26 57875 0`: candidates, literal bit pairs, same-color pairs. Both registered ordinary and optimized replays authenticate source bytes and compare the frozen result. They use only bounded address-layout arithmetic; no payload address census, production build, Lean or Docker runs. The source `production_census` and the existing full producer/scanner replay are deliberately not invoked. The verifier works without Git when this package and its declared live source inputs are exported together.

The test contract is caller-selection completeness and exact same-color feasibility. Credible failures include missing a root partition, wrong active-stream rank, stale positions, incorrect half-open interval arithmetic and excluding an interval endpoint that is a multiple of `K`. PR4174 checks placement but does not classify same-color pairs; PR4990 begins with supplied unary positions. The new verifier owns this gap and adds no production test hook or behavior change. Its tiny interval positive controls test the arithmetic detector only; they are explicitly not synthetic CRT callers.

## Scope change and handoff

The original assignment sought a paid source-layout-to-unary frontend, starting with a real two-target full-guard color containing a split axis. That first fixture fails for the pinned production example. In accordance with the stop condition, the result narrows to this incompatibility and its complete finite certificate. No descriptor setup, transport, preservation, return or erasure tariff is claimed. Those obligations remain open, alongside variable-size batches, last-`K` handling, physical placement, key generation, repair and a common complete machine invoice. Selected conditional κ remains `0.00302015`.

## Open next questions

1. Does another explicitly specified admissible PR4174 `Layout` have a real exactly-two-target full-guard color containing a split axis? Before restarting frontend implementation, provide its binary layout, actual level/partition/batch and synchronized target-bit schedule, and verify complete guards after placement. This result supplies no such witness and authorizes no parameter search.
2. If a paid frontend is pursued for a non-split actual pair instead, record that changed fixture premise explicitly and retain split-axis transport as an unresolved obligation. Reusing PR4990's small mask tuple alone does not establish actual caller reachability.

Credit Hiroki KUMAZAKI (@kumagi), PR4174 for `Layout`, `Plan`, `Placement` and its production fixture, and PR4990 for the seven-unary producer handoff; Cinna Davis, PR4100 for CRT batching and coloring; ToikY, unpaidmoon, Ryanson Jonathan, Douglas Colkitt and John-Michael Smith for the retained unary, scanner, repair and compact lineage. Original source bytes are unchanged. New investigation by JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
