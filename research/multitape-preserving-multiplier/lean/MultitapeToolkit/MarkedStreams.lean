import MultitapeToolkit.MarkedStreamModel

/-!
Concrete three-state marked-stream transfer and a real bit-flipping child.
The transfer table follows PR1379 commit 3a45bd089ad56c38b55da8d80d7b056f2d90e5fa.
Each cost counts literal transitions, including empty input and marker return.
-/
namespace MultitapeToolkit.Absolute.MarkedStreams
open MultitapeToolkit.Locality MultitapeToolkit.Absolute.FrameRule
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

@[simp] theorem view_two_last_blank (h : ℤ) (l : List Symbol) (v : Symbol) (p : ℤ → Symbol) :
    cellView h l [v,.blank] p = cellView h l [v] p :=
  view_trailing_blank h l [v] p

def moveProgram (s d : ι) : Program ι Symbol MovePhase where
  transition q scanned := match q, scanned s, scanned d with
    | .copy, .bit b, .blank => some (.copy, actions2 s d (.blank,.right) (.bit b,.right) scanned)
    | .copy, .blank, .blank => some (.rewind, actions2 s d (.blank,.left) (.blank,.left) scanned)
    | .rewind, .blank, .bit b => some (.rewind, actions2 s d (.blank,.left) (.bit b,.left) scanned)
    | .rewind, .separator, .separator => some (.done, actions2 s d (.separator,.right) (.separator,.right) scanned)
    | _, _, _ => none

def streamTape (bits : List Bool) (past : ℤ → Symbol) : TapeData :=
  ⟨0,[.separator],bits.map .bit,past⟩
@[simp] theorem streamTape_cell (bits : List Bool) (past : ℤ → Symbol) :
    (streamTape bits past).cell = markedStream bits past := rfl

def moveInput (s d : ι) (bits : List Bool) (sourcePast destPast : ℤ → Symbol)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) : Config ι Symbol MovePhase :=
  bank2 s d .copy (streamTape bits sourcePast) (streamTape [] destPast) heads cells

def moveOutput (s d : ι) (bits : List Bool) (sourcePast destPast : ℤ → Symbol)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) : Config ι Symbol MovePhase :=
  bank2 s d .done (streamTape [] sourcePast) (streamTape bits destPast) heads cells

def sourceReading (erased : ℕ) (bits : List Bool) (past : ℤ → Symbol) : TapeData :=
  ⟨erased,List.replicate erased .blank ++ [.separator],bits.map .bit,past⟩

def sourceRewind : ℕ → (ℤ → Symbol) → TapeData
  | 0,past => ⟨-1,[],[.separator],past⟩
  | n+1,past => ⟨n,List.replicate n .blank ++ [.separator],[],past⟩

def destEnd (bits : List Bool) (past : ℤ → Symbol) : TapeData :=
  ⟨bits.length,bits.map .bit ++ [.separator],[],past⟩

def destRewind : List Bool → List Symbol → (ℤ → Symbol) → TapeData
  | [],r,past => ⟨-1,[],.separator::r,past⟩
  | b::bs,r,past => ⟨bs.length,bs.map .bit ++ [.separator],.bit b::r,past⟩

def destFinish (bits : List Bool) (r : List Symbol) (past : ℤ → Symbol) : TapeData :=
  ⟨0,[.separator],bits.reverse.map .bit ++ r,past⟩

@[simp] theorem sourceReading_read (e : ℕ) (b : Bool) (bs : List Bool) (p : ℤ → Symbol) :
    (sourceReading e (b::bs) p).read = .bit b := rfl
@[simp] theorem sourceReading_nil_read (e : ℕ) (p : ℤ → Symbol) :
    (sourceReading e [] p).read = .blank := rfl
@[simp] theorem destEnd_read (bs : List Bool) (p : ℤ → Symbol) :
    (destEnd bs p).read = .blank := rfl
@[simp] theorem sourceRewind_zero_read (p : ℤ → Symbol) :
    (sourceRewind 0 p).read = .separator := rfl
@[simp] theorem sourceRewind_succ_read (n : ℕ) (p : ℤ → Symbol) :
    (sourceRewind (n+1) p).read = .blank := rfl
