import Current1094Row1FamilyBlocks
import Current1094CallSequenceRouting

/-!
Selected call000 raw2 is ADD(L119,L169,1/2), with source frame annotation0.
This module defines a new exact-real reference implementation: read the source
component, halve it, add the current target component, and write the target.
The instruction language embeds the unchanged core used by the accepted dyadic
SCALE interpreter. Only addMemory is new; its later encoded implementation needs
explicit common-exponent alignment, not a same-grid assumption.

Disjoint consecutive family blocks preserve every source read. The accepted
own-coordinate fold then derives the target result; every other family view is
unchanged. Bank's accepted call0 dataOwner supplies the literal families and
injection. No helper-table decision or arbitrary executor equality is assumed.

An untransported ADD on physical components agrees with Hosting when its two
whole-family charts agree. The emitted frame0 annotation alone does not prove
that chart premise. Actual selected numeric allocation, primitive code,
rounding, bit costs and scratch cleanup remain separate.

Canonical PR509/516/1309, bank routing and machine reference attributions stay
with their exact predecessors. New work prepared with OpenAI assistance.
Apache-2.0. Uncompiled source proposal.
-/
set_option Elab.async false
noncomputable section
namespace CurrentMain.Current1094Row2AddReference

open ComponentStoreFoldRefinement ReferenceMinusHalfStore IndependentEntryFold
open Current1094Row1FamilyBlocks Current1094CallSequenceRouting

/-- Core instructions and their exact state are shared with the accepted dyadic
SCALE interpreter. An encoded addMemory must separately align exponents. -/
inductive Instruction where
  | core (op : Current1094Row1FlatReference.Instruction)
  | addMemory (address : ℕ)

def addMemory (a : ℕ) (s : RefState ℕ) : RefState ℕ :=
  ⟨s.memory, s.memory a + s.accumulator⟩

def executeInstruction : Instruction → RefState ℕ → RefState ℕ
  | .core op => Current1094Row1FlatReference.executeInstruction op
  | .addMemory a => addMemory a

def execute : List Instruction → RefState ℕ → RefState ℕ
  | [], s => s
  | op :: ops, s => execute ops (executeInstruction op s)

theorem execute_core (ops : List Current1094Row1FlatReference.Instruction)
    (s : RefState ℕ) :
    execute (ops.map Instruction.core) s = Current1094Row1FlatReference.execute ops s := by
  induction ops generalizing s with
  | nil => rfl
  | cons op ops ih => exact ih (Current1094Row1FlatReference.executeInstruction op s)

def componentCode (target source : ℕ) : List Instruction :=
  [.core (.read source), .core .halve, .addMemory target, .core (.write target)]

def addStep (target source : ℕ) (s : RefState ℕ) : RefState ℕ :=
  execute (componentCode target source) s

/-- The memory update follows from the four operations, with no assumed result. -/
theorem addStep_memory (target source : ℕ) (s : RefState ℕ) :
    (addStep target source s).memory =
      Function.update s.memory target
        (s.memory target + (1 / 2 : ℝ) * s.memory source) := by
  change Function.update s.memory target (s.memory target + s.memory source / 2) = _
  have he : s.memory target + s.memory source / 2 =
      s.memory target + (1 / 2 : ℝ) * s.memory source := by ring
  rw [he]

/-- The arithmetic result remains in the visible scratch accumulator. -/
theorem addStep_accumulator (target source : ℕ) (s : RefState ℕ) :
    (addStep target source s).accumulator =
      s.memory target + (1 / 2 : ℝ) * s.memory source := by
  change s.memory target + s.memory source / 2 = _
  ring

def addRun {I : Type*} (target source : I → ℕ) : List I → RefState ℕ → RefState ℕ
  | [], s => s
  | i :: rest, s => addRun target source rest (addStep (target i) (source i) s)

def emit {I : Type*} (target source : I → ℕ) : List I → List Instruction
  | [] => []
  | i :: rest => componentCode (target i) (source i) ++ emit target source rest

private theorem execute_append (xs ys : List Instruction) (s : RefState ℕ) :
    execute (xs ++ ys) s = execute ys (execute xs s) := by
  induction xs generalizing s with
  | nil => rfl
  | cons op ops ih => exact ih (executeInstruction op s)

theorem execute_emit {I : Type*} (target source : I → ℕ)
    (order : List I) (s : RefState ℕ) :
    execute (emit target source order) s = addRun target source order s := by
  induction order generalizing s with
  | nil => rfl
  | cons i rest ih =>
      simpa only [emit, execute_append, addRun, addStep]
        using ih (addStep (target i) (source i) s)

