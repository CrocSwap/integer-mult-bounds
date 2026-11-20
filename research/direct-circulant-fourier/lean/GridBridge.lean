import ChirpTransform
import PublicGrid
import Mathlib.Data.ZMod.QuotientRing

/-!
A fiber changes one physical coordinate. The induction below expands the
actual two-pass operator on each fiber. Both integer addresses go through
the CRT and the same prefix inverse before the character identity is used.
-/
namespace CirculantGridBridge

open Finset
open scoped BigOperators ComplexConjugate
open CirculantRoot

variable {N : ℕ} [NeZero N]

noncomputable def twoPass (x : Signal N) (k : ZMod N) : ℂ :=
  ((∑ j : ZMod N, quadChirp j) / ((N : ℂ) * midScalar (2*N))) * quadDiag k *
    (multiplier quadRoot)^[2] (fun j ↦ quadDiag j * x j) k

noncomputable def axis (pos : Bool) (x : Signal N) (k : ZMod N) : ℂ :=
  if pos then conj (twoPass (fun j ↦ conj (x j)) k) else twoPass x k

def sign (pos : Bool) : ℤ := if pos then 1 else -1

noncomputable def entry (pos : Bool) (j k : ZMod N) : ℂ :=
  ZMod.stdAddChar (((sign pos : ℤ) : ZMod N) * j * k) / (N : ℂ)

theorem axis_kernel (pos : Bool) (x : Signal N) (k : ZMod N) :
    axis pos x k = ∑ j, entry pos j k * x j := by
  have hp (y : Signal N) : twoPass y k = ZMod.dft y k / (N:ℂ) := (two_stage_mean y k).symm
  cases pos
  · simp only [axis, Bool.false_eq_true, ↓reduceIte, hp, entry, sign, Int.cast_neg, Int.cast_one,
      neg_mul, one_mul, ZMod.dft_apply, smul_eq_mul]
    rw [Finset.sum_div]
    exact Finset.sum_congr rfl fun j _ ↦ by ring
  · simp only [axis, ↓reduceIte, hp, ← opposite_mean, entry, sign, Int.cast_one, one_mul,
      ZMod.invDFT_apply, smul_eq_mul, Finset.mul_sum]
    exact Finset.sum_congr rfl fun j _ ↦ by ring

abbrev Profile {d : ℕ} (s : Fin d → ℕ) := (i : Fin d) → ZMod (s i)

/-- Apply the tail transforms to each fiber, then apply its head transform.
The input at dimension zero is a single scalar. -/
noncomputable def tensor : (d : ℕ) → (s : Fin d → ℕ) →
    (A : ∀ i, Signal (s i) → Signal (s i)) → (Profile s → ℂ) → Profile s → ℂ
  | 0, _, _, f, k => f k
  | d+1, s, A, f, k =>
    A 0 (fun u ↦ tensor d (fun i ↦ s i.succ) (fun i ↦ A i.succ)
      (fun v ↦ f (Fin.cons u v)) (Fin.tail k)) (k 0)

theorem tensor_kernel (d : ℕ) (s : Fin d → ℕ) [∀ i, NeZero (s i)] (pos : Bool)
    (f : Profile s → ℂ) (k : Profile s) :
    tensor d s (fun _ ↦ axis pos) f k =
      ∑ v : Profile s, (∏ i, entry pos (v i) (k i)) * f v := by
  classical
  induction d with
  | zero =>
    rw [tensor, Fintype.sum_unique, Fin.prod_univ_zero, one_mul]
    exact congrArg f (Subsingleton.elim _ _)
  | succ d ih =>
    rw [tensor, axis_kernel]
    simp_rw [ih (fun i ↦ s i.succ) (fun v ↦ _) (Fin.tail k), Finset.mul_sum]
    let e := Fin.consEquiv fun i ↦ ZMod (s i)
    rw [← e.sum_comp (fun v ↦ (∏ i, entry pos (v i) (k i)) * f v), Fintype.sum_prod_type]
    apply Finset.sum_congr rfl
    intro u _
    apply Finset.sum_congr rfl
    intro v _
    rw [show e (u, v) = Fin.cons u v by rfl, Fin.prod_univ_succ]
    simp [Fin.tail, mul_assoc]

variable {d : ℕ} (s : Fin d → ℕ) (hs : Pairwise fun i j ↦ Nat.Coprime (s i) (s j))
  [∀ i, NeZero (s i)] [NeZero (∏ i, s i)]

