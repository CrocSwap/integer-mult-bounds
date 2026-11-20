import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.Algebra.Field.ZMod
import Mathlib.NumberTheory.Padics.RingHoms

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace TensorPot
open Module

section dims
variable {K V T : Type*} [Field K] [AddCommGroup V] [Module K V] [FiniteDimensional K V]
  [AddCommGroup T] [Module K T] [FiniteDimensional K T]

lemma map_dim_le (f : V →ₗ[K] T) {C D : Submodule K V} (h : C ≤ D) :
    finrank K (D.map f) + finrank K C ≤ finrank K (C.map f) + finrank K D := by
  have hD := LinearMap.finrank_range_add_finrank_ker (f.domRestrict D)
  have hC := LinearMap.finrank_range_add_finrank_ker (f.domRestrict C)
  rw [LinearMap.range_domRestrict] at hD hC
  have hk : finrank K (LinearMap.ker (f.domRestrict C)) ≤ finrank K (LinearMap.ker (f.domRestrict D)) := by
    have e1 := Submodule.finrank_map_subtype_eq C (LinearMap.ker (f.domRestrict C))
    have e2 := Submodule.finrank_map_subtype_eq D (LinearMap.ker (f.domRestrict D))
    rw [← e1, ← e2]
    apply Submodule.finrank_mono
    rintro x ⟨y, hy, rfl⟩
    refine ⟨⟨y.1, h y.2⟩, ?_, rfl⟩
    simpa [LinearMap.mem_ker] using hy
  omega

/-- ascent lemma -/
lemma ascent_dim (f : V →ₗ[K] T) {C D : Submodule K V} (h : C ≤ D) (S : Submodule K T)
    (hS : C.map f ≤ S) :
    finrank K (S ⊔ D.map f : Submodule K T) + finrank K C ≤ finrank K S + finrank K D := by
  have h1 := Submodule.finrank_sup_add_finrank_inf_eq S (D.map f)
  have h2 := Submodule.finrank_mono (le_inf hS (Submodule.map_mono h) : C.map f ≤ S ⊓ D.map f)
  have h3 := map_dim_le f h
  omega
end dims

/-! ## Run model -/
section model
open Finset Function
variable {K : Type*} [Field K] {ν ω ι : Type*} [Fintype ν] [Fintype ω] [DecidableEq ι]

/-- `c ↦ c ⊗ w`, as the outer-product matrix `c wᵀ` (V ⊗ W ≅ Matrix ν ω K). -/
def outer (w : ω → K) : (ν → K) →ₗ[K] Matrix ν ω K where
  toFun c := Matrix.vecMulVec c w
  map_add' a b := by ext i j; simp [Matrix.vecMulVec, add_mul]
  map_smul' a b := by ext i j; simp [Matrix.vecMulVec, mul_assoc]

lemma outer_apply (w : ω → K) (c : ν → K) : outer w c = Matrix.vecMulVec c w := rfl

/-- `C ⊗ w`. -/
def pot (C : Submodule K (ν → K)) (w : ω → K) : Submodule K (Matrix ν ω K) := C.map (outer w)

lemma pot_zero (C : Submodule K (ν → K)) : pot C (0 : ω → K) = ⊥ := by
  unfold pot
  rw [eq_bot_iff]; rintro _ ⟨c, -, rfl⟩
  ext i j; simp [outer_apply, Matrix.vecMulVec]

lemma pot_mono {C D : Submodule K (ν → K)} (h : C ≤ D) (w : ω → K) : pot C w ≤ pot D w :=
  Submodule.map_mono h

/-- A register state: a chart (subspace of `K^ν`) and a value (vector in `K^ω`) per register. -/
structure St (K ν ω ι : Type*) [Field K] where
  ch : ι → Submodule K (ν → K)
  v : ι → (ω → K)

/-- Potential of a state: `Σ_r C_r ⊗ w_r`. -/
def potOf (s : St K ν ω ι) : Submodule K (Matrix ν ω K) := ⨆ r, pot (s.ch r) (s.v r)

lemma potOf_le_iff (s : St K ν ω ι) (S : Submodule K (Matrix ν ω K)) :
    potOf s ≤ S ↔ ∀ r, pot (s.ch r) (s.v r) ≤ S := iSup_le_iff

