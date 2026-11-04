import PortRowData
import Mathlib.Data.Matrix.Mul
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Algebra.BigOperators.Fin

/-!
The concrete dyadic port charts used by the selected source construction.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.

`basis` is the source matrix B_q = [q/2 | complement_columns], obtained by
casting the literal integer table `2 B_q` then dividing by two. This is valid
in every field in which two is nonzero, including admitted odd finite fields;
no rational-to-finite-field ring homomorphism is assumed. Its transpose is
the inverse. `chart64` applies this basis to coordinates 0..7 and fixes 8..63.
These proofs establish the chart, not local-word endpoint correctness or
physical ownership, which must be supplied separately.
-/
namespace PortGeometry
open scoped Matrix BigOperators

def integerBasis (port : Fin 120) : Matrix (Fin 8) (Fin 8) Int :=
  Matrix.of (doubledBasis port)

theorem doubled_orthogonal (port : Fin 120) :
    (integerBasis port).transpose * integerBasis port =
      (4 : Int) • (1 : Matrix (Fin 8) (Fin 8) Int) := by
  ext i j
  have h := doubled_orthogonal_entries port i j
  by_cases hij : i = j <;>
    simpa [Matrix.mul_apply, Matrix.transpose_apply, Fin.sum_univ_succ,
      Matrix.smul_apply, Matrix.one_apply, doubledDot, columnDot, hij, smul_eq_mul,
      integerBasis] using h

theorem doubled_row_orthogonal (port : Fin 120) :
    integerBasis port * (integerBasis port).transpose =
      (4 : Int) • (1 : Matrix (Fin 8) (Fin 8) Int) := by
  ext i j
  have h := doubled_row_orthogonal_entries port i j
  by_cases hij : i = j <;>
    simpa [Matrix.mul_apply, Matrix.transpose_apply, Fin.sum_univ_succ,
      Matrix.smul_apply, Matrix.one_apply, doubledRowDot, rowDot, hij, smul_eq_mul,
      integerBasis] using h

def castBasis (K : Type*) [Field K] (port : Fin 120) : Matrix (Fin 8) (Fin 8) K :=
  Matrix.map (integerBasis port) (Int.castRingHom K)

def basis (K : Type*) [Field K] (port : Fin 120) : Matrix (Fin 8) (Fin 8) K :=
  (2 : K)⁻¹ • castBasis K port

theorem basis_entry (K : Type*) [Field K] (port : Fin 120) (i j : Fin 8) :
    basis K port i j = (doubledBasis port i j : K) / 2 := by
  simp [basis, castBasis, integerBasis, Matrix.map, Matrix.smul_apply, div_eq_mul_inv,
    smul_eq_mul, mul_comm]

theorem cast_orthogonal (K : Type*) [Field K] (port : Fin 120) :
    (castBasis K port).transpose * castBasis K port =
      (4 : K) • (1 : Matrix (Fin 8) (Fin 8) K) := by
  have h := congrArg (fun m : Matrix (Fin 8) (Fin 8) Int => m.map (Int.castRingHom K))
    (doubled_orthogonal port)
  dsimp only at h
  rw [Matrix.map_mul] at h
  change (castBasis K port).transpose * castBasis K port = _ at h
  rw [h]
  ext i j
  by_cases hij : i = j <;>
    simp [Matrix.map, Matrix.smul_apply, Matrix.one_apply, hij, smul_eq_mul]

theorem cast_row_orthogonal (K : Type*) [Field K] (port : Fin 120) :
    castBasis K port * (castBasis K port).transpose =
      (4 : K) • (1 : Matrix (Fin 8) (Fin 8) K) := by
  have h := congrArg (fun m : Matrix (Fin 8) (Fin 8) Int => m.map (Int.castRingHom K))
    (doubled_row_orthogonal port)
  dsimp only at h
  rw [Matrix.map_mul] at h
  change castBasis K port * (castBasis K port).transpose = _ at h
  rw [h]
  ext i j
  by_cases hij : i = j <;>
    simp [Matrix.map, Matrix.smul_apply, Matrix.one_apply, hij, smul_eq_mul]

/-- Checked orthogonality survives reduction to any field of characteristic
other than two. This quantifies over the field; it is not a numerical sample. -/
theorem basis_transpose_mul (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) : (basis K port).transpose * basis K port = 1 := by
  unfold basis
  rw [Matrix.transpose_smul, Matrix.smul_mul, Matrix.mul_smul, cast_orthogonal]
  have hs : (2 : K)⁻¹ * ((2 : K)⁻¹ * 4) = 1 := by
    field_simp [h2]
    ring
  simp only [smul_smul, hs, one_smul]

