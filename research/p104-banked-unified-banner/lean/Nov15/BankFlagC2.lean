/-
BankFlagC2 .  
P-BLOCK / P-R1CUT DISCHARGED abstractly from the main contract, WITHOUT the 400-main matrix:
  contract = every row's support is {self, partner π f}, partner in-degree 1, partner coefficient O e (π e) ≠ 0
  .
  Extra pair e at a cut P (P := D_j for the OUT side, P := {d_j = 1} for IN / the R1 cut): A e ∉ P, B e ∉ P,
  A(π e), B(π e) ∈ P.  Then the cross submatrix R = C ∪ E, S = C ∪ π E is block triangular
  (O[C, π E] = 0 by in-degree 1), so the extras need only the partner coefficients ≠ 0, not the N-clique structure.
  cut_extras: #banks crossing P→P^c ≥ |C| + |E|  (C ⊆ crossing fields with nonzero principal minor).
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.BankFlagC

namespace BankFlagC
open Finset Submodule BankNC0

variable {K : Type} {Chart Fld Bank : Type} [Field K] [Fintype Fld] [DecidableEq Fld]
  [Fintype Bank] [LinearOrder Bank]

theorem cut_extras (N : Net K Chart Fld Bank) (P : Chart → Prop) [DecidablePred P]
    (C E : Finset Fld) (π : Fld → Fld)
    (hC : ∀ c ∈ C, P (N.A c) ∧ ¬ P (N.B c))
    (hdetC : (Matrix.of (fun (r : C) (s : C) => N.O r s)).det ≠ 0)
    (hE : ∀ e ∈ E, ¬ P (N.A e) ∧ ¬ P (N.B e))
    (hπ : ∀ e ∈ E, P (N.A (π e)) ∧ P (N.B (π e)))
    (hnz : ∀ e ∈ E, N.O e (π e) ≠ 0)
    (hsupp : ∀ f g, N.O f g ≠ 0 → g = f ∨ g = π f)
    (hinj : ∀ e ∈ E, ∀ r ∈ C ∪ E, π r = π e → r = e) :
    C.card + E.card ≤ (Finset.univ.filter (fun k => P (N.src k) ∧ ¬ P (N.dst k))).card := by
  classical
  have hdisj : Disjoint C E := by
    rw [Finset.disjoint_left]; intro x hx hxE; exact (hE x hxE).1 (hC x hx).1
  have hcard : (C ∪ E).card = C.card + E.card := Finset.card_union_of_disjoint hdisj
  rw [← hcard]
  -- columns
  have hzero : ∀ e ∈ E, ∀ r ∈ C ∪ E, r ≠ e → N.O r (π e) = 0 := by
    intro e he r hr hre
    by_contra hne
    rcases hsupp r (π e) hne with h | h
    · -- π e = r
      rcases Finset.mem_union.mp hr with hrC | hrE
      · exact (hC r hrC).2 (h ▸ (hπ e he).2)
      · exact (hE r hrE).1 (h ▸ (hπ e he).1)
    · exact hre (hinj e he r hr h.symm)
  apply cut_rank N P (C ∪ E) (C ∪ E.image π)
  · intro r hr
    rcases Finset.mem_union.mp hr with h | h
    · exact (hC r h).2
    · exact (hE r h).2
  · intro s hs
    rcases Finset.mem_union.mp hs with h | h
    · exact (hC s h).1
    · obtain ⟨e, he, rfl⟩ := Finset.mem_image.mp h; exact (hπ e he).1
  · rw [Fintype.linearIndependent_iff]
    intro g hg
    let g' : Fld → K := fun f => if h : f ∈ C ∪ E then g ⟨f, h⟩ else 0
    have hg' : ∀ s ∈ C ∪ E.image π, ∑ r ∈ C ∪ E, g' r * N.O r s = 0 := by
      intro s hs
      have := congrFun hg ⟨s, hs⟩
      simp only [Finset.univ_eq_attach, Pi.add_apply, Finset.sum_apply, Pi.smul_apply,
        smul_eq_mul, Pi.zero_apply] at this
      rw [← Finset.sum_attach (C ∪ E) (fun r => g' r * N.O r s)]
      rw [← this]
      apply Finset.sum_congr rfl
      intro r _
      simp only [g', dif_pos r.2]
    have hE0 : ∀ e ∈ E, g' e = 0 := by
      intro e he
      have h1 := hg' (π e) (Finset.mem_union_right _ (Finset.mem_image_of_mem _ he))
      rw [Finset.sum_eq_single_of_mem e (Finset.mem_union_right _ he)] at h1
      · rcases mul_eq_zero.mp h1 with h | h
        · exact h
        · exact absurd h (hnz e he)
      · intro r hr hre; rw [hzero e he r hr hre, mul_zero]
    have hC0 : ∀ c ∈ C, g' c = 0 := by
      have hli := Matrix.linearIndependent_rows_of_det_ne_zero hdetC
      rw [Fintype.linearIndependent_iff] at hli
      have key := hli (fun c : C => g' c) (by
        funext s
        have h1 := hg' s (Finset.mem_union_left _ s.2)
        have hEz : ∑ r ∈ E, g' r * N.O r s = 0 :=
          Finset.sum_eq_zero (fun e he => by rw [hE0 e he, zero_mul])
        rw [Finset.sum_union hdisj, hEz, add_zero] at h1
        simp only [Finset.univ_eq_attach, Pi.add_apply, Finset.sum_apply, Pi.smul_apply,
          smul_eq_mul, Pi.zero_apply, Matrix.of_apply]
        rw [← Finset.sum_attach C] at h1
        exact h1)
      intro c hc; exact key ⟨c, hc⟩
    intro r
    have hr := r.2
    have : g r = g' r := by simp only [g', dif_pos hr]
    rw [this]
    rcases Finset.mem_union.mp hr with h | h
    · exact hC0 r h
    · exact hE0 r h

end BankFlagC
#print axioms BankFlagC.cut_extras
