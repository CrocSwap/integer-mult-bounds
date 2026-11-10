# The sixteen characteristic-5 masks do not force a legal sum-33 centre

**Partial obstruction. No new κ.** In the unchanged unsigned dirty connector,
neither half of the sixteen masks of weights 2 and 6 forces the centre
`S(16) = q_16 + q_17` into `{0,1,5,6,10}^6`. Every all-ones window has a
floor word with that window and an illegal centre. The fifteen weight-2
masks are realized both by a word with a legal centre and by a word with
an illegal centre. No pair of sum 33 can carry any of those sixteen masks.

This does not prove that a word realizing all sixteen at once has an illegal
centre, and it does not prove hypothesis (H) of the centre-freeze. The
selected conditional κ stays `781451/250000000`.

## Proved statement

Let a floor word of length 30 call each of six sources exactly five times.
Write `q_t` for the count vector of the first `t` letters. Letters are
`w_0,...,w_29`, with `q_{t+1} = q_t + e_{w_t}`. For the adjacent pair at
the middle of `s + t = 33`,

```text
S(16) = q_16 + q_17 = 2 q_16 + e_{w_16}.
```

Let `A = {0,1,5,6,10}`. Call `S(16)` **legal** when every coordinate lies in
`A`, and **illegal** otherwise. The same reading as PR #7038: a coordinate
sum in `{0,...,10}` lies in `A` exactly when it is congruent to 0 or 1
modulo 5, and the mask bit is 1 exactly on `{1,6}`.

**Theorem.** The sixteen masks do not determine the legality of `S(16)`,
in the following three senses.

1. **Weight 6.** There are 4095 admissible ways to assign coordinate types
   to an all-ones window. For every one of them there is a length-30 floor
   word that realizes that window and has illegal `S(16)`. For 1731 of them
   there is also a floor word with the same window and legal `S(16)`. No
   window forces `S(16)` to be legal. Of the 2364 windows that force it to
   be illegal, 1573 do so because `q_16` cannot contain a coordinate 0, by
   the three human classes below. The other 791 admit a coordinate 0, but
   none of their feasible vectors `q_16` is a legal centre; that last split
   is the exhaustive comparison in `verify.py`.
2. **Weight 2.** The sorted floor word realizes all fifteen weight-2 masks
   and has illegal `S(16)`. The explicit word
   `001211112322203343354444555500` realizes all fifteen and has legal
   `S(16)`. Neither word realizes the weight-6 mask.
3. **No diagonal pair.** Every 6-tuple with coordinates in `A` has coordinate
   sum congruent to its mask weight modulo 5. A tuple of sum 33 therefore
   has weight 3, never weight 2 or 6. The thirteen pairs with `s + t = 33`
   cannot realize any of the sixteen masks.

The evidence class is an exhaustive finite census. The domains are finite:
the 36 ordered pairs of counts in `{0,...,5}`, the centre vectors of sum 16,
the 4095 type assignments, the bounded compositions for `q_16`, and the 465
pairs of each explicit word. The completeness argument is the case split
below. The checker does not call a SAT solver. Two of the explicit words
were first found by a local CaDiCaL search; the census then checks those
words directly. A failed search is not used as evidence.

## Interface, unchanged

This is the depth-two interface of PR #4231 and PR #4248, as used by
PR #6141 and by the centre classification in PR #7038. A pair
`0 ≤ s ≤ t ≤ 29` realizes a binary mask when `q_s + q_t` has every
coordinate in `A`. The coordinate sum is `s + t`, so a realized mask of
weight `w` has `s + t ≡ w (mod 5)`. Nothing here adds a connector operation.
Boundary 30 is not a second endpoint: `q_30` is the all-fives vector.

Hypothesis (H) from PR #7038 asks every `S(s) = q_s + q_{33-s}`, for
`s = 4,...,16`, to be legal. That note proves (H) is empty for every floor
word, because a legal `S(16)` freezes a coordinate at 10 and the diagonal
step cannot move 10 inside `A`. It leaves open whether the sixteen masks
force `S(16)` into `A^6`. That is the question decided here for each half
of the sixteen, and left open for their conjunction.

