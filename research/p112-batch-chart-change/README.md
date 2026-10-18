# P112 two-call batch under changed cross-call label charts (isometric, free-conversion case of PR1714 open question 3)

**Scoped negative result and research note. No new supplier and no κ claim.
The selected frontier is unchanged.**

Merged PR1714 (`research/p112-batch-centre-floor`, alephnan) proves a 64k
root-code copy floor for k independent P112 calls. It assumes that all
calls share **one common label chart**, and its open question 3 asks
whether changing cross-call charts can help. This package changes exactly
that premise for k = 2 and C = I_2. It answers only the isometric,
free-conversion case of that question; PR1714's question also asks for
legal maps with priced conversions, which this package does not supply. Call 2's labels are re-charted by an
isometry φ of the label form, so call 2's own pairing is unchanged.
Conversions are granted free. All other parts of PR1714's model are kept:
root-code factors, ordinary transpose, the all-pairs endpoint and the
separate-total union price.

## What was learned

1. **PR1714's per-term step does not extend to changed charts.** That
   step is "every active term costs ≥ 8, even across call indices".
   PR1714 asserts it only under its common chart, so this is not an
   error in PR1714. A
   *pure cross term* has its reader in call 1 and its source in call 2.
   Under φ it costs 7 exactly when `b(v_i, φ v_j) = 0`, where
   `H_i = v_i^⊥` are the eight exceptional label hyperplanes. The
   transvection `t_u` with isotropic u makes exactly s² ordered pairs
   rank 7, where s = #{k : b(v_k,u) = 1}.
   - All 255 isotropic transvections were checked. The s² census is 0 for
     15 vectors, 16 for 224 vectors and 64 for 16 vectors.
   - Some isometric charts therefore make **all 64** exceptional cross
     pairs rank 7.
   - A seeded sample of 162 charts in O(V,b) gives rank-7 pair counts
     {0, 16, 24, 28, 32, 36, 40, 64}.
   - 1,600 direct 56×56 F2 ranks agree with the formula.
2. **The two-call floor still holds: Theorem A.** For every isometric chart,
   every exact root-code factorization costs at least **128**. Equality
   holds only when there are no pure cross terms. The proof splits terms
   into non-pure terms, which cost ≥ 8 by PR1714's pair lemma, and pure
   cross terms, which cost ≥ 7. A Schur-complement count gives
   `|N| ≥ 16 − min(r01, r10)`. Hence
   `cost ≥ 128 + 6·min + 7·(r01 + r10 − 2·min) ≥ 128`. A rank-7 term saves
   one unit locally, but costs a whole extra term. See [PROOF.md](PROOF.md).
3. **General cross forms give a sufficient condition only.** In a V⊕V
   model with arbitrary cross forms, `c01 + c10 ≥ 8` suffices for the
   128 floor (Proposition B). The zero cross form has c = 0, yet it still
   obeys the floor by a separate additivity argument (Proposition C). In
   this "β = 0 pitfall", the cheap-looking Schur pattern has 16 free pure
   cross terms. Its both-call terms cost 16 each, so the replayed total is
   exactly 128. More generally, Proposition D holds for **any** cross
   forms:
   `total ≥ 128 − Σ_double min(8, ρ01+ρ10) + Σ_pure price`.
   A sub-128 decoder in any cross-form model therefore needs pure terms in
   both directions, so that min(r01, r10) ≥ 1. It also needs "double"
   terms, which touch both calls on both sides, whose cross-form ranks
   strictly exceed what the pure terms pay.
   **Corollary B′:** every *invertible* chart φ, isometric or not, read in
   the V⊕V model (each call keeps its own b; cross forms `b(x, φy)` and
   `b(φx, y)`) has c01, c10 ≥ 7, because
   `rank b|(H_i × φH_j) ≥ 8 + 8 − 9`. So Proposition B gives the 128 floor
   there too. The same holds for any cross forms with
   `rank β01 + rank β10 ≥ 12`, since restricting to a hyperplane pair
   lowers rank by at most 2 on each side.

No exact decoder costing ≤ 127 was found in any model. That is a statement
about the fixtures and the finite search below, not an impossibility
theorem for general cross forms.

