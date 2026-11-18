/-
LEAN-PREM1, Nov 17. CLEAR certificates on the TokenCancel row model. See ClearCert.md.
Rank lemma (span form), checker soundness+completeness, CLEARFORM same-events theorem, toy instance.
-/
import Nov15.TokenCancel
import Mathlib.LinearAlgebra.Finsupp.LinearCombination
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace ClearCert
open TokenCancel

variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C]

/-- Span of all current rows (zero rows contribute nothing). -/
def rowSpan (s : St K Reg C) : Submodule K (Reg → K) := Submodule.span K (Set.range s.row)

/-- Span of the rows of the registers other than `i`. -/
def othersSpan (s : St K Reg C) (i : Reg) : Submodule K (Reg → K) :=
  Submodule.span K (s.row '' {j | j ≠ i})

/-- CLEAR of `i` is lossless at `s`: the erased row lies in the span of the other rows. -/
def Lossless (s : St K Reg C) (i : Reg) : Prop := s.row i ∈ othersSpan s i

/-- No births in the tail (public inputs are born in the prefix). -/
def NoBorn : Ev K Reg C → Prop
  | .born _ _ => False
  | _ => True

/-- What the checker (check.py) enforces besides legality: no SCALE by 0, ADD between distinct
registers, COPY / INIT into a zero row, no births. CLEAR is unconstrained. -/
def Good (s : St K Reg C) : Ev K Reg C → Prop
  | .born _ _ => False
  | .init i _ => s.row i = 0
  | .move _ _ => True
  | .add i j _ _ => i ≠ j
  | .scale _ u _ => u ≠ 0
  | .clear _ _ => True
  | .copy i _ _ => s.row i = 0

def GoodRun : St K Reg C → List (Ev K Reg C) → Prop
  | _, [] => True
  | s, e :: es => Good s e ∧ GoodRun (step s e) es

lemma run_append (s : St K Reg C) (a b : List (Ev K Reg C)) :
    run s (a ++ b) = run (run s a) b := by
  induction a generalizing s with
  | nil => rfl
  | cons e es ih => simp [run, ih]

lemma row_mem (s : St K Reg C) (j : Reg) : s.row j ∈ rowSpan s :=
  Submodule.subset_span ⟨j, rfl⟩

lemma update_range_le (s : St K Reg C) (i : Reg) (v : Reg → K) (hv : v ∈ rowSpan s) :
    Submodule.span K (Set.range (Function.update s.row i v)) ≤ rowSpan s := by
  refine Submodule.span_le.mpr ?_
  rintro _ ⟨j, rfl⟩
  by_cases h : j = i
  · subst h; simpa using hv
  · simpa [Function.update_of_ne h] using row_mem s j

/-- Every non-birth event can only shrink the span of the rows. -/
theorem span_step_le (s : St K Reg C) (e : Ev K Reg C) (he : NoBorn e) :
    rowSpan (step s e) ≤ rowSpan s := by
  cases e with
  | born i c => exact he.elim
  | init i c => exact update_range_le s i 0 (Submodule.zero_mem _)
  | move i c => exact le_rfl
  | add i j a c =>
    exact update_range_le s i _ (Submodule.add_mem _ (row_mem s i)
      (Submodule.smul_mem _ _ (row_mem s j)))
  | scale i u c => exact update_range_le s i _ (Submodule.smul_mem _ _ (row_mem s i))
  | clear i c => exact update_range_le s i 0 (Submodule.zero_mem _)
  | copy i j c => exact update_range_le s i _ (row_mem s j)

