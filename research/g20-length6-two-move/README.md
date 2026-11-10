# Two moved corrections do not emit on length-6 G20 intervals

**Exhaustive finite census. No new κ.** The selected conditional exponent stays
`781451/250000000` (`0.003125804`) in
[certificates/selected-result.json](../../certificates/selected-result.json).

On the emitted local word of
[PR #5708](https://github.com/CrocSwap/integer-mult-bounds/pull/5708),
every A2 conjugation with exactly six contacts was tested with every pair of
corrections moved onto other frames of the published one-edge route table.
All 520,160,250 such assignments miss a published edge. None emits, so none
lowers the paid-query moment on `(0, 1)`. The argument is in
[PROOF.md](PROOF.md).

This is a census of length exactly 6. It does not say that two moved
corrections fail at length 7 or above.

## Task and overlap

Base `17469fff78c22941280f04d39dc5a1faee09c840`, priority revision 8. Card
`bit-helper-contract`, scope **refined**. The card says to review the
#5679/#5708 chain and stop when a proposed cut does not improve the paid
moment. This package is open question 1 of
[#6963](https://github.com/CrocSwap/integer-mult-bounds/pull/6963).
The named first step is one length-6 interval. The same finite machine
classifies every length-6 interval, so the census covers all 86 rather than
a sample. Length 7 and above stays open.

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
corrections at length exactly 5. Its discussion finding
[#1166 comment 19507176](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19507176)
leaves the length-at-least-6 two-move question open. No open PR enumerates
length-6 two-move pairs on this word and route table.

## Census

The route table has 636 frames, so each correction has 635 legal moves.
Each of the 86 intervals has `C(6, 2) = 15` correction pairs.

| Class | Assignments | Outcome |
|---|---:|---|
| Prefix already missing | 105,644,950 | missing edge |
| First moved meeting rejects the new frame | 404,922,355 | missing edge |
| Records between the two meetings missing | 9,229,090 | missing edge |
| Second moved meeting rejects the new frame | 363,487 | missing edge |
| Tail or final return missing | 368 | missing edge |
| Emitted | 0 | — |
| Total | 520,160,250 | no saving |

The declared first interval is the least pair of scalar positions,
`2,649..9,125`, outer gate `ADD(436, 99)`. Its 6,048,375 assignments are
4,311,015 first-meeting failures, 1,734,820 middle failures and 2,540
second-meeting failures. None reaches the tail.

## Reproduce

Python 3.12 and the standard library, from the repository root. The census
and the cold replays finish in well under a minute here.

```sh
python3 -I -B research/g20-length6-two-move/verify.py
python3 -I -O -B research/g20-length6-two-move/verify.py
python3 -B scripts/research_package.py --package research/g20-length6-two-move
```

The direct verifier prints

```text
PASS_G20_LENGTH6_TWO_MOVE intervals=86 pairs=1290 assignments=520160250 prefix_fail=105644950 first_meet=404922355 middle_fail=9229090 second_meet=363487 full_replays=368 tail_missing=368 emitted=0 savings=0 first_interval=2649-9125/6048375/0 cold_replays=468 one_move_control=3H2-H4 tail_example=4067-9218/1,2/369,369 length7_open=1165 no_new_kappa=true
```

Checks raise exceptions, so `-O` does not disable them. Not run: the #5708
integration replay, the 18-call caller, adjoint columns, moduli 101 and
10201, ordinary admission, Lean, Docker, and `make frontier6030-verify`.

## Open next questions

1. Can two corrections in one interval of length at least 7 lower the paid
   moment when both frames move? Length 7 has 79 intervals on this word, and
   length at least 7 has 1,165. #6664 stops at four contacts, #6963 stops at
   five, and this census stops at six. The first step is one length-7
   interval's two-move pairs on this route table. No length-6 assignment
   emits, so none supplies a saving seed.
2. Can a third moved correction on one of the 368 length-6 words that
   survive both meetings, and then miss a later edge, make that word emit
   and lower the paid moment? Those words are rejections. A partial
   third-move search would not by itself be a census. This is not the
   length-5 three-move question left by #6963.

[#6923](https://github.com/CrocSwap/integer-mult-bounds/pull/6923) question 2,
one added route at the first missing edge of a dirty one-move failure, stays
on that package. [#6963](https://github.com/CrocSwap/integer-mult-bounds/pull/6963)
question 2, three or more moved corrections on a length-5 interval, stays on
that package. This census holds the published route table fixed.

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
length-5 two-move census this package continues is unpaidmoon's #6963.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