| Exact fixture (full 224×224 all-pairs replay) | Chart / form | Cost | Theorem A bound |
|---|---|---|---|
| Standard decoder, 16 terms | all 162 sampled isometric charts, β = 0 | 128 | 128 |
| One-cross decoder, 16 N terms + 1 rank-7 pure term | targeted transvection | 135 | 135 (tight) |
| Same decoder | common chart | 136 | — |
| Two-cross decoder, 15 N terms + 2 rank-7 pure terms | targeted transvection | 135 | 134 |
| Schur pattern R01 = R10 = I, 8 N terms + 16 pure terms | targeted transvection | 188 | 176 |
| Schur pattern | β = 0 | 128 (8×16 + 16×0) | Proposition C |
| Non-coordinate Schur pattern `[I;−I]MM⁻¹[I,−I]` + 16 pure terms | targeted transvection / β = 0 | 192 / 140 | 176 / Prop. C |

The **cross-form search** is finite and fixed-seed (20261016). Its domain is
four exact decoder families: three coordinate families and the
non-coordinate Schur pattern. Each was crossed with β = 0, the targeted
chart, and 48 random cross-form pairs. The minimum cost found is 128, and
the minimum Proposition D bound is also 128. This search is weak: 49 of
the 50 forms already meet the Proposition B condition. The PROOF.md
remark proves that the coordinate families cost ≥ 128 for every cross
form. No other decoders were searched.

## Reproduce

Python ≥ 3.12, standard library only. From the repository root:

```sh
python3 -I -O -B research/p112-batch-chart-change/verify.py
```

Expected result: the command prints a JSON receipt and
`receipt_sha256 92d4555bb78cbcc7b0945391416ea1a5df4fafaabc356e735406c96844bbf2bd`,
then `PASS_P112_BATCH_CHART_CHANGE`. It takes about 19 s on one CPU and
needs well under 100 MB. Validated on CPython 3.14.4 only; the registered
Python 3.12 replay (`research_package.py` without `--check-only`) was not
run on this machine. Package metadata check:
`python3 scripts/research_package.py --package research/p112-batch-chart-change --check-only`.

**Method.** The verifier builds P112 independently as the norm-4 shell of
{x ∈ Z⁸ : x mod 2 ∈ RM(1,3)}, checking reflection closure and
`XᵀX = 56I`. It then cross-checks this geometry against the pinned data file
`research/p112-single-lift/reference-geometry.json`
(sha256 `4f44af36…a080`). That check matches the 112 lines and confirms the
reference doubled roots are the 120 doubled E8 lines. It also checks
`q·q' = 2x·x'` on 12,544 entries. The labels satisfy `B = 1 + x·x'/2 mod 2`
with rank 9, and `B = cᵀGc` holds on all 120² entries. The verifier
rechecks the finite support premises: 503/8 rational ranks over all 511
functionals, and all 64 common-chart pairs at rank 8.

The verifier then checks the chart facts and five exact decoders by full
all-pairs Gaussian-integer replay (250,880 entries). It prices them by
F2 ranks of union-support pairings in two independent ways: by the span
basis in V⊕V, and by the direct single-V union matrix. It also checks that
the chart model equals the cross-form model with
`β01 = Gφ, β10 = φᵀG`. No predecessor code is imported or executed.

**Negative controls (all must fail and do).** The verifier runs seven
internal controls:

1. An invertible non-isometric shear (`e_k ↦ e_k + e_l`) is rejected by
   the pairing-preservation branch of the isometry check.
2. The same invertible non-isometric chart changes call 2's own pairing.
3. The all-ones C endpoint mutation is rejected against I₂, although it
   is exact for its own C.
4. A Hermitian-only decoder `(i, i)` is rejected under the ordinary
   transpose, while `(i, −i)` passes.
5. Cross-call crosstalk passes a diagonal-only check but fails the
   all-pairs check.
6. A corrupted rank claim, rank 8 for the targeted rank-7 pair, is
   detected.
7. A corrupted fixture cost, 127, is detected.

Controls 6 and 7 are literal-claim guards: they show that a wrong
recorded value is caught, not that the pipeline has independent detection
power. The semantic mutations below and in the review are the stronger
evidence. As a positive fact (not a control), the verifier also records
that the anisotropic map `x ↦ x + b(x,a)a` is singular over F2 (rank 8),
so it is not a chart at all.

On-disk mutation replays in a scratch tree also gave `FAIL`, while the
unmutated scratch replay passed. (These were run on the previous receipt;
the only receipt change since then is the renamed controls 1–2.) The
author's four mutations were:

- flipping a decoder sign, which fails with "one-cross decoder exact";
- breaking the inverse M⁻¹ in the non-coordinate Schur decoder, which
  fails with "generic Schur-pattern decoder exact";
- changing the sample size, which fails with "receipt digest mismatch";
- corrupting one reference-geometry row, which fails with
  "same live lines".

