# Two moved corrections do not emit on length-5 G20 intervals

**Exhaustive finite census. No new κ.** The selected conditional exponent stays
`781451/250000000` (`0.003125804`) in
[certificates/selected-result.json](../../certificates/selected-result.json).

On the emitted local word of
[PR #5708](https://github.com/CrocSwap/integer-mult-bounds/pull/5708),
every A2 conjugation with exactly five contacts was tested with every pair of
corrections moved onto other frames of the published one-edge route table.
All 536,289,250 such assignments miss a published edge. None emits, so none
lowers the paid-query moment on `(0, 1)`. The argument is in
[PROOF.md](PROOF.md).

## Task and overlap

Base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8. Card
`bit-helper-contract`, scope **refined**. The card says to review the
#5679/#5708 chain and stop when a proposed cut does not improve the paid
moment. This package is open question 1 of
[#6923](https://github.com/CrocSwap/integer-mult-bounds/pull/6923),
carried out on every length-5 interval rather than on a single sample.

[#6305](https://github.com/CrocSwap/integer-mult-bounds/pull/6305) keeps every
correction on its contact frame for length 4 and above.
[#6337](https://github.com/CrocSwap/integer-mult-bounds/pull/6337) moves one
correction only for lengths 1..3.
[#6633](https://github.com/CrocSwap/integer-mult-bounds/pull/6633) moves one
correction at length 4.
[#6664](https://github.com/CrocSwap/integer-mult-bounds/pull/6664) moves two
corrections at lengths 2..4.
[#6923](https://github.com/CrocSwap/integer-mult-bounds/pull/6923) moves one
correction at length 5 or more. Its discussion finding
[#1166 comment 19473561](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19473561)
leaves the two-move question open. No open PR enumerates length-5 two-move
pairs on this word and route table.

## Census

The route table has 636 frames, so each correction has 635 legal moves.
Each of the 133 intervals has `C(5, 2) = 10` correction pairs.

| Class | Assignments | Outcome |
|---|---:|---|
| Prefix already missing | 86,290,150 | missing edge |
| First moved meeting rejects the new frame | 332,300,580 | missing edge |
| Records between the two meetings missing | 116,497,735 | missing edge |
| Second moved meeting rejects the new frame | 1,196,454 | missing edge |
| Tail or final return missing | 4,331 | missing edge |
| Emitted | 0 | — |
| Total | 536,289,250 | no saving |

The declared first interval is the least pair of scalar positions,
`1,119..8,918`, outer gate `ADD(572, 22)`. Its 4,032,250 assignments are
2,419,350 prefix failures and 1,612,900 first-meeting failures. None reaches
the second correction.

## Reproduce

Python 3.12 and the standard library, from the repository root. The census
and the cold replays finish in well under a minute here.

```sh
python3 -I -B research/g20-length5-two-move/verify.py
python3 -I -O -B research/g20-length5-two-move/verify.py
python3 -B scripts/research_package.py --package research/g20-length5-two-move
```

The direct verifier prints

```text
PASS_G20_LENGTH5_TWO_MOVE intervals=133 pairs=1330 assignments=536289250 prefix_fail=86290150 first_meet=332300580 middle_fail=116497735 second_meet=1196454 full_replays=4331 tail_missing=4331 emitted=0 savings=0 first_interval=1119-8918/4032250/0 cold_replays=4431 one_move_control=3H2-H4 length6_open=86 no_new_kappa=true
```

Checks raise exceptions, so `-O` does not disable them. Not run: the #5708
integration replay, the 18-call caller, adjoint columns, moduli 101 and
10201, ordinary admission, Lean, Docker, and `make frontier6030-verify`.

## Open next questions

1. Can two corrections in one interval of length at least 6 lower the paid
   moment when both frames move? Length 6 has 86 intervals on this word.
   #6664 stops at four contacts and this census stops at five. The first
   step is one length-6 interval's two-move pairs on this route table. No
   length-5 assignment emits, so none supplies a saving seed.
2. Can three or more moved corrections in one length-5 interval emit and
   lower the paid moment? The first step is one further correction on one of
   the 4,331 words that survive both moved meetings and then miss a later
   edge. Those words are rejections. A partial third-move search would not
   by itself be a census.

[#6923](https://github.com/CrocSwap/integer-mult-bounds/pull/6923) question 2,
one added route at the first missing edge of a dirty one-move failure, stays
on that package. This census holds the published route table fixed.

## Credit

The emitted word, route table, A2 relation, and the local-only conjugation
count are Ali Romman's `research/g20-conjugation-admission`, following
Dugongue, ai-nanachi, and the retained G20 lineage named there. The
length-4-and-above contact-frame obstruction is Nick Petalas's #6305. The
two-move classification at lengths 2..4, and the prefix machine this census
reimplements, are Nick Petalas's #6664. The length-1..3 one-move obstruction
is unpaidmoon's #6337. The length-4 one-move obstruction is unpaidmoon's
#6633. The length-at-least-5 one-move obstruction, including the length-5
emission replayed here as a positive control, is unpaidmoon's #6923.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
