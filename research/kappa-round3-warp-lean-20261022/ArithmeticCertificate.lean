/- Exact source-formula rational certificates. Apache-2.0.
Substantial OpenAI Codex assistance. Signed Cao Yifan.
No claim here that externally computed enclosures bound real powers. -/
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Positivity

set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace KappaChangedG.Arithmetic

def kappa : ℚ := (9443 / 3125000 : ℚ)
def tested : ℚ := (302177 / 100000000 : ℚ)
def complexUniformSaving : ℚ := (1057619 / 350000000 : ℚ)
def b : ℚ := (2115237 / 700000000 : ℚ)
def a : ℚ := (528809 / 175000000 : ℚ)
def q : ℚ := (423047 / 140000000 : ℚ)
def epsilon : ℚ := (699999999 / 700000000 : ℚ)
def beta : ℚ := (699999997 / 700000000 : ℚ)
def r0 : ℚ := (1 / 7000000000 : ℚ)
def stop : ℚ := (1 / 700000000 : ℚ)
def layout : ℚ := (1 / 700000000 : ℚ)
def bitSaving : ℚ := (17 / 5000 : ℚ)
def oldBaseline : ℚ := (865485209599581851369 / 500000000000000000000000 : ℚ)
def sigma : ℚ := 1-b
def tau : ℚ := 1-a
def internal : ℚ := tau+(1-stop)*max (sigma-tau) 0
def leaf : ℚ := sigma+stop*(1-sigma)
def lam : ℚ := 1-(q+a)/2
def capConstant : ℚ := 3/32
def xi : ℚ := epsilon*(1+q)-capConstant+layout
def key : ℚ := beta+1-epsilon

def margin_main_transform : ℚ := (epsilon * q)
def margin_global_coordinate_router : ℚ := a
def margin_fused_gaussian : ℚ := ((1 - epsilon) + (q * beta))
def margin_group_bit_router : ℚ := ((1 - epsilon) + (a * beta))
def margin_group_scans : ℚ := ((1 - epsilon) + beta)
def margin_boundary_algebraic_matrix : ℚ := ((capConstant + xi) - epsilon)
def margin_sparse_union_movement : ℚ := ((xi + (1 / 2)) - epsilon)
def margin_polynomial_products : ℚ := epsilon
def margin_microbox_face_corrections : ℚ := (1 - ((((epsilon + beta) + 48) - 128) + 2))
def outerSlacks : List (String × ℚ) := [
  ("actual_bit_above_effective", (bitSaving - a)),
  ("complex_above_effective", (b - a)),
  ("q_positive", q),
  ("complex_endpoint", (b - q)),
  ("q_below_effective", (a - q)),
  ("stop_positive", stop),
  ("stop_below_one", (1 - stop)),
  ("leaf_saving_above_effective", (((1 - stop) * b) - a)),
  ("q_below_internal", ((1 - internal) - q)),
  ("q_below_leaf", ((1 - leaf) - q)),
  ("lambda_above_tau", (lam - tau)),
  ("lambda_above_sigma", (lam - sigma)),
  ("lambda_above_internal", (lam - internal)),
  ("lambda_prime_above_lambda", ((1 - q) - lam)),
  ("lambda_prime_above_leaf", ((1 - q) - leaf)),
  ("epsilon_positive", epsilon),
  ("epsilon_below_one", (1 - epsilon)),
  ("cap_above_band", (xi - (1 / 2))),
  ("cap_below_cell", (epsilon - xi)),
  ("group_positive", beta),
  ("group_below_dimension", (epsilon - beta)),
  ("support_router_span", (1 - beta)),
  ("group_gauge_power_slack", (((1 - ((2 * xi) - 2)) - r0) - beta)),
  ("actual_logarithmic_group_guard", ((1 - ((2 * xi) - 2)) - beta)),
  ("global_gamma_power_slack", ((1 - epsilon) - r0)),
  ("actual_logarithmic_gamma_guard", (1 - epsilon)),
  ("alpha_logarithm_absorption", r0),
  ("group_key_fits_record", (1 - key)),
  ("membership_arithmetic_fits_record", ((1 - beta) - (2 * (1 - epsilon)))),
  ("microbox_halo_volume", ((128 - 48) - beta)),
  ("positive_layout_slack", layout),
  ("short_record_fallback", (epsilon - a)),
  ("complex_below_one_over_32", ((1 / 32) - b)),
  ("strassen_integer_power_gap", ((2 ^ 45) - (7 ^ 16))),
  ("theta_positive_polynomial_power", 2),
  ("cap_below_phase_cell_power", (2 - xi)),
  ("halo_covers_generic_inverse_radius", (48 - 43)),
  ("union_tag_work_per_visit_fits_record", (1 - beta)),
  ("union_header_fits_record", (1 - beta)),
  ("source_axis_superpolynomial", (1 - epsilon)),
  ("gaussian_above_main", (margin_fused_gaussian - margin_main_transform)),
  ("new_complex_uniform_saving_above_b", (complexUniformSaving - b)),
  ("improvement_over_user_baseline", (kappa - oldBaseline)),
  ("new_semantic_guard_with_C1_one", (1 - epsilon)),
  ("fine_prime_halo_umbrella", (10 - (((2 * 2) + 2) + (1 / 2)))),
  ("main_transform_above_kappa", margin_main_transform-kappa),
  ("global_coordinate_router_above_kappa", margin_global_coordinate_router-kappa),
  ("fused_gaussian_above_kappa", margin_fused_gaussian-kappa),
  ("group_bit_router_above_kappa", margin_group_bit_router-kappa),
  ("group_scans_above_kappa", margin_group_scans-kappa),
  ("boundary_algebraic_matrix_above_kappa", margin_boundary_algebraic_matrix-kappa),
  ("sparse_union_movement_above_kappa", margin_sparse_union_movement-kappa),
  ("polynomial_products_above_kappa", margin_polynomial_products-kappa),
  ("microbox_face_corrections_above_kappa", margin_microbox_face_corrections-kappa)]
