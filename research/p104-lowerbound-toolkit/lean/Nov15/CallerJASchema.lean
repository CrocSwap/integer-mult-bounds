/-
CallerJASchema (lane JASCHEMA, Nov 20).  word_hpq for the type-A J record (two HOSTs in different events).
Problem: in the event-labelled frame the two stage columns of a type-A stage sit in DIFFERENT slots (events pos s and pos s+1),
so CallerBridge.Host (both host columns in one slot) and the leaf laws (LeafSet: a leaf vanishes off ONE slot) do not apply verbatim.
Fix (all [P Lean]):
 * G_zero          : G(col s 1, col s 0) = b_{HOST2} . a_{HOST1} = -2 [v = y] = 0  (v, y distinct fields; M M^-1 = 1).
 * regroup        : beta' merges the slot pos s + 1 into pos s.  The relation (beta' j < beta' i) differs from (beta j < beta i) only at
                    (col s 1, col s 0), where G = 0, hence sgLow beta' G = sgLow beta G, sgK beta' G = sgK beta G (sgK_eq) and
                    sgProd beta' = sgProd beta (sgProd_eq).  So P = -1 and every K-block hypothesis transfers.
 * hostA          : the CallerBridge.Host structure on (Aw, Bw, beta') (two columns per merged slot, <= 2 per slot, hA/hB from the schema).
 * word_lawQ_gen  : the Frame -> Cfg bridge of CallerCfgBridge for ANY Sch (leaf laws taken as hypotheses).
 * word_hpq_A     : legal type-A word, odd targets, k >= 77, n+2 = |Iota|, lambda /= -1 on each stage's 2x2 K-block, every role of degree
                    >= 1  ==>  cHatQ w < 128.891.
Kernel only.
-/
import Nov15.CallerCfgBridge
import Nov15.CallerAsmA

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerJA
open Finset Matrix CallerSign CallerWord CallerAsm CallerEv CallerHP CallerBridge

/-! ## abstract regrouping: the relation matters only through Low -/
section regroup
variable {K : Type*} [Field K] {ι : Type*} [Fintype ι] [DecidableEq ι] {n : ℕ}

theorem low_eq (β β' : ι → ℕ) (G : Matrix ι ι K)
    (h : ∀ i j, (β' j < β' i ↔ β j < β i) ∨ G i j = 0) : sgLow β' G = sgLow β G := by
  ext i j
  simp only [sgLow, Matrix.of_apply]
  rcases h i j with h | h
  · exact if_congr h rfl rfl
  · simp [h]

theorem sgK_regroup (β β' : ι → ℕ) (G : Matrix ι ι K)
    (h : ∀ i j, (β' j < β' i ↔ β j < β i) ∨ G i j = 0) : sgK β' G = sgK β G := by
  rw [sgK_eq, sgK_eq, low_eq β β' G h]

theorem prod_regroup (A B : Matrix (Fin n) ι K) (β β' : ι → ℕ) (m : ℕ) (hβ : ∀ i, β i < m) (hβ' : ∀ i, β' i < m)
    (h : ∀ i j, (β' j < β' i ↔ β j < β i) ∨ sgG A B i j = 0) : sgProd A B β' m = sgProd A B β m := by
  rw [sgProd_eq A B β' m hβ', sgProd_eq A B β m hβ, low_eq β β' _ h]

end regroup

/-! ## the type-A schema: slots and the zero cross term -/
section jaw
variable {n k : ℕ} {w : CWord n k}

theorem col_slot0 (J : JA w) (s : Fin k) : (J.col s 0).1.2 = 1 := by simp [JA.col]
theorem col_slot1 (J : JA w) (s : Fin k) : (J.col s 1).1.2 = 0 := by simp [JA.col]
theorem beta_col0 (J : JA w) (s : Fin k) : βw w (J.col s 0) = J.pos s := by simp [JA.col, βw]
theorem beta_col1 (J : JA w) (s : Fin k) : βw w (J.col s 1) = J.pos s + 1 := by simp [JA.col, βw]

theorem pos_ne (J : JA w) (s t : Fin k) : J.pos s ≠ J.pos t + 1 := by
  rcases lt_trichotomy s t with h | h | h
  · have := J.sep s t h; have := J.mono h; omega
  · subst h; omega
  · have := J.sep t s h; omega

/-- the only column in event `pos s + 1` is the second HOST's slot 0. -/
theorem slot2 (J : JA w) (s : Fin k) (i : Iota w) (h : βw w i = J.pos s + 1) : i = J.col s 1 := by
  have hlt' : J.pos s + 1 < w.evs.length := by have := J.lt s; omega
  obtain ⟨⟨j, c⟩, hnz⟩ := i
  have hj : j = ⟨J.pos s + 1, hlt'⟩ := Fin.ext h
  subst hj
  fin_cases c
  · simp [JA.col]
  · exfalso
    apply hnz
    unfold tm
    rw [J.h1 s]
    simp [terms]

/-- the only column in event `pos s` is the first HOST's slot 1. -/
theorem slot1 (J : JA w) (s : Fin k) (i : Iota w) (h : βw w i = J.pos s) : i = J.col s 0 := by
  have hlt' : J.pos s < w.evs.length := by have := J.lt s; omega
  obtain ⟨⟨j, c⟩, hnz⟩ := i
  have hj : j = ⟨J.pos s, hlt'⟩ := Fin.ext h
  subst hj
  fin_cases c
  · exfalso
    apply hnz
    unfold tm
    rw [J.h0 s]
    simp [terms]
  · simp [JA.col]

/-- b_{HOST2} . a_{HOST1} = 0 : the cross term of the two single-column blocks of a type-A stage. -/
theorem G_zero (hL : Legal w) (J : JA w) (s : Fin k) :
    sgG (Aw w Complex.I) (Bw w Complex.I) (J.col s 1) (J.col s 0) = 0 := by
  obtain ⟨_, hb⟩ := legal_dn w hL s
  have hlt := J.lt s
  have hu : IsUnit (P1 w Complex.I (J.pos s + 1)).det :=
    isUnit_iff_ne_zero.mpr (det_P1_ne w Complex.I hb (J.pos s + 1) (by omega))
  have hM : P1 w Complex.I (J.pos s + 1) * (P1 w Complex.I (J.pos s + 1))⁻¹ = 1 := Matrix.mul_nonsing_inv _ hu
  have h0 := congrFun (congrFun hM (J.v s)) (J.y s)
  rw [Matrix.one_apply_ne (J.hyv s).symm, Matrix.mul_apply] at h0
  have t1 : tm w (J.col s 1).1 = (J.u s, J.v s, -2 * J.α s) := by
    have : (J.col s 1).1 = (⟨J.pos s + 1, by omega⟩, 0) := by simp [JA.col]
    rw [this]; unfold tm; rw [J.h1 s]; simp [terms]
  have t0 : tm w (J.col s 0).1 = (J.y s, J.x s, -2 * 1) := by
    have : (J.col s 0).1 = (⟨J.pos s, by omega⟩, 1) := by simp [JA.col]
    rw [this]; unfold tm; rw [J.h0 s]; simp [terms]
  have b1 : βw w (J.col s 1) = J.pos s + 1 := beta_col1 J s
  have b0 : βw w (J.col s 0) = J.pos s := beta_col0 J s
  have e1 : ∀ r, Bw w Complex.I r (J.col s 1) = P1 w Complex.I (J.pos s + 1) (J.v s) r := by
    intro r
    simp only [Bw, Matrix.of_apply, t1]
    rw [show (J.col s 1).1.1.val = J.pos s + 1 from b1]
  have e2 : ∀ r, Aw w Complex.I r (J.col s 0) =
      (P1 w Complex.I (J.pos s + 1))⁻¹ r (J.y s) * algebraMap ℚ ℂ (-2 * 1) := by
    intro r
    simp only [Aw, Matrix.of_apply, t0]
    rw [show (J.col s 0).1.1.val = J.pos s from b0]
  simp only [sgG, Matrix.mul_apply, Matrix.transpose_apply]
  calc ∑ r, Bw w Complex.I r (J.col s 1) * Aw w Complex.I r (J.col s 0)
      = ∑ r, algebraMap ℚ ℂ (-2 * 1) * (P1 w Complex.I (J.pos s + 1) (J.v s) r *
          (P1 w Complex.I (J.pos s + 1))⁻¹ r (J.y s)) := by
        refine Finset.sum_congr rfl fun r _ => ?_
        rw [e1 r, e2 r]; ring
    _ = algebraMap ℚ ℂ (-2 * 1) * ∑ r, (P1 w Complex.I (J.pos s + 1) (J.v s) r *
          (P1 w Complex.I (J.pos s + 1))⁻¹ r (J.y s)) := by rw [← Finset.mul_sum]
    _ = 0 := by rw [h0, mul_zero]

/-! ## the merged slots -/
open Classical in
/-- merge slot `pos s + 1` into slot `pos s`. -/
noncomputable def βA (J : JA w) : Iota w → ℕ :=
  fun i => if ∃ s, βw w i = J.pos s + 1 then βw w i - 1 else βw w i

theorem βA_Q (J : JA w) (i : Iota w) (s : Fin k) (h : βw w i = J.pos s + 1) : βA J i = J.pos s := by
  unfold βA
  rw [if_pos ⟨s, h⟩]; omega

theorem βA_nQ (J : JA w) (i : Iota w) (h : ¬ ∃ s, βw w i = J.pos s + 1) : βA J i = βw w i := by
  unfold βA
  rw [if_neg h]

theorem βA_le (J : JA w) (i : Iota w) : βA J i ≤ βw w i := by
  unfold βA
  split_ifs <;> omega

theorem βA_rel (hL : Legal w) (J : JA w) (i j : Iota w) :
    (βA J j < βA J i ↔ βw w j < βw w i) ∨ sgG (Aw w Complex.I) (Bw w Complex.I) i j = 0 := by
  by_cases hi : ∃ s, βw w i = J.pos s + 1
  · obtain ⟨s, hs⟩ := hi
    rw [βA_Q J i s hs]
    by_cases hj : ∃ t, βw w j = J.pos t + 1
    · obtain ⟨t, ht⟩ := hj
      rw [βA_Q J j t ht]
      left; omega
    · rw [βA_nQ J j hj]
      by_cases c : βw w j = J.pos s
      · right
        have hj' := slot1 J s j c
        have hi' := slot2 J s i hs
        rw [hj', hi']
        exact G_zero hL J s
      · left; omega
  · rw [βA_nQ J i hi]
    by_cases hj : ∃ t, βw w j = J.pos t + 1
    · obtain ⟨t, ht⟩ := hj
      rw [βA_Q J j t ht]
      have : βw w i ≠ J.pos t + 1 := fun h => hi ⟨t, h⟩
      left; omega
    · rw [βA_nQ J j hj]
      left; exact Iff.rfl

theorem βA_lt (J : JA w) (i : Iota w) : βA J i < w.evs.length :=
  lt_of_le_of_lt (βA_le J i) (beta_lt w i)

/-- the merged frame is a `CallerBridge.Host`: two columns per merged slot, the schema's masks. -/
noncomputable def hostA (hL : Legal w) (J : JA w) (hodd : ∀ r, w.ex r % 2 = 1)
    (hlam : ∀ s, IsUnit ((sgK (βw w) (sgG (Aw w Complex.I) (Bw w Complex.I))).submatrix (J.col s) (J.col s)).det) :
    Host (Aw w Complex.I) (Bw w Complex.I) (βA J) k w.evs.length w.mask where
  col := J.col
  pos := J.pos
  hβ := βA_lt J
  hP := by
    rw [prod_regroup (Aw w Complex.I) (Bw w Complex.I) (βw w) (βA J) w.evs.length (beta_lt w) (βA_lt J)
      (fun i j => βA_rel hL J i j)]
    exact (legal_frame w hL hodd).1
  hpos := J.mono.injective
  hposlt := fun s => by have := J.lt s; omega
  hcolβ := fun s a => by
    fin_cases a
    · have h0 := beta_col0 J s
      have hn : ¬ ∃ t, βw w (J.col s 0) = J.pos t + 1 := by
        rintro ⟨t, ht⟩; rw [h0] at ht; exact pos_ne J s t ht
      show βA J (J.col s 0) = J.pos s
      rw [βA_nQ J _ hn, h0]
    · show βA J (J.col s 1) = J.pos s
      exact βA_Q J _ s (beta_col1 J s)
  hcolinj := by
    intro p q h
    obtain ⟨s, a⟩ := p; obtain ⟨s', b⟩ := q
    have hb : ∀ s a, βA J (J.col s a) = J.pos s := by
      intro s a
      fin_cases a
      · have h0 := beta_col0 J s
        have hn : ¬ ∃ t, βw w (J.col s 0) = J.pos t + 1 := by
          rintro ⟨t, ht⟩; rw [h0] at ht; exact pos_ne J s t ht
        show βA J (J.col s 0) = J.pos s
        rw [βA_nQ J _ hn, h0]
      · exact βA_Q J _ s (beta_col1 J s)
    have h1 : J.pos s = J.pos s' := by
      rw [← hb s a, ← hb s' b]; exact congrArg (βA J) h
    have hs : s = s' := J.mono.injective h1
    subst hs
    have : a = b := by
      fin_cases a <;> fin_cases b
      · rfl
      · exfalso
        have := congrArg (fun i : Iota w => i.1.2) h
        simp [col_slot0, col_slot1] at this
      · exfalso
        have := congrArg (fun i : Iota w => i.1.2) h
        simp [col_slot0, col_slot1] at this
      · rfl
    rw [this]
  hslot := by
    intro s i hi
    by_cases hq : ∃ t, βw w i = J.pos t + 1
    · obtain ⟨t, ht⟩ := hq
      rw [βA_Q J i t ht] at hi
      have hts : t = s := J.mono.injective hi
      subst hts
      exact ⟨1, slot2 J t i ht⟩
    · rw [βA_nQ J i hq] at hi
      exact ⟨0, slot1 J s i hi⟩
  hw := by
    intro t ht
    let f : {i : Iota w // βA J i = t} → Fin 2 := fun i => i.1.1.2
    have hf : Function.Injective f := by
      intro i j hij
      have hi := i.2
      have hj := j.2
      have hij' : i.1.1.2 = j.1.1.2 := hij
      apply Subtype.ext
      by_cases hqi : ∃ s, βw w i.1 = J.pos s + 1
      · obtain ⟨s, hs⟩ := hqi
        have hi' := slot2 J s i.1 hs
        by_cases hqj : ∃ s', βw w j.1 = J.pos s' + 1
        · obtain ⟨s', hs'⟩ := hqj
          have hj' := slot2 J s' j.1 hs'
          have e1 := βA_Q J i.1 s hs
          have e2 := βA_Q J j.1 s' hs'
          have : s = s' := J.mono.injective (by rw [← e1, ← e2, hi, hj])
          subst this
          rw [hi', hj']
        · exfalso
          have e1 := βA_Q J i.1 s hs
          have e2 := βA_nQ J j.1 hqj
          have hjs : βw w j.1 = J.pos s := by rw [← e2, hj, ← hi, e1]
          have hj' := slot1 J s j.1 hjs
          rw [hi', hj'] at hij'
          simp [col_slot0, col_slot1] at hij'
      · by_cases hqj : ∃ s', βw w j.1 = J.pos s' + 1
        · exfalso
          obtain ⟨s', hs'⟩ := hqj
          have e1 := βA_nQ J i.1 hqi
          have e2 := βA_Q J j.1 s' hs'
          have his : βw w i.1 = J.pos s' := by rw [← e1, hi, ← hj, e2]
          have hi' := slot1 J s' i.1 his
          have hj' := slot2 J s' j.1 hs'
          rw [hi', hj'] at hij'
          simp [col_slot0, col_slot1] at hij'
        · have e1 := βA_nQ J i.1 hqi
          have e2 := βA_nQ J j.1 hqj
          have hev : i.1.1.1 = j.1.1.1 := Fin.ext (by
            have : βw w i.1 = βw w j.1 := by rw [← e1, ← e2, hi, hj]
            exact this)
          exact Subtype.ext (Prod.ext hev hij')
    have := Fintype.card_le_of_injective f hf
    simpa using this
  hlam := fun s => by
    rw [sgK_regroup (βw w) (βA J) _ (fun i j => βA_rel hL J i j)]
    exact (hlam s).ne_zero
  hA := fun r s hs a => (JA.sch J).hah hL r s hs a
  hB := fun r s hs a => (JA.sch J).hbh hL r s hs a

end jaw

/-! ## the Frame -> Cfg bridge for any schema (leaf laws as hypotheses) -/
section gen
variable {n k : ℕ} {w : CWord n k}

theorem word_lawQ_gen (hL : Legal w) (S : Sch w) (hodd : ∀ r, w.ex r % 2 = 1) (hk : 2 ≤ k)
    (hn : n + 2 = Fintype.card (Iota w))
    (hlam : ∀ s, IsUnit ((sgK (βw w) (sgG (Aw w Complex.I) (Bw w Complex.I))).submatrix (S.col s) (S.col s)).det)
    (hdeg1 : ∀ r, 1 ≤ (w.mask r).card)
    (h2k : 2 * k ≤ Fintype.card (Iota w))
    (hle : (univ.filter fun r : Fin n => (w.mask r).card = 1).card ≤ k + (Fintype.card (Iota w) - 2 * k))
    (hkT : (univ.filter fun r : Fin n => (w.mask r).card = 1).card ≤ k * (Fintype.card (Iota w) - 2 * k)) :
    ∃ C : Cfg k, C.LawQ ∧ C.valQ = cHatQ w := by
  have hkpos : 0 < k := by omega
  have hG := word_hG hL S hodd hn hlam
  let s0 : Fin k := ⟨0, hkpos⟩
  let e₀ : Fin w.evs.length := (S.col s0 0).1.1
  obtain ⟨Pm⟩ := exists_match w.mask (fun r s a => Bw w Complex.I r (S.col s a)) (evS w)
    (wordEv hL S) e₀ (word_count hL)
  have hex : ∀ s : Fin k, ∃ t : Fin k, s ≠ t := by
    intro s
    by_cases h : s.val = 0
    · exact ⟨⟨1, by omega⟩, fun e => by have := congrArg Fin.val e; simp at this; omega⟩
    · exact ⟨⟨0, hkpos⟩, fun e => by have := congrArg Fin.val e; simp at this; omega⟩
  have hdeep : ∀ s : Fin k, 2 ≤ (univ.filter fun r => s ∈ w.mask r ∧ 2 ≤ (w.mask r).card ∧
      (evS w (Pm.ev r s)).card = 1).card := by
    intro s
    obtain ⟨t, hst⟩ := hex s
    exact deep_stage w.mask (evS w) Pm s t hst (word_rc2_pair hL S hodd hn hlam s t hst 2)
  rw [← hn] at hle hkT h2k
  have e : (univ.filter fun r : Fin n => ¬ 2 ≤ (w.mask r).card) = (univ.filter fun r : Fin n => (w.mask r).card = 1) := by
    ext r; simp only [mem_filter, mem_univ, true_and]; have := hdeg1 r; omega
  have hsplit := Finset.card_filter_add_card_filter_not (s := (univ : Finset (Fin n))) (fun r => 2 ≤ (w.mask r).card)
  rw [e] at hsplit
  simp only [Finset.card_univ, Fintype.card_fin] at hsplit
  generalize hnl : (univ.filter fun r : Fin n => 2 ≤ (w.mask r).card).card = nl at hsplit
  generalize hn1 : (univ.filter fun r : Fin n => (w.mask r).card = 1).card = n1 at hsplit hle hkT
  let C : Cfg k :=
    { R := Fin n
      st := w.mask
      a := fun r s => (evS w (Pm.ev r s)).card
      mn := fun r s => decide ((evS w (Pm.ev r s)).card = 1) }
  refine ⟨C, ?_, ?_⟩
  · refine ⟨hdeg1, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
    · intro r s hs; exact card_pos.2 ⟨s, Pm.mem r s hs⟩
    · intro r s hs; exact card_le_card (Pm.sub r s hs)
    · intro r s hs hm; simpa [C] using hm
    · exact mains_real w.mask (evS w) Pm hdeep
    · intro l hl3 hlk
      exact rc2_row_real hkpos w.mask (fun r s a => Bw w Complex.I r (S.col s a))
        (fun r s a => Aw w Complex.I r (S.col s a)) (evS w)
        (fun r s hs a => S.hbh hL r s hs a) (fun r s hs a => S.hah hL r s hs a) (wordEv hL S) hG Pm l (by omega)
    · have hc' : (univ.filter fun r : Fin n => 2 ≤ (C.st r).card).card = nl := hnl
      show (k : ℝ) - 2 ≤ (((univ.filter fun r : Fin n => 2 ≤ (C.st r).card).card : ℕ) : ℝ)
      rw [hc']
      have : k ≤ nl + 2 := by omega
      have h := (Nat.cast_le (α := ℝ)).2 this
      push_cast at h
      linarith
    · show (k : ℝ) * (2 * k - 2) ≤ k * (Fintype.card (Fin n) : ℝ) - (((univ.filter fun r : Fin n => (C.st r).card = 1).card : ℕ) : ℝ)
      have hc : (univ.filter fun r : Fin n => (C.st r).card = 1).card = n1 := hn1
      rw [hc, Fintype.card_fin]
      have hT : ((n + 2 - 2 * k : ℕ) : ℝ) = (n : ℝ) + 2 - 2 * k := by
        rw [Nat.cast_sub (by omega)]; push_cast; ring
      have h1 : (n1 : ℝ) ≤ k * ((n : ℝ) + 2 - 2 * k) := by
        rw [← hT]; exact_mod_cast hkT
      nlinarith
  · unfold Cfg.valQ cHatQ
    have hsum := roleVal_sum w.mask (evS w) Pm σ0
    show 104 / (k : ℝ) * (∑ r, roleVal σ0 (w.mask r) (fun s => (evS w (Pm.ev r s)).card) - (Fintype.card (Fin n) : ℝ) + 2 * k - 2) = _
    rw [hsum, Fintype.card_fin]
    ring

/-- HEADLINE, type A.  Legal type-A caller word, odd targets, tight role count `n + 2 = |Iota|` (`e = 0`, `T = Q`), `lambda /= -1` on each
stage's 2x2 K-block, every role of degree `>= 1`, `k >= 77`:  `cHatQ w < 128.891`. -/
theorem word_hpq_A (hL : Legal w) (J : JA w) (hodd : ∀ r, w.ex r % 2 = 1) (hk : 77 ≤ k)
    (hn : n + 2 = Fintype.card (Iota w))
    (hlam : ∀ s, IsUnit ((sgK (βw w) (sgG (Aw w Complex.I) (Bw w Complex.I))).submatrix (J.col s) (J.col s)).det)
    (hdeg1 : ∀ r, 1 ≤ (w.mask r).card) :
    cHatQ w < 128891 / 1000 := by
  have H := hostA hL J hodd hlam
  obtain ⟨C, hC, hv⟩ := word_lawQ_gen hL J.sch hodd (by omega) hn hlam hdeg1 H.two_k_le
    (H.leaves_le (by norm_num : (2 : ℂ) ≠ 0)) (H.leaves_le_kT (by norm_num : (2 : ℂ) ≠ 0))
  rw [← hv]
  exact valQ_lt hk C hC

end gen

/-! ## non-vacuity of the regroup (frame level): two single-column stage slots with a nonzero G_pq and G_qp = 0 -/
section toy
open CallerSign

def tA : Matrix (Fin 2) (Fin 2) ℚ := !![1, 0; 0, 1]
def tB : Matrix (Fin 2) (Fin 2) ℚ := !![0, 0; 1, 1]
def tβ : Fin 2 → ℕ := ![0, 1]
def tβ' : Fin 2 → ℕ := ![0, 0]

theorem toy_G : sgG tA tB = !![0, 1; 0, 1] := by
  ext i j; fin_cases i <;> fin_cases j <;> simp [sgG, tA, tB, Matrix.mul_apply, Fin.sum_univ_two]

/-- hypothesis of the regroup lemma holds, with G_pq = 1 /= 0 and the order relation genuinely changed at (q, p). -/
theorem toy_rel : ∀ i j : Fin 2, (tβ' j < tβ' i ↔ tβ j < tβ i) ∨ sgG tA tB i j = 0 := by
  intro i j
  rw [toy_G]
  fin_cases i <;> fin_cases j <;> simp [tβ, tβ']

theorem toy_changed : ¬ (∀ i j : Fin 2, (tβ' j < tβ' i ↔ tβ j < tβ i)) := by
  intro h
  have := h 1 0
  simp [tβ, tβ'] at this

theorem toy_G_pq : sgG tA tB 0 1 ≠ 0 := by rw [toy_G]; simp

/-- the merged and the split stage products agree (both `1 + E12 + E22`), and so do the K matrices. -/
theorem toy_prod : sgProd tA tB tβ' 2 = sgProd tA tB tβ 2 :=
  prod_regroup tA tB tβ tβ' 2 (fun i => by fin_cases i <;> simp [tβ]) (fun i => by fin_cases i <;> simp [tβ'])
    toy_rel

theorem toy_pi0 : (blkPi tβ 0 : Matrix (Fin 2) (Fin 2) ℚ) = !![1, 0; 0, 0] := by
  ext i j; fin_cases i <;> fin_cases j <;> simp [blkPi, tβ, Matrix.diagonal_apply]
theorem toy_pi1 : (blkPi tβ 1 : Matrix (Fin 2) (Fin 2) ℚ) = !![0, 0; 0, 1] := by
  ext i j; fin_cases i <;> fin_cases j <;> simp [blkPi, tβ, Matrix.diagonal_apply]
theorem toy_BT : tBᵀ = !![0, 1; 0, 1] := by
  ext i j; fin_cases i <;> fin_cases j <;> simp [tB]

theorem toy_prod_val : sgProd tA tB tβ 2 = !![1, 1; 0, 2] := by
  simp only [sgProd, sgStage, toy_pi0, toy_pi1, tA, toy_BT]
  simp [tB, Matrix.mul_fin_two, Matrix.one_fin_two, Matrix.of_add_of]
  norm_num

theorem toy_K : sgK tβ' (sgG tA tB) = sgK tβ (sgG tA tB) := sgK_regroup tβ tβ' _ toy_rel

end toy

end CallerJA

#print axioms CallerJA.G_zero
#print axioms CallerJA.βA_rel
#print axioms CallerJA.prod_regroup
#print axioms CallerJA.hostA
#print axioms CallerJA.word_lawQ_gen
#print axioms CallerJA.word_hpq_A
#print axioms CallerJA.toy_rel
#print axioms CallerJA.toy_prod
#print axioms CallerJA.toy_prod_val
#print axioms CallerJA.toy_K
#print axioms CallerJA.toy_changed