/-- A non-CLEAR "good" event preserves the span of the rows exactly (rank unchanged). -/
theorem span_step_ge (s : St K Reg C) (e : Ev K Reg C) (hg : Good s e)
    (hc : ∀ i c, e ≠ .clear i c) : rowSpan s ≤ rowSpan (step s e) := by
  have key : ∀ (i : Reg) (v : Reg → K), s.row i ∈ rowSpan (⟨Function.update s.row i v, s.loc⟩ : St K Reg C) →
      rowSpan s ≤ rowSpan (⟨Function.update s.row i v, s.loc⟩ : St K Reg C) := by
    intro i v hi
    refine Submodule.span_le.mpr ?_
    rintro _ ⟨j, rfl⟩
    by_cases h : j = i
    · subst h; exact hi
    · exact Submodule.subset_span ⟨j, by simp [Function.update_of_ne h]⟩
  cases e with
  | born i c => exact hg.elim
  | init i c =>
    exact key i 0 (by simp [Good] at hg; rw [hg]; exact Submodule.zero_mem _)
  | move i c => exact le_rfl
  | add i j a c =>
    apply key
    have hne : i ≠ j := hg
    have h1 : (⟨Function.update s.row i (s.row i + a • s.row j), s.loc⟩ : St K Reg C).row i
        = s.row i + a • s.row j := by simp
    have h2 : (⟨Function.update s.row i (s.row i + a • s.row j), s.loc⟩ : St K Reg C).row j
        = s.row j := by simp [Function.update_of_ne hne.symm]
    have := Submodule.sub_mem (rowSpan (⟨Function.update s.row i (s.row i + a • s.row j), s.loc⟩ : St K Reg C))
      (row_mem ⟨Function.update s.row i (s.row i + a • s.row j), s.loc⟩ i)
      (Submodule.smul_mem _ a (row_mem ⟨Function.update s.row i (s.row i + a • s.row j), s.loc⟩ j))
    rw [h1, h2] at this
    simpa using this
  | scale i u c =>
    apply key
    have hu : u ≠ 0 := hg
    have h1 : (⟨Function.update s.row i (u • s.row i), s.loc⟩ : St K Reg C).row i = u • s.row i := by simp
    have := Submodule.smul_mem (rowSpan (⟨Function.update s.row i (u • s.row i), s.loc⟩ : St K Reg C))
      u⁻¹ (row_mem ⟨Function.update s.row i (u • s.row i), s.loc⟩ i)
    rw [h1, smul_smul, inv_mul_cancel₀ hu, one_smul] at this
    exact this
  | clear i c => exact absurd rfl (hc i c)
  | copy i j c =>
    exact key i _ (by simp [Good] at hg; rw [hg]; exact Submodule.zero_mem _)

/-- Span after a CLEAR = span of the other rows. -/
theorem span_clear_eq (s : St K Reg C) (i : Reg) (c : C) :
    rowSpan (step s (.clear i c)) = othersSpan s i := by
  apply le_antisymm
  · refine Submodule.span_le.mpr ?_
    rintro _ ⟨j, rfl⟩
    by_cases h : j = i
    · subst h; simp [step]
    · simp only [step, Function.update_of_ne h]
      exact Submodule.subset_span ⟨j, h, rfl⟩
  · refine Submodule.span_le.mpr ?_
    rintro _ ⟨j, hj, rfl⟩
    exact Submodule.subset_span ⟨j, by simp [step, Function.update_of_ne hj]⟩

/-- A CLEAR is lossless iff it does not change the span of the rows. -/
theorem lossless_iff (s : St K Reg C) (i : Reg) (c : C) :
    Lossless s i ↔ rowSpan (step s (.clear i c)) = rowSpan s := by
  rw [span_clear_eq]
  constructor
  · intro h
    apply le_antisymm
    · refine Submodule.span_le.mpr ?_
      rintro _ ⟨j, hj, rfl⟩; exact row_mem s j
    · refine Submodule.span_le.mpr ?_
      rintro _ ⟨j, rfl⟩
      by_cases hj : j = i
      · subst hj; exact h
      · exact Submodule.subset_span ⟨j, hj, rfl⟩
  · intro h
    have : s.row i ∈ rowSpan s := row_mem s i
    rw [← h] at this; exact this

/-- RANK LEMMA, part 1 (span form): in a birth-free tail the span of the rows only shrinks. -/
theorem span_run_le (s : St K Reg C) (es : List (Ev K Reg C)) (h : ∀ e ∈ es, NoBorn e) :
    rowSpan (run s es) ≤ rowSpan s := by
  induction es generalizing s with
  | nil => exact le_rfl
  | cons e es ih =>
    exact (ih (step s e) (fun x hx => h x (by simp [hx]))).trans
      (span_step_le s e (h e (by simp)))

/-- Endpoint exactness at the span level, relative to the input space `U` (the span of the public
inputs e_i): the final rows span `U`. For the real words (final public rows = identity, owned rows
zero) this is implied by exactness. -/
def FullEnd (U : Submodule K (Reg → K)) (s : St K Reg C) (es : List (Ev K Reg C)) : Prop :=
  U ≤ rowSpan (run s es)

