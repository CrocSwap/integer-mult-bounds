/-
UniCaller7113Facts (lane UNI-L2L3, Nov 19).  L2 of the unification plan: `CallerFacts` for the #7113 17-stage caller block, by `decide` on its data
(pattern BankPrem.consts7761 / BankCallerGen.consts7786).  DATA: SafeRungsPrice.Tcal/Pcal = MONOCALLER/invoice.json caller_7113 (events-recount control True).
Records (kernel, decide/norm_num): block data; 17 calls; Mn = 400 = 104*2 + 96*2 (8 B-port X + 96 X2 | 104 Y rows); 17*400 = 6800 mains;
the block is NOT in the CallerGen family: at s = 1 the K = 17 sign condition fails by exactly 13, so the shipped .00952721 banner does not apply to 7113 words.
Kernel only.
-/
import Nov15.BankCallerGen

namespace UniCaller7113
open SafeRungsPrice BankCallerGen

/-- decidable facts of the 7113 caller block (T = root targets, P = caller paid rows, L calls). -/
structure CallerFacts (T P : List (ℕ × ℕ)) (L : ℕ) : Prop where
  hT : T = [(9, 416), (17, 416), (25, 416), (33, 416), (41, 416), (49, 416), (57, 416), (65, 416), (73, 208), (137, 208)]
  hP : P = [(1, 384), (8, 656), (9, 32), (16, 416), (24, 416), (32, 416), (40, 416), (48, 416), (56, 416), (64, 208)]
  hL : L = 17
  hMn : 400 = 104 * 2 + 96 * 2
  hmains : L * 400 = 6800
  -- integer mass at s = 1: sum rank*count; 7113 exceeds 17 x (per-call banked block) by exactly 13
  hS1 : (T.map fun p => p.1 * p.2).sum + 17 * (P1.map fun p => p.1 * p.2).sum
        = (P.map fun p => p.1 * p.2).sum + 17 * (T1.map fun p => p.1 * p.2).sum + 13

theorem callerFacts7113 : CallerFacts Tcal Pcal 17 := by
  refine ⟨rfl, rfl, rfl, by decide, by decide, ?_⟩
  decide

/-- the 7113 block violates the CallerGen sign condition at s = 1 (K = 17): cdat T - cdat P = 17 (cdat T1 - cdat P1) + 13. -/
theorem not_callergen_family7113 :
    17 * (cdat 1 T1 - cdat 1 P1) < cdat 1 Tcal - cdat 1 Pcal := by
  simp only [cdat, T1, P1, Tcal, Pcal, List.map_cons, List.map_nil, List.sum_cons, List.sum_nil, Real.rpow_one]
  norm_num

theorem not_callergen_hTP7113 :
    ¬ ∀ s : ℝ, 0 ≤ s → s ≤ 1 → cdat s Tcal - cdat s Pcal ≤ (17 : ℕ) * (cdat s T1 - cdat s P1) := by
  intro h
  have := h 1 (by norm_num) le_rfl
  have h2 := not_callergen_family7113
  push_cast at this
  linarith

end UniCaller7113
#print axioms UniCaller7113.callerFacts7113
#print axioms UniCaller7113.not_callergen_hTP7113
