import CliffordChild009Decoder
import GaussianPhaseNormalization
import Mathlib.Data.Complex.Basic
import Mathlib.Algebra.Ring.GrindInstances

/-!
One selected directed-child identity, old=0/new=9/rank=1, over complete complex
payloads. The fixed raw record and input/preimage phase convention are inherited
from CliffordChild009Decoder. The canonical frame uses the source's greedy basis
for [11], its exact binary inverse and Q correction. Gaussian inverse/linearity
are reused from GaussianPhaseNormalization. Apache-2.0; see NOTICE.md.

This does not identify a serialized physical executor, prove another record, or
supply residual wrappers and expanded coefficient/tableau work.
-/
namespace CurrentMain.CliffordChild009Canonical

open CliffordChild009Decoder
open CliffordMonomialDecoder

/-- Bounded translation of the source rank loop. Every selected mask is below
2^9. Ten loop tests allow all nine pivot eliminations and the terminal zero test.
Exhaustion is `none`, never a fabricated rank. -/
private def insertPivot : Nat → List (Nat × Nat) → Nat → Option (List (Nat × Nat))
  | 0, _, _ => none
  | fuel + 1, pivots, x =>
      if x = 0 then some pivots else
      match pivots.lookup x.log2 with
      | none => some ((x.log2, x) :: pivots)
      | some y => insertPivot fuel pivots (x ^^^ y)

private def rank9 (rows : List Nat) : Option Nat := do
  let pivots ← rows.foldlM (fun p x => insertPivot 10 p x) []
  return pivots.length

/-- Source `basis_extend(cols,9)`, with its rank calls checked rather than an
assumed basis. The final assertion is also explicit. -/
private def basisExtend9 (cols : List Nat) : Option (List Nat) := do
  let out ← (cols ++ (List.range 9).map (fun i => 2 ^ i)).foldlM
    (fun out x => do
      let r ← rank9 (out ++ [x])
      return if r > out.length then out ++ [x] else out) []
  if out.length = 9 then return out else none

private def transpose9 (rows : List Nat) : List Nat :=
  (List.range 9).map (fun j => (List.range 9).foldl
    (fun out i => out + if (rows.getD i 0).testBit j then 2 ^ i else 0) 0)

private def parity9 (x : Nat) : Bool :=
  (List.range 9).foldl (fun out i => out ^^ x.testBit i) false

private def gramCorrection9 (inverseRows : List Nat) : List Nat :=
  let cols := transpose9 inverseRows
  (List.range 9).map (fun i => (2 ^ i) ^^^ ((List.range 9).foldl
    (fun out j => out + if parity9 ((cols.getD i 0) &&& (cols.getD j 0))
      then 2 ^ j else 0) 0))

def canonicalBasis : List Nat := [11, 1, 2, 4, 16, 32, 64, 128, 256]
def canonicalInverseRows : List Nat := [8, 9, 10, 4, 16, 32, 64, 128, 256]
def canonicalQ : List Nat := [8, 8, 0, 3, 0, 0, 0, 0, 0]

