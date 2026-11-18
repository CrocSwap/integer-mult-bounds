/-
Delivery .  See Delivery.md.  Structural lemmas of internal notes, D3.md, D5.md.

 1. TWO-STOP   (algebra, from TokenCancel.T2_corrected): a single contact delivers nothing; a courier whose row does not
               change between its contacts with t delivers nothing; delivery needs >= 2 contacts with DIFFERENT rows.
               (price, from CallerCost.fL = r ln r and FibreK.d0_native): a courier with three genuine hops pays
               f(d) - f(d-2) >= f(3); the C-type (1,7,1) route pays exactly f(9) - f(7).  A zero-gap hop breaks ">= f(3)".
 2. ENTRY RANK / DIRECT-READ CAPACITY (from Annihilator): single hop A -> L serves <= dim A - dim L ports of an
               orthonormal group; any number of hops: <= descending owned rank; the >= N - R remaining ports are not sparse.
 3. TIME-ORDER (charts only ascend): after a register sits at a chart containing u_a it never meets Y_a again; so a
               carrier delivering x_b to Y_a picked x_b up strictly BEFORE the read.
Kernel only: no sorry, no native_decide.
-/
import Nov15.TokenCancel
import Nov15.FibreK
import Nov15.Annihilator
import Mathlib.Analysis.SpecialFunctions.Log.NegMulLog
import Mathlib.Analysis.Complex.ExponentialBounds

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace Delivery
open CallerCost

/-! ## 1a. TWO-STOP, algebra -/
section TwoStop
open TokenCancel
variable {K Reg : Type*} [Field K] [DecidableEq Reg]

/-- a single contact (at most one entry in `contacts`) delivers nothing net. -/
theorem single_contact_null (k : Reg) (ops : List (YOp K Reg)) (y0 : Reg → K) (hy0 : y0 k = 0)
    (hK : ∀ a r, YOp.addK a r ∈ ops → r k = 1) (hO : ∀ w, YOp.addO w ∈ ops → w k = 0)
    (hfin : (yRun (y0, 0, 0) ops).1 k = 0) (hlen : (contacts ops).length ≤ 1) :
    (yRun (y0, 0, 0) ops).2.1 = 0 := by
  obtain ⟨h1, h2, -⟩ := T2_corrected k ops y0 hy0 hK hO hfin 0
  rw [h2]
  rcases hc : contacts ops with _ | ⟨p, _ | ⟨q, l⟩⟩
  · simp
  · rw [hc] at h1; simp at h1; simp [h1]
  · rw [hc] at hlen; simp at hlen

/-- delivery needs at least two contacts. -/
theorem two_contacts_needed (k : Reg) (ops : List (YOp K Reg)) (y0 : Reg → K) (hy0 : y0 k = 0)
    (hK : ∀ a r, YOp.addK a r ∈ ops → r k = 1) (hO : ∀ w, YOp.addO w ∈ ops → w k = 0)
    (hfin : (yRun (y0, 0, 0) ops).1 k = 0) (hrec : (yRun (y0, 0, 0) ops).2.1 ≠ 0) :
    2 ≤ (contacts ops).length := by
  by_contra h
  exact hrec (single_contact_null k ops y0 hy0 hK hO hfin (by omega))

/-- a courier whose row (at the contacts) never changes delivers nothing: the rows must DIFFER somewhere. -/
theorem const_rows_null (k : Reg) (ops : List (YOp K Reg)) (y0 : Reg → K) (hy0 : y0 k = 0)
    (hK : ∀ a r, YOp.addK a r ∈ ops → r k = 1) (hO : ∀ w, YOp.addO w ∈ ops → w k = 0)
    (hfin : (yRun (y0, 0, 0) ops).1 k = 0) (r1 : Reg → K) (hrows : ∀ p ∈ contacts ops, p.2 = r1) :
    (yRun (y0, 0, 0) ops).2.1 = 0 := by
  obtain ⟨-, -, h3⟩ := T2_corrected k ops y0 hy0 hK hO hfin r1
  rw [h3]
  have : ∀ l : List (K × (Reg → K)), (∀ p ∈ l, p.2 = r1) → (l.map fun p => p.1 • (p.2 - r1)).sum = 0 := by
    intro l; induction l with
    | nil => intro _; simp
    | cons p l ih =>
      intro h
      simp only [List.map_cons, List.sum_cons]
      rw [h p List.mem_cons_self, ih (fun q hq => h q (List.mem_cons_of_mem _ hq))]; simp
  exact this _ hrows