/-- Moves. `P` is the finite set of public registers. Costs: (owned climb, public climb).
ADD needs `chart d ≤ chart e` (REV's "same chart" is the special case `=`).
Descents/discards (discard = descent to `⊥`) are owned-only; publics only ascend. -/
inductive Mv (P : Finset ι) (s : St K ν ω ι) : St K ν ω ι → ℕ → ℕ → Prop
  | add (d e : ι) (l : K) (h : s.ch d ≤ s.ch e) :
      Mv P s { s with v := update s.v d (s.v d + l • s.v e) } 0 0
  | init (r : ι) : Mv P s { s with v := update s.v r 0 } 0 0
  | down (r : ι) (D : Submodule K (ν → K)) (hr : r ∉ P) (h : D ≤ s.ch r) :
      Mv P s { s with ch := update s.ch r D } 0 0
  | upOwn (r : ι) (D : Submodule K (ν → K)) (hr : r ∉ P) (h : s.ch r ≤ D) :
      Mv P s { s with ch := update s.ch r D } (finrank K D - finrank K (s.ch r)) 0
  | upPub (r : ι) (D : Submodule K (ν → K)) (hr : r ∈ P) (h : s.ch r ≤ D) :
      Mv P s { s with ch := update s.ch r D } 0 (finrank K D - finrank K (s.ch r))

/-- A run from `s0` to `s`: `S` is the cumulative potential `Σ_history C ⊗ w`,
`c` the owned climbs, `p` the public climbs. -/
inductive Run (P : Finset ι) (s0 : St K ν ω ι) :
    St K ν ω ι → Submodule K (Matrix ν ω K) → ℕ → ℕ → Prop
  | refl : Run P s0 s0 (potOf s0) 0 0
  | step {s s' S c p dc dp} : Run P s0 s S c p → Mv P s s' dc dp →
      Run P s0 s' (S ⊔ potOf s') (c + dc) (p + dp)

lemma pot_update_le (s : St K ν ω ι) (S : Submodule K (Matrix ν ω K)) (hS : potOf s ≤ S) (r : ι)
    (r' : ι) (hr : r' ≠ r) : pot (s.ch r') (s.v r') ≤ S :=
  le_trans (le_iSup (fun r => pot (s.ch r) (s.v r)) r') hS

/-- Per-move: ADD / INIT / descent / discard add nothing; an ascent adds ≤ its climb. -/
theorem step_bound {P : Finset ι} {s s' : St K ν ω ι} {dc dp : ℕ}
    (hm : Mv P s s' dc dp) (S : Submodule K (Matrix ν ω K)) (hS : potOf s ≤ S) :
    finrank K (S ⊔ potOf s' : Submodule K _) ≤ finrank K S + dc + dp := by
  have hr : ∀ r, pot (s.ch r) (s.v r) ≤ S := fun r =>
    le_trans (le_iSup (fun r => pot (s.ch r) (s.v r)) r) hS
  cases hm with
  | add d e l h =>
    have : potOf { s with v := update s.v d (s.v d + l • s.v e) } ≤ S := by
      rw [potOf_le_iff]; intro r'
      by_cases hd : r' = d
      · subst hd
        simp only [update_self]
        rintro _ ⟨c, hc, rfl⟩
        have h1 : outer (s.v r') c ∈ S := hr r' ⟨c, hc, rfl⟩
        have h2 : outer (s.v e) c ∈ S := hr e ⟨c, h hc, rfl⟩
        have : outer (s.v r' + l • s.v e) c = outer (s.v r') c + l • outer (s.v e) c := by
          simp only [outer_apply]; ext i j; simp [Matrix.vecMulVec, mul_add, mul_left_comm]
        rw [this]; exact S.add_mem h1 (S.smul_mem l h2)
      · simpa [update_of_ne hd] using hr r'
    rw [sup_eq_left.2 this]; omega
  | init r' =>
    have : potOf { s with v := update s.v r' 0 } ≤ S := by
      rw [potOf_le_iff]; intro r
      by_cases hd : r = r'
      · subst hd; simp [pot_zero]
      · simpa [update_of_ne hd] using hr r
    rw [sup_eq_left.2 this]; omega
  | down r' D _ h =>
    have : potOf { s with ch := update s.ch r' D } ≤ S := by
      rw [potOf_le_iff]; intro r
      by_cases hd : r = r'
      · subst hd; simp only [update_self]; exact le_trans (pot_mono h _) (hr r)
      · simpa [update_of_ne hd] using hr r
    rw [sup_eq_left.2 this]; omega
  | upOwn r' D _ h =>
    have key := ascent_dim (outer (s.v r')) h S (hr r')
    have hle : potOf { s with ch := update s.ch r' D } ≤ S ⊔ pot D (s.v r') := by
      rw [potOf_le_iff]; intro r
      by_cases hd : r = r'
      · subst hd; simp only [update_self]; exact le_sup_right
      · simpa [update_of_ne hd] using le_sup_of_le_left (hr r)
    have := Submodule.finrank_mono (sup_le_sup_left hle S)
    have hm := Submodule.finrank_mono h
    have : finrank K (S ⊔ potOf { s with ch := update s.ch r' D } : Submodule K _) ≤ finrank K (S ⊔ pot D (s.v r') : Submodule K _) :=
      Submodule.finrank_mono (sup_le le_sup_left hle)
    unfold pot at *
    omega
  | upPub r' D _ h =>
    have key := ascent_dim (outer (s.v r')) h S (hr r')
    have hle : potOf { s with ch := update s.ch r' D } ≤ S ⊔ pot D (s.v r') := by
      rw [potOf_le_iff]; intro r
      by_cases hd : r = r'
      · subst hd; simp only [update_self]; exact le_sup_right
      · simpa [update_of_ne hd] using le_sup_of_le_left (hr r)
    have hm := Submodule.finrank_mono h
    have : finrank K (S ⊔ potOf { s with ch := update s.ch r' D } : Submodule K _) ≤ finrank K (S ⊔ pot D (s.v r') : Submodule K _) :=
      Submodule.finrank_mono (sup_le le_sup_left hle)
    unfold pot at *
    omega


/-- Invariants of a run. -/
theorem run_inv {P : Finset ι} {s0 s : St K ν ω ι} {S : Submodule K (Matrix ν ω K)} {c p : ℕ}
    (h : Run P s0 s S c p) :
    potOf s ≤ S ∧ potOf s0 ≤ S ∧ finrank K S ≤ finrank K (potOf s0) + c + p := by
  induction h with
  | refl => exact ⟨le_rfl, le_rfl, by omega⟩
  | step hr hm ih =>
    obtain ⟨h1, h2, h3⟩ := ih
    refine ⟨le_sup_right, le_trans h2 le_sup_left, ?_⟩
    have := step_bound hm _ h1
    omega

lemma sum_update_chart (P : Finset ι) (ch : ι → Submodule K (ν → K)) (r : ι) (D : Submodule K (ν → K))
    (hr : r ∈ P) :
    ∑ x ∈ P, finrank K (update ch r D x) + finrank K (ch r) = ∑ x ∈ P, finrank K (ch x) + finrank K D := by
  rw [← Finset.add_sum_erase P _ hr, ← Finset.add_sum_erase P (fun x => finrank K (ch x)) hr]
  have : ∑ x ∈ P.erase r, finrank K (update ch r D x) = ∑ x ∈ P.erase r, finrank K (ch x) :=
    Finset.sum_congr rfl fun x hx => by rw [update_of_ne (Finset.ne_of_mem_erase hx)]
  rw [this]; rw [update_self]; ring

lemma sum_update_chart_out (P : Finset ι) (ch : ι → Submodule K (ν → K)) (r : ι) (D : Submodule K (ν → K))
    (hr : r ∉ P) :
    ∑ x ∈ P, finrank K (update ch r D x) = ∑ x ∈ P, finrank K (ch x) :=
  Finset.sum_congr rfl fun x hx => by rw [update_of_ne (fun h : x = r => hr (h ▸ hx))]

/-- Public climbs telescope to the final minus start chart dimensions. -/
theorem run_pub_climb {P : Finset ι} {s0 s : St K ν ω ι} {S : Submodule K (Matrix ν ω K)} {c p : ℕ}
    (h : Run P s0 s S c p) :
    p + ∑ r ∈ P, finrank K (s0.ch r) = ∑ r ∈ P, finrank K (s.ch r) := by
  induction h with
  | refl => simp
  | step hr hm ih =>
    cases hm with
    | add d e l h => simpa using ih
    | init r => simpa using ih
    | down r D hr' h => simpa [sum_update_chart_out P _ r D hr'] using ih
    | upOwn r D hr' h => simpa [sum_update_chart_out P _ r D hr'] using ih
    | upPub r D hr' h =>
      rename_i s1 S1 c1 p1
      have := sum_update_chart P (s1.ch) r D hr'
      have hm := Submodule.finrank_mono h
      simp only
      omega

/-- Start / final potentials of the publics. -/
def S0 (P : Finset ι) (s : St K ν ω ι) : Submodule K (Matrix ν ω K) :=
  ⨆ r ∈ P, pot (s.ch r) (s.v r)

/-- **HEADLINE (REV §1).** Owned registers start with value 0; publics only ascend.
`finrank(S0 ⊔ T) + Σ_P dim(start chart) ≤ finrank S0 + R + Σ_P dim(final chart)`,
i.e. `R ≥ dim(S0+T) − dim S0 − Σ_publics (dim F_P − dim S_P)`. -/
theorem headline {P : Finset ι} {s0 s : St K ν ω ι} {S : Submodule K (Matrix ν ω K)} {c p : ℕ}
    (h0 : ∀ r, r ∉ P → s0.v r = 0) (h : Run P s0 s S c p) :
    finrank K (S0 P s0 ⊔ S0 P s : Submodule K _) + ∑ r ∈ P, finrank K (s0.ch r)
      ≤ finrank K (S0 P s0) + c + ∑ r ∈ P, finrank K (s.ch r) := by
  obtain ⟨h1, h2, h3⟩ := run_inv h
  have h4 := run_pub_climb h
  have hS0 : potOf s0 ≤ S0 P s0 := by
    rw [potOf_le_iff]; intro r
    by_cases hr : r ∈ P
    · exact le_biSup (fun r => pot (s0.ch r) (s0.v r)) hr
    · rw [h0 r hr, pot_zero]; exact bot_le
  have hS1 : S0 P s0 ≤ S := le_trans (iSup₂_le fun r _ => le_trans
    (le_iSup (fun r => pot (s0.ch r) (s0.v r)) r) le_rfl) h2
  have hS2 : S0 P s ≤ S := le_trans (iSup₂_le fun r _ => le_iSup (fun r => pot (s.ch r) (s.v r)) r) h1
  have h5 := Submodule.finrank_mono (sup_le hS1 hS2)
  have h6 := Submodule.finrank_mono hS0
  omega


/-! ## Item 4: ring-valued ADD scalars, reduction to the field `K` -/
section reduction
variable {Λ : Type*} [CommRing Λ] (φ : Λ →+* K)

/-- States over a coefficient ring `Λ` (values in `Λ^ω`); charts are still `K`-subspaces. -/
structure StR (K ν ω ι Λ : Type*) [Field K] where
  ch : ι → Submodule K (ν → K)
  v : ι → (ω → Λ)

inductive MvR (P : Finset ι) (s : StR K ν ω ι Λ) : StR K ν ω ι Λ → ℕ → ℕ → Prop
  | add (d e : ι) (l : Λ) (h : s.ch d ≤ s.ch e) :
      MvR P s { s with v := update s.v d (s.v d + l • s.v e) } 0 0
  | init (r : ι) : MvR P s { s with v := update s.v r 0 } 0 0
  | down (r : ι) (D : Submodule K (ν → K)) (hr : r ∉ P) (h : D ≤ s.ch r) :
      MvR P s { s with ch := update s.ch r D } 0 0
  | upOwn (r : ι) (D : Submodule K (ν → K)) (hr : r ∉ P) (h : s.ch r ≤ D) :
      MvR P s { s with ch := update s.ch r D } (finrank K D - finrank K (s.ch r)) 0
  | upPub (r : ι) (D : Submodule K (ν → K)) (hr : r ∈ P) (h : s.ch r ≤ D) :
      MvR P s { s with ch := update s.ch r D } 0 (finrank K D - finrank K (s.ch r))

inductive RunR (P : Finset ι) (s0 : StR K ν ω ι Λ) : StR K ν ω ι Λ → ℕ → ℕ → Prop
  | refl : RunR P s0 s0 0 0
  | step {s s' c p dc dp} : RunR P s0 s c p → MvR P s s' dc dp → RunR P s0 s' (c + dc) (p + dp)

/-- Coefficient-wise reduction of a state. -/
def red (s : StR K ν ω ι Λ) : St K ν ω ι := ⟨s.ch, fun r j => φ (s.v r j)⟩

lemma red_mv {P : Finset ι} {s s' : StR K ν ω ι Λ} {dc dp : ℕ} (h : MvR P s s' dc dp) :
    Mv P (red φ s) (red φ s') dc dp := by
  cases h with
  | add d e l h =>
    have := Mv.add (P := P) (s := red φ s) d e (φ l) h
    have e : red φ { s with v := update s.v d (s.v d + l • s.v e) } =
        { red φ s with v := update (red φ s).v d ((red φ s).v d + φ l • (red φ s).v e) } := by
      simp only [red]; congr 1; funext r j
      by_cases hr : r = d
      · subst hr; simp
      · simp [update_of_ne hr]
    rw [e]; exact this
  | init r =>
    have := Mv.init (P := P) (s := red φ s) r
    have e : red φ { s with v := update s.v r 0 } =
        { red φ s with v := update (red φ s).v r 0 } := by
      simp only [red]; congr 1; funext r' j
      by_cases hr : r' = r
      · subst hr; simp
      · simp [update_of_ne hr]
    rw [e]; exact this
  | down r D hr h => exact Mv.down r D hr h
  | upOwn r D hr h => exact Mv.upOwn r D hr h
  | upPub r D hr h => exact Mv.upPub r D hr h

lemma red_run {P : Finset ι} {s0 s : StR K ν ω ι Λ} {c p : ℕ} (h : RunR P s0 s c p) :
    ∃ S, Run P (red φ s0) (red φ s) S c p := by
  induction h with
  | refl => exact ⟨_, Run.refl⟩
  | step hr hm ih =>
    obtain ⟨S, hS⟩ := ih
    exact ⟨_, Run.step hS (red_mv φ hm)⟩

/-- **Item 4.** A run with arbitrary `Λ`-scalars in ADD (e.g. `Λ = ℤ_[2]`, `φ` = reduction mod 2)
obeys the headline bound for the reduced states. -/
theorem headline_reduced {P : Finset ι} {s0 s : StR K ν ω ι Λ} {c p : ℕ}
    (h0 : ∀ r, r ∉ P → ∀ j, φ (s0.v r j) = 0) (h : RunR P s0 s c p) :
    finrank K (S0 P (red φ s0) ⊔ S0 P (red φ s) : Submodule K _)
        + ∑ r ∈ P, finrank K (s0.ch r)
      ≤ finrank K (S0 P (red φ s0)) + c + ∑ r ∈ P, finrank K (s.ch r) := by
  obtain ⟨S, hS⟩ := red_run φ h
  exact headline (s0 := red φ s0) (s := red φ s) (fun r hr => funext fun j => h0 r hr j) hS

/-- The 2-adic instance: `ℤ_[2] → 𝔽₂`. -/
theorem headline_padic2 {P : Finset ι} {s0 s : StR (ZMod 2) ν ω ι ℤ_[2]} {c p : ℕ}
    (h0 : ∀ r, r ∉ P → ∀ j, PadicInt.toZMod (s0.v r j) = 0) (h : RunR P s0 s c p) :
    finrank (ZMod 2) (S0 P (red PadicInt.toZMod s0) ⊔ S0 P (red PadicInt.toZMod s) : Submodule (ZMod 2) _)
        + ∑ r ∈ P, finrank (ZMod 2) (s0.ch r)
      ≤ finrank (ZMod 2) (S0 P (red PadicInt.toZMod s0)) + c + ∑ r ∈ P, finrank (ZMod 2) (s.ch r) :=
  haveI : Fact (Nat.Prime 2) := ⟨Nat.prime_two⟩
  headline_reduced PadicInt.toZMod h0 h

end reduction

/-! ## Simplified headline: `dim(S0 ⊔ T) ≤ R + Σ_P dim(final chart)` -/
section simple
lemma finrank_biSup_le {T : Type*} [AddCommGroup T] [Module K T] [FiniteDimensional K T]
    (f : ι → Submodule K T) (F : Finset ι) :
    finrank K (⨆ r ∈ F, f r : Submodule K T) ≤ ∑ r ∈ F, finrank K (f r) := by
  induction F using Finset.induction_on with
  | empty => simp
  | insert a F ha ih =>
    rw [Finset.iSup_insert, Finset.sum_insert ha]
    exact le_trans (Submodule.finrank_add_le_finrank_add_finrank _ _) (by omega)

lemma finrank_S0_le (P : Finset ι) (s : St K ν ω ι) :
    finrank K (S0 P s) ≤ ∑ r ∈ P, finrank K (s.ch r) :=
  le_trans (finrank_biSup_le _ P) (Finset.sum_le_sum fun r _ => Submodule.finrank_map_le _ _)

/-- Headline, start-free form. -/
theorem headline' {P : Finset ι} {s0 s : St K ν ω ι} {S : Submodule K (Matrix ν ω K)} {c p : ℕ}
    (h0 : ∀ r, r ∉ P → s0.v r = 0) (h : Run P s0 s S c p) :
    finrank K (S0 P s0 ⊔ S0 P s : Submodule K _) ≤ c + ∑ r ∈ P, finrank K (s.ch r) := by
  have := headline h0 h
  have := finrank_S0_le P s0
  omega
end simple


/-! ## Item 2: the toy form, `R ≥ rank (Q∘M)` -/
section toy
variable {Q J O : Type*} [Fintype Q] [Fintype J] [Fintype O]
  [DecidableEq Q] [DecidableEq J] [DecidableEq O]

/-- value coordinates: `x`-block, `y`-block, relay block -/
abbrev Wd (Q J : Type*) := Q ⊕ Q ⊕ J
/-- registers: publics `X_t`, `Y_t`, relays, then owned -/
abbrev Rg (Q J O : Type*) := (Q ⊕ Q ⊕ J) ⊕ O

def eX (t : Q) : Wd Q J → K := Sum.elim (Pi.single t 1) 0
def eY (t : Q) : Wd Q J → K := Sum.elim 0 (Sum.elim (Pi.single t 1) 0)
def eZ (j : J) : Wd Q J → K := Sum.elim 0 (Sum.elim 0 (Pi.single j 1))
/-- final value of `X_t`: `x_t + Σ_s M t s · y_s` -/
def finX (M : Matrix Q Q K) (t : Q) : Wd Q J → K := Sum.elim (Pi.single t 1) (Sum.elim (M t) 0)
/-- the `y`-part `Σ_s M t s · y_s` -/
def mY (M : Matrix Q Q K) (t : Q) : Wd Q J → K := Sum.elim 0 (Sum.elim (M t) 0)

def dotLin (q : ν → K) : (ν → K) →ₗ[K] K where
  toFun v := q ⬝ᵥ v
  map_add' a b := dotProduct_add _ _ _
  map_smul' a b := by simp [dotProduct_smul]

/-- `q^⊥` for the standard dot product -/
def perp (q : ν → K) : Submodule K (ν → K) := LinearMap.ker (dotLin q)

lemma mem_perp {q c : ν → K} : c ∈ perp q ↔ q ⬝ᵥ c = 0 := Iff.rfl

/-- Start state: `X_t : ⟨q_t⟩, x_t`; `Y_t : {0}, y_t`; relay `j : S_j, z_j`; owned: any chart, value 0. -/
def toyStart (q : Q → ν → K) (Sj : J → Submodule K (ν → K)) (A0 : O → Submodule K (ν → K)) :
    St K ν (Wd Q J) (Rg Q J O) where
  ch := Sum.elim (Sum.elim (fun t => Submodule.span K {q t}) (Sum.elim (fun _ => ⊥) Sj)) A0
  v := Sum.elim (Sum.elim eX (Sum.elim eY eZ)) (fun _ => 0)

/-- Final state: `X_t : V, x_t + M_t y`; `Y_t : q_t^⊥, y_t`; relay `j : F_j, z_j`; owned arbitrary. -/
def toyFinal (q : Q → ν → K) (M : Matrix Q Q K) (Fj : J → Submodule K (ν → K))
    (A1 : O → Submodule K (ν → K)) (V1 : O → Wd Q J → K) : St K ν (Wd Q J) (Rg Q J O) where
  ch := Sum.elim (Sum.elim (fun _ => ⊤) (Sum.elim (fun s => perp (q s)) Fj)) A1
  v := Sum.elim (Sum.elim (finX M) (Sum.elim eY eZ)) V1

/-- the public registers -/
def pubs (Q J O : Type*) [Fintype Q] [Fintype J] : Finset (Rg Q J O) :=
  Finset.univ.map Function.Embedding.inl

lemma mem_pubs {r : Rg Q J O} : r ∈ pubs Q J O ↔ ∃ a, r = Sum.inl a := by
  simp [pubs, eq_comm]

lemma mem_S0 {P : Finset ι} {s : St K ν ω ι} {r : ι} (hr : r ∈ P) {x : Matrix ν ω K}
    (hx : x ∈ pot (s.ch r) (s.v r)) : x ∈ S0 P s :=
  Submodule.mem_iSup_of_mem r (Submodule.mem_iSup_of_mem hr hx)

lemma mem_pot {C : Submodule K (ν → K)} {w : ω → K} {c : ν → K} (hc : c ∈ C) :
    outer w c ∈ pot C w := ⟨c, hc, rfl⟩

/-- projection onto the `x`-columns -/
def piX : Matrix ν (Wd Q J) K →ₗ[K] Matrix ν Q K where
  toFun m := Matrix.of fun i t => m i (Sum.inl t)
  map_add' a b := rfl
  map_smul' a b := rfl

lemma piX_apply (m : Matrix ν (Wd Q J) K) (i : ν) (t : Q) : piX m i t = m i (Sum.inl t) := rfl

/-- `ψ m = (q_s · (y_s-column of m))_s` -/
def psiY (q : Q → ν → K) : Matrix ν (Wd Q J) K →ₗ[K] (Q → K) where
  toFun m := fun s => ∑ i, q s i * m i (Sum.inr (Sum.inl s))
  map_add' a b := by funext s; simp [mul_add, Finset.sum_add_distrib]
  map_smul' a b := by funext s; simp [Finset.mul_sum, mul_left_comm]

/-- the injection of `Π_s q_s^⊥ × Π_j F_j` into the `y`- and relay-columns -/
def Phi (q : Q → ν → K) (Fj : J → Submodule K (ν → K)) :
    ((s : Q) → perp (q s)) × ((j : J) → Fj j) →ₗ[K] Matrix ν (Wd Q J) K :=
  LinearMap.coprod
    (∑ s, (outer (eY s)).comp ((perp (q s)).subtype.comp (LinearMap.proj s)))
    (∑ j, (outer (eZ j)).comp ((Fj j).subtype.comp (LinearMap.proj j)))

lemma Phi_inl (q : Q → ν → K) (Fj : J → Submodule K (ν → K)) (x) (i : ν) (t : Q) :
    Phi q Fj x i (Sum.inl t) = 0 := by
  simp [Phi, LinearMap.coprod_apply, LinearMap.sum_apply, Matrix.sum_apply, outer_apply,
    Matrix.vecMulVec, eY, eZ]

lemma Phi_y (q : Q → ν → K) (Fj : J → Submodule K (ν → K)) (x) (i : ν) (t : Q) :
    Phi q Fj x i (Sum.inr (Sum.inl t)) = (x.1 t : ν → K) i := by
  simp [Phi, LinearMap.coprod_apply, LinearMap.sum_apply, Matrix.sum_apply, outer_apply,
    Matrix.vecMulVec, eY, eZ, Pi.single_apply]

lemma Phi_z (q : Q → ν → K) (Fj : J → Submodule K (ν → K)) (x) (i : ν) (j : J) :
    Phi q Fj x i (Sum.inr (Sum.inr j)) = (x.2 j : ν → K) i := by
  simp [Phi, LinearMap.coprod_apply, LinearMap.sum_apply, Matrix.sum_apply, outer_apply,
    Matrix.vecMulVec, eY, eZ, Pi.single_apply]

lemma Phi_inj (q : Q → ν → K) (Fj : J → Submodule K (ν → K)) : Function.Injective (Phi q Fj) := by
  rintro ⟨c, f⟩ ⟨c', f'⟩ h
  refine Prod.ext (funext fun s => Subtype.ext (funext fun i => ?_))
    (funext fun j => Subtype.ext (funext fun i => ?_))
  · have := congrFun (congrFun h i) (Sum.inr (Sum.inl s))
    simpa [Phi_y] using this
  · have := congrFun (congrFun h i) (Sum.inr (Sum.inr j))
    simpa [Phi_z] using this

lemma psi_Phi (q : Q → ν → K) (Fj : J → Submodule K (ν → K)) (x) : psiY q (Phi q Fj x) = 0 := by
  funext s
  have h : q s ⬝ᵥ (x.1 s : ν → K) = 0 := (mem_perp).1 (x.1 s).2
  simp only [psiY, LinearMap.coe_mk, AddHom.coe_mk, Phi_y, Pi.zero_apply]
  exact h

lemma piX_Phi (q : Q → ν → K) (Fj : J → Submodule K (ν → K)) (x) : piX (Phi q Fj x) = 0 := by
  ext i t; exact Phi_inl q Fj x i t


variable (q : Q → ν → K) (M : Matrix Q Q K) (Sj Fj : J → Submodule K (ν → K))
  (A0 A1 : O → Submodule K (ν → K)) (V1 : O → Wd Q J → K)

/-- Hadamard product `Q ∘ M`, `Q_ts = q_t · q_s`. -/
def had : Matrix Q Q K := Matrix.of fun t s => (q t ⬝ᵥ q s) * M t s

/-- the span `S0 + T` of the toy -/
def toyA : Submodule K (Matrix ν (Wd Q J) K) :=
  S0 (pubs Q J O) (toyStart q Sj A0) ⊔ S0 (pubs Q J O) (toyFinal q M Fj A1 V1)

/-- **Toy lower bound.** `dim(S0 + T) ≥ |ν||Q| + Σ_s dim q_s^⊥ + Σ_j dim F_j + rank(Q∘M)`. -/
theorem toy_lower :
    Fintype.card ν * Fintype.card Q + (∑ s, finrank K (perp (q s))) + (∑ j, finrank K (Fj j)) + (had q M).rank
      ≤ finrank K (toyA q M Sj Fj A0 A1 V1) := by
  set A := toyA q M Sj Fj A0 A1 V1 with hA
  have hmemF : ∀ a : Q ⊕ Q ⊕ J, ∀ x, x ∈ pot ((toyFinal q M Fj A1 V1).ch (Sum.inl a))
      ((toyFinal q M Fj A1 V1).v (Sum.inl a)) → x ∈ A := fun a x hx =>
    Submodule.mem_sup_right (mem_S0 (mem_pubs.2 ⟨a, rfl⟩) hx)
  have hmemS : ∀ a : Q ⊕ Q ⊕ J, ∀ x, x ∈ pot ((toyStart q Sj A0).ch (Sum.inl a))
      ((toyStart q Sj A0).v (Sum.inl a)) → x ∈ A := fun a x hx =>
    Submodule.mem_sup_left (mem_S0 (mem_pubs.2 ⟨a, rfl⟩) hx)
  -- generators of A
  have hX : ∀ t v, outer (finX M t) v ∈ A := fun t v =>
    hmemF (Sum.inl t) _ (mem_pot (C := ⊤) Submodule.mem_top)
  have hX0 : ∀ t, outer (eX t) (q t) ∈ A := fun t =>
    hmemS (Sum.inl t) _ (mem_pot (Submodule.mem_span_singleton_self (q t)))
  have hY : ∀ s c, c ∈ perp (q s) → outer (eY s) c ∈ A := fun s c hc =>
    hmemF (Sum.inr (Sum.inl s)) _ (mem_pot hc)
  have hZ : ∀ j c, c ∈ Fj j → outer (eZ j) c ∈ A := fun j c hc =>
    hmemF (Sum.inr (Sum.inr j)) _ (mem_pot hc)
  -- K' = range Φ ⊔ Kc
  set Kb := LinearMap.range (Phi q Fj) with hKb
  set Kc : Submodule K (Matrix ν (Wd Q J) K) :=
    Submodule.span K (Set.range fun t => Matrix.vecMulVec (q t) (mY M t)) with hKc
  have hKcA : Kc ≤ A := by
    rw [hKc, Submodule.span_le]
    rintro _ ⟨t, rfl⟩
    have : Matrix.vecMulVec (q t) (mY (J := J) M t) =
        outer (finX (J := J) M t) (q t) - outer (eX (J := J) t) (q t) := by
      ext i w; rcases w with x | y | z <;> simp [outer_apply, Matrix.vecMulVec, finX, eX, mY, Pi.single_apply]
    show Matrix.vecMulVec (q t) (mY M t) ∈ A
    rw [this]; exact A.sub_mem (hX t (q t)) (hX0 t)
  have hKbA : Kb ≤ A := by
    rintro _ ⟨⟨c, f⟩, rfl⟩
    have : Phi q Fj (c, f) = ∑ s, outer (eY s) (c s : ν → K) + ∑ j, outer (eZ j) (f j : ν → K) := by
      simp [Phi, LinearMap.coprod_apply, LinearMap.sum_apply]
    rw [this]
    exact A.add_mem (A.sum_mem fun s _ => hY s _ (c s).2) (A.sum_mem fun j _ => hZ j _ (f j).2)
  obtain ⟨K', hK'⟩ : ∃ K' : Submodule K (Matrix ν (Wd Q J) K), K' = Kb ⊔ Kc := ⟨_, rfl⟩
  have hKb' : Kb ≤ K' := hK' ▸ le_sup_left
  have hKc' : Kc ≤ K' := hK' ▸ le_sup_right
  have hK'A : K' ≤ A := hK' ▸ sup_le hKbA hKcA
  -- Step 1: A.map piX = ⊤
  have hpi : A.map piX = ⊤ := by
    rw [eq_top_iff]; intro m _
    have hm : m = ∑ t : Q, piX (outer (finX (J := J) M t) (fun i => m i t)) := by
      ext i t'
      simp [Matrix.sum_apply, piX_apply, outer_apply, Matrix.vecMulVec, finX, Pi.single_apply]
    rw [hm]
    exact Submodule.sum_mem _ fun t _ => ⟨outer (finX (J := J) M t) (fun i => m i t), hX t _, rfl⟩
  have hker : K' ≤ LinearMap.ker piX := by
    rw [hK']
    refine sup_le ?_ ?_
    · rintro _ ⟨x, rfl⟩; exact piX_Phi q Fj x
    · rw [hKc, Submodule.span_le]
      rintro _ ⟨t, rfl⟩
      show piX _ = 0
      ext i t'
      show q t i * mY (J := J) M t (Sum.inl t') = 0
      simp [mY]
  have hmapbot : K'.map piX = ⊥ := eq_bot_iff.2 (Submodule.map_le_iff_le_comap.2 hker)
  have d1 := map_dim_le piX hK'A
  rw [hpi, hmapbot, finrank_top, Module.finrank_matrix, finrank_bot, Module.finrank_self, mul_one] at d1
  -- Step 2
  have hker2 : Kb ≤ LinearMap.ker (psiY q) := by
    rintro _ ⟨x, rfl⟩; exact psi_Phi q Fj x
  have hmapbot2 : Kb.map (psiY q) = ⊥ := eq_bot_iff.2 (Submodule.map_le_iff_le_comap.2 hker2)
  have d2 := map_dim_le (psiY q) hKb'
  rw [hmapbot2, finrank_bot] at d2
  have hrows : Submodule.span K (Set.range (had q M).row) ≤ K'.map (psiY q) := by
    rw [Submodule.span_le]
    rintro _ ⟨t, rfl⟩
    refine ⟨Matrix.vecMulVec (q t) (mY M t),
      hKc' (Submodule.subset_span ⟨t, rfl⟩), ?_⟩
    funext s
    simp only [psiY, LinearMap.coe_mk, AddHom.coe_mk, Matrix.row, had, Matrix.of_apply]
    simp only [Matrix.vecMulVec, Matrix.of_apply, mY, Sum.elim_inr, Sum.elim_inl, dotProduct]
    rw [Finset.sum_mul]
    exact Finset.sum_congr rfl fun i _ => by ring
  have d3 := Submodule.finrank_mono hrows
  rw [← Matrix.rank_eq_finrank_span_row] at d3
  have d4 : finrank K Kb = (∑ s, finrank K (perp (q s))) + ∑ j, finrank K (Fj j) := by
    rw [hKb, LinearMap.finrank_range_of_inj (Phi_inj q Fj), Module.finrank_prod,
      Module.finrank_pi_fintype, Module.finrank_pi_fintype]
  omega


/-- **ITEM 2 (toy form).** Every run from the toy start to the toy final (any relays `J`, any
owned registers `O`, any charts/values for the owned ones at the end) has owned climb
`R ≥ rank (Q∘M)`. -/
theorem toy_rank_le {S : Submodule K (Matrix ν (Wd Q J) K)} {c p : ℕ}
    (h : Run (pubs Q J O) (toyStart q Sj A0) (toyFinal q M Fj A1 V1) S c p) :
    (had q M).rank ≤ c := by
  have h0 : ∀ r, r ∉ pubs Q J O → (toyStart q Sj A0).v r = 0 := by
    intro r hr
    rcases r with a | o
    · exact absurd (mem_pubs.2 ⟨a, rfl⟩) hr
    · rfl
  have h1 := headline' h0 h
  have h2 := toy_lower q M Sj Fj A0 A1 V1
  have h3 : ∑ r ∈ pubs Q J O, finrank K ((toyFinal q M Fj A1 V1).ch r) =
      Fintype.card Q * Fintype.card ν + (∑ s, finrank K (perp (q s))) + ∑ j, finrank K (Fj j) := by
    rw [pubs, Finset.sum_map]
    change ∑ a : Wd Q J, finrank K ((toyFinal q M Fj A1 V1).ch (Sum.inl a)) = _
    have hfin : finrank K (⊤ : Submodule K (ν → K)) = Fintype.card ν := by
      rw [finrank_top, Module.finrank_fintype_fun_eq_card]
    have hX : ∀ t : Q, finrank K ((toyFinal q M Fj A1 V1).ch (Sum.inl (Sum.inl t))) =
        Fintype.card ν := fun t => hfin
    have hY : ∀ s : Q, finrank K ((toyFinal q M Fj A1 V1).ch (Sum.inl (Sum.inr (Sum.inl s)))) =
        finrank K (perp (q s)) := fun _ => rfl
    have hZ : ∀ j : J, finrank K ((toyFinal q M Fj A1 V1).ch (Sum.inl (Sum.inr (Sum.inr j)))) =
        finrank K (Fj j) := fun _ => rfl
    rw [Fintype.sum_sum_type, Fintype.sum_sum_type]
    simp only [hX, hY, hZ, Finset.sum_const, Finset.card_univ, smul_eq_mul]
    ring
  unfold toyA at h2
  rw [h3] at h1
  rw [mul_comm (Fintype.card ν)] at h2
  omega

/-- **ITEM 4 (ring-valued ADD scalars).** If the registers carry values over a ring `Λ` with a
ring map `φ : Λ → K` (e.g. `Λ = ℤ_[2]`, `K = 𝔽₂`), and the run reduces to the toy start/final
under `φ`, then `R ≥ rank_K (Q ∘ φ(M))`. -/
theorem toy_rank_le_reduced {Λ : Type*} [CommRing Λ] (φ : Λ →+* K) (M' : Matrix Q Q Λ)
    {s0 s : StR K ν (Wd Q J) (Rg Q J O) Λ} {c : ℕ} {p : ℕ}
    (hs0 : red φ s0 = toyStart q Sj A0) (hs : red φ s = toyFinal q (M'.map φ) Fj A1 V1)
    (h : RunR (pubs Q J O) s0 s c p) : (had q (M'.map φ)).rank ≤ c := by
  obtain ⟨S, hS⟩ := red_run φ h
  rw [hs0, hs] at hS
  exact toy_rank_le q (M'.map φ) Sj Fj A0 A1 V1 hS

/-- The 2-adic instance: ADD scalars in `ℤ_[2]`, charts over `𝔽₂`. -/
theorem toy_rank_le_padic2 {ν Q J O : Type*} [Fintype ν] [Fintype Q] [Fintype J] [Fintype O]
    [DecidableEq Q] [DecidableEq J] [DecidableEq O]
    (q : Q → ν → ZMod 2) (M' : Matrix Q Q ℤ_[2]) (Sj Fj : J → Submodule (ZMod 2) (ν → ZMod 2))
    (A0 A1 : O → Submodule (ZMod 2) (ν → ZMod 2)) (V1 : O → Wd Q J → ZMod 2)
    {s0 s : StR (ZMod 2) ν (Wd Q J) (Rg Q J O) ℤ_[2]} {c p : ℕ}
    (hs0 : red PadicInt.toZMod s0 = toyStart q Sj A0)
    (hs : red PadicInt.toZMod s = toyFinal q (M'.map PadicInt.toZMod) Fj A1 V1)
    (h : RunR (pubs Q J O) s0 s c p) :
    (had q (M'.map PadicInt.toZMod)).rank ≤ c :=
  haveI : Fact (Nat.Prime 2) := ⟨Nat.prime_two⟩
  toy_rank_le_reduced q Sj Fj A0 A1 V1 PadicInt.toZMod M' hs0 hs h


end toy

/-! ## Non-vacuity: the toy `{1,2,7}` witness (n = 3 over 𝔽₂, M = I, no relays), `R = 3 = rank`. -/
section inst
open Function

lemma St.ext' {K ν ω ι : Type*} [Field K] (a b : St K ν ω ι) (h1 : a.ch = b.ch) (h2 : a.v = b.v) :
    a = b := by
  cases a; cases b; simp_all

lemma Run.step_to {K ν ω ι : Type*} [Field K] [Fintype ν] [Fintype ω] [DecidableEq ι]
    {P : Finset ι} {s0 s s' : St K ν ω ι} {S : Submodule K (Matrix ν ω K)} {c p dc dp : ℕ}
    (h : Run P s0 s S c p) (hm : Mv P s s' dc dp) :
    ∃ S', Run P s0 s' S' (c + dc) (p + dp) := ⟨_, h.step hm⟩

lemma Run.cast {K ν ω ι : Type*} [Field K] [Fintype ν] [Fintype ω] [DecidableEq ι]
    {P : Finset ι} {s0 s s' : St K ν ω ι} {S : Submodule K (Matrix ν ω K)} {c p : ℕ}
    (e : s = s') (h : Run P s0 s S c p) : Run P s0 s' S c p := e ▸ h

/-- the odd ports `1, 2, 7` as bit-vectors in `𝔽₂³` -/
def q127 : Fin 3 → Fin 3 → ZMod 2 := ![![1, 0, 0], ![0, 1, 0], ![1, 1, 1]]
abbrev Sj0 : Fin 0 → Submodule (ZMod 2) (Fin 3 → ZMod 2) := fun j => j.elim0
abbrev Mid : Matrix (Fin 3) (Fin 3) (ZMod 2) := 1
abbrev A00 : Unit → Submodule (ZMod 2) (Fin 3 → ZMod 2) := fun _ => ⊥
abbrev V00 : Unit → Wd (Fin 3) (Fin 0) → ZMod 2 := fun _ => 0

lemma q127_ne (t : Fin 3) : q127 t ≠ 0 := by revert t; decide

theorem had_q127 : had q127 Mid = 1 := by
  ext t s
  fin_cases t <;> fin_cases s <;> simp [had, q127, dotProduct, Fin.sum_univ_three] <;> decide

theorem rank_q127 : (had q127 Mid).rank = 3 := by
  rw [had_q127, Matrix.rank_one]; simp


abbrev P3 : Finset (Rg (Fin 3) (Fin 0) Unit) := pubs (Fin 3) (Fin 0) Unit
abbrev St3 := St (ZMod 2) (Fin 3) (Wd (Fin 3) (Fin 0)) (Rg (Fin 3) (Fin 0) Unit)
abbrev T0 : St3 := toyStart q127 Sj0 A00
def oR : Rg (Fin 3) (Fin 0) Unit := Sum.inr ()
def xR (t : Fin 3) : Rg (Fin 3) (Fin 0) Unit := Sum.inl (Sum.inl t)
def yR (t : Fin 3) : Rg (Fin 3) (Fin 0) Unit := Sum.inl (Sum.inr (Sum.inl t))

def Own (s : St3) : Prop := s.ch oR = ⊥ ∧ s.v oR = 0
def Todo (t : Fin 3) (s : St3) : Prop :=
  s.ch (yR t) = ⊥ ∧ s.v (yR t) = eY t ∧ s.ch (xR t) = Submodule.span (ZMod 2) {q127 t} ∧
    s.v (xR t) = eX t
def Done (t : Fin 3) (s : St3) : Prop :=
  s.ch (yR t) = perp (q127 t) ∧ s.v (yR t) = eY t ∧ s.ch (xR t) = ⊤ ∧ s.v (xR t) = finX Mid t

lemma ne_oy (t : Fin 3) : oR ≠ yR t := by simp [oR, yR]
lemma ne_ox (t : Fin 3) : oR ≠ xR t := by simp [oR, xR]
lemma ne_xy (t t' : Fin 3) : xR t ≠ yR t' := by simp [xR, yR]
lemma ne_xx {t t' : Fin 3} (h : t' ≠ t) : xR t' ≠ xR t := by simp [xR, h]
lemma ne_yy {t t' : Fin 3} (h : t' ≠ t) : yR t' ≠ yR t := by simp [yR, h]

lemma eX_add_eY (t : Fin 3) : eX (J := Fin 0) t + eY t = finX Mid t := by
  funext w
  rcases w with x | y | z
  · simp [eX, eY, finX, Pi.single_apply]
  · simp [eX, eY, finX, Pi.single_apply, Matrix.one_apply, eq_comm]
  · exact z.elim0

lemma Own0 : Own T0 := ⟨rfl, rfl⟩
lemma Todo0 (t : Fin 3) : Todo t T0 :=
  ⟨rfl, rfl, rfl, rfl⟩

lemma port_step (t : Fin 3) {s : St3} {S : Submodule (ZMod 2) (Matrix (Fin 3) (Wd (Fin 3) (Fin 0)) (ZMod 2))}
    {c p : ℕ} (hrun : Run P3 T0 s S c p) (hown : Own s) (ht : Todo t s) :
    ∃ (s' : St3) (S' : Submodule (ZMod 2) (Matrix (Fin 3) (Wd (Fin 3) (Fin 0)) (ZMod 2))) (c' p' : ℕ),
      Run P3 T0 s' S' c' p' ∧ c' = c + 1 ∧ Own s' ∧ Done t s' ∧
      (∀ t', t' ≠ t → Todo t' s → Todo t' s') ∧ (∀ t', t' ≠ t → Done t' s → Done t' s') := by
  obtain ⟨ho1, ho2⟩ := hown
  obtain ⟨hy1, hy2, hx1, hx2⟩ := ht
  have hown' : oR ∉ P3 := by rw [mem_pubs]; simp [oR]
  have e1 : oR ≠ yR t := ne_oy t
  have e2 : yR t ≠ oR := (ne_oy t).symm
  have e3 : oR ≠ xR t := ne_ox t
  have e4 : xR t ≠ oR := (ne_ox t).symm
  have e5 : xR t ≠ yR t := ne_xy t t
  have e6 : yR t ≠ xR t := (ne_xy t t).symm
  obtain ⟨_, r1⟩ := hrun.step_to (Mv.add oR (yR t) 1 (by rw [ho1, hy1]))
  obtain ⟨_, r2⟩ := r1.step_to (Mv.upOwn oR (Submodule.span (ZMod 2) {q127 t}) hown'
    (by simp [ho1]))
  obtain ⟨_, r3⟩ := r2.step_to (Mv.add (xR t) oR 1 (by simp [ho1, hx1, update_apply, e1, e2, e3, e4, e5, e6]))
  obtain ⟨_, r4⟩ := r3.step_to (Mv.down oR ⊥ hown' bot_le)
  obtain ⟨_, r5⟩ := r4.step_to (Mv.init oR)
  obtain ⟨_, r6⟩ := r5.step_to (Mv.upPub (xR t) ⊤ (mem_pubs.2 ⟨_, rfl⟩) le_top)
  obtain ⟨_, r7⟩ := r6.step_to (Mv.upPub (yR t) (perp (q127 t)) (mem_pubs.2 ⟨_, rfl⟩)
    (by simp [hy1, update_apply, e1, e2, e3, e4, e5, e6]))
  refine ⟨_, _, _, _, r7, ?_, ?_, ?_, ?_, ?_⟩
  · simp [finrank_span_singleton (q127_ne t), update_apply, e1, e2, e3, e4, e5, e6]
    rw [ho1]; simp
  · refine ⟨?_, ?_⟩ <;> simp [update_apply, e1, e2, e3, e4, e5, e6]
  · refine ⟨?_, ?_, ?_, ?_⟩
    · simp [update_apply, e1, e2, e3, e4, e5, e6]
    · simp [update_apply, e1, e2, e3, e4, e5, e6, hy2]
    · simp [update_apply, e1, e2, e3, e4, e5, e6]
    · simp [update_apply, e1, e2, e3, e4, e5, e6, hy2, hx2, ho2, eX_add_eY]
  · intro t' ht' ⟨a, b, c, d⟩
    have f1 : yR t' ≠ yR t := ne_yy ht'
    have f2 : yR t' ≠ xR t := (ne_xy t t').symm
    have f3 : yR t' ≠ oR := (ne_oy t').symm
    have f4 : xR t' ≠ oR := (ne_ox t').symm
    have f5 : xR t' ≠ yR t := ne_xy t' t
    have f6 : xR t' ≠ xR t := ne_xx ht'
    refine ⟨?_, ?_, ?_, ?_⟩ <;> simp [update_apply, f1, f2, f3, f4, f5, f6, a, b, c, d]
  · intro t' ht' ⟨a, b, c, d⟩
    have f1 : yR t' ≠ yR t := ne_yy ht'
    have f2 : yR t' ≠ xR t := (ne_xy t t').symm
    have f3 : yR t' ≠ oR := (ne_oy t').symm
    have f4 : xR t' ≠ oR := (ne_ox t').symm
    have f5 : xR t' ≠ yR t := ne_xy t' t
    have f6 : xR t' ≠ xR t := ne_xx ht'
    refine ⟨?_, ?_, ?_, ?_⟩ <;> simp [update_apply, f1, f2, f3, f4, f5, f6, a, b, c, d]

theorem inst_run : ∃ S p, Run P3 T0 (toyFinal q127 Mid Sj0 A00 V00) S 3 p := by
  have r0 : Run P3 T0 T0 _ 0 0 := Run.refl
  obtain ⟨s1, S1, c1, p1, r1, hc1, hO1, hD1, hT1, hP1⟩ := port_step 0 r0 Own0 (Todo0 0)
  obtain ⟨s2, S2, c2, p2, r2, hc2, hO2, hD2, hT2, hP2⟩ :=
    port_step 1 r1 hO1 (hT1 1 (by decide) (Todo0 1))
  obtain ⟨s3, S3, c3, p3, r3, hc3, hO3, hD3, hT3, hP3⟩ :=
    port_step 2 r2 hO2 (hT2 2 (by decide) (hT1 2 (by decide) (Todo0 2)))
  have hD : ∀ x, Done x s3 := by
    intro x
    fin_cases x
    · exact hP3 0 (by decide) (hP2 0 (by decide) hD1)
    · exact hP3 1 (by decide) hD2
    · exact hD3
  have e : s3 = toyFinal q127 Mid Sj0 A00 V00 := by
    refine St.ext' _ _ (funext fun r => ?_) (funext fun r => ?_)
    · rcases r with (x | y | z) | u
      · exact (hD x).2.2.1
      · exact (hD y).1
      · exact z.elim0
      · exact hO3.1
    · rcases r with (x | y | z) | u
      · exact (hD x).2.2.2
      · exact (hD y).2.1
      · exact z.elim0
      · exact hO3.2
  have hc : c3 = 3 := by omega
  exact ⟨_, _, hc ▸ Run.cast e r3⟩

/-- the toy `{1,2,7}` witness: lower bound `rank = 3` and a run with `R = 3`: tight. -/
theorem inst_tight : (had q127 Mid).rank = 3 ∧ ∃ S p, Run P3 T0 (toyFinal q127 Mid Sj0 A00 V00) S 3 p :=
  ⟨rank_q127, inst_run⟩

theorem inst_bound {S : Submodule (ZMod 2) (Matrix (Fin 3) (Wd (Fin 3) (Fin 0)) (ZMod 2))} {c p : ℕ}
    (h : Run P3 T0 (toyFinal q127 Mid Sj0 A00 V00) S c p) : 3 ≤ c := by
  have := toy_rank_le q127 Mid Sj0 Sj0 A00 A00 V00 h
  rwa [rank_q127] at this

end inst
end model
end TensorPot

open TensorPot in
#print axioms TensorPot.step_bound
open TensorPot in
#print axioms TensorPot.headline
open TensorPot in
#print axioms TensorPot.headline'
open TensorPot in
#print axioms TensorPot.headline_padic2
open TensorPot in
#print axioms TensorPot.toy_lower
open TensorPot in
#print axioms TensorPot.toy_rank_le
open TensorPot in
#print axioms TensorPot.toy_rank_le_padic2
open TensorPot in
#print axioms TensorPot.inst_tight
open TensorPot in
#print axioms TensorPot.inst_bound
