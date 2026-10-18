# Label-field census: certified ceilings for rank-k E8 units (no κ claim)

Rohan Guliani (@Rohansguliani), 2026-10-13. Apache-2.0. Prepared with substantial AI assistance (Mux agent). The tables use the rational-interval roots of `research/format-limits-corrected`.
Decimal displays are approximations; the exact upper endpoints are in `RESULT.json`.
This is a historical 2026-10-13 experiment, restricted to odd stage counts 3 through 13.
Extension-field interpretations require the proposed rank-scaling and pairing hypotheses; no supplier is constructed.

**This package makes no κ claim and ships no word.** It turns the copy-cost floors reported for E8 over other label
fields into conditional B_K format ceilings. From those ceilings it states which decoder cost each unit would need.

## Prior and concurrent work (read first)

- GamingPuzzled / Joel Pulikkan, #620: the extension-ring screen of Gaussian, Eisenstein and Hurwitz E8 units.
- Hurwitz: #703 (Mister-Meeseeks) proves the asymmetric copy cost is exactly 10 on the 10 quaternionic lines; #785
  covers fixed-support nonlinear messages.
- Gaussian: #738 (Sagar Thakrar) proves floor 40 on the 60 lines and excludes three stages. #770 shows 40 is
  optimal among weighted maximal-clique certificates. #767 adds planar and incidence decoder obstructions.
- Eisenstein: #798 (jonathanlam) proves cost ≥ 22 for any finite set of scalar binary totals. It also shows 22 is the
  limit of the clique method, so the true optimum lies in [22, 40].
- Rational E8: #765 shows tensor basis mixing cannot lower the copy rank 72^d.
- The format ceiling a ≤ X(s, h/k, x/k): research/format-limits-corrected, building on DreamingOfClouds' #446
  Theorems B and C.

This package does not re-prove any of those floors. It adds the conversion to certified ceilings, a common table, and
an argued complex-side window bound.

## Two observations

1. **Historical outer conversion.** At the submission checkpoint, the binding supplier had
   a = 65528268492323474503/(4·10²²), and the selected κ was
   51110230636731/31250000000000000. They nearly saturate a/(1+a) in the stated assembly.
   Holding that supplier and assembly fixed leaves little parameter headroom. This is not
   a restriction on other multiplication algorithms, rings, transforms or recursive interfaces.
2. **A richer label field halves or quarters w, but raises the copy cost.** The Eisenstein and Hurwitz E8 are rank-2
   and rank-4 rational labels in the same 8-dimensional window. So w = 4 or 2 instead of 8, and the proposed ceiling depends on
   the copy cost per port x/k, conditional on a compatible field-to-rational and residue-field realization.

## Results (certified roots, maximised over odd s ≤ 13)

**Copy cost to ceiling.** Here x = cost / v. The Eisenstein window is n = 4 Q(ω)-dimensions; the Gaussian window is
n = 4; the Hurwitz window is n = 2.

