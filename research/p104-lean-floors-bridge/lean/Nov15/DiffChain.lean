/-
Difference chaining, lane LEAN-NEXT11, Nov 16. See DiffChain.md.
Source: REBUILD-V2 stage C (cards/WILD/REBUILDKIT/ROUNDLOG.md "V2:" lines): "one helper delivers v_j then
v_k at G_k ⊇ G_j if v_k/q_k − v_j/q_j is pickable in between; keeps j's alpha-chain + k's beta-chain".

Op model: TokenCancel's. Delivery of v into receiver j by helper h = `add j h q` (j += q·h).
(1) `run_recv`: if h is written only by ADDs in a window, its end row is its start row plus the receipt
    `recv` (Σ a·row_source at read time). "Pickable" = the receipt can be made equal to a given vector.
(2) `diff_chain`: if h holds v_j/q_j at the j-delivery (j's alpha-chain), and its receipt between the two
    deliveries is v_k/q_k − v_j/q_j, then j receives v_j, k receives v_k, and h ends holding v_k/q_k,
    exactly the row k's own helper would hold, so k's beta-chain (later clean-up) runs unchanged.
(3) `scale_breaks`: a SCALE of h in the window breaks the rule (the prose needs "h written only by ADDs").

Build:
  lake env lean -o .lake/build/lib/lean/Nov15/TokenCancel.olean Nov15/TokenCancel.lean
  lake env lean Nov15/DiffChain.lean
-/
import Nov15.TokenCancel

set_option linter.unusedSectionVars false

namespace DiffChain
open TokenCancel

variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C]

theorem run_append (s : St K Reg C) (p q : List (Ev K Reg C)) :
    run s (p ++ q) = run (run s p) q := by
  induction p generalizing s with
  | nil => rfl
  | cons e p ih => exact ih (step s e)

/-- `p` is written only by ADDs in `e` (MOVEs and ops on other registers are free). -/
def AddOnly (p : Reg) : Ev K Reg C → Prop
  | .born i _ | .init i _ | .scale i _ _ | .clear i _ | .copy i _ _ => i ≠ p
  | .add _ _ _ _ | .move _ _ => True

/-- What `p` receives in one event. -/
def recvEv (p : Reg) (s : St K Reg C) : Ev K Reg C → (Reg → K)
  | .add i j a _ => if i = p then a • s.row j else 0
  | _ => 0

/-- The receipt of `p` over a window: Σ a·row_source(read time) over the ADDs into `p`. -/
def recv (p : Reg) : St K Reg C → List (Ev K Reg C) → (Reg → K)
  | _, [] => 0
  | s, e :: es => recvEv p s e + recv p (step s e) es

theorem step_recv (p : Reg) (s : St K Reg C) (e : Ev K Reg C) (h : AddOnly p e) :
    (step s e).row p = s.row p + recvEv p s e := by
  cases e with
  | add i j a c =>
    by_cases hi : i = p
    · subst hi; simp [step, recvEv]
    · simp [step, recvEv, hi, Function.update_of_ne (Ne.symm hi)]
  | move i c => simp [step, recvEv]
  | born i c => have : i ≠ p := h; simp [step, recvEv, Function.update_of_ne this.symm]
  | init i c => have : i ≠ p := h; simp [step, recvEv, Function.update_of_ne this.symm]
  | scale i u c => have : i ≠ p := h; simp [step, recvEv, Function.update_of_ne this.symm]
  | clear i c => have : i ≠ p := h; simp [step, recvEv, Function.update_of_ne this.symm]
  | copy i j c => have : i ≠ p := h; simp [step, recvEv, Function.update_of_ne this.symm]

/-- **Receipt law.** -/
theorem run_recv (p : Reg) : ∀ (evs : List (Ev K Reg C)) (s : St K Reg C),
    (∀ e ∈ evs, AddOnly p e) → (run s evs).row p = s.row p + recv p s evs
  | [], s, _ => by simp [run, recv]
  | e :: es, s, h => by
    simp only [run, recv]
    rw [run_recv p es (step s e) (fun e' he' => h e' (List.mem_cons_of_mem _ he')),
      step_recv p s e (h e List.mem_cons_self)]
    abel

/-- **Difference chaining (V2 stage C).** -/
theorem diff_chain (s : St K Reg C) (h j k : Reg) (hjh : j ≠ h) (hkh : k ≠ h)
    (qj qk : K) (hqj : qj ≠ 0) (hqk : qk ≠ 0) (vj vk : Reg → K) (cj ck : C)
    (mid : List (Ev K Reg C)) (hs : s.row h = qj⁻¹ • vj) (hA : ∀ e ∈ mid, AddOnly h e)
    (hpick : recv h (step s (.add j h qj cj)) mid = qk⁻¹ • vk - qj⁻¹ • vj) :
    (step s (.add j h qj cj)).row j = s.row j + vj ∧
      (run s (.add j h qj cj :: mid ++ [.add k h qk ck])).row k =
        (run (step s (.add j h qj cj)) mid).row k + vk ∧
      (run s (.add j h qj cj :: mid ++ [.add k h qk ck])).row h = qk⁻¹ • vk ∧
      ∀ r, r ≠ k → (run s (.add j h qj cj :: mid ++ [.add k h qk ck])).row r =
        (run (step s (.add j h qj cj)) mid).row r := by
  have h1 : (step s (.add j h qj cj)).row h = qj⁻¹ • vj := by
    simp [step, Function.update_of_ne hjh.symm, hs]
  have hmid := run_recv h mid (step s (.add j h qj cj)) hA
  rw [hpick, h1, add_sub_cancel] at hmid
  have hrun : run s (.add j h qj cj :: mid ++ [.add k h qk ck]) =
      step (run (step s (.add j h qj cj)) mid) (.add k h qk ck) := by
    rw [List.cons_append, run, run_append]; rfl
  rw [hrun]
  generalize run (step s (.add j h qj cj)) mid = r at hmid ⊢
  refine ⟨?_, ?_, ?_, ?_⟩
  · simp [step, hs, smul_smul, hqj]
  · simp [step, hmid, smul_smul, hqk]
  · simp [step, Function.update_of_ne hkh.symm, hmid]
  · intro x hx
    simp [step, Function.update_of_ne hx]

/-- **Finding (SCALE in the window).** h = 0 holds v_j/q_j = e_2 (q_j = 1), the window is `h *= 2` plus
a pickup of `e_3 − e_2` (so the literal difference v_k/q_k − v_j/q_j = e_3 − e_2 IS picked), yet k
receives e_3 + e_2, not v_k = e_3. The rule needs h written only by ADDs (or the difference taken
against the scaled row). -/
def sx : St ℚ (Fin 5) Unit :=
  ⟨fun r => if r = 0 then Pi.single 2 1 else if r = 4 then Pi.single 3 1 - Pi.single 2 1 else 0,
   fun _ => some ()⟩

theorem scale_breaks :
    (run sx [.add 1 0 1 (), .scale 0 2 (), .add 0 4 1 (), .add (3 : Fin 5) 0 1 ()]).row 3 =
      Pi.single 3 1 + Pi.single 2 1 := by
  funext x
  fin_cases x <;> simp [run, step, sx] <;> norm_num

end DiffChain

#print axioms DiffChain.run_recv
#print axioms DiffChain.diff_chain
#print axioms DiffChain.scale_breaks
