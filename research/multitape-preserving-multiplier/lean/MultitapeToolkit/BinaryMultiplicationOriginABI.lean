import MultitapeToolkit.TM2AnchoredCompiler
import MultitapeToolkit.Reused.Computability.BinaryMultitape20261013
import MultitapeToolkit.SubroutineContracts
import MultitapeToolkit.ControlEmbedding
import MultitapeToolkit.StackOriginSerializer

/-!
# Quadratic arithmetic at a physically anchored tape ABI

The ordinary padded LSB operands occupy two compiler stacks, both initially
headed at zero; all four work tapes are globally blank. The bottom anchors
are retained through actual finite-control arithmetic. A later charged
serializer exports the padded MSB product to sumReverse at physical origin.
This interface does not claim single-tape serialized input or complete
arithmetic-workspace cleanup.
-/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
namespace MultitapeToolkit.BinaryMultiplicationOriginABI
open Turing Lax51Proofs.RamToTM
open MultitapeToolkit.BinaryMultiplication MultitapeToolkit.BinaryMultiplicationIntegration
open MultitapeToolkit.TM2Compiler MultitapeToolkit.TM2Compiler.Anchored
open MultitapeToolkit.Locality
open MultitapeToolkit.Absolute

local instance : Fintype setupMachine.K := inferInstanceAs (Fintype MulStack)
local instance : Fintype setupMachine.Λ := inferInstanceAs (Fintype SetupLabel)
local instance : Fintype setupMachine.σ := inferInstanceAs (Fintype MulControl)

/-- Only the two length-n input stacks have nonzero bottom anchors. -/
def anchors (n : ℕ) : MulStack → ℤ
  | .multiplier | .multiplicand => n
  | _ => 0

noncomputable def arithmetic : Program MulStack (Option Bool) (Control setupMachine.m) :=
  ofMachine (compile setupMachine.m)

noncomputable def arithmeticInput (n a b : ℕ) : MultitapeToolkit.Absolute.Config MulStack (Option Bool) (Control setupMachine.m) :=
  anchoredEncode setupMachine.m (anchors n) (rawInput n a b)

noncomputable def arithmeticEnd (n product : ℕ) (finalMultiplicand : List Bool) :
    MultitapeToolkit.Absolute.Config MulStack (Option Bool) (Control setupMachine.m) :=
  anchoredEncode setupMachine.m (anchors n)
    (liftMulCfg (mulHaltedCfg finalMultiplicand (fixedBits (2*n) product)))

/-- The physical input heads are all zero, including when n=0. -/
theorem arithmeticInput_heads (n a b : ℕ) : (arithmeticInput n a b).head = fun _ => 0 := by
  funext k
  cases k <;> simp [arithmeticInput,anchoredEncode,realize,stackHeads,anchors,rawInput,mulStacks]

/-- The machine entry state is fixed independently of length and operand values. -/
theorem arithmeticInput_state (n a b : ℕ) :
    (arithmeticInput n a b).state = (arithmeticInput 0 0 0).state := rfl

private theorem blankCell (h : ℤ) : absoluteCell (MultitapeToolkit.stackTape ([] : List Bool)) h = fun _ => none := by
  funext x
  simp only [absoluteCell]
  generalize x-h = z
  cases z with
  | ofNat n => cases n <;> simp [MultitapeToolkit.stackTape,Turing.Tape.nth,Turing.ListBlank.nth_mk]; rfl
  | negSucc n => simp [MultitapeToolkit.stackTape,Turing.Tape.nth,Turing.ListBlank.nth_mk]; rfl

/-- Every initially private work tape is completely blank at every coordinate. -/
theorem arithmeticInput_work_blank (n a b : ℕ) (k : MulStack)
    (hk : k≠.multiplier ∧ k≠.multiplicand) :
    (arithmeticInput n a b).cell k = fun _ => none := by
  funext x
  cases k <;> simp_all [arithmeticInput,anchoredEncode,realize,encode,stackHeads,
    anchors,rawInput,mulStacks,blankCell]

/-- Terminal heads are the true moving compiler heads; none is reset for free. -/
theorem arithmeticEnd_heads (n product : ℕ) (final : List Bool) (hlen : final.length=2*n) :
    (arithmeticEnd n product final).head =
      fun k => match k with
      | .multiplier => n
      | .multiplicand => -(n : ℤ)
      | .accumulator => -((2*n : ℕ) : ℤ)
      | _ => 0 := by
  funext k
  cases k <;> simp [arithmeticEnd,anchoredEncode,realize,stackHeads,anchors,liftMulCfg,
    mulHaltedCfg,mulStacks,hlen]
  <;> omega