## Coordinate types of an all-ones window

The weight-6 mask is the all-ones vector. A realizing pair has every
coordinate sum in `{1,6}`. Since `q_t ≥ q_s` coordinatewise and both counts
lie in `{0,...,5}`, the only possibilities are:

| type | `q_s` | `q_t` | letters in the window |
|---|---:|---:|---:|
| A | 0 | 1 | 1 |
| B | 1 | 5 | 4 |
| C | 2 | 4 | 2 |
| D | 3 | 3 | 0 |

Sum 1 is only `0+1`. Sum 6 with the first count at most the second is
`1+5`, `2+4`, or `3+3`. The pairs `0+6` and `6+0` use a count 6, which a
single prefix does not have. The checker scans all `6 × 6` ordered pairs
and finds these four.

An assignment of types to the six sources determines

```text
s = n_B + 2 n_C + 3 n_D,    t - s = n_A + 4 n_B + 2 n_C.
```

The assignment is admissible when `0 ≤ s ≤ t ≤ 29`. There are 4095 such
assignments. The same count is the sum of the multinomial coefficients
`6! / (n_A! n_B! n_C! n_D!)` over the admissible multiplicity vectors, so
the distinct permutations were not under-counted. Every floor word that
realizes the all-ones mask has one of these 4095 windows: its prefixes at
the realizing boundaries are one of the four types in each coordinate.

## Which vectors `q_16` a window allows

Fix an admissible window, and write `δ` for the letter counts between `s`
and `t`. The position of 16 relative to the window puts `q_16` in exactly
one of three finite sets.

- If `t ≤ 16`, then `q_16 = q_t + e` where `e` sums to `16 - t` and
  `0 ≤ e_j ≤ 5 - q_t[j]`.
- If `s ≥ 16`, then `q_16 = q_s - d` where `d` sums to `s - 16` and
  `0 ≤ d_j ≤ q_s[j]`.
- If `s < 16 < t`, then `q_16 = q_s + c` where `c` sums to `16 - s` and
  `0 ≤ c_j ≤ δ_j`.

Each set is a set of bounded compositions. Any such vector extends to a
floor word with the prescribed window: place the determined multiset on
each block, and append the missing copies so that every source ends at 5.
The centre letter `w_16` has to lie in the block that contains position 16.
In every one of the 4095 windows, every feasible vector that the centre
test accepts or rejects has such a letter available. The constructions
below use one explicit letter and are checked as floor words.

A centre is legal only for the two shapes already classified in PR #7038.
The checker does not trust that classification for the zero lemma: it
enumerates every `q_16 ∈ {0,...,5}^6` of sum 16 and every centre letter
used at most four times, and it finds 300 legal pairs. The count vector of
every one of those pairs contains a coordinate 0. The short reason is the same two-row
arithmetic. A non-centre coordinate of a legal centre lies in `{0,3,5}`,
and the centre letter lies in `{0,2}`.

- Centre letter 0. The count equation is `3 n_3 + 5 n_5 = 16` on the other
  five coordinates. The only solution in range is two 3s, two 5s and a 0.
- Centre letter 2. The equation is `3 n_3 + 5 n_5 = 14`. The only solution
  is three 3s, one 5 and a 0.

Both rows contain a 0. A vector with no coordinate 0 is not a legal centre,
whatever letter follows it.

## Three classes in which `q_16` has no zero

These classes are disjoint, and every window outside them has at least one
feasible `q_16` that does contain a 0. The checker compares the class
predicate with the enumerated vectors on all 4095 assignments.

**Early, 845 windows.** The window ends at `t ≤ 16`. Every type has
`q_t ∈ {1,3,4,5}`, so `q_16 ≥ q_t` has no coordinate 0.

