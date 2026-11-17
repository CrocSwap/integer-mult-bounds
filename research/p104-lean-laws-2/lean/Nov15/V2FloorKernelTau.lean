/-
V2FloorKernelTau (lane LEAN-KERNEL, Nov 16): the τ form of the Gaussian top-M rule, and small list/finset bridges.

  Σ_{q ∈ Q, Y ≤ U_{key q}} v q  ≤  Σ_{g ∈ key(Q), dim Y ≤ du g} (W_g − τ(du g)) + Σ_{d = dim Y}^{8} Mt (dim Y) d · τ d

for ANY τ : ℕ → ℕ, where W_g = Σ_{q ∈ Q, key q = g} v q, provided U is injective on the keys and dim U_g = du g ≤ 8.
With τ_d = the Mt-th largest W among the keys of dimension d this is exactly the top-M sum of check.c / flagcheck.c.
-/
import Nov15.V2FloorKernelLemmas

namespace V2Floor
open Finset

attribute [local instance 10] Classical.propDecidable

theorem tau_bound {ι : Type*} (Q : Finset ι) (key : ι → ℕ) (Uk : ℕ → Sub) (du : ℕ → ℕ)
    (hdu : ∀ q ∈ Q, fdim (Uk (key q)) = du (key q)) (hd8 : ∀ q ∈ Q, du (key q) ≤ 8)
    (hinj : Set.InjOn Uk (Q.image key)) (v : ι → ℕ) (Y : Sub) (τ : ℕ → ℕ) :
    ∑ q ∈ Q.filter (fun q => Y ≤ Uk (key q)), v q ≤
      ∑ g ∈ (Q.image key).filter (fun g => fdim Y ≤ du g), (∑ q ∈ Q.filter (fun q => key q = g), v q - τ (du g)) +
      ∑ d ∈ Icc (fdim Y) 8, Mt (fdim Y) d * τ d := by
  set b := fdim Y
  set G := Q.image key
  set W := fun g => ∑ q ∈ Q.filter (fun q => key q = g), v q
  have hG : ∀ g ∈ G, fdim (Uk g) = du g ∧ du g ≤ 8 := by
    intro g hg; obtain ⟨q, hq, rfl⟩ := mem_image.mp hg; exact ⟨hdu q hq, hd8 q hq⟩
  -- step 1: group by key
  have s1 : ∑ q ∈ Q.filter (fun q => Y ≤ Uk (key q)), v q = ∑ g ∈ G.filter (fun g => Y ≤ Uk g), W g := by
    rw [← Finset.sum_fiberwise_of_maps_to (s := Q.filter (fun q => Y ≤ Uk (key q))) (t := G.filter (fun g => Y ≤ Uk g))
      (g := key)]
    · refine Finset.sum_congr rfl fun g hg => ?_
      simp only [mem_filter] at hg
      simp only [W, Finset.filter_filter]
      refine Finset.sum_congr ?_ fun _ _ => rfl
      ext q; simp only [mem_filter]; constructor
      · rintro ⟨h1, _, h3⟩; exact ⟨h1, h3⟩
      · rintro ⟨h1, h3⟩; exact ⟨h1, h3 ▸ hg.2, h3⟩
    · intro q hq; simp only [mem_filter] at hq ⊢; exact ⟨mem_image_of_mem key hq.1, hq.2⟩
  rw [s1]
  set A := G.filter (fun g => Y ≤ Uk g)
  have hAb : ∀ g ∈ A, b ≤ du g ∧ du g ≤ 8 := by
    intro g hg; simp only [A, mem_filter] at hg
    have := hG g hg.1; have := Submodule.finrank_mono hg.2; unfold b fdim at *; omega
  -- step 2: W ≤ (W − τ) + τ
  have s2 : ∑ g ∈ A, W g ≤ ∑ g ∈ A, (W g - τ (du g)) + ∑ g ∈ A, τ (du g) := by
    rw [← Finset.sum_add_distrib]; exact Finset.sum_le_sum fun g _ => by omega
  refine le_trans s2 (add_le_add ?_ ?_)
  · apply Finset.sum_le_sum_of_subset_of_nonneg
    · intro g hg; simp only [A, mem_filter] at hg ⊢; exact ⟨hg.1, (hAb g (by simp [A, hg.1, hg.2])).1⟩
    · intros; exact Nat.zero_le _
  · rw [← Finset.sum_fiberwise_of_maps_to (s := A) (t := Icc b 8) (g := du)]
    · refine Finset.sum_le_sum fun d hd => ?_
      rw [Finset.sum_congr rfl (fun g hg => by rw [(mem_filter.mp hg).2]), Finset.sum_const, smul_eq_mul]
      apply Nat.mul_le_mul_right
      have hsub : (A.filter (fun g => du g = d)).image Uk ⊆ univ.filter (fun U : Sub => Y ≤ U ∧ fdim U = d) := by
        intro U hU
        obtain ⟨g, hg, rfl⟩ := mem_image.mp hU
        simp only [A, mem_filter] at hg
        simp only [mem_filter, mem_univ, true_and]
        exact ⟨hg.1.2, by rw [(hG g hg.1.1).1, hg.2]⟩
      rw [← Finset.card_image_of_injOn (fun x hx y hy h => hinj
        (Finset.mem_coe.mpr (mem_filter.mp (mem_filter.mp (Finset.mem_coe.mp hx)).1).1)
        (Finset.mem_coe.mpr (mem_filter.mp (mem_filter.mp (Finset.mem_coe.mp hy)).1).1) h)]
      exact (Finset.card_le_card hsub).trans (count_le' Y d)
    · intro g hg; have := hAb g hg; simp only [mem_Icc]; exact this

/-- a finset sum over the support of a list is at most the list sum (ℕ-valued). -/
theorem sum_toFinset_le_list {ι : Type*} [DecidableEq ι] (l : List ι) (f : ι → ℕ) : ∑ x ∈ l.toFinset, f x ≤ (l.map f).sum := by
  induction l with
  | nil => simp
  | cons a l ih =>
    rw [List.toFinset_cons, List.map_cons, List.sum_cons]
    by_cases h : a ∈ l.toFinset
    · rw [Finset.insert_eq_of_mem h]; omega
    · rw [Finset.sum_insert h]; omega

theorem sum_toFinset_nodup {ι : Type*} [DecidableEq ι] (l : List ι) (hl : l.Nodup) (f : ι → ℕ) :
    ∑ x ∈ l.toFinset, f x = (l.map f).sum := List.sum_toFinset f hl

theorem sum_Icc_list (b : ℕ) (f : ℕ → ℕ) (hb : b ≤ 9) :
    ∑ d ∈ Icc b 8, f d = ((List.range' b (9 - b)).map f).sum := by
  rw [← sum_toFinset_nodup _ List.nodup_range']
  congr 1; ext d; simp only [mem_Icc, List.mem_toFinset, List.mem_range'_1]; constructor <;> intro h <;> omega

theorem sum_range_getD {α : Type*} (l : List α) (d : α) (f : α → ℕ) :
    ∑ j ∈ range l.length, f (l.getD j d) = (l.map f).sum := by
  induction l with
  | nil => simp
  | cons a l ih =>
    rw [List.length_cons, Finset.sum_range_succ', List.map_cons, List.sum_cons]
    simp only [List.getD_cons_succ, List.getD_cons_zero]
    rw [ih]; ring

theorem mono_le (F : ℕ → ℕ) (hmono : ∀ k, k < 9 → F k ≤ F (k + 1)) (i j : ℕ) (hij : i ≤ j) (hj : j ≤ 9) : F i ≤ F j := by
  induction j, hij using Nat.le_induction with
  | base => exact le_rfl
  | succ m hm ih => exact (ih (by omega)).trans (hmono m (by omega))

/-- telescoping of a monotone packed cumulative table. -/
theorem sum_Ico_tele (F : ℕ → ℕ) (hmono : ∀ k, k < 9 → F k ≤ F (k + 1)) (a b : ℕ) (hab : a ≤ b) (hb : b ≤ 9) :
    ∑ k ∈ Ico a b, (if k < 9 then F (k + 1) - F k else 0) = F b - F a := by
  induction b, hab using Nat.le_induction with
  | base => simp
  | succ n hn ih =>
    rw [Finset.sum_Ico_succ_top hn, ih (by omega), if_pos (by omega)]
    have h1 := hmono n (by omega)
    have h2 : F a ≤ F n := mono_le F hmono a n hn (by omega)
    omega

end V2Floor
