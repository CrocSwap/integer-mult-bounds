import Std

/-
Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
Scoped formalization of PR628's reserved-depth dispatcher. PR1278/1294
motivate the four local invariants; neither interval support nor numerical
leaf implementation is proved here. See README.md for the source bridge.
-/

namespace DirtyDispatcher

set_option autoImplicit false

inductive Tree where
  | leaf (factor : Nat)
  | node (left right : Tree)
  deriving Repr, DecidableEq

structure Gate where
  src : Nat
  dst : Nat
  factor : Nat
  positive : Bool
  deriving Repr, DecidableEq

def emit : Tree → Bool → Nat → Nat → Nat → List Gate
  | .leaf f, sign, x, y, _ => [⟨x, y, f, sign⟩]
  | .node l r, true, x, y, d =>
      emit l true x d (d+1) ++ emit r true d y (d+1) ++
      emit l false x d (d+1) ++ emit r false d y (d+1)
  | .node l r, false, x, y, d =>
      emit r true d y (d+1) ++ emit l true x d (d+1) ++
      emit r false d y (d+1) ++ emit l false x d (d+1)

def height : Tree → Nat
  | .leaf _ => 0
  | .node l r => 1 + max (height l) (height r)

/-- Every leaf source is x or a reserved scratch register; every destination
is y or a reserved scratch register. No balancing assumption is needed. -/
theorem emit_ports (t : Tree) (sign : Bool) (x y d : Nat) :
    ∀ g ∈ emit t sign x y d, (g.src = x ∨ d ≤ g.src) ∧ (g.dst = y ∨ d ≤ g.dst) := by
  induction t generalizing sign x y d with
  | leaf f => simp [emit]
  | node l r il ir =>
      have left (s : Bool) (g : Gate) (hg : g ∈ emit l s x d (d+1)) :
          (g.src = x ∨ d ≤ g.src) ∧ (g.dst = y ∨ d ≤ g.dst) := by
        obtain ⟨hs, hd⟩ := il s x d (d+1) g hg
        constructor <;> omega
      have right (s : Bool) (g : Gate) (hg : g ∈ emit r s d y (d+1)) :
          (g.src = x ∨ d ≤ g.src) ∧ (g.dst = y ∨ d ≤ g.dst) := by
        obtain ⟨hs, hd⟩ := ir s d y (d+1) g hg
        constructor <;> omega
      cases sign <;> intro g hg <;> simp only [emit, List.mem_append] at hg
      · rcases hg with ((h | h) | h) | h
        · exact right true g h
        · exact left true g h
        · exact right false g h
        · exact left false g h
      · rcases hg with ((h | h) | h) | h
        · exact left true g h
        · exact right true g h
        · exact left false g h
        · exact right false g h

theorem prefix_ports (t : Tree) (sign : Bool) (x y d k : Nat) :
    ∀ g ∈ (emit t sign x y d).take k,
      (g.src = x ∨ d ≤ g.src) ∧ (g.dst = y ∨ d ≤ g.dst) := by
  intro g hg
  exact emit_ports t sign x y d g (List.mem_of_mem_take hg)

theorem emit_bounded (t : Tree) (sign : Bool) (x y d : Nat)
    (hx : x < d) (hy : y < d) :
    ∀ g ∈ emit t sign x y d, g.src < d + height t ∧ g.dst < d + height t := by
  induction t generalizing sign x y d with
  | leaf f => simp [emit, height, hx, hy]
  | node l r il ir =>
      have hl := Nat.le_max_left (height l) (height r)
      have hr := Nat.le_max_right (height l) (height r)
      have left (s : Bool) (g : Gate) (hg : g ∈ emit l s x d (d+1)) :
          g.src < d + height (.node l r) ∧ g.dst < d + height (.node l r) := by
        obtain ⟨hs, hd⟩ := il s x d (d+1) (by omega) (by omega) g hg
        simp only [height]
        constructor <;> omega
      have right (s : Bool) (g : Gate) (hg : g ∈ emit r s d y (d+1)) :
          g.src < d + height (.node l r) ∧ g.dst < d + height (.node l r) := by
        obtain ⟨hs, hd⟩ := ir s d y (d+1) (by omega) (by omega) g hg
        simp only [height]
        constructor <;> omega
      cases sign <;> intro g hg <;> simp only [emit, List.mem_append] at hg
      · rcases hg with ((h | h) | h) | h
        · exact right true g h
        · exact left true g h
        · exact right false g h
        · exact left false g h
      · rcases hg with ((h | h) | h) | h
        · exact left true g h
        · exact right true g h
        · exact left false g h
        · exact right false g h

