import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Abel

/-! Integral column counts and the single charge for every edge of a finite band. -/

namespace BandFlow

open scoped BigOperators

/-- The generator puts this many complete columns at virtual width `x`. -/
noncomputable def columns (x : ℝ) : ℕ := ⌊x⌋₊ - 1

theorem column_window {x : ℝ} (hx : 2 ≤ x) :
    x - 2 < (columns x : ℝ) ∧ (columns x : ℝ) ≤ x - 1 := by
  have hf : 1 ≤ ⌊x⌋₊ := Nat.le_floor (by simpa using (show (1 : ℝ) ≤ x by linarith))
  have h1 := Nat.floor_le (show 0 ≤ x by linarith)
  have h2 := Nat.lt_floor_add_one x
  simp only [columns, Nat.cast_sub hf, Nat.cast_one]
  constructor <;> linarith

/-- An internal port takes the first child axes. Its complement is a valid
    nonnegative integral rank and costs fewer than two target blocks. -/
theorem interface_fringe {x y : ℝ} {r k : ℕ} (hx : 2 ≤ x) (hy : 2 ≤ y)
    (hr : 0 < r) (hk : 2*r ≤ k) (hmatch : (r : ℝ)*y = (k : ℝ)*x) :
    k * columns x ≤ r * columns y ∧
    r * columns y - k * columns x < 2*k := by
  obtain ⟨hx₁, hx₂⟩ := column_window hx
  obtain ⟨hy₁, hy₂⟩ := column_window hy
  have hrr : (0 : ℝ) < r := by exact_mod_cast hr
  have hkk : (2 : ℝ)*r ≤ k := by exact_mod_cast hk
  have hkp : (0 : ℝ) < k := by linarith
  have he : (k : ℝ) * (columns x : ℝ) ≤ (r : ℝ) * (columns y : ℝ) := by
    nlinarith [mul_le_mul_of_nonneg_left hx₂ hkp.le,
      mul_le_mul_of_nonneg_left hy₁.le hrr.le]
  have he' : k * columns x ≤ r * columns y := by exact_mod_cast he
  refine ⟨he', ?_⟩
  have hs : (r : ℝ)*(columns y : ℝ) - (k : ℝ)*(columns x : ℝ) < 2*(k : ℝ) := by
    nlinarith [mul_le_mul_of_nonneg_left hy₂ hrr.le,
      mul_lt_mul_of_pos_left hx₁ hkp]
  exact_mod_cast (show ((r * columns y - k * columns x : ℕ) : ℝ) < (2 : ℝ)*k by
    simpa only [Nat.cast_sub he', Nat.cast_mul] using hs)

/-- The true number of source axes pays a fixed fraction of the virtual size. -/
theorem source_columns {x L : ℝ} (hL : 2 ≤ L) (hx : L ≤ x) :
    (1 - 2/L)*x ≤ (columns x : ℝ) := by
  have hL' : 0 < L := by linarith
  have h := (column_window (hL.trans hx)).1.le
  have hdiv : (2/L)*L = (2 : ℝ) := div_mul_cancel₀ _ hL'.ne'
  have hz : 0 ≤ 2/L := by positivity
  nlinarith [mul_le_mul_of_nonneg_left hx hz]

private theorem powers_recombine {x C : ℝ} (hx : 0 < x) :
    x^C * x^(1-C) = x := by
  rw [← Real.rpow_add hx, add_sub_cancel, Real.rpow_one]

/-- The same factor that pays terminal calls also pays complete rank-one
    residuals at internal ports. -/
theorem port_allowance {C A L k x : ℝ} (hC : 0 ≤ C) (ht : C ≤ 1)
    (hL : 0 < L) (hk : 0 < k) (hkA : k ≤ A) (hx : L ≤ x) :
    L*k ≤ (A*L)^C * (k*x)^(1-C) := by
  have hs := Real.rpow_le_rpow (mul_pos hk hL).le (mul_le_mul_of_nonneg_right hkA hL.le) hC
  have hp := Real.rpow_le_rpow (mul_pos hk hL).le (mul_le_mul_of_nonneg_left hx hk.le)
    (show 0 ≤ 1-C by linarith)
  calc
    L*k = (k*L)^C*(k*L)^(1-C) := by rw [powers_recombine (mul_pos hk hL), mul_comm]
    _ ≤ _ := mul_le_mul hs hp (Real.rpow_nonneg (mul_pos hk hL).le _)
        (Real.rpow_nonneg (mul_nonneg (hk.le.trans hkA) hL.le) _)

theorem terminal_allowance {C A L a : ℝ} (hC : 0 ≤ C)
    (ha : 0 < a) (hstop : a ≤ A*L) :
    a ≤ (A*L)^C * a^(1-C) := by
  calc
    a = a^C * a^(1-C) := (powers_recombine ha).symm
    _ ≤ _ := mul_le_mul_of_nonneg_right (Real.rpow_le_rpow ha.le hstop hC)
      (Real.rpow_nonneg ha.le _)

/-- Use one strict native moment for all inputs at a live node. -/
theorem local_charge {I J : Type*} [Fintype I] [Fintype J]
    (k : I → ℝ) (r : J → ℝ) (lost : I → ℝ) {C A L x ε : ℝ}
    (hC : 0 ≤ C) (ht : C ≤ 1) (hL : 0 < L) (hx : L ≤ x)
    (hε : 0 ≤ ε) (hfund : 2 ≤ ε*L)
    (hk : ∀ i, 0 < k i ∧ k i ≤ A) (hr : ∀ j, 0 ≤ r j)
    (hfringe : ∀ i, lost i ≤ 2*k i)
    (hnative : ∑ j, (r j)^(1-C) ≤ (1-ε) * ∑ i, (k i)^(1-C)) :
    (∑ i, lost i) + (A*L)^C * ∑ j, (r j*x)^(1-C) ≤
      (A*L)^C * ∑ i, (k i*x)^(1-C) := by
  have hx' : 0 < x := hL.trans_le hx
  have hn : ∑ j, (r j*x)^(1-C) ≤ (1-ε) * ∑ i, (k i*x)^(1-C) := by
    simpa only [Real.mul_rpow (hr _) hx'.le, Real.mul_rpow (hk _).1.le hx'.le,
      Finset.sum_mul, mul_assoc] using
      mul_le_mul_of_nonneg_right hnative (Real.rpow_nonneg hx'.le (1-C))
  have hloc : ∀ i, lost i ≤ ε*((A*L)^C*(k i*x)^(1-C)) := by
    intro i
    have h := port_allowance hC ht hL (hk i).1 (hk i).2 hx
    calc
      lost i ≤ 2*k i := hfringe i
      _ ≤ ε*(L*k i) := by simpa only [mul_assoc] using
        mul_le_mul_of_nonneg_right hfund (hk i).1.le
      _ ≤ _ := mul_le_mul_of_nonneg_left h hε
  have hsum := Finset.sum_le_sum (s := Finset.univ) (fun i _ => hloc i)
  simp only [← Finset.mul_sum] at hsum
  by_cases hI : Nonempty I
  · have hA : 0 ≤ A := ((hk (Classical.choice hI)).1.le).trans (hk _).2
    have hm := Real.rpow_nonneg (mul_nonneg hA hL.le) C
    nlinarith [mul_le_mul_of_nonneg_left hn hm]
  · have : IsEmpty I := not_nonempty_iff.mp hI
    simp only [Fintype.sum_empty, mul_zero] at hn hsum ⊢
    have hq : 0 ≤ ∑ j, (r j*x)^(1-C) := Finset.sum_nonneg fun j _ =>
      Real.rpow_nonneg (mul_nonneg (hr j) hx'.le) _
    have hz := le_antisymm hn hq
    rw [hz]
    simp

/-- Sum the weights whose endpoint is a given node. `none` is the boundary. -/
noncomputable def atEnd {V E : Type*} [Fintype E] [DecidableEq V]
    (endpoint : E → Option V) (weight : E → ℝ) (v : Option V) : ℝ :=
  ∑ e, if endpoint e = v then weight e else 0

private theorem partition {V E : Type*} [Fintype V] [Fintype E] [DecidableEq V]
    (endpoint : E → Option V) (weight : E → ℝ) :
    (∑ v : V, atEnd endpoint weight (some v)) + atEnd endpoint weight none = ∑ e, weight e := by
  classical
  unfold atEnd
  rw [Finset.sum_comm, ← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro e _
  cases he : endpoint e with
  | none => simp
  | some v => simp

/-- Directed edges use the same virtual rank at their two ends. Each edge
    is counted once at each end even when the forest has holes. -/
theorem finite_flow {V E : Type*} [Fintype V] [Fintype E] [DecidableEq V]
    (src dst : E → Option V) (weight : E → ℝ)
    (fringe : V → ℝ) {M stop : ℝ} (hM : 0 ≤ M)
    (node : ∀ v, fringe v + M * atEnd src weight (some v) ≤
      M * atEnd dst weight (some v))
    (terminal : stop ≤ M * atEnd dst weight none) :
    (∑ v, fringe v) + stop ≤ M * atEnd src weight none := by
  have h := Finset.sum_le_sum (s := Finset.univ) (fun v _ => node v)
  simp only [Finset.sum_add_distrib, ← Finset.mul_sum] at h
  have hi := partition dst weight
  have ho := partition src weight
  linarith [mul_le_mul_of_nonneg_left (le_of_eq (hi.trans ho.symm)) hM]

/-- Price one source at its actual period. The factor `scale` accounts for the
    reduction from virtual columns to complete physical columns. -/
theorem period_price {u v s X q scale C : ℝ} (hu : 0 < u) (hv : 0 < v)
    (hX : 0 < X) (hq : 0 ≤ q) (hscale : 0 ≤ scale) (hC : 0 ≤ C)
    (hentry : u ≤ X*v) (hphysical : scale*v ≤ s) (hperiod : q*s ≤ 2*u) :
    scale*q*v^(1-C) ≤ 2*X^C*u^(1-C) := by
  have hvp := Real.rpow_nonneg hv.le (1-C)
  have hXp := Real.rpow_nonneg hX.le C
  have hs := Real.rpow_le_rpow hu.le hentry hC
  rw [Real.mul_rpow hX.le hv.le] at hs
  have hcomb : u^C * v^(1-C) ≤ X^C * v := by
    calc
      _ ≤ (X^C*v^C)*v^(1-C) := mul_le_mul_of_nonneg_right hs hvp
      _ = _ := by rw [mul_assoc, powers_recombine hv]
  have hreal : q*(scale*v) ≤ 2*u :=
    (mul_le_mul_of_nonneg_left hphysical hq).trans hperiod
  have hm : u^C*(scale*q*v^(1-C)) ≤ u^C*(2*X^C*u^(1-C)) := by
    calc
      _ = (scale*q)*(u^C*v^(1-C)) := by ring
      _ ≤ (scale*q)*(X^C*v) := mul_le_mul_of_nonneg_left hcomb (mul_nonneg hscale hq)
      _ = X^C*(q*(scale*v)) := by ring
      _ ≤ X^C*(2*u) := mul_le_mul_of_nonneg_left hreal hXp
      _ = _ := by conv_lhs => rw [← powers_recombine (C := C) hu]
                  ring
  exact (mul_le_mul_iff_right₀ (Real.rpow_pos_of_pos hu C)).mp hm

/-- Divide only by returned independent owners. The common lane multiplicity
    includes the calls on zero fields and the completed period at each source. -/
theorem normalized_flow {V E : Type*} [Fintype V] [Fintype E] [DecidableEq V]
    (src dst : E → Option V) (weight shares : E → ℝ) (fringe : V → ℝ)
    {M Q stop lanes B pad : ℝ} (hM : 0 ≤ M) (hQ : 0 ≤ Q)
    (hlanes : 0 ≤ lanes) (hB : 0 < B)
    (node : ∀ v, fringe v + M * atEnd src weight (some v) ≤
      M * atEnd dst weight (some v))
    (terminal : stop ≤ M * atEnd dst weight none)
    (source : ∀ e, src e = none → weight e ≤ Q*shares e)
    (owners : lanes*atEnd src shares none ≤ pad*B) :
    (lanes*((∑ v, fringe v) + stop))/B ≤ pad*M*Q := by
  have hs : atEnd src weight none ≤ Q*atEnd src shares none := by
    simp only [atEnd, Finset.mul_sum]
    apply Finset.sum_le_sum
    intro e _
    by_cases he : src e = none
    · simpa [he] using source e he
    · simp [he]
  have hp := (finite_flow src dst weight fringe hM node terminal).trans
    (mul_le_mul_of_nonneg_left hs hM)
  rw [div_le_iff₀ hB]
  calc
    _ ≤ lanes*(M*(Q*atEnd src shares none)) := mul_le_mul_of_nonneg_left hp hlanes
    _ = (M*Q)*(lanes*atEnd src shares none) := by ring
    _ ≤ (M*Q)*(pad*B) := mul_le_mul_of_nonneg_left owners (mul_nonneg hM hQ)
    _ = _ := by ring


/- The row-reserve argument below generalizes PR 7981 to a variable atom exponent. -/
private theorem depth_growth {eta z : ℝ} (hη : eta ≤ 1/2) (hz : 0 ≤ z) :
    1+z/4 ≤ (2:ℝ)^((1-eta)*z) := by
  have h := Real.one_sub_inv_le_log_of_pos (by norm_num : (0:ℝ)<2)
  have hl : (1:ℝ)/2 ≤ Real.log 2 := by linarith
  have he := Real.add_one_le_exp (Real.log 2*((1-eta)*z))
  rw [Real.rpow_def_of_pos (by norm_num : (0:ℝ)<2)]
  have hη' : (1:ℝ)/2 ≤ 1-eta := by linarith
  have hprod := mul_le_mul hl hη' (by norm_num : (0:ℝ) ≤ 1/2)
      (le_trans (by norm_num) hl)
  nlinarith [mul_le_mul_of_nonneg_right hprod hz]

/-- Charge one stage's complete row reserve, also when the caller is suspended. -/
theorem stage_reserve {eta h cut t n k : ℝ} (heta : 0 ≤ eta) (hη : eta ≤ 1/2)
    (hh : 1 ≤ h) (hc : cut ≤ 3*h) (entered : cut ≤ t) (hn : 1 ≤ n)
    (nonnegative : 0 ≤ t)
    (first : (2:ℝ)^64 * n^2 ≤ (2:ℝ)^((1-eta)*cut))
    (bill : k ≤ 1+6*(3+t/h)*n^2*(2:ℝ)^(eta*t)) :
    k < (2:ℝ)^t/64 := by
  have hd' := depth_growth hη (sub_nonneg.mpr entered)
  set D := (2:ℝ)^((1-eta)*(t-cut))
  have hd : 1 ≤ D := (by linarith : (1:ℝ) ≤ 1+(t-cut)/4).trans hd'
  have hcut : cut/h ≤ 3 := (div_le_iff₀ (by linarith : 0 < h)).mpr hc
  have hrem : (t-cut)/h ≤ t-cut :=
    div_le_self (sub_nonneg.mpr entered) hh
  have hsum : 3+t/h ≤ 6*D := by
    rw [show t/h = cut/h+(t-cut)/h by ring]
    dsimp [D] at *
    linarith
  have hp : 1 ≤ (2:ℝ)^(eta*t) :=
    Real.one_le_rpow (by norm_num) (mul_nonneg heta nonnegative)
  have prod : 1 ≤ n^2 * D * (2:ℝ)^(eta*t) :=
    one_le_mul_of_one_le_of_one_le
      (one_le_mul_of_one_le_of_one_le (one_le_pow₀ hn) hd) hp
  have iden : (2:ℝ)^((1-eta)*cut) * (D * 2^(eta*t)) = 2^t := by
    dsimp [D]
    rw [← Real.rpow_add (by norm_num : (0:ℝ)<2),
        ← Real.rpow_add (by norm_num : (0:ℝ)<2)]
    congr 1
    ring
  have room := mul_le_mul_of_nonneg_right first
    (mul_nonneg (le_trans (by norm_num) hd) (le_trans (by norm_num) hp))
  rw [iden] at room
  have tariff := mul_le_mul_of_nonneg_right hsum
    (mul_nonneg (sq_nonneg n) (le_trans (by norm_num) hp))
  norm_num at room
  nlinarith

/-- The producer's projector exchanges act on arbitrary additive address
    groups. The two operated coordinates can each be a whole product module. -/
def exchange {M : Type*} [AddCommGroup M] (p : M →+ M) (a : M × M) : M × M :=
  (a.1 + p (a.2-a.1), a.2 - p (a.2-a.1))

def weighted {M : Type*} [AddCommGroup M] (A : M ≃+ M) (p : M →+ M)
    (a : M × M) : M × M :=
  let b := exchange p (A.symm a.1, a.2)
  (A b.1, b.2)

theorem nested_exchange {M : Type*} [AddCommGroup M] (p q : M →+ M)
    (nested : ∀ z, p (q z) = p z) (a : M × M) :
    exchange p (exchange q a) = exchange (q-p) a := by
  obtain ⟨x, y⟩ := a
  apply Prod.ext
  · simp [exchange, map_sub, nested]
    abel
  · simp [exchange, map_sub, nested]
    abel

theorem weighted_nested {M : Type*} [AddCommGroup M] (A : M ≃+ M) (p q : M →+ M)
    (nested : ∀ z, p (q z) = p z) (a : M × M) :
    weighted A p (weighted A q a) = weighted A (q-p) a := by
  obtain ⟨x, y⟩ := a
  unfold weighted
  simp only [AddEquiv.symm_apply_apply, Prod.mk.eta, nested_exchange p q nested]


#print axioms weighted_nested
#print axioms stage_reserve
#print axioms interface_fringe
#print axioms source_columns
#print axioms port_allowance
#print axioms terminal_allowance
#print axioms local_charge
#print axioms finite_flow
#print axioms period_price
#print axioms normalized_flow

/-- A high positive rank can pay an adjacent negative rank at every larger moment. -/
theorem paired_high_monotone {a b s t : ℝ} (ha : 1 ≤ a) (hab : a ≤ b)
    (hs : 0 ≤ s) (hst : s ≤ t) : b ^ s - a ^ s ≤ b ^ t - a ^ t := by
  have hst' : 0 ≤ t - s := by linarith
  have a0 : 0 < a := by linarith
  have b0 : 0 < b := by linarith
  have m₁ := Real.rpow_le_rpow a0.le hab hs
  have m₂ := sub_le_sub_right (Real.rpow_le_rpow a0.le hab hst') 1
  have prod := mul_le_mul m₁ m₂ (sub_nonneg.mpr (Real.one_le_rpow ha hst'))
    (Real.rpow_nonneg b0.le s)
  have eq : s + (t - s) = t := by ring
  have ea := Real.rpow_add a0 s (t-s)
  have eb := Real.rpow_add b0 s (t-s)
  rw [eq] at ea eb
  linarith only [prod, ea, eb]

/-- With the stated raw crossing even the five-bit-only invoice needs this rank. -/
theorem outer_five_bit_floor {H : ℕ} {b c : ℝ}
    (raw : c ≤ 38901152866 / (10:ℝ)^13) (rate : 389011527145 / (10:ℝ)^14 ≤ b)
    (bill : 5 < (c-b)*H) : 330033003301 ≤ H := by
  by_contra! h
  have hz : (H : ℝ) ≤ 330033003300 := by exact_mod_cast (show H ≤ 330033003300 by omega)
  have step := mul_le_mul_of_nonneg_right (sub_le_sub raw rate) (Nat.cast_nonneg (α := ℝ) H)
  norm_num at step
  linarith only [hz, step, bill]

/-- The actual integral invoice at the installed ordinary rate has a stronger floor. -/
theorem installed_nineteen_bit_floor {H : ℕ}
    (bill : 19 < (17108907955/(2:ℝ)^42 - 3890115271496/(10:ℝ)^15)*H) :
    1455682013917 ≤ H := by
  by_contra! h
  have hz : (H : ℝ) ≤ 1455682013916 :=
    by exact_mod_cast (show H ≤ 1455682013916 by omega)
  norm_num at bill
  linarith only [hz, bill]

#print axioms paired_high_monotone
#print axioms outer_five_bit_floor
#print axioms installed_nineteen_bit_floor

end BandFlow
