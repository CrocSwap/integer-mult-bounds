# Length-28 all-ones distance 8 splits by turn-off order

**Scoped written proof with finite corroboration. No new κ.** The selected
record stays `363005817/100000000000`. The inherited gap `28 <= f(8) <= 32`
is unchanged. This does not decide whether a universal length-28 word exists.

In the restored binary singleton model, take a closed length-28 word that uses
six sources four times and two sources twice, and suppose two prefixes differ
by the all-ones vector across an 8-step arc. After translation, rotation, and
coordinate relabeling, that arc is `0,1,2,3,4,5,6,7`. The two multiplicity-2
sources `a < b` each turn off once in the complementary 20 steps. If `b` turns
off before `a`, no prefix has bits `(a, b) = (0, 1)`, and the three nonempty
body slices `P00`, `P10`, and `P11` are pairwise difference bases of `F_2^6`.
The nine arc prefixes already force three flags in those slices. Their
pairwise sums are direct and have size at most 16, so the flags themselves
miss the obligation. The complement has to add further body states. The same
reduction does not apply when `a` turns off first.

## Scope

This is item 2 of the handoff-first list on discussion
[#1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166)
after the selected commit
`e54523517d0f03e58352e647c403a5af3e525a57`: the eight-source search-failure
handoff
[comment 19537798](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19537798).
That handoff asks for a proof-producing split of the length-28 all-ones
cases, beginning with the placements of the two multiplicity-2 letters in a
monotone eight-step interval. The single fixed prefix in the handoff is the
normal form below. The new statement is the turn-off split and the case-II
sumset obligation.

Card `connector-alphabet-change`, priority revision 8. Scope status:
**changed**. The card asks for one new priced connector operation. The
alphabet stays the published singleton alphabet. Base commit
`e54523517d0f03e58352e647c403a5af3e525a57`.

The multiplicity shape and the inequality `28 <= f(8) <= 32` are inherited
from Nick Petalas's
[#5234](https://github.com/CrocSwap/integer-mult-bounds/pull/5234). The
rank-at-least-4 constraint is inherited from
[#6966](https://github.com/CrocSwap/integer-mult-bounds/pull/6966). Neither
proof is replayed. Distances 10, 12, and 14, and every length-30 profile,
stay outside this argument.

## Definitions

Sources are the standard basis of `F_2^8`. A closed word `w_0,...,w_27` has
prefixes `q_0 = 0` and `q_{t+1} = q_t + e_{w_t}`, with `q_28 = 0`.
Universality means `P + P = F_2^8` for `P = {q_0,...,q_27}`, as in Ross
Richardson's [#943](https://github.com/CrocSwap/integer-mult-bounds/pull/943).

The **body** of a label pair `a < b` is the other six coordinates, packed in
increasing label order as bits of `F_2^6`. A prefix lies in quadrant `(x, y)`
when its `a`-bit is `x` and its `b`-bit is `y`. The slice `Pxy` is the set of
body projections of prefixes in that quadrant.

The **rank** of an arc between the two occurrences of a multiplicity-2 source
is the number of distinct sources strictly between them, as in #6966.

## Proof

**Shorter all-ones distances.** Suppose `q_i + q_j = 255` with `i < j`. The
steps from `i` to `j` sum to 255, so each source appears oddly on that arc.
The whole word sums to 0, so the complementary arc has the same sum and the
same odd-count property. Eight odd positive counts have even sum and sum at
least 8. Both arc lengths are therefore even and at least 8. They add to 28,
so the shorter length lies in `{8, 10, 12, 14}`.

**Distance 8.** An 8-step arc with eight odd positive counts uses each source
once. It is a permutation `π`. Translate by `q_i`, rotate that arc to the
front, and apply the coordinate permutation that sends `e_{π(t)}` to `e_t`.
Translation preserves differences, rotation preserves the circular difference
set, and a coordinate permutation preserves the standard basis, the all-ones
vector, and the multiplicity pattern. The arc becomes `0,1,2,3,4,5,6,7`, and
the state after those steps is 255. Every permutation and every coordinate
permutation of 255 is checked by the verifier: there are `8! = 40320` of
them, and each relabels onto the chain

```text
0, 1, 3, 7, 15, 31, 63, 127, 255.
```

Each multiplicity-2 source already occurs once on this arc, at the position
equal to its new label. The two labels are some pair `a < b` in `0..7`.
There are 28 such pairs, and the normal form runs through all of them. The
complement is the remaining 20 steps, from 255 back to 0. It uses `a` and `b`
once each and every other source three times.

**Flip schedule.** A 20-step walk from weight 8 to weight 0 has exactly 6
steps that turn a bit on and 14 steps that turn a bit off: if `u` is the
number of on-steps, then `u + (20 - u) = 20` and `8 + u - (20 - u) = 0`.
Each complement bit starts at 1 and ends at 0, so its flips alternate and
begin with an off-step. A multiplicity-2 source flips once, from 1 to 0. A
multiplicity-4 source flips off, on, off. The six on-steps are exactly those
six middle flips. Every ordering of this multiset has the same pattern. The
pattern does not delete orderings. Each double therefore has one on-interval:
it turns on during the arc and off once during the complement.

**Two cases.** The arc turns `a` on before `b`. The two complement off-steps
have two orders.

- Case I: `a` turns off before `b`. The quadrant `(0, 1)` occurs between
  those two steps.
- Case II: `b` turns off before `a`. The quadrant sequence is
  `(0,0), (1,0), (1,1), (1,0), (0,0)`. Quadrant `(0, 1)` does not occur, so
  `P01` is empty.

**Case II sumsets.** A difference of two prefixes has `(a, b)` bits equal to
the xor of their quadrants. With `P01` empty, the only surviving pairs are:

| target bits `(a, b)` | only surviving slices |
| --- | --- |
| `(1, 0)` | `P00 + P10` |
| `(1, 1)` | `P00 + P11` |
| `(0, 1)` | `P10 + P11` |

Universality requires every body vector with every `(a, b)` pattern, so

```text
P00 + P10 = P00 + P11 = P10 + P11 = F_2^6.
```

The pattern `(0, 0)` is the union of the three within-slice sumsets. Case I
keeps `P01` nonempty, so each cross pattern is a union of two slice sums.
The three-sumset reduction is special to case II.

**Forced flags.** On the arc the body bits turn on in order and do not turn
off. Write `n00 = a`, `n10 = b - a - 1`, and `n11 = 7 - b`.

- `P00` contains the initial-segment flag of the first `n00` body bits,
  a set `F00` of size `n00 + 1`.
- `P10` contains that block's all-ones vector plus the initial-segment flag
  of the next `n10` body bits, a set `F10` of size `n10 + 1`.
- `P11` contains the all-ones vector of the first two blocks plus the
  initial-segment flag of the last `n11` body bits, a set `F11` of size
  `n11 + 1`.

These are the body states of `q_0,...,q_8`. The three sizes are positive and
sum to 9.

The three blocks of body bits are disjoint. `F00` varies only in the first
block. `F10` is a constant on the first block plus a flag in the second.
`F11` is a constant on the first two blocks plus a flag in the third. A sum
of one vector from each of two flags therefore separates into independent
blocks, and distinct pairs give distinct sums:

```text
|F00 + F10| = |F00| |F10|,
|F00 + F11| = |F00| |F11|,
|F10 + F11| = |F10| |F11|.
```

For any positive integers `x, y, z` with `x + y + z = 9`, each pairwise
product is at most 16, because the two factors sum to at most 8. Every
forced product is therefore at most 16, which is strictly less than 64. The
flags do not meet the case-II obligation. Any universal case-II word has to
add further body states during the complement.

The exact sizes and sumset cardinalities are:

| `a, b` | `|F00|, |F10|, |F11|` | sumset sizes |
| --- | --- | --- |
| 0, 1 | 1, 1, 7 | 1, 7, 7 |
| 0, 2 | 1, 2, 6 | 2, 6, 12 |
| 0, 3 | 1, 3, 5 | 3, 5, 15 |
| 0, 4 | 1, 4, 4 | 4, 4, 16 |
| 0, 5 | 1, 5, 3 | 5, 3, 15 |
| 0, 6 | 1, 6, 2 | 6, 2, 12 |
| 0, 7 | 1, 7, 1 | 7, 1, 7 |
| 1, 2 | 2, 1, 6 | 2, 12, 6 |
| 1, 3 | 2, 2, 5 | 4, 10, 10 |
| 1, 4 | 2, 3, 4 | 6, 8, 12 |
| 1, 5 | 2, 4, 3 | 8, 6, 12 |
| 1, 6 | 2, 5, 2 | 10, 4, 10 |
| 1, 7 | 2, 6, 1 | 12, 2, 6 |
| 2, 3 | 3, 1, 5 | 3, 15, 5 |
| 2, 4 | 3, 2, 4 | 6, 12, 8 |
| 2, 5 | 3, 3, 3 | 9, 9, 9 |
| 2, 6 | 3, 4, 2 | 12, 6, 8 |
| 2, 7 | 3, 5, 1 | 15, 3, 5 |
| 3, 4 | 4, 1, 4 | 4, 16, 4 |
| 3, 5 | 4, 2, 3 | 8, 12, 6 |
| 3, 6 | 4, 3, 2 | 12, 8, 6 |
| 3, 7 | 4, 4, 1 | 16, 4, 4 |
| 4, 5 | 5, 1, 3 | 5, 15, 3 |
| 4, 6 | 5, 2, 2 | 10, 10, 4 |
| 4, 7 | 5, 3, 1 | 15, 5, 3 |
| 5, 6 | 6, 1, 2 | 6, 12, 2 |
| 5, 7 | 6, 2, 1 | 12, 6, 2 |
| 6, 7 | 7, 1, 1 | 7, 7, 1 |

**The size budget does not finish the exclusion.** The full slices still
satisfy `|P00| + |P10| + |P11| <= 28`, because every prefix lies in one
slice. Positive integers `x, y, z` with `x + y + z <= 28` and
`xy, xz, yz >= 64` exist; `(8, 8, 8)` is one. Meeting the numerical room is
not a construction. This package contains no search of the complement walks
that would have to fill that room.

**Rank floor, both cases.** #6966 requires each of the four double arcs to
use at least four other sources. That constraint does not delete a label
pair from either turn-off case. For the six sources other than `a` and `b`,
written in increasing order as `t1,...,t6`, form the background word

```text
(t1,...,t6, t6,...,t1, t1,...,t6)
```

of length 18. Insert `a` and `b` into two distinct slots of a 20-step word
and fill the other slots from this background. There are `28 * 20 * 19 = 10640`
insertion indices. In lexicographic slot order, every label pair has a case-I
word and a case-II word whose four arc ranks are at least 4. The recorded
witnesses cover at most 111 of the 256 differences. They are compatibility
witnesses for the rank floor. They are not universal words, and the scan does
not rank the insertions that follow the first success.

## What this leaves open

No universal length-28 word is constructed or ruled out. Case II remains open
because the complement may still enlarge the three slices. Case I remains
open because the empty-quadrant reduction does not apply. Distances 10, 12,
and 14 are untouched. The cited bound `f(7) = 24` is not replayed. No
supplier, readout schedule, selected-frontier record, or multiplication
theorem is changed. The batch minimum 538, 540, or 542 from #5234 stays
blocked on finding a word. A failed or unfinished search is not an exclusion
of either turn-off order.

## Evidence and reproduction

The exclusions and obligations are the counting arguments above. The verifier
checks the distance set `{8,10,12,14}`, all 40320 relabelings, all 28 positive
compositions of 9, the flag table, the abstract triple `(8,8,8)`, the 10640
insertion indices, 28 witnesses in each case, the Gray control, and rejecting
mutations. CPython 3.12 and the standard library:

```sh
python3 -W error -I -B research/length28-allones-case-two/verify.py
python3 -W error -I -O -B research/length28-allones-case-two/verify.py
python3 -B scripts/research_package.py --package research/length28-allones-case-two
```

Expected marker:

```text
PASS_LENGTH28_ALLONES_CASE_TWO permutations=40320 flags=28 max_forced_sum=16 case_i=28 case_ii=28 min_rank=4 witness_coverage_max=111 gray_distance=16
```

The length-32 Gray concatenation has exactly one unordered prefix pair at
difference 255, at circular distance 16, and it covers all 256 differences.
Deleting the last complement step of a witness breaks closure. Replacing that
step, or using a constant 20-step word, fails the off/on/off schedule. One
changed Gray label fails closure or coverage.

## Overlap

Targeted open-PR search on 2026-11-11 for `all-ones d=8` and `length-28
all-ones` returned no upstream records. That search is not a complete open-PR
or closed-PR body index. Local fork branches were listed before writing.
Closed-PR coverage is the reading below. No match is a novelty certificate.

- [#5234](https://github.com/CrocSwap/integer-mult-bounds/pull/5234) proves
  `28 <= f(8) <= 32` and the multiplicity shape. Its existence question is
  the parent question. No word is given there.
- [#6966](https://github.com/CrocSwap/integer-mult-bounds/pull/6966) proves
  the rank-at-least-4 constraint used here as an inherited filter. It does
  not normalize an all-ones interval.
- [#6943](https://github.com/CrocSwap/integer-mult-bounds/pull/6943),
  [#7015](https://github.com/CrocSwap/integer-mult-bounds/pull/7015), and
  [#7093](https://github.com/CrocSwap/integer-mult-bounds/pull/7093) are
  length-30 statements.
- [#7088](https://github.com/CrocSwap/integer-mult-bounds/pull/7088) is the
  pending flat-step budget. Its constants are not used and not re-proved.
- Fork branch `cursor/length28-allones-placement-09de` at
  `25ce041f09c0924b382b2360b5c470ad598ac978`, draft
  [unpaidmoon#293](https://github.com/unpaidmoon/integer-mult-bounds/pull/293),
  counts rank-feasible segment matrices on this same normal form. It reports
  that all 28 label pairs survive that matrix test. It does not split
  turn-off order, does not form the body slices, and does not prove the flag
  bound. This package does not recount those matrices. In that census, case
  II is the placements whose earlier complement copy is the larger arc label.

The handoff's SAT rows, including the single fixed prefix `0..7` with
`q_8 = 255`, returned UNKNOWN. They did not separate the 28 label pairs or
the two turn-off orders.

## Open next questions

1. Does any case-II complement put enough extra body states into the three
   slices to make all three pairwise sums equal `F_2^6`? A no answer would
   remove one turn-off order from the distance-8 family. The forced flags
   reach at most 16 sums, while each required sumset has size 64. First step:
   for labels `(6, 7)`, where one slice already contains the full 6-bit flag,
   list the positive size triples inside the 28-prefix budget whose products
   are at least 64, and test only walks that realize those sizes. Blocker:
   the legal complement orderings are still too many for an unpruned listing,
   and a partial search would not be an exclusion.

2. Does case I contain a universal length-28 word? The empty-quadrant
   reduction does not apply, so both turn-off orders have to be decided
   before the distance-8 anchor can be removed. First step: write the
   two-sumset union that replaces each cross condition when `P01` is
   nonempty. Blocker: that union is weaker than a single sumset, and no
   universal length-28 word is known.

3. Do the all-ones distances 10, 12, and 14 have a turn-off split with a
   forced-flag bound? The handoff leaves those anchors unresolved, and
   distance 8 is the only length whose short arc is a permutation. First
   step: for distance 10, record that the short arc uses one source three
   times and the other seven once. Blocker: the identity normalization and
   the nine-prefix flag decomposition stop applying once a source repeats
   inside the arc.

## Credit

Ross Richardson, #943, for the singleton model and prefix criterion. Douglas
Colkitt, #1185, for the length-32 Gray upper construction checked here as a
positive control. conorholds, #3058, for `f(7) = 24`; that theorem is cited
by #5234 and is not replayed. Nick Petalas, #5234, for the length-28 floor,
the multiplicity shape, and the 2026-11-11 handoff that asks for this
all-ones split. The rank-at-least-4 theorem is unpaidmoon's merged #6966.
The parallel rank-matrix census is unpaidmoon's fork branch
`cursor/length28-allones-placement-09de`.

Prepared by unpaidmoon with substantial Cursor Grok assistance. New work is
Apache-2.0. Independent human and proof-kernel review are unclaimed.
