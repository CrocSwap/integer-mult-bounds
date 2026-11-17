/-
SwapWord, lane LEAN-NEXT10, Nov 16. See SwapWord.md.

The SWAPBUILD edit (cards/WILD/BIG/SWAPBUILD, from BIG/TOKENRANK TR2): at a moment when helper h's row
is exactly e_h, inject `j += c·h` (data: c = −1, just before the native's own `h += j`, so the pair is
the swap `j -= h; h += j`). General facts in TokenCancel's op model:
* `run_diff`: the run is affine in the rows; the difference of two runs with equal locations is the
  run of the difference with births read as INITs.
* `inject`: the injection changes the final rows ONLY in column h: final' r = final r + δ r • e_h.
* `inject_two`: two injections (457 → 242, 461 → X10) change the final rows only in columns h1, h2.
* `inject_col`: every final row is unchanged on every column k ≠ h, for every register (non-V-enders included).
* `absorb`: the debt is absorbed by the V mix: if e_h lies in the span of the V targets (h ends at V
  with target e_h), the non-V-enders end on target, the original V-ender rows lie in that span and
  targets are independent, then the edited run has a V mix iff it is loss-free.

Build (imports the RankLawC olean; see RankLawC.lean for the chain):
  lake env lean -o .lake/build/lib/lean/Nov15/RankLawC.olean Nov15/RankLawC.lean
  lake env lean Nov15/SwapWord.lean
-/
import Nov15.RankLawC

set_option linter.unusedSectionVars false

namespace SwapWord
open Submodule Module TokenCancel RankLaw

variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C]

/-- Births read as INITs (a birth writes the same e_i in both runs, so the difference row is 0). -/
def unborn : Ev K Reg C → Ev K Reg C
  | .born i c => .init i c
  | e => e

theorem run_append (s : St K Reg C) (p q : List (Ev K Reg C)) :
    run s (p ++ q) = run (run s p) q := by
  induction p generalizing s with
  | nil => rfl
  | cons e p ih => exact ih (step s e)

lemma upd_sub (f g : Reg → Reg → K) (i : Reg) (a b : Reg → K) :
    Function.update f i a - Function.update g i b = Function.update (f - g) i (a - b) := by
  funext k; by_cases hk : k = i
  · subst hk; simp
  · simp [Function.update_of_ne hk]

/-- One step of the difference. -/
theorem step_diff (s t : St K Reg C) (hl : s.loc = t.loc) (e : Ev K Reg C) :
    (step t e).loc = (step s e).loc ∧
      (step t e).row - (step s e).row = (step ⟨t.row - s.row, s.loc⟩ (unborn e)).row := by
  cases e with
  | born i c => exact ⟨by simp [step, hl], by simp [step, unborn, upd_sub]⟩
  | init i c => exact ⟨by simp [step, hl], by simp [step, unborn, upd_sub]⟩
  | move i c => exact ⟨by simp [step, hl], by simp [step, unborn]⟩
  | add i j a c =>
    refine ⟨by simp [step, hl], ?_⟩
    simp only [step, unborn, upd_sub, Pi.sub_apply]
    congr 1; rw [smul_sub]; abel
  | scale i u c => exact ⟨by simp [step, hl], by simp [step, unborn, upd_sub, smul_sub]⟩
  | clear i c => exact ⟨by simp [step, hl], by simp [step, unborn, upd_sub]⟩
  | copy i j c => exact ⟨by simp [step, hl], by simp [step, unborn, upd_sub]⟩

/-- **Difference law.** Two runs of the same events from states with equal locations differ by the
run of the difference state (births read as INITs). -/
theorem run_diff : ∀ (evs : List (Ev K Reg C)) (s t : St K Reg C), s.loc = t.loc →
    (run t evs).loc = (run s evs).loc ∧
      (run t evs).row - (run s evs).row = (run ⟨t.row - s.row, s.loc⟩ (evs.map unborn)).row
  | [], s, t, hl => ⟨hl.symm, rfl⟩
  | e :: es, s, t, hl => by
    obtain ⟨h1, h2⟩ := step_diff s t hl e
    have ih := run_diff es (step s e) (step t e) h1.symm
    refine ⟨ih.1, ?_⟩
    simp only [run, List.map_cons]
    rw [ih.2]
    have hst : (⟨(step t e).row - (step s e).row, (step s e).loc⟩ : St K Reg C) =
        step ⟨t.row - s.row, s.loc⟩ (unborn e) := by
      cases e <;> simp only [step, unborn] at h2 ⊢ <;> rw [h2]
    rw [hst]