/-- tightness: two contacts with different rows deliver a nonzero net (over ℚ, k = 0, content v = 1). -/
theorem two_contacts_suffice :
    let r1 : Fin 2 → ℚ := ![1, 0]
    let r2 : Fin 2 → ℚ := ![1, 1]
    let ops : List (YOp ℚ (Fin 2)) := [.addK 1 r1, .addK (-1) r2]
    (yRun ((0 : Fin 2 → ℚ), 0, 0) ops).1 0 = 0 ∧ (yRun ((0 : Fin 2 → ℚ), 0, 0) ops).2.1 ≠ 0 := by
  refine ⟨?_, ?_⟩
  · simp [yRun, yStep]
  · intro h
    have := congrFun h 1
    simp [yRun, yStep] at this
end TwoStop

/-! ## 1b. TWO-STOP, price: three genuine hops cost f(d) - f(d-2) >= f(3) -/
section Price
open FibreK

/-- f x = x log x on ℝ (CallerCost.fL on ℕ). -/
noncomputable def ff (x : ℝ) : ℝ := x * Real.log x

theorem fL_eq (n : ℕ) : fL n = ff n := rfl

/-- convexity: increments of f over a fixed length h grow with the base point. -/
theorem inc (x y h : ℝ) (hx : 0 ≤ x) (hxy : x ≤ y) (hh : 0 ≤ h) :
    ff (x + h) - ff x ≤ ff (y + h) - ff y := by
  rcases eq_or_lt_of_le hh with rfl | hpos
  · simp
  have hD : 0 < y + h - x := by linarith
  have hs0 : 0 ≤ h / (y + h - x) := by positivity
  have hs1 : h / (y + h - x) ≤ 1 := by rw [div_le_one hD]; linarith
  set s := h / (y + h - x) with hs
  have hsD : s * (y + h - x) = h := by rw [hs]; field_simp
  have c := Real.convexOn_mul_log
  have mx : x ∈ Set.Ici (0 : ℝ) := hx
  have my : y + h ∈ Set.Ici (0 : ℝ) := by show 0 ≤ y + h; linarith
  have h1 := c.2 mx my (by linarith : (0:ℝ) ≤ 1 - s) hs0 (by ring : (1 - s) + s = 1)
  have h2 := c.2 mx my hs0 (by linarith : (0:ℝ) ≤ 1 - s) (by ring : s + (1 - s) = 1)
  have e1 : (1 - s) • x + s • (y + h) = x + h := by simp only [smul_eq_mul]; nlinarith
  have e2 : s • x + (1 - s) • (y + h) = y := by simp only [smul_eq_mul]; nlinarith
  rw [e1] at h1
  rw [e2] at h2
  simp only [smul_eq_mul] at h1 h2
  show ff (x + h) - ff x ≤ ff (y + h) - ff y
  unfold ff
  nlinarith

theorem ff_one : ff 1 = 0 := by simp [ff]
theorem fL_one : fL 1 = 0 := by simp [fL]
theorem fL_zero : fL 0 = 0 := by simp [fL]

/-- two positive gaps never beat one gap that is one shorter: f(a+1) + f(b+1) <= f(a+b+1). -/
theorem two_gaps (a b : ℕ) : fL (a + 1) + fL (b + 1) ≤ fL (a + b + 1) := by
  have := inc 1 ((b : ℝ) + 1) (a : ℝ) (by norm_num) (by linarith [(Nat.cast_nonneg b : (0:ℝ) ≤ b)])
    (Nat.cast_nonneg a)
  rw [ff_one] at this
  simp only [fL_eq]
  push_cast
  have e1 : ((1 : ℝ) + a) = (a : ℝ) + 1 := by ring
  have e2 : (b : ℝ) + 1 + a = (a : ℝ) + b + 1 := by ring
  rw [e1, e2] at this
  linarith

theorem three_gaps (a b c : ℕ) : fL (a + 1) + fL (b + 1) + fL (c + 1) ≤ fL (a + b + c + 1) := by
  have h1 := two_gaps a b
  have h2 := two_gaps (a + b) c
  have e : a + b + 1 = a + b + 1 := rfl
  have : fL (a + b + 1) + fL (c + 1) ≤ fL (a + b + c + 1) := h2
  linarith

