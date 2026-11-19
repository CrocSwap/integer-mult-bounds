/-
Bridge7761T1 .  Digit extraction from the packed bank forms of Bridge7761PG:
  bdig Q i              : balanced base-2^72 digit i of the integer Q (offset trick, Nat arithmetic);
  chkDig k              : sum_{i<256} bdig(Q_k,i) 2^(72 i) = Q_k  and  bk k < 2^70   (block 0 = columns 0..255, Q_k = QT0.get k);
  dig_extract           : chkDig k -> for g < 256:  D_k * dRec Recipe7761 k g = bdig (QT0.get k) g   (digits_zero + bound7761 + packed_blk).
Kernel only.
-/
import Nov15.Bridge7761PG

namespace Bridge7761
open Finset Module BankNC0 BridgeP

def CST : ℕ := 2 ^ 71 * ((2 ^ (72 * 256) - 1) / (2 ^ 72 - 1))

def bdig (Q : ℤ) (i : ℕ) : ℤ := (((Q + (CST : ℤ)).toNat / 2 ^ (72 * i)) % 2 ^ 72 : ℕ) - 2 ^ 71

theorem bdig_abs (Q : ℤ) (i : ℕ) : |bdig Q i| ≤ 2 ^ 71 := by
  unfold bdig
  have h := Nat.mod_lt ((Q + (CST : ℤ)).toNat / 2 ^ (72 * i)) (show 0 < 2 ^ 72 by positivity)
  have h1 : ((((Q + (CST : ℤ)).toNat / 2 ^ (72 * i)) % 2 ^ 72 : ℕ) : ℤ) < 2 ^ 72 := by exact_mod_cast h
  have h2 : (0 : ℤ) ≤ ((((Q + (CST : ℤ)).toNat / 2 ^ (72 * i)) % 2 ^ 72 : ℕ) : ℤ) := Int.natCast_nonneg _
  rw [abs_le]; constructor <;> linarith

theorem lsum_range (f : ℕ → ℤ) (n : ℕ) : ((List.range n).map f).sum = ∑ i ∈ range n, f i := by
  induction n with
  | zero => simp
  | succ n ih => rw [List.range_succ, List.map_append, List.sum_append, ih, Finset.sum_range_succ]; simp

def digSum (Q : ℤ) : ℤ := ((List.range 256).map fun i => bdig Q i * pw i).sum

noncomputable def chkDig (k : ℕ) : Bool := digSum (QT0.get k) == QT0.get k && decide (bk k < 2 ^ 70)

theorem pw_eq (e : ℕ) : pw e = ((2 : ℤ) ^ 72) ^ e := by
  unfold pw; push_cast; rw [pow_mul]; norm_num

theorem dig_extract (k : Fin 5746) (hchk : chkDig k.val = true) (g : Fin 1262) (hg : g.val < 256) :
    (dk k.val : ℚ) * dRec Recipe7761 k g = ((bdig (QT0.get k.val) g.val : ℤ) : ℚ) := by
  simp only [chkDig, Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq] at hchk
  obtain ⟨hsum, hbk⟩ := hchk
  have hI := bound7761 k
  choose z hz hzb using hI
  set v : ℕ → ℤ := fun i => if h : i < 1262 then z ⟨i, h⟩ else 0 with hv
  have hp := packed_blk 0 QT0 allC0 k
  have hE : ((∑ i ∈ range 256, v i * ((2 : ℤ) ^ 72) ^ i : ℤ) : ℚ) = ((QT0.get k.val : ℤ) : ℚ) := by
    rw [← hp, EB_apply]; push_cast
    rw [Finset.mul_sum]
    refine Finset.sum_congr rfl fun i _ => ?_
    simp only [hv, zero_add]
    split_ifs with h
    · rw [← hz ⟨i, h⟩]; norm_num <;> ring
    · simp
  have hE' : ∑ i ∈ range 256, v i * ((2 : ℤ) ^ 72) ^ i = QT0.get k.val := by exact_mod_cast hE
  have hW : ∑ i ∈ range 256, bdig (QT0.get k.val) i * ((2 : ℤ) ^ 72) ^ i = QT0.get k.val := by
    have : digSum (QT0.get k.val) = ∑ i ∈ range 256, bdig (QT0.get k.val) i * ((2 : ℤ) ^ 72) ^ i := by
      unfold digSum
      rw [lsum_range]
      exact Finset.sum_congr rfl fun i _ => by rw [pw_eq]
    rw [← this]; exact hsum
  have hz0 : ∀ i < 256, v i - bdig (QT0.get k.val) i = 0 := by
    have hs : ∑ i ∈ range 256, (v i - bdig (QT0.get k.val) i) * ((2 : ℤ) ^ 72) ^ i = 0 := by
      simp only [sub_mul, Finset.sum_sub_distrib, hE', hW, sub_self]
    refine digits_zero ((2 : ℤ) ^ 72) (by positivity) 256 (fun i => v i - bdig (QT0.get k.val) i) ?_ hs
    intro i _
    have h1 := bdig_abs (QT0.get k.val) i
    have h2 : |v i| ≤ (bk k.val : ℤ) := by
      simp only [hv]; split_ifs with h
      · exact hzb ⟨i, h⟩
      · simp
    have h3 : (bk k.val : ℤ) < 2 ^ 70 := by exact_mod_cast hbk
    calc |v i - bdig (QT0.get k.val) i| ≤ |v i| + |bdig (QT0.get k.val) i| := abs_sub _ _
      _ < 2 ^ 72 := by linarith
  have := hz0 g.val hg
  have hvg : v g.val = z g := by simp only [hv]; rw [dif_pos g.isLt]
  rw [hvg] at this
  rw [hz g]
  have : z g = bdig (QT0.get k.val) g.val := by linarith
  rw [this]

end Bridge7761
