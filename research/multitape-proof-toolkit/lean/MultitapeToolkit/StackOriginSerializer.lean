import MultitapeToolkit.StackOriginModel
import MultitapeToolkit.MarkedStreams
import MultitapeToolkit.ParkStack

/-!
# Actual compiler-stack to origin-anchored output serialization

This is a concrete compiler ABI bridge, not new upstream serialization mathematics.
The upstream clocked serializer is already proved. Here a fixed five-state,
three-symbol native machine consumes an actual compiler stack, preserves every
padded bit, and restores both heads in exactly3m+4 physical transitions.
The reused proof-cursor erase lemma follows the credited Apache-2.0 PR64 lineage.
-/
set_option autoImplicit false
namespace MultitapeToolkit.Absolute.StackOriginSerializer
open MultitapeToolkit.Locality MarkedStreams
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

def actions (s d : ι) (a b : Option Bool × Move) (r : ι → Option Bool) :
    ι → Option Bool × Move :=
  fun i => if i=s then a else if i=d then b else (r i,.stay)

@[simp] theorem encoded_zero_read (t : TapeData) : encodedCell 0 t t.head = toBool t.read := by
  simpa using encodedCell_read 0 t
@[simp] theorem empty_stream_read : (streamTape [] clean).read = .blank := rfl
@[simp] theorem sourceInitial_read (bits : List Bool) : (sourceInitial bits).read = .separator := rfl
@[simp] theorem encodedActions_eq (s d : ι) (a b : Symbol × Move) (r : ι → Option Bool) :
    encodedActions s d a b r = actions s d (toBool a.1,a.2) (toBool b.1,b.2) r := rfl
/-- A literal finite control table; no list, length, absolute position or value
is available to the machine control. -/
def program (s d : ι) : Program ι (Option Bool) Phase where
  transition q r := match q with
    | .enter => some (.scan,actions s d (none,.right) (r d,.stay) r)
    | .scan => match r s with
      | some b => some (.scan,actions s d (some b,.right) (r d,.stay) r)
      | none => some (.copyReverse,actions s d (none,.left) (r d,.stay) r)
    | .copyReverse => match r s with
      | some b => some (.copyReverse,actions s d (none,.left) (some b,.right) r)
      | none => some (.rewind,actions s d (none,.stay) (r d,.left) r)
    | .rewind => match r d with
      | some b => some (.rewind,actions s d (r s,.stay) (some b,.left) r)
      | none => some (.done,actions s d (r s,.stay) (none,.right) r)
    | .done => none

def scanCursor (acc remaining : List Bool) : TapeData :=
  ⟨acc.length,acc.map .bit ++ [.separator],remaining.map .bit,clean⟩

def backSource (bits : List Bool) : TapeData := ParkStack.popReady bits 0 clean

theorem enter_physical (bits : List Bool) :
    Physical (sourceInitial bits) (.separator,.right) (scanCursor [] bits) := by
  convert physical_right (sourceInitial bits) .separator using 1 <;>
    simp [sourceInitial,scanCursor,TapeData.write,TapeData.rightward,TapeData.read]

theorem scan_bit_physical (acc bs : List Bool) (b : Bool) :
    Physical (scanCursor acc (b::bs)) (.bit b,.right) (scanCursor (b::acc) bs) := by
  convert physical_right (scanCursor acc (b::bs)) (.bit b) using 1 <;>
    simp [scanCursor,TapeData.write,TapeData.rightward,TapeData.read]

theorem scan_turn_physical (acc : List Bool) :
    Physical (scanCursor acc []) (.blank,.left) (backSource acc) := by
  cases acc with
  | nil => simpa [scanCursor,backSource,ParkStack.popReady,destEnd,destRewind] using dest_start_rewind [] clean
  | cons b bs => simpa [scanCursor,backSource,ParkStack.popReady,destEnd,destRewind] using dest_start_rewind (b::bs) clean

@[simp] theorem scan_read_bit (acc bs : List Bool) (b : Bool) :
    (scanCursor acc (b::bs)).read = .bit b := rfl
@[simp] theorem scan_read_nil (acc : List Bool) : (scanCursor acc []).read = .blank := rfl
@[simp] theorem back_read_bit (bs : List Bool) (b : Bool) :
    (backSource (b::bs)).read = .bit b := rfl
@[simp] theorem back_read_nil : (backSource []).read = .separator := rfl