@[simp] theorem destRewind_zero_read (r : List Symbol) (p : ℤ → Symbol) :
    (destRewind [] r p).read = .separator := rfl
@[simp] theorem destRewind_cons_read (b : Bool) (bs : List Bool) (r : List Symbol) (p : ℤ → Symbol) :
    (destRewind (b::bs) r p).read = .bit b := rfl

theorem source_read_bit (e : ℕ) (b : Bool) (bs : List Bool) (p : ℤ → Symbol) :
    Physical (sourceReading e (b::bs) p) (.blank,.right) (sourceReading (e+1) bs p) := by
  convert physical_right (sourceReading e (b::bs) p) .blank using 1 <;>
    simp [sourceReading,TapeData.write,TapeData.rightward,TapeData.read,List.replicate_succ]

theorem dest_append_bit (bs : List Bool) (b : Bool) (p : ℤ → Symbol) :
    Physical (destEnd bs p) (.bit b,.right) (destEnd (b::bs) p) := by
  convert physical_right (destEnd bs p) (.bit b) using 1 <;>
    simp [destEnd,TapeData.write,TapeData.rightward,TapeData.read]

theorem source_start_rewind (e : ℕ) (p : ℤ → Symbol) :
    Physical (sourceReading e [] p) (.blank,.left) (sourceRewind e p) := by
  have h := physical_left (sourceReading e [] p) .blank (by simp [sourceReading])
  apply h.congr
  cases e with
  | zero => constructor <;> simp [sourceReading,sourceRewind,TapeData.write,TapeData.leftward,TapeData.cell]
  | succ e =>
    constructor
    · simp [sourceReading,sourceRewind,TapeData.write,TapeData.leftward]
    · simp [sourceReading,sourceRewind,TapeData.write,TapeData.leftward,TapeData.cell,List.replicate_succ]

theorem dest_start_rewind (bs : List Bool) (p : ℤ → Symbol) :
    Physical (destEnd bs p) (.blank,.left) (destRewind bs [] p) := by
  have h := physical_left (destEnd bs p) .blank (by simp [destEnd])
  apply h.congr
  cases bs with
  | nil => constructor <;> simp [destEnd,destRewind,TapeData.write,TapeData.leftward,TapeData.cell]
  | cons b bs => constructor <;> simp [destEnd,destRewind,TapeData.write,TapeData.leftward,TapeData.cell]

theorem source_rewind_bit (n : ℕ) (p : ℤ → Symbol) :
    Physical (sourceRewind (n+1) p) (.blank,.left) (sourceRewind n p) := by
  have h := physical_left (sourceRewind (n+1) p) .blank (by simp [sourceRewind])
  apply h.congr
  cases n with
  | zero => constructor <;> simp [sourceRewind,TapeData.write,TapeData.leftward,TapeData.cell]
  | succ n => constructor <;> simp [sourceRewind,TapeData.write,TapeData.leftward,TapeData.cell,List.replicate_succ]

theorem dest_rewind_bit (b : Bool) (bs : List Bool) (r : List Symbol) (p : ℤ → Symbol) :
    Physical (destRewind (b::bs) r p) (.bit b,.left) (destRewind bs (.bit b::r) p) := by
  have h := physical_left (destRewind (b::bs) r p) (.bit b) (by simp [destRewind])
  apply h.congr
  cases bs with
  | nil => constructor <;> simp [destRewind,TapeData.write,TapeData.leftward,TapeData.cell]
  | cons a bs => constructor <;> simp [destRewind,TapeData.write,TapeData.leftward,TapeData.cell]

theorem source_finish_rewind (p : ℤ → Symbol) :
    Physical (sourceRewind 0 p) (.separator,.right) (streamTape [] p) := by
  convert physical_right (sourceRewind 0 p) .separator using 1 <;>
    simp [sourceRewind,streamTape,TapeData.write,TapeData.rightward,TapeData.read]

theorem dest_finish_rewind (r : List Symbol) (p : ℤ → Symbol) :
    Physical (destRewind [] r p) (.separator,.right) (destFinish [] r p) := by
  convert physical_right (destRewind [] r p) .separator using 1 <;>
    simp [destRewind,destFinish,TapeData.write,TapeData.rightward,TapeData.read]

