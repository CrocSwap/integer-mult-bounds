import Std

/-! Scalar cleanup commutation and checked recipe-order extraction.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
No frame, compiler, asymptotic or multiplication-theorem claims.
-/
namespace CleanupPrefix

class Scalar (α : Type) extends Add α, Mul α where
  add_assoc : ∀ a b c : α, (a + b) + c = a + (b + c)
  add_comm : ∀ a b : α, a + b = b + a

inductive Shape where
  | add (target source : Nat)
  | scale (target : Nat)
  deriving DecidableEq, Repr

def target : Shape → Nat
  | .add t _ => t
  | .scale t => t

def touches : Shape → Nat → Bool
  | .add t s, r => r == t || r == s
  | .scale t, r => r == t

/-- Exactly the two branches of build_hpe.py's `commute`, including self-adds. -/
def commute (a b : Shape) : Bool :=
  (!touches b (target a) && !touches a (target b)) ||
  match a, b with
  | .add t s, .add u v => t == u && s != u && v != t
  | _, _ => false

def disjoint (a b : Shape) : Bool :=
  match a with
  | .scale t => !touches b t
  | .add t s => !touches b t && !touches b s

abbrev State (α : Type) := Nat → α

def put (σ : State α) (t : Nat) (v : α) : State α :=
  fun r => if r = t then v else σ r

def eval [Scalar α] (g : Shape) (q : α) (σ : State α) : State α :=
  match g with
  | .add t s => put σ t (σ t + q * σ s)
  | .scale t => put σ t (q * σ t)

theorem commute_sound [Scalar α] (a b : Shape) (p q : α)
    (h : commute a b = true) (σ : State α) :
    eval b q (eval a p σ) = eval a p (eval b q σ) := by
  cases a with
  | scale t =>
    cases b with
    | scale u =>
      simp [commute, touches, target] at h
      funext r
      simp only [eval, put]
      by_cases rt : r = t <;> by_cases ru : r = u <;> simp_all [Ne.symm]
    | add u v =>
      simp [commute, touches, target] at h
      funext r
      simp only [eval, put]
      by_cases rt : r = t <;> by_cases ru : r = u <;> simp_all [Ne.symm]
  | add t s =>
    cases b with
    | scale u =>
      simp [commute, touches, target] at h
      funext r
      simp only [eval, put]
      by_cases rt : r = t <;> by_cases ru : r = u <;> simp_all [Ne.symm]
    | add u v =>
      simp [commute, touches, target] at h
      rcases h with h | h
      · funext r
        simp only [eval, put]
        by_cases rt : r = t <;> by_cases ru : r = u <;> simp_all [Ne.symm]
      · obtain ⟨⟨h, hs⟩, hv⟩ := h
        subst u
        funext r
        simp only [eval, put]
        by_cases rt : r = t
        · simp only [rt, ↓reduceIte]
          simp only [hs, hv, ↓reduceIte]
          rw [Scalar.add_assoc, Scalar.add_assoc,
            Scalar.add_comm (p * σ s) (q * σ v)]
        · simp [rt]

/-- Untouched pairs are the vacuous cases of Python's overlap-only scan. -/
theorem disjoint_commute (a b : Shape) (h : disjoint a b = true) :
    commute a b = true := by
  cases a <;> cases b <;> simp_all [disjoint, commute, touches, target, Ne.symm]

structure Instruction where
  index : Nat
  shape : Shape
  deriving DecidableEq, Repr

def run [Scalar α] (coeff : Nat → α) : List Instruction → State α → State α
  | [], σ => σ
  | g :: gs, σ => run coeff gs (eval g.shape (coeff g.index) σ)

theorem run_append [Scalar α] (coeff : Nat → α) (xs ys : List Instruction) (σ : State α) :
    run coeff (xs ++ ys) σ = run coeff ys (run coeff xs σ) := by
  induction xs generalizing σ with
  | nil => rfl
  | cons x xs ih => exact ih _

