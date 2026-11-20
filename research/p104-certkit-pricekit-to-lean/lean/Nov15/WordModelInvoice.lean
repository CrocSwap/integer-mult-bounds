/-
WordModelInvoice (lane WORDMODEL, coordinator, Nov 18).  REPAIR after WM-AUDIT item 7: `FWword` passed full
paths AND −nStops·cstop (double charge).  Here:
* `FWreal` = the word's REAL invoice: full chart paths, every hop priced, NO stop term (pricekit: T = helper
  climbs, P = every MOVE; caller Dc as data).
* `FWcol`  = endpoint-collapsed invoice: one hop per register (start → end) + nst·cstop with
  nst = Σ (#hops − 1) = nStops.
* STOP-EXCESS lemma (`stop_excess`): for hops r_i ≥ 1 and s ∈ [0,1],
    Σ r_i^s ≥ (Σ r_i)^s + (m − 1)(2 − 2^s)
  (concavity of x^s: increments shrink), hence pcost(full path) ≥ d(start,end)^s + (m−1)·cstop, and
  FWreal ≤ FWcol (`real_le_col`).
* So the SAFE rungs bound every crossing of the REAL invoice: `P0_real`, `U0_real`.
Kernel only: no sorry, no native_decide, no axioms.
-/
import Nov15.WordModelSpec
import Mathlib.Data.List.GetD

set_option linter.unusedSectionVars false

namespace WordModel

open Finset SafeRungsClique SafeRungsPrice Module

/-! ## Stop-excess -/

theorem concave_inc {f : ℝ → ℝ} (hf : ConcaveOn ℝ (Set.Ici 0) f) {x y h : ℝ} (hx : 0 ≤ x) (hxy : x ≤ y)
    (hh : 0 ≤ h) : f (y + h) - f y ≤ f (x + h) - f x := by
  rcases eq_or_lt_of_le hh with rfl | hh'
  · simp
  have hD : 0 < y - x + h := by linarith
  set a := h / (y - x + h) with ha
  set b := (y - x) / (y - x + h) with hb
  have ha0 : 0 ≤ a := div_nonneg hh hD.le
  have hb0 : 0 ≤ b := div_nonneg (by linarith) hD.le
  have hab : a + b = 1 := by rw [ha, hb, ← add_div]; field_simp; ring
  have hX : x ∈ Set.Ici (0 : ℝ) := hx
  have hYH : y + h ∈ Set.Ici (0 : ℝ) := by simp only [Set.mem_Ici]; linarith
  have e1 : b • x + a • (y + h) = x + h := by
    simp only [smul_eq_mul, ha, hb]; field_simp; ring
  have e2 : a • x + b • (y + h) = y := by
    simp only [smul_eq_mul, ha, hb]; field_simp; ring
  have i1 := hf.2 hX hYH hb0 ha0 (by linarith)
  have i2 := hf.2 hX hYH ha0 hb0 hab
  rw [e1] at i1; rw [e2] at i2
  simp only [smul_eq_mul] at i1 i2
  have hb' : b = 1 - a := by linarith
  rw [hb'] at i1 i2
  have key : f x + f (y + h) ≤ f (x + h) + f y := by nlinarith [i1, i2]
  linarith

theorem merge_ge (s : ℝ) (hs0 : 0 ≤ s) (hs1 : s ≤ 1) {a b : ℝ} (ha : 1 ≤ a) (hb : 1 ≤ b) :
    (a + b) ^ s + cstop s ≤ a ^ s + b ^ s := by
  have hf := Real.concaveOn_rpow hs0 hs1
  have i1 := concave_inc hf (x := 1) (y := 1 + b) (h := a - 1) (by norm_num) (by linarith) (by linarith)
  have i2 := concave_inc hf (x := 1) (y := 2) (h := b - 1) (by norm_num) (by norm_num) (by linarith)
  simp only [Real.one_rpow] at i1 i2
  have e1 : (1 : ℝ) + b + (a - 1) = a + b := by ring
  have e2 : (1 : ℝ) + (a - 1) = a := by ring
  have e3 : (2 : ℝ) + (b - 1) = 1 + b := by ring
  have e4 : (1 : ℝ) + (b - 1) = b := by ring
  rw [e1, e2] at i1; rw [e3, e4] at i2
  unfold cstop; linarith

theorem stop_excess (s : ℝ) (hs0 : 0 ≤ s) (hs1 : s ≤ 1) (f : ℕ → ℝ) (hf : ∀ i, 1 ≤ f i) :
    ∀ n, 1 ≤ n → (∑ i ∈ range n, f i) ^ s + ((n : ℝ) - 1) * cstop s ≤ ∑ i ∈ range n, f i ^ s := by
  intro n hn
  induction n with
  | zero => omega
  | succ n ih =>
    rcases Nat.eq_zero_or_pos n with rfl | hpos
    · simp
    have ih' := ih hpos
    have hS : 1 ≤ ∑ i ∈ range n, f i := by
      calc (1 : ℝ) ≤ f 0 := hf 0
        _ ≤ ∑ i ∈ range n, f i := single_le_sum (fun i _ => le_trans zero_le_one (hf i))
            (mem_range.2 hpos)
    have hm := merge_ge s hs0 hs1 hS (hf n)
    rw [sum_range_succ, sum_range_succ]
    push_cast
    linarith

theorem path_excess {α : Type*} {d : α → α → ℝ} (hm : PriceMetric d) (s : ℝ) (hs0 : 0 ≤ s) (hs1 : s ≤ 1)
    (x : ℕ → α) (n : ℕ) (hn : 1 ≤ n) (hop : ∀ i < n, 1 ≤ d (x i) (x (i + 1))) :
    d (x 0) (x n) ^ s + ((n : ℝ) - 1) * cstop s ≤ pcost d x n s := by
  let f : ℕ → ℝ := fun i => if i < n then d (x i) (x (i + 1)) else 1
  have hf : ∀ i, 1 ≤ f i := by intro i; simp only [f]; split_ifs with h; exact hop i h; exact le_rfl
  have hsum : ∀ g : ℝ → ℝ, ∑ i ∈ range n, g (f i) = ∑ i ∈ range n, g (d (x i) (x (i + 1))) := by
    intro g; refine sum_congr rfl fun i hi => ?_; simp [f, mem_range.1 hi]
  have h1 := stop_excess s hs0 hs1 f hf n hn
  have h2 := hsum (fun v => v ^ s); have h3 := hsum (fun v => v)
  rw [h2, h3] at h1
  have h4 := Real.rpow_le_rpow (hm.nonneg _ _) (chain_le hm x n) hs0
  unfold pcost; linarith

/-! ## Hop and stop-count invariants -/

section Gen
variable {R : Type} [Fintype R] [DecidableEq R] (pb : R → Bool)

structure QInv (s : St R) : Prop where
  plogPub : ∀ m ∈ s.plog, pb m.1 = true
  aPub : ∀ r c, r ∈ s.A c → pb r = true
  aUnb : ∀ r c, s.loc r = .unborn → r ∉ s.A c
  aMv : ∀ r c, s.loc r = .sit c → (r ∈ s.A c ↔ mvs s r ≠ [])
  asc : ∀ r c0, r ∈ s.B c0 → ∀ i < (mvs s r).length, (c0 :: mvs s r).getD i ∅ < (c0 :: mvs s r).getD (i + 1) ∅
  cnt : s.slog.length = ∑ r, ((mvs s r).length - 1)

theorem mvs_nil_of_not_pub {s : St R} (hq : ∀ m ∈ s.plog, pb m.1 = true) {r : R} (hr : pb r = false) :
    mvs s r = [] := by
  simp only [mvs, List.reverse_eq_nil_iff, List.map_eq_nil_iff, List.filter_eq_nil_iff, decide_eq_true_eq]
  intro m hm he; rw [← he, hq m hm] at hr; cases hr

theorem qinv_init : QInv pb (init : St R) where
  plogPub := by intro m h; simp [init] at h
  aPub := by intro r c h; simp [init] at h
  aUnb := by intro r c _ h; simp [init] at h
  aMv := by intro r c h; simp [init] at h
  asc := by intro r c h; simp [init] at h
  cnt := by simp [init, mvs]

theorem step_qinv {s s' : St R} (hp : PInv pb s) (hs : QInv pb s) (h : Step pb s s') : QInv pb s' := by
  cases h with
  | birthPub r c hu hpb =>
    obtain ⟨hnB, hmv⟩ := hp.unb r hu
    refine ⟨hs.plogPub, hs.aPub, ?_, ?_, ?_, by simpa [mvs] using hs.cnt⟩
    · intro r' c' hl
      have hr : r' ≠ r := by rintro rfl; simp at hl
      simp only [Function.update_of_ne hr] at hl
      exact hs.aUnb r' c' hl
    · intro r' c' hl
      by_cases hr : r' = r
      · subst hr
        simp only [Function.update_self, Loc.sit.injEq] at hl; subst hl
        have : mvs s r' = [] := hmv
        simp only [mvs] at this ⊢
        simp [this, hs.aUnb r' _ hu]
      · simp only [Function.update_of_ne hr] at hl
        simpa [mvs] using hs.aMv r' c' hl
    · intro r' c0 hB i hi
      by_cases hr : r' = r
      · subst hr
        have : mvs s r' = [] := hmv
        simp only [mvs] at this hi
        simp [this] at hi
      · have hB' : r' ∈ s.B c0 := by
          by_cases hc : c0 = c
          · subst hc; simpa [hr] using hB
          · simpa [Function.update_of_ne hc] using hB
        simpa [mvs] using hs.asc r' c0 hB' i (by simpa [mvs] using hi)
  | birthOwn r c hu hpb =>
    obtain ⟨_, hmv⟩ := hp.unb r hu
    refine ⟨hs.plogPub, hs.aPub, ?_, ?_, by simpa [mvs] using hs.asc, by simpa [mvs] using hs.cnt⟩
    · intro r' c' hl
      have hr : r' ≠ r := by rintro rfl; simp at hl
      simp only [Function.update_of_ne hr] at hl
      exact hs.aUnb r' c' hl
    · intro r' c' hl
      by_cases hr : r' = r
      · subst hr
        have : mvs s r' = [] := hmv
        simp only [mvs] at this ⊢
        simp [this, hs.aUnb r' _ hu]
      · simp only [Function.update_of_ne hr] at hl
        simpa [mvs] using hs.aMv r' c' hl
  | gate r c coef hl =>
    exact ⟨hs.plogPub, hs.aPub, hs.aUnb, by simpa [mvs] using hs.aMv, by simpa [mvs] using hs.asc,
      by simpa [mvs] using hs.cnt⟩
  | movePub r c d hl hpb hlt =>
    have hmv : ∀ r', mvs ({ s with loc := Function.update s.loc r (.sit d), A := Function.update s.A d (insert r (s.A d)), eRow := fun r' c' => if r' = r ∧ c' = d then s.row r else s.eRow r' c', slog := if r ∈ s.A c then (r, c) :: s.slog else s.slog, plog := (r, c, d) :: s.plog } : St R) r' =
        if r = r' then mvs s r' ++ [d] else mvs s r' := by
      intro r'
      by_cases h : r = r'
      · subst h; simp [mvs]
      · simp [mvs, h]
    refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
    · intro m hm
      simp only [List.mem_cons] at hm
      rcases hm with rfl | hm
      · exact hpb
      · exact hs.plogPub m hm
    · intro r' c' h'
      by_cases hr : r' = r
      · subst hr; exact hpb
      · have h'' : r' ∈ s.A c' := by
          by_cases hc : c' = d
          · subst hc; simpa [hr] using h'
          · simpa [Function.update_of_ne hc] using h'
        exact hs.aPub r' c' h''
    · intro r' c' hl'
      have hr : r' ≠ r := by rintro rfl; simp at hl'
      simp only [Function.update_of_ne hr] at hl'
      by_cases hc : c' = d
      · subst hc; simpa [hr] using hs.aUnb r' c' hl'
      · simpa [Function.update_of_ne hc] using hs.aUnb r' c' hl'
    · intro r' c' hl'
      rw [hmv]
      by_cases hr : r' = r
      · subst hr
        simp only [Function.update_self, Loc.sit.injEq] at hl'; subst hl'
        simp
      · simp only [Function.update_of_ne hr] at hl'
        rw [if_neg (Ne.symm hr)]
        by_cases hc : c' = d
        · subst hc; simpa [hr] using hs.aMv r' c' hl'
        · simpa [Function.update_of_ne hc] using hs.aMv r' c' hl'
    · intro r' c0 hB i hi
      rw [hmv] at hi ⊢
      by_cases hr : r' = r
      · subst hr
        simp only [if_true] at hi ⊢
        have hlast := hp.last r' c0 hB
        rw [hl] at hlast
        simp only [Loc.sit.injEq] at hlast
        have hL : c0 :: (mvs s r' ++ [d]) = (c0 :: mvs s r') ++ [d] := rfl
        rw [hL]
        simp only [List.length_append, List.length_singleton] at hi
        rcases Nat.lt_or_ge i (mvs s r').length with h1 | h1
        · rw [List.getD_append _ _ _ _ (by simp; omega), List.getD_append _ _ _ _ (by simp; omega)]
          exact hs.asc r' c0 hB i h1
        · have hi' : i = (mvs s r').length := by omega
          subst hi'
          rw [List.getD_append _ _ _ _ (by simp), List.getD_append_right _ _ _ _ (by simp)]
          rw [getD_length_eq_getLast, ← hlast]
          simpa using hlt
      · rw [if_neg (Ne.symm hr)] at hi ⊢
        exact hs.asc r' c0 hB i hi
    · -- count: the moving register gains a stop iff it had moved before
      have hA : r ∈ s.A c ↔ mvs s r ≠ [] := hs.aMv r c hl
      have hsum : ∑ r', ((mvs ({ s with loc := Function.update s.loc r (.sit d), A := Function.update s.A d (insert r (s.A d)), eRow := fun r' c' => if r' = r ∧ c' = d then s.row r else s.eRow r' c', slog := if r ∈ s.A c then (r, c) :: s.slog else s.slog, plog := (r, c, d) :: s.plog } : St R) r').length - 1)
          = ∑ r' ∈ univ.erase r, ((mvs s r').length - 1) + (mvs s r).length := by
        rw [← Finset.sum_erase_add _ _ (Finset.mem_univ r)]
        congr 1
        · refine Finset.sum_congr rfl fun r' hr' => ?_
          rw [hmv, if_neg (Ne.symm (Finset.ne_of_mem_erase hr'))]
        · rw [hmv, if_pos rfl]; simp
      have hold : ∑ r', ((mvs s r').length - 1) = ∑ r' ∈ univ.erase r, ((mvs s r').length - 1) +
          ((mvs s r).length - 1) := (Finset.sum_erase_add _ _ (Finset.mem_univ r)).symm
      rw [hsum]
      by_cases hin : r ∈ s.A c
      · have hne := hA.1 hin
        have hpos : 1 ≤ (mvs s r).length := List.length_pos_iff.2 hne
        simp only [hin, if_true, List.length_cons]
        rw [hs.cnt, hold]; omega
      · have hnil : mvs s r = [] := by by_contra h; exact hin (hA.2 h)
        simp only [hin, if_false]
        rw [hs.cnt, hold, hnil]; simp
  | moveOwn r c d hl hpb =>
    have hnil : mvs s r = [] := mvs_nil_of_not_pub pb hs.plogPub hpb
    have hnA : ∀ c', r ∉ s.A c' := fun c' h => by rw [hs.aPub r c' h] at hpb; cases hpb
    refine ⟨hs.plogPub, hs.aPub, ?_, ?_, by simpa [mvs] using hs.asc, by simpa [mvs] using hs.cnt⟩
    · intro r' c' hl'
      have hr : r' ≠ r := by rintro rfl; simp at hl'
      simp only [Function.update_of_ne hr] at hl'
      exact hs.aUnb r' c' hl'
    · intro r' c' hl'
      by_cases hr : r' = r
      · subst hr
        simp only [mvs] at hnil ⊢
        simp [hnil, hnA]
      · simp only [Function.update_of_ne hr] at hl'
        simpa [mvs] using hs.aMv r' c' hl'
  | clearOwn r c hl hpb =>
    refine ⟨hs.plogPub, hs.aPub, ?_, ?_, by simpa [mvs] using hs.asc, by simpa [mvs] using hs.cnt⟩
    · intro r' c' hl'
      have hr : r' ≠ r := by rintro rfl; simp at hl'
      simp only [Function.update_of_ne hr] at hl'
      exact hs.aUnb r' c' hl'
    · intro r' c' hl'
      have hr : r' ≠ r := by rintro rfl; simp at hl'
      simp only [Function.update_of_ne hr] at hl'
      simpa [mvs] using hs.aMv r' c' hl'

