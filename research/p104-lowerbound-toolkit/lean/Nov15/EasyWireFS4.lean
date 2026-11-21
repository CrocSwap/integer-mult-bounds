/-
EasyWireFS4 (lane EASYWIRE, Nov 20).  H_FS4 and H_id DERIVED from the decoder identity (8 rows).
FS item 4 ("W^T V = 2 I per frame, hence V W^T = 2 I, hence V W^T = 0 mod 2"):
  decoder identity  sum_{k in J} w_k(t) v_k(s) Q_ts = 2 [t = s]  (E8 form, as in DataId.p104_linear_cost_ge_E8),  |J| = 8.
On an orthogonal 8-frame T all Q_ts = 1, so (w_k(t))_{t in T,k in J} (v_k(s))_{k in J,s in T} = 2 I_T; T and J are both 8-element,
so the product the other way round is 2 I_J too:  sum_{t in T} v_k(t) w_l(t) = 2 [k = l]  (even).
Hence for every pair of rows k, l: the indicator of (odd support of w_l) ∩ (odd support of v_k) lies in F^perp.
Wrappers:  `fs4_of_decoder` (H_FS4 discharged), `all_or_nothing_dec` (all_or_nothing_8row with H_FS4 gone: A, B the odd supports,
D, S the mod-4 supports so hA, hB are automatic), `hid_of_decoder` (LemmaT.H_id for Odd t s := Q_ts = 1, on every port).
Kernel only.  Non-vacuity: the honest E8 decoder (P104.wI, vI, J = Fin 8).
-/
import Nov15.DataIdB
import Nov15.BlockLaw
import Nov15.LemmaT

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace EasyWire
open Matrix Finset FrameCert DataId

/-- odd support of an integer vector (cast to F2 is 1) -/
def oddSupp (z : Fin 104 → ℤ) : Finset (Fin 104) := univ.filter fun t => ((z t : ℤ) : ZMod 2) = 1

/-- mod-4 support -/
def supp4 (z : Fin 104 → ℤ) : Finset (Fin 104) := univ.filter fun t => ¬ ((4 : ℤ) ∣ z t)

theorem ind_oddSupp_inter (x y : Fin 104 → ℤ) (i : Fin 104) :
    ind (oddSupp x ∩ oddSupp y) i = ((x i * y i : ℤ) : ZMod 2) := by
  unfold ind oddSupp
  simp only [mem_inter, mem_filter, mem_univ, true_and, Int.cast_mul]
  generalize ((x i : ℤ) : ZMod 2) = a
  generalize ((y i : ℤ) : ZMod 2) = b
  revert a b; decide

theorem oddSupp_sub_supp4 (x : Fin 104 → ℤ) : oddSupp x ⊆ supp4 x := by
  intro t ht
  simp only [oddSupp, supp4, mem_filter, mem_univ, true_and] at ht ⊢
  intro h4
  have h2 : (2 : ℤ) ∣ x t := dvd_trans (by norm_num) h4
  have := (ZMod.intCast_zmod_eq_zero_iff_dvd (x t) 2).2 (by exact_mod_cast h2)
  rw [ht] at this
  exact one_ne_zero this