**Covering and not of type A, 721 windows.** There is no type-A source, and
`s ≤ 16 ≤ t`. Then `q_s` lies in `{1,2,3}^6`, and inside the window
`q_16 ≥ q_s`.

**Tight drop, 7 windows.** There is no type A or B.

- One C and five D: `s = 17`, `t = 19`, and `q_17` is a 2 and five 3s.
  The single letter in position 16 reduces one coordinate by 1, which
  cannot produce a 0. There are 6 places for the C.
- Six D: `s = t = 18`, and `q_18 = (3,3,3,3,3,3)`. The two letters in
  positions 16 and 17 reduce the all-threes vector by one or two. The
  resulting 21 vectors are fifteen with two 2s and six with a single 1.
  The minimum coordinate is 1.

That is `845 + 721 + 7 = 1573` windows. Each forces `S(16)` illegal, and
each has a constructed floor word realizing the window.

## The other windows

The remaining `4095 - 1573 = 2522` windows each have at least one feasible
`q_16` containing a 0. Comparing those vectors with the 300 legal centres
splits them in two.

- **1731 windows admit both polarities.** For each, the checker builds one
  floor word with legal `S(16)` and one with illegal `S(16)`, both
  realizing the same window.
- **791 windows admit a zero but no legal centre.** Every feasible vector
  was compared with the centre test. This comparison is the exhaustive
  census. It is not a second closed-form classification of those 791
  multiplicity vectors.

No window lands in a third bin. In particular, **no all-ones window forces
`S(16)` to be legal.** The checker builds 5826 floor words:
`2364` illegal-only windows, plus two words for each of the 1731 flexible
windows. Each constructed word is checked to be a floor word, to reproduce
the prescribed prefixes at `s`, `t` and 16, to realize all-ones on that
window, and to have the claimed centre polarity.

One flexible window is visible by hand. The word

```text
012300333300112241122545545544
```

has `q_4 = (1,1,1,1,0,0)` and `q_22 = (5,5,5,5,1,1)`. The sum is
`(6,6,6,6,1,1)`, all-ones, at `s + t = 26`. Its centre is

```text
q_16 = (5,3,3,5,0,0),  w_16 = 4,  S(16) = (10,6,6,10,1,0),
```

which is legal. The same prefixes are realized by

```text
012311222233334500001144445555
```

with `q_16 = (1,3,5,5,1,1)`, `w_16 = 0` and
`S(16) = (3,6,10,10,2,2)`, which is illegal. The two words share the
window and differ on the centre. This is one of the 1731, not a substitute
for the census.

## The fifteen weight-2 masks

The sorted word `00000 11111 22222 33333 44444 55555`, written without
spaces as `000001111122222333334444455555`, realizes every weight-2 mask.
For `0 ≤ a < b ≤ 5` take the boundaries `s = 5a + 1` and `t = 5b + 1`.
The prefix `q_{5a+1}` is ones on sources `0,...,a-1`, a single `a`, and
zeros after that, and likewise for `b`. Their sum is 10 on sources before
`a`, 6 on `a`, 5 on the sources strictly between `a` and `b`, 1 on `b`,
and 0 after `b`. The mask bits are exactly `{a,b}`. There are
`C(6,2) = 15` such pairs, and `s + t = 5(a+b) + 2 ≡ 2 (mod 5)`. The full
scan of the 465 pairs finds no further weight-2 mask and no weight-6 mask.
The centre is `q_16 = (5,5,5,1,0,0)`, `w_16 = 3`,
`S(16) = (10,10,10,3,0,0)`. The coordinate 3 is outside `A`.

Swapping positions 0 and 5 drops four of those fifteen masks. The checker
rejects that swap as a control.

The word

```text
001211112322203343354444555500
```

also realizes all fifteen weight-2 masks, and no weight-6 mask. Its centre
is `q_16 = (3,5,5,3,0,0)`, `w_16 = 4`,
`S(16) = (6,10,10,6,1,0)`, which is legal of weight 3. The checker scans
all 465 pairs. This word was found by a local solver and is checked here
as a literal; the solver is not part of the replay.

