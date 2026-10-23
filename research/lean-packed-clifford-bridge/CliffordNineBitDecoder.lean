import RankOneRecipeCertificate
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.Data.ZMod.Basic

/-!
Nine-coordinate source decoder for the retained f19 Clifford records.
Apache-2.0; prepared with OpenAI assistance. See NOTICE.md.

Rows act on column vectors, with bit zero at coordinate zero. ZMod2 is used
only for addresses; stored phases remain Nat values reduced modulo four.
Both matrix inverse equations and all raw field/basis certificates are inputs.
The existing fuel-bounded transcription of the source rank/basis loop is
retained. Its fast evaluator
is proved equal, including zero, fallback, fuel exhaustion and skipped rows.
-/
namespace CurrentMain.CliffordNineBitDecoder

open scoped BigOperators Matrix
open RankOneRecipeCertificate

abbrev Bit := ZMod 2
abbrev Address := Fin 9 → Bit

def mask (n : Nat) : Address := fun i => if n.testBit i.val then 1 else 0

def matrix (rows : List Nat) : Matrix (Fin 9) (Fin 9) Bit :=
  fun i j => if (rows.getD i.val 0).testBit j.val then 1 else 0

/-- Existing matrix linearity and linear-equivalence constructors supply all
group laws. Both inverse products must be checked for the actual raw rows. -/
def coordinateEquiv (rows inverseRows : List Nat)
    (hforward : matrix rows * matrix inverseRows = 1)
    (hbackward : matrix inverseRows * matrix rows = 1) : Address ≃ₗ[Bit] Address :=
  LinearEquiv.ofLinear (matrix rows).mulVecLin (matrix inverseRows).mulVecLin
    (by
      apply LinearMap.ext
      intro x
      change matrix rows *ᵥ (matrix inverseRows *ᵥ x) = x
      rw [Matrix.mulVec_mulVec, hforward, Matrix.one_mulVec])
    (by
      apply LinearMap.ext
      intro x
      change matrix inverseRows *ᵥ (matrix rows *ᵥ x) = x
      rw [Matrix.mulVec_mulVec, hbackward, Matrix.one_mulVec])

theorem coordinateEquiv_apply (rows inverseRows : List Nat) (hf hb) (x : Address) :
    coordinateEquiv rows inverseRows hf hb x = matrix rows *ᵥ x := rfl

theorem coordinateEquiv_symm_apply (rows inverseRows : List Nat) (hf hb) (x : Address) :
    (coordinateEquiv rows inverseRows hf hb).symm x = matrix inverseRows *ᵥ x := rfl

def offsetEquiv (n : Nat) : Address ≃ Address := Equiv.addRight (mask n)

theorem offsetEquiv_apply (n : Nat) (x : Address) : offsetEquiv n x = x + mask n := rfl

theorem offsetEquiv_symm_apply (n : Nat) (x : Address) :
    (offsetEquiv n).symm x = x + mask n := by
  change x + -(mask n) = x + mask n
  rw [ZModModule.neg_eq_self]

/-- Source strict-upper-triangular parity, followed by its factor two, and
the full linear Z4 contribution. This is the bit-vector interpretation;
packed-address/executor correspondence remains a separate binding. -/
def qvalue (Q alpha : List Nat) (x : Address) : Nat :=
  ((∑ i : Fin 9, alpha.getD i.val 0 * (x i).val) +
    2 * ∑ i : Fin 9, (x i).val *
      ((∑ j : Fin 9, if i.val < j.val then matrix Q i j * x j else 0) : Bit).val) % 4

def defaultAlpha (Q : List Nat) : List Nat :=
  (List.range 9).map (fun i => if (Q.getD i 0).testBit i then 1 else 0)

def monomial (rows inverseRows Q alpha : List Nat) (offset phase : Nat)
    (hf : matrix rows * matrix inverseRows = 1)
    (hb : matrix inverseRows * matrix rows = 1) : Monomial Address where
  linear := (coordinateEquiv rows inverseRows hf hb).toEquiv
  offset := offsetEquiv offset
  quadraticPhase := qvalue Q alpha
  globalPhase := phase

/-- The fuel-bounded source elimination and greedy extension, parameterized solely by the
logarithm evaluator. `sourceBasis` below uses the original Nat.log2. -/
def insertPivotWith (log : Nat → Nat) :
    Nat → List (Nat × Nat) → Nat → Option (List (Nat × Nat))
  | 0, _, _ => none
  | fuel + 1, pivots, x =>
      if x = 0 then some pivots else
      match pivots.lookup (log x) with
      | none => some ((log x, x) :: pivots)
      | some y => insertPivotWith log fuel pivots (x ^^^ y)

def rankWith (log : Nat → Nat) (rows : List Nat) : Option Nat := do
  let pivots ← rows.foldlM (fun p x => insertPivotWith log 10 p x) []
  return pivots.length

def basisWith (log : Nat → Nat) (cols : List Nat) : Option (List Nat) := do
  let out ← (cols ++ (List.range 9).map (fun i => 2 ^ i)).foldlM
    (fun out x => do
      let r ← rankWith log (out ++ [x])
      return if r > out.length then out ++ [x] else out) []
  if out.length = 9 then return out else none

def sourceBasis (cols : List Nat) : Option (List Nat) := basisWith Nat.log2 cols

/-- Nine finite thresholds, with explicit zero behavior. -/
def smallLog (x : Nat) : Nat :=
  if x < 2 then 0 else if x < 4 then 1 else if x < 8 then 2 else
  if x < 16 then 3 else if x < 32 then 4 else if x < 64 then 5 else
  if x < 128 then 6 else if x < 256 then 7 else 8

