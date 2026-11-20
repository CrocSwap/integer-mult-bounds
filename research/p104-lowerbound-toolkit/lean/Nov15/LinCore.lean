import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.Field.ZMod
import Mathlib.Algebra.BigOperators.Ring.Finset
import Nov15.LinOrd
import Mathlib.LinearAlgebra.LinearIndependent.Lemmas
import Mathlib.LinearAlgebra.Dimension.Finite
import Mathlib.Order.CompleteLattice.Finset
/-!
LINCORE (lane LEANLINEAR).  Core of LINEAR56 Theorem B over F2:
  alternating forms Lam n = (pairs i<j) -> F2, wedge, symmat, the key lemma
  (a quadric relation with filtered coefficients forces every coefficient to vanish), via `LinOrd`.
-/
open Matrix Finset

section RadoSec
open Module Submodule
namespace LinRado

variable {K : Type*} [Field K] {U : Type*} [AddCommGroup U] [Module K U] [FiniteDimensional K U]
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- the span of the subfamily J -/
def sp (W : ι → Submodule K U) (J : Finset ι) : Submodule K U := ⨆ t ∈ J, W t

/-- Hall condition with deficiency δ -/
def Hall (δ : ℕ) (W : ι → Submodule K U) : Prop :=
  ∀ J : Finset ι, J.card ≤ finrank K (sp W J) + δ

lemma le_sp (W : ι → Submodule K U) {J : Finset ι} {t : ι} (h : t ∈ J) : W t ≤ sp W J :=
  le_iSup₂ (f := fun t (_ : t ∈ J) => W t) t h

lemma sp_le (W : ι → Submodule K U) {J : Finset ι} {S : Submodule K U} (h : ∀ t ∈ J, W t ≤ S) :
    sp W J ≤ S := iSup₂_le h

lemma sp_union (W : ι → Submodule K U) (J₁ J₂ : Finset ι) :
    sp W (J₁ ∪ J₂) = sp W J₁ ⊔ sp W J₂ := by
  unfold sp; exact Finset.iSup_union

