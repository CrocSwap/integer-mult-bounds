import DirectedChildRecipes
import Mathlib.LinearAlgebra.Pi

/-!
Source-linked monomial evaluation for the selected exact Clifford compiler.
Apache-2.0. Prepared with OpenAI assistance; see NOTICE.md.

`clifford_exact.py` executes D, P, X, global phase in that order. Address maps
are certified equivalences, and q is the already decoded source qvalue. This
module supplies the resulting all-payload formula and invertible linear map
using existing Mathlib constructors. It does not certify the raw JSON matrix,
bit order, quadratic coefficients or the compiler's tableau assertions.
-/
namespace CurrentMain.CliffordMonomialDecoder

variable {X K : Type*} [CommSemiring K]

/-- Pointwise powers of the supplied fourth-root unit. -/
def diagonal (omega : Kˣ) (q : X → Nat) : (X → K) ≃ₗ[K] (X → K) :=
  LinearEquiv.piCongrRight (fun x => LinearEquiv.smulOfUnit (M := K) (omega ^ q x))

/-- Push coordinates forward: the output at p(x) is read from x. -/
def push (p : X ≃ X) : (X → K) ≃ₗ[K] (X → K) :=
  LinearEquiv.funCongrLeft K K p.symm

@[simp] theorem diagonal_apply (omega : Kˣ) (q : X → Nat) (v : X → K) (x : X) :
    diagonal omega q v x = (↑(omega ^ q x) : K) * v x := rfl

@[simp] theorem push_apply (p : X ≃ X) (v : X → K) (y : X) :
    push (K := K) p v y = v (p.symm y) := rfl

/-- Literal chronological D → P → X → phase. `linear` is x ↦ Gx and
`offset` is x ↦ x xor b, with their source-specific inverse proofs supplied. -/
def circuit (omega : Kˣ) (q : X → Nat) (phase : Nat)
    (linear offset : X ≃ X) : (X → K) ≃ₗ[K] (X → K) :=
  (((diagonal omega q).trans (push linear)).trans (push offset)).trans
    (diagonal omega (fun _ => phase))

/-- Compact normal-form decoder. Phase is evaluated at the input coordinate,
then the payload is pushed to offset(linear(x)); the exponent is reduced mod 4. -/
def decoded (omega : Kˣ) (q : X → Nat) (phase : Nat)
    (linear offset : X ≃ X) : (X → K) ≃ₗ[K] (X → K) :=
  (diagonal omega (fun x => (phase + q x) % 4)).trans (push (linear.trans offset))

theorem circuit_apply_at (omega : Kˣ) (q : X → Nat) (phase : Nat)
    (linear offset : X ≃ X) (v : X → K) (x : X) :
    circuit omega q phase linear offset v (offset (linear x)) =
      (↑(omega ^ phase) : K) * ((↑(omega ^ q x) : K) * v x) := by
  simp only [circuit, LinearEquiv.trans_apply, diagonal_apply, push_apply,
    Equiv.symm_apply_apply]

theorem decoded_apply_at (omega : Kˣ) (q : X → Nat) (phase : Nat)
    (linear offset : X ≃ X) (v : X → K) (x : X) :
    decoded omega q phase linear offset v (offset (linear x)) =
      (↑(omega ^ ((phase + q x) % 4)) : K) * v x := by
  change diagonal omega (fun x => (phase + q x) % 4) v
    ((linear.trans offset).symm ((linear.trans offset) x)) = _
  rw [Equiv.symm_apply_apply, diagonal_apply]

/-- The compiler's literal monomial sequence equals the compact decoder for
all payloads. This reuses standard unit-action, coordinate and power laws. -/
theorem circuit_eq_decoded (omega : Kˣ) (hfour : omega ^ 4 = 1)
    (q : X → Nat) (phase : Nat) (linear offset : X ≃ X) :
    circuit omega q phase linear offset = decoded omega q phase linear offset := by
  apply LinearEquiv.ext
  intro v
  funext y
  obtain ⟨x, rfl⟩ := (linear.trans offset).surjective y
  change circuit omega q phase linear offset v (offset (linear x)) =
    decoded omega q phase linear offset v (offset (linear x))
  rw [circuit_apply_at, decoded_apply_at, ← pow_eq_pow_mod (phase + q x) hfour]
  simp only [pow_add, Units.val_mul, mul_assoc]

/-- A rank-zero interpreted child has a null right side, exactly as serialized. -/
def rankZeroChild (omega : Kˣ) (q : X → Nat) (phase : Nat)
    (linear offset : X ≃ X) : DirectedChildRecipes.Child K (X → K) where
  rank := 0
  left := decoded omega q phase linear offset
  right := none
  right_none_iff_rank_zero := by simp

/-- Removes the rank-zero monomial execution equality from the preceding
interface after actual primitive semantics and raw decoding have been bound.
It does not prove equality to canonical(new) after inverse canonical(old). -/
theorem rankZero_execution (omega : Kˣ) (hfour : omega ^ 4 = 1)
    (q : X → Nat) (phase : Nat) (linear offset : X ≃ X)
    (blocks : Nat → (X → K) ≃ₗ[K] (X → K)) (v : X → K) :
    DirectedChildRecipes.Child.eval blocks (rankZeroChild omega q phase linear offset) v =
      circuit omega q phase linear offset v := by
  change decoded omega q phase linear offset v = circuit omega q phase linear offset v
  rw [circuit_eq_decoded omega hfour]

end CurrentMain.CliffordMonomialDecoder

#print axioms CurrentMain.CliffordMonomialDecoder.diagonal_apply
#print axioms CurrentMain.CliffordMonomialDecoder.push_apply
#print axioms CurrentMain.CliffordMonomialDecoder.circuit_apply_at
#print axioms CurrentMain.CliffordMonomialDecoder.decoded_apply_at
#print axioms CurrentMain.CliffordMonomialDecoder.circuit_eq_decoded
#print axioms CurrentMain.CliffordMonomialDecoder.rankZero_execution
