import Mathlib.Data.Matrix.Basic
import Mathlib.Data.Fintype.BigOperators

/-! Explicit hybrid construction. A commutative leaf may mix both input banks;
its outputs use only fixed linear recombination of a finite product vector.
Block stability is an input property of the outer component, never of the hybrid. -/
namespace PersonalMatrix.Hybrid
open scoped BigOperators
set_option maxHeartbeats 2000000
variable {K : Type*} [CommRing K]
variable {a b r ell : ℕ}
abbrev Square (n : ℕ) := Matrix (Fin n) (Fin n) K
abbrev Index (n : ℕ) := Fin n × Fin n
abbrev Input (n : ℕ) := Index n ⊕ Index n
abbrev Full (a b : ℕ) := Matrix (Fin a × Fin b) (Fin a × Fin b) K
abbrev Blocked (a b : ℕ) := Matrix (Fin a) (Fin a) (Square (K := K) b)

def blocks (A : Full (K := K) a b) : Blocked (K := K) a b :=
  fun i j x y => A (i,x) (j,y)
def flatten (A : Blocked (K := K) a b) : Full (K := K) a b :=
  fun ix jy => A ix.1 jy.1 ix.2 jy.2

@[simp] theorem flatten_blocks (A : Full (K := K) a b) : flatten (blocks A) = A := rfl
@[simp] theorem blocks_flatten (A : Blocked (K := K) a b) : blocks (flatten A) = A := rfl

theorem blocks_mul (A B : Full (K := K) a b) : blocks (A*B) = blocks A * blocks B := by
  ext i j x y
  simp only [blocks, Matrix.mul_apply, Matrix.sum_apply]
  rw [Fintype.sum_prod_type]

structure Outer (K : Type*) (a r : ℕ) where
  left : Fin r → Index a → K
  right : Fin r → Index a → K
  output : Fin a → Fin a → Fin r → K

def blockLinear (c : Index a → K) (A : Blocked (K := K) a b) : Square (K := K) b :=
  ∑ p : Index a, c p • A p.1 p.2

def outerEval (o : Outer K a r) (A B : Blocked (K := K) a b) : Blocked (K := K) a b :=
  fun i j => ∑ t : Fin r, o.output i j t •
    (blockLinear (o.left t) A * blockLinear (o.right t) B)

/-- Ordinary component validity at matrix-valued entries. Scalar-only correctness
is not silently substituted for this noncommutative block property. -/
def BlockStable (o : Outer K a r) (b : ℕ) : Prop :=
  ∀ A B : Blocked (K := K) a b, outerEval o A B = A*B

/-- Finite multiplication gates of mixed linear forms, followed only by fixed
linear recombination. This forbids hiding extra variable products in an evaluator. -/
structure Leaf (K : Type*) (b ell : ℕ) where
  left : Fin ell → Input b → K
  right : Fin ell → Input b → K
  output : Fin b → Fin b → Fin ell → K

def inputValue (X Y : Square (K := K) b) : Input b → K :=
  Sum.elim (fun p => X p.1 p.2) (fun p => Y p.1 p.2)
def scalarLinear (c : Input b → K) (X Y : Square (K := K) b) : K :=
  ∑ p : Input b, c p * inputValue X Y p

def leafProducts (l : Leaf K b ell) (X Y : Square (K := K) b) : Fin ell → K :=
  fun g => scalarLinear (l.left g) X Y * scalarLinear (l.right g) X Y

def leafReconstruct (l : Leaf K b ell) (products : Fin ell → K) : Square (K := K) b :=
  fun i j => ∑ g : Fin ell, l.output i j g * products g

def leafEval (l : Leaf K b ell) (X Y : Square (K := K) b) : Square (K := K) b :=
  leafReconstruct l (leafProducts l X Y)

def LeafValid (l : Leaf K b ell) : Prop := ∀ X Y, leafEval l X Y = X*Y

