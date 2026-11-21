/-
WordShapeH (lane WORDSHAPEH, Nov 20).  The word-shape lemma at ANY label rank n (= h), any port set:
the analogue of UniFold7113 (A_x/B_x/A_y/B_y, foldS_O, minors7113) and UniHSC7113 (hsc7113) typed at F_2^n instead of Fin 9.
  * charts: Finset-ℕ label charts (WordModelDefs.Ch) with VcH n = range (2^n), HqH n q = {v < 2^n | v . q = 0}, line q, {0};
    bridge toSubH n : Ch -> Submodule (ZMod 2) (Fin n -> ZMod 2)  (span of the label vectors);
    toSubH_zero / toSubH_line / toSubH_Vc / toSubH_Hq : the shapes bot, span{vec q}, top, ker(phiH q).
  * CallerH n Pt: port labels lab p in [1, 2^n) (any nonzero label), D-port flag; pubH, tgtH (the #7113 target rows), WordH n cl s (= WordModel.Word with
    the label-rank-n constants; the SAME final-state clauses).
  * foldSH h : the fold of a legal trace as a Net over submodules of F_2^n (UniTrace.fold pushed through toSubH).
  * A_xH, B_xH, A_yH, B_yH (+ x2/y2): the port-row chart shape.   foldSH_O : O = tgtH.   minorsH : every principal minor nonzero.
  * hscH : HCutGen.HSContractH (foldSH h) finrank n |Pt| : the height-stop contract of the fold of EVERY legal word on any port set.
  * mains: mainsH (x, y of every port, x2, y2 of D ports): climb n-1, card 2|Pt| + 2|D|  (so hmain, hcard are PROVED, QR = |D|).
Nothing here is P104 data: the 9 and 104 of UniHSC7113 enter only as finrank V = n and the port count.
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.HCutGen
import Nov15.UniTrace

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace WordShapeH
open Finset Module Matrix WordModel Uni

/-! ## 1. F_2^n label vectors and charts -/

abbrev VH (n : ℕ) := Fin n → ZMod 2

/-- the bit vector of label m. -/
def vecH (n m : ℕ) : VH n := fun i => if m.testBit i then 1 else 0

theorem vecH_xor (n a b : ℕ) : vecH n (a ^^^ b) = vecH n a + vecH n b := by
  funext i
  simp only [vecH, Nat.testBit_xor, Pi.add_apply]
  cases a.testBit i <;> cases b.testBit i <;> decide

theorem vecH_zero (n : ℕ) : vecH n 0 = 0 := by funext i; simp [vecH]

theorem vecH_inj (n : ℕ) {a b : ℕ} (ha : a < 2 ^ n) (hb : b < 2 ^ n) (h : vecH n a = vecH n b) : a = b := by
  apply Nat.eq_of_testBit_eq
  intro i
  by_cases hi : i < n
  · have := congrFun h ⟨i, hi⟩
    simp only [vecH] at this
    cases ha' : a.testBit i <;> cases hb' : b.testBit i <;> simp_all
  · have h9 : 2 ^ n ≤ 2 ^ i := Nat.pow_le_pow_right (by norm_num) (by omega)
    rw [Nat.testBit_lt_two_pow (lt_of_lt_of_le ha h9), Nat.testBit_lt_two_pow (lt_of_lt_of_le hb h9)]

theorem vecH_surj (n : ℕ) (v : VH n) : ∃ m < 2 ^ n, vecH n m = v := by
  classical
  have hinj : Set.InjOn (vecH n) (↑(range (2 ^ n)) : Set ℕ) := fun a ha b hb h =>
    vecH_inj n (mem_range.1 ha) (mem_range.1 hb) h
  have hc : ((range (2 ^ n)).image (vecH n)).card = Fintype.card (VH n) := by
    rw [card_image_of_injOn hinj, card_range]
    simp [VH, Fintype.card_fun, ZMod.card]
  have hu := Finset.eq_univ_of_card _ hc
  have : v ∈ (range (2 ^ n)).image (vecH n) := by rw [hu]; exact mem_univ v
  obtain ⟨m, hm, rfl⟩ := mem_image.1 this
  exact ⟨m, mem_range.1 hm, rfl⟩

/-- span of a chart's label vectors. -/
noncomputable def toSubH (n : ℕ) (c : Ch) : Submodule (ZMod 2) (VH n) := Submodule.span (ZMod 2) (vecH n '' ↑c)

