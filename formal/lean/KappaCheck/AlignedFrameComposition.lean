import Mathlib.Tactic.NormNum
import Mathlib.Data.Nat.Choose.Basic

/-!
Exact arithmetic supplement for the frozen final frame composition.
Prepared with OpenAI assistance; inherited formulas retain their upstream credits.

This file proves rational arithmetic only. The supplied physical profile arrays,
the analytic validity of the logarithm and Taylor enclosures, and the all-size
tape/prime/recovery hypotheses are outside this module. It does not assert an
unconditional multiplication theorem. No sorry, native_decide, or new axioms.
The theorem statements recompute counts and parameter formulas rather than
merely asserting positivity of externally supplied fractions.
-/
namespace KappaCheck.AlignedFrameComposition
set_option maxRecDepth 10000
set_option maxHeartbeats 4000000

-- Frozen selection SHA256: 43a762adf17b2338b2d7ec486fd6eb17d00d1d221e7f1e4041711cbce9964ea7
-- Complete portfolio SHA256: 5ecde1320034b152779c702d7ccefdf953a00f678a62adcfd8c3ef7a8fb1cf31
def m : ℕ := 23 * 25
def n : ℕ := Nat.choose 23 3 * Nat.choose 25 3
def roles23 : ℕ := 26387
def blocks23 : List ℕ := [0, 371505, 11855, 16183, 4817, 3983, 3154, 2137, 1923, 1415, 1172, 853, 822, 499, 393, 293, 268, 68, 320, 0, 171, 23, 0, 0]
def roles25 : ℕ := 34772
def blocks25 : List ℕ := [0, 504683, 18260, 19030, 7746, 4400, 4491, 3537, 3136, 2209, 2257, 1550, 1493, 910, 909, 469, 581, 263, 210, 59, 387, 101, 169, 25, 0, 0]
def width : ℕ := 2*n + Nat.choose 25 3 * roles23 + Nat.choose 23 3 * roles25
def counts : List (ℕ × ℕ) :=
  [(1, 23*n), (21, 4*n), (17, 2*n), (481, 2*n), (23, 2*n),
   (23, Nat.choose 25 3 * roles23), (529, Nat.choose 25 3 * roles23),
   (25, Nat.choose 23 3 * roles25), (525, Nat.choose 23 3 * roles25)] ++
  (blocks23.zipIdx.map fun (c,t) => (t, Nat.choose 25 3 * c)) ++
  (blocks25.zipIdx.map fun (c,t) => (t, Nat.choose 23 3 * c))
def count (t : ℕ) : ℕ :=
  (counts.map fun p => if p.1 = t then p.2 else 0).sum
def mass : ℕ := (counts.map fun p => p.1*p.2).sum

theorem network_counts : m = 575 ∧ n = 4073300 ∧ width = 130417912 := by
  norm_num [m, n, width, roles23, roles25, Nat.choose]

theorem rank_mass : mass = 74988452500 ∧ m*width-mass = 1846900 := by
  norm_num [mass, counts, blocks23, blocks25, n, m, width, roles23, roles25, Nat.choose]

theorem count_1 : count 1 = 1841940993 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_2 : count 2 = 59604960 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_3 : count 3 = 70923030 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_4 : count 4 = 24797266 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_5 : count 5 = 16953300 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_6 : count 6 = 15207761 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_7 : count 7 = 11179127 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_8 : count 8 = 9976756 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_9 : count 9 = 7166639 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_10 : count 10 = 6692747 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_11 : count 11 = 4706950 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_12 : count 12 = 4534703 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_13 : count 13 = 2759310 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_14 : count 14 = 2513739 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_15 : count 15 = 1504499 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_16 : count 16 = 1645351 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_17 : count 17 = 8768773 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_18 : count 18 = 1107910 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_19 : count 19 = 104489 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_20 : count 20 = 1078677 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_21 : count 21 = 16524971 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_22 : count 22 = 299299 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_23 : count 23 = 68880975 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_25 : count 25 = 61581212 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_481 : count 481 = 8146600 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_525 : count 525 = 61581212 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

theorem count_529 : count 529 = 60690100 := by
  norm_num [count, counts, blocks23, blocks25, n, roles23, roles25, Nat.choose]

def childSizes : List ℕ := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 481, 525, 529]
theorem complete_child_support : ∀ p ∈ counts, p.2 ≠ 0 → p.1 ∈ childSizes := by
  norm_num [counts, blocks23, blocks25, n, roles23, roles25, Nat.choose, childSizes]

theorem strict_child_contraction : ∀ t ∈ childSizes, 0 < t ∧ t < m := by
  norm_num [childSizes, m]

def a : ℚ := 52792403826155 / 1000000000000000000
def b : ℚ := 717 / 10000000
def kappa : ℚ := 52789616935221 / 1000000000000000000
def eta : ℚ := 1 / 1000000000000
def beta : ℚ := 1 / 20
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
def complexWidth : ℕ := 537696432
def complexRank : ℕ := 421548223824
def scalar : ℕ := 4793351472
def guardE : ℕ := 64*(complexWidth+784+scalar+1)^3
def guardB : ℕ := complexRank+guardE
def literal : ℕ := 2*scalar*complexWidth^2+8*complexRank+4*complexWidth+4+32*784
def guardC : ℕ := 32*784*guardB^2
def literalGap : ℚ := (guardE : ℚ)-literal
def rowGap : ℚ := 2000-(51/25)*(9*27+20*30)
def margins : List ℚ := [1-epsilon,a,g,a,min (1-epsilon-delta) (r-delta),1-epsilon-delta,epsilon]

