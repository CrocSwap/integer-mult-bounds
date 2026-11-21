/-
WARNING (WM-AUDIT item 7): `FWword` charges stops twice (full paths AND −nStops·cstop), so it is NOT the word's
real invoice; P0_word/U0_word/P0_spec/U0_spec say nothing about the real κ. Use WordModelInvoice.P0_real /
U0_real (FWreal = real invoice, proved ≤ endpoint-collapsed invoice by the stop-excess lemma).
WordModelPrice (lane WORDMODEL, coordinator, Nov 18).  The PRICE SIDE of SafeRungs read off the word model:
* paths: register r's chart path = birth chart, then the targets of its public MOVEs in time order (plog);
  run invariant: the path ends at the current chart (`PInv`).
* helpers H = helper registers; credit hc = climb dim(final) − dim(birth) (Theorem-K T); pcost over the path.
* mains M = X_p, Y_p (104 ports) + X2_p, Y2_p (96 D ports) = 400 (`DCount`), endpoint price ≥ 8.
* owned MOVEs: oSrc/oTgt of olog (WordModelU0).
Price: any pseudometric dc on charts with dc a b ≥ |dim b − dim a| (SPEC rank(M_b − M_a) ≥ |Δdim|,
AUDIT-MIN (A); lattice distance qualifies); for U0 also integer-valued and separating (hO1).
Then P0 and U0 hold for every model word with NO hR1-hR3, hO1, hH, hM, hM400: only the price clauses and hF
(κ is a crossing of the word's own invoice).
Kernel only: no sorry, no native_decide, no axioms.
-/
import Nov15.WordModelU0

set_option linter.unusedSectionVars false

namespace WordModel

open Finset SafeRungsClique SafeRungsPrice

/-! ## Paths -/

section Gen
variable {R : Type} [Fintype R] [DecidableEq R] (pb : R → Bool)

/-- targets of r's public MOVEs, oldest first. -/
def mvs (s : St R) (r : R) : List Ch :=
  ((s.plog.filter (fun m => decide (m.1 = r))).map (fun m => m.2.2)).reverse

structure PInv (s : St R) : Prop where
  unb : ∀ r, s.loc r = .unborn → (∀ c, r ∉ s.B c) ∧ mvs s r = []
  pB : ∀ r c, r ∈ s.B c → pb r = true
  bu : ∀ r c c', r ∈ s.B c → r ∈ s.B c' → c = c'
  last : ∀ r c, r ∈ s.B c → s.loc r = .sit ((c :: mvs s r).getLast (List.cons_ne_nil _ _))
  born : ∀ r c, pb r = true → s.loc r = .sit c → ∃ c0, r ∈ s.B c0

theorem pinv_init : PInv pb (init : St R) where
  unb := by intro r _; simp [init, mvs]
  pB := by intro r c h; simp [init] at h
  bu := by intro r c c' h; simp [init] at h
  last := by intro r c h; simp [init] at h
  born := by intro r c _ h; simp [init] at h

theorem step_pinv {s s' : St R} (hs : PInv pb s) (h : Step pb s s') : PInv pb s' := by
  cases h with
  | birthPub r c hu hp =>
    obtain ⟨hnB, hmv⟩ := hs.unb r hu
    have hB : ∀ r' c', r' ∈ Function.update s.B c (insert r (s.B c)) c' ↔
        (r' = r ∧ c' = c) ∨ r' ∈ s.B c' := by
      intro r' c'
      by_cases hc : c' = c
      · subst hc; simp
      · simp [Function.update_of_ne hc, hc]
    refine ⟨?_, ?_, ?_, ?_, ?_⟩
    · intro r' hl
      have hr : r' ≠ r := by rintro rfl; simp at hl
      simp only [Function.update_of_ne hr] at hl
      refine ⟨fun c' hm => ?_, hs.unb r' hl |>.2⟩
      rcases (hB r' c').1 hm with ⟨h1, -⟩ | h1
      · exact hr h1
      · exact (hs.unb r' hl).1 c' h1
    · intro r' c' hm
      rcases (hB r' c').1 hm with ⟨rfl, -⟩ | h1
      · exact hp
      · exact hs.pB r' c' h1
    · intro r' c1 c2 h1 h2
      rcases (hB r' c1).1 h1 with ⟨e1, f1⟩ | o1 <;> rcases (hB r' c2).1 h2 with ⟨e2, f2⟩ | o2
      · rw [f1, f2]
      · exact (hnB c2 (e1 ▸ o2)).elim
      · exact (hnB c1 (e2 ▸ o1)).elim
      · exact hs.bu r' c1 c2 o1 o2
    · intro r' c' hm
      rcases (hB r' c').1 hm with ⟨rfl, rfl⟩ | h1
      · simp only [mvs] at hmv ⊢; simp [hmv]
      · have hr : r' ≠ r := by rintro rfl; exact hnB c' h1
        simpa [Function.update_of_ne hr, mvs] using hs.last r' c' h1
    · intro r' c' hp' hl
      by_cases hr : r' = r
      · subst hr; exact ⟨c, (hB r' c).2 (Or.inl ⟨rfl, rfl⟩)⟩
      · simp only [Function.update_of_ne hr] at hl
        obtain ⟨c0, h0⟩ := hs.born r' c' hp' hl
        exact ⟨c0, (hB r' c0).2 (Or.inr h0)⟩
  | birthOwn r c hu hp =>
    obtain ⟨hnB, hmv⟩ := hs.unb r hu
    refine ⟨?_, hs.pB, hs.bu, ?_, ?_⟩
    · intro r' hl
      have hr : r' ≠ r := by rintro rfl; simp at hl
      simp only [Function.update_of_ne hr] at hl
      exact hs.unb r' hl
    · intro r' c' hm
      have hr : r' ≠ r := by rintro rfl; exact hnB c' hm
      simpa [Function.update_of_ne hr, mvs] using hs.last r' c' hm
    · intro r' c' hp' hl
      have hr : r' ≠ r := by rintro rfl; rw [hp] at hp'; cases hp'
      simp only [Function.update_of_ne hr] at hl
      exact hs.born r' c' hp' hl
  | gate r c coef hl => exact ⟨hs.unb, hs.pB, hs.bu, hs.last, hs.born⟩
  | movePub r c d hl hp hlt =>
    have hmv : ∀ r', mvs ({ s with loc := Function.update s.loc r (.sit d), A := Function.update s.A d (insert r (s.A d)), eRow := fun r' c' => if r' = r ∧ c' = d then s.row r else s.eRow r' c', slog := if r ∈ s.A c then (r, c) :: s.slog else s.slog, plog := (r, c, d) :: s.plog } : St R) r' =
        if r = r' then mvs s r' ++ [d] else mvs s r' := by
      intro r'
      by_cases h : r = r'
      · subst h; simp [mvs]
      · simp [mvs, h]
    refine ⟨?_, hs.pB, hs.bu, ?_, ?_⟩
    · intro r' hl
      have hr : r' ≠ r := by rintro rfl; simp at hl
      simp only [Function.update_of_ne hr] at hl
      refine ⟨(hs.unb r' hl).1, ?_⟩
      rw [hmv, if_neg (Ne.symm hr)]; exact (hs.unb r' hl).2
    · intro r' c' hm
      rw [hmv]
      by_cases hr : r' = r
      · subst hr; simp
      · rw [if_neg (Ne.symm hr)]
        simpa [Function.update_of_ne hr] using hs.last r' c' hm
    · intro r' c' hp' hl'
      by_cases hr : r' = r
      · subst hr; exact hs.born r' c hp' hl
      · simp only [Function.update_of_ne hr] at hl'
        exact hs.born r' c' hp' hl'
  | moveOwn r c d hl hp =>
    refine ⟨?_, hs.pB, hs.bu, ?_, ?_⟩
    · intro r' hl'
      have hr : r' ≠ r := by rintro rfl; simp at hl'
      simp only [Function.update_of_ne hr] at hl'
      exact ⟨(hs.unb r' hl').1, by simpa [mvs] using (hs.unb r' hl').2⟩
    · intro r' c' hm
      have hr : r' ≠ r := by rintro rfl; rw [hs.pB r' c' hm] at hp; cases hp
      simpa [Function.update_of_ne hr, mvs] using hs.last r' c' hm
    · intro r' c' hp' hl'
      have hr : r' ≠ r := by rintro rfl; rw [hp] at hp'; cases hp'
      simp only [Function.update_of_ne hr] at hl'
      exact hs.born r' c' hp' hl'
  | clearOwn r c hl hp =>
    refine ⟨?_, hs.pB, hs.bu, ?_, ?_⟩
    · intro r' hl'
      have hr : r' ≠ r := by rintro rfl; simp at hl'
      simp only [Function.update_of_ne hr] at hl'
      exact hs.unb r' hl'
    · intro r' c' hm
      have hr : r' ≠ r := by rintro rfl; rw [hs.pB r' c' hm] at hp; cases hp
      simpa [Function.update_of_ne hr, mvs] using hs.last r' c' hm
    · intro r' c' hp' hl'
      have hr : r' ≠ r := by rintro rfl; rw [hp] at hp'; cases hp'
      simp only [Function.update_of_ne hr] at hl'
      exact hs.born r' c' hp' hl'

theorem reach_pinv {s : St R} (h : Reach pb s) : PInv pb s := by
  induction h with
  | refl => exact pinv_init pb
  | tail _ hst ih => exact step_pinv pb ih hst

theorem getD_length_eq_getLast (c : Ch) (l : List Ch) :
    (c :: l).getD l.length ∅ = (c :: l).getLast (List.cons_ne_nil _ _) := by
  induction l generalizing c with
  | nil => simp
  | cons a l ih => simp only [List.length_cons, List.getD_cons_succ, List.getLast_cons_cons]; exact ih a

open Classical in
/-- birth chart (∅ if never born). -/
noncomputable def bch (s : St R) (r : R) : Ch := if h : ∃ c, r ∈ s.B c then Classical.choose h else ∅

/-- chart path of r: path 0 = birth chart, path (plen r) = current chart. -/
noncomputable def path (s : St R) (r : R) (i : ℕ) : Ch := (bch s r :: mvs s r).getD i ∅
def plen (s : St R) (r : R) : ℕ := (mvs s r).length

theorem path_ends {s : St R} (hs : PInv pb s) {r : R} {c : Ch} (hB : r ∈ s.B c) :
    path s r 0 = c ∧ s.loc r = .sit (path s r (plen s r)) := by
  have hb : bch s r = c := by
    have h : ∃ c, r ∈ s.B c := ⟨c, hB⟩
    simp only [bch, dif_pos h]
    exact hs.bu r _ _ (Classical.choose_spec h) hB
  refine ⟨by simp [path, hb], ?_⟩
  rw [hs.last r c hB, path, plen, hb, getD_length_eq_getLast]

end Gen

/-! ## Charts: dimensions of the contract endpoints -/

theorem dim_Vc : dim Vc = 9 := by
  have : Vc.card = 2 ^ 9 := by simp [Vc]
  rw [dim, this, Nat.log_pow (by norm_num)]

theorem dim_line {q : ℕ} (hq : q ≠ 0) : dim (line q) = 1 := by
  have : (line q).card = 2 ^ 1 := by simp [line, Finset.card_pair (Ne.symm hq)]
  rw [dim, this, Nat.log_pow (by norm_num)]

theorem dim_zero : dim zeroCh = 0 := by simp [dim, zeroCh]

variable {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow]
  [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]

theorem dim_Hq_lab (cl : Caller Pt) (p : Pt) : dim (Hq (cl.lab p)) = 8 := by
  have : (Hq (cl.lab p)).card = 2 ^ 8 := by rw [Hq_card_lab cl p]; norm_num
  rw [dim, this, Nat.log_pow (by norm_num)]

/-! ## Helpers, mains -/

/-- 96 D ports [src l.70 `len(D)==96`]. -/
def DCount (cl : Caller Pt) : Prop := (univ.filter (fun p => cl.isD p = true)).card = 96

def Dset (cl : Caller Pt) : Finset Pt := univ.filter (fun p => cl.isD p = true)

/-- the 400 mains [src l.88]. -/
def mains (cl : Caller Pt) : Finset (Reg Pt Hl Ow) :=
  ((univ.image Reg.x ∪ univ.image Reg.y) ∪ (Dset cl).image Reg.x2) ∪ (Dset cl).image Reg.y2

/-- helpers. -/
def helpers : Finset (Reg Pt Hl Ow) := univ.image Reg.h

theorem mains_card (cl : Caller Pt) (hD : DCount cl) : (mains (Hl := Hl) (Ow := Ow) cl).card = 400 := by
  have i1 : Function.Injective (Reg.x : Pt → Reg Pt Hl Ow) := fun a b h => by cases h; rfl
  have i2 : Function.Injective (Reg.y : Pt → Reg Pt Hl Ow) := fun a b h => by cases h; rfl
  have i3 : Function.Injective (Reg.x2 : Pt → Reg Pt Hl Ow) := fun a b h => by cases h; rfl
  have i4 : Function.Injective (Reg.y2 : Pt → Reg Pt Hl Ow) := fun a b h => by cases h; rfl
  have d12 : Disjoint (univ.image (Reg.x : Pt → Reg Pt Hl Ow)) (univ.image Reg.y) := by
    rw [Finset.disjoint_left]; intro a h1 h2; simp at h1 h2; obtain ⟨_, rfl⟩ := h1; obtain ⟨_, h⟩ := h2; cases h
  have d3 : Disjoint (univ.image (Reg.x : Pt → Reg Pt Hl Ow) ∪ univ.image Reg.y) ((Dset cl).image Reg.x2) := by
    rw [Finset.disjoint_left]; intro a h1 h2; simp at h1 h2; obtain ⟨_, _, rfl⟩ := h2
    simp at h1
  have d4 : Disjoint ((univ.image (Reg.x : Pt → Reg Pt Hl Ow) ∪ univ.image Reg.y) ∪ (Dset cl).image Reg.x2)
      ((Dset cl).image Reg.y2) := by
    rw [Finset.disjoint_left]; intro a h1 h2; simp at h1 h2; obtain ⟨_, _, rfl⟩ := h2
    simp at h1
  rw [mains, card_union_of_disjoint d4, card_union_of_disjoint d3, card_union_of_disjoint d12,
    card_image_of_injective _ i1, card_image_of_injective _ i2, card_image_of_injective _ i3,
    card_image_of_injective _ i4, card_univ, cl.card104]
  have : (Dset cl).card = 96 := hD
  rw [this]

/-- Theorem-K helper credit: the climb of the helper's path endpoints. -/
noncomputable def hcred (s : St (Reg Pt Hl Ow)) (r : Reg Pt Hl Ow) : ℝ :=
  (dim (path s r (plen s r)) : ℝ) - dim (path s r 0)

/-- SPEC price ≥ |Δdim| (AUDIT-MIN (A)). -/
def DimLower (dc : Ch → Ch → ℝ) : Prop := ∀ a b, |(dim b : ℝ) - dim a| ≤ dc a b

theorem hH_word (s : St (Reg Pt Hl Ow)) {dc : Ch → Ch → ℝ} (hdl : DimLower dc) :
    ∀ i ∈ (helpers : Finset (Reg Pt Hl Ow)), hcred s i ≤ dc (path s i 0) (path s i (plen s i)) :=
  fun i _ => (le_abs_self _).trans (hdl _ _)

theorem hM_word {cl : Caller Pt} {s : St (Reg Pt Hl Ow)} (hw : Word cl s) {dc : Ch → Ch → ℝ}
    (hdl : DimLower dc) :
    ∀ j ∈ mains cl, 1 ≤ plen s j ∧ 8 ≤ dc (path s j 0) (path s j (plen s j)) := by
  have hs := reach_pinv (pub cl) hw.reach
  -- generic: born at a, ends at b, dims differ by 8
  have key : ∀ j a b, j ∈ s.B a → s.loc j = .sit b → (dim a : ℝ) + 8 = dim b ∨ (dim b : ℝ) + 8 = dim a →
      1 ≤ plen s j ∧ 8 ≤ dc (path s j 0) (path s j (plen s j)) := by
    intro j a b hB hl hd
    obtain ⟨h0, h1⟩ := path_ends (pub cl) hs hB
    rw [hl] at h1; cases h1
    refine ⟨?_, ?_⟩
    · by_contra hc
      have h00 : plen s j = 0 := by omega
      rw [h00, h0] at hd
      rcases hd with hd | hd <;> linarith
    · refine le_trans ?_ (hdl _ _)
      rw [h0]; rcases hd with hd | hd
      · rw [← hd]; simp
      · rw [← hd, abs_sub_comm]; simp
  intro j hj
  have hne := fun p => lab_ne_zero cl p
  rcases Finset.mem_union.1 hj with hj | hj
  swap
  · obtain ⟨p, hp, rfl⟩ := Finset.mem_image.1 hj
    have hD : cl.isD p = true := (Finset.mem_filter.1 hp).2
    exact key _ _ _ (hw.y2_birth p hD) (hw.y2_final p hD) (Or.inl (by rw [dim_zero, dim_Hq_lab]; norm_num))
  rcases Finset.mem_union.1 hj with hj | hj
  swap
  · obtain ⟨p, hp, rfl⟩ := Finset.mem_image.1 hj
    have hD : cl.isD p = true := (Finset.mem_filter.1 hp).2
    exact key _ _ _ (hw.x2_birth p hD) (hw.x2_final p hD) (Or.inl (by rw [dim_line (hne p), dim_Vc]; norm_num))
  rcases Finset.mem_union.1 hj with hj | hj
  · obtain ⟨p, -, rfl⟩ := Finset.mem_image.1 hj
    exact key _ _ _ (hw.x_birth p) (hw.x_final p) (Or.inl (by rw [dim_line (hne p), dim_Vc]; norm_num))
  · obtain ⟨p, -, rfl⟩ := Finset.mem_image.1 hj
    exact key _ _ _ (hw.y_birth p) (hw.y_final p) (Or.inl (by rw [dim_zero, dim_Hq_lab]; norm_num))

/-! ## The rungs on the word model, price side derived -/

/-- the word's own invoice F at s = 1 − t (SafeRungsPrice.FW with every argument read off the run). -/
noncomputable def FWword (cl : Caller Pt) (s : St (Reg Pt Hl Ow)) (dc : Ch → Ch → ℝ) (σ : ℝ) : ℝ :=
  FW dc σ (helpers : Finset (Reg Pt Hl Ow)) (hcred s) (plen s) (path s) (mains cl) (plen s) (path s)
    (nOwned s) (oSrc s) (oTgt s) (nStops s)

/-- **P0 on the word model**: κ < .0227043 for every crossing κ ∈ (0,1] of the word's invoice.
Hypotheses: a model Word with 96 D ports; price = pseudometric ≥ |Δdim|. -/
theorem P0_word {cl : Caller Pt} {s : St (Reg Pt Hl Ow)} (hw : Word cl s) (hD : DCount cl)
    {dc : Ch → Ch → ℝ} (hm : PriceMetric dc) (hdl : DimLower dc)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ ≤ 1) (hF : 0 ≤ FWword cl s dc (1 - κ)) : κ < 227043 / 10000000 :=
  SafeRungsExact.P0_kappa_exact hm helpers (hcred s) (plen s) (path s) (mains cl) (plen s) (path s)
    (nOwned s) (oSrc s) (oTgt s) (nStops s) (hH_word s hdl) (hM_word hw hdl) (mains_card cl hD)
    (Nat.cast_nonneg _) κ hκ0 hκ1 hF

/-- **U0 on the word model**: κ < .0204111.  Additional hypotheses: owned MOVEs nested (l.51), price
integer-valued and separating (SPEC rank / lattice distance). -/
theorem U0_word {cl : Caller Pt} {s : St (Reg Pt Hl Ow)} (hw : Word cl s) (hD : DCount cl)
    {dc : Ch → Ch → ℝ} (hm : PriceMetric dc) (hdl : DimLower dc)
    (hint : ∀ a b, ∃ n : ℕ, dc a b = n) (hsep : ∀ a b, dc a b = 0 → a = b) (hnest : OwnedNested s)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ ≤ 1) (hF : 0 ≤ FWword cl s dc (1 - κ)) : κ < 204111 / 10000000 :=
  U0_kappa_word_nested hw hm hint hsep hnest helpers (hcred s) (plen s) (path s) (mains cl) (plen s) (path s)
    (hH_word s hdl) (hM_word hw hdl) (mains_card cl hD) κ hκ0 hκ1 hF

end WordModel

#print axioms WordModel.P0_word
#print axioms WordModel.U0_word
