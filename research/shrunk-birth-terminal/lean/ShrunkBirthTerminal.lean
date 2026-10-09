import Mathlib.Tactic.NormNum
import Mathlib.Data.Nat.Choose.Basic

/-!
Exact arithmetic companion for the shrunk-frame / birth-reuse / terminal-elision
composition. Prepared with OpenAI assistance. Upstream construction and analytic
credits are retained in the accompanying proof and source provenance.

Scope: supplied physical-count arrays, all 47 parameter slacks, seven margins,
three row stocks, scalar guards and independent degree-eight moment arithmetic.
The physical-array derivation, real logarithm / exponential enclosure validity,
and all-size framed-word, stopped-product, tape, prime and recovery hypotheses
remain external. This is not an unconditional integer-multiplication theorem.
No sorry, native_decide or additional axioms are introduced.
-/
namespace KappaCheck.ShrunkBirthTerminal
set_option maxRecDepth 20000
set_option maxHeartbeats 8000000

-- Source SHA256 89b115978ab95d8e69e58472cde14a588157a3b3a8c577034c39ca0309eab34d: work/r12-audit/canonical-joint-expansion/joint-expansion/certificate.json
-- Source SHA256 3203dcb2709c3c8f1513c9ff31faafe9903f7ba14cdd7bbe1aaa38c9edbfcf43: work/r12-terminal/joint-expansion/READOUT_COST.json
-- Source SHA256 457287cf9986574cef50235644af77c893b3513e7a0872827b1cce352f4b62d5: work/r12-terminal/joint-expansion/physical-audit.json
-- Source SHA256 11dfe85123d23c17b4e1f4309b7c5fdfdac55faef7563881f2f3db5b2dfae82e: work/r12-terminal/joint-expansion/word.json.gz
def h : ℕ := 24
def m : ℕ := h*h
def v : ℕ := Nat.choose h 3
def n : ℕ := v*v
def virtualRoles : ℕ := 28705
def births : ℕ := 2108
def terminals : ℕ := 381
def roles : ℕ := virtualRoles-births-terminals
def width : ℕ := 2*n+2*v*roles
def forwardHistogram : List (ℕ × ℕ) := [(1, 106459), (2, 65902), (3, 7179), (4, 14980), (5, 6582), (6, 3788), (7, 2901), (8, 5452), (9, 973), (10, 1911), (11, 1645), (12, 8295), (13, 3257), (14, 450), (15, 800), (16, 156), (17, 100), (18, 50), (19, 77), (20, 136), (21, 302), (22, 16), (23, 2071)]
def initialDimensionHistogram : List (ℕ × ℕ) := [(0, 23980), (2, 854), (4, 366), (6, 589), (8, 110), (10, 12), (19, 183), (20, 25), (21, 7), (22, 90)]
def counts : List (ℕ × ℕ) :=
  (forwardHistogram.map fun p => (p.1, 2*v*p.2)) ++
  (initialDimensionHistogram.map fun p => (m-h+p.1, 2*v*p.2)) ++
  [((h-1)^2, 2*n), (1, n)]
def count (t : ℕ) : ℕ := (counts.map fun p => if p.1=t then p.2 else 0).sum
def mass : ℕ := (counts.map fun p => p.1*p.2).sum

theorem network_counts : h = 24 ∧ m = 576 ∧ v = 2024 ∧ n = 4096576 ∧ roles = 26216 ∧ width = 114315520 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose]

theorem initial_dimension_count : (initialDimensionHistogram.map Prod.snd).sum = roles := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem rank_mass : mass = 65843877440 ∧ m*width-mass = 1862080 ∧ n-2*v*h*(h-1) = 1862080 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_1 : count 1 = 435042608 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_2 : count 2 = 266771296 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_3 : count 3 = 29060592 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_4 : count 4 = 60639040 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_5 : count 5 = 26643936 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_6 : count 6 = 15333824 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_7 : count 7 = 11743248 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_8 : count 8 = 22069696 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_9 : count 9 = 3938704 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_10 : count 10 = 7735728 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_11 : count 11 = 6658960 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_12 : count 12 = 33578160 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_13 : count 13 = 13184336 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_14 : count 14 = 1821600 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_15 : count 15 = 3238400 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_16 : count 16 = 631488 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_17 : count 17 = 404800 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_18 : count 18 = 202400 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_19 : count 19 = 311696 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_20 : count 20 = 550528 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_21 : count 21 = 1222496 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_22 : count 22 = 64768 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_23 : count 23 = 8383408 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_529 : count 529 = 8193152 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_552 : count 552 = 97071040 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_554 : count 554 = 3456992 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_556 : count 556 = 1481568 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_558 : count 558 = 2384272 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_560 : count 560 = 445280 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_562 : count 562 = 48576 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_571 : count 571 = 740784 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_572 : count 572 = 101200 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_573 : count 573 = 28336 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem count_574 : count 574 = 364320 := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

def childSizes : List ℕ := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 529, 552, 554, 556, 558, 560, 562, 571, 572, 573, 574]
theorem complete_child_support : ∀ p ∈ counts, p.2 ≠ 0 → p.1 ∈ childSizes := by
  norm_num [h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram, childSizes]

theorem strict_child_contraction : ∀ t ∈ childSizes, 0 < t ∧ t < m := by
  norm_num [childSizes, h, m]

def a : ℚ := (56407455433006738868999943092544566993261131 / 500000000000000000000000000000000000000000000000)
def b : ℚ := (56407455433006738869 / 500000000000000000000000)
def kappa : ℚ := (28200546274389 / 250000000000000000)
def eta : ℚ := (1 / 1000000000000000000000000)
def beta : ℚ := (1 / 1000000000000000000000000)
def backoff : ℚ := (1 / 1000000000000000000000000000000)
def actualBitSaving : ℚ := (1240189553 / 10000000000000)
def tau : ℚ := 1-a
def sigma : ℚ := 1-b
def qParam : ℚ := a*(1-2*eta)
def lp : ℚ := 1-qParam
def c : ℚ := qParam+eta/4
def epsilon : ℚ := (1-eta)/(1+qParam)
def lam : ℚ := (tau+lp)/2
def g : ℚ := epsilon*qParam
def r : ℚ := (g+1-epsilon)/2
def delta : ℚ := eta/8
def internal : ℚ := tau+(1-beta)*max (sigma-tau) 0
def leaf : ℚ := sigma+beta*(1-sigma)

def scalar : ℕ := 3116113870848
def guardE : ℕ := 64*(width+m+scalar+1)^3
def guardB : ℕ := mass+guardE
def literal : ℕ := 2*scalar*width^2+8*mass+4*width+4+32*m
def guardC : ℕ := 32*m*guardB^2
def literalGap : ℚ := (guardE : ℚ)-literal
def rowCoefficient : ℕ := 367*27+200*27+9*28
def rowGap : ℚ := 32000-(51/25)*rowCoefficient
def margins : List ℚ := [1-epsilon,a,g,a,min (1-epsilon-delta) (r-delta),1-epsilon-delta,epsilon]

