/-
CallerAsmA (lane CALLERASM, Nov 20).  The type-A J record (two HOSTs) for the event-indexed caller bound.
  jA t x y u v α = [HOST(x,y,0,1), HOST(u,v,α,0), IDLE x {t}, IDLE y {t}, IDLE u {t}, IDLE v {t}],  α /= 0.
Stage columns: slot 1 of the first HOST (event pos) and slot 0 of the second (event pos+1): in the EVENT-LABELLED frame they
have different times; `G_blk_unit_ord` only needs the stages' column pairs to be ordered (`pos s + 1 < pos t`).
* `jA_xker` : RC2's `x_ker` for both HOST columns: every D_t0-incidence other than the contacts x (resp. v) is orthogonal.
* `JA`, `JA.sch` : the type-A schema as a `CallerAsm.Sch`; hence `word_hp` / `word_rc2_pair` apply verbatim to type-A words.
Kernel only.
-/
import Nov15.CallerAsm
import Nov15.CallerWordA

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerAsm
open Finset Matrix CallerSign CallerWord

section xkerA
variable {n k : ℕ} (w : CWord n k) (t0 : Fin k)
variable (hb : replay (1 : ℂ) Complex.I 1 w.evs = 1) (hL : LegalAt (1 : DN) iD (Dt t0) w)
include hb hL

