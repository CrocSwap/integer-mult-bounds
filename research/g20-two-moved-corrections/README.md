# Two moved corrections do not emit in short G20 conjugations

**Scoped negative result (finite certificate). No new κ.** The selected
conditional exponent stays `781451/250000000` (PR #6030) in
[certificates/selected-result.json](../../certificates/selected-result.json),
with its five framework assumptions.

On the emitted local word of
[PR #5708](https://github.com/CrocSwap/integer-mult-bounds/pull/5708), take
every A2 conjugation with 2, 3 or 4 contacts and move **two** of its
corrections onto other frames of the published one-edge route table. All
723,788,875 such assignments fail to emit. None changes the paid histogram,
so none lowers the paid-query moment on `(0, 1)`. The argument is in
[PROOF.md](PROOF.md).

This answers open question 1 of unpaidmoon's
[PR #6633](https://github.com/CrocSwap/integer-mult-bounds/pull/6633)
(head `2ca0030166f85a833da2a3eb66a0bf82ac3dfe1c`), also posed in
`research/g20-moved-correction-frame` (PR #6337): can two corrections in one
length-2, length-3 or length-4 interval lower the paid moment when both
frames move?

## Result

| Contacts | Intervals | Correction pairs | Assignments | Emitted |
|---:|---:|---:|---:|---:|
| 2 | 331 | 331 | 133,467,475 | 0 |
| 3 | 250 | 750 | 302,418,750 | 0 |
| 4 | 119 | 714 | 287,902,650 | 0 |

Every assignment is rejected at the first missing route of the rewritten
word:

| First rejection | Assignments |
|---|---:|
| Before the first moved contact (shared prefix) | 80,241,775 |
| At the first moved contact and correction | 607,824,540 |
| Between the two moved corrections | 35,467,290 |
| At the second moved contact and correction | 255,171 |
| After the second moved correction | 99 |

The emitter stops at the first missing route, so a prefix rejection rejects
the whole word. The verifier caches the machine state after each shared
prefix and replays the full tail only for the 99 words that pass both
meetings. It asserts that the five classes partition all assignments.

Controls: 125 sampled assignments (25 per class) are rebuilt and emitted
from scratch and all reject. The same emitter reproduces the
PR #6337 one-move census at 1..3 contacts: 28,149 meeting hosts and 26
emitted words with shapes `H4` and `5 H2 − 2 H4`.

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -B research/g20-two-moved-corrections/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -B research/g20-two-moved-corrections/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/g20-two-moved-corrections
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/g20-two-moved-corrections --check-source-history
```

Any CPython 3.12 can replace the local path. Each direct run prints
`PASS_G20_TWO_MOVED_CORRECTIONS ... assignments=723788875 ... emitted=0 savings=0`
and takes about 15 seconds on one core. Inputs are pinned by SHA256 in
[SOURCES.json](SOURCES.json).

## Scope and limits

- Exactly two moved corrections; the other corrections stay on their
  contact frames. Three or more moves are not enumerated.
- Intervals with 2, 3 or 4 contacts. One-contact intervals have no pair.
  Five or more contacts with moved frames are not enumerated.
- The published route table only. A missing edge is a rejection on this
  table, not a proof that no other native path exists.
- Not run: the #5708 integration replay, the 18-call caller, adjoint
  columns, moduli 101 and 10201, ordinary admission, Lean, Docker and
  `make frontier6030-verify`.

## Open next questions

1. Can three or more moved corrections in one 3- or 4-contact interval emit
   and save? Only 99 two-move words reach a full replay, and each misses a
   later route. First step: name the first missing route of each of the 99
   and test whether moving a later correction can supply it.
2. Can one or two moved corrections at five or more contacts lower the paid
   moment? PR #6305 covers those lengths only at the contact frame. First
   step: the same prefix-resumed census on 5-contact intervals.
3. Does one added route make a two-move word emit with a saving? First
   step: group the 255,171 second-meeting failures by their first missing
   ordered frame pair and price the most frequent one.

## Credit

The emitted word, route table, constructor and A2 relation are Ali
Romman's `research/g20-conjugation-admission` (PR #5708), following the G20
lineage named there. The moved-correction model, meeting test and one-move
censuses are unpaidmoon's PR #6337 and PR #6633; the contact-frame census at
four or more contacts is PR #6305. This two-move census and its verifier
were produced by Nick Petalas.
