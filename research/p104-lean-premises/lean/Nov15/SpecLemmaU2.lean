/-
SPECBREAK RB6 survivor #0, part 2 .  Extends SpecLemmaU.lean.
Discharges `hrk` / `hE` from block coordinates, proves the three E-part cases, composes `spec0_core_U4`.
See SpecLemmaU2.md.
-/
import Nov15.SpecLemmaU

open Module LinearMap Matrix

set_option linter.unusedSectionVars false

namespace SpecLemmaU2
open SpecLemmaU

/-! ## §1  generic kernel-bound lemma -/
section KB
variable {K : Type*} [Field K]

theorem kb {A : Type*} [AddCommGroup A] [Module K A] [FiniteDimensional K A]
    {B : Type*} [AddCommGroup B] [Module K B] [FiniteDimensional K B]
    {r c : Type*} [Fintype r] [Fintype c]
    (f : A →ₗ[K] A) (S : Matrix r c K) (θ1 : A →ₗ[K] (c → K)) (θ2 : A →ₗ[K] B)
    (Bs : Submodule K B)
    (hθ : ∀ w ∈ ker f, S *ᵥ θ1 w = 0)
    (hB : ∀ w ∈ ker f, θ2 w ∈ Bs)
    (hinj : ∀ w ∈ ker f, θ1 w = 0 → θ2 w = 0 → w = 0) :
    finrank K (ker f) + S.rank ≤ Fintype.card c + finrank K Bs := by
  set θ1' : ker f →ₗ[K] (c → K) := θ1.domRestrict (ker f) with hθ1'
  have h1 := LinearMap.finrank_range_add_finrank_ker θ1'
  have hr : range θ1' ≤ ker S.mulVecLin := by
    rintro _ ⟨⟨w, hw⟩, rfl⟩
    have := hθ w hw
    simpa [θ1'] using this
  have h2 : finrank K (range θ1') ≤ finrank K (ker S.mulVecLin) := Submodule.finrank_mono hr
  have h3 := LinearMap.finrank_range_add_finrank_ker S.mulVecLin
  have hc : finrank K (c → K) = Fintype.card c := by simp
  have hSr : S.rank = finrank K (range S.mulVecLin) := rfl
  let g0 : ker θ1' →ₗ[K] B := (θ2.domRestrict (ker f)).domRestrict (ker θ1')
  let g : ker θ1' →ₗ[K] Bs := g0.codRestrict Bs (fun x => hB x.1.1 x.1.2)
  have hg : Function.Injective g := by
    rw [← LinearMap.ker_eq_bot, LinearMap.ker_eq_bot']
    intro x hx
    have hx0 : θ2 x.1.1 = 0 := by
      have : ((g x : Bs) : B) = 0 := by rw [hx]; rfl
      exact this
    have hx1 : θ1 x.1.1 = 0 := LinearMap.mem_ker.1 x.2
    have := hinj x.1.1 x.1.2 hx1 hx0
    apply Subtype.ext; apply Subtype.ext
    simpa using this
  have h4 := LinearMap.finrank_le_finrank_of_injective hg
  omega

end KB


/-! ## §2  the model: coordinates `Fin 4 ⊕ (Fin 2 ⊕ E)`, `C4 = inl`, `e5 = I5`, `e6 = I6`, `E' = inr inr` -/
section Model
variable {K : Type*} [Field K] {E : Type*} [Fintype E] [DecidableEq E]

abbrev Ix (E : Type*) := Fin 4 ⊕ (Fin 2 ⊕ E)

local notation "I5" => Sum.inr (Sum.inl (0 : Fin 2))
local notation "I6" => Sum.inr (Sum.inl (1 : Fin 2))
local notation "cE " e:max => Sum.inr (Sum.inr e)

/-- columns `e5, e6, v` (used for both `X = (e5, e6, u)` and `Y = (e5, e6, η)`). -/
def vt (u : Ix E → K) : Matrix (Ix E) (Fin 3) K :=
  Matrix.of fun x j => ![if x = I5 then 1 else 0, if x = I6 then 1 else 0, u x] j

/-- `D`: `-1` on `C4` and on `e5`, `+1` on `e6` and `E'`. -/
def dm (K : Type*) [Field K] (E : Type*) : Fin 2 ⊕ E → K := Sum.elim ![-1, 1] (fun _ => 1)

/-- `P = 1 - X T Yᵀ`. -/
def Pm (u η : Ix E → K) (T : Matrix (Fin 3) (Fin 3) K) : Matrix (Ix E) (Ix E) K :=
  1 - vt u * T * (vt η)ᵀ

theorem tvec_eq (η w : Ix E → K) : (vt η)ᵀ *ᵥ w = ![w I5, w I6, η ⬝ᵥ w] := by
  ext j; fin_cases j <;> simp [vt, Matrix.mulVec, dotProduct, Matrix.transpose_apply]

theorem vt_mulVec (u : Ix E → K) (s : Fin 3 → K) (x : Ix E) :
    (vt u *ᵥ s) x = s 0 * (if x = I5 then 1 else 0) + s 1 * (if x = I6 then 1 else 0) + s 2 * u x := by
  simp [vt, Matrix.mulVec, dotProduct, Fin.sum_univ_three]; ring

/-- `σ = T t(w)`, `t(w) = (w_5, w_6, η·w)`. -/
def sg (η : Ix E → K) (T : Matrix (Fin 3) (Fin 3) K) (w : Ix E → K) : Fin 3 → K :=
  T *ᵥ ![w I5, w I6, η ⬝ᵥ w]

theorem Pm_mulVec (u η : Ix E → K) (T : Matrix (Fin 3) (Fin 3) K) (w : Ix E → K) (x : Ix E) :
    (Pm u η T *ᵥ w) x = w x - (sg η T w 0 * (if x = I5 then 1 else 0)
      + sg η T w 1 * (if x = I6 then 1 else 0) + sg η T w 2 * u x) := by
  simp only [Pm, sub_mulVec, one_mulVec, Pi.sub_apply, ← Matrix.mulVec_mulVec, tvec_eq,
    vt_mulVec, sg]

theorem Dm_mulVec (w : Ix E → K) (x : Ix E) :
    (Dm K (dm K E) *ᵥ w) x = Sum.elim (fun _ => (-1 : K)) (dm K E) x * w x := by
  simp [Dm, Matrix.mulVec_diagonal]

/-- equations for `D w = P w` (i.e. `Λ w = w`). -/
theorem fix_eqs (h2 : (2 : K) ≠ 0) (u η : Ix E → K) (T : Matrix (Fin 3) (Fin 3) K)
    (hu5 : u I5 = 0) (hu6 : u I6 = 0) (w : Ix E → K)
    (h : Dm K (dm K E) *ᵥ w = Pm u η T *ᵥ w) :
    (∀ c : Fin 4, w (Sum.inl c) = sg η T w 2 / 2 * u (Sum.inl c)) ∧ sg η T w 0 = 2 * w I5 ∧
      sg η T w 1 = 0 ∧ (∀ e, sg η T w 2 * u (cE e) = 0) := by
  have hx := fun x => congrFun h x
  refine ⟨fun c => ?_, ?_, ?_, fun e => ?_⟩
  · have := hx (Sum.inl c)
    rw [Dm_mulVec, Pm_mulVec] at this; simp [dm] at this
    rw [div_mul_eq_mul_div, eq_div_iff h2]
    linear_combination (-1 : K) * this
  · have := hx I5
    rw [Dm_mulVec, Pm_mulVec] at this; simp [dm, hu5] at this
    linear_combination this
  · have := hx I6
    rw [Dm_mulVec, Pm_mulVec] at this; simp [dm, hu6] at this
    linear_combination this
  · have := hx (cE e)
    rw [Dm_mulVec, Pm_mulVec] at this; simp [dm] at this
    linear_combination this


/-- `Λ = P⁻¹ D`. -/
noncomputable def Lam (u η : Ix E → K) (T : Matrix (Fin 3) (Fin 3) K) : Matrix (Ix E) (Ix E) K :=
  (Pm u η T)⁻¹ * Dm K (dm K E)

theorem mem_ker_iff (u η : Ix E → K) (T : Matrix (Fin 3) (Fin 3) K)
    (hdet : IsUnit (Pm u η T).det) (w : Ix E → K) :
    w ∈ ker (Matrix.toLin' (Lam u η T) - 1) ↔ Dm K (dm K E) *ᵥ w = Pm u η T *ᵥ w := by
  have hP : Pm u η T * (Pm u η T)⁻¹ = 1 := Matrix.mul_nonsing_inv _ hdet
  have hP' : (Pm u η T)⁻¹ * Pm u η T = 1 := Matrix.nonsing_inv_mul _ hdet
  rw [LinearMap.mem_ker]
  simp only [LinearMap.sub_apply, Matrix.toLin'_apply, Lam, ← Matrix.mulVec_mulVec,
    Module.End.one_apply, sub_eq_zero]
  constructor
  · intro h
    have := congrArg (Matrix.mulVec (Pm u η T)) h
    rw [Matrix.mulVec_mulVec, hP, Matrix.one_mulVec] at this
    exact this
  · intro h
    rw [h, Matrix.mulVec_mulVec, hP', Matrix.one_mulVec]

theorem mem_ker_add_iff (u η : Ix E → K) (T : Matrix (Fin 3) (Fin 3) K)
    (hdet : IsUnit (Pm u η T).det) (w : Ix E → K) :
    w ∈ ker (Matrix.toLin' (Lam u η T) + 1) ↔
      Dm K (dm K E) *ᵥ w + Pm u η T *ᵥ w = 0 := by
  have hP : Pm u η T * (Pm u η T)⁻¹ = 1 := Matrix.mul_nonsing_inv _ hdet
  have hP' : (Pm u η T)⁻¹ * Pm u η T = 1 := Matrix.nonsing_inv_mul _ hdet
  rw [LinearMap.mem_ker]
  simp only [LinearMap.add_apply, Matrix.toLin'_apply, Lam, ← Matrix.mulVec_mulVec,
    Module.End.one_apply]
  constructor
  · intro h
    have := congrArg (Matrix.mulVec (Pm u η T)) h
    rw [Matrix.mulVec_add, Matrix.mulVec_mulVec, hP, Matrix.one_mulVec, Matrix.mulVec_zero] at this
    exact this
  · intro h
    have h' : Dm K (dm K E) *ᵥ w = -(Pm u η T *ᵥ w) := eq_neg_of_add_eq_zero_left h
    rw [h', Matrix.mulVec_neg, Matrix.mulVec_mulVec, hP', Matrix.one_mulVec]; simp

/-- `C4`-part of `k = η·u`. -/
def kC (η u : Ix E → K) : K := ∑ c : Fin 4, η (Sum.inl c) * u (Sum.inl c)
/-- `E'`-part of `η·w`. -/
def lam (η w : Ix E → K) : K := ∑ e : E, η (cE e) * w (cE e)

theorem dot_split (η w : Ix E → K) (hη5 : η I5 = 0) (hη6 : η I6 = 0) :
    η ⬝ᵥ w = ∑ c : Fin 4, η (Sum.inl c) * w (Sum.inl c) + lam η w := by
  simp [dotProduct, Fintype.sum_sum_type, Fin.sum_univ_two, hη5, hη6, lam]

theorem dot_ker (η u w : Ix E → K) (hη5 : η I5 = 0) (hη6 : η I6 = 0) (s : K)
    (hC : ∀ c : Fin 4, w (Sum.inl c) = s * u (Sum.inl c)) :
    η ⬝ᵥ w = kC η u * s + lam η w := by
  rw [dot_split η w hη5 hη6]
  congr 1
  simp only [hC, kC, Finset.sum_mul]
  exact Finset.sum_congr rfl fun c _ => by ring

theorem w_eq_zero (w : Ix E → K) (hC : ∀ c, w (Sum.inl c) = 0) (h5 : w I5 = 0) (h6 : w I6 = 0)
    (hE : ∀ e, w (cE e) = 0) : w = 0 := by
  ext x
  rcases x with c | j | e
  · exact hC c
  · fin_cases j
    · exact h5
    · exact h6
  · exact hE e

/-- the 4-column system (η_E ≠ 0). -/
def S4 (T : Matrix (Fin 3) (Fin 3) K) (κ δ : K) : Matrix (Fin 4) (Fin 4) K :=
  !![T 0 0 - 2, T 0 1, T 0 2 * κ, T 0 2;
     T 1 0, T 1 1, T 1 2 * κ, T 1 2;
     T 2 0, T 2 1, T 2 2 * κ - 2, T 2 2;
     0, 0, δ, 0]

/-- the 3-column system (η_E = 0). -/
def S3 (T : Matrix (Fin 3) (Fin 3) K) (κ δ : K) : Matrix (Fin 4) (Fin 3) K :=
  !![T 0 0 - 2, T 0 1, T 0 2 * κ;
     T 1 0, T 1 1, T 1 2 * κ;
     T 2 0, T 2 1, T 2 2 * κ - 2;
     0, 0, δ]

/-- the three row equations, in the variables `(z0, z1, z2, λ)`. -/
theorem rows_eq (h2 : (2 : K) ≠ 0) (u η : Ix E → K) (T : Matrix (Fin 3) (Fin 3) K)
    (hu5 : u I5 = 0) (hu6 : u I6 = 0) (hη5 : η I5 = 0) (hη6 : η I6 = 0) (w : Ix E → K)
    (h : Dm K (dm K E) *ᵥ w = Pm u η T *ᵥ w) :
    (T 0 0 - 2) * w I5 + T 0 1 * w I6 + T 0 2 * (kC η u * (sg η T w 2 / 2) + lam η w) = 0 ∧
    T 1 0 * w I5 + T 1 1 * w I6 + T 1 2 * (kC η u * (sg η T w 2 / 2) + lam η w) = 0 ∧
    T 2 0 * w I5 + T 2 1 * w I6 + T 2 2 * (kC η u * (sg η T w 2 / 2) + lam η w)
       - 2 * (sg η T w 2 / 2) = 0 := by
  obtain ⟨e1, e2, e3, e4⟩ := fix_eqs h2 u η T hu5 hu6 w h
  have hd := dot_ker η u w hη5 hη6 (sg η T w 2 / 2) e1
  have s0 : sg η T w 0 = T 0 0 * w I5 + T 0 1 * w I6 + T 0 2 * (η ⬝ᵥ w) := by
    simp [sg, Matrix.mulVec, dotProduct, Fin.sum_univ_three]
  have s1 : sg η T w 1 = T 1 0 * w I5 + T 1 1 * w I6 + T 1 2 * (η ⬝ᵥ w) := by
    simp [sg, Matrix.mulVec, dotProduct, Fin.sum_univ_three]
  have s2 : sg η T w 2 = T 2 0 * w I5 + T 2 1 * w I6 + T 2 2 * (η ⬝ᵥ w) := by
    simp [sg, Matrix.mulVec, dotProduct, Fin.sum_univ_three]
  rw [hd] at s0 s1 s2
  have hz : sg η T w 2 / 2 * 2 = sg η T w 2 := div_mul_cancel₀ _ h2
  refine ⟨?_, ?_, ?_⟩
  · linear_combination e2 - s0
  · linear_combination e3 - s1
  · linear_combination (-1 : K) * s2 - hz
  

/-! ### linear maps for the kernel injections -/
def prL (x : Ix E) : (Ix E → K) →ₗ[K] K := LinearMap.proj x

def dotL (η : Ix E → K) : (Ix E → K) →ₗ[K] K where
  toFun w := η ⬝ᵥ w
  map_add' := dotProduct_add _
  map_smul' c w := by simp [dotProduct_smul]

def lamL (η : Ix E → K) : (Ix E → K) →ₗ[K] K where
  toFun w := lam η w
  map_add' a b := by simp [lam, mul_add, Finset.sum_add_distrib]
  map_smul' c w := by
    simp only [lam, Pi.smul_apply, smul_eq_mul, RingHom.id_apply, Finset.mul_sum]
    exact Finset.sum_congr rfl fun e _ => by ring

/-- `lam` on functions of `E` alone. -/
def lamF (η : Ix E → K) : (E → K) →ₗ[K] K where
  toFun v := ∑ e, η (cE e) * v e
  map_add' a b := by simp [mul_add, Finset.sum_add_distrib]
  map_smul' c v := by
    simp only [Pi.smul_apply, smul_eq_mul, RingHom.id_apply, Finset.mul_sum]
    exact Finset.sum_congr rfl fun e _ => by ring

theorem lamL_apply (η w : Ix E → K) : lamL η w = lam η w := rfl

def tL (η : Ix E → K) : (Ix E → K) →ₗ[K] (Fin 3 → K) := LinearMap.pi ![prL I5, prL I6, dotL η]

def sgL (η : Ix E → K) (T : Matrix (Fin 3) (Fin 3) K) : (Ix E → K) →ₗ[K] (Fin 3 → K) :=
  (Matrix.mulVecLin T) ∘ₗ tL η

theorem sgL_apply (η : Ix E → K) (T : Matrix (Fin 3) (Fin 3) K) (w : Ix E → K) :
    sgL η T w = sg η T w := by
  have : tL η w = ![w I5, w I6, η ⬝ᵥ w] := by
    ext j; fin_cases j <;> simp [tL, prL, dotL]
  simp [sgL, this, sg]

def th3 (η : Ix E → K) (T : Matrix (Fin 3) (Fin 3) K) : (Ix E → K) →ₗ[K] (Fin 3 → K) :=
  LinearMap.pi ![prL I5, prL I6, (1 / 2 : K) • (LinearMap.proj (2 : Fin 3) ∘ₗ sgL η T)]

def th4 (η : Ix E → K) (T : Matrix (Fin 3) (Fin 3) K) : (Ix E → K) →ₗ[K] (Fin 4 → K) :=
  LinearMap.pi ![prL I5, prL I6, (1 / 2 : K) • (LinearMap.proj (2 : Fin 3) ∘ₗ sgL η T), lamL η]

theorem th3_apply (η : Ix E → K) (T : Matrix (Fin 3) (Fin 3) K) (w : Ix E → K) :
    th3 η T w = ![w I5, w I6, sg η T w 2 / 2] := by
  ext j; fin_cases j <;> simp [th3, prL, sgL_apply, div_eq_inv_mul]

theorem th4_apply (η : Ix E → K) (T : Matrix (Fin 3) (Fin 3) K) (w : Ix E → K) :
    th4 η T w = ![w I5, w I6, sg η T w 2 / 2, lam η w] := by
  ext j; fin_cases j <;> simp [th4, prL, sgL_apply, lamL_apply, div_eq_inv_mul]

theorem finrank_ix (E : Type*) [Fintype E] :
    finrank K (Ix E → K) = 6 + Fintype.card E := by
  simp [Module.finrank_fintype_fun_eq_card, Fintype.card_sum]; omega

theorem finrank_ker_lamF (η : Ix E → K) (e : E) (he : η (cE e) ≠ 0) :
    finrank K (ker (lamF η)) + 1 ≤ Fintype.card E := by
  have h1 := LinearMap.finrank_range_add_finrank_ker (lamF η)
  have h3 : 0 < finrank K (range (lamF η)) := by
    refine Module.finrank_pos_iff_exists_ne_zero.2
      ⟨⟨lamF η (Pi.single e (η (cE e))⁻¹), ⟨_, rfl⟩⟩, fun h' => ?_⟩
    have := congrArg Subtype.val h'
    simp [lamF, Pi.single_apply, he] at this
  have h4 : finrank K (E → K) = Fintype.card E := by simp
  omega

/-- If the `C4`-block, `e5`, `e6` data of `w` vanish, then `w = 0` (shared injectivity step). -/
theorem key4 (h2 : (2 : K) ≠ 0) (u η : Ix E → K) (T : Matrix (Fin 3) (Fin 3) K)
    (hu5 : u I5 = 0) (hu6 : u I6 = 0) (hη5 : η I5 = 0) (hη6 : η I6 = 0)
    (hdet : IsUnit (Pm u η T).det) (hηE : ∃ e, η (cE e) ≠ 0) (δ : K)
    (hδ : δ = 0 ∨ ∃ e, u (cE e) ≠ 0) :
    3 + (S4 T (kC η u) δ).rank ≤ finrank K (range (Matrix.toLin' (Lam u η T) - 1)) := by
  obtain ⟨e, he⟩ := hηE
  set e0 : E → K := Pi.single e (η (cE e))⁻¹ with he0d
  have he0 : lamF η e0 = 1 := by simp [lamF, e0, Pi.single_apply, he]
  set f := Matrix.toLin' (Lam u η T) - 1 with hf
  let θ2 : (Ix E → K) →ₗ[K] (E → K) :=
    LinearMap.funLeft K K (fun e : E => (cE e : Ix E)) - (lamL η).smulRight e0
  have hθ2 : ∀ w, θ2 w = fun e' => w (cE e') - lam η w * e0 e' := by
    intro w; ext e'; simp [θ2, lamL_apply]
  have hkb := kb f (S4 T (kC η u) δ) (th4 η T) θ2 (ker (lamF η))
    (fun w hw => by
      have h := (mem_ker_iff u η T hdet w).1 hw
      obtain ⟨r1, r2, r3⟩ := rows_eq h2 u η T hu5 hu6 hη5 hη6 w h
      obtain ⟨e1, e2, e3, e4⟩ := fix_eqs h2 u η T hu5 hu6 w h
      have hz : δ * (sg η T w 2 / 2) = 0 := by
        rcases hδ with h0 | ⟨e', he'⟩
        · simp [h0]
        · have := e4 e'
          have : sg η T w 2 = 0 := by
            rcases mul_eq_zero.1 this with h | h
            · exact h
            · exact absurd h he'
          simp [this]
      have hz' := hz
      simp at hz'
      rw [th4_apply]
      ext i; fin_cases i <;>
        simp [S4, Matrix.mulVec, dotProduct, Fin.sum_univ_four] <;>
        first | linear_combination r1 | linear_combination r2 | linear_combination r3 |
          exact hz')
    (fun w _ => by
      rw [LinearMap.mem_ker, hθ2]
      show ∑ e', η (cE e') * (w (cE e') - lam η w * e0 e') = 0
      have : ∑ e', η (cE e') * (w (cE e') - lam η w * e0 e') = lam η w - lam η w * lamF η e0 := by
        simp only [lam, lamF, LinearMap.coe_mk, AddHom.coe_mk, Finset.mul_sum, mul_sub, Finset.sum_sub_distrib]
        congr 1
        exact Finset.sum_congr rfl fun e' _ => by ring
      rw [this, he0]; ring)
    (fun w hw h1 h2' => by
      have h := (mem_ker_iff u η T hdet w).1 hw
      obtain ⟨e1, e2, e3, e4⟩ := fix_eqs h2 u η T hu5 hu6 w h
      rw [th4_apply] at h1
      have z0 : w I5 = 0 := by simpa using congrFun h1 0
      have z1 : w I6 = 0 := by simpa using congrFun h1 1
      have z2 : sg η T w 2 / 2 = 0 := by simpa using congrFun h1 2
      have z3 : lam η w = 0 := by simpa using congrFun h1 3
      have z2' : sg η T w 2 = 0 := by
        rcases div_eq_zero_iff.1 z2 with h | h
        · exact h
        · exact absurd h h2
      rw [hθ2] at h2'
      refine w_eq_zero w (fun c => by rw [e1, z2]; simp) z0 z1 (fun e' => ?_)
      have := congrFun h2' e'
      simpa [z3] using this)
  have h1 := LinearMap.finrank_range_add_finrank_ker f
  have h5 := finrank_ix (K := K) E
  have h6 := finrank_ker_lamF η e he
  rw [Fintype.card_fin] at hkb
  omega


theorem lam_zero' (η w : Ix E → K) (hw : ∀ e, w (cE e) = 0) : lam η w = 0 := by
  simp [lam, hw]

theorem lam_zero (η w : Ix E → K) (hηE : ∀ e, η (cE e) = 0) : lam η w = 0 := by
  simp [lam, hηE]

theorem key3 (h2 : (2 : K) ≠ 0) (u η : Ix E → K) (T : Matrix (Fin 3) (Fin 3) K)
    (hu5 : u I5 = 0) (hu6 : u I6 = 0) (hη5 : η I5 = 0) (hη6 : η I6 = 0)
    (hdet : IsUnit (Pm u η T).det) (hηE : ∀ e, η (cE e) = 0) (δ : K)
    (hδ : δ = 0 ∨ ∃ e, u (cE e) ≠ 0) :
    3 + (S3 T (kC η u) δ).rank ≤ finrank K (range (Matrix.toLin' (Lam u η T) - 1)) := by
  set f := Matrix.toLin' (Lam u η T) - 1 with hf
  let θ2 : (Ix E → K) →ₗ[K] (E → K) :=
    LinearMap.funLeft K K (fun e : E => (cE e : Ix E))
  have hkb := kb f (S3 T (kC η u) δ) (th3 η T) θ2 ⊤
    (fun w hw => by
      have h := (mem_ker_iff u η T hdet w).1 hw
      obtain ⟨r1, r2, r3⟩ := rows_eq h2 u η T hu5 hu6 hη5 hη6 w h
      obtain ⟨e1, e2, e3, e4⟩ := fix_eqs h2 u η T hu5 hu6 w h
      rw [lam_zero η w hηE] at r1 r2 r3
      have hz : δ * (sg η T w 2 / 2) = 0 := by
        rcases hδ with h0 | ⟨e', he'⟩
        · simp [h0]
        · have := e4 e'
          have : sg η T w 2 = 0 := by
            rcases mul_eq_zero.1 this with h | h
            · exact h
            · exact absurd h he'
          simp [this]
      have hz' := hz
      simp at hz'
      rw [th3_apply]
      ext i; fin_cases i <;>
        simp [S3, Matrix.mulVec, dotProduct, Fin.sum_univ_three] <;>
        first | linear_combination r1 | linear_combination r2 | linear_combination r3 |
          exact hz')
    (fun w _ => Submodule.mem_top)
    (fun w hw h1 h2' => by
      have h := (mem_ker_iff u η T hdet w).1 hw
      obtain ⟨e1, e2, e3, e4⟩ := fix_eqs h2 u η T hu5 hu6 w h
      rw [th3_apply] at h1
      have z0 : w I5 = 0 := by simpa using congrFun h1 0
      have z1 : w I6 = 0 := by simpa using congrFun h1 1
      have z2 : sg η T w 2 / 2 = 0 := by simpa using congrFun h1 2
      refine w_eq_zero w (fun c => by rw [e1, z2]; simp) z0 z1 (fun e' => ?_)
      simpa [θ2] using congrFun h2' e')
  have h1 := LinearMap.finrank_range_add_finrank_ker f
  have h5 := finrank_ix (K := K) E
  have h6 : finrank K (⊤ : Submodule K (E → K)) = Fintype.card E := by simp
  rw [Fintype.card_fin] at hkb
  omega


/-! ### the `E_{-1}` side -/
def etaC (η : Ix E → K) : (Fin 4 → K) →ₗ[K] K where
  toFun c := ∑ i, η (Sum.inl i) * c i
  map_add' a b := by simp [mul_add, Finset.sum_add_distrib]
  map_smul' c v := by
    simp only [Pi.smul_apply, smul_eq_mul, RingHom.id_apply, Finset.mul_sum]
    exact Finset.sum_congr rfl fun e _ => by ring

theorem etaC_apply (η : Ix E → K) (c : Fin 4 → K) : etaC η c = ∑ i, η (Sum.inl i) * c i := rfl

/-- the explicit `E_{-1}` vectors `w(t, c)`: `C4 = t₂ c₀ + c`, `e5 = t₀`, `e6 = t₁`, `E' = 0`. -/
def mu (c0 : Fin 4 → K) : ((Fin 3 → K) × (Fin 4 → K)) →ₗ[K] (Ix E → K) where
  toFun p := Sum.elim (fun i => (p.1 2 • c0 + p.2) i) (Sum.elim ![p.1 0, p.1 1] (fun _ => 0))
  map_add' a b := by
    ext x; rcases x with i | j | e
    · simp; ring
    · fin_cases j <;> simp
    · simp
  map_smul' c a := by
    ext x; rcases x with i | j | e
    · simp; ring
    · fin_cases j <;> simp
    · simp

theorem Em1_bound (h2 : (2 : K) ≠ 0) (u η : Ix E → K) (T : Matrix (Fin 3) (Fin 3) K)
    (hu5 : u I5 = 0) (hu6 : u I6 = 0) (hη5 : η I5 = 0) (hη6 : η I6 = 0)
    (hdet : IsUnit (Pm u η T).det) (hηC : ∃ c, η (Sum.inl c) ≠ 0)
    (hT : (T - Dp).rank ≤ 2) :
    4 ≤ finrank K (ker (Matrix.toLin' (Lam u η T) + 1)) := by
  obtain ⟨c1, hc1⟩ := hηC
  set c0 : Fin 4 → K := Pi.single c1 (η (Sum.inl c1))⁻¹ with hc0d
  have hc0 : etaC η c0 = 1 := by simp [etaC_apply, c0, Pi.single_apply, hc1]
  set K1 : Submodule K (Fin 3 → K) := ker (T - Dp).mulVecLin with hK1
  set K2 : Submodule K (Fin 4 → K) := ker (etaC η) with hK2
  let ν : (↥K1 × ↥K2) →ₗ[K] (Ix E → K) :=
    (mu (E := E) c0).comp (K1.subtype.prodMap K2.subtype)
  have hν : ∀ p : ↥K1 × ↥K2, ν p = Sum.elim (fun i => (p.1.1 2 • c0 + p.2.1) i)
      (Sum.elim ![p.1.1 0, p.1.1 1] (fun _ => 0)) := fun p => rfl
  -- dimensions
  have hd1 : 1 ≤ finrank K K1 := by
    have h1 := LinearMap.finrank_range_add_finrank_ker (T - Dp).mulVecLin
    have h3 : (T - Dp).rank = finrank K (range (T - Dp).mulVecLin) := rfl
    have h4 : finrank K (Fin 3 → K) = 3 := by simp
    have e1 : finrank K K1 = finrank K (ker (T - Dp).mulVecLin) := rfl
    omega
  have hd2 : 3 ≤ finrank K K2 := by
    have h1 := LinearMap.finrank_range_add_finrank_ker (etaC η)
    have h3 : finrank K (range (etaC η)) ≤ 1 := by
      have := Submodule.finrank_le (range (etaC η))
      simpa using this
    have h4 : finrank K (Fin 4 → K) = 4 := by simp
    have e1 : finrank K K2 = finrank K (ker (etaC η)) := rfl
    omega
  have hinj : Function.Injective ν := by
    rw [← LinearMap.ker_eq_bot, LinearMap.ker_eq_bot']
    intro p hp
    have h5 := congrFun hp I5
    have h6 := congrFun hp I6
    simp [hν] at h5 h6
    have hC : ∀ i, p.1.1 2 * c0 i + p.2.1 i = 0 := fun i => by
      have := congrFun hp (Sum.inl i)
      simpa [hν] using this
    have ht2 : p.1.1 2 = 0 := by
      have := congrArg (fun v => ∑ i, η (Sum.inl i) * v i) (funext hC : (fun i => p.1.1 2 * c0 i + p.2.1 i) = 0)
      have h7 : p.2.1 ∈ ker (etaC η) := p.2.2
      rw [LinearMap.mem_ker, etaC_apply] at h7
      have h8 : ∑ i, η (Sum.inl i) * c0 i = 1 := hc0
      simp only [mul_add, Finset.sum_add_distrib, mul_left_comm _ (p.1.1 2), ← Finset.mul_sum, h8,
        h7] at this
      simpa using this
    have hp2 : p.2.1 = 0 := by
      ext i; have := hC i; rw [ht2] at this; simpa using this
    have hp1 : p.1.1 = 0 := by
      ext j; fin_cases j
      · simpa using h5
      · simpa using h6
      · simpa using ht2
    exact Prod.ext (Subtype.ext hp1) (Subtype.ext hp2)
  have hrange : range ν ≤ ker (Matrix.toLin' (Lam u η T) + 1) := by
    rintro _ ⟨p, rfl⟩
    rw [mem_ker_add_iff u η T hdet]
    obtain ⟨⟨t, ht⟩, ⟨c, hc⟩⟩ := p
    have htT : T *ᵥ t = Dp *ᵥ t := by
      have : (T - Dp) *ᵥ t = 0 := ht
      rw [Matrix.sub_mulVec] at this
      exact sub_eq_zero.1 this
    set w : Ix E → K := ν (⟨t, ht⟩, ⟨c, hc⟩) with hw
    have hwv : w = Sum.elim (fun i => (t 2 • c0 + c) i)
      (Sum.elim ![t 0, t 1] (fun _ => 0)) := rfl
    have hw5 : w I5 = t 0 := by simp [hwv]
    have hw6 : w I6 = t 1 := by simp [hwv]
    have hwE : ∀ e, w (cE e) = 0 := by intro e; simp [hwv]
    have hwC : ∀ i, w (Sum.inl i) = (t 2 • c0 + c) i := by intro i; simp [hwv]
    have hdw : η ⬝ᵥ w = t 2 := by
      rw [dot_split η w hη5 hη6, lam_zero' η w hwE]
      have h7 : etaC η c = 0 := hc
      simp only [hwC, etaC_apply] at h7 ⊢
      simp only [Pi.add_apply, Pi.smul_apply, smul_eq_mul, mul_add, Finset.sum_add_distrib,
        mul_left_comm _ (t 2), ← Finset.mul_sum] at *
      have h8 : ∑ i, η (Sum.inl i) * c0 i = 1 := hc0
      rw [h8, h7]; ring
    have htv : ![w I5, w I6, η ⬝ᵥ w] = t := by
      ext j; fin_cases j <;> simp [hw5, hw6, hdw]
    have hsg : sg η T w = Dp *ᵥ t := by
      rw [sg, htv, htT]
    have s0 : sg η T w 0 = 0 := by rw [hsg]; simp [Dp, Matrix.mulVec_diagonal]
    have s1 : sg η T w 1 = 2 * t 1 := by rw [hsg]; simp [Dp, Matrix.mulVec_diagonal]
    have s2 : sg η T w 2 = 0 := by rw [hsg]; simp [Dp, Matrix.mulVec_diagonal]
    ext x
    rw [Pi.add_apply, Dm_mulVec, Pm_mulVec]
    rcases x with i | j | e
    · simp [s2]
    · fin_cases j
      · simp [s0, s2, hw5, dm, hu5]
      · simp [s1, s2, hw6, dm, hu6]; ring
    · simp [s2, hwE, dm]
  have h9 := Submodule.finrank_mono hrange
  rw [LinearMap.finrank_range_of_inj hinj, Module.finrank_prod] at h9
  omega

end Model


/-! ## §3  the four E-part cases: `rank S ≤ 1` forces `rank (T - diag(0,2,0)) ≤ 2` -/
section Cases
variable {K : Type*} [Field K]

theorem rank_le_two_of_third_row (T : Matrix (Fin 3) (Fin 3) K)
    (h0 : T 2 0 = 0) (h1 : T 2 1 = 0) (h2 : T 2 2 = 0) : (T - Dp).rank ≤ 2 := by
  apply rank_le_two_of_det_zero
  simp [Matrix.det_fin_three, Dp, diagonal_apply, h0, h1, h2]

theorem rank_le_two_of_third_col (T : Matrix (Fin 3) (Fin 3) K)
    (h0 : T 0 2 = 0) (h1 : T 1 2 = 0) (h2 : T 2 2 = 0) : (T - Dp).rank ≤ 2 := by
  apply rank_le_two_of_det_zero
  simp [Matrix.det_fin_three, Dp, diagonal_apply, h0, h1, h2]

/-- case neither `u_E` nor `η_E` (`δ = 0`, 3 columns). -/
theorem case1 (h2 : (2 : K) ≠ 0) (T : Matrix (Fin 3) (Fin 3) K) (κ : K) (hk : κ ≠ 0)
    (hdet : (1 - T * Gm κ).det = -1) (hr : (S3 T κ 0).rank ≤ 1) : (T - Dp).rank ≤ 2 := by
  obtain ⟨a, c, hS⟩ := rank_le_one_decomp _ hr
  have e : ∀ i j, S3 T κ 0 i j = a i * c j := fun i j => by rw [hS]; simp [vecMulVec_apply]
  have hM : (Mcore T κ).rank ≤ 1 := by
    have : Mcore T κ = vecMulVec ![a 0, a 1, a 2] c := by
      ext i j
      have := e i.castSucc j
      fin_cases i <;> fin_cases j <;>
        simp [S3, Mcore, Gm, Dq, Matrix.mul_apply, Fin.sum_univ_three, diagonal_apply,
          vecMulVec_apply] at this ⊢ <;> linear_combination this
    rw [this]; exact Matrix.rank_vecMulVec_le _ _
  exact (core_neither_rank h2 T κ hk hdet hM).le

/-- case `u_E ≠ 0` only (`δ = 1`, 3 columns). -/
theorem case2 (T : Matrix (Fin 3) (Fin 3) K) (κ : K) (hk : κ ≠ 0)
    (hdet : (1 - T * Gm κ).det = -1) (hr : (S3 T κ 1).rank ≤ 1) : (T - Dp).rank ≤ 2 := by
  obtain ⟨a, c, hS⟩ := rank_le_one_decomp _ hr
  have e : ∀ i j, S3 T κ 1 i j = a i * c j := fun i j => by rw [hS]; simp [vecMulVec_apply]
  have e30 : (0 : K) = a 3 * c 0 := by simpa [S3] using e 3 0
  have e31 : (0 : K) = a 3 * c 1 := by simpa [S3] using e 3 1
  have e32 : (1 : K) = a 3 * c 2 := by simpa [S3] using e 3 2
  have e00 : T 0 0 - 2 = a 0 * c 0 := by simpa [S3] using e 0 0
  have e10 : T 1 0 = a 1 * c 0 := by simpa [S3] using e 1 0
  have e20 : T 2 0 = a 2 * c 0 := by simpa [S3] using e 2 0
  have e01 : T 0 1 = a 0 * c 1 := by simpa [S3] using e 0 1
  have e11 : T 1 1 = a 1 * c 1 := by simpa [S3] using e 1 1
  have e21 : T 2 1 = a 2 * c 1 := by simpa [S3] using e 2 1
  have ha3 : a 3 ≠ 0 := by intro h; rw [h] at e32; simp at e32
  have hc0 : c 0 = 0 := by
    rcases mul_eq_zero.1 e30.symm with h | h
    · exact absurd h ha3
    · exact h
  have hc1 : c 1 = 0 := by
    rcases mul_eq_zero.1 e31.symm with h | h
    · exact absurd h ha3
    · exact h
  rw [hc0] at e00 e10 e20
  rw [hc1] at e01 e11 e21
  have t00 : T 0 0 = 2 := by linear_combination e00
  have t10 : T 1 0 = 0 := by linear_combination e10
  have t20 : T 2 0 = 0 := by linear_combination e20
  have t01 : T 0 1 = 0 := by linear_combination e01
  have t11 : T 1 1 = 0 := by linear_combination e11
  have t21 : T 2 1 = 0 := by linear_combination e21
  simp [Matrix.det_fin_three, Gm, Matrix.one_apply, Matrix.mul_apply, Fin.sum_univ_three,
    diagonal_apply, t00, t10, t20, t01, t11, t21] at hdet
  have t22 : T 2 2 = 0 := by
    have : κ * T 2 2 = 0 := by linear_combination hdet
    rcases mul_eq_zero.1 this with h | h
    · exact absurd h hk
    · exact h
  exact rank_le_two_of_third_row T t20 t21 t22

/-- case `η_E ≠ 0` only (`δ = 0`, 4 columns). -/
theorem case3 (h2 : (2 : K) ≠ 0) (T : Matrix (Fin 3) (Fin 3) K) (κ : K) (hk : κ ≠ 0)
    (hdet : (1 - T * Gm κ).det = -1) (hr : (S4 T κ 0).rank ≤ 1) : (T - Dp).rank ≤ 2 := by
  obtain ⟨a, c, hS⟩ := rank_le_one_decomp _ hr
  have e : ∀ i j, S4 T κ 0 i j = a i * c j := fun i j => by rw [hS]; simp [vecMulVec_apply]
  have e00 : T 0 0 - 2 = a 0 * c 0 := by simpa [S4] using e 0 0
  have e01 : T 0 1 = a 0 * c 1 := by simpa [S4] using e 0 1
  have e02 : T 0 2 * κ = a 0 * c 2 := by simpa [S4] using e 0 2
  have e03 : T 0 2 = a 0 * c 3 := by simpa [S4] using e 0 3
  have e10 : T 1 0 = a 1 * c 0 := by simpa [S4] using e 1 0
  have e11 : T 1 1 = a 1 * c 1 := by simpa [S4] using e 1 1
  have e12 : T 1 2 * κ = a 1 * c 2 := by simpa [S4] using e 1 2
  have e13 : T 1 2 = a 1 * c 3 := by simpa [S4] using e 1 3
  have e22 : T 2 2 * κ - 2 = a 2 * c 2 := by simpa [S4] using e 2 2
  have e23 : T 2 2 = a 2 * c 3 := by simpa [S4] using e 2 3
  have hm0 : a 0 * (κ * c 3 - c 2) = 0 := by linear_combination (-κ) * e03 + e02
  have hm1 : a 1 * (κ * c 3 - c 2) = 0 := by linear_combination (-κ) * e13 + e12
  have hm2 : a 2 * (κ * c 3 - c 2) = 2 := by linear_combination (-κ) * e23 + e22
  have hm : κ * c 3 - c 2 ≠ 0 := by
    intro h; rw [h, mul_zero] at hm2; exact h2 hm2.symm
  have a0 : a 0 = 0 := by
    rcases mul_eq_zero.1 hm0 with h | h
    · exact h
    · exact absurd h hm
  have a1 : a 1 = 0 := by
    rcases mul_eq_zero.1 hm1 with h | h
    · exact h
    · exact absurd h hm
  rw [a0] at e00 e01 e03
  rw [a1] at e10 e11 e13
  have t00 : T 0 0 = 2 := by linear_combination e00
  have t01 : T 0 1 = 0 := by linear_combination e01
  have t02 : T 0 2 = 0 := by linear_combination e03
  have t10 : T 1 0 = 0 := by linear_combination e10
  have t11 : T 1 1 = 0 := by linear_combination e11
  have t12 : T 1 2 = 0 := by linear_combination e13
  simp [Matrix.det_fin_three, Gm, Matrix.one_apply, Matrix.mul_apply, Fin.sum_univ_three,
    diagonal_apply, t00, t01, t02, t10, t11, t12] at hdet
  have t22 : T 2 2 = 0 := by
    have : κ * T 2 2 = 0 := by linear_combination hdet
    rcases mul_eq_zero.1 this with h | h
    · exact absurd h hk
    · exact h
  exact rank_le_two_of_third_col T t02 t12 t22

/-- case `u_E ≠ 0` and `η_E ≠ 0` (`δ = 1`, 4 columns): no `k` hypothesis needed. -/
theorem case4 (T : Matrix (Fin 3) (Fin 3) K) (κ : K) (hr : (S4 T κ 1).rank ≤ 1) :
    (T - Dp).rank ≤ 2 := by
  obtain ⟨a, c, hS⟩ := rank_le_one_decomp _ hr
  have e : ∀ i j, S4 T κ 1 i j = a i * c j := fun i j => by rw [hS]; simp [vecMulVec_apply]
  have e30 : (0 : K) = a 3 * c 0 := by simpa [S4] using e 3 0
  have e32 : (1 : K) = a 3 * c 2 := by simpa [S4] using e 3 2
  have e33 : (0 : K) = a 3 * c 3 := by simpa [S4] using e 3 3
  have e03 : T 0 2 = a 0 * c 3 := by simpa [S4] using e 0 3
  have e13 : T 1 2 = a 1 * c 3 := by simpa [S4] using e 1 3
  have e23 : T 2 2 = a 2 * c 3 := by simpa [S4] using e 2 3
  have ha3 : a 3 ≠ 0 := by intro h; rw [h] at e32; simp at e32
  have hc3 : c 3 = 0 := by
    rcases mul_eq_zero.1 e33.symm with h | h
    · exact absurd h ha3
    · exact h
  rw [hc3] at e03 e13 e23
  exact rank_le_two_of_third_col T (by linear_combination e03) (by linear_combination e13)
    (by linear_combination e23)

end Cases


/-! ## §4  composition: `spec0_core_U4` -/
section Compose
variable {K : Type*} [Field K] {E : Type*} [Fintype E] [DecidableEq E]

local notation "I5" => Sum.inr (Sum.inl (0 : Fin 2))
local notation "I6" => Sum.inr (Sum.inl (1 : Fin 2))
local notation "cE " e:max => Sum.inr (Sum.inr e)

/-- `dim ker(Λ-1) + dim ker(Λ+1) ≥ dim W` (char ≠ 2) forces `Λ² = 1`. -/
theorem invol_of_dims_ge {W : Type*} [AddCommGroup W] [Module K W] [FiniteDimensional K W]
    (h2 : (2 : K) ≠ 0) (Λ : W →ₗ[K] W)
    (h : finrank K W ≤ finrank K (ker (Λ - 1)) + finrank K (ker (Λ + 1))) :
    ∀ w, Λ (Λ w) = w := by
  have hd : ker (Λ - 1) ⊓ ker (Λ + 1) = ⊥ := by
    rw [eq_bot_iff]
    intro w ⟨h1, h3⟩
    have e1 : Λ w = w := sub_eq_zero.1 (by simpa using h1)
    have e2 : Λ w = -w := eq_neg_of_add_eq_zero_left (by simpa using h3)
    have : (2 : K) • w = 0 := by rw [two_smul]; nth_rewrite 1 [← e1]; rw [e2]; abel
    simpa [h2] using this
  have hfs := Submodule.finrank_sup_add_finrank_inf_eq (ker (Λ - 1)) (ker (Λ + 1))
  rw [hd, finrank_bot] at hfs
  have hle := Submodule.finrank_le (ker (Λ - 1) ⊔ ker (Λ + 1))
  have htop : ker (Λ - 1) ⊔ ker (Λ + 1) = ⊤ :=
    Submodule.eq_top_of_finrank_eq (by omega)
  intro w
  have hw : w ∈ ker (Λ - 1) ⊔ ker (Λ + 1) := by rw [htop]; trivial
  obtain ⟨x, hx, y, hy, rfl⟩ := Submodule.mem_sup.1 hw
  have ex : Λ x = x := sub_eq_zero.1 (by simpa using hx)
  have ey : Λ y = -y := eq_neg_of_add_eq_zero_left (by simpa using hy)
  simp [ex, ey]

theorem vt_gram (u η : Ix E → K) (hu5 : u I5 = 0) (hu6 : u I6 = 0) (hη5 : η I5 = 0)
    (hη6 : η I6 = 0) : (vt η)ᵀ * vt u = Gm (η ⬝ᵥ u) := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [vt, Gm, Matrix.mul_apply, dotProduct, diagonal_apply, hu5, hu6, hη5, hη6]

theorem det_gm (u η : Ix E → K) (T : Matrix (Fin 3) (Fin 3) K) (hu5 : u I5 = 0) (hu6 : u I6 = 0)
    (hη5 : η I5 = 0) (hη6 : η I6 = 0) (hdet : (Pm u η T).det = -1) :
    (1 - T * Gm (η ⬝ᵥ u)).det = -1 :=
  core_det_neg (vt u) (vt η) T _ (vt_gram u η hu5 hu6 hη5 hη6) hdet

theorem dot_u (u η : Ix E → K) (hη5 : η I5 = 0) (hη6 : η I6 = 0)
    (hu : u I5 = 0 ∧ u I6 = 0) :
    η ⬝ᵥ u = kC η u + lam η u := by
  rw [dot_split η u hη5 hη6]; rfl

theorem S3_ne_zero (T : Matrix (Fin 3) (Fin 3) K) (κ δ : K) (h : Mcore T κ ≠ 0) :
    S3 T κ δ ≠ 0 := by
  intro hS; apply h
  ext i j
  have := congrFun (congrFun hS i.castSucc) j
  fin_cases i <;> fin_cases j <;>
    simp [S3, Mcore, Gm, Dq, Matrix.mul_apply, Fin.sum_univ_three, diagonal_apply] at this ⊢ <;>
    first | linear_combination this | exact this

theorem S4_ne_zero (T : Matrix (Fin 3) (Fin 3) K) (κ δ : K) (h : Mcore T κ ≠ 0) :
    S4 T κ δ ≠ 0 := by
  intro hS; apply h
  ext i j
  have := congrFun (congrFun hS i.castSucc) j.castSucc
  fin_cases i <;> fin_cases j <;>
    simp [S4, Mcore, Gm, Dq, Matrix.mul_apply, Fin.sum_univ_three, diagonal_apply] at this ⊢ <;>
    first | linear_combination this | exact this

theorem Mcore_ne_zero (h2 : (2 : K) ≠ 0) (T : Matrix (Fin 3) (Fin 3) K) (κ : K)
    (hdet : (1 - T * Gm κ).det = -1) : Mcore T κ ≠ 0 := by
  by_cases hk : κ = 0
  · subst hk; exact core_k0_ne_zero h2 T
  · exact core_neither_ne_zero h2 T κ hdet


theorem rank_eq_finrank (M : Matrix (Ix E) (Ix E) K) :
    (M - 1).rank = finrank K (range (Matrix.toLin' M - 1)) := by
  have hsub : Matrix.toLin' M - 1 = Matrix.toLin' (M - 1) := by
    rw [map_sub, Matrix.toLin'_one]; rfl
  rw [hsub]; rfl

/-- the core case `η_C ≠ 0` (E-part cases and neither), `k = 0` left as `hk0`. -/
theorem core_main (h2 : (2 : K) ≠ 0) (u η : Ix E → K) (T : Matrix (Fin 3) (Fin 3) K)
    (hu5 : u I5 = 0) (hu6 : u I6 = 0) (hη5 : η I5 = 0) (hη6 : η I6 = 0)
    (hdet : (Pm u η T).det = -1) (hηC : ∃ c, η (Sum.inl c) ≠ 0)
    (hk0 : η ⬝ᵥ u = 0 → (Lam u η T - 1).rank = 4 → Lam u η T * Lam u η T = 1) :
    4 ≤ (Lam u η T - 1).rank ∧
      ((Lam u η T - 1).rank = 4 → Lam u η T * Lam u η T = 1) := by
  have hU : IsUnit (Pm u η T).det := by rw [hdet]; exact isUnit_one.neg
  have hdk : (1 - T * Gm (η ⬝ᵥ u)).det = -1 := det_gm u η T hu5 hu6 hη5 hη6 hdet
  have hdu := dot_u u η hη5 hη6 ⟨hu5, hu6⟩
  have key : ∃ r : ℕ, 1 ≤ r ∧
      3 + r ≤ finrank K (range (Matrix.toLin' (Lam u η T) - 1)) ∧
      (r ≤ 1 → η ⬝ᵥ u ≠ 0 → (T - Dp).rank ≤ 2) := by
    by_cases hu : ∃ e, u (cE e) ≠ 0 <;> by_cases hη : ∃ e, η (cE e) ≠ 0
    · refine ⟨(S4 T (kC η u) 1).rank, ?_,
        key4 h2 u η T hu5 hu6 hη5 hη6 hU hη 1 (Or.inr hu), fun hr _ => case4 T _ hr⟩
      refine rank_pos_of_ne_zero _ (fun h => ?_)
      have := congrFun (congrFun h 3) 2
      simp [S4] at this
    · push_neg at hη
      have hk : η ⬝ᵥ u = kC η u := by rw [hdu, lam_zero η u hη]; ring
      refine ⟨(S3 T (kC η u) 1).rank, ?_,
        key3 h2 u η T hu5 hu6 hη5 hη6 hU hη 1 (Or.inr hu),
        fun hr hk' => case2 T _ (by rwa [← hk]) (by rw [← hk]; exact hdk) hr⟩
      refine rank_pos_of_ne_zero _ (fun h => ?_)
      have := congrFun (congrFun h 3) 2
      simp [S3] at this
    · push_neg at hu
      have hk : η ⬝ᵥ u = kC η u := by rw [hdu, lam_zero' η u hu]; ring
      have hd' : (1 - T * Gm (kC η u)).det = -1 := by rw [← hk]; exact hdk
      exact ⟨(S4 T (kC η u) 0).rank,
        rank_pos_of_ne_zero _ (S4_ne_zero _ _ _ (Mcore_ne_zero h2 T _ hd')),
        key4 h2 u η T hu5 hu6 hη5 hη6 hU hη 0 (Or.inl rfl),
        fun hr hk' => case3 h2 T _ (by rwa [← hk]) hd' hr⟩
    · push_neg at hu hη
      have hk : η ⬝ᵥ u = kC η u := by rw [hdu, lam_zero η u hη]; ring
      have hd' : (1 - T * Gm (kC η u)).det = -1 := by rw [← hk]; exact hdk
      exact ⟨(S3 T (kC η u) 0).rank,
        rank_pos_of_ne_zero _ (S3_ne_zero _ _ _ (Mcore_ne_zero h2 T _ hd')),
        key3 h2 u η T hu5 hu6 hη5 hη6 hU hη 0 (Or.inl rfl),
        fun hr hk' => case1 h2 T _ (by rwa [← hk]) hd' hr⟩
  obtain ⟨r, hr1, hr3, hr2⟩ := key
  have hR := rank_eq_finrank (Lam u η T)
  refine ⟨by omega, fun h4 => ?_⟩
  by_cases hk : η ⬝ᵥ u = 0
  · exact hk0 hk h4
  have hT := hr2 (by omega) hk
  have hE := Em1_bound h2 u η T hu5 hu6 hη5 hη6 hU hηC hT
  have h1 := LinearMap.finrank_range_add_finrank_ker (Matrix.toLin' (Lam u η T) - 1)
  have h5 := finrank_ix (K := K) E
  have hinv := invol_of_dims_ge h2 (Matrix.toLin' (Lam u η T)) (by omega)
  apply Matrix.toLin'.injective
  rw [Matrix.toLin'_mul, Matrix.toLin'_one]
  exact LinearMap.ext fun w => hinv w

/-- **`spec0_core_U4`.**  #0's model at `U = 4` (coordinates `Fin 4 ⊕ (Fin 2 ⊕ E)`; `D = -1` on `C4`
and `e5`, `+1` on `e6`, `E'`; `P = 1 - X T Yᵀ` with `X = (e5, e6, u)`, `Y = (e5, e6, η)`, `u, η`
vanishing on `e5, e6`; `det P = -1`; char ≠ 2).  Then `rank(Λ - 1) ≥ 4` and rank `= 4 ⇒ Λ² = 1`,
for `Λ = P⁻¹ D`, EXCEPT on the locus `k = η·u = 0`, where the involution step is the hypothesis
`hk0` (certified separately by the Singular radical computation).  The rank bound itself holds
with no `k` hypothesis. -/
theorem spec0_core_U4 (h2 : (2 : K) ≠ 0) (u η : Ix E → K) (T : Matrix (Fin 3) (Fin 3) K)
    (hu5 : u I5 = 0) (hu6 : u I6 = 0) (hη5 : η I5 = 0) (hη6 : η I6 = 0)
    (hdet : (Pm u η T).det = -1)
    (hk0 : η ⬝ᵥ u = 0 → (Lam u η T - 1).rank = 4 → Lam u η T * Lam u η T = 1) :
    4 ≤ (Lam u η T - 1).rank ∧
      ((Lam u η T - 1).rank = 4 → Lam u η T * Lam u η T = 1) := by
  by_cases hηC : ∃ c, η (Sum.inl c) ≠ 0
  · exact core_main h2 u η T hu5 hu6 hη5 hη6 hdet hηC hk0
  · push_neg at hηC
    have hU : IsUnit (Pm u η T).det := by rw [hdet]; exact isUnit_one.neg
    have hd : ∀ j, dm K E j * dm K E j = 1 := by
      intro j; rcases j with j | e
      · fin_cases j <;> simp [dm]
      · simp [dm]
    have hPc : ∀ (j : Ix E) (i : Fin 4), Pm u η T j (Sum.inl i) =
        (1 : Matrix (Ix E) (Ix E) K) j (Sum.inl i) := by
      intro j i
      simp [Pm, Matrix.mul_apply, Fin.sum_univ_three, vt, hηC i]
    exact lemmaU_mat_T h2 (dm K E) hd (Pm u η T) hU hPc

end Compose

end SpecLemmaU2

#print axioms SpecLemmaU2.kb
#print axioms SpecLemmaU2.key3
#print axioms SpecLemmaU2.key4
#print axioms SpecLemmaU2.Em1_bound
#print axioms SpecLemmaU2.case1
#print axioms SpecLemmaU2.case2
#print axioms SpecLemmaU2.case3
#print axioms SpecLemmaU2.case4
#print axioms SpecLemmaU2.core_main
#print axioms SpecLemmaU2.spec0_core_U4
