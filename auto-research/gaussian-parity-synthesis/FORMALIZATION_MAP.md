# Formal scope

`DyadicCertificates.lean` and `GaussianLattice.lean` are unchanged from PR45.
`GaussianScalarCircuits.lean` extends them with canonical normalization,
heterogeneous exact inverse restoration, mixed-center image contracts,
arbitrary integer superposition, collected side corrections, dirty differences,
common-phase conditions, and the generic complete image guard.
`CommunityPrecisionProfile.lean` checks the 29 PR46 profile rows and proves
the completed-child charge bound for every natural parallel width.

The actual full h28 producer linkage is independently audited using integer
coefficient bitplanes and all 10,732,176 source/target pairs. Lean's abstract
image-guard theorem assumes the decoder's left-inverse contract; the concrete
Python guard is linked to that finite producer by this independent audit.
Lean does not prove the full physical framed network, frame transport, the
complete multiplication theorem, analytic assumptions, or tape costs.

`pi_exact.py` mirrors the proved normalization and phase/halving representation.
Its general add/multiply implementations and finite endpoint simulations have
independent Fraction controls, rather than a claimed full Python-to-Lean
refinement proof.

`GaussianTensorExecution.lean` defines an actual complete recursive cube
and executes every forward/inverse C axis, proving inverse restoration for
every dimension and arbitrary values with charged denominator tags. It links
the terminal p+ceil(D/2) binary grid to the executed tensor, retains odd-depth
parity, and proves sharpness using its actual impulse computation. This is a
formal finite tensor algorithm, without a full physical/tape compiler proof.

All theorem declarations audited (including imports): 168; 99 are new beyond
the original 69-theorem package.

