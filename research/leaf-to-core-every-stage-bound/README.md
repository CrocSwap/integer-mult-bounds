# Leaf-to-core blocks raise the every-stage thin-rank bound to 2q⌈2g/5⌉

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration. No new
kappa, no word, and no selected-frontier change. The selected record stays
`certificates/selected-result.json`, with
`κ = 363005817/100000000000`.

Nick Petalas's open
[PR #7126](https://github.com/CrocSwap/integer-mult-bounds/pull/7126)
proves that, on unpaidmoon's every-stage schedule from open
[PR #7050](https://github.com/CrocSwap/integer-mult-bounds/pull/7050),
the own-leaf degree-1 core-to-leaf block has rank at most `rank(Z)`, and
that a successful word has total thin rank at least `2 q ceil(g / 3)`.
At `g = 31`, `q = 26` that is 572. The same core-to-leaf inequalities
admit a covering point of that value, so they give nothing higher.
Question 1 of #7126 asks whether the leaf-to-core blocks raise the bound.

They do, once the two sides are counted together. The [proof](PROOF.md)
has four steps.

1. **Same contributors.** Under #7050's one-stage identities, the full
   calls contribute `N_j I_d` on leaf-to-core, with
   `N_j = product_{k <= j} D_k`. An internal gap meets `N_{t-1}`, `N_t`
   and `N_{t+1}`. An external gap after `gamma` stages meets
   `N_{gamma-1}` and `N_gamma`. Counted separately, these are #7126's
   contributors, and the covering point of value `2 q ceil(g / 3)` remains
   feasible.
2. **Coupling.** If `P_s Z P_f = 0`, the previous-leaf core-to-leaf rank
   plus the next-leaf leaf-to-core rank is at most `rank(Z)`. Full rank on
   the previous core-to-leaf block forces the next leaf-to-core block to
   vanish.
3. **The test in the question.** For every `q`, with `B12 = B21 = I_q`,
   one internal map of rank `2q` meets leaves `t-1`, `t` and `t+1` at
   core-to-leaf rank `2q` and contributes `I_{2q}` on its own leaf-to-core
   monomial and on the previous leaf's. It contributes `0` on the next
   leaf's leaf-to-core monomial. It also emits a degree-0 own block `I_{2q}`,
   so it is not a successful word.
4. **Bound.** A weight supported on core-to-leaf leaves `j ≡ 0 (mod 5)`
   and leaf-to-core leaves `j ≡ 2 (mod 5)` is feasible for the coupling.
   Its value is `2 q ceil(2g / 5)`. At `g = 31`, `q = 26` this is **676**,
   against #7126's 572. The proved inequalities also admit a point of
   value `2 q ceil(2g / 5)`, so this coupling gives nothing higher. The
   two ceilings agree exactly for `g in {1, 2, 4, 5, 7, 10}` and the new
   one is strictly larger for every other `g >= 3`, including every
   `g >= 15`.

#7050's schedule hypothesis and #7126's rank lemma are cited premises.
They are not replayed.

## Evidence and reproduction

From the repository root, with CPython 3.12 and its standard library:

```sh
python3 -I -W error -B research/leaf-to-core-every-stage-bound/verify.py
python3 -I -O -W error -B research/leaf-to-core-every-stage-bound/verify.py
python3 -B scripts/research_package.py --package research/leaf-to-core-every-stage-bound
```

Each verifier run ends with

```text
PASS_LEAF_TO_CORE_EVERY_STAGE old_g31_q26=572 joint_g31_q26=676 rank_one_maps=65025 square_zero=28161 word_cancelled_core=2 no_new_kappa
```

The checks, all exact:

- the block-alphabet witness, including both degree-0 own blocks equal to `I`;
- the `g = 3`, `q = 1` word: bare `M_j I` and `N_j I`, and the witness's
  cancellations and the surviving `N_2 I`;
- all 65,025 rank-one maps on the core, the stage leaf and the two
  neighbours, plus one square-violating control whose two coupled blocks
  both have rank 1;
- 300 seeded rank-bounded maps, as corroboration rather than a census;
- monomial hits, dual load, feasible point and the comparison with
  `ceil(g / 3)` for every `g <= 64`, plus one rejected dual pattern.

The rank-one census and the seeded sample corroborate Lemma 1. The proof
is sections 1 to 5 of `PROOF.md`.

## Scope and limits

Theorem 2 is conditional on the cited schedule analysis and on the
factor-1 lemma. Nested and crossed intervals are outside that schedule.
The one-gap bound 728 of #7025 and the consecutive bound 806 of #7005 are
not replaced. The number 676 is a lower bound from rank inequalities, not
an attained word. The witness cancels four targeted blocks and emits other
monomials. For six stage counts the new expression equals 572's general
form, so this argument does not raise those values. No `g = 31`, `q = 26`
word is constructed or excluded outside this schedule. No independent
human review and no formal proof-kernel review is claimed. No Lean,
Docker or selected-supplier replay was run. Source pins are in
[SOURCES.json](SOURCES.json).

## Open next questions

- Is total thin rank `2 q ceil(2g / 5)` realized by a word whose
  core-to-leaf and leaf-to-core blocks are exactly the required identities
  and whose other core-leaf monomials vanish? The feasible point only meets
  the rank inequalities, and the witness emits a degree-0 own block `I`.
  First step: at `g = 3`, `q = 1` the bound is 4; decide whether one or two
  internal maps of total rank 4 can cancel every core-leaf monomial.
- Do the extra monomials of a full-rank internal map force rank above
  `2 q ceil(2g / 5)`? The coupling method stops at that number.
  First step: list every nonzero core-leaf monomial of the section-4
  witness at `g = 3`, `q = 1`, and test whether a second rank-2 map cancels
  them.
- For `g in {4, 5, 7, 10}`, where `ceil(2g / 5) = ceil(g / 3)`, can the
  blocks be exactly the identities at total rank `2 q ceil(g / 3)`?
  First step: `g = 4`, `q = 1`, target rank 4, using only block sets that
  obey the coupling.

Structured relevance, first steps and blockers are in [TASK.json](TASK.json).

## Credit

unpaidmoon's #7050 supplies the schedule, the square condition, the
one-stage off-block identities, the core-to-leaf monomials and the
factor-2 bound. Nick Petalas's #7126 supplies the factor-1 lemma, the
bound `2 q ceil(g / 3)`, the covering point and the question answered
here. unpaidmoon's #7025 and #7005 supply the neighbouring bounds.
The paired-star contract and the commuting map-count are from Ali
Romman's #5747, with #5673, #5631 and #5617. Cinna Davis supplied the
controller and simplex lineage those packages retain.
