import MultitapeToolkit.IntegerMultiplicationEngine
import MultitapeToolkit.TM2CompilerCertificates
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
namespace MultitapeToolkit.IntegerMultiplicationCompilerApplications
open Turing Lax51Proofs.RamToTM
open MultitapeToolkit.BinaryMultiplication MultitapeToolkit.BinaryMultiplicationIntegration
open MultitapeToolkit.TM2Compiler MultitapeToolkit.TM2Compiler.Anchored
open MultitapeToolkit.TM2Compiler.Certificates
local instance : Fintype setupMachine.K := inferInstanceAs (Fintype MulStack)
local instance : Fintype setupMachine.Λ := inferInstanceAs (Fintype SetupLabel)
local instance : Fintype setupMachine.σ := inferInstanceAs (Fintype MulControl)

theorem setup_copyA_charged (b a acc backup sum temp : List Bool) :
    ChargedRun setupMachine.m (a.length+1) (8*a.length+5)
      (setupCfg (.inl .copyA) (b) (a) (acc) (backup) (sum) (temp)) (setupCfg (.inl .padA) (b) ([]) (List.replicate a.length false ++ acc) (a.reverse ++ backup) (sum) (List.replicate a.length false ++ temp)) := by
  induction a generalizing b acc backup sum temp with
  | nil =>
    have hs : TM2.step setupMachine.m (setupCfg (.inl .copyA) (b) ([]) (acc) (backup) (sum) (temp)) = some (setupCfg (.inl .padA) (b) ([]) (List.replicate ([] : List Bool).length false ++ acc) ([].reverse ++ backup) (sum) (List.replicate ([] : List Bool).length false ++ temp)) := by
      simp [TM2.step,setupCfg,setupMachine,setupIteration,setupBack,mulStacks]
    simpa [macroCost,statementCost,setupCfg,setupMachine,setupIteration,setupBack,mulStacks] using ChargedRun.cons hs (ChargedRun.refl _)
  | cons x xs ih =>
    have hfirst : setupMachine.step (setupCfg (.inl .copyA) (b) (x :: xs) (acc) (backup) (sum) (temp)) = some (setupCfg (.inl .copyA) (b) (xs) (false :: acc) (x :: backup) (sum) (false :: temp)) := by
      simp [setupCfg, setupMachine, setupIteration, setupBack, mulStacks]
      all_goals (funext k; cases k <;> rfl)
    have hh := ChargedRun.cons (M:=setupMachine.m) hfirst (ih b (false::acc) (x::backup) sum (false::temp))
    convert hh using 1 <;> simp [macroCost,statementCost,setupCfg,setupMachine,setupIteration,setupBack,mulStacks,List.reverse_cons,List.replicate_succ',List.append_assoc] <;> omega

theorem setup_padA_charged (b a acc backup sum temp : List Bool) :
    ChargedRun setupMachine.m (temp.length+1) (7*temp.length+5)
      (setupCfg (.inl .padA) (b) (a) (acc) (backup) (sum) (temp)) (setupCfg (.inl .restoreA) (b) (temp.reverse ++ a) (acc) (backup) (temp.reverse ++ sum) ([])) := by
  induction temp generalizing b a acc backup sum with
  | nil =>
    have hs : TM2.step setupMachine.m (setupCfg (.inl .padA) (b) (a) (acc) (backup) (sum) ([])) = some (setupCfg (.inl .restoreA) (b) ([].reverse ++ a) (acc) (backup) ([].reverse ++ sum) ([])) := by
      simp [TM2.step,setupCfg,setupMachine,setupIteration,setupBack,mulStacks]
    simpa [macroCost,statementCost,setupCfg,setupMachine,setupIteration,setupBack,mulStacks] using ChargedRun.cons hs (ChargedRun.refl _)
  | cons x xs ih =>
    have hfirst : setupMachine.step (setupCfg (.inl .padA) (b) (a) (acc) (backup) (sum) (x :: xs)) = some (setupCfg (.inl .padA) (b) (x :: a) (acc) (backup) (x :: sum) (xs)) := by
      simp [setupCfg, setupMachine, setupIteration, setupBack, mulStacks]
      all_goals (funext k; cases k <;> rfl)
    have hh := ChargedRun.cons (M:=setupMachine.m) hfirst (ih b (x::a) acc backup (x::sum))
    convert hh using 1 <;> simp [macroCost,statementCost,setupCfg,setupMachine,setupIteration,setupBack,mulStacks,List.reverse_cons,List.replicate_succ',List.append_assoc] <;> omega

theorem setup_restoreA_charged (b a acc backup sum temp : List Bool) :
    ChargedRun setupMachine.m (backup.length+1) (6*backup.length+5)
      (setupCfg (.inl .restoreA) (b) (a) (acc) (backup) (sum) (temp)) (setupCfg (.inl .copyB) (b) (backup.reverse ++ a) (acc) ([]) (sum) (temp)) := by
  induction backup generalizing b a acc sum temp with
  | nil =>
    have hs : TM2.step setupMachine.m (setupCfg (.inl .restoreA) (b) (a) (acc) ([]) (sum) (temp)) = some (setupCfg (.inl .copyB) (b) ([].reverse ++ a) (acc) ([]) (sum) (temp)) := by
      simp [TM2.step,setupCfg,setupMachine,setupIteration,setupBack,mulStacks]
    simpa [macroCost,statementCost,setupCfg,setupMachine,setupIteration,setupBack,mulStacks] using ChargedRun.cons hs (ChargedRun.refl _)
  | cons x xs ih =>
    have hfirst : setupMachine.step (setupCfg (.inl .restoreA) (b) (a) (acc) (x :: xs) (sum) (temp)) = some (setupCfg (.inl .restoreA) (b) (x :: a) (acc) (xs) (sum) (temp)) := by
      simp [setupCfg, setupMachine, setupIteration, setupBack, mulStacks]
      all_goals (funext k; cases k <;> rfl)
    have hh := ChargedRun.cons (M:=setupMachine.m) hfirst (ih b (x::a) acc sum temp)
    convert hh using 1 <;> simp [macroCost,statementCost,setupCfg,setupMachine,setupIteration,setupBack,mulStacks,List.reverse_cons,List.replicate_succ',List.append_assoc] <;> omega

theorem setup_copyB_charged (b a acc backup sum temp : List Bool) :
    ChargedRun setupMachine.m (b.length+1) (7*b.length+5)
      (setupCfg (.inl .copyB) (b) (a) (acc) (backup) (sum) (temp)) (setupCfg (.inl .padB) ([]) (a) (List.replicate b.length false ++ acc) (b.reverse ++ backup) (sum) (temp)) := by
  induction b generalizing a acc backup sum temp with
  | nil =>
    have hs : TM2.step setupMachine.m (setupCfg (.inl .copyB) ([]) (a) (acc) (backup) (sum) (temp)) = some (setupCfg (.inl .padB) ([]) (a) (List.replicate ([] : List Bool).length false ++ acc) ([].reverse ++ backup) (sum) (temp)) := by
      simp [TM2.step,setupCfg,setupMachine,setupIteration,setupBack,mulStacks]
    simpa [macroCost,statementCost,setupCfg,setupMachine,setupIteration,setupBack,mulStacks] using ChargedRun.cons hs (ChargedRun.refl _)
  | cons x xs ih =>
    have hfirst : setupMachine.step (setupCfg (.inl .copyB) (x :: xs) (a) (acc) (backup) (sum) (temp)) = some (setupCfg (.inl .copyB) (xs) (a) (false :: acc) (x :: backup) (sum) (temp)) := by
      simp [setupCfg, setupMachine, setupIteration, setupBack, mulStacks]
      all_goals (funext k; cases k <;> rfl)
    have hh := ChargedRun.cons (M:=setupMachine.m) hfirst (ih a (false::acc) (x::backup) sum temp)
    convert hh using 1 <;> simp [macroCost,statementCost,setupCfg,setupMachine,setupIteration,setupBack,mulStacks,List.reverse_cons,List.replicate_succ',List.append_assoc] <;> omega

theorem setup_padB_charged (b a acc backup sum temp : List Bool) :
    ChargedRun setupMachine.m (sum.length+1) (6*sum.length+5)
      (setupCfg (.inl .padB) (b) (a) (acc) (backup) (sum) (temp)) (setupCfg (.inl .restoreB) (sum.reverse ++ b) (a) (acc) (backup) ([]) (temp)) := by
  induction sum generalizing b a acc backup temp with
  | nil =>
    have hs : TM2.step setupMachine.m (setupCfg (.inl .padB) (b) (a) (acc) (backup) ([]) (temp)) = some (setupCfg (.inl .restoreB) ([].reverse ++ b) (a) (acc) (backup) ([]) (temp)) := by
      simp [TM2.step,setupCfg,setupMachine,setupIteration,setupBack,mulStacks]
    simpa [macroCost,statementCost,setupCfg,setupMachine,setupIteration,setupBack,mulStacks] using ChargedRun.cons hs (ChargedRun.refl _)
  | cons x xs ih =>
    have hfirst : setupMachine.step (setupCfg (.inl .padB) (b) (a) (acc) (backup) (x :: xs) (temp)) = some (setupCfg (.inl .padB) (x :: b) (a) (acc) (backup) (xs) (temp)) := by
      simp [setupCfg, setupMachine, setupIteration, setupBack, mulStacks]
      all_goals (funext k; cases k <;> rfl)
    have hh := ChargedRun.cons (M:=setupMachine.m) hfirst (ih (x::b) a acc backup temp)
    convert hh using 1 <;> simp [macroCost,statementCost,setupCfg,setupMachine,setupIteration,setupBack,mulStacks,List.reverse_cons,List.replicate_succ',List.append_assoc] <;> omega

theorem setup_restoreB_charged (b a acc backup sum temp : List Bool) :
    ChargedRun setupMachine.m (backup.length+1) (6*backup.length+5)
      (setupCfg (.inl .restoreB) (b) (a) (acc) (backup) (sum) (temp)) (setupCfg (.inr .outer) (backup.reverse ++ b) (a) (acc) ([]) (sum) (temp)) := by
  induction backup generalizing b a acc sum temp with
  | nil =>
    have hs : TM2.step setupMachine.m (setupCfg (.inl .restoreB) (b) (a) (acc) ([]) (sum) (temp)) = some (setupCfg (.inr .outer) ([].reverse ++ b) (a) (acc) ([]) (sum) (temp)) := by
      simp [TM2.step,setupCfg,setupMachine,setupIteration,setupBack,mulStacks]
    simpa [macroCost,statementCost,setupCfg,setupMachine,setupIteration,setupBack,mulStacks] using ChargedRun.cons hs (ChargedRun.refl _)
  | cons x xs ih =>
    have hfirst : setupMachine.step (setupCfg (.inl .restoreB) (b) (a) (acc) (x :: xs) (sum) (temp)) = some (setupCfg (.inl .restoreB) (x :: b) (a) (acc) (xs) (sum) (temp)) := by
      simp [setupCfg, setupMachine, setupIteration, setupBack, mulStacks]
      all_goals (funext k; cases k <;> rfl)
    have hh := ChargedRun.cons (M:=setupMachine.m) hfirst (ih (x::b) a acc sum temp)
    convert hh using 1 <;> simp [macroCost,statementCost,setupCfg,setupMachine,setupIteration,setupBack,mulStacks,List.reverse_cons,List.replicate_succ',List.append_assoc] <;> omega

theorem charged_trans {r s t u : ℕ} {a b c : setupMachine.Cfg}
    (h : ChargedRun setupMachine.m r t a b) (h' : ChargedRun setupMachine.m s u b c) :
    ChargedRun setupMachine.m (r+s) (t+u) a c := by
  induction h with
  | refl => simpa using h'
  | cons hs hr ih =>
    simpa [Nat.add_assoc,Nat.add_comm,Nat.add_left_comm] using ChargedRun.cons hs (ih h')

theorem setup_charged (n a b : ℕ) (ha : a<2^n) (hb : b<2^n) :
    ChargedRun setupMachine.m (6*n+6) (40*n+30) (rawInput n a b)
      (liftMulCfg (preparedInput n a b)) := by
  let A := fixedBits n a
  let B := fixedBits n b
  let Z := List.replicate n false
  have h1 : ChargedRun setupMachine.m (n+1) (8*n+5)
      (setupCfg (.inl .copyA) B A [] [] [] []) (setupCfg (.inl .padA) B [] Z A.reverse [] Z) := by
    simpa [A, B, Z] using setup_copyA_charged B A [] [] [] []
  have h2 : ChargedRun setupMachine.m (n+1) (7*n+5)
      (setupCfg (.inl .padA) B [] Z A.reverse [] Z) (setupCfg (.inl .restoreA) B Z Z A.reverse Z []) := by
    simpa [Z] using setup_padA_charged B [] Z A.reverse [] Z
  have h3 : ChargedRun setupMachine.m (n+1) (6*n+5)
      (setupCfg (.inl .restoreA) B Z Z A.reverse Z []) (setupCfg (.inl .copyB) B (A ++ Z) Z [] Z []) := by
    simpa [A] using setup_restoreA_charged B Z Z A.reverse Z []
  have h4 : ChargedRun setupMachine.m (n+1) (7*n+5)
      (setupCfg (.inl .copyB) B (A ++ Z) Z [] Z []) (setupCfg (.inl .padB) [] (A ++ Z) (Z ++ Z) B.reverse Z []) := by
    simpa [A, B, Z] using setup_copyB_charged B (A ++ Z) Z [] Z []
  have h5 : ChargedRun setupMachine.m (n+1) (6*n+5)
      (setupCfg (.inl .padB) [] (A ++ Z) (Z ++ Z) B.reverse Z []) (setupCfg (.inl .restoreB) Z (A ++ Z) (Z ++ Z) B.reverse [] []) := by
    simpa [Z] using setup_padB_charged [] (A ++ Z) (Z ++ Z) B.reverse Z []
  have h6 : ChargedRun setupMachine.m (n+1) (6*n+5)
      (setupCfg (.inl .restoreB) Z (A ++ Z) (Z ++ Z) B.reverse [] []) (setupCfg (.inr .outer) (B ++ Z) (A ++ Z) (Z ++ Z) [] [] []) := by
    simpa [B] using setup_restoreB_charged Z (A ++ Z) (Z ++ Z) B.reverse [] []
  have hrun := charged_trans (charged_trans (charged_trans (charged_trans (charged_trans h1 h2) h3) h4) h5) h6
  have hinit : setupCfg (.inl .copyA) B A [] [] [] [] = rawInput n a b := rfl
  have hzero : Z ++ Z = fixedBits (productWidth n) 0 := by
    rw [fixedBits_zero]
    change List.replicate n false ++ List.replicate n false = List.replicate (2 * n) false
    rw [← List.replicate_add]
    congr 1
    omega
  have hfinal : setupCfg (.inr .outer) (B ++ Z) (A ++ Z) (Z ++ Z) [] [] [] =
      liftMulCfg (preparedInput n a b) := by
    rw [show A ++ Z = fixedBits (productWidth n) a from fixedBits_pad ha,
      show B ++ Z = fixedBits (productWidth n) b from fixedBits_pad hb, hzero]
    rfl
  simp only [hinit,hfinal] at hrun
  convert hrun using 1 <;> omega

open MultitapeToolkit.Absolute MultitapeToolkit.BinaryMultiplicationOriginABI
/-- The exact six-phase physical invoice at arbitrary independent bottom anchors. -/
theorem setup_physical (n a b : ℕ) (ha : a<2^n) (hb : b<2^n) (base : MulStack → ℤ) :
    MultitapeToolkit.Absolute.Runs (ofMachine (compile setupMachine.m)) (40*n+30)
      (anchoredEncode setupMachine.m base (rawInput n a b))
      (anchoredEncode setupMachine.m base (liftMulCfg (preparedInput n a b))) :=
  ChargedRun.sound setupMachine.m base (setup_charged n a b ha hb)

/-- The same concrete arithmetic program with exact setup, instead of a depth estimate. -/
theorem arithmetic_tight (n a b : ℕ) (ha : a<2^n) (hb : b<2^n) :
    ∃ (t : ℕ) (final : List Bool), final.length=2*n ∧
      t≤280*n^2+264*n+58 ∧
      MultitapeToolkit.Absolute.Runs arithmetic t (arithmeticInput n a b) (arithmeticEnd n (a*b) final) ∧
      MultitapeToolkit.Absolute.Halts arithmetic (arithmeticEnd n (a*b) final) ∧
      bitsValue (fixedBits (2*n) (a*b))=a*b := by
  rcases exact_product_halts n a b ha hb with ⟨final,hlen,hr,hvalue⟩
  have hlift := liftMul_run (macroTime n b) (preparedInput n a b)
  rw [hr] at hlift
  simp only [Option.map_some] at hlift
  rcases anchored_compile_run setupMachine.m (anchors n) (macroTime n b)
    (liftMulCfg (preparedInput n a b))
    (liftMulCfg (mulHaltedCfg final (fixedBits (productWidth n) (a*b)))) hlift with ⟨t,ht,hrun⟩
  refine ⟨40*n+30+t,final,hlen,?_,MultitapeToolkit.Absolute.Trace.runs_trans _ (setup_physical n a b ha hb (anchors n)) hrun,
    anchored_halts setupMachine.m (anchors n) _ _,hvalue⟩
  have hbnd := (Nat.mul_le_mul_right (macroTime n b) setup_overhead_le)
  have hm := Nat.mul_le_mul_left 14 (macroTime_le n b)
  nlinarith

open ControlEmbedding Subroutines
theorem origin_product_tight (n a b : ℕ) (ha : a<2^n) (hb : b<2^n) :
    ∃ (t : ℕ) (final : List Bool), final.length=2*n ∧
      t≤280*n^2+270*n+63 ∧
      MultitapeToolkit.Absolute.Runs machine t (input n a b) (output n (a*b) final) ∧
      MultitapeToolkit.Absolute.Halts machine (output n (a*b) final) ∧
      (output n (a*b) final).head .sumReverse=0 ∧
      (output n (a*b) final).cell .sumReverse=
        StackOriginSerializer.originWord (fixedBits (2*n) (a*b)).reverse ∧
      (output n (a*b) final).cell .accumulator= (fun _ => none) ∧
      bitsValue ((fixedBits (2*n) (a*b)).reverse.reverse)=a*b := by
  rcases arithmetic_tight n a b ha hb with ⟨t,final,hlen,ht,hr,hh,hvalue⟩
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
  have hFull := MultitapeToolkit.Absolute.Trace.runs_trans machine (MultitapeToolkit.Absolute.Trace.runs_trans machine hFirst hOne) hSecond
  refine ⟨t+1+(6*n+4),final,hlen,by omega,hFull,?_,?_,?_,?_,?_⟩
  · exact scheduler_last_halts components componentEntry _ hbHalt
  · exact (output_product_word n (a*b) final).1
  · exact (output_product_word n (a*b) final).2.1
  · exact (output_product_word n (a*b) final).2.2
  · simpa only [List.reverse_reverse] using hvalue

open MultitapeToolkit.IntegerMultiplicationEngine
theorem clean_product_tight (n a b : ℕ) (ha : a<2^n) (hb : b<2^n) :
    ∃ t, t≤280*n^2+278*n+68 ∧
      MultitapeToolkit.Absolute.Runs cleanMachine t (cleanInput n a b) (cleanOutput n (a*b)) ∧
      MultitapeToolkit.Absolute.Halts cleanMachine (cleanOutput n (a*b)) ∧
      bitsValue ((fixedBits (2*n) (a*b)).reverse.reverse)=a*b := by
  rcases origin_product_tight n a b ha hb with
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

namespace Alphabet
open MultitapeToolkit.Absolute
variable {ι Γ Δ Q : Type} [Fintype ι] [Fintype Γ] [Fintype Δ] [Fintype Q] [Inhabited Γ]

def mapCfg (encode : Γ → Δ) (c : MultitapeToolkit.Absolute.Config ι Γ Q) :
    MultitapeToolkit.Absolute.Config ι Δ Q := ⟨c.state,c.head,fun i x => encode (c.cell i x)⟩

/-- A single fixed alphabet injection compiles the literal finite transition table.
`invFun` is used only to decode one scanned symbol per tape; no tape search occurs. -/
noncomputable def compile (P : Program ι Γ Q) (encode : Γ → Δ) : Program ι Δ Q where
  transition q read := (P.transition q (fun i => Function.invFun encode (read i))).map
    fun p => (p.1,fun i => (encode (p.2 i).1,(p.2 i).2))

theorem compile_step (P : Program ι Γ Q) (encode : Γ → Δ) (hi : Function.Injective encode)
    (c : MultitapeToolkit.Absolute.Config ι Γ Q) :
    MultitapeToolkit.Absolute.step (compile P encode) (mapCfg encode c) =
      (MultitapeToolkit.Absolute.step P c).map (mapCfg encode) := by
  have hscan : (fun i => Function.invFun encode (encode (c.cell i (c.head i)))) =
      (fun i => c.cell i (c.head i)) := funext fun i => Function.leftInverse_invFun hi _
  simp only [MultitapeToolkit.Absolute.step,compile,mapCfg,hscan]
  cases ht : P.transition c.state (fun i => c.cell i (c.head i)) with
  | none => rfl
  | some p =>
    simp only [Option.map_some]
    congr 1
    apply MultitapeToolkit.Absolute.Config.ext
    · rfl
    · rfl
    · funext i x
      by_cases hx : x=c.head i <;> simp [mapCfg,hx]

theorem compile_runs (P : Program ι Γ Q) (encode : Γ → Δ) (hi : Function.Injective encode)
    {n : ℕ} {c d : MultitapeToolkit.Absolute.Config ι Γ Q}
    (hr : MultitapeToolkit.Absolute.Runs P n c d) :
    MultitapeToolkit.Absolute.Runs (compile P encode) n (mapCfg encode c) (mapCfg encode d) := by
  induction hr with
  | refl c => exact .refl _
  | cons hs hr ih =>
    apply MultitapeToolkit.Absolute.Runs.cons (d:=mapCfg encode _)
    · rw [compile_step P encode hi,hs]; rfl
    · exact ih

theorem compile_halts (P : Program ι Γ Q) (encode : Γ → Δ) (hi : Function.Injective encode)
    (c : MultitapeToolkit.Absolute.Config ι Γ Q) :
    MultitapeToolkit.Absolute.Halts (compile P encode) (mapCfg encode c) ↔
      MultitapeToolkit.Absolute.Halts P c := by
  rw [MultitapeToolkit.Absolute.Halts,compile_step P encode hi,MultitapeToolkit.Absolute.Halts]
  cases MultitapeToolkit.Absolute.step P c <;> simp
end Alphabet

/-- For each fixed injective alphabet encoding, one fixed finite program preserves
all exact multiplication transitions and real halting, with the tighter bound. -/
theorem encoded_clean_product {Δ : Type} [Fintype Δ] (encode : Option Bool → Δ)
    (hi : Function.Injective encode) (n a b : ℕ) (ha : a<2^n) (hb : b<2^n) :
    ∃ t, t≤280*n^2+278*n+68 ∧
      MultitapeToolkit.Absolute.Runs (Alphabet.compile cleanMachine encode) t
        (Alphabet.mapCfg encode (cleanInput n a b)) (Alphabet.mapCfg encode (cleanOutput n (a*b))) ∧
      MultitapeToolkit.Absolute.Halts (Alphabet.compile cleanMachine encode)
        (Alphabet.mapCfg encode (cleanOutput n (a*b))) ∧
      bitsValue ((fixedBits (2*n) (a*b)).reverse.reverse)=a*b := by
  rcases clean_product_tight n a b ha hb with ⟨t,ht,hr,hh,hvalue⟩
  exact ⟨t,ht,Alphabet.compile_runs cleanMachine encode hi hr,
    (Alphabet.compile_halts cleanMachine encode hi _).2 hh,hvalue⟩
end MultitapeToolkit.IntegerMultiplicationCompilerApplications