theorem move_forward (s d : ι) (hne : s ≠ d) (bits acc : List Bool)
    (sp dp : ℤ → Symbol) (H : ι → ℤ) (C : ι → ℤ → Symbol) :
    Runs (moveProgram s d) (bits.length+1)
      (bank2 s d .copy (sourceReading acc.length bits sp) (destEnd acc dp) H C)
      (bank2 s d .rewind (sourceRewind (bits.length+acc.length) sp)
        (destRewind (bits.reverse++acc) [] dp) H C) := by
  induction bits generalizing acc with
  | nil =>
    apply Runs.cons _ (Runs.refl _)
    apply bank2_step (moveProgram s d) s d hne (a := (.blank,.left)) (b := (.blank,.left))
    · simp [moveProgram,bank2,hne,Ne.symm hne,TapeData.cell_read]
    · simpa using source_start_rewind acc.length sp
    · exact dest_start_rewind _ _
  | cons b bs ih =>
    have hs : step (moveProgram s d)
        (bank2 s d .copy (sourceReading acc.length (b::bs) sp) (destEnd acc dp) H C) =
        some (bank2 s d .copy (sourceReading (b::acc).length bs sp) (destEnd (b::acc) dp) H C) := by
      apply bank2_step (moveProgram s d) s d hne (a := (.blank,.right)) (b := (.bit b,.right))
      · simp [moveProgram,bank2,hne,Ne.symm hne,TapeData.cell_read]
      · simpa using source_read_bit acc.length b bs sp
      · exact dest_append_bit acc b dp
    have hr := Runs.cons hs (ih (b::acc))
    simpa [List.reverse_cons,List.append_assoc,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm] using hr

theorem move_rewind (s d : ι) (hne : s ≠ d) (bits : List Bool) (r : List Symbol)
    (sp dp : ℤ → Symbol) (H : ι → ℤ) (C : ι → ℤ → Symbol) :
    Runs (moveProgram s d) (bits.length+1)
      (bank2 s d .rewind (sourceRewind bits.length sp) (destRewind bits r dp) H C)
      (bank2 s d .done (streamTape [] sp) (destFinish bits r dp) H C) := by
  induction bits generalizing r with
  | nil =>
    apply Runs.cons _ (Runs.refl _)
    apply bank2_step (moveProgram s d) s d hne (a := (.separator,.right)) (b := (.separator,.right))
    · simp [moveProgram,bank2,hne,Ne.symm hne,TapeData.cell_read]
    · exact source_finish_rewind _
    · exact dest_finish_rewind _ _
  | cons b bs ih =>
    have hs : step (moveProgram s d)
        (bank2 s d .rewind (sourceRewind (b::bs).length sp) (destRewind (b::bs) r dp) H C) =
        some (bank2 s d .rewind (sourceRewind bs.length sp) (destRewind bs (.bit b::r) dp) H C) := by
      apply bank2_step (moveProgram s d) s d hne (a := (.blank,.left)) (b := (.bit b,.left))
      · simp [moveProgram,bank2,hne,Ne.symm hne,TapeData.cell_read]
      · exact source_rewind_bit _ _
      · exact dest_rewind_bit _ _ _ _
    have hr := Runs.cons hs (ih (.bit b::r))
    simpa [destFinish,List.reverse_cons,List.map_append,List.append_assoc] using hr

/-- Actual exact transfer, including the two marker turnaround transitions. -/
theorem move_runs (s d : ι) (hne : s ≠ d) (bits : List Bool)
    (sp dp : ℤ → Symbol) (H : ι → ℤ) (C : ι → ℤ → Symbol) :
    Runs (moveProgram s d) (2*bits.length+2)
      (moveInput s d bits sp dp H C) (moveOutput s d bits sp dp H C) := by
  have hf := move_forward s d hne bits [] sp dp H C
  have hr := move_rewind s d hne bits.reverse [] sp dp H C
  simp only [List.length_nil,Nat.add_zero,List.append_nil,List.length_reverse] at hf hr
  have hh := Trace.runs_trans (moveProgram s d) hf hr
  simpa [moveInput,moveOutput,sourceReading,destEnd,destFinish,streamTape,
    List.reverse_reverse,Nat.mul_comm,Nat.mul_two,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm] using hh

