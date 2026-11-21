/-
CallerCfgBridge (lane CFGBRIDGE, Nov 20).  Frame -> Cfg bridge for the Q >= 1, e = 0 caller branch.
Discharges EVERY field of CallerHPQ.LawQ from a SPEC-legal type-B caller word (CallerAsm.JB schema):
  DEEP   (`mains`) : per stage >= 2 singleton pieces on roles of degree >= 2  <-  ev_pair at l = 2 + the stage matching (`deep_stage`);
  RC2_l  (`rc2`)   : `rc2_row_real` (rc_row_nat of CallerEv, as in ev_frame_bound);
  LC     (`lc`)    : leaf_channel_thin (CallerThinDel) on the host/thin split of the frame: #leaves <= k + T, T = |Iota| - 2k;
  LEAF   (`leaf`)  : CallerThin.leaf_rank, once per stage: #leaves at a stage <= T, hence #leaves <= k T;
  role count       : n + 2 = |Iota|  (e = 0, tight).
Headline `word_hpq`: legal type-B word, odd targets, lambda /= -1 on every host slot, n + 2 = |Iota|, every role of degree >= 1,
k >= 77  ==>  cHatQ w < 128.891  (cHatQ = 104/k (invoice - (n - (2k-2))), the event-form invoice minus one unit per excess role).
Frame-level core (`Host`, `leaves_le`, `leaves_le_kT`) is stated for abstract (A, B, beta) and instantiated on CallerThin's
1-host + 1-thin frame (`inst_*`).  Kernel only.
-/
import Nov15.CallerAsm
import Nov15.CallerThinDel
import Nov15.CallerHPQ

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerBridge
open Finset Matrix CallerSign

/-! ## a 2x2 block with nonzero determinant kills vectors supported on it -/
section blk
variable {K : Type*} [Field K] {ι : Type*} [Fintype ι] [DecidableEq ι]

theorem kblock_zero (G : Matrix ι ι K) (e : Fin 2 → ι) (hinj : Function.Injective e)
    (hdet : (G.submatrix e e).det ≠ 0) (v : ι → K) (hv : ∀ j, (∀ a, e a ≠ j) → v j = 0)
    (hz : ∀ a, (G *ᵥ v) (e a) = 0) : v = 0 := by
  have hsum : ∀ a, (G *ᵥ v) (e a) = ((G.submatrix e e) *ᵥ (v ∘ e)) a := by
    intro a
    simp only [Matrix.mulVec, dotProduct, Matrix.submatrix_apply, Function.comp_apply]
    rw [← Finset.sum_image (f := fun j => G (e a) j * v j) (s := (univ : Finset (Fin 2)))
      (g := e) (fun x _ y _ h => hinj h)]
    refine (Finset.sum_subset (Finset.subset_univ _) ?_).symm
    intro j _ hj
    have : ∀ b, e b ≠ j := fun b hb => hj (Finset.mem_image.2 ⟨b, Finset.mem_univ _, hb⟩)
    rw [hv j this, mul_zero]
  have h0 : (G.submatrix e e) *ᵥ (v ∘ e) = 0 := by
    funext a; rw [← hsum a]; exact hz a
  have h1 := Matrix.eq_zero_of_mulVec_eq_zero hdet h0
  funext j
  by_cases hj : ∃ a, e a = j
  · obtain ⟨a, rfl⟩ := hj
    exact congrFun h1 a
  · push_neg at hj
    exact hv j hj

end blk

/-! ## the frame-level host/thin data -/
section frame
variable {K : Type*} [Field K] {ι : Type*} [Fintype ι] [DecidableEq ι] {n k m : ℕ}

