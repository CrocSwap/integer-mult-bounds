import MultitapeToolkit.BinaryMultiplicationOriginABI
import MultitapeToolkit.TapeEmbedding
import MultitapeToolkit.TM2CompilerCertificates
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
namespace MultitapeToolkit.IntegerMultiplicationEngine
open Turing MultitapeToolkit MultitapeToolkit.Absolute
open MultitapeToolkit.TM2Compiler MultitapeToolkit.TM2Compiler.Anchored
open MultitapeToolkit.BinaryMultiplication MultitapeToolkit.BinaryMultiplicationIntegration
open Lax51Proofs.RamToTM
open MultitapeToolkit.TM2Compiler.Certificates
namespace Eraser
def code : Unit → Statement (K:=Unit) (Γ:=Bool) (Λ:=Unit) (σ:=Bool) :=
  fun _ => .pop () (fun _ a => a.isSome) (.branch id (.goto (fun _ => ())) .halt)
def cfg (l : Option Unit) (v : Bool) (bits : List Bool) :
    TM2.Cfg (fun _ : Unit => Bool) Unit Bool := ⟨l,v,fun _ => bits⟩
def tick (o : Option (TM2.Cfg (fun _ : Unit => Bool) Unit Bool)) := o.bind (TM2.step code)
theorem tick_nil (v : Bool) : tick (some (cfg (some ()) v [])) = some (cfg none false []) := by
  simp [tick,cfg,code,TM2.step,TM2.stepAux]
theorem tick_cons (v b : Bool) (bits : List Bool) :
    tick (some (cfg (some ()) v (b::bits))) = some (cfg (some ()) true bits) := by
  simp [tick,cfg,code,TM2.step,TM2.stepAux]
  rfl
theorem macro_run (bits : List Bool) (v : Bool) :
    (tick^[bits.length+1]) (some (cfg (some ()) v bits)) = some (cfg none false []) := by
  induction bits generalizing v with
  | nil => exact tick_nil v
  | cons b bs ih =>
    rw [List.length_cons, Nat.add_right_comm, Function.iterate_succ_apply, tick_cons]
    exact ih true
theorem overhead_le : overhead code ≤ 6 := by
  change 2 * (Finset.univ.sup (fun l => depth (code l))) ≤ 2 * 3
  apply Nat.mul_le_mul_left 2
  apply Finset.sup_le
  intro l hl
  cases l
  simp [code,depth]
noncomputable def program : MultitapeToolkit.Absolute.Program Unit (Option Bool) (Control code) := ofMachine (compile code)
noncomputable def input (h : ℤ) (bits : List Bool) :=
  anchoredEncode code (fun _ => h+(bits.length : ℤ)) (cfg (some ()) false bits)
noncomputable def output (h : ℤ) (bits : List Bool) :=
  anchoredEncode code (fun _ => h+(bits.length : ℤ)) (cfg none false [])
theorem input_head (h : ℤ) (bits : List Bool) : (input h bits).head ()=h := by
  simp [input,anchoredEncode,realize,stackHeads,cfg]
theorem input_cell (h : ℤ) (bits : List Bool) :
    (input h bits).cell ()=StackOriginSerializer.sourceStack h bits := by
  simp [input,anchoredEncode,realize,stackHeads,cfg,encode,StackOriginSerializer.sourceStack]
theorem output_head (h : ℤ) (bits : List Bool) :
    (output h bits).head ()=h+(bits.length : ℤ) := by
  simp [output,anchoredEncode,realize,stackHeads,cfg]
theorem output_cell (h : ℤ) (bits : List Bool) : (output h bits).cell ()=fun _ => none := by
  simpa [output,anchoredEncode,realize,encode,stackHeads,cfg,
    StackOriginSerializer.sourceStack] using
    StackOriginSerializer.sourceStack_nil (h+(bits.length : ℤ))