/-- A selected gate can cross every skipped gate, in its original order. -/
theorem cross_prefix [Scalar α] (coeff : Nat → α) (g : Instruction)
    (xs : List Instruction) (h : ∀ x ∈ xs, commute x.shape g.shape = true)
    (σ : State α) :
    eval g.shape (coeff g.index) (run coeff xs σ) =
      run coeff xs (eval g.shape (coeff g.index) σ) := by
  induction xs generalizing σ with
  | nil => rfl
  | cons x xs ih =>
    simp only [run]
    rw [ih (fun y hy => h y (List.mem_cons_of_mem x hy)),
      commute_sound x.shape g.shape (coeff x.index) (coeff g.index)
        (h x (List.mem_cons_self))]

/-- Locate an original index, checking the entire skipped prefix, then remove it.
This is deliberately coefficient-independent; no finite state testing is used. -/
def pull (i : Nat) : List Instruction → Option (Instruction × List Instruction)
  | [] => none
  | x :: xs =>
    if x.index = i then some (x, xs)
    else match pull i xs with
    | none => none
    | some (g, rest) =>
      if commute x.shape g.shape then some (g, x :: rest) else none

theorem pull_sound [Scalar α] (coeff : Nat → α) (i : Nat)
    (xs : List Instruction) (g : Instruction) (rest : List Instruction)
    (h : pull i xs = some (g, rest)) (σ : State α) :
    run coeff xs σ = run coeff (g :: rest) σ := by
  induction xs generalizing g rest σ with
  | nil => simp [pull] at h
  | cons x xs ih =>
    simp only [pull] at h
    split at h
    · cases h; rfl
    · cases hp : pull i xs with
      | none => simp [hp] at h
      | some pair =>
        obtain ⟨y, ys⟩ := pair
        simp only [hp] at h
        split at h
        · rename_i hc
          cases h
          simp only [run]
          rw [ih g ys hp]
          simp only [run]
          rw [commute_sound x.shape g.shape (coeff x.index) (coeff g.index) hc]
        · simp at h

/-- Pull neither sorts nor changes gates: it removes one indexed instruction. -/
theorem pull_split (i : Nat) (xs : List Instruction) (g : Instruction)
    (rest : List Instruction) (h : pull i xs = some (g, rest)) :
    g.index = i ∧ ∃ pre post, xs = pre ++ g :: post ∧
      rest = pre ++ post ∧ ∀ x ∈ pre, commute x.shape g.shape = true := by
  induction xs generalizing g rest with
  | nil => simp [pull] at h
  | cons x xs ih =>
    simp only [pull] at h
    split at h
    · rename_i hi
      cases h
      exact ⟨hi, [], xs, rfl, rfl, by simp⟩
    · cases hp : pull i xs with
      | none => simp [hp] at h
      | some pair =>
        obtain ⟨y, ys⟩ := pair
        simp only [hp] at h
        split at h
        · rename_i hc
          cases h
          obtain ⟨hi, pre, post, heq, hr, hall⟩ := ih g ys hp
          refine ⟨hi, x :: pre, post, ?_, ?_, ?_⟩
          · simp [heq]
          · simp [hr]
          · intro z hz
            rcases List.mem_cons.mp hz with hz | hz
            · subst z; exact hc
            · exact hall z hz
        · simp at h

/-- The output is selected gates in recipe order followed by the stable remainder.
Selected gates must have disjoint register sets, as in Python's `seen` guard. -/
def extract : List Nat → List Instruction → Option (List Instruction × List Instruction)
  | [], xs => some ([], xs)
  | i :: is, xs =>
    match pull i xs with
    | none => none
    | some (g, rest) =>
      match extract is rest with
      | none => none
      | some (selected, tail) =>
        if selected.all (fun x => disjoint g.shape x.shape) then
          some (g :: selected, tail)
        else none

