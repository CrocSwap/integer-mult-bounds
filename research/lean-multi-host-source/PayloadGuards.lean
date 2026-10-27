import TreeReplay

/-!
Transport the symbolic copy/erase preconditions to whole arbitrary dirty
payloads at every point in the normalized run. Equality here is equality
of entire functions, not merely a check at one address.
-/
namespace TreeReplay
open LinearReplay (Event evalRow evalRow_zero)

def PayloadClean {X : Type u} (s : Tree (X → Bool)) (e : Event) : Prop :=
  (e.op = 2 → s.get e.y = fun _ => false) ∧
  (e.op = 3 → s.get e.x = s.get e.y)

def PayloadCleanRun {X : Type u} : List Event → Tree (X → Bool) → Prop
  | [], _ => True
  | e :: es, s => PayloadClean s e ∧
      PayloadCleanRun es (step (fun _ => false) (fun a b x => a x ^^ b x) s e)

theorem payload_checks_sound {X : Type u} (n : Nat) (input : Nat → X → Bool)
    (s : Tree Nat) (e : Event) (h : rowChecks s e = true) :
    PayloadClean (evalPayloadRows n input s) e := by
  constructor
  · intro hop
    have hy : s.get e.y = 0 := by
      simp only [rowChecks, hop, Bool.and_eq_true, beq_iff_eq] at h
      exact h.2
    apply funext
    intro x
    change ((s.map (fun row x => evalRow n (fun i => input i x) row)).get e.y) x = false
    rw [Tree.map_get, hy]
    exact evalRow_zero n (fun i => input i x)
  · intro hop
    have hxy : s.get e.x = s.get e.y := by
      simp only [rowChecks, hop, Bool.and_eq_true, beq_iff_eq] at h
      exact h.2
    change (s.map _).get e.x = (s.map _).get e.y
    rw [Tree.map_get, Tree.map_get, hxy]

theorem checked_payload_guards_sound {X : Type u} (n : Nat) (input : Nat → X → Bool)
    (es : List Event) (s : Tree Nat × Bool) (h : (runCheckedRows es s).2 = true) :
    PayloadCleanRun es (evalPayloadRows n input s.1) := by
  induction es generalizing s with
  | nil => trivial
  | cons e es ih =>
      have hfirst := checked_flag_mono es (checkedRowStep s e) h
      have hparts := Bool.and_eq_true_iff.mp hfirst
      constructor
      · exact payload_checks_sound n input s.1 e hparts.2
      · have hi := ih (checkedRowStep s e) h
        have hstep : evalPayloadRows n input (rowStep s.1 e) =
            step (fun _ => false) (fun a b x => a x ^^ b x) (evalPayloadRows n input s.1) e := by
          apply step_map 0 (fun _ => false) (· ^^^ ·) (fun a b x => a x ^^ b x)
          · funext x; exact evalRow_zero n (fun i => input i x)
          · intro a b; funext x; exact LinearReplay.evalRow_xor n (fun i => input i x) a b
        simpa only [checkedRowStep, hstep] using hi

end TreeReplay
