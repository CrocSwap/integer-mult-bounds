# Legal S(16) is impossible for the weight-2 family together with the weight-6 mask

**Exhaustive finite census. No new κ.** In the unchanged unsigned dirty
connector, no length-30 floor word on six sources both realizes all fifteen
weight-2 masks and the weight-6 mask and has a legal centre

```text
S(16) = q_16 + q_17 = 2 q_16 + e_{w_16}.
```

So if any such floor word exists, its `S(16)` is illegal. This census does
not decide whether any such word exists. It does not read the merged PR #6216
DRAT certificate, and it does not use that empty-fibre assertion as an input.
It is not a proof of the characteristic-5 depth-two exclusion: an
illegal-centre word realizing these sixteen masks is not ruled out here.
The selected conditional κ stays `363005817/100000000000`.

## Proved statement

Let a floor word of length 30 call each of six sources exactly five times.
Write `q_t` for the count vector of the first `t` letters, so
`q_{t+1} = q_t + e_{w_t}` and `q_30 = (5,5,5,5,5,5)`. Let
`A = {0,1,5,6,10}`. Call `S(16)` **legal** when every coordinate lies in
`A`, and **illegal** otherwise. A pair `0 ≤ s ≤ t ≤ 29` realizes a binary
mask when `q_s + q_t` has every coordinate in `A`. The mask bit is 1 exactly
on the coordinates whose sum lies in `{1,6}`.

**Theorem.** No floor word realizes all fifteen weight-2 masks and the
weight-6 mask and also has legal `S(16)`.

The evidence class is an exhaustive finite census. The domains are finite:
the centre vectors of sum 16, the two legal count shapes, the
first-occurrence canonical prefixes of those shapes (10,090,080 and
67,267,200), and the canonical continuations of the prefixes that the
future-box test does not already reject. The completeness argument is the
case split below. The checker does not call a SAT solver. A failed search
outside this domain is not used as evidence.

## Legal centres are two shapes

For `q ∈ {0,...,5}^6` of sum 16 and a centre letter `c` with `q_c ≤ 4`,

```text
S(16)_j = 2 q_j    if j ≠ c,    and    2 q_c + 1 if j = c.
```

A non-centre coordinate lies in `A` only for `q_j ∈ {0,3,5}` (the values
`2q ∈ {0,6,10}`). The centre coordinate lies in `A` only for `q_c ∈ {0,2}`
(the values `2q+1 ∈ {1,5}`).

- If `q_c = 0`, the other five coordinates lie in `{0,3,5}` and sum to 16.
  The only solution is two 3s, two 5s and a 0: `3·2 + 5·2 = 16`.
- If `q_c = 2`, the other five coordinates sum to 14. The only solution is
  three 3s, one 5 and a 0: `3·3 + 5·1 = 14`.

Both shapes contain a coordinate 0. The checker enumerates every vector of
sum 16 and every legal letter and finds 300 pairs, all of these two sorted
shapes, 180 of the first and 120 of the second. No other shape occurs.

## Residue test

For `x, y ∈ {0,...,5}` write `res(5) = 0` and `res(v) = v` otherwise. Then
`x + y ∈ A` if and only if `res(x) + res(y) ≢ 2,3,4 (mod 5)`, and the mask
bit is that residue when the sum is in `A`. The sums that can occur are
`0,...,10`, and the members of that range congruent to 0 or 1 modulo 5 are
exactly `A`. The checker compares all 36 ordered pairs.

Consequently a pair of prefixes realizes a mask `m ∈ {0,1}^6` exactly when
`res(q_s) + res(q_t) ≡ m` coordinatewise.

## Future-box prune

After a prefix with count vector `L`, every continuation prefix `Q` satisfies
`L ≤ Q ≤ (5,...,5)` coordinatewise, and every such `Q` occurs on some
continuation: schedule `Q - L` first. On one continuation the prefixes are
totally ordered by the coordinatewise partial order.

A mask `m` that is not yet realized by two prefixes already built is
impossible on every continuation when both of the following fail.

- **Two future prefixes.** There is a coordinate `j` with no integers
  `L_j ≤ x ≤ y ≤ 5` and `res(x) + res(y) ≡ m_j (mod 5)`. For a bit-1
  coordinate this happens exactly when `L_j ≥ 4`. For a bit-0 coordinate it
  never happens, because `5 + 5` has residue 0.
- **One past prefix and one future prefix.** For every prefix `P` already
  built, some coordinate `j` has no value `v ∈ [L_j, 5]` with
  `res(v) ≡ m_j - res(P_j) (mod 5)`. Residue 0 is always available later,
  as the value 5. Residue `r ∈ {1,2,3,4}` is available only while `L_j ≤ r`.

Either witness would be a real continuation, so rejecting both is sound. The
test handles one mask at a time. A prefix can survive it and still have no
continuation that realizes every mask together. Those prefixes are searched,
not accepted.

## What is enumerated

Relabel sources by order of first occurrence. This preserves the floor-word
counts, sends the set of all fifteen weight-2 masks to itself, fixes the
weight-6 mask, and preserves legality of `S(16)`. Every floor word has one
such labeling. The generator emits each labeling once: a source that has not
yet appeared may be introduced only when it is the next unused label.

Counts only increase, so a prefix that already has five positive sources
cannot end at the two-zero shape, and a prefix that already has three
sources above 3 cannot end at a shape with only two such sources. The same
holds for the one-zero shape, which has five positive sources and one source
above 3. The generator drops only those impossible prefixes.

