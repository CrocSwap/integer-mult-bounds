import OAI.Computability.FourierTransform.BinaryBasis

namespace OAI

/-! Fourier frames on one binary column. We use tensor Hadamard for matrix identities only.
All executed scalar constants are in Q(i). -/
namespace PowerSaving.Binary
open Matrix Finset Complex
noncomputable section

def sign (i : F) : ℂ := if i=0 then 1 else -1
def tint (i : F) : ℂ := if i=0 then 1 else I

lemma sign_add (i j : F) : sign (i+j) = sign i * sign j := by
  rcases bit_cases i with rfl|rfl <;>
    rcases bit_cases j with rfl|rfl <;> simp [sign]

lemma sign_sq (i : F) : sign i * sign i = 1 := by
  rw [← sign_add, cancel]; simp [sign]

lemma tint_add (i j : F) : tint (i+j) = tint i * tint j * sign (i*j) := by
  rcases bit_cases i with rfl|rfl <;>
    rcases bit_cases j with rfl|rfl <;> simp [sign,tint]

lemma tint_sq (i : F) : tint i * tint i = sign i := by
  rcases bit_cases i with rfl|rfl <;> simp [sign,tint]

lemma sign_sum {α : Type*} (v : α → F) (s : Finset α) :
    sign (∑ i ∈ s, v i) = ∏ i ∈ s, sign (v i) := by
  classical
  induction s using Finset.induction with
  | empty => simp [sign]
  | insert i s h ih => simp [h, sign_add, ih]

variable {α : Type*} [Fintype α]

def lum (x : Space α) : ℂ := ∏ i, tint (x i)

@[simp] lemma lum_zero : lum (0 : Space α)=1 := by
  simp [lum,tint]

lemma lum_add (x y : Space α) :
    lum (x+y) = lum x * lum y * sign (dot x y) := by
  simp only [dot, lum, Pi.add_apply, tint_add, prod_mul_distrib, sign_sum]

lemma lum_sq (x : Space α) : lum x * lum x = sign (dot x x) := by
  simp only [dot, lum, ← prod_mul_distrib, sign_sum, tint_sq]
  apply prod_congr rfl
  intro j hj
  rcases bit_cases (x j) with h|h <;> simp [h]

lemma lum_nonzero (x : Space α) : lum x ≠ 0 := by
  have h := lum_sq x
  intro ha
  rw [ha, zero_mul, sign] at h
  split at h <;> norm_num at h

lemma lum_of_unit (x : Space α) (h : dot x x=1) :
    lum x = I ∨ lum x = -I := by
  apply sq_eq_sq_iff_eq_or_eq_neg.mp
  rw [pow_two, lum_sq, h]; simp [sign]

def littleH : Matrix F F ℂ := fun i j => sign (i*j)

def littleH' : Matrix F F ℂ := fun i j => sign (i*j)/2

def ca : ℂ := (1+I)/2
def cb : ℂ := (1-I)/2
def littleC : Matrix F F ℂ := fun i j => if i=j then ca else cb

lemma sum_bits (v : F → ℂ) : ∑ i, v i = v 0 + v 1 := by
  have h : (univ : Finset F) = {0,1} := by
    ext i; rcases bit_cases i with rfl|rfl <;> simp
  rw [h]
  simp

