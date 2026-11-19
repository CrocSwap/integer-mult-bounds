/-
BankNC0c .  
(c) Summation.  Integer-interval cuts P_a = {charts with height in [a, a+L)} on chart heights h.
A bank (or field) src→dst crosses P_a (src inside, dst outside) for exactly min(L,|Δh|) values a.
Per-cut lemma (BankNC0b) summed over a gives  Σ_f min(L,Δ_f) ≤ Σ_k min(L,Δ_k)  for each L; weight by c_L ≥ 0
(BankNC0a decomposition of a concave price) to get  Σ_banks paid ≥ Σ_banks g(Δ_k) ≥ Σ_fields g(climb_f).
Named premises of the final theorem: P-LIN (inputs independent: coefficient-vector model), P-ACYC (order on Bank),
P-HLOC (transport only by banks: the Net structure), P-1S' (paid k ≥ g(|Δh|), one scalar per bank),
nonzero principal minors of O, heights bounded by H (any finite network), g concave nondecreasing, g 0 = 0.
Kernel only: no sorry, no native_decide.
-/
import Mathlib.Data.Int.Interval
import Nov15.BankNC0a
import Nov15.BankNC0b

namespace BankNC0
open Finset

/-- height distance -/
def dh (i j : ℕ) : ℕ := Int.natAbs ((i : ℤ) - j)

theorem count_cuts (i j L H : ℕ) (hi : i ≤ H) (hj : j ≤ H) :
    ((Finset.Icc (-(L : ℤ)) H).filter
      (fun a : ℤ => (a ≤ (i:ℤ) ∧ (i : ℤ) < a + L) ∧ ¬ (a ≤ (j:ℤ) ∧ (j : ℤ) < a + L))).card = min L (dh i j) := by
  unfold dh
  rcases le_total i j with h | h
  · have : (Finset.Icc (-(L : ℤ)) H).filter
        (fun a : ℤ => (a ≤ (i:ℤ) ∧ (i : ℤ) < a + L) ∧ ¬ (a ≤ (j:ℤ) ∧ (j : ℤ) < a + L))
        = Finset.Icc ((i : ℤ) + 1 - L) (min (i : ℤ) ((j : ℤ) - L)) := by
      ext a; simp only [Finset.mem_filter, Finset.mem_Icc]; omega
    rw [this, Int.card_Icc]; omega
  · have : (Finset.Icc (-(L : ℤ)) H).filter
        (fun a : ℤ => (a ≤ (i:ℤ) ∧ (i : ℤ) < a + L) ∧ ¬ (a ≤ (j:ℤ) ∧ (j : ℤ) < a + L))
        = Finset.Icc (max ((j : ℤ) + 1) ((i : ℤ) + 1 - L)) (i : ℤ) := by
      ext a; simp only [Finset.mem_filter, Finset.mem_Icc]; omega
    rw [this, Int.card_Icc]; omega

variable {K : Type} {Chart Fld Bank : Type} [Field K] [Fintype Fld] [DecidableEq Fld]
  [Fintype Bank] [LinearOrder Bank]