theorem reach_qinv {s : St R} (h : Reach pb s) : PInv pb s ∧ QInv pb s := by
  induction h with
  | refl => exact ⟨pinv_init pb, qinv_init pb⟩
  | tail _ hst ih => exact ⟨step_pinv pb ih.1 hst, step_qinv pb ih.1 ih.2 hst⟩

theorem mem_mvs {s : St R} {r : R} {x : Ch} (h : x ∈ mvs s r) : ∃ m ∈ s.plog, m.2.2 = x := by
  simp only [mvs, List.mem_reverse, List.mem_map, List.mem_filter] at h
  obtain ⟨m, ⟨hm, _⟩, rfl⟩ := h
  exact ⟨m, hm, rfl⟩

end Gen

/-! ## The real and the collapsed invoice -/

variable {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow]
  [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]

/-- frames of public MOVE targets are spans (l.26-31), appended to FramesSubsp. -/
def PlogSubsp {R : Type} (s : St R) : Prop := ∀ m ∈ s.plog, IsSubsp m.2.2

/-- collapsed path: start, then end. -/
noncomputable def cpath (s : St (Reg Pt Hl Ow)) (r : Reg Pt Hl Ow) (i : ℕ) : Ch :=
  if i = 0 then path s r 0 else path s r (plen s r)
