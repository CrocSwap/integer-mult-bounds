# The characteristic-5 centre on `s + t = 33` freezes a coordinate, and that does not prove the depth-two exclusion

**Partial obstruction. No new κ.** In the unchanged unsigned dirty connector,
classify the centre of `s + t = kc + 3` at characteristic `c = 5` and six
sources. Every legal centre is a weight-3 mask and freezes a coordinate sum
of 10. The same one-step move that froze 14 at `c = 7` then makes the whole
middle diagonal illegal. That is a human proof of one chain hypothesis. It is
not a human proof that no depth-two word exists.

The selected conditional κ stays `781451/250000000`. This note does not rerun
a SAT solver, does not touch the DRAT certificate in open PR #6216, and does
not treat a solver UNSAT as a proof.

## Proved statement

Let a floor word of length 30 call each of six sources exactly five times.
Write `q_t` for the count vector of the first `t` letters, so `q_0 = 0` and
`q_30 = (5,5,5,5,5,5)`. Letters are `w_0,...,w_29`, with
`q_{t+1} = q_t + e_{w_t}`. For `s = 4,...,16` define

```text
S(s) = q_s + q_{33-s}.
```

Let `A = {0,1,5,6,10}`. Call `S(s)` **legal** when every coordinate lies in
`A`. The chain hypothesis is:

> **(H)** `S(s)` is legal for every `s = 4,...,16`.

**Theorem.** No length-30 six-source floor word in characteristic 5 satisfies
(H). Every legal value of `S(16)` is a weight-3 mask with at least one
coordinate equal to 10, that coordinate is immovable by the diagonal step,
and `q_4` would then contain a 5.

The domain of the centre census below is finite, and the type split itself is
the short arithmetic in the next section. The checker recounts the census; the
emptiness of (H) does not depend on the SAT encoding of PR #6141.

## Interface, unchanged

This is the depth-two interface of PR #4231 and PR #4248, as used by PR #6141.
A pair `(s, t)` with `0 ≤ s ≤ t ≤ 29` realizes a binary mask `m` when
`q_s + q_t ≡ m (mod 5)` coordinatewise. Each count is an integer in
`{0,...,5}`, so each coordinate sum lies in `{0,...,10}`. The sums in that
range congruent to 0 or 1 modulo 5 are exactly `A`:

| residue modulo 5 | attainable sums |
|---|---|
| 0 | 0, 5, 10 |
| 1 | 1, 6 |

