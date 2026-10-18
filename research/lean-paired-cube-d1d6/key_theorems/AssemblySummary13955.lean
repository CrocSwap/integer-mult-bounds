import AssemblyPairLaws13955
import AssemblyParameters13955
import AssemblySlacksA13955
import AssemblySlacksB13955
import AssemblyMargins13955
import AssemblyDenominators13955
namespace PairedCubeAssembly13955

def AllSlacksLinked : Prop :=
  (ExactValue slack_bit_positive 4613422943 10000000000000 ∧ Positive slack_bit_positive) ∧
  (ExactValue slack_complex_above_bit 243146057 10000000000000 ∧ Positive slack_complex_above_bit) ∧
  (ExactValue slack_complex_below_one_over32 307643431 10000000000 ∧ Positive slack_complex_below_one_over32) ∧
  (ExactValue slack_beta_positive 1 1000000 ∧ Positive slack_beta_positive) ∧
  (ExactValue slack_beta_below_one 999999 1000000 ∧ Positive slack_beta_below_one) ∧
  (ExactValue slack_leaf_saving_above_bit 243141200431 10000000000000000 ∧ Positive slack_leaf_saving_above_bit) ∧
  (ExactValue slack_q_positive 230671142536577057 500000000000000000000 ∧ Positive slack_q_positive) ∧
  (ExactValue slack_q_below_internal 4613422943 500000000000000000000 ∧ Positive slack_q_below_internal) ∧
  (ExactValue slack_q_below_leaf 12157064634972943 500000000000000000000 ∧ Positive slack_q_below_leaf) ∧
  (ExactValue slack_c_positive 23067114484328848236577057 50000000000000000000000000000 ∧ Positive slack_c_positive) ∧
  (ExactValue slack_c_below_one 49976932885515671151763422943 50000000000000000000000000000 ∧ Positive slack_c_below_one) ∧
  (ExactValue slack_q_below_reservations 230671142536577057 50000000000000000000000000000 ∧ Positive slack_q_below_reservations) ∧
  (ExactValue slack_lambda_above_tau 4613422943 1000000000000000000000 ∧ Positive slack_lambda_above_tau) ∧
  (ExactValue slack_lambda_above_sigma 24314610313422943 1000000000000000000000 ∧ Positive slack_lambda_above_sigma) ∧
  (ExactValue slack_lambda_above_internal 4613422943 1000000000000000000000 ∧ Positive slack_lambda_above_internal) ∧
  (ExactValue slack_lambda_prime_above_lambda 4613422943 1000000000000000000000 ∧ Positive slack_lambda_prime_above_lambda) ∧
  (ExactValue slack_compact_leaf 12157064634972943 500000000000000000000 ∧ Positive slack_compact_leaf) ∧
  (ExactValue slack_compact_reservations 230671142536577057 50000000000000000000000000000 ∧ Positive slack_compact_reservations) ∧
  (ExactValue slack_lambda_prime_below_one 230671142536577057 500000000000000000000 ∧ Positive slack_lambda_prime_below_one) ∧
  (ExactValue slack_epsilon_positive 49999999500000000000000000000 50046134228737986553936577057 ∧ Positive slack_epsilon_positive) ∧
  (ExactValue slack_epsilon_below_one 46134728737986553936577057 50046134228737986553936577057 ∧ Positive slack_epsilon_below_one) ∧
  (ExactValue slack_guard_width 46134728737986553936577057 50046134228737986553936577057 ∧ Positive slack_guard_width) ∧
  (ExactValue slack_K_geometry 2306761448432885054328848236577057 5004613422873798655393657705700000000 ∧ Positive slack_K_geometry) ∧
  (ExactValue slack_K_dominates_log 2306711425365770339328857463422943 5004613422873798655393657705700000000 ∧ Positive slack_K_dominates_log) ∧
  (ExactValue slack_record_suffix 46134728737986553936577057 50046134228737986553936577057 ∧ Positive slack_record_suffix) ∧
  (ExactValue slack_phase_local 36907732944255014411275091663422943 40036907382990389243149261645600000000 ∧ Positive slack_phase_local) ∧
  (ExactValue slack_phase_boundary 27680687058255018102013446063422943 40036907382990389243149261645600000000 ∧ Positive slack_phase_boundary) ∧
  (ExactValue slack_gamma_sublinear 11533807357499995386577057 50046134228737986553936577057 ∧ Positive slack_gamma_sublinear) ∧
  (ExactValue slack_cell_above_band 49988465692642500004613422943 100092268457475973107873154114 ∧ Positive slack_cell_above_band) ∧
  (ExactValue slack_prime_interval_packing 46134728737986553936577057 50046134228737986553936577057 ∧ Positive slack_prime_interval_packing) ∧
  (ExactValue slack_alpha_positive 34600921380486558550000000 50046134228737986553936577057 ∧ Positive slack_alpha_positive) ∧
  (ExactValue slack_alpha_below_one 50011533307357499995386577057 50046134228737986553936577057 ∧ Positive slack_alpha_below_one) ∧
  (ExactValue slack_alpha_below_one_fourth 49907730543216040319736577057 200184536914951946215746308228 ∧ Positive slack_alpha_below_one_fourth) ∧
  (ExactValue slack_delta_positive 1 800000000 ∧ Positive slack_delta_positive) ∧
  (ExactValue slack_delta_below_one_eighth 99999999 800000000 ∧ Positive slack_delta_below_one_eighth) ∧
  (ExactValue slack_short_record_fallback 499769111016140682562896443488438348781249 500461342287379865539365770570000000000000 ∧ Positive slack_short_record_fallback) ∧
  (ExactValue slack_small_field_exposure 23067614714999990773154114 50046134228737986553936577057 ∧ Positive slack_small_field_exposure) ∧
  (ExactValue slack_artificial_boundary 280304486459762979712765368256463422943 40036907382990389243149261645600000000 ∧ Positive slack_artificial_boundary) ∧
  (ExactValue slack_row_product_gap 141461 5 ∧ Positive slack_row_product_gap) ∧
  (ExactValue slack_original_prefix_above_kappa 5054386350468686063524720470067 500461342287379865539365770570000000000 ∧ Positive slack_original_prefix_above_kappa) ∧
  (ExactValue slack_coordinate_movement_above_kappa 4253943 10000000000000 ∧ Positive slack_coordinate_movement_above_kappa) ∧
  (ExactValue slack_compact_phase_layer_above_kappa 49772927594887408131062764367 500461342287379865539365770570000000000 ∧ Positive slack_compact_phase_layer_above_kappa) ∧
  (ExactValue slack_bulk_exposure_above_kappa 4253943 10000000000000 ∧ Positive slack_bulk_exposure_above_kappa) ∧
  (ExactValue slack_Gaussian_arithmetic_above_kappa 230674995542499379056693553711102309 1000922684574759731078731541140000000000 ∧ Positive slack_Gaussian_arithmetic_above_kappa) ∧
  (ExactValue slack_scalar_work_above_kappa 461351142692499286788234693711102309 1000922684574759731078731541140000000000 ∧ Positive slack_scalar_work_above_kappa) ∧
  (ExactValue slack_dimension_above_kappa 499769323909543061963253178701062764367 500461342287379865539365770570000000000 ∧ Positive slack_dimension_above_kappa)

