import Nov15.DecoderWall4Defs

open Matrix
set_option maxHeartbeats 0
namespace DW4

theorem catD_length : catD.length = 196 := by decide +kernel

theorem certY_keys : certY.map Prod.fst = (List.range' 1 511).filter (fun y => !(bad.contains y)) := by
  decide +kernel

theorem certP_keys : certP.map (fun t => (t.1, t.2.1)) =
    bad.flatMap (fun a => bad.filterMap (fun b => if a < b then some (a, b) else none)) := by
  decide +kernel

theorem cover_y (y : ℕ) (hy : y < 512) : y = 0 ∨ y ∈ bad ∨ ∃ p ∈ certY, p.1 = y := by
  by_cases h0 : y = 0
  · exact Or.inl h0
  · by_cases hb : y ∈ bad
    · exact Or.inr (Or.inl hb)
    · refine Or.inr (Or.inr ?_)
      have : y ∈ certY.map Prod.fst := by
        rw [certY_keys, List.mem_filter, List.mem_range'_1]
        refine ⟨by omega, ?_⟩
        simpa using hb
      obtain ⟨p, hp, hpy⟩ := List.mem_map.1 this
      exact ⟨p, hp, hpy⟩

theorem cover_P (a b : ℕ) (ha : a ∈ bad) (hb : b ∈ bad) (hlt : a < b) : ∃ t ∈ certP, t.1 = a ∧ t.2.1 = b := by
  have : (a, b) ∈ certP.map (fun t => (t.1, t.2.1)) := by
    rw [certP_keys, List.mem_flatMap]
    exact ⟨a, ha, List.mem_filterMap.2 ⟨b, hb, by simp [hlt]⟩⟩
  obtain ⟨t, ht, hte⟩ := List.mem_map.1 this
  exact ⟨t, ht, congrArg Prod.fst hte, congrArg Prod.snd hte⟩

end DW4
