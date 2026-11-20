/-
UniBank (lane UNI-L0L1, L1 → L2 hand-off, Nov 19).  The folded word as a BankFit.BankedGraph, up to the two
CALLER facts (principal minors of O, BankWireD.Contract), which are L2's job (CallerFacts for 7113).
* chart constants through the bridge: toSub zeroCh = ⊥, toSub (line q) = span{vec q}, toSub Vc = ⊤,
  toSub (Hq q) = ker (phi q)  (the shapes BankWireD.Contract.chartO/chartI ask for);
* `fold_nest`  : every bank of a legal word is nested (public MOVEs ascend; owned MOVEs by OwnedNested, l.51);
* `fold_main8` : every main field climbs 8;  `mainsF_card` : 400 main fields (DCount);
* `foldBanked` : BankedGraph from a legal Word + FramesSubsp + ChartsSubsp + OwnedNested + DCount + minors + Contract,
  with N = foldS, cl = fclimb, Mn = mainsF (so the banked flag/banner rungs apply to words verbatim once the 7113
  caller block is certified).
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.UniCredit
import Nov15.BankFitA

set_option linter.unusedSectionVars false

namespace Uni

open Finset Module WordModel SafeRungsPrice SafeRungsClique

/-! ## Chart constants through the bridge -/

theorem vec_eq_bank (n : ℕ) : BankWireC.vec n = WordModel.vec n := rfl

theorem toSub_zero : toSub zeroCh = ⊥ := by
  simp [toSub, zeroCh, vec_zero]

theorem toSub_line (q : ℕ) : toSub (line q) = Submodule.span (ZMod 2) {vec q} := by
  unfold toSub line
  rw [Finset.coe_insert, Finset.coe_singleton, Set.image_insert_eq, Set.image_singleton, vec_zero,
    Submodule.span_insert_zero]

theorem toSub_Vc : toSub Vc = ⊤ := by
  rw [eq_top_iff]
  intro v _
  obtain ⟨n, hn, rfl⟩ := vec_surj v
  exact Submodule.subset_span ⟨n, by simpa [Vc] using hn, rfl⟩

theorem par_wt : ∀ x < 512, ((List.range 9).filter (fun i => x.testBit i)).length % 2 = wt x % 2 := by
  decide +kernel

theorem phi_vec_dot {q n : ℕ} (hq : q < 512) (hn : n < 512) :
    BankWireC.phi q (vec n) = ((dot n q : ℕ) : ZMod 2) := by
  rw [← vec_eq_bank, BankWireC.phi_vec]
  congr 1
  unfold BankFlagB.par dot
  rw [Nat.land_comm q n]
  exact par_wt _ (Nat.and_lt_two_pow (n := 9) n (by simpa using hq) |>.trans_le (by norm_num))

theorem dot_lt_two (n q : ℕ) : dot n q < 2 := Nat.mod_lt _ (by norm_num)

