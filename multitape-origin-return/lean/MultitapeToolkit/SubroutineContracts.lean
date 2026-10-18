import MultitapeToolkit.Trace
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Data.Fintype.Prod

set_option autoImplicit false

/-!
# Fixed finite-stage subroutine scheduling with exact handoff charges

A scheduler for `k+1` literal multitape programs has finite control
`Fin (k+1) × Q`.  The number of stages and their transition tables are fixed
before the input.  A component halt executes one stationary handoff to the
next fixed entry state; the last component halt is the scheduler's true halt.

The assembly theorem requires actual completed component executions with
literal head/cell equality at each boundary.  It charges the sum of their
actual transitions plus exactly `k` handoffs.  It does not implement an absent
row router, dynamic recursive call stack, or input conversion.
-/

namespace MultitapeToolkit.Absolute.Subroutines

open scoped BigOperators
open MultitapeToolkit.Locality

variable {ι Γ Q : Type*} [Inhabited Γ]
  [Fintype ι] [Fintype Γ] [Fintype Q]

/-- The next control index is bounded by the fixed stage count. -/
def nextStage {k : ℕ} (i : Fin (k + 1)) (h : i.val < k) : Fin (k + 1) :=
  ⟨i.val + 1, by omega⟩

/-- The same physical tapes, with a finite stage index attached to control. -/
def stageCfg {k : ℕ} (i : Fin (k + 1)) (c : Config ι Γ Q) :
    Config ι Γ (Fin (k + 1) × Q) :=
  ⟨(i, c.state), c.head, c.cell⟩

/-- A concrete fixed finite scheduler; no dispatch oracle or unbounded program
counter is part of its transition semantics. -/
def scheduler {k : ℕ} (stages : Fin (k + 1) → Program ι Γ Q)
    (entry : Fin (k + 1) → Q) : Program ι Γ (Fin (k + 1) × Q) where
  transition iq scanned :=
    match (stages iq.1).transition iq.2 scanned with
    | some (q, actions) => some ((iq.1, q), actions)
    | none =>
      if h : iq.1.val < k then
        some ((nextStage iq.1 h, entry (nextStage iq.1 h)),
          fun tape => (scanned tape, .stay))
      else none

omit [Inhabited Γ] in
 theorem scheduler_step {k : ℕ} (stages : Fin (k + 1) → Program ι Γ Q)
    (entry : Fin (k + 1) → Q) (i : Fin (k + 1))
    {c d : Config ι Γ Q} (h : step (stages i) c = some d) :
    step (scheduler stages entry) (stageCfg i c) = some (stageCfg i d) := by
  cases ht : (stages i).transition c.state (fun tape => c.cell tape (c.head tape)) with
  | none => simp [step, ht] at h
  | some p =>
    have hd : d =
      { state := p.1
        head := fun tape => c.head tape + moveOffset (p.2 tape).2
        cell := fun tape x => if x = c.head tape then (p.2 tape).1 else c.cell tape x } := by
      simpa [step, ht] using h.symm
    subst d
    cases p
    simp [step, scheduler, stageCfg, ht]
    all_goals rfl

omit [Inhabited Γ] in
 theorem scheduler_stage_runs {k : ℕ} (stages : Fin (k + 1) → Program ι Γ Q)
    (entry : Fin (k + 1) → Q) (i : Fin (k + 1))
    {n : ℕ} {c d : Config ι Γ Q} (h : Runs (stages i) n c d) :
    Runs (scheduler stages entry) n (stageCfg i c) (stageCfg i d) := by
  induction h with
  | refl => exact .refl _
  | cons hs hr ih => exact .cons (scheduler_step stages entry i hs) ih

omit [Inhabited Γ] in
private theorem halted_table (P : Program ι Γ Q) (c : Config ι Γ Q) (h : Halts P c) :
    P.transition c.state (fun tape => c.cell tape (c.head tape)) = none := by
  cases ht : P.transition c.state (fun tape => c.cell tape (c.head tape)) with
  | none => rfl
  | some p => simp [Halts, step, ht] at h

omit [Inhabited Γ] in
/-- The handoff is one real transition and preserves every head and every cell,
including arbitrary dirty tapes that are not owned by either component. -/
 theorem scheduler_handoff {k : ℕ} (stages : Fin (k + 1) → Program ι Γ Q)
    (entry : Fin (k + 1) → Q) (i : Fin (k + 1)) (hi : i.val < k)
    (c : Config ι Γ Q) (hh : Halts (stages i) c) :
    step (scheduler stages entry) (stageCfg i c) =
      some (stageCfg (nextStage i hi) ⟨entry (nextStage i hi), c.head, c.cell⟩) := by
  have ht := halted_table (stages i) c hh
  simp only [step, scheduler, stageCfg, ht, dif_pos hi, Option.map_some]
  congr 1
  apply Config.ext
  · rfl
  · funext tape; simp [moveOffset]
  · funext tape x
    by_cases hx : x = c.head tape
    · simp [hx]
    · simp [hx]