private theorem emit_length {I : Type*} (target source : I → ℕ) (order : List I) :
    (emit target source order).length = 4 * order.length := by
  induction order with
  | nil => rfl
  | cons i rest ih =>
      simp only [emit, List.length_append, componentCode, List.length_cons,
        List.length_nil, ih]
      omega

/-- Reads remain the original source values because every source address is
disjoint from every target address. This is an invariant, not a replay premise. -/
theorem addRun_source {I : Type*} (target source : I → ℕ)
    (hsep : ∀ i j, source i ≠ target j) (order : List I) (s : RefState ℕ) (i : I) :
    (addRun target source order s).memory (source i) = s.memory (source i) := by
  induction order generalizing s with
  | nil => rfl
  | cons j rest ih =>
      rw [addRun, ih, addStep_memory, Function.update_of_ne (hsep i j)]

/-- Exact reduction to the already checked independent-update fold. The source
values are read-only; the target reads its own current value. -/
theorem addRun_target_projection {I : Type*} [DecidableEq I]
    (target source : I → ℕ) (hinj : Function.Injective target)
    (hsep : ∀ i j, source i ≠ target j) (values : I → ℝ)
    (order : List I) (s : RefState ℕ) (hread : ∀ i, s.memory (source i) = values i) :
    (fun i => (addRun target source order s).memory (target i)) =
      runUpdates (fun i v => v + (1 / 2 : ℝ) * values i) order
        (fun i => s.memory (target i)) := by
  induction order generalizing s with
  | nil => rfl
  | cons j rest ih =>
      have hnext : ∀ i,
          (addStep (target j) (source j) s).memory (source i) = values i := by
        intro i
        rw [addStep_memory, Function.update_of_ne (hsep i j)]
        exact hread i
      have hupdate :
          (fun i => (addStep (target j) (source j) s).memory (target i)) =
          Function.update (fun i => s.memory (target i)) j
            (s.memory (target j) + (1 / 2 : ℝ) * values j) := by
        simp only [addStep_memory]
        rw [hread j]
        exact Function.update_comp_eq_of_injective' s.memory hinj j _
      calc
        (fun i => (addRun target source (j :: rest) s).memory (target i)) =
            runUpdates (fun i v => v + (1 / 2 : ℝ) * values i) rest
              (fun i => (addStep (target j) (source j) s).memory (target i)) :=
          ih (addStep (target j) (source j) s) hnext
        _ = runUpdates (fun i v => v + (1 / 2 : ℝ) * values i) rest
              (Function.update (fun i => s.memory (target i)) j
                (s.memory (target j) + (1 / 2 : ℝ) * values j)) := by rw [hupdate]
        _ = _ := rfl

private theorem addRun_outside {I : Type*} (target source : I → ℕ)
    (order : List I) (s : RefState ℕ) (a : ℕ) (ha : a ∉ order.map target) :
    (addRun target source order s).memory a = s.memory a := by
  induction order generalizing s with
  | nil => rfl
  | cons i rest ih =>
      have h : a ≠ target i ∧ a ∉ rest.map target := by
        simpa only [List.map_cons, List.mem_cons, not_or] using ha
      rw [addRun, ih _ h.2, addStep_memory, Function.update_of_ne h.1]

def address (n f : ℕ) : Slot (Fin n) → ℕ :=
  Current1094Row1FlatReference.flatAddress (familyBase n f)

theorem address_separation (n target source : ℕ) (hne : source ≠ target)
    (i j : Slot (Fin n)) : address n source i ≠ address n target j := by
  intro heq
  have ho := other_block_outside n target source hne i
  have hb := Current1094Row1FlatReference.flatAddress_bounds n (familyBase n target) j
  change Current1094Row1FlatReference.flatAddress (familyBase n source) i =
    Current1094Row1FlatReference.flatAddress (familyBase n target) j at heq
  omega

def program (n target source : ℕ) : List Instruction :=
  emit (address n target) (address n source)
    (Current1094Row1FlatReference.componentOrder n)

theorem program_length (n target source : ℕ) :
    (program n target source).length = 8 * n := by
  rw [program, emit_length, Current1094Row1FlatReference.componentOrder_length]
  omega

