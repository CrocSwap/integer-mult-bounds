import Nov15.LinP104FreeInstBase
open Matrix Finset LinCore LinFinal
namespace P104
lemma hdec_I0 : ∀ t : Fin 104, 0 ≤ t.1 → t.1 < 13 → ∀ s : Fin 104,
    ∑ k : Fin 8, wI k t * vI k s * Qlab t s = if t = s then 2 else 0 := by
  decide +kernel
end P104
