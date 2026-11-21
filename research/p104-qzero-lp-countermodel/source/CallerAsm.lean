/-
CallerAsm (lane CALLERASM, Nov 20).  Assembly of the event-form RC2 / HP bound (CallerEv) from SPEC-legal caller words.

Schema (`JB w`): the word contains, for every stage s : Fin k, a type-B J record at position `pos s` (HOST(u,v,a,b) with a, b /= 0,
then IDLE u {s}, IDLE v {s}), the stages numbered in call order (`pos` strictly increasing).  Anything else is allowed between records
(multi-stage IDLE pieces, thin IDLE_ODD / QUERY events, ADD / SCALE / ...); extra D-incidences are exactly the extra events.
Event j (index into the word) has support `evS j` = the D-set of an IDLE; kernel vector v_j = P1(j)^-1 e_reg, dual w_j = P1(j)^T e_reg.
No piece -> role attribution is used anywhere: CallerEv is indexed by events.
Proved here (all from `Legal w`):
 * `word_evData`   : the CallerEv.EvData of the word (x_supp from support_VW, x_ker from jB_xker, biorth from W^T V = 1),
                     `word_count` (|roles at s| = |events at s|), `word_hbh` / `word_hah` (support of the frame blocks).
 * `G_blk_unit_ord`: Ghat_st invertible in the EVENT-LABELLED frame (no regrouping into stage blocks is needed:
                     only the order of the two column pairs matters).
 * `word_rc2_pair` : RC2's pair form for legal words (any thin columns, n + 2 = |columns|).
 * `word_hp`       : Q = 0 (|columns| = 2k), lambda /= -1 on every stage block, D >= 2, tight n + 2 = 2k:
                     104/k * invoice(.99) <= HP(k).
Kernel only.
-/
import Nov15.CallerEv
import Nov15.CallerWordK
import Nov15.CallerThin

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerAsm
open Finset Matrix CallerSign CallerWord CallerEv

section events
variable {n k : ℕ}

/-- support of event j: the D-set of an IDLE (empty for every other event). -/
def evS (w : CWord n k) (j : Fin w.evs.length) : Finset (Fin k) :=
  match w.evs.get j with
  | .idle _ T _ => T
  | _ => ∅

theorem mem_evS (w : CWord n k) (t0 : Fin k) (j : Fin w.evs.length) :
    t0 ∈ evS w j ↔ inc t0 (w.evs.get j) = true := by
  unfold evS inc
  generalize w.evs.get j = e
  cases e <;> simp

noncomputable def vE (w : CWord n k) (j : Fin w.evs.length) (r : Fin n) : ℂ :=
  (P1 w Complex.I j.val)⁻¹ r (reg (w.evs.get j))
noncomputable def wE (w : CWord n k) (j : Fin w.evs.length) (r : Fin n) : ℂ :=
  P1 w Complex.I j.val (reg (w.evs.get j)) r

/-- the schema: one type-B J record per stage, in call order. -/
structure JB (w : CWord n k) where
  pos : Fin k → ℕ
  mono : StrictMono pos
  lt : ∀ s, pos s + 2 < w.evs.length
  u : Fin k → Fin n
  v : Fin k → Fin n
  a : Fin k → ℚ
  b : Fin k → ℚ
  a0 : ∀ s, a s ≠ 0
  b0 : ∀ s, b s ≠ 0
  uv : ∀ s, u s ≠ v s
  h0 : ∀ s, w.evs.get ⟨pos s, by have := lt s; omega⟩ = Ev.host (u s) (v s) (a s) (b s)
  h1 : ∀ s, w.evs.get ⟨pos s + 1, by have := lt s; omega⟩ = Ev.idle (u s) {s} 0
  h2 : ∀ s, w.evs.get ⟨pos s + 2, lt s⟩ = Ev.idle (v s) {s} 0

variable {w : CWord n k}