def clen (s : St (Reg Pt Hl Ow)) (r : Reg Pt Hl Ow) : ℕ := min (plen s r) 1

/-- stops of the collapsed invoice. -/
def nstC (cl : Caller Pt) (s : St (Reg Pt Hl Ow)) : ℕ :=
  ∑ r ∈ (helpers : Finset (Reg Pt Hl Ow)), (plen s r - 1) + ∑ r ∈ mains cl, (plen s r - 1)

/-- the REAL invoice of the word: full paths, every hop priced, no stop term. -/
noncomputable def FWreal (cl : Caller Pt) (s : St (Reg Pt Hl Ow)) (dc : Ch → Ch → ℝ) (σ : ℝ) : ℝ :=
  FW dc σ (helpers : Finset (Reg Pt Hl Ow)) (hcred s) (plen s) (path s) (mains cl) (plen s) (path s)
    (nOwned s) (oSrc s) (oTgt s) 0

/-- the endpoint-collapsed invoice. -/
noncomputable def FWcol (cl : Caller Pt) (s : St (Reg Pt Hl Ow)) (dc : Ch → Ch → ℝ) (σ : ℝ) : ℝ :=
  FW dc σ (helpers : Finset (Reg Pt Hl Ow)) (hcred s) (clen s) (cpath s) (mains cl) (clen s) (cpath s)
    (nOwned s) (oSrc s) (oTgt s) (nstC cl s)

