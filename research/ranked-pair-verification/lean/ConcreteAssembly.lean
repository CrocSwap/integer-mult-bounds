import Mathlib.Tactic

/-!
Exact real/rational arithmetic for the both-ranked pair-profile candidate.
All slacks are DERIVED from a,h,kappa and finite bridge constants below.
No precomputed slack list is imported. This is an arithmetic certificate only.

External obligations: the bit and complex characteristic bounds; faithful
compiler/profile binding; physical recurrence, address frames, routing and
fixed finite-tape implementation; analytic transfer and exact recovery.
The supplied scalar-group bound G and finite role counts are not proved here
to describe a machine. Theorems below make no asymptotic multiplication claim.

Source for constraint formulas: independently transcribed in
outputs/independent_assembly.py from the retained PR23/29/34/36/48 assembly.
The parameter/profile improvement is this audit's new both-ranked pair case.
-/

namespace ConcreteAssembly
noncomputable section

def a : ℝ := 63787735011827529 / 1250000000000000000000
def h : ℝ := 1 / 1000000000000000000
def kappa : ℝ := 20411033624901463 / 400000000000000000000
def b : ℝ := 717 / 10000000
def beta : ℝ := 1 / 20
def q : ℝ := a * (1 - 2 * h)
def c : ℝ := q + h / 4
def epsilon : ℝ := (1 - h) / (1 + q)
def tau : ℝ := 1 - a
def sigma : ℝ := 1 - b
def lambdaPrime : ℝ := 1 - q
def lambda : ℝ := (tau + lambdaPrime) / 2
def g : ℝ := epsilon * q
def alpha : ℝ := (g + 1 - epsilon) / 2
def delta : ℝ := h / 8
def internal : ℝ := tau + (1 - beta) * max (sigma - tau) 0
def leaf : ℝ := sigma + beta * (1 - sigma)

-- Fixed complex bridge: these supplied finite quantities remain bound to the
-- concrete construction by external compiler/profile checks.
def W : ℝ := 537696432
def m : ℝ := 784
def rankMass : ℝ := 421548223824
def G : ℝ := 4793351472
def E : ℝ := 64 * (W + m + G + 1) ^ 3
def B : ℝ := rankMass + E
def C0 : ℝ := 32 * m * B ^ 2
def literal : ℝ := 2 * G * W ^ 2 + 8 * rankMass + 4 * W + 4 + 32 * m
def stock : ℝ := 9 * 28 + 20 * 30
def rowGap : ℝ := 2000 - (51 / 25) * stock

def margins : List ℝ :=
  [1 - epsilon, a, g, a, min (1 - epsilon - delta) (alpha - delta),
   1 - epsilon - delta, epsilon]

def constraints : List ℝ := [
  a,                                    -- a_positive
  b - a,                                -- a_below_b
  1 / 32 - b,                           -- b_below_one_over32
  beta,                                 -- beta_positive
  1 - beta,                             -- beta_below_one
  (1 - beta) * b - a,                    -- phase_leaf_above_bit
  q,                                    -- q_positive
  1 - internal - q,                     -- q_below_internal
  1 - leaf - q,                         -- q_below_leaf
  c,                                    -- c_positive
  1 - c,                                -- c_below_one
  c - q,                                -- q_below_reservations
  lambda - tau,                         -- lambda_above_tau
  lambda - sigma,                       -- lambda_above_sigma
  lambda - internal,                    -- lambda_above_internal
  lambdaPrime - lambda,                 -- lambda_prime_above_lambda
  lambdaPrime - leaf,                   -- compact_leaf
  lambdaPrime - (1 - c),                -- compact_reservations
  q,                                    -- lambda_prime_below_one
  epsilon,                              -- epsilon_positive
  1 - epsilon,                          -- epsilon_below_one
  1 - epsilon,                          -- guard_width
  1 - epsilon * (1 + c),                -- K_geometry
  epsilon * c,                          -- K_dominates_log
  1 - epsilon,                          -- record_suffix
  1 - epsilon - delta,                  -- phase_local
  alpha - delta,                        -- phase_boundary
  1 - epsilon - alpha,                 -- gamma_sublinear
  epsilon - (1 - alpha) / 2,            -- cell_above_band
  1 - epsilon,                          -- prime_interval_packing
  alpha,                                -- alpha_positive
  1 - alpha,                            -- alpha_below_one
  1 / 4 - alpha,                        -- alpha_below_one_fourth
  delta,                                -- delta_positive
  1 / 8 - delta,                        -- delta_below_one_eighth
  epsilon - a,                          -- short_record_fallback
  1 - epsilon - g,                      -- small_field_exposure
  8 - epsilon + alpha - delta - g,      -- artificial_boundary
  E - literal,                          -- literal_scalar_guard
  rowGap,                               -- row_product_gap
  (1 - epsilon) - kappa,               -- g1_above_kappa
  a - kappa,                            -- g2_above_kappa
  g - kappa,                            -- g3_above_kappa
  a - kappa,                            -- g4_above_kappa
  min (1 - epsilon - delta) (alpha - delta) - kappa, -- g5_above_kappa
  (1 - epsilon - delta) - kappa,       -- g6_above_kappa
  epsilon - kappa]                     -- g7_above_kappa

theorem constraint_count : constraints.length = 47 := by rfl

set_option maxRecDepth 10000 in
theorem all_constraints_positive : ∀ x ∈ constraints, 0 < x := by
  norm_num [constraints, internal, leaf, lambda, lambdaPrime, tau, sigma,
    delta, alpha, g, epsilon, c, q, a, h, kappa, b, beta,
    E, literal, W, m, G, rankMass, rowGap, stock]

set_option maxRecDepth 10000 in
theorem all_seven_margins : margins.length = 7 ∧ ∀ x ∈ margins, kappa < x := by
  norm_num [margins, delta, alpha, g, epsilon, q, a, h, kappa]

theorem exact_balancing : 1 - epsilon - g = h ∧
    1 - epsilon - alpha = h / 2 ∧
    1 - epsilon * (1 + c) = h - epsilon * h / 4 := by
  norm_num [alpha, g, epsilon, c, q, a, h]

theorem semantic_envelope_arithmetic :
    0 < rankMass ∧ rankMass < m * W ∧ E > literal ∧
    2 * B * (m - 756) ≥ rankMass + E ∧ C0 > 2 * B + 18 ∧ rowGap > 0 := by
  norm_num [rankMass, W, m, E, B, C0, G, literal, rowGap, stock]

theorem strictly_improves_pair_baseline : (5101691 / 100000000000 : ℝ) < kappa := by
  norm_num [kappa]

#print axioms constraint_count
#print axioms all_constraints_positive
#print axioms all_seven_margins
#print axioms exact_balancing
#print axioms semantic_envelope_arithmetic
#print axioms strictly_improves_pair_baseline

end
end ConcreteAssembly