/-- the full chart V = F_2^n. -/
def VcH (n : ℕ) : Ch := range (2 ^ n)

/-- F_2 dot product of two label vectors. -/
def dotH (n a b : ℕ) : ZMod 2 := ∑ i : Fin n, if a.testBit i ∧ b.testBit i then 1 else 0

/-- q^⊥ = labels orthogonal to q. -/
noncomputable def HqH (n q : ℕ) : Ch := by
  classical exact (range (2 ^ n)).filter (fun v => dotH n v q = 0)

/-- the linear form v ↦ v . q. -/
def phiH (n a : ℕ) : VH n →ₗ[ZMod 2] ZMod 2 :=
  ∑ i : Fin n, if a.testBit i then (LinearMap.proj i : VH n →ₗ[ZMod 2] ZMod 2) else 0

theorem phiH_apply (n a : ℕ) (x : VH n) : phiH n a x = ∑ i : Fin n, if a.testBit i then x i else 0 := by
  unfold phiH
  simp only [LinearMap.sum_apply]
  refine Finset.sum_congr rfl (fun i _ => ?_)
  split_ifs <;> simp

theorem phiH_vec (n a b : ℕ) : phiH n a (vecH n b) = dotH n b a := by
  rw [phiH_apply]
  unfold dotH
  refine Finset.sum_congr rfl (fun i _ => ?_)
  by_cases h1 : a.testBit i <;> by_cases h2 : b.testBit i <;> simp [vecH, h1, h2]

theorem toSubH_zero (n : ℕ) : toSubH n zeroCh = ⊥ := by
  simp [toSubH, zeroCh, vecH_zero]

theorem toSubH_line (n q : ℕ) : toSubH n (line q) = Submodule.span (ZMod 2) {vecH n q} := by
  unfold toSubH line
  rw [Finset.coe_insert, Finset.coe_singleton, Set.image_insert_eq, Set.image_singleton, vecH_zero,
    Submodule.span_insert_zero]

theorem toSubH_Vc (n : ℕ) : toSubH n (VcH n) = ⊤ := by
  rw [eq_top_iff]
  intro v _
  obtain ⟨m, hm, rfl⟩ := vecH_surj n v
  exact Submodule.subset_span ⟨m, by simpa [VcH] using hm, rfl⟩

theorem toSubH_Hq (n q : ℕ) : toSubH n (HqH n q) = LinearMap.ker (phiH n q) := by
  have hset : vecH n '' (↑(HqH n q) : Set ℕ) = (LinearMap.ker (phiH n q) : Set (VH n)) := by
    ext v
    obtain ⟨m, hm, rfl⟩ := vecH_surj n v
    simp only [Set.mem_image, Finset.mem_coe, SetLike.mem_coe, LinearMap.mem_ker]
    rw [phiH_vec]
    constructor
    · rintro ⟨k, hk, he⟩
      have hk' := Finset.mem_filter.1 hk
      have hk5 : k < 2 ^ n := Finset.mem_range.1 hk'.1
      rw [← vecH_inj n hk5 hm he]; exact hk'.2
    · intro h
      exact ⟨m, Finset.mem_filter.2 ⟨Finset.mem_range.2 hm, h⟩, rfl⟩
  unfold toSubH; rw [hset, Submodule.span_eq]

/-- a nonzero label below 2^n has a set bit among the first n. -/
theorem bit_of_ne {n q : ℕ} (hq : q < 2 ^ n) (hne : q ≠ 0) : ∃ i : Fin n, q.testBit i = true := by
  by_contra hc
  push Not at hc
  apply hne
  apply Nat.eq_of_testBit_eq
  intro i
  by_cases hi : i < n
  · simpa using hc ⟨i, hi⟩
  · have h9 : 2 ^ n ≤ 2 ^ i := Nat.pow_le_pow_right (by norm_num) (by omega)
    rw [Nat.testBit_lt_two_pow (lt_of_lt_of_le hq h9)]; simp

theorem vecH_ne {n q : ℕ} (hq : q < 2 ^ n) (hne : q ≠ 0) : vecH n q ≠ 0 := by
  obtain ⟨i, hi⟩ := bit_of_ne hq hne
  intro e
  have := congrFun e i
  simp [vecH, hi] at this

