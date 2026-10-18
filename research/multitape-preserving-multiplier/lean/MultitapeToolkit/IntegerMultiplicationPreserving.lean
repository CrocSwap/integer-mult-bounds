import MultitapeToolkit.IntegerMultiplicationOriginRestored
import MultitapeToolkit.PairedInputCopy
import MultitapeToolkit.TapeEmbedding
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false

/-!
# Actual multiplication retaining both input words

Two protectedCells operand tapes are copied by a concrete finite table into the
six-tape multiplier's ordinary input ABI. Both stages return their actual heads
to zero. The original operand banks survive the arithmetic literally.
-/
namespace MultitapeToolkit.IntegerMultiplicationPreserving
open MultitapeToolkit.Absolute
open MultitapeToolkit.Absolute.ControlEmbedding MultitapeToolkit.Absolute.Subroutines
open MultitapeToolkit.BinaryMultiplication Lax51Proofs.RamToTM

abbrev Bank := Fin 2 ⊕ MulStack

def copyEmbedding : MultitapeToolkit.Absolute.PairedInputCopy.PairTape ↪ Bank where
  toFun
    | .sourceA => .inl 0
    | .sourceB => .inl 1
    | .destA => .inr .multiplicand
    | .destB => .inr .multiplier
  inj' := by
    intro i j h
    cases i <;> cases j <;> simp_all

def coreEmbedding : MulStack ↪ Bank := ⟨Sum.inr,Sum.inr_injective⟩

@[simp] theorem core_decode_left (i : Fin 2) : TapeEmbedding.decode coreEmbedding (.inl i)=none := by
  apply (TapeEmbedding.decode_none _ _).2
  rintro ⟨k,hk⟩
  cases hk

@[simp] theorem core_decode_right (k : MulStack) : TapeEmbedding.decode coreEmbedding (.inr k)=some k :=
  TapeEmbedding.decode_image coreEmbedding k

@[simp] theorem copy_decode_left (i : Fin 2) : TapeEmbedding.decode copyEmbedding (.inl i)=
    some (if i=0 then MultitapeToolkit.Absolute.PairedInputCopy.PairTape.sourceA else .sourceB) := by
  by_cases hi : i=0
  · subst i
    exact TapeEmbedding.decode_image copyEmbedding .sourceA
  · have hi1 : i=1 := by
      apply Fin.ext
      have hb := i.isLt
      have hn : i.val≠0 := fun h => hi (Fin.ext h)
      omega
    subst i
    exact TapeEmbedding.decode_image copyEmbedding .sourceB

@[simp] theorem copy_decode_right (k : MulStack) : TapeEmbedding.decode copyEmbedding (.inr k)=
    match k with | .multiplicand => some MultitapeToolkit.Absolute.PairedInputCopy.PairTape.destA
                 | .multiplier => some .destB | _ => none := by
  cases k with
  | multiplier => exact TapeEmbedding.decode_image copyEmbedding .destB
  | multiplicand => exact TapeEmbedding.decode_image copyEmbedding .destA
  | accumulator =>
    apply (TapeEmbedding.decode_none _ _).2
    rintro ⟨i,hi⟩
    cases i <;> cases hi
  | multiplicandBackup =>
    apply (TapeEmbedding.decode_none _ _).2
    rintro ⟨i,hi⟩
    cases i <;> cases hi
  | sumReverse =>
    apply (TapeEmbedding.decode_none _ _).2
    rintro ⟨i,hi⟩
    cases i <;> cases hi
  | shiftTemp =>
    apply (TapeEmbedding.decode_none _ _).2
    rintro ⟨i,hi⟩
    cases i <;> cases hi

/-- These are actual supplied operand tapes, with blank unused working bank. -/
noncomputable def protectedCells (n a b : ℕ) : Bank → ℤ → Option Bool
  | .inl i => if i=0 then StackOriginSerializer.sourceStack 0 (fixedBits n a)
              else StackOriginSerializer.sourceStack 0 (fixedBits n b)
  | .inr _ => fun _ => none

