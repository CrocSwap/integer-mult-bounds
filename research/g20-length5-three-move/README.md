# Three or more moved corrections do not emit on length-5 G20 intervals

**Exhaustive finite census, proved by a complete case split. No new κ.** The
selected conditional exponent stays `781451/250000000` (`0.003125804`) in
[certificates/selected-result.json](../../certificates/selected-result.json).

On the emitted local word of
[PR #5708](https://github.com/CrocSwap/integer-mult-bounds/pull/5708),
every A2 conjugation with exactly five contacts was tested with every choice
of three, four or five corrections moved onto other frames of the published
one-edge route table. All 13,840,035,444,873,750 such assignments miss a
published edge. None emits, so none lowers the paid-query moment on `(0, 1)`.
The argument is in [PROOF.md](PROOF.md).

## Task and overlap

Base `17469fff78c22941280f04d39dc5a1faee09c840`, priority revision 8. Card
`bit-helper-contract`, scope **refined**. The card says to review the
#5679/#5708 chain and stop when a proposed cut does not improve the paid
moment. This package is open question 2 of
[#6963](https://github.com/CrocSwap/integer-mult-bounds/pull/6963),
carried out on every length-5 interval rather than on a single tail word.

[#6305](https://github.com/CrocSwap/integer-mult-bounds/pull/6305) keeps every
correction on its contact frame for length 4 and above.
[#6337](https://github.com/CrocSwap/integer-mult-bounds/pull/6337) moves one
correction only for lengths 1..3.
[#6633](https://github.com/CrocSwap/integer-mult-bounds/pull/6633) moves one
correction at length 4.
[#6664](https://github.com/CrocSwap/integer-mult-bounds/pull/6664) moves two
corrections at lengths 2..4.
[#6923](https://github.com/CrocSwap/integer-mult-bounds/pull/6923) moves one
correction at length 5 or more.
[#6963](https://github.com/CrocSwap/integer-mult-bounds/pull/6963) moves two
corrections at length exactly 5 and leaves 4,331 tail rejections. Its
discussion finding
[#1166 comment 19507176](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19507176)
asks whether one further correction on one of those words can emit. No open
PR enumerates length-5 three-or-more moves on this word and route table.
The three-or-more question at 3 or 4 contacts remains the open question in
`research/g20-two-moved-corrections` and is a different domain.

## Census

The route table has 636 frames, so each moved correction has 635 legal moves.
Each of the 133 intervals has 16 ways to choose at least three of its five
corrections.

The emitter stops at the first missing route. Every assignment has a unique
pair of earliest moved corrections, and it agrees with the two-move word on
that pair through the record where that two-move word is rejected. The
two-move census is recomputed and matches #6963: 536,289,250 assignments,
4,331 of them tails, and no emission. Each of those 4,331 tails misses an
edge before the next correction, at a distance of 2 to 329 records. Later
frame choices are unread.

| Class | Assignments | Outcome |
|---|---:|---|
| Earliest pair rejected before the tail | 13,838,927,940,076,445 | missing edge |
| Earliest pair among the 4,331 tails, any later moves | 1,107,504,797,305 | missing edge |
| Emitted | 0 | — |
| Total | 13,840,035,444,873,750 | no saving |

The 1,107,504,797,305 tail extensions are 4,305 tails with three later slots
(1,107,501,953,775 assignments), 7 tails with two later slots (2,831,465),
and 19 tails with one later slot (12,065). No tail has its second moved
correction at the last contact.

The declared first interval is the least pair of scalar positions,
`1,119..8,918`, outer gate `ADD(572, 22)`. Its 104,060,416,878,750
three-or-more assignments are all early rejections. None of its two-move
pairs reaches a tail.

The first recorded tail is interval `5,673..7,030`, corrections 1 and 2
moved to frames 594 and 353. It misses a route on `ADD(173, 312)` at
rewritten index 6,306. Its next correction begins at index 6,547.

## Reproduce

Python 3.12 and the standard library, from the repository root. The census
and the cold replays finish in about 30 seconds here.

```sh
python3 -I -B research/g20-length5-three-move/verify.py
python3 -I -O -B research/g20-length5-three-move/verify.py
python3 -B scripts/research_package.py --package research/g20-length5-three-move
```

The direct verifier prints

```text
PASS_G20_LENGTH5_THREE_MOVE intervals=133 assignments=13840035444873750 early_extensions=13838927940076445 tail_extensions=1107504797305 tails=4331 tail_j1=4305 tail_j2=7 tail_j3=19 min_gap=2 max_gap=329 emitted=0 savings=0 first_interval=1119-8918/104060416878750/0 first_tail=5673-7030/1/2/594/353/6306/6547 cold_early=100 cold_tails=4331 cold_maximal=3 one_move_control=3H2-H4 length6_open=86 no_new_kappa=true
```

Checks raise exceptions, so `-O` does not disable them. Not run: the #5708
integration replay, the 18-call caller, adjoint columns, moduli 101 and
10201, ordinary admission, Lean, Docker, and `make frontier6030-verify`.

## Open next questions

1. Can three or more moved corrections in one interval of length at least 6
   emit and lower the paid moment on this word and route table? Length 6 has
   86 intervals. One move at length at least 5 is #6923, two moves at length
   exactly 5 are #6963, and three or more moves at length exactly 5 are this
   census. Two moves at length at least 6 remain question 1 of #6963 and are
   a different domain. The first step is one length-6 interval with three
   corrections moved on this route table. No length-5 three-or-more
   assignment emits, so none supplies a saving seed, and a length-6 interval
   is not covered by the case split above.

[#6923](https://github.com/CrocSwap/integer-mult-bounds/pull/6923) question 2,
one added route at the first missing edge of a dirty one-move failure, stays
on that package. This census holds the published route table fixed. Three or
more moves at 3 or 4 contacts stay with
`research/g20-two-moved-corrections`.

## Credit

The emitted word, route table, A2 relation, and the local-only conjugation
count are Ali Romman's `research/g20-conjugation-admission`, following
Dugongue, ai-nanachi, and the retained G20 lineage named there. The
length-4-and-above contact-frame obstruction is Nick Petalas's #6305. The
two-move classification at lengths 2..4, and the prefix machine this census
reimplements, are Nick Petalas's #6664. The length-1..3 one-move obstruction
is unpaidmoon's #6337. The length-4 one-move obstruction is unpaidmoon's
#6633. The length-at-least-5 one-move obstruction, including the length-5
emission replayed here as a positive control, is unpaidmoon's #6923. The
length-5 two-move census, including the 4,331 tail count this argument
extends, is unpaidmoon's #6963.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