/-- The pop uses two physical transitions; branch and goto/halt use one each. -/
theorem charged_run (bits : List Bool) (v : Bool) :
    ChargedRun code (bits.length+1) (4*(bits.length+1))
      (cfg (some ()) v bits) (cfg none false []) := by
  induction bits generalizing v with
  | nil =>
    have hs : TM2.step code (cfg (some ()) v []) = some (cfg none false []) := by
      simpa only [tick,Option.bind_some] using tick_nil v
    simpa [macroCost,statementCost,code,cfg] using ChargedRun.cons hs (ChargedRun.refl (cfg none false []))
  | cons b bs ih =>
    have hs : TM2.step code (cfg (some ()) v (b::bs)) = some (cfg (some ()) true bs) := by
      simpa only [tick,Option.bind_some] using tick_cons v b bs
    convert ChargedRun.cons hs (ih true) using 1 <;>
      simp [macroCost,statementCost,code,cfg] <;> omega

theorem exact_correct (h : ℤ) (bits : List Bool) :
    MultitapeToolkit.Absolute.Runs program (4*(bits.length+1)) (input h bits) (output h bits) ∧
      MultitapeToolkit.Absolute.Halts program (output h bits) := by
  exact ⟨ChargedRun.sound code (fun _ => h+(bits.length : ℤ)) (charged_run bits false),
    anchored_halts code _ false (fun _ => [])⟩

theorem correct (h : ℤ) (bits : List Bool) :
    ∃ t, t≤4*(bits.length+1) ∧ MultitapeToolkit.Absolute.Runs program t (input h bits) (output h bits) ∧
      MultitapeToolkit.Absolute.Halts program (output h bits) :=
  ⟨4*(bits.length+1),le_rfl,(exact_correct h bits).1,(exact_correct h bits).2⟩
end Eraser

open MultitapeToolkit.BinaryMultiplicationOriginABI ControlEmbedding Subroutines
@[simp] theorem absolute_blank (h : ℤ) :
    Locality.absoluteCell (stackTape ([] : List Bool)) h = fun _ => none :=
  StackOriginSerializer.sourceStack_nil h

def eraseTape : Unit ↪ MulStack := ⟨fun _ => .multiplicand, fun _ _ _ => Subsingleton.elim _ _⟩
@[simp] theorem erase_decode (k : MulStack) : TapeEmbedding.decode eraseTape k =
    if k=.multiplicand then some () else none := by
  by_cases hk : k=.multiplicand
  · subst k
    exact TapeEmbedding.decode_image eraseTape ()
  · rw [if_neg hk]
    apply (TapeEmbedding.decode_none eraseTape k).2
    rintro ⟨u,hu⟩
    exact hk (by simpa [eraseTape] using hu.symm)

noncomputable def erasing : MultitapeToolkit.Absolute.Program MulStack (Option Bool) (Control Eraser.code) :=
  TapeEmbedding.liftProgram eraseTape Eraser.program
noncomputable def erasingInput (n product : ℕ) (final : List Bool) :=
  TapeEmbedding.liftCfg eraseTape (Eraser.input (-(n : ℤ)) final)
    (output n product final).head (output n product final).cell
noncomputable def erasingOutput (n product : ℕ) (final : List Bool) :=
  TapeEmbedding.liftCfg eraseTape (Eraser.output (-(n : ℤ)) final)
    (output n product final).head (output n product final).cell

theorem original_heads (n product : ℕ) (final : List Bool) (hlen : final.length=2*n) (k : MulStack) :
    (output n product final).head k = match k with
      | .multiplier => n | .multiplicand => -(n : ℤ)
      | .accumulator => -((2*n : ℕ) : ℤ) | _ => 0 := by
  cases k <;> simp [output,stageCfg,taggedCfg,serializerOutput,StackOriginSerializer.output,
    arithmeticEnd_heads n product final hlen]

theorem original_cells (n product : ℕ) (final : List Bool) (hlen : final.length=2*n) (k : MulStack) :
    (output n product final).cell k =
      if k=.multiplicand then StackOriginSerializer.sourceStack (-(n : ℤ)) final
      else if k=.sumReverse then StackOriginSerializer.originWord (fixedBits (2*n) product).reverse
      else fun _ => none := by
  have hcoord : (n : ℤ)-2*(n : ℤ)=-(n : ℤ) := by omega
  cases k <;> simp [output,stageCfg,taggedCfg,serializerOutput,StackOriginSerializer.output,
    arithmeticEnd,anchoredEncode,realize,encode,stackHeads,anchors,liftMulCfg,
    mulHaltedCfg,mulStacks,hlen,hcoord,StackOriginSerializer.sourceStack]

