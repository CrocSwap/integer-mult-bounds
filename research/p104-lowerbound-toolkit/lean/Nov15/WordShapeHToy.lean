/-
WordShapeHToy (lane WORDSHAPEH, Nov 20).  NON-VACUITY of WordShapeH / RungWordH at label rank 8: a CONCRETE legal word (one B port, label 1, one owned carrier)
whose end state satisfies WordH, so hscH, minorsH, mainsH_card and the cut inequality are instantiated on a real trace (not on hand-built nets).
  trace (12 events): birth x at line 1, y at {0}, owned o at {0}; o := e_y; o -> line 1; x := x - o  (= e_x - e_y); o := x/2 + o  (= e_x/2 + e_y/2);
  y -> q^perp; o -> q^perp; y := o; clear o; x -> V.     Final rows = tgtH (non-D port).
Kernel only.
-/
import Nov15.RungWordH

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false
set_option maxRecDepth 100000

namespace WordShapeHToy
open Finset Module WordModel Uni WordShapeH RungWordH HCutGen PriceH

abbrev R0 := Reg Unit Empty Unit

def clT : CallerH 8 Unit where
  lab := fun _ => 1
  isD := fun _ => false
  lab_lt := fun _ => by norm_num
  lab_ne := fun _ => by norm_num

def X : R0 := .x ()
def Y : R0 := .y ()
def O : R0 := .o ()

/-- computable twin of HqH 8 1 (explicit decidable instance, so the kernel can evaluate it). -/
def HqT : Ch := (range 256).filter (fun v => dotH 8 v 1 = 0)

theorem hq : HqH 8 1 = HqT := by
  ext v; simp [HqH, HqT]

instance okDec (pb : R0 → Bool) (s : St R0) (e : Ev R0) : Decidable (e.ok pb s) := by
  cases e <;> (unfold Ev.ok; infer_instance)

def trT : Trace R0 :=
  [ .birthPub X (line 1), .birthPub Y zeroCh, .birthOwn O zeroCh,
    .gate O zeroCh (Pi.single Y 1), .moveOwn O zeroCh (line 1),
    .gate X (line 1) (fun t => if t = X then 1 else if t = O then -1 else 0),
    .gate O (line 1) (fun t => if t = X then 1 / 2 else if t = O then 1 else 0),
    .movePub Y zeroCh HqT, .moveOwn O (line 1) HqT,
    .gate Y HqT (fun t => if t = O then 1 else 0),
    .clearOwn O HqT, .movePub X (line 1) (VcH 8) ]

theorem trT_legal : Legal (pubH (Hl := Empty) (Ow := Unit) clT) trT := by
  unfold Legal
  simp only [trT, LegalFrom]
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, trivial⟩ <;> decide +kernel

theorem loc_x2 : (exec trT).loc (.x2 ()) = .unborn := by decide +kernel
theorem loc_y2 : (exec trT).loc (.y2 ()) = .unborn := by decide +kernel
theorem loc_o : (exec trT).loc (.o ()) = .cleared := by decide +kernel

theorem trT_word : WordH clT (exec trT) where
  reach := reach_exec trT_legal
  pub_sit r hr := by
    cases r with
    | x p => cases p; exact ⟨VcH 8, by decide +kernel⟩
    | y p => cases p; exact ⟨HqT, by decide +kernel⟩
    | x2 p => exact absurd hr (by simp [pubH, clT])
    | y2 p => exact absurd hr (by simp [pubH, clT])
    | h i => exact i.elim
    | o i => exact absurd hr (by simp [pubH])
  own_off r c hr := by
    cases r with
    | x p => exact absurd hr (by simp [pubH])
    | y p => exact absurd hr (by simp [pubH])
    | x2 p => cases p; rw [loc_x2]; intro h; cases h
    | y2 p => cases p; rw [loc_y2]; intro h; cases h
    | h i => exact i.elim
    | o i => cases i; rw [loc_o]; intro h; cases h
  x_birth p := by cases p; decide +kernel
  x_final p := by cases p; decide +kernel
  y_birth p := by cases p; decide +kernel
  y_final p := by cases p; show _ = Loc.sit (HqH 8 1); rw [hq]; decide +kernel
  x2_birth p hD := by exact absurd hD (by simp [clT])
  x2_final p hD := by exact absurd hD (by simp [clT])
  y2_birth p hD := by exact absurd hD (by simp [clT])
  y2_final p hD := by exact absurd hD (by simp [clT])
  final_row r hr := by
    cases r with
    | x p => cases p; decide +kernel
    | y p => cases p; decide +kernel
    | x2 p => exact absurd hr (by simp [pubH, clT])
    | y2 p => exact absurd hr (by simp [pubH, clT])
    | h i => exact i.elim
    | o i => exact absurd hr (by simp [pubH])

/-- the contract of the toy fold. -/
noncomputable def toyHSC := hscH trT_legal trT_word

theorem toy_minors (C : Finset (Fld (pubH (Hl := Empty) (Ow := Unit) clT))) :
    ((foldSH 8 trT_legal).O.submatrix (fun c : C => c.1) (fun c : C => c.1)).det ≠ 0 :=
  minorsH trT_legal trT_word C

theorem toy_mains : (mainsH (Hl := Empty) (Ow := Unit) clT).card = 2 := by
  rw [mainsH_card]; decide

/-- the cut inequality of the toy word's fold at every mask (n = |Pt| = 1). -/
theorem toy_cut (m : ℕ) :
    ∑ f, xcut m (finrank (ZMod 2) ((foldSH 8 trT_legal).A f)) (finrank (ZMod 2) ((foldSH 8 trT_legal).B f))
      + (if isSepH 8 m then 2 * Fintype.card Unit else 0) ≤
    ∑ k, xcut m (finrank (ZMod 2) ((foldSH 8 trT_legal).src k)) (finrank (ZMod 2) ((foldSH 8 trT_legal).dst k)) :=
  cut_hsH (foldSH 8 trT_legal) (fun C => minorsH trT_legal trT_word C) toyHSC m

end WordShapeHToy

#print axioms WordShapeHToy.trT_legal
#print axioms WordShapeHToy.trT_word
#print axioms WordShapeHToy.toy_cut
#print axioms WordShapeHToy.toy_mains