theorem basis_mul_transpose (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) : basis K port * (basis K port).transpose = 1 := by
  unfold basis
  rw [Matrix.transpose_smul, Matrix.smul_mul, Matrix.mul_smul, cast_row_orthogonal]
  have hs : (2 : K)⁻¹ * ((2 : K)⁻¹ * 4) = 1 := by
    field_simp [h2]
    ring
  simp only [smul_smul, hs, one_smul]

/-- Coordinate-to-ambient map on U0, with the literal source transpose as
inverse. Every coordinate value is arbitrary. -/
def chart8 (K : Type*) [Field K] (h2 : (2 : K) ≠ 0) (port : Fin 120) :
    (Fin 8 → K) ≃ (Fin 8 → K) where
  toFun v := basis K port *ᵥ v
  invFun v := (basis K port).transpose *ᵥ v
  left_inv v := by
    dsimp only
    rw [Matrix.mulVec_mulVec, basis_transpose_mul K h2, Matrix.one_mulVec]
  right_inv v := by
    dsimp only
    rw [Matrix.mulVec_mulVec, basis_mul_transpose K h2, Matrix.one_mulVec]

theorem chart8_dot (K : Type*) [Field K] (h2 : (2 : K) ≠ 0) (port : Fin 120)
    (v w : Fin 8 → K) : (chart8 K h2 port v) ⬝ᵥ (chart8 K h2 port w) = v ⬝ᵥ w := by
  change (basis K port *ᵥ v) ⬝ᵥ (basis K port *ᵥ w) = _
  rw [Matrix.dotProduct_mulVec, Matrix.vecMul_mulVec, basis_transpose_mul K h2,
    Matrix.vecMul_one]

def firstEight {K : Type*} (v : Fin 64 → K) : Fin 8 → K :=
  fun j => v (Fin.castAdd 56 j)

theorem firstEight_add {K : Type*} [Add K] (v w : Fin 64 → K) :
    firstEight (v + w) = firstEight v + firstEight w := rfl

theorem firstEight_smul {K : Type*} [Mul K] (c : K) (v : Fin 64 → K) :
    firstEight (c • v) = c • firstEight v := rfl

def extendEight {K : Type*} (f : (Fin 8 → K) → (Fin 8 → K))
    (v : Fin 64 → K) : Fin 64 → K :=
  fun i => if hi : i.val < 8 then f (firstEight v) ⟨i.val, hi⟩ else v i

theorem firstEight_extendEight {K : Type*} (f : (Fin 8 → K) → (Fin 8 → K))
    (v : Fin 64 → K) : firstEight (extendEight f v) = f (firstEight v) := by
  funext j
  simp [firstEight, extendEight, j.isLt]

theorem extendEight_comp {K : Type*} (f g : (Fin 8 → K) → (Fin 8 → K))
    (v : Fin 64 → K) : extendEight f (extendEight g v) = extendEight (f ∘ g) v := by
  funext i
  by_cases hi : i.val < 8
  · simp [extendEight, hi, firstEight_extendEight]
  · simp [extendEight, hi]

theorem extendEight_id {K : Type*} (v : Fin 64 → K) : extendEight id v = v := by
  funext i
  by_cases hi : i.val < 8 <;> simp [extendEight, firstEight, hi]

def liftChart {K : Type*} (chart : (Fin 8 → K) ≃ (Fin 8 → K)) :
    (Fin 64 → K) ≃ (Fin 64 → K) where
  toFun := extendEight chart
  invFun := extendEight chart.symm
  left_inv v := by
    rw [extendEight_comp]
    have hi : (chart.symm ∘ chart : (Fin 8 → K) → (Fin 8 → K)) = id := by
      funext x
      exact chart.symm_apply_apply x
    rw [hi, extendEight_id]
  right_inv v := by
    rw [extendEight_comp]
    have hi : (chart ∘ chart.symm : (Fin 8 → K) → (Fin 8 → K)) = id := by
      funext x
      exact chart.apply_symm_apply x
    rw [hi, extendEight_id]

def chart64 (K : Type*) [Field K] (h2 : (2 : K) ≠ 0) (port : Fin 120) :
    (Fin 64 → K) ≃ (Fin 64 → K) := liftChart (chart8 K h2 port)

theorem chart64_firstEight (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) (v : Fin 64 → K) :
    firstEight (chart64 K h2 port v) = basis K port *ᵥ firstEight v :=
  firstEight_extendEight _ v

