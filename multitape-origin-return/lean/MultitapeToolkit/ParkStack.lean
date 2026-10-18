/- SPDX-License-Identifier: Apache-2.0
Port of the PR64 primitives by rfu08; see the provenance below. -/
import MultitapeToolkit.MarkedStreamModel
import Mathlib.Data.List.GetD
import Mathlib.Tactic.DeriveFintype

set_option autoImplicit false

/-!
# Exact fixed-control parking push and pop

The transition tables and phase induction follow rfu08's Apache-2.0 licensed
PR64 `TapeStack.lean` and `TapeStackPush.lean`, pinned at commit
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
Modifications: actual Option-valued halting, generic selected physical tapes,
absolute head coordinates, and arbitrary dirty ancestor cell functions.
-/
namespace MultitapeToolkit.Absolute.ParkStack
open MultitapeToolkit.Locality MarkedStreams

variable {ι : Type*} [Fintype ι] [DecidableEq ι]

inductive PushPhase where
  | copy | rewind | done
  deriving DecidableEq, Repr

instance : Fintype PushPhase :=
  ⟨{.copy,.rewind,.done}, by intro q; cases q <;> simp⟩

def pushProgram (s p : ι) : Program ι Symbol PushPhase where
  transition q scanned := match q with
  | .done => none
  | .copy => match scanned s with
    | .bit b => some (.copy,actions2 s p (.blank,.right) (.bit b,.right) scanned)
    | .blank => some (.rewind,actions2 s p (.blank,.left) (.separator,.right) scanned)
    | .separator => some (.done,actions2 s p (scanned s,.stay) (scanned p,.stay) scanned)
  | .rewind => match scanned s with
    | .blank => some (.rewind,actions2 s p (.blank,.left) (scanned p,.stay) scanned)
    | .separator => some (.done,actions2 s p (.separator,.right) (scanned p,.stay) scanned)
    | .bit _ => some (.done,actions2 s p (scanned s,.stay) (scanned p,.stay) scanned)

def atEnd (h : ℤ) (left : List Symbol) (past : ℤ → Symbol) : TapeData :=
  ⟨h,left,[],past⟩

def clean : ℤ → Symbol := fun _ => .blank

def reading (erased : ℕ) (bits : List Bool) : TapeData :=
  ⟨erased,List.replicate erased .blank ++ [.separator],bits.map .bit,clean⟩

def rewinding : ℕ → TapeData
  | 0 => ⟨-1,[],[.separator],clean⟩
  | n+1 => ⟨n,List.replicate n .blank ++ [.separator],[],clean⟩

@[simp] theorem atEnd_read (h : ℤ) (l : List Symbol) (p : ℤ → Symbol) :
    (atEnd h l p).read = .blank := rfl
@[simp] theorem reading_read (e : ℕ) (b : Bool) (bs : List Bool) :
    (reading e (b::bs)).read = .bit b := rfl
@[simp] theorem reading_nil_read (e : ℕ) : (reading e []).read = .blank := rfl
@[simp] theorem rewinding_zero_read : (rewinding 0).read = .separator := rfl
@[simp] theorem rewinding_succ_read (n : ℕ) : (rewinding (n+1)).read = .blank := rfl

theorem append_symbol (h : ℤ) (l : List Symbol) (p : ℤ → Symbol) (v : Symbol) :
    Physical (atEnd h l p) (v,.right) (atEnd (h+1) (v::l) p) := by
  exact physical_right _ _

theorem read_bit (e : ℕ) (b : Bool) (bs : List Bool) :
    Physical (reading e (b::bs)) (.blank,.right) (reading (e+1) bs) := by
  convert physical_right (reading e (b::bs)) .blank using 1 <;>
    simp [reading, TapeData.write, TapeData.rightward, TapeData.read,
      List.replicate_succ]

theorem start_rewind (e : ℕ) :
    Physical (reading e []) (.blank,.left) (rewinding e) := by
  have h := physical_left (reading e []) .blank (by simp [reading])
  apply h.congr
  cases e with
  | zero =>
    constructor
    · rfl
    · simpa [reading,rewinding,TapeData.cell,TapeData.write,TapeData.leftward] using
        (view_trailing_blank (-1) [] [.separator] clean)
  | succ e =>
    constructor
    · simp [reading, rewinding, TapeData.write, TapeData.leftward]
    · simpa [reading,rewinding,TapeData.cell,TapeData.write,TapeData.leftward,List.replicate_succ] using
        (view_trailing_blank (e:ℤ) (List.replicate e .blank ++ [.separator]) [.blank] clean).trans
          (view_blank (e:ℤ) (List.replicate e .blank ++ [.separator]) clean)