/-- Actual scanning reaches the high end; original data are not erased yet. -/
theorem scan_run (s d : ι) (hne : s≠d) (bits acc : List Bool) (offset : ℤ)
    (heads : ι → ℤ) (cells : ι → ℤ → Option Bool) :
    Runs (program s d) (bits.length+1)
      (bank s d .scan offset (scanCursor acc bits) (streamTape [] clean) heads cells)
      (bank s d .copyReverse offset (backSource (bits.reverse++acc))
        (streamTape [] clean) heads cells) := by
  induction bits generalizing acc with
  | nil =>
    apply Runs.cons _ (Runs.refl _)
    apply bank_step (program s d) s d hne .scan .copyReverse offset
      (scanCursor acc []) (streamTape [] clean) (backSource acc) (streamTape [] clean)
      heads cells (.blank,.left) (.blank,.stay)
    · simp [program,bank,encodedActions_eq,hne,Ne.symm hne,encodedCell_read,
        toBool]
    · exact scan_turn_physical acc
    · exact physical_stay _
  | cons b bs ih =>
    have hs : step (program s d)
        (bank s d .scan offset (scanCursor acc (b::bs)) (streamTape [] clean) heads cells) =
        some (bank s d .scan offset (scanCursor (b::acc) bs) (streamTape [] clean) heads cells) := by
      apply bank_step (program s d) s d hne .scan .scan offset
        (scanCursor acc (b::bs)) (streamTape [] clean) (scanCursor (b::acc) bs)
        (streamTape [] clean) heads cells (.bit b,.right) (.blank,.stay)
      · simp [program,bank,encodedActions_eq,hne,Ne.symm hne,encodedCell_read,
          toBool]
      · exact scan_bit_physical acc bs b
      · exact physical_stay _
    simpa [List.reverse_cons,List.append_assoc] using Runs.cons hs (ih (b::acc))

/-- Copy right-to-left while physically clearing every source bit. -/
theorem copy_run (s d : ι) (hne : s≠d) (bits acc : List Bool) (offset : ℤ)
    (heads : ι → ℤ) (cells : ι → ℤ → Option Bool) :
    Runs (program s d) (bits.length+1)
      (bank s d .copyReverse offset (backSource bits) (destEnd acc clean) heads cells)
      (bank s d .rewind offset (backSource [])
        (destRewind (bits.reverse++acc) [] clean) heads cells) := by
  induction bits generalizing acc with
  | nil =>
    apply Runs.cons _ (Runs.refl _)
    apply bank_step (program s d) s d hne .copyReverse .rewind offset
      (backSource []) (destEnd acc clean) (backSource []) (destRewind acc [] clean)
      heads cells (.separator,.stay) (.blank,.left)
    · simp [program,bank,encodedActions_eq,hne,Ne.symm hne,encodedCell_read,toBool]
    · exact physical_stay _
    · exact dest_start_rewind acc clean
  | cons b bs ih =>
    have hs : step (program s d)
        (bank s d .copyReverse offset (backSource (b::bs)) (destEnd acc clean) heads cells) =
        some (bank s d .copyReverse offset (backSource bs) (destEnd (b::acc) clean) heads cells) := by
      apply bank_step (program s d) s d hne .copyReverse .copyReverse offset
        (backSource (b::bs)) (destEnd acc clean) (backSource bs) (destEnd (b::acc) clean)
        heads cells (.blank,.left) (.bit b,.right)
      · simp [program,bank,encodedActions_eq,hne,Ne.symm hne,encodedCell_read,toBool]
      · exact ParkStack.erase_pop b bs 0 clean
      · exact dest_append_bit acc b clean
    simpa [List.reverse_cons,List.append_assoc] using Runs.cons hs (ih (b::acc))

/-- The output head physically returns to origin; no head reset is free. -/
theorem rewind_run (s d : ι) (hne : s≠d) (bits : List Bool) (right : List Symbol)
    (offset : ℤ) (heads : ι → ℤ) (cells : ι → ℤ → Option Bool) :
    Runs (program s d) (bits.length+1)
      (bank s d .rewind offset (backSource []) (destRewind bits right clean) heads cells)
      (bank s d .done offset (backSource []) (destFinish bits right clean) heads cells) := by
  induction bits generalizing right with
  | nil =>
    apply Runs.cons _ (Runs.refl _)
    apply bank_step (program s d) s d hne .rewind .done offset
      (backSource []) (destRewind [] right clean) (backSource []) (destFinish [] right clean)
      heads cells (.separator,.stay) (.separator,.right)
    · simp [program,bank,encodedActions_eq,hne,Ne.symm hne,encodedCell_read,toBool]
    · exact physical_stay _
    · exact dest_finish_rewind right clean
  | cons b bs ih =>
    have hs : step (program s d)
        (bank s d .rewind offset (backSource []) (destRewind (b::bs) right clean) heads cells) =
        some (bank s d .rewind offset (backSource []) (destRewind bs (.bit b::right) clean) heads cells) := by
      apply bank_step (program s d) s d hne .rewind .rewind offset
        (backSource []) (destRewind (b::bs) right clean) (backSource [])
        (destRewind bs (.bit b::right) clean) heads cells (.separator,.stay) (.bit b,.left)
      · simp [program,bank,encodedActions_eq,hne,Ne.symm hne,encodedCell_read,toBool]
      · exact physical_stay _
      · exact dest_rewind_bit b bs right clean
    simpa [destFinish,List.reverse_cons,List.map_append,List.append_assoc] using
      Runs.cons hs (ih (.bit b::right))

@[simp] theorem sourceStack_nil (h : ℤ) : sourceStack h [] = fun _ => none := by
  funext x
  simp only [sourceStack,absoluteCell]
  generalize x-h = z
  cases z with
  | ofNat n => cases n <;> simp [stackTape,Turing.Tape.nth,Turing.ListBlank.nth_mk] <;> rfl
  | negSucc n => simp [stackTape,Turing.Tape.nth,Turing.ListBlank.nth_mk]; rfl