theorem chart64_outside (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) (v : Fin 64 → K) (i : Fin 64) (hi : 8 ≤ i.val) :
    chart64 K h2 port v i = v i := by
  simp [chart64, liftChart, extendEight, Nat.not_lt.mpr hi]

theorem chart64_bijective (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) : Function.Bijective (chart64 K h2 port) :=
  (chart64 K h2 port).bijective

theorem chart64_add (K : Type*) [Field K] (h2 : (2 : K) ≠ 0) (port : Fin 120)
    (v w : Fin 64 → K) :
    chart64 K h2 port (v + w) = chart64 K h2 port v + chart64 K h2 port w := by
  funext i
  by_cases hi : i.val < 8
  · simp [chart64, liftChart, extendEight, chart8, firstEight_add, hi,
      Matrix.mulVec_add, Pi.add_apply]
  · simp [chart64, liftChart, extendEight, hi]

theorem chart64_smul (K : Type*) [Field K] (h2 : (2 : K) ≠ 0) (port : Fin 120)
    (c : K) (v : Fin 64 → K) :
    chart64 K h2 port (c • v) = c • chart64 K h2 port v := by
  funext i
  by_cases hi : i.val < 8
  · simp [chart64, liftChart, extendEight, chart8, firstEight_smul, hi,
      Matrix.mulVec_smul, Pi.smul_apply]
  · simp [chart64, liftChart, extendEight, hi]

/-- Preservation of the ambient dot form, required for genuine orthogonal
cover membership. Bijectivity alone would not establish this property. -/
theorem chart64_dot (K : Type*) [Field K] (h2 : (2 : K) ≠ 0) (port : Fin 120)
    (v w : Fin 64 → K) :
    (∑ i, chart64 K h2 port v i * chart64 K h2 port w i) = ∑ i, v i * w i := by
  rw [Fin.sum_univ_add (a := 8) (b := 56), Fin.sum_univ_add (a := 8) (b := 56)]
  apply congrArg₂ (· + ·)
  · have h := chart8_dot K h2 port (firstEight v) (firstEight w)
    change (∑ i : Fin 8, chart64 K h2 port v (Fin.castAdd 56 i) *
      chart64 K h2 port w (Fin.castAdd 56 i)) = _
    simpa [dotProduct, chart64, liftChart, extendEight, firstEight, Fin.isLt, Fin.castAdd] using h
  · apply Finset.sum_congr rfl
    intro i _
    rw [chart64_outside K h2 port v _ (by exact Nat.le_add_right 8 i.val),
      chart64_outside K h2 port w _ (by exact Nat.le_add_right 8 i.val)]

theorem chart64_symm_dot (K : Type*) [Field K] (h2 : (2 : K) ≠ 0) (port : Fin 120)
    (v w : Fin 64 → K) :
    (∑ i, (chart64 K h2 port).symm v i * (chart64 K h2 port).symm w i) =
      ∑ i, v i * w i := by
  have h := chart64_dot K h2 port ((chart64 K h2 port).symm v)
    ((chart64 K h2 port).symm w)
  simpa only [Equiv.apply_symm_apply] using h.symm

theorem chart64_symm_add (K : Type*) [Field K] (h2 : (2 : K) ≠ 0) (port : Fin 120)
    (v w : Fin 64 → K) :
    (chart64 K h2 port).symm (v + w) =
      (chart64 K h2 port).symm v + (chart64 K h2 port).symm w := by
  apply (chart64 K h2 port).injective
  rw [Equiv.apply_symm_apply, chart64_add, Equiv.apply_symm_apply, Equiv.apply_symm_apply]

theorem chart64_symm_smul (K : Type*) [Field K] (h2 : (2 : K) ≠ 0) (port : Fin 120)
    (c : K) (v : Fin 64 → K) :
    (chart64 K h2 port).symm (c • v) = c • (chart64 K h2 port).symm v := by
  apply (chart64 K h2 port).injective
  rw [Equiv.apply_symm_apply, chart64_smul, Equiv.apply_symm_apply]

/-- Stage 2 exchanges the seven q-perpendicular coordinates 1..7 with the
second exterior block 15..21. The port direction (coordinate 0) is fixed. -/
def stage2Index (i : Fin 64) : Fin 64 :=
  if h : 1 ≤ i.val ∧ i.val < 8 then ⟨i.val + 14, by omega⟩
  else if h : 15 ≤ i.val ∧ i.val < 22 then ⟨i.val - 14, by omega⟩
  else i