theorem JB.nz (J : JB w) (s : Fin k) (c : Fin 2) :
    (tm w (⟨J.pos s, by have := J.lt s; omega⟩, c)).2.2 ≠ 0 := by
  unfold tm
  rw [J.h0 s]
  fin_cases c
  · simpa [terms] using J.a0 s
  · simpa [terms] using J.b0 s

/-- the two frame columns of stage s: the two slots of its HOST. -/
def JB.col (J : JB w) (s : Fin k) (c : Fin 2) : Iota w :=
  ⟨(⟨J.pos s, by have := J.lt s; omega⟩, c), J.nz s c⟩

theorem JB.beta_col (J : JB w) (s : Fin k) (c : Fin 2) : βw w (J.col s c) = J.pos s := rfl

end events

section legal
variable {n k : ℕ} {w : CWord n k}

theorem word_hbh (hL : Legal w) (J : JB w) (r : Fin n) (s : Fin k) (hr : s ∉ w.mask r) (c : Fin 2) :
    Bw w Complex.I r (J.col s c) = 0 :=
  (legal_jB_support w hL s (J.pos s) (J.lt s) (J.u s) (J.v s) (J.a s) (J.b s) (J.uv s) (J.h0 s) (J.h1 s) (J.h2 s)
    r hr (J.col s c) rfl).2

theorem word_hah (hL : Legal w) (J : JB w) (r : Fin n) (s : Fin k) (hr : s ∉ w.mask r) (c : Fin 2) :
    Aw w Complex.I r (J.col s c) = 0 :=
  (legal_jB_support w hL s (J.pos s) (J.lt s) (J.u s) (J.v s) (J.a s) (J.b s) (J.uv s) (J.h0 s) (J.h1 s) (J.h2 s)
    r hr (J.col s c) rfl).1

theorem evS_c1 (J : JB w) (s : Fin k) :
    evS w ⟨J.pos s + 1, by have := J.lt s; omega⟩ = {s} := by
  unfold evS; rw [J.h1 s]

theorem evS_c2 (J : JB w) (s : Fin k) : evS w ⟨J.pos s + 2, J.lt s⟩ = {s} := by
  unfold evS; rw [J.h2 s]

/-- the interface a record schema must supply (type B: `JB.sch`; type A: CallerAsmA). `col s` = the two stage-s frame columns. -/
structure Sch (w : CWord n k) where
  col : Fin k → Fin 2 → Iota w
  ord : ∀ s t, s < t → ∀ a b, βw w (col s a) < βw w (col t b)
  mains : 2 * k ≤ (univ.filter fun j => (evS w j).card = 1).card
  hbh : Legal w → ∀ r s, s ∉ w.mask r → ∀ a, Bw w Complex.I r (col s a) = 0
  hah : Legal w → ∀ r s, s ∉ w.mask r → ∀ a, Aw w Complex.I r (col s a) = 0
  ker : Legal w → ∀ s (j : Fin w.evs.length), s ∈ evS w j → 2 ≤ (evS w j).card → ∀ a,
    ∑ r, vE w j r * Bw w Complex.I r (col s a) = 0