def outerSlacksRecorded : List (String × ℚ) := [
  ("actual_bit_above_effective", (66191 / 175000000 : ℚ)),
  ("complex_above_effective", (1 / 700000000 : ℚ)),
  ("q_positive", (423047 / 140000000 : ℚ)),
  ("complex_endpoint", (1 / 350000000 : ℚ)),
  ("q_below_effective", (1 / 700000000 : ℚ)),
  ("stop_positive", (1 / 700000000 : ℚ)),
  ("stop_below_one", (699999999 / 700000000 : ℚ)),
  ("leaf_saving_above_effective", (697884763 / 490000000000000000 : ℚ)),
  ("q_below_internal", (1 / 700000000 : ℚ)),
  ("q_below_leaf", (1397884763 / 490000000000000000 : ℚ)),
  ("lambda_above_tau", (1 / 1400000000 : ℚ)),
  ("lambda_above_sigma", (3 / 1400000000 : ℚ)),
  ("lambda_above_internal", (1 / 1400000000 : ℚ)),
  ("lambda_prime_above_lambda", (1 / 1400000000 : ℚ)),
  ("lambda_prime_above_leaf", (1397884763 / 490000000000000000 : ℚ)),
  ("epsilon_positive", (699999999 / 700000000 : ℚ)),
  ("epsilon_below_one", (1 / 700000000 : ℚ)),
  ("cap_above_band", (40108632899576953 / 98000000000000000 : ℚ)),
  ("cap_below_cell", (8891366960423047 / 98000000000000000 : ℚ)),
  ("group_positive", (699999997 / 700000000 : ℚ)),
  ("group_below_dimension", (1 / 350000000 : ℚ)),
  ("support_router_span", (3 / 700000000 : ℚ)),
  ("group_gauge_power_slack", (8891367303423047 / 49000000000000000 : ℚ)),
  ("actual_logarithmic_group_guard", (8891367310423047 / 49000000000000000 : ℚ)),
  ("global_gamma_power_slack", (9 / 7000000000 : ℚ)),
  ("actual_logarithmic_gamma_guard", (1 / 700000000 : ℚ)),
  ("alpha_logarithm_absorption", (1 / 7000000000 : ℚ)),
  ("group_key_fits_record", (1 / 350000000 : ℚ)),
  ("membership_arithmetic_fits_record", (1 / 700000000 : ℚ)),
  ("microbox_halo_volume", (55300000003 / 700000000 : ℚ)),
  ("positive_layout_slack", (1 / 700000000 : ℚ)),
  ("short_record_fallback", (697884763 / 700000000 : ℚ)),
  ("complex_below_one_over_32", (19759763 / 700000000 : ℚ)),
  ("strassen_integer_power_gap", (1951441519231 / 1 : ℚ)),
  ("theta_positive_polynomial_power", (2 / 1 : ℚ)),
  ("cap_below_phase_cell_power", (106891367100423047 / 98000000000000000 : ℚ)),
  ("halo_covers_generic_inverse_radius", (5 / 1 : ℚ)),
  ("union_tag_work_per_visit_fits_record", (3 / 700000000 : ℚ)),
  ("union_header_fits_record", (3 / 700000000 : ℚ)),
  ("source_axis_superpolynomial", (1 / 700000000 : ℚ)),
  ("gaussian_above_main", (69576953 / 49000000000000000 : ℚ)),
  ("new_complex_uniform_saving_above_b", (1 / 700000000 : ℚ)),
  ("improvement_over_user_baseline", (645394790400418148631 / 500000000000000000000000 : ℚ)),
  ("new_semantic_guard_with_C1_one", (1 / 700000000 : ℚ)),
  ("fine_prime_halo_umbrella", (7 / 2 : ℚ)),
  ("main_transform_above_kappa", (419576953 / 98000000000000000 : ℚ)),
  ("global_coordinate_router_above_kappa", (1 / 175000000 : ℚ)),
  ("fused_gaussian_above_kappa", (558730859 / 98000000000000000 : ℚ)),
  ("group_bit_router_above_kappa", (873413573 / 122500000000000000 : ℚ)),
  ("group_scans_above_kappa", (348942383 / 350000000 : ℚ)),
  ("boundary_algebraic_matrix_above_kappa", (559576953 / 98000000000000000 : ℚ)),
  ("sparse_union_movement_above_kappa", (39812500559576953 / 98000000000000000 : ℚ)),
  ("polynomial_products_above_kappa", (697884767 / 700000000 : ℚ)),
  ("microbox_face_corrections_above_kappa", (13474471193 / 175000000 : ℚ))]
