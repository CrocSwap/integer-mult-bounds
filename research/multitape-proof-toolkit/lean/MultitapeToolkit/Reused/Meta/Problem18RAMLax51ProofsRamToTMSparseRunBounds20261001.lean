import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMLookupCellMachine20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

open Lax51Proofs.Microcode

theorem sparseEffect_inp_length_le {w : ℕ} {i : Instr} {s s' : SparseState}
    (h : sparseEffect w i s = some s') : s'.inp.length ≤ s.inp.length := by
  cases i <;> simp [sparseEffect] at h
  case read a =>
    cases hin : s.inp with
    | nil => simp [hin] at h
    | cons v inp =>
      simp [hin] at h
      subst s'
      simp
  all_goals subst s' <;> simp

theorem sparseEffect_out_length_le {w : ℕ} {i : Instr} {s s' : SparseState}
    (h : sparseEffect w i s = some s') : s'.out.length ≤ s.out.length + 1 := by
  cases i <;> simp [sparseEffect] at h
  case read a =>
    cases hin : s.inp with
    | nil => simp [hin] at h
    | cons v inp => simp [hin] at h; subst s'; simp
  all_goals subst s' <;> simp

theorem sparseStep_inp_length_le {w : ℕ} {p : Program} {s s' : SparseState}
    (h : sparseStep w p s = some s') : s'.inp.length ≤ s.inp.length := by
  unfold sparseStep at h
  cases hi : p[s.pc]? with
  | none => simp [hi] at h
  | some i =>
      simp [hi] at h
      exact sparseEffect_inp_length_le h

theorem sparseStep_out_length_le {w : ℕ} {p : Program} {s s' : SparseState}
    (h : sparseStep w p s = some s') : s'.out.length ≤ s.out.length + 1 := by
  unfold sparseStep at h
  cases hi : p[s.pc]? with
  | none => simp [hi] at h
  | some i =>
      simp [hi] at h
      exact sparseEffect_out_length_le h

theorem sparseRun_inp_length_le {w : ℕ} {p : Program} {t : ℕ}
    {s s' : SparseState} (h : sparseRun w p t s = some s') :
    s'.inp.length ≤ s.inp.length := by
  induction t generalizing s with
  | zero => simp [sparseRun] at h; subst s'; exact le_rfl
  | succ t ih =>
      simp only [sparseRun] at h
      cases hs : sparseStep w p s with
      | none => simp [hs] at h
      | some s₁ =>
        simp [hs] at h
        exact le_trans (ih h) (sparseStep_inp_length_le hs)

theorem sparseRun_out_length_le {w : ℕ} {p : Program} {t : ℕ}
    {s s' : SparseState} (h : sparseRun w p t s = some s') :
    s'.out.length ≤ s.out.length + t := by
  induction t generalizing s with
  | zero => simp [sparseRun] at h; subst s'; omega
  | succ t ih =>
      simp only [sparseRun] at h
      cases hs : sparseStep w p s with
      | none => simp [hs] at h
      | some s₁ =>
        simp [hs] at h
        have hstep := sparseStep_out_length_le hs
        have hrest := ih h
        omega

theorem sparseRun_init_inp_length_le {w : ℕ} {p : Program} {x : List ℕ}
    {t : ℕ} {s : SparseState}
    (h : sparseRun w p t (sparseInitState x) = some s) :
    s.inp.length ≤ x.length := by
  simpa [sparseInitState] using sparseRun_inp_length_le h

theorem sparseRun_init_out_length_le {w : ℕ} {p : Program} {x : List ℕ}
    {t : ℕ} {s : SparseState}
    (h : sparseRun w p t (sparseInitState x) = some s) :
    s.out.length ≤ t := by
  simpa [sparseInitState] using sparseRun_out_length_le h

/-- Uniform bound on the entire serialized sparse state after `t` RAM
instructions. -/
theorem sparseRun_encoded_state_length_le {w : ℕ} {p : Program} {x : List ℕ}
    {t : ℕ} {s : SparseState}
    (h : sparseRun w p t (sparseInitState x) = some s) :
    (encodeSparseState w s).length ≤
      (w + 1) + t * (2 * w + 3) +
        x.length * (w + 1) + t * (w + 1) + 3 := by
  rw [encodeSparseState_length]
  have hm := sparseRun_init_mem_length_le h
  have hi := sparseRun_init_inp_length_le h
  have ho := sparseRun_init_out_length_le h
  have hmm := Nat.mul_le_mul_right (2 * w + 3) hm
  have hii := Nat.mul_le_mul_right (w + 1) hi
  have hoo := Nat.mul_le_mul_right (w + 1) ho
  omega

/-- Cost budget for scanning every currently materialized sparse cell once. -/
def sparseLookupCost (w : ℕ) (m : SparseMemory) : ℕ :=
  m.length * (3 * w + 4)

theorem sparseLookupCost_le_of_length {w t : ℕ} {m : SparseMemory}
    (hm : m.length ≤ t) : sparseLookupCost w m ≤ t * (3 * w + 4) := by
  exact Nat.mul_le_mul_right _ hm

theorem sparseRun_lookupCost_le {w : ℕ} {p : Program} {x : List ℕ}
    {t : ℕ} {s : SparseState}
    (h : sparseRun w p t (sparseInitState x) = some s) :
    sparseLookupCost w s.mem ≤ t * (3 * w + 4) :=
  sparseLookupCost_le_of_length (sparseRun_init_mem_length_le h)

end Lax51Proofs.RamToTM
