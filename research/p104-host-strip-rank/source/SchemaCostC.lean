/-
SchemaCostC (lane SCHEMACOST, Nov 20).  Part C: the caller laws with (i) NO schema hypothesis (SchemaCostA) and (ii) stated for the REPO's
caller invoice (SchemaCostB), plus the op-by-op link to CERTKIT's items.  See SchemaCostA / SchemaCostB headers.
Kernel only.
-/
import Nov15.SchemaCostB

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace SchemaCost
open Finset Matrix CallerSign CallerWord CallerAsm CallerHP CallerEv CallerBridge

/-! ## link to CertCallerCore items -/
section link
variable {n k : ℕ}

/-- CertCaller opcode of a PLAIN event (J = 0 is a record, never a plain event). -/
def opOf : Ev n k → ℕ
  | .host .. => 0
  | .add .. => 1
  | .scale .. => 2
  | .swap .. => 3
  | .lam .. => 4
  | .query .. => 5
  | .idle _ _ q => if q % 2 = 0 then 6 else 7

/-- the model price of a plain event, times the ports of its type, IS the CERTKIT item `evItem` (op by op). -/
theorem price_eq_item (C : CertCaller.CData) (x : ℕ) (e : Ev n k) (hp : PlainOK e)
    (hop : CertCaller.evOp x = opOf e)
    (hst : ∀ r S q, e = Ev.idle r S q → CertCaller.popc (CertCaller.evSt x) 26 = S.card) (σ : ℝ) :
    SafeRungsPrice.cdat σ (CertCaller.evItem C x) = (CertCaller.portsOf C (CertCaller.evTy x) : ℝ) * price σ e := by
  cases e with
  | query a1 a2 a3 =>
    have : CertCaller.evOp x = 5 := hop
    simp [CertCaller.evItem, this, SafeRungsPrice.cdat, price]
  | idle r S q =>
    have hpc := hst r S q rfl
    by_cases h : q % 2 = 0
    · have : CertCaller.evOp x = 6 := by simpa [opOf, h] using hop
      simp [CertCaller.evItem, this, SafeRungsPrice.cdat, price, h, hpc]
    · have : CertCaller.evOp x = 7 := by simpa [opOf, h] using hop
      simp [CertCaller.evItem, this, SafeRungsPrice.cdat, price, h, hpc]
  | add a1 a2 a3 =>
    have : CertCaller.evOp x = 1 := hop
    simp [CertCaller.evItem, this, SafeRungsPrice.cdat, price]
  | scale a1 a2 =>
    have : CertCaller.evOp x = 2 := hop
    simp [CertCaller.evItem, this, SafeRungsPrice.cdat, price]
  | swap a1 a2 =>
    have : CertCaller.evOp x = 3 := hop
    simp [CertCaller.evItem, this, SafeRungsPrice.cdat, price]
  | lam a1 a2 =>
    have : CertCaller.evOp x = 4 := hop
    simp [CertCaller.evItem, this, SafeRungsPrice.cdat, price]
  | host a1 a2 a3 a4 => exact absurd hp (by simp [PlainOK])

/-- the target rank of CERTKIT for the verifier's exponent -1 (packed slot 2^15 - 1) is 8 |mask| + 1. -/
theorem rowRank_neg1 (m : ℕ) : CertCaller.rowRank ((2 ^ 15 - 1) + 2 ^ 16 * m) = 1 + 8 * CertCaller.popc m 40 := by
  unfold CertCaller.rowRank
  have h1 : ((2 ^ 15 - 1) + 2 ^ 16 * m) % 2 ^ 16 = 2 ^ 15 - 1 := by omega
  have h2 : ((2 ^ 15 - 1) + 2 ^ 16 * m) / 2 ^ 16 = m := by omega
  rw [h1, h2]
  norm_num

end link

/-! ## weighting the two types -/

