# Length-28 double sojourns use at least four other sources

**Scoped written proof with finite corroboration. No new κ.** Selected κ stays
`781451/250000000`. The gap `28 <= f(8) <= 32` is unchanged. This does not
decide whether a universal length-28 word exists.

In the restored binary singleton model, let a closed length-28 word use six
sources four times and two sources twice. If its prefix set `P` satisfies
`P+P = F_2^8`, then each of the four arcs determined by the two multiplicity-2
sources uses at least four other sources.

## Scope

The question is the sharpness question left open by
[#5234](https://github.com/CrocSwap/integer-mult-bounds/pull/5234): does a
universal word with multiplicities `(4,4,4,4,4,4,2,2)` exist? This package
proves one necessary constraint on any such word. It does not construct a
word, exclude every word, or rerun the length-30 sojourn argument.

Card `connector-alphabet-change`, priority revision 8. Scope status:
**changed**. The card asks for one new connector operation. The alphabet stays
the published singleton alphabet; only the length-28 arc constraint is new.
Base commit `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

## Definitions

Sources are the standard basis of `F_2^8`. A closed word has even positive
counts and returns to `0`. For a word `w_0,...,w_27`, the prefixes are
`q_0 = 0` and `q_{t+1} = q_t + e_{w_t}`. Universality means
`P + P = F_2^8` with `P = {q_0,...,q_27}`, as in Ross Richardson's
[#943](https://github.com/CrocSwap/integer-mult-bounds/pull/943) and the
statement recorded by [#5234](https://github.com/CrocSwap/integer-mult-bounds/pull/5234).

A multiplicity-2 source `α` occurs twice. On the circular word those two
occurrences split the remaining letters into two arcs. The **rank** of an arc
is the number of distinct sources in it. Those sources are basis vectors, so
the arc's projected states lie in a coset of a coordinate subspace of that
dimension.

## Proof

Suppose, for a contradiction, that some arc of `α` has rank `ρ ≤ 3`. Rotate
the circular word so that one `α` step is first and the low-rank arc is the
arc that follows it. Translate the visited set so the start is `0`. Rotation
preserves the arc sources and the difference set; translation preserves
differences. The chosen arc then has `s` steps and starts at projection `0`
after the first `α` step. Its projected image `S_B` lies in a coordinate
subspace `V` of dimension `ρ`. The complementary arc has projected image
`S_A`. The two projected sequences together have length 28, so
`|S_A| + |S_B| ≤ 28`. Deleting `α` is a bijection on each layer, and
universality is equivalent to

```text
S_A + S_B = F_2^7
(S_A + S_A) ∪ (S_B + S_B) = F_2^7.
```

**Rank at most 2.** Here `|S_B| ≤ 2^ρ ≤ 4`, so
`|S_A| · |S_B| ≤ 4 · 24 = 96 < 128`. The cross sum cannot be all of `F_2^7`.

**Rank 3 and `|S_B| ≤ 7`.** Write `F_2^7 = V × W` with `|V| = 8` and
`|W| = 16`. Every `W`-fiber `F_w` of `S_A` must satisfy `F_w + S_B = V`. A
one-point fiber produces only `|S_B| ≤ 7` sums, so every fiber has at least
two points. Thus `|S_A| ≥ 32`. But `|S_A| ≤ 28 - |S_B| ≤ 27`.

**Rank 3 and `|S_B| = 8`.** Then `S_B = V`, so the arc is a walk of at least
7 steps through all eight points of `V`. Its three sources form the set `T`.

- If `T` is three multiplicity-4 sources, the other multiplicity-2 source and
  the other three multiplicity-4 sources lie outside `T`. They contribute
  `2 + 12 = 14` steps, all in the complementary arc, and those are exactly the
  steps that change the `W`-coordinate. The complementary arc starts in the
  identity coset of `V`. Fourteen such steps visit at most 15 cosets. Covering
  `F_2^7` by `S_A + V` needs all 16 cosets.

- If `T` contains the other multiplicity-2 source and two multiplicity-4
  sources, those three sources occur `2 + 4 + 4 = 10` times in the whole word.
  At least 7 of those steps lie in the low-rank arc, so the complementary arc
  has at most 3 steps from `T`. Only those steps change its `V`-coordinate, so
  that coordinate takes at most 4 values. A 4-point set in `F_2^3` has at most
  `1 + C(4,2) = 7` pairwise sums, including `0`. Some nonzero `v*` is missed.
  For any nonzero `w`, `(v*, w)` is outside `V`, hence not in `S_B + S_B`, and
  it is not in `S_A + S_A` either.

Both placements of the other double are impossible. Therefore every
multiplicity-2 arc uses at least four other sources.

The same counting does not forbid an arc of rank 4. Five or more
`V`-coordinates can cover `F_2^3`: `{0,1,2,3,4}` does. Reaching five
coordinates would take at least four complementary flat steps, and the
rank-3 budget above supplies at most three.

## What is not claimed

No universal length-28 word is constructed or ruled out. In particular, words
whose four multiplicity-2 arcs all have rank at least 4 remain open, so this
is not a proof that `f(8) > 28`. A failed or unfinished search is not such a
proof. The cited bound `f(7) = 24` is not replayed; the argument uses only the
stated multiplicity vector. No supplier, readout schedule, selected-frontier
record, or multiplication theorem is changed.

## Evidence and reproduction

The exclusions are the counting arguments above. The verifier checks the
numerical bounds, exhausts all 162 nonempty subsets of `F_2^3` of size at
most 4, exhausts all 320 flat walks of length at most 3 on eight starts, and
checks that the five-point set `{0,1,2,3,4}` does cover. It also replays the
length-32 Gray concatenation as a positive coverage control and rejects one
relabelled step and one deleted step. CPython 3.12 and the standard library:

```sh
python3 -W error -I -B research/length28-sojourn-rank/verify.py
python3 -W error -I -O -B research/length28-sojourn-rank/verify.py
python3 -B scripts/research_package.py --package research/length28-sojourn-rank
```

Expected marker:
`PASS_LENGTH28_SOJOURN_RANK subsets=162 paths=320 worst_missed=7 gray=256`.

## Overlap

Open-PR and discussion search at 2026-11-10T02:22:37Z, complete pagination:
895 open PR records and 6934 discussion records, local head
`7c49fe32c55de02c2c873655c804b16e4c3fef0a` with 8919 note records. Terms
`4,4,4,4,4,4,2,2`, `length-28`, and `sojourn rank`. Matches were the
predecessor statements of this open question, not a decision of it:

- [#5234](https://github.com/CrocSwap/integer-mult-bounds/pull/5234) proves
  `28 <= f(8) <= 32` and that these multiplicities are necessary at length 28.
  Its first open question is the existence question. No word is given there.
- [#5430](https://github.com/CrocSwap/integer-mult-bounds/pull/5430) excludes
  one fixed 24-state projection from lifting to 28 steps. It does not exclude
  every projection or every multiplicity vector.
- [#6497](https://github.com/CrocSwap/integer-mult-bounds/pull/6497) attains a
  36-step lift of that same fixed projection, with counts
  `(4,4,4,4,4,2,2,12)`.
- [#6943](https://github.com/CrocSwap/integer-mult-bounds/pull/6943) records
  length-30 sojourn obstructions and leaves length 28 open. The present
  argument is the length-28 rank bound, not that length-30 package and not
  its constrained length-30 existence question.
- Discussion
  [#1166 comment 19377982](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19377982)
  releases the length-30 search failure and does not decide length 28.

Closed-PR coverage is through the local notes and this targeted reading, not
a full closed-PR body index. No match is a novelty certificate.

## Open next questions

1. Does a universal length-28 word exist in which every multiplicity-2 arc
   uses at least four other sources? A yes answer shows the new floor 28 is
   sharp. The rank-at-most-3 arcs are already impossible, and a five-point
   set in `F_2^3` shows the four-value count does not extend unchanged.
   First step: fix one multiplicity-2 source, require both arcs to use four
   or more labels, and test the resulting flat-step budget before a word
   search. Blocker: that budget no longer forces fewer than five flat
   coordinates on the complement.

2. Does the same arc constraint, or a witness, decide the untouched query
   gap 538, 540, or 542 from #5234? First step: price one universal
   length-28 word if question 1 finds one; otherwise the query gap stays
   where #5234 left it. Blocker: no length-28 universal word is known.

## Credit

Ross Richardson, #943, for the singleton model and prefix criterion. Douglas
Colkitt, #1185, for the length-32 Gray upper construction checked here as a
positive control. conorholds, #3058, for `f(7) = 24` and the eight-source
question; that theorem is cited by #5234 and is not replayed. Nick Petalas,
#5234, for the length-28 floor, the multiplicity shape, and the open
sharpness question. Nicholas Stone, #5430, for the fixed-projection matching
obstruction, which this arc argument does not reuse. The length-30 sojourn
package in #6943 is a different length.

Prepared by unpaidmoon with substantial Cursor Grok assistance. New work is
Apache-2.0. Independent human and proof-kernel review are unclaimed.