omit [Inhabited Γ] in
 theorem scheduler_last_halts {k : ℕ} (stages : Fin (k + 1) → Program ι Γ Q)
    (entry : Fin (k + 1) → Q) (c : Config ι Γ Q)
    (hh : Halts (stages (Fin.last k)) c) :
    Halts (scheduler stages entry) (stageCfg (Fin.last k) c) := by
  have ht := halted_table (stages (Fin.last k)) c hh
  simp [Halts, step, scheduler, stageCfg, ht]

/-- Literal boundary compatibility includes both absolute head coordinates and
all tape cells; no descriptor, copy, or re-positioning is silently assumed. -/
def Boundaries {k : ℕ} (begin finish : Fin (k + 1) → Config ι Γ Q) : Prop :=
  ∀ (i : Fin (k + 1)) (hi : i.val < k),
    (begin (nextStage i hi)).head = (finish i).head ∧
      (begin (nextStage i hi)).cell = (finish i).cell

private def segmentIndex {k : ℕ} (i : Fin (k + 1)) (r : ℕ)
    (h : i.val + r = k) (j : Fin (r + 1)) : Fin (k + 1) :=
  ⟨i.val + j.val, by omega⟩

private def segmentSum {k : ℕ} (times : Fin (k + 1) → ℕ) (i : Fin (k + 1))
    (r : ℕ) (h : i.val + r = k) : ℕ :=
  ∑ j : Fin (r + 1), times (segmentIndex i r h j)

private theorem segmentIndex_zero {k : ℕ} (i : Fin (k + 1)) (r : ℕ)
    (h : i.val + r = k) : segmentIndex i r h 0 = i := by
  apply Fin.ext
  simp [segmentIndex]

private theorem segmentSum_succ {k : ℕ} (times : Fin (k + 1) → ℕ)
    (i : Fin (k + 1)) (r : ℕ) (h : i.val + (r + 1) = k) (hi : i.val < k)
    (hn : (nextStage i hi).val + r = k) :
    segmentSum times i (r + 1) h = times i + segmentSum times (nextStage i hi) r hn := by
  unfold segmentSum
  rw [Fin.sum_univ_succ]
  rw [segmentIndex_zero]
  congr 1
  apply Finset.sum_congr rfl
  intro j _
  congr 1
  apply Fin.ext
  simp [segmentIndex, nextStage]
  omega

private theorem scheduler_from {k : ℕ} (stages : Fin (k + 1) → Program ι Γ Q)
    (entry : Fin (k + 1) → Q) (begin finish : Fin (k + 1) → Config ι Γ Q)
    (times : Fin (k + 1) → ℕ)
    (hentry : ∀ i, (begin i).state = entry i)
    (hrun : ∀ i, Runs (stages i) (times i) (begin i) (finish i))
    (hhalt : ∀ i, Halts (stages i) (finish i))
    (hb : Boundaries begin finish)
    (r : ℕ) (i : Fin (k + 1)) (h : i.val + r = k) :
    Runs (scheduler stages entry) (segmentSum times i r h + r)
      (stageCfg i (begin i)) (stageCfg (Fin.last k) (finish (Fin.last k))) := by
  induction r generalizing i with
  | zero =>
    have hi : i = Fin.last k := by apply Fin.ext; simpa using h
    subst i
    have hsum : segmentSum times (Fin.last k) 0 h = times (Fin.last k) := by
      change (∑ j : Fin 1, times (segmentIndex (Fin.last k) 0 h j)) = _
      rw [Fin.sum_univ_one]
      exact congrArg times (segmentIndex_zero (Fin.last k) 0 h)
    simpa only [hsum, Nat.add_zero] using
      scheduler_stage_runs stages entry (Fin.last k) (hrun (Fin.last k))
  | succ r ih =>
    have hi : i.val < k := by omega
    have hn : (nextStage i hi).val + r = k := by simp only [nextStage]; omega
    have htail := ih (nextStage i hi) hn
    have hfirst := scheduler_stage_runs stages entry i (hrun i)
    have hboundary : (⟨entry (nextStage i hi), (finish i).head, (finish i).cell⟩ :
        Config ι Γ Q) = begin (nextStage i hi) := by
      apply Config.ext
      · exact (hentry _).symm
      · exact (hb i hi).1.symm
      · exact (hb i hi).2.symm
    have hh := scheduler_handoff stages entry i hi (finish i) (hhalt i)
    rw [hboundary] at hh
    have hhand : Runs (scheduler stages entry) 1 (stageCfg i (finish i))
        (stageCfg (nextStage i hi) (begin (nextStage i hi))) := .cons hh (.refl _)
    have hfull := Trace.runs_trans (scheduler stages entry)
      (Trace.runs_trans (scheduler stages entry) hfirst hhand) htail
    rw [segmentSum_succ times i r h hi hn]
    convert hfull using 1 <;> omega

