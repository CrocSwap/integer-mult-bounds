import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMWordTransferMacro20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

open Lax51Proofs.Microcode

def SparseMemory.Normalized (w : ℕ) : SparseMemory → Prop
  | [] => True
  | (a, v) :: m => a < 2 ^ w ∧ v < 2 ^ w ∧ Normalized w m

@[simp] theorem SparseMemory.normalized_nil (w : ℕ) :
    SparseMemory.Normalized w [] := by simp [SparseMemory.Normalized]

theorem SparseMemory.put_normalized {w : ℕ} {m : SparseMemory}
    (hm : m.Normalized w) {a v : ℕ} (ha : a < 2 ^ w) (hv : v < 2 ^ w) :
    (m.put a v).Normalized w := by
  induction m with
  | nil => simp [SparseMemory.put, SparseMemory.Normalized, ha, hv]
  | cons cell m ih =>
      rcases cell with ⟨b, u⟩
      rcases hm with ⟨hb, hu, htail⟩
      by_cases hab : a = b
      · subst b
        simp [SparseMemory.put, SparseMemory.Normalized, ha, hv, htail]
      · simp only [SparseMemory.put, hab, if_false]
        exact ⟨hb, hu, ih htail⟩

theorem SparseMemory.write_normalized (w : ℕ) {m : SparseMemory}
    (hm : m.Normalized w) (a v : ℕ) :
    (m.write w a v).Normalized w := by
  exact ⟨Nat.mod_lt _ (by positivity), Nat.mod_lt _ (by positivity), hm⟩

theorem SparseMemory.normalize_eq_self {w : ℕ} {m : SparseMemory}
    (hm : m.Normalized w) : normalizeSparseMemory w m = m := by
  induction m with
  | nil => rfl
  | cons cell m ih =>
      rcases cell with ⟨a, v⟩
      rcases hm with ⟨ha, hv, htail⟩
      change (a % 2 ^ w, v % 2 ^ w) :: normalizeSparseMemory w m = (a, v) :: m
      rw [Nat.mod_eq_of_lt ha, Nat.mod_eq_of_lt hv, ih htail]

theorem sparseEffect_mem_normalized {w : ℕ} {i : Instr} {s s' : SparseState}
    (hm : s.mem.Normalized w) (h : sparseEffect w i s = some s') :
    s'.mem.Normalized w := by
  cases i <;> simp [sparseEffect] at h
  case read a =>
    cases hin : s.inp with
    | nil => simp [hin] at h
    | cons v inp =>
      simp [hin] at h
      subst s'
      exact SparseMemory.write_normalized w hm a v
  all_goals
    subst s'
    first
    | exact SparseMemory.write_normalized _ hm _ _
    | exact hm

theorem sparseStep_mem_normalized {w : ℕ} {p : Program} {s s' : SparseState}
    (hm : s.mem.Normalized w) (h : sparseStep w p s = some s') :
    s'.mem.Normalized w := by
  unfold sparseStep at h
  cases hi : p[s.pc]? with
  | none => simp [hi] at h
  | some i =>
      simp [hi] at h
      exact sparseEffect_mem_normalized hm h

theorem sparseRun_mem_normalized {w : ℕ} {p : Program} {t : ℕ}
    {s s' : SparseState} (hm : s.mem.Normalized w)
    (h : sparseRun w p t s = some s') : s'.mem.Normalized w := by
  induction t generalizing s with
  | zero =>
      simp [sparseRun] at h
      subst s'
      exact hm
  | succ t ih =>
      simp only [sparseRun] at h
      cases hs : sparseStep w p s with
      | none => simp [hs] at h
      | some s₁ =>
        simp [hs] at h
        exact ih (sparseStep_mem_normalized hm hs) h

theorem sparseRun_init_mem_normalized {w : ℕ} {p : Program} {x : List ℕ}
    {t : ℕ} {s : SparseState}
    (h : sparseRun w p t (sparseInitState x) = some s) :
    s.mem.Normalized w :=
  sparseRun_mem_normalized (SparseMemory.normalized_nil w) h

theorem decodeSparseMemory_encode_exact {w : ℕ} {m : SparseMemory}
    (hm : m.Normalized w) (suffix : List SparseSymbol) :
    decodeSparseMemory w m.length (encodeSparseMemory w m ++ suffix) =
      (m, suffix) := by
  rw [decodeSparseMemory_encode, SparseMemory.normalize_eq_self hm]

end Lax51Proofs.RamToTM
