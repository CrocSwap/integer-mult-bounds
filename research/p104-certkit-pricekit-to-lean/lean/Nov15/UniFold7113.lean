/-
UniFold7113 (lane UNI-L2B, Nov 19).  The two CALLER facts that UniBank.foldBanked takes as premises, discharged for
EVERY legal word under the #7113 caller contract (no per-word data):
* `minors7113`  : every principal minor of (foldS h).O is nonzero.  O f g = tgt cl f g (Word.final_row: the output matrix
  is pinned by the caller targets, independent.py l.79-87 / linear.py:66), and tgt is block diagonal with blocks
  D [[1,0],[1,1]], B [[1,-1],[1/2,1/2]], hosted [[1,-1],[0,1]], helper [1]; each block has positive definite symmetric part,
  so  4·xᵀOx ≥ |x|²  (`qform_ge`), and a matrix with xᵀMx > 0 has all principal minors nonzero (`minors_of_pos`).
* `con7113`     : BankWireD.Contract (foldS h): π = X↔Y, X2↔Y2 (involution ⇒ in-degree clauses), rowO i = X2 (D port) or
  X (B port) of the port labelled OUT_i, rowI i = Y of the port labelled IN_i; needs only `Ports7113 cl` (the caller's
  104 port labels are the #7113 ports) and the 28 counted flag lines ⊆ ports7113 (decide).
* `foldBanked7113` : a BankedGraph from any Legal trace whose end state is a Word, with ONLY the verifier clauses as
  hypotheses: FramesSubsp + ChartsSubsp (independent.py l.26-31 `span`, l.33 `frames=[span(b)...]`) and OwnedNested
  (independent.py l.51 owned MOVE `frames[a]<frames[b] or frames[b]<frames[a]`).
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.UniBank

set_option linter.unusedSectionVars false

namespace UniFold7113
open Finset Module Matrix WordModel Uni SafeRungsClique BankFlagB

/-! ## 1. Principal minors from a positive quadratic form -/

theorem sum_eq_subtype {ι : Type} [Fintype ι] (C : Finset ι) (g : ι → ℚ) (hg : ∀ i ∉ C, g i = 0) :
    ∑ i, g i = ∑ c : C, g c := by
  rw [Finset.sum_coe_sort C g]
  exact (Finset.sum_subset (subset_univ C) (fun i _ hi => hg i hi)).symm

/-- a matrix whose quadratic form is positive on nonzero vectors has every principal minor nonzero. -/
theorem minors_of_pos {ι : Type} [Fintype ι] [DecidableEq ι] (M : Matrix ι ι ℚ)
    (hpos : ∀ x : ι → ℚ, x ≠ 0 → 0 < x ⬝ᵥ (M *ᵥ x)) (C : Finset ι) :
    (M.submatrix (fun c : C => c.1) (fun c : C => c.1)).det ≠ 0 := by
  intro hdet
  obtain ⟨v, hv0, hv⟩ := (Matrix.exists_mulVec_eq_zero_iff).2 hdet
  let w : ι → ℚ := fun i => if h : i ∈ C then v ⟨i, h⟩ else 0
  have hwc : ∀ c : C, w c = v c := fun c => by simp [w, c.2]
  have hw0 : ∀ i ∉ C, w i = 0 := fun i hi => by simp [w, hi]
  have hMw : ∀ c : C, (M *ᵥ w) c = (M.submatrix (fun c : C => c.1) (fun c : C => c.1) *ᵥ v) c := by
    intro c
    simp only [mulVec, dotProduct, submatrix_apply]
    rw [sum_eq_subtype C _ (fun j hj => by rw [hw0 j hj, mul_zero])]
    exact Finset.sum_congr rfl (fun d _ => by rw [hwc d])
  have hq : w ⬝ᵥ (M *ᵥ w) = 0 := by
    unfold dotProduct
    rw [sum_eq_subtype C _ (fun j hj => by rw [hw0 j hj, zero_mul])]
    refine Finset.sum_eq_zero (fun c _ => ?_)
    rw [hMw c, hv]; simp
  have hwne : w ≠ 0 := by
    intro h0; apply hv0; funext c
    have := congrFun h0 c
    rw [hwc c] at this; simpa using this
  have := hpos w hwne
  rw [hq] at this
  exact lt_irrefl _ this

/-! ## 2. The caller's output matrix: tgt is positive definite on public coordinates -/

section Caller
variable {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow]
  [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]

/-- a sum over registers, split by role (pairs X,Y and X2,Y2 per port; helpers; owned). -/
theorem sum_reg (F : Reg Pt Hl Ow → ℚ) :
    ∑ r, F r = ∑ p, (F (.x p) + F (.y p)) + ∑ p, (F (.x2 p) + F (.y2 p)) + ∑ i, F (.h i) + ∑ i, F (.o i) := by
  rw [← Fintype.sum_equiv regEquiv.symm (fun z => F (regEquiv.symm z)) F (fun _ => rfl)]
  simp only [Fintype.sum_sum_type]
  show (∑ p, F (.x p)) + ((∑ p, F (.y p)) + ((∑ p, F (.x2 p)) + ((∑ p, F (.y2 p)) +
    ((∑ i, F (.h i)) + (∑ i, F (.o i)))))) = _
  rw [Finset.sum_add_distrib, Finset.sum_add_distrib]; ring

/-- public fields → registers, extended by 0. -/
def ext (cl : Caller Pt) (x : Fld (pub (Hl := Hl) (Ow := Ow) cl) → ℚ) : Reg Pt Hl Ow → ℚ :=
  fun r => if h : pub cl r = true then x ⟨r, h⟩ else 0

theorem ext_val (cl : Caller Pt) (x : Fld (pub (Hl := Hl) (Ow := Ow) cl) → ℚ) (f : Fld (pub (Hl := Hl) (Ow := Ow) cl)) :
    ext cl x f.1 = x f := by simp [ext, f.2]

theorem ext_off (cl : Caller Pt) (x : Fld (pub (Hl := Hl) (Ow := Ow) cl) → ℚ) {r : Reg Pt Hl Ow}
    (h : pub cl r = false) : ext cl x r = 0 := by simp [ext, h]

theorem sum_fld (cl : Caller Pt) (g : Reg Pt Hl Ow → ℚ) (hg : ∀ r, pub cl r = false → g r = 0) :
    ∑ f : Fld (pub (Hl := Hl) (Ow := Ow) cl), g f.1 = ∑ r, g r := by
  rw [← Finset.sum_subtype (univ.filter (fun r => pub cl r = true)) (fun r => by simp) g]
  exact Finset.sum_subset (subset_univ _) (fun r _ hr => hg r (by simpa using hr))

/-- the quadratic form of the caller's output matrix, on registers. -/
theorem qform_eq (cl : Caller Pt) (M : Matrix (Fld (pub (Hl := Hl) (Ow := Ow) cl)) (Fld (pub (Hl := Hl) (Ow := Ow) cl)) ℚ)
    (hM : ∀ f g, M f g = tgt cl f.1 g.1) (x : Fld (pub (Hl := Hl) (Ow := Ow) cl) → ℚ) :
    x ⬝ᵥ (M *ᵥ x) = ∑ r, ext cl x r * (tgt cl r ⬝ᵥ ext cl x) := by
  have hrow : ∀ f, (M *ᵥ x) f = tgt cl f.1 ⬝ᵥ ext cl x := by
    intro f
    simp only [mulVec, dotProduct, hM]
    rw [← sum_fld cl (fun r => tgt cl f.1 r * ext cl x r) (fun r hr => by rw [ext_off cl x hr, mul_zero])]
    exact Finset.sum_congr rfl (fun g _ => by rw [ext_val])
  show ∑ f, x f * (M *ᵥ x) f = _
  simp only [hrow]
  rw [← sum_fld cl (fun r => ext cl x r * (tgt cl r ⬝ᵥ ext cl x)) (fun r hr => by rw [ext_off cl x hr, zero_mul])]
  exact Finset.sum_congr rfl (fun f _ => by rw [ext_val])

/-- 4 · yᵀ tgt y ≥ |y|² when y vanishes on owned registers (2x2 blocks with positive definite symmetric part). -/
theorem qform_ge (cl : Caller Pt) (y : Reg Pt Hl Ow → ℚ) (ho : ∀ i, y (.o i) = 0) :
    ∑ r, y r ^ 2 ≤ ∑ r, 4 * (y r * (tgt cl r ⬝ᵥ y)) := by
  rw [sum_reg, sum_reg]
  refine add_le_add (add_le_add (add_le_add (Finset.sum_le_sum fun p _ => ?_) (Finset.sum_le_sum fun p _ => ?_))
    (Finset.sum_le_sum fun i _ => ?_)) (Finset.sum_le_sum fun i _ => ?_)
  · cases hD : cl.isD p <;>
      simp [tgt, e, hD, sub_dotProduct, add_dotProduct, smul_dotProduct, single_dotProduct] <;>
      nlinarith [sq_nonneg (y (.x p) + y (.y p)), sq_nonneg (y (.x p) - y (.y p)), sq_nonneg (y (.x p)),
        sq_nonneg (y (.y p))]
  · simp [tgt, e, sub_dotProduct, single_dotProduct]
    nlinarith [sq_nonneg (y (.x2 p) + y (.y2 p)), sq_nonneg (y (.x2 p) - y (.y2 p)), sq_nonneg (y (.x2 p)),
      sq_nonneg (y (.y2 p))]
  · simp [tgt, e, single_dotProduct]; nlinarith [sq_nonneg (y (.h i))]
  · simp [tgt, ho i]

theorem qform_pos (cl : Caller Pt) (M : Matrix (Fld (pub (Hl := Hl) (Ow := Ow) cl)) (Fld (pub (Hl := Hl) (Ow := Ow) cl)) ℚ)
    (hM : ∀ f g, M f g = tgt cl f.1 g.1) (x : Fld (pub (Hl := Hl) (Ow := Ow) cl) → ℚ) (hx : x ≠ 0) :
    0 < x ⬝ᵥ (M *ᵥ x) := by
  rw [qform_eq cl M hM x]
  obtain ⟨f, hf⟩ : ∃ f, x f ≠ 0 := by
    by_contra hc; push Not at hc; exact hx (funext hc)
  have h1 : 0 < ∑ r, ext cl x r ^ 2 := by
    refine lt_of_lt_of_le ?_ (Finset.single_le_sum (fun r _ => sq_nonneg (ext cl x r)) (mem_univ f.1))
    rw [ext_val]; positivity
  have h2 := qform_ge cl (ext cl x) (fun i => ext_off cl x rfl)
  rw [← Finset.mul_sum] at h2
  linarith

/-! ## 3. The folded output matrix is the caller's target matrix -/

theorem foldS_O (cl : Caller Pt) {tr : Trace (Reg Pt Hl Ow)} (h : Legal (pub cl) tr) (hw : Word cl (exec tr))
    (f g : Fld (pub (Hl := Hl) (Ow := Ow) cl)) : (foldS h).O f g = tgt cl f.1 g.1 := by
  show fO (pb := pub cl) tr f g = _
  unfold fO oRow
  obtain ⟨c, hc⟩ := hw.pub_sit f.1 f.2
  rw [hc]
  simp [restr, LinearMap.funLeft_apply, hw.final_row f.1 f.2]

/-- **minors7113**: every principal minor of the folded output matrix of a legal 7113 word is nonzero. -/
theorem minors7113 (cl : Caller Pt) {tr : Trace (Reg Pt Hl Ow)} (h : Legal (pub cl) tr) (hw : Word cl (exec tr))
    (C : Finset (Fld (pub (Hl := Hl) (Ow := Ow) cl))) :
    ((foldS h).O.submatrix (fun c : C => c.1) (fun c : C => c.1)).det ≠ 0 :=
  minors_of_pos _ (qform_pos cl _ (foldS_O cl h hw)) C

/-! ## 4. The Contract -/

/-- the 104 #7113 port labels (t7669.json / w_s4.json `ports`, identical; = TradeLawsCapData.ports). -/
def ports7113 : List ℕ := [11, 19, 35, 131, 259, 13, 21, 37, 69, 133, 261, 41, 73, 265, 49, 81, 145, 273, 161, 193,
  321, 385, 14, 22, 38, 70, 134, 262, 26, 74, 138, 50, 146, 274, 98, 290, 194, 322, 386, 28, 44, 140, 268, 84, 148, 276,
  100, 164, 292, 196, 324, 388, 56, 88, 152, 280, 168, 296, 200, 328, 392, 112, 176, 304, 208, 336, 400, 224, 352, 416,
  508, 506, 502, 494, 478, 446, 382, 254, 505, 501, 493, 477, 445, 381, 253, 499, 475, 443, 379, 251, 487, 471, 439, 375,
  247, 463, 431, 367, 239, 415, 351, 223, 319, 191]

/-- caller premise: the caller's port labels are the #7113 ports. -/
def Ports7113 (cl : Caller Pt) : Prop := ∀ q ∈ ports7113, ∃ p, cl.lab p = q

theorem out_lab : ∀ i ∈ cnt OUT, (OUT.getD i (0, 0)).1 ∈ ports7113 ∧ (OUT.getD i (0, 0)).2 = (OUT.getD i (0, 0)).1 := by
  rw [out_cnt]; decide +kernel
theorem in_lab : ∀ i ∈ cnt IN, (IN.getD i (0, 0)).1 ∈ ports7113 ∧ (IN.getD i (0, 0)).2 = (IN.getD i (0, 0)).1 := by
  rw [in_cnt]; decide +kernel
theorem out_inj : ∀ i ∈ cnt OUT, ∀ i' ∈ cnt OUT, (OUT.getD i (0, 0)).1 = (OUT.getD i' (0, 0)).1 → i = i' := by
  rw [out_cnt]; decide +kernel