- `GaussianParity.GInt.ext`
- `GaussianParity.residue_zero_iff`
- `GaussianParity.dividePi_exact_iff`
- `GaussianParity.dividePi_mulPi`
- `GaussianParity.butterfly_integral_iff`
- `GaussianParity.butterfly_exact`
- `GaussianParity.butterfly_sameResidue`
- `GaussianParity.butterfly_square`
- `GaussianParity.residue_mulI`
- `GaussianParity.residue_add`
- `GaussianParity.residue_mulPi`
- `GaussianParity.component_parity_implies_sameResidue`
- `GaussianParity.cross_parity_example`
- `GaussianParity.changed_pairing_obstruction`
- `GaussianParity.piIter_mulPi`
- `GaussianParity.piIter_add`
- `GaussianParity.piIter_commute`
- `GaussianParity.mulPi_injective`
- `GaussianParity.piIter_injective`
- `GaussianParity.SameValue.refl`
- `GaussianParity.SameValue.symm`
- `GaussianParity.SameValue.trans`
- `GaussianParity.certifiedButterfly_contract`
- `GaussianParity.certifiedButterfly_refines`
- `GaussianParity.certifiedButterfly_exponent_bound`
- `GaussianParity.inverseButterfly_eq_swap`
- `GaussianParity.inverseButterfly_after`
- `GaussianParity.butterfly_fourth`
- `GaussianParity.doubleButterfly_joint_parity`
- `GaussianParity.sharedDefect_is_bit`
- `GaussianParity.sharedDefect_zero_iff`
- `GaussianParity.shared_defect_reconstruction`
- `GaussianParity.doubleButterfly_exact`
- `GaussianParity.halfHadamard_exact_iff`
- `GaussianParity.cross_parity_fails_halfHadamard`
- `GaussianParity.raiseTo_sameValue`
- `GaussianParity.alignedButterfly_input_exact`
- `GaussianParity.alignedButterfly_refines`
- `GaussianParity.mulPi_square`
- `GaussianParity.mulI_scale`
- `GaussianParity.scale_mul`
- `GaussianParity.repeatPi_even`
- `GaussianParity.mulI_negI`
- `GaussianParity.negI_mulI`
- `GaussianParity.repeatI_commute`
- `GaussianParity.repeatI_negI_commute`
- `GaussianParity.repeatI_cancel`
- `GaussianParity.mulPi_scale`
- `GaussianParity.repeatPi_odd`
- `GaussianParity.pi_even_ideal`
- `GaussianParity.pi_odd_ideal`
- `GaussianParity.odd_ideal_parity`
- `GaussianParity.pi_not_binary_one`
- `GaussianParity.even_binary_conversion`
- `GaussianParity.odd_binary_conversion`
- `GaussianParity.residue_negI`
- `GaussianParity.repeatNegI_residue`
- `GaussianParity.odd_binary_numerator_parity`
- `GaussianParity.binary_grid_conversion`
- `GaussianParity.binary_one_residue_zero`
- `GaussianParity.even_impulse_primitive`
- `GaussianParity.bothOdd_negI`
- `GaussianParity.bothOdd_repeatNegI`
- `GaussianParity.odd_impulse_primitive`
- `GaussianParity.scale_injective`
- `GaussianParity.even_grid_sharp`
- `GaussianParity.odd_grid_sharp`
- `GaussianParity.gaussianMul_pi_pi`
- `GaussianParity.two_pi_factors_binary`
- `GaussianSynthesis.cancelPi_sameValue`
- `GaussianSynthesis.normalizeCore_sound`
- `GaussianSynthesis.normalize_sound`
- `GaussianSynthesis.normalizeCore_canonical`
- `GaussianSynthesis.normalize_canonical`
- `GaussianSynthesis.normalize_fixed`
- `GaussianSynthesis.normalize_idempotent`
- `GaussianSynthesis.normalizeCore_exponent_bound`
- `GaussianSynthesis.normalize_zero`
- `GaussianSynthesis.positive_piIter_residue`
- `GaussianSynthesis.canonical_tags_equal`
- `GaussianSynthesis.canonical_unique`
- `GaussianSynthesis.normalize_congr`
- `GaussianSynthesis.mixed_center_image`
- `GaussianSynthesis.fresh_total_recovery`
- `GaussianSynthesis.fresh_doubled_center`
- `GaussianSynthesis.fresh_scatter_denominator_cancellation`
- `GaussianSynthesis.corrected_bulk_coefficient`
- `GaussianSynthesis.dirty_center_obstruction`
- `GaussianSynthesis.dirty_center_difference_is_fresh`
- `GaussianSynthesis.centerColumn_image`
- `GaussianSynthesis.centerPlus_image`
- `GaussianSynthesis.arbitrary_fresh_columns_image`
- `GaussianSynthesis.arbitrary_fresh_columns_total`
- `GaussianSynthesis.dirty_update_difference_image`
- `GaussianSynthesis.raw_dirty_update_defect`
- `GaussianSynthesis.corrected_scatter_column_exact`
- `GaussianSynthesis.corrected_scatter_sum_exact`
- `GaussianSynthesis.corrected_scatter_sum_integral`
- `GaussianSynthesis.fresh_bulk_half_sharp`
- `GaussianSynthesis.rawC_left_square`
- `GaussianSynthesis.rawC_right_square`
- `GaussianSynthesis.two_pi_numerator_sameValue`
- `GaussianSynthesis.rawC_square_exact`
- `GaussianSynthesis.rawC_inverse_exact`
- `GaussianSynthesis.heterogeneous_inverse_restores`
- `GaussianSynthesis.canonical_inverse_restores`
- `GaussianSynthesis.phase_inverse_restores`
- `GaussianSynthesis.half_double_restores`
- `GaussianSynthesis.gaussian_update_difference`
- `GaussianSynthesis.mulI_difference`
- `GaussianSynthesis.phase_difference`
- `GaussianSynthesis.matching_phase_dirty_difference`
- `GaussianSynthesis.mismatched_phase_image_obstruction`
- `GaussianSynthesis.producer_image_iff_roundtrip`
- `GaussianSynthesis.producer_projection_idempotent`
- `GaussianSynthesis.image_difference_recovers`
- `GaussianSynthesis.recoverIfImage_exact`
- `GaussianSynthesis.recoverIfImage_rejects`
- `GaussianSynthesis.certified_dirty_recovery_and_restore`
- `GaussianSynthesis.phase_scale`
- `GaussianSynthesis.common_phase_center_image`
- `GaussianSynthesis.per_role_phase_image_obstruction`
- `GaussianSynthesis.canonical_tag_minimal`
- `GaussianSynthesis.normalized_tag_minimal`
- `CommunityPrecision.ceilHalf_subadditive`
- `CommunityPrecision.ceilHalf_mul_bound`
- `CommunityPrecision.arbitrary_profile_bound`
- `CommunityPrecision.profile_rank_mass`
- `CommunityPrecision.profile_odd_multiplicity`
- `CommunityPrecision.profile_precision_charge`
- `CommunityPrecision.profile_call_count`
- `CommunityPrecision.certified_all_width_bound`
- `CommunityPrecision.profile_saving`
- `GaussianTensorExecution.cubeMap_congr`
- `GaussianTensorExecution.cubeMap_comp`
- `GaussianTensorExecution.cubeMap_zip`
- `GaussianTensorExecution.mulPi_add`
- `GaussianTensorExecution.mulPi_mulI`
- `GaussianTensorExecution.cubePi_add`
- `GaussianTensorExecution.cubePi_I`
- `GaussianTensorExecution.axisForward_pi`
- `GaussianTensorExecution.axisInverse_pi`
- `GaussianTensorExecution.inverse_pi`
- `GaussianTensorExecution.cubePiIter_succ`
- `GaussianTensorExecution.cubePiIter_add`
- `GaussianTensorExecution.cube_ext`
- `GaussianTensorExecution.get_map`
- `GaussianTensorExecution.get_zip`
- `GaussianTensorExecution.cubeMap_id`
- `GaussianTensorExecution.inverse_piIter`
- `GaussianTensorExecution.axis_inverse_forward`
- `GaussianTensorExecution.inverse_forward`
- `GaussianTensorExecution.shifted_tag_sameValue`
- `GaussianTensorExecution.inverse_forward_leaf_sameValue`
- `GaussianTensorExecution.inverse_forward_leaf_canonical`
- `GaussianTensorExecution.repeatPi_eq_piIter`
- `GaussianTensorExecution.forward_leaf_binary_grid`
- `GaussianTensorExecution.cubeI_zero`
- `GaussianTensorExecution.cubeAdd_zero_left`
- `GaussianTensorExecution.forward_zero`
- `GaussianTensorExecution.forward_impulse_first`
- `GaussianTensorExecution.forward_even_grid_sharp`
- `GaussianTensorExecution.forward_odd_grid_sharp`
- `GaussianTensorExecution.execute_inverse_forward_exact`
- `GaussianTensorExecution.execute_inverse_forward_canonical`
- `GaussianTensorExecution.execute_forward_tag`
- `GaussianTensorExecution.forward_binary_input_grid`
- `GaussianTensorExecution.forward_odd_binary_sublattice`