noncomputable def addresses : ZMod (∏ i, s i) ≃ Profile s :=
  (ZMod.prodEquivPi s hs).toEquiv.trans <|
    Equiv.piCongrRight fun i ↦ (MixedRankIntegrated.mu s hs i).mulLeft

omit [∀ i, NeZero (s i)] [NeZero (∏ i, s i)] in
theorem address_word (j : ℕ) (i : Fin d) :
    addresses s hs j i = (MixedRankIntegrated.mu s hs i).val * (j : ZMod (s i)) := by
  change (MixedRankIntegrated.mu s hs i).val *
      (ZMod.prodEquivPi s hs _ i) = _
  rw [ZMod.prodEquivPi_apply, map_natCast]

def oneWeight (_i : Fin d) : ℕ := 1

omit [∀ i, NeZero (s i)] [NeZero (∏ i, s i)] in
theorem oneWeight_coprime (i : Fin d) : Nat.Coprime (oneWeight i) (s i) := Nat.coprime_one_left _

noncomputable def unit : (ZMod (∏ i, s i))ˣ :=
  MixedRankIntegrated.sourceUnit s oneWeight hs (oneWeight_coprime s)

theorem kernel_original (pos : Bool) (j k : ZMod (∏ i, s i)) :
    (∏ i, entry pos (addresses s hs j i) (addresses s hs k i)) =
      ZMod.stdAddChar (((sign pos : ℤ) : ZMod (∏ i, s i)) * j * ((unit s hs).val*k)) /
        ((∏ i, s i : ℕ) : ℂ) := by
  obtain ⟨jj, rfl⟩ : ∃ jj : ℕ, ((jj : ℕ) : ZMod (∏ i, s i)) = j := ⟨j.val, ZMod.natCast_zmod_val _⟩
  obtain ⟨kk, rfl⟩ : ∃ kk : ℕ, ((kk : ℕ) : ZMod (∏ i, s i)) = k := ⟨k.val, ZMod.natCast_zmod_val _⟩
  simp only [entry, Finset.prod_div_distrib, ← Nat.cast_prod]
  congr 1
  have h := MixedRankIntegrated.physical_character s oneWeight hs (oneWeight_coprime s)
    (sign pos * (jj:ℤ) * kk)
  calc
    _ = ∏ i, ZMod.stdAddChar (((sign pos * (jj:ℤ) * kk *
            (MixedRankIntegrated.factor s oneWeight hs i : ℤ) : ℤ) : ZMod (s i))) := by
      apply Finset.prod_congr rfl
      intro i _
      rw [address_word, address_word]
      simp only [MixedRankIntegrated.factor, oneWeight, one_mul, Int.cast_mul, Int.cast_natCast,
        Nat.cast_pow, Int.cast_pow, ZMod.natCast_zmod_val]
      congr 1
      ring
    _ = _ := by
      rw [h]
      simp only [unit, Int.cast_mul, Int.cast_natCast]
      congr 1
      ring

noncomputable def fromAxes (pos : Bool) (x : Signal (∏ i, s i)) (k : ZMod (∏ i, s i)) : ℂ :=
  let p := addresses s hs
  tensor d s (fun _ ↦ axis pos) (fun v ↦ x (p.symm v)) (p k)

noncomputable def target (pos : Bool) : Signal (∏ i, s i) → Signal (∏ i, s i) :=
  if pos then MixedRankRecovery.opposite (unit s hs) else MixedRankRecovery.forward (unit s hs)

theorem tensor_at_original_coordinates (pos : Bool) (x : Signal (∏ i, s i)) :
    fromAxes s hs pos x = target s hs pos x := by
  funext k
  rw [fromAxes, tensor_kernel, ← (addresses s hs).sum_comp]
  simp only [Equiv.symm_apply_apply, kernel_original]
  cases pos
  · simp only [target, Bool.false_eq_true, ↓reduceIte, sign, Int.cast_neg, Int.cast_one,
      neg_mul, one_mul, MixedRankRecovery.forward, ZMod.dft_apply, smul_eq_mul, Finset.mul_sum]
    exact Finset.sum_congr rfl fun j _ ↦ by ring
  · simp only [target, ↓reduceIte, sign, Int.cast_one, one_mul, MixedRankRecovery.opposite,
      ZMod.invDFT_apply, smul_eq_mul, Finset.mul_sum]
    exact Finset.sum_congr rfl fun j _ ↦ by ring

