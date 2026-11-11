# Two moved corrections do not emit on length-7 G20 intervals

**Exhaustive finite census. No new κ.** The selected conditional exponent stays
`363005817/100000000000` (`0.00363005817`) in
[certificates/selected-result.json](../../certificates/selected-result.json).
This package does not edit that record and does not claim a κ change.

On the emitted local word of
[PR #5708](https://github.com/CrocSwap/integer-mult-bounds/pull/5708),
every A2 conjugation with exactly seven contacts was tested with every pair of
corrections moved onto other frames of the published one-edge route table.
All 668,950,275 such assignments miss a published edge. None emits, so none
lowers the paid-query moment on `(0, 1)`. The argument is in
[PROOF.md](PROOF.md).

This is a census of length exactly 7. It does not say that two moved
corrections fail at length 8 or above.

## Task and overlap

Base `e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8. Card
`bit-helper-contract`, scope **refined**. The card says to review the
#5679/#5708 chain and stop when a proposed cut does not improve the paid
moment. This package is open question 1 of
[#7079](https://github.com/CrocSwap/integer-mult-bounds/pull/7079).
The named first step is one length-7 interval. The same finite machine
classifies every length-7 interval, so the census covers all 79 rather than
a sample. Length 8 and above stays open.

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
corrections at length exactly 5.
[#7079](https://github.com/CrocSwap/integer-mult-bounds/pull/7079) moves two
corrections at length exactly 6 and leaves length at least 7 open. No open
PR enumerates length-7 two-move pairs on this word and route table.
[#7095](https://github.com/CrocSwap/integer-mult-bounds/pull/7095) is the
three-or-more census at length 5. [#7074](https://github.com/CrocSwap/integer-mult-bounds/pull/7074)
adds a route. This census does neither.

## Census

The route table has 636 frames, so each correction has 635 legal moves.
Each of the 79 intervals has `C(7, 2) = 21` correction pairs.

| Class | Assignments | Outcome |
|---|---:|---|
| Prefix already missing | 157,257,750 | missing edge |
| First moved meeting rejects the new frame | 379,275,340 | missing edge |
| Records between the two meetings missing | 123,717,685 | missing edge |
| Second moved meeting rejects the new frame | 8,670,307 | missing edge |
| Tail or final return missing | 29,193 | missing edge |
| Emitted | 0 | — |
| Total | 668,950,275 | no saving |

The declared first interval is the least pair of scalar positions,
`2,235..9,308`, outer gate `ADD(482, 6)`. Its 8,467,725 assignments are
1,209,675 prefix failures, 6,094,095 first-meeting failures, 969,645 middle
failures, 194,300 second-meeting failures and 10 tail failures. None emits.

## Reproduce

Python 3.12 and the standard library, from the repository root. The census
and the cold replays finish in about two minutes here.

```sh
python3 -I -B research/g20-length7-two-move/verify.py
python3 -I -O -B research/g20-length7-two-move/verify.py
python3 -B scripts/research_package.py --package research/g20-length7-two-move
```

The direct verifier prints

```text
PASS_G20_LENGTH7_TWO_MOVE intervals=79 pairs=1659 assignments=668950275 prefix_fail=157257750 first_meet=379275340 middle_fail=123717685 second_meet=8670307 full_replays=29193 tail_missing=29193 emitted=0 savings=0 first_interval=2235-9308/8467725/10 cold_replays=29293 one_move_control=3H2-H4 tail_example=2235-9308/0,1/345,345 length6_tail_control=4067-9218/1,2/369,369 length8_open=1086 no_new_kappa=true
```

Checks raise exceptions, so `-O` does not disable them. Not run: the #5708
integration replay, the 18-call caller, adjoint columns, moduli 101 and
10201, ordinary admission, Lean, Docker, and `make frontier7000-verify`.
The 1,086 intervals of length at least 8 were not enumerated.

## Open next questions

1. Can two corrections in one interval of length at least 8 lower the paid
   moment when both frames move? Length at least 7 has 1,165 intervals on
   this word. This census settles the 79 of length exactly 7 and leaves
   1,086. Length 8 has 124 of them. #6664 stops at four contacts, #6963
   stops at five, #7079 stops at six, and this census stops at seven. The
   first step is one length-8 interval's two-move pairs on this route table.
   No length-7 assignment emits, so none supplies a saving seed.
2. Can a third moved correction on one of the 29,193 length-7 words that
   survive both meetings, and then miss a later edge, make that word emit
   and lower the paid moment? Those words are rejections. A partial
   third-move search would not by itself be a census. This is not the
   length-6 third-move question left by #7079, and it is not the length-5
   three-or-more census of #7095.

[#7079](https://github.com/CrocSwap/integer-mult-bounds/pull/7079) question 2
stays on that package. [#7095](https://github.com/CrocSwap/integer-mult-bounds/pull/7095)
stays on that package.
[#7074](https://github.com/CrocSwap/integer-mult-bounds/pull/7074) question,
adding the second missing edge of a dirty one-move failure, stays on that
package. This census holds the published route table fixed.

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
length-5 two-move census is unpaidmoon's #6963. The length-6 two-move census
this package continues, including the single tail rejection replayed here as
a control, is unpaidmoon's #7079.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
