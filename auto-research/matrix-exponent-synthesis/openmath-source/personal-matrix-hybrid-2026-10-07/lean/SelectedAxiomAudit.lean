import Concrete16
import DAGRefinement

-- All nine qualified original source files are reached by these two imports.
#print axioms PersonalMatrix.Hybrid.blocks_mul
#print axioms PersonalMatrix.Hybrid.hybrid_sound
#print axioms PersonalMatrix.Hybrid.hybrid_gate_count
#print axioms PersonalMatrix.Hybrid.hybrid_sound_and_cost
#print axioms PersonalMatrix.Hybrid.hybrid_W_cost
#print axioms PersonalMatrix.Hybrid.perfect_square_cost
#print axioms PersonalMatrix.RosowskiEven.sound
#print axioms PersonalMatrix.RosowskiEven.gate_count
#print axioms PersonalMatrix.RosowskiEven.square_four_gate_count
#print axioms PersonalMatrix.RosowskiEven.square_four_sound
#print axioms PersonalMatrix.Ordinal.toFull_mul
#print axioms PersonalMatrix.Ordinal.sound_and_W_cost
#print axioms PersonalMatrix.DAG.translatedStep_state
#print axioms PersonalMatrix.DAG.translatedRun_state
#print axioms PersonalMatrix.DAG.translatedRun_trace
#print axioms PersonalMatrix.DAG.translated_cost
#print axioms PersonalMatrix.DAG.synthesized_correct_and_cost
#print axioms PersonalMatrix.Outer48.brent_integer
#print axioms PersonalMatrix.Outer48.brent_common_denominator
#print axioms PersonalMatrix.Outer48.alpha_nonzero
#print axioms PersonalMatrix.Outer48.beta_nonzero
#print axioms PersonalMatrix.Outer48.gamma_nonzero
#print axioms PersonalMatrix.Lifting.weighted_contraction
#print axioms PersonalMatrix.Lifting.delta_contraction
#print axioms PersonalMatrix.Lifting.block_stable_from_tensor
#print axioms PersonalMatrix.Outer48Scheme.target_transport
#print axioms PersonalMatrix.Outer48Scheme.inverse_eight
#print axioms PersonalMatrix.Outer48Scheme.tensor_correct
#print axioms PersonalMatrix.Outer48Scheme.all_block_sizes
#print axioms PersonalMatrix.Leaf46.products_match
#print axioms PersonalMatrix.Leaf46.weighted_reconstruction
#print axioms PersonalMatrix.Leaf46.valid
#print axioms PersonalMatrix.Concrete16.algorithm_correct
#print axioms PersonalMatrix.Concrete16.gate_count
#print axioms PersonalMatrix.Concrete16.certified_2208

#check @PersonalMatrix.Concrete16.certified_2208
#check @PersonalMatrix.DAG.synthesized_correct_and_cost
