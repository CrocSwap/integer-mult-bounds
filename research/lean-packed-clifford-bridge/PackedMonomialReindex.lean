import PackedMatrixReindex
import PackedQuadraticReindex

/-!
Literal packed D → P → X → global-phase composition under the accepted
little-endian payload map. Reuses the existing monomial composition theorem;
there is no new circuit induction or selected finite certificate.
Apache-2.0; prepared with OpenAI assistance. See NOTICE.md.
-/
set_option Elab.async false
namespace CurrentMain.PackedMonomialReindex
open Current535PackedCoordinates
open CliffordNineBitDecoder
open CliffordMonomialDecoder
open CliffordChild009Canonical (imagUnit imagUnit_four)
open HyperplaneEnd.Clifford (gC gL cL)
open scoped Matrix

/-- Both source operands fit in the nine-coordinate address domain. -/
theorem source_xor (x y : Packed) :
    HyperplaneEnd.Clifford.fx 512 (x.val ^^^ y.val) = packedXor x y := by
  apply Fin.ext
  change (x.val ^^^ y.val) % 512 = x.val ^^^ y.val
  exact Nat.mod_eq_of_lt (Nat.xor_lt_two_pow (n := 9) x.isLt y.isLt)

noncomputable section

/-- X reads the XOR preimage, which is also the inverse of the offset map. -/
theorem offset_reindex (offset : Nat) (hb : offset < 512) (v : Packed → ℂ) :
    payloadEquiv (gC 512 (.xg offset) v) =
      push (K := ℂ) (offsetEquiv offset) (payloadEquiv v) := by
  funext a
  obtain ⟨x, rfl⟩ := addressEquiv.surjective a
  rw [show addressEquiv x = unpack x from rfl]
  simp only [payload_apply, pack_unpack, push_apply, offsetEquiv_symm_apply, gC]
  have ho : mask offset = unpack (⟨offset, hb⟩ : Packed) := rfl
  rw [ho, ← unpack_xor x ⟨offset, hb⟩, ← source_xor x ⟨offset, hb⟩, pack_unpack]

/-- The stored global phase is retained exactly, without quotienting by phase. -/
theorem phase_reindex (phase : Nat) (v : Packed → ℂ) :
    payloadEquiv (gC 512 (.ph phase) v) =
      diagonal imagUnit (fun _ : Address => phase) (payloadEquiv v) := by
  funext a
  simp only [payload_apply, gC, diagonal_apply, Units.val_pow_eq_pow_val, imagUnit]

/-- The source's four chronological gates equal the accepted decoded monomial
on arbitrary payloads. P reads inverseRows; D is consequently evaluated at the
input/preimage coordinate. Both inverse equations and every length/bound
needed by the primitive representation bridges are explicit. -/
theorem monomial_reindex (rows inverseRows Q alpha : List Nat)
    (hi : inverseRows.length = 9) (hQ : Q.length = 9) (ha : alpha.length = 9)
    (offset phase : Nat) (ho : offset < 512)
    (hf : matrix rows * matrix inverseRows = 1)
    (hb : matrix inverseRows * matrix rows = 1) (v : Packed → ℂ) :
    payloadEquiv (cL 512 [.dg Q alpha, .pm rows inverseRows, .xg offset, .ph phase] v) =
      (monomial rows inverseRows Q alpha offset phase hf hb).operator (payloadEquiv v) := by
  have hd (w : Packed → ℂ) :
      payloadEquiv (gC 512 (.dg Q alpha) w) =
        diagonal imagUnit (qvalue Q alpha) (payloadEquiv w) := by
    rw [PackedQuadraticReindex.diagonal_reindex Q alpha hQ ha w]
    funext a
    simp only [diagonal_apply, Units.val_pow_eq_pow_val, imagUnit]
  simp only [monomial, RankOneRecipeCertificate.Monomial.operator]
  rw [← circuit_eq_decoded imagUnit imagUnit_four]
  simp only [HyperplaneEnd.Clifford.cL_cons, HyperplaneEnd.Clifford.cL_nil,
    LinearMap.comp_apply, LinearMap.id_apply, HyperplaneEnd.Clifford.gL_apply,
    circuit, LinearEquiv.trans_apply]
  rw [phase_reindex, offset_reindex offset ho,
    PackedMatrixReindex.permutation_reindex rows inverseRows hi hf hb, hd]

end
end CurrentMain.PackedMonomialReindex

#print axioms CurrentMain.PackedMonomialReindex.source_xor
#print axioms CurrentMain.PackedMonomialReindex.offset_reindex
#print axioms CurrentMain.PackedMonomialReindex.phase_reindex
#print axioms CurrentMain.PackedMonomialReindex.monomial_reindex
