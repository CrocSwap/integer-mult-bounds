import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.Analysis.Complex.Basic
import Mathlib.Tactic.Ring

/-! The two boundary terms for a circulant embedded in a larger identity. -/

namespace DirectCirculant

open Matrix

def liveEntry (r : ℤ) (f : ℤ → ℂ) (i j : ℤ) : ℂ :=
  if 0 ≤ i ∧ i < r ∧ 0 ≤ j ∧ j < r then f (i-j) else 0

def boundaryLeft (r i : ℤ) : ℂ :=
  (if i = r then 1 else 0) - (if i = 0 then 1 else 0)

theorem two_boundaries (r i j : ℤ) (hr : 0 < r) (hi : 0 ≤ i) (hj : 0 ≤ j)
    (f : ℤ → ℂ) (period : ∀ x, f (r + x) = f x) :
    liveEntry r f (i-1) j - liveEntry r f i (j+1) =
      boundaryLeft r i * (if j < r then f (-1-j) else 0) +
      (if i < r then f i else 0) * (if j = r-1 then 1 else 0) := by
  have h₁ : f (r - 1 - j) = f (-1-j) := by
    simpa only [show r - 1 - j = r + (-1-j) by ring] using period (-1-j)
  have h₂ (h : j = r-1) : f (i-1-j) = f i := by
    rw [h]
    have := period (i-r)
    rw [show r+(i-r) = i by ring] at this
    simpa only [show i-1-(r-1) = i-r by ring] using this.symm
  have indices : i - (j+1) = i-1-j := by ring
  unfold liveEntry boundaryLeft
  split_ifs <;> (try omega) <;> simp_all

def lowerShift (t : ℕ) : Matrix (Fin t) (Fin t) ℂ :=
  fun i j ↦ if (i : ℕ) = (j : ℕ)+1 then 1 else 0

def embedded (t : ℕ) (r : ℤ) (f : ℤ → ℂ) : Matrix (Fin t) (Fin t) ℂ :=
  fun i j ↦ liveEntry r f i j

theorem left_shift (t : ℕ) (r : ℤ) (f : ℤ → ℂ) (i j : Fin t) :
    (lowerShift t * embedded t r f) i j = liveEntry r f ((i:ℤ)-1) j := by
  classical
  by_cases h : i.val = 0
  · have hz : (i:ℤ) = 0 := by exact_mod_cast h
    simp only [Matrix.mul_apply, lowerShift, embedded]
    rw [Finset.sum_eq_zero]
    · simp [hz, liveEntry]
    · intro k _
      have hn : i.val ≠ k.val+1 := by omega
      simp [hn]
  · let k : Fin t := ⟨i.val-1, by omega⟩
    have hk : i.val = k.val+1 := by dsimp [k]; omega
    have hki : (k:ℤ) = (i:ℤ)-1 := by omega
    rw [Matrix.mul_apply, Finset.sum_eq_single k]
    · change (if i.val = k.val+1 then (1:ℂ) else 0) * liveEntry r f k j = _
      have v : (if i.val = k.val+1 then (1:ℂ) else 0) = 1 := by
        split
        · rfl
        · contradiction
      rw [v, one_mul, hki]
    · intro b _ hb
      have hn : i.val ≠ b.val+1 := by intro eq; apply hb; apply Fin.ext; omega
      simp [lowerShift, hn]
    · simp

theorem right_shift (t : ℕ) (r : ℤ) (hrt : r ≤ t) (f : ℤ → ℂ) (i j : Fin t) :
    (embedded t r f * lowerShift t) i j = liveEntry r f i ((j:ℤ)+1) := by
  classical
  by_cases h : j.val+1 < t
  · let k : Fin t := ⟨j.val+1, h⟩
    have hk : k.val = j.val+1 := rfl
    rw [Matrix.mul_apply, Finset.sum_eq_single k]
    · simp [lowerShift, embedded, hk]
    · intro b _ hb
      have hn : b.val ≠ j.val+1 := by intro eq; apply hb; exact Fin.ext eq
      simp [lowerShift, hn]
    · simp
  · simp only [Matrix.mul_apply]
    rw [Finset.sum_eq_zero]
    · have hn : ¬ (j:ℤ)+1 < r := by omega
      simp [liveEntry, hn]
    · intro k _
      have hn : k.val ≠ j.val+1 := by omega
      simp [lowerShift, hn]

/-- Padding by identity adds at most two independent displacement columns. -/
theorem padded_rank (t r : ℕ) (hr : 0 < r) (hrt : r ≤ t) (f : ℤ → ℂ)
    (period : ∀ x, f ((r:ℤ)+x) = f x) :
    let A := 1 + embedded t r f
    (lowerShift t * A - A * lowerShift t).rank ≤ 2 := by
  classical
  dsimp only
  let U : Matrix (Fin t) (Fin 2) ℂ := fun i k ↦
    if k = 0 then boundaryLeft r i else if (i:ℤ) < r then f i else 0
  let V : Matrix (Fin 2) (Fin t) ℂ := fun k j ↦
    if k = 0 then (if (j:ℤ) < r then f (-1-j) else 0)
    else if (j:ℤ) = (r:ℤ)-1 then 1 else 0
  have fact : lowerShift t * (1 + embedded t r f) - (1 + embedded t r f) * lowerShift t =
      U * V := by
    simp only [mul_add, add_mul, mul_one, one_mul, add_sub_add_left_eq_sub]
    ext i j
    rw [Matrix.sub_apply, left_shift, right_shift t r (by exact_mod_cast hrt)]
    rw [Matrix.mul_apply, Fin.sum_univ_two]
    simpa [U, V] using
      two_boundaries r i j (by exact_mod_cast hr) (by positivity) (by positivity) f period
  rw [fact]
  exact (Matrix.rank_mul_le_left U V).trans (by simpa using U.rank_le_card_width)

#print axioms padded_rank

end DirectCirculant
