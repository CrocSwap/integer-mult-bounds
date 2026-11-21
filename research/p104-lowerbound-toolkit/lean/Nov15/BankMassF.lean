/-
BankMassF (lane S-MASSF, Nov 18).  The 'mass -> F' pricing step of the banked ladder, kernel only.
(1) mass_price: if for every window length L the banked d-mass M_L = sum_k min(L,D_k) is at least the field mass
    sum_f min(L,D_f) plus an extra X for every L > m, then for ANY concave nondecreasing price g (g 0 = 0)
        sum_k g(D_k) >= sum_f g(D_f) + X * (g(m+1) - g m).
    (concavity handled by the min(L,.) decomposition BankNC0a.decomp; sum_{L>m} c_L = g(m+1)-g(m) is the
     'c_infty + c_L terms' accounting; X*(g9-g8) of the certificates is the case m = 8.)
(2) net_mass_price: for a Net with nonzero principal minors the L <= m masses come from BankNC0c.perL (no premise);
    the premise left is exactly the extra mass at L > m (P-CUTMASS, hE).
(3) rpow price: g d = d^s, s in (0,1] is concave nondecreasing with g 0 = 0 (rpow_price), so for 16 calls with 400
    fields climbing 8:  16*(400*8^s + X*(9^s-8^s)) <= total banked paid (call_price).
(4) no_cross: if the caller invoice I(s) dominates that paid cost then I s - 16*(400*8^s+X*(9^s-8^s)) >= 0, i.e. the
    BankFlagCert F (= FceilBank, same shape, I s = cdat s TB - cdat s PB) cannot be < 0: the cert refutes the premise.
NOTE: Phi_t/t-at-t->0 / f = g - eps d conversion is NOT needed here: the price is d^s itself, concave for every s in (0,1].
-/
import Nov15.BankNC0c
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Analysis.Convex.SpecificFunctions.Pow

namespace BankMassF
open Finset BankNC0

theorem sum_g_eq (H : ℕ) (g : ℕ → ℝ) (c : ℕ → ℝ)
    (hg : ∀ d, d ≤ H → g d = ∑ L ∈ Icc 1 H, c L * (min L d : ℕ))
    {X : Type} [Fintype X] (D : X → ℕ) (hD : ∀ x, D x ≤ H) :
    ∑ x, g (D x) = ∑ L ∈ Icc 1 H, c L * ((∑ x, min L (D x) : ℕ) : ℝ) := by
  simp_rw [fun x => hg (D x) (hD x)]
  rw [Finset.sum_comm]
  refine Finset.sum_congr rfl (fun L _ => ?_)
  push_cast; rw [Finset.mul_sum]

theorem mass_price {Fld Bank : Type} [Fintype Fld] [Fintype Bank]
    (H m : ℕ) (hm : m < H) (g : ℕ → ℝ) (g0 : g 0 = 0)
    (hmono : ∀ j, j < H → g j ≤ g (j+1))
    (hconc : ∀ j, j + 1 < H → g (j+2) - g (j+1) ≤ g (j+1) - g j)
    (Df : Fld → ℕ) (Dk : Bank → ℕ) (hf : ∀ f, Df f ≤ H) (hk : ∀ k, Dk k ≤ H) (X : ℝ)
    (hM : ∀ L ∈ Icc 1 H, ((∑ f, min L (Df f) : ℕ) : ℝ) + (if m < L then X else 0)
            ≤ ((∑ k, min L (Dk k) : ℕ) : ℝ)) :
    ∑ f, g (Df f) + X * (g (m+1) - g m) ≤ ∑ k, g (Dk k) := by
  obtain ⟨c, hc, hg⟩ := decomp H g g0 hmono hconc
  have hslope : g (m+1) - g m = ∑ L ∈ Icc 1 H, c L * (if m < L then (1:ℝ) else 0) := by
    rw [hg (m+1) (by omega), hg m (by omega), ← Finset.sum_sub_distrib]
    refine Finset.sum_congr rfl (fun L _ => ?_)
    by_cases h : m < L
    · have e1 : min L (m+1) = m+1 := by omega
      have e2 : min L m = m := by omega
      rw [e1, e2]; simp [h]; ring
    · have e1 : min L (m+1) = L := by omega
      have e2 : min L m = L := by omega
      rw [e1, e2]; simp [h]
  rw [sum_g_eq H g c hg Df hf, sum_g_eq H g c hg Dk hk, hslope, Finset.mul_sum]
  rw [← Finset.sum_add_distrib]
  refine Finset.sum_le_sum (fun L hL => ?_)
  have := mul_le_mul_of_nonneg_left (hM L hL) (hc L)
  have e : c L * (((∑ f, min L (Df f) : ℕ) : ℝ) + (if m < L then X else 0))
      = c L * ((∑ f, min L (Df f) : ℕ) : ℝ) + X * (c L * (if m < L then (1:ℝ) else 0)) := by
    by_cases h : m < L <;> simp [h] <;> ring
  linarith