noncomputable def copying : MultitapeToolkit.Absolute.Program Bank (Option Bool) MultitapeToolkit.Absolute.PairedInputCopy.Phase :=
  TapeEmbedding.liftProgram copyEmbedding MultitapeToolkit.Absolute.PairedInputCopy.program

noncomputable def copyingInput (n a b : ℕ) : MultitapeToolkit.Absolute.Config Bank (Option Bool) MultitapeToolkit.Absolute.PairedInputCopy.Phase :=
  TapeEmbedding.liftCfg copyEmbedding (MultitapeToolkit.Absolute.PairedInputCopy.input (fixedBits n a) (fixedBits n b))
    (fun _ => 0) (protectedCells n a b)
noncomputable def copyingOutput (n a b : ℕ) : MultitapeToolkit.Absolute.Config Bank (Option Bool) MultitapeToolkit.Absolute.PairedInputCopy.Phase :=
  TapeEmbedding.liftCfg copyEmbedding (MultitapeToolkit.Absolute.PairedInputCopy.output (fixedBits n a) (fixedBits n b))
    (fun _ => 0) (protectedCells n a b)

noncomputable def core : MultitapeToolkit.Absolute.Program Bank (Option Bool) MultitapeToolkit.IntegerMultiplicationOriginRestored.State :=
  TapeEmbedding.liftProgram coreEmbedding MultitapeToolkit.IntegerMultiplicationOriginRestored.machine
noncomputable def coreInput (n a b : ℕ) : MultitapeToolkit.Absolute.Config Bank (Option Bool) MultitapeToolkit.IntegerMultiplicationOriginRestored.State :=
  TapeEmbedding.liftCfg coreEmbedding (MultitapeToolkit.IntegerMultiplicationOriginRestored.input n a b) (fun _ => 0) (protectedCells n a b)
noncomputable def coreOutput (n a b : ℕ) : MultitapeToolkit.Absolute.Config Bank (Option Bool) MultitapeToolkit.IntegerMultiplicationOriginRestored.State :=
  TapeEmbedding.liftCfg coreEmbedding (MultitapeToolkit.IntegerMultiplicationOriginRestored.output n (a*b)) (fun _ => 0) (protectedCells n a b)

/-- The physical copier finishes at the literal arithmetic bank, including heads. -/
theorem boundary (n a b : ℕ) :
    (copyingOutput n a b).head=(coreInput n a b).head ∧
      (copyingOutput n a b).cell=(coreInput n a b).cell := by
  constructor
  · funext k
    cases k with
    | inl i => simp [copyingOutput,coreInput,TapeEmbedding.liftCfg,MultitapeToolkit.Absolute.PairedInputCopy.output,MultitapeToolkit.IntegerMultiplicationOriginRestored.input_heads]
    | inr k => cases k <;> simp [copyingOutput,coreInput,TapeEmbedding.liftCfg,MultitapeToolkit.Absolute.PairedInputCopy.output,MultitapeToolkit.IntegerMultiplicationOriginRestored.input_heads]
  · funext k
    cases k with
    | inl i =>
      by_cases hi : i=0 <;> simp [copyingOutput,coreInput,TapeEmbedding.liftCfg,MultitapeToolkit.Absolute.PairedInputCopy.output,protectedCells,hi]
    | inr k =>
      cases k <;> simp [copyingOutput,coreInput,TapeEmbedding.liftCfg,MultitapeToolkit.Absolute.PairedInputCopy.output,
        MultitapeToolkit.IntegerMultiplicationOriginRestored.input_operands,MultitapeToolkit.IntegerMultiplicationOriginRestored.input_work_blank,protectedCells]

abbrev Payload := MultitapeToolkit.Absolute.PairedInputCopy.Phase ⊕ MultitapeToolkit.IntegerMultiplicationOriginRestored.State
abbrev State := Fin 2 × Payload
noncomputable def components : Fin 2 → MultitapeToolkit.Absolute.Program Bank (Option Bool) Payload :=
  fun i => if i=0 then liftProgram copying Sum.inl leftDecode else liftProgram core Sum.inr rightDecode
