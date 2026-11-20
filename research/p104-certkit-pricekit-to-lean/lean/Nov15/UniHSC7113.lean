/-
UniHSC7113 (lane UNI-HSC, Nov 19).  The height-stop contract of the fold of ANY legal 7113 word, proved once (like con7113):
  hsc7113 : HSContract (foldS h)   -- π = sw; Ehi = X (B port) / X2 (D port) of every port (rank 1->9 | 0->8),
                                   -- Elo = Y of every port (0->8 | 1->9); O-entries from the caller targets (-1, 1/2, 1).
Needs only Word (final charts, final_row) and the caller facts (lab odd, < 512, injective, 104 ports).
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.UniFold7113
import Nov15.BankFitB
import Nov15.BankFitHS1
import Nov15.UniUniversal

set_option linter.unusedSectionVars false

namespace UniHSC7113
open Finset Module Matrix WordModel Uni SafeRungsClique BankFlagB UniFold7113 BankWireC

theorem bits_of_lab : ∀ q < 512, wt q % 2 = 1 → ∃ i : Fin 9, q.testBit i = true := by decide +kernel

section Caller
variable {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow]
  [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]

/-- the high-end row of port p: X2 (D port) or X (B port). -/
def rowP (cl : Caller Pt) (p : Pt) : Fld (pub (Hl := Hl) (Ow := Ow) cl) :=
  if hD : cl.isD p = true then ⟨.x2 p, hD⟩ else ⟨.x p, rfl⟩

def rowL (cl : Caller Pt) (p : Pt) : Fld (pub (Hl := Hl) (Ow := Ow) cl) := ⟨.y p, rfl⟩

theorem rowP_inj (cl : Caller Pt) : Function.Injective (rowP (Hl := Hl) (Ow := Ow) cl) := by
  intro a b hab
  have h1 := congrArg (fun f => rp f.1) hab
  simp only [rowP] at h1
  split_ifs at h1 <;> exact Option.some.inj h1

theorem rowL_inj (cl : Caller Pt) : Function.Injective (rowL (Hl := Hl) (Ow := Ow) cl) := by
  intro a b hab
  have h1 := congrArg (fun f => rp f.1) hab
  simp only [rowL, rp] at h1
  exact Option.some.inj h1

variable {cl : Caller Pt} {tr : Trace (Reg Pt Hl Ow)} (h : Legal (pub cl) tr) (hw : Word cl (exec tr))

theorem bitsP (p : Pt) : ∃ i : Fin 9, (cl.lab p).testBit i = true :=
  bits_of_lab _ (cl.lab_lt p) (cl.lab_odd p)

include h hw in
/-- **hsc7113**: the height-stop contract of the fold of every legal 7113 word. -/
noncomputable def hsc7113 : BankFitHS.HSContract (foldS h) where
  π := piF cl
  πinj := piF_inj cl
  hsupp f g hne := by
    rw [foldS_O cl h hw] at hne
    rcases tgt_supp cl _ _ hne with h1 | h1
    · exact Or.inl (Subtype.ext h1)
    · exact Or.inr (Subtype.ext h1)
  Ehi := univ.image (rowP cl)
  Elo := univ.image (rowL cl)
  hi_card := by rw [card_image_of_injective _ (rowP_inj cl), card_univ, cl.card104]
  lo_card := by rw [card_image_of_injective _ (rowL_inj cl), card_univ, cl.card104]
  hi_h e he := by
    obtain ⟨p, -, rfl⟩ := mem_image.1 he
    have hb := bitsP (cl := cl) p
    by_cases hD : cl.isD p = true
    · rw [show rowP (Hl := Hl) (Ow := Ow) cl p = ⟨.x2 p, hD⟩ from dif_pos hD]
      refine ⟨?_, ?_, ?_, ?_⟩
      · rw [A_x2 h hw hD rfl]; exact finrank_span_singleton (BankFitB.vec_ne hb)
      · rw [B_x2 h hw hD, finrank_top]; exact BankFitB.finrank_V
      · show finrank (ZMod 2) ((foldS h).A ⟨.y2 p, hD⟩) = 0
        rw [A_y2 h hw hD]; exact finrank_bot _ _
      · show finrank (ZMod 2) ((foldS h).B ⟨.y2 p, hD⟩) = 8
        rw [B_y2 h hw hD rfl]; exact BankFitB.ker_rank hb
    · rw [show rowP (Hl := Hl) (Ow := Ow) cl p = ⟨.x p, rfl⟩ from dif_neg hD]
      refine ⟨?_, ?_, ?_, ?_⟩
      · rw [A_x h hw rfl]; exact finrank_span_singleton (BankFitB.vec_ne hb)
      · rw [B_x h hw, finrank_top]; exact BankFitB.finrank_V
      · show finrank (ZMod 2) ((foldS h).A ⟨.y p, rfl⟩) = 0
        rw [A_y h hw]; exact finrank_bot _ _
      · show finrank (ZMod 2) ((foldS h).B ⟨.y p, rfl⟩) = 8
        rw [B_y h hw rfl]; exact BankFitB.ker_rank hb
  lo_h e he := by
    obtain ⟨p, -, rfl⟩ := mem_image.1 he
    have hb := bitsP (cl := cl) p
    refine ⟨?_, ?_, ?_, ?_⟩
    · show finrank (ZMod 2) ((foldS h).A ⟨.y p, rfl⟩) = 0
      rw [A_y h hw]; exact finrank_bot _ _
    · show finrank (ZMod 2) ((foldS h).B ⟨.y p, rfl⟩) = 8
      rw [B_y h hw rfl]; exact BankFitB.ker_rank hb
    · show finrank (ZMod 2) ((foldS h).A ⟨.x p, rfl⟩) = 1
      rw [A_x h hw rfl]; exact finrank_span_singleton (BankFitB.vec_ne hb)
    · show finrank (ZMod 2) ((foldS h).B ⟨.x p, rfl⟩) = 9
      rw [B_x h hw, finrank_top]; exact BankFitB.finrank_V
  nz_hi e he := by
    obtain ⟨p, -, rfl⟩ := mem_image.1 he
    rw [foldS_O cl h hw]
    unfold rowP
    split_ifs with hD
    · simp [piF, sw, tgt, e]
    · rw [Bool.not_eq_true] at hD
      simp [piF, sw, tgt, e, hD]
  nz_lo e he := by
    obtain ⟨p, -, rfl⟩ := mem_image.1 he
    rw [foldS_O cl h hw]
    simp only [rowL, piF, sw, tgt]
    split_ifs <;> simp [e, Pi.single_apply]