theorem phiH_ne {n q : ℕ} (hq : q < 2 ^ n) (hne : q ≠ 0) : phiH n q ≠ 0 := by
  obtain ⟨i, hi⟩ := bit_of_ne hq hne
  intro e
  have h1 := LinearMap.congr_fun e (Pi.single i 1)
  rw [phiH_apply] at h1
  have hsum : (∑ x : Fin n, if q.testBit x = true then (Pi.single i 1 : VH n) x else 0) = 1 := by
    rw [Finset.sum_eq_single i]
    · simp [hi]
    · intro b _ hb; simp [hb]
    · simp
  rw [hsum] at h1
  exact absurd h1 (by simp)

/-! ## 2. The caller contract and the word at label rank n -/

/-- the fixed caller data at label rank n: port labels are nonzero vectors of F_2^n; D-port flags. -/
structure CallerH (n : ℕ) (Pt : Type) where
  lab : Pt → ℕ
  isD : Pt → Bool
  lab_lt : ∀ p, lab p < 2 ^ n
  lab_ne : ∀ p, lab p ≠ 0

variable {n : ℕ} {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow]
  [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]

def pubH (cl : CallerH n Pt) : Reg Pt Hl Ow → Bool
  | .x _ | .y _ | .h _ => true
  | .x2 p | .y2 p => cl.isD p
  | .o _ => false

/-- target rows (identical to WordModel.tgt; depends on the D-flag only). -/
noncomputable def tgtH (cl : CallerH n Pt) : Reg Pt Hl Ow → Reg Pt Hl Ow → ℚ
  | .x p => if cl.isD p then e (.x p) else e (.x p) - e (.y p)
  | .y p => if cl.isD p then e (.y p) + e (.x p) else (1/2 : ℚ) • e (.x p) + (1/2 : ℚ) • e (.y p)
  | .x2 p => e (.x2 p) - e (.y2 p)
  | .y2 p => e (.y2 p)
  | .h i => e (.h i)
  | .o _ => 0

/-- WordModel.Word with the label-rank-n constants VcH, HqH (the same clauses). -/
structure WordH (cl : CallerH n Pt) (s : St (Reg Pt Hl Ow)) : Prop where
  reach : Reach (pubH cl) s
  pub_sit : ∀ r, pubH cl r = true → ∃ c, s.loc r = .sit c
  own_off : ∀ r c, pubH cl r = false → s.loc r ≠ .sit c
  x_birth : ∀ p, Reg.x p ∈ s.B (line (cl.lab p))
  x_final : ∀ p, s.loc (.x p) = .sit (VcH n)
  y_birth : ∀ p, Reg.y p ∈ s.B zeroCh
  y_final : ∀ p, s.loc (.y p) = .sit (HqH n (cl.lab p))
  x2_birth : ∀ p, cl.isD p = true → Reg.x2 p ∈ s.B (line (cl.lab p))
  x2_final : ∀ p, cl.isD p = true → s.loc (.x2 p) = .sit (VcH n)
  y2_birth : ∀ p, cl.isD p = true → Reg.y2 p ∈ s.B zeroCh
  y2_final : ∀ p, cl.isD p = true → s.loc (.y2 p) = .sit (HqH n (cl.lab p))
  final_row : ∀ r, pubH cl r = true → s.row r = tgtH cl r

/-! ## 3. The fold as a Net over submodules of F_2^n -/

/-- the fold of a legal trace on label-rank-n charts. -/
noncomputable def foldSH (n : ℕ) {tr : Trace (Reg Pt Hl Ow)} {cl : CallerH n Pt} (h : Legal (pubH (Hl := Hl) (Ow := Ow) cl) tr) :
    BankNC0.Net ℚ (Submodule (ZMod 2) (VH n)) (Fld (pubH (Hl := Hl) (Ow := Ow) cl)) (Fin (mlog tr).length) :=
  (fold h).mapChart (toSubH n)

section Charts
variable {cl : CallerH n Pt} {tr : Trace (Reg Pt Hl Ow)}

theorem fA_eqH (h : Legal (pubH cl) tr) {f : Fld (pubH (Hl := Hl) (Ow := Ow) cl)} {c : Ch}
    (hb : f.1 ∈ (exec tr).B c) : fA tr f = c :=
  bch_eq (reach_pinv (pubH cl) (reach_exec h)) hb

theorem fB_eqH {f : Fld (pubH (Hl := Hl) (Ow := Ow) cl)} {c : Ch} (hl : (exec tr).loc f.1 = .sit c) : fB tr f = c := by
  show locCh ((exec tr).loc f.1) = c; rw [hl]; rfl