/-- the repo caller quantity is the ports-weighted sum of the two types' per-port quantities; each type bounded => the total is. -/
theorem total_le (k : ℕ) (hk : 0 < k) (pA pB RA RB b : ℝ) (hpA : 0 ≤ pA) (hpB : 0 ≤ pB) (hp : pA + pB = 104)
    (hA : 104 / (k : ℝ) * RA ≤ b) (hB : 104 / (k : ℝ) * RB ≤ b) :
    (pA * RA + pB * RB) / k ≤ b := by
  have hk' : (0:ℝ) < k := by exact_mod_cast hk
  have h1 : pA * (104 / (k:ℝ) * RA) ≤ pA * b := mul_le_mul_of_nonneg_left hA hpA
  have h2 : pB * (104 / (k:ℝ) * RB) ≤ pB * b := mul_le_mul_of_nonneg_left hB hpB
  have : (pA * RA + pB * RB) / k * 104 ≤ 104 * b := by
    have e : (pA * RA + pB * RB) / k * 104 = pA * (104 / (k:ℝ) * RA) + pB * (104 / (k:ℝ) * RB) := by
      field_simp
    have hab : pA * b + pB * b = 104 * b := by rw [← add_mul, hp]
    rw [e]; linarith
  nlinarith

/-! ## the headlines for the repo invoice -/
section headlines
variable {n k : ℕ}

theorem GramB.jm (G : GramB n k) (c : Fin k) :
    ((G.blk.jx c).map (mdl σ0)).sum = ((2 : ℕ) : ℝ) * 8 ^ σ0 := by
  simp [GramB.blk, jB, mdl]; ring

theorem GramB.jc (G : GramB n k) (c : Fin k) :
    ((G.blk.jx c).map fun e => (colCnt e : ℝ)).sum = 2 := by
  simp [GramB.blk, jB, colCnt_eq_sum, terms, Fin.sum_univ_two]
  norm_num

theorem GramA.jm (G : GramA n k) (c : Fin k) :
    ((G.blk.jx c).map (mdl σ0)).sum = ((4 : ℕ) : ℝ) * 8 ^ σ0 := by
  simp [GramA.blk, jA, mdl]; ring

theorem GramA.jc (G : GramA n k) (c : Fin k) :
    ((G.blk.jx c).map fun e => (colCnt e : ℝ)).sum = 2 := by
  simp [GramA.blk, jA, colCnt_eq_sum, terms, Fin.sum_univ_two]
  norm_num

variable (G : GramB n k) (hpre : ∀ c, ∀ e ∈ G.pre c, PlainOK e) (hpost : ∀ e ∈ G.post, PlainOK e)
include hpre hpost

/-- B, Q = 0: the REPO invoice (per port, native contacts removed) is `<= HP(k)`; no schema, no odd-target hypothesis. -/
theorem gramB_real_hp (hL : Legal G.word) (hk : 3 ≤ k)
    (hQ0 : Fintype.card (Iota G.word) = 2 * k) (hn : n + 2 = Fintype.card (Iota G.word))
    (hlam : ∀ s, IsUnit ((sgK (βw G.word) (sgG (Aw G.word Complex.I) (Bw G.word Complex.I))).submatrix
      (G.jb.col s) (G.jb.col s)).det)
    (hdeg : ∀ r, 2 ≤ (G.word.mask r).card) :
    104 / (k : ℝ) * repo G.blk 2 ≤ HPr k := by
  have e : repo G.blk 2 = (k : ℝ) / 104 * cHat G.word := repo_eq_q0 2 G.jm G.jc hpre hpost G.ex_eq (by omega) hn hQ0
  have h2 := gramB_hp G hL hk hQ0 hn hlam hdeg
  have hk' : (k : ℝ) ≠ 0 := by have : 0 < k := by omega
                               positivity
  rw [e]; field_simp; exact h2

