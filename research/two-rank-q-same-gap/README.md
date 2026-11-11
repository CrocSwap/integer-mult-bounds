# Two rank-q maps in one internal gap

**No new kappa.** On the paired-star one-gap schedule, two matrices of rank
at most `q` in the same internal gap, each with `P_s Z P_f = 0`, can make
every helped core block equal `I_{2q}`. The selected frontier stays
`363005817/100000000000`.

The prescribed first step does not. Two copies of the rank-`q` witness of
open PR #7053, placed on complementary leaf halves or on complementary core
directions, do not reach rank `2q` while obeying the square equation. With
`B12 = B21 = 0` the next-leaf block of every internal sum has rank at most
`q`, because it factors through a projector image of dimension `q`. That
negative step is not an unrestricted nonexistence claim.

The positive pair uses `B12 = B21 = I_q`. Each factor has rank `q`, kills
the image of the first half, and the three blocks of the sum are `I_{2q}`
for both half orders and every `q >= 1`. A helped leaf can therefore meet
`A_j + B_j = I_d` with no external rank. The uniform lift of open PR #7053
to external rank `q(g - 1)` does not apply to every placement. The
dropped-leaf bound `q(g - 3)` of open PR #7025 still applies.

With those identity blocks the parity count is sharp for the inequalities,
and it depends on the stage:

- odd `g`, even stage: external rank at least `q(g - 1)`,
- odd `g`, odd stage: external rank at least `q(g - 3)`,
- even `g`: external rank at least `q(g - 2)` at every stage.

At `g = 31` and `q = 26` the odd-`g` numbers are **780** and **728**. The
even-stage number `780` holds for any internal matrices, because an even
stage helps only one even leaf. The tuples that meet these counts are
solutions of the gap inequalities, not words.

This is a proof under those hypotheses. The statement, the case split, and
the limits are in [PROOF.md](PROOF.md). The `q = 1` census is an exhaustive
check of the rank-at-most-1 matrices on eight `F_2` coordinates. It is not
a census of words.

The question is the first open question of open PR #7053. The every-stage
theorems of open PRs #7050 and #7126, and the second open question of
#7053, are not taken.

## Evidence

The argument is a proof in the projector algebra and in elementary linear
rank, over any field of characteristic two. The registered checker also
records four finite checks:

- the explicit pair at `q` in `{1, 2, 3, 8, 26}`, both half orders, with
  the three blocks equal to `I_{2q}`;
- the projector-image cap `q + rank(B21)` on several explicit blocks,
  including singular ones;
- the two complementary copies of the rank-`q` witness, which miss rank
  `2q`;
- an exhaustive census, over `F_2` at `q = 1`, of every rank-at-most-1
  matrix on the eight coordinates, for every scalar pair `(B12, B21)` and
  both half orders.

The gap tuples are checked for every `g` from `3` through `40` and every
stage. The closed form is proved for every `g >= 3` in
[PROOF.md](PROOF.md). The census is complete for its finite domain. It is
not a proof for general `q`.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/two-rank-q-same-gap
```

Expected status: `PASS_TWO_RANK_Q_SAME_GAP`, with `blocks=I_2q`,
`odd_stage_external=728` and `even_stage_external=780`. The same command
under `python3 -O -B` is registered. The checks raise `SystemExit`, so
optimized mode does not drop them.

## Open next questions

- At an odd stage, can external gaps of total rank `q(g - 3)`, together
  with the two maps of [PROOF.md](PROOF.md), meet `A_j + B_j = I_d` on
  every leaf at `g = 31`, `q = 26`? The inequality count is sharp at 728,
  and no word is constructed. First step: at stage `1`, place the two
  maps, set the three helped external blocks to zero, and test the cover
  of [PROOF.md](PROOF.md) on the remaining leaves. The monomial transport
  is not rebuilt in this package, so a passing rank tuple would still not
  be a word. This is not the every-stage question, and it is not the
  one-matrix gap tuple of open PR #7053.
- For `0 < rank(B21) < q`, can two rank-at-most-`q` maps attain next-block
  rank `q + rank(B21)` and own-block rank `2q` at once? The image cap is
  proved for every off-diagonal block, and the extremes `0` and `q` are
  attained. First step: at `q = 4`, take `B21` of rank 1 and `B12 = I_4`,
  and test whether a sum of two rank-at-most-4 maps meets both ranks while
  killing `im P_f`. The identity witness uses `B21 = I_q`, so its
  functionals need not kill the smaller image.

## Credit

The one-gap schedule and `q(g - 3)` are open PR #7025. The three blocks,
the one-map cap, the rank-`q` witness, and this question are open PR
#7053. The paired-star contract and the commuting map-count are from PR
#5747 (Ali Romman), including PR #5673, PR #5631, and PR #5617. Cinna Davis
supplied the controller and simplex lineage those packages retain. Open PR
#7005 is the consecutive-halves bound. Open PR #7126 is the every-stage
factor. Neither is rerun.

Prepared by unpaidmoon with substantial Cursor Grok assistance.
Independent human review and a proof-assistant proof are unclaimed.