theorem in_inj : ∀ i ∈ cnt IN, ∀ i' ∈ cnt IN, (IN.getD i (0, 0)).1 = (IN.getD i' (0, 0)).1 → i = i' := by
  rw [in_cnt]; decide +kernel

/-- the port carrying label q (if any). -/
noncomputable def portOf (cl : Caller Pt) (q : ℕ) : Pt := by
  classical
  exact if h : ∃ p, cl.lab p = q then Classical.choose h
    else Classical.choice (Fintype.card_pos_iff.1 (by rw [cl.card104]; norm_num))

theorem lab_portOf (cl : Caller Pt) {q : ℕ} (hq : ∃ p, cl.lab p = q) : cl.lab (portOf cl q) = q := by
  unfold portOf; rw [dif_pos hq]; exact Classical.choose_spec hq

/-- partner swap X↔Y, X2↔Y2. -/
def sw : Reg Pt Hl Ow → Reg Pt Hl Ow
  | .x p => .y p | .y p => .x p | .x2 p => .y2 p | .y2 p => .x2 p | .h i => .h i | .o i => .o i

theorem sw_sw (r : Reg Pt Hl Ow) : sw (sw r) = r := by cases r <;> rfl
theorem pub_sw (cl : Caller Pt) (r : Reg Pt Hl Ow) : pub cl (sw r) = pub cl r := by cases r <;> rfl