/-- RANK LEMMA / THEOREM 1: in an endpoint-exact birth-free word, EVERY CLEAR is lossless. -/
theorem every_clear_lossless (U : Submodule K (Reg → K)) (s : St K Reg C) (es : List (Ev K Reg C))
    (hU : rowSpan s ≤ U) (hnb : ∀ e ∈ es, NoBorn e) (hend : FullEnd U s es)
    (pre post : List (Ev K Reg C)) (i : Reg) (c : C) (hsplit : es = pre ++ .clear i c :: post) :
    Lossless (run s pre) i := by
  subst hsplit
  rw [lossless_iff _ _ c]
  have hn : ∀ e ∈ post, NoBorn e := fun x hx => hnb x (by simp [hx])
  have hpre : ∀ e ∈ pre, NoBorn e := fun x hx => hnb x (by simp [hx])
  have h1 : U ≤ rowSpan (run (step (run s pre) (.clear i c)) post) := by
    have := hend; unfold FullEnd at this
    rwa [run_append, run] at this
  have h2 := h1.trans (span_run_le _ post hn)
  have h3 : rowSpan (run s pre) ≤ U := (span_run_le s pre hpre).trans hU
  exact le_antisymm (span_step_le _ _ trivial) (h3.trans h2)

/-- Rank lemma, dimension form: a CLEAR lowers the rank by at most 1. -/
theorem finrank_clear_le [Finite Reg] (s : St K Reg C) (i : Reg) (c : C) :
    Module.finrank K (rowSpan s) ≤ Module.finrank K (rowSpan (step s (.clear i c))) + 1 := by
  have hsup : rowSpan s ≤ rowSpan (step s (.clear i c)) ⊔ Submodule.span K {s.row i} := by
    refine Submodule.span_le.mpr ?_
    rintro _ ⟨j, rfl⟩
    by_cases h : j = i
    · subst h; exact Submodule.mem_sup_right (Submodule.subset_span rfl)
    · exact Submodule.mem_sup_left (Submodule.subset_span ⟨j, by simp [step, Function.update_of_ne h]⟩)
  have h1 := Submodule.finrank_mono hsup
  have h2 := Submodule.finrank_add_le_finrank_add_finrank (rowSpan (step s (.clear i c)))
    (Submodule.span K {s.row i})
  have h3 : Module.finrank K (Submodule.span K {s.row i}) ≤ 1 := le_trans (finrank_span_le_card {s.row i}) (by simp)
  omega


/-! ## Checker model (verify_certificates, as read in check.py:656-694) -/

/-- Dead registers (never born/INITed) carry the zero row. -/
def DeadZero (s : St K Reg C) : Prop := ∀ j, s.loc j = none → s.row j = 0

section legal
variable (z V : C)

theorem deadZero_step (s : St K Reg C) (e : Ev K Reg C) (hd : DeadZero s)
    (hL : LegalEv z V s e) : DeadZero (step s e) := by
  intro j hj
  cases e with
  | born i c => by_cases h : j = i <;> simp_all [step, DeadZero, Function.update_apply]
  | init i c => by_cases h : j = i <;> simp_all [step, DeadZero, Function.update_apply]
  | move i c =>
    by_cases h : j = i
    · subst h; simp [step] at hj
    · simp only [step, Function.update_of_ne h] at hj ⊢; exact hd j hj
  | add i j' a c =>
    by_cases h : j = i
    · subst h; simp only [step] at hj; rw [hL.2.1] at hj; simp at hj
    · simp only [step, Function.update_of_ne h] at hj ⊢; exact hd j hj
  | scale i u c =>
    by_cases h : j = i
    · subst h; simp only [step] at hj; rw [hL] at hj; simp at hj
    · simp only [step, Function.update_of_ne h] at hj ⊢; exact hd j hj
  | clear i c =>
    by_cases h : j = i
    · subst h; simp [step]
    · simp only [step, Function.update_of_ne h] at hj ⊢; exact hd j hj
  | copy i j' c =>
    by_cases h : j = i
    · subst h; simp only [step] at hj; rw [hL.1] at hj; simp at hj
    · simp only [step, Function.update_of_ne h] at hj ⊢; exact hd j hj

