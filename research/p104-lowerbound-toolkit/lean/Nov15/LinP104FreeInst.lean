import Nov15.LinP104FreeInstBase
import Nov15.LinP104FreeInstC0
import Nov15.LinP104FreeInstC1
import Nov15.LinP104FreeInstC2
import Nov15.LinP104FreeInstC3
import Nov15.LinP104FreeInstC4
import Nov15.LinP104FreeInstC5
import Nov15.LinP104FreeInstC6
import Nov15.LinP104FreeInstC7
open Matrix Finset LinCore LinFinal
namespace P104
lemma hdec_I : ∀ t s : Fin 104, ∑ k : Fin 8, wI k t * vI k s * Qlab t s = if t = s then 2 else 0 := by
  intro t s
  have h := t.2
  by_cases h0 : t.1 < 13
  · exact hdec_I0 t (by omega) h0 s
  by_cases h1 : t.1 < 26
  · exact hdec_I1 t (by omega) h1 s
  by_cases h2 : t.1 < 39
  · exact hdec_I2 t (by omega) h2 s
  by_cases h3 : t.1 < 52
  · exact hdec_I3 t (by omega) h3 s
  by_cases h4 : t.1 < 65
  · exact hdec_I4 t (by omega) h4 s
  by_cases h5 : t.1 < 78
  · exact hdec_I5 t (by omega) h5 s
  by_cases h6 : t.1 < 91
  · exact hdec_I6 t (by omega) h6 s
  exact hdec_I7 t (by omega) (by omega) s

lemma Z4_I : Z4Lin (Finset.univ : Finset (Fin 8)) wI vI xE yG ctI where
  hct := hct_I
  hw := by
    intro k _ t
    have : ∑ i : Fin 8, xE k i * ctI t i = ctI t k := by simp [xE]
    rw [this]; rfl
  hv := by
    intro k _ t
    simp only [vI, yG]
    exact Int.ModEq.refl _

theorem nonvac_instance :
    56 ≤ ∑ k ∈ (Finset.univ : Finset (Fin 8)), (Doubling.Qk Qlab (wI k) (vI k)).rank :=
  p104_linear_cost_ge_free Z4_I (fun t s => by simpa using hdec_I t s)

#print axioms P104.nonvac_instance

end P104
