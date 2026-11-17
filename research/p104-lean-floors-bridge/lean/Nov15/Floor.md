# Floor.lean: class-K junk floor lemmas (FANOUT F1, F2, F3-cert, F4; RANKSTEINER R0(b,c), R1, R2, R3, R4-cert). No sorry, ~6 s, 2.0 GB RSS
Lane LEAN-NEXT6, Nov 16. Sources: cards/WILD/BIG/FANOUT/THEORY.md, cards/WILD/BIG/RANKSTEINER/THEORY.md.
Self-contained, namespace Floor. Axioms (11 printed): [propext, Classical.choice, Quot.sound]. Any field K.

**Stay floor at one chart (§2).** Rows in `ι → K`, ρ linear. `S` = span of rows ever at c; `Tok` = registers whose own token is held at c and killed by ρ (he class-N helper enders + hb helper births), |Tok| = he + hb.
- `stay_floor`: any set X ⊆ S has rank ρ(X) ≤ hd + ka + oa + kb. Core: `finrank_map_add_le` (dim ρA + dim T ≤ dim S for A, T ≤ S, T ⊆ ker ρ) and `finrank_tokens` (distinct tokens are independent).
- `R1_local_rank`: hd ≥ rank(ρK_c + ρR(c)) − ka − oa − kb (X = K_c ∪ R(c)).
- `F2_count` (= R0(c)): hd ≥ a_H − slr with a_H, slr in the ρ-form (X = K_c ∪ HelpArr_c).
- `hop_count`: helper arrivals b_1..b_m held at c whose ρ-rows are independent mod ρK_c + ρR(c) give hd ≥ rank(ρK + ρR) − ka − oa − kb + m. R = ∅: F3's #hops(c) ≤ hd + slr. Type-A hops: R3's hd ≥ needR + #A-hops.
- `indepMod_of_proj`: FANOUT's π-form. If π = π'∘ρ and π'(ρK_c) ⊆ KA_c, then π-independence mod KA_c gives ρ-independence mod ρK_c (the "apply π" step of F2).
- Hypotheses (from the op model, not re-proved here): `hent` dim S_c ≤ hd + he + ka + oa + hb + kb. This is ExportLaw.forward_span + entry count + hOnce (one entry per public register; exact on #7623, EXPORTLAW/lean5/once.py). K_c, R(c), HelpArr_c, Tok ⊆ S_c. ρ kills Tok.

**Descent (§3).** Charts C: a partial order, well-founded (finite). `P c` = π(S_c) (ρ(S_c) for R2), `KA c` = the kept part, `HB c` = fixed helper arrivals at c with `tail`, `vec`.
- `F1_descent`. Hypotheses:
  - `hP`: P(c) ⊆ KA_c + span vec(HB_c). This is the forward span law plus the choice of HB_c as a spanning set mod KA_c.
  - `hvec`: vec b ∈ P(tail b) and tail b < c (helper moves strictly ascend; [C] FANOUT).
  - If φ kills KA_t and φ(v) ≠ 0 for some v ∈ P(t), there is a φ-source s and a first hop b ∈ HB_{c₁} with tail s and φ(vec b) ≠ 0, plus a ReflTransGen chain of φ-visible hops c₁ → … → t. So s < c₁ ≤ t.
  - Independence of HB_c is NOT needed for the descent, only spanning. Independence is used only in the count (`hop_count`).
- `R0b`: P(c) ⊆ ⨆_{c' ≤ c} KA_{c'}.
- `exists_sep` + `F4_single_source` (also R2 in ρ). If φ kills KA_t and every KA_{s'} with s' < t, s' ≠ s, the first hop leaves s itself.

**R3 (§4).**
- `tri_indepMod`: triangular functionals give independence mod M. Uses a maximal element of {s_j : β_j ≠ 0} in the partial order. The prose's "largest dim" works too, but is not needed.
- `R3_indep` hypotheses:
  - distinct sources s_j;
  - ψ_j kills Kρ_{c'} for c' ≤ t_j, c' ≠ s_j (R2's W);
  - s_j < c ≤ t_j, ψ_j(b_j) ≠ 0;
  - b_j ∈ ⨆_{c' ≤ s_j} Kρ_{c'} (R0b);
  - for type A, ψ_j kills R.
  - Conclusion: IndepMod (Kρ_c ⊔ R) b. Feed it to `hop_count`.

**LP certificate (§5).** `weak_duality`: min cᵀx, Ax ≥ b, x ≥ 0. Then y ≥ 0 with yᵀA ≤ c gives bᵀy ≤ cᵀx (any linearly ordered field).
- `floor_of_certificate`: κ ≥ 0, the native objective ≤ Σ hd, and cost ≥ κ Σ hd give cost ≥ κ·bᵀy.
- The LP rows (F3 / R4) and the dual vector stay data: lp2.py and rslp.py check them in Fractions.

**Still prose / data:**
- the native-feasibility map (hop ↦ z/a/x variables, non-Nat hops ↦ fresh minimal heads, objective ≤ Σ hd);
- the exact LP data and the type-A flags (rslp.py);
- "each paid stay costs ≥ κ" (JunkLB2 `T4_stop_cost`);
- the ρ-replay being exact;
- summing over charts (distinct stays);
- HB_c existence as a basis (only spanning is used in F1, only independence in the count; a basis gives both).
- JunkT5's chain-existence step is the F1 pattern (coordinate φ, root chart as t). It is not wired into JunkT5.lean.

**Findings.** No statement found false. Two over-strong prose steps:
- (1) F2's "π K^ρ_c = KA_c" is only needed as ⊆. Equality needs the token finals of kept non-Y enders at c to have π in KA_c. That holds when no live X ends below V; it was not checked here.
- (2) R3 needs only a partial order, not ordering by dimension.

**Update (LEAN-NEXT7, Nov 16).**
- `hent` is now derived from ExportLaw + hOnce: FloorGlue.entry_count / chart_floor.
- Summing over charts with distinct stays is formal: FloorGlue.sum_chart_floors / global_floor_*.
- JunkT5's chain-existence step is wired: JunkT5Descent.descent_chain.
- What stays checked input: the LP rows plus the native-feasibility map, and the dual vector.
