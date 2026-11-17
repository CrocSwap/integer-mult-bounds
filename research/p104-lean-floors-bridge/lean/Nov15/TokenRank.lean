/-
BIG-TOKENRANK TR1 (box law), the swap canceller, "the regress stops", and the TR3/TR4 cut lemma.
Lane LEAN-NEXT8, Nov 16. Source: cards/WILD/BIG/TOKENRANK/THEORY.md (+ RESULT.md §b). See TokenRank.md.

Part A/B use ExportLaw's one-chart event model (arrive / born / add / scale / depart / clear / copy, rows in
initial-row coordinates, from the empty state). Part C uses TokenCancel's multi-chart model (events carry
their chart; `move`).

Build: imports the oleans of Nov15/ExportLaw.lean and Nov15/TokenCancel.lean:
  lake env lean -o .lake/build/lib/lean/Nov15/ExportLaw.olean Nov15/ExportLaw.lean
  lake env lean -o .lake/build/lib/lean/Nov15/TokenCancel.olean Nov15/TokenCancel.lean
  lake env lean Nov15/TokenRank.lean
-/
import Nov15.ExportLaw
import Nov15.TokenCancel
import Mathlib.LinearAlgebra.Dual.Lemmas

open Finset Module Submodule

set_option linter.unusedSectionVars false

namespace TokenRank

/-! ## Part A. TR1, the box law (one chart c) -/
section TR1
open ExportLaw
variable {K Reg : Type*} [Field K] [Fintype Reg] [DecidableEq Reg]

