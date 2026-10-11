import SignedTraceCore

namespace CurrentMain.SignedTrace
open Lean.Grind CurrentMain.SignedWord

def leavesCheck (p : α → Bool) : Table α → Bool
  | .leaf x => p x
  | .fork l r => leavesCheck p l && leavesCheck p r

theorem leavesCheck_get (p : α → Bool) (t : Table α)
    (h : leavesCheck p t = true) (i : Nat) : p (get t i) = true := by
  induction t generalizing i with
  | leaf x => exact h
  | fork l r hl hr =>
    have hh := Bool.and_eq_true_iff.mp h
    simp only [get]
    split
    · exact hl hh.1 _
    · exact hr hh.2 _

variable {F : Type u} [Ring F]

def sourceInjection (start : Table Nat) (payload : Nat → F) : State F :=
  fun i => if get start i = 0 then 0 else payload (get start i - 1)

/-- The start table is an exact source-injection map. Every nonzero label is an
input index plus one; zero labels receive zero. Its concrete table is source-bound. -/
theorem sourceInjection_sound (start : Table Nat) (width : Nat)
    (hbound : leavesCheck (fun n => decide (n ≤ width)) start = true)
    (value payload : Nat → F) (hz : value 0 = 0)
    (hin : ∀ j, j < width → value (j+1) = payload j) (i : Nat) :
    value (get start i) = sourceInjection start payload i := by
  have hn : get start i ≤ width := of_decide_eq_true (leavesCheck_get _ start hbound i)
  by_cases hzero : get start i = 0
  · simp [sourceInjection, hzero, hz]
  · have hp : 0 < get start i := by omega
    have hlt : get start i - 1 < width := by omega
    have hid : get start i - 1 + 1 = get start i := by omega
    simpa only [sourceInjection, if_neg hzero, hid] using hin (get start i - 1) hlt

structure RootBinding where
  rootIndex : Nat
  role : Nat
  node : Nat
  deriving DecidableEq, Repr

def rootCheck (depth : Nat) (finish : Table Nat) (r : RootBinding) : Bool :=
  decide (r.role < 2^depth ∧ get finish r.role = r.node)

theorem certificate_root_value (depth : Nat) (width : Nat) (node : Graph)
    (start finish : Table Nat) (annotations : List Annotation)
    (hc : Certificate depth node start finish annotations)
    (hbound : leavesCheck (fun n => decide (n ≤ width)) start = true)
    (r : RootBinding) (hr : rootCheck depth finish r = true)
    (value payload : Nat → F) (hz : value 0 = 0)
    (hin : ∀ j, j < width → value (j+1) = payload j)
    (ha : ∀ n l q neg, node n = .add l q neg → value n = value l + signed neg (value q)) :
    run (annotations.map Annotation.step) (sourceInjection start payload) r.role = value r.node := by
  have hroot : r.role < 2^depth ∧ get finish r.role = r.node := of_decide_eq_true hr
  have he := certificate_sound depth node start finish annotations hc value
    (sourceInjection start payload) hz ha
    (fun i _ => sourceInjection_sound start width hbound value payload hz hin i)
    r.role hroot.1
  rw [hroot.2] at he
  exact he.symm

end CurrentMain.SignedTrace
#print axioms CurrentMain.SignedTrace.leavesCheck_get
#print axioms CurrentMain.SignedTrace.sourceInjection_sound
#print axioms CurrentMain.SignedTrace.certificate_root_value
