import ExactFrameTransport

/-!
Exact Gaussian-dyadic gate and phase identities over any commutative ring
containing i and an inverse of 2.  All dimensions and all address involutions
are allowed.  Cost, Clifford synthesis and selected-word binding are absent.
-/
namespace CurrentMain.GaussianPhaseNormalization
open Lean.Grind
open CurrentMain.FrameTransport
attribute [local instance] Semiring.natCast Ring.intCast
universe u v
variable {F : Type u} [CommRing F] {X : Type v}

/-- h is the specified inverse of 2; no implicit division is introduced. -/
def a (i h : F) : F := (1 + i) * h
def b (i h : F) : F := (1 - i) * h
def gate (i h : F) (t : X → X) (f : X → F) (x : X) : F :=
  a i h * f x + b i h * f (t x)
def inverseGate (i h : F) (t : X → X) := gate (-i) h t

def sign (bit : Bool) : F := if bit then -1 else 1
def zPhase (bit : X → Bool) (f : X → F) (x : X) : F := sign (bit x) * f x

theorem inverse_coefficients (i h : F) : a (-i) h = b i h ∧ b (-i) h = a i h := by
  simp only [a, b]
  constructor <;> grind

theorem phase_coefficients (i h : F) (hi : i * i = -1) :
    i * b i h = a i h ∧ i * a i h = -b i h := by
  simp only [a, b]
  constructor <;> grind

theorem coefficient_square (i h : F) (hi : i * i = -1) (hh : 2 * h = 1) :
    a i h * a i h + b i h * b i h = 0 ∧
      a i h * b i h + b i h * a i h = 1 := by
  constructor
  · simp only [a, b]
    clear hh
    grind
  · have hp : a i h * b i h + b i h * a i h = (2 * h) * (2 * h) := by
      simp only [a, b]
      clear hh
      grind
    rw [hp, hh, Semiring.mul_one]

theorem gate_square (i h : F) (hi : i * i = -1) (hh : 2 * h = 1)
    (t : X → X) (ht : ∀ x, t (t x) = x) (f : X → F) :
    gate i h t (gate i h t f) = fun x => f (t x) := by
  have hc := coefficient_square i h hi hh
  funext x
  simp only [gate, ht]
  grind

theorem gate_inverse_left (i h : F) (hi : i * i = -1) (hh : 2 * h = 1)
    (t : X → X) (ht : ∀ x, t (t x) = x) (f : X → F) :
    inverseGate i h t (gate i h t f) = f := by
  have hc := coefficient_square i h hi hh
  have hv := inverse_coefficients i h
  funext x
  simp only [inverseGate, gate, ht, hv.1, hv.2]
  grind

theorem gate_inverse_right (i h : F) (hi : i * i = -1) (hh : 2 * h = 1)
    (t : X → X) (ht : ∀ x, t (t x) = x) (f : X → F) :
    gate i h t (inverseGate i h t f) = f := by
  have hc := coefficient_square i h hi hh
  have hv := inverse_coefficients i h
  funext x
  simp only [inverseGate, gate, ht, hv.1, hv.2]
  grind

def exactGate (i h : F) (hi : i * i = -1) (hh : 2 * h = 1)
    (t : X → X) (ht : ∀ x, t (t x) = x) : ExactFrame X F where
  encode := gate i h t
  decode := inverseGate i h t
  left_inverse := gate_inverse_left i h hi hh t ht
  right_inverse := gate_inverse_right i h hi hh t ht
  encode_add := by intro f g; funext x; simp only [gate]; grind
  encode_scale := by intro s f; funext x; simp only [gate]; grind

theorem zPhase_square (bit : X → Bool) (f : X → F) : zPhase bit (zPhase bit f) = f := by
  funext x
  simp only [zPhase, sign]
  cases bit x <;> simp only [Bool.false_eq_true, if_false, if_true] <;> grind

