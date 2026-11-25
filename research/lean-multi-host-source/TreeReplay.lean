import LinearReplay

/-!
An executable binary register store with the same linear semantics as
`LinearReplay`. Low bits of a register index choose successive branches.
The source certificate uses a full tree of depth 10 and verifies every
access is below 988; no out-of-range index is thereby allowed to alias a
physical register. The generic reflection result itself is shape-agnostic.
-/
namespace TreeReplay
open LinearReplay (Event evalRow evalRow_zero evalRow_xor)
universe u v

inductive Tree (α : Type u) where
  | leaf : α → Tree α
  | node : Tree α → Tree α → Tree α
  deriving DecidableEq

namespace Tree

def get : Tree α → Nat → α
  | .leaf a, _ => a
  | .node l r, i => if i % 2 == 0 then l.get (i / 2) else r.get (i / 2)

def put : Tree α → Nat → α → Tree α
  | .leaf _, _, a => .leaf a
  | .node l r, i, a =>
    if i % 2 == 0 then .node (l.put (i / 2) a) r else .node l (r.put (i / 2) a)

def map (f : α → β) : Tree α → Tree β
  | .leaf a => .leaf (f a)
  | .node l r => .node (l.map f) (r.map f)

theorem map_get (f : α → β) (s : Tree α) (i : Nat) :
    (s.map f).get i = f (s.get i) := by
  induction s generalizing i with
  | leaf a => rfl
  | node l r ihl ihr =>
      simp only [get, map]
      split <;> simp_all

theorem map_put (f : α → β) (s : Tree α) (i : Nat) (a : α) :
    (s.put i a).map f = (s.map f).put i (f a) := by
  induction s generalizing i with
  | leaf b => rfl
  | node l r ihl ihr =>
      simp only [put, map]
      split <;> simp_all [map]

theorem map_map (f : α → β) (g : β → γ) (s : Tree α) :
    (s.map f).map g = s.map (g ∘ f) := by
  induction s with
  | leaf a => rfl
  | node l r ihl ihr => simp [map, ihl, ihr]

/-- Full binary store; the least significant index bit chooses the root branch. -/
def tabulate : Nat → (Nat → α) → Tree α
  | 0, f => .leaf (f 0)
  | d + 1, f => .node (tabulate d (fun i => f (2 * i)))
      (tabulate d (fun i => f (2 * i + 1)))

theorem map_tabulate (f : α → β) (d : Nat) (g : Nat → α) :
    (tabulate d g).map f = tabulate d (f ∘ g) := by
  induction d generalizing g with
  | zero => rfl
  | succ d ih => simp [tabulate, map, ih, Function.comp_def]

theorem get_tabulate (d : Nat) (f : Nat → α) (i : Nat) (h : i < 2 ^ d) :
    (tabulate d f).get i = f i := by
  induction d generalizing f i with
  | zero =>
      have hi : i = 0 := by simp at h; omega
      subst i; rfl
  | succ d ih =>
      have hdiv : i / 2 < 2 ^ d := by
        rw [Nat.pow_succ] at h
        omega
      simp only [tabulate, get]
      split
      · rw [ih _ _ hdiv]
        congr 1
        rename_i hz
        have hm : i % 2 = 0 := by simpa using hz
        omega
      · rw [ih _ _ hdiv]
        congr 1
        rename_i hz
        have hm : i % 2 ≠ 0 := by simpa using hz
        omega

def Full : Nat → Tree α → Prop
  | 0, .leaf _ => True
  | d + 1, .node l r => Full d l ∧ Full d r
  | _, _ => False

theorem full_tabulate (d : Nat) (f : Nat → α) : Full d (tabulate d f) := by
  induction d generalizing f with
  | zero => trivial
  | succ d ih => exact ⟨ih _, ih _⟩

theorem full_put (d : Nat) (s : Tree α) (h : Full d s) (i : Nat) (a : α) :
    Full d (s.put i a) := by
  induction d generalizing s i with
  | zero => cases s <;> simp_all [Full, put]
  | succ d ih =>
      cases s with
      | leaf b => cases h
      | node l r =>
          simp only [put]
          split <;> exact ⟨by first | exact ih _ h.1 _ | exact h.1,
            by first | exact ih _ h.2 _ | exact h.2⟩

/-- Within a full store, an update changes exactly the selected register. -/
theorem get_put (d : Nat) (s : Tree α) (h : Full d s) (i j : Nat) (a : α)
    (hi : i < 2 ^ d) (hj : j < 2 ^ d) :
    (s.put i a).get j = if i = j then a else s.get j := by
  induction d generalizing s i j with
  | zero =>
      have hi0 : i = 0 := by simp at hi; omega
      have hj0 : j = 0 := by simp at hj; omega
      subst i; subst j
      cases s <;> simp_all [Full, put, get]
  | succ d ih =>
      cases s with
      | leaf b => cases h
      | node l r =>
          have hid : i / 2 < 2 ^ d := by rw [Nat.pow_succ] at hi; omega
          have hjd : j / 2 < 2 ^ d := by rw [Nat.pow_succ] at hj; omega
          by_cases hip : i % 2 = 0 <;> by_cases hjp : j % 2 = 0
          · simp only [put, get, hip, hjp, beq_self_eq_true, ite_true]
            rw [ih l h.1 _ _ hid hjd]
            have heq : (i / 2 = j / 2) ↔ i = j := by omega
            simp only [heq]
          · have hij : i ≠ j := by omega
            simp [put, get, hip, hjp, hij]
          · have hij : i ≠ j := by omega
            simp [put, get, hip, hjp, hij]
          · simp only [put, get, beq_iff_eq, hip, hjp, ↓reduceIte]
            rw [ih r h.2 _ _ hid hjd]
            have heq : (i / 2 = j / 2) ↔ i = j := by omega
            simp only [heq]