variable {V : Type}
abbrev State (V : Type) := Nat → V

/-- Abstract completed leaf shear. op can be nonlinear and sign-dependent.
Its reads are restricted to g.src by this explicit semantic contract. -/
def step (add : V → V → V) (op : Nat → Bool → V → V)
    (g : Gate) (s : State V) : State V :=
  fun i => if i = g.dst then add (s i) (op g.factor g.positive (s g.src)) else s i

def run (add : V → V → V) (op : Nat → Bool → V → V)
    (word : List Gate) (s : State V) : State V :=
  word.foldl (fun state gate => step add op gate state) s

def shift (add : V → V → V) (s : State V) (port : Nat) (v : V) : State V :=
  fun i => if i = port then add (s i) v else s i

def axis (zero : V) (port : Nat) (v : V) : State V :=
  fun i => if i = port then v else zero

theorem run_preserves (add : V → V → V) (op : Nat → Bool → V → V)
    (word : List Gate) (p : Nat) (safe : ∀ g ∈ word, g.dst ≠ p) (s : State V) :
    run add op word s p = s p := by
  induction word generalizing s with
  | nil => rfl
  | cons g gs ih =>
      have h : g.dst ≠ p := safe g (by simp)
      have hs : ∀ a ∈ gs, a.dst ≠ p := by
        intro a ha
        exact safe a (by simp [ha])
      change run add op gs (step add op g s) p = s p
      rw [ih hs]
      simp [step, Ne.symm h]

theorem step_shift (add : V → V → V)
    (commute : ∀ a b c, add (add a b) c = add (add a c) b)
    (op : Nat → Bool → V → V) (g : Gate) (p : Nat) (safe : g.src ≠ p)
    (s : State V) (v : V) :
    step add op g (shift add s p v) = shift add (step add op g s) p v := by
  funext i
  by_cases hi : i = p
  · subst i
    by_cases hd : p = g.dst
    · simp only [step, shift, if_neg safe, if_pos hd]
      exact commute _ _ _
    · simp only [step, shift, if_neg safe, if_neg hd]
  · simp [step, shift, safe, hi]

theorem run_shift (add : V → V → V)
    (commute : ∀ a b c, add (add a b) c = add (add a c) b)
    (op : Nat → Bool → V → V) (word : List Gate) (p : Nat)
    (safe : ∀ g ∈ word, g.src ≠ p) (s : State V) (v : V) :
    run add op word (shift add s p v) = shift add (run add op word s) p v := by
  induction word generalizing s with
  | nil => rfl
  | cons g gs ih =>
      have h : g.src ≠ p := safe g (by simp)
      have hs : ∀ a ∈ gs, a.src ≠ p := by
        intro a ha
        exact safe a (by simp [ha])
      change run add op gs (step add op g (shift add s p v)) =
        shift add (run add op gs (step add op g s)) p v
      rw [step_shift add commute op g p h]
      exact ih hs (step add op g s)

theorem run_zero (add : V → V → V) (zero : V) (add_zero : add zero zero = zero)
    (op : Nat → Bool → V → V) (op_zero : ∀ f sign, op f sign zero = zero)
    (word : List Gate) : run add op word (fun _ => zero) = (fun _ => zero) := by
  induction word with
  | nil => rfl
  | cons g gs ih =>
      have h : step add op g (fun _ => zero) = (fun _ => zero) := by
        funext i
        simp [step, op_zero, add_zero]
      change run add op gs (step add op g (fun _ => zero)) = _
      rw [h]
      exact ih

/-- Every complete-leaf prefix, in either sign, preserves the outer source.
It also preserves every earlier register other than the target. -/
theorem prefix_preserves (add : V → V → V) (op : Nat → Bool → V → V)
    (t : Tree) (sign : Bool) (x y d k p : Nat) (hp : p < d) (hy : p ≠ y)
    (s : State V) : run add op ((emit t sign x y d).take k) s p = s p := by
  apply run_preserves
  intro g hg
  have h := (prefix_ports t sign x y d k g hg).2
  omega