variable {K : Type} {Chart Fld Bank : Type} [Field K] [Fintype Fld] [DecidableEq Fld]
  [Fintype Bank] [LinearOrder Bank]

/-- banked network: paid >= g(|dh|) per bank, nonzero minors; extra mass X at every L > m (P-CUTMASS) gives
    paid >= sum_f g(climb_f) + X (g(m+1) - g m). -/
theorem net_mass_price (N : Net K Chart Fld Bank)
    (hminor : ∀ C : Finset Fld,
      (N.O.submatrix (fun c : C => (c : Fld)) (fun c : C => (c : Fld))).det ≠ 0)
    (h : Chart → ℕ) (H m : ℕ) (hm : m < H) (hH : ∀ c, h c ≤ H)
    (g : ℕ → ℝ) (g0 : g 0 = 0) (hmono : ∀ j, j < H → g j ≤ g (j+1))
    (hconc : ∀ j, j + 1 < H → g (j+2) - g (j+1) ≤ g (j+1) - g j)
    (paid : Bank → ℝ) (hpaid : ∀ k, g (dh (h (N.src k)) (h (N.dst k))) ≤ paid k)
    (X : ℝ)
    (hE : ∀ L, m < L → L ≤ H →
      ((∑ f, min L (dh (h (N.A f)) (h (N.B f))) : ℕ) : ℝ) + X
        ≤ ((∑ k, min L (dh (h (N.src k)) (h (N.dst k))) : ℕ) : ℝ)) :
    ∑ f, g (dh (h (N.A f)) (h (N.B f))) + X * (g (m+1) - g m) ≤ ∑ k, paid k := by
  have hd : ∀ i j, i ≤ H → j ≤ H → dh i j ≤ H := by intro i j hi hj; unfold dh; omega
  refine le_trans (mass_price H m hm g g0 hmono hconc _ _
    (fun f => hd _ _ (hH _) (hH _)) (fun k => hd _ _ (hH _) (hH _)) X ?_)
    (Finset.sum_le_sum (fun k _ => hpaid k))
  intro L hL
  have hL' := Finset.mem_Icc.mp hL
  by_cases hmL : m < L
  · simpa [hmL] using hE L hmL hL'.2
  · simp only [hmL, if_false, add_zero]
    exact_mod_cast perL N hminor h H hH L