/-- Universal actual arithmetic execution with a fully anchored terminal bank
and the schoolbook quadratic charge. Input preparation and halt are included. -/
theorem arithmetic_correct (n a b : ℕ) (ha : a<2^n) (hb : b<2^n) :
    ∃ (t : ℕ) (final : List Bool), final.length=2*n ∧
      t≤280*n^2+308*n+112 ∧
      MultitapeToolkit.Absolute.Runs arithmetic t (arithmeticInput n a b) (arithmeticEnd n (a*b) final) ∧
      MultitapeToolkit.Absolute.Halts arithmetic (arithmeticEnd n (a*b) final) ∧
      bitsValue (fixedBits (2*n) (a*b))=a*b := by
  rcases raw_product_halts n a b ha hb with ⟨final,hlen,hr,hvalue⟩
  rcases anchored_compile_run setupMachine.m (anchors n)
    (6*n+6+macroTime n b) (rawInput n a b)
    (liftMulCfg (mulHaltedCfg final (fixedBits (productWidth n) (a*b)))) hr with ⟨t,ht,hrun⟩
  refine ⟨t,final,hlen,?_,hrun,anchored_halts setupMachine.m (anchors n) _ _,hvalue⟩
  have hraw := rawTime_le n b
  calc
    t ≤ overhead setupMachine.m * (6*n+6+macroTime n b) := ht
    _ ≤ 14*(6*n+6+macroTime n b) := Nat.mul_le_mul_right _ setup_overhead_le
    _ ≤ 14*(20*n^2+22*n+8) := Nat.mul_le_mul_left _ hraw
    _ = 280*n^2+308*n+112 := by ring





open ControlEmbedding Subroutines


/-- Export the concrete finite dictionary used by the compiled arithmetic bank. -/
noncomputable instance arithmeticControlFinite : Fintype (Control setupMachine.m) := inferInstance

abbrev Payload := Control setupMachine.m ⊕ StackOriginSerializer.Phase
abbrev MachineState := Fin 2 × Payload

noncomputable def components : Fin 2 → Program MulStack (Option Bool) Payload :=
  fun i => if i=0 then liftProgram arithmetic Sum.inl leftDecode
    else liftProgram (StackOriginSerializer.program .accumulator .sumReverse) Sum.inr rightDecode

noncomputable def componentEntry : Fin 2 → Payload :=
  fun i => if i=0 then .inl (arithmeticInput 0 0 0).state else .inr .enter

/-- One fixed finite-control six-tape machine for arithmetic and origin export. -/
noncomputable def machine : Program MulStack (Option Bool) MachineState :=
  scheduler components componentEntry

noncomputable def input (n a b : ℕ) : MultitapeToolkit.Absolute.Config MulStack (Option Bool) MachineState :=
  stageCfg 0 (taggedCfg (R:=Payload) Sum.inl (arithmeticInput n a b))

noncomputable def serializerInput (n product : ℕ) (final : List Bool) :
    MultitapeToolkit.Absolute.Config MulStack (Option Bool) StackOriginSerializer.Phase :=
  StackOriginSerializer.input .accumulator .sumReverse (-((2*n : ℕ) : ℤ))
    (fixedBits (2*n) product) (arithmeticEnd n product final).head
    (arithmeticEnd n product final).cell

noncomputable def serializerOutput (n product : ℕ) (final : List Bool) :
    MultitapeToolkit.Absolute.Config MulStack (Option Bool) StackOriginSerializer.Phase :=
  StackOriginSerializer.output .accumulator .sumReverse (-((2*n : ℕ) : ℤ))
    (fixedBits (2*n) product) (arithmeticEnd n product final).head
    (arithmeticEnd n product final).cell

noncomputable def output (n product : ℕ) (final : List Bool) :
    MultitapeToolkit.Absolute.Config MulStack (Option Bool) MachineState :=
  stageCfg (Fin.last 1) (taggedCfg (R:=Payload) Sum.inr (serializerOutput n product final))

/-- Arithmetic finishes at the serializer's literal required head/cell bank. -/
theorem serializer_boundary (n product : ℕ) (final : List Bool) (hlen : final.length=2*n) :
    serializerInput n product final =
      ⟨.enter,(arithmeticEnd n product final).head,(arithmeticEnd n product final).cell⟩ := by
  apply MultitapeToolkit.Absolute.Config.ext
  · rfl
  · funext k
    rw [arithmeticEnd_heads n product final hlen]
    cases k <;> simp [serializerInput,StackOriginSerializer.input,arithmeticEnd_heads n product final hlen]
  · funext k
    cases k <;> simp [serializerInput,StackOriginSerializer.input,arithmeticEnd,anchoredEncode,
      realize,encode,stackHeads,anchors,liftMulCfg,mulHaltedCfg,mulStacks,
      StackOriginSerializer.sourceStack,blankCell]

