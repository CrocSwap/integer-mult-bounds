/-
SafeRungsPrice .  the pricing notes.
PRICE LAYER of the two SAFE word rungs.  s = 1 - t in [0,1], g(k) = k^s, c = 2 - 2^s.
 SPEC: the price of a MOVE is a pseudometric d (rank of the frame change): d >= 0, d a a = 0, triangle  (htri).
 Invoice (Theorem K): per word  FW = Dc + 17 * ( helper credits - helper move costs - main costs - owned costs
   - stops * c ).  Dc = the #7113 caller invoice (data: ladder.log T/P tables, caller = 17 J calls).
 Proved here (kernel only):
   chain_le        : d x0 xn <= sum of step prices (triangle)
   path_cost_ge    : v <= d x0 xn, n >= 1  ->  v^s <= sum of step^s   (subadditivity of x^s)
   helper_net_le   : credit <= cost (helpers <= 0),  main_cost_ge: each main costs >= 8^s
   P0_ceiling      : FW <= Dc - 17*400*8^s                       (400 rank-8 mains; owned, stops >= 0)
   U0_ceiling      : with >= 16 owned moves of price >= 1 and stops >= 104 - n:  FW <= Dc - 17*(400*8^s+16+88c)
   kappa_le_P0 / kappa_le_U0 : the crossing is below .0227043 / .0204111, given the real-number certificate
       CertP0 / CertU0 (named hypotheses: negativity of the ceiling invoice on [kbar,1]; ladder.log / ma.log).
 NOT proved here: the geometric premises: the 400 mains + endpoint distance 8 (#7113 contract),
 owned price >= 1 (SPEC lattice distance, ERRATUM), V-asc (l.51) for R1-R3 counts, R3 stops.
-/
import Mathlib.Analysis.Convex.SpecificFunctions.Pow
import Mathlib.Analysis.MeanInequalitiesPow
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Positivity

open Finset

namespace SafeRungsPrice

/-- sum over a list of (rank, count) of count * rank^s. -/
noncomputable def cdat (s : ℝ) (l : List (ℕ × ℕ)) : ℝ :=
  (l.map fun p => (p.2 : ℝ) * (p.1 : ℝ) ^ s).sum

/-- DATA (ladder.log, caller of #7113, 17 J calls): helper climb counts T_r. -/
def Tcal : List (ℕ × ℕ) :=
  [(9, 416), (17, 416), (25, 416), (33, 416), (41, 416), (49, 416), (57, 416), (65, 416), (73, 208), (137, 208)]
/-- DATA (ladder.log): MOVE rank counts P_r of the caller. -/
def Pcal : List (ℕ × ℕ) :=
  [(1, 384), (8, 656), (9, 32), (16, 416), (24, 416), (32, 416), (40, 416), (48, 416), (56, 416), (64, 208)]

/-- the caller invoice D(s) = sum (T_r - P_r) r^s. -/
noncomputable def Dc (s : ℝ) : ℝ := cdat s Tcal - cdat s Pcal

noncomputable def cstop (s : ℝ) : ℝ := 2 - 2 ^ s

theorem cstop_nonneg (s : ℝ) (hs0 : 0 ≤ s) (hs1 : s ≤ 1) : 0 ≤ cstop s := by
  have : (2:ℝ) ^ s ≤ 2 ^ (1:ℝ) := Real.rpow_le_rpow_of_exponent_le (by norm_num) hs1
  unfold cstop; simp at this; linarith

theorem cstop_le_one (s : ℝ) (hs0 : 0 ≤ s) : cstop s ≤ 1 := by
  have : (1:ℝ) ≤ 2 ^ s := Real.one_le_rpow (by norm_num) hs0
  unfold cstop; linarith

/-- subadditivity of x^s on [0,inf), s in [0,1], summed over a range, with a base term. -/
theorem sum_rpow_aux (s : ℝ) (hs0 : 0 ≤ s) (hs1 : s ≤ 1) (f : ℕ → ℝ) (hf : ∀ i, 0 ≤ f i)
    (a : ℝ) (ha : 0 ≤ a) (n : ℕ) :
    (a + ∑ i ∈ range n, f i) ^ s ≤ a ^ s + ∑ i ∈ range n, f i ^ s := by
  induction n with
  | zero => simp
  | succ n ih =>
    have hsum : 0 ≤ ∑ i ∈ range n, f i := sum_nonneg (fun i _ => hf i)
    have h := Real.rpow_add_le_add_rpow (add_nonneg ha hsum) (hf n) hs0 hs1
    rw [sum_range_succ, sum_range_succ, ← add_assoc]
    linarith

theorem sum_rpow_ge (s : ℝ) (hs0 : 0 ≤ s) (hs1 : s ≤ 1) (f : ℕ → ℝ) (hf : ∀ i, 0 ≤ f i)
    (n : ℕ) (hn : 1 ≤ n) : (∑ i ∈ range n, f i) ^ s ≤ ∑ i ∈ range n, f i ^ s := by
  obtain ⟨m, rfl⟩ : ∃ m, n = m + 1 := ⟨n - 1, by omega⟩
  rw [sum_range_succ', sum_range_succ', add_comm (∑ i ∈ range m, f (i + 1)) (f 0),
    add_comm (∑ i ∈ range m, f (i + 1) ^ s) (f 0 ^ s)]
  exact sum_rpow_aux s hs0 hs1 (fun i => f (i + 1)) (fun i => hf _) (f 0) (hf 0) m

section Metric
variable {α : Type*} (d : α → α → ℝ)

/-- SPEC premise: MOVE price is a pseudometric (rank of the frame change). -/
structure PriceMetric : Prop where
  nonneg : ∀ a b, 0 ≤ d a b
  refl : ∀ a, d a a = 0
  tri : ∀ a b c, d a c ≤ d a b + d b c

/-- price^s of a path x 0, x 1, ..., x n. -/
noncomputable def pcost (x : ℕ → α) (n : ℕ) (s : ℝ) : ℝ := ∑ i ∈ range n, d (x i) (x (i + 1)) ^ s

variable {d}

theorem chain_le (hm : PriceMetric d) (x : ℕ → α) (n : ℕ) :
    d (x 0) (x n) ≤ ∑ i ∈ range n, d (x i) (x (i + 1)) := by
  induction n with
  | zero => simp [hm.refl]
  | succ n ih =>
    rw [sum_range_succ]
    have := hm.tri (x 0) (x n) (x (n + 1))
    linarith

theorem path_cost_ge (hm : PriceMetric d) (s : ℝ) (hs0 : 0 ≤ s) (hs1 : s ≤ 1) (x : ℕ → α) (n : ℕ)
    (hn : 1 ≤ n) (v : ℝ) (hv0 : 0 ≤ v) (hv : v ≤ d (x 0) (x n)) : v ^ s ≤ pcost d x n s := by
  have h1 : v ≤ ∑ i ∈ range n, d (x i) (x (i + 1)) := le_trans hv (chain_le hm x n)
  have h2 := Real.rpow_le_rpow hv0 h1 hs0
  have h3 := sum_rpow_ge s hs0 hs1 (fun i => d (x i) (x (i + 1))) (fun i => hm.nonneg _ _) n hn
  unfold pcost; linarith

theorem pcost_nonneg (hm : PriceMetric d) (s : ℝ) (x : ℕ → α) (n : ℕ) : 0 ≤ pcost d x n s :=
  sum_nonneg (fun i _ => Real.rpow_nonneg (hm.nonneg _ _) s)

/-- credit of a helper that climbs by c (zero if no climb). -/
noncomputable def gc (s c : ℝ) : ℝ := if c ≤ 0 then 0 else c ^ s

/-- helpers <= 0: climb <= distance of endpoints <= path price, so credit <= cost. -/
theorem helper_net_le (hm : PriceMetric d) (s : ℝ) (hs0 : 0 ≤ s) (hs1 : s ≤ 1) (x : ℕ → α) (n : ℕ)
    (c : ℝ) (hc : c ≤ d (x 0) (x n)) : gc s c ≤ pcost d x n s := by
  unfold gc
  split_ifs with h
  · exact pcost_nonneg hm s x n
  · push_neg at h
    have hn : 1 ≤ n := by
      by_contra hn
      have : n = 0 := by omega
      subst this
      simp [hm.refl] at hc; linarith
    exact path_cost_ge hm s hs0 hs1 x n hn c h.le hc

/-- each main (>= 1 move, endpoints at distance >= 8) costs >= 8^s. -/
theorem main_cost_ge (hm : PriceMetric d) (s : ℝ) (hs0 : 0 ≤ s) (hs1 : s ≤ 1) (x : ℕ → α) (n : ℕ)
    (hn : 1 ≤ n) (h8 : 8 ≤ d (x 0) (x n)) : (8:ℝ) ^ s ≤ pcost d x n s :=
  path_cost_ge hm s hs0 hs1 x n hn 8 (by norm_num) h8

end Metric

section Word
variable {α : Type*} (d : α → α → ℝ) {ι μ : Type*}

/-- THE INVOICE of a word (per Theorem K; L = 17 caller calls):
helpers i in H (climb hc i, path hx i of length hn i), mains j in M (path mx j of length mn j),
owned moves k < no (price d (oa k) (ob k)), nst stops each of net cost cstop. -/
noncomputable def FW (s : ℝ) (H : Finset ι) (hc : ι → ℝ) (hn : ι → ℕ) (hx : ι → ℕ → α)
    (M : Finset μ) (mn : μ → ℕ) (mx : μ → ℕ → α)
    (no : ℕ) (oa ob : ℕ → α) (nst : ℝ) : ℝ :=
  Dc s + 17 * (∑ i ∈ H, gc s (hc i) - ∑ i ∈ H, pcost d (hx i) (hn i) s
    - ∑ j ∈ M, pcost d (mx j) (mn j) s - ∑ k ∈ range no, d (oa k) (ob k) ^ s - nst * cstop s)

variable {d}
variable (hm : PriceMetric d) (s : ℝ) (hs0 : 0 ≤ s) (hs1 : s ≤ 1)
  (H : Finset ι) (hc : ι → ℝ) (hn : ι → ℕ) (hx : ι → ℕ → α)
  (M : Finset μ) (mn : μ → ℕ) (mx : μ → ℕ → α)
  (no : ℕ) (oa ob : ℕ → α) (nst : ℝ)
  (hH : ∀ i ∈ H, hc i ≤ d (hx i 0) (hx i (hn i)))
  (hM : ∀ j ∈ M, 1 ≤ mn j ∧ 8 ≤ d (mx j 0) (mx j (mn j)))
  (hM400 : M.card = 400) (hnst : 0 ≤ nst)

include hm hs0 hs1 hH hM hM400 hnst in
/-- P0: FW <= Dc - 17*400*8^s.  Uses only SPEC pricing (metric), the 400 mains, owned >= 0, stops >= 0. -/
theorem P0_ceiling :
    FW d s H hc hn hx M mn mx no oa ob nst ≤ Dc s - 17 * (400 * 8 ^ s) := by
  have h1 : ∑ i ∈ H, gc s (hc i) ≤ ∑ i ∈ H, pcost d (hx i) (hn i) s :=
    sum_le_sum (fun i hi => helper_net_le hm s hs0 hs1 _ _ _ (hH i hi))
  have h2 : ∑ _j ∈ M, (8:ℝ) ^ s ≤ ∑ j ∈ M, pcost d (mx j) (mn j) s :=
    sum_le_sum (fun j hj => main_cost_ge hm s hs0 hs1 _ _ (hM j hj).1 (hM j hj).2)
  rw [sum_const, hM400] at h2
  simp only [nsmul_eq_mul] at h2
  have h3 : 0 ≤ ∑ k ∈ range no, d (oa k) (ob k) ^ s :=
    sum_nonneg (fun k _ => Real.rpow_nonneg (hm.nonneg _ _) s)
  have h4 : 0 ≤ nst * cstop s := mul_nonneg hnst (cstop_nonneg s hs0 hs1)
  unfold FW
  push_cast at h2
  nlinarith

include hm hs0 hs1 hH hM hM400 hnst in
/-- U0: >= 16 owned moves of price >= 1, stops >= 104 - no. -/
theorem U0_ceiling (hO1 : ∀ k < no, 1 ≤ d (oa k) (ob k)) (h16 : 16 ≤ no)
    (hR3 : 104 - (no : ℝ) ≤ nst) :
    FW d s H hc hn hx M mn mx no oa ob nst ≤ Dc s - 17 * (400 * 8 ^ s + 16 + 88 * cstop s) := by
  have h1 : ∑ i ∈ H, gc s (hc i) ≤ ∑ i ∈ H, pcost d (hx i) (hn i) s :=
    sum_le_sum (fun i hi => helper_net_le hm s hs0 hs1 _ _ _ (hH i hi))
  have h2 : ∑ _j ∈ M, (8:ℝ) ^ s ≤ ∑ j ∈ M, pcost d (mx j) (mn j) s :=
    sum_le_sum (fun j hj => main_cost_ge hm s hs0 hs1 _ _ (hM j hj).1 (hM j hj).2)
  rw [sum_const, hM400] at h2
  simp only [nsmul_eq_mul] at h2
  push_cast at h2
  have h3 : ∑ _k ∈ range no, (1:ℝ) ≤ ∑ k ∈ range no, d (oa k) (ob k) ^ s :=
    sum_le_sum (fun k hk => Real.one_le_rpow (hO1 k (mem_range.1 hk)) hs0)
  simp only [sum_const, card_range, nsmul_eq_mul, mul_one] at h3
  have hc0 := cstop_nonneg s hs0 hs1
  have hc1 := cstop_le_one s hs0
  have h16' : (16:ℝ) ≤ no := by exact_mod_cast h16
  have h5 : (104 - (no:ℝ)) * cstop s ≤ nst * cstop s := mul_le_mul_of_nonneg_right hR3 hc0
  have h6 : (no:ℝ) * (1 - cstop s) ≥ 16 * (1 - cstop s) :=
    mul_le_mul_of_nonneg_right h16' (by linarith)
  unfold FW
  nlinarith

end Word

/-- THE CROSSING STEP.  Cert: the ceiling invoice is negative on [kbar,1] (s = 1 - t). -/
def Cert (Fceil : ℝ → ℝ) (kbar : ℝ) : Prop := ∀ t, kbar ≤ t → t ≤ 1 → Fceil (1 - t) < 0

/-- any crossing kappa in (0,1] (F >= 0 there, F = 0 at the crossing) lies below kbar. -/
theorem kappa_lt (FWt Fceil : ℝ → ℝ) (kbar : ℝ)
    (hle : ∀ t, 0 ≤ t → t ≤ 1 → FWt t ≤ Fceil (1 - t)) (hc : Cert Fceil kbar)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ ≤ 1) (hF : 0 ≤ FWt κ) : κ < kbar := by
  by_contra h
  push_neg at h
  have := hle κ hκ0.le hκ1
  have := hc κ h hκ1
  linarith

noncomputable def FceilP0 (s : ℝ) : ℝ := Dc s - 17 * (400 * 8 ^ s)
noncomputable def FceilU0 (s : ℝ) : ℝ := Dc s - 17 * (400 * 8 ^ s + 16 + 88 * cstop s)

/-- NAMED HYPOTHESES: real-number certificates (ladder.log / ma.log, interval cover, Decimal prec 60).
Numerically: FceilP0 < 0 on [.0227043,1] and FceilU0 < 0 on [.0204111,1] (checked in floats; not in Lean). -/
def CertP0 : Prop := Cert FceilP0 (227043 / 10000000)
def CertU0 : Prop := Cert FceilU0 (204111 / 10000000)

end SafeRungsPrice
