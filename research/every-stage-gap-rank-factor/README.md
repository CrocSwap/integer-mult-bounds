# The every-stage gap: rank factor 1 and total thin rank at least 2q⌈g/3⌉

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration. No new
kappa, no word, no selected-frontier change.

unpaidmoon's open
[PR #7050](https://github.com/CrocSwap/integer-mult-bounds/pull/7050)
studies paired-star words with one internal thin gap in every stage. It
proves that the own-leaf degree-1 core-to-leaf block has rank at most
`2 rank(Z)`, deduces total thin rank at least `q g / 2`, and asks in its
open question 1 whether the factor is 1 under the square condition
`P_s Z P_f = 0` for every half width `q`.

The answer is yes. The [proof](PROOF.md) has three results.

1. **Rank lemma.** For complementary idempotents `P + Q = I` over any
   field and any `Z` with `Q Z P = 0`,
   `rank(P Z P + Q Z Q) = rank(P Z P) + rank(Q Z Q) <= rank(Z)`.
2. **Factor 1, sharp.** For every `q`, every `B12`, `B21` and either half
   order, the own-leaf degree-1 block has rank at most `rank(Z)`. Equality
   holds at every `q`, with `rank(Z) = 2q`.
3. **Bound.** Under #7050's schedule analysis, a successful every-stage
   word has total thin rank at least `2 q ceil(g/3)`. At `g = 31`,
   `q = 26` this is **572**. #7050 proves 403. Its predicted factor-1
   weight count would give 538.

The third result counts leaves `0, 3, 6, ...`, whose contributing gaps are
pairwise disjoint. The same inequalities admit a covering point of value
`2 q ceil(g/3)`, so rank counting on these blocks gives nothing higher.
That is a limit of the method, not a word.

#7050's schedule hypothesis, square condition and monomial comparison are
cited premises. They are not audited or replayed. The lemma and its
application to the stage halves are self-contained.

## Evidence and reproduction

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/every-stage-gap-rank-factor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/every-stage-gap-rank-factor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/every-stage-gap-rank-factor
```

Each verifier run takes about three seconds and ends with

```text
PASS_EVERY_STAGE_GAP_RANK_FACTOR factor=1 bound_g31_q26=572 certificate=e42b24ab6676fb20 no_new_kappa
```

The checks, all exact:

- every 4 by 4 matrix over `F_2`, every `B`, both half orders: 524,288
  cases, of which 32,768 satisfy the square condition, and the lemma and
  the block bound hold on each;
- a control: 168 of 1,800 rank-one cases have block rank 2, and each
  violates the square condition;
- 4,500 seeded random cases on the actual stage halves at `q = 2, 3, 4`;
- 3,200 seeded random cases of the lemma over `F_2`, `F_3`, `F_5`, `F_7`;
- the sharpness witness at `q = 1, 2, 3, 5, 26`;
- 1,170 rank-one maps at `q = 1` that satisfy the square condition and
  meet leaves `t-1`, `t`, `t+1` at rank one each;
- contributor sets, disjointness and the covering point for every
  `g <= 64`, with two rejection controls.

The random cases corroborate the proof. They are not a census.

## Scope and limits

Theorem 4 is conditional on #7050's analysis of the every-stage schedule.
Nested and crossed stage intervals are outside that schedule. The
one-gap bound 728 of #7025 and the consecutive bound 806 of #7005 concern
smaller schedule families and are not replaced. The bound 572 is not shown
to be attained, and the leaf-to-core blocks are not used. No `g = 31`,
`q = 26` word is constructed or excluded outside this schedule. No
independent human review and no formal proof-kernel review is claimed. No
Lean, Docker or selected-supplier replay was run. Source pins are in
[SOURCES.json](SOURCES.json).

## Open next questions

- Do the leaf-to-core blocks raise the every-stage bound above
  `2 q ceil(g/3)`? The covering point of section 3 shows that the
  core-to-leaf rank inequalities stop there. First step: write the
  leaf-to-core degree-1 block of one internal gap under
  `P_s Z P_f = 0` and test whether a map that meets leaves `t-1`, `t`,
  `t+1` at full rank can also cancel its own leaf-to-core monomials.
- Is total thin rank `2 q ceil(g/3)` compatible with the other monomials
  of the endpoint at `g = 3`, `q = 1`, where the bound is 2? #7050's
  control word there has total rank 6. First step: an exhaustive census of
  one internal map of rank at most 2 in stage 1 against every
  core-to-leaf monomial.
- Does the block-triangular argument extend to nested or crossed
  intervals? There the map between two halves is conjugated by another
  stage's half, and the square condition changes. First step: derive the
  squared-monomial condition for one nested pair.

Structured relevance, first steps and blockers are in [TASK.json](TASK.json).

## Credit

unpaidmoon's #7050 supplies the schedule, the square condition, the
degree-1 block, the monomial comparison, the factor-2 bound, the `q = 1`
census observation and the question answered here. unpaidmoon's #7025 and
#7005 supply the neighbouring bounds. The paired-star contract and the
commuting map-count are from Ali Romman's #5747 with its predecessors
#5673, #5631 and #5617, and Cinna Davis supplied the controller and
simplex lineage those packages retain. The rank inequality for block
triangular matrices is classical.
