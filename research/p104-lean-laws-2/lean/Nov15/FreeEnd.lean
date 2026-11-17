/-
FreeEnd (lane LEAN-NEXT24, Nov 17): FLOOR3 collapse of the free-endpoint relaxation. See FreeEnd.md.
Source: cards/WILD/REBUILDKIT/v2/floor/FLOOR3.md; definitions w0/corr/rho from Nov15.V2Bridge.

* `chD0_eq_sum_w0`: for an ascending MOVE chain a → … → b, D0 (FloorD0.chD0, f = r ln r)
    = Σ_moves w0 θ (dim tail) (dim head) − w0 θ (dim a) (dim b), for EVERY θ (the corr-free bridge identity).
* `chD0_nonneg`: D0 ≥ 0 on every ascending chain.
* `oneMove_D0`: a helper born at L making one MOVE to U (dim L < dim U) has D0 = 0.
* `floor3_collapse`: over any list of pairs with dim L < dim U, the one-move helpers cost 0 in total,
  and 0 is a lower bound for every ascending-chain realisation: relaxation optimum = 0.
* PAPER SLIP (FLOOR3.md / task wording "Σ w0 − corr = 0"): false as written. The identity is
  Σ w0 − w0(d0,e) = D0. With the full `corr = w0 + ρ(d0) − ρ(e)`: Σ w0 − corr = D0 + ρ(e) − ρ(d0)
  (`sum_w0_sub_corr`); for a one-move helper this is ρ(U) − ρ(L), nonzero e.g. θ = 1, 1 → 2: −B1
  (`slip_counterexample`). The collapse itself (D0 = 0) is unaffected.
-/
import Nov15.V2Bridge

open FloorE2E FloorD0 V2Bridge

set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false

namespace FreeEnd
open V2Floor (flog B1)

variable {K Reg C : Type*} [Field K] [DecidableEq K] [Fintype Reg] [DecidableEq Reg]
  [PartialOrder C] [DecidableEq C]

/-- corr-free bridge identity along a chain. -/
theorem chD0_eq_sum_w0 (θ : ℝ) (dim : C → ℕ) :
    ∀ (a : C) (ms : List (Mv K Reg C)) (b : C), MChain a ms b → Asc dim ms →
      chD0 JunkLB2.fL dim a b ms =
        (ms.map fun m => w0 θ (dim m.tail) (dim m.head)).sum - w0 θ (dim a) (dim b)
  | a, [], b, hc, _ => by
    simp only [MChain] at hc; subst hc
    simp [chD0, w0, cB, cA, flog_zero, JunkLB2.fL0]
  | a, m :: ms, b, ⟨hm, hc⟩, hA => by
    have hlt := hA m List.mem_cons_self
    have hA' : Asc dim ms := fun x hx => hA x (List.mem_cons_of_mem _ hx)
    have ih := chD0_eq_sum_w0 θ dim m.head ms b hc hA'
    have hle := chain_le m.head ms b hc hA'
    rw [chD0_cons a b m ms hm hlt, ih]
    rw [hm] at hlt
    have hst := w0_step θ hlt.le hle (a := dim a)
    simp only [List.map_cons, List.sum_cons, hm]
    linarith

lemma h_nonneg {a b e : ℕ} (hab : a ≤ b) (hbe : b ≤ e) :
    0 ≤ JunkLB2.h JunkLB2.fL (e : ℝ) (a : ℝ) (b : ℝ) := by
  simp only [JunkLB2.h, fL_sub (le_trans hab hbe), fL_sub hab, fL_sub hbe]
  have := flog_super (b - a) (e - b)
  rw [show b - a + (e - b) = e - a by omega] at this
  linarith

theorem chD0_nonneg (dim : C → ℕ) :
    ∀ (a : C) (ms : List (Mv K Reg C)) (b : C), MChain a ms b → Asc dim ms →
      0 ≤ chD0 JunkLB2.fL dim a b ms
  | a, [], b, hc, _ => by
    simp only [MChain] at hc; subst hc
    simp [chD0, JunkLB2.fL0]
  | a, m :: ms, b, ⟨hm, hc⟩, hA => by
    have hlt := hA m List.mem_cons_self
    have hA' : Asc dim ms := fun x hx => hA x (List.mem_cons_of_mem _ hx)
    have ih := chD0_nonneg dim m.head ms b hc hA'
    have hle := chain_le m.head ms b hc hA'
    rw [chD0_cons a b m ms hm hlt]
    rw [hm] at hlt
    have := h_nonneg (a := dim a) (b := dim m.head) (e := dim b) hlt.le hle
    linarith

