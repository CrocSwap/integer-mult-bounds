/-
UniInhabitMain (lane UNI-INHABIT, Nov 19).  **t7669 inhabits `Crossing.word`** (UniUniversal), modulo ONE named clause:
  `t7669_crossing (hrow : Rows7669) : Crossing .w7113 κ7669`,   κ7669 = 93/25000 = .00372 (< t7669's .0037214)
  `kappa_t7669_concrete (hrow : Rows7669) : κ7669 < .0093453742`.
Everything else is proved from the concrete 152023-event trace `tr7669` (UniInhabitReg): Legal (kernel replay),
Word up to final_row, FramesSubsp / ChartsSubsp / OwnedNested, HSContract (UNI-HSC `hsc7113`), D = 56 and R = 56
(the fold's chart heights = T7669Data tables, read off the trace), and Valid = t7669's own invoice at κ7669:
  paid  = Σ over the 6157 MOVEs of |Δdim|^σ  (fold_paid; specPrice = |Δdim| on nested subspace charts),
  credit = Σ over the 1101 helpers of gc(climb)  (path ends = birth / final frames),
  FW(σ) = cdat T − cdat P + 17 (credit − paid) ≥ 0.5414 > 0 at σ = 1 − 93/25000 (UniInhabitNum enclosures).
`Rows7669` (every public register's final row = the caller target) is NOT replayed: see cards/WILD/UNIMODEL/INHABIT.md.
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.UniInhabitFold
import Nov15.UniInhabitNum
import Nov15.UniInhabitNest

set_option linter.unusedSectionVars false

namespace UniInhabit
open Uni WordModel Finset UniFold7113 Module BankFitHS UniUniversal SafeRungsPrice

attribute [local irreducible] tr7669 evs7669 Tabs.maskT Tabs.ck26 Tabs.xI Tabs.yI Tabs.x2I Tabs.y2I Tabs.finP
  Tabs.initP Tabs.hI

/-! ## histograms -/

theorem hist (n : ℕ) (a : ℕ → ℕ) (F : ℕ → ℝ) (ha : ∀ j ∈ range n, a j ∈ range 10) :
    ∑ j ∈ range n, F (a j) = ∑ r ∈ range 10, (((range n).filter (fun j => a j = r)).card : ℝ) * F r := by
  rw [← Finset.sum_fiberwise_of_maps_to ha]
  apply sum_congr rfl
  intro r _
  rw [sum_congr rfl (fun j hj => by rw [(mem_filter.1 hj).2]), sum_const, nsmul_eq_mul]

theorem cnt_list (n r : ℕ) (a : ℕ → ℕ) :
    ((range n).filter (fun j => a j = r)).card = ((List.range n).filter (fun j => Nat.beq (a j) r)).length := by
  have := card_filt_gen (fun j => Nat.beq (a j) r) n
  rw [← this]
  congr 1
  ext j; simp [beq_iff]

/-! ## paid -/

theorem specPrice_mv (k : ℕ) (hk : k < mvAll.length) :
    specPrice (chOf (mvAll[k]).1) (chOf (mvAll[k]).2) = (prc k : ℝ) := by
  have hl := mv_lt' k hk
  have hn := List.all_eq_true.1 mv_nest _ (List.getElem_mem hk)
  have hs : chOf (mvAll[k]).1 ⊆ chOf (mvAll[k]).2 ∨ chOf (mvAll[k]).2 ⊆ chOf (mvAll[k]).1 := by
    simp only [Bool.or_eq_true] at hn
    rcases hn with h | h
    · exact Or.inl (ssub_lt _ _ h).le
    · exact Or.inr (ssub_lt _ _ h).le
  rw [specPrice_eq_mvPrice (frame_subsp _ hl.1) (frame_subsp _ hl.2) hs]
  unfold mvPrice
  rw [dim_chOf _ hl.1, dim_chOf _ hl.2]
  have e := chkT_sound mvAll _ _ tab_bank k hk
  have hp : prc k = dhN (gt 11 Tabs.dimT (mvAll[k]).1) (gt 11 Tabs.dimT (mvAll[k]).2) := by
    unfold prc nb; rw [e.1, e.2]
  rw [hp]
  congr 1
  unfold dhN
  split_ifs <;> omega

theorem fsrc_eq {R : Type} [Fintype R] [DecidableEq R] (tr : Trace R) (k : Fin (mlog tr).length) :
    fsrc tr k = ((mlog tr)[k.1]'k.2).src := rfl
theorem fdst_eq {R : Type} [Fintype R] [DecidableEq R] (tr : Trace R) (k : Fin (mlog tr).length) :
    fdst tr k = ((mlog tr)[k.1]'k.2).dst := rfl

theorem paid7 (σ : ℝ) : wordPaid caller7113 (exec tr7669) specPrice σ = ∑ j ∈ range 6157, ((prc j : ℕ) : ℝ) ^ σ := by
  rw [← fold_paid caller7113 legal7669 specPrice σ]
  unfold paidF
  have e : ∀ k : Fin (mlog tr7669).length, specPrice (fsrc tr7669 k) (fdst tr7669 k) ^ σ = ((prc k.1 : ℕ) : ℝ) ^ σ := by
    intro k
    have hk : k.1 < mvAll.length := by have h1 := k.2; have h2 := mlog_len; have h3 := mvAll_len; omega
    rewrite [fsrc_eq, fdst_eq, mlog_src k.1 k.2, mlog_dst k.1 k.2, specPrice_mv k.1 hk]
    rfl
  rw [Finset.sum_congr rfl (fun k _ => e k)]
  rw [Fin.sum_univ_eq_sum_range (fun j => ((prc j : ℕ) : ℝ) ^ σ) (mlog tr7669).length, mlog_len]

theorem prc_mem : ∀ j ∈ range 6157, prc j ∈ range 10 := by
  intro j hj
  have := List.all_eq_true.1 prc_lt j (List.mem_range.2 (mem_range.1 hj))
  simp only [blt_iff] at this
  exact mem_range.2 this

theorem paid7_hist (σ : ℝ) (hσ : σ ≠ 0) : wordPaid caller7113 (exec tr7669) specPrice σ =
    3962 + 879 * (2:ℝ) ^ σ + 602 * (3:ℝ) ^ σ + 243 * (4:ℝ) ^ σ + 362 * (5:ℝ) ^ σ + 87 * (6:ℝ) ^ σ +
      11 * (7:ℝ) ^ σ + 7 * (8:ℝ) ^ σ + 4 * (9:ℝ) ^ σ := by
  rw [paid7, hist 6157 prc (fun r => ((r : ℕ) : ℝ) ^ σ) prc_mem]
  simp only [Finset.sum_range_succ, Finset.sum_range_zero, cnt_list, prc_0, prc_1, prc_2, prc_3, prc_4, prc_5,
    prc_6, prc_7, prc_8, prc_9]
  push_cast
  rw [Real.zero_rpow hσ, Real.one_rpow]
  ring

/-! ## credit -/

theorem idx_h (i : Fin 1101) : idxOf (.h i : R7) = lk Tabs.hI i := rfl

theorem hcred7 (i : Fin 1101) : hcred (exec tr7669) (.h i : R7) = ((clm i.1 : ℕ) : ℝ) := by
  have hj : lk Tabs.hI i < 1501 := by
    have := List.all_eq_true.1 hI_lt i.1 (List.mem_range.2 i.2)
    simpa [blt_iff] using this
  have hr : regOf (lk Tabs.hI i) = .h i := by rw [← idx_h]; exact regOf_idx _
  obtain ⟨h0, h1⟩ := path_ends (pub caller7113) pinv_end (born _ hj)
  rw [hr] at h0 h1
  have hl := loc_pub _ hj
  rw [hr, h1] at hl
  have hend : path (exec tr7669) (.h i) (plen (exec tr7669) (.h i)) = chOf (fin7 (lk Tabs.hI i)) := by
    injection hl
  unfold hcred
  rw [hend, h0, dim_chOf (fin7 _) (fin_codes _ hj).2, dim_chOf (ini7 _) (init_lt _ hj)]
  have hf := tab_field _ hj
  obtain ⟨hle, _⟩ := clm_ok i.1 i.2
  unfold clm
  rw [Nat.cast_sub hle]
  unfold nb
  rw [hf.1, hf.2]
  rfl

theorem cred7 (σ : ℝ) : ∑ r ∈ (helpers : Finset R7), gc σ (hcred (exec tr7669) r) =
    ∑ i ∈ range 1101, gc σ ((clm i : ℕ) : ℝ) := by
  unfold helpers
  rw [sum_image (fun a _ b _ h => by cases h; rfl)]
  rw [Finset.sum_congr rfl (fun i _ => by rw [hcred7 i])]
  exact Fin.sum_univ_eq_sum_range (fun i => gc σ ((clm i : ℕ) : ℝ)) 1101

theorem clm_mem : ∀ j ∈ range 1101, clm j ∈ range 10 := fun j hj => mem_range.2 (clm_ok j (mem_range.1 hj)).2

theorem gc_pos (σ : ℝ) (r : ℕ) (hr : 0 < r) : gc σ (r : ℝ) = (r : ℝ) ^ σ := by
  have : (0:ℝ) < r := by exact_mod_cast hr
  unfold gc; rw [if_neg (not_le.2 this)]

theorem cred7_hist (σ : ℝ) : ∑ r ∈ (helpers : Finset R7), gc σ (hcred (exec tr7669) r) =
    18 + 21 * (2:ℝ) ^ σ + 47 * (3:ℝ) ^ σ + 227 * (4:ℝ) ^ σ + 78 * (5:ℝ) ^ σ + 44 * (6:ℝ) ^ σ +
      19 * (7:ℝ) ^ σ + 32 * (8:ℝ) ^ σ + 615 * (9:ℝ) ^ σ := by
  rw [cred7, hist 1101 clm (fun r => gc σ ((r : ℕ) : ℝ)) clm_mem]
  simp only [Finset.sum_range_succ, Finset.sum_range_zero, cnt_list, clm_0, clm_1, clm_2, clm_3, clm_4, clm_5,
    clm_6, clm_7, clm_8, clm_9]
  rw [gc_pos σ 1 (by norm_num), gc_pos σ 2 (by norm_num), gc_pos σ 3 (by norm_num), gc_pos σ 4 (by norm_num),
    gc_pos σ 5 (by norm_num), gc_pos σ 6 (by norm_num), gc_pos σ 7 (by norm_num), gc_pos σ 8 (by norm_num),
    gc_pos σ 9 (by norm_num)]
  push_cast
  rw [Real.one_rpow]
  ring

/-! ## Valid at κ7669 -/

/-- κ7669 = 93/25000 = .00372, just below t7669's published κ = .0037214. -/
noncomputable def κ7669 : ℝ := 93 / 25000

theorem valid7669 : cdat (1 - κ7669) Pcal + ∑ _i : Fin 17, wordPaid caller7113 (exec tr7669) specPrice (1 - κ7669) ≤
    cdat (1 - κ7669) Tcal + ∑ _i : Fin 17, ∑ r ∈ (helpers : Finset R7), gc (1 - κ7669) (hcred (exec tr7669) r) := by
  have hσ : (1 - κ7669) ≠ 0 := by unfold κ7669; norm_num
  rw [paid7_hist _ hσ, cred7_hist]
  simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]
  have hw := fw_pos
  unfold SafeCertGen.phi at hw
  unfold κ7669
  simp only [cdat, Tcal, Pcal, List.map_cons, List.map_nil, List.sum_cons, List.sum_nil]
  push_cast
  rw [Real.one_rpow]
  linarith

/-! ## the inhabitant -/

/-- **t7669 is a `Crossing.word` at κ7669**, given only the row clause `Rows7669`. -/
theorem t7669_crossing (hrow : Rows7669) : Crossing .w7113 κ7669 :=
  Crossing.word caller7113 ports_caller7113 dcount_caller7113 (fun _ => tr7669) (fun _ => legal7669)
    (fun _ => word7669 hrow) (fun _ => frames7669) (fun _ => charts7669) (fun _ => nested7669)
    (fun _ => UniHSC7113.hsc7113 legal7669 (word7669 hrow))
    (fun _ => dhalfGen caller7113 ports_caller7113 dcount_caller7113 legal7669 (word7669 hrow) frames7669 charts7669
      nested7669 (foldsGen caller7113 ports_caller7113 dcount_caller7113 legal7669 (word7669 hrow) frames7669
        charts7669 nested7669 eB7 eF7 hs7 hd7 hi7 hf7))
    (fun _ => rhalfGen caller7113 ports_caller7113 dcount_caller7113 legal7669 (word7669 hrow) frames7669 charts7669
      nested7669 (foldsGen caller7113 ports_caller7113 dcount_caller7113 legal7669 (word7669 hrow) frames7669
        charts7669 nested7669 eB7 eF7 hs7 hd7 hi7 hf7))
    κ7669 (by unfold κ7669; norm_num) (by unfold κ7669; norm_num) valid7669

/-- **kappa_t7669_concrete**: the concrete t7669 word lies below the #7113 X = 112 rung (κ < .0093453742). -/
theorem kappa_t7669_concrete (hrow : Rows7669) : κ7669 < 93453742 / 10000000000 :=
  kappa_lt_universal .w7113 κ7669 (t7669_crossing hrow)

end UniInhabit

#print axioms UniInhabit.valid7669
#print axioms UniInhabit.t7669_crossing
#print axioms UniInhabit.kappa_t7669_concrete