theorem toSub_Hq {q : ℕ} (hq : q < 512) : toSub (Hq q) = LinearMap.ker (BankWireC.phi q) := by
  have hset : vec '' (↑(Hq q) : Set ℕ) = (LinearMap.ker (BankWireC.phi q) : Set V9) := by
    ext v
    obtain ⟨n, hn, rfl⟩ := vec_surj v
    simp only [Set.mem_image, Finset.mem_coe, SetLike.mem_coe, LinearMap.mem_ker]
    rw [phi_vec_dot hq hn]
    constructor
    · rintro ⟨m, hm, he⟩
      have hm' := Finset.mem_filter.1 hm
      have hm5 : m < 512 := Finset.mem_range.1 hm'.1
      rw [← vec_inj hm5 hn he, hm'.2]; simp
    · intro h
      refine ⟨n, Finset.mem_filter.2 ⟨Finset.mem_range.2 hn, ?_⟩, rfl⟩
      have h2 := dot_lt_two n q
      rcases (show dot n q = 0 ∨ dot n q = 1 by omega) with h0 | h1
      · exact h0
      · rw [h1] at h; exact absurd h (by decide)
  unfold toSub; rw [hset, Submodule.span_eq]

/-! ## Banked premises of the fold -/

section Legal
variable {R : Type} [Fintype R] [DecidableEq R] {pb : R → Bool}

theorem mlog_pub_asc (tr : Trace R) : ∀ s, LegalFrom pb s tr → ∀ m ∈ mlogFrom s tr, m.pubk = true → m.src < m.dst := by
  induction tr with
  | nil => intro s _ m hm; simp [mlogFrom] at hm
  | cons e tr ih =>
    intro s hl m hm hk
    simp only [mlogFrom, List.mem_append] at hm
    rcases hm with hm | hm
    · cases e with
      | movePub r c d => simp [Ev.mrec] at hm; subst hm; exact hl.1.2.2
      | moveOwn r c d => simp [Ev.mrec] at hm; subst hm; simp at hk
      | _ => simp [Ev.mrec] at hm
    · exact ih _ hl.2 m hm hk

theorem mlog_mem_logs (tr : Trace R) (m : MRec R) (hm : m ∈ mlog tr) :
    (m.pubk = true → (m.reg, m.src, m.dst) ∈ (exec tr).plog) ∧
      (m.pubk = false → (m.src, m.dst, m.row) ∈ (exec tr).olog) := by
  obtain ⟨h1, h2⟩ := run_logs tr init
  simp only [exec] at h1 h2 ⊢
  refine ⟨fun hk => ?_, fun hk => ?_⟩
  · rw [h1]; simp only [List.mem_append, List.mem_reverse, List.mem_map, List.mem_filter]
    exact Or.inl ⟨m, ⟨hm, hk⟩, rfl⟩
  · rw [h2]; simp only [List.mem_append, List.mem_reverse, List.mem_map, List.mem_filter]
    exact Or.inl ⟨m, ⟨hm, by simp [hk]⟩, rfl⟩

/-- **fold_nest**: every bank of a legal trace with subspace MOVE charts and nested owned MOVEs is nested. -/
theorem fold_nest {tr : Trace R} (h : Legal pb tr) (hcs : ChartsSubsp (exec tr)) (hn : OwnedNested (exec tr))
    (k : Fin (mlog tr).length) : (foldS h).src k ≤ (foldS h).dst k ∨ (foldS h).dst k ≤ (foldS h).src k := by
  show toSub (fsrc tr k) ≤ toSub (fdst tr k) ∨ toSub (fdst tr k) ≤ toSub (fsrc tr k)
  have hm : (mlog tr)[k.1] ∈ mlog tr := List.getElem_mem k.2
  obtain ⟨hp, ho⟩ := mlog_mem_logs tr _ hm
  unfold fsrc fdst
  cases hk : ((mlog tr)[k.1]).pubk
  · have hmo := ho hk
    obtain ⟨s1, s2⟩ := hcs.1 _ hmo
    rcases hn _ hmo with hlt | hlt
    · exact Or.inl ((toSub_le_iff s1 s2).2 hlt.le)
    · exact Or.inr ((toSub_le_iff s2 s1).2 hlt.le)
  · have hmp := hp hk
    obtain ⟨s1, s2⟩ := hcs.2 _ hmp
    exact Or.inl ((toSub_le_iff s1 s2).2 (mlog_pub_asc tr init h _ hm hk).le)

end Legal

section WordBank
variable {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow]
  [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]

theorem fA_eq {cl : Caller Pt} {tr : Trace (Reg Pt Hl Ow)} (h : Legal (pub cl) tr) {f : Fld (pub cl)} {c : Ch}
    (hb : f.1 ∈ (exec tr).B c) : fA tr f = c :=
  bch_eq (reach_pinv (pub cl) (reach_exec h)) hb

theorem fB_eq {cl : Caller Pt} {tr : Trace (Reg Pt Hl Ow)} {f : Fld (pub cl)} {c : Ch}
    (hl : (exec tr).loc f.1 = .sit c) : fB tr f = c := by
  show locCh ((exec tr).loc f.1) = c; rw [hl]; rfl

/-- **fold_main8**: every main field of a legal Word climbs exactly 8. -/
theorem fold_main8 (cl : Caller Pt) {tr : Trace (Reg Pt Hl Ow)} (h : Legal (pub cl) tr) (hw : Word cl (exec tr)) :
    ∀ f ∈ mainsF cl, fclimb cl tr f = 8 := by
  intro f hf
  have hm : f.1 ∈ mains cl := (mem_filter.1 hf).2
  have hne := fun p => lab_ne_zero cl p
  obtain ⟨r, hr⟩ := f
  simp only [mains, Dset, mem_union, mem_image, mem_univ, true_and, mem_filter] at hm
  unfold fclimb
  rcases hm with ((⟨p, rfl⟩ | ⟨p, rfl⟩) | ⟨p, hD, rfl⟩) | ⟨p, hD, rfl⟩
  · rw [fA_eq h (hw.x_birth p), fB_eq (hw.x_final p), dim_Vc, dim_line (hne p)]
  · rw [fA_eq h (hw.y_birth p), fB_eq (hw.y_final p), dim_Hq_lab, dim_zero]
  · rw [fA_eq h (hw.x2_birth p hD), fB_eq (hw.x2_final p hD), dim_Vc, dim_line (hne p)]
  · rw [fA_eq h (hw.y2_birth p hD), fB_eq (hw.y2_final p hD), dim_Hq_lab, dim_zero]

theorem mainsF_card (cl : Caller Pt) (hD : DCount cl) : (mainsF (Hl := Hl) (Ow := Ow) cl).card = 400 := by
  rw [← mains_card (Hl := Hl) (Ow := Ow) cl hD]
  refine Finset.card_bij (fun f _ => f.1) (fun f hf => (mem_filter.1 hf).2) (fun a _ b _ he => Subtype.ext he) ?_
  intro r hr
  have hp : r ∈ univ.filter (fun r : Reg Pt Hl Ow => pub cl r = true) := by
    rw [pub_filter]; exact mem_union_right _ hr
  exact ⟨⟨r, by simpa using hp⟩, mem_filter.2 ⟨mem_univ _, hr⟩, rfl⟩

/-- **foldBanked**: a legal 7113-contract word IS a banked graph, given the two caller facts (L2). -/
noncomputable def foldBanked (cl : Caller Pt) {tr : Trace (Reg Pt Hl Ow)} (h : Legal (pub cl) tr)
    (hw : Word cl (exec tr)) (hfr : FramesSubsp (exec tr)) (hcs : ChartsSubsp (exec tr))
    (hn : OwnedNested (exec tr)) (hD : DCount cl)
    (hminor : ∀ C : Finset (Fld (pub (Hl := Hl) (Ow := Ow) cl)),
      ((foldS h).O.submatrix (fun c : C => c.1) (fun c : C => c.1)).det ≠ 0)
    (hcon : BankWireD.Contract (foldS h)) :
    BankFit.BankedGraph ℚ (Fld (pub (Hl := Hl) (Ow := Ow) cl)) (Fin (mlog tr).length) where
  N := foldS h
  minors := hminor
  con := hcon
  nest := fold_nest h hcs hn
  cl := fclimb cl tr
  climb f := ⟨(fold_climb cl h hw hfr f).1, (fold_climb cl h hw hfr f).2.1⟩
  Mn := mainsF cl
  main8 := fold_main8 cl h hw
  card := mainsF_card cl hD

/-- the banked SPEC invoice of the folded word = the word's paid invoice (FWreal's paid part). -/
theorem foldBanked_paid (cl : Caller Pt) {tr : Trace (Reg Pt Hl Ow)} (h : Legal (pub cl) tr)
    (hw : Word cl (exec tr)) (hfr : FramesSubsp (exec tr)) (hcs : ChartsSubsp (exec tr))
    (hn : OwnedNested (exec tr)) (hD : DCount cl) hminor hcon (σ : ℝ) :
    ∑ k, BankPrem.specInvoice (foldBanked cl h hw hfr hcs hn hD hminor hcon) σ k
      = wordPaid cl (exec tr) specPrice σ := by
  rw [← fold_paid cl h]; rfl

end WordBank

end Uni

#print axioms Uni.toSub_Hq
#print axioms Uni.toSub_line
#print axioms Uni.toSub_Vc
#print axioms Uni.fold_nest
#print axioms Uni.fold_main8
#print axioms Uni.foldBanked
#print axioms Uni.foldBanked_paid
