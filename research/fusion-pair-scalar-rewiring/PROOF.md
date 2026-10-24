# Why no pair fuses: statements and their status

Notation follows `research/fragmentation-ceiling/PROOF.md` (#5226): a field holds one
logical value in a current frame; paid transports (climbs) change the frame and cost
its dimension gap; warps and scalar operations are free; a scalar ADD needs source and
destination in the same frame (contract H1, checked by every replay of the word).
A *fusion* replaces two consecutive rank-1 climbs `E ⊂ F ⊂ G` of one field f by the
single rank-2 climb `E ⊂ G`, lowering Λ_f by 2 − 2^t.

## Lemma 1 (CHECKED-EXACT, verify.py S1)

Every one of the 1,363 consecutive rank-1 pairs (per orientation) has at least one
event touching f while f stands in F. So a fusion must move or replace that event.

## Lemma 2 (CHECKED-EXACT, verify.py S2)

For each of the 1,261 pairs whose intermediate events are plain ADDs, some partner
field P of an intermediate ADD never occupies G at any time of the program. Since an
ADD needs P and f in one frame and f occupies only E (before) or G (after) the merged
climb, that ADD cannot be executed after the merged climb with P's own content.

## Lemma 3 (CHECKED-EXACT, verify.py S3 and the relocation test)

Exactly 12 pairs have all partners in E at some time (E = frame 0, cold helpers
241, 243, 257, 259, 273, 275, 289, 291, 305, 307, 401, 417 with partners 240, …, 416).
In each, between the partner's own climb into F and the intermediate ADD there is
exactly one event on the partner by a main field M at frame F (backward: `M += q·P`;
forward: `P += q·M`), so the value the ADD transfers at F exists only at F. M never
occupies E or G later, so no compensating ADD between f and M exists. The
frame-level relocation test, which allows the partner to receive commuting ADDs
or to be read while waiting, finds 0 relocatable pairs; deleting that one main
event makes pair 241/240 relocatable (control).

## Lemma 4 (PROVED-PAPER)

Any repair that introduces a paid job pays at least 1^t = 1 > 2 − 2^t for every
t ∈ (0, 1); a descent pays ≥ r^t + (9+r)^t − 9^t ≥ 1.99022 at t\* (#5226 Theorem D).
Hence a fusion can only be funded by free operations, which Lemmas 1–3 exclude for
operations that keep the partners' own contents, and the row-level searches
(RESULT.json, tools/) exclude for arbitrary same-frame linear recombination of the
contents present in a frame (pre- or post-payment in the exact window; greedy
propagation downstream), on the backward word.

## Scope and status

| claim | status |
|---|---|
| S1, S2, S3, relocation count, controls | CHECKED-EXACT (verify.py, both orientations) |
| price order (Lemma 4) | PROVED-PAPER; constants CHECKED-EXACT |
| row-level pre/post-payment: 0 pairs (backward) | CHECKED-EXACT by tools/compsearch.py, recorded |
| row-level propagated repayment: 0 pairs (backward) | computational, greedy, sampled in frames with > 80 members; recorded |
| forward row-level searches | not run to completion (transpose of backward) |
| 102 pairs with a warp or scale between the climbs | outside the claim |
| helper-input relations (#5377, #5383) | outside the claim |