theorem stage2Index_involutive : Function.Involutive stage2Index := by
  change ∀ i : Fin 64, stage2Index (stage2Index i) = i
  decide

def stage2Permutation : Equiv.Perm (Fin 64) where
  toFun := stage2Index
  invFun := stage2Index
  left_inv := stage2Index_involutive
  right_inv := stage2Index_involutive

def stage2Coordinates {K : Type*} : (Fin 64 → K) ≃ (Fin 64 → K) where
  toFun v := v ∘ stage2Index
  invFun v := v ∘ stage2Index
  left_inv v := by funext i; exact congrArg v (stage2Index_involutive i)
  right_inv v := by funext i; exact congrArg v (stage2Index_involutive i)

theorem stage2Coordinates_dot (K : Type*) [Field K] (v w : Fin 64 → K) :
    (∑ i, stage2Coordinates v i * stage2Coordinates w i) = ∑ i, v i * w i :=
  Fintype.sum_equiv stage2Permutation _ _ (fun _ => rfl)

/-- Concrete stage-2 data-port route B_q P B_q⁻¹. `sourceRoute64_eq` below
identifies this with the literal source rho15 matrix. This chart result does
not alone establish a complete provider's primitive execution or endpoint. -/
def dataRoute64 (K : Type*) [Field K] (h2 : (2 : K) ≠ 0) (port : Fin 120) :
    (Fin 64 → K) ≃ (Fin 64 → K) :=
  (chart64 K h2 port).symm.trans (stage2Coordinates.trans (chart64 K h2 port))

theorem dataRoute64_dot (K : Type*) [Field K] (h2 : (2 : K) ≠ 0) (port : Fin 120)
    (v w : Fin 64 → K) :
    (∑ i, dataRoute64 K h2 port v i * dataRoute64 K h2 port w i) = ∑ i, v i * w i := by
  change (∑ i, chart64 K h2 port (stage2Coordinates ((chart64 K h2 port).symm v)) i *
    chart64 K h2 port (stage2Coordinates ((chart64 K h2 port).symm w)) i) = _
  rw [chart64_dot, stage2Coordinates_dot, chart64_symm_dot]

theorem dataRoute64_add (K : Type*) [Field K] (h2 : (2 : K) ≠ 0) (port : Fin 120)
    (v w : Fin 64 → K) :
    dataRoute64 K h2 port (v + w) = dataRoute64 K h2 port v + dataRoute64 K h2 port w := by
  change chart64 K h2 port (stage2Coordinates ((chart64 K h2 port).symm (v + w))) = _
  rw [chart64_symm_add]
  change chart64 K h2 port (stage2Coordinates ((chart64 K h2 port).symm v) +
    stage2Coordinates ((chart64 K h2 port).symm w)) = _
  exact chart64_add K h2 port _ _

theorem dataRoute64_smul (K : Type*) [Field K] (h2 : (2 : K) ≠ 0) (port : Fin 120)
    (c : K) (v : Fin 64 → K) :
    dataRoute64 K h2 port (c • v) = c • dataRoute64 K h2 port v := by
  change chart64 K h2 port (stage2Coordinates ((chart64 K h2 port).symm (c • v))) = _
  rw [chart64_symm_smul]
  change chart64 K h2 port (c • stage2Coordinates ((chart64 K h2 port).symm v)) = _
  exact chart64_smul K h2 port _ _

theorem dataRoute64_involutive (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) : Function.Involutive (dataRoute64 K h2 port) := by
  intro v
  change chart64 K h2 port (stage2Coordinates ((chart64 K h2 port).symm
    (chart64 K h2 port (stage2Coordinates ((chart64 K h2 port).symm v))))) = v
  rw [Equiv.symm_apply_apply]
  change chart64 K h2 port ((stage2Coordinates : (Fin 64 → K) ≃ _).symm
    (stage2Coordinates ((chart64 K h2 port).symm v))) = v
  rw [Equiv.symm_apply_apply, Equiv.apply_symm_apply]

/-- The literal source rho15 matrix, reduced by its true denominator four.
PortData checks its integer entries against the source port basis. -/
def route15 (K : Type*) [Field K] (port : Fin 120) : Matrix (Fin 15) (Fin 15) K :=
  fun i j => (quarteredRoute port i j : K) / 4

def expectedRoute15 (K : Type*) [Field K] (port : Fin 120) (i j : Fin 15) : K :=
  if hi : i.val < 8 then
    if hj : j.val < 8 then
      basis K port ⟨i.val, hi⟩ 0 * basis K port ⟨j.val, hj⟩ 0
    else basis K port ⟨i.val, hi⟩ ⟨j.val - 7, by omega⟩
  else if hj : j.val < 8 then
    basis K port ⟨j.val, hj⟩ ⟨i.val - 7, by omega⟩
  else 0

