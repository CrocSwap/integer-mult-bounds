# One added route does not save a dirty one-move G20 failure

**Exhaustive finite census. No new κ.** The selected conditional exponent stays
`781451/250000000` (`0.003125804`) in
[certificates/selected-result.json](../../certificates/selected-result.json).

On the emitted local word of
[PR #5708](https://github.com/CrocSwap/integer-mult-bounds/pull/5708),
every length-at-least-5 one-move assignment that
[#6923](https://github.com/CrocSwap/integer-mult-bounds/pull/6923)
classifies as a dirty failure was replayed with exactly one route added at
its first missing edge. The added route has an integer rank in `1..7`, the
same range as every published edge. Of the 686,779 assignments, 686,386 still
miss a different edge. The other 393 emit. Each emission pays the new edge
one, two, or three times, and each is a strict loss on `(0, 1)` at every rank
in `1..7`. None is a strict saving. The argument is in [PROOF.md](PROOF.md).

## Task and overlap

Base `17469fff78c22941280f04d39dc5a1faee09c840`, priority revision 8. Card
`bit-helper-contract`, scope **refined**. The card asks whether a changed G20
helper path improves the complete BIT moment. This package answers open
question 2 of
[#6923](https://github.com/CrocSwap/integer-mult-bounds/pull/6923):
one added route at the first missing edge of a dirty one-move failure.
[#6963](https://github.com/CrocSwap/integer-mult-bounds/pull/6963)
settled two moved corrections on length-5 intervals and left this question
on the #6923 package.

[#6305](https://github.com/CrocSwap/integer-mult-bounds/pull/6305) keeps every
correction on its contact frame for length 4 and above.
[#6337](https://github.com/CrocSwap/integer-mult-bounds/pull/6337) moves one
correction only for lengths 1..3.
[#6633](https://github.com/CrocSwap/integer-mult-bounds/pull/6633) moves one
correction at length 4.
[#6664](https://github.com/CrocSwap/integer-mult-bounds/pull/6664) moves two
corrections at lengths 2..4.
This census does not rerun those screens, does not move a second correction,
and does not add a second route. The family expansion gate is unchanged: a
local moment obstruction is not a new construction round.

## Census

The 686,779 dirty failures use 22,709 distinct missing frame pairs. The
multiplicity table, sorted as `origin target count`, has SHA-256
`8f38eb2f6e526ede87a62c1fc88c35fd5d3ba87a16f755df690a76cea5a68494`.
The maximum multiplicity is 1,841. It is attained by 303 edges, all into
frame 1, from every frame in `326..635` except 507 and 519–524. Those 303
pairs account for 557,823 of the failures. Every first missing hop pays.

| Class | Assignments | Outcome |
|---|---:|---|
| Still missing a different edge | 686,386 | no paid histogram |
| Emitted, strict loss at ranks 1..7 | 393 | no saving |
| Total | 686,779 | no saving |

The lex-first emission is scalar positions 5,760–6,924, length 13, outer gate
`ADD(89, 19)`, correction 6 (`ADD(161, 19)` moved from frame 575 to frame
429). Its first missing edge is `(429, 575)`. At rank 1 the paid difference
is `3 H2 − H4`, which splits as `H4 = H2 + H2` and leaves `H2`.

## Reproduce

Python 3.12 and the standard library, from the repository root. The census
finishes in about one minute here.

```sh
python3 -I -B research/g20-dirty-one-move-added-route/verify.py
python3 -I -O -B research/g20-dirty-one-move-added-route/verify.py
python3 -B scripts/research_package.py --package research/g20-dirty-one-move-added-route
```

The direct verifier prints

```text
PASS_G20_DIRTY_ONE_MOVE_ADDED_ROUTE dirty=686779 pairs=22709 later_missing=686386 emitted=393 savings=0 mismatches=0 first_hop_pays=686779 max_multiplicity=1841 pair_sha256=8f38eb2f6e526ede87a62c1fc88c35fd5d3ba87a16f755df690a76cea5a68494 split=382 elementary=11 witness=5760-6924/6/429/429-575/uses1 no_new_kappa=true
```

Checks raise exceptions, so `-O` does not disable them. Not run: the #5708
integration replay, the 18-call caller, adjoint columns, moduli 101 and
10201, ordinary admission, Lean, Docker, and `make frontier6030-verify`.

## Open next questions

1. Does adding the second missing edge as well turn one of the 686,386
   still-rejected words into a strict saving? One added route leaves those
   words short of an emission. The first step is the lexicographically first
   still-rejected word: record the edge that rejects it after the first route
   is added, and replay that word with both edges present at rank 1. The
   blocker is that this package inserts only the first missing edge.

## Credit

The emitted word, route table, A2 relation, and the local-only conjugation
count are Ali Romman's `research/g20-conjugation-admission`, following
Dugongue, ai-nanachi, and the retained G20 lineage named there. The
length-4-and-above contact-frame obstruction is Nick Petalas's #6305. The
two-move classification at lengths 2..4 is Nick Petalas's #6664. The
length-1..3 one-move obstruction is unpaidmoon's #6337. The length-4 one-move
obstruction is unpaidmoon's #6633. The length-at-least-5 one-move obstruction,
including the dirty-failure count and the one-hop classifier this census
replays, is unpaidmoon's #6923. The length-5 two-move census that left this
question open is unpaidmoon's #6963. The strict-loss splitting inequality is
the same elementary estimate used in those censuses.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
