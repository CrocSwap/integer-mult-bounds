/-
Bridge7761F2 (lane LEAN-BRIDGE3, Nov 18).  Mass totals of #7761 by O(1)-lookup encodings:
chart heights are packed base 16 into one Nat (`pkH`), looked up by `/` and `%` (GMP in the kernel), banks/fields are folded with `zs`
(one pass, tail recursive).  Kernel-checked:  D7761 : model.D = 56,  A7761 : model.A = 9721,  climb7761 : model.climb = 9665,
X7761 : model.X = 2*56 (via flow7761 from Bridge7761F1).  Kernel only.
-/
import Nov15.Bridge7761F1
namespace Bridge7761
open Finset

def pk : List ℕ → ℕ
  | [] => 0
  | x :: l => x + 16 * pk l

theorem pk_get (l : List ℕ) (hl : ∀ x ∈ l, x < 16) (i : ℕ) : (pk l / 16 ^ i) % 16 = l.getD i 0 := by
  induction l generalizing i with
  | nil => simp [pk]
  | cons x l ih =>
    have hx := hl x List.mem_cons_self
    have ih' := ih (fun y hy => hl y (List.mem_cons_of_mem _ hy))
    cases i with
    | zero => simp [pk]; omega
    | succ i =>
      have : (pk (x :: l)) / 16 ^ (i + 1) = pk l / 16 ^ i := by
        rw [pow_succ', ← Nat.div_div_eq_div_mul]
        have e : pk (x :: l) / 16 = pk l := by simp only [pk]; omega
        rw [e]
      rw [this, ih']; simp

def lensL : List ℕ := chBasis.map List.length
def HT : ℕ := pk lensL

theorem lens_lt : ∀ x ∈ lensL, x < 16 := by decide +kernel
theorem lens_len : lensL.length = 1099 := by decide +kernel

def hp (x : ℕ) : ℤ := (((HT / 16 ^ (x % 1099)) % 16 : ℕ) : ℤ)

theorem getD_map_len : ∀ (l : List (List ℕ)) (n : ℕ), (l.map List.length).getD n 0 = (l.getD n []).length := by
  intro l
  induction l with
  | nil => intro n; simp
  | cons a l ih =>
    intro n; cases n with
    | zero => simp
    | succ m => simp only [List.map_cons, List.getD_cons_succ]; exact ih m

theorem hp_eq (x : ℕ) : hgt (x % 1099) = hp x := by
  unfold hp hgt HT
  rw [pk_get lensL lens_lt]
  unfold lensL
  have : (chBasis.map List.length).getD (x % 1099) 0 = (chBasis.getD (x % 1099) []).length :=
    getD_map_len chBasis _
  rw [this]

def zs (g : ℕ → ℕ → ℤ) : ℤ → List ℕ → List ℕ → ℤ
  | acc, a :: S, b :: T => zs g (acc + g a b) S T
  | acc, _, _ => acc

theorem zs_eq (g : ℕ → ℕ → ℤ) : ∀ (S T : List ℕ) (acc : ℤ), S.length = T.length →
    zs g acc S T = acc + ∑ i ∈ range S.length, g (S.getD i 0) (T.getD i 0) := by
  intro S
  induction S with
  | nil => intro T acc _; simp [zs]
  | cons a S ih =>
    intro T acc h
    cases T with
    | nil => simp at h
    | cons b T =>
      have h' : S.length = T.length := by simpa using h
      simp only [zs, ih T _ h', List.length_cons, Finset.sum_range_succ' _ S.length, List.getD_cons_succ, List.getD_cons_zero]
      ring

theorem len_eq_banks : bS.length = bT.length := by rw [len_bS, len_bT]
theorem len_eq_fields : fA.length = fB.length := by rw [len_fA, len_fB]

theorem dl_eq (i : ℕ) : dl i = hp (bT.getD i 0) - hp (bS.getD i 0) := by
  unfold dl; rw [hp_eq, hp_eq]

theorem D_sum : ∑ i ∈ range 5746, max (-(dl i)) 0 =
    ∑ i ∈ range bS.length, (fun s t => max (hp s - hp t) 0) (bS.getD i 0) (bT.getD i 0) := by
  rw [len_bS]; refine Finset.sum_congr rfl fun i _ => ?_
  rw [dl_eq]; simp only [neg_sub]

theorem A_sum : ∑ i ∈ range 5746, max (dl i) 0 =
    ∑ i ∈ range bS.length, (fun s t => max (hp t - hp s) 0) (bS.getD i 0) (bT.getD i 0) := by
  rw [len_bS]; refine Finset.sum_congr rfl fun i _ => ?_
  rw [dl_eq]

theorem zs_append (g : ℕ → ℕ → ℤ) : ∀ (S1 T1 S2 T2 : List ℕ) (acc : ℤ), S1.length = T1.length →
    zs g acc (S1 ++ S2) (T1 ++ T2) = zs g (zs g acc S1 T1) S2 T2 := by
  intro S1
  induction S1 with
  | nil => intro T1 S2 T2 acc h; cases T1 <;> simp_all [zs]
  | cons a S ih =>
    intro T1 S2 T2 acc h
    cases T1 with
    | nil => simp at h
    | cons b T => simp only [List.cons_append, zs]; exact ih T S2 T2 _ (by simpa using h)

theorem lenT0 : bT0.length = 1500 := by decide +kernel
theorem lenT1 : bT1.length = 1500 := by decide +kernel
theorem lenT2 : bT2.length = 1500 := by decide +kernel
theorem lenS0 : bS0.length = 1500 := by decide +kernel
theorem lenS1 : bS1.length = 1500 := by decide +kernel
theorem lenS2 : bS2.length = 1500 := by decide +kernel

theorem zs_banks (g : ℕ → ℕ → ℤ) (acc : ℤ) :
    zs g acc bS bT = zs g (zs g (zs g (zs g acc bS0 bT0) bS1 bT1) bS2 bT2) bS3 bT3 := by
  have h0 : bS0.length = bT0.length := by rw [lenS0, lenT0]
  have h01 : (bS0 ++ bS1).length = (bT0 ++ bT1).length := by simp [lenS0, lenS1, lenT0, lenT1]
  have h012 : (bS0 ++ bS1 ++ bS2).length = (bT0 ++ bT1 ++ bT2).length := by
    simp [lenS0, lenS1, lenS2, lenT0, lenT1, lenT2]
  unfold bS bT
  rw [zs_append g _ _ bS3 bT3 acc h012, zs_append g _ _ bS2 bT2 acc h01, zs_append g _ _ bS1 bT1 acc h0]

theorem zD0 : zs (fun s t => max (hp s - hp t) 0) 0 bS0 bT0 = 0 := by decide +kernel
theorem zD1 : zs (fun s t => max (hp s - hp t) 0) 0 bS1 bT1 = 0 := by decide +kernel
theorem zD2 : zs (fun s t => max (hp s - hp t) 0) 0 bS2 bT2 = 20 := by decide +kernel
theorem zD3 : zs (fun s t => max (hp s - hp t) 0) 20 bS3 bT3 = 56 := by decide +kernel
theorem zD : zs (fun s t => max (hp s - hp t) 0) 0 bS bT = 56 := by
  rw [zs_banks, zD0, zD1, zD2, zD3]
theorem zA0 : zs (fun s t => max (hp t - hp s) 0) 0 bS0 bT0 = 2442 := by decide +kernel
theorem zA1 : zs (fun s t => max (hp t - hp s) 0) 2442 bS1 bT1 = 5109 := by decide +kernel
theorem zA2 : zs (fun s t => max (hp t - hp s) 0) 5109 bS2 bT2 = 7960 := by decide +kernel
theorem zA3 : zs (fun s t => max (hp t - hp s) 0) 7960 bS3 bT3 = 9721 := by decide +kernel
theorem zA : zs (fun s t => max (hp t - hp s) 0) 0 bS bT = 9721 := by
  rw [zs_banks, zA0, zA1, zA2, zA3]
theorem zC : zs (fun s t => hp t - hp s) 0 fA fB = 9665 := by decide +kernel

theorem D7761 : model.D = 56 := by
  rw [D_eq, D_sum]
  have := zs_eq (fun s t => max (hp s - hp t) 0) bS bT 0 len_eq_banks
  rw [zD, zero_add] at this; exact this.symm
theorem A7761 : model.A = 9721 := by
  rw [A_eq, A_sum]
  have := zs_eq (fun s t => max (hp t - hp s) 0) bS bT 0 len_eq_banks
  rw [zA, zero_add] at this; exact this.symm

theorem climb7761 : model.climb = 9665 := by
  unfold XBal.Model.climb
  have h1 : ∀ i : Fin 1262, model.h (model.fin i) - model.h (model.ini i)
      = hp (fB.getD i 0) - hp (fA.getD i 0) := by
    intro i
    show hgt (fB.getD i 0 % 1099) - hgt (fA.getD i 0 % 1099) = _
    rw [hp_eq, hp_eq]
  rw [Finset.sum_congr rfl (fun i _ => h1 i),
    Fin.sum_univ_eq_sum_range (fun i => hp (fB.getD i 0) - hp (fA.getD i 0)) 1262]
  have := zs_eq (fun s t => hp t - hp s) fA fB 0 len_eq_fields
  rw [zC, len_fA, zero_add] at this
  exact this.symm

theorem X7761 : model.X = 2 * 56 := X_of_flow_D flow7761 D7761

end Bridge7761