Thus the fifteen weight-2 masks occur with both centre polarities. They do
not determine `S(16)`.

## A mixed family that is still illegal

The word

```text
102431540325045231253054314120
```

has `q_18 = (3,3,3,3,3,3)`, so `(18, 18)` is the six-D window above and
`S(16) = (6,4,6,5,6,6)` is illegal. The same word realizes 13 of the 15
weight-2 masks. The two it misses are `(0,0,1,0,1,0)` and
`(0,1,0,0,0,1)`. The illegality is already forced by the six-D window, so
these thirteen masks do not push that window onto a legal centre. They are
not the full set of fifteen.

## What was not proved

The conjunction of all fifteen weight-2 masks with the weight-6 mask is not
decided. PR #7038's proposed derivation was: those sixteen masks force
`S(16)` legal, and the frozen step then empties (H). Each half fails to
force the legal centre, and the halves meet on no sum-33 pair. A derivation
that uses all sixteen at once is not supplied here.

Merged PR #6216 is a checked DRAT certificate that no floor word realizes
all sixteen masks. Emptiness makes both "`S(16)` is legal" and "`S(16)` is
illegal" vacuously true. That is not a derivation of the centre, and this
package does not replay the certificate. The centre-freeze needs a legal
centre that a word actually reaches, or an argument that produces one. The
transports above produce illegal centres, or both polarities, and never a
forced legal centre.

No supplier, consumer, or selected frontier changes. The live selected
record at the base commit is κ `= 781451/250000000 = 0.003125804`.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/c5-mask-centre-nondetermination/verify.py
python3.12 -I -O -W error -B research/c5-mask-centre-nondetermination/verify.py
python3.12 -B scripts/research_package.py --package research/c5-mask-centre-nondetermination --check-only
```

The marker is

```text
PASS_C5_MASK_CENTRE_NONDETERMINATION assignments=4095 illegal_only=2364 both=1731 legal_only=0 no_zero=1573 zero_but_illegal=791 classes=845+721+7 constructed=5826 midpoint_q16=21 weight2_polarities=2 weight6_forces_legal=0 joint_weight2=13 joint_missing=2 controls=9
```

The nine controls are the near-miss centre `(3,3,3,3,3,1)`, the agreement of
the human no-zero classes with the enumerated vectors, the 21 midpoint
vectors, the weight identity on every allowed 6-tuple, the sorted staircase
and its centre, the swapped sorted word, the legal weight-2 witness, the
flexible all-ones pair and its illegal twin, and the 13-mask joint word.
Failures raise `SystemExit`. Optimized mode cannot silence them. No Lean,
Docker, or historical suite was run.

## Open next questions

1. Does any satisfiable family made of the weight-6 mask and at least 14 of
   the weight-2 masks force `S(16)` into `A^6`?
   *Why:* the families decided above do not, and a forced legal centre is
   the input the PR #7038 freeze still lacks. The full sixteen are a
   different statement: their emptiness, as certified by PR #6216, does not
   select a centre.
   *First step:* take the fifteen weight-2 masks except `(0,0,1,0,1,0)`,
   together with the all-ones mask, and either exhibit a floor word with
   illegal `S(16)` or prove that every realization has legal `S(16)`.
   *Blocked by:* this census does not decide that 14-mask family. The
   weight identity still gives it no pair on `s + t = 33`.

## Credit

The depth-two interface and the weight identity are Nick Petalas's
(PR #4231, PR #4248, PR #6107), with the Ross Richardson PR #934 / PR #943
lineage. JosieElliston's PR #6141 is the solver exclusion. queelius's merged
PR #6216 is the characteristic-5 DRAT certificate; it is not replayed here.
The centre-freeze and the statement of (H) are PR #7038. The sorted word is
the weight-two control of `research/connector-six-source-small-char`.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
