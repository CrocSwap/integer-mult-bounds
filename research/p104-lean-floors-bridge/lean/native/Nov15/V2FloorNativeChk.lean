/-
V2FloorNativeChk (lane LEAN-NEXT21, Nov 16): the per-subspace check of the native route and its soundness.
NO native_decide in this file: it only DEFINES the Bool checks and proves  fullCheck d N T M = true → IntFeasible.
The native_decide instances are in V2FloorNativeRun.lean.

Check at a subspace of dimension n with membership table t (X role, 1 ≤ n ≤ 7):
 recsX = pairs with L ⊆ X ⊆ U (grouped by L);  for every b > n:  either the plain total Σ_{recsX} Σ_{k∈[n,b)} num ≤ T n b,
 or the relaxation  Σ_c topsum(M b c)(w_u : class c) ≤ T n b, where w_u is the weight of the distinct upper space u and
 M b c bounds how many class-c upper spaces contain a dim-b space (that bound is itself checked at every subspace, Y role).
-/
import Nov15.V2FloorNativeData
import Nov15.V2FloorNativeLists

namespace V2Floor
open Finset Module
set_option maxRecDepth 10000

abbrev Rec := ℕ × ℕ × List ℕ

def seg (nums : List ℕ) (a : ℕ) : ℕ → ℕ
  | 0 => 0
  | m + 1 => seg nums a m + nums.getD (a + m) 0

def recOf (d : List ℕ × List ℕ × List ℕ) : Rec := (tabOf (Lms d.1), tabOf (kerMs d.2.1), d.2.2)

def clsOf (u : ℕ) : ℕ := Nat.log2 ((List.range 512).countP (fun v => u.testBit v))

structure Pre where
  groups : List (ℕ × List Rec)
  uc : List (ℕ × ℕ)

def recsOfData (d : ℕ → List ℕ × List ℕ × List ℕ) (N : ℕ) : List Rec :=
  List.ofFn (fun p : Fin N => recOf (d p.val))

def mkPre (recs : List Rec) : Pre :=
  { groups := (recs.map (·.1)).eraseDups.map (fun lt => (lt, recs.filter (fun r => r.1 == lt)))
    uc := (recs.map (·.2.1)).eraseDups.map (fun u => (u, clsOf u)) }

def prepOK (d : ℕ → List ℕ × List ℕ × List ℕ) (N : ℕ) (pre : Pre) : Bool :=
  (List.range N).all (fun p => (d p).1.all (fun b => decide (b < 512))) &&
  (pre.groups.flatMap (·.2)).isPerm (recsOfData d N) &&
  pre.groups.all (fun g => g.2.all (fun r => r.1 == g.1)) &&
  decide ((pre.uc.map (·.1)).Nodup) &&
  (recsOfData d N).all (fun r => pre.uc.any (fun x => x.1 == r.2.1)) &&
  pre.uc.all (fun x => decide (x.2 < 10))

def Mget (M : List (List ℕ)) (b c : ℕ) : ℕ := (M.getD (b - 1) []).getD c 0

def recsX (pre : Pre) (xt : ℕ) : List Rec :=
  pre.groups.flatMap (fun g => if (g.1 &&& xt) == g.1 then g.2.filter (fun r => (xt &&& r.2.1) == xt) else [])

def fsum (a b : ℕ) (l : List Rec) : ℕ := (l.map (fun r => seg r.2.2 a (b - a))).sum

def wsum (R : List Rec) (a b u : ℕ) : ℕ := fsum a b (R.filter (fun r => r.2.1 == u))

def refined (M : List (List ℕ)) (pre : Pre) (R : List Rec) (a b : ℕ) : ℕ :=
  ((List.range 10).map (fun c =>
    topsum (Mget M b c) ((pre.uc.filter (fun x => x.2 == c)).map (fun x => wsum R a b x.1)))).sum

def xcheck (T : ℕ → ℕ → ℕ) (M : List (List ℕ)) (pre : Pre) (xt a : ℕ) : Bool :=
  decide (a < 1) || decide (7 < a) ||
  (List.range' (a + 1) (8 - a)).all (fun b =>
    decide (fsum a b (recsX pre xt) ≤ T a b) || decide (refined M pre (recsX pre xt) a b ≤ T a b))

