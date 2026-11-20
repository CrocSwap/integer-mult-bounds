/-
UniTrace (lane UNI-L0L1, stage L1 TRACE+FOLD, Nov 19).  cards/WILD/UNIMODEL/ARCH.md, UM.md.
Words and banked graphs are ONE model: a legal word run, read as a TIME-ORDERED trace, folds to a BankNC0.Net whose
invoice is EQUAL to the word's real invoice (WordModelInvoice.FWreal).
* `Ev`, `Ev.apply`, `Ev.ok`, `step_iff` : WordModelDefs.Step = one event (explicit move index = position in the trace).
* `Trace`, `exec`, `Legal`, `reach_iff` : Reach pb s ↔ ∃ legal trace tr, exec tr = s.
* `mlog tr` : the time-ordered bank list (every MOVE, public AND owned, one bank: kind, register, src, dst, moved row);
  `run_logs`: plog / olog of the end state are its two kind-filters (the global order St forgets).
* `fold tr h : BankNC0.Net ℚ Ch (Fld pb) (Fin #banks)` : fields = public registers, A = birth chart, B = final chart,
  d k = moved row at bank k (restricted to the public coordinates), O = final rows.
  `fold_read` / `fold_out` = Net.read / Net.out (time-stamped CSEntry / CSFinal); `foldS` = same Net on
  Uni.Chart (submodules) through the L0 bridge.
* `fold_paid` : Σ_k dc(src k, dst k)^σ = wordPaid (all public paths priced hop by hop + every owned MOVE), ANY price dc;
  `FWreal_eq` : FWreal = Dc + 17 (Σ_H gc − wordPaid), hence FWreal is the folded Net's invoice EXACTLY.
* `fold_credit` : BankHelp.helperCredit (foldS) σ (mains) = Σ_H gc σ (climb) (Theorem-K helper credit), frames = spans.
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.UniChart
import Nov15.WordModelInvoice
import Nov15.BankHelpA

set_option linter.unusedSectionVars false

namespace Uni

open Finset Module WordModel SafeRungsPrice SafeRungsClique

/-! ## Events and traces -/

inductive Ev (R : Type) where
  | birthPub (r : R) (c : Ch)
  | birthOwn (r : R) (c : Ch)
  | gate (r : R) (c : Ch) (coef : R → ℚ)
  | movePub (r : R) (c d : Ch)
  | moveOwn (r : R) (c d : Ch)
  | clearOwn (r : R) (c : Ch)

section Trace
variable {R : Type} [Fintype R] [DecidableEq R]

/-- the post-state of an event (WordModelDefs.Step's right-hand sides, verbatim). -/
def Ev.apply (s : St R) : Ev R → St R
  | .birthPub r c => ⟨Function.update s.loc r (.sit c), Function.update s.row r (Pi.single r 1),
      Function.update s.B c (insert r (s.B c)), s.A, s.eRow, s.olog, s.slog, s.plog⟩
  | .birthOwn r c => ⟨Function.update s.loc r (.sit c), Function.update s.row r 0,
      s.B, s.A, s.eRow, s.olog, s.slog, s.plog⟩
  | .gate r c coef => ⟨s.loc,
      Function.update s.row r (∑ t ∈ univ.filter (fun t => s.loc t = .sit c), coef t • s.row t),
      s.B, s.A, s.eRow, s.olog, s.slog, s.plog⟩
  | .movePub r c d => ⟨Function.update s.loc r (.sit d), s.row, s.B, Function.update s.A d (insert r (s.A d)),
      (fun r' c' => if r' = r ∧ c' = d then s.row r else s.eRow r' c'), s.olog,
      (if r ∈ s.A c then (r, c) :: s.slog else s.slog), (r, c, d) :: s.plog⟩
  | .moveOwn r c d => ⟨Function.update s.loc r (.sit d), s.row, s.B, s.A, s.eRow, (c, d, s.row r) :: s.olog,
      s.slog, s.plog⟩
  | .clearOwn r _ => ⟨Function.update s.loc r .cleared, Function.update s.row r 0, s.B, s.A, s.eRow, s.olog,
      s.slog, s.plog⟩

/-- the event's precondition (WordModelDefs.Step's hypotheses). -/
def Ev.ok (pb : R → Bool) (s : St R) : Ev R → Prop
  | .birthPub r _ => s.loc r = .unborn ∧ pb r = true
  | .birthOwn r _ => s.loc r = .unborn ∧ pb r = false
  | .gate r c _ => s.loc r = .sit c
  | .movePub r c d => s.loc r = .sit c ∧ pb r = true ∧ c < d
  | .moveOwn r c _ => s.loc r = .sit c ∧ pb r = false
  | .clearOwn r c => s.loc r = .sit c ∧ pb r = false