theorem rewind_blank (e : ℕ) :
    Physical (rewinding (e+1)) (.blank,.left) (rewinding e) := by
  have h := physical_left (rewinding (e+1)) .blank (by simp [rewinding])
  apply h.congr
  cases e with
  | zero =>
    constructor
    · rfl
    · simpa [reading,rewinding,TapeData.cell,TapeData.write,TapeData.leftward] using
        (view_trailing_blank (-1) [] [.separator] clean)
  | succ e =>
    constructor
    · simp [rewinding, TapeData.write, TapeData.leftward]
    · simpa [rewinding,TapeData.cell,TapeData.write,TapeData.leftward,List.replicate_succ] using
        (view_trailing_blank (e:ℤ) (List.replicate e .blank ++ [.separator]) [.blank] clean).trans
          (view_blank (e:ℤ) (List.replicate e .blank ++ [.separator]) clean)

theorem rewind_end : Physical (rewinding 0) (.separator,.right) (atEnd 0 [.separator] clean) := by
  exact physical_right _ _

end MultitapeToolkit.Absolute.ParkStack

namespace MultitapeToolkit.Absolute.ParkStack
open MultitapeToolkit.Locality MarkedStreams
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

theorem push_copy (s p : ι) (hne : s ≠ p) (bits : List Bool) (erased : ℕ)
    (h : ℤ) (left : List Symbol) (past : ℤ → Symbol)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) :
    Runs (pushProgram s p) (bits.length+1)
      (bank2 s p .copy (reading erased bits) (atEnd h left past) heads cells)
      (bank2 s p .rewind (rewinding (erased+bits.length))
        (atEnd (h+bits.length+1) (.separator::(bits.reverse.map .bit ++ left)) past) heads cells) := by
  induction bits generalizing erased h left with
  | nil =>
    simpa using Runs.cons
      (bank2_step (pushProgram s p) s p hne .copy .rewind
        (reading erased []) (atEnd h left past) (rewinding erased)
        (atEnd (h+1) (.separator::left) past) heads cells
        (.blank,.left) (.separator,.right)
        (by simp [pushProgram, bank2]) (start_rewind erased)
        (append_symbol h left past .separator)) (Runs.refl _)
  | cons b bits ih =>
    have hs := bank2_step (pushProgram s p) s p hne .copy .copy
      (reading erased (b::bits)) (atEnd h left past) (reading (erased+1) bits)
      (atEnd (h+1) (.bit b::left) past) heads cells
      (.blank,.right) (.bit b,.right)
      (by simp [pushProgram, bank2]) (read_bit erased b bits)
      (append_symbol h left past (.bit b))
    have hr := Runs.cons hs (ih (erased+1) (h+1) (.bit b::left))
    simpa [List.reverse_cons, List.map_append, List.append_assoc,
      Nat.add_assoc, Nat.add_comm, Nat.add_left_comm, add_assoc, add_comm,
      add_left_comm] using hr

theorem push_rewind (s p : ι) (hne : s ≠ p) (n : ℕ) (park : TapeData)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) :
    Runs (pushProgram s p) (n+1)
      (bank2 s p .rewind (rewinding n) park heads cells)
      (bank2 s p .done (atEnd 0 [.separator] clean) park heads cells) := by
  induction n with
  | zero =>
    exact Runs.cons (bank2_step (pushProgram s p) s p hne .rewind .done
      (rewinding 0) park (atEnd 0 [.separator] clean) park heads cells
      (.separator,.right) (park.read,.stay)
      (by simp [pushProgram, bank2, Ne.symm hne]) rewind_end
      (physical_stay park)) (Runs.refl _)
  | succ n ih =>
    exact Runs.cons (bank2_step (pushProgram s p) s p hne .rewind .rewind
      (rewinding (n+1)) park (rewinding n) park heads cells
      (.blank,.left) (park.read,.stay)
      (by simp [pushProgram, bank2, Ne.symm hne]) (rewind_blank n)
      (physical_stay park)) ih