def piF (cl : Caller Pt) (f : Fld (pub (Hl := Hl) (Ow := Ow) cl)) : Fld (pub (Hl := Hl) (Ow := Ow) cl) :=
  ⟨sw f.1, by rw [pub_sw]; exact f.2⟩

theorem piF_inj (cl : Caller Pt) : Function.Injective (piF (Hl := Hl) (Ow := Ow) cl) := by
  intro a b hab
  apply Subtype.ext
  have := congrArg (fun f => sw f.1) hab
  simpa [piF, sw_sw] using this

noncomputable def rowO (cl : Caller Pt) (i : ℕ) : Fld (pub (Hl := Hl) (Ow := Ow) cl) :=
  if hD : cl.isD (portOf cl (OUT.getD i (0, 0)).1) = true then ⟨.x2 (portOf cl (OUT.getD i (0, 0)).1), hD⟩
  else ⟨.x (portOf cl (OUT.getD i (0, 0)).1), rfl⟩

noncomputable def rowI (cl : Caller Pt) (i : ℕ) : Fld (pub (Hl := Hl) (Ow := Ow) cl) :=
  ⟨.y (portOf cl (IN.getD i (0, 0)).1), rfl⟩

def rp : Reg Pt Hl Ow → Option Pt
  | .x p => some p | .y p => some p | .x2 p => some p | .y2 p => some p | _ => none