/-- final rows at c (the enders' rows), one per present register -/
noncomputable def finals (evs : List (Ev K Reg)) : List (Reg → K) :=
  (run start evs).pres.toList.map (run start evs).row

/-- exits of c: departure rows, CLEARed (and COPY-overwritten) rows, final rows of enders -/
noncomputable def exits (evs : List (Ev K Reg)) : List (Reg → K) := removed start evs ++ finals evs

lemma mem_finals {evs : List (Ev K Reg)} {v : Reg → K} :
    v ∈ finals evs ↔ v ∈ cur (run start evs) := by
  simp [finals, cur]

lemma removed_sub_held : ∀ (s : St K Reg) (evs : List (Ev K Reg)), Legal s evs →
    ∀ v ∈ removed s evs, v ∈ held s evs
  | _, [], _, v, hv => by simp [removed] at hv
  | s, ev :: evs, ⟨hev, hL⟩, v, hv => by
    simp only [removed, List.mem_append] at hv
    rcases hv with hv | hv
    · left
      cases ev <;> simp only [remBy, List.mem_singleton, List.not_mem_nil] at hv
      all_goals first
        | (subst hv; exact ⟨_, by simpa [LegalEv] using hev, rfl⟩)
        | (subst hv; exact ⟨_, hev.1, rfl⟩)
    · exact Or.inr (removed_sub_held _ evs hL v hv)

lemma entRows_sub_held : ∀ (s : St K Reg) (evs : List (Ev K Reg)), Legal s evs →
    ∀ v ∈ entRows evs, v ∈ held s evs
  | _, [], _, v, hv => by simp [entRows] at hv
  | s, ev :: evs, ⟨_, hL⟩, v, hv => by
    cases ev with
    | arrive i w =>
      simp only [entRows, List.mem_cons] at hv
      rcases hv with rfl | hv
      · exact Or.inr (cur_sub_held _ evs ⟨i, by simp [step], by simp [step]⟩)
      · exact Or.inr (entRows_sub_held _ evs hL v hv)
    | born b =>
      simp only [entRows, List.mem_cons] at hv
      rcases hv with rfl | hv
      · exact Or.inr (cur_sub_held _ evs ⟨b, by simp [step], by simp [step]⟩)
      · exact Or.inr (entRows_sub_held _ evs hL v hv)
    | add _ _ _ => exact Or.inr (entRows_sub_held _ evs hL v hv)
    | scale _ _ => exact Or.inr (entRows_sub_held _ evs hL v hv)
    | depart _ => exact Or.inr (entRows_sub_held _ evs hL v hv)
    | clear _ => exact Or.inr (entRows_sub_held _ evs hL v hv)
    | copy _ _ => exact Or.inr (entRows_sub_held _ evs hL v hv)

/-- **TR1(a), span part.** span(exits) = span(entries), for every legal word from the empty state
(CLEAR and even COPY allowed). -/
theorem TR1_span (evs : List (Ev K Reg)) (hL : Legal start evs) :
    span K {v | v ∈ exits evs} = span K {v | v ∈ entRows evs} := by
  apply le_antisymm
  · rw [Submodule.span_le]
    have hS := forward_span (span K {v | v ∈ entRows evs}) start evs hL (by simp [cur, start])
      (fun v hv => Submodule.subset_span hv)
    intro v hv
    simp only [exits, Set.mem_ofPred_eq, List.mem_append] at hv
    rcases hv with hv | hv
    · exact hS (removed_sub_held _ _ hL v hv)
    · exact hS (final_sub_held _ _ (mem_finals.1 hv))
  · rw [Submodule.span_le]
    intro v hv
    have h1 := E1_reverse start evs hL
    have h2 : v ∈ span K (held start evs) := Submodule.subset_span (entRows_sub_held _ _ hL v hv)
    refine (h1.trans (sup_le ?_ ?_)) h2
    · exact Submodule.span_mono fun w hw => by
        simp only [exits, Set.mem_ofPred_eq, List.mem_append]; exact Or.inr (mem_finals.2 hw)
    · exact Submodule.span_mono fun w hw => by
        simp only [exits, Set.mem_ofPred_eq, List.mem_append]; exact Or.inl hw

lemma removed_length : ∀ (s : St K Reg) (evs : List (Ev K Reg)),
    (removed s evs).length = nDep univ evs + nClr evs
  | _, [] => rfl
  | s, ev :: evs => by
    have ih := removed_length (step s ev) evs
    cases ev <;> simp [removed, remBy, nDep, nClr, ih] <;> omega

/-- **TR1(a), count part, corrected.** |exits| = |entries| + #(CLEAR/COPY events). The card's
"|exits| = |entries|" holds only without CLEAR (see `TR1_count_literal_false`). -/
theorem TR1_count (evs : List (Ev K Reg)) (hL : Legal start evs) :
    (exits evs).length = (entRows evs).length + nClr evs := by
  have hs := stay_count univ start evs hL
  have h0 : ((start : St K Reg).pres ∩ univ).card = 0 := by simp [start]
  rw [h0, add_zero, Finset.inter_univ] at hs
  simp only [exits, finals, List.length_append, List.length_map, Finset.length_toList,
    removed_length, entRows_length]
  omega

/-- The literal count is false with a CLEAR: born b, clear b (b ends at c). One entry (e_b), two exits
(the cleared e_b and the final 0). -/
theorem TR1_count_literal_false :
    ∃ evs : List (Ev ℚ (Fin 1)), Legal start evs ∧ (exits evs).length ≠ (entRows evs).length := by
  refine ⟨[.born 0, .clear 0], ?_, ?_⟩
  · simp [Legal, LegalEv, start, step]
  · simp [exits, finals, removed, remBy, entRows, run, step, start]

/-! ### TR1(b), (c): the c-pure part -/

/-- c-pure vectors: no coordinate on the helpers born at c -/
def pure (Hc : Finset Reg) : Submodule K (Reg → K) where
  carrier := {v | ∀ h ∈ Hc, v h = 0}
  add_mem' ha hb h hh := by simp [ha h hh, hb h hh]
  zero_mem' h _ := rfl
  smul_mem' c v hv h hh := by simp [hv h hh]

/-- arrival rows (an owned INIT is the arrival of 0) -/
def arrRows : List (Ev K Reg) → List (Reg → K)
  | [] => []
  | .arrive _ v :: evs => v :: arrRows evs
  | _ :: evs => arrRows evs

lemma mem_entRows : ∀ (evs : List (Ev K Reg)) (v : Reg → K),
    v ∈ entRows evs ↔ v ∈ arrRows evs ∨ ∃ b ∈ bornSet evs, v = Pi.single b 1
  | [], v => by simp [entRows, arrRows, bornSet]
  | .arrive i w :: evs, v => by
    simp only [entRows, arrRows, bornSet, List.mem_cons, mem_entRows evs v]; tauto
  | .born b :: evs, v => by
    simp only [entRows, arrRows, bornSet, List.mem_cons, mem_entRows evs v, Finset.mem_insert,
      exists_eq_or_imp]; tauto
  | .add _ _ _ :: evs, v => by simp only [entRows, arrRows, bornSet]; exact mem_entRows evs v
  | .scale _ _ :: evs, v => by simp only [entRows, arrRows, bornSet]; exact mem_entRows evs v
  | .depart _ :: evs, v => by simp only [entRows, arrRows, bornSet]; exact mem_entRows evs v
  | .clear _ :: evs, v => by simp only [entRows, arrRows, bornSet]; exact mem_entRows evs v
  | .copy _ _ :: evs, v => by simp only [entRows, arrRows, bornSet]; exact mem_entRows evs v

/-- A_c = span(arrival rows, tokens of the non-helper births at c) -/
def Ac (Hc : Finset Reg) (evs : List (Ev K Reg)) : Submodule K (Reg → K) :=
  span K ({v | v ∈ arrRows evs} ∪ (fun b => (Pi.single b 1 : Reg → K)) '' ↑(bornSet evs \ Hc))

/-- **TR1(c).** Under (b) (no arrival row has an H_c coordinate), for any helper set H_c:
span(exits) ∩ (c-pure) = A_c. -/
theorem TR1_pure (evs : List (Ev K Reg)) (hL : Legal start evs) (Hc : Finset Reg)
    (hb : ∀ v ∈ arrRows evs, ∀ h ∈ Hc, v h = 0) :
    span K {v | v ∈ exits evs} ⊓ pure Hc = Ac Hc evs := by
  rw [TR1_span evs hL]
  have hAcpure : Ac Hc evs ≤ pure Hc := by
    rw [Ac, Submodule.span_le]
    rintro v (hv | ⟨b, hb', rfl⟩)
    · exact hb v hv
    · intro h hh
      have hbh : b ≠ h := fun e => (Finset.mem_sdiff.1 hb').2 (e ▸ hh)
      simp [Pi.single_apply, hbh.symm]
  have hAcent : Ac Hc evs ≤ span K {v | v ∈ entRows evs} := by
    rw [Ac, Submodule.span_le]
    rintro v (hv | ⟨b, hb', rfl⟩)
    · exact Submodule.subset_span ((mem_entRows evs v).2 (Or.inl hv))
    · exact Submodule.subset_span ((mem_entRows evs _).2 (Or.inr ⟨b, (Finset.mem_sdiff.1 hb').1, rfl⟩))
  apply le_antisymm
  · -- span(entries) ≤ A_c ⊔ span{e_h : h ∈ Hc}
    set Tk : Submodule K (Reg → K) := span K ((fun b => (Pi.single b 1 : Reg → K)) '' ↑Hc)
    have hent : span K {v | v ∈ entRows evs} ≤ Ac Hc evs ⊔ Tk := by
      rw [Submodule.span_le]
      intro v hv
      rcases (mem_entRows evs v).1 hv with hv | ⟨b, hbB, rfl⟩
      · exact Submodule.mem_sup_left (Submodule.subset_span (Or.inl hv))
      · by_cases hbH : b ∈ Hc
        · exact Submodule.mem_sup_right (Submodule.subset_span ⟨b, hbH, rfl⟩)
        · exact Submodule.mem_sup_left (Submodule.subset_span
            (Or.inr ⟨b, Finset.mem_sdiff.2 ⟨hbB, hbH⟩, rfl⟩))
    have hTk : ∀ t ∈ Tk, ∀ r ∉ Hc, t r = 0 := by
      intro t ht
      refine Submodule.span_induction ?_ ?_ ?_ ?_ ht
      · rintro _ ⟨b, hb', rfl⟩ r hr
        have : b ≠ r := fun e => hr (e ▸ hb')
        simp [Pi.single_apply, this.symm]
      · intro r _; rfl
      · intro x y _ _ hx hy r hr; simp [hx r hr, hy r hr]
      · intro a x _ hx r hr; simp [hx r hr]
    rintro v ⟨hv, hvp⟩
    obtain ⟨a, ha, t, ht, rfl⟩ := Submodule.mem_sup.1 (hent hv)
    have ht0 : t = 0 := by
      funext r
      by_cases hr : r ∈ Hc
      · have h1 := hvp r hr
        have h2 := hAcpure ha r hr
        simp only [Pi.add_apply] at h1
        simp only [Pi.zero_apply]; rw [h2, zero_add] at h1; exact h1
      · exact hTk t ht r hr
    rw [ht0, add_zero]; exact ha
  · exact le_inf hAcent hAcpure

/-- dim A_c ≤ #arrivals + #(non-helper births at c) -/
theorem Ac_finrank (Hc : Finset Reg) (evs : List (Ev K Reg)) :
    finrank K (Ac Hc evs) ≤ (arrRows evs).length + (bornSet evs \ Hc).card := by
  classical
  have e : Ac Hc evs = span K (↑((arrRows evs).toFinset ∪
      (bornSet evs \ Hc).image (fun b => (Pi.single b 1 : Reg → K))) : Set (Reg → K)) := by
    rw [Ac]; congr 1; ext v; simp
  rw [e]
  refine (finrank_span_finset_le_card _).trans ?_
  refine (Finset.card_union_le _ _).trans (Nat.add_le_add (List.toFinset_card_le _)
    Finset.card_image_le)

/-- **TR1, tokens leave.** Every token born at c leaves c inside some exit row. -/
theorem TR1_tokens (evs : List (Ev K Reg)) (hL : Legal start evs) (h : Reg)
    (hh : h ∈ bornSet evs) : ∃ x ∈ exits evs, x h ≠ 0 := by
  by_contra hc
  push Not at hc
  let ev_h : (Reg → K) →ₗ[K] K := LinearMap.proj h
  have hle : span K {v | v ∈ exits evs} ≤ LinearMap.ker ev_h := by
    rw [Submodule.span_le]; intro v hv; exact hc v hv
  have hmem : (Pi.single h 1 : Reg → K) ∈ span K {v | v ∈ exits evs} := by
    rw [TR1_span evs hL]
    exact Submodule.subset_span ((mem_entRows evs _).2 (Or.inr ⟨h, hh, rfl⟩))
  have := hle hmem
  simp [ev_h] at this

/-! ## Part B. The swap canceller, and why the regress stops -/

/-- **The swap.** While h's row is exactly e_h: `j -= h; h += j`. Then h holds j's old row, j holds
(j's old row) − e_h, nothing else changes. -/
theorem swap (s : St K Reg) (h j : Reg) (hhj : h ≠ j) (hh : h ∈ s.pres) (hj : j ∈ s.pres)
    (hrow : s.row h = Pi.single h 1) :
    Legal s [.add j h (-1), .add h j 1] ∧
      (run s [.add j h (-1), .add h j 1]).row h = s.row j ∧
      (run s [.add j h (-1), .add h j 1]).row j = s.row j - Pi.single h 1 ∧
      (run s [.add j h (-1), .add h j 1]).pres = s.pres ∧
      ∀ r, r ≠ h → r ≠ j → (run s [.add j h (-1), .add h j 1]).row r = s.row r := by
  refine ⟨⟨⟨hhj.symm, hj, hh⟩, ⟨hhj, hh, hj⟩, trivial⟩, ?_, ?_, rfl, ?_⟩
  · simp [run, step, Function.update_of_ne hhj, hrow]
  · simp [run, step, Function.update_of_ne hhj.symm, hrow, sub_eq_add_neg]
  · intro r hrh hrj
    simp [run, step, Function.update_of_ne hrh, Function.update_of_ne hrj]

/-- After the swap h carries no token iff j's old row had no e_h coordinate; j then carries −e_h (the debt). -/
theorem swap_token (s : St K Reg) (h j : Reg) (hhj : h ≠ j) (hh : h ∈ s.pres) (hj : j ∈ s.pres)
    (hrow : s.row h = Pi.single h 1) :
    (run s [.add j h (-1), .add h j 1]).row h h = s.row j h ∧
      (run s [.add j h (-1), .add h j 1]).row j h = s.row j h - 1 := by
  obtain ⟨-, h1, h2, -, -⟩ := swap s h j hhj hh hj hrow
  rw [h1, h2]; simp

/-- Cancellers are ADD events: inserting any block of ADD/SCALE events (e.g. a swap) does not change
the entry list. -/
lemma entRows_append (l1 l2 : List (Ev K Reg)) : entRows (l1 ++ l2) = entRows l1 ++ entRows l2 := by
  induction l1 with
  | nil => rfl
  | cons e l ih => cases e <;> simp [entRows, ih]

/-- **The regress stops (TR1 counts directions, not carriers).** Two legal words from the empty state
with the same entries have the same span of exits, hence the same c-pure part A_c and the same token
directions. In particular inserting a swap (two ADDs) into a legal word changes neither: the debt
carrier's −e_h is not a new direction, so it demands no further canceller from TR1. -/
theorem regress_stops (evs evs' : List (Ev K Reg)) (hL : Legal start evs) (hL' : Legal start evs')
    (he : entRows evs = entRows evs') :
    span K {v | v ∈ exits evs} = span K {v | v ∈ exits evs'} := by
  rw [TR1_span evs hL, TR1_span evs' hL', he]

theorem regress_stops_swap (l1 l2 : List (Ev K Reg)) (h j : Reg)
    (hL : Legal start (l1 ++ l2)) (hL' : Legal start (l1 ++ [.add j h (-1), .add h j 1] ++ l2)) :
    span K {v | v ∈ exits (l1 ++ [.add j h (-1), .add h j 1] ++ l2)} =
      span K {v | v ∈ exits (l1 ++ l2)} :=
  regress_stops _ _ hL' hL (by simp [entRows_append, entRows])

end TR1

/-! ## Part C. TR3 token-aware cut lemma and TR4 (multi-chart, TokenCancel's model) -/
section TR3
open TokenCancel (Ev St step run)
variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C]

/-- co-presence of in-chart ops (births/INITs/MOVEs unrestricted) -/
def CoEv (s : St K Reg C) : Ev K Reg C → Prop
  | .add i j _ c => s.loc i = some c ∧ s.loc j = some c
  | .scale i _ c => s.loc i = some c
  | .clear i c => s.loc i = some c
  | .copy i j c => s.loc i = some c ∧ s.loc j = some c
  | _ => True

def Co : St K Reg C → List (Ev K Reg C) → Prop
  | _, [] => True
  | s, e :: es => CoEv s e ∧ Co (step s e) es

variable (Ω : Finset C) (s0 : C)

/-- the cut hypothesis: every MOVE into Ω comes from Ω or from s0 (TR3's "no non-ascending move enters
Ω from outside D(t)", with ascending moves into Ω ⊆ D(t) − {s} coming from D(t) = Ω ∪ {s}) -/
def CutEv (s : St K Reg C) : Ev K Reg C → Prop
  | .move i c => c ∈ Ω → ∃ c0, s.loc i = some c0 ∧ (c0 ∈ Ω ∨ c0 = s0)
  | _ => True

def Cut : St K Reg C → List (Ev K Reg C) → Prop
  | _, [] => True
  | s, e :: es => CutEv Ω s0 s e ∧ Cut (step s e) es

/-- the rows moving s0 → Ω, at their move times -/
def depRows : St K Reg C → List (Ev K Reg C) → List (Reg → K)
  | _, [] => []
  | s, .move i c :: es =>
      (if c ∈ Ω ∧ s.loc i = some s0 then [s.row i] else []) ++ depRows (step s (.move i c)) es
  | s, e :: es => depRows (step s e) es

/-- Φ kills every row currently in Ω -/
def InvΩ (Φ : (Reg → K) →ₗ[K] K) (s : St K Reg C) : Prop :=
  ∀ r c, s.loc r = some c → c ∈ Ω → Φ (s.row r) = 0

/-- `P` holds at every state of the run -/
def Always (P : St K Reg C → Prop) : St K Reg C → List (Ev K Reg C) → Prop
  | s, [] => P s
  | s, e :: es => P s ∧ Always P (step s e) es

lemma Always_final (P : St K Reg C → Prop) : ∀ (s : St K Reg C) (evs : List (Ev K Reg C)),
    Always P s evs → P (run s evs)
  | _, [], h => h
  | s, _ :: es, h => Always_final P _ es h.2

lemma invΩ_step (Φ : (Reg → K) →ₗ[K] K) (s : St K Reg C) (e : Ev K Reg C)
    (hI : InvΩ Ω Φ s) (hco : CoEv s e) (hcut : CutEv Ω s0 s e)
    (hdep : ∀ v ∈ depRows Ω s0 s [e], Φ v = 0)
    (hborn : ∀ i c, e = .born i c → c ∈ Ω → Φ (Pi.single i 1) = 0) :
    InvΩ Ω Φ (step s e) := by
  intro r c hr hc
  cases e with
  | born i c' =>
    simp only [step] at hr ⊢
    by_cases hri : r = i
    · subst hri; simp only [Function.update_self, Option.some.injEq] at hr ⊢
      subst hr; exact hborn r _ rfl hc
    · rw [Function.update_of_ne hri] at hr ⊢; exact hI r c hr hc
  | init i c' =>
    simp only [step] at hr ⊢
    by_cases hri : r = i
    · subst hri; simp
    · rw [Function.update_of_ne hri] at hr ⊢; exact hI r c hr hc
  | move i c' =>
    simp only [step] at hr ⊢
    by_cases hri : r = i
    · subst hri
      simp only [Function.update_self, Option.some.injEq] at hr
      subst hr
      obtain ⟨c0, hc0, hc0'⟩ := hcut hc
      rcases hc0' with h | rfl
      · exact hI r c0 hc0 h
      · exact hdep _ (by simp [depRows, hc, hc0])
    · rw [Function.update_of_ne hri] at hr; exact hI r c hr hc
  | add i j a c' =>
    obtain ⟨hi, hj⟩ := hco
    simp only [step] at hr ⊢
    by_cases hri : r = i
    · subst hri; rw [hi] at hr; cases hr
      simp only [Function.update_self, map_add, map_smul, hI r c hi hc, hI j c hj hc, smul_zero,
        add_zero]
    · rw [Function.update_of_ne hri]; exact hI r c hr hc
  | scale i u c' =>
    simp only [step] at hr ⊢
    by_cases hri : r = i
    · subst hri; rw [hco] at hr; cases hr
      simp only [Function.update_self, map_smul, hI r c hco hc, smul_zero]
    · rw [Function.update_of_ne hri]; exact hI r c hr hc
  | clear i c' =>
    simp only [step] at hr ⊢
    by_cases hri : r = i
    · subst hri; simp
    · rw [Function.update_of_ne hri]; exact hI r c hr hc
  | copy i j c' =>
    obtain ⟨hi, hj⟩ := hco
    simp only [step] at hr ⊢
    by_cases hri : r = i
    · subst hri; rw [hi] at hr; cases hr
      simp only [Function.update_self]; exact hI j c hj hc
    · rw [Function.update_of_ne hri]; exact hI r c hr hc

/-- **TR3 claim.** If Φ kills every row in Ω initially, every birth token in Ω (Φ supported on the
registers born at s0, none of which is born in Ω), and every row moving s0 → Ω, then Φ kills every
row in Ω at all times. -/
theorem TR3_claim (Φ : (Reg → K) →ₗ[K] K) : ∀ (s : St K Reg C) (evs : List (Ev K Reg C)),
    InvΩ Ω Φ s → Co s evs → Cut Ω s0 s evs → (∀ v ∈ depRows Ω s0 s evs, Φ v = 0) →
    (∀ i c, Ev.born i c ∈ evs → c ∈ Ω → Φ (Pi.single i 1) = 0) →
    Always (InvΩ Ω Φ) s evs
  | _, [], hI, _, _, _, _ => hI
  | s, e :: es, hI, ⟨hco, hco'⟩, ⟨hcut, hcut'⟩, hdep, hborn => by
    have hsplit : depRows Ω s0 s (e :: es) = depRows Ω s0 s [e] ++ depRows Ω s0 (step s e) es := by
      cases e <;> simp [depRows]
    rw [hsplit] at hdep
    refine ⟨hI, TR3_claim Φ _ es ?_ hco' hcut' (fun v hv => hdep v (List.mem_append_right _ hv))
      (fun i c h hc => hborn i c (List.mem_cons_of_mem _ h) hc)⟩
    exact invΩ_step Ω s0 Φ s e hI hco hcut (fun v hv => hdep v (List.mem_append_left _ hv))
      (fun i c h hc => hborn i c (h ▸ List.mem_cons_self) hc)

/-- projection onto the coordinates in B (e.g. Kept_s, the kept registers born at s0) -/
def projB (B : Finset Reg) : (Reg → K) →ₗ[K] (Reg → K) where
  toFun v r := if r ∈ B then v r else 0
  map_add' x y := by funext r; by_cases hr : r ∈ B <;> simp [hr]
  map_smul' a x := by funext r; by_cases hr : r ∈ B <;> simp [hr]

/-- **TR3 corollary (duality form).** From the empty state: for every register r in Ω at the end,
π_B(row r) ∈ span π_B(rows moving s0 → Ω), for any B none of whose registers is born in Ω. -/
theorem TR3_cor (B : Finset Reg) (evs : List (Ev K Reg C)) (hco : Co TokenCancel.start evs)
    (hcut : Cut Ω s0 TokenCancel.start evs)
    (hB : ∀ i c, Ev.born i c ∈ evs → c ∈ Ω → i ∉ B)
    (r : Reg) (c : C) (hr : (run TokenCancel.start evs).loc r = some c) (hc : c ∈ Ω) :
    projB B ((run TokenCancel.start evs).row r) ∈
      span K ((projB B) '' {v | v ∈ depRows Ω s0 TokenCancel.start evs}) := by
  by_contra hx
  obtain ⟨g, hg, hmap⟩ := Submodule.exists_dual_map_eq_bot_of_notMem hx inferInstance
  let Φ : (Reg → K) →ₗ[K] K := g ∘ₗ projB B
  have hkill : ∀ v ∈ depRows Ω s0 TokenCancel.start evs, Φ v = 0 := by
    intro v hv
    have hm : g (projB B v) ∈ (span K ((projB B) '' {v | v ∈ depRows Ω s0 TokenCancel.start evs})).map g :=
      Submodule.mem_map_of_mem (Submodule.subset_span ⟨v, hv, rfl⟩)
    rw [hmap] at hm; simpa [Φ] using hm
  have hborn : ∀ i c, Ev.born i c ∈ evs → c ∈ Ω → Φ (Pi.single i 1) = 0 := by
    intro i c' h hc'
    have hiB := hB i c' h hc'
    have : projB B (Pi.single i 1 : Reg → K) = 0 := by
      funext q; by_cases hq : q ∈ B
      · have : q ≠ i := fun e => hiB (e ▸ hq)
        simp [projB, hq, Pi.single_apply, this]
      · simp [projB, hq]
    simp [Φ, this]
  have hI0 : InvΩ Ω Φ (TokenCancel.start : St K Reg C) := by
    intro q c' hq; simp [TokenCancel.start] at hq
  have := Always_final _ _ _ (TR3_claim Ω s0 Φ _ evs hI0 hco hcut hkill hborn) r c hr hc
  exact hg (by simpa [Φ] using this)

/-! ### TR4: counting -/

/-- number of moves s0 → Ω by registers satisfying p -/
def nMvΩ (p : Reg → Prop) [DecidablePred p] : St K Reg C → List (Ev K Reg C) → ℕ
  | _, [] => 0
  | s, .move i c :: es =>
      (if p i ∧ c ∈ Ω ∧ s.loc i = some s0 then 1 else 0) + nMvΩ p (step s (.move i c)) es
  | s, e :: es => nMvΩ p (step s e) es

lemma depRows_length : ∀ (s : St K Reg C) (evs : List (Ev K Reg C)),
    (depRows Ω s0 s evs).length = nMvΩ Ω s0 (fun _ => True) s evs
  | _, [] => rfl
  | s, .move i c :: es => by
    simp only [depRows, nMvΩ, List.length_append, depRows_length _ es, true_and]
    split_ifs <;> simp
  | s, .born _ _ :: es => depRows_length _ es
  | s, .init _ _ :: es => depRows_length _ es
  | s, .add _ _ _ _ :: es => depRows_length _ es
  | s, .scale _ _ _ :: es => depRows_length _ es
  | s, .clear _ _ :: es => depRows_length _ es
  | s, .copy _ _ _ :: es => depRows_length _ es

lemma nMvΩ_split (p q : Reg → Prop) [DecidablePred p] [DecidablePred q] :
    ∀ (s : St K Reg C) (evs : List (Ev K Reg C)),
    nMvΩ Ω s0 p s evs = nMvΩ Ω s0 (fun i => p i ∧ q i) s evs + nMvΩ Ω s0 (fun i => p i ∧ ¬ q i) s evs
  | _, [] => rfl
  | s, .move i c :: es => by
    simp only [nMvΩ, nMvΩ_split p q _ es]
    by_cases hq : q i <;> split_ifs <;> simp_all <;> omega
  | s, .born _ _ :: es => nMvΩ_split p q _ es
  | s, .init _ _ :: es => nMvΩ_split p q _ es
  | s, .add _ _ _ _ :: es => nMvΩ_split p q _ es
  | s, .scale _ _ _ :: es => nMvΩ_split p q _ es
  | s, .clear _ _ :: es => nMvΩ_split p q _ es
  | s, .copy _ _ _ :: es => nMvΩ_split p q _ es

lemma nMvΩ_congr (p p' : Reg → Prop) [DecidablePred p] [DecidablePred p'] (h : ∀ i, p i ↔ p' i) :
    ∀ (s : St K Reg C) (evs : List (Ev K Reg C)), nMvΩ Ω s0 p s evs = nMvΩ Ω s0 p' s evs
  | _, [] => rfl
  | s, .move i c :: es => by
    simp only [nMvΩ, nMvΩ_congr p p' h _ es, h i]
  | s, .born _ _ :: es => nMvΩ_congr p p' h _ es
  | s, .init _ _ :: es => nMvΩ_congr p p' h _ es
  | s, .add _ _ _ _ :: es => nMvΩ_congr p p' h _ es
  | s, .scale _ _ _ :: es => nMvΩ_congr p p' h _ es
  | s, .clear _ _ :: es => nMvΩ_congr p p' h _ es
  | s, .copy _ _ _ :: es => nMvΩ_congr p p' h _ es

/-- entries into s0 by p-registers: MOVEs into s0 and INITs at s0 (the arrivals) -/
def nArr (p : Reg → Prop) [DecidablePred p] : List (Ev K Reg C) → ℕ
  | [] => 0
  | .move i c :: es => (if p i ∧ c = s0 then 1 else 0) + nArr p es
  | .init i c :: es => (if p i ∧ c = s0 then 1 else 0) + nArr p es
  | _ :: es => nArr p es

/-- births at s0 of p-registers -/
def nBorn (p : Reg → Prop) [DecidablePred p] : List (Ev K Reg C) → ℕ
  | [] => 0
  | .born i c :: es => (if p i ∧ c = s0 then 1 else 0) + nBorn p es
  | _ :: es => nBorn p es

lemma nBorn_zero (p : Reg → Prop) [DecidablePred p] : ∀ evs : List (Ev K Reg C),
    (∀ i c, Ev.born i c ∈ evs → c = s0 → ¬ p i) → nBorn s0 p evs = 0
  | [], _ => rfl
  | .born i c :: es, h => by
    simp only [nBorn]
    rw [nBorn_zero p es (fun i c hm => h i c (List.mem_cons_of_mem _ hm))]
    have := h i c List.mem_cons_self
    split_ifs with hh
    · exact absurd hh.1 (this hh.2)
    · rfl
  | .init _ _ :: es, h => nBorn_zero p es (fun i c hm => h i c (List.mem_cons_of_mem _ hm))
  | .move _ _ :: es, h => nBorn_zero p es (fun i c hm => h i c (List.mem_cons_of_mem _ hm))
  | .add _ _ _ _ :: es, h => nBorn_zero p es (fun i c hm => h i c (List.mem_cons_of_mem _ hm))
  | .scale _ _ _ :: es, h => nBorn_zero p es (fun i c hm => h i c (List.mem_cons_of_mem _ hm))
  | .clear _ _ :: es, h => nBorn_zero p es (fun i c hm => h i c (List.mem_cons_of_mem _ hm))
  | .copy _ _ _ :: es, h => nBorn_zero p es (fun i c hm => h i c (List.mem_cons_of_mem _ hm))

/-- p-registers (in R) located at s0 -/
def nAt (p : Reg → Prop) [DecidablePred p] (R : Finset Reg) (loc : Reg → Option C) : ℕ :=
  (R.filter fun r => p r ∧ loc r = some s0).card

lemma card_split (A : Finset Reg) (i : Reg) : A.card = (A.erase i).card + if i ∈ A then 1 else 0 := by
  split_ifs with h
  · rw [Finset.card_erase_add_one h]
  · rw [Finset.erase_eq_of_notMem h, add_zero]

lemma nAt_update (p : Reg → Prop) [DecidablePred p] (R : Finset Reg) (hR : ∀ i, p i → i ∈ R)
    (loc : Reg → Option C) (i : Reg) (o : Option C) :
    nAt s0 p R (Function.update loc i o) + (if p i ∧ loc i = some s0 then 1 else 0) =
      nAt s0 p R loc + (if p i ∧ o = some s0 then 1 else 0) := by
  unfold nAt
  rw [card_split _ i, card_split (R.filter fun r => p r ∧ loc r = some s0) i]
  have he : (R.filter fun r => p r ∧ Function.update loc i o r = some s0).erase i =
      (R.filter fun r => p r ∧ loc r = some s0).erase i := by
    ext r
    simp only [Finset.mem_erase, Finset.mem_filter]
    constructor
    · rintro ⟨hri, h1, h2, h3⟩; rw [Function.update_of_ne hri] at h3; exact ⟨hri, h1, h2, h3⟩
    · rintro ⟨hri, h1, h2, h3⟩; rw [← Function.update_of_ne hri o loc] at h3; exact ⟨hri, h1, h2, h3⟩
  rw [he]
  have m1 : (i ∈ R.filter fun r => p r ∧ Function.update loc i o r = some s0) ↔ (p i ∧ o = some s0) := by
    simp only [Finset.mem_filter, Function.update_self]
    exact ⟨fun h => h.2, fun h => ⟨hR i h.1, h⟩⟩
  have m2 : (i ∈ R.filter fun r => p r ∧ loc r = some s0) ↔ (p i ∧ loc i = some s0) := by
    simp only [Finset.mem_filter]
    exact ⟨fun h => h.2, fun h => ⟨hR i h.1, h⟩⟩
  simp only [m1, m2]
  omega

/-- **flow.** (p-moves s0 → Ω) + (p-registers at s0 at the end) ≤ (p-arrivals at s0) + (p-births at s0)
+ (p-registers at s0 at the start). `R` contains every p-register. -/
theorem flow (p : Reg → Prop) [DecidablePred p] (R : Finset Reg) (hR : ∀ i, p i → i ∈ R) :
    ∀ (s : St K Reg C) (evs : List (Ev K Reg C)),
    nMvΩ Ω s0 p s evs + nAt s0 p R (run s evs).loc ≤
      nArr s0 p evs + nBorn s0 p evs + nAt s0 p R s.loc
  | _, [] => by simp [nMvΩ, nArr, nBorn, run]
  | s, e :: es => by
    have ih := flow p R hR (step s e) es
    simp only [run] at ih ⊢
    cases e with
    | move i c =>
      have hu := nAt_update s0 p R hR s.loc i (some c)
      simp only [nMvΩ, nArr, nBorn, step] at ih hu ⊢
      have hle : (if p i ∧ c ∈ Ω ∧ s.loc i = some s0 then 1 else 0) ≤
          (if p i ∧ s.loc i = some s0 then 1 else 0) := by
        split_ifs <;> simp_all
      have hc : (if p i ∧ some c = some s0 then 1 else 0) = (if p i ∧ c = s0 then 1 else 0) := by
        simp
      omega
    | born i c =>
      have hu := nAt_update s0 p R hR s.loc i (some c)
      simp only [nMvΩ, nArr, nBorn, step] at ih hu ⊢
      have hc : (if p i ∧ some c = some s0 then 1 else 0) = (if p i ∧ c = s0 then 1 else 0) := by
        simp
      omega
    | init i c =>
      have hu := nAt_update s0 p R hR s.loc i (some c)
      simp only [nMvΩ, nArr, nBorn, step] at ih hu ⊢
      have hc : (if p i ∧ some c = some s0 then 1 else 0) = (if p i ∧ c = s0 then 1 else 0) := by
        simp
      omega
    | add _ _ _ _ => simp only [nMvΩ, nArr, nBorn, step] at ih ⊢; exact ih
    | scale _ _ _ => simp only [nMvΩ, nArr, nBorn, step] at ih ⊢; exact ih
    | clear _ _ => simp only [nMvΩ, nArr, nBorn, step] at ih ⊢; exact ih
    | copy _ _ _ => simp only [nMvΩ, nArr, nBorn, step] at ih ⊢; exact ih

/-- **TR4.** From the empty state, with Co and Cut. H = helpers; `q` marks the registers born at s0
(`hq`); B (e.g. Kept_s) has no register born in Ω. Hypothesis `hkept`: no non-helper born at s0 moves
s0 → Ω (the kept departers from s0 go outside D(t)). Let ρ be the rank of the B-projections of the rows
of any registers Rk located in Ω at the end (e.g. the kept finals). Then
  (helper moves s0 → Ω) ≥ ρ − (non-helper arrivals, i.e. MOVEs in and INITs, at s0). -/
theorem TR4 [Fintype Reg] (B H : Finset Reg) (q : Reg → Prop) [DecidablePred q]
    (evs : List (Ev K Reg C)) (hco : Co TokenCancel.start evs)
    (hcut : Cut Ω s0 TokenCancel.start evs)
    (hB : ∀ i c, Ev.born i c ∈ evs → c ∈ Ω → i ∉ B)
    (hq : ∀ i c, Ev.born i c ∈ evs → c = s0 → q i)
    (hkept : nMvΩ Ω s0 (fun i => i ∉ H ∧ q i) TokenCancel.start evs = 0)
    (Rk : Finset Reg) (hRk : ∀ r ∈ Rk, ∃ c ∈ Ω, (run TokenCancel.start evs).loc r = some c) :
    finrank K (span K ((projB B) '' ((run TokenCancel.start evs).row '' ↑Rk))) ≤
      nMvΩ Ω s0 (fun i => i ∈ H) TokenCancel.start evs +
        nArr s0 (fun i => i ∉ H ∧ ¬ q i) evs := by
  classical
  set L := depRows Ω s0 (TokenCancel.start : St K Reg C) evs
  -- ρ ≤ dim span π_B(dep rows)
  have h1 : span K ((projB B) '' ((run TokenCancel.start evs).row '' ↑Rk)) ≤
      span K ((projB B) '' {v | v ∈ L}) := by
    rw [Submodule.span_le]
    rintro _ ⟨_, ⟨r, hr, rfl⟩, rfl⟩
    obtain ⟨c, hc, hloc⟩ := hRk r hr
    exact TR3_cor Ω s0 B evs hco hcut hB r c hloc hc
  have e2 : span K ((projB B) '' {v | v ∈ L}) =
      span K (↑((L.map (projB B)).toFinset) : Set (Reg → K)) := by
    congr 1; ext v; simp
  have h2 : finrank K (span K ((projB B) '' {v | v ∈ L})) ≤ L.length := by
    rw [e2]
    refine (finrank_span_finset_le_card _).trans ((List.toFinset_card_le _).trans ?_)
    simp
  -- |dep| = helper moves + non-helper moves; non-helper moves ≤ arrivals
  have h3 : L.length = nMvΩ Ω s0 (fun _ => True) TokenCancel.start evs :=
    depRows_length Ω s0 (TokenCancel.start : St K Reg C) evs
  have h4 := nMvΩ_split Ω s0 (fun _ => True) (fun i => i ∈ H) (TokenCancel.start : St K Reg C) evs
  have e4a : nMvΩ Ω s0 (fun i => True ∧ i ∈ H) TokenCancel.start evs =
      nMvΩ Ω s0 (fun i => i ∈ H) TokenCancel.start evs := nMvΩ_congr Ω s0 _ _ (by simp) _ _
  have e4b : nMvΩ Ω s0 (fun i => True ∧ ¬ i ∈ H) TokenCancel.start evs =
      nMvΩ Ω s0 (fun i => i ∉ H) TokenCancel.start evs := nMvΩ_congr Ω s0 _ _ (by simp) _ _
  have h5 := nMvΩ_split Ω s0 (fun i => i ∉ H) q (TokenCancel.start : St K Reg C) evs
  have hfl := flow Ω s0 (fun i => i ∉ H ∧ ¬ q i) Finset.univ (fun i _ => Finset.mem_univ i)
    (TokenCancel.start : St K Reg C) evs
  have hb0 := nBorn_zero s0 (fun i => i ∉ H ∧ ¬ q i) evs (fun i c h hc hh => hh.2 (hq i c h hc))
  have hat0 : nAt s0 (fun i => i ∉ H ∧ ¬ q i) Finset.univ
      (TokenCancel.start : St K Reg C).loc = 0 := by
    simp [nAt, TokenCancel.start]
  have h6 := (Submodule.finrank_mono h1).trans h2
  omega

end TR3

end TokenRank

#print axioms TokenRank.TR1_span
#print axioms TokenRank.TR1_count
#print axioms TokenRank.TR1_count_literal_false
#print axioms TokenRank.TR1_pure
#print axioms TokenRank.TR1_tokens
#print axioms TokenRank.swap_token
#print axioms TokenRank.regress_stops_swap
#print axioms TokenRank.TR3_cor
#print axioms TokenRank.TR4
