/-
UniInhabitWs4Fold (lane UNI-INHABIT, Nov 19).  The fold of the CONCRETE tWs4 trace pins the UNI-L4 tables:
`foldsWs4 hrow : UniWC.Folds (GWs4 hrow)` — the 6250 banks of `mlog trWs4` are the trace's MOVEs (Uni.mlog_charts),
their chart heights are the frame dims (dim = finrank on subspace charts) and equal TWs4Data.HS / HD nibble by
nibble; the 1501 fields' birth / final heights equal FI / FF.  Hence D = 56 and R = 10943 − 10887 = 56 come from
the trace (`dhalfWs4`, `rhalfWs4`), not from free tables.  Only `RowsWs4` (final_row) is assumed, because
`foldBanked7113` needs a `Word`.
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.UniInhabitWs4Word
import Nov15.UniInhabitWs4Hist
import Nov15.UniHSC7113

set_option linter.unusedSectionVars false

namespace UniInhabitWs4
open Uni WordModel Finset UniFold7113 Module BankFitHS UniUniversal

attribute [local irreducible] trWs4 evsWs4 Tabs.maskT Tabs.ck26 Tabs.xI Tabs.yI Tabs.x2I Tabs.y2I Tabs.finP
  Tabs.initP Tabs.hI

/-! ## MOVE list of the trace -/

theorem mv_toEv (e : PE) : Ev.mvCh (MWs4.toEv e) = (mvOf e).map (fun p => (chOf p.1, chOf p.2)) := by
  unfold Model.toEv mvOf
  by_cases o4 : e.op = 4
  · have : Nat.beq e.op 4 = true := (beq_iff _ _).2 o4
    rw [this]
    have n0 : ¬ e.op = 0 := by omega
    have n1 : ¬ e.op = 1 := by omega
    have n2 : ¬ e.op = 2 := by omega
    have n3 : ¬ e.op = 3 := by omega
    rw [if_neg n0, if_neg n1, if_neg n2, if_neg n3, if_pos o4]
    split <;> rfl
  · have : Nat.beq e.op 4 = false := by
      cases h : Nat.beq e.op 4; rfl; exact absurd ((beq_iff _ _).1 h) o4
    rw [this]
    simp only [cond_false, Option.map_none]
    split_ifs <;> rfl

theorem evs_mv : evsWs4.filterMap mvOf = mvAll := by
  unfold evsWs4 chainEvs LWs4 mvAll
  simp only [List.map_cons, List.map_nil, List.flatten_cons, List.flatten_nil, List.filterMap_append, mv0_eq, mv1_eq,
    mv2_eq, mv3_eq, mv4_eq, mv5_eq, mv6_eq, mv7_eq, mv8_eq, mv9_eq, mv10_eq, mv11_eq, mv12_eq, mv13_eq, mv14_eq,
    mv15_eq, mv16_eq, mv17_eq, mv18_eq, mv19_eq, mv20_eq, mv21_eq, mv22_eq, mv23_eq, mv24_eq, mv25_eq,
    List.filterMap_nil, List.append_nil, List.append_assoc]

theorem mlog_ch : (mlog trWs4).map (fun m => (m.src, m.dst)) = mvAll.map (fun p => (chOf p.1, chOf p.2)) := by
  unfold mlog
  rw [mlog_charts trWs4 init, ← evs_mv, List.map_filterMap]
  unfold trWs4
  rw [List.filterMap_map]
  congr 1
  funext e
  exact mv_toEv e

theorem mlog_len : (mlog trWs4).length = 6250 := by
  have := congrArg List.length mlog_ch
  rw [List.length_map, List.length_map, mvAll_len] at this
  exact this

