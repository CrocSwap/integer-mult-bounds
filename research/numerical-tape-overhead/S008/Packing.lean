import Mathlib.Data.Nat.Log
import S008.NumericalCutoff

namespace S008.Packing
open S008.NumericalCutoff

def digitWidth (n : ℕ) := Nat.clog 2 n
def digitCount (n : ℕ) := (n-1)/digitWidth n + 1
def addressWidth (n : ℕ) := Nat.clog 2 (4*digitCount n)
def paddedSize (n : ℕ) := 2^addressWidth n

private theorem square_below_length {b : ℕ} (hb : 8 ≤ b) : b^2 ≤ 2^(b-1) := by
  induction b, hb using Nat.le_induction with
  | base => decide
  | succ b hb ih =>
    have h1 : b-1+1 = b := by omega
    have he : 2^b = 2^(b-1)*2 := by rw [← pow_succ, h1]
    have hbig : 2*b+1 ≤ b^2 := by
      nlinarith [Nat.mul_le_mul_right b (by omega : 3≤b)]
    simp only [Nat.add_sub_cancel]
    rw [he]
    nlinarith

theorem physical_sizes {n : ℕ} (hn : 2^48 < n) :
    32 ≤ addressWidth n ∧ digitWidth n < 2*addressWidth n ∧
    paddedSize n < n ∧ paddedSize n*addressWidth n ≤ 8*n := by
  let b := digitWidth n
  let h := digitCount n
  let k := addressWidth n
  change 32 ≤ k ∧ b < 2*k ∧ 2^k < n ∧ 2^k*k ≤ 8*n
  have hb : 48 < b := (Nat.lt_clog_iff_pow_lt (by decide : 1<2)).2 hn
  have hbp : 0<b := by omega
  have hpre : 2^(b-1) < n := Nat.pow_pred_clog_lt_self (by decide : 1<2) (by omega)
  have hnB : n ≤ 2^b := Nat.le_pow_clog (by decide : 1<2) n
  have hbN : b ≤ n := (Nat.clog_le_iff_le_pow (by decide : 1<2)).2 (Nat.lt_two_pow_self.le)
  have h0 : h = (n-1)/b+1 := rfl
  have hp : 0<h := by rw [h0]; exact Nat.succ_pos _
  have hbottom : (h-1)*b < n := by
    rw [h0, Nat.add_sub_cancel]
    have hh := Nat.div_mul_le_self (n-1) b
    omega
  have htop : n ≤ h*b := by
    rw [h0, Nat.add_mul, Nat.one_mul]
    have hh := Nat.mod_add_div (n-1) b
    have hr := Nat.mod_lt (n-1) hbp
    rw [Nat.mul_comm b] at hh
    omega
  have hbSq := square_below_length (by omega : 8≤b)
  have hbh : b ≤ h := by
    by_contra! bad
    have := Nat.mul_lt_mul_of_pos_right bad hbp
    nlinarith
  have hk : 0<k := Nat.clog_pos (n:=4*h) (by decide : 1<2) (by omega)
  have hkhi : 4*h ≤ 2^k := Nat.le_pow_clog (by decide : 1<2) _
  have hklo : 2^(k-1)<4*h := Nat.pow_pred_clog_lt_self (x:=4*h) (by decide : 1<2) (by omega)
  have hkeq : 2^k=2^(k-1)*2 := by rw [← pow_succ, Nat.sub_add_cancel (by omega : 1≤k)]
  have hkvol : 2^k < 8*h := by omega
  have hp16 : 16*(h-1) ≤ (h-1)*b := by
    rw [Nat.mul_comm 16]
    exact Nat.mul_le_mul_left _ (by omega)
  have hless : 8*h ≤ n := by omega
  have hkBn : 2^k < n := lt_of_lt_of_le hkvol hless

  have hsmall : h ≤ 2^(k-1) := by omega
  have hsq : n ≤ (2^(k-1))^2 := by
    calc
      n ≤ h*b := htop
      _ ≤ h*h := Nat.mul_le_mul_left h hbh
      _ ≤ (2^(k-1))^2 := by simpa only [pow_two] using Nat.mul_le_mul hsmall hsmall
  rw [← pow_mul] at hsq
  have hb2 : b ≤ (k-1)*2 := (Nat.clog_le_iff_le_pow (by decide : 1<2)).2 hsq
  have h32 : 32≤k := by
    by_contra! bad
    have hpp := Nat.pow_le_pow_right (by decide : 0<2) (show k≤31 by omega)
    have hv : h ≤ 2^31 := by omega
    have hbb : b ≤ 62 := by omega
    have ha := Nat.mul_le_mul hv hbb
    omega
  have double : 2^b = 2^(b-1)*2 := by
    rw [← pow_succ, Nat.sub_add_cancel (by omega : 1≤b)]
  have hk' : k ≤ b-1 := (Nat.clog_le_iff_le_pow (by decide : 1<2)).2 (by omega)
  have hbody : h*(b-1) ≤ n := by
    have ha : (h-1)*b+b=h*b := by
      rw [← Nat.add_one_mul,Nat.sub_add_cancel (by omega : 1≤h)]
    have hc : h*(b-1)+h=h*b := by
      rw [← Nat.mul_add_one,Nat.sub_add_cancel (by omega : 1≤b)]
    omega
  refine ⟨h32, by omega, hkBn, ?_⟩
  calc
    2^k*k ≤ (8*h)*(b-1) := Nat.mul_le_mul hkvol.le hk'
    _ = 8*(h*(b-1)) := Nat.mul_assoc _ _ _
    _ ≤ 8*n := Nat.mul_le_mul_left _ hbody

end S008.Packing