@[simp] theorem backSource_nil_cell (offset : ℤ) :
    encodedCell offset (backSource []) = fun _ => none := by
  have he : backSource [] = sourceInitial [] := rfl
  rw [he]
  simpa only [sub_add_cancel,sourceStack_nil] using sourceInitial_abi (offset-1) []

@[simp] theorem originWord_nil : originWord [] = fun _ => none := by
  funext x; simp [originWord]

/-- Literal compiler-stack entry; all other physical cells and heads are arbitrary. -/
def input (s d : ι) (h : ℤ) (bits : List Bool)
    (heads : ι → ℤ) (cells : ι → ℤ → Option Bool) : Config ι (Option Bool) Phase :=
  ⟨.enter,fun i => if i=s then h else if i=d then 0 else heads i,
    fun i => if i=s then sourceStack h bits else if i=d then fun _ => none else cells i⟩

/-- Literal clean-source, padded reverse-word endpoint with both heads restored. -/
def output (s d : ι) (h : ℤ) (bits : List Bool)
    (heads : ι → ℤ) (cells : ι → ℤ → Option Bool) : Config ι (Option Bool) Phase :=
  ⟨.done,fun i => if i=s then h else if i=d then 0 else heads i,
    fun i => if i=s then fun _ => none else if i=d then originWord bits.reverse else cells i⟩

theorem input_bank (s d : ι) (h : ℤ) (bits : List Bool)
    (heads : ι → ℤ) (cells : ι → ℤ → Option Bool) :
    bank s d .enter (h+1) (sourceInitial bits) (streamTape [] clean) heads cells =
      input s d h bits heads cells := by
  apply Config.ext
  · rfl
  · funext i; simp [bank,input,sourceInitial,streamTape]
  · funext i; simp [bank,input,sourceInitial_abi,streamTape_origin,originWord]

theorem output_bank (s d : ι) (h : ℤ) (bits : List Bool)
    (heads : ι → ℤ) (cells : ι → ℤ → Option Bool) :
    bank s d .done (h+1) (backSource []) (destFinish bits [] clean) heads cells =
      output s d h bits heads cells := by
  apply Config.ext
  · rfl
  · funext i; simp [bank,output,backSource,ParkStack.popReady,destFinish]
  · have hd : destFinish bits [] clean = streamTape bits.reverse clean := by
      simp [destFinish,streamTape]
    funext i
    simp [bank,output,hd,streamTape_origin]

/-- Universal exact physical serializer. Width, stack value and head position
are proof parameters only. Every padded bit is retained; empty input costs4. -/
theorem serialize_correct (s d : ι) (hne : s≠d) (h : ℤ) (bits : List Bool)
    (heads : ι → ℤ) (cells : ι → ℤ → Option Bool) :
    Runs (program s d) (3*bits.length+4)
      (input s d h bits heads cells) (output s d h bits heads cells) ∧
    Halts (program s d) (output s d h bits heads cells) := by
  have he : step (program s d)
      (bank s d .enter (h+1) (sourceInitial bits) (streamTape [] clean) heads cells) =
      some (bank s d .scan (h+1) (scanCursor [] bits) (streamTape [] clean) heads cells) := by
    apply bank_step (program s d) s d hne .enter .scan (h+1)
      (sourceInitial bits) (streamTape [] clean) (scanCursor [] bits) (streamTape [] clean)
      heads cells (.separator,.right) (.blank,.stay)
    · simp [program,bank,encodedActions_eq,hne,Ne.symm hne,encodedCell_read,
        toBool]
    · exact enter_physical bits
    · exact physical_stay _
  have hs := scan_run s d hne bits [] (h+1) heads cells
  have hc := copy_run s d hne bits.reverse [] (h+1) heads cells
  have hr := rewind_run s d hne bits [] (h+1) heads cells
  simp only [List.append_nil] at hs
  simp only [List.reverse_reverse,List.append_nil] at hc
  have hb : destEnd [] clean = streamTape [] clean := rfl
  rw [hb] at hc
  have hall := Trace.runs_trans (program s d)
    (Trace.runs_trans (program s d) (Runs.cons he hs) hc) hr
  constructor
  · simpa [List.length_reverse,input_bank,output_bank,Nat.mul_comm,
      Nat.add_assoc,Nat.add_comm,Nat.add_left_comm,Nat.mul_succ] using hall
  · simp [Halts,step,program,output]

/-- The machine preserves any spectator literally; no clean-exterior premise. -/
theorem spectator_preserved (s d j : ι) (hs : j≠s) (hd : j≠d)
    (h : ℤ) (bits : List Bool) (heads : ι → ℤ) (cells : ι → ℤ → Option Bool) :
    (output s d h bits heads cells).head j = heads j ∧
    (output s d h bits heads cells).cell j = cells j := by
  simp [output,hs,hd]

theorem phase_card : Fintype.card Phase = 5 := by decide
theorem alphabet_card : Fintype.card (Option Bool) = 3 := by decide

end MultitapeToolkit.Absolute.StackOriginSerializer


