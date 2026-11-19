/-
BankFlagA .  
FLAG-CUT LEMMA, kernel-checked over any field K and finite-dim module M.
Flag F 0 = ⊥ ≤ F 1 ≤ … ≤ F n, each step of dimension +1 (hstep), c ≤ F n.
  d c j = dim((c ⊓ F(j+1)) ⊔ F j) − dim F j  (= dim(c ⊓ F(j+1)) − dim(c ⊓ F j) ∈ {0,1}).
(1) d is monotone in c (so D_j = {d_j = 0} is a down-set) and Σ_j d c j = dim c.
(2) NESTED a ≤ b: exactly dim b − dim a cuts j have d a j < d b j (outward), none inward.
(3) NON-NESTED (no P-NEST): #out ≤ dim V − dim(U⊓V), #in ≤ dim U − dim(U⊓V); total ≤ lattice distance.
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.LinearAlgebra.FiniteDimensional.Defs
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.Algebra.BigOperators.Group.Finset.Basic

namespace BankFlag
open Finset Module Submodule

variable {K M : Type*} [Field K] [AddCommGroup M] [Module K M] [FiniteDimensional K M]

/-- the flag-coordinate of a subspace at cut j -/
noncomputable def d (F : ℕ → Submodule K M) (c : Submodule K M) (j : ℕ) : ℕ :=
  finrank K (((c ⊓ F (j+1)) ⊔ F j : Submodule K M)) - finrank K (F j)

variable (F : ℕ → Submodule K M)

theorem d_add (hmono : ∀ j, F j ≤ F (j+1)) (c : Submodule K M) (j : ℕ) :
    d F c j + finrank K (c ⊓ F j : Submodule K M) = finrank K (c ⊓ F (j+1) : Submodule K M) := by
  have h1 := Submodule.finrank_sup_add_finrank_inf_eq (c ⊓ F (j+1)) (F j)
  have h2 : (c ⊓ F (j+1)) ⊓ F j = c ⊓ F j := by
    ext x; simp only [Submodule.mem_inf]
    constructor
    · rintro ⟨⟨a, _⟩, b⟩; exact ⟨a, b⟩
    · rintro ⟨a, b⟩; exact ⟨⟨a, hmono j b⟩, b⟩
  rw [h2] at h1
  have h3 : finrank K (F j) ≤ finrank K (((c ⊓ F (j+1)) ⊔ F j : Submodule K M)) :=
    Submodule.finrank_mono le_sup_right
  unfold d; omega

theorem d_mono (a b : Submodule K M) (hab : a ≤ b) (j : ℕ) : d F a j ≤ d F b j := by
  unfold d
  have : finrank K (((a ⊓ F (j+1)) ⊔ F j : Submodule K M)) ≤ finrank K (((b ⊓ F (j+1)) ⊔ F j : Submodule K M)) :=
    Submodule.finrank_mono (sup_le_sup_right (inf_le_inf_right _ hab) _)
  omega

theorem d_le_one (hmono : ∀ j, F j ≤ F (j+1)) (hstep : ∀ j, finrank K (F (j+1)) = finrank K (F j) + 1)
    (c : Submodule K M) (j : ℕ) : d F c j ≤ 1 := by
  unfold d
  have : finrank K (((c ⊓ F (j+1)) ⊔ F j : Submodule K M)) ≤ finrank K (F (j+1)) :=
    Submodule.finrank_mono (sup_le inf_le_right (hmono j))
  have := hstep j
  omega

theorem d_sum (hmono : ∀ j, F j ≤ F (j+1)) (h0 : F 0 = ⊥) (c : Submodule K M) (n : ℕ) :
    ∑ j ∈ range n, d F c j = finrank K (c ⊓ F n : Submodule K M) := by
  induction n with
  | zero => rw [h0, inf_bot_eq]; simp
  | succ n ih => rw [sum_range_succ, ih]; have := d_add F hmono c n; omega

theorem d_sum_le (hmono : ∀ j, F j ≤ F (j+1)) (h0 : F 0 = ⊥) (c : Submodule K M) (n : ℕ)
    (hc : c ≤ F n) : ∑ j ∈ range n, d F c j = finrank K c := by
  rw [d_sum F hmono h0, inf_eq_left.mpr hc]

/-- cut counts: out = (U ∈ D_j, V ∉ D_j) in the strict sense d U j < d V j -/
theorem card_lt_le_sum (f g : ℕ → ℕ) (n : ℕ) (hgf : ∀ j, g j ≤ f j) :
    ((range n).filter (fun j => g j < f j)).card ≤ ∑ j ∈ range n, (f j - g j) := by
  rw [Finset.card_filter]
  apply sum_le_sum
  intro j _
  have := hgf j
  split_ifs with h <;> omega

