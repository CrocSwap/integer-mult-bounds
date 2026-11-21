/-
RungWordH (lane WORDSHAPEH, Nov 20).  The port-parametric rung chain from a LEGAL WORD at label rank h in {7, 8}:
  WordShapeH (shape of every legal word)  ->  HCutGen (cut contract)  ->  PriceH (molecule price)  ->  BudH (budget)  ->  UniJoint (aggregate rung).
  mainsH cl         : the main fields (x, y of every port; x2, y2 of D ports); `mainsH_card` : card = 2|Pt| + 2|D|  (QR := |D|), `mainsH_climb` : climb n-1.
  callH h hw        : the HCall of the fold of a legal word (HCall.ofNet with minorsH, hscH, mains) -- NOTHING assumed about the word beyond Legal + WordH.
  rung_port_h_joint : PriceH + UniJoint: the aggregate rung for ANY family of HCalls (L.X0 <= sum of excesses).
  rung_port_word_h  : generic label rank n >= 3 with any molecule certificate + budget premise.
  rung_port_word_h7 / rung_port_word_h8 : hbud DISCHARGED (BudH).  Remaining premises: the aggregate wall premise (D+R >= (rhoD+rhoR) n per call on
     average, as D_i, R_i masses below the call's excess), the caller Cert (cdat T - cdat P - L PortInv < 0 on [kbar,1]) with kbar >= 146/15625,
     Valid (hV: the Theorem-K crossing statement against the caller block, in the fold's native |dim| invoice).
Kernel only.
-/
import Nov15.WordShapeH
import Nov15.BudH
import Nov15.WordRungJoint
import Nov15.PriceHRung

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace RungWordH
open Finset Module Matrix WordModel Uni WordShapeH HCutGen BankNC0 PriceH SafeRungsPrice

/-! ## 1. Aggregate rung for any family of HCalls (joint form of PriceH.rung_port_h) -/

theorem rung_port_h_joint (h n QR : ℕ) (hh : 3 ≤ h) (MD : MolData h) (X0 kbar : ℝ) (L : ℕ) (T P : List (ℕ × ℕ))
    (hcert : Cert (fun s => cdat s T - cdat s P - (L : ℝ) * UniPort.PortInvX n QR h X0 0 s) kbar)
    {Fld Bank : Fin L → Type} [∀ i, Fintype (Fld i)] [∀ i, DecidableEq (Fld i)] [∀ i, Fintype (Bank i)]
    (C : ∀ i, HCall h n QR (Fld i) (Bank i))
    (hsum : (L : ℝ) * X0 ≤ ∑ i, (C i).excess)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hbud : kbar ≤ κ → 0 ≤ bud h MD (fun d : ℕ => (d : ℝ) ^ (1 - κ)))
    (hV : cdat (1 - κ) P + ∑ i, (C i).spec (1 - κ) ≤ cdat (1 - κ) T + ∑ i, (C i).cred (1 - κ)) :
    κ < kbar := by
  refine UniJoint.rung_port_joint n QR h (by omega) X0 0 kbar L T P hcert (fun i s => (C i).spec s)
    (fun i s => (C i).cred s) (fun i => (C i).excess) hsum κ hκ0 hκ1 ?_ hV
  intro hge i
  have := price_h MD hh (C i) (s := 1 - κ) (by linarith) (by linarith) (hbud hge) (C i).excess le_rfl
  simp only [UniPort.PortInvX, UniPort.mains, zero_mul, add_zero]
  exact this

/-! ## 2. The main fields of a word -/

section Mains
variable {n : ℕ} {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow]
  [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]

/-- main fields: x, y of every port, x2, y2 of D ports (= fields whose register is a port register). -/
def mainsH (cl : CallerH n Pt) : Finset (Fld (pubH (Hl := Hl) (Ow := Ow) cl)) :=
  univ.filter (fun f => UniFold7113.rp f.1 ≠ none)

theorem mem_mainsH (cl : CallerH n Pt) (f : Fld (pubH (Hl := Hl) (Ow := Ow) cl)) :
    f ∈ mainsH cl ↔ UniFold7113.rp f.1 ≠ none := by simp [mainsH]

/-- |mains| = 2 |Pt| + 2 |D|. -/
theorem mainsH_card (cl : CallerH n Pt) :
    (mainsH (Hl := Hl) (Ow := Ow) cl).card = 2 * Fintype.card Pt + 2 * (univ.filter (fun p => cl.isD p = true)).card := by
  classical
  have hq : (((mainsH (Hl := Hl) (Ow := Ow) cl).card : ℕ) : ℚ) =
      ∑ f : Fld (pubH (Hl := Hl) (Ow := Ow) cl), (if UniFold7113.rp f.1 ≠ none then (1 : ℚ) else 0) := by
    rw [Finset.card_eq_sum_ones, Nat.cast_sum]
    unfold mainsH
    rw [Finset.sum_filter]
    simp
  set g : Reg Pt Hl Ow → ℚ := fun r => if (UniFold7113.rp r ≠ none ∧ pubH cl r = true) then 1 else 0 with hg
  have h1 : ∑ f : Fld (pubH (Hl := Hl) (Ow := Ow) cl), g f.1 = ∑ r, g r :=
    sum_fldH cl g (fun r hr => by simp [hg, hr])
  have h2 : ∑ f : Fld (pubH (Hl := Hl) (Ow := Ow) cl), g f.1 =
      ∑ f : Fld (pubH (Hl := Hl) (Ow := Ow) cl), (if UniFold7113.rp f.1 ≠ none then (1 : ℚ) else 0) := by
    refine Finset.sum_congr rfl (fun f _ => ?_)
    simp [hg, f.2]
  have h3 : ∑ r, g r = 2 * (Fintype.card Pt : ℚ) + 2 * ((univ.filter (fun p => cl.isD p = true)).card : ℚ) := by
    rw [sum_regH]
    simp [hg, UniFold7113.rp, pubH, Finset.sum_add_distrib, Finset.sum_boole]
    ring
  have : (((mainsH (Hl := Hl) (Ow := Ow) cl).card : ℕ) : ℚ) =
      ((2 * Fintype.card Pt + 2 * (univ.filter (fun p => cl.isD p = true)).card : ℕ) : ℚ) := by
    rw [hq, ← h2, h1, h3]; push_cast; ring
  exact_mod_cast this

theorem dh_one_n (hn : 1 ≤ n) : dh 1 n = n - 1 := by unfold dh; omega
theorem dh_zero_pred : dh 0 (n - 1) = n - 1 := by unfold dh; omega

/-- every main field of a legal word climbs n - 1. -/
theorem mainsH_climb (hn : 1 ≤ n) {cl : CallerH n Pt} {tr : Trace (Reg Pt Hl Ow)}
    (h : Legal (pubH (Hl := Hl) (Ow := Ow) cl) tr) (hw : WordH cl (exec tr)) :
    ∀ f ∈ mainsH (Hl := Hl) (Ow := Ow) cl,
      dh (finrank (ZMod 2) ((foldSH n h).A f)) (finrank (ZMod 2) ((foldSH n h).B f)) = n - 1 := by
  intro f hf
  rw [mem_mainsH] at hf
  have hW : finrank (ZMod 2) (VH n) = n := Module.finrank_fin_fun _
  obtain ⟨r, hr⟩ := f
  have key : ∀ p : Pt, vecH n (cl.lab p) ≠ 0 ∧ phiH n (cl.lab p) ≠ 0 := fun p =>
    ⟨vecH_ne (cl.lab_lt p) (cl.lab_ne p), phiH_ne (cl.lab_lt p) (cl.lab_ne p)⟩
  cases r with
  | x p =>
    show dh (finrank (ZMod 2) ((foldSH n h).A ⟨.x p, rfl⟩)) (finrank (ZMod 2) ((foldSH n h).B ⟨.x p, rfl⟩)) = n - 1
    rw [A_xH h hw, B_xH h hw, finrank_span_singleton (key p).1, finrank_top, hW]; exact dh_one_n hn
  | y p =>
    show dh (finrank (ZMod 2) ((foldSH n h).A ⟨.y p, rfl⟩)) (finrank (ZMod 2) ((foldSH n h).B ⟨.y p, rfl⟩)) = n - 1
    rw [A_yH h hw, B_yH h hw, finrank_bot, finrank_ker_pred _ (key p).2 hW]; exact dh_zero_pred
  | x2 p =>
    have hD : cl.isD p = true := hr
    show dh (finrank (ZMod 2) ((foldSH n h).A ⟨.x2 p, hD⟩)) (finrank (ZMod 2) ((foldSH n h).B ⟨.x2 p, hD⟩)) = n - 1
    rw [A_x2H h hw hD, B_x2H h hw hD, finrank_span_singleton (key p).1, finrank_top, hW]; exact dh_one_n hn
  | y2 p =>
    have hD : cl.isD p = true := hr
    show dh (finrank (ZMod 2) ((foldSH n h).A ⟨.y2 p, hD⟩)) (finrank (ZMod 2) ((foldSH n h).B ⟨.y2 p, hD⟩)) = n - 1
    rw [A_y2H h hw hD, B_y2H h hw hD, finrank_bot, finrank_ker_pred _ (key p).2 hW]; exact dh_zero_pred
  | h i => exact absurd rfl hf
  | o i => exact absurd rfl hf

/-- **callH**: the HCall of the fold of a legal word at label rank n >= 1 on any port set (n ports = |Pt|, QR = |D|). -/
noncomputable def callH (hn : 1 ≤ n) {cl : CallerH n Pt} {tr : Trace (Reg Pt Hl Ow)}
    (h : Legal (pubH (Hl := Hl) (Ow := Ow) cl) tr) (hw : WordH cl (exec tr)) :
    HCall n (Fintype.card Pt) (univ.filter (fun p => cl.isD p = true)).card
      (Fld (pubH (Hl := Hl) (Ow := Ow) cl)) (Fin (mlog tr).length) :=
  HCall.ofNet (foldSH n h) (fun c => finrank (ZMod 2) c) n (Fintype.card Pt) _ (minorsH h hw) (hscH h hw)
    (fun c => ht_le_h (Module.finrank_fin_fun _) c) (mainsH cl) (mainsH_climb hn h hw) (mainsH_card cl)

end Mains

/-! ## 3. The headline: the rung from legal words at label rank n -/

section Headline
variable {n : ℕ} {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow]
  [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]

/-- **rung_port_word_h**: for any label rank n >= 3, any port set, any L legal words with the Word end-state clauses:
κ < kbar from the aggregate wall premise `hsum`, the caller Cert, the budget and Valid. -/
theorem rung_port_word_h (hn : 3 ≤ n) (MD : MolData n) (X0 kbar : ℝ) (L : ℕ) (T P : List (ℕ × ℕ))
    (cl : CallerH n Pt)
    (hcert : Cert (fun s => cdat s T - cdat s P - (L : ℝ) *
      UniPort.PortInvX (Fintype.card Pt) (univ.filter (fun p => cl.isD p = true)).card n X0 0 s) kbar)
    (tr : Fin L → Trace (Reg Pt Hl Ow))
    (hleg : ∀ i, Legal (pubH (Hl := Hl) (Ow := Ow) cl) (tr i)) (hw : ∀ i, WordH cl (exec (tr i)))
    (hsum : (L : ℝ) * X0 ≤ ∑ i, (callH (by omega) (hleg i) (hw i)).excess)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hbud : kbar ≤ κ → 0 ≤ bud n MD (fun d : ℕ => (d : ℝ) ^ (1 - κ)))
    (hV : cdat (1 - κ) P + ∑ i, (callH (by omega) (hleg i) (hw i)).spec (1 - κ) ≤
      cdat (1 - κ) T + ∑ i, (callH (by omega) (hleg i) (hw i)).cred (1 - κ)) :
    κ < kbar :=
  rung_port_h_joint n _ _ hn MD X0 kbar L T P hcert (fun i => callH (by omega) (hleg i) (hw i)) hsum κ hκ0 hκ1 hbud hV