variable (h : Legal (pubH cl) tr) (hw : WordH cl (exec tr))

include h hw

theorem A_xH (p : Pt) : (foldSH n h).A ⟨.x p, rfl⟩ = Submodule.span (ZMod 2) {vecH n (cl.lab p)} := by
  show toSubH n (fA tr _) = _
  rw [fA_eqH h (hw.x_birth p), toSubH_line]
theorem B_xH (p : Pt) : (foldSH n h).B ⟨.x p, rfl⟩ = ⊤ := by
  show toSubH n (fB tr _) = _
  rw [fB_eqH (hw.x_final p), toSubH_Vc]
theorem A_yH (p : Pt) : (foldSH n h).A ⟨.y p, rfl⟩ = ⊥ := by
  show toSubH n (fA tr _) = _
  rw [fA_eqH h (hw.y_birth p), toSubH_zero]
theorem B_yH (p : Pt) : (foldSH n h).B ⟨.y p, rfl⟩ = LinearMap.ker (phiH n (cl.lab p)) := by
  show toSubH n (fB tr _) = _
  rw [fB_eqH (hw.y_final p), toSubH_Hq]
theorem A_x2H {p : Pt} (hD : cl.isD p = true) :
    (foldSH n h).A ⟨.x2 p, hD⟩ = Submodule.span (ZMod 2) {vecH n (cl.lab p)} := by
  show toSubH n (fA tr _) = _
  rw [fA_eqH h (hw.x2_birth p hD), toSubH_line]
theorem B_x2H {p : Pt} (hD : cl.isD p = true) : (foldSH n h).B ⟨.x2 p, hD⟩ = ⊤ := by
  show toSubH n (fB tr _) = _
  rw [fB_eqH (hw.x2_final p hD), toSubH_Vc]
theorem A_y2H {p : Pt} (hD : cl.isD p = true) : (foldSH n h).A ⟨.y2 p, hD⟩ = ⊥ := by
  show toSubH n (fA tr _) = _
  rw [fA_eqH h (hw.y2_birth p hD), toSubH_zero]
theorem B_y2H {p : Pt} (hD : cl.isD p = true) :
    (foldSH n h).B ⟨.y2 p, hD⟩ = LinearMap.ker (phiH n (cl.lab p)) := by
  show toSubH n (fB tr _) = _
  rw [fB_eqH (hw.y2_final p hD), toSubH_Hq]

theorem foldSH_O (f g : Fld (pubH (Hl := Hl) (Ow := Ow) cl)) : (foldSH n h).O f g = tgtH cl f.1 g.1 := by
  show fO (pb := pubH cl) tr f g = _
  unfold fO oRow
  obtain ⟨c, hc⟩ := hw.pub_sit f.1 f.2
  rw [hc]
  simp [restr, LinearMap.funLeft_apply, hw.final_row f.1 f.2]

end Charts

/-! ## 4. Principal minors of the output matrix (positive definiteness of tgtH) -/

section Minors

theorem minors_of_pos {ι : Type} [Fintype ι] [DecidableEq ι] (M : Matrix ι ι ℚ)
    (hpos : ∀ x : ι → ℚ, x ≠ 0 → 0 < x ⬝ᵥ (M *ᵥ x)) (C : Finset ι) :
    (M.submatrix (fun c : C => c.1) (fun c : C => c.1)).det ≠ 0 :=
  UniFold7113.minors_of_pos M hpos C

/-- public fields → registers, extended by 0. -/
def extH (cl : CallerH n Pt) (x : Fld (pubH (Hl := Hl) (Ow := Ow) cl) → ℚ) : Reg Pt Hl Ow → ℚ :=
  fun r => if h : pubH cl r = true then x ⟨r, h⟩ else 0

theorem extH_val (cl : CallerH n Pt) (x : Fld (pubH (Hl := Hl) (Ow := Ow) cl) → ℚ) (f : Fld (pubH (Hl := Hl) (Ow := Ow) cl)) :
    extH cl x f.1 = x f := by simp [extH, f.2]

theorem extH_off (cl : CallerH n Pt) (x : Fld (pubH (Hl := Hl) (Ow := Ow) cl) → ℚ) {r : Reg Pt Hl Ow}
    (h : pubH cl r = false) : extH cl x r = 0 := by simp [extH, h]