def ycheck (M : List (List ℕ)) (uc : List (ℕ × ℕ)) (yt n : ℕ) : Bool :=
  decide (n < 1) || decide (8 < n) ||
  (List.range 10).all (fun c =>
    decide ((uc.filter (fun x => (x.2 == c) && ((yt &&& x.1) == yt))).length ≤ Mget M n c))

def nodeChk (T : ℕ → ℕ → ℕ) (M : List (List ℕ)) (pre : Pre) (ms : List ℕ) (n : ℕ) : Bool :=
  ycheck M pre.uc (tabOf ms) n && xcheck T M pre (tabOf ms) n

def fullCheck (d : ℕ → List ℕ × List ℕ × List ℕ) (N : ℕ) (T : ℕ → ℕ → ℕ) (M : List (List ℕ)) : Bool :=
  let pre := mkPre (recsOfData d N)
  prepOK d N pre && go' (nodeChk T M pre) 9 0 [0] 0 0

/-! ### core: the combinatorial bound on lists -/

theorem sum_map_le {α : Type*} (l : List α) (f g : α → ℕ) (h : ∀ x ∈ l, f x ≤ g x) :
    (l.map f).sum ≤ (l.map g).sum := by
  induction l with
  | nil => simp
  | cons a l ih =>
    simp only [List.map_cons, List.sum_cons]
    have := h a (by simp)
    have := ih (fun x hx => h x (by simp [hx]))
    omega

theorem recsX_eq (pre : Pre) (xt : ℕ) (hgrp : ∀ g ∈ pre.groups, ∀ r ∈ g.2, r.1 = g.1) :
    recsX pre xt = (pre.groups.flatMap (·.2)).filter (fun r => ((r.1 &&& xt) == r.1) && ((xt &&& r.2.1) == xt)) := by
  unfold recsX
  rw [List.filter_flatMap]
  apply List.flatMap_congr
  intro g hg
  by_cases hc : ((g.1 &&& xt) == g.1) = true
  · simp only [hc, if_true]
    apply List.filter_congr
    intro r hr
    rw [hgrp g hg r hr, hc]; simp
  · simp only [hc, if_false, Bool.false_eq_true]
    symm
    rw [List.filter_eq_nil_iff]
    intro r hr
    rw [hgrp g hg r hr]; simp [hc]

theorem and_sub {xt yt u : ℕ} (hxy : xt &&& yt = xt) (h : yt &&& u = yt) : xt &&& u = xt := by
  calc xt &&& u = (xt &&& yt) &&& u := by rw [hxy]
    _ = xt &&& (yt &&& u) := Nat.and_assoc _ _ _
    _ = xt := by rw [h, hxy]

