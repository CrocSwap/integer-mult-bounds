/- Copyright 2026 Gabriele Nespoli. Apache-2.0. Developed with OpenAI Codex.
   Lucas-Lehmer criterion and norm_num extension: mathlib contributors.
   This verifies prime eligibility only, not the integer multiplication theorem. -/
import Mathlib.NumberTheory.LucasLehmer

theorem fixed_prime_prime : (mersenne 127).Prime :=
  lucas_lehmer_sufficiency _ (by simp) (by norm_num)

theorem fixed_prime_value : mersenne 127 = 170141183460469231731687303715884105727 := by
  norm_num [mersenne]

theorem fixed_prime_large : 2 ^ 80 < mersenne 127 := by
  norm_num [mersenne]

theorem fixed_prime_density :
    (0 : ℚ) < 3456000 / 170141183460469231731687303715884105727 ∧
    (3456000 / 170141183460469231731687303715884105727 : ℚ) < 1 / 10 ^ 16 := by
  norm_num

#print axioms fixed_prime_prime
#print axioms fixed_prime_large
#print axioms fixed_prime_density
