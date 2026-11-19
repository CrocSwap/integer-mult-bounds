/-
BankNC0d .  
Main-contract minor fact.  DATA : the 400 main outputs are
exactly 96 blocks of (x, y+x), 96 blocks of (u-v, v), 8 blocks of (x-y, (x+y)/2) -- the caller-declared maps --
pairwise disjoint, nothing left over; the 1070 helpers return their own input and no main reads a helper.
Here: for ANY number of helpers and ANY assignment of block types, every principal minor of the output matrix is nonzero.
Generic engine: matrices  diag d + at most one off-diagonal entry per row (partner p), where every partner chain
ends or lands in a 2-cycle with d_i d_j - o_i o_j ≠ 0.
Kernel only: no sorry, no native_decide.
-/
import Mathlib.LinearAlgebra.Matrix.ToLinearEquiv
import Mathlib.Data.Rat.Defs
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Data.Rat.Cast.Defs

namespace BankNC0
open Finset Matrix

/-- diagonal `d`, at most one off-diagonal entry `o i` per row, at the partner `p i`. -/
def funcMat {K ι : Type} [Field K] [DecidableEq ι] (d o : ι → K) (p : ι → Option ι) : Matrix ι ι K :=
  fun i j => if j = i then d i else if p i = some j then o i else 0