An independent reproducibility review added eight more, all caught:
pricing that ignores φ ("direct price"), re-asserting PR1714's ≥ 8 step
under the targeted chart ("pure cross >= c"), an inverted zero-pair test,
a diagonal-only default check, a sign-flipped or duplicated reference
root, an always-true isometry check, and a weakened Proposition D bound
(now also caught by `require(min Prop D bound == 128)`). After the
control change, an `is_isometry` that skips its pairing branch fails with
"negative control did not fail: invertible non-isometric shear rejected
by pairing check".

## Scope, inherited assumptions, unresolved obligations

- Base commit `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. Source pins are in
  [SOURCES.json](SOURCES.json); the selected record is pinned as
  provenance only.
- **Inherited:** PR1714's model, including root-code factors, the
  separate-total union price, the all-pairs endpoint and ordinary transpose.
  The finite support and pair lemmas come from PR845, PR1098 and PR1714;
  their finite premises are rechecked here, and their written arguments
  are cited.
- **Scope:** k = 2, C = I₂, call 1 fixed, and call 2 re-charted by φ ∈ O(V,b)
  with free conversions. Charging conversions could only raise costs.
  The general cross-form statements are Proposition B, a sufficient
  condition, and Proposition D, a lower bound with necessary conditions
  for going below 128; neither is an "iff".
- **Not covered:** general k, C ≠ I₂, outside-code overcomplete factors,
  masked identities, temporal relations, non-isometric charts in the
  single-V model (where call 2's own pairing changes), the exact minimum
  for cross forms with c01 + c10 ≤ 7, and any physical or legal interface
  realizing a cross form.
- **Non-claims inherited from PR1714.** The 128 floor is internal to the
  algebraic separate-total union-price objective. It is not a lower bound
  for arbitrary interacting circuits, and it presupposes a corresponding
  separate-total copy/delivery interface. No compiler/all-size, hosting,
  precision/tape, analytic-transfer, H1–H5 or selected cold-replay
  obligation is touched. The per-call centre charge stays 64, so the
  card's acceptance ceiling is unchanged.
- PROOF.md is a written proof checked by the author with AI assistance.
  It is not a Lean proof or independent human review. Finite replays
  certify only the stated fixtures and samples.

## Open next questions

1. **Is 128 the minimum for every general cross form?** This matters
   because a sub-128 form would locate the cross-call pairing a sharing
   interface would need to realize. Proposition D narrows the search to
   decoders with pure terms in both directions and double terms whose
   cross-form ranks exceed the pure payments. The first step is to search
   low-rank cross forms (rank ≤ 3 on hyperplane pairs) against such
   *non-coordinate* decoders, using this verifier's exact pricing. The
   blocker is the lack of a mechanism; any hit would be only a
   model-sharpness control until a legal, priced interface exists.
2. **Does Theorem A extend to k ≥ 3?** This matters because batching more
   calls is the natural sharing route. The first step is to bound
   `rank(I − R)` for zero-diagonal block R by pure-term ranks, then test
   k = 3 coordinate fixtures. The blocker is that the two-block Schur
   count does not generalize directly.
3. **Can non-isometric charts in the single-V reading, with an
   explicitly priced demand change, help?** They alter call 2's own
   pairing. (In the V⊕V reading every invertible chart is already
   covered by Corollary B′.) The first step is to state the
   changed within-call price and recheck the pair lemma. The blocker is
   the need for a new legal demand contract; per PR1714, relabelling is
   not free.

## Credit

- **alephnan (PR1714)**: the common-chart batch coupling-rank law, the
  pair-lemma use and open question 3.
- **Mihir Srivastava (PR845)**: the support classification.
- **Adam Gall (PR1098)**: independent corroboration of that
  classification.
- **woklerx (PR1077/PR1180)** and **themilkman216 (PR968)**: root-code
  floors.
- **Douglas Colkitt (PR1240)**: the packing ceiling and centre-sharing
  motivation, the complex-local-word-ceiling lever screen and the
  research-package generator.
- Related concurrent work, not built on here: **DreamingOfClouds (PR2228,
  PR2277)** on one-call root-code floors, and PR1708/PR1748 (1337isnot1337,
  ToikY) on physical sharing.
- The `research/p112-single-lift/reference-geometry.json` data file is
  used only for comparison. It is credited to Mihir Srivastava's package,
  which snapshots **DreamingOfClouds' PR717** arrays. Joel Pulikkan /
  GamingPuzzled (PR620) and the lineage in that package's NOTICE.md keep
  their credit.
- Selected-construction credit is unchanged: Rohan Arun, Jeremy Kothe,
  Hao Yan and the lineage in the selected review.

Prepared by thakrarsagar with substantial AI assistance from Claude (Anthropic, Claude Opus 5.5). Apache-2.0.