theorem rp_rowO (cl : Caller Pt) (i : ℕ) :
    rp (rowO (Hl := Hl) (Ow := Ow) cl i).1 = some (portOf cl (OUT.getD i (0, 0)).1) := by
  unfold rowO; split <;> rfl

theorem tgt_supp (cl : Caller Pt) (r t : Reg Pt Hl Ow) (hne : tgt cl r t ≠ 0) : t = r ∨ t = sw r := by
  by_contra hc
  push Not at hc
  obtain ⟨h1, h2⟩ := hc
  apply hne
  cases r <;> simp only [tgt, sw] at h2 ⊢ <;> (try split_ifs) <;> simp [e, Pi.single_apply, h1, h2]

section Charts
variable {cl : Caller Pt} {tr : Trace (Reg Pt Hl Ow)} (h : Legal (pub cl) tr) (hw : Word cl (exec tr))
include h hw

theorem A_x {p : Pt} {q : ℕ} (hl : cl.lab p = q) :
    (foldS h).A ⟨.x p, rfl⟩ = Submodule.span (ZMod 2) {BankWireC.vec q} := by
  show toSub (fA tr _) = _
  rw [fA_eq h (hw.x_birth p), toSub_line, hl]; rfl
theorem B_x (p : Pt) : (foldS h).B ⟨.x p, rfl⟩ = ⊤ := by
  show toSub (fB tr _) = _
  rw [fB_eq (hw.x_final p), toSub_Vc]