def AllMarginsLinked : Prop :=
  (ExactValue margin_original_prefix 2306761448432885054328848236577057 5004613422873798655393657705700000000 ∧ AtMost minimum margin_original_prefix ∧ Below KAPPA margin_original_prefix) ∧
  (ExactValue margin_coordinate_movement 4613422943 10000000000000 ∧ AtMost minimum margin_coordinate_movement ∧ Below KAPPA margin_coordinate_movement) ∧
  (ExactValue margin_compact_phase_layer 23067114022986563163422943 50046134228737986553936577057 ∧ AtMost minimum margin_compact_phase_layer ∧ Below KAPPA margin_compact_phase_layer) ∧
  (ExactValue margin_bulk_exposure 4613422943 10000000000000 ∧ AtMost minimum margin_bulk_exposure ∧ Below KAPPA margin_bulk_exposure) ∧
  (ExactValue margin_Gaussian_arithmetic 27680687058255018102013446063422943 40036907382990389243149261645600000000 ∧ AtMost minimum margin_Gaussian_arithmetic ∧ Below KAPPA margin_Gaussian_arithmetic) ∧
  (ExactValue margin_scalar_work 36907732944255014411275091663422943 40036907382990389243149261645600000000 ∧ AtMost minimum margin_scalar_work ∧ Below KAPPA margin_scalar_work) ∧
  (ExactValue margin_dimension 49999999500000000000000000000 50046134228737986553936577057 ∧ AtMost minimum margin_dimension ∧ Below KAPPA margin_dimension)

