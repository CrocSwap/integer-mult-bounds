# One rank-q internal map raises the external bound to `q(g-1)`

**No new kappa.** On the paired-star schedule of open PR #7025, let the
single internal gap contribute one matrix `Z` of rank at most `q`. A
successful word needs `P_s Z P_f = 0`. The three core blocks of `Z` on leaves `t - 1`, `t` and
`t + 1` each have rank at most `q`. Every external gap-rank tuple of a
successful word then satisfies

```text
R_ext >= q (g - 1).
```

That is strictly above the dropped-leaf bound `q(g - 3)` of PR #7025, by
`2q`. At `g = 31` and `q = 26` the bounds are **780** and **728**. The
selected frontier stays `781451/250000000`.

This is a proof under those hypotheses. It is not a census of words, not a
heuristic search, and not unrestricted nonexistence of the `g = 31`,
`q = 26` profile. A sum of internal maps whose rank exceeds `q` is outside
the claim. The statement and the limits are in [PROOF.md](PROOF.md).

The question is the second open question of open PR #7025. The consecutive
bound `q g = 806` in open PR #7005 excludes the internal slot and is not
reproved here.

## Evidence

The argument is a proof in the projector algebra and in elementary linear
rank. The registered checker also records three finite checks:

- an exhaustive census, over `F_2` at `q = 1`, of every rank-at-most-1
  matrix on the eight coordinate lines, for every scalar pair
  `(B_12, B_21)` and both half orders;
- an explicit matrix of rank `q`, for several `q` including `26`, whose
  three blocks have ranks `q, q, q`, and a second matrix of rank `q` that
  reaches block ranks `q, q, 2q` once `P_s Z P_f = 0` is dropped;
- the gap-rank tuple of total `q(g - 1)` at stage `1`, for every `g` from
  `3` through `40`.

The census is complete for that finite domain. It is not a proof for general
`q`, and the gap tuple is not a paired-star word.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/paired-star-internal-three-blocks
```

Expected status: `PASS_INTERNAL_THREE_BLOCKS`, with
`external_rank=780`, `dropped_leaf_rank=728` and `rank_sum_cap=78`. The
same command under `python3 -O -B` is registered. The checks raise
`SystemExit`, so optimized mode does not drop them.

## Open next questions

- Can two matrices of rank at most `q` in the same internal gap, each with
  `P_s Z P_f = 0`, make every helped core block sum to rank `2q`? That
  would cancel the external remainder and could return the external bound
  to `q(g - 3)`. First step: add two copies of the rank-`q` witness in
  [PROOF.md](PROOF.md) on complementary core coordinates and read the three
  block ranks.
- Does a gap-rank tuple of total `q(g - 1)`, together with one internal
  matrix of rank `q`, meet `I_d` on every core-to-leaf block at `g = 31`,
  `q = 26`? The inequality count is sharp, and no word is constructed.
  First step: at stage `1`, place the rank-`q` witness in the internal gap
  and solve the even external gaps for a complement of its three blocks.

## Credit

The paired-star contract and the commuting map-count are from PR #5747
(Ali Romman), including PR #5673, PR #5631, and PR #5617. Cinna Davis
supplied the controller/simplex lineage those packages retain. Open PR
#7005 is the consecutive-halves bound. Open PR #7025 is the one-gap
coefficient and the source of this question.

Prepared by unpaidmoon with substantial Cursor Grok assistance.
Independent human review and a proof-assistant proof are unclaimed.