theorem axis_nonexpanding {m : ℕ} [NeZero m] (pos : Bool) (x : Signal m) (b : ℝ)
    (hx : ∀ j, ‖x j‖ ≤ b) (k : ZMod m) : ‖axis pos x k‖ ≤ b := by
  rw [axis_kernel]
  have hcoeff (j : ZMod m) : ‖entry pos j k‖ = (m:ℝ)⁻¹ := by
    simp [entry, ZMod.stdAddChar_apply]
  have hn : (m:ℝ) ≠ 0 := NeZero.ne _
  calc
    _ ≤ ∑ j, ‖entry pos j k * x j‖ := norm_sum_le _ _
    _ ≤ ∑ _ : ZMod m, (m:ℝ)⁻¹ * b := Finset.sum_le_sum fun j _ ↦ by
      rw [norm_mul, hcoeff]
      exact mul_le_mul_of_nonneg_left (hx j) (by positivity)
    _ = b := by simp [nsmul_eq_mul, ZMod.card, hn]

theorem axis_difference {m : ℕ} [NeZero m] (pos : Bool) (x y : Signal m) (e : ℝ)
    (hxy : ∀ j, ‖x j - y j‖ ≤ e) (k : ZMod m) : ‖axis pos x k - axis pos y k‖ ≤ e := by
  have h : axis pos x k - axis pos y k = axis pos (x-y) k := by
    simp [axis_kernel, mul_sub, Finset.sum_sub_distrib]
  rw [h]
  exact axis_nonexpanding pos _ e hxy k

theorem tensor_radius (m : ℕ) (r : Fin m → ℕ) [∀ i, NeZero (r i)] (pos : Bool)
    (f : Profile r → ℂ) (b : ℝ) (hf : ∀ v, ‖f v‖ ≤ b) (k : Profile r) :
    ‖tensor m r (fun _ ↦ axis pos) f k‖ ≤ b := by
  induction m with
  | zero => exact hf k
  | succ m ih =>
    rw [tensor]
    apply axis_nonexpanding
    exact fun u ↦ ih (fun i ↦ r i.succ) (fun v ↦ f (Fin.cons u v)) (fun v ↦ hf _) _

/-- Each fiber is read inside the unit disk. The proof checks this domain
at every dimension for imperfect as well as exact intermediate data. -/
theorem tensor_error (m : ℕ) (r : Fin m → ℕ) [∀ i, NeZero (r i)] (pos : Bool)
    (A : ∀ i, Signal (r i) → Signal (r i)) {e : ℝ} (he : 0 ≤ e) (hd : m * e ≤ 1/2)
    (hA : ∀ i x, (∀ j, ‖x j‖ ≤ 1) → ∀ k, ‖A i x k - axis pos x k‖ ≤ e)
    (f : Profile r → ℂ) (hf : ∀ v, ‖f v‖ ≤ 1/2) (k : Profile r) :
    ‖tensor m r A f k - tensor m r (fun _ ↦ axis pos) f k‖ ≤ m * e := by
  induction m with
  | zero => simp [tensor]
  | succ m ih =>
    rw [Nat.cast_succ, add_mul, one_mul] at hd ⊢
    let y (u : ZMod (r 0)) := tensor m (fun i ↦ r i.succ) (fun i ↦ A i.succ)
      (fun v ↦ f (Fin.cons u v)) (Fin.tail k)
    let z (u : ZMod (r 0)) := tensor m (fun i ↦ r i.succ) (fun _ ↦ axis pos)
      (fun v ↦ f (Fin.cons u v)) (Fin.tail k)
    have htail (u) : ‖y u-z u‖ ≤ (m:ℝ)*e := ih (fun i ↦ r i.succ) (fun i ↦ A i.succ)
      (by linarith) (fun i ↦ hA i.succ) (fun v ↦ f (Fin.cons u v)) (fun _ ↦ hf _) (Fin.tail k)
    have hrad (u) : ‖z u‖ ≤ 1/2 := tensor_radius m _ pos _ _ (fun _ ↦ hf _) _
    have hy (u) : ‖y u‖ ≤ 1 := by
      have b := norm_sub_le_norm_sub_add_norm_sub (y u) (z u) 0
      simp only [sub_zero] at b
      linarith [htail u, hrad u]
    change ‖A 0 y (k 0) - axis pos z (k 0)‖ ≤ _
    have t := norm_sub_le_norm_sub_add_norm_sub (A 0 y (k 0)) (axis pos y (k 0)) (axis pos z (k 0))
    linarith [hA 0 y hy (k 0), axis_difference pos y z _ htail (k 0)]