theorem slack_a_positive : (a) = ((10558480765231 / 200000000000000000) : ℚ) ∧ (0 : ℚ) < (a) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_a_below_b : (b-a) = ((3781519234769 / 200000000000000000) : ℚ) ∧ (0 : ℚ) < (b-a) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_b_below_one_over32 : (1/32-b) = ((311783 / 10000000) : ℚ) ∧ (0 : ℚ) < (1/32-b) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_beta_positive : (beta) = ((1 / 20) : ℚ) ∧ (0 : ℚ) < (beta) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_beta_below_one : (1-beta) = ((19 / 20) : ℚ) ∧ (0 : ℚ) < (1-beta) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_phase_leaf_above_bit : ((1-beta)*b-a) = ((3064519234769 / 200000000000000000) : ℚ) ∧ (0 : ℚ) < ((1-beta)*b-a) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_q_positive : (qParam) = ((5279240382604941519234769 / 100000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (qParam) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_q_below_internal : (1-internal-qParam) = ((10558480765231 / 100000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (1-internal-qParam) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_q_below_leaf : (1-leaf-qParam) = ((1532259617395058480765231 / 100000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (1-leaf-qParam) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_c_positive : (c) = ((5279240407604941519234769 / 100000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (c) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_c_below_one : (1-c) = ((99994720759592395058480765231 / 100000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (1-c) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_q_below_reservations : (c-qParam) = ((1 / 4000000000000) : ℚ) ∧ (0 : ℚ) < (c-qParam) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_lambda_above_tau : (lam-tau) = ((10558480765231 / 200000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (lam-tau) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_lambda_above_sigma : (lam-sigma) = ((3781519234779558480765231 / 200000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (lam-sigma) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_lambda_above_internal : (lam-internal) = ((10558480765231 / 200000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (lam-internal) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_lambda_prime_above_lambda : (lp-lam) = ((10558480765231 / 200000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (lp-lam) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_compact_leaf : (lp-leaf) = ((1532259617395058480765231 / 100000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (lp-leaf) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_compact_reservations : (lp-(1-c)) = ((1 / 4000000000000) : ℚ) ∧ (0 : ℚ) < (lp-(1-c)) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_lambda_prime_below_one : (qParam) = ((5279240382604941519234769 / 100000000000000000000000000000) : ℚ) ∧ (0 : ℚ) < (qParam) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_epsilon_positive : (epsilon) = ((99999999999900000000000000000 / 100005279240382604941519234769) : ℚ) ∧ (0 : ℚ) < (epsilon) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_epsilon_below_one : (1-epsilon) = ((5279240482604941519234769 / 100005279240382604941519234769) : ℚ) ∧ (0 : ℚ) < (1-epsilon) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_guard_width : (1-epsilon) = ((5279240482604941519234769 / 100005279240382604941519234769) : ℚ) ∧ (0 : ℚ) < (1-epsilon) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_K_geometry : (1-epsilon*(1+c)) = ((75005279240407604941519234769 / 100005279240382604941519234769000000000000) : ℚ) ∧ (0 : ℚ) < (1-epsilon*(1+c)) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_K_dominates_log : (epsilon*c) = ((5279240407599662278827164058480765231 / 100005279240382604941519234769000000000000) : ℚ) ∧ (0 : ℚ) < (epsilon*c) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_record_suffix : (1-epsilon) = ((5279240482604941519234769 / 100005279240382604941519234769) : ℚ) ∧ (0 : ℚ) < (1-epsilon) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_phase_local : (1-epsilon-delta) = ((42233923760834252913495547058480765231 / 800042233923060839532153878152000000000000) : ℚ) ∧ (0 : ℚ) < (1-epsilon-delta) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_phase_boundary : (r-delta) = ((8446784672162627190393025458480765231 / 160008446784612167906430775630400000000000) : ℚ) ∧ (0 : ℚ) < (r-delta) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_gamma_sublinear : (1-epsilon-r) = ((1 / 2000000000000) : ℚ) ∧ (0 : ℚ) < (1-epsilon-r) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_cell_above_band : (epsilon-(1-r)/2) = ((199999999999699994720759617395058480765231 / 400021116961530419766076939076000000000000) : ℚ) ∧ (0 : ℚ) < (epsilon-(1-r)/2) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_prime_interval_packing : (1-epsilon) = ((5279240482604941519234769 / 100005279240382604941519234769) : ℚ) ∧ (0 : ℚ) < (1-epsilon) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_alpha_positive : (r) = ((10558480865204603798086933058480765231 / 200010558480765209883038469538000000000000) : ℚ) ∧ (0 : ℚ) < (r) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_alpha_below_one : (1-r) = ((199999999999900005279240382604941519234769 / 200010558480765209883038469538000000000000) : ℚ) ∧ (0 : ℚ) < (1-r) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_alpha_below_one_fourth : (1/4-r) = ((49992081139326097866961530451441519234769 / 200010558480765209883038469538000000000000) : ℚ) ∧ (0 : ℚ) < (1/4-r) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_delta_positive : (delta) = ((1 / 8000000000000) : ℚ) ∧ (0 : ℚ) < (delta) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_delta_below_one_eighth : (1/8-delta) = ((999999999999 / 8000000000000) : ℚ) ∧ (0 : ℚ) < (1/8-delta) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_short_record_fallback : (epsilon-a) = ((19998944096162718865234979846828072503338483361 / 20001055848076520988303846953800000000000000000) : ℚ) ∧ (0 : ℚ) < (epsilon-a) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_small_field_exposure : (1-epsilon-g) = ((1 / 1000000000000) : ℚ) ∧ (0 : ℚ) < (1-epsilon-g) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_artificial_boundary : (8-epsilon+r-delta-g) = ((5600337871385586732094952173030824557704307 / 800042233923060839532153878152000000000000) : ℚ) ∧ (0 : ℚ) < (8-epsilon+r-delta-g) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_literal_scalar_guard : (literalGap) = (9693793493753822316795466474748 : ℚ) ∧ (0 : ℚ) < (literalGap) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_row_product_gap : (rowGap) = ((7007 / 25) : ℚ) ∧ (0 : ℚ) < (rowGap) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_g1_above_kappa : ((1-epsilon)-kappa) = ((100005334854822405963918081036101051 / 100005279240382604941519234769000000000000000000) : ℚ) ∧ (0 : ℚ) < ((1-epsilon)-kappa) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_g2_above_kappa : ((a)-kappa) = ((1393445467 / 500000000000000000) : ℚ) ∧ (0 : ℚ) < ((a)-kappa) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_g3_above_kappa : ((g)-kappa) = ((55614439801022398846267101051 / 100005279240382604941519234769000000000000000000) : ℚ) ∧ (0 : ℚ) < ((g)-kappa) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_g4_above_kappa : ((a)-kappa) = ((1393445467 / 500000000000000000) : ℚ) ∧ (0 : ℚ) < ((a)-kappa) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_g5_above_kappa : ((min (1-epsilon-delta) (r-delta))-kappa) = ((37502035329583277875468559305476051 / 100005279240382604941519234769000000000000000000) : ℚ) ∧ (0 : ℚ) < ((min (1-epsilon-delta) (r-delta))-kappa) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_g6_above_kappa : ((1-epsilon-delta)-kappa) = ((87504674949774580346228176689976051 / 100005279240382604941519234769000000000000000000) : ℚ) ∧ (0 : ℚ) < ((1-epsilon-delta)-kappa) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem slack_g7_above_kappa : ((epsilon)-kappa) = ((99994720759517400393335587636963918081036101051 / 100005279240382604941519234769000000000000000000) : ℚ) ∧ (0 : ℚ) < ((epsilon)-kappa) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem margins_strict : ∀ x ∈ margins, kappa < x := by
  norm_num [margins, a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem balanced_identities : 1-epsilon-g = eta ∧ 1-epsilon-r = eta/2 ∧ 1-epsilon*(1+c) = eta-epsilon*eta/4 := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem controlling_margin : g < kappa+1/1000000000000000000 ∧ kappa < g := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem gain_over_original : kappa > (384569/10000000000 : ℚ) ∧ kappa > (409953/10000000000 : ℚ) ∧ (1/2^15 : ℚ) < kappa ∧ kappa < (1/2^14 : ℚ) := by
  norm_num [a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

theorem finite_bridge : 575^9 > (2:ℕ)*529^9 ∧ 575^8 ≤ (2:ℕ)*529^8 ∧ 784^20 > (2:ℕ)*756^20 ∧ 784^19 ≤ (2:ℕ)*756^19 ∧ (2:ℕ)^26 ≤ width ∧ width < (2:ℕ)^27 ∧ (2:ℕ)^29 ≤ complexWidth ∧ complexWidth < (2:ℕ)^30 ∧ guardE > literal ∧ 2*guardB*(784-756) ≥ complexRank+guardE ∧ guardC > 2*guardB+18 := by
  norm_num [width, n, roles23, roles25, Nat.choose, a, b, kappa, eta, beta, tau, sigma, qParam, lp, c, epsilon, lam, g, r, delta, internal, leaf, literalGap, rowGap, guardE, guardB, guardC, literal, complexWidth, complexRank, scalar]

-- Rounded exponential bounds are supplied here. Their weighted sums and
-- their domination of the degree-eight Taylor arithmetic are checked below.
-- Analytic connections to real log/exp remain external to this supplement.
def taylor8 (x : ℚ) : ℚ := 1+x+x^2/2+x^3/6+x^4/24+x^5/120+x^6/720+x^7/5040+x^8/40320
def expUpper (x : ℚ) : ℚ := taylor8 x+x^9/362880/(1-x/10)

def accepted_1 : ℚ := (10003355187430811436301506884590968371643 / 10000000000000000000000000000000000000000)
theorem accepted_interval_1 : (0 : ℚ) ≤ a*(3177185020398675220004135749131 / 500000000000000000000000000000) ∧ a*(3177185020398675220004135749131 / 500000000000000000000000000000) ≤ a*(6354370040797350440008271498263 / 1000000000000000000000000000000) ∧ a*(6354370040797350440008271498263 / 1000000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_1 : expUpper (a*(6354370040797350440008271498263 / 1000000000000000000000000000000)) ≤ accepted_1 := by
  norm_num [expUpper, taylor8, a, accepted_1]

def accepted_2 : ℚ := (10002989142293451273171593526174883283451 / 10000000000000000000000000000000000000000)
theorem accepted_interval_2 : (0 : ℚ) ≤ a*(1415305715059351282647759844201 / 250000000000000000000000000000) ∧ a*(1415305715059351282647759844201 / 250000000000000000000000000000) ≤ a*(1132244572047481026118207875361 / 200000000000000000000000000000) ∧ a*(1132244572047481026118207875361 / 200000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_2 : expUpper (a*(1132244572047481026118207875361 / 200000000000000000000000000000)) ≤ accepted_2 := by
  norm_num [expUpper, taylor8, a, accepted_2]

def accepted_3 : ℚ := (10002775025823826712873382847907587702911 / 10000000000000000000000000000000000000000)
theorem accepted_interval_3 : (0 : ℚ) ≤ a*(262787887606462037430651313067 / 50000000000000000000000000000) ∧ a*(262787887606462037430651313067 / 50000000000000000000000000000) ≤ a*(5255757752129240748613026261341 / 1000000000000000000000000000000) ∧ a*(5255757752129240748613026261341 / 1000000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_3 : expUpper (a*(5255757752129240748613026261341 / 1000000000000000000000000000000)) ≤ accepted_3 := by
  norm_num [expUpper, taylor8, a, accepted_3]

def accepted_4 : ℚ := (10002623110550501292874892056529826574567 / 10000000000000000000000000000000000000000)
theorem accepted_interval_4 : (0 : ℚ) ≤ a*(2484037839838729910586903627673 / 500000000000000000000000000000) ∧ a*(2484037839838729910586903627673 / 500000000000000000000000000000) ≤ a*(4968075679677459821173807255347 / 1000000000000000000000000000000) ∧ a*(4968075679677459821173807255347 / 1000000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_4 : expUpper (a*(4968075679677459821173807255347 / 1000000000000000000000000000000)) ≤ accepted_4 := by
  norm_num [expUpper, taylor8, a, accepted_4]

def accepted_5 : ℚ := (2500626319374711445506337453244448044473 / 2500000000000000000000000000000000000000)
theorem accepted_interval_5 : (0 : ℚ) ≤ a*(1186233032090812516351878041259 / 250000000000000000000000000000) ∧ a*(1186233032090812516351878041259 / 250000000000000000000000000000) ≤ a*(4744932128363250065407512165037 / 1000000000000000000000000000000) ∧ a*(4744932128363250065407512165037 / 1000000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_5 : expUpper (a*(4744932128363250065407512165037 / 1000000000000000000000000000000)) ≤ accepted_5 := by
  norm_num [expUpper, taylor8, a, accepted_5]

def accepted_6 : ℚ := (10002409001915877196548506453272943391457 / 10000000000000000000000000000000000000000)
theorem accepted_interval_6 : (0 : ℚ) ≤ a*(4562610571569295439195794139881 / 1000000000000000000000000000000) ∧ a*(4562610571569295439195794139881 / 1000000000000000000000000000000) ≤ a*(2281305285784647719597897069941 / 500000000000000000000000000000) ∧ a*(2281305285784647719597897069941 / 500000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_6 : expUpper (a*(2281305285784647719597897069941 / 500000000000000000000000000000)) ≤ accepted_6 := by
  norm_num [expUpper, taylor8, a, accepted_6]

def accepted_7 : ℚ := (2500581900698318395642073696120815915489 / 2500000000000000000000000000000000000000)
theorem accepted_interval_7 : (0 : ℚ) ≤ a*(4408459891742037134902918754819 / 1000000000000000000000000000000) ∧ a*(4408459891742037134902918754819 / 1000000000000000000000000000000) ≤ a*(220422994587101856745145937741 / 50000000000000000000000000000) ∧ a*(220422994587101856745145937741 / 50000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_7 : expUpper (a*(220422994587101856745145937741 / 50000000000000000000000000000)) ≤ accepted_7 := by
  norm_num [expUpper, taylor8, a, accepted_7]

def accepted_8 : ℚ := (10002257092201471363988158192070974714601 / 10000000000000000000000000000000000000000)
theorem accepted_interval_8 : (0 : ℚ) ≤ a*(66795757798711164246196486467 / 15625000000000000000000000000) ∧ a*(66795757798711164246196486467 / 15625000000000000000000000000) ≤ a*(4274928499117514511756575133889 / 1000000000000000000000000000000) ∧ a*(4274928499117514511756575133889 / 1000000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_8 : expUpper (a*(4274928499117514511756575133889 / 1000000000000000000000000000000)) ≤ accepted_8 := by
  norm_num [expUpper, taylor8, a, accepted_8]

def accepted_9 : ℚ := (10002194897864301657979067676219328248557 / 10000000000000000000000000000000000000000)
theorem accepted_interval_9 : (0 : ℚ) ≤ a*(4157145463461131057217781024417 / 1000000000000000000000000000000) ∧ a*(4157145463461131057217781024417 / 1000000000000000000000000000000) ≤ a*(2078572731730565528608890512209 / 500000000000000000000000000000) ∧ a*(2078572731730565528608890512209 / 500000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_9 : expUpper (a*(2078572731730565528608890512209 / 500000000000000000000000000000)) ≤ accepted_9 := by
  norm_num [expUpper, taylor8, a, accepted_9]

def accepted_10 : ℚ := (5001069631730795364866219488772806507267 / 5000000000000000000000000000000000000000)
theorem accepted_interval_10 : (0 : ℚ) ≤ a*(2025892473901652377995140021789 / 500000000000000000000000000000) ∧ a*(2025892473901652377995140021789 / 500000000000000000000000000000) ≤ a*(4051784947803304755990280043579 / 1000000000000000000000000000000) ∧ a*(4051784947803304755990280043579 / 1000000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_10 : expUpper (a*(4051784947803304755990280043579 / 1000000000000000000000000000000)) ≤ accepted_10 := by
  norm_num [expUpper, taylor8, a, accepted_10]

def accepted_11 : ℚ := (10002088936289163062957430790317836045217 / 10000000000000000000000000000000000000000)
theorem accepted_interval_11 : (0 : ℚ) ≤ a*(3956474767998979895946327920297 / 1000000000000000000000000000000) ∧ a*(3956474767998979895946327920297 / 1000000000000000000000000000000) ≤ a*(1978237383999489947973163960149 / 500000000000000000000000000000) ∧ a*(1978237383999489947973163960149 / 500000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_11 : expUpper (a*(1978237383999489947973163960149 / 500000000000000000000000000000)) ≤ accepted_11 := by
  norm_num [expUpper, taylor8, a, accepted_11]

def accepted_12 : ℚ := (500102149570078051572238975318143787567 / 500000000000000000000000000000000000000)
theorem accepted_interval_12 : (0 : ℚ) ≤ a*(3869463391009350129778562018423 / 1000000000000000000000000000000) ∧ a*(3869463391009350129778562018423 / 1000000000000000000000000000000) ≤ a*(483682923876168766222320252303 / 125000000000000000000000000000) ∧ a*(483682923876168766222320252303 / 125000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_12 : expUpper (a*(483682923876168766222320252303 / 125000000000000000000000000000)) ≤ accepted_12 := by
  norm_num [expUpper, taylor8, a, accepted_12]

def accepted_13 : ℚ := (5001000363194215412824161557833931245023 / 5000000000000000000000000000000000000000)
theorem accepted_interval_13 : (0 : ℚ) ≤ a*(3789420683335813703954784056697 / 1000000000000000000000000000000) ∧ a*(3789420683335813703954784056697 / 1000000000000000000000000000000) ≤ a*(1894710341667906851977392028349 / 500000000000000000000000000000) ∧ a*(1894710341667906851977392028349 / 500000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_13 : expUpper (a*(1894710341667906851977392028349 / 500000000000000000000000000000)) ≤ accepted_13 := by
  norm_num [expUpper, taylor8, a, accepted_13]

def accepted_14 : ℚ := (10001961595257533350854888857953597009453 / 10000000000000000000000000000000000000000)
theorem accepted_interval_14 : (0 : ℚ) ≤ a*(3715312711182091825485686633361 / 1000000000000000000000000000000) ∧ a*(3715312711182091825485686633361 / 1000000000000000000000000000000) ≤ a*(1857656355591045912742843316681 / 500000000000000000000000000000) ∧ a*(1857656355591045912742843316681 / 500000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_14 : expUpper (a*(1857656355591045912742843316681 / 500000000000000000000000000000)) ≤ accepted_14 := by
  norm_num [expUpper, taylor8, a, accepted_14]

def accepted_15 : ℚ := (250048129129595846749566354536254898103 / 250000000000000000000000000000000000000)
theorem accepted_interval_15 : (0 : ℚ) ≤ a*(3646319839695140374012266928113 / 1000000000000000000000000000000) ∧ a*(3646319839695140374012266928113 / 1000000000000000000000000000000) ≤ a*(1823159919847570187006133464057 / 500000000000000000000000000000) ∧ a*(1823159919847570187006133464057 / 500000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_15 : expUpper (a*(1823159919847570187006133464057 / 500000000000000000000000000000)) ≤ accepted_15 := by
  norm_num [expUpper, taylor8, a, accepted_15]

def accepted_16 : ℚ := (500094554362293568651157626675808595793 / 500000000000000000000000000000000000000)
theorem accepted_interval_16 : (0 : ℚ) ≤ a*(3581781318557569202339343012429 / 1000000000000000000000000000000) ∧ a*(3581781318557569202339343012429 / 1000000000000000000000000000000) ≤ a*(358178131855756920233934301243 / 100000000000000000000000000000) ∧ a*(358178131855756920233934301243 / 100000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_16 : expUpper (a*(358178131855756920233934301243 / 100000000000000000000000000000)) ≤ accepted_16 := by
  norm_num [expUpper, taylor8, a, accepted_16]

def accepted_17 : ℚ := (2000371815209893715990125475253531588243 / 2000000000000000000000000000000000000000)
theorem accepted_interval_17 : (0 : ℚ) ≤ a*(3521156696741134359758736880389 / 1000000000000000000000000000000) ∧ a*(3521156696741134359758736880389 / 1000000000000000000000000000000) ≤ a*(352115669674113435975873688039 / 100000000000000000000000000000) ∧ a*(352115669674113435975873688039 / 100000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_17 : expUpper (a*(352115669674113435975873688039 / 100000000000000000000000000000)) ≤ accepted_17 := by
  norm_num [expUpper, taylor8, a, accepted_17]

def accepted_18 : ℚ := (10001828895184531552662296367755603258471 / 10000000000000000000000000000000000000000)
theorem accepted_interval_18 : (0 : ℚ) ≤ a*(3463998282901185747800548902959 / 1000000000000000000000000000000) ∧ a*(3463998282901185747800548902959 / 1000000000000000000000000000000) ≤ a*(43299978536264821847506861287 / 12500000000000000000000000000) ∧ a*(43299978536264821847506861287 / 12500000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_18 : expUpper (a*(43299978536264821847506861287 / 12500000000000000000000000000)) ≤ accepted_18 := by
  norm_num [expUpper, taylor8, a, accepted_18]

def accepted_19 : ℚ := (10001800346619198540731263851600207293969 / 10000000000000000000000000000000000000000)
theorem accepted_interval_19 : (0 : ℚ) ≤ a*(1704965530815454989999622033187 / 500000000000000000000000000000) ∧ a*(1704965530815454989999622033187 / 500000000000000000000000000000) ≤ a*(27279448493047279839993952531 / 8000000000000000000000000000) ∧ a*(27279448493047279839993952531 / 8000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_19 : expUpper (a*(27279448493047279839993952531 / 8000000000000000000000000000)) ≤ accepted_19 := by
  norm_num [expUpper, taylor8, a, accepted_19]

def accepted_20 : ℚ := (5000886631408803918937931522522045324127 / 5000000000000000000000000000000000000000)
theorem accepted_interval_20 : (0 : ℚ) ≤ a*(83965944181083986164326198053 / 25000000000000000000000000000) ∧ a*(83965944181083986164326198053 / 25000000000000000000000000000) ≤ a*(3358637767243359446573047922121 / 1000000000000000000000000000000) ∧ a*(3358637767243359446573047922121 / 1000000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_20 : expUpper (a*(3358637767243359446573047922121 / 1000000000000000000000000000000)) ≤ accepted_20 := by
  norm_num [expUpper, taylor8, a, accepted_20]

def accepted_21 : ℚ := (10001747500782808572431534092953530248277 / 10000000000000000000000000000000000000000)
theorem accepted_interval_21 : (0 : ℚ) ≤ a*(413730950384240930438459189737 / 125000000000000000000000000000) ∧ a*(413730950384240930438459189737 / 125000000000000000000000000000) ≤ a*(3309847603073927443507673517897 / 1000000000000000000000000000000) ∧ a*(3309847603073927443507673517897 / 1000000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_21 : expUpper (a*(3309847603073927443507673517897 / 1000000000000000000000000000000)) ≤ accepted_21 := by
  norm_num [expUpper, taylor8, a, accepted_21]

def accepted_22 : ℚ := (10001722937486763959646233420754369152731 / 10000000000000000000000000000000000000000)
theorem accepted_interval_22 : (0 : ℚ) ≤ a*(3263327587439034586529095798839 / 1000000000000000000000000000000) ∧ a*(3263327587439034586529095798839 / 1000000000000000000000000000000) ≤ a*(81583189685975864663227394971 / 25000000000000000000000000000) ∧ a*(81583189685975864663227394971 / 25000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_22 : expUpper (a*(81583189685975864663227394971 / 25000000000000000000000000000)) ≤ accepted_22 := by
  norm_num [expUpper, taylor8, a, accepted_22]

def accepted_23 : ℚ := (2000339893263411175150443996908118155021 / 2000000000000000000000000000000000000000)
theorem accepted_interval_23 : (0 : ℚ) ≤ a*(804718956217050187300379666613 / 250000000000000000000000000000) ∧ a*(804718956217050187300379666613 / 250000000000000000000000000000) ≤ a*(3218875824868200749201518666453 / 1000000000000000000000000000000) ∧ a*(3218875824868200749201518666453 / 1000000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_23 : expUpper (a*(3218875824868200749201518666453 / 1000000000000000000000000000000)) ≤ accepted_23 := by
  norm_num [expUpper, taylor8, a, accepted_23]

def accepted_25 : ℚ := (10001655439777341409928794291140256708281 / 10000000000000000000000000000000000000000)
theorem accepted_interval_25 : (0 : ℚ) ≤ a*(313549421592914969080675283181 / 100000000000000000000000000000) ∧ a*(313549421592914969080675283181 / 100000000000000000000000000000) ≤ a*(3135494215929149690806752831811 / 1000000000000000000000000000000) ∧ a*(3135494215929149690806752831811 / 1000000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_25 : expUpper (a*(3135494215929149690806752831811 / 1000000000000000000000000000000)) ≤ accepted_25 := by
  norm_num [expUpper, taylor8, a, accepted_25]

def accepted_481 : ℚ := (10000094236347566049853859114967129582319 / 10000000000000000000000000000000000000000)
theorem accepted_interval_481 : (0 : ℚ) ≤ a*(35700554138317851917337677133 / 200000000000000000000000000000) ∧ a*(35700554138317851917337677133 / 200000000000000000000000000000) ≤ a*(89251385345794629793344192833 / 500000000000000000000000000000) ∧ a*(89251385345794629793344192833 / 500000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_481 : expUpper (a*(89251385345794629793344192833 / 500000000000000000000000000000)) ≤ accepted_481 := by
  norm_num [expUpper, taylor8, a, accepted_481]

def accepted_525 : ℚ := (10000048026303844125101140750756918734051 / 10000000000000000000000000000000000000000)
theorem accepted_interval_525 : (0 : ℚ) ≤ a*(22742944551431673576538712861 / 250000000000000000000000000000) ∧ a*(22742944551431673576538712861 / 250000000000000000000000000000) ≤ a*(18194355641145338861230970289 / 200000000000000000000000000000) ∧ a*(18194355641145338861230970289 / 200000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_525 : expUpper (a*(18194355641145338861230970289 / 200000000000000000000000000000)) ≤ accepted_525 := by
  norm_num [expUpper, taylor8, a, accepted_525]

def accepted_529 : ℚ := (1000004401925259229481104531257806676897 / 1000000000000000000000000000000000000000)
theorem accepted_interval_529 : (0 : ℚ) ≤ a*(41690804469525529197382917321 / 500000000000000000000000000000) ∧ a*(41690804469525529197382917321 / 500000000000000000000000000000) ≤ a*(83381608939051058394765834643 / 1000000000000000000000000000000) ∧ a*(83381608939051058394765834643 / 1000000000000000000000000000000) < 1 := by
  norm_num [a]

theorem accepted_taylor_529 : expUpper (a*(83381608939051058394765834643 / 1000000000000000000000000000000)) ≤ accepted_529 := by
  norm_num [expUpper, taylor8, a, accepted_529]

def acceptedMoment : ℚ :=
  ((1*1841940993 : ℚ)/(575*130417912))*accepted_1 +
  ((2*59604960 : ℚ)/(575*130417912))*accepted_2 +
  ((3*70923030 : ℚ)/(575*130417912))*accepted_3 +
  ((4*24797266 : ℚ)/(575*130417912))*accepted_4 +
  ((5*16953300 : ℚ)/(575*130417912))*accepted_5 +
  ((6*15207761 : ℚ)/(575*130417912))*accepted_6 +
  ((7*11179127 : ℚ)/(575*130417912))*accepted_7 +
  ((8*9976756 : ℚ)/(575*130417912))*accepted_8 +
  ((9*7166639 : ℚ)/(575*130417912))*accepted_9 +
  ((10*6692747 : ℚ)/(575*130417912))*accepted_10 +
  ((11*4706950 : ℚ)/(575*130417912))*accepted_11 +
  ((12*4534703 : ℚ)/(575*130417912))*accepted_12 +
  ((13*2759310 : ℚ)/(575*130417912))*accepted_13 +
  ((14*2513739 : ℚ)/(575*130417912))*accepted_14 +
  ((15*1504499 : ℚ)/(575*130417912))*accepted_15 +
  ((16*1645351 : ℚ)/(575*130417912))*accepted_16 +
  ((17*8768773 : ℚ)/(575*130417912))*accepted_17 +
  ((18*1107910 : ℚ)/(575*130417912))*accepted_18 +
  ((19*104489 : ℚ)/(575*130417912))*accepted_19 +
  ((20*1078677 : ℚ)/(575*130417912))*accepted_20 +
  ((21*16524971 : ℚ)/(575*130417912))*accepted_21 +
  ((22*299299 : ℚ)/(575*130417912))*accepted_22 +
  ((23*68880975 : ℚ)/(575*130417912))*accepted_23 +
  ((25*61581212 : ℚ)/(575*130417912))*accepted_25 +
  ((481*8146600 : ℚ)/(575*130417912))*accepted_481 +
  ((525*61581212 : ℚ)/(575*130417912))*accepted_525 +
  ((529*60690100 : ℚ)/(575*130417912))*accepted_529
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
  ((25*(count 25 : ℚ))/(m*width))*accepted_25 +
  ((481*(count 481 : ℚ))/(m*width))*accepted_481 +
  ((525*(count 525 : ℚ))/(m*width))*accepted_525 +
  ((529*(count 529 : ℚ))/(m*width))*accepted_529
theorem accepted_profile_link : acceptedFromCounts = acceptedMoment := by
  norm_num [acceptedFromCounts, acceptedMoment, m, width, n, roles23, roles25, Nat.choose, count_1, count_10, count_11, count_12, count_13, count_14, count_15, count_16, count_17, count_18, count_19, count_2, count_20, count_21, count_22, count_23, count_25, count_3, count_4, count_481, count_5, count_525, count_529, count_6, count_7, count_8, count_9]

theorem accepted_moment : acceptedMoment < 1 ∧ acceptedMoment = (45921799999999999986718939153021994591711554531 / 45921800000000000000000000000000000000000000000) := by
  norm_num [acceptedMoment, accepted_1, accepted_10, accepted_11, accepted_12, accepted_13, accepted_14, accepted_15, accepted_16, accepted_17, accepted_18, accepted_19, accepted_2, accepted_20, accepted_21, accepted_22, accepted_23, accepted_25, accepted_3, accepted_4, accepted_481, accepted_5, accepted_525, accepted_529, accepted_6, accepted_7, accepted_8, accepted_9]

theorem accepted_paid_moment : acceptedFromCounts < 1 := by
  rw [accepted_profile_link]
  exact accepted_moment.1

def rejected_1 : ℚ := (10003355187430811499866527395056080467997 / 10000000000000000000000000000000000000000)
theorem rejected_interval_1 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(3177185020398675220004135749131 / 500000000000000000000000000000) ∧ (a+1/1000000000000000000)*(3177185020398675220004135749131 / 500000000000000000000000000000) ≤ (a+1/1000000000000000000)*(6354370040797350440008271498263 / 1000000000000000000000000000000) ∧ (a+1/1000000000000000000)*(6354370040797350440008271498263 / 1000000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_1 : rejected_1 ≤ taylor8 ((a+1/1000000000000000000)*(3177185020398675220004135749131 / 500000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_1]

def rejected_2 : ℚ := (10002989142293451329800744329233123034741 / 10000000000000000000000000000000000000000)
theorem rejected_interval_2 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(1415305715059351282647759844201 / 250000000000000000000000000000) ∧ (a+1/1000000000000000000)*(1415305715059351282647759844201 / 250000000000000000000000000000) ≤ (a+1/1000000000000000000)*(1132244572047481026118207875361 / 200000000000000000000000000000) ∧ (a+1/1000000000000000000)*(1132244572047481026118207875361 / 200000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_2 : rejected_2 ≤ taylor8 ((a+1/1000000000000000000)*(1415305715059351282647759844201 / 250000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_2]

def rejected_3 : ℚ := (10002775025823826765445545232685930877759 / 10000000000000000000000000000000000000000)
theorem rejected_interval_3 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(262787887606462037430651313067 / 50000000000000000000000000000) ∧ (a+1/1000000000000000000)*(262787887606462037430651313067 / 50000000000000000000000000000) ≤ (a+1/1000000000000000000)*(5255757752129240748613026261341 / 1000000000000000000000000000000) ∧ (a+1/1000000000000000000)*(5255757752129240748613026261341 / 1000000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_3 : rejected_3 ≤ taylor8 ((a+1/1000000000000000000)*(262787887606462037430651313067 / 50000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_3]

def rejected_4 : ℚ := (2500655777637625335642170166258868801979 / 2500000000000000000000000000000000000000)
theorem rejected_interval_4 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(2484037839838729910586903627673 / 500000000000000000000000000000) ∧ (a+1/1000000000000000000)*(2484037839838729910586903627673 / 500000000000000000000000000000) ≤ (a+1/1000000000000000000)*(4968075679677459821173807255347 / 1000000000000000000000000000000) ∧ (a+1/1000000000000000000)*(4968075679677459821173807255347 / 1000000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_4 : rejected_4 ≤ taylor8 ((a+1/1000000000000000000)*(2484037839838729910586903627673 / 500000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_4]

def rejected_5 : ℚ := (10002505277498845829486558468305031292667 / 10000000000000000000000000000000000000000)
theorem rejected_interval_5 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(1186233032090812516351878041259 / 250000000000000000000000000000) ∧ (a+1/1000000000000000000)*(1186233032090812516351878041259 / 250000000000000000000000000000) ≤ (a+1/1000000000000000000)*(4744932128363250065407512165037 / 1000000000000000000000000000000) ∧ (a+1/1000000000000000000)*(4744932128363250065407512165037 / 1000000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_5 : rejected_5 ≤ taylor8 ((a+1/1000000000000000000)*(1186233032090812516351878041259 / 250000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_5]

def rejected_6 : ℚ := (10002409001915877242185603506574209342913 / 10000000000000000000000000000000000000000)
theorem rejected_interval_6 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(4562610571569295439195794139881 / 1000000000000000000000000000000) ∧ (a+1/1000000000000000000)*(4562610571569295439195794139881 / 1000000000000000000000000000000) ≤ (a+1/1000000000000000000)*(2281305285784647719597897069941 / 500000000000000000000000000000) ∧ (a+1/1000000000000000000)*(2281305285784647719597897069941 / 500000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_6 : rejected_6 ≤ taylor8 ((a+1/1000000000000000000)*(4562610571569295439195794139881 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_6]

def rejected_7 : ℚ := (10002327602793273626663154845461687901127 / 10000000000000000000000000000000000000000)
theorem rejected_interval_7 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(4408459891742037134902918754819 / 1000000000000000000000000000000) ∧ (a+1/1000000000000000000)*(4408459891742037134902918754819 / 1000000000000000000000000000000) ≤ (a+1/1000000000000000000)*(220422994587101856745145937741 / 50000000000000000000000000000) ∧ (a+1/1000000000000000000)*(220422994587101856745145937741 / 50000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_7 : rejected_7 ≤ taylor8 ((a+1/1000000000000000000)*(4408459891742037134902918754819 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_7]

def rejected_8 : ℚ := (1000225709220147140674709209102332522021 / 1000000000000000000000000000000000000000)
theorem rejected_interval_8 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(66795757798711164246196486467 / 15625000000000000000000000000) ∧ (a+1/1000000000000000000)*(66795757798711164246196486467 / 15625000000000000000000000000) ≤ (a+1/1000000000000000000)*(4274928499117514511756575133889 / 1000000000000000000000000000000) ∧ (a+1/1000000000000000000)*(4274928499117514511756575133889 / 1000000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_8 : rejected_8 ≤ taylor8 ((a+1/1000000000000000000)*(66795757798711164246196486467 / 15625000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_8]

def rejected_9 : ℚ := (10002194897864301699559646820529980541793 / 10000000000000000000000000000000000000000)
theorem rejected_interval_9 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(4157145463461131057217781024417 / 1000000000000000000000000000000) ∧ (a+1/1000000000000000000)*(4157145463461131057217781024417 / 1000000000000000000000000000000) ≤ (a+1/1000000000000000000)*(2078572731730565528608890512209 / 500000000000000000000000000000) ∧ (a+1/1000000000000000000)*(2078572731730565528608890512209 / 500000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_9 : rejected_9 ≤ taylor8 ((a+1/1000000000000000000)*(4157145463461131057217781024417 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_9]

def rejected_10 : ℚ := (10002139263461590770258956291071719040393 / 10000000000000000000000000000000000000000)
theorem rejected_interval_10 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(2025892473901652377995140021789 / 500000000000000000000000000000) ∧ (a+1/1000000000000000000)*(2025892473901652377995140021789 / 500000000000000000000000000000) ≤ (a+1/1000000000000000000)*(4051784947803304755990280043579 / 1000000000000000000000000000000) ∧ (a+1/1000000000000000000)*(4051784947803304755990280043579 / 1000000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_10 : rejected_10 ≤ taylor8 ((a+1/1000000000000000000)*(2025892473901652377995140021789 / 500000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_10]

def rejected_11 : ℚ := (2000417787257832620506088658805533126881 / 2000000000000000000000000000000000000000)
theorem rejected_interval_11 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(3956474767998979895946327920297 / 1000000000000000000000000000000) ∧ (a+1/1000000000000000000)*(3956474767998979895946327920297 / 1000000000000000000000000000000) ≤ (a+1/1000000000000000000)*(1978237383999489947973163960149 / 500000000000000000000000000000) ∧ (a+1/1000000000000000000)*(1978237383999489947973163960149 / 500000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_11 : rejected_11 ≤ taylor8 ((a+1/1000000000000000000)*(3956474767998979895946327920297 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_11]

def rejected_12 : ℚ := (10002042991401561070147318696892863889617 / 10000000000000000000000000000000000000000)
theorem rejected_interval_12 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(3869463391009350129778562018423 / 1000000000000000000000000000000) ∧ (a+1/1000000000000000000)*(3869463391009350129778562018423 / 1000000000000000000000000000000) ≤ (a+1/1000000000000000000)*(483682923876168766222320252303 / 125000000000000000000000000000) ∧ (a+1/1000000000000000000)*(483682923876168766222320252303 / 125000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_12 : rejected_12 ≤ taylor8 ((a+1/1000000000000000000)*(3869463391009350129778562018423 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_12]

def rejected_13 : ℚ := (312562522699638464485940985718250456479 / 312500000000000000000000000000000000000)
theorem rejected_interval_13 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(3789420683335813703954784056697 / 1000000000000000000000000000000) ∧ (a+1/1000000000000000000)*(3789420683335813703954784056697 / 1000000000000000000000000000000) ≤ (a+1/1000000000000000000)*(1894710341667906851977392028349 / 500000000000000000000000000000) ∧ (a+1/1000000000000000000)*(1894710341667906851977392028349 / 500000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_13 : rejected_13 ≤ taylor8 ((a+1/1000000000000000000)*(3789420683335813703954784056697 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_13]

def rejected_14 : ℚ := (10001961595257533388015303909569022972699 / 10000000000000000000000000000000000000000)
theorem rejected_interval_14 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(3715312711182091825485686633361 / 1000000000000000000000000000000) ∧ (a+1/1000000000000000000)*(3715312711182091825485686633361 / 1000000000000000000000000000000) ≤ (a+1/1000000000000000000)*(1857656355591045912742843316681 / 500000000000000000000000000000) ∧ (a+1/1000000000000000000)*(1857656355591045912742843316681 / 500000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_14 : rejected_14 ≤ taylor8 ((a+1/1000000000000000000)*(3715312711182091825485686633361 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_14]

def rejected_15 : ℚ := (10001925165183833906452872346406102984941 / 10000000000000000000000000000000000000000)
theorem rejected_interval_15 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(3646319839695140374012266928113 / 1000000000000000000000000000000) ∧ (a+1/1000000000000000000)*(3646319839695140374012266928113 / 1000000000000000000000000000000) ≤ (a+1/1000000000000000000)*(1823159919847570187006133464057 / 500000000000000000000000000000) ∧ (a+1/1000000000000000000)*(1823159919847570187006133464057 / 500000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_15 : rejected_15 ≤ taylor8 ((a+1/1000000000000000000)*(3646319839695140374012266928113 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_15]

def rejected_16 : ℚ := (1000189108724587140884773918006088804391 / 1000000000000000000000000000000000000000)
theorem rejected_interval_16 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(3581781318557569202339343012429 / 1000000000000000000000000000000) ∧ (a+1/1000000000000000000)*(3581781318557569202339343012429 / 1000000000000000000000000000000) ≤ (a+1/1000000000000000000)*(358178131855756920233934301243 / 100000000000000000000000000000) ∧ (a+1/1000000000000000000)*(358178131855756920233934301243 / 100000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_16 : rejected_16 ≤ taylor8 ((a+1/1000000000000000000)*(3581781318557569202339343012429 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_16]

def rejected_17 : ℚ := (10001859076049468615168740441760338415449 / 10000000000000000000000000000000000000000)
theorem rejected_interval_17 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(3521156696741134359758736880389 / 1000000000000000000000000000000) ∧ (a+1/1000000000000000000)*(3521156696741134359758736880389 / 1000000000000000000000000000000) ≤ (a+1/1000000000000000000)*(352115669674113435975873688039 / 100000000000000000000000000000) ∧ (a+1/1000000000000000000)*(352115669674113435975873688039 / 100000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_17 : rejected_17 ≤ taylor8 ((a+1/1000000000000000000)*(3521156696741134359758736880389 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_17]

def rejected_18 : ℚ := (10001828895184531587308614486546283814127 / 10000000000000000000000000000000000000000)
theorem rejected_interval_18 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(3463998282901185747800548902959 / 1000000000000000000000000000000) ∧ (a+1/1000000000000000000)*(3463998282901185747800548902959 / 1000000000000000000000000000000) ≤ (a+1/1000000000000000000)*(43299978536264821847506861287 / 12500000000000000000000000000) ∧ (a+1/1000000000000000000)*(43299978536264821847506861287 / 12500000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_18 : rejected_18 ≤ taylor8 ((a+1/1000000000000000000)*(3463998282901185747800548902959 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_18]

def rejected_19 : ℚ := (10001800346619198574836713525767813923699 / 10000000000000000000000000000000000000000)
theorem rejected_interval_19 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(1704965530815454989999622033187 / 500000000000000000000000000000) ∧ (a+1/1000000000000000000)*(1704965530815454989999622033187 / 500000000000000000000000000000) ≤ (a+1/1000000000000000000)*(27279448493047279839993952531 / 8000000000000000000000000000) ∧ (a+1/1000000000000000000)*(27279448493047279839993952531 / 8000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_19 : rejected_19 ≤ taylor8 ((a+1/1000000000000000000)*(1704965530815454989999622033187 / 500000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_19]

def rejected_20 : ℚ := (2500443315704401967867049116237037674879 / 2500000000000000000000000000000000000000)
theorem rejected_interval_20 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(83965944181083986164326198053 / 25000000000000000000000000000) ∧ (a+1/1000000000000000000)*(83965944181083986164326198053 / 25000000000000000000000000000) ≤ (a+1/1000000000000000000)*(3358637767243359446573047922121 / 1000000000000000000000000000000) ∧ (a+1/1000000000000000000)*(3358637767243359446573047922121 / 1000000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_20 : rejected_20 ≤ taylor8 ((a+1/1000000000000000000)*(83965944181083986164326198053 / 25000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_20]

def rejected_21 : ℚ := (10001747500782808605535794084970152975453 / 10000000000000000000000000000000000000000)
theorem rejected_interval_21 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(413730950384240930438459189737 / 125000000000000000000000000000) ∧ (a+1/1000000000000000000)*(413730950384240930438459189737 / 125000000000000000000000000000) ≤ (a+1/1000000000000000000)*(3309847603073927443507673517897 / 1000000000000000000000000000000) ∧ (a+1/1000000000000000000)*(3309847603073927443507673517897 / 1000000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_21 : rejected_21 ≤ taylor8 ((a+1/1000000000000000000)*(413730950384240930438459189737 / 125000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_21]

def rejected_22 : ℚ := (2500430734371690998071282951144176062319 / 2500000000000000000000000000000000000000)
theorem rejected_interval_22 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(3263327587439034586529095798839 / 1000000000000000000000000000000) ∧ (a+1/1000000000000000000)*(3263327587439034586529095798839 / 1000000000000000000000000000000) ≤ (a+1/1000000000000000000)*(81583189685975864663227394971 / 25000000000000000000000000000) ∧ (a+1/1000000000000000000)*(81583189685975864663227394971 / 25000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_22 : rejected_22 ≤ taylor8 ((a+1/1000000000000000000)*(3263327587439034586529095798839 / 1000000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_22]

def rejected_23 : ℚ := (5000849733158527953973224302132873373081 / 5000000000000000000000000000000000000000)
theorem rejected_interval_23 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(804718956217050187300379666613 / 250000000000000000000000000000) ∧ (a+1/1000000000000000000)*(804718956217050187300379666613 / 250000000000000000000000000000) ≤ (a+1/1000000000000000000)*(3218875824868200749201518666453 / 1000000000000000000000000000000) ∧ (a+1/1000000000000000000)*(3218875824868200749201518666453 / 1000000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_23 : rejected_23 ≤ taylor8 ((a+1/1000000000000000000)*(804718956217050187300379666613 / 250000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_23]

def rejected_25 : ℚ := (10001655439777341441288927072278426167767 / 10000000000000000000000000000000000000000)
theorem rejected_interval_25 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(313549421592914969080675283181 / 100000000000000000000000000000) ∧ (a+1/1000000000000000000)*(313549421592914969080675283181 / 100000000000000000000000000000) ≤ (a+1/1000000000000000000)*(3135494215929149690806752831811 / 1000000000000000000000000000000) ∧ (a+1/1000000000000000000)*(3135494215929149690806752831811 / 1000000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_25 : rejected_25 ≤ taylor8 ((a+1/1000000000000000000)*(313549421592914969080675283181 / 100000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_25]

def rejected_481 : ℚ := (5000047118173783025819451821666081022959 / 5000000000000000000000000000000000000000)
theorem rejected_interval_481 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(35700554138317851917337677133 / 200000000000000000000000000000) ∧ (a+1/1000000000000000000)*(35700554138317851917337677133 / 200000000000000000000000000000) ≤ (a+1/1000000000000000000)*(89251385345794629793344192833 / 500000000000000000000000000000) ∧ (a+1/1000000000000000000)*(89251385345794629793344192833 / 500000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_481 : rejected_481 ≤ taylor8 ((a+1/1000000000000000000)*(35700554138317851917337677133 / 200000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_481]

def rejected_525 : ℚ := (2000009605260768825202172580370489299563 / 2000000000000000000000000000000000000000)
theorem rejected_interval_525 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(22742944551431673576538712861 / 250000000000000000000000000000) ∧ (a+1/1000000000000000000)*(22742944551431673576538712861 / 250000000000000000000000000000) ≤ (a+1/1000000000000000000)*(18194355641145338861230970289 / 200000000000000000000000000000) ∧ (a+1/1000000000000000000)*(18194355641145338861230970289 / 200000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_525 : rejected_525 ≤ taylor8 ((a+1/1000000000000000000)*(22742944551431673576538712861 / 250000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_525]

def rejected_529 : ℚ := (500002200962629614782243253618234113253 / 500000000000000000000000000000000000000)
theorem rejected_interval_529 : (0 : ℚ) ≤ (a+1/1000000000000000000)*(41690804469525529197382917321 / 500000000000000000000000000000) ∧ (a+1/1000000000000000000)*(41690804469525529197382917321 / 500000000000000000000000000000) ≤ (a+1/1000000000000000000)*(83381608939051058394765834643 / 1000000000000000000000000000000) ∧ (a+1/1000000000000000000)*(83381608939051058394765834643 / 1000000000000000000000000000000) < 1 := by
  norm_num [a]

theorem rejected_taylor_529 : rejected_529 ≤ taylor8 ((a+1/1000000000000000000)*(41690804469525529197382917321 / 500000000000000000000000000000)) := by
  norm_num [expUpper, taylor8, a, rejected_529]

def rejectedMoment : ℚ :=
  ((1*1841940993 : ℚ)/(575*130417912))*rejected_1 +
  ((2*59604960 : ℚ)/(575*130417912))*rejected_2 +
  ((3*70923030 : ℚ)/(575*130417912))*rejected_3 +
  ((4*24797266 : ℚ)/(575*130417912))*rejected_4 +
  ((5*16953300 : ℚ)/(575*130417912))*rejected_5 +
  ((6*15207761 : ℚ)/(575*130417912))*rejected_6 +
  ((7*11179127 : ℚ)/(575*130417912))*rejected_7 +
  ((8*9976756 : ℚ)/(575*130417912))*rejected_8 +
  ((9*7166639 : ℚ)/(575*130417912))*rejected_9 +
  ((10*6692747 : ℚ)/(575*130417912))*rejected_10 +
  ((11*4706950 : ℚ)/(575*130417912))*rejected_11 +
  ((12*4534703 : ℚ)/(575*130417912))*rejected_12 +
  ((13*2759310 : ℚ)/(575*130417912))*rejected_13 +
  ((14*2513739 : ℚ)/(575*130417912))*rejected_14 +
  ((15*1504499 : ℚ)/(575*130417912))*rejected_15 +
  ((16*1645351 : ℚ)/(575*130417912))*rejected_16 +
  ((17*8768773 : ℚ)/(575*130417912))*rejected_17 +
  ((18*1107910 : ℚ)/(575*130417912))*rejected_18 +
  ((19*104489 : ℚ)/(575*130417912))*rejected_19 +
  ((20*1078677 : ℚ)/(575*130417912))*rejected_20 +
  ((21*16524971 : ℚ)/(575*130417912))*rejected_21 +
  ((22*299299 : ℚ)/(575*130417912))*rejected_22 +
  ((23*68880975 : ℚ)/(575*130417912))*rejected_23 +
  ((25*61581212 : ℚ)/(575*130417912))*rejected_25 +
  ((481*8146600 : ℚ)/(575*130417912))*rejected_481 +
  ((525*61581212 : ℚ)/(575*130417912))*rejected_525 +
  ((529*60690100 : ℚ)/(575*130417912))*rejected_529
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
  ((25*(count 25 : ℚ))/(m*width))*rejected_25 +
  ((481*(count 481 : ℚ))/(m*width))*rejected_481 +
  ((525*(count 525 : ℚ))/(m*width))*rejected_525 +
  ((529*(count 529 : ℚ))/(m*width))*rejected_529
theorem rejected_profile_link : rejectedFromCounts = rejectedMoment := by
  norm_num [rejectedFromCounts, rejectedMoment, m, width, n, roles23, roles25, Nat.choose, count_1, count_10, count_11, count_12, count_13, count_14, count_15, count_16, count_17, count_18, count_19, count_2, count_20, count_21, count_22, count_23, count_25, count_3, count_4, count_481, count_5, count_525, count_529, count_6, count_7, count_8, count_9]

theorem rejected_moment : 1 < rejectedMoment ∧ rejectedMoment = (32604478000000000005782543032459327907899102761243 / 32604478000000000000000000000000000000000000000000) := by
  norm_num [rejectedMoment, rejected_1, rejected_10, rejected_11, rejected_12, rejected_13, rejected_14, rejected_15, rejected_16, rejected_17, rejected_18, rejected_19, rejected_2, rejected_20, rejected_21, rejected_22, rejected_23, rejected_25, rejected_3, rejected_4, rejected_481, rejected_5, rejected_525, rejected_529, rejected_6, rejected_7, rejected_8, rejected_9]

theorem rejected_paid_moment : 1 < rejectedFromCounts := by
  rw [rejected_profile_link]
  exact rejected_moment.1

end KappaCheck.AlignedFrameComposition
#print axioms KappaCheck.AlignedFrameComposition.network_counts
#print axioms KappaCheck.AlignedFrameComposition.rank_mass
#print axioms KappaCheck.AlignedFrameComposition.count_1
#print axioms KappaCheck.AlignedFrameComposition.count_2
#print axioms KappaCheck.AlignedFrameComposition.count_3
#print axioms KappaCheck.AlignedFrameComposition.count_4
#print axioms KappaCheck.AlignedFrameComposition.count_5
#print axioms KappaCheck.AlignedFrameComposition.count_6
#print axioms KappaCheck.AlignedFrameComposition.count_7
#print axioms KappaCheck.AlignedFrameComposition.count_8
#print axioms KappaCheck.AlignedFrameComposition.count_9
#print axioms KappaCheck.AlignedFrameComposition.count_10
#print axioms KappaCheck.AlignedFrameComposition.count_11
#print axioms KappaCheck.AlignedFrameComposition.count_12
#print axioms KappaCheck.AlignedFrameComposition.count_13
#print axioms KappaCheck.AlignedFrameComposition.count_14
#print axioms KappaCheck.AlignedFrameComposition.count_15
#print axioms KappaCheck.AlignedFrameComposition.count_16
#print axioms KappaCheck.AlignedFrameComposition.count_17
#print axioms KappaCheck.AlignedFrameComposition.count_18
#print axioms KappaCheck.AlignedFrameComposition.count_19
#print axioms KappaCheck.AlignedFrameComposition.count_20
#print axioms KappaCheck.AlignedFrameComposition.count_21
#print axioms KappaCheck.AlignedFrameComposition.count_22
#print axioms KappaCheck.AlignedFrameComposition.count_23
#print axioms KappaCheck.AlignedFrameComposition.count_25
#print axioms KappaCheck.AlignedFrameComposition.count_481
#print axioms KappaCheck.AlignedFrameComposition.count_525
#print axioms KappaCheck.AlignedFrameComposition.count_529
#print axioms KappaCheck.AlignedFrameComposition.complete_child_support
#print axioms KappaCheck.AlignedFrameComposition.strict_child_contraction
#print axioms KappaCheck.AlignedFrameComposition.slack_a_positive
#print axioms KappaCheck.AlignedFrameComposition.slack_a_below_b
#print axioms KappaCheck.AlignedFrameComposition.slack_b_below_one_over32
#print axioms KappaCheck.AlignedFrameComposition.slack_beta_positive
#print axioms KappaCheck.AlignedFrameComposition.slack_beta_below_one
#print axioms KappaCheck.AlignedFrameComposition.slack_phase_leaf_above_bit
#print axioms KappaCheck.AlignedFrameComposition.slack_q_positive
#print axioms KappaCheck.AlignedFrameComposition.slack_q_below_internal
#print axioms KappaCheck.AlignedFrameComposition.slack_q_below_leaf
#print axioms KappaCheck.AlignedFrameComposition.slack_c_positive
#print axioms KappaCheck.AlignedFrameComposition.slack_c_below_one
#print axioms KappaCheck.AlignedFrameComposition.slack_q_below_reservations
#print axioms KappaCheck.AlignedFrameComposition.slack_lambda_above_tau
#print axioms KappaCheck.AlignedFrameComposition.slack_lambda_above_sigma
#print axioms KappaCheck.AlignedFrameComposition.slack_lambda_above_internal
#print axioms KappaCheck.AlignedFrameComposition.slack_lambda_prime_above_lambda
#print axioms KappaCheck.AlignedFrameComposition.slack_compact_leaf
#print axioms KappaCheck.AlignedFrameComposition.slack_compact_reservations
#print axioms KappaCheck.AlignedFrameComposition.slack_lambda_prime_below_one
#print axioms KappaCheck.AlignedFrameComposition.slack_epsilon_positive
#print axioms KappaCheck.AlignedFrameComposition.slack_epsilon_below_one
#print axioms KappaCheck.AlignedFrameComposition.slack_guard_width
#print axioms KappaCheck.AlignedFrameComposition.slack_K_geometry
#print axioms KappaCheck.AlignedFrameComposition.slack_K_dominates_log
#print axioms KappaCheck.AlignedFrameComposition.slack_record_suffix
#print axioms KappaCheck.AlignedFrameComposition.slack_phase_local
#print axioms KappaCheck.AlignedFrameComposition.slack_phase_boundary
#print axioms KappaCheck.AlignedFrameComposition.slack_gamma_sublinear
#print axioms KappaCheck.AlignedFrameComposition.slack_cell_above_band
#print axioms KappaCheck.AlignedFrameComposition.slack_prime_interval_packing
#print axioms KappaCheck.AlignedFrameComposition.slack_alpha_positive
#print axioms KappaCheck.AlignedFrameComposition.slack_alpha_below_one
#print axioms KappaCheck.AlignedFrameComposition.slack_alpha_below_one_fourth
#print axioms KappaCheck.AlignedFrameComposition.slack_delta_positive
#print axioms KappaCheck.AlignedFrameComposition.slack_delta_below_one_eighth
#print axioms KappaCheck.AlignedFrameComposition.slack_short_record_fallback
#print axioms KappaCheck.AlignedFrameComposition.slack_small_field_exposure
#print axioms KappaCheck.AlignedFrameComposition.slack_artificial_boundary
#print axioms KappaCheck.AlignedFrameComposition.slack_literal_scalar_guard
#print axioms KappaCheck.AlignedFrameComposition.slack_row_product_gap
#print axioms KappaCheck.AlignedFrameComposition.slack_g1_above_kappa
#print axioms KappaCheck.AlignedFrameComposition.slack_g2_above_kappa
#print axioms KappaCheck.AlignedFrameComposition.slack_g3_above_kappa
#print axioms KappaCheck.AlignedFrameComposition.slack_g4_above_kappa
#print axioms KappaCheck.AlignedFrameComposition.slack_g5_above_kappa
#print axioms KappaCheck.AlignedFrameComposition.slack_g6_above_kappa
#print axioms KappaCheck.AlignedFrameComposition.slack_g7_above_kappa
#print axioms KappaCheck.AlignedFrameComposition.margins_strict
#print axioms KappaCheck.AlignedFrameComposition.balanced_identities
#print axioms KappaCheck.AlignedFrameComposition.controlling_margin
#print axioms KappaCheck.AlignedFrameComposition.gain_over_original
#print axioms KappaCheck.AlignedFrameComposition.finite_bridge
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_1
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_1
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_2
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_2
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_3
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_3
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_4
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_4
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_5
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_5
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_6
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_6
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_7
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_7
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_8
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_8
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_9
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_9
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_10
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_10
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_11
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_11
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_12
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_12
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_13
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_13
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_14
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_14
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_15
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_15
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_16
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_16
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_17
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_17
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_18
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_18
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_19
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_19
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_20
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_20
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_21
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_21
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_22
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_22
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_23
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_23
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_25
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_25
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_481
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_481
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_525
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_525
#print axioms KappaCheck.AlignedFrameComposition.accepted_interval_529
#print axioms KappaCheck.AlignedFrameComposition.accepted_taylor_529
#print axioms KappaCheck.AlignedFrameComposition.accepted_profile_link
#print axioms KappaCheck.AlignedFrameComposition.accepted_moment
#print axioms KappaCheck.AlignedFrameComposition.accepted_paid_moment
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_1
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_1
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_2
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_2
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_3
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_3
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_4
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_4
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_5
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_5
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_6
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_6
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_7
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_7
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_8
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_8
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_9
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_9
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_10
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_10
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_11
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_11
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_12
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_12
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_13
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_13
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_14
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_14
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_15
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_15
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_16
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_16
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_17
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_17
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_18
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_18
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_19
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_19
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_20
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_20
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_21
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_21
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_22
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_22
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_23
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_23
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_25
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_25
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_481
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_481
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_525
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_525
#print axioms KappaCheck.AlignedFrameComposition.rejected_interval_529
#print axioms KappaCheck.AlignedFrameComposition.rejected_taylor_529
#print axioms KappaCheck.AlignedFrameComposition.rejected_profile_link
#print axioms KappaCheck.AlignedFrameComposition.rejected_moment
#print axioms KappaCheck.AlignedFrameComposition.rejected_paid_moment