theorem jA_xker (j : ℕ) (hj5 : j + 5 < w.evs.length) (x y u v : Fin n) (α : ℚ)
    (hxy : x ≠ y) (hxu : x ≠ u) (hxv : x ≠ v) (hyu : y ≠ u) (hyv : y ≠ v) (huv : u ≠ v)
    (h0 : w.evs.get ⟨j, by omega⟩ = Ev.host x y 0 1)
    (h1 : w.evs.get ⟨j + 1, by omega⟩ = Ev.host u v α 0)
    (h2 : w.evs.get ⟨j + 2, by omega⟩ = Ev.idle x {t0} 0)
    (h3 : w.evs.get ⟨j + 3, by omega⟩ = Ev.idle y {t0} 0)
    (h4 : w.evs.get ⟨j + 4, by omega⟩ = Ev.idle u {t0} 0)
    (h5 : w.evs.get ⟨j + 5, hj5⟩ = Ev.idle v {t0} 0)
    (e : Inc w t0) (he2 : e.1.val ≠ j + 2) (he5 : e.1.val ≠ j + 5)
    (p : Iota w) (hp : (p.1.1.val = j ∧ p.1.2 = 1) ∨ (p.1.1.val = j + 1 ∧ p.1.2 = 0)) :
    ∑ r, incV w t0 r e * Bw w Complex.I r p = 0 := by
  have g2 : w.evs[j + 2]'(by omega) = Ev.idle x {t0} 0 := by simpa using h2
  have g5 : w.evs[j + 5]'hj5 = Ev.idle v {t0} 0 := by simpa using h5
  have i2 : inc t0 (w.evs.get ⟨j + 2, by omega⟩) = true := by rw [h2]; simp [inc]
  have i5 : inc t0 (w.evs.get ⟨j + 5, hj5⟩) = true := by rw [h5]; simp [inc]
  have stepI : ∀ m (hm : m < w.evs.length) (z : Fin n),
      w.evs.get ⟨m, hm⟩ = Ev.idle z {t0} 0 → P1 w Complex.I (m + 1) = P1 w Complex.I m := by
    intro m hm z hz
    unfold P1; rw [pre_succ, evAt_get w _ 1 1 m hm, hz, idle_base, Matrix.one_mul]
  have P3 := stepI (j + 2) (by omega) x h2
  have P4 := stepI (j + 3) (by omega) y h3
  have P5 := stepI (j + 4) (by omega) u h4
  have hP2 : P1 w Complex.I (j + 2) = (1 + E1 u v (algebraMap ℚ ℂ α)) * P1 w Complex.I (j + 1) := by
    unfold P1; rw [pre_succ, evAt_get w _ 1 1 (j + 1) (by omega), h1, host2_base]
  have hbi := (biorth w t0 hb hL).1
  let c2 : Inc w t0 := ⟨_, i2⟩
  let c5 : Inc w t0 := ⟨_, i5⟩
  have hne2 : c2 ≠ e := by intro h; apply he2; rw [← h]
  have hne5 : c5 ≠ e := by intro h; apply he5; rw [← h]
  have z2 : ∑ r, incV w t0 r e * P1 w Complex.I (j + 2) x r = 0 := by
    have := congrFun (congrFun hbi c2) e
    rw [Matrix.one_apply_ne hne2] at this
    rw [← this]; simp only [Matrix.mul_apply, Matrix.transpose_apply, incW, Matrix.of_apply]
    refine Finset.sum_congr rfl fun r _ => ?_
    simp [c2, g2, reg, mul_comm]
  have z5 : ∑ r, incV w t0 r e * P1 w Complex.I (j + 5) v r = 0 := by
    have := congrFun (congrFun hbi c5) e
    rw [Matrix.one_apply_ne hne5] at this
    rw [← this]; simp only [Matrix.mul_apply, Matrix.transpose_apply, incW, Matrix.of_apply]
    refine Finset.sum_congr rfl fun r _ => ?_
    simp [c5, g5, reg, mul_comm]
  obtain ⟨⟨j', c⟩, hc⟩ := p
  simp only at hp
  rcases hp with ⟨hj', hc1⟩ | ⟨hj', hc0⟩
  · -- first HOST, slot 1: B column = row x of P1(j) = row x of P1(j+2)
    obtain ⟨jF, hjF⟩ : ∃ jF : Fin w.evs.length, jF.val = j := ⟨⟨j, by omega⟩, rfl⟩
    have h0' : w.evs.get jF = Ev.host x y 0 1 := by
      have : jF = ⟨j, by omega⟩ := Fin.ext hjF
      rw [this]; exact h0
    have hr := host_rows w jF x y 0 1 h0' hxy
    have hj'F : j' = jF := Fin.ext (hj'.trans hjF.symm)
    subst hj'F
    subst hc1
    have htm : tm w (j', 1) = terms (Ev.host x y 0 1 : Ev n k) 1 := by unfold tm; rw [h0']
    simp only [Bw, Matrix.of_apply, htm, terms]
    show ∑ r, incV w t0 r e * P1 w Complex.I j'.val x r = 0
    have hrow : ∀ r, P1 w Complex.I j'.val x r = P1 w Complex.I (j + 2) x r := by
      intro r
      have a1 := (hr r).2
      rw [hjF] at a1
      simp only [map_zero, zero_mul, mul_one, zero_add, add_zero, one_mul, sub_zero] at a1
      have a2 := congrFun (congrFun hP2 x) r
      rw [Matrix.add_mul, Matrix.one_mul, Matrix.add_apply, E1_mul_apply] at a2
      simp only [hxu, if_false, add_zero] at a2
      rw [hjF, a1, a2]
    simp_rw [hrow]
    exact z2
  · -- second HOST, slot 0: B column = row v of P1(j+1) = row v of P1(j+5)
    obtain ⟨jF, hjF⟩ : ∃ jF : Fin w.evs.length, jF.val = j + 1 := ⟨⟨j + 1, by omega⟩, rfl⟩
    have h1' : w.evs.get jF = Ev.host u v α 0 := by
      have : jF = ⟨j + 1, by omega⟩ := Fin.ext hjF
      rw [this]; exact h1
    have hr := host_rows w jF u v α 0 h1' huv
    have hj'F : j' = jF := Fin.ext (hj'.trans hjF.symm)
    subst hj'F
    subst hc0
    have htm : tm w (j', 0) = terms (Ev.host u v α 0 : Ev n k) 0 := by unfold tm; rw [h1']
    simp only [Bw, Matrix.of_apply, htm, terms]
    show ∑ r, incV w t0 r e * P1 w Complex.I j'.val v r = 0
    have hrow : ∀ r, P1 w Complex.I j'.val v r = P1 w Complex.I (j + 5) v r := by
      intro r
      have a1 := (hr r).1
      rw [hjF] at a1
      simp only [map_zero, zero_mul, sub_zero] at a1
      rw [hjF, a1, P5, P4, P3]
    simp_rw [hrow]
    exact z5

end xkerA

section schemaA
variable {n k : ℕ} {w : CWord n k}

/-- the type-A schema: one two-HOST J record per stage, in call order (records do not interleave). -/
structure JA (w : CWord n k) where
  pos : Fin k → ℕ
  mono : StrictMono pos
  sep : ∀ s t, s < t → pos s + 1 < pos t
  lt : ∀ s, pos s + 5 < w.evs.length
  x : Fin k → Fin n
  y : Fin k → Fin n
  u : Fin k → Fin n
  v : Fin k → Fin n
  α : Fin k → ℚ
  α0 : ∀ s, α s ≠ 0
  hxy : ∀ s, x s ≠ y s
  hxu : ∀ s, x s ≠ u s
  hxv : ∀ s, x s ≠ v s
  hyu : ∀ s, y s ≠ u s
  hyv : ∀ s, y s ≠ v s
  huv : ∀ s, u s ≠ v s
  h0 : ∀ s, w.evs.get ⟨pos s, by have := lt s; omega⟩ = Ev.host (x s) (y s) 0 1
  h1 : ∀ s, w.evs.get ⟨pos s + 1, by have := lt s; omega⟩ = Ev.host (u s) (v s) (α s) 0
  h2 : ∀ s, w.evs.get ⟨pos s + 2, by have := lt s; omega⟩ = Ev.idle (x s) {s} 0
  h3 : ∀ s, w.evs.get ⟨pos s + 3, by have := lt s; omega⟩ = Ev.idle (y s) {s} 0
  h4 : ∀ s, w.evs.get ⟨pos s + 4, by have := lt s; omega⟩ = Ev.idle (u s) {s} 0
  h5 : ∀ s, w.evs.get ⟨pos s + 5, lt s⟩ = Ev.idle (v s) {s} 0

theorem JA.nz1 (J : JA w) (s : Fin k) :
    (tm w (⟨J.pos s, by have := J.lt s; omega⟩, 1)).2.2 ≠ 0 := by
  unfold tm; rw [J.h0 s]; simp [terms]

theorem JA.nz2 (J : JA w) (s : Fin k) :
    (tm w (⟨J.pos s + 1, by have := J.lt s; omega⟩, 0)).2.2 ≠ 0 := by
  unfold tm; rw [J.h1 s]; simpa [terms] using J.α0 s

/-- the two stage-s frame columns: slot 1 of the first HOST, slot 0 of the second. -/
def JA.col (J : JA w) (s : Fin k) (c : Fin 2) : Iota w :=
  if c = 0 then ⟨(⟨J.pos s, by have := J.lt s; omega⟩, 1), J.nz1 s⟩
  else ⟨(⟨J.pos s + 1, by have := J.lt s; omega⟩, 0), J.nz2 s⟩

theorem JA.col_val (J : JA w) (s : Fin k) (c : Fin 2) :
    ((J.col s c).1.1.val = J.pos s ∧ (J.col s c).1.2 = 1) ∨
    ((J.col s c).1.1.val = J.pos s + 1 ∧ (J.col s c).1.2 = 0) := by
  unfold JA.col; split_ifs <;> simp

theorem JA.beta_col (J : JA w) (s : Fin k) (c : Fin 2) :
    J.pos s ≤ βw w (J.col s c) ∧ βw w (J.col s c) ≤ J.pos s + 1 := by
  rcases JA.col_val J s c with h | h <;> simp only [βw] <;> omega

theorem JA.evS2 (J : JA w) (s : Fin k) : evS w ⟨J.pos s + 2, by have := J.lt s; omega⟩ = {s} := by
  unfold evS; rw [J.h2 s]

theorem JA.evS5 (J : JA w) (s : Fin k) : evS w ⟨J.pos s + 5, J.lt s⟩ = {s} := by
  unfold evS; rw [J.h5 s]

theorem JA.mains (J : JA w) : 2 * k ≤ (univ.filter fun j => (evS w j).card = 1).card := by
  let f : Fin k × Fin 2 → Fin w.evs.length := fun p => ⟨J.pos p.1 + 2 + 3 * p.2.val, by have := J.lt p.1; have := p.2.isLt; omega⟩
  have hS : ∀ p, evS w (f p) = {p.1} := by
    intro p
    obtain ⟨s, i⟩ := p
    fin_cases i
    · exact J.evS2 s
    · exact J.evS5 s
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

theorem JA.ker (hL : Legal w) (J : JA w) (s' : Fin k) (j : Fin w.evs.length) (hs' : s' ∈ evS w j)
    (hj : 2 ≤ (evS w j).card) (a : Fin 2) :
    ∑ r, vE w j r * Bw w Complex.I r (J.col s' a) = 0 := by
  obtain ⟨hL', hb⟩ := legal_dn w hL s'
  have he2 : j.val ≠ J.pos s' + 2 := by
    intro h
    have : j = ⟨J.pos s' + 2, by have := J.lt s'; omega⟩ := Fin.ext h
    rw [this, J.evS2] at hj; simp at hj
  have he5 : j.val ≠ J.pos s' + 5 := by
    intro h
    have : j = ⟨J.pos s' + 5, J.lt s'⟩ := Fin.ext h
    rw [this, J.evS5] at hj; simp at hj
  exact jA_xker w s' hb hL' (J.pos s') (J.lt s') (J.x s') (J.y s') (J.u s') (J.v s') (J.α s')
    (J.hxy s') (J.hxu s') (J.hxv s') (J.hyu s') (J.hyv s') (J.huv s')
    (J.h0 s') (J.h1 s') (J.h2 s') (J.h3 s') (J.h4 s') (J.h5 s')
    ⟨j, (mem_evS w s' j).mp hs'⟩ he2 he5 (J.col s' a) (JA.col_val J s' a)

/-- the type-A schema as a `Sch`. -/
def JA.sch (J : JA w) : Sch w where
  col := J.col
  ord := by
    intro s t h a b
    have h1 := (JA.beta_col J s a).2
    have h2 := (JA.beta_col J t b).1
    have h3 := J.sep s t h
    omega
  mains := J.mains
  hbh := fun hL r s hs a =>
    (legal_jA_support w hL s (J.pos s) (J.lt s) (J.x s) (J.y s) (J.u s) (J.v s) (J.α s)
      (J.hxy s) (J.hxu s) (J.hxv s) (J.hyu s) (J.hyv s) (J.huv s)
      (J.h0 s) (J.h1 s) (J.h2 s) (J.h3 s) (J.h4 s) (J.h5 s) r hs (J.col s a) (by
        rcases JA.col_val J s a with h | h
        · exact Or.inl h.1
        · exact Or.inr h.1)).2
  hah := fun hL r s hs a =>
    (legal_jA_support w hL s (J.pos s) (J.lt s) (J.x s) (J.y s) (J.u s) (J.v s) (J.α s)
      (J.hxy s) (J.hxu s) (J.hxv s) (J.hyu s) (J.hyv s) (J.huv s)
      (J.h0 s) (J.h1 s) (J.h2 s) (J.h3 s) (J.h4 s) (J.h5 s) r hs (J.col s a) (by
        rcases JA.col_val J s a with h | h
        · exact Or.inl h.1
        · exact Or.inr h.1)).1
  ker := fun hL s j hs hj a => JA.ker hL J s j hs hj a

/-- HEADLINE, type A. -/
theorem word_hp_A (hL : Legal w) (J : JA w) (hodd : ∀ r, w.ex r % 2 = 1) (hk : 3 ≤ k)
    (hQ0 : Fintype.card (Iota w) = 2 * k) (hn : n + 2 = Fintype.card (Iota w))
    (hlam : ∀ s, IsUnit ((sgK (βw w) (sgG (Aw w Complex.I) (Bw w Complex.I))).submatrix (J.col s) (J.col s)).det)
    (hdeg : ∀ r, 2 ≤ (w.mask r).card) :
    cHat w ≤ CallerHP.HPr k :=
  word_hp hL J.sch hodd hk hQ0 hn hlam hdeg

end schemaA

end CallerAsm

#print axioms CallerAsm.jA_xker
#print axioms CallerAsm.JA.sch
#print axioms CallerAsm.word_hp_A