/-- the increment f(n+3) - f(n+1) is at least f(3) (f(1) = 0). -/
theorem step2_ge (n : ℕ) : fL 3 ≤ fL (n + 3) - fL (n + 1) := by
  have := inc 1 ((n : ℝ) + 1) 2 (by norm_num) (by linarith [(Nat.cast_nonneg n : (0:ℝ) ≤ n)]) (by norm_num)
  rw [ff_one] at this
  simp only [fL_eq]
  push_cast
  have e1 : ((1 : ℝ) + 2) = 3 := by norm_num
  have e2 : (n : ℝ) + 1 + 2 = (n : ℝ) + 3 := by ring
  rw [e1, e2] at this
  linarith

/-- per-helper D0 term of FibreK.d0_native. -/
noncomputable def courierD0 (h : Helper) : ℝ := fL (h.e - h.b) - (h.steps.map fun s => fL (gap s)).sum

theorem steps_sum (h : Helper) : (h.steps.map fun s => fL (gap s)).sum = ((h.steps.map gap).map fL).sum := by
  rw [List.map_map]; rfl

/-- **TWO-STOP price.**  A courier with >= 2 stops has >= 3 hops (birth -> s1 -> s2 -> end).  If all three hops are
genuine (gap >= 1) and the route climbs by their total d = e - b, its D0 is >= f(d) - f(d-2) >= f(3). -/
theorem three_hop_cost (h : Helper) (a b c : ℕ) (hs : h.steps.map gap = [a + 1, b + 1, c + 1])
    (hd : h.e - h.b = a + b + c + 3) :
    fL (a + b + c + 3) - fL (a + b + c + 1) ≤ courierD0 h ∧ fL 3 ≤ courierD0 h := by
  have hsum : (h.steps.map fun s => fL (gap s)).sum = fL (a + 1) + fL (b + 1) + fL (c + 1) := by
    rw [steps_sum, hs]; simp; ring
  have h3 := three_gaps a b c
  have h2 := step2_ge (a + b + c)
  unfold courierD0
  rw [hsum, hd]
  constructor <;> linarith

/-- the C-type route: gaps (1, n+1, 1) (pickup at dim 1, delivery at dim n+2, ...) pays EXACTLY f(n+3) - f(n+1);
n = 6 is the C-type (0 -> 1 -> 8 -> 9): f(9) - f(7). -/
theorem ctype_cost (h : Helper) (n : ℕ) (hs : h.steps.map gap = [1, n + 1, 1]) (hd : h.e - h.b = n + 3) :
    courierD0 h = fL (n + 3) - fL (n + 1) := by
  have hsum : (h.steps.map fun s => fL (gap s)).sum = fL (n + 1) := by
    rw [steps_sum, hs]; simp [fL_one]
  unfold courierD0
  rw [hsum, hd]

/-- equality in `three_hop_cost` iff the gaps are (1, d-2, 1) up to order is NOT claimed; but d = 3, gaps (1,1,1): cost = f(3). -/
theorem unit_hops_cost (h : Helper) (hs : h.steps.map gap = [1, 1, 1]) (hd : h.e - h.b = 3) :
    courierD0 h = fL 3 := by
  have := ctype_cost h 0 (by simpa using hs) (by simpa using hd)
  simpa [fL_one] using this

/-- f(3) = 3 log 3 > 3 (numerically 3.2958 [C]). -/
theorem fL_three_gt : 3 < fL 3 := by
  have h : (1 : ℝ) < Real.log 3 := by
    rw [Real.lt_log_iff_exp_lt (by norm_num)]
    have := Real.exp_one_lt_d9
    linarith
  simp only [fL]; push_cast; linarith

