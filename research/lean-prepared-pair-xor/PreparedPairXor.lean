import BackwardPairedInput
import MarkedXorFraming

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.

Five-tape sequential controller: actual public PR488 preparation, paid backward
pair creation, then the accepted marked XOR scan. Both mode switches are real
charged transitions. The four original preparation tapes remain in the state;
only its two work copies are consumed by the pairing phase. The other two
complete tapes are framed, and all four are framed during XOR.

PR488 provides an existential endpoint bound, not an exact first-halt formula.
A short generic trace-extraction argument below uses its actual successful
steps to obtain a genuine halt witness. No padding/reversal or XOR algebra is
reproved. The resulting first halt is at most 18*max(input widths)+24.

The new same-tape context lemma directly reuses MarkedXorFraming; it does not
repeat confinement. The complete pipeline constructs an isolated output; any
additional ambient contexts are supplied only in the explicit XOR-stage lemma.
Initial bit-word encoding, pristine work/output storage, physical tape/address
allocation, dirty-state inversion and a whole-pipeline prefix-space bound for
historical PR488 remain separate. No Nat-to-bits conversion is priced here.
Author-checked context kappa=836330098538459/500000000000000000.
Uncompiled source candidate; acceptance is recorded separately.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.PreparedPairXor
open PairedBitXorScan (Tape Pair xorPair value)
abbrev PrepConfig := FixedTapeMachine.Configuration BinaryInputPreparation.machine
abbrev InputTape := FixedTapeMachine.Tape
abbrev OutputTape := Tape MarkedBitXorScan.Symbol

inductive State where
  | prepare (c : PrepConfig) (output : OutputTape) (a b : Bool)
  | pairing (originalLeft originalRight : InputTape) (s : BackwardPairedInput.State)
  | xor (originalLeft originalRight workLeft workRight : InputTape) (spare : Bool)
      (s : MarkedBitXorScan.State)

/-- Selects the two actual work tapes; the enclosing state retains tapes 0/1. -/
def enterPair (c : PrepConfig) (output : OutputTape) (a b : Bool) : State :=
  .pairing (c.tapes (0 : Fin 4)) (c.tapes (1 : Fin 4))
    ⟨c.tapes (2 : Fin 4), c.tapes (3 : Fin 4), output, a,b,.writeLeft⟩

def step : State → State
  | .prepare c output a b =>
      match FixedTapeMachine.step BinaryInputPreparation.machine c with
      | some d => .prepare d output a b
      | none => enterPair c output a b
  | .pairing left right s =>
      if s.phase = .halt then
        .xor left right s.leftInput s.rightInput s.rightBit (BackwardPairedInput.xorEntrance s)
      else .pairing left right (BackwardPairedInput.step s)
  | .xor left right wl wr spare s => .xor left right wl wr spare (MarkedBitXorScan.step s)

def Halted : State → Prop
  | .prepare .. => False
  | .pairing .. => False
  | .xor _ _ _ _ _ s => s.phase = .halt

def run : Nat → State → State
  | 0,s => s
  | n+1,s => run n (step s)

inductive Trace : Nat → State → State → Prop where
  | nil (s : State) : Trace 0 s s
  | next {n : Nat} {s t : State} (live : ¬ Halted s)
      (tail : Trace n (step s) t) : Trace (n+1) s t

private theorem trace_trans {m n : Nat} {s u t : State}
    (h : Trace m s u) (g : Trace n u t) : Trace (m+n) s t := by
  induction h with
  | nil => simpa using g
  | next live tail ih => simpa only [Nat.succ_add] using Trace.next live (ih g)

private theorem trace_sound {n : Nat} {s t : State} (h : Trace n s t) : run n s=t := by
  induction h with
  | nil => rfl
  | next _ _ ih => exact ih

private theorem trace_live {n : Nat} {s t : State} (h : Trace n s t)
    (k : Nat) (hk:k<n) : ¬ Halted (run k s) := by
  induction h generalizing k with
  | nil => omega
  | next live tail ih =>
      cases k with
      | zero => exact live
      | succ k => exact ih k (by omega)