/-- Empty top at h, marker h-1, arbitrary cells strictly below its marker. -/
def parkBase (h : ℤ) (past : ℤ → Symbol) : ℤ → Symbol :=
  cellView h [.separator] [] past

/-- A concrete pushed frame, with bits in forward absolute order. -/
def parkRecord (bits : List Bool) (h : ℤ) (past : ℤ → Symbol) : ℤ → Symbol :=
  cellView (h+bits.length+1) (.separator::(bits.reverse.map .bit ++ [.separator])) [] past

def pushInput (s p : ι) (bits : List Bool) (h : ℤ) (past : ℤ → Symbol)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) : Config ι Symbol PushPhase :=
  bank2 s p .copy (reading 0 bits) (atEnd h [.separator] past) heads cells

def pushFinal (s p : ι) (bits : List Bool) (h : ℤ) (past : ℤ → Symbol)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) : Config ι Symbol PushPhase :=
  bank2 s p .done (atEnd 0 [.separator] clean)
    (atEnd (h+bits.length+1) (.separator::(bits.reverse.map .bit ++ [.separator])) past)
    heads cells

/-- Universal exact physical execution of retained push: includes empty input. -/
theorem push_correct (s p : ι) (hne : s ≠ p) (bits : List Bool)
    (h : ℤ) (past : ℤ → Symbol) (heads : ι → ℤ) (cells : ι → ℤ → Symbol) :
    Runs (pushProgram s p) (2*bits.length+2)
      (pushInput s p bits h past heads cells) (pushFinal s p bits h past heads cells) := by
  have hc := push_copy s p hne bits 0 h [.separator] past heads cells
  simp only [Nat.zero_add] at hc
  have hr := push_rewind s p hne bits.length
    (atEnd (h+bits.length+1) (.separator::(bits.reverse.map .bit ++ [.separator])) past)
    heads cells
  have ht := Trace.runs_trans (pushProgram s p) hc hr
  have hn : bits.length+1+(bits.length+1) = 2*bits.length+2 := by omega
  simpa only [hn, pushInput, pushFinal] using ht

@[simp] theorem pushFinal_halts (s p : ι) (bits : List Bool) (h : ℤ)
    (past : ℤ → Symbol) (heads : ι → ℤ) (cells : ι → ℤ → Symbol) :
    Halts (pushProgram s p) (pushFinal s p bits h past heads cells) := by
  simp [Halts, step, pushProgram, pushFinal, bank2]

end MultitapeToolkit.Absolute.ParkStack
namespace MultitapeToolkit.Absolute.ParkStack
open MultitapeToolkit.Locality MarkedStreams
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

def bank3 {Q : Type*} (s t p : ι) (q : Q) (out tmp park : TapeData)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) : Config ι Symbol Q :=
  bank2 s p q out park (fun i => if i=t then tmp.head else heads i)
    (fun i => if i=t then tmp.cell else cells i)

def actions3 (s t p : ι) (a b c : Symbol × Move) (scanned : ι → Symbol) :
    ι → Symbol × Move :=
  fun i => if i=s then a else if i=p then c else if i=t then b else (scanned i,.stay)

end MultitapeToolkit.Absolute.ParkStack


namespace MultitapeToolkit.Absolute.ParkStack
open MultitapeToolkit.Locality MarkedStreams
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