A coordinate in `{1,6}` contributes a mask bit 1. A coordinate in `{0,5,10}`
contributes a mask bit 0. The coordinate sum of `q_s + q_t` is `s + t`, so a
legal pair of mask weight `w` satisfies `s + t ≡ w (mod 5)` (PR #6107). The
endpoint `t = 30` is dropped, because `q_30` is the all-fives vector and is
identified with `q_0` modulo 5. Nothing here adds a connector operation.

## Centre classification

The pair on `s + t = 33` nearest the middle is `(16, 17)`. These prefixes
differ by one letter: `q_17 = q_16 + e_w` with `w = w_16`. Write `r = q_16`.
Then `∑ r_j = 16`, every `r_j` lies in `{0,...,5}`, and `r_w ≤ 4`.

The centre sum is `2r + e_w`. For a coordinate other than `w` the sum is the
even number `2r_j`. The values of `r_j` in `{0,...,5}` give

| `r_j` | `2r_j` | in `A` |
|---:|---:|---|
| 0 | 0 | yes, mask bit 0 |
| 1 | 2 | no |
| 2 | 4 | no |
| 3 | 6 | yes, mask bit 1 |
| 4 | 8 | no |
| 5 | 10 | yes, mask bit 0 |

For the centre letter the sum is `2r_w + 1`, and `r_w ≤ 4`:

| `r_w` | `2r_w + 1` | in `A` |
|---:|---:|---|
| 0 | 1 | yes, mask bit 1 |
| 1 | 3 | no |
| 2 | 5 | yes, mask bit 0 |
| 3 | 7 | no |
| 4 | 9 | no |

So a legal centre has non-centre coordinates of types `r ∈ {0,3,5}` only, and
the centre letter is type `r_w = 0` or `r_w = 2`. Let `n_0, n_3, n_5` count
the five non-centre coordinates. Then `n_0 + n_3 + n_5 = 5`.

**Type `r_w = 0`.** The centre contributes mask bit 1 and count 0. Weight 3
is not required for this case split: the count equation alone is
`3 n_3 + 5 n_5 = 16`. The nonnegative possibilities with `n_5 ≤ 3` are

| `n_5` | remainder | solution |
|---:|---:|---|
| 0 | 16 | not divisible by 3 |
| 1 | 11 | not divisible by 3 |
| 2 | 6 | `n_3 = 2`, so `n_0 = 1` |
| 3 | 1 | not divisible by 3 |

The only solution has mask weight `n_3 + 1 = 3` and two coordinates equal to
10. Each of those is a pair of fives on a source other than `w`.

**Type `r_w = 2`.** The centre contributes count 2 and mask bit 0. The count
equation is `2 + 3 n_3 + 5 n_5 = 16`, so `3 n_3 + 5 n_5 = 14`.

| `n_5` | remainder | solution |
|---:|---:|---|
| 0 | 14 | not divisible by 3 |
| 1 | 9 | `n_3 = 3`, so `n_0 = 1` |
| 2 | 4 | not divisible by 3 |

`n_5 ≥ 3` gives at least 15. The only solution has mask weight `n_3 = 3` and
one coordinate equal to 10, again a pair of fives off `w`.

These two rows are the whole legal centre. In particular there is no legal
centre of weight 0, 1, 2, 4, 5 or 6. Both legal types freeze at least one
coordinate at 10.

The same arithmetic counts the realizations. Choose the centre coordinate in
6 ways.

- Type `r_w = 0`: the other five coordinates are two 3s, two 5s and one 0.
  `6 · C(5,2) · C(3,2) = 180`.
- Type `r_w = 2`: three 3s, one 5 and one 0.
  `6 · C(5,3) · C(2,1) = 120`.

That is 300 centres and `2·180 + 120 = 480` coordinates equal to 10. The
checker enumerates every vector in `{0,...,5}^6` of sum 16 and every legal
centre letter, and it finds the same two types with these counts. That
enumeration is an exhaustive finite census of a finite domain. It is a check
of the table above, not a solver verdict.

## The frozen step, and why (H) is empty

On this diagonal the prefixes obey

```text
S(s) = S(s-1) + e_{w_{s-1}} - e_{w_{33-s}}.
```

Indeed `q_s = q_{s-1} + e_{w_{s-1}}` and
`q_{34-s} = q_{33-s} + e_{w_{33-s}}`, so

```text
S(s-1) = q_{s-1} + q_{34-s} = S(s) - e_{w_{s-1}} + e_{w_{33-s}}.
```

For each step from `s = 16` down to `s = 5`, both letters lie in
`w_4,...,w_28`. If the two letters agree, `S` does not change. If they
differ, one coordinate increases by 1 and another decreases by 1.

Inside `A`, the only `+1` moves are `0 → 1` and `5 → 6`. The only `-1` moves
are `1 → 0` and `6 → 5`. The value 10 meets neither list: `9` and `11` are
outside `A`. Therefore, whenever `S(s)` and `S(s-1)` are both legal and
`S(s)` has a coordinate 10, that same coordinate of `S(s-1)` is 10.

Assume (H). The classification gives a source `j` with `S(16)_j = 10`.
Walking down to `s = 4` keeps coordinate `j` equal to 10. The only way to
write 10 as a sum of two integers in `{0,...,5}` is `5 + 5`, so `q_4[j] = 5`.
The coordinates of `q_4` sum to 4, so none of them is 5.

This contradiction is the theorem. One index `s ∈ {4,...,16}` whose vector is
illegal stops the walk. The argument uses every index on this diagonal and no
pair with a different sum.

## Scope of the obstruction

The theorem is exactly the emptiness of (H). A depth-two word is a floor word
such that every nonzero mask in `{0,1}^6` is realized by some pair
`0 ≤ s ≤ t ≤ 29`. PR #6141 reports that no such word exists at `c = 5`,
including the relaxation to the 16 masks of weights 2 and 6, as output of
CaDiCaL and Glucose on one encoding. Open PR #6216 supplies a DRAT/LRAT
certificate of that same encoding. Those are solver artifacts. This note is
not a certificate, and a certificate is not this note.

(H) does not follow from depth two. Two independent reasons:

1. **Weights 2 and 6 never meet this diagonal.** A legal vector has coordinate
   sum `w + 5λ`. If the sum is 33, then `w ≡ 3 (mod 5)`. The only Hamming
   weight in `0..6` congruent to 3 is 3. Every pair with `s + t = 33`,
   centre or not, is disjoint from the 16 masks certified by PR #6216.
   Freezing a coordinate of `S(16)` does not mention those masks.

2. **A weight-3 mask need not sit on `s + t = 33`.** The pairs
   `0 ≤ s ≤ t ≤ 29` number `465`. Those with `s + t ≡ 3 (mod 5)` are the 93
   pairs on

   ```text
   3, 8, 13, 18, 23, 28, 33, 38, 43, 48, 53, 58
   ```

   with raw slot counts

   ```text
   2, 5, 7, 10, 12, 15, 13, 11, 8, 6, 3, 1.
   ```

   Thirteen of the 93 lie on `s + t = 33`, namely `(s, 33-s)` for
   `s = 4,...,16`. The other eighty are outside the walk. The witness below
   realizes a weight-3 mask at sum 13 while `S(16)` is illegal, so a single
   weight-3 realization does not force (H).

The missing implication, and the whole remaining obligation of this method, is:

> **(I)** every six-source depth-two floor word in characteristic 5 satisfies (H).

Together with the theorem, (I) would be a human proof of the exclusion. This
package does not prove (I). No inequality here moves a weight-2 mask, a
weight-6 mask, or a pair with `s + t ≠ 33` onto the frozen coordinate.

Nick Petalas's handoff already records a different, weaker counting
obstruction to the *restricted* model in which weight-3 masks may use only
`s + t ∈ {3, 33}`. That count is rechecked here and left at its original
strength. The raw pairs of sum 3 are `(0,3)` and `(1,2)`. The second is never
legal: the first letter `a` satisfies `q_2[a] ≥ 1`, so the sum on `a` is at
least 2, while a legal vector of total sum 3 can use only the values `{0,1}`.
Thus that restricted model has at most `1 + 13 = 14` slots and `C(6,3) = 20`
masks. Fourteen slots cannot cover twenty masks. That pigeonhole is not (H),
and it is not the depth-two exclusion: the other residue-3 sums remain
available. The frozen step does not close them.

## Witness that (H) is stricter than one off-diagonal mask

The length-30 word

```text
000001231234512345123451234545
```

calls each source five times. Its prefixes `q_5 = (5,0,0,0,0,0)` and
`q_8 = (5,1,1,1,0,0)` sum to `(10,1,1,1,0,0)`, a weight-3 mask on sources
1, 2 and 3, at `s + t = 13`. The centre is

```text
q_16 = (5,3,3,3,1,1),  q_17 = (5,3,3,3,2,1),
S(16) = (10,6,6,6,3,2).
```

The coordinates 3 and 2 lie outside `A`, so `S(16)` is illegal and (H) does
not apply. Across all 465 pairs this word realizes 8 nonzero masks: three of
weight 2, two of weight 3, one of weight 4 and two of weight 1. It realizes
no weight-6 mask. It is a floor word with an off-diagonal weight-3 pair. It
is not a depth-two word, and it is not a counterexample to PR #6141.

## What was not rerun

No SAT solver, no DRAT/LRAT check, no replay of PR #6216, and no search for a
depth-two word. The characteristic-6 centre is a different arithmetic: `c + 1`
is odd, so the doubled non-centre sum cannot hit `c + 1`. That classification
is not done here. The off-diagonal replacement question at `c = 7` is not
done here. The `c = 7` chain on `s + t = 45` is not rerun.

No supplier, consumer, or selected frontier changes. The live selected record
at the base commit is κ `= 781451/250000000 = 0.003125804`. The priority note
on this same commit still quotes the older selected figure from PR #5599;
this package follows the selected record.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/c5-frozen-centre-gap/verify.py
python3.12 -I -O -W error -B research/c5-frozen-centre-gap/verify.py
python3.12 -B scripts/research_package.py --package research/c5-frozen-centre-gap --check-only
```

The marker is

```text
PASS_C5_FROZEN_CENTRE_GAP centres=300 type_r0=180 type_r2=120 frozen_coordinates=480 moves=+[0, 5]/-[1, 6] residue3_pairs=93 middle_slots=13 early_realizable_slots=1 witness_masks=8 chain_H=empty controls=7
```

The seven controls are the near-miss centre `(3,3,3,3,3,1)`, the absence of a
5 in every length-4 count, the weight identity on all `5^6` allowed tuples,
the pair census, the exhaustive failure of `(1,2)`, the positive `(0,3)`
pattern `(1,1,1,0,0,0)`, and the witness above. No Lean, Docker, or historical
suite was run.

## Open next questions

1. Does every six-source depth-two floor word in characteristic 5 satisfy (H)?
   *Why:* the emptiness of (H) is proved for every floor word, so this
   implication is a human proof of the exclusion. *First step:* derive
   `S(16) ∈ A^6` from the sixteen masks of weights 2 and 6, or show that those
   masks do not determine the sum-33 diagonal. *Blocked by:* the weight
   identity places weights 2 and 6 on sums congruent to 2 and 1 modulo 5.
   Sum 33 is congruent to 3. No transport lemma is proved here.
2. Can the adjacent centre on one other sum `σ ≡ 3 (mod 5)`, `σ ≠ 33`, freeze
   a coordinate that meets a positive share of the twenty weight-3 masks?
   *Why:* the witness realizes a weight-3 mask at sum 13, which the sum-33
   walk never sees. *First step:* classify the single adjacent pair on `σ = 13`
   or on `σ = 28`, at characteristic 5 only. *Blocked by:* adjacency
   `q_t = q_s + e_w` with `|t - s| = 1` forces the sum `2s + 1`, and that sum
   is 33 only for `s = 16`. A different sum has a different count total.

## Credit

The depth-two interface is Nick Petalas's (PR #4231, PR #4248), with the Ross
Richardson PR #934 / PR #943 lineage. PR #6107 supplies the weight identity.
JosieElliston's PR #6141 is the solver exclusion at characteristics 5 and 6
and leaves characteristic 7 open; its README states that no human proof is
given. queelius's open PR #6216 is a DRAT certificate of the characteristic-5
encoding, a separate artifact, and it is not replayed or replaced here.
Nick Petalas's handoff of 2026-11-03
([discussion comment 19384981](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19384981))
records the diagonal move, the slot counts 14, 17, 20 and 23, and the c=7
centre shape. The c=7 chain proof is the fork draft
[PR #156](https://github.com/unpaidmoon/integer-mult-bounds/pull/156)
and discussion comment 19493159; this note answers only the characteristic-5
half of that draft's second open question. zxv's PR #6057 and JosieElliston's
PR #6061 supply words for every `c ≥ 8`, which are outside this obstruction.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
