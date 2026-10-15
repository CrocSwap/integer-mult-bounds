# E6 B0 root-coordinate bilinear forms: exact rank-six floor

**Scoped negative result. No κ or selected-result change.** For one fixed E6 root-line realization and the B0 zero mask, every exact decoder that factors through the six-dimensional root-coordinate map is a scalar multiple of the Gram decoder. Its coordinate form has rational rank six, so this family contains no decoder with four or fewer totals.

This closes only a narrow algebraic ansatz. It does not rule out arbitrary rational E6 decoders, another admissible pairing, or a better multiplication bound.

## Exact statement

Scale E8 roots by two, so every root has squared norm eight. Start from its 120 root lines and retain the lines orthogonal to

```text
r1 = (2, 2, 0, 0, 0, 0, 0, 0)
r2 = (2, 0, 2, 0, 0, 0, 0, 0)
```

These roots have inner product four (one in the unscaled E8 normalization); their common orthogonal root lines form an E6 subsystem with 36 lines. Choose the first six independent normalized lines in lexicographic order as a basis. For each line `t`, let `x_t` be its exact `Q^6` coordinate column in that basis, and let `R` be the 36-by-6 matrix with rows `x_t^T`.

The fixed B0 mask is one on each **distinct orthogonal pair**. Consider all rational 6-by-6 matrices `L`, including nonsymmetric ones, satisfying

```text
x_t^T L x_s = 0 for every ordered pair t != s with <r_t,r_s> = 0,
x_t^T L x_t != 0 for all 36 lines.
```

Equivalently, the decoded matrix is `M = R L R^T`. Since `rank_Q(L)` is the number of rational rank-one terms needed to factor this coordinate form, `rank_Q(L) <= 4` would give a four-total decoder in this family.

The verifier constructs all 540 ordered orthogonal-pair equations on the 36 entries of `L` and row-reduces them over `Q`. The constraint matrix has rank 35 and its nullspace is exactly the one-dimensional span of the basis Gram matrix `G`. The matrix `G` has rank six; the scaled decoder diagonal is eight on every root line. Therefore every nonzero exact form in this family is `L = λG`, with `λ != 0`, and has rank six. No such form can use four or fewer totals.

## Cost screen and scope

For E6, the per-total floor is `w=5`. A T=4 candidate gets an optimistic floor-only bill of 20 if every term costs exactly five; the open E6 T=4 window thresholds are 23 at h=8, 22 at h=9 and 21 at h=10–11. Copies, frames, source access, restoration, hosting and precision are all granted free in this screen. This shows that the family was not screened out by the most favorable cost model before testing its exactness constraints.

The exact result removes this one root-coordinate route to those windows. It leaves open factors outside the image of `R`, other admissible pairings, larger total counts, and the full E6 non-star decoder problem. No actual decoder support tariff or supplier admission is claimed because no rank-at-most-four form survives.

## Evidence and controls

`RESULT.json` records the exact root, basis, coordinate and constraint hashes, the nullspace generator, its rank, and the diagonal. The positive control `L=G` satisfies every required zero and has diagonal eight. Negative controls confirm that `L=0` fails the nonzero-diagonal condition and that `G+E_00` violates an orthogonal-pair zero (260 ordered violations).

The root set is generated directly with integer vectors for the E8 D8 and even-half-sign families. The predecessor file `research/root-unit-decoder-lemmas/lib/ade.py` is pinned as provenance and checked for byte drift, but its floating-point root construction is not used by the proof calculation. All coordinates, constraints, ranks and controls in `verify.py` use `fractions.Fraction`.

## Reproduce

```sh
python3 -I -O -B research/e6-coordinate-bilinear-form-seed8e9cf2/verify.py
python3 -I -O -B research/e6-coordinate-bilinear-form-seed8e9cf2/test_verify.py
python3 scripts/research_package.py --package research/e6-coordinate-bilinear-form-seed8e9cf2 --check-only
```

The first command prints:

```text
PASS_E6_B0_COORDINATE_BILINEAR_RANK_FLOOR lines=36 orthogonal_ordered=540 constraint_rank=35 kernel=1 generator_rank=6 no_rank_le4_in_coordinate_form_family no_new_kappa
```

The generic package manifest registers a full replay with Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/e6-coordinate-bilinear-form-seed8e9cf2
```

Python 3.12 is not installed in this environment. Direct verifier, focused tests, and metadata/pin checks were exercised with the available Python 3.14.7; the registered 3.12 replay remains for hosted CI.

## Provenance and coordination

- Assignment: OS seed `8e9cf2d0cc1e238cdbea7700328e99f0`; track `complex-mechanisms`; card `complex-rank-shape-decoder`, refined from selector scope `cad3ba853d7f324f16fa`.
- Base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
- Priority revision 4; catalogue SHA-256 `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`.
- Selected record SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Coordination claim: [Discussion #1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18933558), taking the E6 T=4 handoff and narrowing it to this coordinate-form family.
- Predecessor pins: #1590 head `08e134b4a0c7f04869dae703f2a2e688e53c44f0` (merged/closed partial result); #2111 head `98da76c2839ba38538b510420dec54546ccabf0b`; #2125 head `d9eb80ac183bb4df185ca044fd65432b817333bb` at the overlap check. #1590 and #2111 develop the root-unit cost/decoder model; #2125 checks the standard-Gram E6 costs and leaves the E6 windows open. None classifies this rational `L` family.
- Exact predecessor source in this base: `research/root-unit-decoder-lemmas/lib/ade.py`, git blob `7e0063d97673b7d278ac9b5b4b511df8705d5f98`, SHA-256 `8185afc77fd34a599094e9f93b293a5afac61f4184ec5c5a02b81ee3c0b0053c`.

### Selected-result context

At the pinned base, `certificates/selected-result.json` points to review `docs/research/community-batch1099-review.md` (SHA-256 `7e76d2c38e5fce30587835b7251df1430488ae4dd372611ef69a3f03f476b6cb`), source manifest `research/community-frontier1094-audit/SELECTED-SOURCE.json` (SHA-256 `79b3de5db3dbcb9829789ba58e9e45758926031e2a7d80667a08429d369be53b`), certificate `research/community-frontier1094-audit/ASSEMBLY.json` (SHA-256 `1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045`), and full reproduction command `make frontier1094-verify`. `make selected-record-check` and the selected binding baseline pass in this cycle; the full cold replay was not run here and is not evidence for this E6 result.

Predecessor attribution: DreamingOfClouds' #1590/#2111/#2125 root-unit decoder work and the inherited #446/#595 cost model. Prepared for Adam Gall with substantial OpenAI Codex assistance. No independent human review is claimed. Apache-2.0.

Prepared for Adam Gall with substantial OpenAI Codex assistance. No independent human review is claimed. Apache-2.0.

## Open next questions

- Can an E6 T=4 decoder outside the image of `R` meet a 21–23 cost window? This would test the main omitted decoder family. First name a support alphabet and screen its exact minimum B0 F2 tariff. Arbitrary rational factors are outside the present linear system.
- Does another admissible E6 pairing admit a rank-at-most-four root-coordinate form? The current equations use only B0; a new pairing needs its own exact mask and constraint matrix.
