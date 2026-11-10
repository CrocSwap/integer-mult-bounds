# One moved correction at length 5 or more does not lower the G20 moment

**Negative result. No new κ.** The selected conditional exponent stays
`781451/250000000` (`0.003125804`) in
[certificates/selected-result.json](../../certificates/selected-result.json).

On the emitted local word of
[PR #5708](https://github.com/CrocSwap/integer-mult-bounds/pull/5708),
every A2 conjugation of length at least 5 keeps a legal scalar endpoint when
exactly one correction moves onto a different frame of the published one-edge
route table. All 10,074,275 such assignments fail to lower the paid-query
moment on `(0, 1)`. Eight assignments emit, and each emitted shape is a strict
loss. The argument is in [PROOF.md](PROOF.md).

## Task and overlap

Base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8. Card
`bit-helper-contract`, scope **refined**. The card says to review the
#5679/#5708 chain and stop when a proposed cut does not improve the paid
moment. This package is the length-at-least-5 one-move clause left open by
the length-4 screen and by PR #6664.

Ordered eligible list for session r99, rebuilt on 2026-11-08 against that
main. The revision-8 "Next bounded decisions" table is the list. A row stays
while that table still states the decision. Catalogue cards not named by the
table follow, in catalogue order. Dropped before the cut: work this account
already delivered, results closed on current main, questions covered by an
open pull request, and topics already on a fork `cursor/*` branch. The 19
October handoff index is already delivered. Discussion #1166 through
2026-11-07 is completed claims and caller handoffs, not a newer finite index
that replaces the table.

1. Complex helpers (`p104-side-correction`, `coverage-law-change`).
2. **This package.** BIT (`bit-helper-contract`): one correction of a #5708
   conjugation of length at least 5, moved off its contact frame.
3. New decoders and interfaces.
4. Supplier audit (`supplier-boundary-audit`).
5. All-size audit (`uniform-transfer-audit`).
6. Verification tooling (`replay-runtime`).
7. `bit-new-register-model`.
8. `r437-carrier-integration`.
9. `complex-rank-shape-decoder`.
10. `complex-new-helper-inventory`.

[#6305](https://github.com/CrocSwap/integer-mult-bounds/pull/6305) keeps every
correction on its contact frame for length 4 and above.
[#6337](https://github.com/CrocSwap/integer-mult-bounds/pull/6337) moves one
correction only for lengths 1..3.
[#6633](https://github.com/CrocSwap/integer-mult-bounds/pull/6633) moves one
correction at length 4.
[#6664](https://github.com/CrocSwap/integer-mult-bounds/pull/6664) moves two
corrections at lengths 2..4 and leaves length at least 5 open.
The GL(2) floor, the extra-wire floor, and the relocated-output floor are
different boundaries. No open PR replays this length-at-least-5 one-move
domain.

## Census

| Class | Assignments | Outcome |
|---|---:|---|
| Prefix already missing | 6,114,415 | missing edge |
| Pair rejects the new frame | 3,272,780 | missing edge |
| Dirty wire's next route missing | 686,779 | missing edge |
| Clean later route missing | 179 | missing edge |
| Failed contact pair, alternate frame replayed | 112 | missing edge |
| Lemma remainder, independently replayed | 2 | missing edge |
| Emitted | 8 | strict loss |
| Total | 10,074,275 | no saving |

The contact-frame slice of these 1,384 intervals is 1,332 missing routes, 13
unchanged histograms, and 39 strict losses. Together with the 119 length-4
intervals, that is the published #6305 total.

## Reproduce

Python 3.12 and the standard library, from the repository root. The census
finishes in about twenty seconds here.

```sh
python3 -I -B research/g20-length5plus-one-move/verify.py
python3 -I -O -B research/g20-length5plus-one-move/verify.py
python3 -B scripts/research_package.py --package research/g20-length5plus-one-move
```

The direct verifier prints

```text
PASS_G20_LENGTH5PLUS_ONE_MOVE intervals=1384 lengths=28 fixed_missing=1332 fixed_neutral=13 fixed_loss=39 assignments=10074275 prefix_fail=6114415 pair_fail=3272780 dirty_fail=686779 clean_fail=179 failed_pair_replays=112 repairs=2 emitted=8 savings=0 length4_control=119/504 no_new_kappa=true
```

Checks raise exceptions, so `-O` does not disable them. Not run: the #5708
integration replay, the 18-call caller, adjoint columns, moduli 101 and
10201, ordinary admission, Lean, Docker, and `make frontier6030-verify`.

## Open next questions

1. Can two corrections in one length-at-least-5 interval lower the paid
   moment when both frames move? This certificate moves exactly one
   correction. PR #6664 answers the two-move question only through length 4.
   The first step is one length-5 interval's two-move pairs on this word and
   route table. No saving seed is supplied by the one-move census.
2. Does one added route at the first missing edge of a dirty failure turn
   that word into a strict saving? The first step is to group the 686,779
   dirty failures by the missing frame pair. The blocker is that this package
   holds the published route table fixed.

## Credit

The emitted word, route table, A2 relation, and the local-only conjugation
count are Ali Romman's `research/g20-conjugation-admission`, following
Dugongue, ai-nanachi, and the retained G20 lineage named there. The
length-4-and-above contact-frame obstruction is Nick Petalas's #6305. The
length-1..3 one-move obstruction is unpaidmoon's #6337. The length-4 one-move
obstruction is unpaidmoon's #6633. The two-move obstruction at lengths 2..4
is Nick Petalas's #6664. The strict-loss splitting inequality is the same
elementary estimate used in those censuses.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
