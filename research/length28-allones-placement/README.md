# Length-28 all-ones placements of the two double sources

**Exhaustive finite census, plus two written rank bounds. No new κ.** The
selected record stays `363005817/100000000000`. The inherited gap
`28 <= f(8) <= 32` is unchanged. This does not decide whether a universal
length-28 word exists.

In the restored binary singleton model, take a closed length-28 word that uses
six sources four times and two sources twice, and suppose its prefix set `P`
satisfies `P+P = F_2^8`. Suppose some circular interval of eight steps sums to
the all-ones vector. After translation, rotation, and labeling sources by their
order on that interval, the interval is the word `0,1,2,3,4,5,6,7`. Exactly
2510 of the 10640 ways to place the two later copies of the multiplicity-2
sources admit no segment-count matrix whose four arcs all have rank at least
4. The cited flat-step budget of open
[#7088](https://github.com/CrocSwap/integer-mult-bounds/pull/7088), which this
package does not re-prove, rules out 4469 of the same 10640 placements. All
28 choices of which two labels are the double sources survive both filters.

## Scope

This is the fifth concrete next step in the two open handoffs posted on
discussion #1166 after the selected commit
`e54523517d0f03e58352e647c403a5af3e525a57`:

1. A complete characteristic-7 word or a complete exclusion.
2. An adaptive cube split, with checked proofs, of the unfinished c = 7 cubes.
3. A word search around the two published floor words beyond two transpositions.
4. A structural c = 7 exclusion outside the centre-only and diagonal hypotheses.
5. A proof-producing split of the length-28 all-ones cases, beginning with the
   placements of the two multiplicity-2 letters in a monotone eight-step
   interval. That is this package.
6. A named length-30 encoding of the rank-4 layer restriction in #7093.

The first four steps are the open questions in
[comment 19537594](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19537594).
Steps 5 and 6 are the open questions in
[comment 19537798](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19537798).
None of the six is the title of an excluded or already opened unpaidmoon PR.
Item 5 is the one taken here.

Card `connector-alphabet-change`, priority revision 8. Scope status:
**changed**. The card asks for one new priced connector operation. The
alphabet stays the published singleton alphabet. The new fact is the placement
split above. Base commit `e54523517d0f03e58352e647c403a5af3e525a57`.

Merged [#6966](https://github.com/CrocSwap/integer-mult-bounds/pull/6966) is
used only for the necessary condition that every multiplicity-2 arc of a
universal word has rank at least 4. Its proof is not replayed. Open #7088 is
cited only for the optional stronger budget. The distances 10, 12, and 14, and
the length-30 question, are not enumerated.

## Normalization

Sources are the standard basis of `F_2^8`. Prefixes of `w_0,...,w_27` are
`q_0 = 0` and `q_{t+1} = q_t + e_{w_t}`. Universality means
`P+P = F_2^8` with `P = {q_0,...,q_27}`, as in Ross Richardson's
[#943](https://github.com/CrocSwap/integer-mult-bounds/pull/943) and the
length bound recorded by
[#5234](https://github.com/CrocSwap/integer-mult-bounds/pull/5234).

An 8-step circular interval summing to all-ones uses each source once: the
interval has eight steps, the target has eight odd coordinates, and every
extra visit would add two occurrences of some source. Rotate that interval to
the front and translate its start to `0`. Relabel sources by appearance order.
The relabeling preserves all-ones, the standard-basis alphabet, and the
multiplicity pattern. The word then begins `0,1,2,3,4,5,6,7`, and the state
after those steps is all-ones.

Each multiplicity-2 source already occurs once in that interval, so its other
occurrence lies in the remaining 20 steps. Call the source that reappears
first `early` and the other `late`. Their suffix positions `i < j` cut the
other 18 steps into segments of lengths

```text
la = i,  lb = j - i - 1,  lc = 19 - j.
```

Those 18 steps are three copies of each of the other six sources. There are
`8 * 7 * C(20,2) = 10640` ordered placements.

The rank of an arc is the number of distinct sources strictly between the two
occurrences of its double, as in #6966. The forward arc of `early` contains
the monotone tail `{early+1,...,7}` and segment A. Its backward arc contains
the monotone head `{0,...,early-1}`, the suffix step `late`, and segments B
and C. The forward arc of `late` contains `{late+1,...,7}`, the suffix step
`early`, and segments A and B. Its backward arc contains `{0,...,late-1}` and
segment C.

## Two rank bounds

**Short prefix.** The forward arc of `early` has rank at most
`(7 - early) + la`: the tail contributes `7 - early` sources, and segment A
has only `la` steps. If `la < early - 3`, that rank is at most 3. A direct
count gives 1260 such placements. By #6966, none of them occurs in a universal
word.

**Long prefix.** If `early = 0` and `la >= 16`, the backward arc of source 0
has `19 - la <= 3` steps, so its rank is at most 3. There are 42 such
placements. Source 0 has empty monotone head, so this family is disjoint from
the short-prefix family. By #6966, none of them occurs in a universal word.

## Exhaustive census

**Rank at least 4.** Exactly 2510 of the 10640 placements have no
multiplicity matrix, with each of the six quadruple sources used three times
and the three column sums equal to `(la, lb, lc)`, in which all four arcs have
rank at least 4. The other 8130 placements have at least one such matrix.
The 1302 placements named above are included in the 2510. The remaining 1208
fail only after the matrices are examined. One of them is `early = 0`,
`late = 5`, and `(la, lb, lc) = (0, 0, 18)`: the forward arc of source 5 is
exactly `{0, 6, 7}`.

Every one of the 28 unordered label pairs occurs among the 8130. The merged
rank bound therefore does not delete a pair inside the normalized interval.
It deletes placements.

The enumeration visits every nonnegative integer solution of the row-sum
equations. A partial assignment is dropped only when one column already
exceeds its target, or when the untouched rows cannot meet the residual
targets even if each puts all three copies on those columns. Both drops have
no solutions. On the 1064 placements with `la = 0`, each quadruple source has
four ways to split its three copies between the other two segments. That
independent product agrees with the search on both the rank test and the
budget test below, including the forced rejections.

**Cited budget.** Assume, as stated by open #7088 and not re-proved here, that
a universal word also forces every ordered arc-rank pair into
`{(4,7),(5,7),(6,7),(7,7)}` and, when the smaller rank is `r < 7`, puts at
least `b(r)` steps of that arc's support on the complementary arc, where
`b(4) = 6`, `b(5) = 10`, and `b(6) = 14`. Under that hypothesis, exactly 4469
placements have no matrix meeting the budget, and the other 6171 do. All 28
label pairs still occur. A placement counted here is not a word: the matrix
fixes segment counts, and the order inside a segment is still free.

## What is not claimed

No universal length-28 word is constructed or ruled out. Surviving placements
are multiplicity matrices, not prefix-difference bases. The distances 10, 12,
and 14 are untouched, as is length 30. The cited bound `f(7) = 24` is not
replayed. No supplier, readout schedule, selected-frontier record, or
multiplication theorem is changed. The batch minimum 538, 540, or 542 from
#5234 remains blocked on finding a word. If the #7088 budget is not necessary,
the rank-at-least-4 census and the two written bounds still stand.

## Evidence and reproduction

CPython 3.12 and the standard library. The census uses four worker processes.
Normal and optimized runs call the same `require` checks:

```sh
python3 -W error -I -B research/length28-allones-placement/verify.py
python3 -W error -I -O -B research/length28-allones-placement/verify.py
python3 -B scripts/research_package.py --package research/length28-allones-placement
```

Expected marker:

```text
PASS_LENGTH28_ALLONES_PLACEMENT domain=10640 rank4_survivors=8130 rank4_impossible=2510 budget_survivors=6171 budget_impossible=4469 pairs=28 short_prefix=1260 long_prefix=42
```

The controls are the short-prefix and long-prefix thresholds, an explicit
rank-1 word for `early = 7` and `la = 3`, the adjacent rank-3 example above,
one matrix for labels `(0, 1)` that meets the cited budget, and the
empty-prefix product.

## Overlap

Open-PR and discussion search at 2026-11-11T15:33:13Z, complete pagination:
592 open PR records and 7254 discussion records. Local head
`e54523517d0f03e58352e647c403a5af3e525a57` with a complete note inventory.
Terms `monotone eight-step`, `all-ones cases`, and `multiplicity-2 letters`.
The only remote match is the handoff itself, discussion #1166 comment
19537798. That comment records a bounded SAT search failure and asks for this
split; it does not contain the census.

The length-28 predecessors are merged #6966 and open #7088. #6966 proves the
rank-at-least-4 input and asks for the flat-step budget. #7088 computes that
budget and leaves the four surviving rank pairs unsearched. Neither one
normalizes an all-ones interval of length 8 or counts these 10640 placements.
#7015 and #7093 are length-30 statements. Closed-PR coverage is through the
local notes and those readings, not a full closed-PR body index. No match is
a novelty certificate.

## Open next questions

1. Does any of the 8130 rank-feasible matrices have an ordering whose prefix
   set is a difference basis of `F_2^8`? A yes answer would show that the
   length-28 floor is compatible with an all-ones interval of length 8.
   First step: order the explicit `(0, 1)` matrix whose 18 quadruple steps all
   lie in the final segment. Blocker: that ordering is still unresolved, and a
   failed search of one matrix would not empty the 8130.
2. Do the all-ones distances 10, 12, and 14 have a segment census of the same
   kind? The handoff leaves those three anchors open. First step: write the
   repeated-source count vector on an interval of length 10. Blocker: the
   identity normalization and the suffix counts both change once a source
   repeats inside the interval.
3. Does a surviving word decide whether the #5234 batch minimum is 538, 540,
   or 542 queries? First step: price one universal length-28 word if question
   1 finds one. Blocker: no such word is known.

## Credit

Ross Richardson, #943, for the singleton model and prefix criterion. Douglas
Colkitt, #1185, for the length-32 Gray upper construction; it is not replayed
here. conorholds, #3058, for `f(7) = 24`, cited by #5234 and not replayed.
Nick Petalas, #5234, for the length-28 floor and the multiplicity shape, and
for the 2026-11-11 handoff that asks for this all-ones split. The
rank-at-least-4 theorem is unpaidmoon's merged #6966. The optional budget
constants are unpaidmoon's open #7088.

Prepared by unpaidmoon with substantial Cursor Grok assistance. New work is
Apache-2.0. Independent human and proof-kernel review are unclaimed.