| unit | copy cost | source of the cost | bit-side ceiling X |
|---|---:|---|---|
| Eisenstein, 40 lines | 22 | scalar-total model floor (#798) | ≈ 1.496·10⁻² (s = 3) |
| | 23 | | ≈ 1.295·10⁻² |
| | **24** | | **≈ 1.150·10⁻²: largest cost with X > 1/99** |
| | 25 | | ≈ 1.0053·10⁻² < 1/99 |
| | 26 | | ≈ 8.61·10⁻³ |
| | 28 | coordinate-total lower bound (this census) | ≈ 6.335·10⁻³ |
| | 29 | | ≈ 5.32·10⁻³: below the P111 format ceiling (6.000·10⁻³) |
| | ≥ 37 | | no positive saving for s ≤ 13 |
| Gaussian, 60 lines | 40 | floor (#738) | ≈ 7.688·10⁻³ (s = 7) |
| Hurwitz, 10 lines | 10 | exact (#703) | no positive saving for s ≤ 13 (x = 1) |

`RESULT.json` lists every cost from 22 to 40. For calibration, the same engine gives 6.000·10⁻³ for the submitted bit
unit (h = 8, x = 63/111) and 5.186·10⁻³ for the submitted complex unit (h = 9, x = 64/112).

**Rational and field configurations with coordinate-total decoders.** The quantity x_lb is the sum of the support
cliques divided by v.

| configuration | field, k | v | n | ω | support cliques | x_lb | ceiling X |
|---|---|---:|---:|---:|---|---|---|
| E8, Hamming frame | Q, 1 | 120 | 8 | 8 | 8 × 8 | 8/15 | ≈ 8.009·10⁻³ |
| E7 | Q, 1 | 63 | 7 | 7 | 7 × 7 | 7/9 | ≈ 1.847·10⁻³ |
| D4 | Q, 1 | 12 | 4 | 3 | 4 × 3 | 1 | none (s ≤ 13) |
| F4 | Q, 1 | 24 | 4 | 5 | 4 × 5 | 5/6 | ≈ 2.155·10⁻³ |
| Eisenstein E8 (Witting) | Q(ω), 2 | 40 | 4 | 7 | 4 × 7 | 7/10 | ≈ 6.335·10⁻³ |
| Hurwitz E8 | H, 4 | 10 | 2 | 5 | 2 × 5 | 1 | none (s ≤ 13) |

Why x_lb is a lower bound: with coordinate totals, N_TS ≠ 0 exactly on non-orthogonal pairs. B_TT = 1 and B_TS = 0
there force B[K, K] = I on every clique K inside a total, so each total costs at least its largest support clique. The
Eisenstein value 28 sits inside #798's open interval [22, 40]. For these coordinate-total decoders and stage counts, the conditional ceiling
is below 1/99. Other decoders would be necessary to reach cost ≤ 24; they are not supplied here.

## Conditional implications for κ > 0.01

- **Bit pricing.** Within the tested stages and field-rank interpretation, costs 22–24
  leave a ceiling above 1/99; costs at least 25 do not. A ceiling above the target
  is only remaining headroom, not an achievable saving or a network construction.
- **Complex-side proposal.** If the relevant pairing has a 7 × 7 identity block
  over the proposed residue field, its rank is at least seven. Applying the same
  format formula additionally requires a valid complex-window realization and
  the stated rank/cost conversion. Under those hypotheses, window seven and cost
  22/40 or 24/40 give upper endpoints below 0.00807 and 0.00598 respectively
  for the tested stages. These two rows are separately checked in the maintainer
  review; the original `census.py` instead records the cost-28/40 calibration.
- **Scope.** Under those additional hypotheses, this tested family cannot reach
  κ > 0.01. Stage counts at least 15, other field implementations and different
  recursive contracts remain outside this calculation. A higher upper ceiling
  does not establish an improvement over any implemented supplier.

## Scope and verification

- **Rays.** The Witting rays are generated in Z[ω]⁴. The script asserts Hermitian norm 3 and |⟨u, w⟩|² ∈ {0, 3}, and
  each ray is orthogonal to exactly 12 others. The Hurwitz lines are H(1,0), H(0,1) and H(1, y) for y ∈ {±1, ±i, ±j, ±k}.
- **Exact computation.** Cliques are found by exhaustive search (`e8units.first_clique`). Ceilings are rational-interval
  roots from the unchanged `skel.X`.
- **Not checked here:**
  - Stage counts s ≥ 15. Rows marked "none" or with a best s at 13 could change there.
  - Decoders other than coordinate totals in the x_lb table.
  - Whether the bit contract's rational shears, residue-field ranks and complex phase frames admit the proposed Q(ω) or quaternionic realizations.
  - Helper, hosting, compiler and analytic obligations. The ceilings are upper bounds, and realised words sit 2.5–2.7×
    below them (format-limits §A.5).

```sh
python3 -B research/label-field-census/census.py --json /tmp/label-field-census.json
# compare with research/label-field-census/RESULT.json (about 4 minutes; numpy only)
```

## Open next questions

- Extend or bound the stage-count tail, beginning at s = 15; the current census
  cannot support an all-stage exclusion.
- Prove the field-to-rational and residue-field rank conversion for a concrete
  legal circuit before treating the extension-field price as a supplier bound.
- Seek a non-coordinate Eisenstein decoder, then price its full helper and
  restoration obligations. Passing a ceiling screen alone is not a positive result.