end Tree

def step (zero : α) (xor : α → α → α) (s : Tree α) (e : Event) : Tree α :=
  match e.op with
  | 0 => s
  | 1 => if e.odd then s.put e.x (xor (s.get e.x) (s.get e.y)) else s
  | 2 => s.put e.y (s.get e.x)
  | _ => s.put e.y zero

def run (zero : α) (xor : α → α → α) (es : List Event) (s : Tree α) : Tree α :=
  es.foldl (step zero xor) s

def rowStep := step (0 : Nat) (· ^^^ ·)
def boolStep := step false (· ^^ ·)
def runRows := run (0 : Nat) (· ^^^ ·)
def runBools := run false (· ^^ ·)

def rowChecks (s : Tree Nat) (e : Event) : Bool :=
  match e.op with
  | 0 => e.x < 987
  | 1 => e.x < 987 && e.y <= 987 && e.x != e.y
  | 2 => e.x < 987 && e.y == 987 && s.get e.y == 0
  | 3 => e.x < 987 && e.y == 987 && s.get e.x == s.get e.y
  | _ => false

def checkedRowStep (s : Tree Nat × Bool) (e : Event) : Tree Nat × Bool :=
  (rowStep s.1 e, s.2 && rowChecks s.1 e)

def runCheckedRows (es : List Event) (s : Tree Nat × Bool) : Tree Nat × Bool :=
  es.foldl checkedRowStep s

def evalRows (n : Nat) (u : Nat → Bool) (s : Tree Nat) : Tree Bool :=
  s.map (evalRow n u)