/-- Only the fixed selected nine-coordinate data are reduced. This checks the
source greedy order, transpose and I+G^-T G^-1 correction, not a generic rank
algorithm or any of the other 2,921 child records. -/
theorem canonical_data_certificate :
    basisExtend9 [11] = some canonicalBasis ∧
    transpose9 canonicalBasis = leftRows ∧
    gramCorrection9 canonicalInverseRows = canonicalQ ∧
    transpose9 canonicalQ = canonicalQ ∧
    (∀ r ∈ canonicalBasis, r < 512) ∧
    (∀ r ∈ canonicalInverseRows, r < 512) := by
  refine ⟨?_, by decide, by decide, by decide, by decide, by decide⟩
  -- No recursive log2 equation is placed in a symbolic simplifier context.
  have l1 : Nat.log2 1 = 0 := by
    simpa only using (Nat.log2_two_pow (n := 0))
  have l2 : Nat.log2 2 = 1 := by
    simpa only using (Nat.log2_two_pow (n := 1))
  have l4 : Nat.log2 4 = 2 := by
    simpa only using (Nat.log2_two_pow (n := 2))
  have l8 : Nat.log2 8 = 3 := by
    simpa only using (Nat.log2_two_pow (n := 3))
  have l16 : Nat.log2 16 = 4 := by
    simpa only using (Nat.log2_two_pow (n := 4))
  have l32 : Nat.log2 32 = 5 := by
    simpa only using (Nat.log2_two_pow (n := 5))
  have l64 : Nat.log2 64 = 6 := by
    simpa only using (Nat.log2_two_pow (n := 6))
  have l128 : Nat.log2 128 = 7 := by
    simpa only using (Nat.log2_two_pow (n := 7))
  have l256 : Nat.log2 256 = 8 := by
    simpa only using (Nat.log2_two_pow (n := 8))
  have l3 : Nat.log2 3 = 1 := by
    apply Nat.eq_of_le_of_lt_succ
    · exact (Nat.le_log2 (by decide)).2 (by decide)
    · exact (Nat.log2_lt (by decide)).2 (by decide)
  have l11 : Nat.log2 11 = 3 := by
    apply Nat.eq_of_le_of_lt_succ
    · exact (Nat.le_log2 (by decide)).2 (by decide)
    · exact (Nat.log2_lt (by decide)).2 (by decide)
  -- Exact pivot states in the selected greedy order; the skipped 8 reduces
  -- through 8 xor 11 = 3, then xor 2 = 1, then xor 1 = 0.
  let p1 : List (Nat × Nat) := [(3, 11)]
  let p2 : List (Nat × Nat) := (0, 1) :: p1
  let p3 : List (Nat × Nat) := (1, 2) :: p2
  let p4 : List (Nat × Nat) := (2, 4) :: p3
  let p5 : List (Nat × Nat) := (4, 16) :: p4
  let p6 : List (Nat × Nat) := (5, 32) :: p5
  let p7 : List (Nat × Nat) := (6, 64) :: p6
  let p8 : List (Nat × Nat) := (7, 128) :: p7
  let p9 : List (Nat × Nat) := (8, 256) :: p8
  have i11 : insertPivot 10 [] 11 = some p1 := by
    simp [insertPivot, List.lookup, p1, l11]
  have i1 : insertPivot 10 p1 1 = some p2 := by
    simp [insertPivot, List.lookup, p1, p2, l1]
  have i2 : insertPivot 10 p2 2 = some p3 := by
    simp [insertPivot, List.lookup, p1, p2, p3, l2]
  have i4 : insertPivot 10 p3 4 = some p4 := by
    simp [insertPivot, List.lookup, p1, p2, p3, p4, l4]
  have i16 : insertPivot 10 p4 16 = some p5 := by
    simp [insertPivot, List.lookup, p1, p2, p3, p4, p5, l16]
  have i32 : insertPivot 10 p5 32 = some p6 := by
    simp [insertPivot, List.lookup, p1, p2, p3, p4, p5, p6, l32]
  have i64 : insertPivot 10 p6 64 = some p7 := by
    simp [insertPivot, List.lookup, p1, p2, p3, p4, p5, p6, p7, l64]
  have i128 : insertPivot 10 p7 128 = some p8 := by
    simp [insertPivot, List.lookup, p1, p2, p3, p4, p5, p6, p7, p8, l128]
  have i256 : insertPivot 10 p8 256 = some p9 := by
    simp [insertPivot, List.lookup, p1, p2, p3, p4, p5, p6, p7, p8, p9, l256]
  have i8 : insertPivot 10 p4 8 = some p4 := by
    simp [insertPivot, List.lookup, p1, p2, p3, p4, l8, l3, l1]
  -- Each rank equation consumes only the displayed closed insertion facts.
  have r1 : rank9 [11] = some 1 := by
    simp only [rank9, List.foldlM_cons, List.foldlM_nil, Option.pure_def,
      Option.bind_eq_bind, Option.bind_some, i11]
    rfl
  have r2 : rank9 [11, 1] = some 2 := by
    simp only [rank9, List.foldlM_cons, List.foldlM_nil, Option.pure_def,
      Option.bind_eq_bind, Option.bind_some, i11, i1]
    rfl
  have r3 : rank9 [11, 1, 2] = some 3 := by
    simp only [rank9, List.foldlM_cons, List.foldlM_nil, Option.pure_def,
      Option.bind_eq_bind, Option.bind_some, i11, i1, i2]
    rfl
  have r4 : rank9 [11, 1, 2, 4] = some 4 := by
    simp only [rank9, List.foldlM_cons, List.foldlM_nil, Option.pure_def,
      Option.bind_eq_bind, Option.bind_some, i11, i1, i2, i4]
    rfl
  have rSkip : rank9 [11, 1, 2, 4, 8] = some 4 := by
    simp only [rank9, List.foldlM_cons, List.foldlM_nil, Option.pure_def,
      Option.bind_eq_bind, Option.bind_some, i11, i1, i2, i4, i8]
    rfl
  have r5 : rank9 [11, 1, 2, 4, 16] = some 5 := by
    simp only [rank9, List.foldlM_cons, List.foldlM_nil, Option.pure_def,
      Option.bind_eq_bind, Option.bind_some, i11, i1, i2, i4, i16]
    rfl
  have r6 : rank9 [11, 1, 2, 4, 16, 32] = some 6 := by
    simp only [rank9, List.foldlM_cons, List.foldlM_nil, Option.pure_def,
      Option.bind_eq_bind, Option.bind_some, i11, i1, i2, i4, i16, i32]
    rfl
  have r7 : rank9 [11, 1, 2, 4, 16, 32, 64] = some 7 := by
    simp only [rank9, List.foldlM_cons, List.foldlM_nil, Option.pure_def,
      Option.bind_eq_bind, Option.bind_some, i11, i1, i2, i4, i16, i32, i64]
    rfl
  have r8 : rank9 [11, 1, 2, 4, 16, 32, 64, 128] = some 8 := by
    simp only [rank9, List.foldlM_cons, List.foldlM_nil, Option.pure_def,
      Option.bind_eq_bind, Option.bind_some, i11, i1, i2, i4, i16, i32, i64, i128]
    rfl
  have r9 : rank9 [11, 1, 2, 4, 16, 32, 64, 128, 256] = some 9 := by
    simp only [rank9, List.foldlM_cons, List.foldlM_nil, Option.pure_def,
      Option.bind_eq_bind, Option.bind_some, i11, i1, i2, i4, i16, i32, i64, i128, i256]
    rfl
  have units : (List.range 9).map (fun i => 2 ^ i) =
      [1, 2, 4, 8, 16, 32, 64, 128, 256] := by decide
  -- Unfold the fixed basis fold, never the rank/log evaluator under its lambda.
  simpa [basisExtend9, units, List.foldlM, canonicalBasis,
    r1, r2, r3, r4, rSkip, r5, r6, r7, r8, r9]