theorem core (T : ℕ → ℕ → ℕ) (M : List (List ℕ)) (pre : Pre) (recs : List Rec) (xt yt a b : ℕ)
    (hperm : (pre.groups.flatMap (·.2)).Perm recs)
    (hgrp : ∀ g ∈ pre.groups, ∀ r ∈ g.2, r.1 = g.1)
    (hnd : (pre.uc.map (·.1)).Nodup) (hkeys : ∀ r ∈ recs, r.2.1 ∈ pre.uc.map (·.1))
    (hcls : ∀ x ∈ pre.uc, x.2 < 10) (hxy : xt &&& yt = xt) (hab : a < b) (ha1 : 1 ≤ a) (hb8 : b ≤ 8)
    (hX : xcheck T M pre xt a = true) (hY : ycheck M pre.uc yt b = true) :
    fsum a b (recs.filter (fun r => ((r.1 &&& xt) == r.1) && ((yt &&& r.2.1) == yt))) ≤ T a b := by
  set G := pre.groups.flatMap (·.2) with hG
  set R := recsX pre xt with hR
  have hRG : R = G.filter (fun r => ((r.1 &&& xt) == r.1) && ((xt &&& r.2.1) == xt)) := recsX_eq pre xt hgrp
  have e1 : fsum a b (recs.filter (fun r => ((r.1 &&& xt) == r.1) && ((yt &&& r.2.1) == yt))) =
      fsum a b (G.filter (fun r => ((r.1 &&& xt) == r.1) && ((yt &&& r.2.1) == yt))) := by
    unfold fsum
    exact (((hperm.filter _).map _).sum_eq).symm
  have e2 : G.filter (fun r => ((r.1 &&& xt) == r.1) && ((yt &&& r.2.1) == yt)) =
      R.filter (fun r => (yt &&& r.2.1) == yt) := by
    rw [hRG, List.filter_filter]
    apply List.filter_congr
    intro r _
    by_cases h1 : ((r.1 &&& xt) == r.1) = true
    · by_cases h2 : ((yt &&& r.2.1) == yt) = true
      · have h3 : ((xt &&& r.2.1) == xt) = true := by
          simp only [beq_iff_eq] at h2 ⊢; exact and_sub hxy h2
        simp [h1, h2, h3]
      · simp [h1, h2]
    · simp [h1]
  rw [e1, e2]
  have hb : b ∈ List.range' (a + 1) (8 - a) := List.mem_range'_1.2 ⟨by omega, by omega⟩
  unfold xcheck at hX
  simp only [Bool.or_eq_true, decide_eq_true_eq, List.all_eq_true] at hX
  have hX' : fsum a b R ≤ T a b ∨ refined M pre R a b ≤ T a b := by
    rcases hX with (h | h) | h
    · omega
    · omega
    · have := h b hb
      simpa only [Bool.or_eq_true, decide_eq_true_eq] using this
  rcases hX' with h | h
  · exact le_trans (sum_filter_le R _ _) h
  · refine le_trans ?_ h
    unfold ycheck at hY
    simp only [Bool.or_eq_true, decide_eq_true_eq, List.all_eq_true] at hY
    have hY' : ∀ c ∈ List.range 10, (pre.uc.filter (fun x => (x.2 == c) && ((yt &&& x.1) == yt))).length ≤ Mget M b c := by
      rcases hY with (h | h) | h
      · omega
      · omega
      · intro c hc; simpa using h c hc
    have hkeysF : ∀ r ∈ R.filter (fun r => (yt &&& r.2.1) == yt), r.2.1 ∈ pre.uc.map (·.1) := by
      intro r hr
      rw [List.mem_filter] at hr
      have : r ∈ G := by rw [hRG] at hr; exact (List.mem_filter.1 hr.1).1
      exact hkeys r (hperm.subset this)
    have hA : fsum a b (R.filter (fun r => (yt &&& r.2.1) == yt)) =
        ((pre.uc.map (·.1)).map (fun u => fsum a b
          ((R.filter (fun r => (yt &&& r.2.1) == yt)).filter (fun r => decide (r.2.1 = u))))).sum :=
      sum_group (κ := ℕ) (fun r : Rec => r.2.1) (fun r : Rec => seg r.2.2 a (b - a)) (pre.uc.map (fun x : ℕ × ℕ => x.1))
        (R.filter (fun r => (yt &&& r.2.1) == yt)) hnd hkeysF
    have hB : ∀ u, fsum a b ((R.filter (fun r => (yt &&& r.2.1) == yt)).filter (fun r => decide (r.2.1 = u))) =
        if (yt &&& u) == yt then wsum R a b u else 0 := by
      intro u
      by_cases hyu : ((yt &&& u) == yt) = true
      · rw [if_pos hyu]
        have : (R.filter (fun r => (yt &&& r.2.1) == yt)).filter (fun r => decide (r.2.1 = u)) =
            R.filter (fun r => r.2.1 == u) := by
          rw [List.filter_filter]
          apply List.filter_congr
          intro r _
          by_cases h : r.2.1 = u
          · subst h; simp [hyu]
          · simp [h]
        rw [this]; rfl
      · rw [if_neg hyu]
        have : (R.filter (fun r => (yt &&& r.2.1) == yt)).filter (fun r => decide (r.2.1 = u)) = [] := by
          rw [List.filter_eq_nil_iff]
          intro r hr hc
          have h1 := List.mem_filter.1 hr
          have hk : r.2.1 = u := by simpa using hc
          apply hyu; rw [← hk]; exact h1.2
        rw [this]; rfl
    have hA2 : fsum a b (R.filter (fun r => (yt &&& r.2.1) == yt)) =
        (pre.uc.map (fun x => if (yt &&& x.1) == yt then wsum R a b x.1 else 0)).sum := by
      rw [hA, List.map_map]
      congr 1
      apply List.map_congr_left
      intro x _
      exact hB x.1
    have hC := sum_group (fun x : ℕ × ℕ => x.2)
      (fun x : ℕ × ℕ => if (yt &&& x.1) == yt then wsum R a b x.1 else 0) (List.range 10) pre.uc
      List.nodup_range (fun x hx => List.mem_range.2 (hcls x hx))
    rw [hA2, hC]
    unfold refined
    apply sum_map_le
    intro c hc
    have hf : pre.uc.filter (fun x => decide (x.2 = c)) = pre.uc.filter (fun x => x.2 == c) :=
      List.filter_congr (by intro x _; rw [Bool.eq_iff_iff]; simp)
    have h1 : ((pre.uc.filter (fun x => decide (x.2 = c))).map
        (fun x : ℕ × ℕ => if (yt &&& x.1) == yt then wsum R a b x.1 else 0)).sum =
        (((pre.uc.filter (fun x => x.2 == c)).filter (fun x => (yt &&& x.1) == yt)).map
          (fun x => wsum R a b x.1)).sum := by
      rw [hf, sum_filter_map_ite (pre.uc.filter (fun x => x.2 == c))]
    rw [h1]
    apply top_le
    · exact (List.filter_sublist).map _
    · calc _ = (pre.uc.filter (fun x => (x.2 == c) && ((yt &&& x.1) == yt))).length := by
            rw [List.length_map, List.filter_filter]
            congr 1
            apply List.filter_congr
            intro x _
            simp [Bool.and_comm]
        _ ≤ _ := hY' c hc

