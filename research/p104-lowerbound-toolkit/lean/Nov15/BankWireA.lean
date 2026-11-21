/-
BankWireA (lane S-BANKWIRE, Nov 18).  See cards/WILD/LEANSWARM/FLAG.md.
(0) FIX: BankFlagA's `cross_nested` assumed hstep for ALL j (finrank (F (j+1)) = finrank (F j) + 1 forever), which is
    unsatisfiable in a finite-dimensional M (vacuous).  Here the same lemmas under hstep for j < n only.
(1) chart model: the flag coordinate d_j of the chart types of the main contract:
      d(⊥)=0, d(⊤)=1, d(span v)=1 iff v ∈ F(j+1)∖F j, d(ker φ)=0 iff F j ≤ ker φ ∌ F(j+1).
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.BankFlagA

namespace BankWire
open Finset Module Submodule BankFlag

variable {K M : Type*} [Field K] [AddCommGroup M] [Module K M] [FiniteDimensional K M]
variable (F : ℕ → Submodule K M)

theorem d_le_one_lt (hmono : ∀ j, F j ≤ F (j+1)) (n : ℕ)
    (hstep : ∀ j, j < n → finrank K (F (j+1)) = finrank K (F j) + 1)
    (c : Submodule K M) (j : ℕ) (hj : j < n) : d F c j ≤ 1 := by
  unfold d
  have : finrank K (((c ⊓ F (j+1)) ⊔ F j : Submodule K M)) ≤ finrank K (F (j+1)) :=
    Submodule.finrank_mono (sup_le inf_le_right (hmono j))
  have := hstep j hj
  omega

theorem cross_nested_lt (hmono : ∀ j, F j ≤ F (j+1)) (h0 : F 0 = ⊥) (n : ℕ)
    (hstep : ∀ j, j < n → finrank K (F (j+1)) = finrank K (F j) + 1)
    (a b : Submodule K M) (hab : a ≤ b) (hb : b ≤ F n) :
    ((range n).filter (fun j => d F a j < d F b j)).card = finrank K b - finrank K a ∧
    ((range n).filter (fun j => d F b j < d F a j)).card = 0 := by
  have ha : a ≤ F n := hab.trans hb
  constructor
  · have hsum := sum_sub (d F b) (d F a) n (fun j => d_mono F a b hab j)
    rw [d_sum_le F hmono h0 b n hb, d_sum_le F hmono h0 a n ha] at hsum
    rw [← hsum, Finset.card_filter]
    apply sum_congr rfl
    intro j hj
    have h1 := d_le_one_lt F hmono n hstep a j (Finset.mem_range.mp hj)
    have h2 := d_le_one_lt F hmono n hstep b j (Finset.mem_range.mp hj)
    have h3 := d_mono F a b hab j
    split_ifs with h <;> omega
  · rw [Finset.card_eq_zero, Finset.filter_eq_empty_iff]
    intro j _ h; have := d_mono F a b hab j; omega

theorem finrank_flag (h0 : F 0 = ⊥) (n : ℕ)
    (hstep : ∀ j, j < n → finrank K (F (j+1)) = finrank K (F j) + 1) :
    ∀ j, j ≤ n → finrank K (F j) = j := by
  intro j
  induction j with
  | zero => intro _; simp [h0]
  | succ j ih => intro hj; rw [hstep j (by omega), ih (by omega)]

theorem d_bot (j : ℕ) : d F (⊥ : Submodule K M) j = 0 := by
  unfold d; rw [bot_inf_eq, bot_sup_eq]; exact Nat.sub_self _

theorem d_top (hmono : ∀ j, F j ≤ F (j+1)) (j : ℕ)
    (hs : finrank K (F (j+1)) = finrank K (F j) + 1) : d F (⊤ : Submodule K M) j = 1 := by
  unfold d
  rw [top_inf_eq, sup_eq_left.mpr (hmono j)]; omega

theorem d_span (hmono : ∀ j, F j ≤ F (j+1)) (j : ℕ) (v : M) (hv1 : v ∈ F (j+1)) (hv0 : v ∉ F j) :
    d F (span K {v}) j = 1 := by
  have h := d_add F hmono (span K {v}) j
  have hv : v ≠ 0 := fun h => hv0 (h ▸ Submodule.zero_mem _)
  have e1 : span K {v} ⊓ F (j+1) = span K {v} :=
    inf_eq_left.mpr ((Submodule.span_singleton_le_iff_mem v _).mpr hv1)
  have e0 : span K {v} ⊓ F j = ⊥ := by
    have : Disjoint (span K {v}) (F j) := by
      rw [disjoint_comm]; exact (Submodule.disjoint_span_singleton' hv).mpr hv0
    exact this.eq_bot
  rw [e1, e0, finrank_span_singleton hv] at h
  simp at h; exact h

theorem d_ker (hmono : ∀ j, F j ≤ F (j+1)) (j : ℕ)
    (hs : finrank K (F (j+1)) = finrank K (F j) + 1) (φ : M →ₗ[K] K)
    (hle : F j ≤ LinearMap.ker φ) (hnle : ¬ F (j+1) ≤ LinearMap.ker φ) :
    d F (LinearMap.ker φ) j = 0 := by
  have h := d_add F hmono (LinearMap.ker φ) j
  have e0 : LinearMap.ker φ ⊓ F j = F j := inf_eq_right.mpr hle
  have hlt : LinearMap.ker φ ⊓ F (j+1) < F (j+1) := by
    refine lt_of_le_of_ne inf_le_right (fun h' => hnle ?_)
    rw [← h']; exact inf_le_left
  have h1 := Submodule.finrank_lt_finrank_of_lt hlt
  rw [e0] at h
  omega

end BankWire
#print axioms BankWire.cross_nested_lt
#print axioms BankWire.d_span
#print axioms BankWire.d_ker