theorem route15_entry (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) (i j : Fin 15) : route15 K port i j = expectedRoute15 K port i j := by
  have h4 : (4 : K) ≠ 0 := by
    convert mul_ne_zero h2 h2 using 1
    norm_num
  simp only [route15, quarteredRoute_exact, expectedRoute15, expectedQuarteredRoute,
    routeExpected]
  split_ifs <;> simp [basis_entry] <;>
    field_simp [h2, h4] <;> ring <;> simp

def gatherStage2 {K : Type*} (v : Fin 64 → K) (i : Fin 15) : K :=
  if hi : i.val < 8 then v ⟨i.val, Nat.lt_trans hi (by decide)⟩
  else v ⟨i.val + 7, by omega⟩

/-- Literal rho15 acting on the source-listed axes [0..7,15..21]. All other
coordinates are retained exactly; its conjugacy with the concrete isometry
is established by `sourceRoute64_eq`. -/
def sourceRoute64 (K : Type*) [Field K] (port : Fin 120) (v : Fin 64 → K)
    (i : Fin 64) : K :=
  if hi : i.val < 8 then (route15 K port *ᵥ gatherStage2 v) ⟨i.val, Nat.lt_trans hi (by decide)⟩
  else if hi : 15 ≤ i.val ∧ i.val < 22 then
    (route15 K port *ᵥ gatherStage2 v) ⟨i.val - 7, by omega⟩
  else v i

theorem sourceRoute64_eq (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) (v : Fin 64 → K) : sourceRoute64 K port v = dataRoute64 K h2 port v := by
  funext i
  by_cases hi : i.val < 8
  · simp [sourceRoute64, hi, Matrix.mulVec, dotProduct, Fin.sum_univ_succ,
      route15_entry K h2, expectedRoute15, gatherStage2,
      dataRoute64, chart64, liftChart, extendEight, chart8,
      stage2Coordinates, firstEight, stage2Index, Matrix.transpose_apply]
    ring
  · by_cases hj : 15 ≤ i.val ∧ i.val < 22
    · have hsub : i.val - 14 < 8 := by omega
      have hsub' : ¬i.val - 7 < 8 := by omega
      have hsub'' : i.val - 7 - 7 = i.val - 14 := by omega
      simp [sourceRoute64, hi, hj, Matrix.mulVec, dotProduct, Fin.sum_univ_succ,
        route15_entry K h2, expectedRoute15, gatherStage2,
        dataRoute64, chart64, liftChart, extendEight, chart8,
        stage2Coordinates, firstEight, stage2Index, Matrix.transpose_apply,
        hsub, hsub', hsub'']
    · simp [sourceRoute64, hi, hj, dataRoute64, chart64, liftChart,
        extendEight, stage2Coordinates, stage2Index]

end PortGeometry

#print axioms PortGeometry.cast_orthogonal
#print axioms PortGeometry.doubled_orthogonal
#print axioms PortGeometry.doubled_row_orthogonal
#print axioms PortGeometry.cast_row_orthogonal
#print axioms PortGeometry.basis_entry
#print axioms PortGeometry.basis_transpose_mul
#print axioms PortGeometry.basis_mul_transpose
#print axioms PortGeometry.firstEight_extendEight
#print axioms PortGeometry.firstEight_add
#print axioms PortGeometry.firstEight_smul
#print axioms PortGeometry.extendEight_comp
#print axioms PortGeometry.extendEight_id
#print axioms PortGeometry.chart64_firstEight
#print axioms PortGeometry.chart64_outside
#print axioms PortGeometry.chart64_bijective
#print axioms PortGeometry.chart64_add
#print axioms PortGeometry.chart64_smul
#print axioms PortGeometry.chart8_dot
#print axioms PortGeometry.chart64_dot
#print axioms PortGeometry.chart64_symm_dot
#print axioms PortGeometry.chart64_symm_add
#print axioms PortGeometry.chart64_symm_smul
#print axioms PortGeometry.stage2Index_involutive
#print axioms PortGeometry.stage2Coordinates_dot
#print axioms PortGeometry.dataRoute64_dot
#print axioms PortGeometry.dataRoute64_add
#print axioms PortGeometry.dataRoute64_smul
#print axioms PortGeometry.dataRoute64_involutive
#print axioms PortGeometry.route15_entry
#print axioms PortGeometry.sourceRoute64_eq