theorem A_y (p : Pt) : (foldS h).A ⟨.y p, rfl⟩ = ⊥ := by
  show toSub (fA tr _) = _
  rw [fA_eq h (hw.y_birth p), toSub_zero]
theorem B_y {p : Pt} {q : ℕ} (hl : cl.lab p = q) :
    (foldS h).B ⟨.y p, rfl⟩ = LinearMap.ker (BankWireC.phi q) := by
  show toSub (fB tr _) = _
  rw [fB_eq (hw.y_final p), toSub_Hq (cl.lab_lt p), hl]
theorem A_x2 {p : Pt} (hD : cl.isD p = true) {q : ℕ} (hl : cl.lab p = q) :
    (foldS h).A ⟨.x2 p, hD⟩ = Submodule.span (ZMod 2) {BankWireC.vec q} := by
  show toSub (fA tr _) = _
  rw [fA_eq h (hw.x2_birth p hD), toSub_line, hl]; rfl
theorem B_x2 {p : Pt} (hD : cl.isD p = true) : (foldS h).B ⟨.x2 p, hD⟩ = ⊤ := by
  show toSub (fB tr _) = _
  rw [fB_eq (hw.x2_final p hD), toSub_Vc]
theorem A_y2 {p : Pt} (hD : cl.isD p = true) : (foldS h).A ⟨.y2 p, hD⟩ = ⊥ := by
  show toSub (fA tr _) = _
  rw [fA_eq h (hw.y2_birth p hD), toSub_zero]
theorem B_y2 {p : Pt} (hD : cl.isD p = true) {q : ℕ} (hl : cl.lab p = q) :
    (foldS h).B ⟨.y2 p, hD⟩ = LinearMap.ker (BankWireC.phi q) := by
  show toSub (fB tr _) = _
  rw [fB_eq (hw.y2_final p hD), toSub_Hq (cl.lab_lt p), hl]

end Charts

/-- **con7113**: the main contract of a legal 7113 word's fold. -/
noncomputable def con7113 (cl : Caller Pt) (hP : Ports7113 cl) {tr : Trace (Reg Pt Hl Ow)} (h : Legal (pub cl) tr)
    (hw : Word cl (exec tr)) : BankWireD.Contract (foldS h) where
  π := piF cl
  rowO := rowO cl
  rowI := rowI cl
  hsupp f g hne := by
    rw [foldS_O cl h hw] at hne
    rcases tgt_supp cl _ _ hne with h1 | h1
    · exact Or.inl (Subtype.ext h1)
    · exact Or.inr (Subtype.ext h1)
  injO i hi i' hi' he := by
    have h1 := congrArg (fun f => rp f.1) he
    simp only [rp_rowO] at h1
    have h2 := congrArg cl.lab (Option.some.inj h1)
    rw [lab_portOf cl (hP _ (out_lab i hi).1), lab_portOf cl (hP _ (out_lab i' hi').1)] at h2
    exact out_inj i hi i' hi' h2
  injI i hi i' hi' he := by
    have h1 := congrArg (fun f => rp f.1) he
    simp only [rowI, rp] at h1
    have h2 := congrArg cl.lab (Option.some.inj h1)
    rw [lab_portOf cl (hP _ (in_lab i hi).1), lab_portOf cl (hP _ (in_lab i' hi').1)] at h2
    exact in_inj i hi i' hi' h2
  chartO i hi := by
    have hl := lab_portOf cl (hP _ (out_lab i hi).1)
    rw [(out_lab i hi).2]
    unfold rowO
    split_ifs with hD
    · exact ⟨A_x2 h hw hD hl, B_x2 h hw hD, A_y2 h hw hD, B_y2 h hw hD hl⟩
    · exact ⟨A_x h hw hl, B_x h hw _, A_y h hw _, B_y h hw hl⟩
  chartI i hi := by
    have hl := lab_portOf cl (hP _ (in_lab i hi).1)
    rw [(in_lab i hi).2]
    exact ⟨A_y h hw _, B_y h hw hl, A_x h hw hl, B_x h hw _⟩
  nzO i _ := by
    rw [foldS_O cl h hw]
    unfold rowO
    generalize portOf cl (OUT.getD i (0, 0)).1 = p
    split_ifs with hD
    · simp [piF, sw, tgt, e]
    · rw [Bool.not_eq_true] at hD
      simp [piF, sw, tgt, e, hD]
  nzI i _ := by
    rw [foldS_O cl h hw]
    simp only [rowI, piF, sw, tgt]
    split_ifs <;> simp [e, Pi.single_apply]
  indegO _ _ _ _ _ _ hr := piF_inj cl hr
  indegI _ _ _ _ _ _ hr := piF_inj cl hr