/-- All input-dependent multiplication gates are indexed by this actual product type. -/
def hybridProducts (o : Outer K a r) (l : Leaf K b ell)
    (A B : Full (K := K) a b) : Fin r × Fin ell → K :=
  fun tg => leafProducts l (blockLinear (o.left tg.1) (blocks A))
    (blockLinear (o.right tg.1) (blocks B)) tg.2

/-- Read each stored product vector once per outer term; all reconstruction
multipliers are fixed coefficients. It contains no additional variable product. -/
def hybridEval (o : Outer K a r) (l : Leaf K b ell)
    (A B : Full (K := K) a b) : Full (K := K) a b :=
  flatten (fun i j => ∑ t : Fin r, o.output i j t •
    leafReconstruct l (fun g => hybridProducts o l A B (t,g)))

theorem hybrid_sound (o : Outer K a r) (l : Leaf K b ell)
    (ho : BlockStable o b) (hl : LeafValid l) (A B : Full (K := K) a b) :
    hybridEval o l A B = A*B := by
  have hleaf : ∀ t, leafReconstruct l (fun g => hybridProducts o l A B (t,g)) =
      blockLinear (o.left t) (blocks A) * blockLinear (o.right t) (blocks B) := by
    intro t
    simpa only [leafEval, hybridProducts] using
      hl (blockLinear (o.left t) (blocks A)) (blockLinear (o.right t) (blocks B))
  calc
    hybridEval o l A B = flatten (outerEval o (blocks A) (blocks B)) := by
      unfold hybridEval outerEval
      congr 1
      funext i j
      apply Finset.sum_congr rfl
      intro t _
      rw [hleaf]
    _ = flatten (blocks A * blocks B) := congrArg flatten (ho _ _)
    _ = A*B := by rw [← blocks_mul, flatten_blocks]

/-- Exact scheduled gate cardinality, hence an upper bound on variable products.
Degenerate coefficient vectors may make some scheduled gates input-independent. -/
def scheduledGateCount (o : Outer K a r) (l : Leaf K b ell) : ℕ :=
  Fintype.card (Fin r × Fin ell)

theorem hybrid_gate_count (o : Outer K a r) (l : Leaf K b ell) :
    scheduledGateCount o l = r*ell := by simp [scheduledGateCount]

/-- Component correctness and explicit gate construction jointly yield soundness
and exact schedule cost. Neither composed conclusion is a premise. -/
theorem hybrid_sound_and_cost (o : Outer K a r) (l : Leaf K b ell)
    (ho : BlockStable o b) (hl : LeafValid l) (A B : Full (K := K) a b) :
    hybridEval o l A B = A*B ∧ scheduledGateCount o l = r*ell :=
  ⟨hybrid_sound o l ho hl A B, hybrid_gate_count o l⟩

def W (b : ℕ) : ℕ := b*(b^2+2*b-1)/2

theorem hybrid_W_cost (o : Outer K a r) (l : Leaf K b (W b))
    (ho : BlockStable o b) (hl : LeafValid l) (A B : Full (K := K) a b) :
    hybridEval o l A B = A*B ∧ scheduledGateCount o l = r*W b :=
  hybrid_sound_and_cost o l ho hl A B

theorem perfect_square_cost (o : Outer K a r) (l : Leaf K a (W a))
    (ho : BlockStable o a) (hl : LeafValid l) (A B : Full (K := K) a a) :
    hybridEval o l A B = A*B ∧ scheduledGateCount o l = r*W a :=
  hybrid_W_cost o l ho hl A B

#print axioms blocks_mul
#print axioms hybrid_sound
#print axioms hybrid_gate_count
#print axioms hybrid_sound_and_cost
#print axioms hybrid_W_cost
#print axioms perfect_square_cost
#check @hybrid_sound_and_cost
#check @hybrid_W_cost
end PersonalMatrix.Hybrid
