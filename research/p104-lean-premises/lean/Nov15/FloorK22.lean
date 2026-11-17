/-
FloorK22 : WHOLEFLOOR R5's class-K(S22) floor (internal notes, AUDIT5.md).
See FloorK22.md.  Kernel only: no sorry, no native_decide.
-/
import Nov15.FloorD0
import Nov15.JointCeiling
import Nov15.FloorK22Data
import Mathlib.Analysis.Convex.SpecificFunctions.Pow
import Mathlib.Analysis.Complex.ExponentialBounds

open Finset

set_option linter.unusedSectionVars false

namespace FloorK22
open FloorE2E FloorD0 FloorK22Data

/-! ## 0. AUDIT5 scope fix: entry EVENTS vs registers -/

section Scope
open ExportLaw
variable {K Reg C : Type*} [Field K] [DecidableEq K] [Fintype Reg] [DecidableEq Reg]
  [PartialOrder C] [DecidableEq C]

/-- dim I_C <= births + entries counts entry EVENTS; sigma counts registers.  They agree for every
PUBLIC register (helper or kept) of every accepted word, because each public MOVE strictly climbs
(l.51): a public register enters a chart at most once (`hOnce_proj`).  This is what "helpers ascend" buys. -/
theorem entries_are_registers {Pub H : Finset Reg} {ini : Reg → Option C} {w : List (GEv K Reg C)}
    (hA : Accepted Pub H ini w) (c : C) (h : Reg) (hh : h ∈ H) :
    nEnt {h} (proj c ini w) ≤ 1 :=
  hOnce_proj Pub c ini w hA.legal h (hA.helpers_pub hh) ((hA.pub_ini h).1 (hA.helpers_pub hh))

/-- Without ascent the event count and the register count differ: in the one-chart model (which has no
ascent hypothesis) one register arrives, leaves and arrives again: 2 entry events, 1 register.  So
"dim I_C <= births + entries" bounds registers only for ascending registers (owned registers may
descend and re-enter, so for them the bound is by events: `oa` counts events). -/
theorem reentry_two_events :
    nEnt ({0} : Finset (Fin 1))
      [Ev.arrive (K := ℚ) 0 (fun _ => 1), Ev.depart 0, Ev.arrive 0 (fun _ => 1)] = 2 ∧
    Legal (ExportLaw.start (K := ℚ) (Reg := Fin 1))
      [Ev.arrive 0 (fun _ => 1), Ev.depart 0, Ev.arrive 0 (fun _ => 1)] := by
  refine ⟨by simp [nEnt], ?_⟩
  simp [Legal, LegalEv, step, ExportLaw.start]

end Scope

/-! ## 1. Class K(S22) -/

section ClassK22
variable {K Reg C : Type*} [Field K] [DecidableEq K] [Fintype Reg] [DecidableEq Reg]
  [PartialOrder C] [DecidableEq C] [Fintype C]

/-- |Δ dim| of every MOVE of a non-helper register (mains and owned): PRICEKIT's P-charges of the kept stream. -/
noncomputable def keptDiffs (dim : C → ℕ) (H : Finset Reg) (ini : Reg → Option C)
    (w : List (GEv K Reg C)) : List ℝ :=
  (((moves (s0 ini) w).filter fun m => decide (m.reg ∉ H)).map
    fun m => |(dim m.head : ℝ) - dim m.tail|)

/-- the kept stream of S22 (1,721 MOVEs = 1,674 main + 47 owned) as a multiset of |Δ dim|:
968 x 1, 366 x 2, 103 x 3, 127 x 4, 147 x 5, 10 x 6 (r5cd_rows.py `PK`). -/
def keptExp : List ℝ :=
  List.replicate 968 1 ++ List.replicate 366 2 ++ List.replicate 103 3 ++
    List.replicate 127 4 ++ List.replicate 147 5 ++ List.replicate 10 6

