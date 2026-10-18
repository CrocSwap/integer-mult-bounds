import LemmaG.Stream

namespace LemmaG.TreeCheckpoint

/-- Complete binary label tree. -/
inductive State : Nat → Type where
  | leaf (label : Nat) : State 0
  | node {d : Nat} (left right : State d) : State (d + 1)
  deriving DecidableEq

def get : {d : Nat} → State d → Nat → Nat
  | 0, .leaf v, _ => v
  | _ + 1, .node l r, i => if i % 2 = 0 then get l (i / 2) else get r (i / 2)

def put : {d : Nat} → State d → Nat → Nat → State d
  | 0, .leaf _, _, v => .leaf v
  | _ + 1, .node l r, i, v =>
      if i % 2 = 0 then .node (put l (i / 2) v) r else .node l (put r (i / 2) v)

 theorem get_put {d : Nat} (s : State d) (i j v : Nat)
    (hi : i < 2 ^ d) (hj : j < 2 ^ d) :
    get (put s i v) j = if j = i then v else get s j := by
  induction s generalizing i j with
  | leaf w =>
      have h : j = i := by simp only [Nat.pow_zero] at hi hj; omega
      simp [get, put, h]
  | @node d l r ihl ihr =>
      have hi' : i / 2 < 2 ^ d := by simp only [Nat.pow_succ] at hi; omega
      have hj' : j / 2 < 2 ^ d := by simp only [Nat.pow_succ] at hj; omega
      by_cases pi : i % 2 = 0 <;> by_cases pj : j % 2 = 0
      · have heq : (j / 2 = i / 2) ↔ j = i := by omega
        simp [get, put, pi, pj, ihl (i / 2) (j / 2) hi' hj', heq]
      · have hne : j ≠ i := by omega
        simp [get, put, pi, pj, hne]
      · have hne : j ≠ i := by omega
        simp [get, put, pi, pj, hne]
      · have heq : (j / 2 = i / 2) ↔ j = i := by omega
        simp [get, put, pi, pj, ihr (i / 2) (j / 2) hi' hj', heq]

def view {d : Nat} (s : State d) (r : Fin (2 ^ d)) : Nat := get s r.val

 theorem view_put {d : Nat} (s : State d) (r : Fin (2 ^ d)) (v : Nat) :
    view (put s r.val v) = Function.update (view s) r v := by
  funext i
  simp only [view, get_put s r.val i.val v r.isLt i.isLt, Function.update_apply]
  congr 1
  exact propext Fin.ext_iff.symm

def step {d : Nat} {K : Type*} (e : Event (Fin (2 ^ d)) Nat K) (s : State d) : State d :=
  match e with
  | .relabel r _ B => put s r.val B
  | .copy c _ F => put s c.val F
  | .clear c F => put s c.val F
  | .add .. => s
  | .scale .. => s

def admissible {d : Nat} {K : Type*} (e : Event (Fin (2 ^ d)) Nat K) (s : State d) : Bool :=
  match e with
  | .relabel r A _ => view s r == A
  | .add t r _ => view s t == view s r
  | .copy _ r F => view s r == F
  | .scale .. => true
  | .clear .. => true

 theorem view_step {d : Nat} {K : Type*} (e : Event (Fin (2 ^ d)) Nat K) (s : State d) :
    view (step e s) = e.lab (view s) := by
  cases e <;> simp [step, Event.lab, view_put]

 theorem admissible_iff {d : Nat} {K : Type*} (e : Event (Fin (2 ^ d)) Nat K) (s : State d) :
    admissible e s = true ↔ e.Admissible (view s) := by
  cases e <;> simp [admissible, Event.Admissible]

/-- Execute the existing event labels and reject the first inadmissible event. -/
def check {d : Nat} {K : Type*} : List (Event (Fin (2 ^ d)) Nat K) → State d → Option (State d)
  | [], s => some s
  | e :: es, s => if admissible e s then check es (step e s) else none

 theorem sound {d : Nat} {K : Type*} :
    ∀ (es : List (Event (Fin (2 ^ d)) Nat K)) (s t : State d), check es s = some t →
      Stream.WellLabelled es (view s) ∧ Stream.labRun es (view s) = view t
  | [], s, t, h => by
      simp only [check, Option.some.injEq] at h
      subst t
      exact ⟨True.intro, rfl⟩
  | e :: es, s, t, h => by
      simp only [check] at h
      split at h
      next ha =>
        have ih := sound es (step e s) t h
        rw [view_step] at ih
        exact ⟨⟨(admissible_iff e s).mp ha, ih.1⟩, ih.2⟩
      next ha => contradiction

/-- A finite sequence of checked blocks with shared boundary states. -/
inductive Chain {d : Nat} {K : Type*} :
    State d → State d → List (List (Event (Fin (2 ^ d)) Nat K)) → Prop where
  | nil (s : State d) : Chain s s []
  | cons {s t u : State d} {es : List (Event (Fin (2 ^ d)) Nat K)}
      {ess : List (List (Event (Fin (2 ^ d)) Nat K))}
      (checked : check es s = some t) (rest : Chain t u ess) :
      Chain s u (es :: ess)

 theorem Chain.sound {d : Nat} {K : Type*} {s t : State d}
    {ess : List (List (Event (Fin (2 ^ d)) Nat K))} (h : Chain s t ess) :
    Stream.WellLabelled ess.flatten (view s) ∧
      Stream.labRun ess.flatten (view s) = view t := by
  induction h with
  | nil s => exact ⟨True.intro, rfl⟩
  | @cons s t u es ess checked rest ih =>
      have hs := LemmaG.TreeCheckpoint.sound es s t checked
      simp only [List.flatten_cons]
      constructor
      · rw [Stream.wellLabelled_append]
        exact ⟨hs.1, hs.2 ▸ ih.1⟩
      · rw [Stream.labRun_append, hs.2]
        exact ih.2

end LemmaG.TreeCheckpoint
