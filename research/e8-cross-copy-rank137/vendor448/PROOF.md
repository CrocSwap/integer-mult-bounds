# Cross-copy idle-axis hosting: one residual on two copies of one idle child

This package changes only the global nine-stage templates of #442's two suppliers, which are #434's two suppliers:

- the complex word is #433's split-centre word, R = 560, m = 73;
- the bit word is #434's early-reset kernel word, R = 747, m = 64.

Local programs, scalar replays, data routes, bridges, terminal exchange and cover correction are unchanged. The idle
windows are #442's. What changes is the shape of a hosted slot: a residual may be laid across the pending coordinates
of two copies of the same idle child.

## 1. The waste in whole-residual hosting

An idle child advancing pair j by rank r acts on every copy (side, port) of that pair: 2V = 240 data families on the
bit side, V = 120 ports per side on the complex side, each with r pending coordinates and all with the same window.
#442 places whole residuals inside one copy's pending set. Bit residuals have width 8 − e (entrance rank e ∈ {0, 1, 4};
637 of width 8, 104 of width 7, 6 of width 4), complex residuals have width 9, while the children have ranks
7, 14, 28, 42 (bit) and 8, 16, 32, 48 (complex). A rank-7 child cannot hold a width-8 residual at all, a rank-14 child
holds one and wastes six coordinates, and so on. On the bit side 6,944 of the 45,360 pending coordinates per replica
stay idle and are paid as remainder children; on the complex side 5,760 of 51,840.

## 2. The extension

Fix an idle child Γ of pair j at recipe position τ, and two copies (F₁, g₁), (F₂, g₂) of pair j: two data families with
pending sets S₁ and S₂ of Γ. Let ι be a local invocation inside the window of Γ (the same window for every copy of the
pair: the window condition of #442 §2 names only the pair, the invocation and the child). Let a helper residual of ι
have width w = w₁ + w₂ with w₁, w₂ > 0.

Claim: the residual may be owned by (F₁, d·σ₁⁻¹) on w₁ coordinates S₁' ⊂ S₁ and by (F₂, d·σ₂⁻¹) on w₂ coordinates
S₂' ⊂ S₂, with Γ replaced on F₁ by its factor on S₁ ∖ S₁' and on F₂ by its factor on S₂ ∖ S₂', and the complete
program's operator is unchanged.

Proof, from #442's two inherited facts.

- Fact (a): on the physical coordinates that carry the residual, the dirty invocation ι acts as the coordinate factor
  D_P (bit) or P_g C_block P_g⁻¹ (complex) on those w coordinates, independent of their contents. With P = P₁ + P₂ an
  orthogonal sum of the projectors onto S₁' and S₂', the identity D_{P₁}·D_{P₂} = D_P (the parent's D_{P'}·D_{P−P'} = D_P)
  writes the action as the product of a factor on S₁' and a factor on S₂'. On the complex side the block is the same
  commuting product over coordinates that #442 §1(b) already uses. The two factors act on different families, so they
  commute with everything acting on the other family.
- Window: nothing touches F₁ or F₂ strictly between ι and τ, because both are copies of pair j and the window is a
  property of pair j. So, exactly as in #442 §2, the factor on S₁' is moved to τ on F₁ and the factor on S₂' is moved to
  τ on F₂, independently.
- Fact (b): at τ, Γ on F₁ is the commuting product of coordinate factors on S₁; the moved factor on S₁' times the
  remainder factor on S₁ ∖ S₁' is Γ's factor on F₁. The same on F₂.

The residual's coordinate isometry σ now carries the local residual block onto S₁' ⊔ S₂' inside two families of the
same replica. It is still an elementary coordinate permutation of the address space; the finite invoice charges one
further route factor per helper selector for it (three extra factors instead of #442's two). Phases and reflection are
as in #442 §2: Γ'·(hosted factors) = Γ as exact operators on every family, and the window condition is symmetric.

Residuals of different invocations hosted on the same copy occupy disjoint coordinates and are sequential, as in the
parent. A residual never spans two children and never spans copies of different pairs; the audit rejects both.

## 3. Selection

`tape_core.py` concatenates the pending sets of a child's copies into one tape and solves an integer programme over
the counts n(child, stage, width): maximise Σ ln(m/r)·(hosted coordinates on the child) subject to residual
availability per (stage, width) and, on the bit side, exact width-64 tiling of the leftover (width 7 in eights with one
width 8, width 4 in pairs with seven width 8, width 8 in eights). The frozen choice is `SELECTION.json`; `--discover`
recomputes it with scipy. `expand` lays each child's residuals along the tape widest first; a residual that straddles a
copy boundary becomes a two-piece slot.

## 4. What is checked

- `bit_split.py` and `complex_split.py` read #434's freshly regenerated templates and emit the new owners, remainders
  and banks (bit: exact width-64 tiling, no padding; complex: eight per bank plus one paid pad, final partial bank pays
  the larger pad).
- `audit_split.py` shares no code with the generators. It re-derives every window from the template schedule and, for
  every replica and invocation, checks that every helper has exactly one owner record; that each hosted residual has
  one or two pieces on copies of the child it names, with widths summing to the residual's width, inside the pending
  set, pairwise disjoint per (child, copy), inside the window and off the active pair; that remainder children and bank
  tilings are exact; and it recomputes the profile, live stock and the rank deficit 2496. Twelve mutations are
  rejected, including a split whose pieces sit on two different children and a split whose widths do not sum to the
  residual width.
- `assemble_split.py` is #442's assembly with the extra route factor: two rational moment engines per supplier, fresh
  finite invoices with the new stock, six bootstrap levels and the 47 strict outer inequalities; the next grid point and
  the zero-η, zero-β and unit-β controls are rejected.

## 5. Result

| | live stock | max child | hosted residuals | of which split | certified saving |
| --- | ---: | ---: | ---: | ---: | --- |
| bit, m = 64 | 9,457 → 8,592 | 8 → 24 | 46,160 of 53,784 | 12,496 | c = 66625358964838932161/(5·10²²) ≈ 1.33251·10⁻³ |
| complex, m = 73 | 8,400 → 7,680 | 8 → 48 | 40,320 of 40,320 | 13,720 | b = 718766148669433/(5·10¹⁷) ≈ 1.43753·10⁻³ |

The bit max child 24 is one partial copy of a rank-28 child (eight calls); the complex max child 48 is the 133 copies
per replica of the rank-48 final children that the complex supply (5,040 residuals per replica against 5,760 pending
coordinates of width 9) cannot fill. Both deficits stay 2496.

κ = 1330733966732373/10¹⁸ ≈ 1.330733966732373·10⁻³, bit-bound, +17.44 % over #434 and +7.53 % over #442.

## 6. Scope

This is a written finite extension of #442's hosting interface: a residual's physical slot may lie in two data
families of one idle child. It is the principal new review point. #442's extension (helper residuals on data streams
during idle windows) and all other interfaces remain inherited assumptions: the all-size compiler, correlated
dirty-bank and compressed-window interfaces, restored work, tape/common grid, precision and analytic transfer.

No Lean proof and no unconditional integer-multiplication theorem is claimed. The global operator identity is argued
from the parents' facts (a) and (b) and checked combinatorially, not replayed numerically on the address spaces.