/-- **rung_port_word_h8**: label rank 8 (half-spin-64 / E7+A1 danger rank).  hbud is PROVED (BudH.hbud8, kbar >= 146/15625);
the molecule is md8.  Walls enter as per-call decoder masses D_i, R_i (below the call's excess) with the aggregate density premise
L (rhoD + rhoR) |Pt| <= sum (D_i + R_i). -/
theorem rung_port_word_h8 (ρD ρR kbar : ℝ) (hkb : (146 : ℝ) / 15625 ≤ kbar) (L : ℕ) (T P : List (ℕ × ℕ))
    (cl : CallerH 8 Pt)
    (hcert : Cert (fun s => cdat s T - cdat s P - (L : ℝ) *
      UniPort.PortInv (Fintype.card Pt) (univ.filter (fun p => cl.isD p = true)).card 8 ρD ρR 0 s) kbar)
    (tr : Fin L → Trace (Reg Pt Hl Ow))
    (hleg : ∀ i, Legal (pubH (Hl := Hl) (Ow := Ow) cl) (tr i)) (hw : ∀ i, WordH cl (exec (tr i)))
    (Dm Rm : Fin L → ℝ)
    (hJ : (L : ℝ) * ((ρD + ρR) * (Fintype.card Pt : ℝ)) ≤ ∑ i, (Dm i + Rm i))
    (hX : ∀ i, Dm i + Rm i ≤ (callH (by norm_num) (hleg i) (hw i)).excess)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : cdat (1 - κ) P + ∑ i, (callH (by norm_num) (hleg i) (hw i)).spec (1 - κ) ≤
      cdat (1 - κ) T + ∑ i, (callH (by norm_num) (hleg i) (hw i)).cred (1 - κ)) :
    κ < kbar :=
  rung_port_word_h (by norm_num) md8 ((ρD + ρR) * (Fintype.card Pt : ℝ)) kbar L T P cl hcert tr hleg hw
    (le_trans hJ (Finset.sum_le_sum (fun i _ => hX i))) κ hκ0 hκ1 (BudH.hbud8 kbar hkb κ hκ1) hV

