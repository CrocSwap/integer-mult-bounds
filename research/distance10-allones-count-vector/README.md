# Distance-10 all-ones short-arc source counts

**Scoped written proof, with exhaustive finite censuses of the named finite
sets. No new κ.** The selected record stays
`363005817/100000000000`. The inherited gap `28 <= f(8) <= 32` stays as
recorded by Nick Petalas's
[#5234](https://github.com/CrocSwap/integer-mult-bounds/pull/5234). This
package decides neither whether a universal length-28 word exists nor whether
either turn-off order is empty.

Take a closed length-28 word on eight sources whose multiplicities are six
fours and two twos, and suppose some circular interval of 10 steps sums to
the all-ones vector. That interval uses one source three times and the other
seven sources once. The source that appears three times is one of the six
multiplicity-4 sources. The sorted count vectors are

```text
short arc:   (3, 1, 1, 1, 1, 1, 1, 1)
complement:  (3, 3, 3, 3, 3, 1, 1, 1)
```

The distance-8 identity normalization does not apply. After the short arc is
rotated to the front, the unique coordinate permutation that sends the
repeated source to 0 and the seven once-sources to `1..7` in appearance order
leaves a normal form indexed by the three positions of source 0. There are
`C(10,3) = 120` such words. The two multiplicity-2 sources are then an
unordered pair inside `{1,...,7}`, so the label index has `C(7,2) = 21`
pairs rather than the 28 pairs of the distance-8 census. The count-feasible
index therefore has `120 * 21 = 2520` pairs. This package counts that index.
It does not enumerate complement orderings on it.

## Scope

This is the first step of open question 3 in unpaidmoon's open
[#7302](https://github.com/CrocSwap/integer-mult-bounds/pull/7302) and of
open question 2 in unpaidmoon's open
[#7300](https://github.com/CrocSwap/integer-mult-bounds/pull/7300). Both
packages settle distance-8 facts and leave distances 10, 12, and 14 open,
with the blocker that permutation normalization stops once a source repeats
on the short arc. The underlying handoff is discussion
[#1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166)
comment
[19537798](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19537798).
Its conflict-bounded run `pair 28, all-ones d=10` returned UNKNOWN. That
UNKNOWN is a search failure. It is not an input to the proof below.

Card `connector-alphabet-change`, priority revision 8. Scope status:
**changed**. The card asks for one new priced connector operation. The
alphabet stays the published singleton alphabet. Base commit
`e54523517d0f03e58352e647c403a5af3e525a57`. The priorities page at this
commit still quotes κ `0.00310045` from #5599. The live selected record is
the value pinned above, from the #7000 / #7001 admission. This package does
not edit that record.

The multiplicity shape and the gap `28 <= f(8) <= 32` are inherited from
[#5234](https://github.com/CrocSwap/integer-mult-bounds/pull/5234), as
recorded in `research/eight-source-singleton-floor/README.md`. That proof is
not replayed. Merged
[#6966](https://github.com/CrocSwap/integer-mult-bounds/pull/6966) and open
[#7088](https://github.com/CrocSwap/integer-mult-bounds/pull/7088) are not
applied. Distances 12 and 14, every length-30 profile, and every search for
a universal word stay outside this argument.

## Definitions

Sources are the standard basis of `F_2^8`. A word has prefixes `q_0 = 0` and
`q_{t+1} = q_t + e_{w_t}`. A circular interval **sums to all-ones** when the
corresponding steps sum to `255`. Universality means `P + P = F_2^8` for the
length-28 prefix set, as in Ross Richardson's
[#943](https://github.com/CrocSwap/integer-mult-bounds/pull/943). Universality
is not a hypothesis of the count vector. It is named only so the witness
below can be kept separate from a universal word.

The **multiplicity shape** `(4,4,4,4,4,4,2,2)` is the inherited necessary
shape of a universal length-28 word. A **double** is a multiplicity-2 source.
A **quadruple** is a multiplicity-4 source.

## Lemma 1: the short-arc count vector

Let an arc of `d` steps on eight sources sum to all-ones, and let `c_s` be
the number of times source `s` appears. Then `sum_s c_s e_s = sum_s e_s` in
characteristic 2, so every `c_s` is odd. An odd nonnegative integer is at
least 1, so `d = sum_s c_s >= 8` and `d` is even.

Write `c_s = 1 + 2 a_s` with integers `a_s >= 0`. For `d = 10`,

```text
sum_s (1 + 2 a_s) = 10,
sum_s a_s = 1.
```

If any `a_s >= 2`, or if two of the `a_s` are positive, the sum is at least
2. The only solution is one `a_t = 1` and the other seven `a_s = 0`. Source
`t` appears three times and the other seven sources appear once. The sorted
count vector is `(3, 1, 1, 1, 1, 1, 1, 1)`.

The same identity at excess `(d - 8) / 2` is why this uniqueness is special
to distance 10. Excess 0 is the distance-8 permutation arc already settled
by #7302. This package does not solve the equation at excess 2 or 3, so it
gives no count vector for distance 12 or 14. The verifier only checks that
its enumerator, which finds one shape at excess 1, finds more than one shape
at excess 2, and it does not record those shapes.

## Lemma 2: roles, complement vector, and five on-steps

Now assume the closed length-28 word has the multiplicity shape, and let
`m_s` be the multiplicity of source `s`. The 10-step arc and its 18-step
complement partition the word. The whole word sums to 0, and the short arc
sums to all-ones, so the complement also sums to all-ones. Every complement
count is therefore odd.

The short count `c_s` cannot exceed `m_s`. The source `t` with `c_t = 3`
cannot be a double, because `2 - 3` is negative. So `t` is a quadruple, and
its complement count is `4 - 3 = 1`. Each of the other five quadruples has
short count 1 and complement count 3. Each double has short count 1 and
complement count 1. The sorted complement vector is
`(3, 3, 3, 3, 3, 1, 1, 1)`.

| role | sources | short | complement | total |
| --- | ---: | ---: | ---: | ---: |
| repeated quadruple | 1 | 3 | 1 | 4 |
| ordinary quadruple | 5 | 1 | 3 | 4 |
| double | 2 | 1 | 1 | 2 |

The row sums are 10, 18, and 28. There are `C(8,2) = 28` ways to place the
two doubles and 8 choices for `t`. Exactly `28 * 6 = 168` of those
alignments put `t` on a quadruple and produce the table. The other
`28 * 2 = 56` put `t` on a double and are impossible for a word.

## Normalization change

#7302 and #7300 use the same three operations on a distance-8 all-ones arc.
Translation of the prefix origin sends the start of the arc to 0. Rotation
moves the arc to the front. A coordinate permutation preserves the standard
basis, the all-ones vector, and the multiplicity shape. Distance 8 uses each
source once, so relabeling by appearance order sends every such arc to the
single word `0,1,2,3,4,5,6,7`. The two doubles are then one of `C(8,2) = 28`
label pairs, and the nine arc prefixes split into three monotone flags whose
sizes sum to 9.

At distance 10 those last two sentences stop applying.

Rotation to the front and the prefix origin at 0 still apply, and the state
after the ten steps is 255. The arc is not a permutation: Lemma 1 gives a
repeated source. No coordinate permutation can send a repeated label to eight
distinct labels, so the arc cannot be sent to `0,1,2,3,4,5,6,7`.

The replacement is forced by the count vector. Let `t` be the unique source
of count 3, and let `s_1,...,s_7` be the other sources in the order of their
unique appearances. The coordinate permutation `σ(t) = 0`, `σ(s_k) = k` is
the unique relabeling that makes the repeated source be 0 and makes the
once-sources appear in increasing order. The resulting word is determined by
the three positions of source 0, a 3-subset of `{0,1,...,9}`. There are 120
such words. Every length-10 word of count type `(3, 1^7)` is the image of
exactly one of them: the repeated source and the appearance order determine
`σ`, and `σ` does not move positions.

Each such word uses all eight labels, so only the identity coordinate
permutation fixes it. The action on the set of count-type words is free.
That set has `8 * C(10,3) * 7! = 4,838,400` words, one for each choice of
the repeated source, its three positions, and the order of the other seven
labels. Each orbit has `8! = 40,320` words, and `120 * 40,320 = 4,838,400`,
so the 120 normal forms are a complete set of orbit representatives.

Lemma 2 adds the multiplicity data that the coordinate permutation does not
absorb. Source 0 is a quadruple. The two doubles are an unordered pair in
`{1,...,7}`: 21 pairs, not 28. A pair that includes 0 would make the repeated
source a double, which Lemma 2 forbids. The residual parameter of a
normalized word is the pair

```text
(positions of source 0, double labels inside {1,...,7}).
```

There are 2520 such pairs. Every one of them is count-feasible. The
complement multiset is one copy of source 0, one copy of each double, and
three copies of each of the other five labels. Concatenating the normal-form
arc with any order of that multiset gives every source an even multiplicity,
so the length-28 walk returns to 0. Each pair therefore extends to closed
words. Closure is the even-multiplicity identity. Universality asks for all
256 prefix differences, and this package does not test which of the 2520
pairs have a complement order with that property.

In this normalized position the complement starts at 255 and ends at 0. It
is an 18-step walk from weight 8 to weight 0. If `u` steps turn a bit on
and `18 - u` turn a bit off, then `8 + u - (18 - u) = 0`, so `u = 5` and
there are 13 off-steps. This count is stated after the arc start has been
translated to 0. A translation flips the on/off character of every step in
the coordinates it moves, so the same five is not claimed for an untranslated
representative. Each source starts on and ends off, and a source of
complement count `1 + 2 b` contributes exactly `b` on-steps. The role table
has `b = 1` for the five ordinary quadruples and `b = 0` for the repeated
quadruple and the two doubles. Those five on-steps are the middle flips of
the five ordinary quadruples. Their interleaving with the three single
off-steps is not determined.

The nine-prefix flag table does not transfer. A distance-10 normal form has
11 prefixes, `q_0` through `q_10`, and source 0 toggles three times. Its bit
is on after the first visit and off after the second, so some later prefix
has that bit off. The arc is not eight monotone turn-ons, and the body does
not split into the three initial-segment flags indexed by a distance-8 label
pair.

## A count-feasible word that is not universal

Positions `(0, 1, 2)` have normal form

```text
0, 0, 0, 1, 2, 3, 4, 5, 6, 7.
```

Its prefixes are

```text
0, 1, 0, 1, 3, 7, 15, 31, 63, 127, 255.
```

Bit 0 is on at prefix 1 and off at prefix 2. One complement with doubles
`1` and `2` is

```text
0, 1, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7.
```

The concatenated length-28 word has multiplicities `(4,2,2,4,4,4,4,4)`, ends
at 0, and has all-ones at step 10. Its 28 prefixes realize 58 differences.
A universal word needs 256. This word is a witness that the count vector and
the role table occur together. It is not a universal word, and it is not the
output of a search.

## Evidence class

Lemmas 1 and 2 are written proofs under the hypotheses stated above. They
are scoped to a 10-step all-ones arc, and Lemma 2 also assumes the inherited
multiplicity shape. They do not by themselves decide existence of a universal
length-28 word.

The verifier exhausts four finite domains, and the completeness reasons are
the ones in the proofs:

1. Every positive odd 8-tuple summing to 10 has entries in `{1, 3, 5}`,
   because an entry of 7 or more sums with seven 1s to at least 14. The
   `3^8 = 6561` tuples in that box contain one sorted solution, the short
   vector. An entry of 5 is inside the box and still sums to at least 12.
2. All `28 * 8 = 224` placements of the two doubles and the repeated source
   are visited. The 168 legal placements produce the complement vector, and
   the 56 illegal placements ask a double for three visits.
3. All `C(10,3) = 120` position triples are built. Each ends at 255, has the
   short count vector, is fixed by appearance normalization, and turns source
   0 off after it has turned on.
4. All `4,838,400` count-type words are generated once, by the unique triple
   `(repeated source, positions, order of the other labels)`, and each
   normalizes to the normal form of those positions. Each of the 120 orbits
   has 40,320 words.

The handoff's conflict-bounded SAT run at distance 10 is a separate
incomplete search. This package does not treat that UNKNOWN as an exclusion
or as a construction. No distance-12 or distance-14 vector is computed.

## What stays open

The inherited gap `28 <= f(8) <= 32` is unchanged. No turn-off order is
excluded. No universal length-28 or length-30 word is constructed or ruled
out. The rank floor of #6966 and the flat-step budget of #7088 are not
used. The batch minimum 538, 540, or 542 from #5234 stays blocked on finding
a word. Selected κ is unchanged. The cited `f(7) = 24` proof is not replayed.
No supplier, readout schedule, or multiplication theorem is changed.

## Evidence and reproduction

CPython 3.12 and the standard library. Normal and optimized runs call the
same `require` checks. Optimization does not remove them.

```sh
python3 -W error -I -B research/distance10-allones-count-vector/verify.py
python3 -W error -I -O -B research/distance10-allones-count-vector/verify.py
python3 -B scripts/research_package.py --package research/distance10-allones-count-vector
```

Expected marker:

```text
PASS_DISTANCE10_ALLONES_COUNT_VECTOR short=(3,1,1,1,1,1,1,1) complement=(3,3,3,3,3,1,1,1) normal_forms=120 double_pairs=21 index=2520 classes=4838400 witness_differences=58 kappa=363005817/100000000000
```

The controls are the excess-0 identity shape, the distance-8 monotone chain
and its rejection by the distance-10 normalizer, the worked prefixes, the
58-difference witness, a label swap that returns to that normal form, an odd
mutation that fails to close, and a four-visit arc that the normalizer
rejects. The card's 945-pairing connector command is orientation for a
different question and is not evidence for this count vector.

## Overlap

Open-PR and discussion search at 2026-11-12T13:02:20Z, complete pagination:
730 open PR records and 7333 discussion records. Local head
`e54523517d0f03e58352e647c403a5af3e525a57` with a complete note inventory of
10178 records. The distance-10 phrase in discussion #1166 occurs in comment
19537798, which records UNKNOWN for the anchored SAT run and asks for a
proof-producing split beginning with the monotone eight-step interval. It
does not contain this count vector. Comment 19537807 marks that search
failure done. The open PRs on this anchor are #7300 and #7302, both
distance-8 packages whose next questions name this step and then stop.
Other open-PR hits on the words "all-ones" or "count vector" are different
mechanisms. Fork branches named for this anchor are
`cursor/length28-allones-case-two-4fd2`,
`cursor/length28-allones-placement-09de`,
`cursor/length28-flat-step-budget-5b16`, and
`cursor/length28-multiplicity-sharpness-dae9`. None records the distance-10
vector. Closed-PR coverage is through the local notes and the predecessors
read above, not a full closed-PR body index. No match is a novelty
certificate.

## Open next questions

1. For one of the 120 position triples, which of the 21 double-label pairs
   can meet a difference-basis condition on the complement? A yes for any
   pair would show that distance 10 is compatible with a universal length-28
   word; a no for every pair would remove this anchor. First step: keep the
   arc prefixes of positions `(0, 1, 2)` fixed and apply one adjacent
   transposition to the complement order written above, recording whether
   the difference count rises above 58. Blocker: the legal orders of that
   18-step multiset are still too many for an unpruned listing, and one
   transposition would not be an exclusion.
2. Do the five complement on-steps and the three single off-steps have a
   turn-off split with an empty-quadrant sumset, in the sense of #7302's
   case II? The count vector says which three sources turn off only once.
   It does not say which order they do it in. First step: name the quadrant
   sequence created by one order of those three off-steps, for the single
   normal form in question 1. Blocker: the five ordinary quadruples turn
   back on between those off-steps, so the distance-8 flag table does not
   apply, and this package does not list the orders.
3. What replaces Lemma 1 at distances 12 and 14? Those anchors remain open
   in the handoff and in #7300 and #7302. First step: solve the positive-odd
   composition at that one length in its own package. Blocker: excess 1 is
   the only positive excess for which the equation in Lemma 1 has a unique
   solution, so the distance-10 vector must not be copied forward by
   changing the number 10.

## Credit

Ross Richardson, #943, for the singleton model and prefix criterion. Douglas
Colkitt, #1185, for the length-32 upper construction cited by #5234; it is
not replayed. conorholds, #3058, for `f(7) = 24`, cited by #5234 and not
replayed. Nick Petalas, #5234, for the length-28 floor, the multiplicity
shape, and the 2026-11-11 handoff whose distance-10 anchor this count vector
answers in part. The rank-at-least-4 theorem is unpaidmoon's merged #6966.
The flat-step budget is unpaidmoon's open #7088. The distance-8 placement
census is unpaidmoon's open #7300, head
`25ce041f09c0924b382b2360b5c470ad598ac978`. The distance-8 case-II obligation
is unpaidmoon's open #7302, head
`762f0ffaf66a8f954bf251c88dc6725e585f9745`. This package uses their statements
of what distance 10 still lacked. It does not recount their censuses.

Prepared by unpaidmoon with substantial Cursor Grok assistance. New work is
Apache-2.0. Independent human and proof-kernel review are unclaimed.
