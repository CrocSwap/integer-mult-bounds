/-
UniCredit (lane UNI-L0L1, stage L1 `fold_credit`, Nov 19).
The folded Net's helper credit (BankHelp.helperCredit on foldS, Mn = the 400 mains as fields) equals the word's
Theorem-K helper credit Σ_H gc σ (climb).  Needs: a legal Word end state, frames = spans (FramesSubsp), σ ≠ 0.
The climb is ≥ 0 automatically (public MOVEs strictly ascend: QInv.asc), so gc = climb^σ exactly.
Also `fold_climb`: every field of the fold is nested A ≤ B with finrank B = finrank A + climb (BankedGraph.climb).
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.UniTrace

set_option linter.unusedSectionVars false

namespace Uni

open Finset Module WordModel SafeRungsPrice SafeRungsClique

section
variable {R : Type} [Fintype R] [DecidableEq R] {pb : R → Bool}

/-- a public register's path start is contained in every later chart of its path (ascending MOVEs). -/
theorem path_start_sub {s : St R} (hq : QInv pb s) {r : R} {c0 : Ch} (h0 : r ∈ s.B c0) :
    ∀ i ≤ (mvs s r).length, c0 ⊆ (c0 :: mvs s r).getD i ∅ := by
  intro i
  induction i with
  | zero => intro _; simp
  | succ i ih =>
    intro hi
    exact (ih (by omega)).trans (hq.asc r c0 h0 i (by omega)).le

theorem dim_mono {a b : Ch} (h : a ⊆ b) : dim a ≤ dim b :=
  Nat.log_mono_right (Finset.card_le_card h)

/-- endpoints of a sitting public register: birth chart ⊆ final chart, both from the path. -/
theorem pub_ends {s : St R} (hr : Reach pb s) {r : R} (hp : pb r = true) {c : Ch} (hl : s.loc r = .sit c) :
    ∃ c0, r ∈ s.B c0 ∧ bch s r = c0 ∧ path s r (plen s r) = c ∧ c0 ⊆ c := by
  obtain ⟨hs, hq⟩ := reach_qinv pb hr
  obtain ⟨c0, h0⟩ := hs.born r c hp hl
  obtain ⟨e0, e1⟩ := path_ends pb hs h0
  rw [hl] at e1
  have hc : path s r (plen s r) = c := (Loc.sit.inj e1).symm
  refine ⟨c0, h0, bch_eq hs h0, hc, ?_⟩
  have := path_start_sub hq h0 (plen s r) le_rfl
  rw [← hc]; simpa [path, plen, bch_eq hs h0] using this

end

section WordCred
variable {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow]
  [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]

/-- the 400 mains as fields of the fold. -/
def mainsF (cl : Caller Pt) : Finset (Fld (pub (Hl := Hl) (Ow := Ow) cl)) :=
  univ.filter (fun f => f.1 ∈ mains cl)

/-- the per-field climb read off the fold (dim final − dim birth). -/
noncomputable def fclimb (cl : Caller Pt) (tr : Trace (Reg Pt Hl Ow)) (f : Fld (pub (Hl := Hl) (Ow := Ow) cl)) : ℕ :=
  dim (fB tr f) - dim (fA tr f)