/-- **rung_port_word_h7**: label rank 7 (E7 bound); hbud PROVED (BudH.hbud7), molecule md7. -/
theorem rung_port_word_h7 (ρD ρR kbar : ℝ) (hkb : (146 : ℝ) / 15625 ≤ kbar) (L : ℕ) (T P : List (ℕ × ℕ))
    (cl : CallerH 7 Pt)
    (hcert : Cert (fun s => cdat s T - cdat s P - (L : ℝ) *
      UniPort.PortInv (Fintype.card Pt) (univ.filter (fun p => cl.isD p = true)).card 7 ρD ρR 0 s) kbar)
    (tr : Fin L → Trace (Reg Pt Hl Ow))
    (hleg : ∀ i, Legal (pubH (Hl := Hl) (Ow := Ow) cl) (tr i)) (hw : ∀ i, WordH cl (exec (tr i)))
    (Dm Rm : Fin L → ℝ)
    (hJ : (L : ℝ) * ((ρD + ρR) * (Fintype.card Pt : ℝ)) ≤ ∑ i, (Dm i + Rm i))
    (hX : ∀ i, Dm i + Rm i ≤ (callH (by norm_num) (hleg i) (hw i)).excess)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : cdat (1 - κ) P + ∑ i, (callH (by norm_num) (hleg i) (hw i)).spec (1 - κ) ≤
      cdat (1 - κ) T + ∑ i, (callH (by norm_num) (hleg i) (hw i)).cred (1 - κ)) :
    κ < kbar :=
  rung_port_word_h (by norm_num) md7 ((ρD + ρR) * (Fintype.card Pt : ℝ)) kbar L T P cl hcert tr hleg hw
    (le_trans hJ (Finset.sum_le_sum (fun i _ => hX i))) κ hκ0 hκ1 (BudH.hbud7 kbar hkb κ hκ1) hV

end Headline

end RungWordH

#print axioms RungWordH.mainsH_card
#print axioms RungWordH.mainsH_climb
#print axioms RungWordH.rung_port_h_joint
#print axioms RungWordH.rung_port_word_h7
#print axioms RungWordH.rung_port_word_h8
