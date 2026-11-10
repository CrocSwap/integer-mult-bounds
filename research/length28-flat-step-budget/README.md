# Length-28 flat-step budget forces a rank-7 arc

**Scoped obstruction with an exhaustive cube census. No new κ.** Selected κ
stays `781451/250000000`. The gap `28 <= f(8) <= 32` is unchanged. This does
not decide whether a universal length-28 word exists, and it does not prove
`f(8) > 28`.

In the restored binary singleton model, let a closed length-28 word use six
sources four times and two sources twice, and suppose its prefix set `P`
satisfies `P+P = F_2^8`. Merged
[#6966](https://github.com/CrocSwap/integer-mult-bounds/pull/6966) already
shows that every multiplicity-2 arc uses at least four other sources. For
either multiplicity-2 source, if the two arc ranks are ordered `r ≤ s`, then

```text
(r, s) ∈ {(4,7), (5,7), (6,7), (7,7)}.
```

One arc therefore uses all seven other sources. When the other arc has rank
`r ∈ {4,5,6}`, that arc leaves at least `b(r)` steps from its own support on
the complementary arc, where

```text
b(4) = 6,  b(5) = 10,  b(6) = 14.
```

These are the complementary flat-step budgets. Each constant is the length of
a shortest walk on the `r`-cube whose visited vertices are a difference basis
of `F_2^r`, and an explicit walk meets it.

## Scope

The question is the first open question of
[#6966](https://github.com/CrocSwap/integer-mult-bounds/pull/6966): does a
universal length-28 word exist in which every multiplicity-2 arc uses at least
four other sources? Its prescribed first step was to fix one multiplicity-2
source, require both arcs to use at least four labels, and write the
complementary flat-step budget before searching. This package writes that
budget and the rank-pair list it forces. It does not search the four surviving
pairs, rerun the rank-at-most-3 argument, or touch the length-30 rank-at-least-4
question of
[#7015](https://github.com/CrocSwap/integer-mult-bounds/pull/7015).

Card `connector-alphabet-change`, priority revision 8. Scope status:
**changed**. The card asks for one new connector operation. The alphabet stays
the published singleton alphabet; the new statement is the flat-step budget.
Base commit `17469fff78c22941280f04d39dc5a1faee09c840`.

## Definitions

Sources are the standard basis of `F_2^8`. For a word `w_0,...,w_27`, the
prefixes are `q_0 = 0` and `q_{t+1} = q_t + e_{w_t}`. Universality means
`P+P = F_2^8` with `P = {q_0,...,q_27}`, as in Ross Richardson's
[#943](https://github.com/CrocSwap/integer-mult-bounds/pull/943) and the
statement recorded by
[#5234](https://github.com/CrocSwap/integer-mult-bounds/pull/5234).

A multiplicity-2 source `α` occurs twice. Those occurrences split the circular
word into two arcs. The **rank** of an arc is the number of distinct sources
in it. Deleting `α` leaves a closed walk of length 26 in `F_2^7`. As in
[#6966](https://github.com/CrocSwap/integer-mult-bounds/pull/6966), the two
layers `L_A` and `L_B` of that quotient satisfy

```text
L_A + L_B = F_2^7
(L_A + L_A) ∪ (L_B + L_B) = F_2^7
```

exactly when the original word is universal. An arc that uses only a source
set `T` stays in one coset of `V = span(T)`.

## Flat-step budget

Let one arc use exactly `r ≤ 6` sources `T`, and write `F_2^7 = V ⊕ W` with
`dim W = 7-r ≥ 1`. Pairwise sums from that arc's layer lie in `V`. On the
complementary arc, the `V`-coordinate changes only on steps from `T`. If there
are `k` such steps, they form a walk of length `k` on the coordinate `r`-cube.
Its visited set `U` satisfies `|U| ≤ k+1`.

A vector whose `V`-component lies outside `U+U` and whose `W`-component is
nonzero is not a same-layer sum: the low-rank layer has `W`-component 0, and
the complementary layer has every `V`-component in `U+U`. Universality
therefore forces `U+U = V`. So `k` is at least the shortest cube-walk length
`b(r)` whose vertices form a difference basis of `F_2^r`. Translating the walk
to start at `0` does not change the difference set, and the cube is a Cayley
graph, so it is enough to start at `0`.

The pair count `1 + C(n,2) ≥ 2^r` gives the weaker floors `n ≥ 6, 9, 12` and
hence `k ≥ 5, 8, 11`. The cube is stricter.

**`b(4) = 6`.** Five points give at most `1+C(5,2) = 11 < 16` sums, so no walk
of length at most 4 works. All `4^5 = 1024` walks of length 5 from `0` were
enumerated; none is a difference basis. All `4096` walks of length 6 were
enumerated as a control, and `144` succeed. One of them is `0,1,0,2,3,2`.

**`b(5) = 10`.** Eight points give at most `29 < 32` sums, so length at most 7
is impossible. All `5^8 + 5^9 = 2,343,750` walks of length 8 or 9 from `0`
were enumerated; none is a difference basis. The walk `0,1,0,2,0,1,0,3,4,3`
has length 10 and is a difference basis.

**`b(6) = 14`.** Eleven points give at most `56 < 64` sums. The sharp value
uses the five-dimensional census.

Deleting coordinate `i` from a covering walk of length `k` on the 6-cube leaves
a covering walk of length `k - c_i` on the 5-cube, where `c_i` is the number of
steps in direction `i`. Thus `c_i ≤ k - 10`. Every `c_i` is at least 1, because
an unused direction traps the vertices in a hyperplane. Six positive integers
bounded by `k-10` can sum to `k` only when `k ≥ 12`.

At length 12 every `c_i` equals 2. Deleting any coordinate leaves a 5-cube walk
with counts `(2,2,2,2,2)`. All `10!/(2!^5) = 113,400` such walks were
enumerated, with no pruning; none covers.

At length 13 the only sorted count vectors with entries in `{1,2,3}` and sum
13 are `(1,1,2,3,3,3)`, `(1,2,2,2,3,3)`, and `(2,2,2,2,2,3)`. A count of 4 or
more would leave a 5-cube walk of length at most 9, which the census already
excludes, and a zero count is the hyperplane case. The third vector deletes its
unique triple and leaves `(2,2,2,2,2)`, which does not cover. For each of the
first two vectors, coordinate permutation reduces a covering walk to one fixed
assignment of those counts. The fixed assignments `(3,3,3,2,1,1)` and
`(3,3,2,2,2,1)` were searched. A partial walk is abandoned only when `r` new
vertices cannot finish the difference set: the `t`-th new vertex adds at most
`|U|+t` sums, and a repeat adds none. Neither assignment covers.

The length-14 walk `0,1,0,2,0,1,0,3,4,3,5,3,4,3` does cover. Its counts are
`(4,2,1,4,2,1)`. The same optimistic bound accepts every prefix of the three
positive walks, so that bound does not reject a known covering walk.

Thus no covering 6-cube walk is shorter than 14, and 14 occurs. The same
positive walks show that `6`, `10`, and `14` are sharp as cube-walk lengths. A
multiplicity restriction can still make a legal word longer.

## Rank pairs

By [#6966](https://github.com/CrocSwap/integer-mult-bounds/pull/6966), both
arcs have rank at least 4. Suppose both ranks `r ≤ s` are at most 6. Let `I`
be the intersection of their supports. The complementary flat-step budget puts
at least `b(r)` steps of the first support on the second arc, and at least
`b(s)` steps of the second support on the first arc. Those steps lie in `I`
and are disjoint, so `I` occurs at least `b(r)+b(s)` times.

Every source other than `α` occurs in the word, so the two supports cover all
seven other sources and `|I| = r+s-7`. Each of those sources occurs at most
four times, so `I` occurs at most `4|I|` times. The six pairs fail that test:

```text
(4,4):  4 < 12
(4,5):  8 < 16
(4,6): 12 < 20
(5,5): 12 < 20
(5,6): 16 < 24
(6,6): 20 < 28
```

Both arcs therefore cannot have rank at most 6. The larger rank is 7, and the
ordered pair is one of `(4,7)`, `(5,7)`, `(6,7)`, and `(7,7)`. In the first
three cases the smaller arc leaves at least `b(r)` of its own steps on the
complementary arc.

The same counting does not forbid those four pairs. There are `C(7,4)=35`,
`C(7,5)=21`, and `C(7,6)=7` ways to choose the smaller support inside the full
seven-source arc, and the full seven-source support occurs at least `b(r)`
times on each of those choices. The verifier counts the ordered pairs
`70, 42, 14, 1`.

## What is not claimed

No universal length-28 word is constructed or ruled out. The four surviving
rank pairs remain open, so this is not a proof that `f(8) > 28`. A failed or
unfinished search of those pairs would not be such a proof either. The cube
census is an exhaustive finite check of the stated walk domains; it is not a
search of length-28 words. The cited bound `f(7)=24` is not replayed. No
supplier, readout schedule, selected-frontier record, or multiplication theorem
is changed. The batch minimum 538, 540, or 542 from
[#5234](https://github.com/CrocSwap/integer-mult-bounds/pull/5234) is still
blocked on finding a word.

## Evidence and reproduction

The exclusions are the counting argument above and the cube censuses named
there. The verifier also checks the pair floors, the three positive walks and
their truncations, one five-direction non-covering walk, the 144 length-6
walks on the 4-cube, the ordered support counts `70, 42, 14, 1`, and that
all `63² = 3969` support pairs of ranks 4 through 6 fail the budget. CPython
3.12 and the standard library:

```sh
python3 -W error -I -B research/length28-flat-step-budget/verify.py
python3 -W error -I -O -B research/length28-flat-step-budget/verify.py
python3 -B scripts/research_package.py --package research/length28-flat-step-budget
```

Expected marker:

```text
PASS_LENGTH28_FLAT_STEP_BUDGET b=6,10,14 q4=1024 q5=2343750 q5_equal=113400 q6_nodes=25232587 forbidden=3969 open=(70, 42, 14, 1)
```

The length-13 search visited `25,232,587` nodes under the stated bound. The
equal-count five-cube census did not use that bound. Normal and optimized runs
call the same `require` checks.

## Overlap

Targeted open-PR search on 2026-11-10 against
`CrocSwap/integer-mult-bounds` for `length-28`, `flat-step`, `sojourn`, and
`rank-7`. The length-28 and sojourn hits were
[#7015](https://github.com/CrocSwap/integer-mult-bounds/pull/7015), which
records a rank-3 obstruction for a universal length-30 word. That is a
different length and does not state this budget. The rank-7 hits were
unrelated stage, paired-star, and conditional-κ titles plus the same #7015.
No open PR states `b(4), b(5), b(6) = 6, 10, 14` or the surviving rank-pair
list.

Merged [#6966](https://github.com/CrocSwap/integer-mult-bounds/pull/6966) is
the predecessor. Its README on this base, pinned as a package input, still
asks for the flat-step budget and does not compute it. Merged
[#5234](https://github.com/CrocSwap/integer-mult-bounds/pull/5234) supplies the
floor and the multiplicity shape. The fork branch
`cursor/length28-multiplicity-sharpness-dae9` is that merged predecessor, not
this budget. Closed-PR coverage is through those readings, not a full
closed-PR body index. No match is a novelty certificate.

## Open next questions

1. Does a universal length-28 word realize one of `(4,7)`, `(5,7)`, `(6,7)`,
   or `(7,7)`? A yes answer shows the floor 28 is sharp. The budgets above
   already exclude every pair in which both arcs have rank at most 6.
   First step: fix a rank-4 support, place at least six complementary steps
   from that support, and test one fiber walk on the three outside sources.
   Blocker: those four pairs satisfy the occurrence budget, and no universal
   length-28 word is known.

2. Does a word from question 1 decide whether the #5234 batch minimum is 538,
   540, or 542 queries? First step: price one universal length-28 word if
   question 1 finds one. Blocker: question 1 is open, so the query gap stays
   where #5234 and #6966 left it.

## Credit

Ross Richardson, #943, for the singleton model and prefix criterion. Douglas
Colkitt, #1185, for the length-32 Gray upper construction; it is not replayed
here. conorholds, #3058, for `f(7) = 24`, cited by #5234 and not replayed.
Nick Petalas, #5234, for the length-28 floor, the multiplicity shape, and the
original sharpness question. The rank-at-most-3 arc obstruction and the open
budget question are unpaidmoon's #6966. The length-30 sojourn packages are
different lengths.

Prepared by unpaidmoon with substantial Cursor Grok assistance. New work is
Apache-2.0. Independent human and proof-kernel review are unclaimed.