/-- Chronology / field identity (legality) only reads `loc`, never row contents. -/
theorem legal_congr (s s' : St K Reg C) (h : s.loc = s'.loc) (es : List (Ev K Reg C)) :
    Legal z V s es ↔ Legal z V s' es := by
  induction es generalizing s s' with
  | nil => simp [Legal]
  | cons e es ih =>
    have hl : LegalEv z V s e ↔ LegalEv z V s' e := by
      cases e <;> simp [LegalEv, h]
    have hs : (step s e).loc = (step s' e).loc := by cases e <;> simp [step, h]
    simp only [Legal, hl, ih _ _ hs]

end legal

/-- A certificate at a CLEAR of `i`: finitely supported coefficients on live registers other than `i`,
exact combination of their rows equal to the erased row (check.py:672-678). -/
def CertOK (s : St K Reg C) (i : Reg) (c : Reg →₀ K) : Prop :=
  (∀ k ∈ c.support, k ≠ i ∧ s.loc k ≠ none) ∧
    s.row i = Finsupp.linearCombination K s.row c

/-- Certificates indexed by event position (the JSON `clear_event_index`): every CLEAR has one. -/
def Certified : St K Reg C → List (Ev K Reg C) → (ℕ → Option (Reg →₀ K)) → Prop
  | _, [], _ => True
  | s, e :: es, cs =>
    (match e with
      | .clear i _ => ∃ c, cs 0 = some c ∧ CertOK s i c
      | _ => True) ∧ Certified (step s e) es (fun n => cs (n + 1))

theorem certOK_lossless (s : St K Reg C) (i : Reg) (c : Reg →₀ K) (h : CertOK s i c) :
    Lossless s i := by
  unfold Lossless othersSpan
  rw [h.2]
  have : c ∈ Finsupp.supported K K {j | j ≠ i} := by
    rw [Finsupp.mem_supported]; intro k hk; exact (h.1 k hk).1
  exact (Finsupp.mem_span_image_iff_linearCombination K).mpr ⟨c, this, rfl⟩

theorem lossless_certOK (s : St K Reg C) (hd : DeadZero s) (i : Reg) (h : Lossless s i) :
    ∃ c, CertOK s i c := by
  have h' : othersSpan s i ≤ Submodule.span K (s.row '' {j | j ≠ i ∧ s.loc j ≠ none}) := by
    refine Submodule.span_le.mpr ?_
    rintro _ ⟨j, hj, rfl⟩
    by_cases hl : s.loc j = none
    · rw [hd j hl]; exact Submodule.zero_mem _
    · exact Submodule.subset_span ⟨j, ⟨hj, hl⟩, rfl⟩
  obtain ⟨c, hc, hcomb⟩ := (Finsupp.mem_span_image_iff_linearCombination K).mp (h' h)
  refine ⟨c, fun k hk => ?_, hcomb.symm⟩
  exact (Finsupp.mem_supported K c).mp hc hk

theorem goodRun_noBorn (s : St K Reg C) (es : List (Ev K Reg C)) (h : GoodRun s es) :
    ∀ e ∈ es, NoBorn e := by
  induction es generalizing s with
  | nil => simp
  | cons e es ih =>
    intro x hx
    rcases List.mem_cons.mp hx with rfl | hx
    · cases x <;> simp_all [GoodRun, Good, NoBorn]
    · exact ih _ h.2 x hx

/-- Certified + good steps => the span of the rows never drops (the word is information preserving). -/
theorem certified_span_ge (es : List (Ev K Reg C)) :
    ∀ (s : St K Reg C) (cs : ℕ → Option (Reg →₀ K)), GoodRun s es → Certified s es cs →
      rowSpan s ≤ rowSpan (run s es) := by
  induction es with
  | nil => intro s cs _ _; exact le_rfl
  | cons e es ih =>
    intro s cs hg hc
    have h1 : rowSpan s ≤ rowSpan (step s e) := by
      by_cases hcl : ∃ i c, e = .clear i c
      · obtain ⟨i, c, rfl⟩ := hcl
        obtain ⟨c0, -, hok⟩ := hc.1
        exact ((lossless_iff s i c).mp (certOK_lossless s i c0 hok)).ge
      · exact span_step_ge s e hg.1 (fun i c h => hcl ⟨i, c, h⟩)
    exact h1.trans (ih (step s e) _ hg.2 hc.2)

/-- THEOREM 2 (checker soundness): if the certificate check passes at every CLEAR of a good birth-free
word started from a full-rank state, the endpoint is full-rank and EVERY CLEAR is lossless. -/
theorem checker_sound (U : Submodule K (Reg → K)) (s : St K Reg C) (es : List (Ev K Reg C))
    (cs : ℕ → Option (Reg →₀ K))
    (hU : rowSpan s ≤ U) (hfull : U ≤ rowSpan s) (hg : GoodRun s es) (hc : Certified s es cs) :
    FullEnd U s es ∧ ∀ pre post i c, es = pre ++ .clear i c :: post → Lossless (run s pre) i := by
  have hend : FullEnd U s es := hfull.trans (certified_span_ge es s cs hg hc)
  exact ⟨hend, fun pre post i c h => every_clear_lossless U s es hU (goodRun_noBorn s es hg) hend pre post i c h⟩

/-- Checker completeness: an endpoint-exact legal birth-free word has certificates at every CLEAR. -/
theorem checker_complete (U : Submodule K (Reg → K)) (z V : C) (es : List (Ev K Reg C)) :
    ∀ (s : St K Reg C), rowSpan s ≤ U → DeadZero s → Legal z V s es → (∀ e ∈ es, NoBorn e) →
      FullEnd U s es →
      ∃ cs, Certified s es cs := by
  induction es with
  | nil => intro s _ _ _ _ _; exact ⟨fun _ => none, trivial⟩
  | cons e es ih =>
    intro s hU hd hl hnb hend
    have hU' : rowSpan (step s e) ≤ U := (span_step_le s e (hnb e (by simp))).trans hU
    have hd' := deadZero_step z V s e hd hl.1
    have hnb' : ∀ x ∈ es, NoBorn x := fun x hx => hnb x (by simp [hx])
    obtain ⟨cs', hcs'⟩ := ih (step s e) hU' hd' hl.2 hnb' hend
    by_cases hcl : ∃ i c, e = .clear i c
    · obtain ⟨i, c, rfl⟩ := hcl
      have hloss := every_clear_lossless U s (.clear i c :: es) hU hnb hend [] es i c rfl
      obtain ⟨c0, hc0⟩ := lossless_certOK s hd i hloss
      refine ⟨fun n => match n with | 0 => some c0 | n + 1 => cs' n, ?_, hcs'⟩
      exact ⟨c0, rfl, hc0⟩
    · refine ⟨fun n => match n with | 0 => none | n + 1 => cs' n, ?_, hcs'⟩
      cases e with
      | clear i c => exact absurd ⟨i, c, rfl⟩ hcl
      | _ => trivial

/-! ## THEOREM 3: CLEARFORM same-events theorem -/

/-- The owned INIT / MOVE / CLEAR events (fields, charts, chronology). -/
def ownedEv (owned : Reg → Prop) : Ev K Reg C → Prop
  | .init i _ => owned i
  | .move i _ => owned i
  | .clear i _ => owned i
  | _ => False

open Classical in
noncomputable def ownedEvents (owned : Reg → Prop) (es : List (Ev K Reg C)) : List (Ev K Reg C) :=
  es.filter (fun e => decide (ownedEv owned e))

def AllLossless (s : St K Reg C) (es : List (Ev K Reg C)) : Prop :=
  ∀ pre post i c, es = pre ++ .clear i c :: post → Lossless (run s pre) i

/-- `owned_erasure` split into (a) the contract clauses E1-E3 (allocation, chronology, volume),
which are a predicate `Sk` of the owned-event skeleton ONLY (assumed, not proved here), and
(b) lossless dirty content, which is the only content-dependent part. -/
def ErasureOK (Sk : List (Ev K Reg C) → Prop) (owned : Reg → Prop) (s : St K Reg C)
    (es : List (Ev K Reg C)) : Prop :=
  Sk (ownedEvents owned es) ∧ AllLossless s es

theorem clearform (U : Submodule K (Reg → K)) (Sk : List (Ev K Reg C) → Prop) (owned : Reg → Prop) (s : St K Reg C)
    (es es' : List (Ev K Reg C))
    (hU : rowSpan s ≤ U) (hnb : ∀ e ∈ es, NoBorn e) (hnb' : ∀ e ∈ es', NoBorn e)
    (hend : FullEnd U s es) (hend' : FullEnd U s es')
    (hsame : ownedEvents owned es = ownedEvents owned es') :
    AllLossless s es ∧ AllLossless s es' ∧
      (ErasureOK Sk owned s es ↔ ErasureOK Sk owned s es') := by
  have h1 : AllLossless s es := fun pre post i c h => every_clear_lossless U s es hU hnb hend pre post i c h
  have h2 : AllLossless s es' := fun pre post i c h => every_clear_lossless U s es' hU hnb' hend' pre post i c h
  refine ⟨h1, h2, ?_⟩
  unfold ErasureOK
  rw [hsame]
  exact ⟨fun h => ⟨h.1, h2⟩, fun h => ⟨h.1, h1⟩⟩

/-! ## Counterexample: "every non-CLEAR event keeps the rank" is false for COPY into a nonzero row -/

/-- Two public registers born with rows e_0, e_1. -/
def s2 : St ℚ (Fin 2) Unit := ⟨fun i => Pi.single i 1, fun _ => some ()⟩

/-- COPY 0 <- 1 onto the NONZERO row of register 0 silently erases it: the span loses e_0.
(PROOF.md section 1(a) is right only for COPY into a zero row, which check.py:119-120 enforces.) -/
theorem copy_nonzero_loses_rank :
    (Pi.single 0 1 : Fin 2 → ℚ) ∈ rowSpan s2 ∧
    (Pi.single 0 1 : Fin 2 → ℚ) ∉ rowSpan (step s2 (.copy 0 1 ())) := by
  refine ⟨row_mem s2 0, fun h => ?_⟩
  have hle : rowSpan (step s2 (.copy 0 1 ())) ≤ LinearMap.ker (LinearMap.proj (0 : Fin 2) : (Fin 2 → ℚ) →ₗ[ℚ] ℚ) := by
    refine Submodule.span_le.mpr ?_
    rintro _ ⟨j, rfl⟩
    fin_cases j <;> simp [step, s2, Function.update_apply, Pi.single_apply]
  have := hle h
  simp at this

/-! ## Toy instance in the real certificate format
Public registers 0,1,2 (rows e_0,e_1,e_2); owned register 3 is INITed, receives
`3 += (-1)*0` and `3 += 1*1`, and is CLEARed with certificate {0 : -1, 1 : 1}
(the 2-term shape of e.g. event 127621: {500 : -1, 1072 : 1}). -/

def t0 : St ℚ (Fin 4) Unit :=
  ⟨fun i => if i = 3 then 0 else Pi.single i 1, fun i => if i = 3 then none else some ()⟩

def tw : List (Ev ℚ (Fin 4) Unit) :=
  [.init 3 (), .add 3 0 (-1) (), .add 3 1 1 (), .clear 3 ()]

noncomputable def tcert : ℕ → Option (Fin 4 →₀ ℚ) :=
  fun n => if n = 3 then some (Finsupp.single 0 (-1) + Finsupp.single 1 1) else none

/-- Input space U = span of the three public inputs. -/
def tU : Submodule ℚ (Fin 4 → ℚ) := rowSpan t0

theorem toy_certified : GoodRun t0 tw ∧ Certified t0 tw tcert := by
  refine ⟨?_, ?_⟩
  · simp [GoodRun, Good, tw, step, t0, run, Function.update_apply]
  · refine ⟨trivial, trivial, trivial, ⟨Finsupp.single 0 (-1) + Finsupp.single 1 1,
      by simp [tcert], ?_, ?_⟩, trivial⟩
    · intro k hk
      have := Finsupp.support_add hk
      simp at this
      rcases this with h | h <;> simp [h, step, t0, Function.update_apply]
    · rw [map_add, Finsupp.linearCombination_single, Finsupp.linearCombination_single]
      ext k
      fin_cases k <;> simp [step, t0, Function.update_apply, Pi.single_apply]

/-- The toy word is endpoint-exact on the input space and its CLEAR is lossless (via the checker). -/
theorem toy_end : FullEnd tU t0 tw ∧
    ∀ pre post i c, tw = pre ++ .clear i c :: post → Lossless (run t0 pre) i :=
  checker_sound tU t0 tw tcert le_rfl le_rfl toy_certified.1 toy_certified.2

end ClearCert

open ClearCert in
#print axioms span_step_le
open ClearCert in
#print axioms span_step_ge
open ClearCert in
#print axioms lossless_iff
open ClearCert in
#print axioms every_clear_lossless
open ClearCert in
#print axioms finrank_clear_le
open ClearCert in
#print axioms certOK_lossless
open ClearCert in
#print axioms lossless_certOK
open ClearCert in
#print axioms checker_sound
open ClearCert in
#print axioms checker_complete
open ClearCert in
#print axioms legal_congr
open ClearCert in
#print axioms clearform
open ClearCert in
#print axioms copy_nonzero_loses_rank
open ClearCert in
#print axioms toy_end