/-- per field: nested endpoints, finrank = dim, climb as a natural number (BankedGraph.climb shape). -/
theorem fold_climb (cl : Caller Pt) {tr : Trace (Reg Pt Hl Ow)} (h : Legal (pub cl) tr) (hw : Word cl (exec tr))
    (hfr : FramesSubsp (exec tr)) (f : Fld (pub cl)) :
    (foldS h).A f ≤ (foldS h).B f ∧
      finrank (ZMod 2) ((foldS h).B f) = finrank (ZMod 2) ((foldS h).A f) + fclimb cl tr f ∧
      (fclimb cl tr f : ℝ) = hcred (exec tr) f.1 := by
  obtain ⟨c, hl⟩ := hw.pub_sit f.1 f.2
  obtain ⟨c0, h0, hb, hpe, hsub⟩ := pub_ends hw.reach f.2 hl
  have hA : (foldS h).A f = toSub c0 := by
    show toSub (bch (exec tr) f.1) = toSub c0; rw [hb]
  have hB : (foldS h).B f = toSub c := by
    show toSub (locCh ((exec tr).loc f.1)) = toSub c; rw [hl]; rfl
  have s0 : IsSubsp c0 := hfr.1 f.1 c0 h0
  have s1 : IsSubsp c := hfr.2.1 f.1 c hl
  have hfA : fA tr f = c0 := hb
  have hfB : fB tr f = c := by show locCh ((exec tr).loc f.1) = c; rw [hl]; rfl
  have hdm := dim_mono hsub
  refine ⟨?_, ?_, ?_⟩
  · rw [hA, hB]; exact (toSub_le_iff s0 s1).2 hsub
  · rw [hA, hB, ← dim_eq_finrank c0 s0, ← dim_eq_finrank c s1, fclimb, hfA, hfB]; omega
  · rw [fclimb, hfA, hfB, hcred, hpe, Nat.cast_sub hdm]
    have : path (exec tr) f.1 0 = c0 := by simp [path, hb]
    rw [this]

/-- **fold_credit**: the folded Net's helper credit = the word's Theorem-K helper credit. -/
theorem fold_credit (cl : Caller Pt) {tr : Trace (Reg Pt Hl Ow)} (h : Legal (pub cl) tr) (hw : Word cl (exec tr))
    (hfr : FramesSubsp (exec tr)) {σ : ℝ} (hσ : σ ≠ 0) :
    BankHelp.helperCredit (foldS h) σ (mainsF cl) =
      ∑ i ∈ (helpers : Finset (Reg Pt Hl Ow)), gc σ (hcred (exec tr) i) := by
  unfold BankHelp.helperCredit
  -- per field: dh^σ = gc σ climb
  have hterm : ∀ f : Fld (pub cl),
      ((BankNC0.dh (finrank (ZMod 2) ((foldS h).A f)) (finrank (ZMod 2) ((foldS h).B f)) : ℕ) : ℝ) ^ σ
        = gc σ (hcred (exec tr) f.1) := by
    intro f
    obtain ⟨-, h2, h3⟩ := fold_climb cl h hw hfr f
    have hdh : BankNC0.dh (finrank (ZMod 2) ((foldS h).A f)) (finrank (ZMod 2) ((foldS h).B f)) = fclimb cl tr f := by
      unfold BankNC0.dh; rw [h2, Nat.cast_add, sub_add_cancel_left, Int.natAbs_neg, Int.natAbs_natCast]
    rw [hdh, ← h3, gc]
    split_ifs with hc
    · have : (fclimb cl tr f : ℝ) = 0 := le_antisymm hc (Nat.cast_nonneg _)
      rw [this, Real.zero_rpow hσ]
    · rfl
  simp_rw [hterm]
  refine Finset.sum_bij (fun f _ => f.1) ?_ ?_ ?_ ?_
  · intro f hf
    have hm : f.1 ∉ mains cl := by simpa [mainsF] using hf
    have hp : f.1 ∈ univ.filter (fun r : Reg Pt Hl Ow => pub cl r = true) := by simpa using f.2
    rw [pub_filter, mem_union] at hp
    exact hp.resolve_right hm
  · intro a _ b _ he; exact Subtype.ext he
  · intro i hi
    have hp : i ∈ univ.filter (fun r : Reg Pt Hl Ow => pub cl r = true) := by
      rw [pub_filter]; exact mem_union_left _ hi
    have hm : i ∉ mains cl := Finset.disjoint_left.1 (helpers_mains_disj cl) hi
    exact ⟨⟨i, by simpa using hp⟩, by simpa [mainsF] using hm, rfl⟩
  · intro f _; rfl

end WordCred

end Uni

#print axioms Uni.fold_climb
#print axioms Uni.fold_credit
