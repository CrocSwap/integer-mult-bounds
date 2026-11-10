# The c=6 centre on s+t=39 carries no weight-3 mask

**Scoped classification. No new κ.** In the unchanged unsigned dirty
connector, the centre pair of the diagonal `s + t = 39` never realizes a
weight-3 mask. The frozen-14 step, which starts from a weight-3 centre and
propagates a coordinate equal to `2c`, therefore has no c=6 input. The
six-source depth-two exclusion at characteristic 6 stays the solver verdict
of PR6141.

The selected conditional κ remains `781451/250000000` in
`certificates/selected-result.json`.

## Interface, unchanged

A floor word on `k = 6` sources in characteristic `c = 6` has length 36 and
calls each source exactly six times. `q_t` counts the first `t` letters, so
`q_0 = 0`, `q_36 = (6,6,6,6,6,6)`, and each step adds one basis vector.
Counts stay in `{0,...,6}`. The word has depth two when every nonzero binary
mask is congruent modulo 6 to `q_s + q_t` for some `0 ≤ s ≤ t ≤ 35`. This is
the interface of PR4231/PR4248, as used by PR6141. Boundary 36 is identified
with 0 because `q_36 = 6·1 ≡ q_0`.

A pair realizes a **weight-3 mask** when every coordinate of `q_s + q_t`
lies in `{0,1,6,7,12}` and exactly three coordinates lie in `{1,7}`. Every
sum of two counts in `{0,...,6}` is an integer in `{0,...,12}`, and the
members of that range congruent to 0 or 1 modulo 6 are exactly
`{0,1,6,7,12}`. The value 13 is outside the range. Mask bits are the
residues 1. This is the same reading of the weight identity (PR6107) that
the c=7 diagonal note uses, specialized to `c = 6`.

## Centre classification

The pairs with `s + t = 39` and `s ≤ t ≤ 35` are `(s, 39-s)` for
`s = 4,...,19`. The centre is the adjacent pair `(19, 20)`:
`q_20 = q_19 + e_j` for the single letter `j` in position 19, and
`q_19[j] ≤ 5`. Write `r` for `q_19`. The centre sum is `2r + e_j`.

The coordinate types that land in `{0,1,6,7,12}` are:

| role | count | sum | residue | mask bit |
|---|---:|---:|---:|---:|
| other | 0 | 0 | 0 | 0 |
| other | 3 | 6 | 0 | 0 |
| other | 6 | 12 | 0 | 2·`c` carries no mask bit |
| centre | 0 | 1 | 1 | 1 |
| centre | 3 | 7 | 1 | 1 |

No other count in `{0,...,6}` works. In particular a non-centre coordinate
is even, and every even allowed value is a mask bit 0. A centre coordinate
is odd, so it is the only coordinate that can carry a mask bit.

Every count in the table is a multiple of 3. A residue-legal centre would
therefore have coordinate sum divisible by 3. The centre length is 19, and
`19 ≡ 1 (mod 3)`. There is no residue-legal centre, and the weight-3 subset
is empty.

The same arithmetic still forbids a centre if the unreachable value 13 is
added to the allowed set and the centre source is allowed to have count 6.
Those counts are `{0,3}` for a sum of 1 or 7, and `6` for a sum of 13. All
three are multiples of 3.

`verify.py` exhausts the finite domain: all `7^6` vectors with coordinates
in `{0,...,6}`, the 9,156 of them that sum to 19, and the 46,956 choices of
centre letter that have not already been used six times. None of the 46,956
sums is residue-legal. The widened domain, 54,936 pairs with 13 admitted and
the count-6 centre letter admitted, is empty as well. This census covers the
centre pair only. It is not a census of words, and it is not a SAT run.

## Why the frozen-14 step has no c=6 input

On the c=7 diagonal `s + t = 45`, the equality-case argument starts from a
weight-3 centre and a coordinate equal to 14, which is `2c` at `c = 7`.
Inside `{0,1,7,8,14}` a step can add 1 only from 0 or 7 and subtract 1 only
from 1 or 8, so 14 stays fixed. If every index `s = 4,...,22` is weight-3,
that coordinate is still 14 at `s = 4`, and both sides are 7, which a
length-4 prefix cannot hold. That is the frozen-14 step. It is an argument
about the equality case in which all 20 weight-3 masks sit on the 20
diagonal slots.

At `c = 6` the analogous allowed set is `{0,1,6,7,12}`. A step can add 1
only from 0 or 6 and subtract 1 only from 1 or 7, so the immovable value is
12, which is `2c` at `c = 6`. The integer 14 is congruent to 2 modulo 6, so
it is not a weight-3 coordinate in this characteristic. The centre
classification supplies no residue-legal vector on which a 12 could sit.
The induction that keeps a frozen coordinate from the centre down to `s = 4`
therefore does not start.