theorem bank3_step {Q : Type*} [Fintype Q] (P : Program ι Symbol Q)
    (s t p : ι) (hst : s ≠ t) (hsp : s ≠ p) (htp : t ≠ p)
    (q q' : Q) (out tmp park out' tmp' park' : TapeData)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) (a b c : Symbol × Move)
    (htable : P.transition q
      (fun i => (bank3 s t p q out tmp park heads cells).cell i
        ((bank3 s t p q out tmp park heads cells).head i)) =
      some (q',actions3 s t p a b c
        (fun i => (bank3 s t p q out tmp park heads cells).cell i
          ((bank3 s t p q out tmp park heads cells).head i))))
    (ho : Physical out a out') (ht : Physical tmp b tmp') (hp : Physical park c park') :
    step P (bank3 s t p q out tmp park heads cells) =
      some (bank3 s t p q' out' tmp' park' heads cells) := by
  have hq : (bank3 s t p q out tmp park heads cells).state = q := rfl
  simp only [step,hq,htable,Option.map_some]
  congr 1
  apply Config.ext
  · rfl
  · funext i
    by_cases hs : i=s
    · subst i; simpa [bank3, bank2, actions3] using ho.1.symm
    · by_cases hpp : i=p
      · subst i; simpa [bank3, bank2, actions3, Ne.symm hsp] using hp.1.symm
      · by_cases htt : i=t
        · subst i; simpa [bank3,bank2,actions3,Ne.symm hst,htp] using ht.1.symm
        · simp [bank3,bank2,actions3,hs,hpp,htt,moveOffset]
  · funext i x
    by_cases hs : i=s
    · subst i; simpa [bank3, bank2, actions3] using congrFun ho.2.symm x
    · by_cases hpp : i=p
      · subst i; simpa [bank3,bank2,actions3,Ne.symm hsp] using congrFun hp.2.symm x
      · by_cases htt : i=t
        · subst i; simpa [bank3,bank2,actions3,Ne.symm hst,htp] using congrFun ht.2.symm x
        · by_cases hx : x=heads i <;> simp [bank3,bank2,actions3,hs,hpp,htt,hx]

inductive PopPhase where
  | enterDelimiter | enterPayload | copyPark | copyOutput | rewindOutput | done
  deriving DecidableEq, Repr

instance : Fintype PopPhase :=
  ⟨{.enterDelimiter,.enterPayload,.copyPark,.copyOutput,.rewindOutput,.done},
    by intro q; cases q <;> simp⟩

/-- The retained six-state table, now with a true halt and literal local actions. -/
def popProgram (s t p : ι) : Program ι Symbol PopPhase where
  transition q r := match q with
  | .done => none
  | .enterDelimiter => some (.enterPayload, actions3 s t p (r s,.stay) (r t,.stay) (r p,.left) r)
  | .enterPayload => some (.copyPark, actions3 s t p (r s,.stay) (r t,.stay) (.blank,.left) r)
  | .copyPark => match r p with
    | .bit b => some (.copyPark,actions3 s t p (r s,.stay) (.bit b,.right) (.blank,.left) r)
    | .separator => some (.copyOutput,actions3 s t p (r s,.stay) (r t,.left) (.separator,.right) r)
    | .blank => some (.done,actions3 s t p (r s,.stay) (r t,.stay) (r p,.stay) r)
  | .copyOutput => match r t with
    | .bit b => some (.copyOutput,actions3 s t p (.bit b,.right) (.blank,.left) (r p,.stay) r)
    | .separator => some (.rewindOutput,actions3 s t p (r s,.left) (.separator,.right) (r p,.stay) r)
    | .blank => some (.done,actions3 s t p (r s,.stay) (r t,.stay) (r p,.stay) r)
  | .rewindOutput => match r s with
    | .bit b => some (.rewindOutput,actions3 s t p (.bit b,.left) (r t,.stay) (r p,.stay) r)
    | .separator => some (.done,actions3 s t p (.separator,.right) (r t,.stay) (r p,.stay) r)
    | .blank => some (.done,actions3 s t p (r s,.stay) (r t,.stay) (r p,.stay) r)

/-- Nearest-first remaining payload ending at the marker of base. -/
def popReady (bits : List Bool) (base : ℤ) (past : ℤ → Symbol) : TapeData :=
  match bits with
  | [] => ⟨base-1,[],[.separator],past⟩
  | b::rest => ⟨base+rest.length,rest.map .bit ++ [.separator],[.bit b],past⟩

def rewindReady (bits : List Bool) (right : List Symbol) : TapeData :=
  match bits with
  | [] => ⟨-1,[],.separator::right,clean⟩
  | b::rest => ⟨rest.length,rest.map .bit ++ [.separator],.bit b::right,clean⟩

@[simp] theorem popReady_nil_read (h : ℤ) (p : ℤ → Symbol) : (popReady [] h p).read = .separator := rfl
@[simp] theorem popReady_cons_read (b : Bool) (bs : List Bool) (h : ℤ) (p : ℤ → Symbol) :
    (popReady (b::bs) h p).read = .bit b := rfl
@[simp] theorem rewindReady_nil_read (r : List Symbol) : (rewindReady [] r).read = .separator := rfl
@[simp] theorem rewindReady_cons_read (b : Bool) (bs : List Bool) (r : List Symbol) :
    (rewindReady (b::bs) r).read = .bit b := rfl

theorem erase_pop (b : Bool) (rest : List Bool) (base : ℤ) (past : ℤ → Symbol) :
    Physical (popReady (b::rest) base past) (.blank,.left) (popReady rest base past) := by
  have h := physical_left (popReady (b::rest) base past) .blank (by simp [popReady])
  apply h.congr
  cases rest with
  | nil =>
    constructor
    · simp [popReady,TapeData.write,TapeData.leftward]
    · simpa [popReady,TapeData.cell,TapeData.write,TapeData.leftward] using
        (view_trailing_blank (base-1) [] [.separator] past)
  | cons b' rest =>
    constructor
    · simp [popReady,TapeData.write,TapeData.leftward,add_assoc,add_sub_assoc]
    · simpa [popReady,TapeData.cell,TapeData.write,TapeData.leftward,add_assoc,add_sub_assoc] using
        (view_trailing_blank (base+rest.length) (rest.map .bit ++ [.separator]) [.bit b'] past)
theorem separator_return (base : ℤ) (past : ℤ → Symbol) :
    Physical (popReady [] base past) (.separator,.right) (atEnd base [.separator] past) := by
  convert physical_right (popReady [] base past) .separator using 1 <;>
    simp [popReady,atEnd,TapeData.write,TapeData.rightward,TapeData.read]

theorem enter_bits (bits : List Bool) (base : ℤ) (past : ℤ → Symbol) :
    Physical (atEnd (base+bits.length) (bits.map .bit ++ [.separator]) past)
      (.blank,.left) (popReady bits base past) := by
  have h := physical_left
    (atEnd (base+bits.length) (bits.map .bit ++ [.separator]) past) .blank (by simp [atEnd])
  apply h.congr
  cases bits with
  | nil =>
    constructor
    · simp [atEnd,popReady,TapeData.write,TapeData.leftward]
    · simpa [atEnd,popReady,TapeData.write,TapeData.leftward,TapeData.cell] using
        (view_trailing_blank (base-1) [] [.separator] past)
  | cons b bits =>
    constructor
    · simp [atEnd,popReady,TapeData.write,TapeData.leftward,add_assoc,add_sub_assoc]
    · simpa [atEnd,popReady,TapeData.write,TapeData.leftward,TapeData.cell,add_assoc,add_sub_assoc] using
        (view_trailing_blank (base+bits.length) (bits.map .bit ++ [.separator]) [.bit b] past)
theorem pop_to_rewind (bits : List Bool) : popReady bits 0 clean = rewindReady bits [] := by
  cases bits <;> simp [popReady,rewindReady]

theorem rewind_bit (b : Bool) (rest : List Bool) (right : List Symbol) :
    Physical (rewindReady (b::rest) right) (.bit b,.left)
      (rewindReady rest (.bit b::right)) := by
  have h := physical_left (rewindReady (b::rest) right) (.bit b) (by simp [rewindReady])
  apply h.congr
  cases rest <;> constructor <;>
    simp [rewindReady,TapeData.write,TapeData.leftward,TapeData.cell]

theorem rewind_separator (right : List Symbol) :
    Physical (rewindReady [] right) (.separator,.right) ⟨0,[.separator],right,clean⟩ := by
  exact physical_right _ _

end MultitapeToolkit.Absolute.ParkStack
namespace MultitapeToolkit.Absolute.ParkStack
open MultitapeToolkit.Locality MarkedStreams
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

theorem pop_copy_park (s t p : ι) (hst : s ≠ t) (hsp : s ≠ p) (htp : t ≠ p)
    (bits acc : List Bool) (base : ℤ) (past : ℤ → Symbol) (out : TapeData)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) :
    Runs (popProgram s t p) (bits.length+1)
      (bank3 s t p .copyPark out (atEnd acc.length (acc.map .bit ++ [.separator]) clean)
        (popReady bits base past) heads cells)
      (bank3 s t p .copyOutput out (popReady (bits.reverse++acc) 0 clean)
        (atEnd base [.separator] past) heads cells) := by
  induction bits generalizing acc with
  | nil =>
    have ht := enter_bits acc 0 clean
    simp only [zero_add] at ht
    simpa using Runs.cons
      (bank3_step (popProgram s t p) s t p hst hsp htp .copyPark .copyOutput
        out (atEnd acc.length (acc.map .bit ++ [.separator]) clean) (popReady [] base past)
        out (popReady acc 0 clean) (atEnd base [.separator] past) heads cells
        (out.read,.stay) (.blank,.left) (.separator,.right)
        (by simp [popProgram,bank3,bank2,htp,Ne.symm hst,Ne.symm hsp])
        (physical_stay out) ht (separator_return base past)) (Runs.refl _)
  | cons b bits ih =>
    have ht := append_symbol (acc.length : ℤ) (acc.map .bit ++ [.separator]) clean (.bit b)
    have hs := bank3_step (popProgram s t p) s t p hst hsp htp .copyPark .copyPark
      out (atEnd acc.length (acc.map .bit ++ [.separator]) clean) (popReady (b::bits) base past)
      out (atEnd (acc.length+1) (.bit b::(acc.map .bit ++ [.separator])) clean)
      (popReady bits base past) heads cells
      (out.read,.stay) (.bit b,.right) (.blank,.left)
      (by simp [popProgram,bank3,bank2,Ne.symm hsp])
      (physical_stay out) ht (erase_pop b bits base past)
    have hr := Runs.cons hs (by simpa using ih (b::acc))
    simpa [List.reverse_cons,List.append_assoc] using hr

theorem pop_copy_output (s t p : ι) (hst : s ≠ t) (hsp : s ≠ p) (htp : t ≠ p)
    (bits acc : List Bool) (park : TapeData)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) :
    Runs (popProgram s t p) (bits.length+1)
      (bank3 s t p .copyOutput (atEnd acc.length (acc.map .bit ++ [.separator]) clean)
        (popReady bits 0 clean) park heads cells)
      (bank3 s t p .rewindOutput (rewindReady (bits.reverse++acc) [])
        (atEnd 0 [.separator] clean) park heads cells) := by
  induction bits generalizing acc with
  | nil =>
    have ho := enter_bits acc 0 clean
    simp only [zero_add] at ho
    rw [pop_to_rewind] at ho
    simpa using Runs.cons
      (bank3_step (popProgram s t p) s t p hst hsp htp .copyOutput .rewindOutput
        (atEnd acc.length (acc.map .bit ++ [.separator]) clean) (popReady [] 0 clean) park
        (rewindReady acc []) (atEnd 0 [.separator] clean) park heads cells
        (.blank,.left) (.separator,.right) (park.read,.stay)
        (by simp [popProgram,bank3,bank2,htp,Ne.symm hst,Ne.symm hsp])
        ho (separator_return 0 clean) (physical_stay park)) (Runs.refl _)
  | cons b bits ih =>
    have ho := append_symbol (acc.length : ℤ) (acc.map .bit ++ [.separator]) clean (.bit b)
    have hs := bank3_step (popProgram s t p) s t p hst hsp htp .copyOutput .copyOutput
      (atEnd acc.length (acc.map .bit ++ [.separator]) clean) (popReady (b::bits) 0 clean) park
      (atEnd (acc.length+1) (.bit b::(acc.map .bit ++ [.separator])) clean)
      (popReady bits 0 clean) park heads cells
      (.bit b,.right) (.blank,.left) (park.read,.stay)
      (by simp [popProgram,bank3,bank2,htp,Ne.symm hst,Ne.symm hsp])
      ho (erase_pop b bits 0 clean) (physical_stay park)
    have hr := Runs.cons hs (by simpa using ih (b::acc))
    simpa [List.reverse_cons,List.append_assoc] using hr

theorem pop_rewind_output (s t p : ι) (hst : s ≠ t) (hsp : s ≠ p) (htp : t ≠ p)
    (bits : List Bool) (right : List Symbol) (tmp park : TapeData)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) :
    Runs (popProgram s t p) (bits.length+1)
      (bank3 s t p .rewindOutput (rewindReady bits right) tmp park heads cells)
      (bank3 s t p .done ⟨0,[.separator],bits.reverse.map .bit ++ right,clean⟩ tmp park heads cells) := by
  induction bits generalizing right with
  | nil =>
    simpa using Runs.cons
      (bank3_step (popProgram s t p) s t p hst hsp htp .rewindOutput .done
        (rewindReady [] right) tmp park ⟨0,[.separator],right,clean⟩ tmp park heads cells
        (.separator,.right) (tmp.read,.stay) (park.read,.stay)
        (by simp [popProgram,bank3,bank2,htp,Ne.symm hst,Ne.symm hsp])
        (rewind_separator right) (physical_stay tmp) (physical_stay park)) (Runs.refl _)
  | cons b bits ih =>
    have hs := bank3_step (popProgram s t p) s t p hst hsp htp .rewindOutput .rewindOutput
      (rewindReady (b::bits) right) tmp park (rewindReady bits (.bit b::right)) tmp park heads cells
      (.bit b,.left) (tmp.read,.stay) (park.read,.stay)
      (by simp [popProgram,bank3,bank2,htp,Ne.symm hst,Ne.symm hsp])
      (rewind_bit b bits right) (physical_stay tmp) (physical_stay park)
    simpa [List.reverse_cons,List.map_append,List.append_assoc] using Runs.cons hs (ih (.bit b::right))