/-- `k` host slots (`pos s`), each with exactly two host columns `col s a`; every other column is a thin;
`mask` is the declared D-mask: the A/B host columns of stage `s` vanish on roles with `s ∉ mask r`;
`lambda_s /= -1` is `hlam` (the 2x2 K-block of slot `s` is nonsingular); the product is `-1`. -/
structure Host (A B : Matrix (Fin n) ι K) (β : ι → ℕ) (k m : ℕ) (mask : Fin n → Finset (Fin k)) where
  col : Fin k → Fin 2 → ι
  pos : Fin k → ℕ
  hβ : ∀ i, β i < m
  hP : sgProd A B β m = -1
  hpos : Function.Injective pos
  hposlt : ∀ s, pos s < m
  hcolβ : ∀ s a, β (col s a) = pos s
  hcolinj : Function.Injective (fun p : Fin k × Fin 2 => col p.1 p.2)
  hslot : ∀ s i, β i = pos s → ∃ a, i = col s a
  hw : ∀ t < m, Fintype.card {i // β i = t} ≤ 2
  hlam : ∀ s, ((sgK β (sgG A B)).submatrix (col s) (col s)).det ≠ 0
  hA : ∀ r s, s ∉ mask r → ∀ a, A r (col s a) = 0
  hB : ∀ r s, s ∉ mask r → ∀ a, B r (col s a) = 0

namespace Host
variable {A B : Matrix (Fin n) ι K} {β : ι → ℕ} {mask : Fin n → Finset (Fin k)}

/-- the `2k` host columns. -/
def hcols (H : Host A B β k m mask) : Finset ι := univ.image (fun p : Fin k × Fin 2 => H.col p.1 p.2)
/-- the thin columns: everything else. -/
def Th (H : Host A B β k m mask) : Finset ι := univ \ H.hcols

theorem hcols_card (H : Host A B β k m mask) : H.hcols.card = 2 * k := by
  unfold hcols
  rw [Finset.card_image_of_injective _ H.hcolinj]
  simp [mul_comm]

theorem two_k_le (H : Host A B β k m mask) : 2 * k ≤ Fintype.card ι := by
  rw [← H.hcols_card]; exact Finset.card_le_univ _

theorem th_card (H : Host A B β k m mask) : H.Th.card = Fintype.card ι - 2 * k := by
  unfold Th
  rw [Finset.card_sdiff_of_subset (Finset.subset_univ _), Finset.card_univ, H.hcols_card]

theorem notTh_iff (H : Host A B β k m mask) (i : ι) : i ∉ H.Th ↔ ∃ s a, i = H.col s a := by
  unfold Th hcols
  simp only [Finset.mem_sdiff, Finset.mem_univ, Finset.mem_image, true_and, not_not, Prod.exists]
  constructor
  · rintro ⟨s, a, h⟩; exact ⟨s, a, h.symm⟩
  · rintro ⟨s, a, h⟩; exact ⟨s, a, h.symm⟩

theorem col_inj (H : Host A B β k m mask) (s : Fin k) : Function.Injective (H.col s) := by
  intro a b h
  have := H.hcolinj (show (fun p : Fin k × Fin 2 => H.col p.1 p.2) (s, a) = (fun p : Fin k × Fin 2 => H.col p.1 p.2) (s, b) from h)
  exact (Prod.mk.inj this).2

theorem kinj (H : Host A B β k m mask) (s : Fin k) : CallerLeaf.KInj β (sgG A B) (H.pos s) := by
  intro v hv hz
  refine kblock_zero (sgK β (sgG A B)) (H.col s) (H.col_inj s) (H.hlam s) v ?_ (fun a => hz _ (H.hcolβ s a))
  intro j hj
  refine hv j (fun hb => ?_)
  obtain ⟨a, ha⟩ := H.hslot s j hb
  exact hj a ha.symm

theorem knondeg (H : Host A B β k m mask) (s : Fin k) : CallerThin.KNondeg β (sgG A B) (H.pos s) := by
  intro v hv hz
  refine kblock_zero (sgK β (sgG A B)) (H.col s) (H.col_inj s) (H.hlam s) v ?_ (fun a => hz _ (H.hcolβ s a))
  intro j hj
  refine hv j (fun hb => ?_)
  obtain ⟨a, ha⟩ := H.hslot s j hb
  exact hj a ha.symm

/-- off the slot of a role of mask `{s0}`, a non-thin column is a column of another stage, where the role vanishes. -/
theorem leaf_vanish (H : Host A B β k m mask) (r : Fin n) (s0 : Fin k) (hr : mask r = {s0}) (i : ι)
    (hT : i ∉ H.Th) (hb : β i ≠ H.pos s0) : A r i = 0 ∧ B r i = 0 := by
  obtain ⟨s, a, rfl⟩ := (H.notTh_iff i).1 hT
  have hs : s ≠ s0 := by
    intro h; apply hb; rw [H.hcolβ, h]
  have hn : s ∉ mask r := by rw [hr]; simpa using hs
  exact ⟨H.hA r s hn a, H.hB r s hn a⟩

/-- LC at frame level: #leaves <= k + T. -/
theorem leaves_le (H : Host A B β k m mask) (h2 : (2 : K) ≠ 0) :
    (univ.filter fun r => (mask r).card = 1).card ≤ k + (Fintype.card ι - 2 * k) := by
  have hmain := CallerLeaf.leaf_channel_thin (Lf := univ.filter fun r => (mask r).card = 1) (A := A) (B := B)
    H.hβ H.Th (univ.image H.pos) ?_ ?_ h2 H.hP ?_ ?_ H.hw
  · rw [Finset.card_image_of_injective _ H.hpos, H.th_card, Finset.card_univ, Fintype.card_fin] at hmain
    exact hmain
  · intro t ht
    obtain ⟨s, _, rfl⟩ := Finset.mem_image.1 ht
    exact Finset.mem_range.2 (H.hposlt s)
  · intro i hi
    obtain ⟨s, a, rfl⟩ := (H.notTh_iff i).1 hi
    exact Finset.mem_image.2 ⟨s, Finset.mem_univ _, (H.hcolβ s a).symm⟩
  · intro r hr
    obtain ⟨s0, hs0⟩ := Finset.card_eq_one.1 (Finset.mem_filter.1 hr).2
    exact ⟨H.pos s0, fun i hT hb => H.leaf_vanish r s0 hs0 i hT hb⟩
  · intro t ht
    obtain ⟨s, _, rfl⟩ := Finset.mem_image.1 ht
    refine CallerLeaf.kinj_host H.Th A B β (H.pos s) (fun i hi => ?_) (H.kinj s)
    obtain ⟨a, ha⟩ := H.hslot s i hi
    exact (H.notTh_iff i).2 ⟨s, a, ha⟩

/-- LEAF-RANK at one stage: #leaves of that stage <= T. -/
theorem leaf_stage (H : Host A B β k m mask) (h2 : (2 : K) ≠ 0) (s : Fin k) :
    (univ.filter fun r => mask r = {s}).card ≤ Fintype.card ι - 2 * k := by
  have h := CallerThin.leaf_rank A B β m (H.pos s) (H.hposlt s) h2 H.hP (H.knondeg s)
    (univ.filter fun r => mask r = {s}) H.Th
    (fun r hr i hb hT => (H.leaf_vanish r s (Finset.mem_filter.1 hr).2 i hT hb).2)
  rwa [H.th_card] at h

/-- LEAF at frame level: #leaves <= k T. -/
theorem leaves_le_kT (H : Host A B β k m mask) (h2 : (2 : K) ≠ 0) :
    (univ.filter fun r => (mask r).card = 1).card ≤ k * (Fintype.card ι - 2 * k) := by
  calc (univ.filter fun r => (mask r).card = 1).card
      ≤ (univ.biUnion fun s : Fin k => univ.filter fun r => mask r = {s}).card := by
        apply Finset.card_le_card
        intro r hr
        obtain ⟨s, hs⟩ := Finset.card_eq_one.1 (Finset.mem_filter.1 hr).2
        exact Finset.mem_biUnion.2 ⟨s, Finset.mem_univ _, Finset.mem_filter.2 ⟨Finset.mem_univ _, hs⟩⟩
    _ ≤ ∑ s : Fin k, (univ.filter fun r => mask r = {s}).card := Finset.card_biUnion_le
    _ ≤ ∑ s : Fin k, (Fintype.card ι - 2 * k) := Finset.sum_le_sum fun s _ => H.leaf_stage h2 s
    _ = k * (Fintype.card ι - 2 * k) := by simp

end Host
end frame

/-! ## non-vacuity of the frame-level bridge: CallerThin's 1 host (columns 0,1) + 1 thin (column 2), n = 1, one leaf -/
section inst

def inst_mask : Fin 1 → Finset (Fin 1) := fun _ => {0}

def instHost : Host (CallerThin.A1) (CallerThin.B1) CallerThin.beta1 1 2 inst_mask where
  col := fun _ a => ![0, 1] a
  pos := fun _ => 0
  hβ := fun i => by fin_cases i <;> simp [CallerThin.beta1]
  hP := CallerThin.prod1
  hpos := fun a b _ => Subsingleton.elim a b
  hposlt := fun _ => by norm_num
  hcolβ := fun s a => by fin_cases a <;> simp [CallerThin.beta1]
  hcolinj := by
    intro p q h
    obtain ⟨s, a⟩ := p; obtain ⟨s', b⟩ := q
    have hs : s = s' := Subsingleton.elim _ _
    subst hs
    have : (![0, 1] : Fin 2 → Fin 3) a = ![0, 1] b := h
    fin_cases a <;> fin_cases b <;> simp_all
  hslot := fun s i hi => by
    fin_cases i
    · exact ⟨0, rfl⟩
    · exact ⟨1, rfl⟩
    · simp [CallerThin.beta1] at hi
  hw := fun t ht => by
    interval_cases t
    · decide +kernel
    · decide +kernel
  hlam := fun s => by
    rw [Matrix.det_fin_two]
    simp [sgK, sgG, sgDiag, sgUp, sgLow, CallerThin.A1, CallerThin.B1, CallerThin.beta1, Matrix.mul_apply,
      one_apply, Matrix.transpose_apply]
    norm_num
  hA := fun r s hs a => absurd (Subsingleton.elim s 0) (by simpa [inst_mask] using hs)
  hB := fun r s hs a => absurd (Subsingleton.elim s 0) (by simpa [inst_mask] using hs)

/-- the bridge instantiated: the leaf (|mask| = 1) satisfies LC (<= k + T = 2) and LEAF (<= k T = 1), with n + 2 = |iota| = 3. -/
theorem inst_leaves : (univ.filter fun r : Fin 1 => (inst_mask r).card = 1).card ≤ 1 + (Fintype.card (Fin 3) - 2 * 1) ∧
    (univ.filter fun r : Fin 1 => (inst_mask r).card = 1).card ≤ 1 * (Fintype.card (Fin 3) - 2 * 1) :=
  ⟨instHost.leaves_le (by norm_num), instHost.leaves_le_kT (by norm_num)⟩

theorem inst_leaves_val : (univ.filter fun r : Fin 1 => (inst_mask r).card = 1).card = 1 := by
  decide +kernel

theorem inst_count : 1 + 2 = Fintype.card (Fin 3) := by simp

end inst

/-! ## the word-level bridge -/
section word
open CallerWord CallerEv CallerAsm CallerHP
variable {n k : ℕ} {w : CWord n k}

theorem iota_slot_card (w : CWord n k) (t : ℕ) : Fintype.card {i : Iota w // βw w i = t} ≤ 2 := by
  let f : {i : Iota w // βw w i = t} → Fin 2 := fun i => i.1.1.2
  have hf : Function.Injective f := by
    intro i j h
    have hi : i.1.1.1.val = t := i.2
    have hj : j.1.1.1.val = t := j.2
    have h1 : i.1.1.1 = j.1.1.1 := Fin.ext (hi.trans hj.symm)
    apply Subtype.ext; apply Subtype.ext; exact Prod.ext h1 h
  have := Fintype.card_le_of_injective f hf
  simpa using this

/-- the host/thin split of a legal type-B word. -/
noncomputable def hostOf (hL : Legal w) (J : JB w) (hodd : ∀ r, w.ex r % 2 = 1)
    (hlam : ∀ s, IsUnit ((sgK (βw w) (sgG (Aw w Complex.I) (Bw w Complex.I))).submatrix (J.col s) (J.col s)).det) :
    Host (Aw w Complex.I) (Bw w Complex.I) (βw w) k w.evs.length w.mask where
  col := J.col
  pos := J.pos
  hβ := beta_lt w
  hP := (legal_frame w hL hodd).1
  hpos := J.mono.injective
  hposlt := fun s => by have := J.lt s; omega
  hcolβ := fun s a => J.beta_col s a
  hcolinj := by
    intro p q h
    obtain ⟨s, a⟩ := p; obtain ⟨s', b⟩ := q
    have hb : J.pos s = J.pos s' := by simpa [JB.col, βw] using congrArg (fun i => βw w i) h
    have hs : s = s' := J.mono.injective hb
    subst hs
    have ha : a = b := by simpa [JB.col] using congrArg (fun i : Iota w => i.1.2) h
    rw [ha]
  hslot := by
    intro s i hi
    obtain ⟨⟨j, c⟩, hnz⟩ := i
    have hj : j = ⟨J.pos s, by have := J.lt s; omega⟩ := Fin.ext (by simpa [βw] using hi)
    exact ⟨c, Subtype.ext (Prod.ext hj rfl)⟩
  hw := fun t _ => iota_slot_card w t
  hlam := fun s => (hlam s).ne_zero
  hA := fun r s hs a => word_hah hL J r s hs a
  hB := fun r s hs a => word_hbh hL J r s hs a


/-! ### DEEP: two singleton pieces on non-leaf roles at every stage -/
section deep
variable {R E : Type*} [Fintype R] [DecidableEq R] [Fintype E] [DecidableEq E]

theorem deep_stage (M : R → Finset (Fin k)) (S : E → Finset (Fin k)) (Pm : Match M S) (s t : Fin k) (hst : s ≠ t)
    (hp : 2 + (gSet S s t 2).card ≤ (wSet M s t 2).card) :
    2 ≤ (univ.filter fun r => s ∈ M r ∧ 2 ≤ (M r).card ∧ (S (Pm.ev r s)).card = 1).card := by
  set Y := univ.filter fun r => s ∈ M r ∧ 2 ≤ (S (Pm.ev r s)).card with hY
  set N := univ.filter fun r => s ∈ M r ∧ 2 ≤ (M r).card ∧ (S (Pm.ev r s)).card = 1 with hN
  have h1 : wSet M s t 2 ⊆ Y ∪ N := by
    intro r hr
    simp only [wSet, mem_filter, mem_univ, true_and] at hr
    obtain ⟨hs, hr2⟩ := hr
    have hM2 : 2 ≤ (M r).card := by
      rcases hr2 with h | h
      · exact h
      · have hsub : ({s, t} : Finset (Fin k)) ⊆ M r := by
          intro x hx
          simp only [mem_insert, mem_singleton] at hx
          rcases hx with rfl | rfl <;> assumption
        have := card_le_card hsub
        rwa [card_pair hst] at this
    have hc1 : 1 ≤ (S (Pm.ev r s)).card := card_pos.2 ⟨s, Pm.mem r s hs⟩
    rw [mem_union]
    by_cases h2 : 2 ≤ (S (Pm.ev r s)).card
    · left; simp only [hY, mem_filter, mem_univ, true_and]; exact ⟨hs, h2⟩
    · right; simp only [hN, mem_filter, mem_univ, true_and]; exact ⟨hs, hM2, by omega⟩
  have h2 : Y.card ≤ (gSet S s t 2).card := by
    apply card_le_card_of_injOn (fun r => Pm.ev r s)
    · intro r hr
      have hr' : r ∈ Y := hr
      simp only [hY, mem_filter, mem_univ, true_and] at hr'
      show Pm.ev r s ∈ gSet S s t 2
      unfold gSet
      rw [mem_filter]
      exact ⟨mem_univ _, Pm.mem r s hr'.1, hr'.2, Or.inl hr'.2⟩
    · intro r hr r' hr' h
      have h1 : r ∈ Y := hr
      have h2 : r' ∈ Y := hr'
      simp only [hY, mem_filter, mem_univ, true_and] at h1 h2
      exact Pm.inj s r r' h1.1 h2.1 h
  have h3 := card_le_card h1
  have h4 := card_union_le Y N
  omega

theorem mains_real (M : R → Finset (Fin k)) (S : E → Finset (Fin k)) (Pm : Match M S)
    (hd : ∀ s : Fin k, 2 ≤ (univ.filter fun r => s ∈ M r ∧ 2 ≤ (M r).card ∧ (S (Pm.ev r s)).card = 1).card) :
    2 * (k : ℝ) ≤ ∑ r, (if 2 ≤ (M r).card then mainCnt (M r) (fun s => decide ((S (Pm.ev r s)).card = 1)) else 0) := by
  have e1 : ∀ r, (if 2 ≤ (M r).card then mainCnt (M r) (fun s => decide ((S (Pm.ev r s)).card = 1)) else 0)
      = ∑ s ∈ M r, (if 2 ≤ (M r).card ∧ (S (Pm.ev r s)).card = 1 then (1 : ℝ) else 0) := by
    intro r
    by_cases h : 2 ≤ (M r).card
    · simp only [h, if_true, true_and, mainCnt, decide_eq_true_eq]
    · simp [h]
  rw [Finset.sum_congr rfl fun r _ => e1 r]
  have e2 : ∑ r, ∑ s ∈ M r, (if 2 ≤ (M r).card ∧ (S (Pm.ev r s)).card = 1 then (1 : ℝ) else 0)
      = ∑ s : Fin k, ∑ r ∈ univ.filter (fun r => s ∈ M r),
          (if 2 ≤ (M r).card ∧ (S (Pm.ev r s)).card = 1 then (1 : ℝ) else 0) := by
    rw [Finset.sum_comm' (t' := (univ : Finset (Fin k))) (s' := fun s => univ.filter (fun r => s ∈ M r))]
    intro r s; simp
  rw [e2]
  calc 2 * (k : ℝ) = ∑ s : Fin k, (2 : ℝ) := by simp [mul_comm]
    _ ≤ _ := by
      refine Finset.sum_le_sum fun s _ => ?_
      rw [Finset.sum_boole, Finset.filter_filter]
      exact_mod_cast hd s

end deep

/-! ### RC2_l for l >= 3, real form -/
theorem rc2_row_real {K : Type*} [Field K] {R E : Type*} [Fintype R] [DecidableEq R] [Fintype E] [DecidableEq E]
    (hk : 1 ≤ k) (M : R → Finset (Fin k)) (bh ah : R → Fin k → Fin 2 → K) (S : E → Finset (Fin k))
    (hbh : ∀ r s, s ∉ M r → ∀ a, bh r s a = 0) (hah : ∀ r s, s ∉ M r → ∀ a, ah r s a = 0)
    (P : EvData M bh S) (hG : ∀ s t, s ≠ t → IsUnit (gBlk bh ah s t).det) (Pm : Match M S) (l : ℕ) (hl : 2 ≤ l) :
    2 * (k : ℝ) * ((k : ℝ) - 1) ≤ ∑ r, rowS k (M r) (fun s => (S (Pm.ev r s)).card) l := by
  have h := rc_row_nat M bh ah S hbh hah P hG Pm l hl
  have hc2 : ((2 * (k * (k - 1)) : ℕ) : ℝ) ≤ ((∑ r, ∑ s ∈ M r,
    (if l ≤ (M r).card then (if (S (Pm.ev r s)).card < l then k - (S (Pm.ev r s)).card else 0)
      else (M r).card - (S (Pm.ev r s)).card) : ℕ) : ℝ) := by exact_mod_cast h
  rw [Nat.cast_sum] at hc2
  have e1 : ∀ r, (((∑ s ∈ M r,
    (if l ≤ (M r).card then (if (S (Pm.ev r s)).card < l then k - (S (Pm.ev r s)).card else 0)
      else (M r).card - (S (Pm.ev r s)).card) : ℕ)) : ℝ)
      = rowS k (M r) (fun s => (S (Pm.ev r s)).card) l := by
    intro r
    unfold rowS
    rw [Nat.cast_sum]
    refine Finset.sum_congr rfl fun s hs => ?_
    have hsub := Finset.card_le_card (Pm.sub r s hs)
    have hDk : (M r).card ≤ k := by simpa using Finset.card_le_univ (M r)
    by_cases h1 : l ≤ (M r).card
    · by_cases h2 : (S (Pm.ev r s)).card < l
      · simp only [h1, h2, if_true]
        rw [Nat.cast_sub (by omega)]
      · simp [h1, h2]
    · simp only [h1, if_false]
      rw [Nat.cast_sub hsub]
  simp_rw [e1] at hc2
  push_cast [Nat.cast_sub hk] at hc2
  linarith

/-! ### the Cfg and the headline -/

/-- the event-form caller value with the thin excess: `104/k (invoice - (n - (2k-2)))` (each excess role costs one unit). -/
noncomputable def cHatQ (w : CWord n k) : ℝ :=
  104 / (k : ℝ) * (invoice σ0 w.mask (evS w) - ((n : ℝ) - (2 * k - 2)))

/-- consistency with the Q = 0 value: at `n + 2 = 2k` the excess term vanishes and `cHatQ = cHat` (CallerAsm). -/
theorem cHatQ_q0 (h : n + 2 = 2 * k) : cHatQ w = cHat w := by
  have : (n : ℝ) = 2 * k - 2 := by
    have : ((n + 2 : ℕ) : ℝ) = ((2 * k : ℕ) : ℝ) := by rw [h]
    push_cast at this; linarith
  unfold cHatQ cHat
  rw [this]; ring

/-- every field of `LawQ` is derived from a legal type-B word (no frame data is assumed in `LawQ` any more). -/
theorem word_lawQ (hL : Legal w) (J : JB w) (hodd : ∀ r, w.ex r % 2 = 1) (hk : 2 ≤ k)
    (hn : n + 2 = Fintype.card (Iota w))
    (hlam : ∀ s, IsUnit ((sgK (βw w) (sgG (Aw w Complex.I) (Bw w Complex.I))).submatrix (J.col s) (J.col s)).det)
    (hdeg1 : ∀ r, 1 ≤ (w.mask r).card) :
    ∃ C : Cfg k, C.LawQ ∧ C.valQ = cHatQ w := by
  have hkpos : 0 < k := by omega
  have hG := word_hG hL J.sch hodd hn hlam
  have H := hostOf hL J hodd hlam
  let s0 : Fin k := ⟨0, hkpos⟩
  let e₀ : Fin w.evs.length := ⟨J.pos s0, by have := J.lt s0; omega⟩
  obtain ⟨Pm⟩ := exists_match w.mask (fun r s a => Bw w Complex.I r (J.sch.col s a)) (evS w)
    (wordEv hL J.sch) e₀ (word_count hL)
  have hex : ∀ s : Fin k, ∃ t : Fin k, s ≠ t := by
    intro s
    by_cases h : s.val = 0
    · exact ⟨⟨1, by omega⟩, fun e => by have := congrArg Fin.val e; simp at this; omega⟩
    · exact ⟨⟨0, hkpos⟩, fun e => by have := congrArg Fin.val e; simp at this; omega⟩
  have hdeep : ∀ s : Fin k, 2 ≤ (univ.filter fun r => s ∈ w.mask r ∧ 2 ≤ (w.mask r).card ∧
      (evS w (Pm.ev r s)).card = 1).card := by
    intro s
    obtain ⟨t, hst⟩ := hex s
    exact deep_stage w.mask (evS w) Pm s t hst (word_rc2_pair hL J.sch hodd hn hlam s t hst 2)
  -- the leaf laws
  have hle := H.leaves_le (by norm_num : (2 : ℂ) ≠ 0)
  have hkT := H.leaves_le_kT (by norm_num : (2 : ℂ) ≠ 0)
  have h2k := H.two_k_le
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
      exact rc2_row_real hkpos w.mask (fun r s a => Bw w Complex.I r (J.sch.col s a))
        (fun r s a => Aw w Complex.I r (J.sch.col s a)) (evS w)
        (fun r s hs a => J.sch.hbh hL r s hs a) (fun r s hs a => J.sch.hah hL r s hs a) (wordEv hL J.sch) hG Pm l (by omega)
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

/-- HEADLINE.  Every legal type-B caller word with odd targets, `lambda /= -1` on every host slot, tight role count
`n + 2 = |Iota|` (`T = Q`, `e = 0`) and every role of degree `>= 1`, with `k >= 77` stages, has
`c^(.99) = cHatQ w < 128.891`.  No `LawQ` field is assumed. -/
theorem word_hpq (hL : Legal w) (J : JB w) (hodd : ∀ r, w.ex r % 2 = 1) (hk : 77 ≤ k)
    (hn : n + 2 = Fintype.card (Iota w))
    (hlam : ∀ s, IsUnit ((sgK (βw w) (sgG (Aw w Complex.I) (Bw w Complex.I))).submatrix (J.col s) (J.col s)).det)
    (hdeg1 : ∀ r, 1 ≤ (w.mask r).card) :
    cHatQ w < 128891 / 1000 := by
  obtain ⟨C, hC, hv⟩ := word_lawQ hL J hodd (by omega) hn hlam hdeg1
  rw [← hv]
  exact valQ_lt hk C hC

end word
end CallerBridge

#print axioms CallerBridge.kblock_zero
#print axioms CallerBridge.Host.leaves_le
#print axioms CallerBridge.Host.leaves_le_kT
#print axioms CallerBridge.inst_leaves
#print axioms CallerBridge.deep_stage
#print axioms CallerBridge.mains_real
#print axioms CallerBridge.rc2_row_real
#print axioms CallerBridge.word_lawQ
#print axioms CallerBridge.cHatQ_q0
#print axioms CallerBridge.word_hpq