@[simp] theorem move_halts (s d : ι) (bits : List Bool)
    (sp dp : ℤ → Symbol) (H : ι → ℤ) (C : ι → ℤ → Symbol) :
    Halts (moveProgram s d) (moveOutput s d bits sp dp H C) := by
  simp [Halts,step,moveProgram,moveOutput,bank2]

end MultitapeToolkit.Absolute.MarkedStreams
namespace MultitapeToolkit.Absolute.MarkedStreams
open MultitapeToolkit.Locality MultitapeToolkit.Absolute.FrameRule
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

def bank1 {Q : Type*} (s : ι) (q : Q) (t : TapeData)
    (H : ι → ℤ) (C : ι → ℤ → Symbol) : Config ι Symbol Q :=
  ⟨q, fun i => if i=s then t.head else H i,
    fun i => if i=s then t.cell else C i⟩

def actions1 (s : ι) (a : Symbol × Move) (scanned : ι → Symbol) : ι → Symbol × Move :=
  fun i => if i=s then a else (scanned i,.stay)

theorem bank1_step {Q : Type*} [Fintype Q] (P : Program ι Symbol Q)
    (s : ι) (q q' : Q) (t t' : TapeData) (H : ι → ℤ) (C : ι → ℤ → Symbol)
    (a : Symbol × Move)
    (htable : P.transition q (fun i => (bank1 s q t H C).cell i ((bank1 s q t H C).head i)) =
      some (q',actions1 s a (fun i => (bank1 s q t H C).cell i ((bank1 s q t H C).head i))))
    (ht : Physical t a t') :
    step P (bank1 s q t H C) = some (bank1 s q' t' H C) := by
  change P.transition (bank1 s q t H C).state _ = _ at htable
  simp only [step,htable,Option.map_some]
  congr 1
  apply Config.ext
  · rfl
  · funext i
    by_cases hi : i=s
    · subst i; simpa [bank1,actions1] using ht.1.symm
    · simp [bank1,actions1,hi,moveOffset]
  · funext i x
    by_cases hi : i=s
    · subst i; simpa [bank1,actions1] using congrFun ht.2.symm x
    · by_cases hx : x=H i <;> simp [bank1,actions1,hi,hx]

/-- A real finite child: flip each bit while scanning right, then return to its marker. -/
def flipProgram (s : ι) : Program ι Symbol FlipPhase where
  transition q scanned := match q, scanned s with
    | .copy,.bit b => some (.copy,actions1 s (.bit (!b),.right) scanned)
    | .copy,.blank => some (.rewind,actions1 s (.blank,.left) scanned)
    | .rewind,.bit b => some (.rewind,actions1 s (.bit b,.left) scanned)
    | .rewind,.separator => some (.done,actions1 s (.separator,.right) scanned)
    | _,_ => none

def flipInput (s : ι) (bits : List Bool) (past : ℤ → Symbol)
    (H : ι → ℤ) (C : ι → ℤ → Symbol) : Config ι Symbol FlipPhase :=
  bank1 s .copy (streamTape bits past) H C

def flipOutput (s : ι) (bits : List Bool) (past : ℤ → Symbol)
    (H : ι → ℤ) (C : ι → ℤ → Symbol) : Config ι Symbol FlipPhase :=
  bank1 s .done (streamTape (bits.map Bool.not) past) H C

def flipReading (acc bits : List Bool) (past : ℤ → Symbol) : TapeData :=
  ⟨acc.length,acc.map .bit ++ [.separator],bits.map .bit,past⟩

@[simp] theorem flipReading_read (acc : List Bool) (b : Bool) (bs : List Bool) (p : ℤ → Symbol) :
    (flipReading acc (b::bs) p).read = .bit b := rfl
@[simp] theorem flipReading_nil_read (acc : List Bool) (p : ℤ → Symbol) :
    (flipReading acc [] p).read = .blank := rfl

theorem flip_read_bit (acc : List Bool) (b : Bool) (bs : List Bool) (p : ℤ → Symbol) :
    Physical (flipReading acc (b::bs) p) (.bit (!b),.right) (flipReading ((!b)::acc) bs p) := by
  convert physical_right (flipReading acc (b::bs) p) (.bit (!b)) using 1 <;>
    simp [flipReading,TapeData.write,TapeData.rightward,TapeData.read]

theorem flip_forward (s : ι) (bits acc : List Bool) (p : ℤ → Symbol)
    (H : ι → ℤ) (C : ι → ℤ → Symbol) :
    Runs (flipProgram s) (bits.length+1)
      (bank1 s .copy (flipReading acc bits p) H C)
      (bank1 s .rewind (destRewind ((bits.map Bool.not).reverse++acc) [] p) H C) := by
  induction bits generalizing acc with
  | nil =>
    apply Runs.cons _ (Runs.refl _)
    apply bank1_step (flipProgram s) s (a := (.blank,.left))
    · simp [flipProgram,bank1,TapeData.cell_read]
    · exact dest_start_rewind acc p
  | cons b bs ih =>
    have hs : step (flipProgram s) (bank1 s .copy (flipReading acc (b::bs) p) H C) =
        some (bank1 s .copy (flipReading ((!b)::acc) bs p) H C) := by
      apply bank1_step (flipProgram s) s (a := (.bit (!b),.right))
      · simp [flipProgram,bank1,TapeData.cell_read]
      · exact flip_read_bit acc b bs p
    have hr := Runs.cons hs (ih ((!b)::acc))
    simpa [List.reverse_cons,List.append_assoc] using hr

theorem flip_rewind (s : ι) (bits : List Bool) (r : List Symbol) (p : ℤ → Symbol)
    (H : ι → ℤ) (C : ι → ℤ → Symbol) :
    Runs (flipProgram s) (bits.length+1)
      (bank1 s .rewind (destRewind bits r p) H C)
      (bank1 s .done (destFinish bits r p) H C) := by
  induction bits generalizing r with
  | nil =>
    apply Runs.cons _ (Runs.refl _)
    apply bank1_step (flipProgram s) s (a := (.separator,.right))
    · simp [flipProgram,bank1,TapeData.cell_read]
    · exact dest_finish_rewind r p
  | cons b bs ih =>
    have hs : step (flipProgram s) (bank1 s .rewind (destRewind (b::bs) r p) H C) =
        some (bank1 s .rewind (destRewind bs (.bit b::r) p) H C) := by
      apply bank1_step (flipProgram s) s (a := (.bit b,.left))
      · simp [flipProgram,bank1,TapeData.cell_read]
      · exact dest_rewind_bit b bs r p
    have hr := Runs.cons hs (ih (.bit b::r))
    simpa [destFinish,List.reverse_cons,List.map_append,List.append_assoc] using hr

/-- Fully instantiated actual bit-flip child; no assumed subroutine appears. -/
theorem flip_runs (s : ι) (bits : List Bool) (p : ℤ → Symbol)
    (H : ι → ℤ) (C : ι → ℤ → Symbol) :
    Runs (flipProgram s) (2*bits.length+2) (flipInput s bits p H C) (flipOutput s bits p H C) := by
  have hf := flip_forward s bits [] p H C
  have hr := flip_rewind s (bits.map Bool.not).reverse [] p H C
  simp only [List.append_nil,List.length_reverse,List.length_map] at hf hr
  have hh := Trace.runs_trans (flipProgram s) hf hr
  simpa [flipInput,flipOutput,flipReading,destFinish,streamTape,List.reverse_reverse,
    Nat.mul_comm,Nat.mul_two,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm] using hh

@[simp] theorem flip_halts (s : ι) (bits : List Bool) (p : ℤ → Symbol)
    (H : ι → ℤ) (C : ι → ℤ → Symbol) :
    Halts (flipProgram s) (flipOutput s bits p H C) := by
  simp [Halts,step,flipProgram,flipOutput,bank1]

end MultitapeToolkit.Absolute.MarkedStreams