/-- Successful steps, stopping at the actual missing transition. This exposes
only the old machine's finite execution and does not replace its preparation. -/
inductive PrepTrace : Nat → PrepConfig → PrepConfig → Prop where
  | done (c : PrepConfig) (h : FixedTapeMachine.Halted BinaryInputPreparation.machine c) : PrepTrace 0 c c
  | next {n : Nat} {c d e : PrepConfig}
      (h : FixedTapeMachine.step BinaryInputPreparation.machine c=some d)
      (tail : PrepTrace n d e) : PrepTrace (n+1) c e

private theorem prep_trace_of_halted_run (N:Nat) (c:PrepConfig)
    (h:FixedTapeMachine.Halted BinaryInputPreparation.machine
      (FixedTapeMachine.run BinaryInputPreparation.machine N c)) :
    ∃ k≤N, PrepTrace k c (FixedTapeMachine.run BinaryInputPreparation.machine N c) := by
  induction N generalizing c with
  | zero => exact ⟨0,Nat.le_refl _,PrepTrace.done c h⟩
  | succ N ih =>
      cases hs:FixedTapeMachine.step BinaryInputPreparation.machine c with
      | none =>
          have hr:FixedTapeMachine.run BinaryInputPreparation.machine (N+1) c=c := by
            simp only [FixedTapeMachine.run,hs]
          refine ⟨0,by omega,?_⟩
          rw [hr]
          exact PrepTrace.done c hs
      | some d =>
          have hr:FixedTapeMachine.run BinaryInputPreparation.machine (N+1) c=
              FixedTapeMachine.run BinaryInputPreparation.machine N d := by
            simp only [FixedTapeMachine.run,hs]
          obtain ⟨k,hk,htrace⟩:=ih d (by simpa only [hr] using h)
          refine ⟨k+1,by omega,?_⟩
          rw [hr]
          exact PrepTrace.next hs htrace

private theorem prepare_trace {n:Nat} {c d:PrepConfig} (h:PrepTrace n c d)
    (out:OutputTape) (a b:Bool) : Trace n (.prepare c out a b) (.prepare d out a b) := by
  induction h with
  | done => exact Trace.nil _
  | next hs tail ih =>
      apply Trace.next (by simp [Halted])
      simpa only [step,hs] using ih

private theorem pairing_trace (left right:InputTape) {n:Nat} {s t:BackwardPairedInput.State}
    (h:BackwardPairedInput.Trace n s t) : Trace n (.pairing left right s) (.pairing left right t) := by
  induction h with
  | nil => exact Trace.nil _
  | next live tail ih =>
      apply Trace.next (by simp [Halted])
      simpa only [step,if_neg live] using ih

private theorem xor_trace (left right wl wr:InputTape) (spare:Bool)
    {n:Nat} {s t:MarkedBitXorScan.State} (h:MarkedBitXorScan.RunsToHalt n s t) :
    Trace n (.xor left right wl wr spare s) (.xor left right wl wr spare t) := by
  induction h with
  | done => exact Trace.nil _
  | next live _ tail ih => exact Trace.next live ih

def initial (xs ys:List Bool) (a b:Bool) : State :=
  .prepare (BinaryInputPreparation.initialConfiguration xs ys) ⟨[],[]⟩ a b

def pairedRows (xs ys:List Bool) : List Pair :=
  (BinaryInputPreparation.pad (max xs.length ys.length) xs).zip
    (BinaryInputPreparation.pad (max xs.length ys.length) ys)

def final (xs ys:List Bool) : State :=
  let px:=BinaryInputPreparation.pad (max xs.length ys.length) xs
  let py:=BinaryInputPreparation.pad (max xs.length ys.length) ys
  .xor (BinaryWordReversal.finalInput px) (BinaryWordReversal.finalInput py)
    (BackwardPairedInput.finalInput px) (BackwardPairedInput.finalInput py) false
    (MarkedBitXorScan.final ((px.zip py).map xorPair))

