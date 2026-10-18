# Label-field census: certified ceilings for rank-k E8 units (no κ claim)

Rohan Guliani (@Rohansguliani), 2026-10-13. Apache-2.0. Prepared with substantial AI assistance (Mux agent). Every
number below is printed by `census.py`, using the certified roots of `research/format-limits-corrected`.

**This package makes no κ claim and ships no word.** It turns the copy-cost floors proved for E8 over other label
fields into certified B_K format ceilings. From those ceilings it states which decoder cost each unit would need.

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

1. **The outer assembly is saturated.** With the binding complex supplier a = 65528268492323474503/4·10²², the exact
   value a/(1+a) equals the selected κ = 51110230636731/31250000000000000 to a relative 1.4·10⁻¹⁶.
   a/(1+a) is the balance of `min(1−ε, εq)` ([assembly-domain audit](../../docs/research/assembly-domain-audit.md)).
   Ring, transform length, Gaussian resampling, and Fürer / Schönhage–Strassen / Harvey–van der Hoeven changes act only
   through this conversion. They can raise κ by at most a factor 1+a ≈ 1.0016. A meaningful factor must come from the
   supplier saving a, which the B_K format caps through the unit's (w = h/k, x/k).
2. **A richer label field halves or quarters w, but raises the copy cost.** The Eisenstein and Hurwitz E8 are rank-2
   and rank-4 rational labels in the same 8-dimensional window. So w = 4 or 2 instead of 8, and the ceiling depends on
   how much the copy cost per port x/k rises.

## Results (certified roots, maximised over odd s ≤ 13)

**Copy cost to ceiling.** Here x = cost / v. The Eisenstein window is n = 4 Q(ω)-dimensions; the Gaussian window is
n = 4; the Hurwitz window is n = 2.

| unit | copy cost | source of the cost | bit-side ceiling X |
|---|---:|---|---|
| Eisenstein, 40 lines | 22 | lower bound for any decoder (#798) | ≤ 1.496·10⁻² (s = 3) |
| | 23 | | ≤ 1.295·10⁻² |
| | **24** | | **≤ 1.150·10⁻²: largest cost with X > 1/99** |
| | 25 | | ≤ 1.0053·10⁻² < 1/99 |
| | 26 | | ≤ 8.61·10⁻³ |
| | 28 | coordinate-total lower bound (this census) | ≤ 6.335·10⁻³ |
| | 29 | | ≤ 5.32·10⁻³: below the realised bit unit (6.000·10⁻³) |
| | ≥ 37 | | no positive saving for s ≤ 13 |
| Gaussian, 60 lines | 40 | floor (#738) | ≤ 7.688·10⁻³ (s = 7) |
| Hurwitz, 10 lines | 10 | exact (#703) | no positive saving for s ≤ 13 (x = 1) |

`RESULT.json` lists every cost from 22 to 40. For calibration, the same engine gives 6.000·10⁻³ for the realised bit
unit (h = 8, x = 63/111) and 5.186·10⁻³ for the realised complex unit (h = 9, x = 64/112).

**Rational and field configurations with coordinate-total decoders.** The quantity x_lb is the sum of the support
cliques divided by v.

| configuration | field, k | v | n | ω | support cliques | x_lb | ceiling X |
|---|---|---:|---:|---:|---|---|---|
| E8, Hamming frame | Q, 1 | 120 | 8 | 8 | 8 × 8 | 8/15 | ≤ 8.009·10⁻³ |
| E7 | Q, 1 | 63 | 7 | 7 | 7 × 7 | 7/9 | ≤ 1.847·10⁻³ |
| D4 | Q, 1 | 12 | 4 | 3 | 4 × 3 | 1 | none (s ≤ 13) |
| F4 | Q, 1 | 24 | 4 | 5 | 4 × 5 | 5/6 | ≤ 2.155·10⁻³ |
| Eisenstein E8 (Witting) | Q(ω), 2 | 40 | 4 | 7 | 4 × 7 | 7/10 | ≤ 6.335·10⁻³ |
| Hurwitz E8 | H, 4 | 10 | 2 | 5 | 2 × 5 | 1 | none (s ≤ 13) |

Why x_lb is a lower bound: with coordinate totals, N_TS ≠ 0 exactly on non-orthogonal pairs. B_TT = 1 and B_TS = 0
there force B[K, K] = I on every clique K inside a total, so each total costs at least its largest support clique. The
Eisenstein value 28 sits inside #798's open interval [22, 40]. So **coordinate-total decoders are excluded from the
range that would matter**, and only other decoders could reach cost ≤ 24.

## What this means for κ > 0.01

- **Bit side.** An Eisenstein decoder of cost ≤ 24 would give a bit-side ceiling above 1/99. A decoder of cost ≤ 28
  would still beat the realised E8 bit unit. Whether such a decoder exists is #798's open question; the clique method
  cannot settle it.
- **Complex side (argued, not proved here).** Let the complex unit's window be the residue-field rank of the pairing B,
  as for E8, where the F₂ window is 9 and the clique is 8. Then an Eisenstein complex unit has an F₄ window of at least
  ω = 7, because a 7-clique forces a 7 × 7 identity block. At window 7 the certified ceiling is ≤ 8.07·10⁻³ even at
  cost 22, and ≤ 5.98·10⁻³ at cost 24. Keeping the current complex unit instead caps the ceiling at 5.19·10⁻³.
- **Outcome.** Since κ ≤ min(bit, complex), **the label-field change cannot reach κ > 0.01 in the B_K format.** This
  holds even if #798's open interval resolves at its lower end. The change could still raise the ceiling several-fold
  above today's frontier, if a cost ≤ 24 Eisenstein bit decoder exists and the Q(ω) frames carry over.

## Scope and verification

- **Rays.** The Witting rays are generated in Z[ω]⁴. The script asserts Hermitian norm 3 and |⟨u, w⟩|² ∈ {0, 3}, and
  each ray is orthogonal to exactly 12 others. The Hurwitz lines are H(1,0), H(0,1) and H(1, y) for y ∈ {±1, ±i, ±j, ±k}.
- **Exact computation.** Cliques are found by exhaustive search (`e8units.first_clique`). Ceilings are rational-interval
  roots from the unchanged `skel.X`.
- **Not checked here:**
  - Stage counts s ≥ 15. Rows marked "none" or with a best s at 13 could change there.
  - Decoders other than coordinate totals in the x_lb table.
  - Whether the bit contract's rational shears and the complex phase frames can be realised over Q(ω).
  - Helper, hosting, compiler and analytic obligations. The ceilings are upper bounds, and realised words sit 2.5–2.7×
    below them (format-limits §A.5).

```sh
python3 -B research/label-field-census/census.py --json /tmp/label-field-census.json
# compare with research/label-field-census/RESULT.json (about 4 minutes; numpy only)
```
