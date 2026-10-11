# Idle-axis hosting: helper residuals on pending idle coordinates

This package changes only the global nine-stage templates of #434's two suppliers. Both local words are unchanged:

- the complex word is #433's split-centre word, R = 560, m = 73;
- the bit word is #434's early-reset kernel word, R = 747, m = 64.

So are their local programs, scalar replays, data routes, bridges, terminal exchange and cover correction. What
changes is where whole dirty-helper residuals live. Many of them move from bank streams onto coordinates of *idle*
data families that would otherwise be advanced later by an idle child.

## 1. The two inherited facts used

**(a) Dirty invocations act on a helper stream as its residual.** The complete dirty local invocation is block
diagonal on helpers at its endpoint and admits arbitrary correlated helper values (#425/#433, #386/#434). On the
physical stream that owns a helper residual of width w, it acts as an exact coordinate factor on w coordinates:

- complex: P_g C_block P_g⁻¹ (PR425-COMPLEX §5, INHERITED-COMPLEX-GEOMETRY);
- bit: D_P with P the width-w coordinate projector (PR386-BIT-GEOMETRY; mixed widths 8 − entrance rank, #434).

This holds whatever the stream held before. Banks rely on exactly this: eight sequential residuals and a pad tile a
bank stream.

**(b) An idle child is a product of coordinate factors.** Advancing a data pair from level a to level b applies, on
every physical data stream (F, g) of that pair, the commuting product of coordinate factors on its pending set S:

- complex: C over S, in the basis U_q ⊕ I used by the inherited idle factorisation;
- bit: D_{P_V−P_U}, an orthogonal coordinate projector difference.

Factors on disjoint coordinate sets commute and multiply:

- complex: C_{S'}·C_{S∖S'} = C_S;
- bit: D_{P'}·D_{P−P'} = D_P for P' ≤ P (the parent's identity D_I·D_P = D_{I−P}).

## 2. Hosting lemma

Fix a data family F (replica r, pair j, side, port) and an idle child Γ that advances pair j at recipe position τ.
Let λ be the position of the last local invocation or bridge that names pair j before τ; idle children do not
count as touches, since they act on other coordinates or on the other member. Let ι be any local invocation with
λ < ι < τ. Then:

1. ι is an invocation on another pair, and nothing touches F between ι and τ.
2. A helper residual of ι, of width w, may be owned by stream (F, d·σ⁻¹) instead of a bank slot. Here d is the
   invocation's cover class, and σ is a coordinate isometry carrying the local residual block onto a set S' ⊂ S of
   w pending coordinates. When S' meets the local block of a level −1 advance, σ is composed with U_q ⊕ I.
3. Γ is replaced by Γ' acting on S ∖ ⋃S' over all hosted residuals of F, which have pairwise disjoint S'.

The complete program's operator is unchanged:

- By (a), ι applies exactly the factor on S' to (F, d·σ⁻¹), for any prior contents.
- Nothing else acts on F between ι and τ, so this factor may be moved to τ.
- By (b), the moved factors times Γ' equal Γ.

Distinct slots of one invocation have distinct σ, so distinct physical classes for every d. They are also disjoint
from the invocation's own data owners, because pair j is not active, and from bank owners, because the families
differ. Residuals of different invocations on F occupy disjoint coordinates. They are sequential, exactly as the
parent's banks are co-owned sequentially by different cover classes.

Two further points:

- **Phases.** The stored Z₄ translations after Γ remain valid, because Γ'·∏(hosted factors) = Γ as exact operators.
  The final X_δ(g) correction still applies to every live family; hosting changes no data endpoint.
- **Reflection.** The inverse-transpose program reverses chronology and reflects each factor. The window condition
  (no touch strictly between ι and τ) is symmetric, so hosting commutes with reflection.

## 3. What is checked here

- `bit_hosted.py` and `complex_hosted.py` read #434's freshly regenerated templates and compute windows from each
  recipe. They apply a frozen integer-programme selection (`SELECTION.json`; `--discover` recomputes it with scipy)
  and emit new owners, remainder children and banks.
  - Bit: unhosted residuals keep an exact width-64 tiling with no padding.
  - Complex: eight per bank plus one paid pad; a final partial bank pays the larger pad.
- `audit.py` shares no code with the generators. It re-derives every window from the template schedule. For every
  replica and invocation it checks that:
  - each helper has exactly one owner;
  - each hosted slot is inside its child's pending set, disjoint from other slots, outside the active pair, and in
    window;
  - every remainder child is exact, and the bank tiling is exact.

  It also recomputes the paid profile and the rank deficit 2496, and rejects nine mutations.
- `assemble.py` prices both suppliers with the two inherited rational moment engines and recomputes both finite
  invoices with the hosted stock. Route charging is conservative: two extra route factors per helper selector, and
  the parent's larger complex per-vertex bill is kept. It then runs #434's strict outer assembly: six bootstrap
  levels and 47 inequalities. The next grid point and the zero-η, zero-β and unit-β controls are rejected.

## 4. Result

| | live stock | max child | hosted residuals | certified saving |
| --- | ---: | ---: | ---: | --- |
| bit | 14,259 → 9,457 | 42 → 8 | 39,568 of 53,784 | c = 1239085165241180038597/10²⁴ |
| complex | 12,720 → 8,400 | 48 → 8 | 34,560 of 40,320 | b = 1267453159029119/10¹⁸ |

κ = 618775866623647/(5·10¹⁷) ≈ 1.237551733247294·10⁻³, bit-bound, +9.218% over #434.

## 5. Scope

This is a written finite extension of the inherited correlated dirty-bank and compressed-window interfaces. The
streams that own residuals now include data streams during idle windows. It is the principal new review point.

All other interfaces remain inherited assumptions: the all-size compiler, restored-work, tape/common-grid, precision
and analytic interfaces.

No Lean proof and no unconditional integer-multiplication theorem is claimed. The global operator identity is argued
from (a) and (b) and checked combinatorially. It is not replayed numerically on the 2⁷³- and 2⁶⁴-point address
spaces; neither parent does that either.