/-- Every target slot is visited exactly once and reads an unchanged source. -/
theorem program_slot (n target source : ℕ) (hne : source ≠ target)
    (s : RefState ℕ) (slot : Slot (Fin n)) :
    (execute (program n target source) s).memory (address n target slot) =
      s.memory (address n target slot) + (1 / 2 : ℝ) * s.memory (address n source slot) := by
  rw [program, execute_emit]
  have h := addRun_target_projection (address n target) (address n source)
    (Current1094Row1FlatReference.flatAddress_injective n (familyBase n target))
    (address_separation n target source hne)
    (fun i => s.memory (address n source i))
    (Current1094Row1FlatReference.componentOrder n) s (fun _ => rfl)
  exact (congrFun h slot).trans
    (runUpdates_of_mem _ _ (Current1094Row1FlatReference.componentOrder_nodup n)
      slot (Current1094Row1FlatReference.componentOrder_complete n slot) _)

private theorem program_other_address (n target source other : ℕ)
    (hne : other ≠ target) (s : RefState ℕ) (slot : Slot (Fin n)) :
    (execute (program n target source) s).memory (address n other slot) =
      s.memory (address n other slot) := by
  rw [program, execute_emit]
  apply addRun_outside
  intro hm
  rcases List.mem_map.mp hm with ⟨j, _, heq⟩
  exact address_separation n target other hne slot j heq.symm

private theorem decode_add_real (n : ℕ) (x y : Slot (Fin n) → ℝ) (q : ℝ) :
    decode (fun i => x i + q * y i) = decode x + (q : ℂ) • decode y := by
  apply PiLp.ext
  intro i
  apply Complex.ext
  · change x (.inl i) + q * y (.inl i) =
      ((⟨x (.inl i), x (.inr i)⟩ : ℂ) +
        (q : ℂ) * ⟨y (.inl i), y (.inr i)⟩).re
    simp only [Complex.add_re, Complex.mul_re, Complex.ofReal_re, Complex.ofReal_im,
      zero_mul, sub_zero]
  · change x (.inr i) + q * y (.inr i) =
      ((⟨x (.inl i), x (.inr i)⟩ : ℂ) +
        (q : ℂ) * ⟨y (.inl i), y (.inr i)⟩).im
    simp only [Complex.add_im, Complex.mul_im, Complex.ofReal_re, Complex.ofReal_im,
      zero_mul, add_zero]

theorem program_target_view (n target source : ℕ) (hne : source ≠ target)
    (s : RefState ℕ) :
    familyViews n (execute (program n target source) s).memory target =
      familyViews n s.memory target + ((1 / 2 : ℝ) : ℂ) • familyViews n s.memory source := by
  have h : (fun slot => (execute (program n target source) s).memory (address n target slot)) =
      (fun slot => s.memory (address n target slot) +
        (1 / 2 : ℝ) * s.memory (address n source slot)) := by
    funext slot
    exact program_slot n target source hne s slot
  change decode (fun slot => (execute (program n target source) s).memory
    (address n target slot)) = decode (fun slot => s.memory (address n target slot)) +
      ((1 / 2 : ℝ) : ℂ) • decode (fun slot => s.memory (address n source slot))
  rw [h]
  exact decode_add_real n _ _ (1 / 2)

theorem program_other_view (n target source other : ℕ) (hne : other ≠ target)
    (s : RefState ℕ) :
    familyViews n (execute (program n target source) s).memory other =
      familyViews n s.memory other := by
  apply PiLp.ext
  intro i
  apply Complex.ext
  · exact program_other_address n target source other hne s (.inl i)
  · exact program_other_address n target source other hne s (.inr i)

/-- Complete family-view update, including unchanged source and all spectators. -/
theorem familyViews_update (n target source : ℕ) (hne : source ≠ target)
    (s : RefState ℕ) :
    familyViews n (execute (program n target source) s).memory =
      Function.update (familyViews n s.memory) target
        (familyViews n s.memory target + ((1 / 2 : ℝ) : ℂ) • familyViews n s.memory source) := by
  funext other
  by_cases h : other = target
  · subst other
    rw [Function.update_self]
    exact program_target_view n target source hne s
  · rw [Function.update_of_ne h]
    exact program_other_view n target source other h s

/-- These two ordinary owners come from bank's accepted call0 routing. -/
def selectedTargetFamily : ℕ := (dataOwner 0 119).val
def selectedSourceFamily : ℕ := (dataOwner 0 169).val

theorem selected_family_literals : selectedTargetFamily = 119 ∧ selectedSourceFamily = 169 :=
  ⟨rfl, rfl⟩

theorem selected_families_ne : selectedSourceFamily ≠ selectedTargetFamily := by
  intro h
  have heq : dataOwner 0 (169 : Fin 224) = dataOwner 0 (119 : Fin 224) := Fin.ext h
  have hi := dataOwner_injective 0 heq
  have hv := congrArg Fin.val hi
  change (169 : ℕ) = 119 at hv
  omega