/-! ### the algebra on one frame -/
theorem frame_pair_sum {κ : Type*} [DecidableEq κ] (J : Finset κ) (T : Finset (Fin 104)) (hJT : J.card = T.card)
    (w v : κ → Fin 104 → ℤ)
    (hQ : ∀ t ∈ T, ∀ s ∈ T, ∑ k ∈ J, w k t * v k s = if t = s then 2 else 0)
    (k l : κ) (hk : k ∈ J) (hl : l ∈ J) :
    ∑ t ∈ T, v k t * w l t = if k = l then 2 else 0 := by
  classical
  let M1 : Matrix T J ℚ := Matrix.of fun t k => (w k.1 t.1 : ℚ)
  let M2 : Matrix J T ℚ := Matrix.of fun k s => (v k.1 s.1 : ℚ)
  have h12 : M1 * ((1 / 2 : ℚ) • M2) = 1 := by
    ext t s
    simp only [Matrix.mul_apply, Matrix.smul_apply, M1, M2, Matrix.of_apply, smul_eq_mul, Matrix.one_apply]
    have h := hQ t.1 t.2 s.1 s.2
    have h' : ∑ k : J, (w k.1 t.1 : ℚ) * (v k.1 s.1 : ℚ) = if t.1 = s.1 then 2 else 0 := by
      rw [Finset.sum_coe_sort J (fun k => (w k t.1 : ℚ) * (v k s.1 : ℚ))]
      have h2 : ((∑ k ∈ J, w k t.1 * v k s.1 : ℤ) : ℚ) = ((if t.1 = s.1 then 2 else 0 : ℤ) : ℚ) := by rw [h]
      push_cast at h2
      rw [h2]
    calc ∑ k : J, (w k.1 t.1 : ℚ) * (1 / 2 * (v k.1 s.1 : ℚ))
        = (1 / 2) * ∑ k : J, (w k.1 t.1 : ℚ) * (v k.1 s.1 : ℚ) := by
          rw [Finset.mul_sum]; exact Finset.sum_congr rfl fun k _ => by ring
      _ = _ := by
          rw [h']
          by_cases hts : t = s
          · subst hts; simp
          · have : t.1 ≠ s.1 := fun e => hts (Subtype.ext e)
            simp [hts, this]
  have hc : Fintype.card T = Fintype.card J := by simp [hJT]
  have h21 : ((1 / 2 : ℚ) • M2) * M1 = 1 := (Matrix.mul_eq_one_comm_of_equiv (Fintype.card_eq.mp hc).some).1 h12
  have e := congrFun (congrFun h21 ⟨k, hk⟩) ⟨l, hl⟩
  simp only [Matrix.mul_apply, Matrix.smul_apply, M1, M2, Matrix.of_apply, smul_eq_mul, Matrix.one_apply] at e
  have e2 : ∑ t : T, (v k t.1 : ℚ) * (w l t.1 : ℚ) = if k = l then 2 else 0 := by
    have : ∑ t : T, (1 / 2 : ℚ) * (v k t.1 : ℚ) * (w l t.1 : ℚ) = (1 / 2 : ℚ) * ∑ t : T, (v k t.1 : ℚ) * (w l t.1 : ℚ) := by
      rw [Finset.mul_sum]; exact Finset.sum_congr rfl fun t _ => by ring
    rw [this] at e
    by_cases hkl : k = l
    · subst hkl; simp at e ⊢; try linarith
    · have : (⟨k, hk⟩ : J) ≠ ⟨l, hl⟩ := fun h => hkl (congrArg Subtype.val h)
      simp [this, hkl] at e ⊢
      exact e
  rw [Finset.sum_coe_sort T (fun t => (v k t : ℚ) * (w l t : ℚ))] at e2
  have : ((∑ t ∈ T, v k t * w l t : ℤ) : ℚ) = ((if k = l then 2 else 0 : ℤ) : ℚ) := by
    push_cast; rw [e2]
  exact_mod_cast this

/-! ### frames as finsets -/
def frameT (l : List Nat) : Finset (Fin 104) := univ.filter fun i => l.contains i.val = true

theorem frameT_card (l : List Nat) (h : l.length = 8 ∧ l.Sublist (List.range 104) ∧ True) : (frameT l).card = 8 := by
  have hnd : l.Nodup := h.2.1.nodup (List.nodup_range)
  have hsub : ∀ x ∈ l, x < 104 := fun x hx => List.mem_range.1 (h.2.1.subset hx)
  have : (frameT l).map Fin.valEmbedding = l.toFinset := by
    ext x
    simp only [mem_map, frameT, mem_filter, mem_univ, true_and, List.contains_iff_mem, Fin.valEmbedding_apply,
      List.mem_toFinset]
    constructor
    · rintro ⟨i, hi, rfl⟩; exact hi
    · intro hx; exact ⟨⟨x, hsub x hx⟩, hx, rfl⟩
  rw [← Finset.card_map Fin.valEmbedding, this, List.toFinset_card_of_nodup hnd, h.1]

theorem dot_comm' (x y : List Int) : DataId.dot x y = DataId.dot y x := by
  unfold DataId.dot
  rw [List.zipWith_comm]
  simp [mul_comm]

theorem frameT_Q (l : List Nat)
    (h : l.Pairwise (fun a b => DataId.dot (DataId.rootAt a) (DataId.rootAt b) = 0)) :
    ∀ t ∈ frameT l, ∀ s ∈ frameT l, Qroot t s = 1 := by
  intro t ht s hs
  by_cases hts : t = s
  · subst hts
    rw [← Qlab_eq_Qroot]; exact P104.Qlab_diag t
  · simp only [frameT, mem_filter, mem_univ, true_and, List.contains_iff_mem] at ht hs
    haveI : Std.Symm (fun a b => DataId.dot (DataId.rootAt a) (DataId.rootAt b) = 0) :=
      ⟨fun a b hab => by simpa [dot_comm'] using hab⟩
    have := h.forall ht hs (fun e => hts (Fin.ext e))
    simp [Qroot, QrootN, this]

/-- H_FS4, derived: for every pair of rows k, l of an 8-row decoder, 1_{Abar_l ∩ Bbar_k} ∈ F^perp. -/
theorem fs4_of_decoder {κ : Type*} [DecidableEq κ] {J : Finset κ} (hJ : J.card = 8) {w v : κ → Fin 104 → ℤ}
    (hdec : ∀ t s, ∑ k ∈ J, w k t * v k s * Qroot t s = if t = s then 2 else 0) {k l : κ}
    (hk : k ∈ J) (hl : l ∈ J) :
    ind (oddSupp (w l) ∩ oddSupp (v k)) ∈ Fperp := by
  rw [Fperp_iff_orth]
  intro lst hlst
  have hc := frameT_card lst ⟨hlst.1, hlst.2.1, trivial⟩
  have hQ := frameT_Q lst hlst.2.2
  have hsum := frame_pair_sum J (frameT lst) (by rw [hJ, hc]) w v
    (fun t ht s hs => by have := hdec t s; simpa [hQ t ht s hs] using this) k l hk hl
  have e1 : ∑ i : Fin 104, (if lst.contains i.val then ind (oddSupp (w l) ∩ oddSupp (v k)) i else 0)
      = ∑ i ∈ frameT lst, ind (oddSupp (w l) ∩ oddSupp (v k)) i := by
    unfold frameT
    rw [Finset.sum_filter]
  rw [e1]
  simp only [ind_oddSupp_inter]
  rw [← Int.cast_sum]
  have : ∑ i ∈ frameT lst, w l i * v k i = if k = l then 2 else 0 := by
    rw [← hsum]; exact Finset.sum_congr rfl fun i _ => mul_comm _ _
  rw [this]
  split_ifs <;> decide

/-- ALL-OR-NOTHING for an 8-row decoder with H_FS4 (and hA, hB) discharged: A = odd support of row l of w, B = odd support
of row k of v, D, S the mod-4 supports; the dimension-7 / frame-blocking hypotheses on the span of the labels of D stay. -/
theorem all_or_nothing_dec {κ : Type*} [DecidableEq κ] {J : Finset κ} (hJ : J.card = 8) {w v : κ → Fin 104 → ℤ}
    (hdec : ∀ t s, ∑ k ∈ J, w k t * v k s * Qroot t s = if t = s then 2 else 0) {k l : κ}
    (hk : k ∈ J) (hl : l ∈ J)
    (h7 : Module.finrank (ZMod 2) (Submodule.span (ZMod 2) (BlockLaw.lab '' ((supp4 (w l) : Finset (Fin 104)) : Set (Fin 104)))) = 7)
    (hblock : BlockLaw.SemBlocking (Submodule.span (ZMod 2) (BlockLaw.lab '' ((supp4 (w l) : Finset (Fin 104)) : Set (Fin 104))))) :
    oddSupp (w l) ∩ oddSupp (v k) = ∅ ∨
      (oddSupp (w l) = BlockLaw.Lam (Submodule.span (ZMod 2) (BlockLaw.lab '' ((supp4 (w l) : Finset (Fin 104)) : Set (Fin 104)))) ∧
       BlockLaw.Lam (Submodule.span (ZMod 2) (BlockLaw.lab '' ((supp4 (w l) : Finset (Fin 104)) : Set (Fin 104)))) ⊆ oddSupp (v k) ∧
       Submodule.span (ZMod 2) (BlockLaw.lab '' ((supp4 (w l) : Finset (Fin 104)) : Set (Fin 104))) ≤
         Submodule.span (ZMod 2) (BlockLaw.lab '' ((supp4 (v k) : Finset (Fin 104)) : Set (Fin 104)))) :=
  BlockLaw.all_or_nothing_8row (supp4 (w l)) (supp4 (v k)) (oddSupp (w l)) (oddSupp (v k)) h7 hblock
    (oddSupp_sub_supp4 _) (oddSupp_sub_supp4 _) (fs4_of_decoder hJ hdec hk hl)

/-! ### H_id of Lemma T -/
theorem hid_of_decoder {κ : Type*} [DecidableEq κ] {J : Finset κ} {w v : κ → Fin 104 → ℤ}
    (hdec : ∀ t s, ∑ k ∈ J, w k t * v k s * Qroot t s = if t = s then 2 else 0) :
    ∀ t s : Fin 104, Qroot t s = 1 →
      ∑ k : J, ((w k.1 t : ℤ) : ZMod 4) * ((v k.1 s : ℤ) : ZMod 4) = if t = s then 2 else 0 := by
  intro t s hq
  have h := hdec t s
  simp only [hq, mul_one] at h
  rw [Finset.sum_coe_sort J (fun k => ((w k t : ℤ) : ZMod 4) * ((v k s : ℤ) : ZMod 4))]
  have := congrArg (fun z : ℤ => (z : ZMod 4)) h
  simp only [Int.cast_sum, Int.cast_mul] at this
  rw [this]
  split_ifs <;> simp

/-- Lemma T's `Hyp.H_id` with `Odd t s := (Q_ts = 1)` on every port (the other three fields of `Hyp` are row-structure data). -/
theorem hid_hyp {κ : Type*} [DecidableEq κ] {J : Finset κ} {w v : κ → Fin 104 → ℤ}
    (hdec : ∀ t s, ∑ k ∈ J, w k t * v k s * Qroot t s = if t = s then 2 else 0) :
    ∀ t ∈ (Set.univ : Set (Fin 104)), ∀ s ∈ (Set.univ : Set (Fin 104)), (fun t s => Qroot t s = 1) t s →
      ∑ k : J, ((w k.1 t : ℤ) : ZMod 4) * ((v k.1 s : ℤ) : ZMod 4) = if t = s then 2 else 0 :=
  fun t _ s _ hq => hid_of_decoder hdec t s hq

/-! ### non-vacuity: the honest E8 decoder -/
theorem hdec_E8 : ∀ t s : Fin 104, ∑ k ∈ (Finset.univ : Finset (Fin 8)), P104.wI k t * P104.vI k s * Qroot t s
    = if t = s then 2 else 0 := by
  intro t s; rw [← Qlab_funext]; exact P104.hdec_I t s

theorem fs4_nonvac (k l : Fin 8) :
    ind (oddSupp (P104.wI l) ∩ oddSupp (P104.vI k)) ∈ Fperp :=
  fs4_of_decoder (J := Finset.univ) (by simp) hdec_E8 (Finset.mem_univ k) (Finset.mem_univ l)

theorem hid_nonvac : ∀ t s : Fin 104, Qroot t s = 1 →
    ∑ k : (Finset.univ : Finset (Fin 8)), ((P104.wI k.1 t : ℤ) : ZMod 4) * ((P104.vI k.1 s : ℤ) : ZMod 4)
      = if t = s then 2 else 0 :=
  hid_of_decoder hdec_E8

end EasyWire

#print axioms EasyWire.frame_pair_sum
#print axioms EasyWire.fs4_of_decoder
#print axioms EasyWire.all_or_nothing_dec
#print axioms EasyWire.hid_of_decoder
#print axioms EasyWire.fs4_nonvac
#print axioms EasyWire.hid_nonvac
