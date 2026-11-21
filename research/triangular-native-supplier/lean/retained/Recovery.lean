import Mathlib.Analysis.Fourier.ZMod
import Mathlib.Algebra.Order.Round
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.NormNum

/-! Normalized Fourier recovery on the cyclic index of the original digit stream. -/
namespace MixedRankRecovery

open Finset
open scoped BigOperators ZMod

variable {S : ℕ} [NeZero S]
abbrev Signal (S : ℕ) := ZMod S → ℂ

noncomputable def cyclic (f g : Signal S) (k : ZMod S) : ℂ :=
  ∑ j : ZMod S, f j * g (k - j)

noncomputable def forward (u : (ZMod S)ˣ) (f : Signal S) (k : ZMod S) :=
  (S : ℂ)⁻¹ * ZMod.dft f (u.val * k)

noncomputable def opposite (u : (ZMod S)ˣ) (f : Signal S) (k : ZMod S) :=
  ZMod.dft.symm f (u.val * k)

theorem dft_cyclic (f g : Signal S) :
    ZMod.dft (cyclic f g) = fun k ↦ ZMod.dft f k * ZMod.dft g k := by
  classical
  funext k
  simp only [ZMod.dft_apply, smul_eq_mul, cyclic]
  rw [Finset.sum_mul]
  simp only [Finset.mul_sum]
  rw [sum_comm]
  apply sum_congr rfl
  intro j _

  refine Fintype.sum_equiv (Equiv.subRight j) _ _ (fun x ↦ ?_)
  simp only [Equiv.subRight_apply]
  have h : -(x * k) = -(j * k) + -((x-j)*k) := by ring
  rw [h, AddChar.map_add_eq_mul]
  ring