/-- The proposed inverse is proved by the already certified coordinate inverse;
its upper five rows are literal identity. No source `inv` assertion is assumed. -/
theorem canonical_inverse_decode (x : Low) :
    mv4 canonicalInverseRows x = leftEquiv.symm x ∧
    canonicalInverseRows.drop 4 = [16, 32, 64, 128, 256] := by
  rcases x with ⟨a, b, c, d⟩
  cases a <;> cases b <;> cases c <;> cases d <;> decide

def canonicalPhase (x : Low) : Nat :=
  ((if x.1 && x.2.2.2 then 2 else 0) +
   (if x.2.1 && x.2.2.2 then 2 else 0)) % 4

theorem canonical_phase_decode (x : Low) :
    qvalue4 canonicalQ (List.replicate 9 0) x = canonicalPhase x := by
  rcases x with ⟨a, b, c, d⟩
  cases a <;> cases b <;> cases c <;> cases d <;> decide

noncomputable section

/-- The phase unit is actual complex i, rather than an unspecified fourth root. -/
def imagUnit : ℂˣ where
  val := Complex.I
  inv := -Complex.I
  val_inv := by simp
  inv_val := by simp

theorem imagUnit_four : imagUnit ^ 4 = 1 := by
  apply Units.ext
  change Complex.I ^ 4 = 1
  exact Complex.I_pow_four

variable {S : Type*}

private def flipZero (x : Low × S) : Low × S := (offsetEquiv x.1, x.2)

private theorem flipZero_twice (x : Low × S) : flipZero (flipZero x) = x := by
  rcases x with ⟨⟨a, b, c, d⟩, s⟩
  cases a <;> rfl

