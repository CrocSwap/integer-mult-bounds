import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.LinearAlgebra.Matrix.BilinearForm
import Mathlib.LinearAlgebra.BilinearForm.Orthogonal
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.LinearAlgebra.Dimension.StrongRankCondition
import Mathlib.Data.Nat.Choose.Basic
import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.Field.ZMod
import Mathlib.Order.WellFounded
import Mathlib.Tactic.LinearCombination
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Order.Interval.Finset.Fin
import Mathlib.Algebra.BigOperators.Intervals
import Mathlib.Order.Preorder.Finite
/-!
NETNG (lane LEANNG, Nov 20).  Kernel-only.  THEOREM NG of cards/WILD/NOVEL/net2dec/N2D.md sec 1, mod-4 form.
Model `Net4`: ports ι with odd-weight labels q_p ∈ F2^h, nodes κ with a DAG order `lt`, subspaces b_k ≤ a_k,
F,G,H,N matrices over Z/4 (the reduction of a 2-adically integral network), N = (1-H)^{-1} (two-sided), M = G N F,
M∘Q = diag(c) on odd cells, c_s ≠ 0 in Z/4 (⇔ v_2(c_s) ≤ 1).  Drop d_k = dim a_k - dim b_k.
 ng_fwd : n ≤ Σ_k [C(d_k+1,2) + ι_k d_k (h - dim a_k)]          ι_k = [k receives a relay]
 ng_mir : n ≤ Σ_k [C(d_k+1,2) + o_k d_k dim b_k]                o_k = [k sends a relay]   (dual network)
 ng_sum : 2n ≤ (h+1)·D;  ng_P104 : n=104,h=9 ⇒ D ≥ 21.
-/
open Matrix Finset Module
namespace NetNG

/-- Lifting lemma: if the rows `c_t e_t` (c_t ≠ 0 in Z/4) of diag(c) lie in the Z/4-span of a finset Γ of
vectors, then n ≤ |Γ|.  (Lift to ℤ, multiply unit rows by 2, halve: A ≡ I mod 2, so det ≠ 0 but rank ≤ |Γ|.) -/
theorem lift_rank {ι : Type*} [Fintype ι] [DecidableEq ι] (Γ : Finset (ι → ZMod 4))
    (c : ι → ZMod 4) (hc : ∀ t, c t ≠ 0)
    (hspan : ∀ t, (Pi.single t (c t) : ι → ZMod 4) ∈ Submodule.span (ZMod 4) (Γ : Set (ι → ZMod 4))) :
    Fintype.card ι ≤ Γ.card := by
  classical
  choose Λ hΛ using fun t => (Submodule.mem_span_finset).1 (hspan t)
  -- e t : 2 if c t odd, 1 if c t = 2
  let e : ι → ℤ := fun t => if c t = 2 then 1 else 2
  let P : Matrix ι Γ ℤ := fun t γ => e t * ((Λ t γ.1).val : ℤ)
  let S : Matrix Γ ι ℤ := fun γ p => ((γ.1 p).val : ℤ)
  let R : Matrix ι ι ℤ := P * S
  have hcast : ∀ t p, ((R t p : ℤ) : ZMod 4) = if t = p then 2 else 0 := by
    intro t p
    have h1 : ∑ γ ∈ Γ, Λ t γ • γ = Pi.single t (c t) := (hΛ t).2
    have h2 := congrFun h1 p
    simp only [Finset.sum_apply, Pi.smul_apply, smul_eq_mul] at h2
    have h3 : ((R t p : ℤ) : ZMod 4) = (e t : ZMod 4) * ∑ γ ∈ Γ, Λ t γ * γ p := by
      rw [show R t p = ∑ γ : Γ, P t γ * S γ p from Matrix.mul_apply]
      simp only [P, S, Int.cast_sum, Int.cast_mul, Int.cast_natCast, ZMod.natCast_zmod_val, Finset.mul_sum]
      rw [← Finset.sum_coe_sort Γ (fun γ => (e t : ZMod 4) * (Λ t γ * γ p))]
      refine Finset.sum_congr rfl fun γ _ => ?_
      ring
    rw [h3, h2]
    by_cases htp : t = p
    · subst htp
      simp only [Pi.single_eq_same, if_true, e]
      have := hc t
      revert this; generalize c t = x; revert x; decide
    · simp [Pi.single_apply, htp]
  have hdiv : ∀ t p, (4 : ℤ) ∣ (if t = p then (2:ℤ) else 0) - R t p := by
    intro t p
    have := hcast t p
    have h5 : ((R t p : ℤ) : ZMod 4) = (((if t = p then (2:ℤ) else 0) : ℤ) : ZMod 4) := by
      rw [this]; split_ifs <;> simp
    have := (ZMod.intCast_eq_intCast_iff_dvd_sub _ _ 4).1 h5
    simpa using this
  choose Q hQ using fun t p => hdiv t p
  let A : Matrix ι ι ℤ := Matrix.of fun t p => (if t = p then 1 else 0) - 2 * Q t p
  have hRA : R = (2 : ℤ) • A := by
    ext t p
    have := hQ t p
    simp only [A, Matrix.smul_apply, Matrix.of_apply, smul_eq_mul]
    split_ifs at this ⊢ <;> omega
  have hA2 : (Int.castRingHom (ZMod 2)).mapMatrix A = 1 := by
    ext t p
    have h2 : (2 : ZMod 2) = 0 := by decide
    simp only [RingHom.mapMatrix_apply, Matrix.map_apply, A, Matrix.of_apply, Matrix.one_apply]
    by_cases htp : t = p
    · simp [htp, h2]
    · simp [htp, h2]
  have hdetA : A.det ≠ 0 := by
    intro h0
    have := (Int.castRingHom (ZMod 2)).map_det A
    rw [hA2, h0] at this
    simp at this
  have hdetR : R.det ≠ 0 := by
    rw [hRA, Matrix.det_smul]
    exact mul_ne_zero (pow_ne_zero _ (by norm_num)) hdetA
  -- rank over ℚ
  let RQ : Matrix ι ι ℚ := R.map (Int.cast : ℤ → ℚ)
  have hdetQ : IsUnit RQ.det := by
    have : RQ.det = ((R.det : ℤ) : ℚ) := by
      have := (Int.castRingHom ℚ).map_det R
      simpa [RQ, RingHom.mapMatrix_apply] using this.symm
    rw [this]
    exact isUnit_iff_ne_zero.2 (by exact_mod_cast hdetR)
  have hr1 := Matrix.rank_of_isUnit RQ ((Matrix.isUnit_iff_isUnit_det _).2 hdetQ)
  have hr2 : RQ.rank ≤ Fintype.card Γ := by
    have : RQ = P.map (Int.cast : ℤ → ℚ) * S.map (Int.cast : ℤ → ℚ) :=
      Matrix.map_mul (f := Int.castRingHom ℚ)
    rw [this]
    exact (Matrix.rank_mul_le_left _ _).trans (Matrix.rank_le_card_width _)
  have := hr1 ▸ hr2
  simpa using this