theorem cpath_end (s : St (Reg Pt Hl Ow)) (r : Reg Pt Hl Ow) :
    cpath s r 0 = path s r 0 ∧ cpath s r (clen s r) = path s r (plen s r) := by
  refine ⟨by simp [cpath], ?_⟩
  unfold cpath clen
  by_cases h : plen s r = 0
  · rw [h]; simp
  · have : min (plen s r) 1 = 1 := by omega
    rw [this]; simp

/-- per register: full path cost ≥ collapsed cost + (#hops − 1)·cstop. -/
theorem reg_excess {dc : Ch → Ch → ℝ} (hm : PriceMetric dc) (σ : ℝ) (hs0 : 0 ≤ σ) (hs1 : σ ≤ 1)
    (s : St (Reg Pt Hl Ow)) (r : Reg Pt Hl Ow) (hop : ∀ i < plen s r, 1 ≤ dc (path s r i) (path s r (i + 1))) :
    pcost dc (cpath s r) (clen s r) σ + ((plen s r - 1 : ℕ) : ℝ) * cstop σ ≤ pcost dc (path s r) (plen s r) σ := by
  by_cases h : plen s r = 0
  · have hc : clen s r = 0 := by simp [clen, h]
    rw [hc, h]; simp [pcost]
  · have hc : clen s r = 1 := by unfold clen; omega
    have hx := path_excess hm σ hs0 hs1 (path s r) (plen s r) (by omega) hop
    rw [hc]
    have e : pcost dc (cpath s r) 1 σ = dc (path s r 0) (path s r (plen s r)) ^ σ := by
      simp [pcost, cpath]
    rw [e]
    have : ((plen s r - 1 : ℕ) : ℝ) = (plen s r : ℝ) - 1 := by
      rw [Nat.cast_sub (by omega)]; simp
    rw [this]; exact hx

/-- every hop of a public register's path costs ≥ 1 under the SPEC price. -/
theorem hops_ge_one {cl : Caller Pt} {s : St (Reg Pt Hl Ow)} (hw : Word cl s) (hfr : FramesSubsp s)
    (hpl : PlogSubsp s) (r : Reg Pt Hl Ow) (hp : pub cl r = true) :
    ∀ i < plen s r, 1 ≤ specPrice (path s r i) (path s r (i + 1)) := by
  obtain ⟨hP, hQ⟩ := reach_qinv (pub cl) hw.reach
  obtain ⟨c, hc⟩ := hw.pub_sit r hp
  obtain ⟨c0, h0⟩ := hP.born r c hp hc
  have hb : bch s r = c0 := by
    have h : ∃ c, r ∈ s.B c := ⟨c0, h0⟩
    simp only [bch, dif_pos h]
    exact hP.bu r _ _ (Classical.choose_spec h) h0
  have hsub : ∀ j ≤ plen s r, IsSubsp (path s r j) := by
    intro j hj
    rcases j with _ | j
    · simp only [path, hb, List.getD_cons_zero]; exact hfr.1 r c0 h0
    · simp only [path, hb, List.getD_cons_succ]
      have hj' : j < (mvs s r).length := by unfold plen at hj; omega
      rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hj', Option.getD_some]
      obtain ⟨m, hm, he⟩ := mem_mvs (List.getElem_mem hj')
      rw [← he]; exact hpl m hm
  intro i hi
  have hlt := hQ.asc r c0 h0 i hi
  have e : ∀ j, path s r j = (c0 :: mvs s r).getD j ∅ := by intro j; simp [path, hb]
  rw [e, e] at *
  exact specPrice_nested (by rw [← e]; exact hsub i hi.le) (by rw [← e]; exact hsub (i + 1) hi) (Or.inl hlt)

/-- non-public registers never make a public MOVE. -/
theorem plen_np {cl : Caller Pt} {s : St (Reg Pt Hl Ow)} (hw : Word cl s) (r : Reg Pt Hl Ow)
    (hp : pub cl r = false) : plen s r = 0 := by
  obtain ⟨_, hQ⟩ := reach_qinv (pub cl) hw.reach
  simp [plen, mvs_nil_of_not_pub (pub cl) hQ.plogPub hp]

theorem pub_mem {cl : Caller Pt} (r : Reg Pt Hl Ow) (hp : pub cl r = true) :
    r ∈ (helpers : Finset (Reg Pt Hl Ow)) ∪ mains cl := by
  rcases r with p|p|p|p|i|i <;> simp [pub, helpers, mains, Dset] at hp ⊢ <;> simp [hp]

theorem helpers_mains_disj (cl : Caller Pt) : Disjoint (helpers : Finset (Reg Pt Hl Ow)) (mains cl) := by
  rw [Finset.disjoint_left]; intro a h1 h2
  simp [helpers] at h1; obtain ⟨_, rfl⟩ := h1; simp [mains] at h2

/-- the collapsed stop count is the run's stop count. -/
theorem nstC_eq {cl : Caller Pt} {s : St (Reg Pt Hl Ow)} (hw : Word cl s) : nstC cl s = nStops s := by
  obtain ⟨_, hQ⟩ := reach_qinv (pub cl) hw.reach
  unfold nStops; rw [hQ.cnt, nstC, ← Finset.sum_union (helpers_mains_disj cl)]
  symm
  rw [← Finset.sum_subset (Finset.subset_univ _)]
  · rfl
  · intro r _ hr
    have : pub cl r = false := by
      cases h : pub cl r
      · rfl
      · exact absurd (pub_mem r h) hr
    have := plen_np hw r this
    simp [plen] at this; simp [this]

/-- **real ≤ collapsed**. -/
theorem real_le_col {cl : Caller Pt} {s : St (Reg Pt Hl Ow)} (hw : Word cl s) (hfr : FramesSubsp s)
    (hpl : PlogSubsp s) (σ : ℝ) (hs0 : 0 ≤ σ) (hs1 : σ ≤ 1) :
    FWreal cl s specPrice σ ≤ FWcol cl s specPrice σ := by
  have hex : ∀ r, pub cl r = true → pcost specPrice (cpath s r) (clen s r) σ +
      ((plen s r - 1 : ℕ) : ℝ) * cstop σ ≤ pcost specPrice (path s r) (plen s r) σ :=
    fun r hp => reg_excess specPrice_metric σ hs0 hs1 s r (hops_ge_one hw hfr hpl r hp)
  have hH : ∀ r ∈ (helpers : Finset (Reg Pt Hl Ow)), pub cl r = true := by
    intro r hr; simp [helpers] at hr; obtain ⟨_, rfl⟩ := hr; rfl
  have hM : ∀ r ∈ mains (Hl := Hl) (Ow := Ow) cl, pub cl r = true := by
    intro r hr
    simp only [mains, Dset, Finset.mem_union, Finset.mem_image, Finset.mem_univ, true_and,
      Finset.mem_filter] at hr
    rcases hr with ((⟨p, rfl⟩ | ⟨p, rfl⟩) | ⟨p, hD, rfl⟩) | ⟨p, hD, rfl⟩ <;> simp [pub, *]
  have sH := Finset.sum_le_sum fun r hr => hex r (hH r hr)
  have sM := Finset.sum_le_sum fun r hr => hex r (hM r hr)
  rw [Finset.sum_add_distrib] at sH sM
  rw [← Finset.sum_mul] at sH sM
  unfold FWreal FWcol FW nstC
  push_cast
  nlinarith [cstop_nonneg σ hs0 hs1]

/-! ## The SAFE rungs for the REAL invoice -/

theorem hH_col {cl : Caller Pt} {s : St (Reg Pt Hl Ow)} (hw : Word cl s) (hfr : FramesSubsp s) :
    ∀ i ∈ (helpers : Finset (Reg Pt Hl Ow)), hcred s i ≤ specPrice (cpath s i 0) (cpath s i (clen s i)) := by
  intro i hi; rw [(cpath_end s i).1, (cpath_end s i).2]; exact hH_spec hw hfr i hi

theorem hM_col {cl : Caller Pt} {s : St (Reg Pt Hl Ow)} (hw : Word cl s) (hfr : FramesSubsp s) :
    ∀ j ∈ mains cl, 1 ≤ clen s j ∧ 8 ≤ specPrice (cpath s j 0) (cpath s j (clen s j)) := by
  intro j hj
  obtain ⟨h1, h2⟩ := hM_spec hw hfr j hj
  refine ⟨by unfold clen; omega, ?_⟩
  rw [(cpath_end s j).1, (cpath_end s j).2]; exact h2

/-- **P0 for the REAL invoice** of every model word (96 D ports, frames = spans). -/
theorem P0_real {cl : Caller Pt} {s : St (Reg Pt Hl Ow)} (hw : Word cl s) (hD : DCount cl)
    (hfr : FramesSubsp s) (hpl : PlogSubsp s) (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ ≤ 1)
    (hF : 0 ≤ FWreal cl s specPrice (1 - κ)) : κ < 227043 / 10000000 :=
  SafeRungsExact.P0_kappa_exact specPrice_metric helpers (hcred s) (clen s) (cpath s) (mains cl) (clen s)
    (cpath s) (nOwned s) (oSrc s) (oTgt s) (nstC cl s) (hH_col hw hfr) (hM_col hw hfr) (mains_card cl hD)
    (Nat.cast_nonneg _) κ hκ0 hκ1 (hF.trans (real_le_col hw hfr hpl _ (by linarith) (by linarith)))

/-- **U0 for the REAL invoice**: adding owned nesting (l.51), κ < .0204111. -/
theorem U0_real {cl : Caller Pt} {s : St (Reg Pt Hl Ow)} (hw : Word cl s) (hD : DCount cl)
    (hfr : FramesSubsp s) (hpl : PlogSubsp s) (hnest : OwnedNested s) (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ ≤ 1)
    (hF : 0 ≤ FWreal cl s specPrice (1 - κ)) : κ < 204111 / 10000000 := by
  have hF' := hF.trans (real_le_col hw hfr hpl (1 - κ) (by linarith) (by linarith))
  have h16 := owned16 hw
  have hR3 : 104 - (nOwned s : ℝ) ≤ (nstC cl s : ℝ) := by rw [nstC_eq hw]; exact stops_ge hw
  refine kappa_lt (fun t => FWcol cl s specPrice (1 - t)) FceilU0 _ ?_ SafeRungsExact.certU0 κ hκ0 hκ1 hF'
  intro t ht0 ht1
  exact U0_ceiling specPrice_metric (1 - t) (by linarith) (by linarith) helpers (hcred s) (clen s) (cpath s)
    (mains cl) (clen s) (cpath s) (nOwned s) (oSrc s) (oTgt s) (nstC cl s) (hH_col hw hfr) (hM_col hw hfr)
    (mains_card cl hD) (Nat.cast_nonneg _) (hO1_spec hfr hnest) h16 hR3

/-- on a nested pair of subspace charts the SPEC price is the native MOVE price |Δdim| (pricekit P[rank]),
so `FWreal` under `specPrice` is pricekit's invoice for every legal (nested) word. -/
theorem specPrice_nested_eq {a b : Ch} (ha : IsSubsp a) (hb : IsSubsp b) (h : a < b) :
    specPrice a b = (dim b : ℝ) - dim a := by
  have hle := (toSub_lt ha hb h).le
  unfold specPrice latD
  rw [inf_eq_left.2 hle, dim_eq_finrank a ha, dim_eq_finrank b hb]; ring

end WordModel

#print axioms WordModel.stop_excess
#print axioms WordModel.real_le_col
#print axioms WordModel.P0_real
#print axioms WordModel.U0_real
#print axioms WordModel.specPrice_nested_eq