theorem step_iff (pb : R → Bool) (s s' : St R) : Step pb s s' ↔ ∃ e : Ev R, e.ok pb s ∧ s' = e.apply s := by
  constructor
  · intro h
    cases h with
    | birthPub r c h1 h2 => exact ⟨.birthPub r c, ⟨h1, h2⟩, rfl⟩
    | birthOwn r c h1 h2 => exact ⟨.birthOwn r c, ⟨h1, h2⟩, rfl⟩
    | gate r c coef h1 => exact ⟨.gate r c coef, h1, rfl⟩
    | movePub r c d h1 h2 h3 => exact ⟨.movePub r c d, ⟨h1, h2, h3⟩, rfl⟩
    | moveOwn r c d h1 h2 => exact ⟨.moveOwn r c d, ⟨h1, h2⟩, rfl⟩
    | clearOwn r c h1 h2 => exact ⟨.clearOwn r c, ⟨h1, h2⟩, rfl⟩
  · rintro ⟨e, he, rfl⟩
    cases e with
    | birthPub r c => exact Step.birthPub s r c he.1 he.2
    | birthOwn r c => exact Step.birthOwn s r c he.1 he.2
    | gate r c coef => exact Step.gate s r c coef he
    | movePub r c d => exact Step.movePub s r c d he.1 he.2.1 he.2.2
    | moveOwn r c d => exact Step.moveOwn s r c d he.1 he.2
    | clearOwn r c => exact Step.clearOwn s r c he.1 he.2

abbrev Trace (R : Type) := List (Ev R)

/-- run a trace from s. -/
def run (s : St R) (tr : Trace R) : St R := tr.foldl Ev.apply s

/-- the end state of a trace from `init`. -/
def exec (tr : Trace R) : St R := run init tr

/-- every event legal at its prefix state. -/
def LegalFrom (pb : R → Bool) : St R → Trace R → Prop
  | _, [] => True
  | s, e :: tr => e.ok pb s ∧ LegalFrom pb (e.apply s) tr

def Legal (pb : R → Bool) (tr : Trace R) : Prop := LegalFrom pb init tr

theorem legalFrom_snoc (pb : R → Bool) (tr : Trace R) (e : Ev R) :
    ∀ s, LegalFrom pb s (tr ++ [e]) ↔ LegalFrom pb s tr ∧ e.ok pb (run s tr) := by
  induction tr with
  | nil => intro s; simp [LegalFrom, run]
  | cons e' tr ih =>
    intro s
    simp only [List.cons_append, LegalFrom, run, List.foldl_cons]
    rw [ih]; simp only [run]; tauto

theorem rtg_of_legalFrom (pb : R → Bool) (tr : Trace R) :
    ∀ s, LegalFrom pb s tr → Relation.ReflTransGen (Step pb) s (run s tr) := by
  induction tr with
  | nil => intro s _; exact Relation.ReflTransGen.refl
  | cons e tr ih =>
    intro s h
    exact Relation.ReflTransGen.head ((step_iff pb _ _).2 ⟨e, h.1, rfl⟩) (ih _ h.2)

/-- **reach_iff**: reachable states are exactly the end states of legal traces. -/
theorem reach_iff (pb : R → Bool) (s : St R) : Reach pb s ↔ ∃ tr, Legal pb tr ∧ exec tr = s := by
  constructor
  · intro h
    induction h with
    | refl => exact ⟨[], trivial, rfl⟩
    | tail _ hst ih =>
      obtain ⟨tr, hl, rfl⟩ := ih
      obtain ⟨e, he, rfl⟩ := (step_iff pb _ _).1 hst
      refine ⟨tr ++ [e], (legalFrom_snoc pb tr e init).2 ⟨hl, he⟩, ?_⟩
      simp [exec, run, List.foldl_append]
  · rintro ⟨tr, hl, rfl⟩
    exact rtg_of_legalFrom pb tr init hl

theorem reach_exec {pb : R → Bool} {tr : Trace R} (h : Legal pb tr) : Reach pb (exec tr) :=
  (reach_iff pb _).2 ⟨tr, h, rfl⟩

/-! ## The time-ordered bank list -/

/-- one bank: kind (true = public MOVE), register, source chart, target chart, the moved row. -/
structure MRec (R : Type) where
  pubk : Bool
  reg : R
  src : Ch
  dst : Ch
  row : R → ℚ

def Ev.mrec (s : St R) : Ev R → List (MRec R)
  | .movePub r c d => [⟨true, r, c, d, s.row r⟩]
  | .moveOwn r c d => [⟨false, r, c, d, s.row r⟩]
  | _ => []

/-- the banks of a trace from s, oldest first. -/
def mlogFrom : St R → Trace R → List (MRec R)
  | _, [] => []
  | s, e :: tr => e.mrec s ++ mlogFrom (e.apply s) tr

def mlog (tr : Trace R) : List (MRec R) := mlogFrom init tr

/-- the chart pair of a MOVE event (syntactic). -/
def Ev.mvCh : Ev R → Option (Ch × Ch)
  | .movePub _ c d => some (c, d)
  | .moveOwn _ c d => some (c, d)
  | _ => none

/-- the banks' chart pairs are read off the trace syntactically (the um3 control extracts exactly these). -/
theorem mlog_charts (tr : Trace R) : ∀ s, (mlogFrom s tr).map (fun m => (m.src, m.dst)) = tr.filterMap Ev.mvCh := by
  induction tr with
  | nil => intro s; rfl
  | cons e tr ih =>
    intro s
    cases e <;> simp [mlogFrom, Ev.mrec, Ev.mvCh, ih, List.filterMap_cons]

/-- the end state's public / owned MOVE logs are the two kind-filters of the bank list (newest first). -/
theorem run_logs (tr : Trace R) : ∀ s,
    (run s tr).plog = (((mlogFrom s tr).filter (fun m => m.pubk)).map (fun m => (m.reg, m.src, m.dst))).reverse
      ++ s.plog ∧
    (run s tr).olog = (((mlogFrom s tr).filter (fun m => !m.pubk)).map (fun m => (m.src, m.dst, m.row))).reverse
      ++ s.olog := by
  induction tr with
  | nil => intro s; simp [run, mlogFrom]
  | cons e tr ih =>
    intro s
    obtain ⟨h1, h2⟩ := ih (e.apply s)
    simp only [run, List.foldl_cons] at h1 h2 ⊢
    rw [h1, h2]
    cases e <;> simp [mlogFrom, Ev.mrec, Ev.apply]

/-! ## Span invariant (time-stamped CSFinal) -/

/-- unit rows of registers born at c. -/
def units (B : Ch → Finset R) (c : Ch) : Set (R → ℚ) := {v | ∃ g ∈ B c, v = Pi.single g 1}
/-- rows delivered into c by the banks M. -/
def rowsTo (M : List (MRec R)) (c : Ch) : Set (R → ℚ) := {v | ∃ m ∈ M, m.dst = c ∧ v = m.row}
/-- the content of chart c. -/
def Gs (B : Ch → Finset R) (M : List (MRec R)) (c : Ch) : Submodule ℚ (R → ℚ) :=
  Submodule.span ℚ (units B c ∪ rowsTo M c)

theorem Gs_mono {B B' : Ch → Finset R} {M M' : List (MRec R)} {c : Ch} (hB : B c ⊆ B' c)
    (hM : ∀ m ∈ M, m ∈ M') : Gs B M c ≤ Gs B' M' c := by
  apply Submodule.span_mono
  rintro v (⟨g, hg, rfl⟩ | ⟨m, hm, h1, rfl⟩)
  · exact Or.inl ⟨g, hB hg, rfl⟩
  · exact Or.inr ⟨m, hM m hm, h1, rfl⟩

/-- every register sitting at c carries a row of c's content. -/
def SInv (s : St R) (M : List (MRec R)) : Prop := ∀ r c, s.loc r = .sit c → s.row r ∈ Gs s.B M c

/-- every bank reads its source chart's content at its time (prefix-decomposition form). -/
def Good (Bf : Ch → Finset R) (L : List (MRec R)) : Prop :=
  ∀ L1 m L2, L = L1 ++ m :: L2 → m.row ∈ Gs Bf L1 m.src

theorem good_nil (Bf : Ch → Finset R) : Good Bf [] := by
  intro L1 m L2 h; simp at h

theorem good_snoc {Bf : Ch → Finset R} {M : List (MRec R)} {m : MRec R} (hg : Good Bf M)
    (hm : m.row ∈ Gs Bf M m.src) : Good Bf (M ++ [m]) := by
  intro L1 m0 L2 h
  rcases List.eq_nil_or_concat L2 with rfl | ⟨L2', b, rfl⟩
  · obtain ⟨h1, h2⟩ := List.append_inj' h (by simp)
    simp only [List.cons.injEq, and_true] at h2
    subst h1; subst h2; exact hm
  · have h' : M ++ [m] = (L1 ++ m0 :: L2') ++ [b] := by rw [h]; simp
    obtain ⟨h1, -⟩ := List.append_inj' h' (by simp)
    exact hg L1 m0 L2' h1

theorem B_sub_apply (s : St R) (e : Ev R) (c : Ch) : s.B c ⊆ (e.apply s).B c := by
  cases e with
  | birthPub r c0 =>
    intro x hx
    simp only [Ev.apply]
    by_cases h : c = c0
    · subst h; simp [hx]
    · rw [Function.update_of_ne h]; exact hx
  | _ => intro x hx; simpa [Ev.apply] using hx

theorem B_sub_run (tr : Trace R) : ∀ s c, s.B c ⊆ (run s tr).B c := by
  induction tr with
  | nil => intro s c; exact subset_rfl
  | cons e tr ih => intro s c; exact (B_sub_apply s e c).trans (ih _ c)

theorem sinv_step (pb : R → Bool) {s : St R} {M : List (MRec R)} {e : Ev R} (he : e.ok pb s) (h : SInv s M) :
    SInv (e.apply s) (M ++ e.mrec s) := by
  have hM : ∀ m ∈ M, m ∈ M ++ e.mrec s := fun m hm => List.mem_append_left _ hm
  intro r' c' hl
  cases e with
  | birthPub r c =>
    simp only [Ev.apply] at hl ⊢
    by_cases hr : r' = r
    · subst hr
      simp only [Function.update_self, Loc.sit.injEq] at hl ⊢
      subst hl
      exact Submodule.subset_span (Or.inl ⟨r', by simp, rfl⟩)
    · rw [Function.update_of_ne hr] at hl ⊢
      exact Gs_mono (B_sub_apply s (.birthPub r c) c') hM (h r' c' hl)
  | birthOwn r c =>
    simp only [Ev.apply] at hl ⊢
    by_cases hr : r' = r
    · subst hr; simp only [Function.update_self]; exact Submodule.zero_mem _
    · rw [Function.update_of_ne hr] at hl ⊢
      exact Gs_mono subset_rfl hM (h r' c' hl)
  | gate r c coef =>
    simp only [Ev.apply] at hl ⊢
    by_cases hr : r' = r
    · subst hr
      simp only [Function.update_self]
      have hc : c' = c := by rw [he] at hl; exact (Loc.sit.inj hl).symm
      subst hc
      refine Submodule.sum_mem _ (fun t ht => Submodule.smul_mem _ _ ?_)
      exact Gs_mono subset_rfl hM (h t _ (mem_filter.1 ht).2)
    · rw [Function.update_of_ne hr]
      exact Gs_mono subset_rfl hM (h r' c' hl)
  | movePub r c d =>
    simp only [Ev.apply, Ev.mrec] at hl ⊢
    by_cases hr : r' = r
    · subst hr
      simp only [Function.update_self, Loc.sit.injEq] at hl
      subst hl
      exact Submodule.subset_span (Or.inr ⟨_, List.mem_append_right _ (List.mem_singleton_self _), rfl, rfl⟩)
    · rw [Function.update_of_ne hr] at hl
      exact Gs_mono subset_rfl hM (h r' c' hl)
  | moveOwn r c d =>
    simp only [Ev.apply, Ev.mrec] at hl ⊢
    by_cases hr : r' = r
    · subst hr
      simp only [Function.update_self, Loc.sit.injEq] at hl
      subst hl
      exact Submodule.subset_span (Or.inr ⟨_, List.mem_append_right _ (List.mem_singleton_self _), rfl, rfl⟩)
    · rw [Function.update_of_ne hr] at hl
      exact Gs_mono subset_rfl hM (h r' c' hl)
  | clearOwn r c =>
    simp only [Ev.apply] at hl ⊢
    by_cases hr : r' = r
    · subst hr; simp at hl
    · rw [Function.update_of_ne hr] at hl ⊢
      exact Gs_mono subset_rfl hM (h r' c' hl)

theorem good_step (pb : R → Bool) {s : St R} {M : List (MRec R)} {e : Ev R} {Bf : Ch → Finset R}
    (he : e.ok pb s) (h : SInv s M) (hg : Good Bf M) (hB : ∀ c, s.B c ⊆ Bf c) :
    Good Bf (M ++ e.mrec s) := by
  cases e with
  | movePub r c d =>
    simp only [Ev.mrec]
    exact good_snoc hg (Gs_mono (hB c) (fun _ h => h) (h r c he.1))
  | moveOwn r c d =>
    simp only [Ev.mrec]
    exact good_snoc hg (Gs_mono (hB c) (fun _ h => h) (h r c he.1))
  | _ => simpa [Ev.mrec] using hg

theorem good_run (pb : R → Bool) (Bf : Ch → Finset R) (tr : Trace R) :
    ∀ s M, LegalFrom pb s tr → SInv s M → Good Bf M → (∀ c, (run s tr).B c ⊆ Bf c) →
      SInv (run s tr) (M ++ mlogFrom s tr) ∧ Good Bf (M ++ mlogFrom s tr) := by
  induction tr with
  | nil => intro s M _ h hg _; simpa [run, mlogFrom] using ⟨h, hg⟩
  | cons e tr ih =>
    intro s M hl h hg hB
    have hB' : ∀ c, s.B c ⊆ Bf c := fun c => (B_sub_run (e :: tr) s c).trans (hB c)
    have := ih (e.apply s) (M ++ e.mrec s) hl.2 (sinv_step pb hl.1 h)
      (good_step pb hl.1 h hg (fun c => (B_sub_apply s e c).trans ((B_sub_run tr _ c).trans (hB c)))) hB
    simpa [run, mlogFrom, List.append_assoc] using this

theorem sinv_init : SInv (init : St R) [] := by
  intro r c h; simp [init] at h

/-- the bank-list facts of a legal trace: end-state span invariant + every bank reads its source content. -/
theorem legal_good {pb : R → Bool} {tr : Trace R} (h : Legal pb tr) :
    SInv (exec tr) (mlog tr) ∧ Good (exec tr).B (mlog tr) := by
  have := good_run pb (exec tr).B tr init [] h sinv_init (good_nil _) (fun c => subset_rfl)
  simpa [exec, mlog] using this

end Trace

/-! ## The fold: Word → BankNC0.Net -/

section Fold
variable {R : Type} [Fintype R] [DecidableEq R] (pb : R → Bool)

/-- fields = public registers. -/
abbrev Fld := {r : R // pb r = true}

/-- restriction of a row to the public coordinates. -/
def restr : (R → ℚ) →ₗ[ℚ] (Fld pb → ℚ) := LinearMap.funLeft ℚ ℚ Subtype.val

def locCh : Loc → Ch
  | .sit c => c
  | _ => ∅

/-- final row of a field (0 if it does not sit). -/
def oRow (s : St R) (f : Fld pb) : Fld pb → ℚ :=
  match s.loc f.1 with
  | .sit _ => restr pb (s.row f.1)
  | _ => 0

variable {pb}

theorem restr_single {g : R} (hg : pb g = true) : restr pb (Pi.single g 1) = Pi.single (⟨g, hg⟩ : Fld pb) 1 := by
  funext f
  simp only [restr, LinearMap.funLeft_apply, Pi.single_apply, Subtype.ext_iff]

theorem bch_eq {s : St R} (hs : PInv pb s) {g : R} {c : Ch} (h : g ∈ s.B c) : bch s g = c := by
  have hex : ∃ c, g ∈ s.B c := ⟨c, h⟩
  unfold bch; rw [dif_pos hex]
  exact hs.bu g _ _ (Classical.choose_spec hex) h

/-- the restricted content of chart c lies in the Net's generator span at c. -/
theorem restr_Gs {s : St R} (hs : PInv pb s) {M : List (MRec R)} {c : Ch} {v : R → ℚ} (hv : v ∈ Gs s.B M c)
    (T : Set (Fld pb → ℚ)) (hT1 : ∀ g (hg : pb g = true), g ∈ s.B c → Pi.single (⟨g, hg⟩ : Fld pb) 1 ∈ T)
    (hT2 : ∀ m ∈ M, m.dst = c → restr pb m.row ∈ T) :
    restr pb v ∈ Submodule.span ℚ T := by
  have h2 : restr pb v ∈ (Gs s.B M c).map (restr pb) := Submodule.mem_map_of_mem hv
  rw [Gs, Submodule.map_span] at h2
  refine (Submodule.span_le.2 ?_) h2
  rintro _ ⟨w, hw | hw, rfl⟩
  · obtain ⟨g, hg, rfl⟩ := hw
    have hp := hs.pB g c hg
    rw [restr_single hp]; exact Submodule.subset_span (hT1 g hp hg)
  · obtain ⟨m, hm, hd, rfl⟩ := hw
    exact Submodule.subset_span (hT2 m hm hd)

variable (tr : Trace R)

/-- the folded Net's data (charts = labels). -/
noncomputable def fA (f : Fld pb) : Ch := bch (exec tr) f.1
def fB (f : Fld pb) : Ch := locCh ((exec tr).loc f.1)
def fsrc (k : Fin (mlog tr).length) : Ch := ((mlog tr)[k.1]).src
def fdst (k : Fin (mlog tr).length) : Ch := ((mlog tr)[k.1]).dst
def fd (k : Fin (mlog tr).length) : Fld pb → ℚ := restr pb ((mlog tr)[k.1]).row
def fO : Matrix (Fld pb) (Fld pb) ℚ := fun f => oRow pb (exec tr) f

variable {tr}

/-- **fold_read** (time-stamped CSEntry): bank k carries a form of its source chart: inputs born there + EARLIER
deliveries there. -/
theorem fold_read (h : Legal pb tr) (k : Fin (mlog tr).length) :
    fd (pb := pb) tr k ∈ Submodule.span ℚ ({v | ∃ g, fA (pb := pb) tr g = fsrc tr k ∧ v = Pi.single g 1} ∪
      {v | ∃ j, j < k ∧ fdst tr j = fsrc tr k ∧ v = fd (pb := pb) tr j}) := by
  have hs := reach_pinv pb (reach_exec h)
  obtain ⟨-, hg⟩ := legal_good h
  have hdec : mlog tr = (mlog tr).take k.1 ++ (mlog tr)[k.1] :: (mlog tr).drop (k.1 + 1) := by
    conv_lhs => rw [← List.take_append_drop k.1 (mlog tr)]
    rw [List.drop_eq_getElem_cons k.2]
  have hrow := hg _ _ _ hdec
  refine restr_Gs hs hrow _ (fun g hp hgB => ?_) ?_
  · exact Or.inl ⟨⟨g, hp⟩, bch_eq hs hgB, rfl⟩
  intro m hm hd
  obtain ⟨j, hj, rfl⟩ := List.mem_iff_getElem.1 hm
  have hjk : j < k.1 := by simp at hj; omega
  have hjL : j < (mlog tr).length := by omega
  refine Or.inr ⟨⟨j, hjL⟩, hjk, ?_, ?_⟩
  · simp only [fdst, fsrc]; rw [← hd, List.getElem_take]
  · simp only [fd]; rw [List.getElem_take]

/-- **fold_out** (time-stamped CSFinal): each output is a form of its final chart's content. -/
theorem fold_out (h : Legal pb tr) (f : Fld pb) :
    fO (pb := pb) tr f ∈ Submodule.span ℚ ({v | ∃ g, fA (pb := pb) tr g = fB (pb := pb) tr f ∧ v = Pi.single g 1} ∪
      {v | ∃ j, fdst tr j = fB (pb := pb) tr f ∧ v = fd (pb := pb) tr j}) := by
  have hs := reach_pinv pb (reach_exec h)
  obtain ⟨hi, -⟩ := legal_good h
  unfold fO oRow fB
  cases hl : (exec tr).loc f.1 with
  | sit c =>
    simp only [locCh]
    refine restr_Gs hs (hi f.1 c hl) _ (fun g hp hgB => ?_) ?_
    · exact Or.inl ⟨⟨g, hp⟩, bch_eq hs hgB, rfl⟩
    intro m hm hd
    obtain ⟨j, hj, rfl⟩ := List.mem_iff_getElem.1 hm
    exact Or.inr ⟨⟨j, hj⟩, hd, rfl⟩
  | unborn => exact Submodule.zero_mem _
  | cleared => exact Submodule.zero_mem _

/-- **fold**: a legal word trace as a BankNC0.Net over label charts. -/
noncomputable def fold (h : Legal pb tr) : BankNC0.Net ℚ Ch (Fld pb) (Fin (mlog tr).length) where
  A := fA tr
  B := fB tr
  src := fsrc tr
  dst := fdst tr
  d := fd tr
  O := fO tr
  read := fold_read h
  out := fold_out h

/-- push a Net through a chart map (read/out only use chart equalities, which φ preserves). -/
def _root_.BankNC0.Net.mapChart {K Chart Chart' Fld Bank : Type} [Field K] [DecidableEq Fld] [LinearOrder Bank]
    (N : BankNC0.Net K Chart Fld Bank) (φ : Chart → Chart') : BankNC0.Net K Chart' Fld Bank where
  A f := φ (N.A f)
  B f := φ (N.B f)
  src k := φ (N.src k)
  dst k := φ (N.dst k)
  d := N.d
  O := N.O
  read k := by
    refine Submodule.span_mono ?_ (N.read k)
    rintro v (⟨g, hg, rfl⟩ | ⟨j, hj, hd, rfl⟩)
    · exact Or.inl ⟨g, by rw [hg], rfl⟩
    · exact Or.inr ⟨j, hj, by rw [hd], rfl⟩
  out f := by
    refine Submodule.span_mono ?_ (N.out f)
    rintro v (⟨g, hg, rfl⟩ | ⟨j, hd, rfl⟩)
    · exact Or.inl ⟨g, by rw [hg], rfl⟩
    · exact Or.inr ⟨j, by rw [hd], rfl⟩

/-- **foldS**: the fold on Uni.Chart = Submodule (ZMod 2) (F₂⁹) through the L0 bridge (BankedGraph's chart type). -/
noncomputable def foldS (h : Legal pb tr) : BankNC0.Net ℚ Chart (Fld pb) (Fin (mlog tr).length) :=
  (fold h).mapChart toSub

end Fold

/-! ## Invoice: paid -/

section Paid
variable {R : Type} [Fintype R] [DecidableEq R]

/-- the folded Net's paid invoice under a chart price dc at exponent σ (one term per bank). -/
noncomputable def paidF (dc : Ch → Ch → ℝ) (σ : ℝ) (tr : Trace R) : ℝ :=
  ∑ k : Fin (mlog tr).length, dc (fsrc tr k) (fdst tr k) ^ σ

theorem paidF_list (dc : Ch → Ch → ℝ) (σ : ℝ) (tr : Trace R) :
    paidF dc σ tr = ((mlog tr).map (fun m => dc m.src m.dst ^ σ)).sum := by
  unfold paidF fsrc fdst
  exact Fin.sum_univ_fun_getElem (mlog tr) (fun m => dc m.src m.dst ^ σ)

theorem sum_split_kind (g : MRec R → ℝ) (L : List (MRec R)) :
    (L.map g).sum = ((L.filter (fun m => m.pubk)).map g).sum + ((L.filter (fun m => !m.pubk)).map g).sum := by
  induction L with
  | nil => simp
  | cons m L ih => cases hm : m.pubk <;> simp [hm, ih] <;> ring

theorem sum_getD_range {α : Type*} (f : α → ℝ) (a0 : α) (l : List α) :
    (l.map f).sum = ∑ k ∈ range l.length, f (l.getD k a0) := by
  induction l with
  | nil => simp
  | cons a l ih => rw [List.length_cons, sum_range_succ', List.map_cons, List.sum_cons, ih]; simp [add_comm]

/-- paid = public MOVE log + owned MOVE log, for every trace (no legality needed). -/
theorem paidF_logs (dc : Ch → Ch → ℝ) (σ : ℝ) (tr : Trace R) :
    paidF dc σ tr = ((exec tr).plog.map (fun m => dc m.2.1 m.2.2 ^ σ)).sum +
      ((exec tr).olog.map (fun m => dc m.1 m.2.1 ^ σ)).sum := by
  obtain ⟨h1, h2⟩ := run_logs tr init
  rw [paidF_list, sum_split_kind]
  simp only [exec] at h1 h2 ⊢
  rw [h1, h2]
  simp [init, List.map_reverse, List.sum_reverse, Function.comp_def, mlog]

/-! ### Public log = Σ over public registers of the hop-by-hop path cost -/

/-- sources / targets of r's public MOVEs in a public log, oldest first. -/
def srcsL (P : List (R × Ch × Ch)) (r : R) : List Ch :=
  ((P.filter (fun m => decide (m.1 = r))).map (fun m => m.2.1)).reverse
def mvsL (P : List (R × Ch × Ch)) (r : R) : List Ch :=
  ((P.filter (fun m => decide (m.1 = r))).map (fun m => m.2.2)).reverse

theorem mvs_eq (s : St R) (r : R) : mvs s r = mvsL s.plog r := rfl

theorem srcsL_self (P : List (R × Ch × Ch)) (r : R) (c d : Ch) : srcsL ((r, c, d) :: P) r = srcsL P r ++ [c] := by
  simp [srcsL]
theorem mvsL_self (P : List (R × Ch × Ch)) (r : R) (c d : Ch) : mvsL ((r, c, d) :: P) r = mvsL P r ++ [d] := by
  simp [mvsL]
theorem srcsL_ne (P : List (R × Ch × Ch)) {r r' : R} (h : r' ≠ r) (c d : Ch) : srcsL ((r, c, d) :: P) r' = srcsL P r' := by
  simp [srcsL, Ne.symm h]
theorem mvsL_ne (P : List (R × Ch × Ch)) {r r' : R} (h : r' ≠ r) (c d : Ch) : mvsL ((r, c, d) :: P) r' = mvsL P r' := by
  simp [mvsL, Ne.symm h]

/-- chain invariant: r's MOVE sources are its path minus the last chart. -/
def CInvL (P : List (R × Ch × Ch)) (B : Ch → Finset R) : Prop :=
  (∀ r c0, r ∈ B c0 → srcsL P r = (c0 :: mvsL P r).dropLast) ∧ (∀ r, (∀ c, r ∉ B c) → srcsL P r = [])

def CInv (s : St R) : Prop := CInvL s.plog s.B

theorem cinv_step (pb : R → Bool) {s s' : St R} (hp : PInv pb s) (h : CInv s) (hst : Step pb s s') : CInv s' := by
  cases hst with
  | birthPub r c hu hpb =>
    obtain ⟨hnB, hmv⟩ := hp.unb r hu
    rw [mvs_eq] at hmv
    show CInvL s.plog (Function.update s.B c (insert r (s.B c)))
    refine ⟨fun r' c0 hr' => ?_, fun r' hr' => ?_⟩
    · by_cases hc : c0 = c
      · subst hc
        rw [Function.update_self, Finset.mem_insert] at hr'
        rcases hr' with rfl | hr'
        · rw [h.2 r' hnB, hmv]; rfl
        · exact h.1 r' c0 hr'
      · rw [Function.update_of_ne hc] at hr'; exact h.1 r' c0 hr'
    · refine h.2 r' (fun c' hc' => hr' c' ?_)
      by_cases hc : c' = c
      · subst hc; rw [Function.update_self]; exact Finset.mem_insert_of_mem hc'
      · rw [Function.update_of_ne hc]; exact hc'
  | birthOwn r c _ _ => exact h
  | gate r c coef _ => exact h
  | moveOwn r c d _ _ => exact h
  | clearOwn r c _ _ => exact h
  | movePub r c d hl hpb hlt =>
    show CInvL ((r, c, d) :: s.plog) s.B
    refine ⟨fun r' c0 hr' => ?_, fun r' hr' => ?_⟩
    · by_cases hr : r' = r
      · subst hr
        have hlast := hp.last r' c0 hr'
        rw [hl, mvs_eq] at hlast
        have hc := Loc.sit.inj hlast
        rw [srcsL_self, mvsL_self, h.1 r' c0 hr', hc, ← List.cons_append, List.dropLast_concat]
        exact List.dropLast_append_getLast _
      · rw [srcsL_ne _ hr, mvsL_ne _ hr]; exact h.1 r' c0 hr'
    · by_cases hr : r' = r
      · subst hr
        obtain ⟨c0, h0⟩ := hp.born r' c hpb hl
        exact absurd h0 (hr' c0)
      · rw [srcsL_ne _ hr]; exact h.2 r' hr'

theorem cinv_init : CInv (init : St R) := ⟨fun r c h => by simp [init] at h, fun r _ => by simp [srcsL, init]⟩

theorem reach_cinv {pb : R → Bool} {s : St R} (h : Reach pb s) : CInv s := by
  induction h with
  | refl => exact cinv_init
  | tail hr hst ih => exact cinv_step pb (reach_pinv pb hr) ih hst

/-- zip lemma: a list of hops whose sources are the path minus its end and targets the path minus its start. -/
theorem chain_sum (g : Ch → Ch → ℝ) :
    ∀ (l : List (R × Ch × Ch)) (c0 : Ch) (t : List Ch), (l.map (fun m => m.2.1)) = (c0 :: t).dropLast →
      l.map (fun m => m.2.2) = t →
      (l.map (fun m => g m.2.1 m.2.2)).sum = ∑ i ∈ range t.length, g ((c0 :: t).getD i ∅) ((c0 :: t).getD (i + 1) ∅) := by
  intro l
  induction l with
  | nil => intro c0 t _ h2; subst h2; simp
  | cons m l ih =>
    intro c0 t h1 h2
    cases t with
    | nil => simp at h2
    | cons x t =>
      simp only [List.map_cons, List.cons.injEq] at h2
      obtain ⟨hx, ht⟩ := h2
      rw [List.dropLast_cons_cons, List.map_cons, List.cons.injEq] at h1
      obtain ⟨hc, hl⟩ := h1
      rw [List.map_cons, List.sum_cons, ih x t hl ht, List.length_cons, sum_range_succ']
      simp only [List.getD_cons_succ, List.getD_cons_zero, zero_add]
      rw [hc, hx, add_comm]

theorem sum_fiber (g : R × Ch × Ch → ℝ) (l : List (R × Ch × Ch)) :
    (l.map g).sum = ∑ r, ((l.filter (fun m => decide (m.1 = r))).map g).sum := by
  induction l with
  | nil => simp
  | cons m l ih =>
    rw [List.map_cons, List.sum_cons, ih]
    have : ∀ r, ((List.filter (fun m' => decide (m'.1 = r)) (m :: l)).map g).sum =
        (if m.1 = r then g m else 0) + ((l.filter (fun m' => decide (m'.1 = r))).map g).sum := by
      intro r; by_cases h : m.1 = r <;> simp [h]
    simp_rw [this, sum_add_distrib, sum_ite_eq, mem_univ, if_true]

/-- **public log = Σ_public pcost**: for every reachable state, the public MOVE log priced hop by hop equals the
sum over public registers of their chart-path cost (WordModelPrice.path / plen). -/
theorem plog_sum_path {pb : R → Bool} {s : St R} (h : Reach pb s) (dc : Ch → Ch → ℝ) (σ : ℝ) :
    (s.plog.map (fun m => dc m.2.1 m.2.2 ^ σ)).sum =
      ∑ r ∈ univ.filter (fun r => pb r = true), pcost dc (path s r) (plen s r) σ := by
  obtain ⟨hp, hq⟩ := reach_qinv pb h
  have hc := reach_cinv h
  rw [sum_fiber]
  have hzero : ∀ r ∈ (univ : Finset R), r ∉ univ.filter (fun r => pb r = true) →
      ((s.plog.filter (fun m => decide (m.1 = r))).map (fun m => dc m.2.1 m.2.2 ^ σ)).sum = 0 := by
    intro r _ hr
    have hr' : pb r = false := by simpa using hr
    have : s.plog.filter (fun m => decide (m.1 = r)) = [] := by
      rw [List.filter_eq_nil_iff]; intro m hm he
      have := hq.plogPub m hm; simp at he; rw [he] at this; rw [this] at hr'; cases hr'
    rw [this]; simp
  rw [← sum_subset (filter_subset (fun r => pb r = true) univ) hzero]
  refine sum_congr rfl (fun r _ => ?_)
  set F := s.plog.filter (fun m => decide (m.1 = r)) with hF
  have hrev : (F.map (fun m => dc m.2.1 m.2.2 ^ σ)).sum = (F.reverse.map (fun m => dc m.2.1 m.2.2 ^ σ)).sum := by
    rw [List.map_reverse, List.sum_reverse]
  have hS : F.reverse.map (fun m => m.2.1) = srcsL s.plog r := by simp [srcsL, hF, List.map_reverse]
  have hT : F.reverse.map (fun m => m.2.2) = mvs s r := by simp [mvs, hF, List.map_reverse]
  rw [hrev]
  by_cases hb : ∃ c, r ∈ s.B c
  · obtain ⟨c0, h0⟩ := hb
    have hbch : bch s r = c0 := bch_eq hp h0
    have h1 : F.reverse.map (fun m => m.2.1) = (c0 :: mvs s r).dropLast := by rw [hS, mvs_eq]; exact hc.1 r c0 h0
    refine (chain_sum (fun a b => dc a b ^ σ) F.reverse c0 (mvs s r) h1 hT).trans ?_
    simp only [pcost, path, plen, hbch]
  · push Not at hb
    have h1 := hc.2 r hb
    have hnil : F.reverse = [] := by rw [← List.map_eq_nil_iff (f := fun m => m.2.1), hS, h1]
    have hm : mvs s r = [] := by rw [← hT, hnil]; rfl
    rw [hnil]; simp [pcost, plen, hm]

end Paid

/-! ### Word specialisation: the folded invoice IS FWreal -/

section WordInv
variable {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow]
  [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]

/-- the word's paid invoice: every public path hop (helpers + mains) and every owned MOVE. -/
noncomputable def wordPaid (cl : Caller Pt) (s : St (Reg Pt Hl Ow)) (dc : Ch → Ch → ℝ) (σ : ℝ) : ℝ :=
  ∑ i ∈ (helpers : Finset (Reg Pt Hl Ow)), pcost dc (path s i) (plen s i) σ +
    ∑ j ∈ mains cl, pcost dc (path s j) (plen s j) σ + ∑ k ∈ range (nOwned s), dc (oSrc s k) (oTgt s k) ^ σ

/-- FWreal = caller block + 17·(helper credit − folded paid). -/
theorem FWreal_eq (cl : Caller Pt) (s : St (Reg Pt Hl Ow)) (dc : Ch → Ch → ℝ) (σ : ℝ) :
    FWreal cl s dc σ = Dc σ + 17 * (∑ i ∈ (helpers : Finset (Reg Pt Hl Ow)), gc σ (hcred s i) - wordPaid cl s dc σ) := by
  unfold FWreal FW wordPaid; ring

theorem pub_filter (cl : Caller Pt) :
    univ.filter (fun r : Reg Pt Hl Ow => pub cl r = true) = helpers ∪ mains cl := by
  ext r
  simp only [mem_filter, mem_univ, true_and, mem_union, helpers, mains, Dset, mem_image]
  cases r <;> simp [pub]

/-- **fold_paid** (invoice EQUALITY, any chart price dc): the folded Net's paid invoice = the word's paid invoice. -/
theorem fold_paid (cl : Caller Pt) {tr : Trace (Reg Pt Hl Ow)} (h : Legal (pub cl) tr) (dc : Ch → Ch → ℝ) (σ : ℝ) :
    paidF dc σ tr = wordPaid cl (exec tr) dc σ := by
  rw [paidF_logs, plog_sum_path (reach_exec h), pub_filter, sum_union (helpers_mains_disj cl),
    sum_getD_range (fun m : Ch × Ch × (Reg Pt Hl Ow → ℚ) => dc m.1 m.2.1 ^ σ) (∅, ∅, 0) (exec tr).olog]
  rfl

/-- **FWreal is the folded Net's invoice** (SPEC price). -/
theorem FWreal_fold (cl : Caller Pt) {tr : Trace (Reg Pt Hl Ow)} (h : Legal (pub cl) tr) (σ : ℝ) :
    FWreal cl (exec tr) specPrice σ = Dc σ + 17 * (∑ i ∈ (helpers : Finset (Reg Pt Hl Ow)), gc σ (hcred (exec tr) i)
      - ∑ k : Fin (mlog tr).length, latD ((foldS h).src k) ((foldS h).dst k) ^ σ) := by
  rw [FWreal_eq, ← fold_paid cl h]; rfl

end WordInv

end Uni

#print axioms Uni.reach_iff
#print axioms Uni.fold
#print axioms Uni.foldS
#print axioms Uni.fold_read
#print axioms Uni.fold_out
#print axioms Uni.fold_paid
#print axioms Uni.FWreal_fold