/-- First charged mode switch; all four preparation tapes are retained. -/
theorem preparation_handoff (xs ys:List Bool) (a b:Bool) :
    step (.prepare (BinaryInputPreparation.finalConfiguration xs ys) ⟨[],[]⟩ a b)=
      let px:=BinaryInputPreparation.pad (max xs.length ys.length) xs
      let py:=BinaryInputPreparation.pad (max xs.length ys.length) ys
      .pairing (BinaryWordReversal.finalInput px) (BinaryWordReversal.finalInput py)
        (BackwardPairedInput.initial px py a b) := rfl

/-- Second charged mode switch; pairing's cleared bit is the XOR scratch.
All four other tapes and the spare cleared bit remain explicit spectators. -/
theorem pairing_handoff (left right:InputTape) (xs ys:List Bool) :
    step (.pairing left right (BackwardPairedInput.final xs ys))=
      .xor left right (BackwardPairedInput.finalInput xs) (BackwardPairedInput.finalInput ys) false
        (MarkedBitXorScan.initial (xs.zip ys)) := rfl

/-- Genuine first-halt witness. The preparation upper bound is not changed
into an exact elapsed formula. Both actual switch steps are included. -/
theorem machine_exact (xs ys:List Bool) (a b:Bool) :
    ∃ k≤6*(max xs.length ys.length)+7,
      Trace (k+12*(max xs.length ys.length)+17) (initial xs ys a b) (final xs ys) := by
  let n:=max xs.length ys.length
  let px:=BinaryInputPreparation.pad n xs
  let py:=BinaryInputPreparation.pad n ys
  have hx:px.length=n:=BinaryInputPreparation.pad_length _ _ (Nat.le_max_left _ _)
  have hy:py.length=n:=BinaryInputPreparation.pad_length _ _ (Nat.le_max_right _ _)
  have hxy:=hx.trans hy.symm
  obtain ⟨t,ht,hrun⟩:=BinaryInputPreparation.prepare_run xs ys
  have hh:FixedTapeMachine.Halted BinaryInputPreparation.machine
      (FixedTapeMachine.run BinaryInputPreparation.machine t
        (BinaryInputPreparation.initialConfiguration xs ys)) := by
    rw [hrun]
    exact BinaryInputPreparation.final_halted xs ys
  obtain ⟨k,hk,htrace⟩:=prep_trace_of_halted_run t (BinaryInputPreparation.initialConfiguration xs ys) hh
  rw [hrun] at htrace
  have hp:=prepare_trace htrace ⟨[],[]⟩ a b
  have hs1:Trace 1 (.prepare (BinaryInputPreparation.finalConfiguration xs ys) ⟨[],[]⟩ a b)
      (.pairing (BinaryWordReversal.finalInput px) (BinaryWordReversal.finalInput py)
        (BackwardPairedInput.initial px py a b)) := by
    apply Trace.next (by simp [Halted])
    rw [preparation_handoff]
    exact Trace.nil _
  have hb:=pairing_trace (BinaryWordReversal.finalInput px) (BinaryWordReversal.finalInput py)
    (BackwardPairedInput.pair_exact px py hxy a b)
  have hs2:Trace 1 (.pairing (BinaryWordReversal.finalInput px) (BinaryWordReversal.finalInput py)
      (BackwardPairedInput.final px py))
      (.xor (BinaryWordReversal.finalInput px) (BinaryWordReversal.finalInput py)
        (BackwardPairedInput.finalInput px) (BackwardPairedInput.finalInput py) false
        (MarkedBitXorScan.initial (px.zip py))) := by
    apply Trace.next (by simp [Halted])
    rw [pairing_handoff]
    exact Trace.nil _
  have hxScan:MarkedBitXorScan.RunsToHalt (5*(px.zip py).length+4)
      (MarkedBitXorScan.initial (px.zip py))
      (MarkedBitXorScan.final ((px.zip py).map xorPair)) := by
    simpa only [MarkedXorFraming.embed,List.append_nil] using
      MarkedXorFraming.framed_scan_exact [] [] (px.zip py)
  have hxor:=xor_trace (BinaryWordReversal.finalInput px) (BinaryWordReversal.finalInput py)
    (BackwardPairedInput.finalInput px) (BackwardPairedInput.finalInput py) false hxScan
  have all:=trace_trans (trace_trans (trace_trans (trace_trans hp hs1) hb) hs2) hxor
  have count:k+1+(7*px.length+11)+1+(5*(px.zip py).length+4)=k+12*n+17 := by
    rw [List.length_zip,hx,hy,Nat.min_self]
    omega
  rw [count] at all
  exact ⟨k,Nat.le_trans hk ht,all⟩