/-- Fixed input control and physical origin heads; four globally blank work tapes. -/
theorem input_control_and_heads (n a b : ℕ) :
    (input n a b).state=(input 0 0 0).state ∧ (input n a b).head=fun _ => 0 := by
  exact ⟨rfl,arithmeticInput_heads n a b⟩

theorem input_work_blank (n a b : ℕ) (k : MulStack)
    (hk : k≠.multiplier ∧ k≠.multiplicand) :
    (input n a b).cell k=fun _ => none := arithmeticInput_work_blank n a b k hk

/-- The full padded MSB word starts at physical cell zero, with blank exterior. -/
theorem output_product_word (n product : ℕ) (final : List Bool) :
    (output n product final).head .sumReverse=0 ∧
    (output n product final).cell .sumReverse=
      StackOriginSerializer.originWord (fixedBits (2*n) product).reverse ∧
    (output n product final).cell .accumulator=fun _ => none := by
  simp [output,stageCfg,taggedCfg,serializerOutput,StackOriginSerializer.output]

/-- The serializer preserves the entire remaining arithmetic bank literally.
The multiplicand remains an explicit width-2n residual, rather than being
claimed clean or restored. -/
theorem output_other_tapes (n product : ℕ) (final : List Bool) (k : MulStack)
    (hs : k≠.accumulator) (hd : k≠.sumReverse) :
    (output n product final).head k=(arithmeticEnd n product final).head k ∧
    (output n product final).cell k=(arithmeticEnd n product final).cell k := by
  simp [output,stageCfg,taggedCfg,serializerOutput,StackOriginSerializer.output,hs,hd]

/-- Actual arithmetic plus exact `6n+4` serialization and one charged handoff.
This is a positive closed machine theorem, with no hypothetical child routine. -/
theorem quadratic_origin_product (n a b : ℕ) (ha : a<2^n) (hb : b<2^n) :
    ∃ (t : ℕ) (final : List Bool), final.length=2*n ∧
      t≤280*n^2+314*n+117 ∧
      MultitapeToolkit.Absolute.Runs machine t (input n a b) (output n (a*b) final) ∧
      MultitapeToolkit.Absolute.Halts machine (output n (a*b) final) ∧
      (output n (a*b) final).head .sumReverse=0 ∧
      (output n (a*b) final).cell .sumReverse=
        StackOriginSerializer.originWord (fixedBits (2*n) (a*b)).reverse ∧
      (output n (a*b) final).cell .accumulator= (fun _ => none) ∧
      bitsValue ((fixedBits (2*n) (a*b)).reverse.reverse)=a*b := by
  rcases arithmetic_correct n a b ha hb with ⟨t,final,hlen,ht,hr,hh,hvalue⟩
  have haRun : MultitapeToolkit.Absolute.Runs (components 0) t
      (taggedCfg (R:=Payload) Sum.inl (arithmeticInput n a b))
      (taggedCfg (R:=Payload) Sum.inl (arithmeticEnd n (a*b) final)) := by
    simpa [components] using lift_runs arithmetic Sum.inl leftDecode (fun _ => rfl) hr
  have haHalt : MultitapeToolkit.Absolute.Halts (components 0) (taggedCfg (R:=Payload) Sum.inl (arithmeticEnd n (a*b) final)) := by
    simpa [components] using (lift_halts arithmetic Sum.inl leftDecode (fun _ => rfl) _).2 hh
  have hs := StackOriginSerializer.serialize_correct (MulStack.accumulator) .sumReverse (by decide)
    (-((2*n : ℕ) : ℤ)) (fixedBits (2*n) (a*b))
    (arithmeticEnd n (a*b) final).head (arithmeticEnd n (a*b) final).cell
  have hbRun : MultitapeToolkit.Absolute.Runs (components (Fin.last 1)) (6*n+4)
      (taggedCfg (R:=Payload) Sum.inr (serializerInput n (a*b) final))
      (taggedCfg (R:=Payload) Sum.inr (serializerOutput n (a*b) final)) := by
    simpa [components,serializerInput,serializerOutput,←Nat.mul_assoc] using
      lift_runs (R:=Payload) (StackOriginSerializer.program MulStack.accumulator .sumReverse) Sum.inr rightDecode (fun _ => rfl) hs.1
  have hbHalt : MultitapeToolkit.Absolute.Halts (components (Fin.last 1))
      (taggedCfg (R:=Payload) Sum.inr (serializerOutput n (a*b) final)) := by
    simpa [components,serializerOutput] using
      (lift_halts (R:=Payload) (StackOriginSerializer.program MulStack.accumulator .sumReverse) Sum.inr rightDecode (fun _ => rfl) _).2 hs.2
  have hFirst := scheduler_stage_runs components componentEntry (0:Fin 2) haRun
  have hHand := scheduler_handoff components componentEntry (0:Fin 2) (by decide)
    (taggedCfg (R:=Payload) Sum.inl (arithmeticEnd n (a*b) final)) haHalt
  have hBank :
      (⟨componentEntry (nextStage (0:Fin 2) (by decide)),
        (taggedCfg (R:=Payload) Sum.inl (arithmeticEnd n (a*b) final)).head,
        (taggedCfg (R:=Payload) Sum.inl (arithmeticEnd n (a*b) final)).cell⟩ : MultitapeToolkit.Absolute.Config MulStack (Option Bool) Payload) =
      taggedCfg (R:=Payload) Sum.inr (serializerInput n (a*b) final) := by
    rw [serializer_boundary n (a*b) final hlen]
    rfl
  rw [hBank] at hHand
  have hSecond := scheduler_stage_runs components componentEntry (Fin.last 1) hbRun
  have hOne : MultitapeToolkit.Absolute.Runs machine 1
      (stageCfg (0:Fin 2) (taggedCfg (R:=Payload) Sum.inl (arithmeticEnd n (a*b) final)))
      (stageCfg (Fin.last 1) (taggedCfg (R:=Payload) Sum.inr (serializerInput n (a*b) final))) :=
    .cons hHand (.refl _)
  have hFull := Trace.runs_trans machine (Trace.runs_trans machine hFirst hOne) hSecond
  refine ⟨t+1+(6*n+4),final,hlen,by omega,hFull,?_,?_,?_,?_,?_⟩
  · exact scheduler_last_halts components componentEntry _ hbHalt
  · exact (output_product_word n (a*b) final).1
  · exact (output_product_word n (a*b) final).2.1
  · exact (output_product_word n (a*b) final).2.2
  · simpa only [List.reverse_reverse] using hvalue

