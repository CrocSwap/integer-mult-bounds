/-
WordModelU0 (lane WORDMODEL, coordinator, Nov 18).  INTEGRATION: the SAFE rung U0 (κ < .0204111) for every
legal word of the shared word model (WordModelDefs.Word), with SafeRungs' hR1, hR2, hR3 DERIVED:
  R1 (WordModelR1.R1, WM-R1) + R2 (WordModelR2.R2) + target-disjointness (SafeRungsClique.down_up_disjoint)
    ⇒ nOwned ≥ 16;
  Theorem Y (WordModelY.theoremY, WM-Y) on CS / slack-rank (WordModelR3, WM-R3) ⇒ nStops ≥ 104 − nOwned.
The price side stays the SafeRungsPrice model, linked by  no := nOwned s  (# owned MOVEs of the run) and
nst := nStops s  (# stops of the run).  Remaining named hypotheses: hO1 (owned MOVE price ≥ 1), hH, hM, hM400
(price-side data of helpers / the 400 mains), hF (κ is a crossing of the word invoice).
Kernel only: no sorry, no native_decide, no axioms.
-/
import Nov15.WordModelR1
import Nov15.WordModelR2
import Nov15.WordModelR3
import Nov15.WordModelY
import Nov15.SafeRungsExact

set_option linter.unusedSectionVars false

namespace WordModel

open Finset SafeRungsClique SafeRungsPrice Module

theorem countP_add_le {β : Type} (l : List β) (p q : β → Bool) (h : ∀ a, ¬ (p a = true ∧ q a = true)) :
    l.countP p + l.countP q ≤ l.length := by
  induction l with
  | nil => simp
  | cons a l ih =>
    simp only [List.countP_cons, List.length_cons]
    by_cases hp : p a = true <;> by_cases hq : q a = true
    · exact absurd ⟨hp, hq⟩ (h a)
    · simp [hp, hq]; omega
    · simp [hp, hq]; omega
    · simp [hp, hq]; omega

variable {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow]
  [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]

open Classical in
/-- R1 + R2 + clique disjointness: at least 16 owned MOVEs. -/
theorem owned16 {cl : Caller Pt} {s : St (Reg Pt Hl Ow)} (hw : Word cl s) : 16 ≤ nOwned s := by
  have h1 := R1 hw
  have h2 := R2 cl hw
  have h := countP_add_le s.olog (fun m => decide (InDown m.2.1)) (fun m => decide (InUp m.2.1))
    (fun a ⟨ha, hb⟩ => down_up_disjoint a.2.1 ⟨of_decide_eq_true ha, of_decide_eq_true hb⟩)
  unfold nR1 at h1; unfold nR2 at h2; unfold nOwned
  omega

/-- R3 (stops ≥ 104 − m) from Theorem Y. -/
theorem stops_ge {cl : Caller Pt} {s : St (Reg Pt Hl Ow)} (hw : Word cl s) : 104 - (nOwned s : ℝ) ≤ nStops s := by
  have hY := theoremY hw (cs_final hw) (cs_entry hw) (born_unique hw) (slack_rank hw)
  have hle : nOwnNonV s ≤ nOwned s := by
    unfold nOwnNonV nOwned; exact List.countP_le_length
  have : 104 ≤ nStops s + nOwned s := by omega
  have : (104 : ℝ) ≤ nStops s + nOwned s := by exact_mod_cast this
  linarith

variable {α : Type*} {ι μ : Type*} {d : α → α → ℝ} (hm : PriceMetric d)
  (H : Finset ι) (hc : ι → ℝ) (hn : ι → ℕ) (hx : ι → ℕ → α)
  (M : Finset μ) (mn : μ → ℕ) (mx : μ → ℕ → α) (oa ob : ℕ → α)
  (hH : ∀ i ∈ H, hc i ≤ d (hx i 0) (hx i (hn i)))
  (hM : ∀ j ∈ M, 1 ≤ mn j ∧ 8 ≤ d (mx j 0) (mx j (mn j)))
  (hM400 : M.card = 400)

include hm hH hM hM400 in
/-- **RUNG U0 on the word model**: for every legal word (WordModelDefs.Word: run of the model, #7113 endpoints,
target final rows), priced by SafeRungsPrice with no = #owned MOVEs and nst = #stops of THIS run, every crossing
κ ∈ (0,1] of the word invoice is < .0204111.  hR1, hR2, hR3 are no longer hypotheses. -/
theorem U0_kappa_word {cl : Caller Pt} {s : St (Reg Pt Hl Ow)} (hw : Word cl s)
    (hO1 : ∀ k < nOwned s, 1 ≤ d (oa k) (ob k))
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ ≤ 1)
    (hF : 0 ≤ FW d (1 - κ) H hc hn hx M mn mx (nOwned s) oa ob (nStops s)) : κ < 204111 / 10000000 := by
  have h16 := owned16 hw
  have hR3 := stops_ge hw
  have hnst : (0 : ℝ) ≤ nStops s := Nat.cast_nonneg _
  refine kappa_lt (fun t => FW d (1 - t) H hc hn hx M mn mx (nOwned s) oa ob (nStops s)) FceilU0 _ ?_
    SafeRungsExact.certU0 κ hκ0 hκ1 hF
  intro t ht0 ht1
  exact U0_ceiling hm (1 - t) (by linarith) (by linarith) H hc hn hx M mn mx (nOwned s) oa ob (nStops s)
    hH hM hM400 hnst hO1 h16 hR3

/-! ### hO1 from model clauses: owned MOVEs are nested (l.51 owned clause), price separates charts and is
integer-valued (SPEC rank price).  Owned MOVE k = k-th entry of `olog` (newest first; the order is irrelevant). -/

/-- source / target chart of owned MOVE k. -/
def oSrc (s : St (Reg Pt Hl Ow)) (k : ℕ) : Ch := (s.olog.getD k (∅, ∅, 0)).1
def oTgt (s : St (Reg Pt Hl Ow)) (k : ℕ) : Ch := (s.olog.getD k (∅, ∅, 0)).2.1

theorem hO1_of_nested {s : St (Reg Pt Hl Ow)} (dc : Ch → Ch → ℝ)
    (hint : ∀ a b, ∃ n : ℕ, dc a b = n) (hsep : ∀ a b, dc a b = 0 → a = b) (hn : OwnedNested s) :
    ∀ k < nOwned s, 1 ≤ dc (oSrc s k) (oTgt s k) := by
  intro k hk
  have hmem : s.olog.getD k (∅, ∅, 0) ∈ s.olog := by
    rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hk, Option.getD_some]; exact List.getElem_mem hk
  have hne : oSrc s k ≠ oTgt s k := by
    rcases hn _ hmem with h | h
    · exact ne_of_lt h
    · exact (ne_of_lt h).symm
  obtain ⟨n, hn'⟩ := hint (oSrc s k) (oTgt s k)
  have : n ≠ 0 := by
    rintro rfl; exact hne (hsep _ _ (by simpa using hn'))
  rw [hn']; exact_mod_cast Nat.one_le_iff_ne_zero.2 this

/-- **U0 with hO1 discharged**: price = a separating, integer-valued pseudometric on charts (SPEC rank price);
owned MOVEs nested (verifier l.51).  Owned MOVE endpoints are those of the run. -/
theorem U0_kappa_word_nested {cl : Caller Pt} {s : St (Reg Pt Hl Ow)} (hw : Word cl s)
    {dc : Ch → Ch → ℝ} (hmc : PriceMetric dc) (hint : ∀ a b, ∃ n : ℕ, dc a b = n)
    (hsep : ∀ a b, dc a b = 0 → a = b) (hnest : OwnedNested s)
    {ι' μ' : Type*} (H' : Finset ι') (hc' : ι' → ℝ) (hn' : ι' → ℕ) (hx' : ι' → ℕ → Ch)
    (M' : Finset μ') (mn' : μ' → ℕ) (mx' : μ' → ℕ → Ch)
    (hH' : ∀ i ∈ H', hc' i ≤ dc (hx' i 0) (hx' i (hn' i)))
    (hM' : ∀ j ∈ M', 1 ≤ mn' j ∧ 8 ≤ dc (mx' j 0) (mx' j (mn' j))) (hM400' : M'.card = 400)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ ≤ 1)
    (hF : 0 ≤ FW dc (1 - κ) H' hc' hn' hx' M' mn' mx' (nOwned s) (oSrc s) (oTgt s) (nStops s)) :
    κ < 204111 / 10000000 :=
  U0_kappa_word hmc H' hc' hn' hx' M' mn' mx' (oSrc s) (oTgt s) hH' hM' hM400' hw
    (hO1_of_nested dc hint hsep hnest) κ hκ0 hκ1 hF

end WordModel

#print axioms WordModel.owned16
#print axioms WordModel.U0_kappa_word
#print axioms WordModel.U0_kappa_word_nested