def popInput (s t p : ι) (bits : List Bool) (base : ℤ) (past : ℤ → Symbol)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) : Config ι Symbol PopPhase :=
  bank3 s t p .enterDelimiter (atEnd 0 [.separator] clean) (atEnd 0 [.separator] clean)
    (atEnd (base+bits.length+1) (.separator::(bits.reverse.map .bit ++ [.separator])) past) heads cells

def popFinal (s t p : ι) (bits : List Bool) (base : ℤ) (past : ℤ → Symbol)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) : Config ι Symbol PopPhase :=
  bank3 s t p .done (reading 0 bits) (atEnd 0 [.separator] clean)
    (atEnd base [.separator] past) heads cells

theorem pop_enter_parked (s t p : ι) (hst : s ≠ t) (hsp : s ≠ p) (htp : t ≠ p)
    (bits : List Bool) (base : ℤ) (past : ℤ → Symbol)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) :
    Runs (popProgram s t p) 2 (popInput s t p bits base past heads cells)
      (bank3 s t p .copyPark (atEnd 0 [.separator] clean) (atEnd 0 [.separator] clean)
        (popReady bits.reverse base past) heads cells) := by
  let mid : TapeData := ⟨base+bits.length,bits.reverse.map .bit ++ [.separator],[.separator],past⟩
  have hp1 : Physical
      (atEnd (base+bits.length+1) (.separator::(bits.reverse.map .bit ++ [.separator])) past)
      (.blank,.left) mid := by
    apply (physical_left _ .blank (by simp [atEnd])).congr
    constructor
    · simp [mid,atEnd,TapeData.write,TapeData.leftward]
    · simpa [mid,atEnd,TapeData.write,TapeData.leftward,TapeData.cell,add_assoc,add_sub_assoc] using
        (view_trailing_blank (base+bits.length) (bits.reverse.map .bit ++ [.separator]) [.separator] past)
  have hp2 : Physical mid (.blank,.left) (popReady bits.reverse base past) := by
    have he : SameTape (mid.write .blank)
        (atEnd (base+bits.reverse.length) (bits.reverse.map .bit ++ [.separator]) past) := by
      constructor
      · simp [mid,atEnd]
      · simp [mid,atEnd,TapeData.write,TapeData.cell,view_blank]
    have hl : mid.left ≠ [] := by simp [mid]
    have hp := physical_left mid .blank hl
    have henter := enter_bits bits.reverse base past
    constructor
    · simpa [mid,atEnd] using henter.1
    · have hh : (atEnd (base+bits.reverse.length) (bits.reverse.map .bit ++ [.separator]) past).head = mid.head := by simp [mid,atEnd]
      exact henter.2.trans (by
        rw [hh,←he.2,TapeData.write_cell]
        funext x
        by_cases hx : x=mid.head <;> simp [hx])
  have hs1 := bank3_step (popProgram s t p) s t p hst hsp htp .enterDelimiter .enterPayload
    (atEnd 0 [.separator] clean) (atEnd 0 [.separator] clean)
    (atEnd (base+bits.length+1) (.separator::(bits.reverse.map .bit ++ [.separator])) past)
    (atEnd 0 [.separator] clean) (atEnd 0 [.separator] clean) mid heads cells
    (.blank,.stay) (.blank,.stay) (.blank,.left)
    (by simp [popProgram,bank3,bank2,htp,Ne.symm hst,Ne.symm hsp])
    (physical_stay _) (physical_stay _) hp1
  have hs2 := bank3_step (popProgram s t p) s t p hst hsp htp .enterPayload .copyPark
    (atEnd 0 [.separator] clean) (atEnd 0 [.separator] clean) mid
    (atEnd 0 [.separator] clean) (atEnd 0 [.separator] clean)
    (popReady bits.reverse base past) heads cells
    (.blank,.stay) (.blank,.stay) (.blank,.left)
    (by simp [popProgram,bank3,bank2,htp,Ne.symm hst])
    (physical_stay _) (physical_stay _) hp2
  exact Runs.cons hs1 (Runs.cons hs2 (Runs.refl _))