theorem sum_regH (F : Reg Pt Hl Ow → ℚ) :
    ∑ r, F r = ∑ p, (F (.x p) + F (.y p)) + ∑ p, (F (.x2 p) + F (.y2 p)) + ∑ i, F (.h i) + ∑ i, F (.o i) :=
  UniFold7113.sum_reg F

theorem sum_fldH (cl : CallerH n Pt) (g : Reg Pt Hl Ow → ℚ) (hg : ∀ r, pubH cl r = false → g r = 0) :
    ∑ f : Fld (pubH (Hl := Hl) (Ow := Ow) cl), g f.1 = ∑ r, g r := by
  rw [← Finset.sum_subtype (univ.filter (fun r => pubH cl r = true)) (fun r => by simp) g]
  exact Finset.sum_subset (subset_univ _) (fun r _ hr => hg r (by simpa using hr))

theorem qform_eqH (cl : CallerH n Pt)
    (M : Matrix (Fld (pubH (Hl := Hl) (Ow := Ow) cl)) (Fld (pubH (Hl := Hl) (Ow := Ow) cl)) ℚ)
    (hM : ∀ f g, M f g = tgtH cl f.1 g.1) (x : Fld (pubH (Hl := Hl) (Ow := Ow) cl) → ℚ) :
    x ⬝ᵥ (M *ᵥ x) = ∑ r, extH cl x r * (tgtH cl r ⬝ᵥ extH cl x) := by
  have hrow : ∀ f, (M *ᵥ x) f = tgtH cl f.1 ⬝ᵥ extH cl x := by
    intro f
    simp only [mulVec, dotProduct, hM]
    rw [← sum_fldH cl (fun r => tgtH cl f.1 r * extH cl x r) (fun r hr => by rw [extH_off cl x hr, mul_zero])]
    exact Finset.sum_congr rfl (fun g _ => by rw [extH_val])
  show ∑ f, x f * (M *ᵥ x) f = _
  simp only [hrow]
  rw [← sum_fldH cl (fun r => extH cl x r * (tgtH cl r ⬝ᵥ extH cl x)) (fun r hr => by rw [extH_off cl x hr, zero_mul])]
  exact Finset.sum_congr rfl (fun f _ => by rw [extH_val])

theorem qform_geH (cl : CallerH n Pt) (y : Reg Pt Hl Ow → ℚ) (ho : ∀ i, y (.o i) = 0) :
    ∑ r, y r ^ 2 ≤ ∑ r, 4 * (y r * (tgtH cl r ⬝ᵥ y)) := by
  rw [sum_regH, sum_regH]
  refine add_le_add (add_le_add (add_le_add (Finset.sum_le_sum fun p _ => ?_) (Finset.sum_le_sum fun p _ => ?_))
    (Finset.sum_le_sum fun i _ => ?_)) (Finset.sum_le_sum fun i _ => ?_)
  · cases hD : cl.isD p <;>
      simp [tgtH, e, hD, sub_dotProduct, add_dotProduct, smul_dotProduct, single_dotProduct] <;>
      nlinarith [sq_nonneg (y (.x p) + y (.y p)), sq_nonneg (y (.x p) - y (.y p)), sq_nonneg (y (.x p)),
        sq_nonneg (y (.y p))]
  · simp [tgtH, e, sub_dotProduct, single_dotProduct]
    nlinarith [sq_nonneg (y (.x2 p) + y (.y2 p)), sq_nonneg (y (.x2 p) - y (.y2 p)), sq_nonneg (y (.x2 p)),
      sq_nonneg (y (.y2 p))]
  · simp [tgtH, e, single_dotProduct]; nlinarith [sq_nonneg (y (.h i))]
  · simp [tgtH, ho i]

theorem qform_posH (cl : CallerH n Pt)
    (M : Matrix (Fld (pubH (Hl := Hl) (Ow := Ow) cl)) (Fld (pubH (Hl := Hl) (Ow := Ow) cl)) ℚ)
    (hM : ∀ f g, M f g = tgtH cl f.1 g.1) (x : Fld (pubH (Hl := Hl) (Ow := Ow) cl) → ℚ) (hx : x ≠ 0) :
    0 < x ⬝ᵥ (M *ᵥ x) := by
  rw [qform_eqH cl M hM x]
  obtain ⟨f, hf⟩ : ∃ f, x f ≠ 0 := by
    by_contra hc; push Not at hc; exact hx (funext hc)
  have h1 : 0 < ∑ r, extH cl x r ^ 2 := by
    refine lt_of_lt_of_le ?_ (Finset.single_le_sum (fun r _ => sq_nonneg (extH cl x r)) (mem_univ f.1))
    rw [extH_val]; positivity
  have h2 := qform_geH cl (extH cl x) (fun i => extH_off cl x rfl)
  rw [← Finset.mul_sum] at h2
  linarith