theorem extract_sound [Scalar α] (coeff : Nat → α) (recipe : List Nat)
    (xs selected tail : List Instruction)
    (h : extract recipe xs = some (selected, tail)) (σ : State α) :
    run coeff xs σ = run coeff (selected ++ tail) σ := by
  induction recipe generalizing xs selected tail σ with
  | nil => simp [extract] at h; obtain ⟨rfl, rfl⟩ := h; rfl
  | cons i is ih =>
    simp only [extract] at h
    cases hp : pull i xs with
    | none => simp [hp] at h
    | some pair =>
      obtain ⟨g, rest⟩ := pair
      simp only [hp] at h
      cases he : extract is rest with
      | none => simp [he] at h
      | some pair =>
        obtain ⟨gs, ts⟩ := pair
        simp only [he] at h
        split at h
        · cases h
          rw [pull_sound coeff i xs g rest hp]
          simp only [run, List.cons_append]
          exact ih rest gs tail he _
        · simp at h

/-- In particular the selected prefix follows the recipe, not sorted indices. -/
theorem extract_recipe_order (recipe : List Nat) (xs selected tail : List Instruction)
    (h : extract recipe xs = some (selected, tail)) :
    selected.map Instruction.index = recipe := by
  induction recipe generalizing xs selected tail with
  | nil => simp [extract] at h; obtain ⟨rfl, rfl⟩ := h; rfl
  | cons i is ih =>
    simp only [extract] at h
    cases hp : pull i xs with
    | none => simp [hp] at h
    | some pair =>
      obtain ⟨g, rest⟩ := pair
      simp only [hp] at h
      cases he : extract is rest with
      | none => simp [he] at h
      | some pair =>
        obtain ⟨gs, ts⟩ := pair
        simp only [he] at h
        split at h
        · cases h
          simp only [List.map_cons, (pull_split i xs g rest hp).1,
            ih rest gs tail he]
        · simp at h

/-- The selected instructions obey the source's pairwise register-disjoint guard. -/
theorem extract_disjoint (recipe : List Nat) (xs selected tail : List Instruction)
    (h : extract recipe xs = some (selected, tail)) :
    selected.Pairwise (fun a b => disjoint a.shape b.shape = true) := by
  induction recipe generalizing xs selected tail with
  | nil => simp [extract] at h; obtain ⟨rfl, rfl⟩ := h; exact .nil
  | cons i is ih =>
    simp only [extract] at h
    cases hp : pull i xs with
    | none => simp [hp] at h
    | some pair =>
      obtain ⟨g, rest⟩ := pair
      simp only [hp] at h
      cases he : extract is rest with
      | none => simp [he] at h
      | some pair =>
        obtain ⟨gs, ts⟩ := pair
        simp only [he] at h
        split at h
        · rename_i hd
          cases h
          apply List.Pairwise.cons
          · exact List.all_eq_true.mp hd
          · exact ih rest gs tail he
        · simp at h

/-- Check full ORIGINAL prefixes as in build_hpe.apply, even for reversed recipes.
The extra checks in extract revalidate the surviving prefixes after deletion. -/
def sourceExtract (recipe : List Nat) (xs : List Instruction) :
    Option (List Instruction × List Instruction) :=
  if recipe.all (fun i => (pull i xs).isSome) then extract recipe xs else none

theorem sourceExtract_sound [Scalar α] (coeff : Nat → α) (recipe : List Nat)
    (xs selected tail : List Instruction)
    (h : sourceExtract recipe xs = some (selected, tail)) (σ : State α) :
    run coeff xs σ = run coeff (selected ++ tail) σ := by
  unfold sourceExtract at h
  split at h
  · exact extract_sound coeff recipe xs selected tail h σ
  · simp at h

