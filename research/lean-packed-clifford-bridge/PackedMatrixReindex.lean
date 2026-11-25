import PackedParityReindex

/-!
Symbolic source-list assembly and inverse matrix reads under packed coordinates.
Apache-2.0; prepared with OpenAI assistance. See NOTICE.md.
The paired matrix inverse equations remain certified caller data. This module
only binds the source mv evaluator to the existing raw9 matrix interpretation.
-/
set_option Elab.async false
namespace CurrentMain.PackedMatrixReindex
open Current535PackedCoordinates
open PackedParityReindex
open CliffordNineBitDecoder
open HyperplaneEnd.Clifford (mv mvAux par9)
open scoped BigOperators Matrix

private theorem mvAux_bits (rows : List Nat) (x w : Nat) :
    mvAux rows x w =
      w * (BitVec.ofBoolListLE (rows.map (fun row => par9 (row &&& x)))).toNat := by
  induction rows generalizing w with
  | nil => simp [mvAux, BitVec.ofBoolListLE]
  | cons row rows ih =>
    simp only [mvAux, List.map_cons, BitVec.ofBoolListLE, BitVec.toNat_concat]
    rw [ih]
    cases h : par9 (row &&& x) <;> simp [h] <;> ring

/-- The source emits each row parity at its little-endian row index. -/
theorem mv_bits (rows : List Nat) (x : Nat) :
    mv rows x =
      (BitVec.ofBoolListLE (rows.map (fun row => par9 (row &&& x)))).toNat := by
  simpa only [mv, one_mul] using mvAux_bits rows x 1

/-- Nine source rows fit in the packed address domain without modulo loss. -/
theorem mv_bound (rows : List Nat) (hl : rows.length = 9) (x : Nat) :
    mv rows x < 512 := by
  rw [mv_bits]
  simpa only [List.length_map, hl] using
    (BitVec.ofBoolListLE (rows.map (fun row => par9 (row &&& x)))).isLt

/-- Exact source mv-to-matrix correspondence for every address and nine rows. -/
theorem packed_matrix (rows : List Nat) (hl : rows.length = 9) (x : Packed) :
    unpack (HyperplaneEnd.Clifford.fx 512 (mv rows x.val)) =
      matrix rows *ᵥ unpack x := by
  funext i
  change (if (mv rows x.val % 512).testBit i.val then (1 : Bit) else 0) = _
  rw [Nat.mod_eq_of_lt (mv_bound rows hl x.val), mv_bits]
  change boolBit ((BitVec.ofBoolListLE
    (rows.map (fun row => par9 (row &&& x.val)))).getLsbD i.val) = _
  rw [BitVec.getLsbD_ofBoolListLE]
  have hmap : (rows.map (fun row => par9 (row &&& x.val))).getD i.val false =
      par9 ((rows.getD i.val 0) &&& x.val) := by
    simp only [List.getD_eq_getElem?_getD, List.getElem?_map]
    cases h : rows[i.val]? <;> simp [h, HyperplaneEnd.Clifford.par9]
  rw [hmap, packed_parity_dot]
  rfl

noncomputable section
private theorem permutation_normal_form (rows inverseRows : List Nat)
    (hf : matrix rows * matrix inverseRows = 1)
    (hb : matrix inverseRows * matrix rows = 1) (v : Packed → ℂ) (x : Packed) :
    (payloadEquiv (HyperplaneEnd.Clifford.gC 512 (.pm rows inverseRows) v)
        (addressEquiv x) =
      CliffordMonomialDecoder.push (K := ℂ)
        (coordinateEquiv rows inverseRows hf hb).toEquiv (payloadEquiv v)
        (addressEquiv x)) ↔
    v (HyperplaneEnd.Clifford.fx 512 (mv inverseRows x.val)) =
      v (pack (matrix inverseRows *ᵥ unpack x)) := by
  rw [show addressEquiv x = unpack x from rfl]
  simp only [payload_apply, pack_unpack, CliffordMonomialDecoder.push_apply,
    LinearEquiv.coe_symm_toEquiv, coordinateEquiv_symm_apply,
    HyperplaneEnd.Clifford.gC]

/-- Source P reads the inverse rows. Its payload action is the accepted push
along the certified coordinate equivalence, rather than the forward read. -/
theorem permutation_reindex (rows inverseRows : List Nat)
    (hi : inverseRows.length = 9)
    (hf : matrix rows * matrix inverseRows = 1)
    (hb : matrix inverseRows * matrix rows = 1) (v : Packed → ℂ) :
    payloadEquiv (HyperplaneEnd.Clifford.gC 512 (.pm rows inverseRows) v) =
      CliffordMonomialDecoder.push (K := ℂ)
        (coordinateEquiv rows inverseRows hf hb).toEquiv (payloadEquiv v) := by
  funext a
  obtain ⟨x, rfl⟩ := addressEquiv.surjective a
  apply (permutation_normal_form rows inverseRows hf hb v x).2
  rw [← packed_matrix inverseRows hi x, pack_unpack]
end
end CurrentMain.PackedMatrixReindex

#print axioms CurrentMain.PackedMatrixReindex.mv_bits
#print axioms CurrentMain.PackedMatrixReindex.mv_bound
#print axioms CurrentMain.PackedMatrixReindex.packed_matrix
#print axioms CurrentMain.PackedMatrixReindex.permutation_reindex
