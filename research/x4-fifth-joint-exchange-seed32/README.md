# X4 fifth joint exchange: complete census (negative)

Seed 32, complex-supplier track, base commit `f567884a`.

## Question

The selected X4 word applies four joint read-set exchanges to BRoute's sw4 word
(research/gauge44-frames-x). Does a fifth exchange of the same kind, applied jointly
with X4's recipe and PR741's eight explicit frames, raise κ above X4's
`1661634653669567/10^18` (0.001661634653669567)?

## Result

No. No candidate in the domain improves or ties X4.

| quantity | value |
|---|---|
| copy pairs / pairs with movable reads | 107 / 54 |
| target-sharing pair-pairs, total / after X4 | 40 / 28 |
| subset combinations after X4 | 3180 |
| candidates (with frame policies) | 10144 |
| rejected: target cap | 5640 |
| rejected: duplicate frame | 2968 |
| rejected: B-segment exactness | 0 |
| legal | 1536 (12 distinct profiles) |
| improving / equal to X4 | 0 / 0 |
| best legal κ | `13292213039457/8×10^15` (0.001661526629932125), profile {1:2550, 2:337, 3:430, 4:194, 5:56, 8:8} |

Every legal candidate is replayed through the pinned `build_jx.build` as an X4 recipe
extension: 1536 accepted, 0 rejected, 0 profile mismatches. Each distinct profile is
priced with the repository pricer.

## Domain

Every unordered pair of sw4 copy pairs with movable reads, neither among X4's eight,
whose movable-read target sets intersect; every pair of nonempty movable-read subsets;
and a frame policy per moved read, either K (keep the stored frame, X4's rule) or J (plain
join, BRoute's rule). Core mode runs all-K and all-J on every subset pair, plus every
per-read mask on the full exchanges. A K on a read that already carries a PR741 frame is
rejected as a duplicate frame, as `build_jx` does. See the census.py docstring for the
exact definition.

## Controls

Positive: X4 rebuilt byte-for-byte from sw4 (content sha `1e1d99ba…`) by both the census
builder and `build_jx`; PR741 rebuilt; both pricer mappings reproduced; one X4 instance
re-derived from the copy-pair rule with its +1.0798e-7 κ gain; domain counts match the
PR799 and BRoute reports; seeded cross-check against `build_jx` (45/45 agree).
Negative: dropped, wrong-sign and kept-H pre-reads rejected; X4 recipe controls N1 and
N4 reproduced; stale gate, tampered input pin and frame tamper detected.

## Reproduce

From the repository root, Python 3.11+ standard library only (about 25 minutes):

```
research/x4-fifth-joint-exchange-seed32/reproduce.sh /absolute/new-outdir
```

Recorded outputs are in `evidence/`.

## Scope

This closes one neighborhood: a single additional copy-pair exchange on top of X4, with
X4's edits and PR741's frames fixed. It does not cover exchanges outside the copy-pair
rule, re-selecting X4's own four exchanges, two or more additional exchanges (none of
the legal candidates is neutral or better, so no pair was evaluated), or changes to the
supplier model.