noncomputable def entry : Fin 2 → Payload :=
  fun i => if i=0 then .inl (copyingInput 0 0 0).state else .inr (coreInput 0 0 0).state
noncomputable def machine : MultitapeToolkit.Absolute.Program Bank (Option Bool) State := scheduler components entry
noncomputable def input (n a b : ℕ) : MultitapeToolkit.Absolute.Config Bank (Option Bool) State :=
  stageCfg 0 (taggedCfg (R:=Payload) Sum.inl (copyingInput n a b))
noncomputable def output (n a b : ℕ) : MultitapeToolkit.Absolute.Config Bank (Option Bool) State :=
  stageCfg (Fin.last 1) (taggedCfg (R:=Payload) Sum.inr (coreOutput n a b))

/-- The originals are retained, the core work is erased, and actual halt occurs. -/
theorem product_correct (n a b : ℕ) (ha : a<2^n) (hb : b<2^n) :
    ∃ t, t≤280*n^2+284*n+74 ∧ MultitapeToolkit.Absolute.Runs machine t (input n a b) (output n a b) ∧
      MultitapeToolkit.Absolute.Halts machine (output n a b) ∧
      bitsValue ((fixedBits (2*n) (a*b)).reverse.reverse)=a*b := by
  have hc := MultitapeToolkit.Absolute.PairedInputCopy.exact_correct (fixedBits n a) (fixedBits n b) (by simp)
  have hcr := TapeEmbedding.lift_runs copyEmbedding MultitapeToolkit.Absolute.PairedInputCopy.program hc.1 (fun _ => 0) (protectedCells n a b)
  have hch := (TapeEmbedding.lift_halts copyEmbedding MultitapeToolkit.Absolute.PairedInputCopy.program _ (fun _ => 0) (protectedCells n a b)).2 hc.2
  rcases MultitapeToolkit.IntegerMultiplicationOriginRestored.product_correct n a b ha hb with ⟨t,ht,hr,hh,hvalue⟩
  have hpr := TapeEmbedding.lift_runs coreEmbedding MultitapeToolkit.IntegerMultiplicationOriginRestored.machine hr (fun _ => 0) (protectedCells n a b)
  have hph := (TapeEmbedding.lift_halts coreEmbedding MultitapeToolkit.IntegerMultiplicationOriginRestored.machine _ (fun _ => 0) (protectedCells n a b)).2 hh
  have hFirst : MultitapeToolkit.Absolute.Runs (components 0) (2*n+2)
      (taggedCfg (R:=Payload) Sum.inl (copyingInput n a b))
      (taggedCfg (R:=Payload) Sum.inl (copyingOutput n a b)) := by
    simpa [components,copying,copyingInput,copyingOutput] using
      lift_runs copying Sum.inl leftDecode (fun _ => rfl) hcr
  have hFirstHalt : MultitapeToolkit.Absolute.Halts (components 0) (taggedCfg (R:=Payload) Sum.inl (copyingOutput n a b)) := by
    simpa [components,copying,copyingOutput] using
      (lift_halts copying Sum.inl leftDecode (fun _ => rfl) _).2 hch
  have hSecond : MultitapeToolkit.Absolute.Runs (components (Fin.last 1)) t
      (taggedCfg (R:=Payload) Sum.inr (coreInput n a b))
      (taggedCfg (R:=Payload) Sum.inr (coreOutput n a b)) := by
    simpa [components,core,coreInput,coreOutput] using
      lift_runs (R:=Payload) core Sum.inr rightDecode (fun _ => rfl) hpr
  have hSecondHalt : MultitapeToolkit.Absolute.Halts (components (Fin.last 1))
      (taggedCfg (R:=Payload) Sum.inr (coreOutput n a b)) := by
    simpa [components,core,coreOutput] using
      (lift_halts (R:=Payload) core Sum.inr rightDecode (fun _ => rfl) _).2 hph
  have hBank :
      (⟨entry (nextStage (0:Fin 2) (by decide)),
        (taggedCfg (R:=Payload) Sum.inl (copyingOutput n a b)).head,
        (taggedCfg (R:=Payload) Sum.inl (copyingOutput n a b)).cell⟩ :
        MultitapeToolkit.Absolute.Config Bank (Option Bool) Payload) = taggedCfg (R:=Payload) Sum.inr (coreInput n a b) := by
    apply MultitapeToolkit.Absolute.Config.ext
    · rfl
    · exact (boundary n a b).1
    · exact (boundary n a b).2
  have hHand := scheduler_handoff components entry (0:Fin 2) (by decide) _ hFirstHalt
  rw [hBank] at hHand
  have hOne : MultitapeToolkit.Absolute.Runs machine 1
      (stageCfg 0 (taggedCfg (R:=Payload) Sum.inl (copyingOutput n a b)))
      (stageCfg (Fin.last 1) (taggedCfg (R:=Payload) Sum.inr (coreInput n a b))) :=
    .cons hHand (.refl _)
  have hFull := MultitapeToolkit.Absolute.Trace.runs_trans machine
    (MultitapeToolkit.Absolute.Trace.runs_trans machine (scheduler_stage_runs components entry 0 hFirst) hOne)
    (scheduler_stage_runs components entry (Fin.last 1) hSecond)
  exact ⟨(2*n+2)+1+t,by omega,hFull,scheduler_last_halts components entry _ hSecondHalt,hvalue⟩

