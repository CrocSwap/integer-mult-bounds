import Mathlib.Tactic.NormNum

namespace MixedRankPrices

abbrev k : Rat := 387992803556 / 100000000000000
abbrev h : Rat := 1 / 100000000000000
abbrev e : Rat := 1-h
abbrev z : Rat := 1-3*h
abbrev q : Rat := k+3*h
abbrev a : Rat := k+4*h
abbrev x : Rat := e*(1+q)-3/32+h
abbrev ordinary : Rat := 3879928035646 / 1000000000000000

def costs : List Rat := [
  1-e*q, 1-a, e-q*z, e-a*z, e-z, e-x+29/32, e+1/2-x,
  1-e, e+z+54-128, 1-ordinary+2*(1-e), 1-e]

theorem costs_fit : ∀ u ∈ costs, u < 1-k := by
  norm_num [costs, x, e, z, q, a, ordinary, k, h, List.forall_mem_cons]

theorem crt_saving : ordinary-2*(1-e) = 3879928035626 / 1000000000000000 := by
  norm_num [ordinary, e, h]
theorem actual_word : ordinary-(k+7*h) = 16 / 1000000000000000 := by
  norm_num [ordinary, k, h]

#print axioms costs_fit
#print axioms crt_saving
#print axioms actual_word
end MixedRankPrices