/-- Every complete-leaf prefix is equivariant under translating its target,
or any earlier register other than its source. -/
theorem prefix_shift (add : V → V → V)
    (commute : ∀ a b c, add (add a b) c = add (add a c) b)
    (op : Nat → Bool → V → V) (t : Tree) (sign : Bool) (x y d k p : Nat)
    (hp : p < d) (hx : p ≠ x) (s : State V) (v : V) :
    run add op ((emit t sign x y d).take k) (shift add s p v) =
      shift add (run add op ((emit t sign x y d).take k) s) p v := by
  apply run_shift add commute
  intro g hg
  have h := (prefix_ports t sign x y d k g hg).1
  omega

/-- For zero-preserving leaves, the preceding equivariance gives the column
invariant: a vector supported only at the unread coordinate is fixed. -/
theorem prefix_fixes_axis (add : V → V → V)
    (commute : ∀ a b c, add (add a b) c = add (add a c) b)
    (zero : V) (left_zero : ∀ v, add zero v = v)
    (op : Nat → Bool → V → V) (op_zero : ∀ f sign, op f sign zero = zero)
    (t : Tree) (sign : Bool) (x y d k p : Nat) (hp : p < d) (hx : p ≠ x) (v : V) :
    run add op ((emit t sign x y d).take k) (axis zero p v) = axis zero p v := by
  have h : shift add (fun _ => zero) p v = axis zero p v := by
    funext i
    simp only [shift, axis, left_zero]
  rw [← h]
  rw [prefix_shift add commute op t sign x y d k p hp hx]
  rw [run_zero add zero (left_zero zero) op op_zero]

/-- Coordinate preservation passes to any genuine right inverse; no claim
that sign negation implements an inverse is hidden in this statement. -/
theorem inverse_preserves (f inv : State V → State V) (p : Nat)
    (preserves : ∀ s, f s p = s p) (right_inverse : ∀ s, f (inv s) = s)
    (s : State V) : inv s p = s p := by
  calc
    inv s p = f (inv s) p := (preserves (inv s)).symm
    _ = s p := congrFun (right_inverse s) p

/-- PR1294's four local invariants for two children sharing all deeper
scratch. P and Q are arbitrary completed-leaf prefixes of the left/right
child. R and S are their genuine right inverses. For linear leaves these
are exactly P e_y = Q e_y = e_y and e_x^T R = e_x^T S = e_x^T. -/
theorem four_phase_invariants (add : V → V → V)
    (commute : ∀ a b c, add (add a b) c = add (add a c) b)
    (zero : V) (left_zero : ∀ v, add zero v = v)
    (op : Nat → Bool → V → V) (op_zero : ∀ f sign, op f sign zero = zero)
    (l r : Tree) (sl sr : Bool) (x y d kl kr : Nat)
    (hx : x < d) (hy : y < d) (hxy : x ≠ y)
    (R S : State V → State V)
    (hR : ∀ s, run add op ((emit l sl x d (d+1)).take kl) (R s) = s)
    (hS : ∀ s, run add op ((emit r sr d y (d+1)).take kr) (S s) = s) :
    (∀ v, run add op ((emit l sl x d (d+1)).take kl) (axis zero y v) = axis zero y v) ∧
    (∀ v, run add op ((emit r sr d y (d+1)).take kr) (axis zero y v) = axis zero y v) ∧
    (∀ s, R s x = s x) ∧ (∀ s, S s x = s x) := by
  refine ⟨?_, ?_, ?_, ?_⟩
  · intro v
    exact prefix_fixes_axis add commute zero left_zero op op_zero l sl x d (d+1)
      kl y (by omega) (by omega) v
  · intro v
    exact prefix_fixes_axis add commute zero left_zero op op_zero r sr d y (d+1)
      kr y (by omega) (by omega) v
  · intro s
    apply inverse_preserves _ R x _ hR s
    intro a
    exact prefix_preserves add op l sl x d (d+1) kl x (by omega) (by omega) a
  · intro s
    apply inverse_preserves _ S x _ hS s
    intro a
    exact prefix_preserves add op r sr d y (d+1) kr x (by omega) hxy a

#print axioms emit_ports
#print axioms emit_bounded
#print axioms prefix_preserves
#print axioms prefix_shift
#print axioms prefix_fixes_axis
#print axioms inverse_preserves
#print axioms four_phase_invariants

end DirtyDispatcher