/-- The source Gaussian C0, with its exact dyadic normalization. This packages
an existing ExactFrame as a Mathlib LinearEquiv without redoing its algebra. -/
def gaussian : (Low × S → ℂ) ≃ₗ[ℂ] (Low × S → ℂ) :=
  let E := GaussianPhaseNormalization.exactGate Complex.I ((2 : ℂ)⁻¹)
    Complex.I_mul_I (mul_inv_cancel₀ two_ne_zero) flipZero flipZero_twice
  { toFun := E.encode
    invFun := E.decode
    left_inv := E.left_inverse
    right_inv := E.right_inverse
    map_add' := E.encode_add
    map_smul' := E.encode_scale }

@[simp] theorem gaussian_apply (v : Low × S → ℂ) (x : Low) (s : S) :
    gaussian v (x, s) =
      GaussianPhaseNormalization.a Complex.I ((2 : ℂ)⁻¹) * v (x, s) +
      GaussianPhaseNormalization.b Complex.I ((2 : ℂ)⁻¹) * v (offsetEquiv x, s) := rfl

/-- Source K=perm(G).then(diag(Q)), hence D_Q after P_G. -/
def canonicalK : (Low × S → ℂ) ≃ₗ[ℂ] (Low × S → ℂ) :=
  (push (liftAddress leftEquiv)).trans
    (diagonal imagUnit (fun x => canonicalPhase x.1))

@[simp] theorem canonicalK_apply (v : Low × S → ℂ) (x : Low) (s : S) :
    canonicalK v (x, s) = Complex.I ^ canonicalPhase x * v (leftEquiv.symm x, s) := rfl

private theorem right_apply (v : Low × S → ℂ) (x : Low) (s : S) :
    rightDecoded imagUnit v (x, s) =
      Complex.I ^ ((1 + rightPhase ((rightEquiv.trans offsetEquiv).symm x)) % 4) *
        v ((rightEquiv.trans offsetEquiv).symm x, s) := by
  have h := right_decoded_apply imagUnit v ((rightEquiv.trans offsetEquiv).symm x) s
  change rightDecoded imagUnit v
    ((rightEquiv.trans offsetEquiv) ((rightEquiv.trans offsetEquiv).symm x), s) = _ at h
  rw [Equiv.apply_symm_apply] at h
  simpa only [Units.val_pow_eq_pow_val] using h

/-- The finite proof keeps arbitrary complex payloads and an arbitrary spectator
type. It compares both Gaussian branches, retaining offset 1 and global phase 1
of the stored right monomial. It is not a zero-state or tableau test. -/
theorem decoded_child_on_canonical (v : Low × S → ℂ) :
    leftDecoded imagUnit (gaussian (rightDecoded imagUnit (canonicalK v))) =
      canonicalK (gaussian v) := by
  have hp := GaussianPhaseNormalization.phase_coefficients Complex.I ((2 : ℂ)⁻¹)
    Complex.I_mul_I
  have ha := hp.2
  have hb := hp.1
  have ha' : GaussianPhaseNormalization.a Complex.I ((2 : ℂ)⁻¹) * Complex.I =
      -GaussianPhaseNormalization.b Complex.I ((2 : ℂ)⁻¹) := by
    simpa only [mul_comm] using ha
  have hb' : GaussianPhaseNormalization.b Complex.I ((2 : ℂ)⁻¹) * Complex.I =
      GaussianPhaseNormalization.a Complex.I ((2 : ℂ)⁻¹) := by
    simpa only [mul_comm] using hb
  funext y
  rcases y with ⟨y, s⟩
  obtain ⟨x, rfl⟩ := leftEquiv.surjective y
  rw [left_decoded_apply, canonicalK_apply]
  simp only [gaussian_apply, right_apply, canonicalK_apply]
  rcases x with ⟨a, b, c, d⟩
  cases a <;> cases b <;> cases c <;> cases d <;>
    simp [canonicalPhase,
      leftPhase, rightPhase, leftEquiv, leftMap, leftInverse, rightEquiv,
      rightMap, rightInverse, offsetEquiv, Equiv.trans_apply,
      Units.val_pow_eq_pow_val, imagUnit, pow_succ, Complex.I_mul_I,
      mul_add, add_mul, ← mul_assoc, ha, hb, ha', hb', add_comm]

/-- Canonical [] is identity. Canonical [11] is K C0 K^-1, in the direct
old→new direction from phases_delta.py. -/
def canonicalOld : (Low × S → ℂ) ≃ₗ[ℂ] (Low × S → ℂ) := LinearEquiv.refl _ _
def canonicalNew : (Low × S → ℂ) ≃ₗ[ℂ] (Low × S → ℂ) :=
  (canonicalK.symm.trans gaussian).trans canonicalK

def selectedChild : DirectedChildRecipes.Child ℂ (Low × S → ℂ) where
  rank := 1
  left := leftDecoded imagUnit
  right := some (rightDecoded imagUnit)
  right_none_iff_rank_zero := by simp

/-- Discharges this one interpreted record's canonical-child operator equation
for all payloads. The block argument is C0 only because this record has rank 1;
no meaning is assigned here to other ranks or raw physical recipe execution. -/
theorem selected_child_operator (v : Low × S → ℂ) :
    DirectedChildRecipes.Child.eval (fun _ => gaussian) selectedChild v =
      canonicalNew (canonicalOld.symm v) := by
  have h := decoded_child_on_canonical (canonicalK.symm v)
  simpa only [DirectedChildRecipes.Child.eval, selectedChild,
    LinearEquiv.apply_symm_apply, canonicalNew, canonicalOld,
    LinearEquiv.trans_apply, LinearEquiv.refl_symm, LinearEquiv.refl_apply] using h

end
end CurrentMain.CliffordChild009Canonical

#print axioms CurrentMain.CliffordChild009Canonical.canonical_data_certificate
#print axioms CurrentMain.CliffordChild009Canonical.canonical_inverse_decode
#print axioms CurrentMain.CliffordChild009Canonical.canonical_phase_decode
#print axioms CurrentMain.CliffordChild009Canonical.imagUnit_four
#print axioms CurrentMain.CliffordChild009Canonical.gaussian
#print axioms CurrentMain.CliffordChild009Canonical.decoded_child_on_canonical
#print axioms CurrentMain.CliffordChild009Canonical.selected_child_operator
