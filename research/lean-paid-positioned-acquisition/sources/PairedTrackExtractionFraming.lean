import PairedTrackExtraction

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.
Ambient source confinement for the unchanged paired-track extractor. Literal
markers stop every source scan and rewind. Arbitrary left/right packed-store
spectators survive every actual prefix, even if they contain markers. The
fresh output remains a distinct tape, whose allocation is counted.
This reuses the accepted marked-XOR/writeback framing proof pattern; no copy
algorithm, assumed endpoint or unpriced tape relayout is introduced.
Actual access from global home and return are the subsequent charged join.
Author-checked context kappa=836330098538459/500000000000000000.
-/
set_option Elab.async false
set_option autoImplicit false
namespace CurrentMain.PairedTrackExtractionFraming
open PairedBitXorScan (Tape Pair)
open MarkedBitXorScan (marked dataSymbol)
open PairedTrackExtraction
open SequentialBitAddition (Registers)

def embed (left right:List Symbol) (s:State) : State :=
  {s with source:=⟨s.source.left++left,s.source.right++right⟩}

/-- Only phases whose next source move cannot cross R may inhabit R. -/
def RightSafe : Phase → Prop
  | .copyTest | .advanceOutput | .writeOutputRight | .rewindOutput | .rewindInput | .clear _ | .halt => True
  | _ => False
inductive Confined : State → Prop where
  | home (rows:List Pair) (out:Tape BitSymbol) (r:Registers) (p:Phase) :
      Confined ⟨⟨[],marked rows⟩,out,r,p⟩
  | body (ls:List Pair) (a b:Bool) (rs:List Pair) (out:Tape BitSymbol) (r:Registers) (p:Phase) :
      Confined ⟨⟨ls.map dataSymbol++[.leftMarker],.data a b::(rs.map dataSymbol++[.rightMarker])⟩,out,r,p⟩
  | rightEnd (ls:List Pair) (out:Tape BitSymbol) (r:Registers) (p:Phase) (safe:RightSafe p) :
      Confined ⟨⟨ls.map dataSymbol++[.leftMarker],[.rightMarker]⟩,out,r,p⟩
private theorem inside (ls rs:List Pair) (out:Tape BitSymbol) (r:Registers) (p:Phase) (safe:RightSafe p) :
    Confined ⟨⟨ls.map dataSymbol++[.leftMarker],rs.map dataSymbol++[.rightMarker]⟩,out,r,p⟩ := by
  cases rs with
  | nil => exact Confined.rightEnd ls out r p safe
  | cons row rs => rcases row with ⟨a,b⟩;exact Confined.body ls a b rs out r p

/-- Confinement is derived from the actual finite transition table. -/
theorem confined_step (second:Bool) {s:State} (h:Confined s) : Confined (step second s) := by
  cases h with
  | home rows out r p =>
      cases p with
      | enterInput =>
          simpa [step,marked,Tape.moveRight] using inside [] rows out r .copyTest (by trivial)
      | advanceInput =>
          simpa [step,marked,Tape.moveRight] using inside [] rows out r .advanceOutput (by trivial)
      | copyTest => simpa [step,marked,Tape.readHead] using Confined.home rows out r .halt
      | rewindInput => simpa [step,marked,Tape.readHead] using Confined.home rows out r (.clear .x)
      | rewindOutput =>
          by_cases hh:out.readHead .blank=.leftMarker <;> simp only [step,hh,if_true,if_false]
          all_goals exact Confined.home _ _ _ _
      | writeOutputLeft => exact Confined.home _ _ _ _
      | enterOutput => exact Confined.home _ _ _ _
      | copyWrite => exact Confined.home _ _ _ _
      | advanceOutput => exact Confined.home _ _ _ _
      | writeOutputRight => exact Confined.home _ _ _ _
      | clear slot => exact Confined.home _ _ _ _
      | halt => exact Confined.home _ _ _ _
  | body ls a b rs out r p =>
      cases p with
      | enterInput =>
          simpa [step,Tape.moveRight,dataSymbol] using inside ((a,b)::ls) rs out r .copyTest (by trivial)
      | advanceInput =>
          simpa [step,Tape.moveRight,dataSymbol] using inside ((a,b)::ls) rs out r .advanceOutput (by trivial)
      | copyTest => simpa [step,Tape.readHead] using Confined.body ls a b rs out {r with sum:=chosen second (a,b)} .copyWrite
      | rewindInput =>
          cases ls with
          | nil => simpa [step,Tape.readHead,Tape.moveLeft,marked,dataSymbol] using Confined.home ((a,b)::rs) out r .rewindInput
          | cons row ls =>
              rcases row with ⟨x,y⟩
              simpa [step,Tape.readHead,Tape.moveLeft,dataSymbol] using Confined.body ls x y ((a,b)::rs) out r .rewindInput
      | rewindOutput =>
          by_cases hh:out.readHead .blank=.leftMarker <;> simp only [step,hh,if_true,if_false]
          all_goals exact Confined.body _ _ _ _ _ _ _
      | writeOutputLeft => exact Confined.body _ _ _ _ _ _ _
      | enterOutput => exact Confined.body _ _ _ _ _ _ _
      | copyWrite => exact Confined.body _ _ _ _ _ _ _
      | advanceOutput => exact Confined.body _ _ _ _ _ _ _
      | writeOutputRight => exact Confined.body _ _ _ _ _ _ _
      | clear slot => exact Confined.body _ _ _ _ _ _ _
      | halt => exact Confined.body _ _ _ _ _ _ _
  | rightEnd ls out r p safe =>
      cases p with
      | writeOutputLeft | enterOutput | enterInput | copyWrite | advanceInput => exact False.elim safe
      | copyTest => simpa [step,Tape.readHead] using Confined.rightEnd ls out r .writeOutputRight (by trivial)
      | advanceOutput => exact Confined.rightEnd _ _ _ _ (by trivial)
      | writeOutputRight => exact Confined.rightEnd _ _ _ _ (by trivial)
      | rewindOutput =>
          by_cases hh:out.readHead .blank=.leftMarker <;> simp only [step,hh,if_true,if_false]
          all_goals exact Confined.rightEnd _ _ _ _ (by trivial)
      | rewindInput =>
          cases ls with
          | nil => simpa [step,Tape.readHead,Tape.moveLeft,marked] using Confined.home [] out r .rewindInput
          | cons row ls =>
              rcases row with ⟨x,y⟩
              simpa [step,Tape.readHead,Tape.moveLeft,dataSymbol] using Confined.body ls x y [] out r .rewindInput
      | clear slot => cases slot <;> exact Confined.rightEnd _ _ _ _ (by trivial)
      | halt => exact Confined.rightEnd _ _ _ _ (by trivial)

