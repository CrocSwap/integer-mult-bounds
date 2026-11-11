# One internal thin gap misses total rank 130

**No new kappa.** On the paired-star contract, keep the two full calls of
every stage adjacent, and allow thin maps in at most one gap between the
two halves of a single stage. The core-to-leaf coefficient of that gap is
quadratic in the stage variable. In the eigenbasis of the half idempotent
the off-diagonal blocks of `B` stay free, and the coefficient meets the
required monomial of at most three leaves. The remaining leaves still force

```text
total thin rank >= q (g-3).
```

At `g=31`, `q=26` the bound is **728**. Five thin maps of rank 26 have
total rank **130**, so this schedule has no endpoint. The selected frontier
stays `781451/250000000`.

This is a proof under that schedule hypothesis. It is not a census of
words, not a heuristic search, and not unrestricted nonexistence of the
`g=31`, `q=26` profile. Nested intervals, crossed intervals, and an
internal gap in every stage stay open. The statement and the limits are in
[PROOF.md](PROOF.md).

The question is the first open question of open PR #7005. The consecutive
bound `q g = 806` in that PR excludes this internal slot and is not
reproved here.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/g31-q26-internal-gap
```

Expected status: `PASS_G31_Q26_INTERNAL_GAP`, with `lower_total_rank` equal
to 728 and `profile_total_rank` equal to 130. The same command under
`python3 -O -B` is registered. The checks raise `SystemExit`, so optimized
mode does not drop them.

The checker proves the eigenbasis form of `B`, both half orders, and the
closed form of `VZU` with noncommuting letters. A `g=3`, `q=1` word with
nonzero `B` is a conjugation control, including the failure of a diagonal
block of `B` and the additivity of two maps in the same gap. The exponent
comparison and the gap count are exhaustive at `g=31`.

## Open next questions

- Can one internal thin gap in every stage meet the `g=31`, `q=26`
  endpoint with total thin rank 130? A single gap leaves at least `g-3`
  leaves to the external count. One gap per stage can remove that count.
  First step: impose `P_s Z P_f = 0` from the squared monomial at one
  stage, then read the core-to-leaf block of the surviving degree-1 term.
- Does the internal map's contribution on its three leaves raise the
  external bound above `q(g-3)`? The argument above drops those leaves
  entirely. First step: bound the sum of the ranks of the three core
  blocks of one matrix of rank at most `q`, using `P_s Z P_f = 0`.

## Credit

The paired-star contract and the commuting map-count are from PR #5747
(Ali Romman), including PR #5673, PR #5631, and PR #5617. Cinna Davis
supplied the controller/simplex lineage those packages retain. Open PR
#7005 is the consecutive-halves bound and the source of this question.
Open PR #7010 keeps the internal slot outside its map-count hypothesis.

Prepared by unpaidmoon with substantial Cursor Grok assistance.
Independent human review and a proof-assistant proof are unclaimed.