theorem mlog_src (k : ℕ) (hk : k < (mlog trWs4).length) :
    ((mlog trWs4)[k]).src = chOf (mvAll[k]'(by rw [mvAll_len]; rw [mlog_len] at hk; exact hk)).1 := by
  have := congrArg (fun L => L[k]?) mlog_ch
  simp only [List.getElem?_map] at this
  rw [List.getElem?_eq_getElem hk, List.getElem?_eq_getElem (by rw [mvAll_len]; rw [mlog_len] at hk; exact hk)] at this
  simp only [Option.map_some, Option.some.injEq, Prod.mk.injEq] at this
  exact this.1

theorem mlog_dst (k : ℕ) (hk : k < (mlog trWs4).length) :
    ((mlog trWs4)[k]).dst = chOf (mvAll[k]'(by rw [mvAll_len]; rw [mlog_len] at hk; exact hk)).2 := by
  have := congrArg (fun L => L[k]?) mlog_ch
  simp only [List.getElem?_map] at this
  rw [List.getElem?_eq_getElem hk, List.getElem?_eq_getElem (by rw [mvAll_len]; rw [mlog_len] at hk; exact hk)] at this
  simp only [Option.map_some, Option.some.injEq, Prod.mk.injEq] at this
  exact this.2

/-! ## tables -/

theorem chkT_sound : ∀ (L : List (ℕ × ℕ)) (X Y : ℕ), chkT L X Y = true → ∀ k (hk : k < L.length),
    X / 16 ^ k % 16 = gt 11 Tabs.dimT (L[k]).1 ∧ Y / 16 ^ k % 16 = gt 11 Tabs.dimT (L[k]).2 := by
  intro L
  induction L with
  | nil => intro X Y _ k hk; simp at hk
  | cons p L ih =>
    obtain ⟨c, d⟩ := p
    intro X Y h k hk
    simp only [chkT, Bool.and_eq_true, beq_iff] at h
    obtain ⟨⟨h1, h2⟩, h3⟩ := h
    cases k with
    | zero => simpa using ⟨h1, h2⟩
    | succ k =>
      have := ih _ _ h3 k (by simpa using hk)
      simp only [List.getElem_cons_succ]
      rw [pow_succ, mul_comm, ← Nat.div_div_eq_div_mul, ← Nat.div_div_eq_div_mul]
      exact this

theorem mv_lt' (k : ℕ) (hk : k < mvAll.length) : (mvAll[k]).1 < 1096 ∧ (mvAll[k]).2 < 1096 := by
  have := List.all_eq_true.1 mv_lt _ (List.getElem_mem hk)
  simp only [Bool.and_eq_true, blt_iff] at this
  exact this

theorem ht_chOf (i : ℕ) (hi : i < 1096) : ht (toSub (chOf i)) = gt 11 Tabs.dimT i := by
  show finrank (ZMod 2) (toSub (chOf i)) = _
  rw [← dim_chartOf, chartOf_toSub (frame_subsp i hi), dim_chOf i hi]


/-! ## the tWs4 tables, read off the concrete trace -/

def eB7 : Fin (mlog trWs4).length ≃ Fin TWs4Data.NB := finCongr mlog_len

theorem eB7_val (k : Fin (mlog trWs4).length) : ((eB7 k : Fin TWs4Data.NB) : ℕ) = k.1 := Fin.coe_cast mlog_len k

theorem nib_eB (X : ℕ) (k : Fin (mlog trWs4).length) : UniWC.nib X (eB7 k) = X / 16 ^ k.1 % 16 := by
  unfold UniWC.nib; rw [eB7_val]

theorem pub_idx (f : Fld (pub (Hl := Fin 1101) (Ow := Fin 180) caller7113)) : idxOf f.1 < 1501 := by
  have hj := (reg_idx f.1).2
  have h := f.2
  rw [← regOf_idx f.1] at h
  exact (MWs4_ok.hpb _ hj).1 h

def eF7 : Fld (pub (Hl := Fin 1101) (Ow := Fin 180) caller7113) ≃ Fin TWs4Data.NF where
  toFun f := ⟨idxOf f.1, pub_idx f⟩
  invFun j := ⟨regOf j.1, by
    have := (MWs4_ok.hpb j.1 (by have := j.2; show j.1 < 1697; simp [TWs4Data.NF] at this; omega)).2
      (by have := j.2; show j.1 < 1501; simpa [TWs4Data.NF] using this)
    exact this⟩
  left_inv f := Subtype.ext (regOf_idx f.1)
  right_inv j := Fin.ext (idx_reg j.1 (by have := j.2; simp [TWs4Data.NF] at this; omega))

theorem pinv_end : PInv (pub caller7113) (exec trWs4) := reach_pinv (pub caller7113) (reach_exec legalWs4)

theorem bch_end (j : ℕ) (hj : j < 1501) : bch (exec trWs4) (regOf j) = chOf (ini7 j) :=
  bch_eq pinv_end (born j hj)

theorem hs7 (k : Fin (mlog trWs4).length) :
    ht (toSub ((mlog trWs4)[k.1]'k.2).src) = UniWC.nib TWs4Data.HS (eB7 k) := by
  have hk : k.1 < mvAll.length := by have h1 := k.2; have h2 := mlog_len; have h3 := mvAll_len; omega
  have h1 : ht (toSub ((mlog trWs4)[k.1]'k.2).src) = gt 11 Tabs.dimT (mvAll[k.1]'hk).1 := by
    rewrite [mlog_src k.1 k.2]; exact ht_chOf _ (mv_lt' k.1 hk).1
  exact (h1.trans (chkT_sound mvAll _ _ tab_bank k.1 hk).1.symm).trans (nib_eB _ k).symm

theorem hd7 (k : Fin (mlog trWs4).length) :
    ht (toSub ((mlog trWs4)[k.1]'k.2).dst) = UniWC.nib TWs4Data.HD (eB7 k) := by
  have hk : k.1 < mvAll.length := by have h1 := k.2; have h2 := mlog_len; have h3 := mvAll_len; omega
  have h1 : ht (toSub ((mlog trWs4)[k.1]'k.2).dst) = gt 11 Tabs.dimT (mvAll[k.1]'hk).2 := by
    rewrite [mlog_dst k.1 k.2]; exact ht_chOf _ (mv_lt' k.1 hk).2
  exact (h1.trans (chkT_sound mvAll _ _ tab_bank k.1 hk).2.symm).trans (nib_eB _ k).symm

theorem nib_eF (X : ℕ) (f : Fld (pub (Hl := Fin 1101) (Ow := Fin 180) caller7113)) :
    UniWC.nib X (eF7 f) = X / 16 ^ (idxOf f.1) % 16 := rfl

theorem hi7 (f : Fld (pub (Hl := Fin 1101) (Ow := Fin 180) caller7113)) :
    ht (toSub (bch (exec trWs4) f.1)) = UniWC.nib TWs4Data.FI (eF7 f) := by
  have hj := pub_idx f
  rw [nib_eF, (tab_field _ hj).1, ← regOf_idx f.1, bch_end _ hj, idx_reg _ (by omega)]
  exact ht_chOf _ (init_lt _ hj)

theorem hf7 (f : Fld (pub (Hl := Fin 1101) (Ow := Fin 180) caller7113)) :
    ht (toSub (locCh ((exec trWs4).loc f.1))) = UniWC.nib TWs4Data.FF (eF7 f) := by
  have hj := pub_idx f
  rw [nib_eF, (tab_field _ hj).2, ← regOf_idx f.1, loc_pub _ hj, idx_reg _ (by omega)]
  exact ht_chOf _ (fin_codes _ hj).2

end UniInhabitWs4

#print axioms UniInhabitWs4.hs7
#print axioms UniInhabitWs4.hi7
#print axioms UniInhabitWs4.hf7
