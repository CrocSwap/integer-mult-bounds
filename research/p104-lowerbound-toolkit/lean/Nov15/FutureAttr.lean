import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.Algebra.Field.ZMod
import Mathlib.Tactic.LinearCombination
import Nov15.PriceLemma

/-!
FUTUREATTR (lane LEANUPHASE).  Kernel-only: no sorry / native_decide / new axioms.

Formalises UPHASE's future-attribution (FA) cancellation law.
Run model: charts are F2-subspaces of F2^n, values are K-vectors indexed by symbols `ω`
(K any field, e.g. ℚ).  Publics only ascend, owned registers start at value 0, ADD needs
`chart d ≤ chart e` and `d ≠ e`.  `ARun` is a run *together with* its attribution
bookkeeping W (reference weights / lifetime output weights), per-lifetime intake meet A,
output join B, lifetime cost; the premises "GTD" (no intake after an output) and
"cold intake" (class F) are constructor arguments of `ARun`.
Results:
 1. `Inv` (exact linear attribution identity, chart invariant) for every `ARun`.
 2. Lifetime cost lemma and price lemma; `attribution_decoder`: a decoder with total price ≤ R.
 3. `mass_le_R`, `R_ge_of_wall`.
-/

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace FutureAttr
open Module Submodule Finset Function PriceLemma

abbrev Chart (n : ℕ) := Submodule (ZMod 2) (Fin n → ZMod 2)

/-! ## dimension lemmas -/
section dims
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V] [FiniteDimensional K V]

lemma fin_le_of_eq {V : Type*} [AddCommGroup V] [Module K V] (N N' M M' : Submodule K V) (lc : ℕ)
    (h1 : N = N') (h2 : M = M') (h : finrank K N' ≤ finrank K M' + lc) :
    finrank K N ≤ finrank K M + lc := by
  subst h1 h2; exact h

lemma sum_ite_zero_add {ι : Type*} [DecidableEq ι] (S : Finset ι) (f : ι → ℕ) (r : ι) (hr : r ∈ S) :
    ∑ x ∈ S, (if x = r then 0 else f x) + f r = ∑ x ∈ S, f x := by
  rw [← Finset.add_sum_erase S f hr, add_comm]
  congr 1
  rw [← Finset.sum_erase S (a := r) (f := fun x => if x = r then 0 else f x) (by simp)]
  apply Finset.sum_congr rfl
  intro x hx
  simp [Finset.ne_of_mem_erase hx]

lemma fin_le_of_eq' {V : Type*} [AddCommGroup V] [Module K V] (N N' M M' : Submodule K V) (lc lc' : ℕ)
    (h1 : N = N') (h2 : M = M') (h3 : lc = lc') (h : finrank K N' ≤ finrank K M' + lc') :
    finrank K N ≤ finrank K M + lc := by
  subst h1 h2 h3; exact h

lemma asc (S Z D : Submodule K V) (hZS : Z ≤ S) (hZD : Z ≤ D) :
    finrank K (S ⊔ D : Submodule K V) + finrank K Z ≤ finrank K S + finrank K D := by
  have h1 := Submodule.finrank_sup_add_finrank_inf_eq S D
  have h2 : finrank K Z ≤ finrank K (S ⊓ D : Submodule K V) :=
    Submodule.finrank_mono (le_inf hZS hZD)
  omega

/-- lifetime potential: an ascent `Z ≤ D` costs at least the growth of `dim (A ⊔ B ⊔ Z)`. -/
lemma life_up (A B Z D : Submodule K V) (h : Z ≤ D) :
    finrank K (A ⊔ B ⊔ D : Submodule K V) + finrank K Z ≤
      finrank K (A ⊔ B ⊔ Z : Submodule K V) + finrank K D := by
  have := asc (A ⊔ B ⊔ Z) Z D le_sup_right h
  have e : (A ⊔ B ⊔ Z) ⊔ D = A ⊔ B ⊔ D := by
    rw [sup_assoc, sup_eq_right.2 h]
  rwa [e] at this

/-- intake: meet with the current chart, no output yet (`B = ⊥`). -/
lemma life_intake (A Z : Submodule K V) (lc : ℕ)
    (h : finrank K (A ⊔ ⊥ ⊔ Z : Submodule K V) ≤ finrank K A + lc) :
    finrank K (A ⊓ Z ⊔ ⊥ ⊔ Z : Submodule K V) ≤ finrank K (A ⊓ Z : Submodule K V) + lc := by
  have e1 : (A ⊓ Z ⊔ ⊥ ⊔ Z : Submodule K V) = Z := by
    simp
  have e2 : (A ⊔ ⊥ ⊔ Z : Submodule K V) = A ⊔ Z := by simp
  rw [e1]; rw [e2] at h
  have := Submodule.finrank_sup_add_finrank_inf_eq A Z
  omega

/-- output: `B ⊔ Z`; the potential `A ⊔ B ⊔ Z` does not change. -/
lemma life_output (A B Z : Submodule K V) :
    (A ⊔ (B ⊔ Z) ⊔ Z : Submodule K V) = A ⊔ B ⊔ Z := by
  simp only [sup_assoc, sup_idem]

end dims

/-! ## Run model with attribution bookkeeping -/
section Model
variable {K : Type*} [Field K] {τ ι ω : Type*} {n : ℕ}

/-- register state: charts and values -/
structure St (K : Type*) (n : ℕ) (ι ω : Type*) where
  ch : ι → Chart n
  v : ι → ω → K

/-- a closed (or final) owned lifetime: output weights `w`, content `val`,
intake meet `A`, output join `B`, lifetime cost `lc`. -/
structure Row (K : Type*) (τ ω : Type*) (n : ℕ) where
  w : τ → K
  val : ω → K
  A : Chart n
  B : Chart n
  lc : ℕ