theorem slack_a_positive : (a) = ((56407455433006738868999943092544566993261131 / 500000000000000000000000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (a) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_a_below_b : (b-a) = ((56907455433006738869 / 500000000000000000000000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (b-a) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_b_below_one_over32 : (1/32-b) = ((15568592544566993261131 / 500000000000000000000000) : ℚ) ∧ (0 : ℚ) < (1/32-b) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_beta_positive : (beta) = ((1 / 1000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (beta) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_beta_below_one : (1-beta) = ((999999999999999999999999 / 1000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (1-beta) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_phase_leaf_above_bit : ((1-beta)*b-a) = ((1 / 1000000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < ((1-beta)*b-a) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_q_positive : (qParam) = ((28203727716503369434499915138816850489891696500056907455433006738869 / 250000000000000000000000000000000000000000000000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (qParam) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_q_below_internal : (1-internal-qParam) = ((56407455433006738868999943092544566993261131 / 250000000000000000000000000000000000000000000000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (1-internal-qParam) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_q_below_leaf : (1-leaf-qParam) = ((56657455433006738868999943092544566993261131 / 250000000000000000000000000000000000000000000000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (1-leaf-qParam) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_c_positive : (c) = ((28203727716503369434562415138816850489891696500056907455433006738869 / 250000000000000000000000000000000000000000000000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (c) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_c_below_one : (1-c) = ((249971796272283496630565437584861183149510108303499943092544566993261131 / 250000000000000000000000000000000000000000000000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (1-c) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_q_below_reservations : (c-qParam) = ((1 / 4000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (c-qParam) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_lambda_above_tau : (lam-tau) = ((56407455433006738868999943092544566993261131 / 500000000000000000000000000000000000000000000000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (lam-tau) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_lambda_above_sigma : (lam-sigma) = ((113314910866013477737999943092544566993261131 / 500000000000000000000000000000000000000000000000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (lam-sigma) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_lambda_above_internal : (lam-internal) = ((56407455433006738868999943092544566993261131 / 500000000000000000000000000000000000000000000000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (lam-internal) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_lambda_prime_above_lambda : (lp-lam) = ((56407455433006738868999943092544566993261131 / 500000000000000000000000000000000000000000000000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (lp-lam) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_compact_leaf : (lp-leaf) = ((56657455433006738868999943092544566993261131 / 250000000000000000000000000000000000000000000000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (lp-leaf) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_compact_reservations : (lp-(1-c)) = ((1 / 4000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (lp-(1-c)) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_lambda_prime_below_one : (qParam) = ((28203727716503369434499915138816850489891696500056907455433006738869 / 250000000000000000000000000000000000000000000000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (qParam) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_epsilon_positive : (epsilon) = ((249999750000249999750000000000000000000000000000000000000000000000 / 250027953699762803606630893284245532604957286739213317694137738869) : ℚ) ∧ (0 : ℚ) < (epsilon) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_epsilon_below_one : (1-epsilon) = ((28203699512803856630893284245532604957286739213317694137738869 / 250027953699762803606630893284245532604957286739213317694137738869) : ℚ) ∧ (0 : ℚ) < (1-epsilon) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_guard_width : (1-epsilon) = ((28203699512803856630893284245532604957286739213317694137738869 / 250027953699762803606630893284245532604957286739213317694137738869) : ℚ) ∧ (0 : ℚ) < (1-epsilon) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_K_geometry : (1-epsilon*(1+c)) = ((187528016199700303669130893284245532604957286739213317694137738869 / 250027953699762803606630893284245532604957286739213317694137738869000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (1-epsilon*(1+c)) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_K_dominates_log : (epsilon*c) = ((28203699512803856630705756229332904653617608320033448605133911713260786682305862261131 / 250027953699762803606630893284245532604957286739213317694137738869000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (epsilon*c) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_record_suffix : (1-epsilon) = ((28203699512803856630893284245532604957286739213317694137738869 / 250027953699762803606630893284245532604957286739213317694137738869) : ℚ) ∧ (0 : ℚ) < (1-epsilon) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_phase_local : (1-epsilon-delta) = ((225629596102430853046896246010561076854687282813257307569305994713260786682305862261131 / 2000223629598102428853047146273964260839658293913706541553101910952000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (1-epsilon-delta) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_phase_boundary : (r-delta) = ((45125919220486170609179226839152405128052151848024065087777233113260786682305862261131 / 400044725919620485770609429254792852167931658782741308310620382190400000000000000000000000) : ℚ) ∧ (0 : ℚ) < (r-delta) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_gamma_sublinear : (1-epsilon-r) = ((1 / 2000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (1-epsilon-r) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_cell_above_band : (epsilon-(1-r)/2) = ((499999500000499999499999749972046300237196393369106715754467395042713260786682305862261131 / 1000111814799051214426523573136982130419829146956853270776550955476000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (epsilon-(1-r)/2) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_prime_interval_packing : (1-epsilon) = ((28203699512803856630893284245532604957286739213317694137738869 / 250027953699762803606630893284245532604957286739213317694137738869) : ℚ) ∧ (0 : ℚ) < (1-epsilon) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_alpha_positive : (r) = ((56407399025607713261536540537365447110966847533351142742872780713260786682305862261131 / 500055907399525607213261786568491065209914573478426635388275477738000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (r) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_alpha_below_one : (1-r) = ((499999500000499999500000250027953699762803606630893284245532604957286739213317694137738869 / 500055907399525607213261786568491065209914573478426635388275477738000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (1-r) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_alpha_below_one_fourth : (1/4-r) = ((124957569450855794090053910101585400855367676522073307704325996653786739213317694137738869 / 500055907399525607213261786568491065209914573478426635388275477738000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (1/4-r) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_delta_positive : (delta) = ((1 / 8000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (delta) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_delta_below_one_eighth : (1/8-delta) = ((999999999999999999999999 / 8000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (1/8-delta) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_short_record_fallback : (epsilon-a) = ((124985771559469674632287261529685377995480559442484781152571541385040823194886876611665983695762005501567194399161 / 125013976849881401803315446642122766302478643369606658847068869434500000000000000000000000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (epsilon-a) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_small_field_exposure : (1-epsilon-g) = ((1 / 1000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (1-epsilon-g) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_artificial_boundary : (8-epsilon+r-delta-g) = ((14001791036782819432824377920275575186005677171202332185161413102487860217639953082413216607 / 2000223629598102428853047146273964260839658293913706541553101910952000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (8-epsilon+r-delta-g) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_literal_scalar_guard : (literalGap) = (1936723974066543198917496885658826453564 : ℚ) ∧ (0 : ℚ) < (literalGap) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_row_product_gap : (rowGap) = ((6389 / 25) : ℚ) ∧ (0 : ℚ) < (rowGap) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_g1_above_kappa : ((1-epsilon)-kappa) = ((12837801344731479849844430239564663423413902568985912017495473959 / 62506988424940700901657723321061383151239321684803329423534434717250000000000000000) : ℚ) ∧ (0 : ℚ) < ((1-epsilon)-kappa) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_g2_above_kappa : ((a)-kappa) = ((6362884228738868999943092544566993261131 / 500000000000000000000000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < ((a)-kappa) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_g3_above_kappa : ((g)-kappa) = ((51350955350972219636574114327365369448123005318656908856664201698261131 / 250027953699762803606630893284245532604957286739213317694137738869000000000000000000000000) : ℚ) ∧ (0 : ℚ) < ((g)-kappa) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_g4_above_kappa : ((a)-kappa) = ((6362884228738868999943092544566993261131 / 500000000000000000000000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < ((a)-kappa) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_g5_above_kappa : ((min (1-epsilon-delta) (r-delta))-kappa) = ((82161678578327771276200746902320561664316371484223097698653339199861131 / 400044725919620485770609429254792852167931658782741308310620382190400000000000000000000000) : ℚ) ∧ (0 : ℚ) < ((min (1-epsilon-delta) (r-delta))-kappa) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_g6_above_kappa : ((1-epsilon-delta)-kappa) = ((410809393003453655432218161035175945303712277250262445346537472550261131 / 2000223629598102428853047146273964260839658293913706541553101910952000000000000000000000000) : ℚ) ∧ (0 : ℚ) < ((1-epsilon-delta)-kappa) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem slack_g7_above_kappa : ((epsilon)-kappa) = ((62492886575184298986180078023670096698605108554761333999879467851735912017495473959 / 62506988424940700901657723321061383151239321684803329423534434717250000000000000000) : ℚ) ∧ (0 : ℚ) < ((epsilon)-kappa) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem margins_strict : ∀ x ∈ margins, kappa < x := by
  norm_num [margins, a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem balanced_identities : 1-epsilon-g = eta ∧ 1-epsilon-r = eta/2 ∧ 1-epsilon*(1+c) = eta-epsilon*eta/4 := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem stopped_parameter_choice : a = min actualBitSaving ((1-beta)*b-backoff) ∧ 0 < eta ∧ eta < 1/2 := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem controlling_margin : kappa < g ∧ g < kappa+1/1000000000000000000 := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem fixed_profile_grid_exclusion : (b+1/1000000000000000000000000)/(1+b+1/1000000000000000000000000) < kappa+1/1000000000000000000 := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem gain_over_pinned_bounds : kappa > (384569/10000000000 : ℚ) ∧ kappa > (52789616935221/1000000000000000000 : ℚ) ∧ kappa > (111192082577/1000000000000000 : ℚ) ∧ (1/2^14 : ℚ) < kappa ∧ kappa < (1/2^13 : ℚ) := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem stock_bit_coarse : (529:ℕ)^367 > 2*528^367 ∧ (529:ℕ)^366 ≤ 2*528^366 ∧ (2:ℕ)^26 ≤ 108516254 ∧ 108516254 < (2:ℕ)^27 := by
  norm_num []

theorem stock_complex : (576:ℕ)^200 > 2*574^200 ∧ (576:ℕ)^199 ≤ 2*574^199 ∧ (2:ℕ)^26 ≤ 114315520 ∧ 114315520 < (2:ℕ)^27 := by
  norm_num []

theorem stock_ordinary_leaf : (575:ℕ)^9 > 2*529^9 ∧ (575:ℕ)^8 ≤ 2*529^8 ∧ (2:ℕ)^27 ≤ 188181929 ∧ 188181929 < (2:ℕ)^28 := by
  norm_num []

theorem row_stock : rowCoefficient = 15561 ∧ rowGap = (6389/25 : ℚ) ∧ 4*(32000:ℕ) = 128000 := by
  norm_num [rowCoefficient, rowGap]

theorem semantic_constants : guardE = 1936723974147986188574068436730358952000 ∧ guardB = 1936723974147986188574068436796202829440 ∧ guardC = 69136584229593344553734547662349298866110568132764137982571664415937240220513075200 ∧ literal = 81442989656571551071532498436 := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

theorem finite_bridge : guardE > literal ∧ 2*guardB*(m-574) ≥ mass+guardE ∧ guardC > 2*guardB+18 := by
  norm_num [a, b, kappa, eta, beta, backoff, actualBitSaving, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, rowCoefficient, guardE, guardB, guardC, literal, scalar, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, mass, count, counts, forwardHistogram, initialDimensionHistogram]

-- The analytic meaning of supplied log intervals is external. These
-- statements prove exact rational Taylor inequalities and complete paid sums.
def taylor8 (x : ℚ) : ℚ := 1+x+x^2/2+x^3/6+x^4/24+x^5/120+x^6/720+x^7/5040+x^8/40320
def expUpper (x : ℚ) : ℚ := taylor8 x+x^9/362880/(1-x/10)

def accepted_1 : ℚ := (10007173208708459192443081796658477476273 / 10000000000000000000000000000000000000000)
theorem accepted_interval_1 : (0 : ℚ) ≤ b*(3178053830347945619646941601297 / 500000000000000000000000000000) ∧ b*(3178053830347945619646941601297 / 500000000000000000000000000000) ≤ b*(1271221532139178247858776640519 / 200000000000000000000000000000) ∧ b*(1271221532139178247858776640519 / 200000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_1 : expUpper (b*(1271221532139178247858776640519 / 200000000000000000000000000000)) ≤ accepted_1 := by
  norm_num [expUpper, taylor8, b, accepted_1]

def accepted_2 : ℚ := (2001278141000794096250171811675050044519 / 2000000000000000000000000000000000000000)
theorem accepted_interval_2 : (0 : ℚ) ≤ b*(1132592096027189185975330216227 / 200000000000000000000000000000) ∧ b*(1132592096027189185975330216227 / 200000000000000000000000000000) ≤ b*(353935030008496620617290692571 / 62500000000000000000000000000) ∧ b*(353935030008496620617290692571 / 62500000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_2 : expUpper (b*(353935030008496620617290692571 / 62500000000000000000000000000)) ≤ accepted_2 := by
  norm_num [expUpper, taylor8, b, accepted_2]

def accepted_3 : ℚ := (5002966499022595054406188132806194434321 / 5000000000000000000000000000000000000000)
theorem accepted_interval_3 : (0 : ℚ) ≤ b*(5257495372027781547898637965671 / 1000000000000000000000000000000) ∧ b*(5257495372027781547898637965671 / 1000000000000000000000000000000) ≤ b*(657186921503472693487329745709 / 125000000000000000000000000000) ∧ b*(657186921503472693487329745709 / 125000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_3 : expUpper (b*(657186921503472693487329745709 / 125000000000000000000000000000)) ≤ accepted_3 := by
  norm_num [expUpper, taylor8, b, accepted_3]

def accepted_4 : ℚ := (10005608262486795586682598316938196351633 / 10000000000000000000000000000000000000000)
theorem accepted_interval_4 : (0 : ℚ) ≤ b*(4969813299576000620459418959677 / 1000000000000000000000000000000) ∧ b*(4969813299576000620459418959677 / 1000000000000000000000000000000) ≤ b*(2484906649788000310229709479839 / 500000000000000000000000000000) ∧ b*(2484906649788000310229709479839 / 500000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_4 : expUpper (b*(2484906649788000310229709479839 / 500000000000000000000000000000)) ≤ accepted_4 := by
  norm_num [expUpper, taylor8, b, accepted_4]

def accepted_5 : ℚ := (5002678192638354252310939591491486682637 / 5000000000000000000000000000000000000000)
theorem accepted_interval_5 : (0 : ℚ) ≤ b*(4746669748261790864693123869367 / 1000000000000000000000000000000) ∧ b*(4746669748261790864693123869367 / 1000000000000000000000000000000) ≤ b*(593333718532723858086640483671 / 125000000000000000000000000000) ∧ b*(593333718532723858086640483671 / 125000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_5 : expUpper (b*(593333718532723858086640483671 / 125000000000000000000000000000)) ≤ accepted_5 := by
  norm_num [expUpper, taylor8, b, accepted_5]

def accepted_6 : ℚ := (10005150591318081334437472307882593960501 / 10000000000000000000000000000000000000000)
theorem accepted_interval_6 : (0 : ℚ) ≤ b*(4564348191467836238481405844213 / 1000000000000000000000000000000) ∧ b*(4564348191467836238481405844213 / 1000000000000000000000000000000) ≤ b*(2282174095733918119240702922107 / 500000000000000000000000000000) ∧ b*(2282174095733918119240702922107 / 500000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_6 : expUpper (b*(2282174095733918119240702922107 / 500000000000000000000000000000)) ≤ accepted_6 := by
  norm_num [expUpper, taylor8, b, accepted_6]

def accepted_7 : ℚ := (10004976598307617933072074586029358175999 / 10000000000000000000000000000000000000000)
theorem accepted_interval_7 : (0 : ℚ) ≤ b*(88203950232811558683770609183 / 20000000000000000000000000000) ∧ b*(88203950232811558683770609183 / 20000000000000000000000000000) ≤ b*(4410197511640577934188530459151 / 1000000000000000000000000000000) ∧ b*(4410197511640577934188530459151 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_7 : expUpper (b*(4410197511640577934188530459151 / 1000000000000000000000000000000)) ≤ accepted_7 := by
  norm_num [expUpper, taylor8, b, accepted_7]

def accepted_8 : ℚ := (1250603235144018751348201924633183002973 / 1250000000000000000000000000000000000000)
theorem accepted_interval_8 : (0 : ℚ) ≤ b*(4276666119016055311042186838219 / 1000000000000000000000000000000) ∧ b*(4276666119016055311042186838219 / 1000000000000000000000000000000) ≤ b*(213833305950802765552109341911 / 50000000000000000000000000000) ∧ b*(213833305950802765552109341911 / 50000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_8 : expUpper (b*(213833305950802765552109341911 / 50000000000000000000000000000)) ≤ accepted_8 := by
  norm_num [expUpper, taylor8, b, accepted_8]

def accepted_9 : ℚ := (10004692941083916304711037875234252480853 / 10000000000000000000000000000000000000000)
theorem accepted_interval_9 : (0 : ℚ) ≤ b*(4158883083359671856503392728749 / 1000000000000000000000000000000) ∧ b*(4158883083359671856503392728749 / 1000000000000000000000000000000) ≤ b*(3327106466687737485202714183 / 800000000000000000000000000) ∧ b*(3327106466687737485202714183 / 800000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_9 : expUpper (b*(3327106466687737485202714183 / 800000000000000000000000000)) ≤ accepted_9 := by
  norm_num [expUpper, taylor8, b, accepted_9]

def accepted_10 : ℚ := (2000914804727484006991228354413582185253 / 2000000000000000000000000000000000000000)
theorem accepted_interval_10 : (0 : ℚ) ≤ b*(4053522567701845555275891747909 / 1000000000000000000000000000000) ∧ b*(4053522567701845555275891747909 / 1000000000000000000000000000000) ≤ b*(405352256770184555527589174791 / 100000000000000000000000000000) ∧ b*(405352256770184555527589174791 / 100000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_10 : expUpper (b*(405352256770184555527589174791 / 100000000000000000000000000000)) ≤ accepted_10 := by
  norm_num [expUpper, taylor8, b, accepted_10]

def accepted_11 : ℚ := (10004466450939586496552205020318496489341 / 10000000000000000000000000000000000000000)
theorem accepted_interval_11 : (0 : ℚ) ≤ b*(989553096974380173807984906157 / 250000000000000000000000000000) ∧ b*(989553096974380173807984906157 / 250000000000000000000000000000) ≤ b*(3958212387897520695231939624629 / 1000000000000000000000000000000) ∧ b*(3958212387897520695231939624629 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_11 : expUpper (b*(3958212387897520695231939624629 / 1000000000000000000000000000000)) ≤ accepted_11 := by
  norm_num [expUpper, taylor8, b, accepted_11]

def accepted_12 : ℚ := (2501092061442675825070071222311488555861 / 2500000000000000000000000000000000000000)
theorem accepted_interval_12 : (0 : ℚ) ≤ b*(774240202181578185812834744551 / 200000000000000000000000000000) ∧ b*(774240202181578185812834744551 / 200000000000000000000000000000) ≤ b*(967800252726972732266043430689 / 250000000000000000000000000000) ∧ b*(967800252726972732266043430689 / 250000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_12 : expUpper (b*(967800252726972732266043430689 / 250000000000000000000000000000)) ≤ accepted_12 := by
  norm_num [expUpper, taylor8, b, accepted_12]

def accepted_13 : ℚ := (1000427790662396194996233470122394286203 / 1000000000000000000000000000000000000000)
theorem accepted_interval_13 : (0 : ℚ) ≤ b*(947789575808588625810098940257 / 250000000000000000000000000000) ∧ b*(947789575808588625810098940257 / 250000000000000000000000000000) ≤ b*(3791158303234354503240395761029 / 1000000000000000000000000000000) ∧ b*(3791158303234354503240395761029 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_13 : expUpper (b*(3791158303234354503240395761029 / 1000000000000000000000000000000)) ≤ accepted_13 := by
  norm_num [expUpper, taylor8, b, accepted_13]

def accepted_14 : ℚ := (1250524283295687260942300726950585983367 / 1250000000000000000000000000000000000000)
theorem accepted_interval_14 : (0 : ℚ) ≤ b*(929262582770158156192824584423 / 250000000000000000000000000000) ∧ b*(929262582770158156192824584423 / 250000000000000000000000000000) ≤ b*(3717050331080632624771298337693 / 1000000000000000000000000000000) ∧ b*(3717050331080632624771298337693 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_14 : expUpper (b*(3717050331080632624771298337693 / 1000000000000000000000000000000)) ≤ accepted_14 := by
  norm_num [expUpper, taylor8, b, accepted_14]

def accepted_15 : ℚ := (10004116399776304731797587454524115614907 / 10000000000000000000000000000000000000000)
theorem accepted_interval_15 : (0 : ℚ) ≤ b*(729611491918736234659575726489 / 200000000000000000000000000000) ∧ b*(729611491918736234659575726489 / 200000000000000000000000000000) ≤ b*(1824028729796840586648939316223 / 500000000000000000000000000000) ∧ b*(1824028729796840586648939316223 / 500000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_15 : expUpper (b*(1824028729796840586648939316223 / 500000000000000000000000000000)) ≤ accepted_15 := by
  norm_num [expUpper, taylor8, b, accepted_15]

def accepted_16 : ℚ := (5002021780497624814863799490608923226717 / 5000000000000000000000000000000000000000)
theorem accepted_interval_16 : (0 : ℚ) ≤ b*(3583518938456110001624954716761 / 1000000000000000000000000000000) ∧ b*(3583518938456110001624954716761 / 1000000000000000000000000000000) ≤ b*(1791759469228055000812477358381 / 500000000000000000000000000000) ∧ b*(1791759469228055000812477358381 / 500000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_16 : expUpper (b*(1791759469228055000812477358381 / 500000000000000000000000000000)) ≤ accepted_16 := by
  norm_num [expUpper, taylor8, b, accepted_16]

def accepted_17 : ℚ := (1000397513996078830412133154494488397217 / 1000000000000000000000000000000000000000)
theorem accepted_interval_17 : (0 : ℚ) ≤ b*(44036178957995939488054357309 / 12500000000000000000000000000) ∧ b*(44036178957995939488054357309 / 12500000000000000000000000000) ≤ b*(3522894316639675159044348584721 / 1000000000000000000000000000000) ∧ b*(3522894316639675159044348584721 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_17 : expUpper (b*(3522894316639675159044348584721 / 1000000000000000000000000000000)) ≤ accepted_17 := by
  norm_num [expUpper, taylor8, b, accepted_17]

def accepted_18 : ℚ := (2500977657830542212572203647666043033353 / 2500000000000000000000000000000000000000)
theorem accepted_interval_18 : (0 : ℚ) ≤ b*(346573590279972654708616060729 / 100000000000000000000000000000) ∧ b*(346573590279972654708616060729 / 100000000000000000000000000000) ≤ b*(3465735902799726547086160607291 / 1000000000000000000000000000000) ∧ b*(3465735902799726547086160607291 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_18 : expUpper (b*(3465735902799726547086160607291 / 1000000000000000000000000000000)) ≤ accepted_18 := by
  norm_num [expUpper, taylor8, b, accepted_18]

def accepted_19 : ℚ := (10003849611767539530251041249190273494001 / 10000000000000000000000000000000000000000)
theorem accepted_interval_19 : (0 : ℚ) ≤ b*(1705834340764725389642427885353 / 500000000000000000000000000000) ∧ b*(1705834340764725389642427885353 / 500000000000000000000000000000) ≤ b*(3411668681529450779284855770707 / 1000000000000000000000000000000) ∧ b*(3411668681529450779284855770707 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_19 : expUpper (b*(3411668681529450779284855770707 / 1000000000000000000000000000000)) ≤ accepted_19 := by
  norm_num [expUpper, taylor8, b, accepted_19]

def accepted_20 : ℚ := (10003791723174336695859928379092107147311 / 10000000000000000000000000000000000000000)
theorem accepted_interval_20 : (0 : ℚ) ≤ b*(3360375387141900245858659626451 / 1000000000000000000000000000000) ∧ b*(3360375387141900245858659626451 / 1000000000000000000000000000000) ≤ b*(840093846785475061464664906613 / 250000000000000000000000000000) ∧ b*(840093846785475061464664906613 / 250000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_20 : expUpper (b*(840093846785475061464664906613 / 250000000000000000000000000000)) ≤ accepted_20 := by
  norm_num [expUpper, taylor8, b, accepted_20]

def accepted_21 : ℚ := (10003736659875036312749799798518888013029 / 10000000000000000000000000000000000000000)
theorem accepted_interval_21 : (0 : ℚ) ≤ b*(827896305743117060698321305557 / 250000000000000000000000000000) ∧ b*(827896305743117060698321305557 / 250000000000000000000000000000) ≤ b*(3311585222972468242793285222229 / 1000000000000000000000000000000) ∧ b*(3311585222972468242793285222229 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_21 : expUpper (b*(3311585222972468242793285222229 / 1000000000000000000000000000000)) ≤ accepted_21 := by
  norm_num [expUpper, taylor8, b, accepted_21]

def accepted_22 : ℚ := (5001842079444036409320152786470891628601 / 5000000000000000000000000000000000000000)
theorem accepted_interval_22 : (0 : ℚ) ≤ b*(326506520733757538581470750317 / 100000000000000000000000000000) ∧ b*(326506520733757538581470750317 / 100000000000000000000000000000) ≤ b*(3265065207337575385814707503171 / 1000000000000000000000000000000) ∧ b*(3265065207337575385814707503171 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_22 : expUpper (b*(3265065207337575385814707503171 / 1000000000000000000000000000000)) ≤ accepted_22 := by
  norm_num [expUpper, taylor8, b, accepted_22]

def accepted_23 : ℚ := (10003633992322138767059090899422809010713 / 10000000000000000000000000000000000000000)
theorem accepted_interval_23 : (0 : ℚ) ≤ b*(3220613444766741548487130370783 / 1000000000000000000000000000000) ∧ b*(3220613444766741548487130370783 / 1000000000000000000000000000000) ≤ b*(100644170148960673390222824087 / 31250000000000000000000000000) ∧ b*(100644170148960673390222824087 / 31250000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_23 : expUpper (b*(100644170148960673390222824087 / 31250000000000000000000000000)) ≤ accepted_23 := by
  norm_num [expUpper, taylor8, b, accepted_23]

def accepted_529 : ℚ := (2500024006910801357156667820225605837451 / 2500000000000000000000000000000000000000)
theorem accepted_interval_529 : (0 : ℚ) ≤ b*(85119228837591857680377538973 / 1000000000000000000000000000000) ∧ b*(85119228837591857680377538973 / 1000000000000000000000000000000) ≤ b*(42559614418795928840188769487 / 500000000000000000000000000000) ∧ b*(42559614418795928840188769487 / 500000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_529 : expUpper (b*(42559614418795928840188769487 / 500000000000000000000000000000)) ≤ accepted_529 := by
  norm_num [expUpper, taylor8, b, accepted_529]

def accepted_552 : ℚ := (10000048013706336914502962445538143648637 / 10000000000000000000000000000000000000000)
theorem accepted_interval_552 : (0 : ℚ) ≤ b*(21279807209397964420094384743 / 500000000000000000000000000000) ∧ b*(21279807209397964420094384743 / 500000000000000000000000000000) ≤ b*(42559614418795928840188769487 / 1000000000000000000000000000000) ∧ b*(42559614418795928840188769487 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_552 : expUpper (b*(42559614418795928840188769487 / 1000000000000000000000000000000)) ≤ accepted_552 := by
  norm_num [expUpper, taylor8, b, accepted_552]

def accepted_554 : ℚ := (400001757343114255072912651180621264047 / 400000000000000000000000000000000000000)
theorem accepted_interval_554 : (0 : ℚ) ≤ b*(38942973948607430007253531611 / 1000000000000000000000000000000) ∧ b*(38942973948607430007253531611 / 1000000000000000000000000000000) ≤ b*(9735743487151857501813382903 / 250000000000000000000000000000) ∧ b*(9735743487151857501813382903 / 250000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_554 : expUpper (b*(9735743487151857501813382903 / 250000000000000000000000000000)) ≤ accepted_554 := by
  norm_num [expUpper, taylor8, b, accepted_554]

def accepted_556 : ℚ := (5000019934077114581960794678319392907493 / 5000000000000000000000000000000000000000)
theorem accepted_interval_556 : (0 : ℚ) ≤ b*(17669683222654431635317020401 / 500000000000000000000000000000) ∧ b*(17669683222654431635317020401 / 500000000000000000000000000000) ≤ b*(35339366445308863270634040803 / 1000000000000000000000000000000) ∧ b*(35339366445308863270634040803 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_556 : expUpper (b*(35339366445308863270634040803 / 1000000000000000000000000000000)) ≤ accepted_556 := by
  norm_num [expUpper, taylor8, b, accepted_556]

def accepted_558 : ℚ := (10000035817329848616000090876431682424381 / 10000000000000000000000000000000000000000)
theorem accepted_interval_558 : (0 : ℚ) ≤ b*(7937174578645075289249070687 / 250000000000000000000000000000) ∧ b*(7937174578645075289249070687 / 250000000000000000000000000000) ≤ b*(31748698314580301156996282749 / 1000000000000000000000000000000) ∧ b*(31748698314580301156996282749 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_558 : expUpper (b*(31748698314580301156996282749 / 1000000000000000000000000000000)) ≤ accepted_558 := by
  norm_num [expUpper, taylor8, b, accepted_558]

def accepted_560 : ℚ := (2000006356200048328919135749948149107147 / 2000000000000000000000000000000000000000)
theorem accepted_interval_560 : (0 : ℚ) ≤ b*(7042719241674080479710660023 / 250000000000000000000000000000) ∧ b*(7042719241674080479710660023 / 250000000000000000000000000000) ≤ b*(28170876966696321918842640093 / 1000000000000000000000000000000) ∧ b*(28170876966696321918842640093 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_560 : expUpper (b*(28170876966696321918842640093 / 1000000000000000000000000000000)) ≤ accepted_560 := by
  norm_num [expUpper, taylor8, b, accepted_560]

def accepted_562 : ℚ := (5000013879531026283516616597127113348633 / 5000000000000000000000000000000000000000)
theorem accepted_interval_562 : (0 : ℚ) ≤ b*(12302905401100082385006378221 / 500000000000000000000000000000) ∧ b*(12302905401100082385006378221 / 500000000000000000000000000000) ≤ b*(24605810802200164770012756443 / 1000000000000000000000000000000) ∧ b*(24605810802200164770012756443 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_562 : expUpper (b*(24605810802200164770012756443 / 1000000000000000000000000000000)) ≤ accepted_562 := by
  norm_num [expUpper, taylor8, b, accepted_562]

def accepted_571 : ℚ := (2500002458929401650667719229571399047519 / 2500000000000000000000000000000000000000)
theorem accepted_interval_571 : (0 : ℚ) ≤ b*(4359225519940511281958503327 / 500000000000000000000000000000) ∧ b*(4359225519940511281958503327 / 500000000000000000000000000000) ≤ b*(1743690207976204512783401331 / 200000000000000000000000000000) ∧ b*(1743690207976204512783401331 / 200000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_571 : expUpper (b*(1743690207976204512783401331 / 200000000000000000000000000000)) ≤ accepted_571 := by
  norm_num [expUpper, taylor8, b, accepted_571]

def accepted_572 : ℚ := (2500001965425291953393961431121574574217 / 2500000000000000000000000000000000000000)
theorem accepted_interval_572 : (0 : ℚ) ≤ b*(6968669316093340343987940147 / 1000000000000000000000000000000) ∧ b*(6968669316093340343987940147 / 1000000000000000000000000000000) ≤ b*(1742167329023335085996985037 / 250000000000000000000000000000) ∧ b*(1742167329023335085996985037 / 250000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_572 : expUpper (b*(1742167329023335085996985037 / 250000000000000000000000000000)) ≤ accepted_572 := by
  norm_num [expUpper, taylor8, b, accepted_572]

def accepted_573 : ℚ := (5000002945566591540622685978536652726911 / 5000000000000000000000000000000000000000)
theorem accepted_interval_573 : (0 : ℚ) ≤ b*(5221943981151675048688013469 / 1000000000000000000000000000000) ∧ b*(5221943981151675048688013469 / 1000000000000000000000000000000) ≤ b*(522194398115167504868801347 / 100000000000000000000000000000) ∧ b*(522194398115167504868801347 / 100000000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_573 : expUpper (b*(522194398115167504868801347 / 100000000000000000000000000000)) ≤ accepted_573 := by
  norm_num [expUpper, taylor8, b, accepted_573]

def accepted_574 : ℚ := (5000001962000812862191416361841862291317 / 5000000000000000000000000000000000000000)
theorem accepted_interval_574 : (0 : ℚ) ≤ b*(695652875264964180906992931 / 200000000000000000000000000000) ∧ b*(695652875264964180906992931 / 200000000000000000000000000000) ≤ b*(217391523520301306533435291 / 62500000000000000000000000000) ∧ b*(217391523520301306533435291 / 62500000000000000000000000000) < 1 := by
  norm_num [b]

theorem accepted_taylor_574 : expUpper (b*(217391523520301306533435291 / 62500000000000000000000000000)) ≤ accepted_574 := by
  norm_num [expUpper, taylor8, b, accepted_574]

def acceptedMoment : ℚ :=
  ((1*435042608 : ℚ)/(576*114315520))*accepted_1 +
  ((2*266771296 : ℚ)/(576*114315520))*accepted_2 +
  ((3*29060592 : ℚ)/(576*114315520))*accepted_3 +
  ((4*60639040 : ℚ)/(576*114315520))*accepted_4 +
  ((5*26643936 : ℚ)/(576*114315520))*accepted_5 +
  ((6*15333824 : ℚ)/(576*114315520))*accepted_6 +
  ((7*11743248 : ℚ)/(576*114315520))*accepted_7 +
  ((8*22069696 : ℚ)/(576*114315520))*accepted_8 +
  ((9*3938704 : ℚ)/(576*114315520))*accepted_9 +
  ((10*7735728 : ℚ)/(576*114315520))*accepted_10 +
  ((11*6658960 : ℚ)/(576*114315520))*accepted_11 +
  ((12*33578160 : ℚ)/(576*114315520))*accepted_12 +
  ((13*13184336 : ℚ)/(576*114315520))*accepted_13 +
  ((14*1821600 : ℚ)/(576*114315520))*accepted_14 +
  ((15*3238400 : ℚ)/(576*114315520))*accepted_15 +
  ((16*631488 : ℚ)/(576*114315520))*accepted_16 +
  ((17*404800 : ℚ)/(576*114315520))*accepted_17 +
  ((18*202400 : ℚ)/(576*114315520))*accepted_18 +
  ((19*311696 : ℚ)/(576*114315520))*accepted_19 +
  ((20*550528 : ℚ)/(576*114315520))*accepted_20 +
  ((21*1222496 : ℚ)/(576*114315520))*accepted_21 +
  ((22*64768 : ℚ)/(576*114315520))*accepted_22 +
  ((23*8383408 : ℚ)/(576*114315520))*accepted_23 +
  ((529*8193152 : ℚ)/(576*114315520))*accepted_529 +
  ((552*97071040 : ℚ)/(576*114315520))*accepted_552 +
  ((554*3456992 : ℚ)/(576*114315520))*accepted_554 +
  ((556*1481568 : ℚ)/(576*114315520))*accepted_556 +
  ((558*2384272 : ℚ)/(576*114315520))*accepted_558 +
  ((560*445280 : ℚ)/(576*114315520))*accepted_560 +
  ((562*48576 : ℚ)/(576*114315520))*accepted_562 +
  ((571*740784 : ℚ)/(576*114315520))*accepted_571 +
  ((572*101200 : ℚ)/(576*114315520))*accepted_572 +
  ((573*28336 : ℚ)/(576*114315520))*accepted_573 +
  ((574*364320 : ℚ)/(576*114315520))*accepted_574
def acceptedFromCounts : ℚ :=
  ((1*(count 1 : ℚ))/(m*width))*accepted_1 +
  ((2*(count 2 : ℚ))/(m*width))*accepted_2 +
  ((3*(count 3 : ℚ))/(m*width))*accepted_3 +
  ((4*(count 4 : ℚ))/(m*width))*accepted_4 +
  ((5*(count 5 : ℚ))/(m*width))*accepted_5 +
  ((6*(count 6 : ℚ))/(m*width))*accepted_6 +
  ((7*(count 7 : ℚ))/(m*width))*accepted_7 +
  ((8*(count 8 : ℚ))/(m*width))*accepted_8 +
  ((9*(count 9 : ℚ))/(m*width))*accepted_9 +
  ((10*(count 10 : ℚ))/(m*width))*accepted_10 +
  ((11*(count 11 : ℚ))/(m*width))*accepted_11 +
  ((12*(count 12 : ℚ))/(m*width))*accepted_12 +
  ((13*(count 13 : ℚ))/(m*width))*accepted_13 +
  ((14*(count 14 : ℚ))/(m*width))*accepted_14 +
  ((15*(count 15 : ℚ))/(m*width))*accepted_15 +
  ((16*(count 16 : ℚ))/(m*width))*accepted_16 +
  ((17*(count 17 : ℚ))/(m*width))*accepted_17 +
  ((18*(count 18 : ℚ))/(m*width))*accepted_18 +
  ((19*(count 19 : ℚ))/(m*width))*accepted_19 +
  ((20*(count 20 : ℚ))/(m*width))*accepted_20 +
  ((21*(count 21 : ℚ))/(m*width))*accepted_21 +
  ((22*(count 22 : ℚ))/(m*width))*accepted_22 +
  ((23*(count 23 : ℚ))/(m*width))*accepted_23 +
  ((529*(count 529 : ℚ))/(m*width))*accepted_529 +
  ((552*(count 552 : ℚ))/(m*width))*accepted_552 +
  ((554*(count 554 : ℚ))/(m*width))*accepted_554 +
  ((556*(count 556 : ℚ))/(m*width))*accepted_556 +
  ((558*(count 558 : ℚ))/(m*width))*accepted_558 +
  ((560*(count 560 : ℚ))/(m*width))*accepted_560 +
  ((562*(count 562 : ℚ))/(m*width))*accepted_562 +
  ((571*(count 571 : ℚ))/(m*width))*accepted_571 +
  ((572*(count 572 : ℚ))/(m*width))*accepted_572 +
  ((573*(count 573 : ℚ))/(m*width))*accepted_573 +
  ((574*(count 574 : ℚ))/(m*width))*accepted_574
theorem accepted_profile_link : acceptedFromCounts = acceptedMoment := by
  norm_num [acceptedFromCounts, acceptedMoment, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, count_1, count_10, count_11, count_12, count_13, count_14, count_15, count_16, count_17, count_18, count_19, count_2, count_20, count_21, count_22, count_23, count_3, count_4, count_5, count_529, count_552, count_554, count_556, count_558, count_560, count_562, count_571, count_572, count_573, count_574, count_6, count_7, count_8, count_9]

theorem accepted_moment : acceptedMoment < 1 ∧ acceptedMoment = (40665599999999999999999992105609200772387856393 / 40665600000000000000000000000000000000000000000) := by
  norm_num [acceptedMoment, accepted_1, accepted_10, accepted_11, accepted_12, accepted_13, accepted_14, accepted_15, accepted_16, accepted_17, accepted_18, accepted_19, accepted_2, accepted_20, accepted_21, accepted_22, accepted_23, accepted_3, accepted_4, accepted_5, accepted_529, accepted_552, accepted_554, accepted_556, accepted_558, accepted_560, accepted_562, accepted_571, accepted_572, accepted_573, accepted_574, accepted_6, accepted_7, accepted_8, accepted_9]

theorem accepted_paid_moment : acceptedFromCounts < 1 := by
  rw [accepted_profile_link]
  exact accepted_moment.1

def rejected_1 : ℚ := (5003586604354229596221572701664384374267 / 5000000000000000000000000000000000000000)
theorem rejected_interval_1 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(3178053830347945619646941601297 / 500000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(3178053830347945619646941601297 / 500000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(1271221532139178247858776640519 / 200000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(1271221532139178247858776640519 / 200000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_1 : rejected_1 ≤ taylor8 ((b+1/1000000000000000000000000)*(3178053830347945619646941601297 / 500000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_1]

def rejected_2 : ℚ := (10006390705003970481250915724170359842273 / 10000000000000000000000000000000000000000)
theorem rejected_interval_2 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(1132592096027189185975330216227 / 200000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(1132592096027189185975330216227 / 200000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(353935030008496620617290692571 / 62500000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(353935030008496620617290692571 / 62500000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_2 : rejected_2 ≤ taylor8 ((b+1/1000000000000000000000000)*(1132592096027189185975330216227 / 200000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_2]

def rejected_3 : ℚ := (10005932998045190108812428871758817532111 / 10000000000000000000000000000000000000000)
theorem rejected_interval_3 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(5257495372027781547898637965671 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(5257495372027781547898637965671 / 1000000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(657186921503472693487329745709 / 125000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(657186921503472693487329745709 / 125000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_3 : rejected_3 ≤ taylor8 ((b+1/1000000000000000000000000)*(5257495372027781547898637965671 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_3]

def rejected_4 : ℚ := (1000560826248679558668264804294320832637 / 1000000000000000000000000000000000000000)
theorem rejected_interval_4 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(4969813299576000620459418959677 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(4969813299576000620459418959677 / 1000000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(2484906649788000310229709479839 / 500000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(2484906649788000310229709479839 / 500000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_4 : rejected_4 ≤ taylor8 ((b+1/1000000000000000000000000)*(4969813299576000620459418959677 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_4]

def rejected_5 : ℚ := (10005356385276708504621926675105446707631 / 10000000000000000000000000000000000000000)
theorem rejected_interval_5 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(4746669748261790864693123869367 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(4746669748261790864693123869367 / 1000000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(593333718532723858086640483671 / 125000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(593333718532723858086640483671 / 125000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_5 : rejected_5 ≤ taylor8 ((b+1/1000000000000000000000000)*(4746669748261790864693123869367 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_5]

def rejected_6 : ℚ := (5002575295659040667218758987436799803833 / 5000000000000000000000000000000000000000)
theorem rejected_interval_6 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(4564348191467836238481405844213 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(4564348191467836238481405844213 / 1000000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(2282174095733918119240702922107 / 500000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(2282174095733918119240702922107 / 500000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_6 : rejected_6 ≤ taylor8 ((b+1/1000000000000000000000000)*(4564348191467836238481405844213 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_6]

def rejected_7 : ℚ := (5002488299153808966536059354976127437137 / 5000000000000000000000000000000000000000)
theorem rejected_interval_7 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(88203950232811558683770609183 / 20000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(88203950232811558683770609183 / 20000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(4410197511640577934188530459151 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(4410197511640577934188530459151 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_7 : rejected_7 ≤ taylor8 ((b+1/1000000000000000000000000)*(88203950232811558683770609183 / 20000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_7]

def rejected_8 : ℚ := (10004825881152150010785658184365335434401 / 10000000000000000000000000000000000000000)
theorem rejected_interval_8 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(4276666119016055311042186838219 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(4276666119016055311042186838219 / 1000000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(213833305950802765552109341911 / 50000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(213833305950802765552109341911 / 50000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_8 : rejected_8 ≤ taylor8 ((b+1/1000000000000000000000000)*(4276666119016055311042186838219 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_8]

def rejected_9 : ℚ := (625293308817744769044442467723904887727 / 625000000000000000000000000000000000000)
theorem rejected_interval_9 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(4158883083359671856503392728749 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(4158883083359671856503392728749 / 1000000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(3327106466687737485202714183 / 800000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(3327106466687737485202714183 / 800000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_9 : rejected_9 ≤ taylor8 ((b+1/1000000000000000000000000)*(4158883083359671856503392728749 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_9]

def rejected_10 : ℚ := (10004574023637420034956182325834494831437 / 10000000000000000000000000000000000000000)
theorem rejected_interval_10 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(4053522567701845555275891747909 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(4053522567701845555275891747909 / 1000000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(405352256770184555527589174791 / 100000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(405352256770184555527589174791 / 100000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_10 : rejected_10 ≤ taylor8 ((b+1/1000000000000000000000000)*(4053522567701845555275891747909 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_10]

def rejected_11 : ℚ := (5002233225469793248276122310060767877723 / 5000000000000000000000000000000000000000)
theorem rejected_interval_11 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(989553096974380173807984906157 / 250000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(989553096974380173807984906157 / 250000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(3958212387897520695231939624629 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(3958212387897520695231939624629 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_11 : rejected_11 ≤ taylor8 ((b+1/1000000000000000000000000)*(989553096974380173807984906157 / 250000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_11]

def rejected_12 : ℚ := (10004368245770703300280323618166419601223 / 10000000000000000000000000000000000000000)
theorem rejected_interval_12 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(774240202181578185812834744551 / 200000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(774240202181578185812834744551 / 200000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(967800252726972732266043430689 / 250000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(967800252726972732266043430689 / 250000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_12 : rejected_12 ≤ taylor8 ((b+1/1000000000000000000000000)*(774240202181578185812834744551 / 200000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_12]

def rejected_13 : ℚ := (10004277906623961949962372629025195281639 / 10000000000000000000000000000000000000000)
theorem rejected_interval_13 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(947789575808588625810098940257 / 250000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(947789575808588625810098940257 / 250000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(3791158303234354503240395761029 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(3791158303234354503240395761029 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_13 : rejected_13 ≤ taylor8 ((b+1/1000000000000000000000000)*(947789575808588625810098940257 / 250000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_13]

def rejected_14 : ℚ := (2000838853273099617507688600339659343221 / 2000000000000000000000000000000000000000)
theorem rejected_interval_14 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(929262582770158156192824584423 / 250000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(929262582770158156192824584423 / 250000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(3717050331080632624771298337693 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(3717050331080632624771298337693 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_14 : rejected_14 ≤ taylor8 ((b+1/1000000000000000000000000)*(929262582770158156192824584423 / 250000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_14]

def rejected_15 : ℚ := (10004116399776304731797623950115573324387 / 10000000000000000000000000000000000000000)
theorem rejected_interval_15 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(729611491918736234659575726489 / 200000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(729611491918736234659575726489 / 200000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(1824028729796840586648939316223 / 500000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(1824028729796840586648939316223 / 500000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_15 : rejected_15 ≤ taylor8 ((b+1/1000000000000000000000000)*(729611491918736234659575726489 / 200000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_15]

def rejected_16 : ℚ := (5002021780497624814863817415448703641629 / 5000000000000000000000000000000000000000)
theorem rejected_interval_16 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(3583518938456110001624954716761 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(3583518938456110001624954716761 / 1000000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(1791759469228055000812477358381 / 500000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(1791759469228055000812477358381 / 500000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_16 : rejected_16 ≤ taylor8 ((b+1/1000000000000000000000000)*(3583518938456110001624954716761 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_16]

def rejected_17 : ℚ := (10003975139960788304121366787892047209213 / 10000000000000000000000000000000000000000)
theorem rejected_interval_17 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(44036178957995939488054357309 / 12500000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(44036178957995939488054357309 / 12500000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(3522894316639675159044348584721 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(3522894316639675159044348584721 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_17 : rejected_17 ≤ taylor8 ((b+1/1000000000000000000000000)*(44036178957995939488054357309 / 12500000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_17]

def rejected_18 : ℚ := (1250488828915271106286106157697051796507 / 1250000000000000000000000000000000000000)
theorem rejected_interval_18 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(346573590279972654708616060729 / 100000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(346573590279972654708616060729 / 100000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(3465735902799726547086160607291 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(3465735902799726547086160607291 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_18 : rejected_18 ≤ taylor8 ((b+1/1000000000000000000000000)*(346573590279972654708616060729 / 100000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_18]

def rejected_19 : ℚ := (5001924805883769765125537689505343779089 / 5000000000000000000000000000000000000000)
theorem rejected_interval_19 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(1705834340764725389642427885353 / 500000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(1705834340764725389642427885353 / 500000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(3411668681529450779284855770707 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(3411668681529450779284855770707 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_19 : rejected_19 ≤ taylor8 ((b+1/1000000000000000000000000)*(1705834340764725389642427885353 / 500000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_19]

def rejected_20 : ℚ := (400151668926973467834398479823503626527 / 400000000000000000000000000000000000000)
theorem rejected_interval_20 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(3360375387141900245858659626451 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(3360375387141900245858659626451 / 1000000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(840093846785475061464664906613 / 250000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(840093846785475061464664906613 / 250000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_20 : rejected_20 ≤ taylor8 ((b+1/1000000000000000000000000)*(3360375387141900245858659626451 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_20]

def rejected_21 : ℚ := (10003736659875036312749832926745384230677 / 10000000000000000000000000000000000000000)
theorem rejected_interval_21 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(827896305743117060698321305557 / 250000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(827896305743117060698321305557 / 250000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(3311585222972468242793285222229 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(3311585222972468242793285222229 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_21 : rejected_21 ≤ taylor8 ((b+1/1000000000000000000000000)*(827896305743117060698321305557 / 250000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_21]

def rejected_22 : ℚ := (100036841588880728186403382356228745047 / 100000000000000000000000000000000000000)
theorem rejected_interval_22 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(326506520733757538581470750317 / 100000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(326506520733757538581470750317 / 100000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(3265065207337575385814707503171 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(3265065207337575385814707503171 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_22 : rejected_22 ≤ taylor8 ((b+1/1000000000000000000000000)*(326506520733757538581470750317 / 100000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_22]

def rejected_23 : ℚ := (5001816996161069383529561558630470038693 / 5000000000000000000000000000000000000000)
theorem rejected_interval_23 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(3220613444766741548487130370783 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(3220613444766741548487130370783 / 1000000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(100644170148960673390222824087 / 31250000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(100644170148960673390222824087 / 31250000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_23 : rejected_23 ≤ taylor8 ((b+1/1000000000000000000000000)*(3220613444766741548487130370783 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_23]

def rejected_529 : ℚ := (10000096027643205428626672132102884396499 / 10000000000000000000000000000000000000000)
theorem rejected_interval_529 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(85119228837591857680377538973 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(85119228837591857680377538973 / 1000000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(42559614418795928840188769487 / 500000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(42559614418795928840188769487 / 500000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_529 : rejected_529 ≤ taylor8 ((b+1/1000000000000000000000000)*(85119228837591857680377538973 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_529]

def rejected_552 : ℚ := (10000048013706336914502962871136330153269 / 10000000000000000000000000000000000000000)
theorem rejected_interval_552 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(21279807209397964420094384743 / 500000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(21279807209397964420094384743 / 500000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(42559614418795928840188769487 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(42559614418795928840188769487 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_552 : rejected_552 ≤ taylor8 ((b+1/1000000000000000000000000)*(21279807209397964420094384743 / 500000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_552]

def rejected_554 : ℚ := (1250005491697232047102852083618372607909 / 1250000000000000000000000000000000000000)
theorem rejected_interval_554 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(38942973948607430007253531611 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(38942973948607430007253531611 / 1000000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(9735743487151857501813382903 / 250000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(9735743487151857501813382903 / 250000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_554 : rejected_554 ≤ taylor8 ((b+1/1000000000000000000000000)*(38942973948607430007253531611 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_554]

def rejected_556 : ℚ := (156250622939909830686274839219279032113 / 156250000000000000000000000000000000000)
theorem rejected_interval_556 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(17669683222654431635317020401 / 500000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(17669683222654431635317020401 / 500000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(35339366445308863270634040803 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(35339366445308863270634040803 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_556 : rejected_556 ≤ taylor8 ((b+1/1000000000000000000000000)*(17669683222654431635317020401 / 500000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_556]

def rejected_558 : ℚ := (1000003581732984861600009119391980159563 / 1000000000000000000000000000000000000000)
theorem rejected_interval_558 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(7937174578645075289249070687 / 250000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(7937174578645075289249070687 / 250000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(31748698314580301156996282749 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(31748698314580301156996282749 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_558 : rejected_558 ≤ taylor8 ((b+1/1000000000000000000000000)*(7937174578645075289249070687 / 250000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_558]

def rejected_560 : ℚ := (10000031781000241644595679031450409373193 / 10000000000000000000000000000000000000000)
theorem rejected_interval_560 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(7042719241674080479710660023 / 250000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(7042719241674080479710660023 / 250000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(28170876966696321918842640093 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(28170876966696321918842640093 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_560 : rejected_560 ≤ taylor8 ((b+1/1000000000000000000000000)*(7042719241674080479710660023 / 250000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_560]

def rejected_562 : ℚ := (10000027759062052567033233440313016625343 / 10000000000000000000000000000000000000000)
theorem rejected_interval_562 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(12302905401100082385006378221 / 500000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(12302905401100082385006378221 / 500000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(24605810802200164770012756443 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(24605810802200164770012756443 / 1000000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_562 : rejected_562 ≤ taylor8 ((b+1/1000000000000000000000000)*(12302905401100082385006378221 / 500000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_562]

def rejected_571 : ℚ := (10000009835717606602670877005470191212957 / 10000000000000000000000000000000000000000)
theorem rejected_interval_571 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(4359225519940511281958503327 / 500000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(4359225519940511281958503327 / 500000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(1743690207976204512783401331 / 200000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(1743690207976204512783401331 / 200000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_571 : rejected_571 ≤ taylor8 ((b+1/1000000000000000000000000)*(4359225519940511281958503327 / 500000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_571]

def rejected_572 : ℚ := (5000003930850583906787922897086522557623 / 5000000000000000000000000000000000000000)
theorem rejected_interval_572 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(6968669316093340343987940147 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(6968669316093340343987940147 / 1000000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(1742167329023335085996985037 / 250000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(1742167329023335085996985037 / 250000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_572 : rejected_572 ≤ taylor8 ((b+1/1000000000000000000000000)*(6968669316093340343987940147 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_572]

def rejected_573 : ℚ := (2000001178226636616249074401858554980071 / 2000000000000000000000000000000000000000)
theorem rejected_interval_573 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(5221943981151675048688013469 / 1000000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(5221943981151675048688013469 / 1000000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(522194398115167504868801347 / 100000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(522194398115167504868801347 / 100000000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_573 : rejected_573 ≤ taylor8 ((b+1/1000000000000000000000000)*(5221943981151675048688013469 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_573]

def rejected_574 : ℚ := (10000003924001625724382832758466380866447 / 10000000000000000000000000000000000000000)
theorem rejected_interval_574 : (0 : ℚ) ≤ (b+1/1000000000000000000000000)*(695652875264964180906992931 / 200000000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(695652875264964180906992931 / 200000000000000000000000000000) ≤ (b+1/1000000000000000000000000)*(217391523520301306533435291 / 62500000000000000000000000000) ∧ (b+1/1000000000000000000000000)*(217391523520301306533435291 / 62500000000000000000000000000) < 1 := by
  norm_num [b]

theorem rejected_taylor_574 : rejected_574 ≤ taylor8 ((b+1/1000000000000000000000000)*(695652875264964180906992931 / 200000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, b, rejected_574]

def rejectedMoment : ℚ :=
  ((1*435042608 : ℚ)/(576*114315520))*rejected_1 +
  ((2*266771296 : ℚ)/(576*114315520))*rejected_2 +
  ((3*29060592 : ℚ)/(576*114315520))*rejected_3 +
  ((4*60639040 : ℚ)/(576*114315520))*rejected_4 +
  ((5*26643936 : ℚ)/(576*114315520))*rejected_5 +
  ((6*15333824 : ℚ)/(576*114315520))*rejected_6 +
  ((7*11743248 : ℚ)/(576*114315520))*rejected_7 +
  ((8*22069696 : ℚ)/(576*114315520))*rejected_8 +
  ((9*3938704 : ℚ)/(576*114315520))*rejected_9 +
  ((10*7735728 : ℚ)/(576*114315520))*rejected_10 +
  ((11*6658960 : ℚ)/(576*114315520))*rejected_11 +
  ((12*33578160 : ℚ)/(576*114315520))*rejected_12 +
  ((13*13184336 : ℚ)/(576*114315520))*rejected_13 +
  ((14*1821600 : ℚ)/(576*114315520))*rejected_14 +
  ((15*3238400 : ℚ)/(576*114315520))*rejected_15 +
  ((16*631488 : ℚ)/(576*114315520))*rejected_16 +
  ((17*404800 : ℚ)/(576*114315520))*rejected_17 +
  ((18*202400 : ℚ)/(576*114315520))*rejected_18 +
  ((19*311696 : ℚ)/(576*114315520))*rejected_19 +
  ((20*550528 : ℚ)/(576*114315520))*rejected_20 +
  ((21*1222496 : ℚ)/(576*114315520))*rejected_21 +
  ((22*64768 : ℚ)/(576*114315520))*rejected_22 +
  ((23*8383408 : ℚ)/(576*114315520))*rejected_23 +
  ((529*8193152 : ℚ)/(576*114315520))*rejected_529 +
  ((552*97071040 : ℚ)/(576*114315520))*rejected_552 +
  ((554*3456992 : ℚ)/(576*114315520))*rejected_554 +
  ((556*1481568 : ℚ)/(576*114315520))*rejected_556 +
  ((558*2384272 : ℚ)/(576*114315520))*rejected_558 +
  ((560*445280 : ℚ)/(576*114315520))*rejected_560 +
  ((562*48576 : ℚ)/(576*114315520))*rejected_562 +
  ((571*740784 : ℚ)/(576*114315520))*rejected_571 +
  ((572*101200 : ℚ)/(576*114315520))*rejected_572 +
  ((573*28336 : ℚ)/(576*114315520))*rejected_573 +
  ((574*364320 : ℚ)/(576*114315520))*rejected_574
def rejectedFromCounts : ℚ :=
  ((1*(count 1 : ℚ))/(m*width))*rejected_1 +
  ((2*(count 2 : ℚ))/(m*width))*rejected_2 +
  ((3*(count 3 : ℚ))/(m*width))*rejected_3 +
  ((4*(count 4 : ℚ))/(m*width))*rejected_4 +
  ((5*(count 5 : ℚ))/(m*width))*rejected_5 +
  ((6*(count 6 : ℚ))/(m*width))*rejected_6 +
  ((7*(count 7 : ℚ))/(m*width))*rejected_7 +
  ((8*(count 8 : ℚ))/(m*width))*rejected_8 +
  ((9*(count 9 : ℚ))/(m*width))*rejected_9 +
  ((10*(count 10 : ℚ))/(m*width))*rejected_10 +
  ((11*(count 11 : ℚ))/(m*width))*rejected_11 +
  ((12*(count 12 : ℚ))/(m*width))*rejected_12 +
  ((13*(count 13 : ℚ))/(m*width))*rejected_13 +
  ((14*(count 14 : ℚ))/(m*width))*rejected_14 +
  ((15*(count 15 : ℚ))/(m*width))*rejected_15 +
  ((16*(count 16 : ℚ))/(m*width))*rejected_16 +
  ((17*(count 17 : ℚ))/(m*width))*rejected_17 +
  ((18*(count 18 : ℚ))/(m*width))*rejected_18 +
  ((19*(count 19 : ℚ))/(m*width))*rejected_19 +
  ((20*(count 20 : ℚ))/(m*width))*rejected_20 +
  ((21*(count 21 : ℚ))/(m*width))*rejected_21 +
  ((22*(count 22 : ℚ))/(m*width))*rejected_22 +
  ((23*(count 23 : ℚ))/(m*width))*rejected_23 +
  ((529*(count 529 : ℚ))/(m*width))*rejected_529 +
  ((552*(count 552 : ℚ))/(m*width))*rejected_552 +
  ((554*(count 554 : ℚ))/(m*width))*rejected_554 +
  ((556*(count 556 : ℚ))/(m*width))*rejected_556 +
  ((558*(count 558 : ℚ))/(m*width))*rejected_558 +
  ((560*(count 560 : ℚ))/(m*width))*rejected_560 +
  ((562*(count 562 : ℚ))/(m*width))*rejected_562 +
  ((571*(count 571 : ℚ))/(m*width))*rejected_571 +
  ((572*(count 572 : ℚ))/(m*width))*rejected_572 +
  ((573*(count 573 : ℚ))/(m*width))*rejected_573 +
  ((574*(count 574 : ℚ))/(m*width))*rejected_574
theorem rejected_profile_link : rejectedFromCounts = rejectedMoment := by
  norm_num [rejectedFromCounts, rejectedMoment, h, m, v, n, roles, width, virtualRoles, births, terminals, Nat.choose, count_1, count_10, count_11, count_12, count_13, count_14, count_15, count_16, count_17, count_18, count_19, count_2, count_20, count_21, count_22, count_23, count_3, count_4, count_5, count_529, count_552, count_554, count_556, count_558, count_560, count_562, count_571, count_572, count_573, count_574, count_6, count_7, count_8, count_9]

theorem rejected_moment : 1 < rejectedMoment ∧ rejectedMoment = (40665600000000000000000002301675639985445787697 / 40665600000000000000000000000000000000000000000) := by
  norm_num [rejectedMoment, rejected_1, rejected_10, rejected_11, rejected_12, rejected_13, rejected_14, rejected_15, rejected_16, rejected_17, rejected_18, rejected_19, rejected_2, rejected_20, rejected_21, rejected_22, rejected_23, rejected_3, rejected_4, rejected_5, rejected_529, rejected_552, rejected_554, rejected_556, rejected_558, rejected_560, rejected_562, rejected_571, rejected_572, rejected_573, rejected_574, rejected_6, rejected_7, rejected_8, rejected_9]

theorem rejected_paid_moment : 1 < rejectedFromCounts := by
  rw [rejected_profile_link]
  exact rejected_moment.1

end KappaCheck.ShrunkBirthTerminal
#print axioms KappaCheck.ShrunkBirthTerminal.network_counts
#print axioms KappaCheck.ShrunkBirthTerminal.initial_dimension_count
#print axioms KappaCheck.ShrunkBirthTerminal.rank_mass
#print axioms KappaCheck.ShrunkBirthTerminal.count_1
#print axioms KappaCheck.ShrunkBirthTerminal.count_2
#print axioms KappaCheck.ShrunkBirthTerminal.count_3
#print axioms KappaCheck.ShrunkBirthTerminal.count_4
#print axioms KappaCheck.ShrunkBirthTerminal.count_5
#print axioms KappaCheck.ShrunkBirthTerminal.count_6
#print axioms KappaCheck.ShrunkBirthTerminal.count_7
#print axioms KappaCheck.ShrunkBirthTerminal.count_8
#print axioms KappaCheck.ShrunkBirthTerminal.count_9
#print axioms KappaCheck.ShrunkBirthTerminal.count_10
#print axioms KappaCheck.ShrunkBirthTerminal.count_11
#print axioms KappaCheck.ShrunkBirthTerminal.count_12
#print axioms KappaCheck.ShrunkBirthTerminal.count_13
#print axioms KappaCheck.ShrunkBirthTerminal.count_14
#print axioms KappaCheck.ShrunkBirthTerminal.count_15
#print axioms KappaCheck.ShrunkBirthTerminal.count_16
#print axioms KappaCheck.ShrunkBirthTerminal.count_17
#print axioms KappaCheck.ShrunkBirthTerminal.count_18
#print axioms KappaCheck.ShrunkBirthTerminal.count_19
#print axioms KappaCheck.ShrunkBirthTerminal.count_20
#print axioms KappaCheck.ShrunkBirthTerminal.count_21
#print axioms KappaCheck.ShrunkBirthTerminal.count_22
#print axioms KappaCheck.ShrunkBirthTerminal.count_23
#print axioms KappaCheck.ShrunkBirthTerminal.count_529
#print axioms KappaCheck.ShrunkBirthTerminal.count_552
#print axioms KappaCheck.ShrunkBirthTerminal.count_554
#print axioms KappaCheck.ShrunkBirthTerminal.count_556
#print axioms KappaCheck.ShrunkBirthTerminal.count_558
#print axioms KappaCheck.ShrunkBirthTerminal.count_560
#print axioms KappaCheck.ShrunkBirthTerminal.count_562
#print axioms KappaCheck.ShrunkBirthTerminal.count_571
#print axioms KappaCheck.ShrunkBirthTerminal.count_572
#print axioms KappaCheck.ShrunkBirthTerminal.count_573
#print axioms KappaCheck.ShrunkBirthTerminal.count_574
#print axioms KappaCheck.ShrunkBirthTerminal.complete_child_support
#print axioms KappaCheck.ShrunkBirthTerminal.strict_child_contraction
#print axioms KappaCheck.ShrunkBirthTerminal.slack_a_positive
#print axioms KappaCheck.ShrunkBirthTerminal.slack_a_below_b
#print axioms KappaCheck.ShrunkBirthTerminal.slack_b_below_one_over32
#print axioms KappaCheck.ShrunkBirthTerminal.slack_beta_positive
#print axioms KappaCheck.ShrunkBirthTerminal.slack_beta_below_one
#print axioms KappaCheck.ShrunkBirthTerminal.slack_phase_leaf_above_bit
#print axioms KappaCheck.ShrunkBirthTerminal.slack_q_positive
#print axioms KappaCheck.ShrunkBirthTerminal.slack_q_below_internal
#print axioms KappaCheck.ShrunkBirthTerminal.slack_q_below_leaf
#print axioms KappaCheck.ShrunkBirthTerminal.slack_c_positive
#print axioms KappaCheck.ShrunkBirthTerminal.slack_c_below_one
#print axioms KappaCheck.ShrunkBirthTerminal.slack_q_below_reservations
#print axioms KappaCheck.ShrunkBirthTerminal.slack_lambda_above_tau
#print axioms KappaCheck.ShrunkBirthTerminal.slack_lambda_above_sigma
#print axioms KappaCheck.ShrunkBirthTerminal.slack_lambda_above_internal
#print axioms KappaCheck.ShrunkBirthTerminal.slack_lambda_prime_above_lambda
#print axioms KappaCheck.ShrunkBirthTerminal.slack_compact_leaf
#print axioms KappaCheck.ShrunkBirthTerminal.slack_compact_reservations
#print axioms KappaCheck.ShrunkBirthTerminal.slack_lambda_prime_below_one
#print axioms KappaCheck.ShrunkBirthTerminal.slack_epsilon_positive
#print axioms KappaCheck.ShrunkBirthTerminal.slack_epsilon_below_one
#print axioms KappaCheck.ShrunkBirthTerminal.slack_guard_width
#print axioms KappaCheck.ShrunkBirthTerminal.slack_K_geometry
#print axioms KappaCheck.ShrunkBirthTerminal.slack_K_dominates_log
#print axioms KappaCheck.ShrunkBirthTerminal.slack_record_suffix
#print axioms KappaCheck.ShrunkBirthTerminal.slack_phase_local
#print axioms KappaCheck.ShrunkBirthTerminal.slack_phase_boundary
#print axioms KappaCheck.ShrunkBirthTerminal.slack_gamma_sublinear
#print axioms KappaCheck.ShrunkBirthTerminal.slack_cell_above_band
#print axioms KappaCheck.ShrunkBirthTerminal.slack_prime_interval_packing
#print axioms KappaCheck.ShrunkBirthTerminal.slack_alpha_positive
#print axioms KappaCheck.ShrunkBirthTerminal.slack_alpha_below_one
#print axioms KappaCheck.ShrunkBirthTerminal.slack_alpha_below_one_fourth
#print axioms KappaCheck.ShrunkBirthTerminal.slack_delta_positive
#print axioms KappaCheck.ShrunkBirthTerminal.slack_delta_below_one_eighth
#print axioms KappaCheck.ShrunkBirthTerminal.slack_short_record_fallback
#print axioms KappaCheck.ShrunkBirthTerminal.slack_small_field_exposure
#print axioms KappaCheck.ShrunkBirthTerminal.slack_artificial_boundary
#print axioms KappaCheck.ShrunkBirthTerminal.slack_literal_scalar_guard
#print axioms KappaCheck.ShrunkBirthTerminal.slack_row_product_gap
#print axioms KappaCheck.ShrunkBirthTerminal.slack_g1_above_kappa
#print axioms KappaCheck.ShrunkBirthTerminal.slack_g2_above_kappa
#print axioms KappaCheck.ShrunkBirthTerminal.slack_g3_above_kappa
#print axioms KappaCheck.ShrunkBirthTerminal.slack_g4_above_kappa
#print axioms KappaCheck.ShrunkBirthTerminal.slack_g5_above_kappa
#print axioms KappaCheck.ShrunkBirthTerminal.slack_g6_above_kappa
#print axioms KappaCheck.ShrunkBirthTerminal.slack_g7_above_kappa
#print axioms KappaCheck.ShrunkBirthTerminal.margins_strict
#print axioms KappaCheck.ShrunkBirthTerminal.balanced_identities
#print axioms KappaCheck.ShrunkBirthTerminal.stopped_parameter_choice
#print axioms KappaCheck.ShrunkBirthTerminal.controlling_margin
#print axioms KappaCheck.ShrunkBirthTerminal.fixed_profile_grid_exclusion
#print axioms KappaCheck.ShrunkBirthTerminal.gain_over_pinned_bounds
#print axioms KappaCheck.ShrunkBirthTerminal.stock_bit_coarse
#print axioms KappaCheck.ShrunkBirthTerminal.stock_complex
#print axioms KappaCheck.ShrunkBirthTerminal.stock_ordinary_leaf
#print axioms KappaCheck.ShrunkBirthTerminal.row_stock
#print axioms KappaCheck.ShrunkBirthTerminal.semantic_constants
#print axioms KappaCheck.ShrunkBirthTerminal.finite_bridge
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_1
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_1
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_2
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_2
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_3
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_3
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_4
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_4
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_5
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_5
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_6
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_6
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_7
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_7
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_8
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_8
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_9
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_9
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_10
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_10
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_11
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_11
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_12
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_12
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_13
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_13
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_14
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_14
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_15
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_15
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_16
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_16
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_17
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_17
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_18
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_18
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_19
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_19
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_20
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_20
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_21
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_21
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_22
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_22
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_23
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_23
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_529
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_529
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_552
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_552
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_554
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_554
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_556
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_556
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_558
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_558
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_560
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_560
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_562
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_562
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_571
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_571
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_572
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_572
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_573
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_573
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_interval_574
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_taylor_574
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_profile_link
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_moment
#print axioms KappaCheck.ShrunkBirthTerminal.accepted_paid_moment
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_1
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_1
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_2
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_2
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_3
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_3
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_4
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_4
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_5
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_5
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_6
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_6
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_7
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_7
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_8
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_8
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_9
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_9
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_10
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_10
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_11
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_11
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_12
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_12
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_13
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_13
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_14
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_14
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_15
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_15
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_16
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_16
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_17
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_17
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_18
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_18
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_19
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_19
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_20
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_20
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_21
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_21
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_22
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_22
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_23
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_23
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_529
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_529
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_552
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_552
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_554
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_554
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_556
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_556
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_558
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_558
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_560
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_560
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_562
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_562
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_571
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_571
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_572
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_572
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_573
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_573
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_interval_574
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_taylor_574
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_profile_link
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_moment
#print axioms KappaCheck.ShrunkBirthTerminal.rejected_paid_moment