theorem minors_ne_zero {K ι : Type} [Field K] [Fintype ι] [DecidableEq ι]
    (d o : ι → K) (p : ι → Option ι) (hd : ∀ i, d i ≠ 0) (hp : ∀ i, p i ≠ some i)
    (rk : ι → ℕ)
    (hrk : ∀ i j, p i = some j → rk j < rk i ∨ (p j = some i ∧ d i * d j ≠ o i * o j))
    (C : Finset ι) :
    ((funcMat d o p).submatrix (fun c : C => (c : ι)) (fun c : C => (c : ι))).det ≠ 0 := by
  intro hdet
  obtain ⟨v, hv0, hv⟩ := Matrix.exists_mulVec_eq_zero_iff.mpr hdet
  apply hv0
  have row : ∀ i : C, d i * v i + ∑ j : C, (if p i = some (j : ι) then o i * v j else 0) = 0 := by
    intro i
    have h := congrFun hv i
    simp only [Matrix.mulVec, dotProduct, Matrix.submatrix_apply, funcMat, Pi.zero_apply] at h
    have this : ∀ j : C, (if (j : ι) = i then d i else if p i = some (j : ι) then o i else 0) * v j
        = (if j = i then d i * v i else 0) + (if p i = some (j : ι) then o i * v j else 0) := by
      intro j
      by_cases hji : j = i
      · subst hji
        have := hp j
        simp [this]
      · have : (j : ι) ≠ i := fun e => hji (Subtype.ext e)
        simp [this, hji]
    have e1 : ∑ j : C, (if j = i then d i * v i else 0) = d i * v i := by simp
    rw [Finset.sum_congr rfl (fun j _ => this j), Finset.sum_add_distrib, e1] at h
    exact h
  have hsome : ∀ (i : C) (j : ι) (hj : j ∈ C), p i = some j →
      ∑ k : C, (if p i = some (k : ι) then o i * v k else 0) = o i * v ⟨j, hj⟩ := by
    intro i j hj hpi
    rw [Finset.sum_eq_single (⟨j, hj⟩ : C)]
    · simp [hpi]
    · intro k _ hk
      have : p i ≠ some (k : ι) := by
        rw [hpi]; intro e; apply hk; exact Subtype.ext (Option.some.inj e).symm
      simp [this]
    · intro h; exact absurd (Finset.mem_univ _) h
  have hzero : ∀ (i : C), (∀ k : C, p i ≠ some (k : ι)) →
      ∑ k : C, (if p i = some (k : ι) then o i * v k else 0) = 0 := by
    intro i h
    exact Finset.sum_eq_zero (fun k _ => by simp [h k])
  have solo : ∀ i : C, (∑ k : C, (if p i = some (k : ι) then o i * v k else 0) = 0) → v i = 0 := by
    intro i hs
    have := row i
    rw [hs, add_zero] at this
    exact (mul_eq_zero.mp this).resolve_left (hd i)
  have main : ∀ n, ∀ i : C, rk i = n → v i = 0 := by
    intro n
    induction n using Nat.strong_induction_on with
    | _ n ih =>
      intro i hi
      cases hpi : p i with
      | none => exact solo i (hzero i (fun k => by simp [hpi]))
      | some j =>
        by_cases hj : j ∈ C
        · rcases hrk i j hpi with hlt | ⟨hpj, hne⟩
          · have hv0' : v ⟨j, hj⟩ = 0 := ih (rk j) (by omega) ⟨j, hj⟩ rfl
            exact solo i (by rw [hsome i j hj hpi, hv0', mul_zero])
          · have r1 := row i
            rw [hsome i j hj hpi] at r1
            have r2 := row ⟨j, hj⟩
            rw [hsome ⟨j, hj⟩ i i.2 hpj] at r2
            have e : (d i * d j - o i * o j) * v i = 0 := by
              have : (d i * d j - o i * o j) * v i
                  = d j * (d i * v i + o i * v ⟨j, hj⟩) - o i * (d j * v ⟨j, hj⟩ + o j * v i) := by ring
              rw [this, r1]
              have r2' : d j * v ⟨j, hj⟩ + o j * v i = 0 := by simpa using r2
              rw [r2']; ring
            exact (mul_eq_zero.mp e).resolve_left (sub_ne_zero.mpr hne)
        · exact solo i (hzero i (fun k hk => by
            rw [hpi] at hk; exact hj (by rw [Option.some.inj hk]; exact k.2)))
  funext i
  exact main _ i rfl

/-! ### The declared caller maps, as data -/

/-- block types: 0: (x, y+x); 1: (u-v, v); 2: (x-y, (x+y)/2).  Entry `blk t a b`. -/
def blk : Fin 3 → Fin 2 → Fin 2 → ℚ
  | 0, 0, 0 => 1 | 0, 0, 1 => 0 | 0, 1, 0 => 1 | 0, 1, 1 => 1
  | 1, 0, 0 => 1 | 1, 0, 1 => -1 | 1, 1, 0 => 0 | 1, 1, 1 => 1
  | 2, 0, 0 => 1 | 2, 0, 1 => -1 | 2, 1, 0 => 1/2 | 2, 1, 1 => 1/2

/-- index: helpers (identity) ⊕ main slots (block b, position i). -/
abbrev Idx (h b : ℕ) := Fin h ⊕ (Fin b × Fin 2)

/-- output matrix: helpers identity; mains block diagonal in the declared maps; no cross terms. -/
def outMat (h b : ℕ) (t : Fin b → Fin 3) : Matrix (Idx h b) (Idx h b) ℚ
  | .inl x, .inl y => if x = y then 1 else 0
  | .inl _, .inr _ => 0
  | .inr _, .inl _ => 0
  | .inr (b1, i), .inr (b2, j) => if b1 = b2 then blk (t b1) i j else 0

def dd (h b : ℕ) (t : Fin b → Fin 3) : Idx h b → ℚ
  | .inl _ => 1
  | .inr (b1, i) => blk (t b1) i i

def pp (h b : ℕ) (t : Fin b → Fin 3) : Idx h b → Option (Idx h b)
  | .inl _ => none
  | .inr (b1, i) => if blk (t b1) i (1 - i) ≠ 0 then some (.inr (b1, 1 - i)) else none

def oo (h b : ℕ) (t : Fin b → Fin 3) : Idx h b → ℚ
  | .inl _ => 0
  | .inr (b1, i) => blk (t b1) i (1 - i)

def rkk (h b : ℕ) (t : Fin b → Fin 3) : Idx h b → ℕ
  | .inl _ => 0
  | .inr (b1, i) => if blk (t b1) i (1 - i) ≠ 0 then 1 else 0

theorem outMat_eq (h b : ℕ) (t : Fin b → Fin 3) :
    outMat h b t = funcMat (dd h b t) (oo h b t) (pp h b t) := by
  funext x y
  rcases x with x | ⟨b1, i⟩ <;> rcases y with y | ⟨b2, j⟩
  · simp [outMat, funcMat, dd, pp, eq_comm]
  · simp [outMat, funcMat, pp]
  · simp [outMat, funcMat, pp, dd]
  · simp only [outMat, funcMat, dd, pp, oo]
    by_cases hb : b1 = b2
    · subst hb
      fin_cases i <;> fin_cases j <;> simp [blk] <;> (generalize t b1 = u; fin_cases u <;> simp [blk])
    · have hb' : ¬ b2 = b1 := fun e => hb e.symm
      simp [hb, hb']

theorem main_minors (h b : ℕ) (t : Fin b → Fin 3) (C : Finset (Idx h b)) :
    ((outMat h b t).submatrix (fun c : C => (c : Idx h b)) (fun c : C => (c : Idx h b))).det ≠ 0 := by
  rw [outMat_eq]
  refine minors_ne_zero (dd h b t) (oo h b t) (pp h b t) ?_ ?_ (rkk h b t) ?_ C
  · intro x; rcases x with x | ⟨b1, i⟩
    · simp [dd]
    · simp only [dd]; generalize t b1 = u; fin_cases u <;> fin_cases i <;> simp [blk]
  · intro x; rcases x with x | ⟨b1, i⟩
    · simp [pp]
    · simp only [pp]; split_ifs
      · simp; fin_cases i <;> decide
      · simp
  · intro x y hxy
    rcases x with x | ⟨b1, i⟩
    · simp [pp] at hxy
    · simp only [pp] at hxy
      split_ifs at hxy with hh
      · have hy := Option.some.inj hxy
        subst hy
        simp only [rkk, dd, oo, pp]
        generalize t b1 = u at *
        fin_cases u <;> fin_cases i <;> simp [blk] at hh ⊢ <;> norm_num

end BankNC0