/-- Sufficient universal assembly for a fixed list of completed physical
subroutines.  The exact cost is the sum of actual stage costs plus one transition
per boundary, with no silent tape reset, allocation, or recursive routing. -/
 theorem scheduler_assembly {k : ℕ} (stages : Fin (k + 1) → Program ι Γ Q)
    (entry : Fin (k + 1) → Q) (begin finish : Fin (k + 1) → Config ι Γ Q)
    (times : Fin (k + 1) → ℕ)
    (hentry : ∀ i, (begin i).state = entry i)
    (hrun : ∀ i, Runs (stages i) (times i) (begin i) (finish i))
    (hhalt : ∀ i, Halts (stages i) (finish i)) (hb : Boundaries begin finish) :
    Runs (scheduler stages entry) ((∑ i, times i) + k)
      (stageCfg 0 (begin 0)) (stageCfg (Fin.last k) (finish (Fin.last k))) ∧
    Halts (scheduler stages entry) (stageCfg (Fin.last k) (finish (Fin.last k))) := by
  constructor
  · have h := scheduler_from stages entry begin finish times hentry hrun hhalt hb k 0 (by simp)
    simpa [segmentSum, segmentIndex] using h
  · exact scheduler_last_halts stages entry _ (hhalt _)

/-- Actual stage budgets aggregate additively, with all `k` administrative
transitions charged even when one or more stages take zero transitions. -/
 theorem scheduler_budget {k : ℕ} (times budgets : Fin (k + 1) → ℕ)
    (h : ∀ i, times i ≤ budgets i) :
    (∑ i, times i) + k ≤ (∑ i, budgets i) + k :=
  Nat.add_le_add_right (Finset.sum_le_sum (fun i _ => h i)) k

/-- Local affine volume invoices aggregate with every fixed-stage dispatch paid.
The volume is an actual supplied stage-size bound; no partition or routing is
inferred from this numerical inequality. -/
 theorem scheduler_affine_volume_bound {k : ℕ} (times volumes : Fin (k + 1) → ℕ)
    (A B : ℕ) (h : ∀ i, times i ≤ A * volumes i + B) :
    (∑ i, times i) + k ≤ A * (∑ i, volumes i) + B * (k + 1) + k := by
  calc
    (∑ i, times i) + k ≤ (∑ i, (A * volumes i + B)) + k :=
      scheduler_budget times (fun i => A * volumes i + B) h
    _ = A * (∑ i, volumes i) + B * (k + 1) + k := by
      simp [Finset.sum_add_distrib, ← Finset.mul_sum, Nat.mul_comm]
omit [Inhabited Γ] in
/-- A stationary spectator-tape certificate survives every scheduler branch. -/
 theorem scheduler_idleOn {k : ℕ} (stages : Fin (k + 1) → Program ι Γ Q)
    (entry : Fin (k + 1) → Q) (tape : ι)
    (hidle : ∀ i, Trace.IdleOn (stages i) tape) :
    Trace.IdleOn (scheduler stages entry) tape := by
  rintro ⟨i, q⟩ scanned next actions h
  cases ht : (stages i).transition q scanned with
  | none =>
    by_cases hi : i.val < k
    · have heq : ((nextStage i hi, entry (nextStage i hi)),
          fun tape => (scanned tape, Move.stay)) = (next, actions) := by
        simpa [scheduler, ht, hi] using h
      have ha : (fun tape => (scanned tape, Move.stay)) = actions := congrArg Prod.snd heq
      rw [← ha]
      exact ⟨rfl, rfl⟩
    · simp [scheduler, ht, hi] at h
  | some p =>
    rcases p with ⟨q', a⟩
    have heq : ((i, q'), a) = (next, actions) := by simpa [scheduler, ht] using h
    have ha : a = actions := congrArg Prod.snd heq
    rw [← ha]
    exact hidle i q scanned q' a ht

/-- Every witnessed execution prefix preserves arbitrary dirty spectator data
and its absolute head position, irrespective of ancestor length. -/
 theorem scheduler_preserves_spectator {k : ℕ} (stages : Fin (k + 1) → Program ι Γ Q)
    (entry : Fin (k + 1) → Q) (tape : ι)
    (hidle : ∀ i, Trace.IdleOn (stages i) tape)
    {n : ℕ} {c d : Config ι Γ (Fin (k + 1) × Q)}
    (hrun : Runs (scheduler stages entry) n c d) :
    d.head tape = c.head tape ∧ ∀ x, d.cell tape x = c.cell tape x :=
  Trace.runs_idle_tape (scheduler stages entry) tape
    (scheduler_idleOn stages entry tape hidle) hrun

end MultitapeToolkit.Absolute.Subroutines