/-- B, thin columns: the repo invoice is within `Q = n - (2k-2)` units of `cHatQ` (one-sided, see SchemaCostB); with no
IDLE_ODD on a nonempty stage set (QUERY-only thins) it IS `cHatQ`, hence `< 128.891`. -/
theorem gramB_real_hpq (hL : Legal G.word) (hk : 77 ≤ k) (hn : n + 2 = Fintype.card (Iota G.word))
    (hlam : ∀ s, IsUnit ((sgK (βw G.word) (sgG (Aw G.word Complex.I) (Bw G.word Complex.I))).submatrix
      (G.jb.col s) (G.jb.col s)).det)
    (hdeg1 : ∀ r, 1 ≤ (G.word.mask r).card)
    (hemp : ∀ c, ∀ e ∈ G.pre c, ∀ r S q, e = Ev.idle r S q → q % 2 = 1 → S = ∅)
    (hemp' : ∀ e ∈ G.post, ∀ r S q, e = Ev.idle r S q → q % 2 = 1 → S = ∅) :
    104 / (k : ℝ) * repo G.blk 2 < 128891 / 1000 := by
  have e : repo G.blk 2 = (k : ℝ) / 104 * cHatQ G.word :=
    repo_eq_of_empty 2 G.jm G.jc hpre hpost G.ex_eq (by omega) hn hemp hemp'
  have h2 := gramB_hpq G hL hk hn hlam hdeg1
  have hk' : (k : ℝ) ≠ 0 := by have : 0 < k := by omega
                               positivity
  rw [e]
  have : 104 / (k : ℝ) * ((k : ℝ) / 104 * cHatQ G.word) = cHatQ G.word := by field_simp
  rw [this]; exact h2

/-- B, thin columns, general IDLE_ODD: `104/k * repo < 128.891 + 104/k * (n - (2k-2))`. -/
theorem gramB_real_hpq_gap (hL : Legal G.word) (hk : 77 ≤ k) (hn : n + 2 = Fintype.card (Iota G.word))
    (hlam : ∀ s, IsUnit ((sgK (βw G.word) (sgG (Aw G.word Complex.I) (Bw G.word Complex.I))).submatrix
      (G.jb.col s) (G.jb.col s)).det)
    (hdeg1 : ∀ r, 1 ≤ (G.word.mask r).card) :
    104 / (k : ℝ) * repo G.blk 2 < 128891 / 1000 + 104 / (k : ℝ) * ((n : ℝ) - (2 * k - 2)) := by
  have e : repo G.blk 2 ≤ (k : ℝ) / 104 * cHatQ G.word + ((n : ℝ) - (2 * k - 2)) :=
    repo_le 2 G.jm G.jc hpre hpost G.ex_eq (by omega) hn
  have h2 := gramB_hpq G hL hk hn hlam hdeg1
  have hk' : (0 : ℝ) < k := by exact_mod_cast (show 0 < k by omega)
  have h3 : 104 / (k : ℝ) * repo G.blk 2 ≤ cHatQ G.word + 104 / (k : ℝ) * ((n : ℝ) - (2 * k - 2)) := by
    have := mul_le_mul_of_nonneg_left e (show (0:ℝ) ≤ 104 / (k : ℝ) by positivity)
    have e2 : 104 / (k : ℝ) * ((k : ℝ) / 104 * cHatQ G.word + ((n : ℝ) - (2 * k - 2)))
        = cHatQ G.word + 104 / (k : ℝ) * ((n : ℝ) - (2 * k - 2)) := by field_simp
    linarith
  linarith

end headlines

/-- non-vacuity of the cost hypotheses (plain-event grammar, per-call contact sums) on the concrete 3-stage B grammar `gB`. -/
theorem gB_plain : (∀ c, ∀ e ∈ gB.pre c, PlainOK e) ∧ ∀ e ∈ gB.post, PlainOK e := by
  refine ⟨fun c e he => ?_, fun e he => ?_⟩
  · simp only [gB] at he; split_ifs at he <;> simp at he <;> subst he <;> trivial
  · simp only [gB] at he; simp at he; subst he; trivial

theorem gB_contacts : ((gB.blk.jx 0).map (mdl σ0)).sum = ((2 : ℕ) : ℝ) * 8 ^ σ0 := GramB.jm gB 0

end SchemaCost

#print axioms SchemaCost.price_eq_item
#print axioms SchemaCost.rowRank_neg1
#print axioms SchemaCost.total_le
#print axioms SchemaCost.repo_eq
#print axioms SchemaCost.repo_ge
#print axioms SchemaCost.repo_le
#print axioms SchemaCost.repo_eq_of_empty
#print axioms SchemaCost.repo_eq_q0
#print axioms SchemaCost.gramB_real_hp
#print axioms SchemaCost.gramB_real_hpq
#print axioms SchemaCost.gramB_real_hpq_gap