theorem step_map (zero : α) (zero' : β) (xor : α → α → α) (xor' : β → β → β)
    (f : α → β) (hzero : f zero = zero')
    (hxor : ∀ a b, f (xor a b) = xor' (f a) (f b)) (s : Tree α) (e : Event) :
    (step zero xor s e).map f = step zero' xor' (s.map f) e := by
  obtain ⟨op, x, y, odd⟩ := e
  cases op with
  | zero => rfl
  | succ op =>
      cases op with
      | zero => cases odd <;> simp [step, Tree.map_put, Tree.map_get, hxor]
      | succ op =>
          cases op with
          | zero => simp [step, Tree.map_put, Tree.map_get]
          | succ op => simp [step, Tree.map_put, hzero]

theorem run_map (zero : α) (zero' : β) (xor : α → α → α) (xor' : β → β → β)
    (f : α → β) (hzero : f zero = zero')
    (hxor : ∀ a b, f (xor a b) = xor' (f a) (f b)) (es : List Event) (s : Tree α) :
    (run zero xor es s).map f = run zero' xor' es (s.map f) := by
  induction es generalizing s with
  | nil => rfl
  | cons e es ih =>
      change (run zero xor es (step zero xor s e)).map f =
        run zero' xor' es (step zero' xor' (s.map f) e)
      rw [ih, step_map zero zero' xor xor' f hzero hxor]

theorem evalRows_step (n : Nat) (u : Nat → Bool) (s : Tree Nat) (e : Event) :
    evalRows n u (rowStep s e) = boolStep (evalRows n u s) e := by
  exact step_map 0 false (· ^^^ ·) (· ^^ ·) (evalRow n u)
    (evalRow_zero n u) (evalRow_xor n u) s e

theorem evalRows_run (n : Nat) (u : Nat → Bool) (es : List Event) (s : Tree Nat) :
    evalRows n u (runRows es s) = runBools es (evalRows n u s) := by
  exact run_map 0 false (· ^^^ ·) (· ^^ ·) (evalRow n u)
    (evalRow_zero n u) (evalRow_xor n u) es s

theorem checked_projection (es : List Event) (s : Tree Nat × Bool) :
    (runCheckedRows es s).1 = runRows es s.1 := by
  induction es generalizing s with
  | nil => rfl
  | cons e es ih => exact ih (checkedRowStep s e)

def boolChecks (s : Tree Bool) (e : Event) : Bool :=
  match e.op with
  | 0 => e.x < 987
  | 1 => e.x < 987 && e.y <= 987 && e.x != e.y
  | 2 => e.x < 987 && e.y == 987 && !(s.get e.y)
  | 3 => e.x < 987 && e.y == 987 && s.get e.x == s.get e.y
  | _ => false

def checkedBoolStep (s : Tree Bool × Bool) (e : Event) : Tree Bool × Bool :=
  (boolStep s.1 e, s.2 && boolChecks s.1 e)

def runCheckedBools (es : List Event) (s : Tree Bool × Bool) : Tree Bool × Bool :=
  es.foldl checkedBoolStep s

theorem evalRows_get (n : Nat) (u : Nat → Bool) (s : Tree Nat) (i : Nat) :
    (evalRows n u s).get i = evalRow n u (s.get i) := Tree.map_get _ _ _

theorem checks_sound (n : Nat) (u : Nat → Bool) (s : Tree Nat) (e : Event)
    (h : rowChecks s e = true) : boolChecks (evalRows n u s) e = true := by
  obtain ⟨op, x, y, odd⟩ := e
  cases op with
  | zero => exact h
  | succ op =>
      cases op with
      | zero => exact h
      | succ op =>
          cases op with
          | zero =>
              simp only [rowChecks, Bool.and_eq_true, beq_iff_eq] at h
              simp only [boolChecks, Bool.and_eq_true, beq_iff_eq, evalRows_get]
              exact ⟨h.1, by simp [h.2]⟩
          | succ op =>
              cases op with
              | zero =>
                  simp only [rowChecks, Bool.and_eq_true, beq_iff_eq] at h
                  simp only [boolChecks, Bool.and_eq_true, beq_iff_eq, evalRows_get]
                  exact ⟨h.1, congrArg (evalRow n u) h.2⟩
              | succ op => cases h

theorem checked_flag_mono (es : List Event) (s : Tree Nat × Bool)
    (h : (runCheckedRows es s).2 = true) : s.2 = true := by
  induction es generalizing s with
  | nil => exact h
  | cons e es ih =>
      have h' := ih (checkedRowStep s e) h
      exact (Bool.and_eq_true_iff.mp h').1

theorem checked_guards_sound (n : Nat) (u : Nat → Bool) (es : List Event)
    (s : Tree Nat × Bool) (h : (runCheckedRows es s).2 = true) :
    (runCheckedBools es (evalRows n u s.1, s.2)).2 = true := by
  induction es generalizing s with
  | nil => exact h
  | cons e es ih =>
      have hfirst := checked_flag_mono es (checkedRowStep s e) h
      have hparts := Bool.and_eq_true_iff.mp hfirst
      have hb := checks_sound n u s.1 e hparts.2
      have hi := ih (checkedRowStep s e) h
      simpa only [runCheckedBools, List.foldl_cons, checkedBoolStep,
        evalRows_step, checkedRowStep, hparts.1, hparts.2, hb] using hi

def basisRows (depth n : Nat) : Tree Nat :=
  Tree.tabulate depth fun i => if i < n then 1 <<< i else 0

def dirtyInput (depth n : Nat) (u : Nat → Bool) : Tree Bool :=
  Tree.tabulate depth fun i => if i < n then u i else false

theorem evalRows_basisRows (depth n : Nat) (u : Nat → Bool) :
    evalRows n u (basisRows depth n) = dirtyInput depth n u := by
  simp only [evalRows, basisRows, dirtyInput, Tree.map_tabulate]
  congr 1
  funext i
  by_cases h : i < n <;> simp [h, LinearReplay.evalRow_shift_basis]

theorem dirtyInput_get (depth n : Nat) (u : Nat → Bool) (i : Nat)
    (h : i < 2 ^ depth) :
    (dirtyInput depth n u).get i = if i < n then u i else false :=
  Tree.get_tabulate _ _ _ h

/-- Interpret rows as entire arbitrary Boolean payloads, without restricting
their dependence on one another or on an address of any type. -/
def evalPayloadRows {X : Type v} (n : Nat) (u : Nat → X → Bool) (s : Tree Nat) : Tree (X → Bool) :=
  s.map fun row address => evalRow n (fun i => u i address) row

def runPayloads {X : Type v} (es : List Event) (s : Tree (X → Bool)) : Tree (X → Bool) :=
  run (fun _ => false) (fun a b x => a x ^^ b x) es s

theorem evalPayloadRows_run {X : Type v} (n : Nat) (u : Nat → X → Bool) (es : List Event) (s : Tree Nat) :
    evalPayloadRows n u (runRows es s) = runPayloads es (evalPayloadRows n u s) := by
  apply run_map 0 (fun _ => false) (· ^^^ ·) (fun a b x => a x ^^ b x)
  · funext x
    exact evalRow_zero n (fun i => u i x)
  · intro a b
    funext x
    exact evalRow_xor n (fun i => u i x) a b

theorem evalPayloadRows_basisRows {X : Type v} (depth n : Nat) (u : Nat → X → Bool) :
    evalPayloadRows n u (basisRows depth n) =
      Tree.tabulate depth (fun i => if i < n then u i else fun _ => false) := by
  simp only [evalPayloadRows, basisRows, Tree.map_tabulate]
  congr 1
  funext i address
  by_cases h : i < n <;> simp [h, LinearReplay.evalRow_shift_basis]

end TreeReplay