/-- bookkeeping: `W r t` = weight with which register `r`'s content is referenced for target `t`
(for owned `r`: the lifetime's output weight); per-register lifetime data. -/
structure Bk (K : Type*) (τ ω ι : Type*) (n : ℕ) where
  W : ι → τ → K
  A : ι → Chart n
  B : ι → Chart n
  dep : ι → Bool
  lc : ι → ℕ
  closed : List (Row K τ ω n)

def Bk.init : Bk K τ ω ι n :=
  ⟨fun _ _ => 0, fun _ => ⊤, fun _ => ⊥, fun _ => false, fun _ => 0, []⟩

variable [Fintype τ] [DecidableEq ι]

/-- effective content: `c|_y − Σ_u c[x_u]·Fy u` (`Fy u` = y-part of the final of `X_u`). -/
def eff (xs ys : τ → ω) (Fy : τ → τ → K) (c : ω → K) : τ → K :=
  fun s => c (ys s) - ∑ u, c (xs u) * Fy u s

/-- indicator of "register `d` is the target register `X_t`". -/
def tv (X : τ → ι) (d : ι) (t : τ) : K := if d = X t then 1 else 0

/-- Runs.  `P` = publics, `X t` = target register of port `t`, `q t` = port label,
`xs/ys` = symbol of x_u/y_s, `Fy` = y-part of the finals of the X registers.
ADD `d += l·e` (needs `d ≠ e`, `chart d ≤ chart e`):
 * attribution `ω_t = l (tv d t − W d t)` goes to the source `e`;
 * intake into owned `d` must be GTD (`dep d = false`) and cold at the intake chart;
 * a read of owned `e` into a public `d` is an output (sets `B e`, `dep e`).
INIT of an owned register closes its lifetime into `closed`. -/
inductive ARun (P : Finset ι) (X : τ → ι) (xs ys : τ → ω) (Fy : τ → τ → K)
    (q : τ → Fin n → ZMod 2) (s0 : St K n ι ω) :
    St K n ι ω → Bk K τ ω ι n → ℕ → Prop
  | refl : ARun P X xs ys Fy q s0 s0 Bk.init 0
  | add {s bk cost} (d e : ι) (l : K) (hne : d ≠ e) (hch : s.ch d ≤ s.ch e)
      (hgtd : d ∉ P → bk.dep d = false)
      (hcold : d ∉ P → ∀ u, l * eff xs ys Fy (s.v e) u ≠ 0 → ∀ a ∈ s.ch d, a ⬝ᵥ q u = 0) :
      ARun P X xs ys Fy q s0 s bk cost →
      ARun P X xs ys Fy q s0
        { s with v := fun r j => s.v r j + if r = d then l * s.v e j else 0 }
        { bk with
          W := fun r t => bk.W r t + if r = e then l * (tv X d t - bk.W d t) else 0
          A := fun r => if r = d ∧ d ∉ P then bk.A d ⊓ s.ch d else bk.A r
          B := fun r => if r = e ∧ d ∈ P ∧ e ∉ P then bk.B e ⊔ s.ch e else bk.B r
          dep := fun r => if r = e ∧ d ∈ P ∧ e ∉ P then true else bk.dep r } cost
  | init {s bk cost} (r : ι) (hr : r ∉ P) :
      ARun P X xs ys Fy q s0 s bk cost →
      ARun P X xs ys Fy q s0
        { s with v := fun r' j => if r' = r then 0 else s.v r' j }
        { W := fun r' t => if r' = r then 0 else bk.W r' t
          A := fun r' => if r' = r then ⊤ else bk.A r'
          B := fun r' => if r' = r then ⊥ else bk.B r'
          dep := fun r' => if r' = r then false else bk.dep r'
          lc := fun r' => if r' = r then 0 else bk.lc r'
          closed := ⟨bk.W r, s.v r, bk.A r, bk.B r, bk.lc r⟩ :: bk.closed } cost
  | down {s bk cost} (r : ι) (D : Chart n) (hr : r ∉ P) (h : D ≤ s.ch r) :
      ARun P X xs ys Fy q s0 s bk cost →
      ARun P X xs ys Fy q s0 { s with ch := fun r' => if r' = r then D else s.ch r' } bk cost
  | upOwn {s bk cost} (r : ι) (D : Chart n) (hr : r ∉ P) (h : s.ch r ≤ D) :
      ARun P X xs ys Fy q s0 s bk cost →
      ARun P X xs ys Fy q s0 { s with ch := fun r' => if r' = r then D else s.ch r' }
        { bk with lc := fun r' =>
            if r' = r then bk.lc r + (finrank (ZMod 2) D - finrank (ZMod 2) (s.ch r)) else bk.lc r' }
        (cost + (finrank (ZMod 2) D - finrank (ZMod 2) (s.ch r)))
  | upPub {s bk cost} (r : ι) (D : Chart n) (hr : r ∈ P) (h : s.ch r ≤ D) :
      ARun P X xs ys Fy q s0 s bk cost →
      ARun P X xs ys Fy q s0 { s with ch := fun r' => if r' = r then D else s.ch r' } bk cost

/-- a lifetime row is valid: weights on labels of `B`, effective content on labels of `A^⊥`,
price bound `dim (A ⊔ B) ≤ dim A + lc`. -/
def Row.ok (xs ys : τ → ω) (Fy : τ → τ → K) (q : τ → Fin n → ZMod 2) (ρ : Row K τ ω n) : Prop :=
  (∀ t, ρ.w t ≠ 0 → q t ∈ ρ.B) ∧
  (∀ u, eff xs ys Fy ρ.val u ≠ 0 → ∀ a ∈ ρ.A, a ⬝ᵥ q u = 0) ∧
  finrank (ZMod 2) (ρ.A ⊔ ρ.B : Chart n) ≤ finrank (ZMod 2) ρ.A + ρ.lc

end Model

/-! ## The invariant -/
section Inv
variable {K : Type*} [Field K] {τ ι ω : Type*} {n : ℕ} [Fintype τ] [DecidableEq ι] [Fintype ι]
variable (P : Finset ι) (X : τ → ι) (xs ys : τ → ω) (Fy : τ → τ → K)
  (q : τ → Fin n → ZMod 2) (s0 : St K n ι ω)

lemma eff_add (f g : ω → K) (l : K) (u : τ) :
    eff xs ys Fy (fun j => f j + l * g j) u = eff xs ys Fy f u + l * eff xs ys Fy g u := by
  simp only [eff, mul_sub, add_mul, Finset.sum_add_distrib, Finset.mul_sum]
  have : ∀ x : τ, l * (g (xs x) * Fy x u) = l * g (xs x) * Fy x u := fun x => by ring
  simp only [this]
  ring

lemma eff_zero (u : τ) : eff xs ys Fy (0 : ω → K) u = 0 := by simp [eff]

/-- the invariant of an attributed run -/
structure Inv (s : St K n ι ω) (bk : Bk K τ ω ι n) (cost : ℕ) : Prop where
  i1 : ∀ t j, s.v (X t) j - s0.v (X t) j =
    ∑ r, bk.W r t * s.v r j + (bk.closed.map fun ρ => ρ.w t * ρ.val j).sum
  i2 : ∀ r ∈ P, ∀ t, bk.W r t ≠ 0 → q t ∈ s.ch r
  i2' : ∀ t, q t ∈ s.ch (X t)
  i3 : ∀ r ∉ P, bk.dep r = false → bk.W r = 0
  i3b : ∀ r ∉ P, bk.dep r = false → bk.B r = ⊥
  i4 : ∀ r ∉ P, ∀ t, bk.W r t ≠ 0 → q t ∈ bk.B r
  i5 : ∀ r ∉ P, ∀ u, eff xs ys Fy (s.v r) u ≠ 0 → ∀ a ∈ bk.A r, a ⬝ᵥ q u = 0
  i6 : ∀ r ∉ P, finrank (ZMod 2) (bk.A r ⊔ bk.B r ⊔ s.ch r : Chart n) ≤
      finrank (ZMod 2) (bk.A r) + bk.lc r
  i7 : ∀ ρ ∈ bk.closed, ρ.ok xs ys Fy q
  i8 : cost = ∑ r ∈ univ.filter (· ∉ P), bk.lc r + (bk.closed.map fun ρ => ρ.lc).sum

theorem Inv.refl (hq : ∀ t, q t ∈ s0.ch (X t)) (h0 : ∀ r ∉ P, s0.v r = 0) :
    Inv P X xs ys Fy q s0 s0 Bk.init 0 where
  i1 := by intro t j; simp [Bk.init]
  i2 := by intro r _ t h; simp [Bk.init] at h
  i2' := hq
  i3 := by intro r _ _; rfl
  i3b := by intro r _ _; rfl
  i4 := by intro r _ t h; simp [Bk.init] at h
  i5 := by
    intro r hr u h; rw [h0 r hr, eff_zero] at h; exact absurd rfl h
  i6 := by
    intro r _
    have : (⊤ ⊔ ⊥ ⊔ s0.ch r : Chart n) = ⊤ := by simp
    show finrank (ZMod 2) ↥((⊤ : Chart n) ⊔ ⊥ ⊔ s0.ch r) ≤ finrank (ZMod 2) ↥(⊤ : Chart n) + 0
    rw [this]; omega
  i7 := by intro ρ h; simp [Bk.init] at h
  i8 := by simp [Bk.init]

theorem Inv.add (hXP : ∀ t, X t ∈ P) {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (h : Inv P X xs ys Fy q s0 s bk cost)
    (d e : ι) (l : K) (hne : d ≠ e) (hch : s.ch d ≤ s.ch e)
    (hgtd : d ∉ P → bk.dep d = false)
    (hcold : d ∉ P → ∀ u, l * eff xs ys Fy (s.v e) u ≠ 0 → ∀ a ∈ s.ch d, a ⬝ᵥ q u = 0) :
    Inv P X xs ys Fy q s0
        { s with v := fun r j => s.v r j + if r = d then l * s.v e j else 0 }
        { bk with
          W := fun r t => bk.W r t + if r = e then l * (tv X d t - bk.W d t) else 0
          A := fun r => if r = d ∧ d ∉ P then bk.A d ⊓ s.ch d else bk.A r
          B := fun r => if r = e ∧ d ∈ P ∧ e ∉ P then bk.B e ⊔ s.ch e else bk.B r
          dep := fun r => if r = e ∧ d ∈ P ∧ e ∉ P then true else bk.dep r } cost := by
  -- intake into an owned register carries no attribution
  have hω0 : d ∉ P → ∀ t, tv X d t - bk.W d t = 0 := by
    intro hd t
    have h1 : tv (K := K) X d t = 0 := by
      simp only [tv]; rw [if_neg]; intro hh; exact hd (hh ▸ hXP t)
    have h2 : bk.W d t = 0 := congrFun (h.i3 d hd (hgtd hd)) t
    rw [h1, h2]; ring
  -- attributed weights live on charts containing the port label
  have hωq : d ∈ P → ∀ t, l * (tv X d t - bk.W d t) ≠ 0 → q t ∈ s.ch e := by
    intro hd t hne0
    have hne1 : tv X d t - bk.W d t ≠ 0 := right_ne_zero_of_mul hne0
    by_cases hdt : d = X t
    · subst hdt; exact hch (h.i2' t)
    · have h1 : tv (K := K) X d t = 0 := by simp [tv, hdt]
      rw [h1] at hne1
      have : bk.W d t ≠ 0 := fun hh => hne1 (by rw [hh]; ring)
      exact hch (h.i2 d hd t this)
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · -- i1: exact linear attribution identity
    intro t j
    have hsum : ∑ r, (bk.W r t + if r = e then l * (tv X d t - bk.W d t) else 0) *
          (s.v r j + if r = d then l * s.v e j else 0) =
        ∑ r, bk.W r t * s.v r j + l * (tv X d t - bk.W d t) * s.v e j
          + bk.W d t * (l * s.v e j) := by
      simp only [add_mul, mul_add, Finset.sum_add_distrib]
      have e1 : ∑ r, (if r = e then l * (tv X d t - bk.W d t) else 0) * s.v r j =
          l * (tv X d t - bk.W d t) * s.v e j := by simp [ite_mul]
      have e2 : ∑ r, bk.W r t * (if r = d then l * s.v e j else 0) =
          bk.W d t * (l * s.v e j) := by simp [mul_ite]
      have e3 : ∑ r, (if r = e then l * (tv X d t - bk.W d t) else 0) *
          (if r = d then l * s.v e j else 0) = 0 := by
        apply Finset.sum_eq_zero; intro r _
        by_cases hr : r = e
        · have : r ≠ d := fun h' => hne (h'.symm.trans hr)
          simp [this]
        · simp [hr]
      rw [e1, e2, e3]; ring
    dsimp only
    rw [hsum]
    have h1 := h.i1 t j
    by_cases hXt : X t = d
    · have : tv (K := K) X d t = 1 := by simp [tv, hXt.symm]
      simp only [hXt, if_true, this]
      rw [hXt] at h1
      linear_combination h1
    · have : tv (K := K) X d t = 0 := by
        simp only [tv]; rw [if_neg]; intro hh; exact hXt hh.symm
      simp only [hXt, if_false, this]
      linear_combination h1
  · -- i2
    intro r hr t hW
    dsimp only at hW ⊢
    by_cases hre : r = e
    · subst hre
      simp only [if_true] at hW
      by_cases hw0 : bk.W r t = 0
      · rw [hw0, zero_add] at hW
        by_cases hdP : d ∈ P
        · exact hωq hdP t hW
        · exact absurd (by rw [hω0 hdP t, mul_zero]) hW
      · exact h.i2 r hr t hw0
    · simp only [hre, if_false, add_zero] at hW; exact h.i2 r hr t hW
  · exact h.i2'
  · -- i3
    intro r hr hdep
    dsimp only at hdep ⊢
    have hnc : ¬(r = e ∧ d ∈ P ∧ e ∉ P) := fun hc => by simp [hc] at hdep
    rw [if_neg hnc] at hdep
    funext t
    have hW := congrFun (h.i3 r hr hdep) t
    by_cases hre : r = e
    · subst hre
      have hdP : d ∉ P := fun hd => hnc ⟨rfl, hd, hr⟩
      simp [hω0 hdP t, hW]
    · simp [hre, hW]
  · -- i3b
    intro r hr hdep
    dsimp only at hdep ⊢
    have hnc : ¬(r = e ∧ d ∈ P ∧ e ∉ P) := fun hc => by simp [hc] at hdep
    rw [if_neg hnc] at hdep ⊢
    exact h.i3b r hr hdep
  · -- i4
    intro r hr t hW
    dsimp only at hW ⊢
    by_cases hc : r = e ∧ d ∈ P ∧ e ∉ P
    · rw [if_pos hc]
      obtain ⟨hr1, hdP, heP⟩ := hc
      subst hr1
      simp only [if_true] at hW
      by_cases hw0 : bk.W r t = 0
      · rw [hw0, zero_add] at hW
        exact Submodule.mem_sup_right (hωq hdP t hW)
      · exact Submodule.mem_sup_left (h.i4 r hr t hw0)
    · rw [if_neg hc]
      by_cases hre : r = e
      · subst hre
        have hdP : d ∉ P := fun hd => hc ⟨rfl, hd, hr⟩
        exact h.i4 r hr t (by simpa [hω0 hdP t] using hW)
      · exact h.i4 r hr t (by simpa [hre] using hW)
  · -- i5
    intro r hr u hef a ha
    dsimp only at hef ha
    by_cases hrd : r = d ∧ d ∉ P
    · rw [if_pos hrd] at ha
      obtain ⟨hr1, hdP⟩ := hrd
      subst hr1
      simp only [if_true] at hef
      rw [eff_add] at hef
      by_cases h1 : eff xs ys Fy (s.v r) u = 0
      · rw [h1, zero_add] at hef
        exact hcold hdP u hef a (Submodule.mem_inf.1 ha).2
      · exact h.i5 r hr u h1 a (Submodule.mem_inf.1 ha).1
    · rw [if_neg hrd] at ha
      have hv : (fun j => s.v r j + if r = d then l * s.v e j else 0) = s.v r := by
        funext j
        have : r ≠ d := fun hh => hrd ⟨hh, hh ▸ hr⟩
        simp [this]
      rw [hv] at hef
      exact h.i5 r hr u hef a ha
  · -- i6
    intro r hr
    dsimp only
    by_cases hrd : r = d ∧ d ∉ P
    · obtain ⟨hr1, hdP⟩ := hrd
      subst hr1
      have hBe : ¬ (r = e ∧ r ∈ P ∧ e ∉ P) := fun hc => hdP hc.2.1
      have hA : (if r = r ∧ r ∉ P then bk.A r ⊓ s.ch r else bk.A r) = bk.A r ⊓ s.ch r :=
        if_pos ⟨rfl, hdP⟩
      have hB := h.i3b r hr (hgtd hdP)
      have key := life_intake (bk.A r) (s.ch r) (bk.lc r) (by have := h.i6 r hr; rwa [hB] at this)
      refine fin_le_of_eq _ _ _ _ _ ?_ hA key
      rw [hA, if_neg hBe, hB]
    · by_cases hc : r = e ∧ d ∈ P ∧ e ∉ P
      · obtain ⟨hr1, hdP, heP⟩ := hc
        subst hr1
        refine fin_le_of_eq _ _ _ _ _ ?_ (if_neg hrd) (h.i6 r hr)
        rw [if_neg hrd, if_pos (And.intro rfl (And.intro hdP heP)), life_output]
      · refine fin_le_of_eq _ _ _ _ _ ?_ (if_neg hrd) (h.i6 r hr)
        rw [if_neg hrd, if_neg hc]
  · exact h.i7
  · exact h.i8


theorem Inv.init' (hXP : ∀ t, X t ∈ P) {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (h : Inv P X xs ys Fy q s0 s bk cost) (r : ι) (hr : r ∉ P) :
    Inv P X xs ys Fy q s0
        { s with v := fun r' j => if r' = r then 0 else s.v r' j }
        { W := fun r' t => if r' = r then 0 else bk.W r' t
          A := fun r' => if r' = r then ⊤ else bk.A r'
          B := fun r' => if r' = r then ⊥ else bk.B r'
          dep := fun r' => if r' = r then false else bk.dep r'
          lc := fun r' => if r' = r then 0 else bk.lc r'
          closed := ⟨bk.W r, s.v r, bk.A r, bk.B r, bk.lc r⟩ :: bk.closed } cost := by
  have hXr : ∀ t, X t ≠ r := fun t hh => hr (hh ▸ hXP t)
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · intro t j
    have h1 := h.i1 t j
    have hterm : ∀ r' : ι, (if r' = r then (0 : K) else bk.W r' t) * (if r' = r then 0 else s.v r' j) =
        bk.W r' t * s.v r' j - (if r' = r then bk.W r' t * s.v r' j else 0) := by
      intro r'; by_cases hh : r' = r <;> simp [hh]
    simp only [hXr t, if_false, List.map_cons, List.sum_cons, hterm, Finset.sum_sub_distrib,
      Finset.sum_ite_eq', Finset.mem_univ, if_true]
    linear_combination h1
  · intro r' hr' t hW
    by_cases hh : r' = r
    · simp [hh] at hW
    · exact h.i2 r' hr' t (by simpa [hh] using hW)
  · exact h.i2'
  · intro r' hr' hdep
    by_cases hh : r' = r
    · funext t; simp [hh]
    · funext t
      have := congrFun (h.i3 r' hr' (by simpa [hh] using hdep)) t
      simp [hh, this]
  · intro r' hr' hdep
    by_cases hh : r' = r
    · simp [hh]
    · simpa [hh] using h.i3b r' hr' (by simpa [hh] using hdep)
  · intro r' hr' t hW
    by_cases hh : r' = r
    · simp [hh] at hW
    · simpa [hh] using h.i4 r' hr' t (by simpa [hh] using hW)
  · intro r' hr' u hef a ha
    by_cases hh : r' = r
    · exfalso
      simp [eff, hh] at hef
    · have hv : (fun j => if r' = r then (0 : K) else s.v r' j) = s.v r' := by
        funext j; simp [hh]
      simp only [hv] at hef
      simp only [hh, if_false] at ha
      exact h.i5 r' hr' u hef a ha
  · intro r' hr'
    by_cases hh : r' = r
    · subst hh
      have e1 : (if r' = r' then (⊤ : Chart n) else bk.A r') ⊔ (if r' = r' then (⊥ : Chart n) else bk.B r') ⊔
          s.ch r' = ⊤ := by simp
      refine fin_le_of_eq' _ _ _ _ _ 0 e1 (if_pos rfl) (by simp) ?_
      simp
    · refine fin_le_of_eq' _ _ _ _ _ _ ?_ (if_neg hh) (by simp [hh]) (h.i6 r' hr')
      dsimp only
      rw [if_neg hh, if_neg hh]
  · intro ρ hρ
    rcases List.mem_cons.1 hρ with rfl | hρ
    · refine ⟨h.i4 r hr, h.i5 r hr, ?_⟩
      have := h.i6 r hr
      exact le_trans (Submodule.finrank_mono le_sup_left) this
    · exact h.i7 ρ hρ
  · have h8 := h.i8
    simp only [List.map_cons, List.sum_cons]
    have hsum := sum_ite_zero_add (univ.filter (· ∉ P)) bk.lc r (by simpa using hr)
    omega


theorem Inv.down (hXP : ∀ t, X t ∈ P) {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (h : Inv P X xs ys Fy q s0 s bk cost) (r : ι) (D : Chart n) (hr : r ∉ P) (hD : D ≤ s.ch r) :
    Inv P X xs ys Fy q s0 { s with ch := fun r' => if r' = r then D else s.ch r' } bk cost := by
  have hXr : ∀ t, X t ≠ r := fun t hh => hr (hh ▸ hXP t)
  refine ⟨h.i1, ?_, ?_, h.i3, h.i3b, h.i4, h.i5, ?_, h.i7, h.i8⟩
  · intro r' hr' t hW
    have hh : r' ≠ r := fun e => hr (e ▸ hr')
    simpa [hh] using h.i2 r' hr' t hW
  · intro t; simpa [hXr t] using h.i2' t
  · intro r' hr'
    by_cases hh : r' = r
    · subst hh
      refine le_trans (Submodule.finrank_mono ?_) (h.i6 r' hr')
      exact sup_le_sup_left (by show (if r' = r' then D else s.ch r') ≤ s.ch r'; simpa using hD) _
    · refine fin_le_of_eq _ _ _ _ _ ?_ (rfl) (h.i6 r' hr')
      dsimp only
      rw [if_neg hh]

theorem Inv.upOwn (hXP : ∀ t, X t ∈ P) {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (h : Inv P X xs ys Fy q s0 s bk cost) (r : ι) (D : Chart n) (hr : r ∉ P) (hD : s.ch r ≤ D) :
    Inv P X xs ys Fy q s0 { s with ch := fun r' => if r' = r then D else s.ch r' }
      { bk with lc := fun r' =>
          if r' = r then bk.lc r + (finrank (ZMod 2) D - finrank (ZMod 2) (s.ch r)) else bk.lc r' }
      (cost + (finrank (ZMod 2) D - finrank (ZMod 2) (s.ch r))) := by
  have hXr : ∀ t, X t ≠ r := fun t hh => hr (hh ▸ hXP t)
  refine ⟨h.i1, ?_, ?_, h.i3, h.i3b, h.i4, h.i5, ?_, h.i7, ?_⟩
  · intro r' hr' t hW
    have hh : r' ≠ r := fun e => hr (e ▸ hr')
    simpa [hh] using h.i2 r' hr' t hW
  · intro t; simpa [hXr t] using h.i2' t
  · intro r' hr'
    by_cases hh : r' = r
    · subst hh
      have h1 := life_up (bk.A r') (bk.B r') (s.ch r') D hD
      have h2 := h.i6 r' hr'
      have h3 : finrank (ZMod 2) (s.ch r') ≤ finrank (ZMod 2) D := Submodule.finrank_mono hD
      refine fin_le_of_eq' _ (bk.A r' ⊔ bk.B r' ⊔ D) _ (bk.A r') _
        (bk.lc r' + (finrank (ZMod 2) D - finrank (ZMod 2) (s.ch r'))) (by simp) rfl (by simp) ?_
      omega
    · refine fin_le_of_eq' _ _ _ _ _ _ ?_ rfl (by dsimp only; rw [if_neg hh]) (h.i6 r' hr')
      dsimp only
      rw [if_neg hh]
  · have h8 := h.i8
    have hterm : ∀ x : ι, (if x = r then bk.lc r + (finrank (ZMod 2) D - finrank (ZMod 2) (s.ch r))
        else bk.lc x) = bk.lc x + (if x = r then (finrank (ZMod 2) D - finrank (ZMod 2) (s.ch r)) else 0) := by
      intro x; by_cases hh : x = r
      · subst hh; simp
      · simp [hh]
    dsimp only
    have e : ∑ x ∈ univ.filter (· ∉ P), (if x = r then bk.lc r + (finrank (ZMod 2) D - finrank (ZMod 2) (s.ch r))
        else bk.lc x) = ∑ x ∈ univ.filter (· ∉ P), bk.lc x +
          (finrank (ZMod 2) D - finrank (ZMod 2) (s.ch r)) := by
      simp only [hterm, Finset.sum_add_distrib, Finset.sum_ite_eq', Finset.mem_filter, Finset.mem_univ,
        true_and, if_pos hr]
    simp only [e]
    omega

theorem Inv.upPub (hXP : ∀ t, X t ∈ P) {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (h : Inv P X xs ys Fy q s0 s bk cost) (r : ι) (D : Chart n) (hr : r ∈ P) (hD : s.ch r ≤ D) :
    Inv P X xs ys Fy q s0 { s with ch := fun r' => if r' = r then D else s.ch r' } bk cost := by
  refine ⟨h.i1, ?_, ?_, h.i3, h.i3b, h.i4, h.i5, ?_, h.i7, h.i8⟩
  · intro r' hr' t hW
    by_cases hh : r' = r
    · subst hh; simpa using hD (h.i2 r' hr' t hW)
    · simpa [hh] using h.i2 r' hr' t hW
  · intro t
    by_cases hh : X t = r
    · have h1 : q t ∈ s.ch r := hh ▸ h.i2' t
      simpa [hh] using hD h1
    · simpa [hh] using h.i2' t
  · intro r' hr'
    have hh : r' ≠ r := fun e => hr' (e ▸ hr)
    refine fin_le_of_eq _ _ _ _ _ ?_ (rfl) (h.i6 r' hr')
    dsimp only
    rw [if_neg hh]

theorem inv_of_run (hXP : ∀ t, X t ∈ P) (hq : ∀ t, q t ∈ s0.ch (X t)) (h0 : ∀ r ∉ P, s0.v r = 0)
    {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (hrun : ARun P X xs ys Fy q s0 s bk cost) : Inv P X xs ys Fy q s0 s bk cost := by
  induction hrun with
  | refl => exact Inv.refl P X xs ys Fy q s0 hq h0
  | add d e l hne hch hgtd hcold _ ih => exact Inv.add P X xs ys Fy q s0 hXP ih d e l hne hch hgtd hcold
  | init r hr _ ih => exact Inv.init' P X xs ys Fy q s0 hXP ih r hr
  | down r D hr hD _ ih => exact Inv.down P X xs ys Fy q s0 hXP ih r D hr hD
  | upOwn r D hr hD _ ih => exact Inv.upOwn P X xs ys Fy q s0 hXP ih r D hr hD
  | upPub r D hr hD _ ih => exact Inv.upPub P X xs ys Fy q s0 hXP ih r D hr hD

end Inv

/-! ## Decoders, the price lemma, and the headline -/
section Decoder
variable {K : Type*} [Field K] {τ ι ω : Type*} {n : ℕ} [Fintype τ]

/-- a decoder row: left vector `w` (ports it reads into), right vector `u` (ports it carries) -/
structure DRow (K : Type*) (τ : Type*) where
  w : τ → K
  u : τ → K

open Classical in
/-- price of a row: `rank_F2 Q[supp w, supp u]` with `Q t s = q_t · q_s`. -/
noncomputable def price (q : τ → Fin n → ZMod 2) (ρ : DRow K τ) : ℕ :=
  (gram (fun t : {t // ρ.w t ≠ 0} => q t.1) (fun s : {s // ρ.u s ≠ 0} => q s.1)).rank

/-- the rows form a Q-mask decoder of the pattern `Rec` on the odd cells (`Q t s = 1`). -/
def IsDec (q : τ → Fin n → ZMod 2) (Rec : τ → τ → K) (rows : List (DRow K τ)) : Prop :=
  ∀ t s, q t ⬝ᵥ q s = 1 → (rows.map fun ρ => ρ.w t * ρ.u s).sum = Rec t s

/-- decoder mass: least total price of a decoder. -/
noncomputable def mass (q : τ → Fin n → ZMod 2) (Rec : τ → τ → K) : ℕ :=
  sInf {m | ∃ rows, IsDec q Rec rows ∧ (rows.map (price q)).sum = m}

/-- the decoder wall hypothesis `Wall N`: every decoder has total price ≥ N. -/
def Wall (q : τ → Fin n → ZMod 2) (Rec : τ → τ → K) (N : ℕ) : Prop :=
  ∀ rows, IsDec q Rec rows → N ≤ (rows.map (price q)).sum

theorem mass_le {q : τ → Fin n → ZMod 2} {Rec : τ → τ → K} {rows : List (DRow K τ)}
    (h : IsDec q Rec rows) : mass q Rec ≤ (rows.map (price q)).sum :=
  Nat.sInf_le ⟨rows, h, rfl⟩

variable (xs ys : τ → ω) (Fy : τ → τ → K) (q : τ → Fin n → ZMod 2)

/-- PRICE LEMMA for a valid lifetime row: price ≤ `dim B − dim (B ∩ A)` ≤ lifetime cost. -/
theorem price_le (ρ : Row K τ ω n) (hok : ρ.ok xs ys Fy q) :
    price q ⟨ρ.w, eff xs ys Fy ρ.val⟩ ≤ ρ.lc := by
  classical
  obtain ⟨h1, h2, h3⟩ := hok
  unfold price
  set lD : {t // ρ.w t ≠ 0} → Fin n → ZMod 2 := fun t => q t.1 with hlD
  set lS : {s // eff xs ys Fy ρ.val s ≠ 0} → Fin n → ZMod 2 := fun s => q s.1 with hlS
  have hM : Submodule.span (ZMod 2) (Set.range lD) ≤ ρ.B := by
    apply Submodule.span_le.2
    rintro _ ⟨t, rfl⟩; exact h1 t.1 t.2
  have hL : ρ.B ⊓ ρ.A ≤ perp (Submodule.span (ZMod 2) (Set.range lS)) := by
    rw [le_perp_iff]
    apply Submodule.span_le.2
    rintro _ ⟨s, rfl⟩
    show q s.1 ∈ perp (ρ.B ⊓ ρ.A)
    rw [mem_perp]
    intro y hy
    exact h2 s.1 s.2 y (Submodule.mem_inf.1 hy).2
  have key := (exact_price lD lS).2
    (show finrank (ZMod 2) ρ.B - finrank (ZMod 2) (ρ.B ⊓ ρ.A : Chart n) ∈ PriceSet lD lS from
      ⟨ρ.B, ρ.B ⊓ ρ.A, hM, inf_le_left, hL, rfl⟩)
  refine le_trans key ?_
  have e1 := Submodule.finrank_sup_add_finrank_inf_eq ρ.A ρ.B
  rw [inf_comm] at e1
  omega


/-- linearity of the effective-content map over a list of rows -/
lemma list_sum_eff (L : List (Row K τ ω n)) (t s' : τ) :
    (L.map fun ρ => ρ.w t * eff xs ys Fy ρ.val s').sum =
      (L.map fun ρ => ρ.w t * ρ.val (ys s')).sum -
        ∑ u, (L.map fun ρ => ρ.w t * ρ.val (xs u)).sum * Fy u s' := by
  induction L with
  | nil => simp
  | cons a L ih =>
    simp only [List.map_cons, List.sum_cons] at ih ⊢
    rw [ih]
    have e1 : a.w t * eff xs ys Fy a.val s' = a.w t * a.val (ys s') -
        ∑ u, (a.w t * a.val (xs u)) * Fy u s' := by
      simp only [eff, mul_sub, Finset.mul_sum, mul_assoc]
    have e2 : ∑ u, (a.w t * a.val (xs u) + (L.map fun ρ => ρ.w t * ρ.val (xs u)).sum) * Fy u s' =
        ∑ u, (a.w t * a.val (xs u)) * Fy u s' +
          ∑ u, (L.map fun ρ => ρ.w t * ρ.val (xs u)).sum * Fy u s' := by
      simp only [add_mul, Finset.sum_add_distrib]
    rw [e2, e1]; ring

variable [DecidableEq ι] [Fintype ι]

/-- the lifetimes of a finished run: closed ones, then the open lifetime of every owned register -/
noncomputable def finalRows (P : Finset ι) (s : St K n ι ω) (bk : Bk K τ ω ι n) : List (Row K τ ω n) :=
  bk.closed ++ (univ.filter (· ∉ P)).toList.map
    (fun r => (⟨bk.W r, s.v r, bk.A r, bk.B r, bk.lc r⟩ : Row K τ ω n))

variable (P : Finset ι) (X : τ → ι) (s0 : St K n ι ω)

lemma finalRows_ok {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (h : Inv P X xs ys Fy q s0 s bk cost) : ∀ ρ ∈ finalRows P s bk, ρ.ok xs ys Fy q := by
  intro ρ hρ
  rcases List.mem_append.1 hρ with hρ | hρ
  · exact h.i7 ρ hρ
  · obtain ⟨r, hr, rfl⟩ := List.mem_map.1 hρ
    have hr' : r ∉ P := by simpa using (Finset.mem_toList.1 hr)
    exact ⟨h.i4 r hr', h.i5 r hr', le_trans (Submodule.finrank_mono le_sup_left) (h.i6 r hr')⟩

lemma finalRows_cost {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (h : Inv P X xs ys Fy q s0 s bk cost) : ((finalRows P s bk).map fun ρ => ρ.lc).sum = cost := by
  rw [h.i8]
  simp only [finalRows, List.map_append, List.sum_append, List.map_map, Function.comp_def,
    Finset.sum_map_toList]
  ring

lemma finalRows_sum {s : St K n ι ω} {bk : Bk K τ ω ι n}
    (t : τ) (j : ω) :
    ∑ r, bk.W r t * s.v r j + (bk.closed.map fun ρ => ρ.w t * ρ.val j).sum =
      ∑ r ∈ P, bk.W r t * s.v r j + ((finalRows P s bk).map fun ρ => ρ.w t * ρ.val j).sum := by
  have hsplit := Finset.sum_filter_add_sum_filter_not (univ : Finset ι) (· ∈ P)
    (fun r => bk.W r t * s.v r j)
  have hP : univ.filter (· ∈ P) = P := by ext; simp
  rw [hP] at hsplit
  rw [← hsplit]
  simp only [finalRows, List.map_append, List.sum_append, List.map_map, Function.comp_def,
    Finset.sum_map_toList]
  ring


/-- HEADLINE (future-attribution cancellation law).  For every run in class F (GTD lifetimes,
cold intake), starting with owned registers at 0, publics never descending, the final data
(`hfx`: x-parts of finals, `hfy`: non-target publics cold at their final chart, `hfyX`: y-part of
the target finals, `hbal`: receipts have zero x-part) yield a decoder of the receipts
`final(X_t)[y_s] − start(X_t)[y_s]` on the odd cells with total price ≤ R (the owned cost). -/
theorem attribution_decoder (hXP : ∀ t, X t ∈ P) (hXinj : Function.Injective X)
    (hq : ∀ t, q t ∈ s0.ch (X t)) (h0 : ∀ r ∉ P, s0.v r = 0)
    {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (hrun : ARun P X xs ys Fy q s0 s bk cost)
    (hfx : ∀ r ∈ P, ∀ u, s.v r (xs u) = if r = X u then 1 else 0)
    (hfy : ∀ r ∈ P, (∀ u, r ≠ X u) → ∀ u, s.v r (ys u) ≠ 0 → ∀ a ∈ s.ch r, a ⬝ᵥ q u = 0)
    (hfyX : ∀ u u', s.v (X u) (ys u') = Fy u u')
    (hbal : ∀ t u, s.v (X t) (xs u) = s0.v (X t) (xs u)) :
    ∃ rows : List (DRow K τ),
      IsDec q (fun t u => s.v (X t) (ys u) - s0.v (X t) (ys u)) rows ∧
      (rows.map (price q)).sum ≤ cost := by
  classical
  have h := inv_of_run P X xs ys Fy q s0 hXP hq h0 hrun
  have hok := finalRows_ok xs ys Fy q P X s0 h
  have hcost := finalRows_cost xs ys Fy q P X s0 h
  refine ⟨(finalRows P s bk).map fun ρ => ⟨ρ.w, eff xs ys Fy ρ.val⟩, ?_, ?_⟩
  · intro t u' hQ
    -- x-balance: the target weights are minus the owned x-content
    have hx : ∀ u, bk.W (X u) t = -(((finalRows P s bk).map fun ρ => ρ.w t * ρ.val (xs u)).sum) := by
      intro u
      have h1 := h.i1 t (xs u)
      rw [hbal t u, sub_self, finalRows_sum P t (xs u)] at h1
      have h2 : ∑ r ∈ P, bk.W r t * s.v r (xs u) = bk.W (X u) t := by
        rw [Finset.sum_congr rfl (fun r hr => by rw [hfx r hr u])]
        simp [hXP u]
      rw [h2] at h1
      exact eq_neg_of_add_eq_zero_left h1.symm
    -- y-part of the public side: only target registers contribute on odd cells
    have hy : ∑ r ∈ P, bk.W r t * s.v r (ys u') = ∑ u, bk.W (X u) t * Fy u u' := by
      have hsub : (univ.image X) ⊆ P := by
        intro r hr; obtain ⟨u, -, rfl⟩ := Finset.mem_image.1 hr; exact hXP u
      rw [← Finset.sum_subset hsub, Finset.sum_image (fun a _ b _ hab => hXinj hab)]
      · exact Finset.sum_congr rfl (fun u _ => by rw [hfyX])
      · intro r hrP hrn
        have hrX : ∀ u, r ≠ X u := fun u hu => hrn (Finset.mem_image.2 ⟨u, mem_univ _, hu.symm⟩)
        by_contra hne
        have hW : bk.W r t ≠ 0 := fun hh => hne (by rw [hh, zero_mul])
        have hv : s.v r (ys u') ≠ 0 := fun hh => hne (by rw [hh, mul_zero])
        have := hfy r hrP hrX u' hv (q t) (h.i2 r hrP t hW)
        rw [this] at hQ
        exact zero_ne_one hQ
    have h2 := h.i1 t (ys u')
    rw [finalRows_sum P t (ys u'), hy] at h2
    have e3 : ∑ u, bk.W (X u) t * Fy u u' =
        -∑ u, ((finalRows P s bk).map fun ρ => ρ.w t * ρ.val (xs u)).sum * Fy u u' := by
      rw [← Finset.sum_neg_distrib]
      apply Finset.sum_congr rfl; intro u _; rw [hx u]; ring
    simp only [List.map_map, Function.comp_def]
    have := list_sum_eff xs ys Fy (finalRows P s bk) t u'
    rw [this, h2, e3]; ring
  · simp only [List.map_map, Function.comp_def]
    rw [← hcost]
    apply List.sum_le_sum
    intro ρ hρ
    exact price_le xs ys Fy q ρ (hok ρ hρ)

/-- R ≥ m(Q): the owned cost is at least the decoder mass of the receipt pattern. -/
theorem mass_le_R (hXP : ∀ t, X t ∈ P) (hXinj : Function.Injective X)
    (hq : ∀ t, q t ∈ s0.ch (X t)) (h0 : ∀ r ∉ P, s0.v r = 0)
    {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (hrun : ARun P X xs ys Fy q s0 s bk cost)
    (hfx : ∀ r ∈ P, ∀ u, s.v r (xs u) = if r = X u then 1 else 0)
    (hfy : ∀ r ∈ P, (∀ u, r ≠ X u) → ∀ u, s.v r (ys u) ≠ 0 → ∀ a ∈ s.ch r, a ⬝ᵥ q u = 0)
    (hfyX : ∀ u u', s.v (X u) (ys u') = Fy u u')
    (hbal : ∀ t u, s.v (X t) (xs u) = s0.v (X t) (xs u)) :
    mass q (fun t u => s.v (X t) (ys u) - s0.v (X t) (ys u)) ≤ cost := by
  obtain ⟨rows, hd, hle⟩ := attribution_decoder xs ys Fy q P X s0 hXP hXinj hq h0 hrun hfx hfy hfyX hbal
  exact le_trans (mass_le hd) hle

/-- Corollary: the decoder wall `Wall N` (an explicit hypothesis, e.g. `N = 56` at Q96)
gives `R ≥ N` for every class-F run. -/
theorem R_ge_of_wall (N : ℕ) (hXP : ∀ t, X t ∈ P) (hXinj : Function.Injective X)
    (hq : ∀ t, q t ∈ s0.ch (X t)) (h0 : ∀ r ∉ P, s0.v r = 0)
    {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (hrun : ARun P X xs ys Fy q s0 s bk cost)
    (hfx : ∀ r ∈ P, ∀ u, s.v r (xs u) = if r = X u then 1 else 0)
    (hfy : ∀ r ∈ P, (∀ u, r ≠ X u) → ∀ u, s.v r (ys u) ≠ 0 → ∀ a ∈ s.ch r, a ⬝ᵥ q u = 0)
    (hfyX : ∀ u u', s.v (X u) (ys u') = Fy u u')
    (hbal : ∀ t u, s.v (X t) (xs u) = s0.v (X t) (xs u))
    (hwall : Wall q (fun t u => s.v (X t) (ys u) - s0.v (X t) (ys u)) N) : N ≤ cost := by
  obtain ⟨rows, hd, hle⟩ := attribution_decoder xs ys Fy q P X s0 hXP hXinj hq h0 hrun hfx hfy hfyX hbal
  exact le_trans (hwall rows hd) hle

end Decoder

/-! ## Non-vacuity: one port, one gather-then-deposit lifetime.
Registers `0 = X` (public, chart ⊤ ∋ q), `1 = Y` (public, chart ⊥ ⊆ q^⊥), `2 = O` (owned, chart ⊥).
O gathers `y` from Y at chart ⊥ (cold intake), ascends ⊥ → ⊤ (cost 1), deposits `−O` into X:
`X = x − y`. -/
namespace Toy

def Pub : Finset (Fin 3) := {0, 1}
def Xr : Unit → Fin 3 := fun _ => 0
def xsym : Unit → Fin 2 := fun _ => 0
def ysym : Unit → Fin 2 := fun _ => 1
def Fy1 : Unit → Unit → ℚ := fun _ _ => -1
def q1 : Unit → Fin 1 → ZMod 2 := fun _ _ => 1
def st0 : St ℚ 1 (Fin 3) (Fin 2) where
  ch := fun r => if r = 0 then ⊤ else ⊥
  v := fun r j => if r = 0 then (if j = 0 then 1 else 0)
    else if r = 1 then (if j = 1 then 1 else 0) else 0

theorem toy_run :
    ∃ (s : St ℚ 1 (Fin 3) (Fin 2)) (bk : Bk ℚ Unit (Fin 2) (Fin 3) 1) (cost : ℕ),
      ARun Pub Xr xsym ysym Fy1 q1 st0 s bk cost ∧ cost = 1 ∧
      mass q1 (fun t u => s.v (Xr t) (ysym u) - st0.v (Xr t) (ysym u)) ≤ 1 ∧
      (fun t u => s.v (Xr t) (ysym u) - st0.v (Xr t) (ysym u)) () () = -1 := by
  have h1 := ARun.add (P := Pub) (X := Xr) (xs := xsym) (ys := ysym) (Fy := Fy1) (q := q1)
    (s0 := st0) (s := st0) (bk := Bk.init) (cost := 0) 2 1 (1 : ℚ) (by decide)
    (by simp [st0]) (fun _ => rfl)
    (by
      intro _ u _ a ha
      have : a = 0 := by simpa [st0] using ha
      simp [this]) ARun.refl
  have h2 := ARun.upOwn (P := Pub) (X := Xr) (xs := xsym) (ys := ysym) (Fy := Fy1) (q := q1)
    (s0 := st0) 2 (⊤ : Chart 1) (by decide) (by simp [st0]) h1
  have h3 := ARun.add (P := Pub) (X := Xr) (xs := xsym) (ys := ysym) (Fy := Fy1) (q := q1)
    (s0 := st0) 0 2 (-1 : ℚ) (by decide) (by simp [st0]) (fun h => absurd (by decide) h)
    (fun h => absurd (by decide) h) h2
  refine ⟨_, _, _, h3, ?_, ?_, ?_⟩
  · have hb : finrank (ZMod 2) (⊥ : Chart 1) = 0 := finrank_bot (ZMod 2) _
    simp only [st0]
    simp
    exact (congrArg (fun m => 1 - m) hb).trans rfl
  · refine le_trans (mass_le_R xsym ysym Fy1 q1 Pub Xr st0 ?_ ?_ ?_ ?_ h3 ?_ ?_ ?_ ?_) ?_
    · intro t; simp [Pub, Xr]
    · intro a b _; exact Subsingleton.elim a b
    · intro t; simp [st0, Xr]
    · intro r hr
      fin_cases r
      · simp [Pub] at hr
      · simp [Pub] at hr
      · funext j; simp [st0]
    · intro r hr u; fin_cases r <;> simp_all [Pub, st0, Xr, xsym]
    · intro r hr hne u hv a ha
      fin_cases r
      · exact absurd rfl (hne ())
      · have : a = 0 := by simpa [st0] using ha
        simp [this]
      · simp [Pub] at hr
    · intro u u'; simp [st0, Xr, ysym, Fy1]
    · intro t u; simp [st0, Xr, xsym]
    · simp only [st0]
      simp
  · simp [st0, Xr, ysym]

end Toy

#print axioms inv_of_run
#print axioms price_le
#print axioms attribution_decoder
#print axioms mass_le_R
#print axioms R_ge_of_wall
#print axioms Toy.toy_run

end FutureAttr