/-- Every head, including both protectedCells input heads, physically returns to zero. -/
theorem output_heads (n a b : ℕ) : (output n a b).head=fun _ => 0 := by
  funext k
  cases k <;> simp [output,stageCfg,taggedCfg,coreOutput,TapeEmbedding.liftCfg,MultitapeToolkit.IntegerMultiplicationOriginRestored.output_heads]

theorem output_protected (n a b : ℕ) (i : Fin 2) :
    (output n a b).cell (.inl i)=
      if i=0 then StackOriginSerializer.sourceStack 0 (fixedBits n a)
      else StackOriginSerializer.sourceStack 0 (fixedBits n b) := by
  simp [output,stageCfg,taggedCfg,coreOutput,TapeEmbedding.liftCfg,protectedCells]

theorem output_work (n a b : ℕ) (k : MulStack) :
    (output n a b).cell (.inr k)=
      if k=.sumReverse then StackOriginSerializer.originWord (fixedBits (2*n) (a*b)).reverse
      else fun _ => none := by
  simp [output,stageCfg,taggedCfg,coreOutput,TapeEmbedding.liftCfg,MultitapeToolkit.IntegerMultiplicationOriginRestored.output_cells]

theorem input_heads (n a b : ℕ) : (input n a b).head=fun _ => 0 := by
  funext k
  cases k with
  | inl i => simp [input,stageCfg,taggedCfg,copyingInput,TapeEmbedding.liftCfg]
  | inr k => cases k <;> simp [input,stageCfg,taggedCfg,copyingInput,TapeEmbedding.liftCfg]

theorem input_protected (n a b : ℕ) (i : Fin 2) :
    (input n a b).cell (.inl i)=
      if i=0 then StackOriginSerializer.sourceStack 0 (fixedBits n a)
      else StackOriginSerializer.sourceStack 0 (fixedBits n b) := by
  by_cases hi : i=0 <;>
    simp [input,stageCfg,taggedCfg,copyingInput,TapeEmbedding.liftCfg,hi]

theorem input_work_blank (n a b : ℕ) (k : MulStack) :
    (input n a b).cell (.inr k)=fun _ => none := by
  cases k <;> simp [input,stageCfg,taggedCfg,copyingInput,TapeEmbedding.liftCfg,protectedCells]

theorem input_control (n a b : ℕ) : (input n a b).state=(input 0 0 0).state := rfl

/-- Equality of whole protectedCells input tapes, including every exterior cell. -/
theorem preserves_inputs (n a b : ℕ) (i : Fin 2) :
    (output n a b).cell (.inl i)=(input n a b).cell (.inl i) := by
  rw [output_protected,input_protected]

end MultitapeToolkit.IntegerMultiplicationPreserving