Nick Petalas's handoff of 2026-11-03 already records that the two-diagonal
model `s + t ∈ {3, 39}` has 17 slots against `C(6,3) = 20`, so that
restricted model is impossible by counting. The centre classification
removes the centre slot from those 17. The other early candidate `(1, 2)`
has sum `2e_a + e_b` or `3e_a`, and neither 2 nor 3 lies in
`{0,1,6,7,12}`. The only early pair left is `(0,3)`. At most the 15 indices
`s = 4,...,18`, plus that one early pair, remain: 16 slots. Sixteen is
still less than 20. The count, with or without the dead centre, is a human
proof of this restricted model only. PR6141's exclusion is the unrestricted
depth-two statement, in which a weight-3 mask may use any pair with
`s + t ≡ 3 (mod 6)`.

## Weight-3 sums that sit off the centre

The centre obstruction is local. Two explicit floor words realize a
weight-3 mask somewhere else. Both call each source six times. Neither is
claimed to have depth two.

Separation 3 on the same diagonal. The word

```text
333333444444555555012000001111122222
```

has `q_18 = (0,0,0,6,6,6)` and `q_21 = (1,1,1,6,6,6)`. The sum is
`(1,1,1,12,12,12)`, a weight-3 mask, at `s + t = 39`. Its centre sum is
`(2,1,0,12,12,12)`, which contains a 2. The three coordinates equal to 12
are immovable under the c=6 move table, and this one pair does not force
them down through `s = 4`, because the centre index between 18 and the
early indices is not weight-3.

Off this diagonal, `s + t = 9`. The word

```text
333333012000001111122222444444555555
```

has `q_9 = (1,1,1,6,0,0)`, so `(0,9)` is a weight-3 mask.

The handoff's c=7 prefix `jjjjabc` does not give a c=6 weight-3 mask.
`q_3 + q_7 = 7e_j + e_a + e_b + e_c`. At characteristic 7 the coefficient 7
is a mask bit 0, and the sum realizes `{a,b,c}`. At characteristic 6 the
same coefficient is a mask bit 1, and four coordinates are mask bits.

## What this establishes

Under the hypotheses above, the centre of `s + t = kc + 3` at `c = 6` has
no weight-3 realization, and no residue-legal realization. The frozen-14
step does not become a human proof of the c=6 depth-two exclusion: its
hypothesis, a weight-3 centre carrying the value `2c`, is empty here, while
the exclusion quantifies over pairs that are not that centre. PR6141's
CaDiCaL 1.9.5 and MapleChrono UNSAT verdicts remain solver evidence. This
package does not rerun them, does not emit a DRAT certificate, and does not
treat that UNSAT as a human proof.

The c=5 centre is a different characteristic and is not classified here.
The c=7 question of replacing one diagonal index by an off-diagonal pair is
a different question. No supplier, consumer, or selected frontier changes.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/six-source-c6-centre-classification/verify.py
python3.12 -I -O -W error -B research/six-source-c6-centre-classification/verify.py
python3.12 -B scripts/research_package.py --package research/six-source-c6-centre-classification --check-only
```

The marker is

```text
PASS_SIX_SOURCE_C6_CENTRE_CLASSIFICATION sum19=9156 examined=46956 residue_legal=0 weight3=0 mod3_shapes=0 widened_legal=0 moves=+[0, 6]/-[1, 7] frozen_value=12 controls=8
```

The eight controls accept two synthetic weight-3 sums, reject a centre sum
that contains a 2, record that the c=7 prefix has weight 4 at c=6, check
both explicit floor words, check that a multiple-of-3 vector can sum to 18,
and reject both integer shapes of the pair `(1,2)`. Failures raise
`SystemExit`. Optimized mode cannot silence them.

## Open next questions

1. Which human step, other than frozen-14, proves the c=6 depth-two
   exclusion? *Why:* PR6141's c=6 verdict is still two solver runs, and the
   centre classification gives that induction nothing to freeze. *First
   step:* classify the separation-3 pairs on `s + t = 39`, starting from the
   explicit type `q_18 = (0,0,0,6,6,6)` with three frozen coordinates equal
   to 12, and price one mask realized at `s + t = 9` against those slots.
   *Blocked by:* the centre index is empty, so a chain through every
   diagonal index is unavailable, and the `s + t = 9` witness lies off the
   diagonal the freeze follows. The c=6 DRAT certificate named in PR6216 is
   a separate budget and is not this step.

## Credit

The depth-two interface and the weight identity are Nick Petalas's
(PR4231, PR4248, PR6107), with the Ross Richardson PR934/PR943 lineage.
JosieElliston's PR6141 records the c=6 solver verdict and leaves the human
proof open. Nick Petalas's handoff on 2026-11-03
([discussion comment 19384981](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19384981))
states the diagonal slot count, the centre shape at c=7, and the off-diagonal
prefix. The frozen-14 equality-case argument at c=7 is the fork draft
[PR156](https://github.com/unpaidmoon/integer-mult-bounds/pull/156), recorded
upstream as discussion comment 19493159. It is not an upstream merge.
queelius's open PR6216 certifies characteristic five and names a
characteristic-six certificate as later work; this package does not produce
that certificate. zxv's PR6057 and JosieElliston's PR6061 supply the
`c ≥ 8` words, which have spare diagonal slots.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