theorem seg_eq (nums : List ℕ) (a : ℕ) : ∀ m, seg nums a m = ∑ k ∈ Finset.Ico a (a + m), nums.getD k 0 := by
  intro m
  induction m with
  | zero => simp [seg]
  | succ m ih =>
    rw [show a + (m + 1) = (a + m) + 1 by ring, Finset.sum_Ico_succ_top (by omega), ← ih]
    rfl

attribute [local instance] Classical.propDecidable

theorem sound_aux (d : ℕ → List ℕ × List ℕ × List ℕ) (N : ℕ) (T : ℕ → ℕ → ℕ) (M : List (List ℕ))
    (recs : List Rec) (hrecs : recs = List.ofFn (fun p : Fin N => recOf (d p.val))) (pre : Pre)
    (hmask : ∀ p, p < N → ∀ b ∈ (d p).1, b < 512)
    (hperm : (pre.groups.flatMap (·.2)).Perm recs)
    (hgrp : ∀ g ∈ pre.groups, ∀ r ∈ g.2, r.1 = g.1)
    (hnd : (pre.uc.map (·.1)).Nodup) (hkeys : ∀ r ∈ recs, r.2.1 ∈ pre.uc.map (·.1))
    (hcls : ∀ x ∈ pre.uc, x.2 < 10)
    (hgo : go' (nodeChk T M pre) 9 0 [0] 0 0 = true) :
    IntFeasible (fun p : Fin N => Lsub (d p.val).1) (fun p => Usub (d p.val).2.1)
      (fun p k => (d p.val).2.2.getD k 0) T := by
  have hall := enum_all' (nodeChk T M pre) hgo
  intro X Y hXY h1 h8
  obtain ⟨msX, nX, hRX, hdX, hcX⟩ := hall X
  obtain ⟨msY, nY, hRY, hdY, hcY⟩ := hall Y
  have hTX := RepT_of_Rep' hRX
  have hTY := RepT_of_Rep' hRY
  have hab : fdim X < fdim Y := Submodule.finrank_lt_finrank_of_lt hXY
  unfold nodeChk at hcX hcY
  simp only [Bool.and_eq_true] at hcX hcY
  rw [← hdX] at hcX
  rw [← hdY] at hcY
  have hxy : tabOf msX &&& tabOf msY = tabOf msX := (RepT_le_iff hTX hTY).1 hXY.le
  have hcore := core T M pre recs (tabOf msX) (tabOf msY) (fdim X) (fdim Y) hperm hgrp
    hnd hkeys hcls hxy hab h1 h8 hcX.2 hcY.1
  refine le_trans (le_of_eq ?_) hcore
  obtain ⟨F, hF⟩ : ∃ F : Fin N → Rec, F = fun p => recOf (d p.val) := ⟨_, rfl⟩
  have hFe : ∀ p, F p = recOf (d p.val) := fun p => by rw [hF]
  have hFp : ∀ p : Fin N, RepT (F p).1 (Lsub (d p.val).1) ∧ RepT (F p).2.1 (Usub (d p.val).2.1) := by
    intro p
    rw [hFe p]
    exact ⟨RepT_of_Rep' (Rep'_Lms _ (hmask p.val p.2)), RepT_of_Rep' (Rep'_kerMs _)⟩
  have hrecsF : recs = List.ofFn F := by rw [hrecs, hF]
  unfold fsum
  rw [sum_filter_map_ite, hrecsF, List.map_ofFn, List.sum_ofFn, Finset.sum_filter]
  apply Finset.sum_congr rfl
  intro p _
  have e1 : (Lsub (d p.val).1 ≤ X) ↔ ((F p).1 &&& tabOf msX == (F p).1) = true := by
    rw [beq_iff_eq]; exact RepT_le_iff (hFp p).1 hTX
  have e2 : (Y ≤ Usub (d p.val).2.1) ↔ ((tabOf msY &&& (F p).2.1) == tabOf msY) = true := by
    rw [beq_iff_eq]; exact RepT_le_iff hTY (hFp p).2
  have e3 : ∑ k ∈ Finset.Ico (fdim X) (fdim Y), (d p.val).2.2.getD k 0 =
      seg (F p).2.2 (fdim X) (fdim Y - fdim X) := by
    rw [seg_eq, show fdim X + (fdim Y - fdim X) = fdim Y by omega, hFe p]; rfl
  by_cases hc : (Lsub (d p.val).1 ≤ X ∧ Y ≤ Usub (d p.val).2.1)
  · rw [if_pos hc, e3]
    have : (((F p).1 &&& tabOf msX == (F p).1) && ((tabOf msY &&& (F p).2.1) == tabOf msY)) = true := by
      simp only [Bool.and_eq_true]; exact ⟨e1.1 hc.1, e2.1 hc.2⟩
    simp only [Function.comp_apply, this, if_true]
  · rw [if_neg hc]
    have : (((F p).1 &&& tabOf msX == (F p).1) && ((tabOf msY &&& (F p).2.1) == tabOf msY)) = false := by
      by_contra hne
      simp only [Bool.not_eq_false, Bool.and_eq_true] at hne
      exact hc ⟨e1.2 hne.1, e2.2 hne.2⟩
    simp only [Function.comp_apply, this]
    simp

