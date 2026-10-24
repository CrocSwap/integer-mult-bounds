import Mathlib

/-!
# Skel: the combinatorial / analytic cores of the fragmentation-loss theory

Companion to `PROOF.md`. Everything here is stated for a generic exponent
`t` (usually `0 < t < 1`); the shipped invoice uses `t* = 1 - 0.0030233`.

* §1  `x ↦ x^t` on `[0,∞)`: subadditivity (finite sums), strict subadditivity,
       `x ↦ x^(t-1)` antitone consequences, and the two-point exchange (majorization) lemma.
* §2  Rank formula (H2) for subspaces: `dim E + dim F - 2 dim (E ⊓ F) ≥ |dim F - dim E|`, parity.
* §3  Field paths (H1+H2): telescoping, `paid mass = R + 2·(down mass)`, Theorem C (mass and
       moment), the fragmentation loss `Λ_f ≥ 0`, and strict positivity with two climbs.
* §4  Theorem B: the per-call decomposition identity.
* §5  Descent price: `Λ_f ≥ r^t + (R+r)^t - R^t ≥ r^t + (9+r)^t - 9^t`.
* §6  A30-CUT: level crossings (each job's rank ≥ levels it crosses; per-level telescoping)
       and dual feasibility of `y = 8^t/8` for owned fields and credited fields.

Not formalised (paper only): the linear-algebra cut lemma of A30-CUT (independence of the
delivered port vectors modulo `N_λ`), and the identification of the verifier's events with
`FieldPath`s (that is the contract H1–H3, checked on the #4610 word by `verify.py`).
-/

open Finset

namespace Skel

/-! ## §1 The analytic core -/

section Analytic

variable {t : ℝ}

/-- Two-term subadditivity of `x ↦ x^t` for `0 ≤ t ≤ 1`. -/
theorem rpow_add_le {a b : ℝ} (ha : 0 ≤ a) (hb : 0 ≤ b) (ht0 : 0 ≤ t) (ht1 : t ≤ 1) :
    (a + b) ^ t ≤ a ^ t + b ^ t := by
  lift a to NNReal using ha
  lift b to NNReal using hb
  exact_mod_cast NNReal.rpow_add_le_add_rpow a b ht0 ht1

/-- Finite subadditivity: `(Σ xᵢ)^t ≤ Σ xᵢ^t` for `0 < t ≤ 1` and `xᵢ ≥ 0`. -/
theorem rpow_sum_le {ι : Type*} (s : Finset ι) (x : ι → ℝ) (hx : ∀ i ∈ s, 0 ≤ x i)
    (ht0 : 0 < t) (ht1 : t ≤ 1) : (∑ i ∈ s, x i) ^ t ≤ ∑ i ∈ s, x i ^ t := by
  classical
  induction s using Finset.induction_on with
  | empty => simp [Real.zero_rpow ht0.ne']
  | insert a s ha ih =>
    rw [sum_insert ha, sum_insert ha]
    have hxa : 0 ≤ x a := hx a (mem_insert_self a s)
    have hxs : ∀ i ∈ s, 0 ≤ x i := fun i hi => hx i (mem_insert_of_mem hi)
    have h1 := rpow_add_le hxa (sum_nonneg hxs) ht0.le ht1
    linarith [ih hxs]

/-- `x^t = x · x^(t-1)` for `x > 0`. -/
theorem rpow_eq_mul_rpow_sub_one {x : ℝ} (hx : 0 < x) : x ^ t = x * x ^ (t - 1) := by
  rw [Real.rpow_sub_one hx.ne']; field_simp

/-- Chord bound from `x ↦ x^(t-1)` antitone: `x · y^(t-1) ≤ x^t` for `0 ≤ x ≤ y`, `t ≤ 1`. -/
theorem mul_rpow_sub_one_le {x y : ℝ} (hx : 0 ≤ x) (hxy : x ≤ y) (ht1 : t ≤ 1) (ht0 : 0 < t) :
    x * y ^ (t - 1) ≤ x ^ t := by
  rcases hx.eq_or_lt with h | h
  · subst h; simp [Real.zero_rpow ht0.ne']
  · rw [rpow_eq_mul_rpow_sub_one h]
    exact mul_le_mul_of_nonneg_left (Real.rpow_le_rpow_of_nonpos h hxy (by linarith)) h.le

/-- Strict two-term subadditivity for `0 < t < 1` and `a, b > 0`. -/
theorem rpow_add_lt {a b : ℝ} (ha : 0 < a) (hb : 0 < b) (ht1 : t < 1) :
    (a + b) ^ t < a ^ t + b ^ t := by
  have hab : 0 < a + b := by linarith
  have h1 : (a + b) ^ (t - 1) < a ^ (t - 1) :=
    Real.rpow_lt_rpow_of_neg ha (by linarith) (by linarith)
  have h2 : (a + b) ^ (t - 1) < b ^ (t - 1) :=
    Real.rpow_lt_rpow_of_neg hb (by linarith) (by linarith)
  rw [rpow_eq_mul_rpow_sub_one hab, rpow_eq_mul_rpow_sub_one ha, rpow_eq_mul_rpow_sub_one hb]
  nlinarith [mul_lt_mul_of_pos_left h1 ha, mul_lt_mul_of_pos_left h2 hb]

/-- Strict finite subadditivity: two positive terms make `(Σ x)^t < Σ x^t`. -/
theorem rpow_sum_lt {ι : Type*} [DecidableEq ι] (s : Finset ι) (x : ι → ℝ)
    (hx : ∀ i ∈ s, 0 ≤ x i) {i k : ι} (hi : i ∈ s) (hk : k ∈ s) (hik : i ≠ k)
    (hxi : 0 < x i) (hxk : 0 < x k) (ht0 : 0 < t) (ht1 : t < 1) :
    (∑ j ∈ s, x j) ^ t < ∑ j ∈ s, x j ^ t := by
  have hk' : k ∈ s.erase i := mem_erase.mpr ⟨hik.symm, hk⟩
  have hxe : ∀ j ∈ s.erase i, 0 ≤ x j := fun j hj => hx j (mem_of_mem_erase hj)
  have hB : x k ≤ ∑ j ∈ s.erase i, x j := single_le_sum hxe hk'
  rw [← add_sum_erase s x hi, ← add_sum_erase s (fun j => x j ^ t) hi]
  have h1 := rpow_add_lt hxi (lt_of_lt_of_le hxk hB) ht1 (t := t)
  have h2 := rpow_sum_le (s.erase i) x hxe ht0 ht1.le
  linarith

/-- Two-point exchange (majorization): for `x ≤ y` and `r ≥ 0`,
`(y+r)^t - y^t ≤ (x+r)^t - x^t`. Equivalently `x^t + (y+r)^t ≤ (x+r)^t + y^t`. -/
theorem rpow_increment_antitone {x y r : ℝ} (hx : 0 ≤ x) (hxy : x ≤ y) (hr : 0 ≤ r)
    (ht0 : 0 ≤ t) (ht1 : t ≤ 1) : (y + r) ^ t - y ^ t ≤ (x + r) ^ t - x ^ t := by
  rcases (add_nonneg (sub_nonneg.mpr hxy) hr).eq_or_lt with hL | hL
  · have hr0 : r = 0 := by linarith [sub_nonneg.mpr hxy]
    have hy : y = x := by linarith [sub_nonneg.mpr hxy]
    subst hr0; subst hy; simp
  set L := y - x + r with hLdef
  set μ := r / L with hμ
  have hμ0 : 0 ≤ μ := div_nonneg hr hL.le
  have hμ1 : μ ≤ 1 := by rw [hμ, div_le_one hL]; linarith
  have hc := (Real.concaveOn_rpow ht0 ht1).2
  have hxI : x ∈ Set.Ici (0 : ℝ) := hx
  have hyrI : y + r ∈ Set.Ici (0 : ℝ) := by simp only [Set.mem_Ici]; linarith
  have e1 : (1 - μ) • x + μ • (y + r) = x + r := by
    simp only [smul_eq_mul]; rw [hμ]; field_simp; ring
  have e2 : μ • x + (1 - μ) • (y + r) = y := by
    simp only [smul_eq_mul]; rw [hμ]; field_simp; ring
  have c1 := hc hxI hyrI (by linarith : 0 ≤ 1 - μ) hμ0 (by ring)
  have c2 := hc hxI hyrI hμ0 (by linarith : 0 ≤ 1 - μ) (by ring)
  rw [e1] at c1; rw [e2] at c2
  simp only [smul_eq_mul] at c1 c2
  linarith

end Analytic

/-! ## §2 The rank formula (H2) -/

section Rank

variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]

/-- Paid rank of a transport `E → F` (P:15): `dim E + dim F - 2 dim (E ∩ F)`. -/
noncomputable def rankCost (E F : Submodule K V) : ℤ :=
  (Module.finrank K E : ℤ) + Module.finrank K F - 2 * Module.finrank K (E ⊓ F : Submodule K V)

/-- H2: the paid rank is at least the dimension change. -/
theorem rankCost_ge_abs [FiniteDimensional K V] (E F : Submodule K V) :
    |(Module.finrank K F : ℤ) - Module.finrank K E| ≤ rankCost E F := by
  have h1 : Module.finrank K (E ⊓ F : Submodule K V) ≤ Module.finrank K E :=
    Submodule.finrank_mono inf_le_left
  have h2 : Module.finrank K (E ⊓ F : Submodule K V) ≤ Module.finrank K F :=
    Submodule.finrank_mono inf_le_right
  unfold rankCost
  rw [abs_le]; constructor <;> omega

/-- Nested frames pay exactly the dimension gap. -/
theorem rankCost_nested {E F : Submodule K V} (h : E ≤ F) :
    rankCost E F = (Module.finrank K F : ℤ) - Module.finrank K E := by
  unfold rankCost; rw [inf_eq_left.mpr h]; ring

/-- Parity: the paid rank has the parity of the dimension change. -/
theorem rankCost_parity (E F : Submodule K V) :
    Even (rankCost E F - ((Module.finrank K F : ℤ) - Module.finrank K E)) := by
  unfold rankCost
  exact ⟨(Module.finrank K E : ℤ) - Module.finrank K (E ⊓ F : Submodule K V), by ring⟩

end Rank

/-! ## §3 Field paths, telescoping, Theorem C and `Λ_f ≥ 0` -/

/-- An abstract field history: `dim j` is the frame dimension after `j` events and `cost j` the
rank paid at event `j` (zero for warps and scalar operations). Hypothesis `hcost` is H1+H2:
free events preserve dimension, paid ones cost at least the dimension change. -/
structure FieldPath where
  n : ℕ
  dim : ℕ → ℤ
  cost : ℕ → ℤ
  hcost : ∀ j ∈ range n, |dim (j + 1) - dim j| ≤ cost j

namespace FieldPath

variable (P : FieldPath)

/-- Credited rank `R_f = dim final - dim start` (P:19 / H3). -/
def R : ℤ := P.dim P.n - P.dim 0
/-- Paid mass. -/
def mass : ℤ := ∑ j ∈ range P.n, P.cost j
/-- Down mass: total size of descents. -/
def down : ℤ := ∑ j ∈ range P.n, max (-(P.dim (j + 1) - P.dim j)) 0

theorem cost_nonneg {j : ℕ} (hj : j ∈ range P.n) : 0 ≤ P.cost j :=
  (abs_nonneg _).trans (P.hcost j hj)

theorem abs_split (x : ℤ) : |x| = x + 2 * max (-x) 0 := by
  rcases abs_cases x with ⟨h1, h2⟩ | ⟨h1, h2⟩ <;>
    rcases max_cases (-x) 0 with ⟨h3, h4⟩ | ⟨h3, h4⟩ <;> omega

/-- Telescoping of the dimension changes. -/
theorem telescope : ∑ j ∈ range P.n, (P.dim (j + 1) - P.dim j) = P.R :=
  sum_range_sub P.dim P.n

/-- The integer path identity: `Σ|Δ| = R + 2·down`. -/
theorem sum_abs_eq : ∑ j ∈ range P.n, |P.dim (j + 1) - P.dim j| = P.R + 2 * P.down := by
  simp_rw [abs_split]
  rw [sum_add_distrib, ← mul_sum, telescope]; rfl

theorem down_nonneg : 0 ≤ P.down := sum_nonneg fun _ _ => le_max_right _ _

/-- Paid mass is at least `R + 2·down`. -/
theorem mass_ge : P.R + 2 * P.down ≤ P.mass := by
  rw [← sum_abs_eq]; exact sum_le_sum P.hcost

/-- Theorem C (mass): `Hnet_f = mass - R ≥ 0`. -/
theorem hnet_nonneg : P.R ≤ P.mass := by linarith [P.mass_ge, P.down_nonneg]

/-- Theorem C (mass) with inverse credit: crediting every descent as well keeps `Hnet ≥ 0`. -/
theorem hnet_inverse_nonneg : P.R + P.down ≤ P.mass := by linarith [P.mass_ge, P.down_nonneg]

/-- Paid `t`-moment of the field. -/
noncomputable def moment (t : ℝ) : ℝ := ∑ j ∈ range P.n, ((P.cost j : ℝ)) ^ t
/-- Fragmentation loss `Λ_f(t) = Σ_j c_j^t - R_f^t`. -/
noncomputable def lam (t : ℝ) : ℝ := P.moment t - ((P.R : ℝ)) ^ t

theorem cast_mass : ((P.mass : ℤ) : ℝ) = ∑ j ∈ range P.n, ((P.cost j : ℝ)) := by
  unfold mass; push_cast; rfl

/-- `(mass)^t ≤ moment`. -/
theorem mass_rpow_le {t : ℝ} (ht0 : 0 < t) (ht1 : t ≤ 1) :
    ((P.mass : ℝ)) ^ t ≤ P.moment t := by
  rw [cast_mass]
  exact rpow_sum_le _ _ (fun j hj => by exact_mod_cast P.cost_nonneg hj) ht0 ht1

/-- Theorem B's inequality: `Λ_f(t) ≥ 0` for `0 < t ≤ 1` whenever `R_f ≥ 0`. -/
theorem lam_nonneg {t : ℝ} (hR : 0 ≤ P.R) (ht0 : 0 < t) (ht1 : t ≤ 1) : 0 ≤ P.lam t := by
  have h1 : ((P.R : ℝ)) ^ t ≤ ((P.mass : ℝ)) ^ t :=
    Real.rpow_le_rpow (by exact_mod_cast hR) (by exact_mod_cast P.hnet_nonneg) ht0.le
  unfold lam; linarith [P.mass_rpow_le ht0 ht1]

/-- Theorem C (moment): a helper credited `R_f` contributes `R_f^t - moment = -Λ_f ≤ 0`. -/
theorem helper_contribution_nonpos {t : ℝ} (hR : 0 ≤ P.R) (ht0 : 0 < t) (ht1 : t ≤ 1) :
    ((P.R : ℝ)) ^ t - P.moment t ≤ 0 := by
  have := P.lam_nonneg hR ht0 ht1; unfold lam at this; linarith

/-- Strictness: two climbs of positive rank make `Λ_f(t) > 0` for `0 < t < 1`.
So `Λ_f = 0` forces at most one paid job. -/
theorem lam_pos_of_two {t : ℝ} (hR : 0 ≤ P.R) (ht0 : 0 < t) (ht1 : t < 1) {i k : ℕ}
    (hi : i ∈ range P.n) (hk : k ∈ range P.n) (hik : i ≠ k)
    (hci : 0 < P.cost i) (hck : 0 < P.cost k) : 0 < P.lam t := by
  have h1 : ((P.R : ℝ)) ^ t ≤ ((P.mass : ℝ)) ^ t :=
    Real.rpow_le_rpow (by exact_mod_cast hR) (by exact_mod_cast P.hnet_nonneg) ht0.le
  have h2 : ((P.mass : ℝ)) ^ t < P.moment t := by
    rw [cast_mass]
    exact rpow_sum_lt _ (fun j => (P.cost j : ℝ)) (fun j hj => by exact_mod_cast P.cost_nonneg hj)
      hi hk hik (by exact_mod_cast hci) (by exact_mod_cast hck) ht0 ht1
  unfold lam; linarith

end FieldPath

/-! ### Bridge: a frame history of actual subspaces is a `FieldPath`

Events are either paid transports (cost `rankCost`, H2) or free events (warps, scalar ops) that
preserve the frame dimension (H1). -/
section Bridge

variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V] [FiniteDimensional K V]

/-- The `FieldPath` of a frame history `E 0, E 1, …, E n` with paid steps `paid`. -/
noncomputable def FieldPath.ofSubspaces (n : ℕ) (E : ℕ → Submodule K V) (paid : ℕ → Prop)
    [DecidablePred paid]
    (hfree : ∀ j ∈ range n, ¬ paid j →
      Module.finrank K (E (j + 1)) = Module.finrank K (E j)) : FieldPath where
  n := n
  dim j := Module.finrank K (E j)
  cost j := if paid j then rankCost (E j) (E (j + 1)) else 0
  hcost j hj := by
    by_cases h : paid j
    · rw [if_pos h]; exact rankCost_ge_abs _ _
    · rw [if_neg h, hfree j hj h]; simp

/-- Theorem B/C for subspace histories: `Λ_f(t) ≥ 0` whenever the final frame is at least as
large as the start (helpers: strict `S ⊂ T`, P:19; mains: contract endpoints). -/
theorem lam_nonneg_ofSubspaces (n : ℕ) (E : ℕ → Submodule K V) (paid : ℕ → Prop)
    [DecidablePred paid]
    (hfree : ∀ j ∈ range n, ¬ paid j →
      Module.finrank K (E (j + 1)) = Module.finrank K (E j))
    (hR : Module.finrank K (E 0) ≤ Module.finrank K (E n)) {t : ℝ} (ht0 : 0 < t) (ht1 : t ≤ 1) :
    0 ≤ (FieldPath.ofSubspaces n E paid hfree).lam t := by
  apply FieldPath.lam_nonneg _ _ ht0 ht1
  show (0 : ℤ) ≤ (Module.finrank K (E n) : ℤ) - Module.finrank K (E 0)
  omega

end Bridge

/-! ## §4 Theorem B: the per-call decomposition identity

Native per-call moment `φ = Σ_helpers h^t - Σ_paid r^t`. Partition paid jobs into helper fields,
main fields and centre jobs. Helpers are credited `h_f = R_f^t`; every main has `R_f = d`.
Then `φ = -(#mains)·d^t - centre - Σ_f Λ_f`. -/
theorem decomposition {ι κ : Type*} (helpers : Finset ι) (mains : Finset κ)
    (credit : ι → ℝ) (paidH : ι → ℝ) (paidM : κ → ℝ) (dt centre : ℝ) :
    (∑ i ∈ helpers, credit i) - (∑ i ∈ helpers, paidH i + ∑ k ∈ mains, paidM k + centre)
      = -(mains.card : ℝ) * dt - centre
        - (∑ i ∈ helpers, (paidH i - credit i) + ∑ k ∈ mains, (paidM k - dt)) := by
  simp only [sum_sub_distrib, sum_const, nsmul_eq_mul]; ring

/-! ## §5 The descent price -/

namespace FieldPath

variable (P : FieldPath)

/-- Descent price: a field with fixed endpoints (`R ≥ 0`) and one descent of rank `r` at step `k`
pays `Λ_f(t) ≥ r^t + (R+r)^t - R^t`. -/
theorem descent_price {t : ℝ} (hR : 0 ≤ P.R) (ht0 : 0 < t) (ht1 : t ≤ 1) {k : ℕ}
    (hk : k ∈ range P.n) {r : ℤ} (hr : 0 ≤ r) (hdesc : P.dim (k + 1) - P.dim k = -r) :
    ((r : ℝ)) ^ t + (((P.R + r : ℤ) : ℝ)) ^ t - ((P.R : ℝ)) ^ t ≤ P.lam t := by
  -- the descent step pays at least r
  have hck : r ≤ P.cost k := by
    have := P.hcost k hk; rw [hdesc, abs_neg, abs_of_nonneg hr] at this; exact this
  -- the remaining steps carry up-mass at least R + r
  have hrest : P.R + r ≤ ∑ j ∈ (range P.n).erase k, P.cost j := by
    have htel := P.telescope
    rw [← add_sum_erase _ _ hk, hdesc] at htel
    have : ∑ j ∈ (range P.n).erase k, (P.dim (j + 1) - P.dim j)
        ≤ ∑ j ∈ (range P.n).erase k, P.cost j :=
      sum_le_sum fun j hj => (le_abs_self _).trans (P.hcost j (mem_of_mem_erase hj))
    linarith
  have hnn : ∀ j ∈ (range P.n).erase k, (0 : ℝ) ≤ (P.cost j : ℝ) :=
    fun j hj => by exact_mod_cast P.cost_nonneg (mem_of_mem_erase hj)
  have e1 : ((r : ℝ)) ^ t ≤ ((P.cost k : ℝ)) ^ t :=
    Real.rpow_le_rpow (by exact_mod_cast hr) (by exact_mod_cast hck) ht0.le
  have e2 : (((P.R + r : ℤ) : ℝ)) ^ t ≤ (∑ j ∈ (range P.n).erase k, (P.cost j : ℝ)) ^ t := by
    apply Real.rpow_le_rpow (by exact_mod_cast (by linarith : (0 : ℤ) ≤ P.R + r))
    · exact_mod_cast hrest
    · exact ht0.le
  have e3 := rpow_sum_le ((range P.n).erase k) (fun j => (P.cost j : ℝ)) hnn ht0 ht1
  have hm : P.moment t = ((P.cost k : ℝ)) ^ t
      + ∑ j ∈ (range P.n).erase k, ((P.cost j : ℝ)) ^ t := by
    unfold moment; rw [← add_sum_erase _ _ hk]
  unfold lam; rw [hm]; linarith

/-- Descent price, worst case over `R ≤ 9` (frames live in `F₂⁹`):
`Λ_f(t) ≥ r^t + (9+r)^t - 9^t`. -/
theorem descent_price_nine {t : ℝ} (hR : 0 ≤ P.R) (hR9 : P.R ≤ 9) (ht0 : 0 < t) (ht1 : t ≤ 1)
    {k : ℕ} (hk : k ∈ range P.n) {r : ℤ} (hr : 0 ≤ r) (hdesc : P.dim (k + 1) - P.dim k = -r) :
    ((r : ℝ)) ^ t + ((9 : ℝ) + r) ^ t - (9 : ℝ) ^ t ≤ P.lam t := by
  have h := P.descent_price hR ht0 ht1 hk hr hdesc
  have hm := rpow_increment_antitone (x := (P.R : ℝ)) (y := 9) (r := (r : ℝ))
    (by exact_mod_cast hR) (by exact_mod_cast hR9) (by exact_mod_cast hr) ht0.le ht1
  push_cast at h
  linarith

end FieldPath

/-! ## §6 A30-CUT: level crossings and the dual certificate `y = 8^t / 8` -/

section Levels

/-- Step `a → b` crosses level `λ` (upward or downward). -/
def Crosses (a b l : ℤ) : Prop := (a < l ∧ l ≤ b) ∨ (b < l ∧ l ≤ a)

instance (a b l : ℤ) : Decidable (Crosses a b l) := by unfold Crosses; infer_instance

/-- A step crosses at most `|b - a|` levels of any level set (rank is 1-Lipschitz). -/
theorem levels_crossed_le (L : Finset ℤ) (a b : ℤ) :
    ((L.filter (Crosses a b)).card : ℤ) ≤ |b - a| := by
  have hsub : L.filter (Crosses a b) ⊆ Ioc (min a b) (max a b) := by
    intro l hl
    rw [mem_filter] at hl
    rw [mem_Ioc]
    rcases hl.2 with ⟨h1, h2⟩ | ⟨h1, h2⟩
    · exact ⟨lt_of_le_of_lt (min_le_left _ _) h1, le_trans h2 (le_max_right _ _)⟩
    · exact ⟨lt_of_le_of_lt (min_le_right _ _) h1, le_trans h2 (le_max_left _ _)⟩
  have hc := card_le_card hsub
  rw [Int.card_Ioc] at hc
  have : ((max a b - min a b).toNat : ℤ) = |b - a| := by
    rw [Int.toNat_of_nonneg (by linarith [min_le_max (a := a) (b := b)])]
    rcases le_total a b with h | h
    · rw [max_eq_right h, min_eq_left h, abs_of_nonneg (by linarith)]
    · rw [max_eq_left h, min_eq_right h, abs_of_nonpos (by linarith)]; ring
  omega

/-- Per-level telescoping: at every step, (up-crossing) − (down-crossing) at level `λ` equals the
change of the indicator `[λ ≤ dim]`. -/
theorem step_level (a b l : ℤ) :
    ((if a < l ∧ l ≤ b then 1 else 0) - (if b < l ∧ l ≤ a then 1 else 0) : ℤ)
      = (if l ≤ b then 1 else 0) - (if l ≤ a then 1 else 0) := by
  split_ifs <;> omega

namespace FieldPath

variable (P : FieldPath)

/-- Up-crossings of level `λ` along the path. -/
def up (l : ℤ) : ℤ := ∑ j ∈ range P.n, if P.dim j < l ∧ l ≤ P.dim (j + 1) then 1 else 0
/-- Down-crossings of level `λ` along the path. -/
def dn (l : ℤ) : ℤ := ∑ j ∈ range P.n, if P.dim (j + 1) < l ∧ l ≤ P.dim j then 1 else 0

/-- Per-level telescoping: `up λ - down λ = [λ ≤ final] - [λ ≤ start]`. -/
theorem up_sub_dn (l : ℤ) :
    P.up l - P.dn l = (if l ≤ P.dim P.n then 1 else 0) - (if l ≤ P.dim 0 then 1 else 0) := by
  unfold up dn
  rw [← sum_sub_distrib]
  simp_rw [step_level]
  exact sum_range_sub (fun j => if l ≤ P.dim j then (1 : ℤ) else 0) P.n

/-- Each job's rank pays for every level it crosses: `Σ_{λ∈L} (up λ + down λ) ≤ mass`. -/
theorem crossings_le_mass (L : Finset ℤ) : ∑ l ∈ L, (P.up l + P.dn l) ≤ P.mass := by
  unfold up dn mass
  simp_rw [← sum_add_distrib]
  rw [sum_comm]
  refine sum_le_sum fun j hj => ?_
  have h1 : ∑ l ∈ L, ((if P.dim j < l ∧ l ≤ P.dim (j + 1) then (1 : ℤ) else 0)
      + (if P.dim (j + 1) < l ∧ l ≤ P.dim j then 1 else 0))
      = ((L.filter (Crosses (P.dim j) (P.dim (j + 1)))).card : ℤ) := by
    rw [card_filter]; push_cast
    refine sum_congr rfl fun l _ => ?_
    unfold Crosses; split_ifs <;> omega
  rw [h1]
  exact (levels_crossed_le L _ _).trans (P.hcost j hj)

end FieldPath

end Levels

section Dual

variable {t : ℝ}

/-- `y = 8^t/8 < 1` for `t < 1`. -/
theorem y_lt_one (ht1 : t < 1) : (8 : ℝ) ^ t / 8 < 1 := by
  have : (8 : ℝ) ^ t < (8 : ℝ) ^ (1 : ℝ) := Real.rpow_lt_rpow_of_exponent_lt (by norm_num) ht1
  rw [Real.rpow_one] at this; rw [div_lt_one (by norm_num)]; exact this

/-- Dual feasibility for an owned job of rank `a`: `a^t ≥ y · min(a, 8)` with `y = 8^t/8`. -/
theorem owned_dual {a : ℝ} (ha : 0 ≤ a) (ht0 : 0 < t) (ht1 : t ≤ 1) :
    (8 : ℝ) ^ t / 8 * min a 8 ≤ a ^ t := by
  rcases le_total a 8 with h | h
  · rw [min_eq_left h]
    have := mul_rpow_sub_one_le ha h ht1 ht0 (t := t)
    rw [Real.rpow_sub_one (by norm_num : (8 : ℝ) ≠ 0)] at this
    linarith [show (8 : ℝ) ^ t / 8 * a = a * ((8 : ℝ) ^ t / 8) by ring]
  · rw [min_eq_right h]
    have := Real.rpow_le_rpow (by norm_num : (0 : ℝ) ≤ 8) h ht0.le
    linarith

/-- Dual feasibility, credited field with `k = 1`: two or more jobs of rank `≥ 1` with total
`≥ R + 2` pay `Σ c^t ≥ R^t + 1`, so the loss `≥ 1 > y`. -/
theorem credited_k1 {ι : Type*} [DecidableEq ι] (s : Finset ι) (c : ι → ℝ)
    (hc : ∀ j ∈ s, 1 ≤ c j) {i k : ι} (hi : i ∈ s) (hk : k ∈ s) (hik : i ≠ k)
    {R : ℝ} (hR : 0 ≤ R) (hsum : R + 2 ≤ ∑ j ∈ s, c j) (ht0 : 0 < t) (ht1 : t ≤ 1) :
    R ^ t + 1 ≤ ∑ j ∈ s, c j ^ t := by
  have hk' : k ∈ s.erase i := mem_erase.mpr ⟨hik.symm, hk⟩
  have hce : ∀ j ∈ s.erase i, 0 ≤ c j := fun j hj => by linarith [hc j (mem_of_mem_erase hj)]
  set B := ∑ j ∈ s.erase i, c j with hBdef
  have hB1 : 1 ≤ B := le_trans (hc k hk) (single_le_sum hce hk')
  have hci := hc i hi
  have hsplit : ∑ j ∈ s, c j = c i + B := (add_sum_erase s c hi).symm
  have hsplit' : ∑ j ∈ s, c j ^ t = c i ^ t + ∑ j ∈ s.erase i, c j ^ t :=
    (add_sum_erase s (fun j => c j ^ t) hi).symm
  have hBt := rpow_sum_le (s.erase i) c hce ht0 ht1
  -- exchange: c_i^t + B^t ≥ 1^t + (c_i + B - 1)^t
  have hx := rpow_increment_antitone (x := 1) (y := B) (r := c i - 1) (by norm_num) hB1
    (by linarith) ht0.le ht1
  have e1 : B + (c i - 1) = c i + B - 1 := by ring
  have e2 : (1 : ℝ) + (c i - 1) = c i := by ring
  rw [e1, e2, Real.one_rpow] at hx
  have hmono : R ^ t ≤ (c i + B - 1) ^ t :=
    Real.rpow_le_rpow hR (by linarith) ht0.le
  rw [hsplit']; linarith

/-- Bernoulli-type bound used for the numerics: `9^(t-1) ≥ 25/27` for `t ≥ 99/100`. -/
theorem nine_rpow_sub_one_ge (ht : 99 / 100 ≤ t) (ht1 : t ≤ 1) :
    (25 / 27 : ℝ) ≤ (9 : ℝ) ^ (t - 1) := by
  have hb := rpow_one_add_le_one_add_mul_self (s := 8) (by norm_num) (p := 1 - t)
    (by linarith) (by linarith)
  have hpos : 0 < (9 : ℝ) ^ (1 - t) := Real.rpow_pos_of_pos (by norm_num) _
  have hle : (9 : ℝ) ^ (1 - t) ≤ 27 / 25 := by norm_num at hb ⊢; linarith
  have : (9 : ℝ) ^ (t - 1) = ((9 : ℝ) ^ (1 - t))⁻¹ := by
    rw [← Real.rpow_neg (by norm_num)]; ring_nf
  rw [this, le_inv_comm₀ (by norm_num) hpos]
  linarith [show ((25 / 27 : ℝ))⁻¹ = 27 / 25 by norm_num]

/-- `x^t ≤ x + 1` for `x ≥ 0`, `0 ≤ t ≤ 1`. -/
theorem rpow_le_add_one {x : ℝ} (hx : 0 ≤ x) (ht0 : 0 ≤ t) (ht1 : t ≤ 1) : x ^ t ≤ x + 1 := by
  rcases le_total x 1 with h | h
  · linarith [Real.rpow_le_one hx h ht0]
  · have := Real.rpow_le_rpow_of_exponent_le h ht1
    rw [Real.rpow_one] at this; linarith

/-- Dual feasibility, credited field with `k ≥ 2` (for `t ∈ [0.99, 1]`): jobs of rank `≤ 9`
with total `≥ R + 2k`, `0 ≤ R ≤ 9`, have loss `Σ c^t - R^t ≥ y·k`. -/
theorem credited_k2 {ι : Type*} (s : Finset ι) (c : ι → ℝ) (hc0 : ∀ j ∈ s, 0 ≤ c j)
    (hc9 : ∀ j ∈ s, c j ≤ 9) {R k : ℝ} (hR : 0 ≤ R) (hR9 : R ≤ 9) (hk : 2 ≤ k)
    (hsum : R + 2 * k ≤ ∑ j ∈ s, c j) (ht : 99 / 100 ≤ t) (ht1 : t ≤ 1) :
    (8 : ℝ) ^ t / 8 * k ≤ ∑ j ∈ s, c j ^ t - R ^ t := by
  have ht0 : 0 < t := by linarith
  set q := (9 : ℝ) ^ (t - 1) with hq
  have hq0 : 25 / 27 ≤ q := nine_rpow_sub_one_ge ht ht1
  have hchord : ∑ j ∈ s, c j * q ≤ ∑ j ∈ s, c j ^ t :=
    sum_le_sum fun j hj => mul_rpow_sub_one_le (hc0 j hj) (hc9 j hj) ht1 ht0
  rw [← sum_mul] at hchord
  have hy : (8 : ℝ) ^ t / 8 ≤ 1 := by
    rcases ht1.eq_or_lt with h | h
    · rw [h, Real.rpow_one]; norm_num
    · exact (y_lt_one h).le
  have hRt := rpow_le_add_one hR ht0.le ht1
  have hy0 : 0 ≤ (8 : ℝ) ^ t / 8 := by positivity
  nlinarith [mul_le_mul_of_nonneg_left hy (by linarith : (0 : ℝ) ≤ k),
    mul_le_mul_of_nonneg_right hsum (by linarith : (0 : ℝ) ≤ q),
    mul_le_mul_of_nonneg_left hq0 (by linarith : (0 : ℝ) ≤ R + 2 * k)]

end Dual

end Skel

#print axioms Skel.rpow_sum_le
#print axioms Skel.rpow_sum_lt
#print axioms Skel.rpow_increment_antitone
#print axioms Skel.rankCost_ge_abs
#print axioms Skel.rankCost_nested
#print axioms Skel.rankCost_parity
#print axioms Skel.FieldPath.sum_abs_eq
#print axioms Skel.FieldPath.hnet_nonneg
#print axioms Skel.FieldPath.hnet_inverse_nonneg
#print axioms Skel.FieldPath.lam_nonneg
#print axioms Skel.FieldPath.helper_contribution_nonpos
#print axioms Skel.FieldPath.lam_pos_of_two
#print axioms Skel.lam_nonneg_ofSubspaces
#print axioms Skel.decomposition
#print axioms Skel.FieldPath.descent_price
#print axioms Skel.FieldPath.descent_price_nine
#print axioms Skel.levels_crossed_le
#print axioms Skel.FieldPath.up_sub_dn
#print axioms Skel.FieldPath.crossings_le_mass
#print axioms Skel.owned_dual
#print axioms Skel.credited_k1
#print axioms Skel.credited_k2