noncomputable def raw {D : ℕ} (A : ∀ i, Signal (s i) → Signal (s i))
    (x : MixedRankPublicGrid.GridSignal (∏ i, s i) D) (k : ZMod (∏ i, s i)) : ℂ :=
  let p := addresses s hs
  tensor d s A (fun v ↦ x.val (p.symm v)) (p k)

theorem certified_grid_product (B : ℕ) (hB : 32 ≤ B) (hEven : Even B) (hsize : ∏ i, s i ≤ B)
    (A : Bool → ∀ i, Signal (s i) → Signal (s i)) {e : ℝ} (he : 0 ≤ e)
    (hroom : (d:ℝ)*e ≤ 1/2) (herr : (d:ℝ)*e ≤ 1 / ((B^6 : ℕ) : ℝ)^4)
    (hA : ∀ pos i x, (∀ j, ‖x j‖ ≤ 1) → ∀ k, ‖A pos i x k - axis pos x k‖ ≤ e)
    (a b : ZMod (∏ i, s i) → ℕ) (ha : ∀ j, a j ≤ B) (hb : ∀ j, b j ≤ B)
    (hspan : ∀ i j, a i ≠ 0 → b j ≠ 0 → i.val+j.val < ∏ i, s i) :
    MixedRankRecovery.pack B (MixedRankRecovery.carry B 0
      (MixedRankRecovery.ordered (MixedRankPublicGrid.wordDecode (by omega : 0 < B) hEven
        (raw s hs (A false)) (raw s hs (A true)) a b))) =
      MixedRankRecovery.radixValue B a * MixedRankRecovery.radixValue B b := by
  have hacc (p : Bool) : MixedRankPublicGrid.RawAccuracy (B^6) (target s hs p) (raw s hs (A p)) := by
    intro x hx k
    rw [← tensor_at_original_coordinates]
    exact (tensor_error d s p (A p) he hroom (hA p)
      (fun v ↦ x.val ((addresses s hs).symm v)) (fun _ ↦ hx _) ((addresses s hs) k)).trans herr
  exact MixedRankPublicGrid.grid_product_at_physical_coordinates s oneWeight hs
    (oneWeight_coprime s) B hB hEven hsize _ _ (hacc false) (hacc true) a b ha hb hspan

/-- This entry point uses the complete error of the fused tape word.
Rounding operations inside the fused evaluator can have any parenthesization. -/
theorem fused_grid_product (B : ℕ) (hB : 32 ≤ B) (hEven : Even B) (hsize : ∏ i, s i ≤ B)
    (W : Bool → MixedRankPublicGrid.GridSignal (∏ i, s i) (B^6) → Signal (∏ i, s i))
    (hW : ∀ p x, MixedRankRecovery.disk x.val (1/2) → ∀ k,
      ‖W p x k - fromAxes s hs p x.val k‖ ≤ 1 / ((B^6 : ℕ) : ℝ)^4)
    (a b : ZMod (∏ i, s i) → ℕ) (ha : ∀ j, a j ≤ B) (hb : ∀ j, b j ≤ B)
    (hspan : ∀ i j, a i ≠ 0 → b j ≠ 0 → i.val+j.val < ∏ i, s i) :
    MixedRankRecovery.pack B (MixedRankRecovery.carry B 0
      (MixedRankRecovery.ordered (MixedRankPublicGrid.wordDecode (by omega : 0 < B) hEven
        (W false) (W true) a b))) =
      MixedRankRecovery.radixValue B a * MixedRankRecovery.radixValue B b := by
  have hacc (p : Bool) : MixedRankPublicGrid.RawAccuracy (B^6) (target s hs p) (W p) := by
    intro x hx k
    rw [← tensor_at_original_coordinates]
    exact hW p x hx k
  exact MixedRankPublicGrid.grid_product_at_physical_coordinates s oneWeight hs
    (oneWeight_coprime s) B hB hEven hsize _ _ (hacc false) (hacc true) a b ha hb hspan

#print axioms fused_grid_product
#print axioms tensor_error
#print axioms certified_grid_product
#print axioms tensor_kernel
#print axioms addresses
#print axioms kernel_original
#print axioms tensor_at_original_coordinates

end CirculantGridBridge