theorem fullCheck_sound (d : ℕ → List ℕ × List ℕ × List ℕ) (N : ℕ) (T : ℕ → ℕ → ℕ) (M : List (List ℕ))
    (h : fullCheck d N T M = true) :
    IntFeasible (fun p : Fin N => Lsub (d p.val).1) (fun p => Usub (d p.val).2.1)
      (fun p k => (d p.val).2.2.getD k 0) T := by
  unfold fullCheck at h
  simp only [Bool.and_eq_true] at h
  obtain ⟨hprep, hgo⟩ := h
  generalize hrecs : recsOfData d N = recs at hprep hgo
  generalize hpre : mkPre recs = pre at hprep hgo
  unfold prepOK at hprep
  rw [hrecs] at hprep
  simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq, List.mem_range, beq_iff_eq] at hprep
  obtain ⟨⟨⟨⟨⟨hmask, hperm⟩, hgrp⟩, hnd⟩, hkeys⟩, hcls⟩ := hprep
  have hkeys' : ∀ r ∈ recs, r.2.1 ∈ pre.uc.map (·.1) := by
    intro r hr
    obtain ⟨x, hx, hxr⟩ := List.any_eq_true.1 (hkeys r hr)
    exact List.mem_map.2 ⟨x, hx, by simpa using hxr⟩
  exact sound_aux d N T M recs hrecs.symm pre
    (fun p hp b hb => by simpa using hmask p hp b hb) (List.isPerm_iff.1 hperm)
    (fun g hg r hr => by simpa using hgrp g hg r hr) (by simpa using hnd) hkeys'
    (fun x hx => by simpa using hcls x hx) hgo

end V2Floor
