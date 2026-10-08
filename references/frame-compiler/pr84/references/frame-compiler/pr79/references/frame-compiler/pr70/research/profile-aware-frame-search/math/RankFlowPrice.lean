import Std
import Init.Data.Rat.Lemmas

/-!
Subtracting the linear rank part from a clearing price preserves its candidate
ordering: the target correction is the same rG-h for every candidate at that
acquisition, while each distinct provider has zero correction. A carried edge
has correction -h; dropping this term preserves matching prices only when the
number of carried edges is fixed. Variable-cardinality searches must retain
the full charged correction. Analytic exp/log evaluation and frame-path binding
remain separate contracts; these are exact algebraic price identities.
-/
namespace RankFlowPrice

theorem clearing_target_rank_delta (rG rA h : Int) :
    (rG-rA)-(h-rA) = rG-h := by omega

theorem clearing_provider_rank_delta (rG rB h : Int) :
    (rG-rB)+(h-rG)-(h-rB) = 0 := by omega

theorem carried_edge_rank_delta (rT rG rP h : Int) :
    (rT-rG)-(h-rG)-rP-(rT-rP) = -h := by omega

theorem constant_shift_preserves_order_and_minimizers {A : Type}
    (cost : A → Rat) (shift : Rat) (x y : A) :
    ((cost x+shift ≤ cost y+shift) ↔ cost x ≤ cost y) ∧
    ((∀ z, cost x+shift ≤ cost z+shift) ↔ ∀ z, cost x ≤ cost z) := by
  constructor
  · exact Rat.add_le_add_right
  · constructor
    · intro h z
      exact Rat.add_le_add_right.mp (h z)
    · intro h z
      exact Rat.add_le_add_right.mpr (h z)

end RankFlowPrice

#print axioms RankFlowPrice.clearing_target_rank_delta
#print axioms RankFlowPrice.clearing_provider_rank_delta
#print axioms RankFlowPrice.carried_edge_rank_delta
#print axioms RankFlowPrice.constant_shift_preserves_order_and_minimizers