theorem outerSlacks_source_equality : outerSlacks = outerSlacksRecorded := by
  norm_num [outerSlacks, outerSlacksRecorded, kappa, tested, complexUniformSaving, b, a, q, epsilon, beta, r0, stop, layout, bitSaving, oldBaseline, sigma, tau, internal, leaf, lam, capConstant, xi, key, margin_main_transform, margin_global_coordinate_router, margin_fused_gaussian, margin_group_bit_router, margin_group_scans, margin_boundary_algebraic_matrix, margin_sparse_union_movement, margin_polynomial_products, margin_microbox_face_corrections]
theorem outerSlacks_all_positive : outerSlacks.all (fun p => decide (0 < p.2)) = true := by
  apply List.all_eq_true.mpr
  norm_num [outerSlacks, kappa, tested, complexUniformSaving, b, a, q, epsilon, beta, r0, stop, layout, bitSaving, oldBaseline, sigma, tau, internal, leaf, lam, capConstant, xi, key, margin_main_transform, margin_global_coordinate_router, margin_fused_gaussian, margin_group_bit_router, margin_group_scans, margin_boundary_algebraic_matrix, margin_sparse_union_movement, margin_polynomial_products, margin_microbox_face_corrections]
theorem outerSlacks_count : outerSlacks.length = 54 := by decide

def functionalSlacks : List (String × ℚ) := [
  ("new_semantic_group_guard", (1 - beta)),
  ("new_BIT_row_stock_sublinear_in_active_group", (beta * (1 - (3 / 1000)))),
  ("fixed_halo_explicit_metadata_branch", ((((128 - 48) - epsilon) - beta) - 1)),
  ("actual_new_BIT_stock_sublinear", beta*(1-(4/1000)))]