theorem sum_sub (f g : ℕ → ℕ) (n : ℕ) (hgf : ∀ j, g j ≤ f j) :
    ∑ j ∈ range n, (f j - g j) = ∑ j ∈ range n, f j - ∑ j ∈ range n, g j := by
  have : ∑ j ∈ range n, g j + ∑ j ∈ range n, (f j - g j) = ∑ j ∈ range n, f j := by
    rw [← sum_add_distrib]; apply sum_congr rfl; intro j _; have := hgf j; omega
  omega

/-- (2) nested: exactly dim b − dim a outward crossings (needs d ≤ 1), and no inward ones. -/
theorem cross_nested (hmono : ∀ j, F j ≤ F (j+1)) (h0 : F 0 = ⊥)
    (hstep : ∀ j, finrank K (F (j+1)) = finrank K (F j) + 1)
    (a b : Submodule K M) (hab : a ≤ b) (n : ℕ) (hb : b ≤ F n) :
    ((range n).filter (fun j => d F a j < d F b j)).card = finrank K b - finrank K a ∧
    ((range n).filter (fun j => d F b j < d F a j)).card = 0 := by
  have ha : a ≤ F n := hab.trans hb
  constructor
  · have hsum := sum_sub (d F b) (d F a) n (fun j => d_mono F a b hab j)
    rw [d_sum_le F hmono h0 b n hb, d_sum_le F hmono h0 a n ha] at hsum
    rw [← hsum, Finset.card_filter]
    apply sum_congr rfl
    intro j _
    have h1 := d_le_one F hmono hstep a j
    have h2 := d_le_one F hmono hstep b j
    have h3 := d_mono F a b hab j
    split_ifs with h <;> omega
  · rw [Finset.card_eq_zero, Finset.filter_eq_empty_iff]
    intro j _ h; have := d_mono F a b hab j; omega

/-- (3) NON-NESTED, no P-NEST: crossings are bounded by the distances to the meet W = U ⊓ V. -/
theorem cross_general (hmono : ∀ j, F j ≤ F (j+1)) (h0 : F 0 = ⊥)
    (U V : Submodule K M) (n : ℕ) (hU : U ≤ F n) (hV : V ≤ F n) :
    ((range n).filter (fun j => d F U j < d F V j)).card ≤ finrank K V - finrank K (U ⊓ V : Submodule K M) ∧
    ((range n).filter (fun j => d F V j < d F U j)).card ≤ finrank K U - finrank K (U ⊓ V : Submodule K M) := by
  have hWU : (U ⊓ V : Submodule K M) ≤ U := inf_le_left
  have hWV : (U ⊓ V : Submodule K M) ≤ V := inf_le_right
  constructor
  · calc _ ≤ ((range n).filter (fun j => d F (U ⊓ V) j < d F V j)).card := by
          apply Finset.card_le_card
          intro j; simp only [mem_filter]
          rintro ⟨hj, h⟩; exact ⟨hj, lt_of_le_of_lt (d_mono F _ _ hWU j) h⟩
      _ ≤ ∑ j ∈ range n, (d F V j - d F (U ⊓ V) j) :=
          card_lt_le_sum _ _ n (fun j => d_mono F _ _ hWV j)
      _ = _ := by
          rw [sum_sub _ _ n (fun j => d_mono F _ _ hWV j), d_sum_le F hmono h0 V n hV,
            d_sum_le F hmono h0 _ n (hWV.trans hV)]
  · calc _ ≤ ((range n).filter (fun j => d F (U ⊓ V) j < d F U j)).card := by
          apply Finset.card_le_card
          intro j; simp only [mem_filter]
          rintro ⟨hj, h⟩; exact ⟨hj, lt_of_le_of_lt (d_mono F _ _ hWV j) h⟩
      _ ≤ ∑ j ∈ range n, (d F U j - d F (U ⊓ V) j) :=
          card_lt_le_sum _ _ n (fun j => d_mono F _ _ hWU j)
      _ = _ := by
          rw [sum_sub _ _ n (fun j => d_mono F _ _ hWU j), d_sum_le F hmono h0 U n hU,
            d_sum_le F hmono h0 _ n (hWU.trans hU)]

end BankFlag
#print axioms BankFlag.cross_general
#print axioms BankFlag.cross_nested
