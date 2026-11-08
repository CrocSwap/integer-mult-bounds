# No equivalent off-593 holder for the two remaining frame-593 reads

**Negative scoped result. No new κ.**

On the selected PR6030 word, helpers 469 and 471 still read helpers 703 and 704
at frame 593. The selected package asks whether either itinerary can avoid that
frame without a new carrier of the read content. This package answers the
pure-carrier part of that question.

Each read has a unique carrier, the source register itself. The only frame that
carrier shares with its receiver, other than 593, is frame 127. Moving the read
to the first such meeting changes final scalar rows. Public input 1 is a witness.

## Statement

The sole computational input is `research/p104-helper470-twin-rung-removal/WORD.json.gz`,
SHA256 `7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f`
(22,803 events, 770 public registers, 29 owned fields). Scalar rows start as
the public basis. `ADD` and `COPY` add a rational multiple of the donor row,
`SCALE` multiplies, and `MOVE` changes only the chart. This is the same contract
used for the helper-469 endpoint replay. It is not a native-map or caller replay.

Let S469 be the row of register 703 immediately before event 14380,
`ADD 469 += 2·703` at frame 593. Let S471 be the row of register 704 immediately
before event 13716, `ADD 471 += 2·704` at frame 593. Both rows have support 116,
and both have coefficient 1/4 on public input 1. The reads therefore contribute
coefficient 1/2 on that input. Neither snapshot is present before the owned-field
absorption that creates it: `ADD 703 += 770` at slot 13459, and `ADD 704 += 770`
at slot 13460, both at frame 593.

**Pure carriers.** After every later event, the only register whose row is a
nonzero rational multiple of S469 is 703, with multiplier 1, and only on charts
593, 712 and 127. The only such register for S471 is 704, on charts 593, 714
and 127. No other multiple occurs on any chart.

**Meetings.** Helper 469 occupies frames 3, 593, 713, 868, 996, 201, 127.
Helper 471 occupies 3, 593, 715, 876, 1002, 190, 127. The source itineraries
meet those lists, off frame 593, only at frame 127. Frame 3 is too early: the
snapshot does not exist there.

**The frame-127 meeting is not a substitute.** Delete the frame-593 read and
insert the same `ADD` immediately after the receiver's move into frame 127
(event 17008 for 469, event 16984 for 471). At that index both registers are
on frame 127 and the source row is still the snapshot. Charts are unchanged.
Final scalar rows are not:

| Read | Final row that changes on input 1 | Selected word | Delayed read |
| --- | --- | --- | --- |
| 469 ← 703 | register 666 | 0 | −1/4 |
| 469 ← 703 | register 469 | 0 | −1/4 |
| 471 ← 704 | register 180 | 0 | −1/2 |
| 471 ← 704 | register 471 | 0 | −1/4 |

The 469 delay changes 11 final rows: 120, 178, 192, 317, 469, 503, 663, 664,
666, 667, 668. The 471 delay changes 12: 180, 181, 208, 209, 333, 471, 515,
672, 673, 674, 675, 676. Deleting the original read and inserting it again at
the same index changes nothing.

For 469 the missed component is visible before frame 127. Events 15285, 16354
and 16358 still read 469 with input-1 coefficient 1/2 (readers 666, 24 and 192).
For 471, `ADD 471 += −1/2·525` at slot 15859 clears input 1 before the later
reads, so those reads are not the witness. The final-row difference is.

Direct additions from the snapshot, besides the two receivers, are recorded in
`RESULT.json`. None of those readers is a pure carrier. They do not put a second
copy of the row on a frame the receiver already visits.

## What this does not show

This does not remove either rung, retime 703 or 704, or change κ. [PR6033](https://github.com/CrocSwap/integer-mult-bounds/pull/6033)
already shows that one added paid call of any rank 1..145 defeats a free repeat
of the helper-470 profile delta. A useful carrier therefore still has to be free.
Moving 703 onto 713, 868, 996 or 201, or 704 onto 715, 876, 1002 or 190, is not
examined. Neither is a mixed row at frame 127 whose span contains the snapshot
without equaling it. The helper-469 receiver-recoding exclusion is a different
interval and is not reused as a lemma. No native, compiler, precision, outer or
all-size check is rerun. Author execution is not independent acceptance.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B research/p104-frame593-content-holders/verify.py
python3.12 -B scripts/research_package.py --package research/p104-frame593-content-holders
```

The direct verifier prints `PASS_P104_FRAME593_CONTENT_HOLDERS` and takes about
four seconds. It checks the word hash, both critical events, the carrier census,
both delay witnesses, the reinsertion identity, the multiple predicate, and a
control that changes the 469 coefficient from 2 to 1 and must yield input-1
increment 1/4 rather than 1/2.

## Open next questions

- Can 703 move onto one of 469's later frames, or 704 onto one of 471's, without
  a new paid call and without changing final scalar rows? This is the remaining
  existing-carrier route. A paid call is already fatal by the PR6033 certificate.
  First step: price replacing 703's move 593→712 by a move onto 713, then compare
  final rows. Blocker: the selected word does not contain that move.
- While 703 still holds S469 at frame 127, is S469 in the span of the other rows
  469 can read there? A mixed holder would be a different substitute. First step:
  row-reduce the co-located registers between slots 17008 and 19393, excluding
  703. Blocker: the legal read set at that frame is not settled by the pure-carrier
  census.

## Credit

The word and the open holder question are DreamingOfClouds's PR6030, the twin of
PR5907, on Ali Romman's PR5827 word and the retained P104 lineage. Nick Petalas's
PR6033 priced an added paid carrier and left the zero-cost parse open. JoyboyBrian's
helper-469 receiver-recoding package excludes a different endpoint program.
Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
