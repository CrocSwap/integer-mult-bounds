import MultitapeToolkit.IntegerMultiplicationCompilerApplications
import MultitapeToolkit.IntegerMultiplicationHeadReturn

set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false

/-!
# Multiplication with actual return of every tape head to origin

One fixed finite six-tape program executes the complete cleaned multiplier and
then the concrete paid head-return table. The input words and output cells are
literal; neither a coordinate relabeling nor a free return operation is used.
-/
namespace MultitapeToolkit.IntegerMultiplicationOriginRestored
open Lax51Proofs.RamToTM
open MultitapeToolkit.BinaryMultiplication MultitapeToolkit.BinaryMultiplicationIntegration
open MultitapeToolkit.Absolute.ControlEmbedding MultitapeToolkit.Absolute.Subroutines
open MultitapeToolkit.IntegerMultiplicationEngine MultitapeToolkit.IntegerMultiplicationCompilerApplications

abbrev Payload := CleanState ⊕ MultitapeToolkit.IntegerMultiplicationHeadReturn.Phase
abbrev State := Fin 2 × Payload

noncomputable def components : Fin 2 → MultitapeToolkit.Absolute.Program MulStack (Option Bool) Payload :=
  fun i => if i=0 then liftProgram cleanMachine Sum.inl leftDecode
    else liftProgram MultitapeToolkit.IntegerMultiplicationHeadReturn.program Sum.inr rightDecode

noncomputable def entry : Fin 2 → Payload :=
  fun i => if i=0 then .inl (cleanInput 0 0 0).state
    else .inr (MultitapeToolkit.IntegerMultiplicationHeadReturn.input 0 0).state

noncomputable def machine : MultitapeToolkit.Absolute.Program MulStack (Option Bool) State :=
  scheduler components entry

noncomputable def input (n a b : ℕ) : MultitapeToolkit.Absolute.Config MulStack (Option Bool) State :=
  stageCfg 0 (taggedCfg (R:=Payload) Sum.inl (cleanInput n a b))

noncomputable def output (n product : ℕ) : MultitapeToolkit.Absolute.Config MulStack (Option Bool) State :=
  stageCfg (Fin.last 1) (taggedCfg (R:=Payload) Sum.inr
    (MultitapeToolkit.IntegerMultiplicationHeadReturn.output n product))