lemma littleH_H' : littleH * littleH' = 1 := by
  ext i j
  rw [Matrix.mul_apply,sum_bits,one_apply]
  rcases bit_cases i with rfl|rfl <;> rcases bit_cases j with rfl|rfl <;>
    norm_num [littleH, littleH', sign]

lemma little_phase :
    littleC * littleH = littleH * diagonal tint := by
  ext i j
  rw [Matrix.mul_apply,sum_bits,Matrix.mul_diagonal]
  rcases bit_cases i with rfl|rfl <;> rcases bit_cases j with rfl|rfl <;>
    simp [littleC, ca, cb, littleH, tint, sign] <;> ring

abbrev CMat (α : Type*) := Matrix (Space α) (Space α) ℂ

def kernel (α : Type*) [Fintype α] : CMat α := digitProd fun _ => littleC

def wal (α : Type*) [Fintype α] : CMat α := digitProd fun _ => littleH
def walI (α : Type*) [Fintype α] : CMat α := digitProd fun _ => littleH'

lemma wal_apply (x y : Space α) : wal α x y = sign (dot x y) := by
  simp [wal, littleH, dot, sign_sum]

variable [DecidableEq α]

lemma wal_right (α : Type*) [Fintype α] [DecidableEq α] :
    wal α * walI α = 1 := by rw [wal, walI, digitProd_mul]; simp_rw [littleH_H',digitProd_one]

lemma wal_left (α : Type*) [Fintype α] [DecidableEq α] :
    walI α * wal α = 1 := mul_eq_one_comm.mp (wal_right α)

def wrap (f : Space α → ℂ) : CMat α := wal α * diagonal f * walI α

lemma wrap_of (M : CMat α) (f : Space α → ℂ)
    (h : M * wal α = wal α * diagonal f) : wrap f = M := by
  rw [wrap, ← h, Matrix.mul_assoc, wal_right, mul_one]

lemma wrap_one : wrap (fun _ : Space α => 1) = 1 := by
  simp_rw [wrap, diagonal_one, mul_one, wal_right]

lemma wrap_mul (f g : Space α → ℂ) :
    wrap f * wrap g = wrap fun x => f x * g x := by
  unfold wrap
  rw [show wal α * diagonal f * walI α * (wal α * diagonal g * walI α) =
        wal α * (diagonal f * (walI α * wal α) * diagonal g) * walI α by
      simp only [Matrix.mul_assoc]]
  rw [wal_left, mul_one]
  simp only [diagonal_mul_diagonal]

lemma wrap_comm (f g : Space α → ℂ) : wrap f * wrap g = wrap g * wrap f := by
  rw [wrap_mul, wrap_mul]; simp_rw [mul_comm]

lemma wrap_lum : wrap (lum : Space α → ℂ) = kernel α := by
  apply wrap_of
  unfold kernel wal
  rw [show diagonal (lum : Space α → ℂ) = digitProd (fun _ => diagonal tint) from
      (digitProd_diagonal fun _ : α => tint).symm,
      digitProd_mul, digitProd_mul]
  simp_rw [little_phase]

def shift (z : Space α) : CMat α :=
  fun i j => if i+z = j then 1 else 0

lemma shift_phase (z : Space α) : shift z = wrap (fun x => sign (dot z x)) := by
  symm
  apply wrap_of
  ext i j
  rw [Matrix.mul_apply, Matrix.mul_diagonal]
  simp [shift, wal_apply, ite_mul, sign_add]

lemma shift_sq (z : Space α) : shift z * shift z = 1 := by
  rw [shift_phase, wrap_mul]
  simp only [sign_sq, wrap_one]

/-- Forward directional factor. -/
def dir (z : Space α) : CMat α := ca • 1 + cb • shift z

lemma dir_phase (z : Space α) : dir z = wrap (fun x => tint (dot z x)) := by
  symm
  apply wrap_of
  have hs : shift z * wal α = wal α * diagonal (fun x => sign (dot z x)) := by
    rw [shift_phase, wrap, Matrix.mul_assoc, wal_left, mul_one]
  unfold dir
  rw [add_mul, Matrix.smul_mul, Matrix.smul_mul, one_mul, hs]
  ext i j
  simp only [Matrix.add_apply, Matrix.smul_apply, Matrix.mul_diagonal, smul_eq_mul]
  rcases bit_cases (dot z j) with h|h <;> simp [ca, cb, tint, sign, h] <;> ring

lemma dir_sq (z : Space α) : dir z * dir z = shift z := by
  rw [dir_phase, wrap_mul, shift_phase]; simp only [tint_sq]

/-- Basis independent frame from projection. -/
def frame (A : OBase α) (s : Finset α) := wrap fun x => lum (A.proj s x)

@[simp] lemma frame_univ (A : OBase α) : frame A univ = kernel α := by
  simp [frame, wrap_lum]

@[simp] lemma frame_zero (A : OBase α) : frame A ∅ = 1 := by
  simp [frame, OBase.proj, wrap_one]

lemma frame_congr (A B : OBase α) (s t : Finset α)
    (h : A.mat s = B.mat t) : frame A s = frame B t := by
  rw [frame, frame, OBase.proj_congr A B _ _ h]

/-- Frames are invertible (so cancellation along a path suffices). -/
def unframe (A : OBase α) (s : Finset α) := wrap fun x => (lum (A.proj s x))⁻¹

lemma unframe_right (A : OBase α) (s : Finset α) : frame A s * unframe A s = 1 := by
  rw [frame, unframe, wrap_mul]
  simp [lum_nonzero, wrap_one]

lemma unframe_left (A : OBase α) (s : Finset α) : unframe A s * frame A s = 1 :=
  mul_eq_one_comm.mp (unframe_right A s)

/-- Change when adding one orthogonal line in a fixed mask. -/
def delta (z : Space α) := wrap fun x => lum (dot z x • z)

lemma frame_ins (A : OBase α) (s : Finset α) (i : α) (hi : i ∉ s) :
    frame A (insert i s) = delta (A.v i) * frame A s := by
  rw [delta, frame, frame, wrap_mul]
  have hh (x : Space α) :
      lum (A.proj (insert i s) x) = lum (dot (A.v i) x • A.v i) * lum (A.proj s x) := by
    rw [show A.proj (insert i s) x = dot (A.v i) x • A.v i + A.proj s x by
      unfold OBase.proj; rw [sum_insert hi], lum_add]
    simp [OBase.dot_proj_omit A x hi, sign]
  simp_rw [hh]

lemma delta_pos (z : Space α) (h : lum z = I) :
    delta z = dir z := by
  rw [dir_phase, delta]
  apply congrArg wrap
  funext x
  rcases bit_cases (dot z x) with g|g <;> simp [tint, g, h]

lemma delta_neg (z : Space α) (h : lum z = -I) :
    delta z = shift z * dir z := by
  rw [delta, dir_phase, shift_phase, wrap_mul]
  apply congrArg wrap
  funext x
  rcases bit_cases (dot z x) with g|g <;> simp [tint, sign, g, h]

lemma delta_sq (z : Space α) (h : dot z z=1) : delta z * delta z = shift z := by
  obtain hp|hn := lum_of_unit z h
  · rw [delta_pos z hp, dir_sq]
  · have hh : dir z * shift z = shift z * dir z := by
      rw [dir_phase, shift_phase]; apply wrap_comm
    rw [delta_neg z hn, ← mul_assoc, mul_assoc (shift z) (dir z), hh]
    simp [← Matrix.mul_assoc, shift_sq, dir_sq]

lemma delta_comm (z : Space α) (A : OBase α) (s : Finset α) :
    delta z * frame A s = frame A s * delta z :=
  wrap_comm _ _

lemma delta_shift_comm (z v : Space α) : delta z * shift v = shift v * delta z := by
  rw [shift_phase]; apply wrap_comm

lemma frame_shift_comm (z : Space α) (A : OBase α) (s : Finset α) :
    shift z * frame A s = frame A s * shift z := by
  rw [shift_phase]; apply wrap_comm

end
end PowerSaving.Binary

end OAI
