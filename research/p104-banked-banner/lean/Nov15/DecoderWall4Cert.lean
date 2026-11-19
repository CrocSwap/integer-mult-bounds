import Nov15.DecoderWall4Defs

open Matrix
set_option maxHeartbeats 0
namespace DW4

theorem certY_ok : ∀ p ∈ certY, p.2 < catD.length ∧ ∀ i : Fin 8, dotb (lab (portOf p.2 i)) p.1 = true := by
  decide +kernel

theorem certP_ok : ∀ t ∈ certP, t.2.2 < catD.length ∧
    ∀ i : Fin 8, (dotb (lab (portOf t.2.2 i)) t.1 || dotb (lab (portOf t.2.2 i)) t.2.1) = true := by
  decide +kernel

end DW4