/-- **WORDING FIX.**  The step "f(d) - max over three-way splits of Σ f >= f(3)" is false once a split may have a ZERO
part (birth or end sitting AT a stop): the courier 0 -> 8 -> 9 -> 9 (gaps 8, 1, 0, d = 9) has D0 = f(9) - f(8) < f(3)
(3.14 < 3.30).  With three genuine hops it is `three_hop_cost`. -/
theorem zero_gap_counterexample :
    ∃ h : Helper, h.e - h.b = 9 ∧ h.steps.map gap = [8, 1, 0] ∧ courierD0 h < fL 3 := by
  refine ⟨⟨0, 9, [(0, 8), (8, 9), (9, 9)]⟩, by simp, by simp [gap], ?_⟩
  have hsum : (([(0, 8), (8, 9), (9, 9)] : List (ℕ × ℕ)).map fun s => fL (gap s)).sum = fL 8 + fL 1 + fL 0 := by
    simp [gap]; ring
  unfold courierD0
  show fL (9 - 0) - _ < _
  rw [hsum, fL_one, fL_zero]
  have l9 : Real.log 9 = 2 * Real.log 3 := by
    rw [show (9 : ℝ) = 3 ^ 2 by norm_num, Real.log_pow]; norm_num
  have l8 : Real.log 8 = 3 * Real.log 2 := by
    rw [show (8 : ℝ) = 2 ^ 3 by norm_num, Real.log_pow]; norm_num
  have key : 5 * Real.log 3 < 8 * Real.log 2 := by
    have h1 : Real.log 243 < Real.log 256 := Real.log_lt_log (by norm_num) (by norm_num)
    have h243 : Real.log 243 = 5 * Real.log 3 := by
      rw [show (243 : ℝ) = 3 ^ 5 by norm_num, Real.log_pow]; norm_num
    have h256 : Real.log 256 = 8 * Real.log 2 := by
      rw [show (256 : ℝ) = 2 ^ 8 by norm_num, Real.log_pow]; norm_num
    linarith
  simp only [fL]
  push_cast
  rw [l9, l8]
  linarith
end Price

/-! ## 2. ENTRY RANK and DIRECT-READ CAPACITY -/
section Entry
open Annihilator Module
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V] [FiniteDimensional K V]

/-- single owned MOVE A -> L as a lineage. -/
def oneHop (A L : Submodule K V) : Lineage K V := ⟨1, fun i => if i = 0 then A else L, fun _ => Kind.own⟩

theorem oneHop_legal (A L : Submodule K V) (h : L ≤ A) : (oneHop A L).Legal := by
  intro i hi
  have hn : (oneHop A L).n = 1 := rfl
  have : i = 0 := by omega
  subst this
  show (oneHop A L).c 1 ≤ (oneHop A L).c 0 ∨ _
  left; simpa [oneHop] using h

theorem oneHop_rank (A L : Submodule K V) : (oneHop A L).ownRank = finrank K A - finrank K L := by
  simp [Lineage.ownRank, oneHop]
  rfl

/-- **DIRECT-READ CAPACITY / ENTRY RANK (single hop).**  An entry A -> L (L ≤ A) whose group G of ports reads X_b
directly (u_b ∈ A for b ∈ G), whose worlds contain L (φ_a vanishes on L), and whose Gram block is the identity
(orthonormal group) serves |G| <= dim A - dim L. -/
theorem direct_read_capacity {P : Type*} [Fintype P] [DecidableEq P] (A L : Submodule K V) (hLA : L ≤ A)
    (φ : P → Module.Dual K V) (u : P → V) (hu : ∀ b, u b ∈ A) (hφ : ∀ a, ∀ x ∈ L, φ a x = 0)
    (hG : ∀ a a', φ a (u a') = if a = a' then 1 else 0) :
    Fintype.card P ≤ finrank K A - finrank K L := by
  classical
  let D : Delivery K V P P :=
    { L := oneHop A L, φ := φ, u := u, start := hu, leafIdx := fun _ => 1, leaf_le := fun _ => le_rfl,
      leaf := fun a x hx => hφ a x (by simpa [oneHop] using hx) }
  have := sparse_serves_le D (oneHop_legal A L hLA) id Function.injective_id hG
  rwa [oneHop_rank] at this

/-- **ENTRY RANK, any number of hops** (ANNIHILATOR corollary): the owned descending rank of the lineage bounds the
ports of an orthonormal group, however many hops. -/
theorem entry_rank_multihop {P S : Type*} [Fintype P] [Fintype S] [DecidableEq P] [DecidableEq S]
    (D : Delivery K V P S) (hL : D.L.Legal) (ι : P → S) (hι : Function.Injective ι)
    (hG : ∀ a a', D.φ a (D.u (ι a')) = if a = a' then 1 else 0) :
    Fintype.card P ≤ D.L.ownRank := sparse_serves_le D hL ι hι hG