theorem pop_correct (s t p : ι) (hst : s ≠ t) (hsp : s ≠ p) (htp : t ≠ p)
    (bits : List Bool) (base : ℤ) (past : ℤ → Symbol)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) :
    Runs (popProgram s t p) (3*bits.length+5)
      (popInput s t p bits base past heads cells) (popFinal s t p bits base past heads cells) := by
  have he := pop_enter_parked s t p hst hsp htp bits base past heads cells
  have hc := pop_copy_park s t p hst hsp htp bits.reverse [] base past
    (atEnd 0 [.separator] clean) heads cells
  simp only [List.length_reverse,List.map_nil,List.nil_append,List.reverse_reverse,List.append_nil] at hc
  have ho := pop_copy_output s t p hst hsp htp bits [] (atEnd base [.separator] past) heads cells
  simp only [List.map_nil,List.nil_append,List.append_nil] at ho
  have hr := pop_rewind_output s t p hst hsp htp bits.reverse []
    (atEnd 0 [.separator] clean) (atEnd base [.separator] past) heads cells
  simp only [List.length_reverse,List.reverse_reverse,List.append_nil] at hr
  have ht := Trace.runs_trans (popProgram s t p)
    (Trace.runs_trans (popProgram s t p) (Trace.runs_trans (popProgram s t p) he hc) ho) hr
  have hn : 2+(bits.length+1)+(bits.length+1)+(bits.length+1) = 3*bits.length+5 := by omega
  simpa [hn,popFinal,reading] using ht