/-- Rewrite within any surrounding scalar program, with arbitrary initial dirt. -/
theorem extract_in_context [Scalar α] (coeff : Nat → α) (recipe : List Nat)
    (xs selected tail before after : List Instruction)
    (h : extract recipe xs = some (selected, tail)) (σ : State α) :
    run coeff (before ++ xs ++ after) σ =
      run coeff (before ++ (selected ++ tail) ++ after) σ := by
  simp only [run_append]
  rw [extract_sound coeff recipe xs selected tail h]
  simp only [run_append]

theorem sourceExtract_in_context [Scalar α] (coeff : Nat → α) (recipe : List Nat)
    (xs selected tail before after : List Instruction)
    (h : sourceExtract recipe xs = some (selected, tail)) (σ : State α) :
    run coeff (before ++ xs ++ after) σ =
      run coeff (before ++ (selected ++ tail) ++ after) σ := by
  unfold sourceExtract at h
  split at h
  · exact extract_in_context coeff recipe xs selected tail before after h σ
  · simp at h

/-- Linear-size certificate for an untouched suffix: every selected original
index is below a cut, and every suffix instruction is at or above it. -/
theorem suffix_unselected_of_bounds (recipe : List Nat) (suffix : List Instruction)
    (cut : Nat)
    (hr : recipe.all (fun i => decide (i < cut)) = true)
    (hs : suffix.all (fun g => decide (cut ≤ g.index)) = true) :
    suffix.all (fun g => !recipe.contains g.index) = true := by
  apply List.all_eq_true.mpr
  intro g hg
  have lower : cut ≤ g.index := of_decide_eq_true (List.all_eq_true.mp hs g hg)
  have absent : g.index ∉ recipe := by
    intro hm
    have upper : g.index < cut := of_decide_eq_true (List.all_eq_true.mp hr g.index hm)
    omega
  cases hc : recipe.contains g.index with
  | false => rfl
  | true => exact False.elim (absent (List.contains_iff_mem.mp hc))

/-- A concrete model, used below for genuine noncommutation counterexamples. -/
instance : Scalar Int where
  add := Int.add
  mul := Int.mul
  add_assoc := Int.add_assoc
  add_comm := Int.add_comm

-- Self-adds are allowed by Python's disjoint branch.
example : commute (.add 0 0) (.scale 1) = true := by decide
-- Same-target independent-source additions are the second branch.
example : commute (.add 0 1) (.add 0 2) = true := by decide
-- Read-after-write and same-register add/scale are excluded.
example : commute (.add 0 1) (.add 1 2) = false := by decide
example : commute (.add 0 1) (.scale 0) = false := by decide
example : commute (.add 0 0) (.add 0 1) = false := by decide
example : (eval (.scale 0) (2 : Int) (eval (.add 0 1) 1 (fun _ => 1))) 0 ≠
    (eval (.add 0 1) (1 : Int) (eval (.scale 0) 2 (fun _ => 1))) 0 := by decide

private def demo : List Instruction :=
  [⟨0, .add 0 0⟩, ⟨1, .scale 1⟩, ⟨2, .add 2 3⟩]
-- Unsorted recipe order must be preserved; the remainder is stable.
example : sourceExtract [2, 0] demo =
    some ([⟨2, .add 2 3⟩, ⟨0, .add 0 0⟩], [⟨1, .scale 1⟩]) := by decide
example : sourceExtract [0, 0] demo = none := by decide
example : sourceExtract [4] demo = none := by decide
example : sourceExtract [1] [⟨0, .add 0 1⟩, ⟨1, .scale 0⟩] = none := by decide
-- Even commuting selected gates sharing a register fail Python's seen guard.
example : sourceExtract [1, 0] [⟨0, .add 0 1⟩, ⟨1, .add 0 2⟩] = none := by decide

#print axioms suffix_unselected_of_bounds
#print axioms extract_disjoint
#print axioms sourceExtract_in_context
#print axioms disjoint_commute
#print axioms pull_split
#print axioms extract_recipe_order
#print axioms sourceExtract_sound
#print axioms commute_sound
#print axioms pull_sound
#print axioms extract_sound
#print axioms extract_in_context
end CleanupPrefix