/-- Full five-tape endpoint and no earlier global halt. The upper bound is
18n+24; the chosen elapsed witness is the actual first halt, not saturation. -/
theorem machine_result (xs ys:List Bool) (a b:Bool) :
    ∃ t≤18*(max xs.length ys.length)+24,
      run t (initial xs ys a b)=final xs ys ∧ Halted (final xs ys) ∧
      ∀ k<t, ¬ Halted (run k (initial xs ys a b)) := by
  obtain ⟨k,hk,htrace⟩:=machine_exact xs ys a b
  refine ⟨k+12*(max xs.length ys.length)+17,by omega,trace_sound htrace,?_,trace_live htrace⟩
  rfl

/-- Numeric interpretation of the actual final output. Reuses PR488's
preserved input values and accepted all-width XOR algebra without enumeration. -/
theorem output_values (xs ys:List Bool) :
    value (((pairedRows xs ys).map xorPair).map Prod.fst)=
      FixedTapeMachine.wordValue xs ^^^ FixedTapeMachine.wordValue ys ∧
    value (((pairedRows xs ys).map xorPair).map Prod.snd)=FixedTapeMachine.wordValue ys := by
  obtain ⟨t,ht,h⟩:=BackwardPairedInput.prepared_pair xs ys false false
  dsimp only at h
  obtain ⟨_,_,hx,hy⟩:=h
  constructor
  · rw [PairedBitXorScan.value_xor]
    simp only [pairedRows, hx, hy]
  · rw [PairedBitXorScan.source_preserved]
    exact hy

/-- Distinct-tape spectators are literal unchanged State fields at every
XOR prefix, independent of the symbol context on the output tape. -/
theorem xor_stage_run (left right wl wr:InputTape) (spare:Bool)
    (s:MarkedBitXorScan.State) (k:Nat) :
    run k (.xor left right wl wr spare s)=
      .xor left right wl wr spare (MarkedBitXorScan.run k s) := by
  induction k generalizing s with
  | zero => rfl
  | succ k ih => exact ih (MarkedBitXorScan.step s)

/-- Direct reuse of the accepted same-tape confinement theorem. Arbitrary
ambient contexts are supplied for this stage; the whole pipeline above starts
with empty output workspace and does not install such contexts for free. -/
theorem xor_stage_context (left right wl wr:InputTape) (spare:Bool)
    (before after:List MarkedBitXorScan.Symbol) (rows:List Pair) :
    Trace (5*rows.length+4)
      (.xor left right wl wr spare (MarkedXorFraming.embed before after (MarkedBitXorScan.initial rows)))
      (.xor left right wl wr spare
        (MarkedXorFraming.embed before after (MarkedBitXorScan.final (rows.map xorPair)))) :=
  xor_trace left right wl wr spare (MarkedXorFraming.framed_scan_exact before after rows)

end CurrentMain.PreparedPairXor

#print axioms CurrentMain.PreparedPairXor.preparation_handoff
#print axioms CurrentMain.PreparedPairXor.pairing_handoff
#print axioms CurrentMain.PreparedPairXor.machine_exact
#print axioms CurrentMain.PreparedPairXor.machine_result
#print axioms CurrentMain.PreparedPairXor.output_values
#print axioms CurrentMain.PreparedPairXor.xor_stage_run
#print axioms CurrentMain.PreparedPairXor.xor_stage_context
#check @CurrentMain.PreparedPairXor.machine_result
#check @CurrentMain.PreparedPairXor.xor_stage_context
