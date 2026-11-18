/-
LEAN-PREM4, Nov 17. E1-E3 of the owned_erasure contract as a DECIDABLE check on the owned-event
skeleton, run (kernel `decide`) on the actual skeleton of the on7623 word (180 lifetimes).
See OwnedSkeleton.md.  Data: OwnedSkeletonData.lean (generated, ownedskel_gen/gen.py).
-/
import Nov15.ClearCert
import Nov15.OwnedSkeletonData

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace OwnedSkeleton
open TokenCancel

abbrev E := Ev ℚ ℕ ℕ

/-- Owned fields are the word registers 1501..1568 (68 labels). -/
def base : ℕ := 1501
def labels : ℕ := 68
def calls : ℕ := 17

/-! ## Charts: GF(2) spans, proper nesting (check.py:104 `sp[a] < sp[b] or sp[b] < sp[a]`) -/

def spanL (gs : List ℕ) : List ℕ := gs.foldl (fun s g => s ++ s.map (· ^^^ g)) [0]

def spanOf (c : ℕ) : Option (List ℕ) := (chartGens.lookup c).map spanL

def subL (a b : List ℕ) : Bool := a.all fun x => b.contains x

/-- charts `a`,`b` are properly nested one way or the other (both must be in the chart table). -/
def nested (a b : ℕ) : Bool :=
  match spanOf a, spanOf b with
  | some sa, some sb => (subL sa sb && !subL sb sa) || (subL sb sa && !subL sa sb)
  | _, _ => false

/-! ## E1/E2: bank discipline (explicit INIT, retained until CLEAR, erased, bounded by the label set) -/

/-- Liveness simulation: INIT only a dead field, MOVE/CLEAR only a live one (the bank is retained
until its unit clears it). Only owned INIT/MOVE/CLEAR events occur in a skeleton. -/
def e1run : List ℕ → List E → Option (List ℕ)
  | l, [] => some l
  | l, .init i _ :: es => if l.contains i then none else e1run (i :: l) es
  | l, .move i _ :: es => if l.contains i then e1run l es else none
  | l, .clear i _ :: es => if l.contains i then e1run (l.erase i) es else none
  | _, _ :: _ => none

/-- E1: explicit init, no overlapping reuse of a name, everything erased at the end. -/
def E1 (es : List E) : Prop := e1run [] es = some []

def evField : E → ℕ
  | .init i _ => i | .move i _ => i | .clear i _ => i | _ => 0

/-- Peak number of simultaneously live owned banks. -/
def peakAux : List ℕ → ℕ → List E → ℕ
  | _, p, [] => p
  | l, p, .init i _ :: es => peakAux (i :: l) (max p (l.length + 1)) es
  | l, p, .clear i _ :: es => peakAux (l.erase i) p es
  | l, p, _ :: es => peakAux l p es

def peak (es : List E) : ℕ := peakAux [] 0 es

/-- E2 (allocation): every field is one of the 68 labels and the peak fits the label set, so one
bank per label per call (17 x 68 = 1,156) retains each lifetime (the reuse lifetime proof). -/
def E2 (es : List E) : Prop := (∀ e ∈ es, base ≤ evField e ∧ evField e < base + labels) ∧ peak es ≤ labels

/-! ## E3: field identity / chronology: MOVE leaves the current chart (nested), CLEAR at current chart -/

def e3run : List (ℕ × ℕ) → List E → Bool
  | l, [] => l.isEmpty
  | l, .init i c :: es => (l.lookup i).isNone && e3run ((i, c) :: l) es
  | l, .move i b :: es =>
      match l.lookup i with
      | some a => nested a b && e3run ((i, b) :: l.filter (·.1 ≠ i)) es
      | none => false
  | l, .clear i c :: es =>
      match l.lookup i with
      | some a => a == c && e3run (l.filter (·.1 ≠ i)) es
      | none => false
  | _, _ :: _ => false

/-- E3 (field identity + chronology on the flat word): MOVE starts at the field's current chart and
is properly nested; CLEAR is at the current chart; nothing is left live. The parent/child half
("parent erases only after the entire child unit completed") needs the unit tree, which a flat
word does not carry: not expressible here. -/
def E3 (es : List E) : Prop := e3run [] es = true

/-- The decidable owned-event-skeleton predicate: E1-E3. -/
def Sk (es : List E) : Prop := E1 es ∧ E2 es ∧ E3 es

instance (es : List E) : Decidable (E1 es) := inferInstanceAs (Decidable (_ = _))
instance (es : List E) : Decidable (E2 es) := inferInstanceAs (Decidable (_ ∧ _))
instance (es : List E) : Decidable (E3 es) := inferInstanceAs (Decidable (_ = _))
instance (es : List E) : Decidable (Sk es) := inferInstanceAs (Decidable (_ ∧ _))

/-! ## The skeleton of the on7623 word, checked in the kernel -/