theorem erasing_boundary (n product : ℕ) (final : List Bool) (hlen : final.length=2*n) :
    (erasingInput n product final).head=(output n product final).head ∧
    (erasingInput n product final).cell=(output n product final).cell := by
  constructor
  · funext k
    cases k <;> simp [erasingInput,TapeEmbedding.liftCfg,Eraser.input_head,
      original_heads n product final hlen]
  · funext k
    cases k <;> simp [erasingInput,TapeEmbedding.liftCfg,Eraser.input_cell,
      original_cells n product final hlen]

theorem erasing_exact (n product : ℕ) (final : List Bool) :
    MultitapeToolkit.Absolute.Runs erasing (4*(final.length+1))
      (erasingInput n product final) (erasingOutput n product final) ∧
      MultitapeToolkit.Absolute.Halts erasing (erasingOutput n product final) := by
  rcases Eraser.exact_correct (-(n : ℤ)) final with ⟨hr,hh⟩
  exact ⟨TapeEmbedding.lift_runs eraseTape Eraser.program hr _ _,
    (TapeEmbedding.lift_halts eraseTape Eraser.program _ _ _).2 hh⟩

theorem erasing_correct (n product : ℕ) (final : List Bool) :
    ∃ t, t≤4*(final.length+1) ∧
      MultitapeToolkit.Absolute.Runs erasing t (erasingInput n product final) (erasingOutput n product final) ∧
      MultitapeToolkit.Absolute.Halts erasing (erasingOutput n product final) := by
  rcases Eraser.correct (-(n : ℤ)) final with ⟨t,ht,hr,hh⟩
  exact ⟨t,ht,TapeEmbedding.lift_runs eraseTape Eraser.program hr _ _,
    (TapeEmbedding.lift_halts eraseTape Eraser.program _ _ _).2 hh⟩

noncomputable instance eraserControlFinite : Fintype (Control Eraser.code) := inferInstance
abbrev CleanPayload := MachineState ⊕ Control Eraser.code
abbrev CleanState := Fin 2 × CleanPayload
noncomputable def cleanComponents : Fin 2 → MultitapeToolkit.Absolute.Program MulStack (Option Bool) CleanPayload :=
  fun i => if i=0 then ControlEmbedding.liftProgram machine Sum.inl leftDecode
    else ControlEmbedding.liftProgram erasing Sum.inr rightDecode
noncomputable def cleanEntry : Fin 2 → CleanPayload :=
  fun i => if i=0 then .inl (input 0 0 0).state else .inr (Eraser.input 0 []).state
noncomputable def cleanMachine : MultitapeToolkit.Absolute.Program MulStack (Option Bool) CleanState :=
  scheduler cleanComponents cleanEntry
noncomputable def cleanInput (n a b : ℕ) : MultitapeToolkit.Absolute.Config MulStack (Option Bool) CleanState :=
  stageCfg 0 (taggedCfg (R:=CleanPayload) Sum.inl (input n a b))

/-- The returned bank contains only the padded MSB product. Actual head positions
are retained, including the cleared accumulator at minus twice the input width. -/
noncomputable def cleanOutput (n product : ℕ) : MultitapeToolkit.Absolute.Config MulStack (Option Bool) CleanState :=
  ⟨(Fin.last 1,Sum.inr (Eraser.output 0 []).state),
    (fun k =>
      match k with
      | .multiplier => n
      | .multiplicand => n
      | .accumulator => -((2*n : ℕ) : ℤ)
      | _ => 0),
    fun k => if k=.sumReverse then StackOriginSerializer.originWord (fixedBits (2*n) product).reverse
      else fun _ => none⟩

theorem clean_endpoint (n product : ℕ) (final : List Bool) (hlen : final.length=2*n) :
    stageCfg (Fin.last 1) (taggedCfg (R:=CleanPayload) Sum.inr (erasingOutput n product final)) =
      cleanOutput n product := by
  apply MultitapeToolkit.Absolute.Config.ext
  · rfl
  · funext k
    cases k <;> simp [stageCfg,taggedCfg,cleanOutput,erasingOutput,TapeEmbedding.liftCfg,
      Eraser.output_head,original_heads n product final hlen,hlen] <;> omega
  · funext k
    cases k <;> simp [stageCfg,taggedCfg,cleanOutput,erasingOutput,TapeEmbedding.liftCfg,
      Eraser.output_cell,original_cells n product final hlen]