end Caller

end UniHSC7113

#print axioms UniHSC7113.hsc7113

namespace UniHSC7113
open Finset Module BankNC0 BankWireC BankFit BankHelp BankBanner SafeRungsPrice BankMassF BankFitHS BankCallerGen UniOwnedBank NoFlow UniWC WordModel Uni SafeRungsClique UniUniversal UniFold7113

section Univ
variable {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow] [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]

/-- **kappa_lt_universal_word'**: every 17-call legal word under a #7113 caller crossing its own invoice has
κ < .0093453742.  HSContract is DISCHARGED (hsc7113); premises: verifier clauses, DHalf (D >= 56), RHalf (R >= 56), Valid. -/
theorem kappa_lt_universal_word' (cl : Caller Pt) (hP : Ports7113 cl) (hDc : DCount cl)
    (tr : Fin 17 → Trace (Reg Pt Hl Ow)) (h : ∀ i, Legal (pub cl) (tr i))
    (hw : ∀ i, Word cl (exec (tr i))) (hfr : ∀ i, FramesSubsp (exec (tr i)))
    (hcs : ∀ i, ChartsSubsp (exec (tr i))) (hn : ∀ i, OwnedNested (exec (tr i)))
    (hD : ∀ i, DHalf (foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i)))
    (hR : ∀ i, RHalf (foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i)))
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : cdat (1 - κ) Pcal + ∑ i, wordPaid cl (exec (tr i)) specPrice (1 - κ) ≤
      cdat (1 - κ) Tcal + ∑ i, ∑ r ∈ (helpers : Finset (Reg Pt Hl Ow)), gc (1 - κ) (hcred (exec (tr i)) r)) :
    κ < 93453742 / 10000000000 :=
  kappa_lt_universal .w7113 κ <|
    Crossing.word cl hP hDc tr h hw hfr hcs hn (fun i => hsc7113 (h i) (hw i)) hD hR κ hκ0 hκ1 hV

/-- the same with the two halves as plain mass premises: D >= 56 and R >= 56 of each call's folded graph. -/
theorem kappa_lt_universal_word_mass (cl : Caller Pt) (hP : Ports7113 cl) (hDc : DCount cl)
    (tr : Fin 17 → Trace (Reg Pt Hl Ow)) (h : ∀ i, Legal (pub cl) (tr i))
    (hw : ∀ i, Word cl (exec (tr i))) (hfr : ∀ i, FramesSubsp (exec (tr i)))
    (hcs : ∀ i, ChartsSubsp (exec (tr i))) (hn : ∀ i, OwnedNested (exec (tr i)))
    (hD : ∀ i, 56 ≤ BankBanner.descMass (foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i)))
    (hR : ∀ i, 56 ≤ UniOwnedBank.hostedRise (foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i)))
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : cdat (1 - κ) Pcal + ∑ i, wordPaid cl (exec (tr i)) specPrice (1 - κ) ≤
      cdat (1 - κ) Tcal + ∑ i, ∑ r ∈ (helpers : Finset (Reg Pt Hl Ow)), gc (1 - κ) (hcred (exec (tr i)) r)) :
    κ < 93453742 / 10000000000 := by
  have hσ : (1 - κ) ≠ 0 := by intro h0; linarith
  refine kappa_of_cert_dep 17 Tcal Pcal _ (by norm_num) cert7113
    (fun i => foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i)) (fun i => hsc7113 (h i) (hw i))
    (fun i => by exact_mod_cast UniOwnedBank.excess_ge_112_halves _ (hD i) (hR i)) κ hκ0 hκ1 ?_
  have e1 : ∀ i, ∑ k, BankPrem.specInvoice (foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i))
      (1 - κ) k = wordPaid cl (exec (tr i)) specPrice (1 - κ) := fun i =>
    foldBanked7113_paid cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i) (1 - κ)
  have e2 : ∀ i, BankHelp.helperCredit (foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i)).N (1 - κ)
      (foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i)).Mn =
      ∑ r ∈ (helpers : Finset (Reg Pt Hl Ow)), gc (1 - κ) (hcred (exec (tr i)) r) :=
    fun i => fold_credit cl (h i) (hw i) (hfr i) hσ
  simp only [e1, e2]
  exact hV

end Univ

/-- **kappa_lt_universal_lt_001**: every crossing of the class (17 legal words, banked 7113 block, banked K-call family)
has κ < 1/100. -/
theorem kappa_lt_universal_lt_001 (k : Kind) (κ : ℝ) (H : Crossing k κ) : κ < 1 / 100 := by
  have := kappa_lt_universal_max k κ H
  linarith

end UniHSC7113

#print axioms UniHSC7113.kappa_lt_universal_word'
#print axioms UniHSC7113.kappa_lt_universal_word_mass
#print axioms UniHSC7113.kappa_lt_universal_lt_001