theorem all_46_slack_formulas_linked : AllSlacksLinked := by
  exact ⟨slack_bit_positive_derived, slack_complex_above_bit_derived, slack_complex_below_one_over32_derived, slack_beta_positive_derived, slack_beta_below_one_derived, slack_leaf_saving_above_bit_derived, slack_q_positive_derived, slack_q_below_internal_derived, slack_q_below_leaf_derived, slack_c_positive_derived, slack_c_below_one_derived, slack_q_below_reservations_derived, slack_lambda_above_tau_derived, slack_lambda_above_sigma_derived, slack_lambda_above_internal_derived, slack_lambda_prime_above_lambda_derived, slack_compact_leaf_derived, slack_compact_reservations_derived, slack_lambda_prime_below_one_derived, slack_epsilon_positive_derived, slack_epsilon_below_one_derived, slack_guard_width_derived, slack_K_geometry_derived, slack_K_dominates_log_derived, slack_record_suffix_derived, slack_phase_local_derived, slack_phase_boundary_derived, slack_gamma_sublinear_derived, slack_cell_above_band_derived, slack_prime_interval_packing_derived, slack_alpha_positive_derived, slack_alpha_below_one_derived, slack_alpha_below_one_fourth_derived, slack_delta_positive_derived, slack_delta_below_one_eighth_derived, slack_short_record_fallback_derived, slack_small_field_exposure_derived, slack_artificial_boundary_derived, slack_row_product_gap_derived, slack_original_prefix_above_kappa_derived, slack_coordinate_movement_above_kappa_derived, slack_compact_phase_layer_above_kappa_derived, slack_bulk_exposure_above_kappa_derived, slack_Gaussian_arithmetic_above_kappa_derived, slack_scalar_work_above_kappa_derived, slack_dimension_above_kappa_derived⟩

theorem all_seven_margin_formulas_linked : AllMarginsLinked := by
  exact ⟨margin_original_prefix_derived, margin_coordinate_movement_derived, margin_compact_phase_layer_derived, margin_bulk_exposure_derived, margin_Gaussian_arithmetic_derived, margin_scalar_work_derived, margin_dimension_derived⟩

theorem minimum_is_attained : margin_compact_phase_layer = minimum := by
  rfl

theorem finite_assembly_formula_certificate : AllSlacksLinked ∧ AllMarginsLinked ∧ ExactValue minimum 23067114022986563163422943 50046134228737986553936577057 ∧ Below KAPPA minimum ∧ ExactValue (minimum-KAPPA) 49772927594887408131062764367 500461342287379865539365770570000000000 := by
  exact ⟨all_46_slack_formulas_linked, all_seven_margin_formulas_linked, minimum_derived.1, strict_absorption, absorption_gap_derived.1⟩

end PairedCubeAssembly13955
#print axioms PairedCubeAssembly13955.all_46_slack_formulas_linked
#print axioms PairedCubeAssembly13955.all_seven_margin_formulas_linked
#print axioms PairedCubeAssembly13955.minimum_is_attained
#print axioms PairedCubeAssembly13955.finite_assembly_formula_certificate