/-- per-L inequality, by summing the cut lemma over the interval cuts of length L. -/
theorem perL (N : Net K Chart Fld Bank)
    (hminor : ∀ C : Finset Fld,
      (N.O.submatrix (fun c : C => (c : Fld)) (fun c : C => (c : Fld))).det ≠ 0)
    (h : Chart → ℕ) (H : ℕ) (hH : ∀ c, h c ≤ H) (L : ℕ) :
    ∑ f, min L (dh (h (N.A f)) (h (N.B f))) ≤ ∑ k, min L (dh (h (N.src k)) (h (N.dst k))) := by
  classical
  let I := Finset.Icc (-(L : ℤ)) (H : ℤ)
  let Pa : ℤ → Chart → Prop := fun (a : ℤ) c => a ≤ (h c : ℤ) ∧ (h c : ℤ) < a + L
  have hcut : ∀ a ∈ I,
      (Finset.univ.filter (fun f => Pa a (N.A f) ∧ ¬ Pa a (N.B f))).card ≤
      (Finset.univ.filter (fun k => Pa a (N.src k) ∧ ¬ Pa a (N.dst k))).card :=
    fun a _ => cut_lemma N hminor (Pa a)
  have hsum := Finset.sum_le_sum hcut
  have e1 : ∀ (X : Type) [Fintype X] (u v : X → Chart),
      ∑ a ∈ I, (Finset.univ.filter (fun x => Pa a (u x) ∧ ¬ Pa a (v x))).card
        = ∑ x, min L (dh (h (u x)) (h (v x))) := by
    intro X _ u v
    simp_rw [Finset.card_filter]
    rw [Finset.sum_comm]
    apply Finset.sum_congr rfl
    intro x _
    rw [← count_cuts (h (u x)) (h (v x)) L H (hH _) (hH _), Finset.card_filter]
  rw [e1 Fld N.A N.B, e1 Bank N.src N.dst] at hsum
  exact hsum

/-- (c) NC0: total paid cost ≥ Σ_fields g(climb_f). -/
theorem NC0 (N : Net K Chart Fld Bank)
    (hminor : ∀ C : Finset Fld,
      (N.O.submatrix (fun c : C => (c : Fld)) (fun c : C => (c : Fld))).det ≠ 0)
    (h : Chart → ℕ) (H : ℕ) (hH : ∀ c, h c ≤ H)
    (g : ℕ → ℝ) (g0 : g 0 = 0) (hmono : ∀ j, j < H → g j ≤ g (j+1))
    (hconc : ∀ j, j + 1 < H → g (j+2) - g (j+1) ≤ g (j+1) - g j)
    (paid : Bank → ℝ) (hpaid : ∀ k, g (dh (h (N.src k)) (h (N.dst k))) ≤ paid k) :
    ∑ f, g (dh (h (N.A f)) (h (N.B f))) ≤ ∑ k, paid k := by
  obtain ⟨c, hc, hg⟩ := decomp H g g0 hmono hconc
  have hd : ∀ i j, i ≤ H → j ≤ H → dh i j ≤ H := by intro i j hi hj; unfold dh; omega
  have hf : ∀ f, g (dh (h (N.A f)) (h (N.B f))) =
      ∑ L ∈ Icc 1 H, c L * (min L (dh (h (N.A f)) (h (N.B f))) : ℕ) :=
    fun f => hg _ (hd _ _ (hH _) (hH _))
  have hk : ∀ k, g (dh (h (N.src k)) (h (N.dst k))) =
      ∑ L ∈ Icc 1 H, c L * (min L (dh (h (N.src k)) (h (N.dst k))) : ℕ) :=
    fun k => hg _ (hd _ _ (hH _) (hH _))
  calc ∑ f, g (dh (h (N.A f)) (h (N.B f)))
      = ∑ L ∈ Icc 1 H, c L * ((∑ f, min L (dh (h (N.A f)) (h (N.B f))) : ℕ) : ℝ) := by
        simp_rw [hf]; rw [Finset.sum_comm]
        refine Finset.sum_congr rfl (fun L _ => ?_)
        push_cast; rw [Finset.mul_sum]
    _ ≤ ∑ L ∈ Icc 1 H, c L * ((∑ k, min L (dh (h (N.src k)) (h (N.dst k))) : ℕ) : ℝ) := by
        refine Finset.sum_le_sum (fun L _ => ?_)
        exact mul_le_mul_of_nonneg_left (by exact_mod_cast perL N hminor h H hH L) (hc L)
    _ = ∑ k, g (dh (h (N.src k)) (h (N.dst k))) := by
        simp_rw [hk]; rw [Finset.sum_comm]
        refine Finset.sum_congr rfl (fun L _ => ?_)
        push_cast; rw [Finset.mul_sum]
    _ ≤ ∑ k, paid k := Finset.sum_le_sum (fun k _ => hpaid k)

end BankNC0
