/-
TC-DEPARTURE lemma (BEAUTY-NOV17A §3; WHOLEFLOOR/R4 "clean-departure rank lemma"),
TokenCancel op model, lane LEAN-NEXT23, Nov 17. See TCDepart.md.
-/
import Nov15.TCLemma

set_option linter.unusedSectionVars false

namespace TCDepart
open TokenCancel TCLemma

variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C] [Preorder C]

/-- State before event `n` (timed model). -/
def st (s0 : St K Reg C) (evs : List (Ev K Reg C)) (n : ℕ) : St K Reg C := run s0 (evs.take n)

theorem legal_nth : ∀ (evs : List (Ev K Reg C)) (s0 : St K Reg C) (h : Reg),
    LegalA s0 evs → ND h s0 evs → ∀ n (hn : n < evs.length),
    LegalEvA (st s0 evs n) evs[n] ∧ NDEv h (st s0 evs n) evs[n]
  | [], _, _, _, _, n, hn => absurd hn (by simp)
  | e :: es, s0, h, ⟨hL, hLs⟩, ⟨hN, hNs⟩, n, hn => by
    cases n with
    | zero => exact ⟨hL, hN⟩
    | succ n =>
      have := legal_nth es (step s0 e) h hLs hNs n (by simpa using hn)
      simpa [st, run] using this

theorem st_succ (s0 : St K Reg C) (evs : List (Ev K Reg C)) (n : ℕ) (hn : n < evs.length) :
    st s0 evs (n + 1) = step (st s0 evs n) evs[n] := by
  unfold st
  rw [List.take_add_one, List.getElem?_eq_getElem hn, run_append]
  rfl

