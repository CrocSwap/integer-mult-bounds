/-
B-FORM PER-SPLIT OPTIMALITY .  Formalises CALLERFLOOR R2 sec 1 (L1-L4) for B ports, pointwise in s = 1 - t in [0,1].
Kernel only: no sorry, no native_decide.  See BFormOpt.md for the model, the statements, and the corrections.
-/
import Nov15.JointCeiling
import Mathlib.Analysis.Convex.SpecificFunctions.Pow
import Mathlib.Analysis.MeanInequalitiesPow
open Finset

namespace BFormOpt
open JointCeiling CallerCost

/-! ### 0. concavity toolkit (phi(l) = (8l)^s, tau(d) = (8d+1)^s, psi = tau - phi) -/

/-- two-point Karamata for x^s: (x, y+d) is more spread than (x+d, y) when x <= y. -/
lemma spread {s : ℝ} (hs0 : 0 ≤ s) (hs1 : s ≤ 1) {x y d : ℝ} (hx : 0 ≤ x) (hxy : x ≤ y) (hd : 0 ≤ d) :
    x ^ s + (y + d) ^ s ≤ (x + d) ^ s + y ^ s := by
  rcases eq_or_lt_of_le hxy with h | h
  · subst h; linarith
  have hc := Real.concaveOn_rpow hs0 hs1
  have hL : 0 < y + d - x := by linarith
  have hy' : (0:ℝ) ≤ y + d := by linarith
  have hab : (y - x) / (y + d - x) + d / (y + d - x) = 1 := by
    rw [← add_div, div_eq_one_iff_eq hL.ne']; ring
  have hab' : d / (y + d - x) + (y - x) / (y + d - x) = 1 := by linarith
  have h1 := hc.2 (Set.mem_Ici.2 hx) (Set.mem_Ici.2 hy') (div_nonneg (by linarith) hL.le) (div_nonneg hd hL.le) hab
  have h2 := hc.2 (Set.mem_Ici.2 hx) (Set.mem_Ici.2 hy') (div_nonneg hd hL.le) (div_nonneg (by linarith) hL.le) hab'
  simp only [smul_eq_mul] at h1 h2
  have e1 : (y - x) / (y + d - x) * x + d / (y + d - x) * (y + d) = x + d := by
    field_simp; ring
  have e2 : d / (y + d - x) * x + (y - x) / (y + d - x) * (y + d) = y := by
    field_simp; ring
  rw [e1] at h1; rw [e2] at h2
  have k1 : (y - x) / (y + d - x) * x ^ s + d / (y + d - x) * x ^ s = x ^ s := by
    rw [← add_mul, hab, one_mul]
  have k2 : d / (y + d - x) * (y + d) ^ s + (y - x) / (y + d - x) * (y + d) ^ s = (y + d) ^ s := by
    rw [← add_mul, hab', one_mul]
  linarith [h1, h2]

/-- phi' : line cost, phi'(0) = 0 (so s = 0 counts lines) -/
noncomputable def ph (s : ℝ) (l : ℕ) : ℝ := if l = 0 then 0 else ((8 * l : ℕ) : ℝ) ^ s
noncomputable def ta (s : ℝ) (d : ℕ) : ℝ := ((8 * d + 1 : ℕ) : ℝ) ^ s
noncomputable def ps (s : ℝ) (d : ℕ) : ℝ := ta s d - ph s d

lemma ph_zero (s : ℝ) : ph s 0 = 0 := by simp [ph]
lemma ph_pos' (s : ℝ) {l : ℕ} (h : 1 ≤ l) : ph s l = ((8 * l : ℕ) : ℝ) ^ s := by
  unfold ph; rw [if_neg (by omega)]

/-- increments of phi' -/
noncomputable def dl (s : ℝ) (j : ℕ) : ℝ := ph s (j + 1) - ph s j

lemma dl_nonneg {s : ℝ} (hs0 : 0 ≤ s) (j : ℕ) : 0 ≤ dl s j := by
  unfold dl
  rcases Nat.eq_zero_or_pos j with rfl | hj
  · rw [ph_zero, ph_pos' s (by omega)]; simp only [sub_zero]; positivity
  · rw [ph_pos' s (by omega), ph_pos' s (by omega)]
    have : ((8 * j : ℕ) : ℝ) ≤ ((8 * (j + 1) : ℕ) : ℝ) := by exact_mod_cast (by omega)
    have := Real.rpow_le_rpow (by positivity) this hs0
    linarith

lemma dl_anti {s : ℝ} (hs0 : 0 ≤ s) (hs1 : s ≤ 1) (j : ℕ) : dl s (j + 1) ≤ dl s j := by
  unfold dl
  rcases Nat.eq_zero_or_pos j with rfl | hj
  · rw [ph_zero, ph_pos' s (by omega), ph_pos' s (by omega)]
    have h := Real.rpow_add_le_add_rpow (a := 8) (b := 8) (by norm_num) (by norm_num) hs0 hs1
    norm_num at h ⊢
    linarith
  · rw [ph_pos' s (by omega), ph_pos' s (by omega), ph_pos' s (by omega)]
    have := spread hs0 hs1 (x := ((8 * j : ℕ) : ℝ)) (y := ((8 * (j + 1) : ℕ) : ℝ)) (d := 8) (by positivity)
      (by exact_mod_cast (by omega)) (by norm_num)
    have e1 : ((8 * j : ℕ) : ℝ) + 8 = ((8 * (j + 1) : ℕ) : ℝ) := by push_cast; ring
    have e2 : ((8 * (j + 1) : ℕ) : ℝ) + 8 = ((8 * (j + 1 + 1) : ℕ) : ℝ) := by push_cast; ring
    rw [e1, e2] at this
    linarith

lemma ps_anti {s : ℝ} (hs0 : 0 ≤ s) (hs1 : s ≤ 1) {d : ℕ} (hd : 1 ≤ d) : ps s (d + 1) ≤ ps s d := by
  unfold ps ta
  rw [ph_pos' s (by omega), ph_pos' s hd]
  have := spread hs0 hs1 (x := ((8 * d : ℕ) : ℝ)) (y := ((8 * (d + 1) : ℕ) : ℝ)) (d := 1) (by positivity)
    (by exact_mod_cast (by omega)) (by norm_num)
  have e1 : ((8 * d : ℕ) : ℝ) + 1 = ((8 * d + 1 : ℕ) : ℝ) := by push_cast; ring
  have e2 : ((8 * (d + 1) : ℕ) : ℝ) + 1 = ((8 * (d + 1) + 1 : ℕ) : ℝ) := by push_cast; ring
  rw [e1, e2] at this
  linarith

lemma ps_le_one {s : ℝ} (hs0 : 0 ≤ s) (hs1 : s ≤ 1) {d : ℕ} (hd : 1 ≤ d) : ps s d ≤ ps s 1 := by
  induction d, hd using Nat.le_induction with
  | base => exact le_rfl
  | succ d hd ih => exact (ps_anti hs0 hs1 hd).trans ih

/-- ps is antitone on [1, oo) -/
lemma ps_antitone {s : ℝ} (hs0 : 0 ≤ s) (hs1 : s ≤ 1) {d d' : ℕ} (hd : 1 ≤ d) (h : d ≤ d') : ps s d' ≤ ps s d := by
  induction d', h using Nat.le_induction with
  | base => exact le_rfl
  | succ d' hd' ih => exact (ps_anti hs0 hs1 (by omega)).trans ih

/-! ### 1. Abel summation (the Karamata engine) -/

/-- if a is nonincreasing (up to index m) and all partial sums of D up to m are >= 0 then sum_{i<m} a_i D_i >= a_m * sum_{i<m} D_i >= ... -/
lemma abel_aux (a D : ℕ → ℝ) (m : ℕ) (ha : ∀ i, i < m → a (i + 1) ≤ a i)
    (hS : ∀ J, J ≤ m → 0 ≤ ∑ i ∈ range J, D i) :
    a m * (∑ i ∈ range m, D i) ≤ ∑ i ∈ range m, a i * D i := by
  induction m with
  | zero => simp
  | succ m ih =>
    have ih' := ih (fun i hi => ha i (by omega)) (fun J hJ => hS J (by omega))
    have hSm1 := hS (m + 1) le_rfl
    have hSm := hS m (by omega)
    have h1 := ha m (by omega)
    rw [Finset.sum_range_succ] at hSm1 ⊢
    rw [Finset.sum_range_succ]
    nlinarith [mul_le_mul_of_nonneg_right h1 hSm1]

lemma abel_nonneg (a D : ℕ → ℝ) (m : ℕ) (ha : ∀ i, i < m → a (i + 1) ≤ a i) (ha0 : 0 ≤ a m)
    (hS : ∀ J, J ≤ m → 0 ≤ ∑ i ∈ range J, D i) : 0 ≤ ∑ i ∈ range m, a i * D i := by
  have := abel_aux a D m ha hS
  have := mul_nonneg ha0 (hS m le_rfl)
  linarith

/-! ### 2. schedules and the line-bill lower bound (L1, pointwise in s, ALL arm lengths)
 A schedule of an arm of length x is a list of lines (start stage, length): a line is one role's idle interval.
 Feasibility = exact occupancy n_c at every stage and at most cap_c lines across boundary c|c+1.
 We prove: every feasible schedule has bill sum phi(len) >= CB (a closed form of n, cap only), for every s in [0,1]. -/
abbrev Line := ℕ × ℕ

def covN (σ : List Line) (c : ℕ) : ℕ := (σ.map fun p => if p.1 ≤ c ∧ c < p.1 + p.2 then 1 else 0).sum
def crossN (σ : List Line) (c : ℕ) : ℕ := (σ.map fun p => if p.1 ≤ c ∧ c + 1 < p.1 + p.2 then 1 else 0).sum
def Valid (x : ℕ) (σ : List Line) : Prop := ∀ p ∈ σ, 1 ≤ p.2 ∧ p.1 + p.2 ≤ x
noncomputable def bill (s : ℝ) (σ : List Line) : ℝ := (σ.map fun p => ph s p.2).sum

lemma list_swap {M : Type*} [AddCommMonoid M] (σ : List Line) (m : ℕ) (g : Line → ℕ → M) :
    (σ.map fun p => ∑ k ∈ range m, g p k).sum = ∑ k ∈ range m, (σ.map fun p => g p k).sum := by
  induction σ with
  | nil => simp
  | cons p σ ih => simp only [List.map_cons, List.sum_cons, ih, Finset.sum_add_distrib]

lemma len_eq {x : ℕ} {p : Line} (h : p.1 + p.2 ≤ x) :
    p.2 = ∑ c ∈ range x, if p.1 ≤ c ∧ c < p.1 + p.2 then 1 else 0 := by
  rw [Finset.sum_boole]
  have : (range x).filter (fun c => p.1 ≤ c ∧ c < p.1 + p.2) = Ico p.1 (p.1 + p.2) := by
    ext c; simp only [Finset.mem_filter, Finset.mem_range, Finset.mem_Ico]; omega
  rw [this]; simp

lemma sum_len_eq {x : ℕ} {σ : List Line} (hv : Valid x σ) :
    (σ.map fun p => p.2).sum = ∑ c ∈ range x, covN σ c := by
  unfold covN
  rw [← list_swap]
  congr 1
  apply List.map_congr_left
  intro p hp
  exact len_eq (hv p hp).2

lemma min_eq (l J : ℕ) : min l J = ∑ j ∈ range J, if j + 1 ≤ l then 1 else 0 := by
  rw [Finset.sum_boole]
  have : (range J).filter (fun j => j + 1 ≤ l) = range (min l J) := by
    ext c; simp only [Finset.mem_filter, Finset.mem_range]; omega
  rw [this]; simp

lemma excess_le {x J : ℕ} (hJ : 1 ≤ J) {p : Line} (hp : 1 ≤ p.2 ∧ p.1 + p.2 ≤ x) :
    p.2 - min p.2 J ≤ ∑ k ∈ range (x - J), if p.1 ≤ k ∧ k + 1 < p.1 + p.2 then 1 else 0 := by
  rw [Finset.sum_boole]
  have hsub : Ico p.1 (p.1 + p.2 - J) ⊆ (range (x - J)).filter (fun k => p.1 ≤ k ∧ k + 1 < p.1 + p.2) := by
    intro k hk
    simp only [Finset.mem_Ico, Finset.mem_filter, Finset.mem_range] at hk ⊢
    omega
  have := Finset.card_le_card hsub
  simp only [Nat.card_Ico] at this
  have h2 : p.2 - min p.2 J = p.1 + p.2 - J - p.1 := by omega
  rw [h2]; exact_mod_cast this

lemma ph_layer {s : ℝ} {x l : ℕ} (h : l ≤ x) :
    ph s l = ∑ j ∈ range x, dl s j * (if j + 1 ≤ l then 1 else 0) := by
  obtain ⟨r, rfl⟩ : ∃ r, x = l + r := ⟨x - l, by omega⟩
  rw [Finset.sum_range_add]
  have h1 : ∑ j ∈ range l, dl s j * (if j + 1 ≤ l then (1:ℝ) else 0) = ∑ j ∈ range l, dl s j := by
    apply Finset.sum_congr rfl
    intro j hj; rw [Finset.mem_range] at hj; simp [show j + 1 ≤ l by omega]
  have h2 : ∑ j ∈ range r, dl s (l + j) * (if l + j + 1 ≤ l then (1:ℝ) else 0) = 0 := by
    apply Finset.sum_eq_zero
    intro j _; simp
  rw [h1, h2, add_zero]
  have := Finset.sum_range_sub (fun j => ph s j) l
  simp only [dl]; rw [this, ph_zero, sub_zero]

/-- the closed form lower bound: W_0 = (sum n) - (sum_{k < x-1} cap), W_j = cap (x-1-j) (j >= 1) -/
noncomputable def Wt (x : ℕ) (n cap : ℕ → ℕ) (j : ℕ) : ℝ :=
  if j = 0 then (∑ c ∈ range x, (n c : ℝ)) - ∑ k ∈ range (x - 1), (cap k : ℝ) else (cap (x - 1 - j) : ℝ)
noncomputable def CB (s : ℝ) (x : ℕ) (n cap : ℕ → ℕ) : ℝ := ∑ j ∈ range x, dl s j * Wt x n cap j

lemma Wt_partial {x : ℕ} (n cap : ℕ → ℕ) {J : ℕ} (h1 : 1 ≤ J) (h2 : J ≤ x) :
    ∑ i ∈ range J, Wt x n cap i = (∑ c ∈ range x, (n c : ℝ)) - ∑ k ∈ range (x - J), (cap k : ℝ) := by
  induction J, h1 using Nat.le_induction with
  | base => simp [Wt]
  | succ J hJ ih =>
    rw [Finset.sum_range_succ, ih (by omega)]
    have : x - J = (x - (J + 1)) + 1 := by omega
    rw [this, Finset.sum_range_succ]
    have e : x - (J + 1) = x - 1 - J := by omega
    simp only [Wt, if_neg (show J ≠ 0 by omega), e]
    ring

/-- partial-sum domination: sum n <= (sum of min(len,J)) + sum_{k<x-J} cap -/
lemma partial_dom {x : ℕ} {σ : List Line} (hv : Valid x σ) (n cap : ℕ → ℕ)
    (hcov : ∀ c, c < x → covN σ c = n c) (hcross : ∀ c, c + 1 < x → crossN σ c ≤ cap c)
    {J : ℕ} (hJ : 1 ≤ J) :
    ∑ c ∈ range x, n c ≤ (σ.map fun p => min p.2 J).sum + ∑ k ∈ range (x - J), cap k := by
  have h1 : ∑ c ∈ range x, n c = (σ.map fun p => p.2).sum := by
    rw [sum_len_eq hv]; apply Finset.sum_congr rfl; intro c hc; rw [hcov c (Finset.mem_range.1 hc)]
  have h2 : (σ.map fun p => p.2).sum = (σ.map fun p => min p.2 J).sum + (σ.map fun p => p.2 - min p.2 J).sum := by
    rw [← List.sum_map_add]; congr 1; apply List.map_congr_left; intro p _; omega
  have h3 : (σ.map fun p => p.2 - min p.2 J).sum ≤
      (σ.map fun p => ∑ k ∈ range (x - J), if p.1 ≤ k ∧ k + 1 < p.1 + p.2 then 1 else 0).sum := by
    apply List.sum_le_sum; intro p hp; exact excess_le hJ (hv p hp)
  rw [list_swap] at h3
  have h4 : ∑ k ∈ range (x - J), crossN σ k ≤ ∑ k ∈ range (x - J), cap k := by
    apply Finset.sum_le_sum; intro k hk; rw [Finset.mem_range] at hk; exact hcross k (by omega)
  have h5 : ∑ k ∈ range (x - J), crossN σ k = ∑ k ∈ range (x - J), (σ.map fun p => if p.1 ≤ k ∧ k + 1 < p.1 + p.2 then 1 else 0).sum := rfl
  omega

/-- L1 (schedule lemma, pointwise in s): every feasible schedule pays at least CB. -/
theorem bill_lb {s : ℝ} (hs0 : 0 ≤ s) (hs1 : s ≤ 1) {x : ℕ} {σ : List Line} (hv : Valid x σ) (n cap : ℕ → ℕ)
    (hcov : ∀ c, c < x → covN σ c = n c) (hcross : ∀ c, c + 1 < x → crossN σ c ≤ cap c) :
    CB s x n cap ≤ bill s σ := by
  -- N j = number of lines of length >= j+1
  let N : ℕ → ℕ := fun j => (σ.map fun p => if j + 1 ≤ p.2 then 1 else 0).sum
  have hbill : bill s σ = ∑ j ∈ range x, dl s j * (N j : ℝ) := by
    unfold bill
    have : ∀ p ∈ σ, ph s p.2 = ∑ j ∈ range x, dl s j * (if j + 1 ≤ p.2 then (1:ℝ) else 0) :=
      fun p hp => ph_layer (by have := hv p hp; omega)
    rw [List.map_congr_left this, list_swap]
    apply Finset.sum_congr rfl; intro j _
    simp only [N]
    rw [Nat.cast_list_sum, ← List.sum_map_mul_left]
    congr 1
    rw [List.map_map]; apply List.map_congr_left; intro p _; simp only [Function.comp]; split_ifs <;> simp
  have hpart : ∀ J, ∑ i ∈ range J, N i = (σ.map fun p => min p.2 J).sum := by
    intro J
    simp only [N]
    rw [← list_swap]; congr 1; apply List.map_congr_left; intro p _; exact (min_eq _ _).symm
  have key : 0 ≤ ∑ j ∈ range x, dl s j * ((N j : ℝ) - Wt x n cap j) := by
    apply abel_nonneg (fun j => dl s j) (fun j => (N j : ℝ) - Wt x n cap j) x
    · intro i _; exact dl_anti hs0 hs1 i
    · exact dl_nonneg hs0 x
    · intro J hJ
      rcases Nat.eq_zero_or_pos J with rfl | hJ1
      · simp
      · have hp : ∑ i ∈ range J, (N i : ℝ) = (((σ.map fun p => min p.2 J).sum : ℕ) : ℝ) := by
          rw [← Nat.cast_sum, hpart J]
        rw [Finset.sum_sub_distrib, Wt_partial n cap hJ1 hJ, hp]
        have := partial_dom hv n cap hcov hcross hJ1
        have : (∑ c ∈ range x, (n c : ℝ)) ≤ ((σ.map fun p => min p.2 J).sum : ℕ) + ∑ k ∈ range (x - J), (cap k : ℝ) := by
          exact_mod_cast this
        push_cast at this ⊢
        linarith
  rw [hbill]; unfold CB
  simp only [mul_sub, Finset.sum_sub_distrib] at key
  linarith

/-! ### 3. B-port layouts: closed form of the bill bound, the own-role Abel step, the hub step -/
def Ecum (e : ℕ → ℕ) (c : ℕ) : ℕ := ∑ i ∈ range (c + 1), e i
/-- occupancy and boundary cap of a B port (m = 2 mains): n_c = h + E_c - 2, cap_c = h + E_c - 4 (Crossing Lemma) -/
def occ (h : ℕ) (e : ℕ → ℕ) (c : ℕ) : ℕ := h + Ecum e c - 2
def capc (h : ℕ) (e : ℕ → ℕ) (c : ℕ) : ℕ := h + Ecum e c - 4

lemma sum_dl (s : ℝ) (m : ℕ) : ∑ j ∈ range m, dl s j = ph s m := by
  have := Finset.sum_range_sub (fun j => ph s j) m
  simp only [dl]; rw [this, ph_zero, sub_zero]

/-- CB for a B arm in closed form: (h-4) phi(x) + 2x phi(1) + sum_c e_c phi(x-c) (all x >= 1, arms of 1 included) -/
theorem CB_closed (s : ℝ) {y h : ℕ} (hh : 2 ≤ h) (e : ℕ → ℕ)
    (hfl : ∀ j, j + 2 ≤ y + 1 → 2 * (j + 1) ≤ Ecum e j) :
    CB s (y + 1) (occ h e) (capc h e) =
      ((h : ℝ) - 4) * ph s (y + 1) + 2 * ((y + 1 : ℕ) : ℝ) * ph s 1 + ∑ c ∈ range (y + 1), (e c : ℝ) * ph s (y + 1 - c) := by
  set q : ℕ → ℝ := fun k => (h : ℝ) + (Ecum e k : ℝ) - 4 with hq
  have hocc : ∀ c, ((occ h e c : ℕ) : ℝ) = q c + 2 := by
    intro c; simp only [occ, hq]; rw [Nat.cast_sub (by omega)]; push_cast; ring
  have hcap : ∀ k, k + 2 ≤ y + 1 → ((capc h e k : ℕ) : ℝ) = q k := by
    intro k hk; have := hfl k hk; simp only [capc, hq]; rw [Nat.cast_sub (by omega)]; push_cast; ring
  have hW0 : Wt (y + 1) (occ h e) (capc h e) 0 = q y + 2 * ((y + 1 : ℕ) : ℝ) := by
    simp only [Wt, if_true, Nat.add_sub_cancel, hocc]
    rw [Finset.sum_add_distrib, Finset.sum_range_succ]
    have : ∑ k ∈ range y, ((capc h e k : ℕ) : ℝ) = ∑ k ∈ range y, q k := by
      apply Finset.sum_congr rfl; intro k hk; rw [Finset.mem_range] at hk; exact hcap k (by omega)
    rw [this]; simp; ring
  have hWj : ∀ j, j < y → Wt (y + 1) (occ h e) (capc h e) (j + 1) = q (y - (j + 1)) := by
    intro j hj
    simp only [Wt, if_neg (Nat.succ_ne_zero j), Nat.add_sub_cancel]
    rw [hcap _ (by omega)]
  have hsum : ∑ j ∈ range (y + 1), dl s j * q (y - j) =
      ((h : ℝ) - 4) * ph s (y + 1) + ∑ c ∈ range (y + 1), (e c : ℝ) * ph s (y + 1 - c) := by
    have h1 : ∀ j ∈ range (y + 1), dl s j * q (y - j) = dl s j * ((h : ℝ) - 4) + ∑ c ∈ range (y + 1 - j), dl s j * (e c : ℝ) := by
      intro j hj
      rw [Finset.mem_range] at hj
      simp only [hq, Ecum]
      have : y - j + 1 = y + 1 - j := by omega
      rw [this, ← Finset.mul_sum]; push_cast; ring
    rw [Finset.sum_congr rfl h1, Finset.sum_add_distrib, ← Finset.sum_mul, sum_dl, mul_comm]
    congr 1
    rw [Finset.sum_comm' (t' := range (y + 1)) (s' := fun c => range (y + 1 - c))
      (by intro j c; simp only [Finset.mem_range]; omega)]
    apply Finset.sum_congr rfl; intro c hc
    rw [← Finset.sum_mul, sum_dl, mul_comm]
  unfold CB
  rw [Finset.sum_range_succ']
  have h2 : ∀ j ∈ range y, dl s (j + 1) * Wt (y + 1) (occ h e) (capc h e) (j + 1) = dl s (j + 1) * q (y - (j + 1)) := by
    intro j hj; rw [hWj j (Finset.mem_range.1 hj)]
  rw [Finset.sum_congr rfl h2, hW0]
  rw [Finset.sum_range_succ'] at hsum
  have h3 : dl s 0 = ph s 1 := by simp [dl, ph_zero]
  simp only [Nat.sub_zero] at hsum
  rw [h3] at hsum ⊢
  push_cast
  linear_combination hsum

/-- own-role Abel step: sum_c (e_c - 2) (psi(1) - psi(x-c)) >= 0 given the Floor lemma E_j >= 2(j+1), j <= x-2 -/
theorem own_abel {s : ℝ} (hs0 : 0 ≤ s) (hs1 : s ≤ 1) {y : ℕ} (e : ℕ → ℕ)
    (hfl : ∀ j, j + 2 ≤ y + 1 → 2 * (j + 1) ≤ Ecum e j) :
    0 ≤ ∑ c ∈ range (y + 1), ((e c : ℝ) - 2) * (ps s 1 - ps s (y + 1 - c)) := by
  rw [Finset.sum_range_succ]
  have hz : ps s 1 - ps s (y + 1 - y) = 0 := by simp
  rw [hz, mul_zero, add_zero]
  have key := abel_nonneg (fun c => ps s 1 - ps s (y + 1 - c)) (fun c => (e c : ℝ) - 2) y
    (by
      intro i hi
      have := ps_anti hs0 hs1 (d := y - i) (by omega)
      have e1 : y - i + 1 = y + 1 - i := by omega
      have e2 : y - i = y + 1 - (i + 1) := by omega
      rw [e1] at this; rw [← e2]; linarith)
    (by simp)
    (by
      intro J hJ
      rcases Nat.eq_zero_or_pos J with rfl | hJ1
      · simp
      · have := hfl (J - 1) (by omega)
        have eJ : J - 1 + 1 = J := by omega
        simp only [Ecum, eJ] at this
        rw [Finset.sum_sub_distrib]
        simp only [Finset.sum_const, Finset.card_range, nsmul_eq_mul]
        have : (2 * J : ℝ) ≤ ((∑ i ∈ range J, e i : ℕ) : ℝ) := by
          have : 2 * J ≤ ∑ i ∈ range J, e i := by nlinarith
          exact_mod_cast this
        push_cast at this
        linarith)
  exact le_of_le_of_eq key (Finset.sum_congr rfl (fun c _ => mul_comm _ _))

/-- hub step: tau(k) - phi(a) - phi(b) - psi(1) <= 0 (subadditivity of x^s and one two-point Karamata) -/
theorem hub_nonpos {s : ℝ} (hs0 : 0 ≤ s) (hs1 : s ≤ 1) {a b : ℕ} (ha : 1 ≤ a) (hb : 1 ≤ b) :
    ta s (a + b) - ph s a - ph s b - ps s 1 ≤ 0 := by
  unfold ps ta
  rw [ph_pos' s ha, ph_pos' s hb, ph_pos' s (le_refl 1)]
  have h1 := Real.rpow_add_le_add_rpow (a := ((8 * a : ℕ) : ℝ)) (b := ((8 * b : ℕ) : ℝ)) (by positivity) (by positivity) hs0 hs1
  have e1 : ((8 * a : ℕ) : ℝ) + ((8 * b : ℕ) : ℝ) = ((8 * (a + b) : ℕ) : ℝ) := by push_cast; ring
  rw [e1] at h1
  have h2 := spread hs0 hs1 (x := ((8 * 1 : ℕ) : ℝ)) (y := ((8 * (a + b) : ℕ) : ℝ)) (d := 1) (by positivity)
    (by exact_mod_cast (by omega)) (by norm_num)
  have e2 : ((8 * (a + b) : ℕ) : ℝ) + 1 = ((8 * (a + b) + 1 : ℕ) : ℝ) := by push_cast; ring
  have e3 : ((8 * 1 : ℕ) : ℝ) + 1 = ((8 * 1 + 1 : ℕ) : ℝ) := by push_cast; ring
  rw [e2, e3] at h2
  linarith

/-! ### 4. the B port: model, value, per-split optimality -/
noncomputable def Hc (s : ℝ) (a b : ℕ) : ℝ := ta s (a + b) - ph s a - ph s b - ps s 1
noncomputable def Kc (s : ℝ) (a b : ℕ) : ℝ :=
  4 * (ph s a + ph s b) - 2 * ((a + b : ℕ) : ℝ) * ph s 1 - (2 - 2 * ((a + b : ℕ) : ℝ)) * ps s 1
/-- own-role part of the R2 L4 form: sum_c e_c (psi(x-c) - psi(1)) -/
noncomputable def Own (s : ℝ) (x : ℕ) (e : ℕ → ℕ) : ℝ := ∑ c ∈ range x, (e c : ℝ) * (ps s (x - c) - ps s 1)
/-- R2 L4: F_B-port = h Hc + Kc + Own_L + Own_R  (psi(1) unit cost) -/
noncomputable def G4 (s : ℝ) (a b h : ℕ) (eL eR : ℕ → ℕ) : ℝ := (h : ℝ) * Hc s a b + Kc s a b + Own s a eL + Own s b eR
/-- the B form: h = 2 hubs, e = 2 own roles per stage -/
noncomputable def Gstar (s : ℝ) (a b : ℕ) : ℝ := G4 s a b 2 (fun _ => 2) (fun _ => 2)

/-- a B port layout with a feasible line schedule per arm (hubs h, own roles e_c entering at arm stage c) -/
structure BPort (a b : ℕ) where
  h : ℕ
  eL : ℕ → ℕ
  eR : ℕ → ℕ
  σL : List Line
  σR : List Line
  hh : 2 ≤ h
  flL : ∀ j, j + 2 ≤ a → 2 * (j + 1) ≤ Ecum eL j       -- Floor lemma, left arm
  flR : ∀ j, j + 2 ≤ b → 2 * (j + 1) ≤ Ecum eR j
  vL : Valid a σL
  vR : Valid b σR
  covL : ∀ c, c < a → covN σL c = occ h eL c
  covR : ∀ c, c < b → covN σR c = occ h eR c
  crL : ∀ c, c + 1 < a → crossN σL c ≤ capc h eL c
  crR : ∀ c, c + 1 < b → crossN σR c ≤ capc h eR c
  /-- sign units u = n + 2 - 2k (n = h + total own roles) -/
  hfeas : 2 * (a + b) ≤ h + (∑ c ∈ range a, eL c) + (∑ c ∈ range b, eR c) + 2
  /-- total price of the sign units (as a function of s) -/
  ucost : ℝ → ℝ
  /-- [H-odd]: each of the u sign units costs at least psi(1) -/
  hodd : ∀ s, 0 ≤ s → s ≤ 1 →
    ((h + (∑ c ∈ range a, eL c) + (∑ c ∈ range b, eR c) + 2 - 2 * (a + b) : ℕ) : ℝ) * ps s 1 ≤ ucost s

/-- the F value of a B port: hub roles + own roles - line bill - sign units, F(s) = sum (T - P) r^s -/
noncomputable def BPort.F {a b : ℕ} (P : BPort a b) (s : ℝ) : ℝ :=
  (P.h : ℝ) * ta s (a + b) + ∑ c ∈ range a, (P.eL c : ℝ) * ta s (a - c) + ∑ c ∈ range b, (P.eR c : ℝ) * ta s (b - c)
    - bill s P.σL - bill s P.σR - P.ucost s

lemma own_split (s : ℝ) (x : ℕ) (e : ℕ → ℕ) :
    ∑ c ∈ range x, (e c : ℝ) * ta s (x - c) - ∑ c ∈ range x, (e c : ℝ) * ph s (x - c) - ps s 1 * ∑ c ∈ range x, (e c : ℝ)
      = Own s x e := by
  unfold Own
  rw [Finset.mul_sum, ← Finset.sum_sub_distrib, ← Finset.sum_sub_distrib]
  apply Finset.sum_congr rfl; intro c _; simp only [ps]; ring

/-- (L1 + L2): every B port has F <= G4 (the R2 closed form), pointwise in s -/
theorem F_le_G4 {a b : ℕ} (ha : 1 ≤ a) (hb : 1 ≤ b) (P : BPort a b) {s : ℝ} (hs0 : 0 ≤ s) (hs1 : s ≤ 1) :
    P.F s ≤ G4 s a b P.h P.eL P.eR := by
  obtain ⟨y, rfl⟩ : ∃ y, a = y + 1 := ⟨a - 1, by omega⟩
  obtain ⟨z, rfl⟩ : ∃ z, b = z + 1 := ⟨b - 1, by omega⟩
  have hL := bill_lb hs0 hs1 P.vL (occ P.h P.eL) (capc P.h P.eL) P.covL P.crL
  have hR := bill_lb hs0 hs1 P.vR (occ P.h P.eR) (capc P.h P.eR) P.covR P.crR
  rw [CB_closed s P.hh P.eL P.flL] at hL
  rw [CB_closed s P.hh P.eR P.flR] at hR
  have hu := P.hodd s hs0 hs1
  have hcast : ((P.h + (∑ c ∈ range (y + 1), P.eL c) + (∑ c ∈ range (z + 1), P.eR c) + 2 - 2 * (y + 1 + (z + 1)) : ℕ) : ℝ)
      = (P.h : ℝ) + (∑ c ∈ range (y + 1), (P.eL c : ℝ)) + (∑ c ∈ range (z + 1), (P.eR c : ℝ)) + 2 - 2 * ((y + 1 + (z + 1) : ℕ) : ℝ) := by
    have := P.hfeas
    rw [Nat.cast_sub this]; push_cast; ring
  rw [hcast] at hu
  have oL := own_split s (y + 1) P.eL
  have oR := own_split s (z + 1) P.eR
  unfold BPort.F G4 Hc Kc
  push_cast at hL hR hu ⊢
  nlinarith [hL, hR, hu, oL, oR]

theorem G4_le_star {a b : ℕ} (ha : 1 ≤ a) (hb : 1 ≤ b) {s : ℝ} (hs0 : 0 ≤ s) (hs1 : s ≤ 1)
    (h : ℕ) (hh : 2 ≤ h) (eL eR : ℕ → ℕ)
    (flL : ∀ j, j + 2 ≤ a → 2 * (j + 1) ≤ Ecum eL j) (flR : ∀ j, j + 2 ≤ b → 2 * (j + 1) ≤ Ecum eR j) :
    G4 s a b h eL eR ≤ Gstar s a b := by
  have hH := hub_nonpos hs0 hs1 ha hb
  have hH' : Hc s a b ≤ 0 := hH
  have key : ∀ (x : ℕ) (e : ℕ → ℕ), 1 ≤ x → (∀ j, j + 2 ≤ x → 2 * (j + 1) ≤ Ecum e j) →
      Own s x e ≤ Own s x (fun _ => 2) := by
    intro x e hx hfl
    obtain ⟨y, rfl⟩ : ∃ y, x = y + 1 := ⟨x - 1, by omega⟩
    have := own_abel hs0 hs1 e hfl
    unfold Own
    have e2 : ∑ c ∈ range (y + 1), (((fun _ => 2 : ℕ → ℕ) c : ℕ) : ℝ) * (ps s (y + 1 - c) - ps s 1)
        = ∑ c ∈ range (y + 1), 2 * (ps s (y + 1 - c) - ps s 1) := by
      apply Finset.sum_congr rfl; intro c _; simp
    rw [e2]
    have e3 : ∑ c ∈ range (y + 1), (e c : ℝ) * (ps s (y + 1 - c) - ps s 1) - ∑ c ∈ range (y + 1), 2 * (ps s (y + 1 - c) - ps s 1)
        = - ∑ c ∈ range (y + 1), ((e c : ℝ) - 2) * (ps s 1 - ps s (y + 1 - c)) := by
      rw [← Finset.sum_sub_distrib, ← Finset.sum_neg_distrib]
      apply Finset.sum_congr rfl; intro c _; ring
    linarith
  have k1 := key a eL ha flL
  have k2 := key b eR hb flR
  unfold Gstar
  unfold G4
  have : ((h : ℝ) - 2) * Hc s a b ≤ 0 := mul_nonpos_of_nonneg_of_nonpos (by
    have : (2 : ℝ) ≤ h := by exact_mod_cast hh
    linarith) hH'
  push_cast
  nlinarith [this, k1, k2]

/-- PER-SPLIT B-FORM OPTIMALITY (B ports, every s in [0,1]): F(layout) <= F(B form) = Gstar. -/
theorem bform_optimal {a b : ℕ} (ha : 1 ≤ a) (hb : 1 ≤ b) (P : BPort a b) {s : ℝ} (hs0 : 0 ≤ s) (hs1 : s ≤ 1) :
    P.F s ≤ Gstar s a b :=
  (F_le_G4 ha hb P hs0 hs1).trans (G4_le_star ha hb hs0 hs1 P.h P.hh P.eL P.eR P.flL P.flR)

/-! ### 5. B form = the closed form FBc used by JointCeiling (bridge), and the discharge of hB -/
noncomputable def Tsum (s : ℝ) (x : ℕ) : ℝ := ∑ c ∈ range x, ta s (x - c)
noncomputable def Psum (s : ℝ) (x : ℕ) : ℝ := ∑ c ∈ range x, ph s (x - c)
noncomputable def Qsum (s : ℝ) (x : ℕ) : ℝ := ∑ J ∈ range (x - 1), ph s (J + 1)

lemma Tsum_eq (s : ℝ) (x : ℕ) : Tsum s x = ∑ i ∈ range x, ((8 * i + 9 : ℕ) : ℝ) ^ s := by
  unfold Tsum
  rw [← Finset.sum_range_reflect]
  apply Finset.sum_congr rfl; intro c hc
  rw [Finset.mem_range] at hc
  have : x - (x - 1 - c) = c + 1 := by omega
  rw [this]; unfold ta
  have h8 : 8 * (c + 1) + 1 = 8 * c + 9 := by ring
  rw [h8]

lemma Psum_eq (s : ℝ) (x : ℕ) : Psum s x = ∑ i ∈ range x, ph s (i + 1) := by
  unfold Psum
  rw [← Finset.sum_range_reflect]
  apply Finset.sum_congr rfl; intro c hc
  rw [Finset.mem_range] at hc
  have : x - (x - 1 - c) = c + 1 := by omega
  rw [this]

lemma Psum_Q (s : ℝ) {x : ℕ} (hx : 1 ≤ x) : Psum s x = Qsum s x + ph s x := by
  rw [Psum_eq]; unfold Qsum
  obtain ⟨y, rfl⟩ : ∃ y, x = y + 1 := ⟨x - 1, by omega⟩
  rw [Finset.sum_range_succ]; simp

lemma Qsum_eq (s : ℝ) {x : ℕ} (hx : 1 ≤ x) :
    Qsum s x = (if 2 ≤ x then (8 : ℝ) ^ s else 0) + ∑ i ∈ range (x - 2), ((8 * i + 16 : ℕ) : ℝ) ^ s := by
  unfold Qsum
  rcases Nat.lt_or_ge x 2 with h | h
  · have : x = 1 := by omega
    subst this; simp
  · obtain ⟨m, rfl⟩ : ∃ m, x = m + 2 := ⟨x - 2, by omega⟩
    have e1 : m + 2 - 1 = m + 1 := by omega
    have e2 : m + 2 - 2 = m := by omega
    rw [e1, e2, Finset.sum_range_succ', if_pos h, add_comm]
    congr 1

lemma Own_two (s : ℝ) (x : ℕ) :
    Own s x (fun _ => 2) = 2 * (Tsum s x - Psum s x) - 2 * (x : ℝ) * ps s 1 := by
  unfold Own Tsum Psum
  have : ∑ c ∈ range x, (((fun _ => 2 : ℕ → ℕ) c : ℕ) : ℝ) * (ps s (x - c) - ps s 1)
      = ∑ c ∈ range x, (2 * (ta s (x - c) - ph s (x - c)) - 2 * ps s 1) := by
    apply Finset.sum_congr rfl; intro c _; simp only [ps]; push_cast; ring
  rw [this, Finset.sum_sub_distrib, ← Finset.mul_sum, Finset.sum_sub_distrib]
  simp; ring

/-- value of an A port in the BUILT type (h = 2, e = 2, m = 4: every line continues to the arm's end; th QUERY units at cost 1) -/
noncomputable def FAport (s : ℝ) (a b th : ℕ) : ℝ :=
  2 * ta s (a + b) + 2 * (Tsum s a + Tsum s b) - 2 * (Qsum s a + Qsum s b) - (th : ℝ)

/-- BRIDGE: 96 A ports (built type) + 8 B ports (B form) = the JointCeiling closed form FBc, for ALL arms >= 1 -/
theorem port_total {a b : ℕ} (ha : 1 ≤ a) (hb : 1 ≤ b) (th : ℕ) (s : ℝ) :
    96 * FAport s a b th + 8 * Gstar s a b = FBc a b th s := by
  have hph1 : ph s 1 = (8 : ℝ) ^ s := by rw [ph_pos' s (le_refl 1)]; norm_num
  have hps1 : ps s 1 = (9 : ℝ) ^ s - (8 : ℝ) ^ s := by
    unfold ps ta; rw [hph1]; norm_num
  have hind : ∀ x, 1 ≤ x → ((ind x : ℕ) : ℝ) = if 2 ≤ x then 0 else 1 := by
    intro x hx; unfold ind
    by_cases h : x = 1
    · subst h; simp
    · have : 2 ≤ x := by omega
      simp [h, this]
  have hQa := Qsum_eq s ha
  have hQb := Qsum_eq s hb
  unfold Gstar G4 Hc Kc FAport FBc FB
  rw [Own_two s a, Own_two s b, Psum_Q s ha, Psum_Q s hb, Tsum_eq, Tsum_eq, hQa, hQb, hph1, hps1]
  unfold ta
  push_cast
  rw [hind a ha, hind b hb]
  by_cases h2a : 2 ≤ a <;> by_cases h2b : 2 <= b <;> simp only [h2a, h2b, if_true, if_false] <;> ring

/-- HB DISCHARGED for B ports: a caller whose 96 A ports are in the built type (B-form masks, th QUERY units) and whose 8 B ports are
    ARBITRARY layouts of the model (hubs, own roles, any feasible line schedules, [H-odd] units) satisfies JointCeiling's hB. -/
theorem hB_discharge {a b th : ℕ} (ha : 1 ≤ a) (hb : 1 ≤ b) (Ps : Fin 8 → BPort a b) (ci : Inv)
    (hci : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → Finv s ci = 96 * FAport s a b th + ∑ i, (Ps i).F s) :
    ∀ s : ℝ, 0 ≤ s → s ≤ 1 → Finv s ci ≤ FBc a b th s := by
  intro s hs0 hs1
  rw [hci s hs0 hs1, ← port_total ha hb th s]
  have : ∑ i, (Ps i).F s ≤ ∑ _i : Fin 8, Gstar s a b :=
    Finset.sum_le_sum (fun i _ => bform_optimal ha hb (Ps i) hs0 hs1)
  simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul] at this
  push_cast at this
  linarith

/-- the class of JointCeiling, with hB supplied by the theorem above instead of a hypothesis -/
def inClassOfPorts {th0 : ℕ} {a b th : ℕ} (ha : 1 ≤ a) (hb : 1 ≤ b) (rho : ℕ) (hth : th0 ≤ th) (hrho : 2 ≤ rho)
    (Ps : Fin 8 → BPort a b) (ci : Inv)
    (hci : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → Finv s ci = 96 * FAport s a b th + ∑ i, (Ps i).F s) : InClass th0 :=
  ⟨a, b, th, rho, ci, ha, hb, hth, hrho, hB_discharge ha hb Ps ci hci⟩

/-- ceiling at tbar4 with hB discharged (only the native floor, NumCert, [H-odd] inside BPort, and the built-type A ports remain hypotheses) -/
theorem ceiling_of_ports (hnum : NumCert 4 tbar4) {a b : ℕ} (ha : 1 ≤ a) (hb : 1 ≤ b) (rho : ℕ) (hrho : 2 ≤ rho)
    (Ps : Fin 8 → BPort a b) (ci : Inv)
    (hci : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → Finv s ci = 96 * FAport s a b 4 + ∑ i, (Ps i).F s)
    (n : Inv) (hN : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → Finv s n ≤ -Nfl s) (s : ℝ) (hs0 : 0 ≤ s) (hs : s ≤ 1 - tbar4) :
    Finv s (invoice ci n (a + b)) < 0 := by
  have := ceiling (th0 := 4) (tbar := tbar4) hnum
    (inClassOfPorts (th0 := 4) ha hb rho le_rfl hrho Ps ci (fun s h0 h1 => hci s h0 h1)) n hN
    (by unfold tbar4; norm_num) s hs0 hs
  exact this

/-! ### 6. the A-port failure (remark with a witness) and the neutrality of centre roles on B ports -/
noncomputable def Fr (s : ℝ) (T P : List ℕ) : ℝ := (T.map fun r => (r : ℝ) ^ s).sum - (P.map fun r => (r : ℝ) ^ s).sum

/-- rank lists of the 2|2 A port (m = 4, 4 QUERY units): B form, and with ONE own role of rank 9 (d = 1, the arm's last stage) dropped
    (the line it would have idled and one QUERY go with it).  Source: r2.py `port(2,2,2,[2,2],[2,2],4,2,False)` and `port(2,2,2,[2,1],[2,2],4,2,False)`. -/
def TA : List ℕ := [33, 33, 17, 17, 9, 9, 17, 17, 9, 9]
def PA : List ℕ := [8, 8, 8, 8, 1, 1, 1, 1]
def TA' : List ℕ := [33, 33, 17, 17, 9, 17, 17, 9, 9]
def PA' : List ℕ := [8, 8, 8, 1, 1, 1]

theorem FrA_eq (s : ℝ) : Fr s TA PA = FAport s 2 2 4 := by
  unfold Fr TA PA FAport Tsum Qsum ta ph
  simp [Finset.sum_range_succ]
  norm_num
  ring

theorem A_drop_gain (s : ℝ) : Fr s TA' PA' - Fr s TA PA = 1 - ((9 : ℝ) ^ s - (8 : ℝ) ^ s) := by
  unfold Fr TA PA TA' PA'
  simp
  ring

/-- A ports: dropping the last-stage own role never loses (psi(1) <= 1 = QUERY price), for every s in [0,1] -/
theorem A_drop_nonneg {s : ℝ} (hs0 : 0 ≤ s) (hs1 : s ≤ 1) : 0 ≤ Fr s TA' PA' - Fr s TA PA := by
  rw [A_drop_gain]
  have := Real.rpow_add_le_add_rpow (a := 8) (b := 1) (by norm_num) (by norm_num) hs0 hs1
  norm_num at this ⊢
  linarith

/-- ... and strictly gains at s = 0 (t = 1): the B form is NOT optimal on A ports -/
theorem A_drop_strict_zero : Fr 0 TA' PA' - Fr 0 TA PA = 1 := by
  rw [A_drop_gain]; norm_num

/-- ... and at s = 1/2 (t = 1/2) -/
theorem A_drop_strict_half : 0 < Fr (1 / 2) TA' PA' - Fr (1 / 2) TA PA := by
  rw [A_drop_gain, ← Real.sqrt_eq_rpow, ← Real.sqrt_eq_rpow]
  have h9 : Real.sqrt 9 = 3 := by
    rw [show (9 : ℝ) = 3 ^ 2 by norm_num]; exact Real.sqrt_sq (by norm_num)
  have h8 : 2 < Real.sqrt 8 := by
    rw [show (2 : ℝ) = Real.sqrt 4 by rw [show (4 : ℝ) = 2 ^ 2 by norm_num]; exact (Real.sqrt_sq (by norm_num)).symm]
    exact Real.sqrt_lt_sqrt (by norm_num) (by norm_num)
  rw [h9]; linarith

/-- B ports: the same drop is NEUTRAL (cost psi(1) per unit): the last-stage own role contributes 0 to the R2 L4 form -/
theorem centre_role_neutral (s : ℝ) (y : ℕ) (e : ℕ → ℕ) (v : ℕ) :
    Own s (y + 1) (Function.update e y v) = Own s (y + 1) e := by
  unfold Own
  rw [Finset.sum_range_succ, Finset.sum_range_succ]
  have h0 : ps s (y + 1 - y) - ps s 1 = 0 := by simp
  rw [h0, mul_zero, mul_zero, add_zero, add_zero]
  apply Finset.sum_congr rfl
  intro c hc
  rw [Finset.mem_range] at hc
  rw [Function.update_of_ne (by omega)]

/-! ### 7. attainment certificate: the canonical B-form schedule (r2.py `lines`) is feasible, small arms by kernel evaluation -/
def repl (k : ℕ) (p : Line) : List Line := List.replicate k p
/-- lines starting at arm stage c in the B form (h = 2, e = 2): stage 0: two 1-lines; last stage: four 1-lines; else two 1-lines and two long lines to the end -/
def latB (x c : ℕ) : List Line :=
  if c = 0 then repl 2 (0, 1) else if c + 1 = x then repl 4 (c, 1) else repl 2 (c, 1) ++ repl 2 (c, x - c)
def sigB (x : ℕ) : List Line := (List.range x).flatMap (latB x)
instance (x : ℕ) (σ : List Line) : Decidable (Valid x σ) := by unfold Valid; infer_instance

/-- B-form arm schedule is feasible (occupancy n_c = 2c+2 exactly, crossing <= cap_c = 2c) -- kernel-evaluated for x = 1..8 -/
theorem sigB_feasible_small : ∀ x ∈ ({1, 2, 3, 4, 5, 6, 7, 8} : Finset ℕ),
    Valid x (sigB x) ∧ (∀ c < x, covN (sigB x) c = occ 2 (fun _ => 2) c) ∧
      (∀ c < x, c + 1 < x → crossN (sigB x) c ≤ capc 2 (fun _ => 2) c) := by
  decide +kernel

/-- its bill is the closed form (2x) phi(1) + 2 sum_{J<x-1} phi(J+1) = CB at the B form, x = 1..6 -/
theorem sigB_bill_small (s : ℝ) : ∀ x ∈ ({1, 2, 3, 4, 5, 6} : Finset ℕ),
    bill s (sigB x) = 2 * (x : ℝ) * ph s 1 + 2 * ∑ J ∈ range (x - 1), ph s (J + 1) := by
  intro x hx
  simp only [Finset.mem_insert, Finset.mem_singleton] at hx
  rcases hx with rfl | rfl | rfl | rfl | rfl | rfl <;>
    simp [bill, sigB, latB, repl, List.range_succ, List.replicate, Finset.sum_range_succ] <;> ring

#print axioms BFormOpt.spread
#print axioms BFormOpt.abel_nonneg
#print axioms BFormOpt.bill_lb
#print axioms BFormOpt.CB_closed
#print axioms BFormOpt.own_abel
#print axioms BFormOpt.hub_nonpos
#print axioms BFormOpt.F_le_G4
#print axioms BFormOpt.G4_le_star
#print axioms BFormOpt.bform_optimal
#print axioms BFormOpt.port_total
#print axioms BFormOpt.hB_discharge
#print axioms BFormOpt.ceiling_of_ports
#print axioms BFormOpt.A_drop_gain
#print axioms BFormOpt.A_drop_nonneg
#print axioms BFormOpt.A_drop_strict_zero
#print axioms BFormOpt.A_drop_strict_half
#print axioms BFormOpt.centre_role_neutral
#print axioms BFormOpt.sigB_feasible_small
#print axioms BFormOpt.sigB_bill_small
#print axioms BFormOpt.inClassOfPorts