/-- C inverse = -i Z C Z, including its scalar phase. -/
theorem inverse_phase_gate (i h : F) (hi : i * i = -1)
    (t : X → X) (bit : X → Bool) (hb : ∀ x, bit (t x) = !(bit x)) (f : X → F) :
    inverseGate i h t f = fun x => -i * zPhase bit (gate i h t (zPhase bit f)) x := by
  have hp := phase_coefficients i h hi
  have hv := inverse_coefficients i h
  funext x
  simp only [inverseGate, gate, zPhase, sign, hb, hv.1, hv.2]
  cases bit x <;> simp only [Bool.not_false, Bool.not_true, Bool.false_eq_true, if_false, if_true] <;> grind

/-- The normalization really executes both diagonal Z wrappers and factor i. -/
theorem normalized_inverse_gate (i h : F) (hi : i * i = -1)
    (t : X → X) (bit : X → Bool) (hb : ∀ x, bit (t x) = !(bit x)) (f : X → F) :
    (fun x => i * zPhase bit (inverseGate i h t (zPhase bit f)) x) = gate i h t f := by
  have hp := phase_coefficients i h hi
  have hv := inverse_coefficients i h
  funext x
  simp only [inverseGate, gate, zPhase, sign, hb, hv.1, hv.2]
  cases bit x <;> simp only [Bool.not_false, Bool.not_true, Bool.false_eq_true, if_false, if_true] <;> grind

/-- A nontrivial exact square survives even though the binary transvection
has square identity; this prevents replacing the inverse by the forward map. -/
theorem square_not_identity (i h : F) (hi : i * i = -1) (hh : 2 * h = 1)
    (nontrivial : (0 : F) ≠ 1) (t : X → X) (ht : ∀ x, t (t x) = x)
    (x : X) (hx : t x ≠ x) :
    ¬ (∀ f : X → F, gate i h t (gate i h t f) = f) := by
  classical
  intro wrong
  let f : X → F := fun y => if y = x then 1 else 0
  have bad := congrFun (wrong f) x
  rw [gate_square i h hi hh t ht] at bad
  simp only [f, if_neg hx, if_pos rfl] at bad
  exact nontrivial bad

/-- Pointwise concrete bit flips provide this normalization in every dimension. -/
def flip {n : Nat} (j : Fin n) (x : Fin n → Bool) : Fin n → Bool :=
  fun k => if k = j then !(x k) else x k

theorem flip_twice {n : Nat} (j : Fin n) (x : Fin n → Bool) : flip j (flip j x) = x := by
  funext k
  by_cases hk : k = j <;> simp only [flip, hk, if_true, if_false, Bool.not_not]

theorem flip_bit {n : Nat} (j : Fin n) (x : Fin n → Bool) : flip j x j = !(x j) := by
  simp [flip]

theorem coordinate_normalization {n : Nat} (i h : F) (hi : i * i = -1)
    (j : Fin n) (f : (Fin n → Bool) → F) :
    (fun x => i * zPhase (fun y => y j)
      (inverseGate i h (flip j) (zPhase (fun y => y j) f)) x) = gate i h (flip j) f :=
  normalized_inverse_gate i h hi (flip j) (fun y => y j) (flip_bit j) f

end CurrentMain.GaussianPhaseNormalization

#print axioms CurrentMain.GaussianPhaseNormalization.inverse_coefficients
#print axioms CurrentMain.GaussianPhaseNormalization.phase_coefficients
#print axioms CurrentMain.GaussianPhaseNormalization.coefficient_square
#print axioms CurrentMain.GaussianPhaseNormalization.gate_square
#print axioms CurrentMain.GaussianPhaseNormalization.gate_inverse_left
#print axioms CurrentMain.GaussianPhaseNormalization.gate_inverse_right
#print axioms CurrentMain.GaussianPhaseNormalization.zPhase_square
#print axioms CurrentMain.GaussianPhaseNormalization.inverse_phase_gate
#print axioms CurrentMain.GaussianPhaseNormalization.normalized_inverse_gate
#print axioms CurrentMain.GaussianPhaseNormalization.square_not_identity
#print axioms CurrentMain.GaussianPhaseNormalization.flip_twice
#print axioms CurrentMain.GaussianPhaseNormalization.flip_bit
#print axioms CurrentMain.GaussianPhaseNormalization.coordinate_normalization