An independent dynamic program, which does not use the future-box test,
counts the canonical length-16 prefixes of each shape:

| shape of `q_16` | centre letter | canonical prefixes |
|---|---|---:|
| permutation of `(5,5,3,3,0,0)` | one of the two zeros | 10,090,080 |
| permutation of `(5,3,3,3,2,0)` | the unique 2 | 67,267,200 |

The census examines the same numbers. Each of those prefixes has exactly one
canonical legal centre letter: the examined-root count equals the dynamic
program. For the two-zero shape the centre letter is a new source, placed at
position 16, so first-occurrence order gives it the next label. For the
one-zero shape the centre letter already has count 2, and the missing source
stays the last label.

For each such root the future-box test is applied to all sixteen masks. It
rejects 10,081,287 of the two-zero roots and leaves 8,793. It rejects
53,770,890 of the one-zero roots and leaves 13,496,310. Every survivor is
extended through its canonical continuations. A continuation is pruned only
by the same future-box test. A completed word is accepted only when the
residue pairs of its actual prefixes realize all fifteen weight-2 masks and
the weight-6 mask. None do.

The two-zero half is repeated by an independent Python enumerator. It reports
the same examined count, the same 8,793 survivors, the same 31,821 suffix
nodes, and the same zero solutions. The one-zero half is the C enumerator
only. Its traversal records 419,423,032 suffix nodes and zero solutions.
Changing the search order would change that node count; the examined-root
count, the survivor count, and the solution count are the census.

## What the separate counterexamples do not give

PR #7058 shows two different facts. No individual all-ones window forces a
legal centre, and the fifteen weight-2 masks, without the weight-6 mask,
occur at both polarities. The sorted word
`000001111122222333334444455555` realizes all fifteen weight-2 masks with
illegal `S(16) = (10,10,10,3,0,0)` and does not realize weight 6. The word
`001211112322203343354444555500` realizes all fifteen with legal
`S(16) = (6,10,10,6,1,0)` and does not realize weight 6. The word
`012300333300112241122545545544` realizes the weight-6 mask with legal
`S(16) = (10,6,6,10,1,0)` and only five weight-2 masks. At depth 12 that last
word has counts `(5,1,1,5,0,0)`. Edge `{1,3}` is already impossible: sources
0 and 3 are finished, the only prefixes with residue 1 on source 3 have
residue 1, 2, or 3 on source 0, and a finished source 0 can only contribute
future residue 0. This is one readable case of the prune, not a substitute
for the census.

PR #7038 shows that a legal `S(16)` freezes a coordinate at 10, so the chain
hypothesis (H) is empty. It does not derive a legal centre from the sixteen
masks. The present census shows that the conjunction does not supply a legal
centre either. It does not show that the conjunction is empty, and it does
not replay the centre-freeze.

## What this does not claim

An illegal-centre floor word realizing all fifteen weight-2 masks and the
weight-6 mask is not constructed and not excluded. The canonical tree in
which every count is still at most 3 has 550,917,287 nodes, and the
future-box test does not fire there, so the same direct census does not
decide that remaining polarity.

A depth-two word would realize these sixteen masks, among others. Ruling out
the legal-centre part of that fibre does not by itself rule out depth two.
No supplier, consumer, or selected frontier changes.

## Reproduce

Python 3.12 and `gcc` with `-std=c11`, from the repository root. The C
census and the Python two-zero enumerator run together; wall time is the
slower of the two, about five minutes here.

```sh
python3.12 -I -W error -B research/c5-joint-mask-s16/verify.py full
python3.12 -I -O -W error -B research/c5-joint-mask-s16/verify.py c-only
python3.12 -B scripts/research_package.py --package research/c5-joint-mask-s16 --check-only
```

`full` repeats the two-zero shape in Python and runs both shapes in C.
`c-only` repeats the controls and the C census. The marker token is the
package id.

```text
PASS_C5_JOINT_MASK_S16 centres=300 shapes=2 canonical_r0=10090080 canonical_r2=67267200 python_mode0_solutions=0 c_solutions=0 legal_centre_impossible=1 mode=full
```

Under `c-only` the same line has `python_mode0_solutions=na`. Failures raise
`SystemExit`. Optimized mode cannot silence them. No Lean, Docker, or
historical suite was run. `scripts/check_research_commit.py --check-source-history`
was not run: this checkout does not carry the full history that preflight
requires.

## Open next questions

1. Does any floor word with illegal `S(16)` realize all fifteen weight-2
   masks and the weight-6 mask?
   *Why:* legal `S(16)` is impossible under that conjunction, so only this
   polarity remains. PR #7038 still has no derivation of a legal centre from
   the sixteen masks, and this census shows that derivation cannot succeed.
   *First step:* a sound prune that cuts inside the region where every count
   is at most 3. The future-box test does not fire there.
   *Blocked by:* that region has 550,917,287 canonical nodes. A failed search
   is not emptiness. The PR #6216 empty-fibre assertion is not an input.

## Credit

The depth-two interface and the weight identity are Nick Petalas's
(PR #4231, PR #4248, PR #6107), with the Ross Richardson PR #934 / PR #943
lineage. JosieElliston's PR #6141 is the solver exclusion. queelius's merged
PR #6216 is the characteristic-5 DRAT certificate; it is not replayed here.
The centre-freeze and hypothesis (H) are open PR #7038. The separate
counterexamples that leave this conjunction open are open PR #7058. The
sorted word is the weight-two control of
`research/connector-six-source-small-char`. The weight-6 legal word is the
flexible all-ones witness of PR #7058.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