/-- **CAPACITY ceiling.**  Entries are disjoint in MOVEs, so the ports served by sparse groups total <= R
(R = word's descending owned rank; R = 56 on S22 by Theorem K + [C d3p], not proved here); the other N - served ports
need dense entries.  (D3: N = 104, R = 56 gives >= 48.) -/
theorem dense_needed {ι : Type*} (s : Finset ι) (card rk : ι → ℕ) (R N : ℕ)
    (hc : ∀ i ∈ s, card i ≤ rk i) (hR : ∑ i ∈ s, rk i ≤ R) (hN : ∑ i ∈ s, card i ≤ N) :
    N - R ≤ N - ∑ i ∈ s, card i := by
  have := total_sparse_le s card rk R hc hR
  omega

theorem numbers_104_56 : 104 - 56 = 48 := by norm_num
end Entry

/-! ## 3. TIME-ORDER -/
section TimeOrder
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]

/-- Setup: public registers' charts only ASCEND (`Monotone`).  Y_a lives in worlds on which φ vanishes, and φ u ≠ 0
(u = u_a, φ = (· u_a); orthonormal: φ u = 1).  X_b read by an owned register at time r at a chart containing u. -/
theorem never_meet_after_read (u : V) (φ : Module.Dual K V) (hφu : φ u ≠ 0)
    (cx cy : ℕ → Submodule K V) (hx : Monotone cx) (hy : ∀ t, ∀ v ∈ cy t, φ v = 0)
    (r : ℕ) (hr : u ∈ cx r) : ∀ t, r ≤ t → cx t ≠ cy t := by
  intro t ht heq
  have : u ∈ cx t := hx ht hr
  rw [heq] at this
  exact hφu (hy t u this)

/-- **TIME-ORDER.**  A carrier (monotone charts `cc`) that picks x_b up from X_b (same chart at time p) and later
(time j ≥ p) meets Y_a (same chart) must have picked up strictly BEFORE the read: p < r.  (In fact u ∉ cx p.) -/
theorem carrier_before_read (u : V) (φ : Module.Dual K V) (hφu : φ u ≠ 0)
    (cx cy cc : ℕ → Submodule K V) (hx : Monotone cx) (hc : Monotone cc) (hy : ∀ t, ∀ v ∈ cy t, φ v = 0)
    (r : ℕ) (hr : u ∈ cx r) (p j : ℕ) (hpj : p ≤ j) (hpick : cc p = cx p) (hdel : cc j = cy j) :
    p < r ∧ u ∉ cx p := by
  have hnot : u ∉ cx p := by
    intro hu
    have h1 : u ∈ cc p := by rw [hpick]; exact hu
    have h2 : u ∈ cy j := by rw [← hdel]; exact hc hpj h1
    exact hφu (hy j u h2)
  refine ⟨?_, hnot⟩
  by_contra hlt
  exact hnot (hx (by omega : r ≤ p) hr)

/-- Direct meeting is the special case: X_b itself cannot hand x_b to Y_a at or after the read. -/
theorem direct_after_read_impossible (u : V) (φ : Module.Dual K V) (hφu : φ u ≠ 0)
    (cx cy : ℕ → Submodule K V) (hx : Monotone cx) (hy : ∀ t, ∀ v ∈ cy t, φ v = 0)
    (r : ℕ) (hr : u ∈ cx r) (t : ℕ) (ht : r ≤ t) : cx t ≠ cy t :=
  never_meet_after_read u φ hφu cx cy hx hy r hr t ht
end TimeOrder

end Delivery

#print axioms Delivery.single_contact_null
#print axioms Delivery.two_contacts_needed
#print axioms Delivery.const_rows_null
#print axioms Delivery.two_contacts_suffice
#print axioms Delivery.three_hop_cost
#print axioms Delivery.ctype_cost
#print axioms Delivery.zero_gap_counterexample
#print axioms Delivery.fL_three_gt
#print axioms Delivery.direct_read_capacity
#print axioms Delivery.entry_rank_multihop
#print axioms Delivery.dense_needed
#print axioms Delivery.carrier_before_read