theorem keptExp_sum (g : ℝ → ℝ) : (keptExp.map g).sum =
    968 * g 1 + 366 * g 2 + 103 * g 3 + 127 * g 4 + 147 * g 5 + 10 * g 6 := by
  simp only [keptExp, List.map_append, List.sum_append, List.map_replicate, List.sum_replicate,
    nsmul_eq_mul]
  push_cast; ring

/-- PRICEKIT P-charge of the kept stream. -/
noncomputable def keptCost (f : ℝ → ℝ) (dim : C → ℕ) (H : Finset Reg) (ini : Reg → Option C)
    (w : List (GEv K Reg C)) : ℝ :=
  (((moves (s0 ini) w).filter fun m => decide (m.reg ∉ H)).map (mvCost f dim)).sum

theorem keptCost_eq (f : ℝ → ℝ) (dim : C → ℕ) (H : Finset Reg) (ini : Reg → Option C)
    (w : List (GEv K Reg C)) :
    keptCost f dim H ini w = ((keptDiffs dim H ini w).map f).sum := by
  unfold keptCost keptDiffs
  rw [List.map_map]
  rfl

/-- **Class K(S22)** (AUDIT5 item 4, made precise).  An accepted word `w` of the verifier model such that
 * (kept data, `K`) its kept (main + owned) content is S22's: `ClassK` for the kept data D = S22's, with
   `Kfin = Pub \ H`: the finals of ALL kept enders (Y-enders included) are kept rows of their chart; so are all
   kept/owned arrival rows and kept birth tokens (K1, K2), and the kept rows at kept events (R: every kept
   row at c at a visited state);
 * (rank/count data, S22's) the per-chart numbers of FloorK22Data: rank rho(kept rows at c) >= rk, kept
   registers entering-or-born at c <= ab, owned entries <= oa.  The rank statement is the one piece of
   checked input that is not kernel-checked here (378-coordinate rational rows; r5cd.py, mod p = 2^31-1
   and independent re-derivation in AUDIT5); the counts are the literal counts of `ClassK`;
 * (kept routes, `keptP`) the multiset of |Δ dim| over the kept MOVEs is S22's (kept routes and times fixed);
 * helpers are free (routes, frames, ops), subject only to verifier acceptance; "ascending only" is not an
   extra restriction: every public MOVE strictly climbs in an accepted word (`moves_facts`).
The chart index `e : C ≃ Fin rows.length` pairs each chart with its row of FloorK22Data. -/
structure ClassK22 (Pub H Kfin : Finset Reg) (ini : Reg → Option C) (w : List (GEv K Reg C))
    (dim : C → ℕ) (e : C ≃ Fin rows.length) (D : KData C (Reg → K)) : Prop where
  kc : ClassK Pub H Kfin ini w D
  kfin_all : Kfin = Pub \ H
  rank_ge : ∀ c, (((rows.get (e c)).rk : ℕ) : ℤ) ≤
    (Module.finrank K (Submodule.span K (D.Kρ c) ⊔ Submodule.span K (D.Rρ c) : Submodule K (Reg → K)) : ℤ)
  count_le : ∀ c, D.ka c + D.kb c ≤ (rows.get (e c)).ab
  oa_le : ∀ c, D.oa c ≤ (rows.get (e c)).oa
  keptP : (keptDiffs dim H ini w).Perm keptExp

variable {Pub H Kfin : Finset Reg} {ini : Reg → Option C} {w : List (GEv K Reg C)}
  {dim : C → ℕ} {e : C ≃ Fin rows.length} {D : KData C (Reg → K)}

/-- **R1 per chart, with the Y finals in the quotient** (= R5 §2): hd(c) >= rk - (ka + kb) - oa
   = need_c - kept passers - owned entries, since rk = |Y| + need and ka + kb = |Y| + kp.
   It is `R1_row` with Kfin = all kept enders; no new lemma about the word is needed. -/
theorem R1Y_row (hK : ClassK22 Pub H Kfin ini w dim e D) (c : C) :
    (((rows.get (e c)).rk : ℤ) - (rows.get (e c)).ab - (rows.get (e c)).oa) ≤ hdW H ini w c := by
  have h := R1_row hK.kc c
  have h1 := hK.rank_ge c; have h2 := hK.count_le c; have h3 := hK.oa_le c
  omega

theorem forced_le_hd (hK : ClassK22 Pub H Kfin ini w dim e D) (c : C) :
    forced (rows.get (e c)) ≤ hdW H ini w c := by
  have := R1Y_row hK c
  unfold forced; omega

/-- **the 748 forced stops, on the word**: every class-K(S22) word has at least 748 paid helper stays. -/
theorem stays_ge_748 (hK : ClassK22 Pub H Kfin ini w dim e D) : 748 ≤ (stays H ini w).card := by
  classical
  rw [← sum_hd hK.kc.acc]
  calc 748 = (rows.map forced).sum := forced_sum.symm
    _ = ∑ i : Fin rows.length, forced (rows.get i) := (sum_fin_get forced rows).symm
    _ = ∑ c : C, forced (rows.get (e c)) := (Equiv.sum_comp e fun i => forced (rows.get i)).symm
    _ ≤ ∑ c, hdW H ini w c := Finset.sum_le_sum fun c _ => forced_le_hd hK c

/-- helper D0 floor of class K(S22): >= 748 * 2 ln 2 >= 1036.948 per call. -/
theorem helperD0_ge_748 (hdim : ∀ a b : C, a < b → dim a < dim b)
    (hK : ClassK22 Pub H Kfin ini w dim e D) :
    748 * (2 * Real.log 2) ≤ helperD0 JunkLB2.fL dim H ini w ∧
      (1036.948 : ℝ) ≤ helperD0 JunkLB2.fL dim H ini w := by
  have h1 := helperD0_ge_fL dim hdim hK.kc.acc
  have h2 : (748 : ℝ) ≤ (stays H ini w).card := by exact_mod_cast stays_ge_748 hK
  have hl := Real.log_two_gt_d9
  have h3 : 748 * (2 * Real.log 2) ≤ 2 * Real.log 2 * (stays H ini w).card := by nlinarith
  exact ⟨h3.trans h1, by nlinarith⟩

/-! ## 2. Kept cost and the composition -/

/-- numeric facts: logs of 3 and 5 from the exponential series (kernel arithmetic). -/
theorem log3_lt : Real.log 3 < 10986123 / 10 ^ 7 := by
  rw [Real.log_lt_iff_lt_exp (by norm_num)]
  have h := Real.sum_le_exp_of_nonneg (x := (10986123 : ℝ) / 10 ^ 7) (by norm_num) 14
  refine lt_of_lt_of_le ?_ h
  simp only [Finset.sum_range_succ, Finset.sum_range_zero, Nat.factorial]
  norm_num

theorem log5_lt : Real.log 5 < 160943792 / 10 ^ 8 := by
  rw [Real.log_lt_iff_lt_exp (by norm_num)]
  have h := Real.sum_le_exp_of_nonneg (x := (160943792 : ℝ) / 10 ^ 8) (by norm_num) 16
  refine lt_of_lt_of_le ?_ h
  simp only [Finset.sum_range_succ, Finset.sum_range_zero, Nat.factorial]
  norm_num

/-- The kept stream's D0 (credit, per call), exact in logs. -/
theorem keptExp_D0 :
    ((keptExp.map JunkLB2.fL).sum) =
      1808 * Real.log 2 + 369 * Real.log 3 + 735 * Real.log 5 := by
  have h4 : Real.log 4 = 2 * Real.log 2 := by
    rw [show (4 : ℝ) = 2 ^ 2 by norm_num, Real.log_pow]; norm_num
  have h6 : Real.log 6 = Real.log 2 + Real.log 3 := by
    rw [show (6 : ℝ) = 2 * 3 by norm_num, Real.log_mul (by norm_num) (by norm_num)]
  rw [keptExp_sum]
  simp only [JunkLB2.fL, h4, h6, Real.log_one]
  push_cast
  ring

theorem keptExp_D0_le : ((keptExp.map JunkLB2.fL).sum) ≤ 2841.53492 := by
  rw [keptExp_D0]
  have h2 := Real.log_two_lt_d9
  have h3 := log3_lt; have h5 := log5_lt
  norm_num at h2 h3 h5 ⊢
  linarith

/-- caller-side numeric input: D0 of the #7113 caller invoice C(8|9) (`CallerCost.reproduction`), exact value
270812.81745340...; evaluating its ~70 logs is the hypothesis `hDc`. -/
def CallerD0Input : Prop := (270812.8174 : ℝ) ≤ CallerCost.Dinv (CallerCost.caller 6 7)

/-- **D0 composition for class K(S22).**  With the PRICEKIT cost model (native D0 = helper D0 - kept P-charges,
`hnat`) and the numeric input `hDc`: invoice D0 >= caller + 17 (748 * 2 ln 2 - kept cost) >= 240,134.84. -/
theorem D0_K22 (hdim : ∀ a b : C, a < b → dim a < dim b)
    (hK : ClassK22 Pub H Kfin ini w dim e D) (n : CallerCost.Inv)
    (hnat : CallerCost.Dinv n = helperD0 JunkLB2.fL dim H ini w - keptCost JunkLB2.fL dim H ini w)
    (hDc : CallerD0Input) :
    (240134.84 : ℝ) ≤ CallerCost.Dinv (CallerCost.invoice (CallerCost.caller 6 7) n 17) := by
  rw [CallerCost.invoice_D0]
  have hk : keptCost JunkLB2.fL dim H ini w = ((keptExp.map JunkLB2.fL).sum) := by
    rw [keptCost_eq]; exact (hK.keptP.map _).sum_eq
  have h1 := (helperD0_ge_748 hdim hK).2
  have h2 := keptExp_D0_le
  have h3 := Real.log_two_gt_d9
  have h4 := (helperD0_ge_748 hdim hK).1
  unfold CallerD0Input at hDc
  rw [hnat, hk]
  push_cast
  nlinarith

/-- general form: any lower bound N on the paid helper stays of a K(S22) word (R5: 748; R6's first-hop LP dual: 845,
NOT formalised here) gives invoice D0 >= 270812.8174 + 17 (N * 2 ln 2 - 2841.53492). -/
theorem D0_of_stops (N : ℕ) (hdim : ∀ a b : C, a < b → dim a < dim b)
    (hK : ClassK22 Pub H Kfin ini w dim e D) (hst : N ≤ (stays H ini w).card) (n : CallerCost.Inv)
    (hnat : CallerCost.Dinv n = helperD0 JunkLB2.fL dim H ini w - keptCost JunkLB2.fL dim H ini w)
    (hDc : CallerD0Input) :
    270812.8174 + 17 * ((N : ℝ) * (2 * Real.log 2) - 2841.53492) ≤
      CallerCost.Dinv (CallerCost.invoice (CallerCost.caller 6 7) n 17) := by
  rw [CallerCost.invoice_D0]
  have hk : keptCost JunkLB2.fL dim H ini w = ((keptExp.map JunkLB2.fL).sum) := by
    rw [keptCost_eq]; exact (hK.keptP.map _).sum_eq
  have h2 := keptExp_D0_le
  have h4 := helperD0_ge_fL dim hdim hK.kc.acc
  have hN : (N : ℝ) ≤ (stays H ini w).card := by exact_mod_cast hst
  have hl := Real.log_two_gt_d9
  unfold CallerD0Input at hDc
  rw [hnat, hk]
  push_cast
  nlinarith

/-- R6's conditional corollary: if the first-hop LP dual (845 stops; WHOLEFLOOR R6, not formalised) holds for the word,
invoice D0 >= 242,420.84. -/
theorem D0_K22_R6 (hdim : ∀ a b : C, a < b → dim a < dim b)
    (hK : ClassK22 Pub H Kfin ini w dim e D) (hst : 845 ≤ (stays H ini w).card) (n : CallerCost.Inv)
    (hnat : CallerCost.Dinv n = helperD0 JunkLB2.fL dim H ini w - keptCost JunkLB2.fL dim H ini w)
    (hDc : CallerD0Input) :
    (242420.84 : ℝ) ≤ CallerCost.Dinv (CallerCost.invoice (CallerCost.caller 6 7) n 17) := by
  have h := D0_of_stops 845 hdim hK hst n hnat hDc
  have hl := Real.log_two_gt_d9
  push_cast at h
  nlinarith

/-- the composition as written in R5.md, with its rounded components: 270,812.82 - 46,300.0 - 2,006.0 + 17 * 1,036.95
is 240,134.97, NOT 240,134.84 (the exact PRICEKIT value is 240,134.843 = 270,812.8175 - 48,306.0933 + 17,628.1191;
mains are -46,300.09 exactly, not -46,300.0).  Statement imprecise as written (0.13). -/
theorem recipe_as_written : (270812.82 - 46300.0 - 2006.0 + 17 * 1036.95 : ℝ) = 240134.97 ∧
    (270812.82 - 46300.0 - 2006.0 + 17 * 1036.95 : ℝ) ≠ 240134.84 := by
  constructor <;> norm_num

/-! ## 3. The kappa ceiling -/

open JointCeiling CallerCost in
/-- the per-call native histogram of the K(S22) floor: kept stream + 748 forced stops priced as 0 -> 1 -> 2 helpers
(T[2] += 748, P[1] += 2 * 748), exactly r5k.py. -/
def nK22 : Inv := ⟨[(2, 748)], [(1, 968), (2, 366), (3, 103), (4, 127), (5, 147), (6, 10), (1, 1496)]⟩

open JointCeiling CallerCost in
/-- NUMERIC CERTIFICATE (hypothesis, WHOLEFLOOR r5k.py `cert`): the K(S22) floor invoice has F(s) < 0 on (0, 1 - tbar]
(r5k: F(hi) < 0 at the root's upper end, F decreasing, F < 0 on [.1, 1] in t), tbar = .0060197405
(root .00601974047925, rounded up).  Interval covers with 40-digit Decimals; not kernel-checked. -/
def NumCert22 (tbar : ℝ) : Prop :=
  ∀ s : ℝ, 0 < s → s ≤ 1 - tbar → Finv s (invoice (caller 6 7) nK22 17) < 0

noncomputable def tbar22 : ℝ := 60197405 / 10 ^ 10

/-- helper F-floor, for every exponent s in (0,1]: with f = -x^s (convex, f 0 = 0), FloorD0.helperD0_ge gives
F_helpers(s) <= -(2 - 2^s) * #stays on every accepted word (class K not needed). -/
theorem helperF_le (dim : C → ℕ) (hdim : ∀ a b : C, a < b → dim a < dim b)
    (hA : Accepted Pub H ini w) {s : ℝ} (hs0 : 0 < s) (hs1 : s ≤ 1) :
    helperD0 (fun x : ℝ => x ^ s) dim H ini w ≤ -(2 - (2 : ℝ) ^ s) * (stays H ini w).card := by
  have cvx : ConvexOn ℝ (Set.Ici (0 : ℝ)) (fun x : ℝ => -(x ^ s)) :=
    (Real.concaveOn_rpow hs0.le hs1).neg
  have h0 : (fun x : ℝ => -(x ^ s)) 0 = 0 := by simp [Real.zero_rpow hs0.ne']
  have h := helperD0_ge (fun x : ℝ => -(x ^ s)) dim hdim cvx h0 hA
  have hneg : helperD0 (fun x : ℝ => -(x ^ s)) dim H ini w =
      -helperD0 (fun x : ℝ => x ^ s) dim H ini w := by
    have key : ∀ l : List (Mv K Reg C), (l.map (mvCost (fun x : ℝ => -(x ^ s)) dim)).sum =
        -(l.map (mvCost (fun x : ℝ => x ^ s) dim)).sum := by
      intro l; induction l with
      | nil => simp
      | cons m l ih => simp only [List.map_cons, List.sum_cons, ih, mvCost]; ring
    simp only [helperD0, regD0, key, ← Finset.sum_neg_distrib]
    refine Finset.sum_congr rfl fun h _ => ?_
    ring
  have hk : kap (fun x : ℝ => -(x ^ s)) = -(2 : ℝ) ^ s + 2 := by
    simp [kap, Real.one_rpow]
  rw [hneg, hk] at h
  linarith

open JointCeiling CallerCost in
/-- **kappa <= .0060197405 on class K(S22)** (conditional on the PRICEKIT cost model link `hF`, the kept rank input in
`ClassK22`, and NumCert22): for every class-K(S22) word with native histogram n, the 17-call invoice
has F(s) < 0 for all 0 < s <= 1 - tbar22, i.e. F(1-t) < 0 for t in [tbar22, 1). -/
theorem ceiling22 (hdim : ∀ a b : C, a < b → dim a < dim b)
    (hK : ClassK22 Pub H Kfin ini w dim e D) (n : Inv)
    (hF : ∀ s : ℝ, 0 < s → s ≤ 1 →
      Finv s n = helperD0 (fun x : ℝ => x ^ s) dim H ini w - keptCost (fun x : ℝ => x ^ s) dim H ini w)
    (hnum : NumCert22 tbar22) {s : ℝ} (hs0 : 0 < s) (hs : s ≤ 1 - tbar22) :
    Finv s (invoice (caller 6 7) n 17) < 0 := by
  have hs1 : s ≤ 1 := by unfold tbar22 at hs; linarith
  have hnum' := hnum s hs0 hs
  rw [invoice_F] at hnum' ⊢
  have hn : Finv s n ≤ Finv s nK22 := by
    rw [hF s hs0 hs1]
    have h1 := helperF_le dim hdim hK.kc.acc hs0 hs1
    have h2 : (748 : ℝ) ≤ (stays H ini w).card := by exact_mod_cast stays_ge_748 hK
    have h2s : (2 : ℝ) ^ s ≤ 2 := by
      calc (2 : ℝ) ^ s ≤ 2 ^ (1 : ℝ) := Real.rpow_le_rpow_of_exponent_le (by norm_num) hs1
        _ = 2 := by simp
    have h3 : -(2 - (2 : ℝ) ^ s) * (stays H ini w).card ≤ -(2 - (2 : ℝ) ^ s) * 748 := by nlinarith
    have hk : keptCost (fun x : ℝ => x ^ s) dim H ini w = ((keptExp.map fun x : ℝ => x ^ s).sum) := by
      rw [keptCost_eq]; exact (hK.keptP.map _).sum_eq
    have hnk : Finv s nK22 = 748 * (2 : ℝ) ^ s - (968 + 366 * (2 : ℝ) ^ s + 103 * (3 : ℝ) ^ s + 127 * (4 : ℝ) ^ s
        + 147 * (5 : ℝ) ^ s + 10 * (6 : ℝ) ^ s + 1496) := by
      simp [Finv, Fh, nK22, Real.one_rpow]
      ring
    rw [hk, hnk]
    rw [keptExp_sum]
    simp only [Real.one_rpow]
    nlinarith
  have hc : (17 : ℕ) * Finv s n ≤ (17 : ℕ) * Finv s nK22 := by
    exact_mod_cast mul_le_mul_of_nonneg_left hn (by norm_num : (0 : ℝ) ≤ 17)
  push_cast at hc hnum' ⊢
  linarith

end ClassK22

end FloorK22

#print axioms FloorK22.entries_are_registers
#print axioms FloorK22.reentry_two_events
#print axioms FloorK22.R1Y_row
#print axioms FloorK22.stays_ge_748
#print axioms FloorK22.helperD0_ge_748
#print axioms FloorK22.keptExp_D0_le
#print axioms FloorK22.D0_K22
#print axioms FloorK22.recipe_as_written
#print axioms FloorK22.D0_of_stops
#print axioms FloorK22.D0_K22_R6
#print axioms FloorK22.helperF_le
#print axioms FloorK22.ceiling22
#print axioms FloorK22Data.forced_sum
#print axioms FloorK22Data.forced_by_dim
#print axioms FloorK22Data.control
#print axioms FloorK22Data.sums