/-! ## F2 geometry -/
abbrev V (h : ℕ) := Fin h → ZMod 2

def perp {h : ℕ} (W : Submodule (ZMod 2) (V h)) : Submodule (ZMod 2) (V h) where
  carrier := {y | ∀ x ∈ W, x ⬝ᵥ y = 0}
  add_mem' := by
    intro a b ha hb x hx
    simp [dotProduct_add, ha x hx, hb x hx]
  zero_mem' := by intro x hx; simp
  smul_mem' := by
    intro c y hy x hx
    simp [dotProduct_smul, hy x hx]

theorem mem_perp {h : ℕ} {W : Submodule (ZMod 2) (V h)} {y : V h} :
    y ∈ perp W ↔ ∀ x ∈ W, x ⬝ᵥ y = 0 := Iff.rfl

theorem perp_anti {h : ℕ} {W W' : Submodule (ZMod 2) (V h)} (hle : W ≤ W') : perp W' ≤ perp W :=
  fun _ hy x hx => hy x (hle hx)

noncomputable def Bd (h : ℕ) : LinearMap.BilinForm (ZMod 2) (V h) :=
  Matrix.toBilin' (1 : Matrix (Fin h) (Fin h) (ZMod 2))

theorem Bd_apply {h : ℕ} (x y : V h) : Bd h x y = x ⬝ᵥ y := by
  simp [Bd, Matrix.toBilin'_apply']