/-- the rpow price d^s, s in (0,1], is a concave nondecreasing price on ℕ with g 0 = 0 -/
theorem rpow_price {s : ℝ} (hs0 : 0 < s) (hs1 : s ≤ 1) (H : ℕ) :
    (fun d : ℕ => (d : ℝ) ^ s) 0 = 0 ∧
    (∀ j, j < H → (j : ℝ) ^ s ≤ ((j+1 : ℕ) : ℝ) ^ s) ∧
    (∀ j, j + 1 < H → ((j+2 : ℕ) : ℝ) ^ s - ((j+1 : ℕ) : ℝ) ^ s ≤ ((j+1 : ℕ) : ℝ) ^ s - (j : ℝ) ^ s) := by
  refine ⟨by simp [Real.zero_rpow hs0.ne'], fun j _ => ?_, fun j _ => ?_⟩
  · exact Real.rpow_le_rpow (Nat.cast_nonneg _) (by push_cast; linarith) hs0.le
  · have hc := (Real.concaveOn_rpow hs0.le hs1).2
      (Set.mem_Ici.mpr (Nat.cast_nonneg (α := ℝ) j)) (Set.mem_Ici.mpr (Nat.cast_nonneg (α := ℝ) (j+2)))
      (show (0:ℝ) ≤ 1/2 by norm_num) (show (0:ℝ) ≤ 1/2 by norm_num) (show (1/2:ℝ) + 1/2 = 1 by norm_num)
    simp only [smul_eq_mul] at hc
    have e : (1/2 : ℝ) * (j : ℝ) + 1/2 * ((j+2 : ℕ) : ℝ) = ((j+1 : ℕ) : ℝ) := by push_cast; ring
    rw [e] at hc
    linarith

/-- 16 calls, 400 fields climbing exactly 8 each, extra mass X above window 8: the total banked paid cost is at
    least 16*(400*8^s + X*(9^s-8^s)).  Per-call hypotheses are the Net data (index `i`). -/
theorem call_price {s : ℝ} (hs0 : 0 < s) (hs1 : s ≤ 1) (H : ℕ) (hH9 : 9 ≤ H) (X : ℝ)
    {Call : Type} [Fintype Call] (ncalls : ℕ) (hcalls : Fintype.card Call = ncalls)
    (Df : Call → Fld → ℕ) (hDf : ∀ i f, Df i f = 8) (hcard : Fintype.card Fld = 400)
    (Dk : Call → Bank → ℕ) (hk : ∀ i k, Dk i k ≤ H) (paid : Call → ℝ)
    (hpaid : ∀ i, ∑ k, (Dk i k : ℝ) ^ s ≤ paid i)
    (hE : ∀ i, ∀ L, 8 < L → L ≤ H →
      ((∑ f, min L (Df i f) : ℕ) : ℝ) + X ≤ ((∑ k, min L (Dk i k) : ℕ) : ℝ))
    (hB : ∀ i, ∀ L, L ≤ 8 → ((∑ f, min L (Df i f) : ℕ) : ℝ) ≤ ((∑ k, min L (Dk i k) : ℕ) : ℝ)) :
    (ncalls : ℝ) * (400 * (8:ℝ) ^ s + X * ((9:ℝ) ^ s - (8:ℝ) ^ s)) ≤ ∑ i, paid i := by
  obtain ⟨p0, pm, pc⟩ := rpow_price hs0 hs1 H
  have each : ∀ i, 400 * (8:ℝ) ^ s + X * ((9:ℝ) ^ s - (8:ℝ) ^ s) ≤ paid i := by
    intro i
    have := mass_price (Fld := Fld) (Bank := Bank) H 8 (by omega) (fun d : ℕ => (d : ℝ) ^ s) p0 pm pc
      (Df i) (Dk i) (fun f => by rw [hDf]; omega) (hk i) X (by
        intro L hL
        have hL' := Finset.mem_Icc.mp hL
        by_cases h8 : 8 < L
        · simpa [h8] using hE i L h8 hL'.2
        · simpa [h8] using hB i L (by omega))
    have e1 : ∑ f, ((Df i f : ℕ) : ℝ) ^ s = 400 * (8:ℝ) ^ s := by
      simp only [hDf]; simp [Finset.sum_const, Finset.card_univ, hcard]
    have e2 : ((8 + 1 : ℕ) : ℝ) = 9 := by norm_num
    have e3 : ((8 : ℕ) : ℝ) = 8 := by norm_num
    rw [e2, e3] at this
    simp only [e1] at this
    linarith [hpaid i]
  calc (ncalls : ℝ) * (400 * (8:ℝ) ^ s + X * ((9:ℝ) ^ s - (8:ℝ) ^ s))
      = ∑ _i : Call, (400 * (8:ℝ) ^ s + X * ((9:ℝ) ^ s - (8:ℝ) ^ s)) := by
        simp [Finset.sum_const, Finset.card_univ, hcalls]; ring
    _ ≤ ∑ i, paid i := Finset.sum_le_sum (fun i _ => each i)

/-- the certificate link: the BankFlagCert integrand F = I - 16*(400*8^s + X*(9^s-8^s)) is >= 0 as soon as the
    caller invoice I (= cdat s TB - cdat s PB) dominates the banked paid cost; Cert (F < 0) refutes the premise. -/
theorem no_cross (I : ℝ) (X s : ℝ) (P : ℝ)
    (hmass : 16 * (400 * (8:ℝ) ^ s + X * ((9:ℝ) ^ s - (8:ℝ) ^ s)) ≤ P) (hinv : P ≤ I) :
    ¬ (I - 16 * (400 * (8:ℝ) ^ s + 8 * ((9:ℝ) ^ s - (8:ℝ) ^ s)) < 0 ∧ X = 8) := by
  rintro ⟨h, rfl⟩
  linarith

end BankMassF
#print axioms BankMassF.call_price
#print axioms BankMassF.net_mass_price