def functionalSlacksRecorded : List (String × ℚ) := [
  ("new_semantic_group_guard", (3 / 700000000 : ℚ)),
  ("new_BIT_row_stock_sublinear_in_active_group", (697899997009 / 700000000000 : ℚ)),
  ("fixed_halo_explicit_metadata_branch", (13475000001 / 175000000 : ℚ)),
  ("actual_new_BIT_stock_sublinear", (174299999253 / 175000000000 : ℚ))]
theorem functionalSlacks_source_equality : functionalSlacks = functionalSlacksRecorded := by
  norm_num [functionalSlacks, functionalSlacksRecorded, kappa, tested, complexUniformSaving, b, a, q, epsilon, beta, r0, stop, layout, bitSaving, oldBaseline, sigma, tau, internal, leaf, lam, capConstant, xi, key, margin_main_transform, margin_global_coordinate_router, margin_fused_gaussian, margin_group_bit_router, margin_group_scans, margin_boundary_algebraic_matrix, margin_sparse_union_movement, margin_polynomial_products, margin_microbox_face_corrections]
theorem functionalSlacks_all_positive : functionalSlacks.all (fun p => decide (0 < p.2)) = true := by
  apply List.all_eq_true.mpr
  norm_num [functionalSlacks, kappa, tested, complexUniformSaving, b, a, q, epsilon, beta, r0, stop, layout, bitSaving, oldBaseline, sigma, tau, internal, leaf, lam, capConstant, xi, key, margin_main_transform, margin_global_coordinate_router, margin_fused_gaussian, margin_group_bit_router, margin_group_scans, margin_boundary_algebraic_matrix, margin_sparse_union_movement, margin_polynomial_products, margin_microbox_face_corrections]
theorem functionalSlacks_count : functionalSlacks.length = 4 := by decide

theorem claimed_saving : kappa = 9443/3125000 := by
  norm_num [kappa]
theorem strict_improvement : (37769/12500000 : ℚ) < kappa := by
  norm_num [kappa]
theorem tested_above_kappa : kappa < tested := by
  norm_num [kappa, tested]
theorem explicit_gap : (tested-kappa)/7 = (1/700000000 : ℚ) := by
  norm_num [kappa, tested]
theorem splitting_base_gap : (20:ℕ)^64 < 21^63 := by decide
theorem tail_decay : (97/100 : ℚ)^128 < 1/16 := by norm_num
theorem normalized_completion : (1/(1+1024*(1/1000000000))+4/(2:ℚ)^32) < 1 := by norm_num
theorem shifted_exit_capacity : 2*((20:ℕ)^1024)^64 ≤ ((145:ℕ)^1024)^63 := by decide
theorem finite_threshold : 700000000*44836 = (31385200000000:ℕ) := by decide
theorem finite_compiler_wins : ((700000000:ℕ)*44836+1)^1000 < 2^44836 := by decide
theorem previous_integer_fails : ¬ (((700000000:ℕ)*44835+1)^1000 < 2^44835) := by decide
theorem local_route_count : (3298+2*408+688)*1000 = (4802000:ℕ) := by decide
theorem local_budget : (158168+4802000:ℕ) < 10000000 := by decide
theorem controller_budget : (181098496:ℕ) < 1000000000 := by decide

end KappaChangedG.Arithmetic

#print axioms KappaChangedG.Arithmetic.outerSlacks_source_equality
#print axioms KappaChangedG.Arithmetic.outerSlacks_all_positive
#print axioms KappaChangedG.Arithmetic.functionalSlacks_source_equality
#print axioms KappaChangedG.Arithmetic.functionalSlacks_all_positive
#print axioms KappaChangedG.Arithmetic.claimed_saving
#print axioms KappaChangedG.Arithmetic.strict_improvement
#print axioms KappaChangedG.Arithmetic.tested_above_kappa
#print axioms KappaChangedG.Arithmetic.explicit_gap
#print axioms KappaChangedG.Arithmetic.tail_decay
#print axioms KappaChangedG.Arithmetic.normalized_completion
#print axioms KappaChangedG.Arithmetic.finite_compiler_wins
