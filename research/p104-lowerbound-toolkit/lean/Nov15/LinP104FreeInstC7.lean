import Nov15.LinP104FreeInstBase
open Matrix Finset LinCore LinFinal
namespace P104
lemma hdec_I7 : ∀ t : Fin 104, 91 ≤ t.1 → t.1 < 104 → ∀ s : Fin 104,
    ∑ k : Fin 8, wI k t * vI k s * Qlab t s = if t = s then 2 else 0 := by
  decide +kernel
end P104