def selectedProgram (n : ℕ) : List Instruction :=
  program n selectedTargetFamily selectedSourceFamily

theorem selected_familyViews_update (n : ℕ) (s : RefState ℕ) :
    familyViews n (execute (selectedProgram n) s).memory =
      Function.update (familyViews n s.memory) selectedTargetFamily
        (familyViews n s.memory selectedTargetFamily +
          ((1 / 2 : ℝ) : ℂ) • familyViews n s.memory selectedSourceFamily) :=
  familyViews_update n selectedTargetFamily selectedSourceFamily selected_families_ne s

section Hosting
variable {I Φ Λ K W M : Type*} [DecidableEq I] [DecidableEq Φ]
  [Semiring K] [AddCommMonoid W] [Module K W] [AddCommMonoid M] [Module K M]

/-- General ADD exposes the chart transport of the source into target coordinates. -/
theorem realize_add (σ : LemmaA.Hosting I Φ K W M) (rec : Λ → Λ → M → M)
    (target source : I) (q : K) (y : Φ → W) :
    LemmaA.realize σ rec (.add target source q) y =
      Function.update y (σ.own target)
        (y (σ.own target) + q • (σ.chart target).symm (σ.chart source (y (σ.own source)))) := by
  simp only [LemmaA.realize, LemmaA.dst, LemmaG.Event.phys, Function.update_self,
    LemmaA.view, LinearEquiv.map_add, LinearEquiv.map_smul, LinearEquiv.symm_apply_apply]

theorem realize_add_common_chart (σ : LemmaA.Hosting I Φ K W M)
    (rec : Λ → Λ → M → M) (target source : I) (q : K)
    (hchart : σ.chart source = σ.chart target) (y : Φ → W) :
    LemmaA.realize σ rec (.add target source q) y =
      Function.update y (σ.own target) (y (σ.own target) + q • y (σ.own source)) := by
  rw [realize_add, hchart]
  simp only [LinearEquiv.symm_apply_apply]
end Hosting

def selectedTarget : Current1094PrivateCentreHosting.Register := .inl 119
def selectedSource : Current1094PrivateCentreHosting.Register := .inl 169
def selectedRow2 : LemmaG.Event Current1094PrivateCentreHosting.Register (Fin 1004) ℂ :=
  .add selectedTarget selectedSource ((1 / 2 : ℝ) : ℂ)

/-- No global executor equality is assumed. Only the actual two owner fields
and common whole-family chart needed by this particular physical ADD remain. -/
theorem selected_refines_realize {n : ℕ} {M : Type*} [AddCommMonoid M] [Module ℂ M]
    (σ : LemmaA.Hosting Current1094PrivateCentreHosting.Register ℕ ℂ
      (EuclideanSpace ℂ (Fin n)) M) (rec : Fin 1004 → Fin 1004 → M → M)
    (ht : σ.own selectedTarget = selectedTargetFamily)
    (hs : σ.own selectedSource = selectedSourceFamily)
    (hchart : σ.chart selectedSource = σ.chart selectedTarget) (s : RefState ℕ) :
    familyViews n (execute (selectedProgram n) s).memory =
      LemmaA.realize σ rec selectedRow2 (familyViews n s.memory) := by
  rw [selected_familyViews_update]
  change _ = LemmaA.realize σ rec (.add selectedTarget selectedSource ((1 / 2 : ℝ) : ℂ)) _
  rw [realize_add_common_chart σ rec selectedTarget selectedSource _ hchart, ht, hs]

end CurrentMain.Current1094Row2AddReference

#print axioms CurrentMain.Current1094Row2AddReference.execute_core
#print axioms CurrentMain.Current1094Row2AddReference.addStep_memory
#print axioms CurrentMain.Current1094Row2AddReference.addStep_accumulator
#print axioms CurrentMain.Current1094Row2AddReference.addRun_source
#print axioms CurrentMain.Current1094Row2AddReference.addRun_target_projection
#print axioms CurrentMain.Current1094Row2AddReference.program_length
#print axioms CurrentMain.Current1094Row2AddReference.familyViews_update
#print axioms CurrentMain.Current1094Row2AddReference.selected_family_literals
#print axioms CurrentMain.Current1094Row2AddReference.selected_families_ne
#print axioms CurrentMain.Current1094Row2AddReference.selected_familyViews_update
#print axioms CurrentMain.Current1094Row2AddReference.realize_add
#print axioms CurrentMain.Current1094Row2AddReference.selected_refines_realize
#check @CurrentMain.Current1094Row2AddReference.selected_familyViews_update
#check @CurrentMain.Current1094Row2AddReference.selected_refines_realize