/-- two proper subspaces summing to a space of dimension >= 2 -/
lemma exists_two_sub (W : Submodule K U) (h : 2 ≤ finrank K W) :
    ∃ H₁ H₂ : Submodule K U, H₁ ≤ W ∧ H₂ ≤ W ∧ W ≤ H₁ ⊔ H₂ ∧
      finrank K H₁ < finrank K W ∧ finrank K H₂ < finrank K W := by
  classical
  set m := finrank K W with hm
  let b : Basis (Fin m) K W := Module.finBasis K W
  let H : Fin m → Submodule K U := fun j =>
    Submodule.span K (Set.range (fun i : {i : Fin m // i ≠ j} => ((b i.1 : W) : U)))
  have hH : ∀ j, H j ≤ W := by
    intro j
    refine Submodule.span_le.2 ?_
    rintro _ ⟨i, rfl⟩
    exact (b i.1).2
  have hcard : ∀ j : Fin m, Fintype.card {i : Fin m // i ≠ j} + 1 = m := by
    intro j
    have := Fintype.card_congr (Equiv.optionSubtypeNe j)
    rw [Fintype.card_option, Fintype.card_fin] at this
    exact this
  have hf : ∀ j, finrank K (H j) < m := by
    intro j
    have h1 := finrank_range_le_card (R := K)
      (fun i : {i : Fin m // i ≠ j} => ((b i.1 : W) : U))
    have := hcard j
    exact lt_of_le_of_lt h1 (by omega)
  let i0 : Fin m := ⟨0, by omega⟩
  let i1 : Fin m := ⟨1, by omega⟩
  have h01 : i0 ≠ i1 := by simp [i0, i1, Fin.ext_iff]
  refine ⟨H i0, H i1, hH _, hH _, ?_, hf _, hf _⟩
  intro w hw
  have hw' : (⟨w, hw⟩ : W) ∈ Submodule.span K (Set.range b) := by rw [b.span_eq]; trivial
  have hmap : (Submodule.span K (Set.range b)).map W.subtype ≤ H i0 ⊔ H i1 := by
    rw [Submodule.map_span]
    refine Submodule.span_le.2 ?_
    rintro _ ⟨_, ⟨i, rfl⟩, rfl⟩
    by_cases hi : i = i0
    · subst hi
      exact Submodule.mem_sup_right (Submodule.subset_span ⟨⟨i0, h01⟩, rfl⟩)
    · exact Submodule.mem_sup_left (Submodule.subset_span ⟨⟨i, hi⟩, rfl⟩)
  exact hmap (Submodule.mem_map.2 ⟨⟨w, hw⟩, hw', rfl⟩)

/-- base case: every W_t has dimension <= 1 -/
lemma rado_base (δ : ℕ) (W : ι → Submodule K U) (hW : ∀ t, finrank K (W t) ≤ 1) (hall : Hall δ W) :
    ∃ x : ι → U, (∀ t, x t ∈ W t) ∧ ∃ T0 : Finset ι, Fintype.card ι ≤ T0.card + δ ∧
      LinearIndependent K (fun t : T0 => x t) := by
  classical
  have hgen : ∀ t, ∃ u : U, u ∈ W t ∧ W t = Submodule.span K {u} := by
    intro t
    obtain ⟨v, hv⟩ := finrank_le_one_iff.1 (hW t)
    refine ⟨v.1, v.2, le_antisymm ?_ ?_⟩
    · intro w hw
      obtain ⟨c, hc⟩ := hv ⟨w, hw⟩
      have : w = c • v.1 := by have := congrArg Subtype.val hc; simpa using this.symm
      rw [this]; exact Submodule.smul_mem _ _ (Submodule.subset_span rfl)
    · exact Submodule.span_le.2 (by simpa using v.2)
  choose u hu1 hu2 using hgen
  have hsp : sp W Finset.univ = Submodule.span K (Set.range u) := by
    apply le_antisymm
    · refine sp_le W fun t _ => ?_
      rw [hu2 t]
      exact Submodule.span_mono (by simp)
    · refine Submodule.span_le.2 ?_
      rintro _ ⟨t, rfl⟩
      exact le_sp W (Finset.mem_univ t) (hu1 t)
  obtain ⟨b, -, -, hspan, hli⟩ := exists_linearIndepOn_extension (K := K) (v := u)
    (s := (∅ : Set ι)) (t := Set.univ) (linearIndepOn_empty K u) (Set.empty_subset _)
  have hLI : LinearIndependent K (fun t : (Finset.univ.filter (· ∈ b) : Finset ι) => u t.1) := by
    have := hli.comp (fun t : (Finset.univ.filter (· ∈ b) : Finset ι) =>
        (⟨t.1, (Finset.mem_filter.1 t.2).2⟩ : b))
      (fun x y h => Subtype.ext (Subtype.mk.inj h))
    exact this
  refine ⟨u, hu1, Finset.univ.filter (· ∈ b), ?_, hLI⟩
  have h1 := hall Finset.univ
  rw [hsp] at h1
  have h2 : Submodule.span K (Set.range u) ≤ Submodule.span K (u '' b) := by
    refine Submodule.span_le.2 ?_
    rintro _ ⟨t, rfl⟩
    exact hspan ⟨t, Set.mem_univ t, rfl⟩
  have h3 := Submodule.finrank_mono h2
  have hrange : Set.range (fun t : (Finset.univ.filter (· ∈ b) : Finset ι) => u t.1) = u '' b := by
    ext w; constructor
    · rintro ⟨t, rfl⟩; exact ⟨t.1, (Finset.mem_filter.1 t.2).2, rfl⟩
    · rintro ⟨t, ht, rfl⟩; exact ⟨⟨t, Finset.mem_filter.2 ⟨Finset.mem_univ _, ht⟩⟩, rfl⟩
  have h5 := finrank_span_eq_card hLI
  rw [hrange, Fintype.card_coe] at h5
  rw [Finset.card_univ] at h1
  omega

/-- RADO with deficiency, by induction on the total dimension -/
theorem rado_aux : ∀ (m : ℕ) (δ : ℕ) (W : ι → Submodule K U), ∑ t, finrank K (W t) ≤ m → Hall δ W →
    ∃ x : ι → U, (∀ t, x t ∈ W t) ∧ ∃ T0 : Finset ι, Fintype.card ι ≤ T0.card + δ ∧
      LinearIndependent K (fun t : T0 => x t) := by
  intro m
  induction m with
  | zero =>
    intro δ W hs hall
    apply rado_base δ W _ hall
    intro t
    have := Finset.single_le_sum (f := fun t => finrank K (W t)) (fun _ _ => Nat.zero_le _)
      (Finset.mem_univ t)
    omega
  | succ m ih =>
    intro δ W hs hall
    by_cases hbase : ∀ t, finrank K (W t) ≤ 1
    · exact rado_base δ W hbase hall
    · push Not at hbase
      obtain ⟨t0, ht0⟩ := hbase
      obtain ⟨H₁, H₂, h1W, h2W, hsum, hf1, hf2⟩ := exists_two_sub (W t0) ht0
      let W1 : ι → Submodule K U := Function.update W t0 H₁
      let W2 : ι → Submodule K U := Function.update W t0 H₂
      have hsumup : ∀ H : Submodule K U, finrank K H < finrank K (W t0) →
          ∑ t, finrank K (Function.update W t0 H t) ≤ m := by
        intro H hH
        have e1 : ∑ t, finrank K (Function.update W t0 H t) =
            ∑ t, Function.update (fun t => finrank K (W t)) t0 (finrank K H) t := by
          refine Finset.sum_congr rfl fun t _ => ?_
          by_cases h : t = t0
          · subst h; rw [Function.update_self, Function.update_self]
          · rw [Function.update_of_ne h, Function.update_of_ne h]
        rw [e1, Finset.sum_update_of_mem (Finset.mem_univ t0)]
        have e2 := Finset.add_sum_erase Finset.univ (fun t => finrank K (W t)) (Finset.mem_univ t0)
        have e3 : ∑ x ∈ Finset.univ \ {t0}, finrank K (W x) = ∑ x ∈ Finset.univ.erase t0, finrank K (W x) := by
          congr 1; ext x; simp
        rw [e3]
        omega
      have hWle1 : ∀ t, W1 t ≤ W t := by
        intro t; by_cases h : t = t0
        · subst h; simpa [W1] using h1W
        · simp [W1, Function.update_of_ne h]
      have hWle2 : ∀ t, W2 t ≤ W t := by
        intro t; by_cases h : t = t0
        · subst h; simpa [W2] using h2W
        · simp [W2, Function.update_of_ne h]
      by_cases hall1 : Hall δ W1
      · obtain ⟨x, hx, T0, hT0, hli⟩ := ih δ W1 (hsumup H₁ hf1) hall1
        exact ⟨x, fun t => hWle1 t (hx t), T0, hT0, hli⟩
      by_cases hall2 : Hall δ W2
      · obtain ⟨x, hx, T0, hT0, hli⟩ := ih δ W2 (hsumup H₂ hf2) hall2
        exact ⟨x, fun t => hWle2 t (hx t), T0, hT0, hli⟩
      exfalso
      unfold Hall at hall1 hall2
      push Not at hall1 hall2
      obtain ⟨J1, hJ1⟩ := hall1
      obtain ⟨J2, hJ2⟩ := hall2
      have hmem1 : t0 ∈ J1 := by
        by_contra hn
        have : sp W1 J1 = sp W J1 := by
          unfold sp
          refine iSup_congr fun t => iSup_congr fun ht => ?_
          have : t ≠ t0 := fun h => hn (h ▸ ht)
          simp [W1, Function.update_of_ne this]
        rw [this] at hJ1
        have := hall J1; omega
      have hmem2 : t0 ∈ J2 := by
        by_contra hn
        have : sp W2 J2 = sp W J2 := by
          unfold sp
          refine iSup_congr fun t => iSup_congr fun ht => ?_
          have : t ≠ t0 := fun h => hn (h ▸ ht)
          simp [W2, Function.update_of_ne this]
        rw [this] at hJ2
        have := hall J2; omega
      set A1 := sp W1 J1 with hA1
      set A2 := sp W2 J2 with hA2
      have hsup : sp W (J1 ∪ J2) ≤ A1 ⊔ A2 := by
        refine sp_le W fun t ht => ?_
        rcases Finset.mem_union.1 ht with h | h
        · by_cases ht0 : t = t0
          · subst ht0
            refine hsum.trans (sup_le_sup ?_ ?_)
            · have : H₁ = W1 t := by simp [W1]
              rw [this]; exact le_sp W1 hmem1
            · have : H₂ = W2 t := by simp [W2]
              rw [this]; exact le_sp W2 hmem2
          · have : W t = W1 t := by simp [W1, Function.update_of_ne ht0]
            rw [this]; exact (le_sp W1 h).trans le_sup_left
        · by_cases ht0 : t = t0
          · subst ht0
            refine hsum.trans (sup_le_sup ?_ ?_)
            · have : H₁ = W1 t := by simp [W1]
              rw [this]; exact le_sp W1 hmem1
            · have : H₂ = W2 t := by simp [W2]
              rw [this]; exact le_sp W2 hmem2
          · have : W t = W2 t := by simp [W2, Function.update_of_ne ht0]
            rw [this]; exact (le_sp W2 h).trans le_sup_right
      have hinf : sp W ((J1 ∩ J2).erase t0) ≤ A1 ⊓ A2 := by
        refine sp_le W fun t ht => ?_
        obtain ⟨hne, hin⟩ := Finset.mem_erase.1 ht
        obtain ⟨h1, h2⟩ := Finset.mem_inter.1 hin
        refine le_inf ?_ ?_
        · have : W t = W1 t := by simp [W1, Function.update_of_ne hne]
          rw [this]; exact le_sp W1 h1
        · have : W t = W2 t := by simp [W2, Function.update_of_ne hne]
          rw [this]; exact le_sp W2 h2
      have hmod := Submodule.finrank_sup_add_finrank_inf_eq A1 A2
      have e1 := hall (J1 ∪ J2)
      have e2 := hall ((J1 ∩ J2).erase t0)
      have e3 := Submodule.finrank_mono hsup
      have e4 := Submodule.finrank_mono hinf
      have e5 := Finset.card_erase_of_mem (Finset.mem_inter.2 ⟨hmem1, hmem2⟩)
      have e6 := Finset.card_union_add_card_inter J1 J2
      have e7 : 0 < (J1 ∩ J2).card := Finset.card_pos.2 ⟨t0, Finset.mem_inter.2 ⟨hmem1, hmem2⟩⟩
      omega

/-- RADO'S THEOREM (deficiency form). -/
theorem rado (δ : ℕ) (W : ι → Submodule K U) (hall : Hall δ W) :
    ∃ x : ι → U, (∀ t, x t ∈ W t) ∧ ∃ T0 : Finset ι, Fintype.card ι ≤ T0.card + δ ∧
      LinearIndependent K (fun t : T0 => x t) :=
  rado_aux _ δ W le_rfl hall

end LinRado

end RadoSec

namespace LinCore

abbrev F2 := ZMod 2

lemma f2_sq (a : F2) : a * a = a := by revert a; decide
lemma f2_two (a : F2) : a + a = 0 := by revert a; decide
lemma f2_eq_of_add (a b : F2) (h : a + b = 0) : a = b := by revert a b; decide

variable {n : ℕ}

/-- index set of unordered pairs -/
abbrev Eix (n : ℕ) := {p : Fin n × Fin n // p.1 < p.2}
/-- alternating forms / second exterior power coordinates -/
abbrev Lam (n : ℕ) := Eix n → F2

/-- wedge of two vectors, in pair coordinates -/
def wedge (γ δ : Fin n → F2) : Lam n := fun e => γ e.1.1 * δ e.1.2 + γ e.1.2 * δ e.1.1

/-- the symmetric zero-diagonal matrix of an alternating form -/
def symmat (ω : Lam n) : Matrix (Fin n) (Fin n) F2 := fun i j =>
  if h : i < j then ω ⟨(i, j), h⟩ else if h : j < i then ω ⟨(j, i), h⟩ else 0

lemma symmat_symm (ω : Lam n) (i j : Fin n) : symmat ω i j = symmat ω j i := by
  unfold symmat
  rcases lt_trichotomy i j with h | h | h
  · simp [h, not_lt.2 h.le]
  · subst h; rfl
  · simp [h, not_lt.2 h.le]

lemma symmat_diag (ω : Lam n) (i : Fin n) : symmat ω i i = 0 := by simp [symmat]

lemma symmat_add_apply (ω₁ ω₂ : Lam n) (i j : Fin n) :
    symmat (ω₁ + ω₂) i j = symmat ω₁ i j + symmat ω₂ i j := by
  unfold symmat; split_ifs <;> simp

lemma symmat_smul_apply (a : F2) (ω : Lam n) (i j : Fin n) :
    symmat (a • ω) i j = a * symmat ω i j := by
  unfold symmat; split_ifs <;> simp

lemma symmat_zero_apply (i j : Fin n) : symmat (0 : Lam n) i j = 0 := by
  unfold symmat; split_ifs <;> simp

lemma symmat_add (ω₁ ω₂ : Lam n) : symmat (ω₁ + ω₂) = symmat ω₁ + symmat ω₂ := by
  ext i j; rw [Matrix.add_apply]; exact symmat_add_apply _ _ _ _

lemma symmat_smul (a : F2) (ω : Lam n) : symmat (a • ω) = a • symmat ω := by
  ext i j; rw [Matrix.smul_apply]; exact symmat_smul_apply _ _ _ _

/-- BILINEAR IDENTITY: γ^T S_ω δ = ⟨ω, γ ∧ δ⟩ -/
theorem bil (ω : Lam n) (γ δ : Fin n → F2) :
    γ ⬝ᵥ (symmat ω *ᵥ δ) = ω ⬝ᵥ wedge γ δ := by
  classical
  set ω' : Fin n × Fin n → F2 := fun p => if h : p.1 < p.2 then ω ⟨p, h⟩ else 0 with hω'
  have hL : γ ⬝ᵥ (symmat ω *ᵥ δ) = ∑ p : Fin n × Fin n, γ p.1 * symmat ω p.1 p.2 * δ p.2 := by
    simp only [dotProduct, mulVec, Fintype.sum_prod_type, Finset.mul_sum, mul_assoc]
  set T1 : Fin n × Fin n → F2 := fun p => if p.1 < p.2 then γ p.1 * ω' p * δ p.2 else 0 with hT1
  set T2' : Fin n × Fin n → F2 := fun q => if q.1 < q.2 then γ q.2 * ω' q * δ q.1 else 0 with hT2'
  have hsplit : ∀ p : Fin n × Fin n, γ p.1 * symmat ω p.1 p.2 * δ p.2 = T1 p + T2' p.swap := by
    intro p
    obtain ⟨i, j⟩ := p
    simp only [hT1, hT2', hω', symmat, Prod.swap_prod_mk]
    rcases lt_trichotomy i j with h | h | h
    · simp [h, not_lt.2 h.le]
    · subst h; simp
    · simp [h, not_lt.2 h.le]
  have hR : ω ⬝ᵥ wedge γ δ = ∑ p : Fin n × Fin n, if p.1 < p.2 then
      ω' p * (γ p.1 * δ p.2 + γ p.2 * δ p.1) else 0 := by
    rw [← Finset.sum_filter]
    rw [Finset.sum_subtype (Finset.univ.filter (fun p : Fin n × Fin n => p.1 < p.2))
      (p := fun p : Fin n × Fin n => p.1 < p.2) (by simp)]
    unfold dotProduct wedge
    refine Finset.sum_congr rfl fun e _ => ?_
    simp [hω', e.2]
  rw [hL, hR]
  simp only [hsplit]
  have hswap : ∑ p : Fin n × Fin n, T2' p.swap = ∑ p : Fin n × Fin n, T2' p :=
    Equiv.sum_comp (Equiv.prodComm (Fin n) (Fin n)) T2'
  rw [Finset.sum_add_distrib, hswap, ← Finset.sum_add_distrib]
  refine Finset.sum_congr rfl fun p _ => ?_
  simp only [hT1, hT2']
  split_ifs <;> ring

/-! ## Key lemma -/
section Key

lemma alt_of_quad (A : Matrix (Fin n) (Fin n) F2) (h : ∀ y, y ⬝ᵥ (A *ᵥ y) = 0) :
    (∀ i, A i i = 0) ∧ (∀ i j, A i j = A j i) := by
  have e : ∀ i j, (Pi.single i (1:F2) : Fin n → F2) ⬝ᵥ (A *ᵥ (Pi.single j 1 : Fin n → F2)) = A i j := by
    intro i j; simp [Matrix.mulVec, dotProduct, Pi.single_apply]
  refine ⟨fun i => ?_, fun i j => ?_⟩
  · have := h (Pi.single i 1); rwa [e] at this
  · have hi := h (Pi.single i 1)
    have hj := h (Pi.single j 1)
    have h1 := h (Pi.single i 1 + Pi.single j 1)
    simp only [mulVec_add, dotProduct_add, add_dotProduct, e] at h1
    rw [e] at hi hj
    rw [hi, hj] at h1
    exact f2_eq_of_add _ _ (by rw [add_comm]; simpa using h1)

lemma quad_self (ω : Lam n) (x : Fin n → F2) : x ⬝ᵥ (symmat ω *ᵥ x) = 0 := by
  rw [bil]
  have : wedge x x = 0 := by
    funext e; simp only [wedge, Pi.zero_apply]; rw [mul_comm (x e.1.2)]; exact f2_two _
  rw [this]; simp

lemma hsd (A : Matrix (Fin n) (Fin n) F2) (hA : ∀ i j, A i j = A j i) (u v : Fin n → F2) :
    (A *ᵥ u) ⬝ᵥ v = u ⬝ᵥ (A *ᵥ v) := by
  have : u ᵥ* A = A *ᵥ u := by
    ext a; simp only [Matrix.vecMul, Matrix.mulVec, dotProduct]
    exact Finset.sum_congr rfl fun b _ => by rw [hA, mul_comm]
  rw [Matrix.dotProduct_mulVec, this]

/-- THE KEY LEMMA.  `α j` covectors, `p k` points, M = (α_j · p_k) invertible and in `OrdProp` order,
`Bm` symmetric.  If forms ω_j satisfy S_{ω_j} β_i = 0 for i < j (β = Bm p) and the quadric
Σ_j (α_j·x)(ζ_j·x) vanishes identically (ζ_j = Bm S_j β_j), then every ζ_j = 0. -/
theorem key_zero (Bm : Matrix (Fin n) (Fin n) F2) (hB : ∀ i j, Bm i j = Bm j i)
    (α p : Fin n → Fin n → F2)
    (hMu : IsUnit (Matrix.of fun j k => α j ⬝ᵥ p k).det)
    (hOrd : LinOrd.OrdProp (Matrix.of fun j k => α j ⬝ᵥ p k))
    (ω : Fin n → Lam n)
    (hω : ∀ j i, i < j → symmat (ω j) *ᵥ (Bm *ᵥ p i) = 0)
    (hrel : ∀ x, ∑ j, (α j ⬝ᵥ x) * ((Bm *ᵥ (symmat (ω j) *ᵥ (Bm *ᵥ p j))) ⬝ᵥ x) = 0) :
    ∀ j, Bm *ᵥ (symmat (ω j) *ᵥ (Bm *ᵥ p j)) = 0 := by
  classical
  set 𝒜 : Matrix (Fin n) (Fin n) F2 := Matrix.of α with h𝒜
  set Pm : Matrix (Fin n) (Fin n) F2 := Matrix.of fun a k => p k a with hPm
  set ζ : Fin n → Fin n → F2 := fun j => Bm *ᵥ (symmat (ω j) *ᵥ (Bm *ᵥ p j)) with hζ
  set Z : Matrix (Fin n) (Fin n) F2 := Matrix.of ζ with hZ
  have hM : (Matrix.of fun j k => α j ⬝ᵥ p k) = 𝒜 * Pm := by
    ext j k; simp [h𝒜, hPm, Matrix.mul_apply, dotProduct]
  have hdet : IsUnit 𝒜.det := by
    rw [hM, Matrix.det_mul] at hMu
    exact isUnit_of_mul_isUnit_left hMu
  have hA1 : 𝒜⁻¹ * 𝒜 = 1 := Matrix.nonsing_inv_mul _ hdet
  have hA2 : 𝒜 * 𝒜⁻¹ = 1 := Matrix.mul_nonsing_inv _ hdet
  set N : Matrix (Fin n) (Fin n) F2 := Z * 𝒜⁻¹ with hN
  -- quadratic form of N vanishes
  have hq : ∀ y, y ⬝ᵥ (N *ᵥ y) = 0 := by
    intro y
    set x := 𝒜⁻¹ *ᵥ y with hx
    have h1 : 𝒜 *ᵥ x = y := by rw [hx, Matrix.mulVec_mulVec, hA2, Matrix.one_mulVec]
    have h2 : N *ᵥ y = Z *ᵥ x := by rw [hN, ← Matrix.mulVec_mulVec, ← hx]
    rw [h2, ← h1]
    first
      | exact hrel x
      | (have := hrel x
         simp only [dotProduct, Matrix.mulVec, h𝒜, hZ, Matrix.of_apply, hζ] at this ⊢
         simpa using this)
  obtain ⟨hd, hs⟩ := alt_of_quad N hq
  -- N * M = Z * Pm
  have hNM : N * (Matrix.of fun j k => α j ⬝ᵥ p k) = Z * Pm := by
    rw [hM, hN, Matrix.mul_assoc, ← Matrix.mul_assoc 𝒜⁻¹, hA1, Matrix.one_mul]
  have hZP : ∀ j k, (Z * Pm) j k = ζ j ⬝ᵥ p k := by
    intro j k; simp [hZ, hPm, Matrix.mul_apply, dotProduct]
  have hup : ∀ j k : Fin n, k ≤ j → (N * (Matrix.of fun j k => α j ⬝ᵥ p k)) j k = 0 := by
    intro j k hk
    rw [hNM, hZP]
    have e1 : ζ j ⬝ᵥ p k = (Bm *ᵥ p j) ⬝ᵥ (symmat (ω j) *ᵥ (Bm *ᵥ p k)) := by
      simp only [hζ]
      rw [hsd Bm hB, hsd (symmat (ω j)) (symmat_symm _)]
    rw [e1]
    rcases hk.lt_or_eq with h | h
    · rw [hω j k h]; simp
    · subst h; exact quad_self _ _
  have hN0 : N = 0 :=
    LinOrd.no_alt_upper hOrd N hs hd hup
  intro j
  have hZ0 : Z = 0 := by
    have : Z = N * 𝒜 := by rw [hN, Matrix.mul_assoc, hA1, Matrix.mul_one]
    rw [this, hN0, Matrix.zero_mul]
  funext a
  have := congrFun (congrFun hZ0 j) a
  simpa [hZ, hζ] using this

end Key

/-! ## Section 3: the filtration and the dimension bound -/
section Filt

variable {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- "no extra quadric through the labels": a quadratic form vanishing on every label vanishes everywhere
(P0 injective on the labels). -/
def HInj (c : ι → Fin n → F2) : Prop :=
  ∀ A : Matrix (Fin n) (Fin n) F2, (∀ t, c t ⬝ᵥ (A *ᵥ c t) = 0) → ∀ y, y ⬝ᵥ (A *ᵥ y) = 0

lemma quad_rank1 (a z y : Fin n → F2) :
    y ⬝ᵥ ((Matrix.of fun i j => a i * z j) *ᵥ y) = (a ⬝ᵥ y) * (z ⬝ᵥ y) := by
  simp only [dotProduct, Matrix.mulVec, Matrix.of_apply]
  rw [Finset.sum_mul_sum]
  refine Finset.sum_congr rfl fun i _ => ?_
  rw [Finset.mul_sum]
  refine Finset.sum_congr rfl fun j _ => ?_
  ring

lemma quad_sum {κ : Type*} [Fintype κ] (α ζ : κ → Fin n → F2) (y : Fin n → F2) :
    y ⬝ᵥ ((Matrix.of fun a b => ∑ j, α j a * ζ j b) *ᵥ y) = ∑ j, (α j ⬝ᵥ y) * (ζ j ⬝ᵥ y) := by
  classical
  have key : ∀ s : Finset κ, y ⬝ᵥ ((Matrix.of fun a b => ∑ j ∈ s, α j a * ζ j b) *ᵥ y) =
      ∑ j ∈ s, (α j ⬝ᵥ y) * (ζ j ⬝ᵥ y) := by
    intro s
    induction s using Finset.induction_on with
    | empty =>
      have h0 : (Matrix.of fun (a b : Fin n) => ∑ j ∈ (∅ : Finset κ), α j a * ζ j b) = 0 := by
        ext a b; simp
      rw [h0]; simp
    | insert k s hk ih =>
      have e : (Matrix.of fun a b => ∑ j ∈ insert k s, α j a * ζ j b) =
          (Matrix.of fun i j => α k i * ζ k j) + (Matrix.of fun a b => ∑ j ∈ s, α j a * ζ j b) := by
        ext a b; simp [Finset.sum_insert hk]
      rw [e, Matrix.add_mulVec, dotProduct_add, quad_rank1, ih, Finset.sum_insert hk]
  exact key Finset.univ

/-- the linear map ω ↦ S_ω β_i -/
def SB (Bm : Matrix (Fin n) (Fin n) F2) (p : Fin n → Fin n → F2) (i : Fin n) :
    Lam n →ₗ[F2] (Fin n → F2) where
  toFun ω := symmat ω *ᵥ (Bm *ᵥ p i)
  map_add' ω₁ ω₂ := by
    ext a
    simp only [Matrix.mulVec, dotProduct, Pi.add_apply, symmat_add_apply, add_mul, Finset.sum_add_distrib]
  map_smul' a ω := by
    ext a'
    simp only [Matrix.mulVec, dotProduct, Pi.smul_apply, symmat_smul_apply, smul_eq_mul, RingHom.id_apply,
      Finset.mul_sum, mul_assoc]

/-- ζ_ω = Bm S_ω β_j as a linear map -/
def ZL (Bm : Matrix (Fin n) (Fin n) F2) (p : Fin n → Fin n → F2) (j : Fin n) :
    Lam n →ₗ[F2] (Fin n → F2) := (Matrix.mulVecLin Bm) ∘ₗ SB Bm p j

lemma ZL_apply (Bm : Matrix (Fin n) (Fin n) F2) (p : Fin n → Fin n → F2) (j : Fin n) (ω : Lam n) :
    ZL Bm p j ω = Bm *ᵥ (symmat ω *ᵥ (Bm *ᵥ p j)) := rfl

/-- the filtration Ω^(j) = {ω ∈ Ω : S_ω β_i = 0 for i < j} -/
def Ωf (Bm : Matrix (Fin n) (Fin n) F2) (p : Fin n → Fin n → F2) (Ω : Submodule F2 (Lam n)) (j : ℕ) :
    Submodule F2 (Lam n) := Ω ⊓ ⨅ (i : Fin n) (_ : (i : ℕ) < j), LinearMap.ker (SB Bm p i)

lemma mem_Ωf (Bm : Matrix (Fin n) (Fin n) F2) (p : Fin n → Fin n → F2) (Ω : Submodule F2 (Lam n))
    (j : ℕ) (ω : Lam n) :
    ω ∈ Ωf Bm p Ω j ↔ ω ∈ Ω ∧ ∀ i : Fin n, (i : ℕ) < j → symmat ω *ᵥ (Bm *ᵥ p i) = 0 := by
  simp [Ωf, Submodule.mem_inf, Submodule.mem_iInf, SB]

lemma Ωf_mono (Bm : Matrix (Fin n) (Fin n) F2) (p : Fin n → Fin n → F2) (Ω : Submodule F2 (Lam n))
    {j k : ℕ} (h : j ≤ k) : Ωf Bm p Ω k ≤ Ωf Bm p Ω j := by
  intro ω hω
  rw [mem_Ωf] at hω ⊢
  exact ⟨hω.1, fun i hi => hω.2 i (lt_of_lt_of_le hi h)⟩

lemma Ωf_zero (Bm : Matrix (Fin n) (Fin n) F2) (p : Fin n → Fin n → F2) (Ω : Submodule F2 (Lam n)) :
    Ωf Bm p Ω 0 = Ω := by
  ext ω; rw [mem_Ωf]; simp

/-- the term map Φ_j : ω ↦ (t ↦ (α_j·c_t)(ζ_ω·c_t)) -/
def Φ (Bm : Matrix (Fin n) (Fin n) F2) (α p : Fin n → Fin n → F2) (c : ι → Fin n → F2) (j : Fin n) :
    Lam n →ₗ[F2] (ι → F2) where
  toFun ω := fun t => (α j ⬝ᵥ c t) * (ZL Bm p j ω ⬝ᵥ c t)
  map_add' ω₁ ω₂ := by funext t; simp [map_add, add_dotProduct, mul_add]
  map_smul' a ω := by funext t; simp [map_smul, smul_dotProduct, mul_left_comm]

lemma Φ_apply (Bm : Matrix (Fin n) (Fin n) F2) (α p : Fin n → Fin n → F2) (c : ι → Fin n → F2)
    (j : Fin n) (ω : Lam n) (t : ι) :
    Φ Bm α p c j ω t = (α j ⬝ᵥ c t) * ((Bm *ᵥ (symmat ω *ᵥ (Bm *ᵥ p j))) ⬝ᵥ c t) := rfl

section Hyp
variable (Bm : Matrix (Fin n) (Fin n) F2) (α p : Fin n → Fin n → F2) (c : ι → Fin n → F2)

lemma M_eq : (Matrix.of fun j k => α j ⬝ᵥ p k) =
    Matrix.of α * Matrix.of (fun a k => p k a) := by
  ext j k; simp [Matrix.mul_apply, dotProduct]

lemma units_of_M (hMu : IsUnit (Matrix.of fun j k => α j ⬝ᵥ p k).det) :
    IsUnit (Matrix.of (fun a k => p k a) : Matrix (Fin n) (Fin n) F2).det := by
  rw [M_eq, Matrix.det_mul] at hMu
  exact isUnit_of_mul_isUnit_right hMu

lemma mulVec_zero_of_unit (hBu : IsUnit Bm.det) (u : Fin n → F2) (h : Bm *ᵥ u = 0) : u = 0 := by
  have := congrArg (fun v => Bm⁻¹ *ᵥ v) h
  simpa [Matrix.mulVec_mulVec, Matrix.nonsing_inv_mul _ hBu] using this

/-- the kernel lemma: a vector (ω_j) with ω_j ∈ Ω^(j) and Σ_j Φ_j ω_j = 0 has ω_j ∈ Ω^(j+1). -/
theorem key_ker (hB : ∀ i j, Bm i j = Bm j i) (hBu : IsUnit Bm.det)
    (hMu : IsUnit (Matrix.of fun j k => α j ⬝ᵥ p k).det)
    (hOrd : LinOrd.OrdProp (Matrix.of fun j k => α j ⬝ᵥ p k)) (hInj : HInj c)
    (Ω : Submodule F2 (Lam n)) (x : ∀ j : Fin n, ↥(Ωf Bm p Ω j))
    (hx : ∀ t, ∑ j, Φ Bm α p c j (x j).1 t = 0) :
    ∀ j : Fin n, (x j).1 ∈ Ωf Bm p Ω ((j : ℕ) + 1) := by
  have hω : ∀ j i : Fin n, i < j → symmat (x j).1 *ᵥ (Bm *ᵥ p i) = 0 := by
    intro j i hij
    exact ((mem_Ωf _ _ _ _ _).1 (x j).2).2 i hij
  set ζ : Fin n → Fin n → F2 := fun j => Bm *ᵥ (symmat (x j).1 *ᵥ (Bm *ᵥ p j)) with hζ
  have hrel : ∀ y, ∑ j, (α j ⬝ᵥ y) * (ζ j ⬝ᵥ y) = 0 := by
    intro y
    rw [← quad_sum]
    apply hInj
    intro t
    rw [quad_sum]
    rw [← hx t]
    simp [Φ_apply, hζ]
  have hz := key_zero Bm hB α p hMu hOrd (fun j => (x j).1) hω hrel
  intro j
  rw [mem_Ωf]
  refine ⟨((mem_Ωf _ _ _ _ _).1 (x j).2).1, fun i hi => ?_⟩
  by_cases hij : (i : ℕ) < j
  · exact hω j i hij
  · have : i = j := by
      apply Fin.ext
      have : (i : ℕ) ≤ j := by omega
      omega
    subst this
    exact mulVec_zero_of_unit Bm hBu _ (hz i)

end Hyp

end Filt

/-! ## Section 4: dimension bound, Hall bound, Rado, rank -/
section Dim
variable {ι : Type*} [Fintype ι] [DecidableEq ι]
variable (Bm : Matrix (Fin n) (Fin n) F2) (α p : Fin n → Fin n → F2) (c : ι → Fin n → F2)

lemma Ωf_top (hBu : IsUnit Bm.det) (hMu : IsUnit (Matrix.of fun j k => α j ⬝ᵥ p k).det)
    (Ω : Submodule F2 (Lam n)) : Ωf Bm p Ω n = ⊥ := by
  rw [eq_bot_iff]; intro ω hω
  rw [mem_Ωf] at hω
  have hP := units_of_M α p hMu
  set Pm : Matrix (Fin n) (Fin n) F2 := Matrix.of (fun a k => p k a) with hPm
  have hBP : IsUnit (Bm * Pm).det := by rw [Matrix.det_mul]; exact hBu.mul hP
  have hS : symmat ω * (Bm * Pm) = 0 := by
    ext a i
    have := congrFun (hω.2 i i.2) a
    simpa [Matrix.mul_apply, Matrix.mulVec, dotProduct, hPm] using this
  have h0 : symmat ω = 0 := by
    have := congrArg (fun M => M * (Bm * Pm)⁻¹) hS
    simpa [Matrix.mul_assoc, Matrix.mul_nonsing_inv _ hBP] using this
  have : ω = 0 := by
    funext e
    have := congrFun (congrFun h0 e.1.1) e.1.2
    simpa [symmat, e.2] using this
  simp [this]

/-- the map Ψ : (ω_j)_j ↦ Σ_j Φ_j ω_j -/
def PsiMap (Bm : Matrix (Fin n) (Fin n) F2) (α p : Fin n → Fin n → F2) (c : ι → Fin n → F2)
    (Ω : Submodule F2 (Lam n)) : (∀ j : Fin n, ↥(Ωf Bm p Ω j)) →ₗ[F2] (ι → F2) :=
  ∑ j : Fin n, ((Φ Bm α p c j).comp (Ωf Bm p Ω j).subtype).comp (LinearMap.proj j)

lemma PsiMap_apply (Ω : Submodule F2 (Lam n)) (x : ∀ j : Fin n, ↥(Ωf Bm p Ω j)) (t : ι) :
    PsiMap Bm α p c Ω x t = ∑ j, Φ Bm α p c j (x j).1 t := by
  simp [PsiMap, LinearMap.sum_apply, Finset.sum_apply]

lemma ker_mem (hB : ∀ i j, Bm i j = Bm j i) (hBu : IsUnit Bm.det)
    (hMu : IsUnit (Matrix.of fun j k => α j ⬝ᵥ p k).det)
    (hOrd : LinOrd.OrdProp (Matrix.of fun j k => α j ⬝ᵥ p k)) (hInj : HInj c)
    (Ω : Submodule F2 (Lam n)) (x : LinearMap.ker (PsiMap Bm α p c Ω)) (j : Fin n) :
    (x.1 j).1 ∈ Ωf Bm p Ω ((j : ℕ) + 1) := by
  refine key_ker Bm α p c hB hBu hMu hOrd hInj Ω x.1 ?_ j
  intro t
  rw [← PsiMap_apply]
  exact congrFun (LinearMap.mem_ker.1 x.2) t

/-- the coordinate-j map ker Ψ → Ω^(j+1) -/
def kerMap (hB : ∀ i j, Bm i j = Bm j i) (hBu : IsUnit Bm.det)
    (hMu : IsUnit (Matrix.of fun j k => α j ⬝ᵥ p k).det)
    (hOrd : LinOrd.OrdProp (Matrix.of fun j k => α j ⬝ᵥ p k)) (hInj : HInj c)
    (Ω : Submodule F2 (Lam n)) (j : Fin n) :
    LinearMap.ker (PsiMap Bm α p c Ω) →ₗ[F2] ↥(Ωf Bm p Ω ((j : ℕ) + 1)) :=
  LinearMap.codRestrict (Ωf Bm p Ω ((j : ℕ) + 1))
    (((Ωf Bm p Ω (j : ℕ)).subtype ∘ₗ
        (LinearMap.proj j : (∀ i : Fin n, ↥(Ωf Bm p Ω (i : ℕ))) →ₗ[F2] ↥(Ωf Bm p Ω (j : ℕ))))
      ∘ₗ (LinearMap.ker (PsiMap Bm α p c Ω)).subtype)
    (fun x => by simpa using ker_mem Bm α p c hB hBu hMu hOrd hInj Ω x j)

lemma kerMap_val (hB : ∀ i j, Bm i j = Bm j i) (hBu : IsUnit Bm.det)
    (hMu : IsUnit (Matrix.of fun j k => α j ⬝ᵥ p k).det)
    (hOrd : LinOrd.OrdProp (Matrix.of fun j k => α j ⬝ᵥ p k)) (hInj : HInj c)
    (Ω : Submodule F2 (Lam n)) (j : Fin n) (x : LinearMap.ker (PsiMap Bm α p c Ω)) :
    ((kerMap Bm α p c hB hBu hMu hOrd hInj Ω j x : ↥(Ωf Bm p Ω ((j : ℕ) + 1))) : Lam n) =
      ((x.1 j : ↥(Ωf Bm p Ω (j : ℕ))) : Lam n) := by
  unfold kerMap
  rw [LinearMap.codRestrict_apply]
  rfl

/-- the kernel of Ψ injects into ∏ Ω^(j+1) -/
lemma ker_bound (hB : ∀ i j, Bm i j = Bm j i) (hBu : IsUnit Bm.det)
    (hMu : IsUnit (Matrix.of fun j k => α j ⬝ᵥ p k).det)
    (hOrd : LinOrd.OrdProp (Matrix.of fun j k => α j ⬝ᵥ p k)) (hInj : HInj c)
    (Ω : Submodule F2 (Lam n)) :
    Module.finrank F2 (LinearMap.ker (PsiMap Bm α p c Ω)) ≤
      ∑ j : Fin n, Module.finrank F2 (Ωf Bm p Ω ((j : ℕ) + 1)) := by
  have hg : Function.Injective (LinearMap.pi (kerMap Bm α p c hB hBu hMu hOrd hInj Ω)) := by
    intro x y h
    have h2 : ∀ j : Fin n, ((x.1 j : ↥(Ωf Bm p Ω (j : ℕ))) : Lam n) = ((y.1 j : ↥(Ωf Bm p Ω (j : ℕ))) : Lam n) := by
      intro j
      have h1 := congrArg Subtype.val (congrFun h j)
      rw [LinearMap.pi_apply, LinearMap.pi_apply] at h1
      rw [← kerMap_val Bm α p c hB hBu hMu hOrd hInj Ω j x, ← kerMap_val Bm α p c hB hBu hMu hOrd hInj Ω j y]
      exact h1
    exact Subtype.ext (funext fun j => Subtype.ext (h2 j))
  have := LinearMap.finrank_le_finrank_of_injective hg
  rwa [Module.finrank_pi_fintype] at this

/-- the range of Ψ lives on J^c -/
lemma range_bound (Ω : Submodule F2 (Lam n)) (J : Finset ι)
    (hΩ : ∀ ω ∈ Ω, ∀ (j : Fin n) (t : ι), t ∈ J → Φ Bm α p c j ω t = 0) :
    Module.finrank F2 (LinearMap.range (PsiMap Bm α p c Ω)) ≤ (Jᶜ).card := by
  classical
  let ρ : (ι → F2) →ₗ[F2] (↥(Jᶜ) → F2) := LinearMap.funLeft F2 F2 (Subtype.val : ↥(Jᶜ) → ι)
  have hρ : Function.Injective (ρ.domRestrict (LinearMap.range (PsiMap Bm α p c Ω))) := by
    intro f f' h
    apply Subtype.ext; funext t
    have hz : ∀ f : LinearMap.range (PsiMap Bm α p c Ω), t ∈ J → f.1 t = 0 := by
      intro f ht
      obtain ⟨x, hx⟩ := f.2
      rw [← hx, PsiMap_apply]
      exact Finset.sum_eq_zero fun j _ => hΩ _ (((mem_Ωf _ _ _ _ _).1 (x j).2).1) j t ht
    by_cases ht : t ∈ J
    · rw [hz f ht, hz f' ht]
    · exact congrFun h ⟨t, by simpa using ht⟩
  have := LinearMap.finrank_le_finrank_of_injective hρ
  rw [Module.finrank_fintype_fun_eq_card, Fintype.card_coe] at this
  exact this

lemma telescope (a : ℕ → ℕ) (n : ℕ) :
    ∑ j : Fin n, a (j : ℕ) + a n = a 0 + ∑ j : Fin n, a ((j : ℕ) + 1) := by
  have e1 : ∑ j : Fin n, a (j : ℕ) = ∑ j ∈ Finset.range n, a j := Fin.sum_univ_eq_sum_range a n
  have e2 : ∑ j : Fin n, a ((j : ℕ) + 1) = ∑ j ∈ Finset.range n, a (j + 1) :=
    Fin.sum_univ_eq_sum_range (fun j => a (j + 1)) n
  have e3 := Finset.sum_range_succ a n
  have e4 := Finset.sum_range_succ' a n
  omega

/-- THE DIMENSION BOUND (Rado step, LINEAR56 §3): if every ω ∈ Ω kills all the terms Φ_j(·)(t) at t ∈ J
then dim Ω <= |J^c|. -/
theorem dim_le (hB : ∀ i j, Bm i j = Bm j i) (hBu : IsUnit Bm.det)
    (hMu : IsUnit (Matrix.of fun j k => α j ⬝ᵥ p k).det)
    (hOrd : LinOrd.OrdProp (Matrix.of fun j k => α j ⬝ᵥ p k)) (hInj : HInj c)
    (Ω : Submodule F2 (Lam n)) (J : Finset ι)
    (hΩ : ∀ ω ∈ Ω, ∀ (j : Fin n) (t : ι), t ∈ J → Φ Bm α p c j ω t = 0) :
    Module.finrank F2 Ω ≤ (Jᶜ).card := by
  have hker := ker_bound Bm α p c hB hBu hMu hOrd hInj Ω
  have hrange := range_bound Bm α p c Ω J hΩ
  have hnull := LinearMap.finrank_range_add_finrank_ker (PsiMap Bm α p c Ω)
  rw [Module.finrank_pi_fintype] at hnull
  have htop : Module.finrank F2 (Ωf Bm p Ω n) = 0 := by
    rw [Ωf_top Bm α p hBu hMu]; simp
  have hzero : Module.finrank F2 (Ωf Bm p Ω 0) = Module.finrank F2 Ω := by rw [Ωf_zero]
  have htel := telescope (fun j => Module.finrank F2 (Ωf Bm p Ω j)) n
  omega

end Dim

/-! ## Section 5: Hall bound for the wedge families, transversal, and the rank bound -/
section Hall
variable {ι : Type*} [Fintype ι] [DecidableEq ι]
variable (Bm : Matrix (Fin n) (Fin n) F2) (α p : Fin n → Fin n → F2) (c : ι → Fin n → F2)

/-- wedge as a linear map in the second argument -/
def wedgeL (γ : Fin n → F2) : (Fin n → F2) →ₗ[F2] Lam n where
  toFun δ := wedge γ δ
  map_add' δ₁ δ₂ := by funext e; simp only [wedge, Pi.add_apply]; ring
  map_smul' a δ := by funext e; simp only [wedge, Pi.smul_apply, smul_eq_mul, RingHom.id_apply]; ring

/-- the Rado family: W_t = span_k { γ_t ∧ (a_k(t) β_k) },  γ_t = Bm c_t, a_k(t) = α_k · c_t, β_k = Bm p_k -/
def Wt (t : ι) : Submodule F2 (Lam n) :=
  Submodule.span F2 (Set.range fun k : Fin n => wedge (Bm *ᵥ c t) ((α k ⬝ᵥ c t) • (Bm *ᵥ p k)))

lemma Φ_eq_wedge (hB : ∀ i j, Bm i j = Bm j i) (j : Fin n) (ω : Lam n) (t : ι) :
    Φ Bm α p c j ω t = ω ⬝ᵥ wedge (Bm *ᵥ c t) ((α j ⬝ᵥ c t) • (Bm *ᵥ p j)) := by
  rw [Φ_apply, hsd Bm hB, dotProduct_comm _ (Bm *ᵥ c t), bil]
  have : wedge (Bm *ᵥ c t) ((α j ⬝ᵥ c t) • (Bm *ᵥ p j)) = (α j ⬝ᵥ c t) • wedge (Bm *ᵥ c t) (Bm *ᵥ p j) :=
    map_smul (wedgeL (Bm *ᵥ c t)) _ _
  rw [this, dotProduct_smul, smul_eq_mul]

/-- inner product on Lam as a bilinear map, and the annihilator of a subspace -/
def dotB : Lam n →ₗ[F2] Lam n →ₗ[F2] F2 :=
  LinearMap.mk₂ F2 (fun ω s => ω ⬝ᵥ s) (fun a b s => add_dotProduct _ _ _)
    (fun a ω s => smul_dotProduct _ _ _) (fun ω s s' => dotProduct_add _ _ _)
    (fun a ω s => dotProduct_smul _ _ _)

/-- HALL BOUND: card(pairs) <= dim(sum_{t in J} W_t) + |J^c|. -/
theorem hall_bound (hB : ∀ i j, Bm i j = Bm j i) (hBu : IsUnit Bm.det)
    (hMu : IsUnit (Matrix.of fun j k => α j ⬝ᵥ p k).det)
    (hOrd : LinOrd.OrdProp (Matrix.of fun j k => α j ⬝ᵥ p k)) (hInj : HInj c) (J : Finset ι) :
    Fintype.card (Eix n) ≤ Module.finrank F2 (LinRado.sp (Wt Bm α p c) J) + (Jᶜ).card := by
  classical
  set S := LinRado.sp (Wt Bm α p c) J with hS
  let ev : Lam n →ₗ[F2] (↥S →ₗ[F2] F2) := (LinearMap.lcomp F2 F2 S.subtype).comp dotB
  have hrk : Module.finrank F2 (LinearMap.range ev) ≤ Module.finrank F2 S := by
    have := Submodule.finrank_le (LinearMap.range ev)
    have h2 : Module.finrank F2 (↥S →ₗ[F2] F2) = Module.finrank F2 S := Subspace.dual_finrank_eq
    omega
  have hnull := LinearMap.finrank_range_add_finrank_ker ev
  have hLam : Module.finrank F2 (Lam n) = Fintype.card (Eix n) := by
    simp [Module.finrank_fintype_fun_eq_card]
  have hΩ : ∀ ω ∈ LinearMap.ker ev, ∀ (j : Fin n) (t : ι), t ∈ J → Φ Bm α p c j ω t = 0 := by
    intro ω hω j t ht
    rw [Φ_eq_wedge Bm α p c hB]
    have hmem : wedge (Bm *ᵥ c t) ((α j ⬝ᵥ c t) • (Bm *ᵥ p j)) ∈ S :=
      LinRado.le_sp (Wt Bm α p c) ht (Submodule.subset_span ⟨j, rfl⟩)
    have := congrArg (fun f => f ⟨_, hmem⟩) (LinearMap.mem_ker.1 hω)
    simpa [ev, dotB] using this
  have hd := dim_le Bm α p c hB hBu hMu hOrd hInj (LinearMap.ker ev) J hΩ
  omega

end Hall

/-! ## Section 6: the transversal and the rank bound (Theorem B core) -/
section RankB
variable {ι : Type*} [Fintype ι] [DecidableEq ι]
variable (Bm : Matrix (Fin n) (Fin n) F2) (α p : Fin n → Fin n → F2) (c : ι → Fin n → F2)

/-- Theorem B core: there is a selection y (rows t, indices k) whose matrix
  R[t,s] = (1 + γ_t·c_s) · Σ_k y_{tk} a_k(t) (β_k·c_s)   has rank >= C(n,2). -/
theorem rho_rank (hB : ∀ i j, Bm i j = Bm j i) (hBu : IsUnit Bm.det)
    (hMu : IsUnit (Matrix.of fun j k => α j ⬝ᵥ p k).det)
    (hOrd : LinOrd.OrdProp (Matrix.of fun j k => α j ⬝ᵥ p k)) (hInj : HInj c)
    (hcard : Fintype.card (Eix n) ≤ Fintype.card ι) :
    ∃ y : ι → Fin n → F2, Fintype.card (Eix n) ≤
      (Matrix.of fun t s : ι => (1 + (Bm *ᵥ c t) ⬝ᵥ c s) *
        ∑ k, (y t k * (α k ⬝ᵥ c t)) * ((Bm *ᵥ p k) ⬝ᵥ c s)).rank := by
  classical
  have hall : LinRado.Hall (Fintype.card ι - Fintype.card (Eix n)) (Wt Bm α p c) := by
    intro J
    have h1 := hall_bound Bm α p c hB hBu hMu hOrd hInj J
    have hc : J.card + (Jᶜ).card = Fintype.card ι := Finset.card_add_card_compl J
    omega
  obtain ⟨x, hx, T0, hT0, hli⟩ := LinRado.rado _ _ hall
  have hco : ∀ t, ∃ y : Fin n → F2,
      ∑ k, y k • wedge (Bm *ᵥ c t) ((α k ⬝ᵥ c t) • (Bm *ᵥ p k)) = x t := fun t =>
    (Submodule.mem_span_range_iff_exists_fun F2).1 (hx t)
  choose y hy using hco
  refine ⟨y, ?_⟩
  set δ : ι → Fin n → F2 := fun t => ∑ k, (y t k * (α k ⬝ᵥ c t)) • (Bm *ᵥ p k) with hδ
  have hxδ : ∀ t, x t = wedge (Bm *ᵥ c t) (δ t) := by
    intro t
    rw [← hy t]
    have e : ∀ k, wedge (Bm *ᵥ c t) ((α k ⬝ᵥ c t) • (Bm *ᵥ p k)) =
        (α k ⬝ᵥ c t) • wedgeL (Bm *ᵥ c t) (Bm *ᵥ p k) := fun k => map_smul (wedgeL (Bm *ᵥ c t)) _ _
    have : wedge (Bm *ᵥ c t) (δ t) = wedgeL (Bm *ᵥ c t) (δ t) := rfl
    rw [this, hδ, map_sum]
    refine Finset.sum_congr rfl fun k _ => ?_
    rw [e, map_smul, smul_smul]
  have hδdot : ∀ t s, δ t ⬝ᵥ c s = ∑ k, (y t k * (α k ⬝ᵥ c t)) * ((Bm *ᵥ p k) ⬝ᵥ c s) := by
    intro t s
    calc δ t ⬝ᵥ c s = ∑ x, ∑ k, (y t k * (α k ⬝ᵥ c t)) * ((Bm *ᵥ p k) x * c s x) := by
          simp only [hδ, dotProduct, Finset.sum_apply, Pi.smul_apply, smul_eq_mul, Finset.sum_mul]
          exact Finset.sum_congr rfl fun x _ => Finset.sum_congr rfl fun k _ => by ring
      _ = ∑ k, ∑ x, (y t k * (α k ⬝ᵥ c t)) * ((Bm *ᵥ p k) x * c s x) := Finset.sum_comm
      _ = _ := by simp only [dotProduct, Finset.mul_sum]
  set Rm : Matrix ι ι F2 := Matrix.of fun t s : ι => (1 + (Bm *ᵥ c t) ⬝ᵥ c s) *
        ∑ k, (y t k * (α k ⬝ᵥ c t)) * ((Bm *ᵥ p k) ⬝ᵥ c s) with hRm
  have hRm' : ∀ t s, Rm t s = (1 + (Bm *ᵥ c t) ⬝ᵥ c s) * (δ t ⬝ᵥ c s) := by
    intro t s; simp [hRm, hδdot]
  have hindep : LinearIndependent F2 (fun t : T0 => Rm t.1) := by
    rw [Fintype.linearIndependent_iff]
    intro g hg
    set A : Matrix (Fin n) (Fin n) F2 := Matrix.diagonal (fun a => ∑ t : T0, g t * δ t.1 a) +
      Matrix.of (fun a b => ∑ t : T0, (g t * (Bm *ᵥ c t.1) a) * δ t.1 b) with hA
    have hQ : ∀ z : Fin n → F2, z ⬝ᵥ (A *ᵥ z) =
        ∑ t : T0, g t * ((1 + (Bm *ᵥ c t.1) ⬝ᵥ z) * (δ t.1 ⬝ᵥ z)) := by
      intro z
      rw [hA, Matrix.add_mulVec, dotProduct_add]
      have h1 : z ⬝ᵥ (Matrix.diagonal (fun a => ∑ t : T0, g t * δ t.1 a) *ᵥ z) =
          ∑ t : T0, g t * (δ t.1 ⬝ᵥ z) := by
        simp only [dotProduct, Matrix.mulVec_diagonal, Finset.sum_mul, Finset.mul_sum]
        rw [Finset.sum_comm]
        refine Finset.sum_congr rfl fun t _ => ?_
        refine Finset.sum_congr rfl fun a _ => ?_
        have := f2_sq (z a)
        calc z a * (g t * δ t.1 a * z a) = g t * δ t.1 a * (z a * z a) := by ring
          _ = _ := by rw [this]; ring
      have h2 := quad_sum (fun (t : T0) a => g t * (Bm *ᵥ c t.1) a) (fun (t : T0) b => δ t.1 b) z
      rw [h1, h2, ← Finset.sum_add_distrib]
      refine Finset.sum_congr rfl fun t _ => ?_
      have hd : (fun a => g t * (Bm *ᵥ c t.1) a) ⬝ᵥ z = g t * ((Bm *ᵥ c t.1) ⬝ᵥ z) := by
        simp [dotProduct, Finset.mul_sum, mul_assoc]
      show g t * (δ t.1 ⬝ᵥ z) + ((fun a => g t * (Bm *ᵥ c t.1) a) ⬝ᵥ z) * (δ t.1 ⬝ᵥ z) = _
      rw [hd]; ring
    have hvan : ∀ s, c s ⬝ᵥ (A *ᵥ c s) = 0 := by
      intro s
      rw [hQ]
      have := congrFun hg s
      simp only [Finset.sum_apply, Pi.smul_apply, smul_eq_mul, Pi.zero_apply, hRm'] at this
      simpa [mul_assoc] using this
    obtain ⟨_, hsym⟩ := alt_of_quad A (hInj A hvan)
    have hsumx : ∑ t : T0, g t • x t.1 = 0 := by
      funext e
      have h := hsym e.1.1 e.1.2
      have hne : e.1.1 ≠ e.1.2 := ne_of_lt e.2
      simp only [hA, Matrix.add_apply, Matrix.diagonal_apply, Matrix.of_apply, hne, hne.symm,
        if_false, zero_add] at h
      simp only [Finset.sum_apply, Pi.smul_apply, smul_eq_mul, hxδ, wedge, Pi.zero_apply]
      have h2 : ∑ t : T0, g t * ((Bm *ᵥ c t.1) e.1.1 * δ t.1 e.1.2 + (Bm *ᵥ c t.1) e.1.2 * δ t.1 e.1.1)
          = ∑ t : T0, g t * (Bm *ᵥ c t.1) e.1.1 * δ t.1 e.1.2 +
            ∑ t : T0, g t * (Bm *ᵥ c t.1) e.1.2 * δ t.1 e.1.1 := by
        rw [← Finset.sum_add_distrib]
        refine Finset.sum_congr rfl fun t _ => ?_; ring
      rw [h2, h]
      exact f2_two _
    exact fun t => Fintype.linearIndependent_iff.1 hli g hsumx t
  have hrk : T0.card ≤ Rm.rank := by
    rw [Matrix.rank_eq_finrank_span_row]
    have h1 := finrank_span_eq_card hindep
    have h2 : Submodule.span F2 (Set.range fun t : T0 => Rm t.1) ≤
        Submodule.span F2 (Set.range Rm.row) :=
      Submodule.span_mono (by rintro _ ⟨t, rfl⟩; exact ⟨t.1, rfl⟩)
    have h3 := Submodule.finrank_mono h2
    rw [Fintype.card_coe] at h1
    omega
  omega


/-- Theorem B core without the ordering hypothesis: only M = (α_j · p_k) invertible. -/
theorem rho_rank_unit (hB : ∀ i j, Bm i j = Bm j i) (hBu : IsUnit Bm.det)
    (hMu : IsUnit (Matrix.of fun j k => α j ⬝ᵥ p k).det) (hInj : HInj c)
    (hcard : Fintype.card (Eix n) ≤ Fintype.card ι) :
    ∃ y : ι → Fin n → F2, Fintype.card (Eix n) ≤
      (Matrix.of fun t s : ι => (1 + (Bm *ᵥ c t) ⬝ᵥ c s) *
        ∑ k, (y t k * (α k ⬝ᵥ c t)) * ((Bm *ᵥ p k) ⬝ᵥ c s)).rank := by
  classical
  have hrk : n ≤ (Matrix.of fun j k => α j ⬝ᵥ p k).rank + 1 := by
    have := Matrix.rank_of_isUnit (Matrix.of fun j k => α j ⬝ᵥ p k)
      ((Matrix.isUnit_iff_isUnit_det _).2 hMu)
    simp at this; omega
  obtain ⟨e, he⟩ := LinOrd.exists_ordering n (Fin n) (by simp) (Matrix.of fun j k => α j ⬝ᵥ p k) hrk
  have hM' : (Matrix.of fun j k => (α ∘ e) j ⬝ᵥ (p ∘ e) k) =
      (Matrix.of fun j k => α j ⬝ᵥ p k).submatrix e e := by ext j k; rfl
  have hdet' : IsUnit (Matrix.of fun j k => (α ∘ e) j ⬝ᵥ (p ∘ e) k).det := by
    rw [hM', Matrix.det_submatrix_equiv_self]; exact hMu
  obtain ⟨y', hy'⟩ := rho_rank Bm (α ∘ e) (p ∘ e) c hB hBu hdet' (by rw [hM']; exact he) hInj hcard
  refine ⟨fun t k => y' t (e.symm k), ?_⟩
  convert hy' using 3
  ext t s
  simp only [Matrix.of_apply, Function.comp]
  congr 1
  rw [← Equiv.sum_comp e]
  simp

end RankB

end LinCore
