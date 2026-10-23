import Current535PackedCoordinates
import PR593Clifford

/-!
Exact packed bit-zero Gaussian gate under the accepted little-endian address
and payload equivalence. Reuses PR593's exact complex gate semantics and the
accepted Gaussian C0; it adds no circuit induction or selected record test.
Apache-2.0; see NOTICE.md.
-/
set_option Elab.async false
namespace CurrentMain.PackedGaussianReindex
open Current535PackedCoordinates
open CliffordNineBitDecoder (Address mask gaussian)

/-- The source modulo-512 XOR and the certified fixed-width XOR agree. -/
theorem source_xor_one (x : Packed) :
    HyperplaneEnd.Clifford.fx 512 (x.val ^^^ 1) = packedXor x 1 := by
  apply Fin.ext
  change (x.val ^^^ 1) % 512 = x.val ^^^ 1
  exact Nat.mod_eq_of_lt (Nat.xor_lt_two_pow (n := 9) x.isLt (by decide))

theorem unpack_source_flip (x : Packed) :
    unpack (HyperplaneEnd.Clifford.fx 512 (x.val ^^^ 1)) =
      CliffordNineBitDecoder.flipZero (unpack x) := by
  change unpack (HyperplaneEnd.Clifford.fx 512 (x.val ^^^ 1)) = unpack x + mask 1
  rw [source_xor_one, unpack_xor, unpack_one]

noncomputable section

/-- The exact dyadic C gate, including its complex phase, becomes Gaussian C0. -/
theorem gaussian_reindex (v : Packed → ℂ) :
    payloadEquiv (HyperplaneEnd.Clifford.gC 512 (.cg 1 true) v) =
      gaussian (payloadEquiv v) := by
  funext a
  obtain ⟨x, rfl⟩ := addressEquiv.surjective a
  change payloadEquiv (HyperplaneEnd.Clifford.gC 512 (.cg 1 true) v) (unpack x) =
    gaussian (payloadEquiv v) (unpack x)
  rw [payload_apply, pack_unpack, CliffordNineBitDecoder.gaussian_apply,
    ← unpack_source_flip x]
  simp only [payload_apply, pack_unpack]
  change ((1 + (1 : ℂ) * Complex.I) * v x +
    (1 - (1 : ℂ) * Complex.I) * v (HyperplaneEnd.Clifford.fx 512 (x.val ^^^ 1))) / 2 =
    RankOneRecipeCertificate.ca * v x +
      RankOneRecipeCertificate.cb * v (HyperplaneEnd.Clifford.fx 512 (x.val ^^^ 1))
  simp only [RankOneRecipeCertificate.ca, RankOneRecipeCertificate.cb,
    GaussianPhaseNormalization.a, GaussianPhaseNormalization.b, div_eq_mul_inv]
  ring

/-- Explicit conjugation for an arbitrary nine-coordinate payload. -/
theorem gaussian_conjugation (v : Address → ℂ) :
    payloadEquiv
      (HyperplaneEnd.Clifford.gC 512 (.cg 1 true) (payloadEquiv.symm v)) = gaussian v := by
  simpa only [LinearEquiv.apply_symm_apply] using gaussian_reindex (payloadEquiv.symm v)

end
end CurrentMain.PackedGaussianReindex

#print axioms CurrentMain.PackedGaussianReindex.source_xor_one
#print axioms CurrentMain.PackedGaussianReindex.unpack_source_flip
#print axioms CurrentMain.PackedGaussianReindex.gaussian_reindex
#print axioms CurrentMain.PackedGaussianReindex.gaussian_conjugation