/-- The only added costs are actual erasure transitions and one physical handoff.
No input conversion, implicit head reset or hypothetical arithmetic child occurs. -/
theorem clean_product (n a b : ℕ) (ha : a<2^n) (hb : b<2^n) :
    ∃ t, t≤280*n^2+322*n+122 ∧
      MultitapeToolkit.Absolute.Runs cleanMachine t (cleanInput n a b) (cleanOutput n (a*b)) ∧
      MultitapeToolkit.Absolute.Halts cleanMachine (cleanOutput n (a*b)) ∧
      bitsValue ((fixedBits (2*n) (a*b)).reverse.reverse)=a*b := by
  rcases quadratic_origin_product n a b ha hb with
    ⟨t,final,hlen,ht,hr,hh,hhead,hword,hblank,hvalue⟩
  rcases erasing_correct n (a*b) final with ⟨s,hs,hsr,hsh⟩
  have hFirst : MultitapeToolkit.Absolute.Runs (cleanComponents 0) t
      (taggedCfg (R:=CleanPayload) Sum.inl (input n a b))
      (taggedCfg (R:=CleanPayload) Sum.inl (output n (a*b) final)) := by
    simpa [cleanComponents] using ControlEmbedding.lift_runs machine Sum.inl leftDecode (fun _ => rfl) hr
  have hFirstHalt : MultitapeToolkit.Absolute.Halts (cleanComponents 0)
      (taggedCfg (R:=CleanPayload) Sum.inl (output n (a*b) final)) := by
    simpa [cleanComponents] using (ControlEmbedding.lift_halts machine Sum.inl leftDecode (fun _ => rfl) _).2 hh
  have hSecond : MultitapeToolkit.Absolute.Runs (cleanComponents (Fin.last 1)) s
      (taggedCfg (R:=CleanPayload) Sum.inr (erasingInput n (a*b) final))
      (taggedCfg (R:=CleanPayload) Sum.inr (erasingOutput n (a*b) final)) := by
    simpa [cleanComponents] using ControlEmbedding.lift_runs (R:=CleanPayload) erasing Sum.inr rightDecode (fun _ => rfl) hsr
  have hSecondHalt : MultitapeToolkit.Absolute.Halts (cleanComponents (Fin.last 1))
      (taggedCfg (R:=CleanPayload) Sum.inr (erasingOutput n (a*b) final)) := by
    simpa [cleanComponents] using (ControlEmbedding.lift_halts (R:=CleanPayload) erasing Sum.inr rightDecode (fun _ => rfl) _).2 hsh
  have hbanks := erasing_boundary n (a*b) final hlen
  have hBank : (⟨cleanEntry (nextStage (0:Fin 2) (by decide)),
      (taggedCfg (R:=CleanPayload) Sum.inl (output n (a*b) final)).head,
      (taggedCfg (R:=CleanPayload) Sum.inl (output n (a*b) final)).cell⟩ : MultitapeToolkit.Absolute.Config MulStack (Option Bool) CleanPayload) =
      taggedCfg (R:=CleanPayload) Sum.inr (erasingInput n (a*b) final) := by
    apply MultitapeToolkit.Absolute.Config.ext
    · rfl
    · exact hbanks.1.symm
    · exact hbanks.2.symm
  have hHand := scheduler_handoff cleanComponents cleanEntry (0:Fin 2) (by decide) _ hFirstHalt
  rw [hBank] at hHand
  have hOne : MultitapeToolkit.Absolute.Runs cleanMachine 1
      (stageCfg 0 (taggedCfg (R:=CleanPayload) Sum.inl (output n (a*b) final)))
      (stageCfg (Fin.last 1) (taggedCfg (R:=CleanPayload) Sum.inr (erasingInput n (a*b) final))) :=
    .cons hHand (.refl _)
  have hFull := MultitapeToolkit.Absolute.Trace.runs_trans cleanMachine
    (MultitapeToolkit.Absolute.Trace.runs_trans cleanMachine (scheduler_stage_runs cleanComponents cleanEntry 0 hFirst) hOne)
    (scheduler_stage_runs cleanComponents cleanEntry (Fin.last 1) hSecond)
  rw [clean_endpoint n (a*b) final hlen] at hFull
  have hHalt := scheduler_last_halts cleanComponents cleanEntry _ hSecondHalt
  rw [clean_endpoint n (a*b) final hlen] at hHalt
  refine ⟨t+1+s,?_,hFull,hHalt,hvalue⟩
  rw [hlen] at hs
  omega