/-- One fixed machine and a uniform quadratic coefficient for every valid word. -/
theorem quadratic_origin_product_uniform :
    ∀ n a b : ℕ, a<2^n → b<2^n →
      ∃ (t : ℕ) (final : List Bool), t≤400*(n+1)^2 ∧
        MultitapeToolkit.Absolute.Runs machine t (input n a b) (output n (a*b) final) ∧
        MultitapeToolkit.Absolute.Halts machine (output n (a*b) final) ∧
        (output n (a*b) final).cell .sumReverse=
          StackOriginSerializer.originWord (fixedBits (2*n) (a*b)).reverse := by
  intro n a b ha hb
  rcases quadratic_origin_product n a b ha hb with ⟨t,final,hlen,ht,hr,hh,hhead,hword,hblank,hvalue⟩
  refine ⟨t,final,?_,hr,hh,hword⟩
  nlinarith





/-- The operand banks are literal length-n LSB compiler stacks at head zero. -/
theorem input_operands (n a b : ℕ) :
    (input n a b).cell .multiplier=StackOriginSerializer.sourceStack 0 (fixedBits n b) ∧
    (input n a b).cell .multiplicand=StackOriginSerializer.sourceStack 0 (fixedBits n a) := by
  simp [input,stageCfg,taggedCfg,arithmeticInput,anchoredEncode,realize,encode,
    StackOriginSerializer.sourceStack,stackHeads,anchors,rawInput,mulStacks]

/-- Width zero is an honest completed empty-product execution, not a positive-
width assumption hidden in the arithmetic or serializer. -/
theorem zero_correct :
    ∃ t, t≤117 ∧ MultitapeToolkit.Absolute.Runs machine t (input 0 0 0) (output 0 0 []) ∧
      MultitapeToolkit.Absolute.Halts machine (output 0 0 []) := by
  rcases quadratic_origin_product 0 0 0 (by decide) (by decide) with
    ⟨t,final,hlen,ht,hr,hh,hhead,hword,hblank,hvalue⟩
  have he : final=[] := List.eq_nil_of_length_eq_zero (by simpa using hlen)
  subst final
  exact ⟨t,by simpa using ht,hr,hh⟩

theorem output_zero_bank :
    (output 0 0 []).head=(fun _ => 0) ∧ (output 0 0 []).cell=(fun _ _ => none) := by
  constructor
  · funext k; cases k <;> simp [output,stageCfg,taggedCfg,serializerOutput,
      StackOriginSerializer.output,arithmeticEnd,anchoredEncode,realize,stackHeads,
      anchors,liftMulCfg,mulHaltedCfg,mulStacks]
  · funext k x; cases k <;> simp [output,stageCfg,taggedCfg,serializerOutput,
      StackOriginSerializer.output,arithmeticEnd,
      anchoredEncode,realize,encode,stackHeads,anchors,liftMulCfg,mulHaltedCfg,mulStacks,
      blankCell,fixedBits_zero]

end MultitapeToolkit.BinaryMultiplicationOriginABI