/-- Every scan and every scheduler transition is charged; the halt is genuine. -/
theorem product_correct (n a b : ℕ) (ha : a<2^n) (hb : b<2^n) :
    ∃ t, t≤280*n^2+282*n+71 ∧
      MultitapeToolkit.Absolute.Runs machine t (input n a b) (output n (a*b)) ∧
      MultitapeToolkit.Absolute.Halts machine (output n (a*b)) ∧
      bitsValue ((fixedBits (2*n) (a*b)).reverse.reverse)=a*b := by
  rcases clean_product_tight n a b ha hb with ⟨t,ht,hr,hh,hvalue⟩
  have hs := MultitapeToolkit.IntegerMultiplicationHeadReturn.exact_correct n (a*b)
  have hFirst : MultitapeToolkit.Absolute.Runs (components 0) t
      (taggedCfg (R:=Payload) Sum.inl (cleanInput n a b))
      (taggedCfg (R:=Payload) Sum.inl (cleanOutput n (a*b))) := by
    simpa [components] using lift_runs cleanMachine Sum.inl leftDecode (fun _ => rfl) hr
  have hFirstHalt : MultitapeToolkit.Absolute.Halts (components 0)
      (taggedCfg (R:=Payload) Sum.inl (cleanOutput n (a*b))) := by
    simpa [components] using (lift_halts cleanMachine Sum.inl leftDecode (fun _ => rfl) _).2 hh
  have hSecond : MultitapeToolkit.Absolute.Runs (components (Fin.last 1)) (4*n+2)
      (taggedCfg (R:=Payload) Sum.inr (MultitapeToolkit.IntegerMultiplicationHeadReturn.input n (a*b)))
      (taggedCfg (R:=Payload) Sum.inr (MultitapeToolkit.IntegerMultiplicationHeadReturn.output n (a*b))) := by
    simpa [components] using lift_runs (R:=Payload) MultitapeToolkit.IntegerMultiplicationHeadReturn.program
      Sum.inr rightDecode (fun _ => rfl) hs.1
  have hSecondHalt : MultitapeToolkit.Absolute.Halts (components (Fin.last 1))
      (taggedCfg (R:=Payload) Sum.inr (MultitapeToolkit.IntegerMultiplicationHeadReturn.output n (a*b))) := by
    simpa [components] using (lift_halts (R:=Payload) MultitapeToolkit.IntegerMultiplicationHeadReturn.program
      Sum.inr rightDecode (fun _ => rfl) _).2 hs.2
  have hBank :
      (⟨entry (nextStage (0:Fin 2) (by decide)),
        (taggedCfg (R:=Payload) Sum.inl (cleanOutput n (a*b))).head,
        (taggedCfg (R:=Payload) Sum.inl (cleanOutput n (a*b))).cell⟩ :
        MultitapeToolkit.Absolute.Config MulStack (Option Bool) Payload) =
      taggedCfg (R:=Payload) Sum.inr (MultitapeToolkit.IntegerMultiplicationHeadReturn.input n (a*b)) := by
    apply MultitapeToolkit.Absolute.Config.ext <;> rfl
  have hHand := scheduler_handoff components entry (0:Fin 2) (by decide) _ hFirstHalt
  rw [hBank] at hHand
  have hOne : MultitapeToolkit.Absolute.Runs machine 1
      (stageCfg 0 (taggedCfg (R:=Payload) Sum.inl (cleanOutput n (a*b))))
      (stageCfg (Fin.last 1)
        (taggedCfg (R:=Payload) Sum.inr (MultitapeToolkit.IntegerMultiplicationHeadReturn.input n (a*b)))) :=
    .cons hHand (.refl _)
  have hFull := MultitapeToolkit.Absolute.Trace.runs_trans machine
    (MultitapeToolkit.Absolute.Trace.runs_trans machine
      (scheduler_stage_runs components entry 0 hFirst) hOne)
    (scheduler_stage_runs components entry (Fin.last 1) hSecond)
  refine ⟨t+1+(4*n+2),by omega,hFull,?_,hvalue⟩
  exact scheduler_last_halts components entry _ hSecondHalt

/-- Actual return puts all six heads at physical coordinate zero. -/
theorem output_heads (n product : ℕ) : (output n product).head=fun _ => 0 := by
  rfl

/-- Only the padded MSB product remains; every other tape is globally blank. -/
theorem output_cells (n product : ℕ) (k : MulStack) :
    (output n product).cell k =
      if k=.sumReverse then MultitapeToolkit.Absolute.StackOriginSerializer.originWord
        (fixedBits (2*n) product).reverse else fun _ => none := by
  rfl

/-- The original input ABI is retained: two literal padded LSB operand stacks. -/
theorem input_operands (n a b : ℕ) :
    (input n a b).cell .multiplier=
      MultitapeToolkit.Absolute.StackOriginSerializer.sourceStack 0 (fixedBits n b) ∧
    (input n a b).cell .multiplicand=
      MultitapeToolkit.Absolute.StackOriginSerializer.sourceStack 0 (fixedBits n a) :=
  clean_input_operands n a b

theorem input_heads (n a b : ℕ) : (input n a b).head=fun _ => 0 :=
  (clean_input_control_and_heads n a b).2

theorem input_control (n a b : ℕ) : (input n a b).state=(input 0 0 0).state := rfl

theorem input_work_blank (n a b : ℕ) (k : MulStack)
    (hk : k≠.multiplier ∧ k≠.multiplicand) :
    (input n a b).cell k=fun _ => none := clean_input_work_blank n a b k hk

end MultitapeToolkit.IntegerMultiplicationOriginRestored
