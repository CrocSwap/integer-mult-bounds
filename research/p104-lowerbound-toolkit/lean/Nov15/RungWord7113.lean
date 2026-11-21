/-
RungWord7113 (lane DISCHARGE, Nov 20).  The P104 / #7113 rung chain for 17 LEGAL WORDS, wired so that the ONLY non-structural hypothesis is the
aggregate wall premise  112 * 17 <= sum_i (descMass G_i + hostedRise G_i)  (Wall56 in aggregate form, on the folded banked graphs G_i).
Discharged here by existing Nov15 theorems:
  * HSContract per call       : UniHSC7113.hsc7113 (every legal 7113 word),
  * caller certificate Cert   : UniUniversal.cert7113 (Tcal/Pcal at kbar = 93453742/10^10),
  * hbud (h = 9)              : inside rung_joint_P104 (UniBud.cert),
  * word -> banked graph      : UniFold7113.foldBanked7113 (hypotheses: Legal, Word, the three verifier clauses FramesSubsp/ChartsSubsp/OwnedNested,
                                caller shape Ports7113 + DCount),
  * hV                        : NOT a lemma but the DEFINITION of the claim "kappa is a crossing of the words' invoice" (Theorem-K crossing: paid <= credit);
                                it is stated in the word's native form (wordPaid, helper climbs gc), exactly as in UniUniversal.Crossing.word.  The
                                theorem reads: if kappa is valid for these words then kappa < kbar.  That antecedent is the object of study, not an assumed fact.
  rung_word_7113_joint : headline.   rung_word_7113_of_halves : the per-call walls (56 <= D_i, 56 <= R_i) imply the aggregate premise.
Kernel only.
-/
import Nov15.UniHSC7113
import Nov15.WordRungJoint

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace RungWord7113
open Finset Module BankNC0 BankWireC BankFit BankHelp BankBanner SafeRungsPrice BankMassF BankFitHS
  BankCallerGen UniOwnedBank NoFlow UniWC UniPort WordModel Uni UniUniversal

theorem rung_word_7113_joint {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow]
    [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]
    (cl : WordModel.Caller Pt) (hP : UniFold7113.Ports7113 cl) (hDc : DCount cl)
    (tr : Fin 17 → Uni.Trace (Reg Pt Hl Ow)) (h : ∀ i, Uni.Legal (pub cl) (tr i))
    (hw : ∀ i, Word cl (exec (tr i))) (hfr : ∀ i, FramesSubsp (exec (tr i)))
    (hcs : ∀ i, ChartsSubsp (exec (tr i))) (hn : ∀ i, OwnedNested (exec (tr i)))
    -- THE aggregate wall premise (Wall56 in aggregate form)
    (hJ : (112 : ℤ) * 17 ≤ ∑ i, (descMass (UniFold7113.foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i))
        + hostedRise (UniFold7113.foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i))))
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : cdat (1 - κ) Pcal + ∑ i, wordPaid cl (exec (tr i)) specPrice (1 - κ) ≤
        cdat (1 - κ) Tcal + ∑ i, ∑ r ∈ (helpers : Finset (Reg Pt Hl Ow)), gc (1 - κ) (hcred (exec (tr i)) r)) :
    κ < 93453742 / 10000000000 := by
  have hσ : (1 - κ) ≠ 0 := by intro h0; linarith
  have hc : ∀ i, HSContract (UniFold7113.foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i)).N :=
    fun i => UniHSC7113.hsc7113 (h i) (hw i)
  have hcert := cert7113
  have := UniJoint.rung_joint_P104 17 Tcal Pcal (93453742 / 10000000000) (by norm_num) (by exact_mod_cast hcert)
    (fun i => UniFold7113.foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i)) hc hJ κ hκ0 hκ1 ?_
  · exact this
  · have e1 : ∀ i, ∑ k, BankPrem.specInvoice (UniFold7113.foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i))
        (1 - κ) k = Uni.wordPaid cl (Uni.exec (tr i)) WordModel.specPrice (1 - κ) := fun i =>
      UniFold7113.foldBanked7113_paid cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i) (1 - κ)
    have e2 : ∀ i, helperCredit (UniFold7113.foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i)).N (1 - κ)
        (UniFold7113.foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i)).Mn =
        ∑ r ∈ (WordModel.helpers : Finset (WordModel.Reg _ _ _)), gc (1 - κ) (WordModel.hcred (Uni.exec (tr i)) r) :=
      fun i => Uni.fold_credit cl (h i) (hw i) (hfr i) hσ
    simp only [e1, e2]
    exact hV

/-- the per-call walls (D_i >= 56, R_i >= 56 on the folded graphs) imply the aggregate premise. -/
theorem rung_word_7113_of_halves {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow]
    [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]
    (cl : WordModel.Caller Pt) (hP : UniFold7113.Ports7113 cl) (hDc : DCount cl)
    (tr : Fin 17 → Uni.Trace (Reg Pt Hl Ow)) (h : ∀ i, Uni.Legal (pub cl) (tr i))
    (hw : ∀ i, Word cl (exec (tr i))) (hfr : ∀ i, FramesSubsp (exec (tr i)))
    (hcs : ∀ i, ChartsSubsp (exec (tr i))) (hn : ∀ i, OwnedNested (exec (tr i)))
    (hD : ∀ i, 56 ≤ descMass (UniFold7113.foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i)))
    (hR : ∀ i, 56 ≤ hostedRise (UniFold7113.foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i)))
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : cdat (1 - κ) Pcal + ∑ i, wordPaid cl (exec (tr i)) specPrice (1 - κ) ≤
        cdat (1 - κ) Tcal + ∑ i, ∑ r ∈ (helpers : Finset (Reg Pt Hl Ow)), gc (1 - κ) (hcred (exec (tr i)) r)) :
    κ < 93453742 / 10000000000 := by
  refine rung_word_7113_joint cl hP hDc tr h hw hfr hcs hn ?_ κ hκ0 hκ1 hV
  have : ∀ i ∈ (Finset.univ : Finset (Fin 17)), (112 : ℤ) ≤
      descMass (UniFold7113.foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i))
        + hostedRise (UniFold7113.foldBanked7113 cl hP hDc (h i) (hw i) (hfr i) (hcs i) (hn i)) :=
    fun i _ => by have := hD i; have := hR i; omega
  have hs := Finset.sum_le_sum this
  simpa using hs

end RungWord7113

#print axioms RungWord7113.rung_word_7113_joint
#print axioms RungWord7113.rung_word_7113_of_halves