@[simp] theorem popFinal_halts (s t p : ι) (bits : List Bool) (base : ℤ)
    (past : ℤ → Symbol) (heads : ι → ℤ) (cells : ι → ℤ → Symbol) :
    Halts (popProgram s t p) (popFinal s t p bits base past heads cells) := by
  simp [Halts,step,popProgram,popFinal,bank3,bank2]

end MultitapeToolkit.Absolute.ParkStack


namespace MultitapeToolkit.Absolute.ParkStack
open MarkedStreams
@[simp] theorem push_state_card : Fintype.card PushPhase = 3 := by decide
@[simp] theorem pop_state_card : Fintype.card PopPhase = 6 := by decide
end MultitapeToolkit.Absolute.ParkStack



namespace MultitapeToolkit.Absolute.ParkStack
open MarkedStreams

theorem parkBase_past (base : ℤ) (past : ℤ → Symbol) (x : ℤ) (hx : x < base-1) :
    parkBase base past x = past x := by
  have hh : x < base := by omega
  have hi : ¬ (base-x-1).toNat < 1 := by omega
  simp only [parkBase,cellView,if_pos hh,List.length_singleton,if_neg hi]

theorem parkRecord_past (bits : List Bool) (base : ℤ) (past : ℤ → Symbol)
    (x : ℤ) (hx : x < base-1) : parkRecord bits base past x = past x := by
  have hh : x < base+bits.length+1 := by omega
  have hi : ¬ (base+bits.length+1-x-1).toNat < bits.length+2 := by omega
  have hlen : (.separator::(bits.reverse.map Symbol.bit ++ [.separator])).length = bits.length+2 := by simp
  simp only [parkRecord,cellView,if_pos hh,hlen,if_neg hi]

end MultitapeToolkit.Absolute.ParkStack




namespace MultitapeToolkit.Absolute.ParkStack
open MarkedStreams
@[simp] theorem reading_zero_cell (bits : List Bool) : (reading 0 bits).cell = word bits := rfl
@[simp] theorem empty_cell : (atEnd 0 [.separator] clean).cell = word [] := rfl
@[simp] theorem base_cell (base : ℤ) (past : ℤ → Symbol) :
    (atEnd base [.separator] past).cell = parkBase base past := rfl
@[simp] theorem record_cell (bits : List Bool) (base : ℤ) (past : ℤ → Symbol) :
    (atEnd (base+bits.length+1) (.separator::(bits.reverse.map .bit ++ [.separator])) past).cell =
      parkRecord bits base past := rfl
end MultitapeToolkit.Absolute.ParkStack