/-- **Dirty departure (stay branch).** If a receiver `r ≠ h` leaves chart `F` for `c'` still
carrying e_h, and the run ends e_h-clean, then for every chart `R` not containing `c'`
some read of `h` after the departure sits outside `R`. -/
theorem dirty_departure (h : Reg) (s0 : St K Reg C) (pre post : List (Ev K Reg C))
    (r : Reg) (c' : C)
    (hL : LegalA s0 (pre ++ Ev.move r c' :: post)) (hN : ND h s0 (pre ++ Ev.move r c' :: post))
    (hf : ∀ x, x ≠ h → (run s0 (pre ++ Ev.move r c' :: post)).row x h = 0)
    (hrh : r ≠ h) (hdirty : (run s0 pre).row r h ≠ 0) (R : C) (hR : ¬ c' ≤ R) :
    ∃ i a c, Ev.add i h a c ∈ post ∧ ¬ c ≤ R := by
  by_contra hno
  push_neg at hno
  rw [legalA_append] at hL
  rw [nd_append] at hN
  rw [run_append] at hf
  have hL2 : LegalA (step (run s0 pre) (Ev.move r c')) post := hL.2.2
  have hN2 : ND h (step (run s0 pre) (Ev.move r c')) post := hN.2.2
  have hf2 : ∀ x, x ≠ h → (run (step (run s0 pre) (Ev.move r c')) post).row x h = 0 := hf
  have H := held_run post _ h R hL2 hN2 (fun i a c hm => hno i a c hm) hf2
  obtain ⟨c0, hc0, hle⟩ := H r hrh (by simpa [step] using hdirty)
  simp [step] at hc0
  subst hc0
  exact hR hle

/-- Cancelling needs a read inside a window: if `r ≠ h` is dirty at time `a` and clean at time
`b > a`, some event `n ∈ [a,b)` is an ADD into `r` whose source is `h` or dirty. -/
theorem cancel_in_window (h : Reg) (s0 : St K Reg C) (evs : List (Ev K Reg C))
    (hL : LegalA s0 evs) (hN : ND h s0 evs) (r : Reg) (hrh : r ≠ h) (a : ℕ) (b : ℕ)
    (hb : b ≤ evs.length) (hab : a ≤ b)
    (hd : (st s0 evs a).row r h ≠ 0) (hc : (st s0 evs b).row r h = 0) :
    ∃ n, a ≤ n ∧ n < b ∧ ∃ (hn : n < evs.length), ∃ j x c, evs[n] = Ev.add r j x c ∧
      (j = h ∨ (st s0 evs n).row j h ≠ 0) := by
  induction b, hab using Nat.le_induction with
  | base => exact absurd hc hd
  | succ b hab ih =>
    have hbl : b < evs.length := by omega
    by_cases hcl : (st s0 evs b).row r h = 0
    · obtain ⟨n, h1, h2, hx⟩ := ih (by omega) hcl
      exact ⟨n, h1, by omega, hx⟩
    · obtain ⟨hl, hn'⟩ := legal_nth evs s0 h hL hN b hbl
      rw [st_succ s0 evs b hbl] at hc
      obtain ⟨j, x, c, he, hj⟩ := cancel_only_by_read h _ _ hl hn' r hrh hcl hc
      exact ⟨b, hab, by omega, hbl, j, x, c, he, hj⟩

/-- **TC-Departure (clean branch).** Import `add r h _ F` at index `t1`, receiver departs at
index `τ`; it sits at `F` on the open window `(t1,τ)`. It is dirty right after the import and
clean at departure. Then some event in the window reads `h` at `F` (a stay at `F`) or reads a
register `j ≠ h` carrying e_h and resident at `F` (the "cover": e_h is already present in the
rows at `F`). -/
theorem clean_departure (h : Reg) (s0 : St K Reg C) (evs : List (Ev K Reg C))
    (hL : LegalA s0 evs) (hN : ND h s0 evs) (r : Reg) (hrh : r ≠ h) (F : C) (t1 τ : ℕ)
    (hτ : τ ≤ evs.length) (hlt : t1 < τ)
    (hsit : ∀ n, t1 < n → n < τ → (st s0 evs n).loc r = some F)
    (hd : (st s0 evs (t1 + 1)).row r h ≠ 0) (hc : (st s0 evs τ).row r h = 0) :
    ∃ n, t1 < n ∧ n < τ ∧ ∃ (hn : n < evs.length), ∃ x,
      (evs[n] = Ev.add r h x F) ∨
      (∃ j, j ≠ h ∧ j ≠ r ∧ (st s0 evs n).loc j = some F ∧ (st s0 evs n).row j h ≠ 0 ∧
        evs[n] = Ev.add r j x F) := by
  obtain ⟨n, h1, h2, hn, j, x, c, he, hj⟩ :=
    cancel_in_window h s0 evs hL hN r hrh (t1 + 1) τ hτ (by omega) hd hc
  have hnn : t1 < n := by omega
  have hleg := (legal_nth evs s0 h hL hN n hn).1
  rw [he] at hleg
  obtain ⟨hij, hli, hlj⟩ := hleg
  have hF := hsit n hnn h2
  rw [hF] at hli
  have hcF : c = F := (Option.some.inj hli).symm
  subst hcF
  refine ⟨n, hnn, h2, hn, x, ?_⟩
  by_cases hjh : j = h
  · subst hjh; exact Or.inl he
  · right
    refine ⟨j, hjh, fun e => hij e.symm, hlj, ?_, he⟩
    rcases hj with hj | hj
    · exact absurd hj hjh
    · exact hj

/-- Cover failure for a window: no register `≠ h, r` carrying e_h is resident at `F`
at any time in `(t1,τ)`. -/
def CoverFail (h r : Reg) (F : C) (s0 : St K Reg C) (evs : List (Ev K Reg C)) (t1 τ : ℕ) : Prop :=
  ∀ n, t1 < n → n < τ → ∀ j, j ≠ h → j ≠ r → (st s0 evs n).loc j = some F →
    (st s0 evs n).row j h = 0

/-- **Forced stay.** If the cover fails, the helper itself reads `h` into `r` at `F` inside the
window. -/
theorem forced_stay (h : Reg) (s0 : St K Reg C) (evs : List (Ev K Reg C))
    (hL : LegalA s0 evs) (hN : ND h s0 evs) (r : Reg) (hrh : r ≠ h) (F : C) (t1 τ : ℕ)
    (hτ : τ ≤ evs.length) (hlt : t1 < τ)
    (hsit : ∀ n, t1 < n → n < τ → (st s0 evs n).loc r = some F)
    (hd : (st s0 evs (t1 + 1)).row r h ≠ 0) (hc : (st s0 evs τ).row r h = 0)
    (hcf : CoverFail h r F s0 evs t1 τ) :
    ∃ n, t1 < n ∧ n < τ ∧ ∃ (hn : n < evs.length), ∃ x, evs[n] = Ev.add r h x F := by
  obtain ⟨n, h1, h2, hn, x, hx⟩ := clean_departure h s0 evs hL hN r hrh F t1 τ hτ hlt hsit hd hc
  rcases hx with hx | ⟨j, hjh, hjr, hl, hrow, _⟩
  · exact ⟨n, h1, h2, hn, x, hx⟩
  · exact absurd (hcf n h1 h2 j hjh hjr hl) hrow

/-! ### Counting corollary -/

open Classical in
/-- Number of reads of `h` (ADD events with source `h`, at any chart) in `evs`. -/
noncomputable def nReads (h : Reg) (evs : List (Ev K Reg C)) : ℕ :=
  ((Finset.range evs.length).filter (fun n =>
    ∃ (hn : n < evs.length), ∃ r x c, evs[n] = Ev.add r h x c)).card

open Classical in
/-- **Counting.** Let `S` be a finite set of imports (receiver `rc i`, chart `F i`, window
`(t1 i, τ i)`), each dirty after the import, clean at departure, resident at its `F` on its window,
with failed cover; and windows of imports with the same receiver pairwise disjoint. Then the
helper reads `h` at least `|S|` times. -/
theorem forced_stays_count {α : Type*} (h : Reg) (s0 : St K Reg C) (evs : List (Ev K Reg C))
    (hL : LegalA s0 evs) (hN : ND h s0 evs) (S : Finset α)
    (rc : α → Reg) (F : α → C) (t1 τ : α → ℕ)
    (hrh : ∀ i ∈ S, rc i ≠ h) (hτ : ∀ i ∈ S, τ i ≤ evs.length) (hlt : ∀ i ∈ S, t1 i < τ i)
    (hsit : ∀ i ∈ S, ∀ n, t1 i < n → n < τ i → (st s0 evs n).loc (rc i) = some (F i))
    (hd : ∀ i ∈ S, (st s0 evs (t1 i + 1)).row (rc i) h ≠ 0)
    (hc : ∀ i ∈ S, (st s0 evs (τ i)).row (rc i) h = 0)
    (hcf : ∀ i ∈ S, CoverFail h (rc i) (F i) s0 evs (t1 i) (τ i))
    (hdisj : ∀ i ∈ S, ∀ j ∈ S, i ≠ j → rc i = rc j → ∀ n,
      ¬ (t1 i < n ∧ n < τ i ∧ t1 j < n ∧ n < τ j)) :
    S.card ≤ nReads h evs := by
  have key : ∀ i ∈ S, ∃ n, t1 i < n ∧ n < τ i ∧ ∃ (hn : n < evs.length), ∃ x,
      evs[n] = Ev.add (rc i) h x (F i) := fun i hi =>
    forced_stay h s0 evs hL hN (rc i) (hrh i hi) (F i) (t1 i) (τ i) (hτ i hi) (hlt i hi)
      (hsit i hi) (hd i hi) (hc i hi) (hcf i hi)
  choose! f hf1 hf2 hf3 using key
  unfold nReads
  apply Finset.card_le_card_of_injOn f
  · intro i hi
    obtain ⟨hn, x, hx⟩ := hf3 i hi
    simp only [Finset.coe_filter, Finset.mem_range, Set.mem_setOf_eq]
    exact ⟨lt_of_lt_of_le (hf2 i hi) (hτ i hi), hn, rc i, x, F i, hx⟩
  · intro i hi j hj hij
    by_contra hne
    obtain ⟨hn1, x1, hx1⟩ := hf3 i hi
    obtain ⟨hn2, x2, hx2⟩ := hf3 j hj
    have hev : (Ev.add (rc i) h x1 (F i) : Ev K Reg C) = Ev.add (rc j) h x2 (F j) := by
      have e : evs[f i]'hn1 = evs[f j]'hn2 := by congr 1
      rw [← hx1, ← hx2]; exact e
    have hrc : rc i = rc j := by injection hev
    exact hdisj i hi j hj hne hrc (f i) ⟨hf1 i hi, hf2 i hi, by rw [hij]; exact hf1 j hj,
      by rw [hij]; exact hf2 j hj⟩


/-! ### Counterexample to the unqualified paper wording

"A dirty departure forces a stay at F" is FALSE: here the receiver `1` leaves `F = 0` dirty, and
the helper `0` reads only once at `F` (the import itself); the cancel happens at chart `1`.
What is true is `dirty_departure`: the forced stay lies outside every `R` not containing the
departure chart (here the read at chart 1). -/
namespace CE
abbrev E := Ev ℚ (Fin 2) ℕ
def evs : List E :=
  [.born 0 0, .born 1 0, .add 1 0 1 0, .move 1 1, .move 0 1, .add 1 0 (-1) 1]
def s0 : St ℚ (Fin 2) ℕ := ⟨fun _ _ => 0, fun _ => none⟩

theorem legal : LegalA s0 evs := by
  simp [evs, s0, LegalA, LegalEvA, step]

theorem nd : ND (0 : Fin 2) s0 evs := by
  simp [evs, s0, ND, NDEv, step, Function.update, Pi.single]

theorem final_clean : ∀ r : Fin 2, r ≠ 0 → (run s0 evs).row r 0 = 0 := by
  intro r hr
  have : r = 1 := by omega
  subst this
  simp [evs, s0, run, step, Function.update, Pi.single]

/-- the receiver `1` is dirty just before its departure from `F = 0`. -/
theorem dirty : (run s0 (evs.take 3)).row 1 0 ≠ 0 := by
  simp [evs, s0, run, step, Function.update, Pi.single]

/-- the only read of `h = 0` at chart `0` is the import (index 2); no read at chart 0 after
the departure (index 3). -/
theorem no_stay_at_F : ∀ i a, Ev.add i (0 : Fin 2) a (0 : ℕ) ∉ evs.drop 3 := by
  intro i a; simp [evs]

end CE

end TCDepart

#print axioms TCDepart.dirty_departure
#print axioms TCDepart.clean_departure
#print axioms TCDepart.forced_stays_count
#print axioms TCDepart.CE.final_clean