/-- one-move helper from L to U: D0 = 0. -/
theorem oneMove_D0 (dim : C → ℕ) (r : Reg) (L U : C) (row : Reg → K) (h : dim L < dim U) :
    chD0 JunkLB2.fL dim L U [(⟨r, L, U, row⟩ : Mv K Reg C)] = 0 := by
  have hp : (0 : ℝ) ≤ (dim U : ℝ) - dim L := by
    have : (dim L : ℝ) < dim U := by exact_mod_cast h
    linarith
  simp [chD0, mvCost, abs_of_nonneg hp]

theorem oneMove_chain (r : Reg) (L U : C) (row : Reg → K) :
    MChain L [(⟨r, L, U, row⟩ : Mv K Reg C)] U := ⟨rfl, rfl⟩

theorem oneMove_asc (dim : C → ℕ) (r : Reg) (L U : C) (row : Reg → K) (h : dim L < dim U) :
    Asc dim [(⟨r, L, U, row⟩ : Mv K Reg C)] := by
  intro m hm; simp at hm; subst hm; exact h

/-- FLOOR3 collapse: for any list of pairs with dim L < dim U, the one-move helpers are
chains realising each pair at total D0 = 0, and no family of ascending chains has negative D0. -/
theorem floor3_collapse (dim : C → ℕ) (ps : List (C × C)) (hp : ∀ p ∈ ps, dim p.1 < dim p.2)
    (r : C × C → Reg) (row : Reg → K) :
    (∀ p ∈ ps, MChain p.1 [(⟨r p, p.1, p.2, row⟩ : Mv K Reg C)] p.2 ∧
        Asc dim [(⟨r p, p.1, p.2, row⟩ : Mv K Reg C)]) ∧
    (ps.map fun p => chD0 JunkLB2.fL dim p.1 p.2 [(⟨r p, p.1, p.2, row⟩ : Mv K Reg C)]).sum = 0 ∧
    (∀ (a b : C) (ms : List (Mv K Reg C)), MChain a ms b → Asc dim ms →
      0 ≤ chD0 JunkLB2.fL dim a b ms) := by
  refine ⟨fun p hpm => ⟨oneMove_chain _ _ _ _, oneMove_asc dim _ _ _ _ (hp p hpm)⟩, ?_,
    fun a b ms hc ha => chD0_nonneg dim a ms b hc ha⟩
  have : (ps.map fun p => chD0 JunkLB2.fL dim p.1 p.2 [(⟨r p, p.1, p.2, row⟩ : Mv K Reg C)]) =
      ps.map fun _ => 0 := List.map_congr_left fun p hpm => oneMove_D0 dim _ _ _ _ (hp p hpm)
  rw [this]; simp

/-- corrected identity: with the full corr, Σ w0 − corr = D0 + ρ(e) − ρ(d0). -/
theorem sum_w0_sub_corr (θ : ℝ) (dim : C → ℕ) (a : C) (ms : List (Mv K Reg C)) (b : C)
    (hc : MChain a ms b) (hA : Asc dim ms) :
    (ms.map fun m => w0 θ (dim m.tail) (dim m.head)).sum - corr θ (dim a) (dim b) =
      chD0 JunkLB2.fL dim a b ms + rho θ (dim b) - rho θ (dim a) := by
  rw [chD0_eq_sum_w0 θ dim a ms b hc hA]; simp only [corr]; ring

lemma B1_pos : 0 < B1 := by
  rw [B1_eq]; unfold flog
  push_cast
  have h8 : (0 : ℝ) < Real.log 8 := Real.log_pos (by norm_num)
  have h98 : Real.log 8 < Real.log 9 := Real.log_lt_log (by norm_num) (by norm_num)
  nlinarith

/-- the naive reading "Σ w0 − corr = 0" fails for the one-move helper 1 → 2 at θ = 1:
it equals −B1 < 0. -/
theorem slip_counterexample :
    w0 1 1 2 - corr 1 1 2 = -B1 ∧ -B1 < 0 := by
  refine ⟨?_, by linarith [B1_pos]⟩
  simp [corr, rho, w0]

end FreeEnd
