import MultitapeToolkit.MarkedStreams
import Mathlib.Data.List.GetD

/-!
# Proof cursors for the actual Bool-stack/origin serializer

The native machine alphabet is Option Bool. Existing four-symbol tape cursors
are used only as finite descriptions in proofs: both their separator and blank
map to the actual blank None. No marker or word list enters machine control.
-/
set_option autoImplicit false
namespace MultitapeToolkit.Absolute.StackOriginSerializer
open MultitapeToolkit.Locality MarkedStreams Turing

inductive Phase where
  | enter | scan | copyReverse | rewind | done
  deriving DecidableEq
instance : Fintype Phase :=
  ⟨{.enter,.scan,.copyReverse,.rewind,.done}, by intro q; cases q <;> simp⟩

/-- Explicit encoding; ghost separators are actual blank cells. -/
def toBool : Symbol → Option Bool
  | .bit b => some b
  | _ => none

def encodedCell (offset : ℤ) (t : TapeData) (x : ℤ) : Option Bool :=
  toBool (t.cell (x-offset))

@[simp] theorem encodedCell_read (offset : ℤ) (t : TapeData) :
    encodedCell offset t (offset+t.head) = toBool t.read := by
  simp [encodedCell,TapeData.cell_read]

/-- Encoding and translating a genuine local action preserves its exact cost. -/
theorem encoded_physical {t u : TapeData} {a : Symbol × Move}
    (hp : Physical t a u) (offset : ℤ) :
    offset+u.head = offset+t.head+moveOffset a.2 ∧
    encodedCell offset u = fun x =>
      if x=offset+t.head then toBool a.1 else encodedCell offset t x := by
  constructor
  · rw [hp.1]; omega
  · funext x
    simp only [encodedCell,hp.2]
    by_cases hx : x=offset+t.head
    · have hy : x-offset=t.head := by omega
      simp [hx,hy]
    · have hy : x-offset≠t.head := by omega
      simp [hx,hy]

variable {ι : Type*} [Fintype ι] [DecidableEq ι]

def bank (s d : ι) (q : Phase) (offset : ℤ) (src dst : TapeData)
    (heads : ι → ℤ) (cells : ι → ℤ → Option Bool) : Config ι (Option Bool) Phase :=
  ⟨q,fun i => if i=s then offset+src.head else if i=d then dst.head else heads i,
    fun i => if i=s then encodedCell offset src else if i=d then encodedCell 0 dst else cells i⟩

def encodedActions (s d : ι) (a b : Symbol × Move) (r : ι → Option Bool) :
    ι → Option Bool × Move :=
  fun i => if i=s then (toBool a.1,a.2) else if i=d then (toBool b.1,b.2) else (r i,.stay)

theorem bank_step (P : Program ι (Option Bool) Phase) (s d : ι) (hne : s≠d)
    (q q' : Phase) (offset : ℤ) (t u t' u' : TapeData)
    (heads : ι → ℤ) (cells : ι → ℤ → Option Bool) (a b : Symbol × Move)
    (htable : P.transition q
      (fun i => (bank s d q offset t u heads cells).cell i ((bank s d q offset t u heads cells).head i)) =
      some (q',encodedActions s d a b
        (fun i => (bank s d q offset t u heads cells).cell i ((bank s d q offset t u heads cells).head i))))
    (ht : Physical t a t') (hu : Physical u b u') :
    step P (bank s d q offset t u heads cells) = some (bank s d q' offset t' u' heads cells) := by
  have htt := encoded_physical ht offset
  have huu := encoded_physical hu 0
  change P.transition (bank s d q offset t u heads cells).state _ = _ at htable
  simp only [step,htable,Option.map_some]
  congr 1
  apply Config.ext
  · rfl
  · funext i
    by_cases hs : i=s
    · subst i; simpa [bank,encodedActions] using htt.1.symm
    · by_cases hd : i=d
      · subst i; simpa [bank,encodedActions,hne,Ne.symm hne] using huu.1.symm
      · simp [bank,encodedActions,hs,hd,moveOffset]
  · funext i x
    by_cases hs : i=s
    · subst i; simpa [bank,encodedActions] using congrFun htt.2.symm x
    · by_cases hd : i=d
      · subst i; simpa [bank,encodedActions,hne,Ne.symm hne] using congrFun huu.2.symm x
      · by_cases hx : x=heads i <;> simp [bank,encodedActions,hs,hd,hx]

/-- Origin-anchored native Bool word, with blanks at every exterior coordinate. -/
def originWord (bits : List Bool) (x : ℤ) : Option Bool :=
  if 0≤x then bits[x.toNat]? else none

/-- The actual compiler representation, located at the supplied physical head. -/
def sourceStack (h : ℤ) (bits : List Bool) : ℤ → Option Bool :=
  absoluteCell (stackTape bits) h

@[simp] theorem sourceStack_eq_absoluteCell (h : ℤ) (bits : List Bool) :
    sourceStack h bits = absoluteCell (stackTape bits) h := rfl

def clean : ℤ → Symbol := fun _ => .blank

def sourceInitial (bits : List Bool) : TapeData :=
  ⟨-1,[],.separator::bits.map .bit,clean⟩

@[simp] theorem map_bit_getD (bits : List Bool) (n : ℕ) :
    toBool ((bits.map .bit).getD n .blank) = bits[n]? := by
  simp only [List.getD_eq_getElem?_getD,List.getElem?_map]
  cases bits[n]? <;> rfl

/-- The shifted proof cursor is exactly the compiler tape representation. -/
theorem sourceInitial_abi (h : ℤ) (bits : List Bool) :
    encodedCell (h+1) (sourceInitial bits) = sourceStack h bits := by
  funext x
  simp only [encodedCell,sourceInitial,TapeData.cell,sourceStack,absoluteCell]
  have hc : x-(h+1) = (x-h)-1 := by omega
  rw [hc]
  generalize x-h = z
  cases z with
  | ofNat n =>
    cases n with
    | zero => simp [cellView,toBool,clean,stackTape,Tape.nth]
    | succ n =>
      have hn : ¬ (n : ℤ)< -1 := by omega
      simp [cellView,toBool,clean,stackTape,Tape.nth,ListBlank.nth_mk,hn,
        List.getD_eq_getElem?_getD,List.getI_eq_getElem?_getD,List.getElem?_map]
      cases bits[n]? <;> rfl
  | negSucc n =>
    have hn : Int.negSucc (n+1)< -1 := by omega
    simp [cellView,toBool,clean,stackTape,Tape.nth,ListBlank.nth_mk,hn]
    rfl

/-- Actual origin anchoring: no separator cell remains in the native alphabet. -/
theorem streamTape_origin (bits : List Bool) :
    encodedCell 0 (streamTape bits clean) = originWord bits := by
  funext x
  cases x with
  | ofNat n =>
    have hn : ¬ (n : ℤ)<0 := by omega
    simp [encodedCell,streamTape,TapeData.cell,cellView,originWord,hn]
    cases bits[n]? <;> rfl
  | negSucc n =>
    cases n <;> simp [encodedCell,streamTape,TapeData.cell,cellView,originWord,toBool,clean]

end MultitapeToolkit.Absolute.StackOriginSerializer