theorem e1_skel : E1 skel := by decide +kernel
theorem e2_skel : E2 skel := by decide +kernel
theorem e3_skel : E3 skel := by decide +kernel
theorem sk_skel : Sk skel := ⟨e1_skel, e2_skel, e3_skel⟩

/-! ## Counting facts -/

def cnt (p : E → Bool) (es : List E) : ℕ := (es.filter p).length
def isInit : E → Bool | .init .. => true | _ => false
def isMove : E → Bool | .move .. => true | _ => false
def isClear : E → Bool | .clear .. => true | _ => false
def initLabels (es : List E) : List ℕ := (es.filter isInit).map evField |>.eraseDups

theorem n_events : skel.length = 407 := by decide +kernel
theorem n_lifetimes : cnt isInit skel = 180 := by decide +kernel
theorem n_clears : cnt isClear skel = 180 := by decide +kernel
theorem n_moves : cnt isMove skel = 47 := by decide +kernel
theorem n_labels : (initLabels skel).length = 68 := by decide +kernel
theorem peak_skel : peak skel = 50 := by decide +kernel
theorem bank_count : calls * labels = 1156 := by decide
theorem peak_le : peak skel ≤ labels := by rw [peak_skel]; decide
theorem lifetimes_exceed_labels : labels < cnt isInit skel := by rw [n_lifetimes]; decide
/-- total lifetimes over the 17 calls vs the fixed 1,156 banks: reuse is real, so the disjointness
proof (E1: INIT only of a dead field) is exactly E2's "smaller reuse allocation needs its own
lifetime proof". -/
theorem total_lifetimes : calls * cnt isInit skel = 3060 := by rw [n_lifetimes]; decide

/-! ## Negative controls: the checker rejects -/

def c0 : List E := [.init 1501 3, .clear 1501 3]
theorem c0_ok : Sk c0 := by decide +kernel
theorem c_double_init : ¬ Sk [.init 1501 3, .init 1501 3, .clear 1501 3] := by decide +kernel
theorem c_leak : ¬ Sk [.init 1501 3] := by decide +kernel
theorem c_clear_dead : ¬ Sk [.clear 1501 3] := by decide +kernel
theorem c_wrong_chart : ¬ Sk [.init 1501 3, .clear 1501 115] := by decide +kernel
theorem c_label_range : ¬ Sk [.init 1569 3, .clear 1569 3] := by decide +kernel
/-- skeleton with one MOVE to a non-nested chart (115 vs 117 are incomparable) is rejected. -/
theorem c_not_nested : ¬ Sk [.init 1501 115, .move 1501 117, .clear 1501 117] := by decide +kernel
theorem c_peak : ¬ E2 ((List.range 69).map (fun i => (Ev.init (1501 + i) 3 : E))) := by decide +kernel
/-- dropping the last event of the real skeleton leaks a bank. -/
theorem c_skel_truncated : ¬ Sk skel.dropLast := by decide +kernel

/-! ## Link to ClearCert: `Sk` is now a fact for this word, so ErasureOK reduces to losslessness -/

def owned (f : ℕ) : Prop := base ≤ f

theorem erasure_ok_iff {K : Type*} [Field K] {C : Type*} [DecidableEq C]
    {Reg : Type*} [DecidableEq Reg] (Skg : List (Ev K Reg C) → Prop) (own : Reg → Prop)
    (s : St K Reg C) (es : List (Ev K Reg C)) (h : Skg (ClearCert.ownedEvents own es)) :
    ClearCert.ErasureOK Skg own s es ↔ ClearCert.AllLossless s es :=
  ⟨fun h => h.2, fun h' => ⟨h, h'⟩⟩

/-- For any endpoint-exact word over ℚ-rows (with Nat registers and Nat charts) whose owned
events are exactly the on7623 skeleton, `owned_erasure`'s E1-E3 half and its content half both hold. -/
theorem erasure_ok_on_skel (U : Submodule ℚ (ℕ → ℚ)) (s : St ℚ ℕ ℕ) (es : List (Ev ℚ ℕ ℕ))
    (hU : ClearCert.rowSpan s ≤ U) (hnb : ∀ e ∈ es, ClearCert.NoBorn e)
    (hend : ClearCert.FullEnd U s es)
    (hsk : ClearCert.ownedEvents owned es = skel) :
    ClearCert.ErasureOK Sk owned s es := by
  refine ⟨by rw [hsk]; exact sk_skel, ?_⟩
  exact fun pre post i c h => ClearCert.every_clear_lossless U s es hU hnb hend pre post i c h

#print axioms sk_skel
#print axioms n_events
#print axioms n_lifetimes
#print axioms n_clears
#print axioms n_moves
#print axioms n_labels
#print axioms peak_skel
#print axioms bank_count
#print axioms total_lifetimes
#print axioms c_not_nested
#print axioms c_skel_truncated
#print axioms c_peak
#print axioms erasure_ok_on_skel

end OwnedSkeleton