/-- With no births, every op keeps all rows inside a fixed subspace P. -/
theorem rows_in_run (P : Submodule K (Reg → K)) :
    ∀ (evs : List (Ev K Reg C)) (d : St K Reg C), (∀ r, d.row r ∈ P) →
      ∀ r, (run d (evs.map unborn)).row r ∈ P
  | [], d, hd => hd
  | e :: es, d, hd => by
    simp only [List.map_cons, run]
    refine rows_in_run P es _ (fun r => ?_)
    by_cases hr : r = (match e with
      | .born i _ | .init i _ | .move i _ | .add i _ _ _ | .scale i _ _ | .clear i _ | .copy i _ _ => i)
    · cases e <;> simp only [step, unborn] at hr ⊢ <;> subst hr <;>
        simp [P.zero_mem, P.add_mem, P.smul_mem, hd]
    · cases e <;> simp only [step, unborn] at hr ⊢ <;> simp [Function.update_of_ne hr, hd]

/-- **Injection law.** If h's row is exactly e_h after the prefix p, injecting `j += c·h` there
changes the final rows only by multiples of e_h. -/
theorem inject (s : St K Reg C) (p q : List (Ev K Reg C)) (h j : Reg) (c : K) (ch : C)
    (hrow : (run s p).row h = Pi.single h 1) :
    ∃ δ : Reg → K, ∀ r, (run s (p ++ .add j h c ch :: q)).row r =
      (run s (p ++ q)).row r + δ r • (Pi.single h 1 : Reg → K) := by
  set s0 := run s p
  set t := step s0 (.add j h c ch)
  have hl : s0.loc = t.loc := rfl
  obtain ⟨-, hd⟩ := run_diff q s0 t hl
  have hin : ∀ r, (t.row - s0.row) r ∈ K ∙ (Pi.single h 1 : Reg → K) := by
    intro r
    by_cases hr : r = j
    · subst hr; simp [t, step, hrow, mem_span_singleton]
    · simp [t, step, Function.update_of_ne hr]
  have hall := rows_in_run (K ∙ (Pi.single h 1 : Reg → K)) q ⟨t.row - s0.row, s0.loc⟩ hin
  have : ∀ r, ∃ a : K, a • (Pi.single h 1 : Reg → K) =
      (run t q).row r - (run s0 q).row r := by
    intro r
    have e := congrFun hd r
    rw [Pi.sub_apply] at e
    rw [e]; exact mem_span_singleton.1 (hall r)
  choose δ hδ using this
  refine ⟨δ, fun r => ?_⟩
  rw [run_append, run_append]
  change (run t q).row r = _
  rw [← sub_add_cancel ((run t q).row r) ((run s0 q).row r), ← hδ r, add_comm]

/-- Column form: every final row (non-V-enders included) is unchanged on every column k ≠ h. -/
theorem inject_col (s : St K Reg C) (p q : List (Ev K Reg C)) (h j : Reg) (c : K) (ch : C)
    (hrow : (run s p).row h = Pi.single h 1) (r k : Reg) (hk : k ≠ h) :
    (run s (p ++ .add j h c ch :: q)).row r k = (run s (p ++ q)).row r k := by
  obtain ⟨δ, hδ⟩ := inject s p q h j c ch hrow
  rw [hδ r]; simp [hk]