theorem exact_sandwich (u : (ZMod S)ˣ) (f g : Signal S) (k : ZMod S) :
    opposite u (fun j ↦ forward u f j * forward u g j) k =
      ((S : ℂ)⁻¹)^2 * cyclic f g k := by
  have hc : (fun j ↦ forward u f j * forward u g j) =
      ((S : ℂ)⁻¹)^2 • (fun j ↦ ZMod.dft (cyclic f g) (u.val * j)) := by
    funext j
    simp only [forward, dft_cyclic, Pi.smul_apply, smul_eq_mul]
    ring
  rw [hc, opposite, map_smul]
  simp only [Pi.smul_apply, smul_eq_mul, ZMod.invDFT_apply']
  rw [ZMod.dft_comp_unitMul, ← mul_neg, u.inv_mul_cancel_left, ZMod.dft_dft]
  simp [NeZero.ne (S : ℂ)]

private theorem mean_bound (a x : Signal S) (B : ℝ)
    (ha : ∀ j, ‖a j‖ = 1) (hx : ∀ j, ‖x j‖ ≤ B) :
    ‖(S : ℂ)⁻¹ * ∑ j, a j * x j‖ ≤ B := by
  have hs : ‖∑ j, a j * x j‖ ≤ ∑ _ : ZMod S, B := by
    refine (norm_sum_le _ _).trans (sum_le_sum fun j _ ↦ ?_)
    simpa [ha j] using hx j
  calc
    _ = (S : ℝ)⁻¹ * ‖∑ j, a j * x j‖ := by simp
    _ ≤ (S : ℝ)⁻¹ * ∑ _ : ZMod S, B :=
      mul_le_mul_of_nonneg_left hs (by positivity)
    _ = B := by simp [nsmul_eq_mul, ZMod.card, NeZero.ne (S : ℝ)]

theorem forward_bound (u : (ZMod S)ˣ) (x : Signal S) (B : ℝ)
    (hx : ∀ j, ‖x j‖ ≤ B) (k : ZMod S) : ‖forward u x k‖ ≤ B := by
  simp only [forward, ZMod.dft_apply, smul_eq_mul]
  apply mean_bound _ x B _ hx
  intro j
  simp [ZMod.stdAddChar_apply]

theorem opposite_error (u : (ZMod S)ˣ) (x y : Signal S) (e : ℝ)
    (h : ∀ j, ‖x j - y j‖ ≤ e) (k : ZMod S) :
    ‖opposite u x k - opposite u y k‖ ≤ e := by
  change ‖ZMod.dft.symm x _ - ZMod.dft.symm y _‖ ≤ e
  have hsub : ZMod.dft.symm x (u.val*k) - ZMod.dft.symm y (u.val*k) =
      ZMod.dft.symm (x-y) (u.val*k) := by simp
  rw [hsub, ZMod.invDFT_apply]
  simp only [smul_eq_mul]
  apply mean_bound _ (x-y) e _ h
  intro j
  simp [ZMod.stdAddChar_apply]

def disk (x : Signal S) (B : ℝ) : Prop := ∀ j, ‖x j‖ ≤ B

def packet (fw : Signal S → Signal S) (mul : ℂ → ℂ → ℂ) (f g : Signal S) : Signal S :=
  fun j ↦ mul (fw f j) (fw g j)

theorem product_error (u : (ZMod S)ˣ) (fw bw : Signal S → Signal S)
    (mul : ℂ → ℂ → ℂ) (e : ℝ) (he : 0 ≤ e) (he' : e ≤ 1/8)
    (hfw : ∀ x, disk x (1/2) → ∀ j, ‖fw x j - forward u x j‖ ≤ e)
    (hbw : ∀ x, disk x (1/2) → ∀ j, ‖bw x j - opposite u x j‖ ≤ e)
    (hm : ∀ a b, ‖a‖ ≤ 1/2 → ‖b‖ ≤ 1/2 → ‖mul a b - a*b‖ ≤ e)
    (f g : Signal S) (hf : disk f (1/4)) (hg : disk g (1/4)) (k : ZMod S) :
    ‖bw (packet fw mul f g) k - ((S : ℂ)⁻¹)^2 * cyclic f g k‖ ≤ 3*e := by
  have close (x : Signal S) (hx : disk x (1/4)) (j : ZMod S) :
      ‖fw x j - forward u x j‖ ≤ e :=
    hfw x (fun i ↦ (hx i).trans (by norm_num)) j
  have approx (x : Signal S) (hx : disk x (1/4)) (j : ZMod S) : ‖fw x j‖ ≤ 1/2 := by
    have ht := norm_le_insert' (fw x j) (forward u x j)
    linarith [close x hx j, forward_bound u x (1/4) hx j]
  have hp (j : ZMod S) := hm _ _ (approx f hf j) (approx g hg j)
  have hdom : disk (packet fw mul f g) (1/2) := by
    intro j
    have ht := norm_le_insert' (mul (fw f j) (fw g j)) (fw f j * fw g j)
    rw [norm_mul] at ht
    have hx := mul_le_mul (approx f hf j) (approx g hg j) (norm_nonneg _) (by norm_num)
    change ‖mul (fw f j) (fw g j)‖ ≤ 1/2
    linarith [hp j]
  let exactPoint : Signal S := fun j ↦ forward u f j * forward u g j
  have hpt (j : ZMod S) : ‖packet fw mul f g j - exactPoint j‖ ≤ 2*e := by
    have h1 := dist_triangle (packet fw mul f g j) (fw f j * fw g j) (exactPoint j)
    simp only [dist_eq_norm] at h1
    have hi : fw f j * fw g j - exactPoint j =
        (fw f j-forward u f j) * fw g j + forward u f j * (fw g j-forward u g j) := by
      dsimp [exactPoint]; ring
    have hh := norm_add_le ((fw f j-forward u f j)*fw g j)
                            (forward u f j*(fw g j-forward u g j))
    rw [hi] at h1
    simp only [norm_mul] at hh
    have h2 := mul_le_mul (close f hf j) (approx g hg j) (norm_nonneg _) he
    have h3 := mul_le_mul (forward_bound u f (1/4) hf j) (close g hg j) (norm_nonneg _) (by norm_num)
    have hr : ‖packet fw mul f g j - fw f j * fw g j‖ ≤ e := hp j
    linarith only [h1, hh, h2, h3, hr, he]
  rw [← exact_sandwich u f g k]
  have ht := dist_triangle (bw (packet fw mul f g) k) (opposite u (packet fw mul f g) k)
                  (opposite u exactPoint k)
  simp only [dist_eq_norm] at ht
  change ‖bw (packet fw mul f g) k - opposite u exactPoint k‖ ≤ 3*e
  linarith [hbw _ hdom k, opposite_error u _ _ _ hpt k]

def coefficient (a b : ZMod S → ℕ) (k : ZMod S) : ℕ :=
  ∑ j : ZMod S, a j * b (k-j)

noncomputable def digitInput (D : ℕ) (a : ZMod S → ℕ) : Signal S :=
  fun j ↦ (D : ℂ)⁻¹ * (a j : ℂ)

theorem remove_scales (D : ℕ) (hD : 0 < D) (a b : ZMod S → ℕ) (k : ZMod S) :
    ((S : ℂ) * D)^2 * (((S : ℂ)⁻¹)^2 * cyclic (digitInput D a) (digitInput D b) k) =
      (coefficient a b k : ℂ) := by
  have hz : (D : ℂ) ≠ 0 := by exact_mod_cast hD.ne'
  simp only [cyclic, digitInput, coefficient, Nat.cast_sum, Nat.cast_mul, mul_sum]
  apply sum_congr rfl
  intro j _
  field_simp [hz, NeZero.ne (S : ℂ)]

theorem final_round (D : ℕ) (hD : 0 < D) (a b : ZMod S → ℕ) (k : ZMod S)
    (out : ℂ) (err : ℝ)
    (h : ‖out - ((S : ℂ)⁻¹)^2 * cyclic (digitInput D a) (digitInput D b) k‖ ≤ err)
    (hprec : ((S : ℝ) * D)^2 * err < 1/2) :
    round ((((S : ℂ) * D)^2 * out).re) = (coefficient a b k : ℤ) := by
  have hn : ‖((S : ℂ) * D)^2 * out - (coefficient a b k : ℂ)‖ < (1/2 : ℝ) := by
    rw [← remove_scales D hD a b k, ← mul_sub, norm_mul]
    simp only [norm_pow, norm_mul, Complex.norm_natCast]
    exact (mul_le_mul_of_nonneg_left h (by positivity)).trans_lt hprec
  have hr := (Complex.abs_re_le_norm _).trans_lt hn
  simp only [Complex.sub_re, Complex.natCast_re] at hr
  rw [round_eq_iff]
  change (coefficient a b k : ℝ) - 1/2 ≤ _ ∧ _ < (coefficient a b k : ℝ) + 1/2
  exact ⟨by linarith [(abs_lt.mp hr).1], by linarith [(abs_lt.mp hr).2]⟩

omit [NeZero S] in
theorem public_grid_margin (B : ℕ) (hB : 32 ≤ B) (hs : S ≤ B) :
    ((S : ℝ) * (4 * B))^2 * (3 * (3 / (B : ℝ)^6)) < 1/2 := by
  have hlow : (32 : ℝ) ≤ B := by exact_mod_cast hB
  have hpos : 0 < (B : ℝ) := by linarith
  have hsb : (S : ℝ) ≤ B := by exact_mod_cast hs
  have hsq : (S : ℝ)^2 ≤ (B : ℝ)^2 := by gcongr
  have h32 : 32^2 ≤ (B : ℝ)^2 := by gcongr
  have ht : ((S : ℝ) * (4 * B))^2 * (3 * (3 / (B : ℝ)^6)) ≤ 144 / (B : ℝ)^2 := by
    field_simp
    nlinarith [mul_nonneg (sub_nonneg.mpr hsq) (sq_nonneg ((B : ℝ)^2))]
  refine ht.trans_lt ?_
  rw [div_lt_iff₀ (by positivity)]
  nlinarith

def radixValue (B : ℕ) (a : ZMod S → ℕ) : ℕ :=
  ∑ j : ZMod S, a j * B^j.val

theorem radix_product (B : ℕ) (a b : ZMod S → ℕ)
    (hspan : ∀ i j, a i ≠ 0 → b j ≠ 0 → i.val + j.val < S) :
    radixValue B (coefficient a b) = radixValue B a * radixValue B b := by
  classical
  simp only [radixValue, coefficient]
  rw [Finset.sum_mul]
  simp only [Finset.mul_sum, Finset.sum_mul]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro i _
  refine Fintype.sum_equiv (Equiv.subRight i) _ _ (fun x ↦ ?_)
  simp only [Equiv.subRight_apply]
  by_cases ha : a i = 0
  · simp [ha]
  by_cases hb : b (x-i) = 0
  · simp [hb]
  have hv := ZMod.val_add_of_lt (hspan i (x-i) ha hb)
  have hx : i + (x-i) = x := by abel
  rw [hx] at hv
  rw [hv, pow_add]
  ring

def pack (B : ℕ) : List ℕ → ℕ
  | [] => 0
  | a :: rest => a + B * pack B rest

def carry (B : ℕ) (k : ℕ) : List ℕ → List ℕ
  | [] => [k]
  | a :: rest => (a+k)%B :: carry B ((a+k)/B) rest

theorem carry_value (B k : ℕ) (cs : List ℕ) :
    pack B (carry B k cs) = k + pack B cs := by
  induction cs generalizing k with
  | nil => simp [pack, carry]
  | cons a as ih =>
    simp only [carry, pack, ih, Nat.mul_add]
    have hd := Nat.mod_add_div (a+k) B
    omega

theorem pack_indices (B m : ℕ) (a : Fin m → ℕ) :
    pack B (List.ofFn a) = ∑ i, a i * B^i.val := by
  induction m with
  | zero => simp [pack]
  | succ n ih =>
    rw [List.ofFn_succ, pack, Fin.sum_univ_succ, ih]
    simp only [Fin.val_zero, pow_zero, mul_one, Fin.val_succ, pow_succ, mul_sum]
    congr 1
    apply sum_congr rfl
    intro i _
    ring

def ordered (a : ZMod S → ℕ) : List ℕ :=
  List.ofFn (fun i : Fin S ↦ a (i.val : ZMod S))

theorem ordered_value (B : ℕ) (a : ZMod S → ℕ) :
    pack B (ordered a) = radixValue B a := by
  unfold ordered radixValue
  rw [pack_indices]
  let bij : Fin S ≃ ZMod S := {
    toFun := fun i ↦ (i.val : ZMod S)
    invFun := fun j ↦ ⟨j.val,j.val_lt⟩
    left_inv := fun i ↦ Fin.ext (ZMod.val_natCast_of_lt i.isLt)
    right_inv := ZMod.natCast_zmod_val }
  refine Fintype.sum_equiv bij _ _ (fun i ↦ ?_)
  change a (i.val : ZMod S) * _ = a (i.val : ZMod S) * B^(i.val : ZMod S).val
  rw [ZMod.val_natCast_of_lt i.isLt]

noncomputable def decode (B : ℕ) (fw bw : Signal S → Signal S)
    (mul : ℂ → ℂ → ℂ) (a b : ZMod S → ℕ) (k : ZMod S) : ℕ :=
  let z := packet fw mul (digitInput (4*B) a) (digitInput (4*B) b)
  (round ((((S : ℂ) * ((4*B : ℕ) : ℂ))^2 * bw z k).re)).toNat

theorem recovered_product (B : ℕ) (hB : 32 ≤ B) (hs : S ≤ B) (u : (ZMod S)ˣ)
    (fw bw : Signal S → Signal S) (mul : ℂ → ℂ → ℂ) (e : ℝ)
    (he : 0 ≤ e) (hpublic : e ≤ 3 / (B : ℝ)^6)
    (hfw : ∀ x, disk x (1/2) → ∀ j, ‖fw x j - forward u x j‖ ≤ e)
    (hbw : ∀ x, disk x (1/2) → ∀ j, ‖bw x j - opposite u x j‖ ≤ e)
    (hm : ∀ x y, ‖x‖ ≤ 1/2 → ‖y‖ ≤ 1/2 → ‖mul x y - x*y‖ ≤ e)
    (a b : ZMod S → ℕ) (ha : ∀ j, a j ≤ B) (hb : ∀ j, b j ≤ B)
    (hspan : ∀ i j, a i ≠ 0 → b j ≠ 0 → i.val + j.val < S) :
    pack B (carry B 0 (ordered (decode B fw bw mul a b))) =
      radixValue B a * radixValue B b := by
  have hpos : 0 < B := by omega
  have hpos' : (0 : ℝ) < B := by exact_mod_cast hpos
  have hlow : (32 : ℝ) ≤ B := by exact_mod_cast hB
  have h6 : (32 : ℝ)^6 ≤ (B : ℝ)^6 := by gcongr
  have he' : e ≤ 1/8 := hpublic.trans (by rw [div_le_iff₀ (by positivity)]; linarith)
  have dom (x : ZMod S → ℕ) (hx : ∀ j, x j ≤ B) : disk (digitInput (4*B) x) (1/4) := by
    intro j
    simp only [digitInput, norm_mul, norm_inv, Complex.norm_natCast]
    rw [← div_eq_inv_mul]
    push_cast
    apply (div_le_iff₀ (by positivity)).mpr
    have hx' : (x j : ℝ) ≤ B := by exact_mod_cast hx j
    linarith
  have budget : ((S : ℝ) * (4*B : ℕ))^2 * (3*e) < 1/2 := by
    norm_cast
    push_cast
    exact (mul_le_mul_of_nonneg_left (mul_le_mul_of_nonneg_left hpublic (by norm_num : (0:ℝ) ≤ 3))
           (sq_nonneg _)).trans_lt (public_grid_margin B hB hs)
  have hc : decode B fw bw mul a b = coefficient a b := by
    funext j
    have err := product_error u fw bw mul e he he' hfw hbw hm _ _ (dom a ha) (dom b hb) j
    have h := final_round (4*B) (by omega) a b j _ _ err budget
    simpa [decode] using congrArg Int.toNat h
  rw [hc, carry_value, Nat.zero_add, ordered_value, radix_product B a b hspan]

#print axioms recovered_product
#print axioms remove_scales
#print axioms final_round
#print axioms public_grid_margin
#print axioms radix_product
#print axioms carry_value
#print axioms product_error
#print axioms dft_cyclic
#print axioms exact_sandwich
end MixedRankRecovery
