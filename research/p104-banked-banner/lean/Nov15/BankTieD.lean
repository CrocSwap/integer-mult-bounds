/-
BankTieD .  AUDIT RESULT + the sound way to shrink the Net data of #7761.
Audit: BankedGraph.price -> net_price28_help -> cut_lemma consumes `read` for EVERY bank (claim1, induction over k) and
`out` for EVERY field (claim2), plus minors/con/nest/climb/Mn; BankTieA/B/C use d only through ChainTie.hcar (23 banks)
and Mediated(S).  So `d` of the other 5723 banks cannot be dropped: the rank/cut argument needs a d satisfying read/out
globally.  What CAN be shrunk is how d is given: the #7761 forms ARE straight-line recipes (python-checked: 134078 field
terms with A g = src k, 11241 bank refs with j < k and dst j = src k, 43106 output terms).  `Recipe` below defines
d by well-founded recursion on the bank order, so `read` is a THEOREM (`dRec_read`) from the cheap side conditions, and
`out` follows from `O f = outVec f` (`outVec_out`).  Only that O-equality needs the expanded forms.
Kernel only.
-/
import Nov15.BankNC0b

namespace BankNC0
open Finset Submodule

variable {K : Type} {Chart Fld Bank : Type} [Field K] [DecidableEq Fld] [LinearOrder Bank] [Finite Bank]

/-- sparse straight-line recipe for the bank forms: field terms and references to earlier banks. -/
structure Recipe (K Fld Bank : Type) where
  fld : Bank → List (K × Fld)
  ref : Bank → List (K × Bank)

/-- the form d k by recursion on the bank order (references to non-earlier banks count as 0). -/
noncomputable def dRec (R : Recipe K Fld Bank) : Bank → Fld → K :=
  haveI : WellFoundedLT Bank := Finite.to_wellFoundedLT
  WellFounded.fix (wellFounded_lt (α := Bank)) fun k ih =>
    ((R.fld k).map fun p => p.1 • (Pi.single p.2 (1 : K) : Fld → K)).sum +
    ((R.ref k).map fun p => if h : p.2 < k then p.1 • ih p.2 h else (0 : Fld → K)).sum

theorem dRec_eq (R : Recipe K Fld Bank) (k : Bank) :
    dRec R k = ((R.fld k).map fun p => p.1 • (Pi.single p.2 (1 : K) : Fld → K)).sum +
      ((R.ref k).map fun p => if p.2 < k then p.1 • dRec R p.2 else (0 : Fld → K)).sum := by
  haveI : WellFoundedLT Bank := Finite.to_wellFoundedLT
  unfold dRec
  rw [WellFounded.fix_eq]
  refine congrArg₂ (· + ·) rfl (congrArg List.sum (List.map_congr_left fun p _ => ?_))
  by_cases h : p.2 < k
  · rw [dif_pos h, if_pos h]
  · rw [dif_neg h, if_neg h]

/-- **read by construction**: if the recipe's field terms are born at `src k` and its bank refs are earlier banks
delivered to `src k`, then dRec k lies in the span required by `Net.read`. -/
theorem dRec_read (R : Recipe K Fld Bank) (A : Fld → Chart) (src dst : Bank → Chart)
    (hf : ∀ k p, p ∈ R.fld k → A p.2 = src k) (hr : ∀ k p, p ∈ R.ref k → p.2 < k ∧ dst p.2 = src k) (k : Bank) :
    dRec R k ∈ span K ({v | ∃ g, A g = src k ∧ v = Pi.single g 1} ∪
                       {v | ∃ j, j < k ∧ dst j = src k ∧ v = dRec R j}) := by
  rw [dRec_eq]
  refine add_mem (list_sum_mem fun v hv => ?_) (list_sum_mem fun v hv => ?_)
  · obtain ⟨p, hp, rfl⟩ := List.mem_map.1 hv
    exact smul_mem _ _ (subset_span (Or.inl ⟨p.2, hf k p hp, rfl⟩))
  · obtain ⟨p, hp, rfl⟩ := List.mem_map.1 hv
    obtain ⟨hlt, hd⟩ := hr k p hp
    rw [if_pos hlt]
    exact smul_mem _ _ (subset_span (Or.inr ⟨p.2, hlt, hd, rfl⟩))

/-- output recipe: field terms and bank refs. -/
noncomputable def outVec (R : Recipe K Fld Bank) (of : List (K × Fld)) (or : List (K × Bank)) : Fld → K :=
  (of.map fun p => p.1 • (Pi.single p.2 (1 : K) : Fld → K)).sum + (or.map fun p => p.1 • dRec R p.2).sum

/-- **out by construction** for an output given by recipe terms born at / delivered to chart `c`. -/
theorem outVec_out (R : Recipe K Fld Bank) (A : Fld → Chart) (dst : Bank → Chart) (c : Chart)
    (of : List (K × Fld)) (or : List (K × Bank))
    (hf : ∀ p ∈ of, A p.2 = c) (hr : ∀ p ∈ or, dst p.2 = c) :
    outVec R of or ∈ span K ({v | ∃ g, A g = c ∧ v = Pi.single g 1} ∪
                             {v | ∃ j, dst j = c ∧ v = dRec R j}) := by
  refine add_mem (list_sum_mem fun v hv => ?_) (list_sum_mem fun v hv => ?_)
  · obtain ⟨p, hp, rfl⟩ := List.mem_map.1 hv
    exact smul_mem _ _ (subset_span (Or.inl ⟨p.2, hf p hp, rfl⟩))
  · obtain ⟨p, hp, rfl⟩ := List.mem_map.1 hv
    exact smul_mem _ _ (subset_span (Or.inr ⟨p.2, hr p hp, rfl⟩))

end BankNC0
#print axioms BankNC0.dRec_read
#print axioms BankNC0.outVec_out