/-- every principal minor of the folded output matrix of a legal word at any label rank is nonzero. -/
theorem minorsH {cl : CallerH n Pt} {tr : Trace (Reg Pt Hl Ow)} (h : Legal (pubH cl) tr) (hw : WordH cl (exec tr))
    (C : Finset (Fld (pubH (Hl := Hl) (Ow := Ow) cl))) :
    ((foldSH n h).O.submatrix (fun c : C => c.1) (fun c : C => c.1)).det ≠ 0 :=
  minors_of_pos _ (qform_posH cl _ (foldSH_O h hw)) C

end Minors

/-! ## 5. The height-stop contract (hsc7113 at label rank n) -/

section HSC
open HCutGen

/-- the high-end row of port p: X2 (D port) or X (B port). -/
def rowPH (cl : CallerH n Pt) (p : Pt) : Fld (pubH (Hl := Hl) (Ow := Ow) cl) :=
  if hD : cl.isD p = true then ⟨.x2 p, hD⟩ else ⟨.x p, rfl⟩

def rowLH (cl : CallerH n Pt) (p : Pt) : Fld (pubH (Hl := Hl) (Ow := Ow) cl) := ⟨.y p, rfl⟩

theorem rowPH_inj (cl : CallerH n Pt) : Function.Injective (rowPH (Hl := Hl) (Ow := Ow) cl) := by
  intro a b hab
  have h1 := congrArg (fun f => UniFold7113.rp f.1) hab
  simp only [rowPH] at h1
  split_ifs at h1 <;> exact Option.some.inj h1

theorem rowLH_inj (cl : CallerH n Pt) : Function.Injective (rowLH (Hl := Hl) (Ow := Ow) cl) := by
  intro a b hab
  have h1 := congrArg (fun f => UniFold7113.rp f.1) hab
  simp only [rowLH, UniFold7113.rp] at h1
  exact Option.some.inj h1

/-- partner swap X↔Y, X2↔Y2. -/
def swH : Reg Pt Hl Ow → Reg Pt Hl Ow
  | .x p => .y p | .y p => .x p | .x2 p => .y2 p | .y2 p => .x2 p | .h i => .h i | .o i => .o i

theorem swH_swH (r : Reg Pt Hl Ow) : swH (swH r) = r := by cases r <;> rfl
theorem pubH_swH (cl : CallerH n Pt) (r : Reg Pt Hl Ow) : pubH cl (swH r) = pubH cl r := by cases r <;> rfl

def piH (cl : CallerH n Pt) (f : Fld (pubH (Hl := Hl) (Ow := Ow) cl)) : Fld (pubH (Hl := Hl) (Ow := Ow) cl) :=
  ⟨swH f.1, by rw [pubH_swH]; exact f.2⟩

theorem piH_inj (cl : CallerH n Pt) : Function.Injective (piH (Hl := Hl) (Ow := Ow) cl) := by
  intro a b hab
  apply Subtype.ext
  have := congrArg (fun f => swH f.1) hab
  simpa [piH, swH_swH] using this

theorem tgtH_supp (cl : CallerH n Pt) (r t : Reg Pt Hl Ow) (hne : tgtH cl r t ≠ 0) : t = r ∨ t = swH r := by
  by_contra hc
  push Not at hc
  obtain ⟨h1, h2⟩ := hc
  apply hne
  cases r <;> simp only [tgtH, swH] at h2 ⊢ <;> (try split_ifs) <;> simp [e, Pi.single_apply, h1, h2]

variable {cl : CallerH n Pt} {tr : Trace (Reg Pt Hl Ow)} (h : Legal (pubH (Hl := Hl) (Ow := Ow) cl) tr)
  (hw : WordH cl (exec tr))

