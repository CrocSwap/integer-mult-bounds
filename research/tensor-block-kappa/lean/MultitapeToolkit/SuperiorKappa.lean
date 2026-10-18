import MultitapeToolkit.ReplicaTailGain

namespace MultitapeToolkit.ReplicaTailGain

/-- A strictly larger realized replica count has a strictly smaller complete
normalized paid moment. Existence of a literal allocation is checked separately. -/
theorem frontier_replica_monotone (p S T : Real) (hp : 99/100 <= p)
    (hp1 : p < 1) (hS : 0 < S) (hST : S < T) :
    frontierReplicaPower T p / ((896*T)*(73:Real)^p) <
      frontierReplicaPower S p / ((896*S)*(73:Real)^p) := by
  have hT : 0 < T := lt_trans hS hST
  have hr : (0:Real) < (73:Real)^p := Real.rpow_pos_of_pos (by norm_num) p
  have hc : 0 < residuePower p := div_pos (tail_power_positive p hp hp1) (by norm_num)
  have hsden : (0:Real) < 896*S*(73:Real)^p := by positivity
  have hd : 896*S*(73:Real)^p < 896*T*(73:Real)^p := by nlinarith
  have hdiv := div_lt_div_of_pos_left hc hsden hd
  have split (U : Real) (hU : 0 < U) :
      frontierReplicaPower U p / (896*U*(73:Real)^p) =
      frontierTenReplicaPower p/(8960*(73:Real)^p) +
        residuePower p/(896*U*(73:Real)^p) := by
    unfold frontierReplicaPower
    field_simp
    ring
  rw [split T hT, split S hS]
  linarith

end MultitapeToolkit.ReplicaTailGain