theorem finrank_perp {h : ℕ} (W : Submodule (ZMod 2) (V h)) :
    finrank (ZMod 2) (perp W) + finrank (ZMod 2) W = h := by
  have hk : LinearMap.ker (Bd h) = ⊥ := by
    rw [LinearMap.ker_eq_bot']
    intro x hx
    funext i
    have := congrArg (fun f => f (Pi.single i 1)) hx
    simpa [Bd_apply, dotProduct, Pi.single_apply] using this
  have e : perp W = (Bd h).orthogonal W := by
    ext y
    rw [LinearMap.BilinForm.mem_orthogonal_iff]
    simp only [mem_perp, LinearMap.IsOrtho, Bd_apply]
  have := LinearMap.BilinForm.finrank_add_finrank_orthogonal' (B := Bd h) W
  rw [hk, inf_bot_eq, finrank_bot] at this
  have h9 : finrank (ZMod 2) (V h) = h := by simp
  rw [e]; omega

theorem finrank_le_h {h : ℕ} (W : Submodule (ZMod 2) (V h)) : finrank (ZMod 2) W ≤ h := by
  have := finrank_perp W; omega

/-! ## chart images over Z/4 -/
section chart
variable {ι : Type*} {h : ℕ} (q : ι → V h)

def chi (v : V h) (p : ι) : ZMod 4 := if v ⬝ᵥ q p = 0 then 0 else 1
def T (x : ι → ZMod 4) (v : V h) : ι → ZMod 4 := fun p => chi q v p * x p
def Bf (x : ι → ZMod 4) (v w : V h) : ι → ZMod 4 := fun p => 2 * (chi q v p * chi q w p) * x p

theorem chi_add (v w : V h) (p : ι) :
    chi q (v + w) p = chi q v p + chi q w p - 2 * (chi q v p * chi q w p) := by
  unfold chi
  rw [add_dotProduct]
  generalize v ⬝ᵥ q p = x
  generalize w ⬝ᵥ q p = y
  revert x y; decide

theorem chi_zero (p : ι) : chi q 0 p = 0 := by simp [chi]

theorem chi_sq (v : V h) (p : ι) : chi q v p * chi q v p = chi q v p := by
  unfold chi; split_ifs <;> simp

theorem T_add (x : ι → ZMod 4) (v w : V h) : T q x (v + w) = T q x v + T q x w - Bf q x v w := by
  funext p
  simp only [T, Bf, Pi.add_apply, Pi.sub_apply, chi_add]
  ring

theorem T_zero (x : ι → ZMod 4) : T q x 0 = 0 := by
  funext p; simp [T, chi_zero]

theorem Bf_zero_left (x : ι → ZMod 4) (w : V h) : Bf q x 0 w = 0 := by
  funext p; simp [Bf, chi_zero]

theorem Bf_comm (x : ι → ZMod 4) (v w : V h) : Bf q x v w = Bf q x w v := by
  funext p; simp only [Bf]; ring

theorem Bf_zero_right (x : ι → ZMod 4) (v : V h) : Bf q x v 0 = 0 := by
  rw [Bf_comm, Bf_zero_left]

theorem Bf_add_left (x : ι → ZMod 4) (v v' w : V h) :
    Bf q x (v + v') w = Bf q x v w + Bf q x v' w := by
  funext p
  simp only [Bf, Pi.add_apply, chi_add]
  have h4 : (4 : ZMod 4) = 0 := by decide
  linear_combination (-(chi q v p * chi q v' p * chi q w p * x p)) * h4

theorem Bf_add_right (x : ι → ZMod 4) (v w w' : V h) :
    Bf q x v (w + w') = Bf q x v w + Bf q x v w' := by
  rw [Bf_comm, Bf_add_left, Bf_comm q x w v, Bf_comm q x w' v]

theorem Bf_self (x : ι → ZMod 4) (v : V h) : Bf q x v v = (2 : ZMod 4) • T q x v := by
  funext p
  simp only [Bf, T, Pi.smul_apply, smul_eq_mul]
  rw [chi_sq]; ring

theorem Bf_eq (x : ι → ZMod 4) (v w : V h) : Bf q x v w = T q x v + T q x w - T q x (v + w) := by
  rw [T_add]; abel

theorem Bf_of_T_zero (x : ι → ZMod 4) (v w : V h) (h0 : T q x v = 0) : Bf q x v w = 0 := by
  funext p
  have := congrFun h0 p
  simp only [T, Pi.zero_apply] at this
  simp only [Bf, Pi.zero_apply]
  calc 2 * (chi q v p * chi q w p) * x p = 2 * chi q w p * (chi q v p * x p) := by ring
    _ = 0 := by rw [this]; ring

theorem zmod2_cases (a : ZMod 2) : a = 0 ∨ a = 1 := by revert a; decide

/-- span lemma: generators T(e_i), B(e_i,e_j) in S ⇒ T(v) ∈ S on the whole F2-span. -/
theorem T_mem_of_span {κ : Type*} (S : Submodule (ZMod 4) (ι → ZMod 4)) (e : κ → V h)
    (x : ι → ZMod 4) (hT : ∀ i, T q x (e i) ∈ S) (hB : ∀ i j, Bf q x (e i) (e j) ∈ S) :
    ∀ v ∈ Submodule.span (ZMod 2) (Set.range e), T q x v ∈ S := by
  have hB' : ∀ v ∈ Submodule.span (ZMod 2) (Set.range e), ∀ w ∈ Submodule.span (ZMod 2) (Set.range e),
      Bf q x v w ∈ S := by
    intro v hv
    refine Submodule.span_induction (p := fun v _ => ∀ w ∈ Submodule.span (ZMod 2) (Set.range e),
      Bf q x v w ∈ S) ?_ ?_ ?_ ?_ hv
    · rintro _ ⟨i, rfl⟩ w hw
      refine Submodule.span_induction (p := fun w _ => Bf q x (e i) w ∈ S) ?_ ?_ ?_ ?_ hw
      · rintro _ ⟨j, rfl⟩; exact hB i j
      · rw [Bf_zero_right]; exact S.zero_mem
      · intro w w' _ _ h1 h2; rw [Bf_add_right]; exact S.add_mem h1 h2
      · intro a w _ h1
        rcases zmod2_cases a with rfl | rfl
        · rw [zero_smul, Bf_zero_right]; exact S.zero_mem
        · rw [one_smul]; exact h1
    · intro w hw; rw [Bf_zero_left]; exact S.zero_mem
    · intro v v' _ _ h1 h2 w hw
      rw [Bf_add_left]; exact S.add_mem (h1 w hw) (h2 w hw)
    · intro a v _ h1 w hw
      rcases zmod2_cases a with rfl | rfl
      · rw [zero_smul, Bf_zero_left]; exact S.zero_mem
      · rw [one_smul]; exact h1 w hw
  intro v hv
  refine Submodule.span_induction (p := fun v _ => T q x v ∈ S) ?_ ?_ ?_ ?_ hv
  · rintro _ ⟨i, rfl⟩; exact hT i
  · rw [T_zero]; exact S.zero_mem
  · intro v v' hv hv' h1 h2
    rw [T_add]; exact S.sub_mem (S.add_mem h1 h2) (hB' v hv v' hv')
  · intro a v _ h1
    rcases zmod2_cases a with rfl | rfl
    · rw [zero_smul, T_zero]; exact S.zero_mem
    · rw [one_smul]; exact h1
end chart

theorem card_lt_pairs (d : ℕ) :
    (Finset.univ.filter (fun pr : Fin d × Fin d => pr.1 < pr.2)).card = d.choose 2 := by
  rw [Finset.card_filter, Fintype.sum_prod_type_right]
  have : ∀ b : Fin d, ∑ a : Fin d, (if a < b then 1 else 0) = (b : ℕ) := by
    intro b
    rw [← Finset.card_filter]
    rw [show (Finset.univ.filter fun a : Fin d => a < b) = Finset.Iio b by ext; simp]
    simp
  simp only [this]
  rw [Fin.sum_univ_eq_sum_range (fun i => i) d, Finset.sum_range_id, Nat.choose_two_right]

theorem choose_succ_two (d : ℕ) : (d + 1).choose 2 = d + d.choose 2 := by
  rw [Nat.choose_succ_succ, Nat.choose_one_right]

/-! ## the network model -/
structure Net4 (ι κ : Type*) [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ] (h : ℕ) where
  q : ι → V h
  hodd : ∀ p, q p ⬝ᵥ q p = 1
  lt : κ → κ → Prop
  ltrans : ∀ a b c, lt a b → lt b c → lt a c
  lirr : ∀ a, ¬ lt a a
  a : κ → Submodule (ZMod 2) (V h)
  b : κ → Submodule (ZMod 2) (V h)
  F : Matrix κ ι (ZMod 4)
  G : Matrix ι κ (ZMod 4)
  H : Matrix κ κ (ZMod 4)
  N : Matrix κ κ (ZMod 4)
  c : ι → ZMod 4
  hba : ∀ k, b k ≤ a k
  hF : ∀ k p, F k p ≠ 0 → q p ∈ a k
  hG : ∀ s k, G s k ≠ 0 → ∀ y ∈ b k, y ⬝ᵥ q s = 0
  hHlt : ∀ k j, H k j ≠ 0 → lt j k
  hH : ∀ k j, H k j ≠ 0 → b j ≤ a k
  hN1 : N = 1 + H * N
  hN2 : N = 1 + N * H
  hc : ∀ s, c s ≠ 0
  hM : ∀ s p, q s ⬝ᵥ q p = 1 → (G * N * F) s p = if s = p then c s else 0

section net
variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ] {h : ℕ}

noncomputable def Net4.drop (Nt : Net4 ι κ h) (k : κ) : ℕ :=
  finrank (ZMod 2) (Nt.a k) - finrank (ZMod 2) (Nt.b k)

/-- k receives a relay. -/
def Net4.relayIn (Nt : Net4 ι κ h) (k : κ) : Prop := ∃ j, Nt.H k j ≠ 0

open Classical in
/-- the forward bound's per-node term. -/
noncomputable def Net4.fwdTerm (Nt : Net4 ι κ h) (k : κ) : ℕ :=
  (Nt.drop k + 1).choose 2 +
    (if Nt.relayIn k then Nt.drop k * (h - finrank (ZMod 2) (Nt.a k)) else 0)

/-- row k of N F. -/
def Net4.r (Nt : Net4 ι κ h) (k : κ) : ι → ZMod 4 := fun p => (Nt.N * Nt.F) k p

theorem Net4.hr (Nt : Net4 ι κ h) (k : κ) (p : ι) :
    Nt.r k p = Nt.F k p + ∑ j, Nt.H k j * Nt.r j p := by
  have e : Nt.N * Nt.F = Nt.F + Nt.H * (Nt.N * Nt.F) := by
    calc Nt.N * Nt.F = (1 + Nt.H * Nt.N) * Nt.F := by rw [← Nt.hN1]
      _ = _ := by rw [Matrix.add_mul, Matrix.one_mul, Matrix.mul_assoc]
  have := congrFun (congrFun e k) p
  simpa [Net4.r, Matrix.add_apply, Matrix.mul_apply] using this

/-- the Z/4-module of chart images at node k. -/
def Net4.Pi (Nt : Net4 ι κ h) (k : κ) : Submodule (ZMod 4) (ι → ZMod 4) :=
  Submodule.span (ZMod 4) {x | ∃ v ∈ perp (Nt.b k), x = T Nt.q (Nt.r k) v}

theorem Net4.chi_F (Nt : Net4 ι κ h) (k : κ) (u : V h) (hu : u ∈ perp (Nt.a k)) (p : ι) :
    chi Nt.q u p * Nt.F k p = 0 := by
  by_cases hF : Nt.F k p = 0
  · simp [hF]
  · have := hu _ (Nt.hF k p hF)
    rw [dotProduct_comm] at this
    simp [chi, this]

theorem Net4.T_row (Nt : Net4 ι κ h) (k : κ) (u : V h) (hu : u ∈ perp (Nt.a k)) :
    T Nt.q (Nt.r k) u = ∑ j, Nt.H k j • T Nt.q (Nt.r j) u := by
  funext p
  simp only [T, Finset.sum_apply, Pi.smul_apply, smul_eq_mul]
  rw [Nt.hr k p, mul_add, Nt.chi_F k u hu p, zero_add, Finset.mul_sum]
  refine Finset.sum_congr rfl fun j _ => ?_
  ring

theorem Net4.T_row_zero (Nt : Net4 ι κ h) (k : κ) (hno : ¬ Nt.relayIn k) (u : V h)
    (hu : u ∈ perp (Nt.a k)) : T Nt.q (Nt.r k) u = 0 := by
  rw [Nt.T_row k u hu]
  refine Finset.sum_eq_zero fun j _ => ?_
  have : Nt.H k j = 0 := by
    by_contra hne; exact hno ⟨j, hne⟩
  simp [this]

theorem Net4.node_gens (Nt : Net4 ι κ h) (k : κ) :
    ∃ Γ : Finset (ι → ZMod 4), Γ.card ≤ Nt.fwdTerm k ∧
      ∀ S : Submodule (ZMod 4) (ι → ZMod 4), (∀ j, Nt.H k j ≠ 0 → Nt.Pi j ≤ S) →
        (↑Γ : Set (ι → ZMod 4)) ⊆ S → Nt.Pi k ≤ S := by
  classical
  set A := perp (Nt.a k) with hA
  set Bs := perp (Nt.b k) with hBs
  have hAB : A ≤ Bs := perp_anti (Nt.hba k)
  obtain ⟨C, hC⟩ := exists_isCompl A
  set W := Bs ⊓ C with hW
  have hsup : A ⊔ W = Bs := by
    apply le_antisymm
    · exact sup_le hAB inf_le_left
    · intro v hv
      have : v ∈ A ⊔ C := by rw [hC.sup_eq_top]; trivial
      obtain ⟨x, hx, y, hy, rfl⟩ := Submodule.mem_sup.1 this
      refine Submodule.mem_sup.2 ⟨x, hx, y, ⟨?_, hy⟩, rfl⟩
      have : y = (x + y) - x := by abel
      rw [this]; exact Bs.sub_mem hv (hAB hx)
  have hdisj : A ⊓ W = ⊥ := by
    apply eq_bot_iff.2
    calc A ⊓ W ≤ A ⊓ C := inf_le_inf_left _ inf_le_right
      _ = ⊥ := hC.inf_eq_bot
      _ ≤ ⊥ := le_rfl
  have hrk := Submodule.finrank_sup_add_finrank_inf_eq A W
  rw [hsup, hdisj, finrank_bot] at hrk
  have p1 : finrank (ZMod 2) A + finrank (ZMod 2) (Nt.a k) = h := finrank_perp _
  have p2 : finrank (ZMod 2) Bs + finrank (ZMod 2) (Nt.b k) = h := finrank_perp _
  have hle := Submodule.finrank_mono (Nt.hba k)
  have hfa := finrank_le_h (Nt.a k)
  have hdW : finrank (ZMod 2) W = Nt.drop k := by unfold Net4.drop; omega
  have hdA : finrank (ZMod 2) A = h - finrank (ZMod 2) (Nt.a k) := by omega
  obtain ⟨f, hfmem, hfspan, -⟩ := Submodule.exists_fun_fin_finrank_span_eq (ZMod 2) (A : Set (V h))
  obtain ⟨g, hgmem, hgspan, -⟩ := Submodule.exists_fun_fin_finrank_span_eq (ZMod 2) (W : Set (V h))
  have hfspan' : Submodule.span (ZMod 2) (Set.range f) = A := hfspan.trans (Submodule.span_eq A)
  have hgspan' : Submodule.span (ZMod 2) (Set.range g) = W := hgspan.trans (Submodule.span_eq W)
  have hm : finrank (ZMod 2) (Submodule.span (ZMod 2) (A : Set (V h))) = h - finrank (ZMod 2) (Nt.a k) := by
    rw [Submodule.span_eq]; exact hdA
  have hd : finrank (ZMod 2) (Submodule.span (ZMod 2) (W : Set (V h))) = Nt.drop k := by
    rw [Submodule.span_eq]; exact hdW
  let ΓT : Finset (ι → ZMod 4) := Finset.univ.image fun a => T Nt.q (Nt.r k) (g a)
  let ΓC : Finset (ι → ZMod 4) :=
    (Finset.univ.filter (fun pr : Fin _ × Fin _ => pr.1 < pr.2)).image
      fun pr => Bf Nt.q (Nt.r k) (g pr.1) (g pr.2)
  let ΓX : Finset (ι → ZMod 4) :=
    if Nt.relayIn k then (Finset.univ : Finset (Fin _ × Fin _)).image
      (fun pr => Bf Nt.q (Nt.r k) (f pr.1) (g pr.2)) else ∅
  refine ⟨ΓT ∪ ΓC ∪ ΓX, ?_, ?_⟩
  · have c1 : ΓT.card ≤ Nt.drop k := by
      refine Finset.card_image_le.trans ?_
      simp [hd]
    have c2 : ΓC.card ≤ (Nt.drop k).choose 2 := by
      refine Finset.card_image_le.trans ?_
      rw [card_lt_pairs, hd]
    have c3 : ΓX.card ≤ (if Nt.relayIn k then Nt.drop k * (h - finrank (ZMod 2) (Nt.a k)) else 0) := by
      by_cases hr : Nt.relayIn k
      · simp only [ΓX, if_pos hr]
        refine Finset.card_image_le.trans ?_
        simp [hd, hm, mul_comm]
      · simp [ΓX, hr]
    have := Finset.card_union_le (ΓT ∪ ΓC) ΓX
    have := Finset.card_union_le ΓT ΓC
    unfold Net4.fwdTerm
    rw [choose_succ_two]
    omega
  · intro S hS hΓ
    refine Submodule.span_le.2 ?_
    rintro x ⟨v, hv, rfl⟩
    have hT1 : ∀ u ∈ A, T Nt.q (Nt.r k) u ∈ S := by
      intro u hu
      rw [Nt.T_row k u hu]
      refine S.sum_mem fun j _ => ?_
      by_cases hj : Nt.H k j = 0
      · simp [hj]
      · refine S.smul_mem _ ?_
        exact hS j hj (Submodule.subset_span ⟨u, perp_anti (Nt.hH k j hj) hu, rfl⟩)
    have hB1 : ∀ u ∈ A, ∀ u' ∈ A, Bf Nt.q (Nt.r k) u u' ∈ S := by
      intro u hu u' hu'
      rw [Bf_eq]
      exact S.sub_mem (S.add_mem (hT1 u hu) (hT1 u' hu')) (hT1 _ (A.add_mem hu hu'))
    have memT : ∀ j, T Nt.q (Nt.r k) (g j) ∈ S := fun j =>
      hΓ (Finset.mem_coe.2 (Finset.mem_union_left _ (Finset.mem_union_left _
        (Finset.mem_image.2 ⟨j, Finset.mem_univ _, rfl⟩))))
    have memC : ∀ i j, i < j → Bf Nt.q (Nt.r k) (g i) (g j) ∈ S := fun i j hij =>
      hΓ (Finset.mem_coe.2 (Finset.mem_union_left _ (Finset.mem_union_right _
        (Finset.mem_image.2 ⟨(i, j), by simp [hij], rfl⟩))))
    have hBX : ∀ i j, Bf Nt.q (Nt.r k) (f i) (g j) ∈ S := by
      intro i j
      by_cases hr : Nt.relayIn k
      · exact hΓ (Finset.mem_coe.2 (Finset.mem_union_right _ (by
          simp only [ΓX, if_pos hr]
          exact Finset.mem_image.2 ⟨(i, j), Finset.mem_univ _, rfl⟩)))
      · rw [Bf_of_T_zero _ _ _ _ (Nt.T_row_zero k hr _ (hfmem i))]; exact S.zero_mem
    let e : Fin (finrank (ZMod 2) (Submodule.span (ZMod 2) (A : Set (V h)))) ⊕
        Fin (finrank (ZMod 2) (Submodule.span (ZMod 2) (W : Set (V h)))) → V h := Sum.elim f g
    have hT : ∀ i, T Nt.q (Nt.r k) (e i) ∈ S := by
      rintro (i | j)
      · exact hT1 (f i) (hfmem i)
      · exact memT j
    have hB : ∀ i j, Bf Nt.q (Nt.r k) (e i) (e j) ∈ S := by
      rintro (i | i) (j | j)
      · exact hB1 _ (hfmem i) _ (hfmem j)
      · exact hBX i j
      · show Bf Nt.q (Nt.r k) (g i) (f j) ∈ S
        rw [Bf_comm]; exact hBX j i
      · show Bf Nt.q (Nt.r k) (g i) (g j) ∈ S
        rcases lt_trichotomy i j with hij | rfl | hij
        · exact memC i j hij
        · rw [Bf_self]; exact S.smul_mem _ (memT i)
        · rw [Bf_comm]; exact memC j i hij
    have hcov : v ∈ Submodule.span (ZMod 2) (Set.range e) := by
      have hv' : v ∈ A ⊔ W := by rw [hsup]; exact hv
      obtain ⟨x, hx, y, hy, rfl⟩ := Submodule.mem_sup.1 hv'
      refine Submodule.add_mem _ ?_ ?_
      · have hx' : x ∈ Submodule.span (ZMod 2) (Set.range f) := by rw [hfspan']; exact hx
        exact Submodule.span_mono (show Set.range f ⊆ Set.range e from Set.range_subset_iff.2 fun i => ⟨Sum.inl i, rfl⟩) hx'
      · have hy' : y ∈ Submodule.span (ZMod 2) (Set.range g) := by rw [hgspan']; exact hy
        exact Submodule.span_mono (show Set.range g ⊆ Set.range e from Set.range_subset_iff.2 fun i => ⟨Sum.inr i, rfl⟩) hy'
    exact T_mem_of_span Nt.q S e (Nt.r k) hT hB v hcov

/-- THEOREM NG (forward bound). -/
theorem ng_fwd (Nt : Net4 ι κ h) : Fintype.card ι ≤ ∑ k, Nt.fwdTerm k := by
  classical
  choose Γ hΓc hΓg using fun k => Nt.node_gens k
  haveI : IsTrans κ Nt.lt := ⟨Nt.ltrans⟩
  haveI : IsIrrefl κ Nt.lt := ⟨Nt.lirr⟩
  have wf : WellFounded Nt.lt := Finite.wellFounded_of_trans_of_irrefl _
  let Gall : Finset (ι → ZMod 4) := Finset.univ.biUnion Γ
  let Z := Submodule.span (ZMod 4) (Gall : Set (ι → ZMod 4))
  have hPi : ∀ k, Nt.Pi k ≤ Z := by
    intro k
    induction k using wf.induction with
    | _ k ih =>
      refine hΓg k Z (fun j hj => ih j (Nt.hHlt k j hj)) ?_
      intro x hx
      exact Submodule.subset_span (Finset.mem_coe.2
        (Finset.mem_biUnion.2 ⟨k, Finset.mem_univ _, Finset.mem_coe.1 hx⟩))
  have hspan : ∀ t, (Pi.single t (Nt.c t) : ι → ZMod 4) ∈ Z := by
    intro t
    have key : (Pi.single t (Nt.c t) : ι → ZMod 4) =
        ∑ k, Nt.G t k • T Nt.q (Nt.r k) (Nt.q t) := by
      funext p
      simp only [Finset.sum_apply, Pi.smul_apply, smul_eq_mul, T]
      have e1 : ∑ k, Nt.G t k * (chi Nt.q (Nt.q t) p * Nt.r k p) =
          chi Nt.q (Nt.q t) p * (Nt.G * Nt.N * Nt.F) t p := by
        rw [Matrix.mul_assoc, Matrix.mul_apply, Finset.mul_sum]
        refine Finset.sum_congr rfl fun k _ => ?_
        simp only [Net4.r, Matrix.mul_apply]
        ring
      rw [e1]
      rcases zmod2_cases (Nt.q t ⬝ᵥ Nt.q p) with h0 | h1
      · have hne : p ≠ t := by
          rintro rfl; rw [Nt.hodd] at h0; exact one_ne_zero h0
        simp [chi, h0, Pi.single_apply, hne]
      · have hM := Nt.hM t p h1
        have hchi : chi Nt.q (Nt.q t) p = 1 := by simp [chi, h1]
        rw [hchi, hM, one_mul]
        by_cases htp : t = p
        · subst htp; simp
        · simp [Pi.single_apply, htp, Ne.symm htp]
    rw [key]
    refine Z.sum_mem fun k _ => ?_
    by_cases hk : Nt.G t k = 0
    · simp [hk]
    · exact Z.smul_mem _ (hPi k (Submodule.subset_span ⟨Nt.q t, Nt.hG t k hk, rfl⟩))
  have := lift_rank Gall Nt.c Nt.hc hspan
  calc Fintype.card ι ≤ Gall.card := this
    _ ≤ ∑ k, (Γ k).card := Finset.card_biUnion_le
    _ ≤ ∑ k, Nt.fwdTerm k := Finset.sum_le_sum fun k _ => hΓc k

/-! ## the dual network (mirror) -/
def Net4.dual (Nt : Net4 ι κ h) : Net4 ι κ h where
  q := Nt.q
  hodd := Nt.hodd
  lt := fun a b => Nt.lt b a
  ltrans := fun a b c h1 h2 => Nt.ltrans c b a h2 h1
  lirr := Nt.lirr
  a := fun k => perp (Nt.b k)
  b := fun k => perp (Nt.a k)
  F := Nt.Gᵀ
  G := Nt.Fᵀ
  H := Nt.Hᵀ
  N := Nt.Nᵀ
  c := Nt.c
  hba := fun k => perp_anti (Nt.hba k)
  hF := fun k p hne => Nt.hG p k hne
  hG := fun s k hne y hy => by
    have := hy _ (Nt.hF k s hne)
    rwa [dotProduct_comm] at this
  hHlt := fun k j hne => Nt.hHlt j k hne
  hH := fun k j hne => perp_anti (Nt.hH j k hne)
  hN1 := by
    have := congrArg Matrix.transpose Nt.hN2
    simpa [Matrix.transpose_add, Matrix.transpose_mul] using this
  hN2 := by
    have := congrArg Matrix.transpose Nt.hN1
    simpa [Matrix.transpose_add, Matrix.transpose_mul] using this
  hc := Nt.hc
  hM := fun s p hs => by
    have e : Nt.Fᵀ * Nt.Nᵀ * Nt.Gᵀ = (Nt.G * Nt.N * Nt.F)ᵀ := by
      simp [Matrix.transpose_mul, Matrix.mul_assoc]
    rw [e, Matrix.transpose_apply]
    rw [dotProduct_comm] at hs
    rw [Nt.hM p s hs]
    by_cases hsp : s = p
    · subst hsp; simp
    · simp [hsp, Ne.symm hsp]

theorem Net4.dual_drop (Nt : Net4 ι κ h) (k : κ) : Nt.dual.drop k = Nt.drop k := by
  have p1 : finrank (ZMod 2) (perp (Nt.a k)) + finrank (ZMod 2) (Nt.a k) = h := finrank_perp _
  have p2 : finrank (ZMod 2) (perp (Nt.b k)) + finrank (ZMod 2) (Nt.b k) = h := finrank_perp _
  have hle := Submodule.finrank_mono (Nt.hba k)
  unfold Net4.drop
  show finrank (ZMod 2) (perp (Nt.b k)) - finrank (ZMod 2) (perp (Nt.a k)) = _
  omega

/-- THEOREM NG (mirror bound): fwd applied to the dual network. -/
theorem ng_mir (Nt : Net4 ι κ h) : Fintype.card ι ≤ ∑ k, Nt.dual.fwdTerm k := ng_fwd Nt.dual

theorem Net4.dual_term_le (Nt : Net4 ι κ h) (k : κ) :
    Nt.dual.fwdTerm k ≤ (Nt.drop k + 1).choose 2 + Nt.drop k * finrank (ZMod 2) (Nt.b k) := by
  classical
  have p2 : finrank (ZMod 2) (perp (Nt.b k)) + finrank (ZMod 2) (Nt.b k) = h := finrank_perp _
  unfold Net4.fwdTerm
  rw [Nt.dual_drop k]
  have : h - finrank (ZMod 2) (Nt.dual.a k) = finrank (ZMod 2) (Nt.b k) := by
    show h - finrank (ZMod 2) (perp (Nt.b k)) = _
    omega
  rw [this]
  split_ifs <;> omega

theorem Net4.fwd_term_le (Nt : Net4 ι κ h) (k : κ) :
    Nt.fwdTerm k ≤ (Nt.drop k + 1).choose 2 + Nt.drop k * (h - finrank (ZMod 2) (Nt.a k)) := by
  classical
  unfold Net4.fwdTerm
  split_ifs <;> omega

theorem two_choose (d : ℕ) : 2 * (d + 1).choose 2 = (d + 1) * d := by
  induction d with
  | zero => simp
  | succ d ih =>
    rw [choose_succ_two (d + 1), mul_add, ih]
    ring

/-- THEOREM NG (sum): 2 n ≤ (h+1) D. -/
theorem ng_sum (Nt : Net4 ι κ h) :
    2 * Fintype.card ι ≤ (h + 1) * ∑ k, Nt.drop k := by
  have h1 := ng_fwd Nt
  have h2 := ng_mir Nt
  have h3 : ∑ k, Nt.fwdTerm k + ∑ k, Nt.dual.fwdTerm k ≤ (h + 1) * ∑ k, Nt.drop k := by
    rw [← Finset.sum_add_distrib, Finset.mul_sum]
    refine Finset.sum_le_sum fun k _ => ?_
    have a1 := Nt.fwd_term_le k
    have a2 := Nt.dual_term_le k
    have hle := Submodule.finrank_mono (Nt.hba k)
    have hfa := finrank_le_h (Nt.a k)
    unfold Net4.drop at a1 a2 ⊢
    obtain ⟨d, hd⟩ : ∃ d, finrank (ZMod 2) (Nt.a k) = finrank (ZMod 2) (Nt.b k) + d :=
      ⟨_, (Nat.add_sub_cancel' hle).symm⟩
    have hd' : finrank (ZMod 2) (Nt.a k) - finrank (ZMod 2) (Nt.b k) = d := by omega
    rw [hd'] at a1 a2 ⊢
    have e : (h - finrank (ZMod 2) (Nt.a k)) + finrank (ZMod 2) (Nt.b k) + (d + 1) = h + 1 := by omega
    have tc := two_choose d
    calc _ ≤ ((d + 1).choose 2 + d * (h - finrank (ZMod 2) (Nt.a k))) +
          ((d + 1).choose 2 + d * finrank (ZMod 2) (Nt.b k)) := Nat.add_le_add a1 a2
      _ = (h + 1) * d := by
        rw [← e]
        nlinarith [tc]
  omega

/-- headline: on P104 (n = 104, h = 9) every such network has total drop ≥ 21. -/
theorem ng_P104 {κ : Type*} [Fintype κ] [DecidableEq κ] (Nt : Net4 (Fin 104) κ 9) :
    21 ≤ ∑ k, Nt.drop k := by
  have := ng_sum Nt
  simp only [Fintype.card_fin] at this
  omega

end net

/-! ## non-vacuity -/
namespace Inst

/-- tight relay-free instance: n = 1, h = 1, one node, d = 1, n = C(2,2). -/
def net1 : Net4 (Fin 1) (Fin 1) 1 where
  q := ![![1]]
  hodd := by decide
  lt := fun _ _ => False
  ltrans := by decide
  lirr := by decide
  a := fun _ => ⊤
  b := fun _ => ⊥
  F := Matrix.of ![![1]]
  G := Matrix.of ![![1]]
  H := 0
  N := 1
  c := ![1]
  hba := fun _ => bot_le
  hF := fun _ _ _ => Submodule.mem_top
  hG := fun s k _ y hy => by
    rw [Submodule.mem_bot] at hy; subst hy; simp
  hHlt := fun k j hne => absurd (Matrix.zero_apply k j) hne
  hH := fun _ _ _ => bot_le
  hN1 := by decide
  hN2 := by decide
  hc := by decide
  hM := by decide

example : ∑ k, net1.drop k = 1 := by
  simp only [Finset.univ_unique, Finset.sum_singleton]
  show finrank (ZMod 2) (⊤ : Submodule (ZMod 2) (V 1)) - finrank (ZMod 2) (⊥ : Submodule (ZMod 2) (V 1)) = 1
  rw [finrank_top, finrank_bot]; simp

/-- two nodes with a relay 0 → 1, two ports with orthogonal labels e1, e2 in F2^2. -/
def net2 : Net4 (Fin 2) (Fin 2) 2 where
  q := ![![1, 0], ![0, 1]]
  hodd := by decide
  lt := fun a b => a < b
  ltrans := fun a b c h1 h2 => lt_trans h1 h2
  lirr := fun a => lt_irrefl a
  a := fun _ => ⊤
  b := fun _ => ⊥
  F := Matrix.of ![![1, 1], ![0, 0]]
  G := Matrix.of ![![1, 0], ![1, 0]]
  H := Matrix.of ![![0, 0], ![1, 0]]
  N := Matrix.of ![![1, 0], ![1, 1]]
  c := ![1, 1]
  hba := fun _ => bot_le
  hF := fun _ _ _ => Submodule.mem_top
  hG := fun s k _ y hy => by
    rw [Submodule.mem_bot] at hy; subst hy; simp
  hHlt := fun k j hne => by
    fin_cases k <;> fin_cases j <;> simp_all [Matrix.of_apply]
  hH := fun _ _ _ => bot_le
  hN1 := by decide
  hN2 := by decide
  hc := by decide
  hM := by decide

theorem net2_relay : net2.relayIn 1 := ⟨0, by decide⟩

/-- the NG sum bound holds (2·2 ≤ 3·D) on the relay instance, and the headline route applies. -/
example : 2 * Fintype.card (Fin 2) ≤ (2 + 1) * ∑ k, net2.drop k := ng_sum net2
example : Fintype.card (Fin 1) ≤ ∑ k, net1.fwdTerm k := ng_fwd net1
example : Fintype.card (Fin 2) ≤ ∑ k, net2.dual.fwdTerm k := ng_mir net2

end Inst

/-! ## arithmetic anchors (P104: n = 104, h = 9) -/
theorem P104_arith : 2 * 104 ≤ (9 + 1) * 21 ∧ ¬ 2 * 104 ≤ (9 + 1) * 20 := by decide
/-- relay-free NET8/E8 has D = 56: the NG inequality 2n ≤ (h+1)D holds with slack. -/
theorem E8_arith : 2 * 104 ≤ (9 + 1) * 56 := by decide
/-- WALLCORE's D = 16 profile violates NG (so it is excluded inside the half-integer class). -/
theorem wallcore16_excluded : ¬ 2 * 104 ≤ (9 + 1) * 16 := by decide

#print axioms lift_rank
#print axioms Net4.node_gens
#print axioms ng_fwd
#print axioms ng_mir
#print axioms ng_sum
#print axioms ng_P104
#print axioms Inst.net1
#print axioms Inst.net2

end NetNG