/-- All input heads are at zero, and the entry control is independent of inputs. -/
theorem clean_input_control_and_heads (n a b : ℕ) :
    (cleanInput n a b).state=(cleanInput 0 0 0).state ∧
    (cleanInput n a b).head=fun _ => 0 := by
  exact ⟨rfl,(input_control_and_heads n a b).2⟩
/-- Both operands are literal padded LSB words on the two designated tapes. -/
theorem clean_input_operands (n a b : ℕ) :
    (cleanInput n a b).cell .multiplier=StackOriginSerializer.sourceStack 0 (fixedBits n b) ∧
    (cleanInput n a b).cell .multiplicand=StackOriginSerializer.sourceStack 0 (fixedBits n a) :=
  input_operands n a b
theorem clean_input_work_blank (n a b : ℕ) (k : MulStack)
    (hk : k≠.multiplier ∧ k≠.multiplicand) :
    (cleanInput n a b).cell k=fun _ => none :=
  input_work_blank n a b k hk
/-- Every cell on each of the other five tapes is globally blank. -/
theorem clean_output_work_blank (n product : ℕ) (k : MulStack) (hk : k≠.sumReverse) :
    (cleanOutput n product).cell k=fun _ => none := by
  simp [cleanOutput,hk]
theorem clean_output_product_word (n product : ℕ) :
    (cleanOutput n product).head .sumReverse=0 ∧
    (cleanOutput n product).cell .sumReverse=
      StackOriginSerializer.originWord (fixedBits (2*n) product).reverse := by
  simp [cleanOutput]
/-- These are actual terminal positions, with no uncharged return to origin. -/
theorem clean_output_heads (n product : ℕ) (k : MulStack) :
    (cleanOutput n product).head k=match k with
      | .multiplier => n
      | .multiplicand => n
      | .accumulator => -((2*n : ℕ) : ℤ)
      | _ => 0 := rfl
/-- One fixed finite six-tape machine computes and fully cleans every valid width. -/
theorem clean_product_uniform :
    ∀ n a b : ℕ, a<2^n → b<2^n →
      ∃ t, t≤400*(n+1)^2 ∧
        MultitapeToolkit.Absolute.Runs cleanMachine t (cleanInput n a b) (cleanOutput n (a*b)) ∧
        MultitapeToolkit.Absolute.Halts cleanMachine (cleanOutput n (a*b)) ∧
        bitsValue ((fixedBits (2*n) (a*b)).reverse.reverse)=a*b := by
  intro n a b ha hb
  rcases clean_product n a b ha hb with ⟨t,ht,hr,hh,hvalue⟩
  refine ⟨t,?_,hr,hh,hvalue⟩
  nlinarith

theorem clean_zero_correct :
    ∃ t, t≤122 ∧ MultitapeToolkit.Absolute.Runs cleanMachine t (cleanInput 0 0 0) (cleanOutput 0 0) ∧
      MultitapeToolkit.Absolute.Halts cleanMachine (cleanOutput 0 0) := by
  rcases clean_product 0 0 0 (by decide) (by decide) with ⟨t,ht,hr,hh,hvalue⟩
  exact ⟨t,by simpa using ht,hr,hh⟩
theorem clean_output_zero_bank :
    (cleanOutput 0 0).head=(fun _ => 0) ∧
    (cleanOutput 0 0).cell=(fun _ _ => none) := by
  constructor
  · funext k; cases k <;> simp [cleanOutput]
  · funext k x; cases k <;>
      simp [cleanOutput,fixedBits_zero,StackOriginSerializer.originWord]
end MultitapeToolkit.IntegerMultiplicationEngine