/-! ## 5. The bridge: every legal 7113 word is a banked graph -/

/-- **foldBanked7113**: a legal trace under a #7113 caller (ports = ports7113, 96 D ports) whose end state is a Word is a
BankedGraph with N = foldS h; the ONLY hypotheses beyond legality are the verifier clauses FramesSubsp, ChartsSubsp
(independent.py l.26-31, l.33) and OwnedNested (l.51). -/
noncomputable def foldBanked7113 (cl : Caller Pt) (hP : Ports7113 cl) (hD : DCount cl) {tr : Trace (Reg Pt Hl Ow)}
    (h : Legal (pub cl) tr) (hw : Word cl (exec tr)) (hfr : FramesSubsp (exec tr)) (hcs : ChartsSubsp (exec tr))
    (hn : OwnedNested (exec tr)) :
    BankFit.BankedGraph ℚ (Fld (pub (Hl := Hl) (Ow := Ow) cl)) (Fin (mlog tr).length) :=
  foldBanked cl h hw hfr hcs hn hD (minors7113 cl h hw) (con7113 cl hP h hw)

theorem foldBanked7113_N (cl : Caller Pt) (hP : Ports7113 cl) (hD : DCount cl) {tr : Trace (Reg Pt Hl Ow)}
    (h : Legal (pub cl) tr) (hw : Word cl (exec tr)) (hfr : FramesSubsp (exec tr)) (hcs : ChartsSubsp (exec tr))
    (hn : OwnedNested (exec tr)) : (foldBanked7113 cl hP hD h hw hfr hcs hn).N = foldS h := rfl

/-- ∀-form: every legal 7113 word, under the verifier clauses, folds to a banked graph. -/
theorem banked7113 (cl : Caller Pt) (hP : Ports7113 cl) (hD : DCount cl) :
    ∀ (tr : Trace (Reg Pt Hl Ow)) (h : Legal (pub cl) tr), Word cl (exec tr) → FramesSubsp (exec tr) →
      ChartsSubsp (exec tr) → OwnedNested (exec tr) →
      ∃ G : BankFit.BankedGraph ℚ (Fld (pub (Hl := Hl) (Ow := Ow) cl)) (Fin (mlog tr).length), G.N = foldS h :=
  fun _ h hw hfr hcs hn => ⟨foldBanked7113 cl hP hD h hw hfr hcs hn, rfl⟩

/-- its banked SPEC invoice = the word's paid invoice. -/
theorem foldBanked7113_paid (cl : Caller Pt) (hP : Ports7113 cl) (hD : DCount cl) {tr : Trace (Reg Pt Hl Ow)}
    (h : Legal (pub cl) tr) (hw : Word cl (exec tr)) (hfr : FramesSubsp (exec tr)) (hcs : ChartsSubsp (exec tr))
    (hn : OwnedNested (exec tr)) (σ : ℝ) :
    ∑ k, BankPrem.specInvoice (foldBanked7113 cl hP hD h hw hfr hcs hn) σ k = wordPaid cl (exec tr) specPrice σ :=
  foldBanked_paid cl h hw hfr hcs hn hD _ _ σ

end Caller

end UniFold7113

#print axioms UniFold7113.minors_of_pos
#print axioms UniFold7113.minors7113
#print axioms UniFold7113.con7113
#print axioms UniFold7113.foldBanked7113
#print axioms UniFold7113.banked7113
#print axioms UniFold7113.foldBanked7113_paid