include h hw in
/-- **hscH**: the height-stop contract of the fold of every legal word, at label rank n, on any port set
(rows: X2 (D port) / X (B port): heights 1 → n with partner 0 → n-1; Y: 0 → n-1 with partner 1 → n). -/
noncomputable def hscH : HSContractH (foldSH n h) (fun c => finrank (ZMod 2) c) n (Fintype.card Pt) where
  π := piH cl
  πinj := piH_inj cl
  hsupp f g hne := by
    rw [foldSH_O h hw] at hne
    rcases tgtH_supp cl _ _ hne with h1 | h1
    · exact Or.inl (Subtype.ext h1)
    · exact Or.inr (Subtype.ext h1)
  Ehi := univ.image (rowPH cl)
  Elo := univ.image (rowLH cl)
  hi_card := by rw [card_image_of_injective _ (rowPH_inj cl), card_univ]
  lo_card := by rw [card_image_of_injective _ (rowLH_inj cl), card_univ]
  hi_h e he := by
    obtain ⟨p, -, rfl⟩ := mem_image.1 he
    have hv := vecH_ne (cl.lab_lt p) (cl.lab_ne p)
    have hf := phiH_ne (n := n) (cl.lab_lt p) (cl.lab_ne p)
    have hW : finrank (ZMod 2) (VH n) = n := Module.finrank_fin_fun _
    by_cases hD : cl.isD p = true
    · rw [show rowPH (Hl := Hl) (Ow := Ow) cl p = ⟨.x2 p, hD⟩ from dif_pos hD]
      refine ⟨?_, ?_, ?_, ?_⟩
      · rw [A_x2H h hw hD]; exact finrank_span_singleton hv
      · rw [B_x2H h hw hD, finrank_top]; exact hW
      · show finrank (ZMod 2) ((foldSH n h).A ⟨.y2 p, hD⟩) = 0
        rw [A_y2H h hw hD]; exact finrank_bot _ _
      · show finrank (ZMod 2) ((foldSH n h).B ⟨.y2 p, hD⟩) = n - 1
        rw [B_y2H h hw hD]; exact finrank_ker_pred _ hf hW
    · rw [show rowPH (Hl := Hl) (Ow := Ow) cl p = ⟨.x p, rfl⟩ from dif_neg hD]
      refine ⟨?_, ?_, ?_, ?_⟩
      · rw [A_xH h hw]; exact finrank_span_singleton hv
      · rw [B_xH h hw, finrank_top]; exact hW
      · show finrank (ZMod 2) ((foldSH n h).A ⟨.y p, rfl⟩) = 0
        rw [A_yH h hw]; exact finrank_bot _ _
      · show finrank (ZMod 2) ((foldSH n h).B ⟨.y p, rfl⟩) = n - 1
        rw [B_yH h hw]; exact finrank_ker_pred _ hf hW
  lo_h e he := by
    obtain ⟨p, -, rfl⟩ := mem_image.1 he
    have hv := vecH_ne (cl.lab_lt p) (cl.lab_ne p)
    have hf := phiH_ne (n := n) (cl.lab_lt p) (cl.lab_ne p)
    have hW : finrank (ZMod 2) (VH n) = n := Module.finrank_fin_fun _
    refine ⟨?_, ?_, ?_, ?_⟩
    · show finrank (ZMod 2) ((foldSH n h).A ⟨.y p, rfl⟩) = 0
      rw [A_yH h hw]; exact finrank_bot _ _
    · show finrank (ZMod 2) ((foldSH n h).B ⟨.y p, rfl⟩) = n - 1
      rw [B_yH h hw]; exact finrank_ker_pred _ hf hW
    · show finrank (ZMod 2) ((foldSH n h).A ⟨.x p, rfl⟩) = 1
      rw [A_xH h hw]; exact finrank_span_singleton hv
    · show finrank (ZMod 2) ((foldSH n h).B ⟨.x p, rfl⟩) = n
      rw [B_xH h hw, finrank_top]; exact hW
  nz_hi e he := by
    obtain ⟨p, -, rfl⟩ := mem_image.1 he
    rw [foldSH_O h hw]
    unfold rowPH
    split_ifs with hD
    · simp [piH, swH, tgtH, e]
    · rw [Bool.not_eq_true] at hD
      simp [piH, swH, tgtH, e, hD]
  nz_lo e he := by
    obtain ⟨p, -, rfl⟩ := mem_image.1 he
    rw [foldSH_O h hw]
    simp only [rowLH, piH, swH, tgtH]
    split_ifs <;> simp [e, Pi.single_apply]

end HSC

end WordShapeH

#print axioms WordShapeH.toSubH_Hq
#print axioms WordShapeH.minorsH
#print axioms WordShapeH.hscH