/-- **Two injections** (the SWAPBUILD "both" word: 457 → 242, then 461 → X10). Hypotheses: h1 = e_h1
at the first point of the unedited prefix, and h2 = e_h2 at the second point of the once-edited word. -/
theorem inject_two (s : St K Reg C) (p1 q1 q2 : List (Ev K Reg C)) (h1 j1 h2 j2 : Reg) (c1 c2 : K)
    (ch1 ch2 : C)
    (hrow1 : (run s p1).row h1 = Pi.single h1 1)
    (hrow2 : (run s (p1 ++ .add j1 h1 c1 ch1 :: q1)).row h2 = Pi.single h2 1) :
    ∃ δ1 δ2 : Reg → K, ∀ r,
      (run s (p1 ++ .add j1 h1 c1 ch1 :: q1 ++ .add j2 h2 c2 ch2 :: q2)).row r =
        (run s (p1 ++ q1 ++ q2)).row r + δ1 r • (Pi.single h1 1 : Reg → K) +
          δ2 r • (Pi.single h2 1 : Reg → K) := by
  obtain ⟨δ2, hδ2⟩ := inject s (p1 ++ .add j1 h1 c1 ch1 :: q1) q2 h2 j2 c2 ch2 hrow2
  obtain ⟨δ1, hδ1⟩ := inject s p1 (q1 ++ q2) h1 j1 c1 ch1 hrow1
  refine ⟨δ1, δ2, fun r => ?_⟩
  rw [hδ2 r]
  have e1 : p1 ++ Ev.add j1 h1 c1 ch1 :: q1 ++ q2 = p1 ++ Ev.add j1 h1 c1 ch1 :: (q1 ++ q2) := by simp
  rw [e1, hδ1 r, List.append_assoc]

/-- Two-column form: every final row is unchanged on every column outside {h1, h2}. -/
theorem inject_two_col (s : St K Reg C) (p1 q1 q2 : List (Ev K Reg C)) (h1 j1 h2 j2 : Reg)
    (c1 c2 : K) (ch1 ch2 : C)
    (hrow1 : (run s p1).row h1 = Pi.single h1 1)
    (hrow2 : (run s (p1 ++ .add j1 h1 c1 ch1 :: q1)).row h2 = Pi.single h2 1)
    (r k : Reg) (hk1 : k ≠ h1) (hk2 : k ≠ h2) :
    (run s (p1 ++ .add j1 h1 c1 ch1 :: q1 ++ .add j2 h2 c2 ch2 :: q2)).row r k =
      (run s (p1 ++ q1 ++ q2)).row r k := by
  obtain ⟨δ1, δ2, hδ⟩ := inject_two s p1 q1 q2 h1 j1 h2 j2 c1 c2 ch1 ch2 hrow1 hrow2
  rw [hδ r]; simp [hk1, hk2]

/-- **The debt is absorbed by the V mix.** Let `evs` be the edited (hub-deleted) word and `X0` the
unedited end rows. Suppose the edited end rows differ from X0 only along e_h (`inject`), the
non-V-enders end on target (the TR2 column condition, data), the unedited V-ender rows lie in
B = span V targets, e_h ∈ B (h ends at V with target e_h) and B ⊓ N = ⊥. Then the edited run has a
V mix iff it is loss-free. -/
theorem absorb [Fintype Reg] (z V : C) (s : St K Reg C) (T : Finset Reg) (evs : List (Ev K Reg C))
    (hL : Legal z V s evs) (hN : ∀ e ∈ evs, NZ e) (hG : Good s T) (hS : Sp s = TS T)
    (Rf : Reg → Reg → K) (G1 : Finset Reg) (h : Reg) (X0 : Reg → Reg → K) (δ : Reg → K)
    (hX : ∀ r, (run s evs).row r = X0 r + δ r • (Pi.single h 1 : Reg → K))
    (hNon : ∀ r ∉ G1, (run s evs).row r = Rf r)
    (hTgt : span K (Set.range Rf) = TS (tokRun T evs))
    (hX0 : ∀ g ∈ G1, X0 g ∈ span K (Rf '' (G1 : Set Reg)))
    (he : (Pi.single h 1 : Reg → K) ∈ span K (Rf '' (G1 : Set Reg)))
    (hBN : span K (Rf '' (G1 : Set Reg)) ⊓ span K (Rf '' (G1 : Set Reg)ᶜ) = ⊥) :
    VMix (run s evs).row Rf G1 ↔ ¬ Loss s evs := by
  rw [RankLawC.rank_law_indep z V s T evs hL hN hG hS Rf G1 hNon hTgt hBN]
  refine ⟨And.left, fun hl => ⟨hl, fun g hg => ?_⟩⟩
  rw [hX g]; exact add_mem (hX0 g hg) (smul_mem _ _ he)

end SwapWord

#print axioms SwapWord.absorb
#print axioms SwapWord.inject_two_col
#print axioms SwapWord.inject_col
#print axioms RankLawC.rank_law_proj
#print axioms RankLawC.rank_law_of_gen
