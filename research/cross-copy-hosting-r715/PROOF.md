# Cross-copy idle-axis hosting on #472's R715 eleven-stage word

The cross-copy slot of #448 (`research/cross-copy-hosting`, PROOF.md §2 and §7, `toy_two_family_check.py`) applied to
#472's suppliers. Nothing in #472's bit construction changes except where helper residuals live: its R715 local word,
109-pivot kernel (entrance rank 120), 56 target mixes, retimings, residual isometries, eleven-stage schedule (K = 5,
m = 78), eight replicas and bridges are byte-identical. The complex supplier is #448's cross-copy hosted #433 word.

## 1. What changes

#472 hosts every one of the 62,920 helper residual occurrences whole on one idle data family, pooling the eight
replicas (an owner may be in another replica). Residual widths are 8 − e (606 of width 8, 98 of width 7, 11 of width 6
per replica), the children have ranks 7, 14, 28, 42 and 56, so copies are left partly empty and paid as remainder
children: #472's bit profile carries remainders of rank 6, 7, 28 and 56.

Here the pending sets of a child's 2V·T = 1,920 pooled copies are concatenated into one tape and residuals are laid
along it widest first; a residual that straddles a copy boundary is owned by two copies of the same child. Both
copies share the child's window, so #442's lemma applies to each piece and #448 §2 gives the complete-program
identity family by family (the exact finite check of §7 covers the two-family case in the model of #451's note).
The remainder of every copy is exact, and concave costs make the contiguous fill optimal: filled copies pay nothing,
and the unfilled copies of the rank-56 final children pay the whole child.

## 2. Accounting

- Paid profile: the local word's climbs and copies, plus every nonzero copy remainder, once per copy (the template
  pools replicas, as #472 does). Deficit (2KV − 72L)·T = 3,264 is unchanged.
- Physical prefix bound: #472's chronological norm bound is recomputed on the new owners; a split owner's two
  families both receive the update (the bound is monotone in that choice). 1,161 bits, charged 1,216. This treatment of a
  split owner in the chronological norm bound is new here and is a review point of its own.
- Finite invoice: #472's eleven-stage invoice (three-level halving, max child 56, complete row bound 19,431 < 20,161)
  with one further route factor per helper selector for the split (three extra instead of #472's two). The complex
  invoice is #448's (#442's formulas with the hosted stock).
- The integer programme (`tape_core.solve`, frozen in `SELECTION.json`) maximises Σ ln(m/r)·(hosted coordinates);
  the generator completes any residual the solver leaves out on an in-window child with room.

## 3. Checks

`audit_split11.py` shares no code with the generators: windows re-derived from the schedule; every residual has
exactly one owner record; pieces on copies of the named child, inside the pending set, widths summing to the residual
width, disjoint per (child, copy), inside the window, off the active pair; owner families recomputed from the piece
copies; the unchanged parts of the template byte-identical to #472's; remainders, profile, live stock, deficit, the
emitted-program digest and the physical prefix bits recomputed; fifteen mutation controls rejected.
`assemble_split11.py` runs both rational moment engines per supplier, both finite invoices, six bootstrap levels and
the 47 strict outer inequalities; the next grid point and the zero-η, zero-β, unit-β controls are rejected.

## 4. Result

| | #472 | this package |
| --- | ---: | ---: |
| bit live / physical | 9,600 / 9,609 | 9,600 / 9,609 |
| hosted residuals (split) | 62,920 (0) | 62,920 (14,612) |
| bit saving c | 1.293771·10⁻³ | **1.374423·10⁻³** |
| complex saving b | 1.297204·10⁻³ (#458) | 1.437532·10⁻³ (#448) |
| κ | 1.292100·10⁻³ | **1.372550·10⁻³** |

κ = 1372550159367980/10¹⁸ ≈ 1.37255·10⁻³, bit-bound, +6.23 % over #472 and +1.63 % over #469.

## 5. Scope

Conditional like its parents. The review point is the cross-copy slot of #448 (a residual's physical slot in two
data families of one idle child), on which #450, #453, #464 and #469 also rest; #451's trace note and the reply on
that thread describe the disagreement. #472's own review points (R715 word, kernel, mixing, pooled whole hosting,
eleven-stage row bound) and all inherited interfaces remain assumptions. No Lean proof and no unconditional
integer-multiplication theorem is claimed.