theorem step_embed (second:Bool) (left right:List Symbol) {s:State} (h:Confined s) :
    step second (embed left right s)=embed left right (step second s) := by
  cases h with
  | home rows out r p =>
      by_cases hh:out.readHead .blank=.leftMarker <;> cases p <;>
        simp_all [embed,step,marked,Tape.readHead,Tape.moveRight,Tape.moveLeft,List.append_assoc]
  | body ls a b rs out r p =>
      by_cases hh:out.readHead .blank=.leftMarker <;> cases p <;> cases ls <;>
        simp_all [embed,step,Tape.readHead,Tape.moveRight,Tape.moveLeft,dataSymbol,List.append_assoc]
  | rightEnd ls out r p safe =>
      by_cases hh:out.readHead .blank=.leftMarker <;> cases p <;> cases ls <;>
        simp_all [RightSafe,embed,step,Tape.readHead,Tape.moveRight,Tape.moveLeft,dataSymbol,List.append_assoc]

theorem run_embed (second:Bool) (left right:List Symbol) (s:State) (h:Confined s) (k:Nat) :
    run second k (embed left right s)=embed left right (run second k s) := by
  induction k generalizing s with
  | zero => rfl
  | succ k ih =>
      simp only [run]
      rw [step_embed second left right h]
      exact ih (step second s) (confined_step second h)

theorem cells_embed (left right:List Symbol) (s:State) :
    cells (embed left right s)=left.length+cells s+right.length := by
  simp [embed,cells]
  omega

/-- The source block and both spectators survive; the fresh output contains
exactly the selected track. Every marker/return/clear transition is charged. -/
theorem framed_result (second:Bool) (left right:List Symbol) (rows:List Pair) (r:Registers) :
    run second (6*rows.length+16) (embed left right (initial rows r))=
      embed left right (final second rows) ∧
    ∀ k<6*rows.length+16,(run second k (embed left right (initial rows r))).phase≠.halt := by
  constructor
  · rw [run_embed second left right (initial rows r) (Confined.home rows _ r _), (extraction_result second rows r).1]
  · intro k hk
    rw [run_embed second left right (initial rows r) (Confined.home rows _ r _)]
    exact (extraction_result second rows r).2.2 k hk

theorem framed_storage (second:Bool) (left right:List Symbol) (rows:List Pair) (r:Registers) (k:Nat) :
    cells (run second k (embed left right (initial rows r)))≤left.length+(2*rows.length+4)+right.length := by
  rw [run_embed second left right (initial rows r) (Confined.home rows _ r _),cells_embed]
  have h:=extraction_storage second rows r k
  omega

end CurrentMain.PairedTrackExtractionFraming
#print axioms CurrentMain.PairedTrackExtractionFraming.confined_step
#print axioms CurrentMain.PairedTrackExtractionFraming.step_embed
#print axioms CurrentMain.PairedTrackExtractionFraming.run_embed
#print axioms CurrentMain.PairedTrackExtractionFraming.cells_embed
#print axioms CurrentMain.PairedTrackExtractionFraming.framed_result
#print axioms CurrentMain.PairedTrackExtractionFraming.framed_storage
#check @CurrentMain.PairedTrackExtractionFraming.framed_result
#check @CurrentMain.PairedTrackExtractionFraming.framed_storage