private theorem log2_of_bounds (x k : Nat) (hn : x ≠ 0)
    (hl : 2 ^ k ≤ x) (hu : x < 2 ^ (k + 1)) : x.log2 = k := by
  have h1 := (Nat.le_log2 hn).2 hl
  have h2 := (Nat.log2_lt hn).2 hu
  omega

theorem smallLog_eq (x : Nat) (hx : x < 512) : smallLog x = x.log2 := by
  unfold smallLog
  split_ifs with h2 h4 h8 h16 h32 h64 h128 h256
  · have h : x = 0 ∨ x = 1 := by omega
    rcases h with rfl | rfl
    · exact Nat.log2_zero.symm
    · exact (Nat.log2_two_pow (n := 0)).symm
  · symm
    exact log2_of_bounds x 1 (by omega) (by change 2 ≤ x; omega) (by change x < 4; omega)
  · symm
    exact log2_of_bounds x 2 (by omega) (by change 4 ≤ x; omega) (by change x < 8; omega)
  · symm
    exact log2_of_bounds x 3 (by omega) (by change 8 ≤ x; omega) (by change x < 16; omega)
  · symm
    exact log2_of_bounds x 4 (by omega) (by change 16 ≤ x; omega) (by change x < 32; omega)
  · symm
    exact log2_of_bounds x 5 (by omega) (by change 32 ≤ x; omega) (by change x < 64; omega)
  · symm
    exact log2_of_bounds x 6 (by omega) (by change 64 ≤ x; omega) (by change x < 128; omega)
  · symm
    exact log2_of_bounds x 7 (by omega) (by change 128 ≤ x; omega) (by change x < 256; omega)
  · symm
    exact log2_of_bounds x 8 (by omega) (by change 256 ≤ x; omega) (by change x < 512; omega)

/-- The fallback makes equality unconditional. No unproved invariant that XOR
stays below512 is needed for semantic equality; selected bounds only govern
which executable branch the closed certificate reduces. -/
def fastLog (x : Nat) : Nat := if x < 512 then smallLog x else x.log2

theorem fastLog_eq (x : Nat) : fastLog x = x.log2 := by
  unfold fastLog
  split_ifs with h
  · exact smallLog_eq x h
  · rfl

def fastBasis (cols : List Nat) : Option (List Nat) := basisWith fastLog cols

/-- Exact equality of the same source evaluator with a proved reduction aid.
Fuel ten, Option.none and skipped dependent candidates are untouched. -/
theorem fastBasis_eq_sourceBasis (cols : List Nat) : fastBasis cols = sourceBasis cols := by
  have h : fastLog = Nat.log2 := funext fastLog_eq
  simp only [fastBasis, sourceBasis, h]

def transpose9 (rows : List Nat) : List Nat :=
  (List.range 9).map (fun j => (List.range 9).foldl
    (fun out i => out + if (rows.getD i 0).testBit j then 2 ^ i else 0) 0)

def parity9 (x : Nat) : Bool :=
  (List.range 9).foldl (fun out i => out ^^ x.testBit i) false

def gramCorrection9 (inverseRows : List Nat) : List Nat :=
  let cols := transpose9 inverseRows
  (List.range 9).map (fun i => (2 ^ i) ^^^ ((List.range 9).foldl
    (fun out j => out + if parity9 ((cols.getD i 0) &&& (cols.getD j 0))
      then 2 ^ j else 0) 0))

noncomputable section

def flipZero (x : Address) : Address := x + mask 1

theorem flipZero_twice (x : Address) : flipZero (flipZero x) = x := by
  simp only [flipZero, add_assoc, ZModModule.add_self, add_zero]

/-- Packages the already accepted exact Gaussian frame, with no new inverse
or Gaussian phase algebra. -/
def gaussian : (Address → ℂ) ≃ₗ[ℂ] (Address → ℂ) :=
  let E := GaussianPhaseNormalization.exactGate Complex.I ((2 : ℂ)⁻¹)
    Complex.I_mul_I (mul_inv_cancel₀ two_ne_zero) flipZero flipZero_twice
  { toFun := E.encode
    invFun := E.decode
    left_inv := E.left_inverse
    right_inv := E.right_inverse
    map_add' := E.encode_add
    map_smul' := E.encode_scale }

theorem gaussian_apply (v : Address → ℂ) (x : Address) :
    gaussian v x = ca * v x + cb * v (flipZero x) := rfl

end
end CurrentMain.CliffordNineBitDecoder

#print axioms CurrentMain.CliffordNineBitDecoder.coordinateEquiv
#print axioms CurrentMain.CliffordNineBitDecoder.coordinateEquiv_apply
#print axioms CurrentMain.CliffordNineBitDecoder.coordinateEquiv_symm_apply
#print axioms CurrentMain.CliffordNineBitDecoder.offsetEquiv_symm_apply
#print axioms CurrentMain.CliffordNineBitDecoder.smallLog_eq
#print axioms CurrentMain.CliffordNineBitDecoder.fastLog_eq
#print axioms CurrentMain.CliffordNineBitDecoder.fastBasis_eq_sourceBasis
#print axioms CurrentMain.CliffordNineBitDecoder.flipZero_twice
#print axioms CurrentMain.CliffordNineBitDecoder.gaussian
#print axioms CurrentMain.CliffordNineBitDecoder.gaussian_apply