/-- the event data of a legal schema word: no attribution. -/
noncomputable def wordEv (hL : Legal w) (S : Sch w) :
    EvData w.mask (fun r s a => Bw w Complex.I r (S.col s a)) (evS w) where
  x := vE w
  y := wE w
  x_supp := by
    intro j r hx t0 ht0
    by_contra hno
    obtain ⟨hL', hb⟩ := legal_dn w hL t0
    exact hx (support_VW w t0 hb hL' r hno ⟨j, (mem_evS w t0 j).mp ht0⟩).1
  x_ker := fun j hj s' hs' a => S.ker hL s' j hs' hj a
  biorth := by
    intro j j' ⟨t0, ht⟩
    obtain ⟨hL', hb⟩ := legal_dn w hL t0
    have h1 := (mem_evS w t0 j).mp (Finset.mem_inter.mp ht).1
    have h2 := (mem_evS w t0 j').mp (Finset.mem_inter.mp ht).2
    have := congrFun (congrFun (biorth w t0 hb hL').1 ⟨j, h1⟩) ⟨j', h2⟩
    rw [Matrix.mul_apply] at this
    simp only [Matrix.transpose_apply, incW, incV, Matrix.of_apply] at this
    simp only [wE, vE]
    rw [this, Matrix.one_apply]
    congr 1
    apply propext
    exact ⟨fun h => congrArg Subtype.val h, fun h => by subst h; rfl⟩

theorem word_count (hL : Legal w) (s : Fin k) :
    (univ.filter fun r => s ∈ w.mask r).card = (univ.filter fun j => s ∈ evS w j).card := by
  obtain ⟨hL', hb⟩ := legal_dn w hL s
  have h := stage_incidence w s hb hL'
  rw [Fintype.card_subtype] at h
  rw [h]
  congr 1
  ext j; simp [mem_evS]

theorem word_mains (J : JB w) : 2 * k ≤ (univ.filter fun j => (evS w j).card = 1).card := by
  let f : Fin k × Fin 2 → Fin w.evs.length := fun p => ⟨J.pos p.1 + 1 + p.2.val, by have := J.lt p.1; have := p.2.isLt; omega⟩
  have hS : ∀ p, evS w (f p) = {p.1} := by
    intro p
    obtain ⟨s, i⟩ := p
    fin_cases i
    · exact evS_c1 J s
    · exact evS_c2 J s
  have hinj : Function.Injective f := by
    intro p q h
    have h1 : ({p.1} : Finset (Fin k)) = {q.1} := by rw [← hS p, ← hS q, h]
    have hs : p.1 = q.1 := Finset.singleton_injective h1
    have h2 := congrArg Fin.val h
    simp only [f] at h2
    have hi : p.2.val = q.2.val := by rw [hs] at h2; omega
    exact Prod.ext hs (Fin.ext hi)
  have := Finset.card_le_card_of_injOn f (s := (univ : Finset (Fin k × Fin 2)))
    (t := univ.filter fun j => (evS w j).card = 1)
    (fun p _ => by simp [hS])
    (hinj.injOn)
  simpa [mul_comm] using this

/-- type B: the kernel law (RC2's `x_ker`) for the schema columns, from `jB_xker`. -/
theorem JB.ker (hL : Legal w) (J : JB w) (s' : Fin k) (j : Fin w.evs.length) (hs' : s' ∈ evS w j)
    (hj : 2 ≤ (evS w j).card) (a : Fin 2) :
    ∑ r, vE w j r * Bw w Complex.I r (J.col s' a) = 0 := by
  obtain ⟨hL', hb⟩ := legal_dn w hL s'
  have he1 : j.val ≠ J.pos s' + 1 := by
    intro h
    have : j = ⟨J.pos s' + 1, by have := J.lt s'; omega⟩ := Fin.ext h
    rw [this, evS_c1] at hj; simp at hj
  have he2 : j.val ≠ J.pos s' + 2 := by
    intro h
    have : j = ⟨J.pos s' + 2, J.lt s'⟩ := Fin.ext h
    rw [this, evS_c2] at hj; simp at hj
  exact jB_xker w s' hb hL' (J.pos s') (J.lt s') (J.u s') (J.v s') (J.a s') (J.b s') (J.uv s')
    (J.h0 s') (J.h1 s') (J.h2 s') ⟨j, (mem_evS w s' j).mp hs'⟩ he1 he2 (J.col s' a) rfl

/-- the type-B schema as a `Sch`. -/
def JB.sch (J : JB w) : Sch w where
  col := J.col
  ord := by
    intro s t h a b
    simpa [JB.beta_col] using J.mono h
  mains := word_mains J
  hbh := fun hL r s hs a => word_hbh hL J r s hs a
  hah := fun hL r s hs a => word_hah hL J r s hs a
  ker := fun hL s j hs hj a => JB.ker hL J s j hs hj a

end legal

/- Ghat_st invertible in an event-LABELLED frame (no regrouping): only the order of the two column pairs matters. -/
section gunit
open CallerThin
variable {K : Type*} [Field K] {ι : Type*} [Fintype ι] [DecidableEq ι] {n : ℕ}

theorem G_blk_unit_ord (A B : Matrix (Fin n) ι K) (β : ι → ℕ) (k : ℕ) (h2 : (2 : K) ≠ 0)
    (hβ : ∀ i, β i < k) (hP : sgProd A B β k = -1) (hn : n + 2 = Fintype.card ι)
    (es et : Fin 2 → ι)
    (hord : (∀ a b, β (es a) < β (et b)) ∨ (∀ a b, β (et b) < β (es a)))
    (hs : IsUnit ((sgK β (sgG A B)).submatrix es es).det)
    (ht : IsUnit ((sgK β (sgG A B)).submatrix et et).det) :
    IsUnit ((sgG A B).submatrix es et).det := by
  have hF := (sgForward A B β k h2 hβ hP).1
  have hr : (sgK β (sgG A B)).rank ≤ 2 := by omega
  have hu := thin_K_blk_unit _ hr es et hs ht
  rcases hord with hlt | hlt
  · have e : (sgG A B).submatrix es et = (sgK β (sgG A B)).submatrix es et := by
      ext a b
      have h1 : β (es a) < β (et b) := hlt a b
      have hne : es a ≠ et b := fun e => by rw [e] at h1; exact lt_irrefl _ h1
      simp [sgK, sgDiag, sgUp, sgLow, one_apply, hne, h1, h1.ne, not_lt.mpr h1.le]
    rw [e]; exact hu
  · have e : (sgG A B).submatrix es et = - (sgK β (sgG A B)).submatrix es et := by
      ext a b
      have h1 : β (et b) < β (es a) := hlt a b
      have hne : es a ≠ et b := fun e => by rw [e] at h1; exact lt_irrefl _ h1
      simp [sgK, sgDiag, sgUp, sgLow, one_apply, hne, h1, h1.ne', not_lt.mpr h1.le]
    rw [e, Matrix.det_neg]
    exact (IsUnit.pow _ (IsUnit.neg isUnit_one)).mul hu

end gunit

section headline
open CallerHP
variable {n k : ℕ} {w : CWord n k}

/-- Ghat_st of the stage columns is invertible (tight frame, lambda /= -1 on every stage block). -/
theorem word_hG (hL : Legal w) (S : Sch w) (hodd : ∀ r, w.ex r % 2 = 1)
    (hn : n + 2 = Fintype.card (Iota w))
    (hlam : ∀ s, IsUnit ((sgK (βw w) (sgG (Aw w Complex.I) (Bw w Complex.I))).submatrix (S.col s) (S.col s)).det)
    (s t : Fin k) (hst : s ≠ t) :
    IsUnit (gBlk (fun r s a => Bw w Complex.I r (S.col s a)) (fun r s a => Aw w Complex.I r (S.col s a)) s t).det := by
  have e : gBlk (fun r s a => Bw w Complex.I r (S.col s a)) (fun r s a => Aw w Complex.I r (S.col s a)) s t
      = (sgG (Aw w Complex.I) (Bw w Complex.I)).submatrix (S.col s) (S.col t) := by
    ext a b
    simp [gBlk, sgG, Matrix.mul_apply, Matrix.transpose_apply]
  rw [e]
  refine G_blk_unit_ord _ _ (βw w) w.evs.length two_ne_zero (beta_lt w) (legal_frame w hL hodd).1 hn
    (S.col s) (S.col t) ?_ (hlam s) (hlam t)
  rcases lt_or_gt_of_ne hst with h | h
  · left; exact S.ord s t h
  · right; intro a b; exact S.ord t s h b a

/-- RC2 pair form of a legal word, event-indexed (any thin columns; `n + 2 = |columns|`). -/
theorem word_rc2_pair (hL : Legal w) (S : Sch w) (hodd : ∀ r, w.ex r % 2 = 1)
    (hn : n + 2 = Fintype.card (Iota w))
    (hlam : ∀ s, IsUnit ((sgK (βw w) (sgG (Aw w Complex.I) (Bw w Complex.I))).submatrix (S.col s) (S.col s)).det)
    (s t : Fin k) (hst : s ≠ t) (l : ℕ) :
    2 + (gSet (evS w) s t l).card ≤ (wSet w.mask s t l).card :=
  ev_pair w.mask (fun r s a => Bw w Complex.I r (S.col s a)) (fun r s a => Aw w Complex.I r (S.col s a)) (evS w)
    (fun r s hs a => S.hbh hL r s hs a) (fun r s hs a => S.hah hL r s hs a) (wordEv hL S) s t hst l
    (word_hG hL S hodd hn hlam s t hst)

/-- the event-form caller value `c^(.99) = 104/k * invoice`. -/
noncomputable def cHat (w : CWord n k) : ℝ := 104 / (k : ℝ) * invoice σ0 w.mask (evS w)

/-- HEADLINE.  A SPEC-legal caller word of a record schema (`Sch`: type B here, type A in CallerAsmA) with odd targets,
`Q = 0` (the frame has exactly the `2k` stage columns), `lambda /= -1` on every stage block, every role of degree `>= 2`,
tight (`n + 2 = 2k`):  `c^(.99) <= HP(k)`.  No piece->role attribution. -/
theorem word_hp (hL : Legal w) (S : Sch w) (hodd : ∀ r, w.ex r % 2 = 1) (hk : 3 ≤ k)
    (hQ0 : Fintype.card (Iota w) = 2 * k) (hn : n + 2 = Fintype.card (Iota w))
    (hlam : ∀ s, IsUnit ((sgK (βw w) (sgG (Aw w Complex.I) (Bw w Complex.I))).submatrix (S.col s) (S.col s)).det)
    (hdeg : ∀ r, 2 ≤ (w.mask r).card) :
    cHat w ≤ HPr k := by
  have s0 : Fin k := ⟨0, by omega⟩
  have e₀ : Fin w.evs.length := ⟨0, by
    have := (S.mains); have h2 : 0 < (univ.filter fun j => (evS w j).card = 1).card := by omega
    obtain ⟨j, _⟩ := Finset.card_pos.mp h2
    exact lt_of_le_of_lt (Nat.zero_le _) j.isLt⟩
  exact ev_frame_bound hk w.mask (fun r s a => Bw w Complex.I r (S.col s a))
    (fun r s a => Aw w Complex.I r (S.col s a)) (evS w)
    (fun r s hs a => S.hbh hL r s hs a) (fun r s hs a => S.hah hL r s hs a) (wordEv hL S)
    (word_hG hL S hodd hn hlam) e₀ (word_count hL) (by simp; omega) hdeg S.mains

/-- HEADLINE, type B. -/
theorem word_hp_B (hL : Legal w) (J : JB w) (hodd : ∀ r, w.ex r % 2 = 1) (hk : 3 ≤ k)
    (hQ0 : Fintype.card (Iota w) = 2 * k) (hn : n + 2 = Fintype.card (Iota w))
    (hlam : ∀ s, IsUnit ((sgK (βw w) (sgG (Aw w Complex.I) (Bw w Complex.I))).submatrix (J.col s) (J.col s)).det)
    (hdeg : ∀ r, 2 ≤ (w.mask r).card) :
    cHat w ≤ HPr k :=
  word_hp hL J.sch hodd hk hQ0 hn hlam hdeg

end headline

end CallerAsm

#print axioms CallerAsm.wordEv
#print axioms CallerAsm.word_hG
#print axioms CallerAsm.word_rc2_pair
#print axioms CallerAsm.word_hp
#print axioms CallerAsm.word_hp_B
