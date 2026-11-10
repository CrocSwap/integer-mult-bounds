# Every-stage internal gaps miss total thin rank 130

**No new kappa.** On the paired-star contract, put the stage blocks in order
`0, ..., g-1` and leave thin maps in the gap between the two halves of every
stage. Other thin maps may sit only in the gaps before, between, and after
those blocks. After the squared stage monomial is removed, the surviving
degree-1 core-to-leaf block of an internal map is a sum of two sandwiches, so
its rank is at most twice the rank of that map. Counting the leaves each map
can meet gives

```text
total thin rank >= q g / 2.
```

At `g=31`, `q=26` the bound is **403**. Five rank-26 maps have total rank
**130**, so this schedule has no endpoint. The selected frontier stays
`781451/250000000`.

This is a proof under that schedule hypothesis. The exponent comparison is an
exhaustive check of a finite set of monomials. The `q=1` rank comparison is an
exhaustive census of `4` by `4` matrices and is not an input to the bound 403.
The note is not a heuristic search and it is not unrestricted nonexistence of
the `g=31`, `q=26` profile. The statement and the limits are in
[PROOF.md](PROOF.md).

The question is the first open question of open PR #7025. That PR proved the
one-gap bound `q(g-3) = 728` and did not place a gap in every stage.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/g31-q26-every-stage-gap
```

Expected status: `PASS_G31_Q26_EVERY_STAGE_GAP`, with `lower_total_rank` equal
to 403 and `profile_total_rank` equal to 130. The same command under
`python3 -O -B` is registered. The checks raise `SystemExit`, so optimized
mode does not drop them.

## Open next questions

- Under `P_s Z P_f = 0`, is the own-leaf degree-1 core-to-leaf block of rank
  at most `rank(Z)` for every half width `q`? The proved estimate is twice
  that rank. The exhaustive `q=1` census finds no square-free excess. A
  general factor of 1 would raise this schedule's bound from `q g / 2` to
  `ceil(2 q g / 3)`. First step: show that the two sandwiches
  `pi_core Z P_f` and `pi_core P_s Z` land in one common subspace of
  dimension `rank(Z)`.
- Do the leaf-to-core blocks of the same every-stage word force total thin
  rank strictly above `q g / 2`? The bound 403 uses only the core-to-leaf
  side. First step: read the leaf-to-core block of the surviving degree-1
  term under `P_s Z P_f = 0`, then repeat the weight count.

## Credit

The paired-star contract and the commuting map-count are from PR #5747
(Ali Romman), including PR #5673, PR #5631, and PR #5617. Cinna Davis
supplied the controller/simplex lineage those packages retain. Open PR
#7025 is the one-gap bound `q(g-3)` and the source of this question. Open
PR #7005 is the consecutive bound `q g`, which excludes the internal slot.

Prepared by unpaidmoon with substantial Cursor Grok assistance.
Independent human review and a proof-assistant proof are unclaimed.
