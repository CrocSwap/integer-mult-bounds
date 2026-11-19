/-
Bridge7761R4 .  The #7761 bank forms as a `BankNC0.Recipe ℚ (Fin 1262) (Fin 5746)` (Bank = schedule position),
from the packed chunk words of Bridge7761R4D* (1500 terms per chunk), and ALL its cheap side conditions, kernel-checked chunk by chunk (R4C*):
  Recipe7761.fld k = field terms (coef, g) owned by bank k  (134078 terms),   Recipe7761.ref k = bank refs (coef, j)  (11241 terms)
  oref7761 f       = output terms (coef, j) of output field f (43106 terms, all bank refs; no direct field terms in the outputs)
  sc_fld7761 : p in fld k -> ChA7761 p.2 = chartOf (srcId k)        sc_ref7761 : p in ref k -> p.2 < k and chartOf (dstId p.2) = chartOf (srcId k)
  sc_out7761 : p in oref f -> chartOf (dstId p.2) = ChB7761 f       (exactly the hypotheses of BankNC0.dRec_read / outVec_out)
Kernel only.
-/
import Nov15.Bridge7761R4Ca
import Nov15.Bridge7761R4Cb
import Nov15.Bridge7761R4Cc
import Nov15.Bridge7761R4Cd
import Nov15.Bridge7761R4Ce
import Nov15.Bridge7761R4Cf
import Nov15.Bridge7761R4Cg
import Nov15.Bridge7761R4Ch
import Nov15.Bridge7761R4Ci
import Nov15.BankTieD
namespace Bridge7761
open Finset Module BankNC0

def FFW : List ℕ := [FF_0, FF_1, FF_2, FF_3, FF_4, FF_5, FF_6, FF_7, FF_8, FF_9, FF_10, FF_11, FF_12, FF_13, FF_14, FF_15, FF_16, FF_17, FF_18, FF_19, FF_20, FF_21, FF_22, FF_23, FF_24, FF_25, FF_26, FF_27, FF_28, FF_29, FF_30, FF_31, FF_32, FF_33, FF_34, FF_35, FF_36, FF_37, FF_38, FF_39, FF_40, FF_41, FF_42, FF_43, FF_44, FF_45, FF_46, FF_47, FF_48, FF_49, FF_50, FF_51, FF_52, FF_53, FF_54, FF_55, FF_56, FF_57, FF_58, FF_59, FF_60, FF_61, FF_62, FF_63, FF_64, FF_65, FF_66, FF_67, FF_68, FF_69, FF_70, FF_71, FF_72, FF_73, FF_74, FF_75, FF_76, FF_77, FF_78, FF_79, FF_80, FF_81, FF_82, FF_83, FF_84, FF_85, FF_86, FF_87, FF_88, FF_89]
def FCW : List ℕ := [FC_0, FC_1, FC_2, FC_3, FC_4, FC_5, FC_6, FC_7, FC_8, FC_9, FC_10, FC_11, FC_12, FC_13, FC_14, FC_15, FC_16, FC_17, FC_18, FC_19, FC_20, FC_21, FC_22, FC_23, FC_24, FC_25, FC_26, FC_27, FC_28, FC_29, FC_30, FC_31, FC_32, FC_33, FC_34, FC_35, FC_36, FC_37, FC_38, FC_39, FC_40, FC_41, FC_42, FC_43, FC_44, FC_45, FC_46, FC_47, FC_48, FC_49, FC_50, FC_51, FC_52, FC_53, FC_54, FC_55, FC_56, FC_57, FC_58, FC_59, FC_60, FC_61, FC_62, FC_63, FC_64, FC_65, FC_66, FC_67, FC_68, FC_69, FC_70, FC_71, FC_72, FC_73, FC_74, FC_75, FC_76, FC_77, FC_78, FC_79, FC_80, FC_81, FC_82, FC_83, FC_84, FC_85, FC_86, FC_87, FC_88, FC_89]
def FBW : List ℕ := [FB_0, FB_1, FB_2, FB_3, FB_4, FB_5, FB_6, FB_7, FB_8, FB_9, FB_10, FB_11, FB_12, FB_13, FB_14, FB_15, FB_16, FB_17, FB_18, FB_19, FB_20, FB_21, FB_22, FB_23, FB_24, FB_25, FB_26, FB_27, FB_28, FB_29, FB_30, FB_31, FB_32, FB_33, FB_34, FB_35, FB_36, FB_37, FB_38, FB_39, FB_40, FB_41, FB_42, FB_43, FB_44, FB_45, FB_46, FB_47, FB_48, FB_49, FB_50, FB_51, FB_52, FB_53, FB_54, FB_55, FB_56, FB_57, FB_58, FB_59, FB_60, FB_61, FB_62, FB_63, FB_64, FB_65, FB_66, FB_67, FB_68, FB_69, FB_70, FB_71, FB_72, FB_73, FB_74, FB_75, FB_76, FB_77, FB_78, FB_79, FB_80, FB_81, FB_82, FB_83, FB_84, FB_85, FB_86, FB_87, FB_88, FB_89]
def RJW : List ℕ := [RJ_0, RJ_1, RJ_2, RJ_3, RJ_4, RJ_5, RJ_6, RJ_7]
def RCW : List ℕ := [RC_0, RC_1, RC_2, RC_3, RC_4, RC_5, RC_6, RC_7]
def RKW : List ℕ := [RK_0, RK_1, RK_2, RK_3, RK_4, RK_5, RK_6, RK_7]
def OJW : List ℕ := [OJ_0, OJ_1, OJ_2, OJ_3, OJ_4, OJ_5, OJ_6, OJ_7, OJ_8, OJ_9, OJ_10, OJ_11, OJ_12, OJ_13, OJ_14, OJ_15, OJ_16, OJ_17, OJ_18, OJ_19, OJ_20, OJ_21, OJ_22, OJ_23, OJ_24, OJ_25, OJ_26, OJ_27, OJ_28]
def OCW : List ℕ := [OC_0, OC_1, OC_2, OC_3, OC_4, OC_5, OC_6, OC_7, OC_8, OC_9, OC_10, OC_11, OC_12, OC_13, OC_14, OC_15, OC_16, OC_17, OC_18, OC_19, OC_20, OC_21, OC_22, OC_23, OC_24, OC_25, OC_26, OC_27, OC_28]
def OFW : List ℕ := [OF_0, OF_1, OF_2, OF_3, OF_4, OF_5, OF_6, OF_7, OF_8, OF_9, OF_10, OF_11, OF_12, OF_13, OF_14, OF_15, OF_16, OF_17, OF_18, OF_19, OF_20, OF_21, OF_22, OF_23, OF_24, OF_25, OF_26, OF_27, OF_28]

def cg (ws : List ℕ) (w t : ℕ) : ℕ := sl (ws.getD (t / 1500) 0) w (t % 1500)
def fin5746 (x : ℕ) : Fin 5746 := ⟨x % 5746, Nat.mod_lt _ (by norm_num)⟩
def cq (ws : List ℕ) (t : ℕ) : ℚ := qdec (cg ws 32 t)

def Recipe7761 : Recipe ℚ (Fin 1262) (Fin 5746) where
  fld k := ((List.range 134078).filter (fun t => fin5746 (cg FBW 13 t) == k)).map (fun t => (cq FCW t, fin1262 (cg FFW 11 t)))
  ref k := ((List.range 11241).filter (fun t => fin5746 (cg RKW 13 t) == k)).map (fun t => (cq RCW t, fin5746 (cg RJW 13 t)))
def oref7761 (f : Fin 1262) : List (ℚ × Fin 5746) :=
  ((List.range 43106).filter (fun t => fin1262 (cg OFW 11 t) == f)).map (fun t => (cq OCW t, fin5746 (cg OJW 13 t)))
def ofld7761 (_ : Fin 1262) : List (ℚ × Fin 1262) := []



theorem allF : ∀ i, i < 90 → chkF (min 1500 (134078 - 1500 * i)) (FFW.getD i 0) (FBW.getD i 0) = true := by
  intro i hi; interval_cases i
  exacts [cF_0, cF_1, cF_2, cF_3, cF_4, cF_5, cF_6, cF_7, cF_8, cF_9, cF_10, cF_11, cF_12, cF_13, cF_14, cF_15, cF_16, cF_17, cF_18, cF_19, cF_20, cF_21, cF_22, cF_23, cF_24, cF_25, cF_26, cF_27, cF_28, cF_29, cF_30, cF_31, cF_32, cF_33, cF_34, cF_35, cF_36, cF_37, cF_38, cF_39, cF_40, cF_41, cF_42, cF_43, cF_44, cF_45, cF_46, cF_47, cF_48, cF_49, cF_50, cF_51, cF_52, cF_53, cF_54, cF_55, cF_56, cF_57, cF_58, cF_59, cF_60, cF_61, cF_62, cF_63, cF_64, cF_65, cF_66, cF_67, cF_68, cF_69, cF_70, cF_71, cF_72, cF_73, cF_74, cF_75, cF_76, cF_77, cF_78, cF_79, cF_80, cF_81, cF_82, cF_83, cF_84, cF_85, cF_86, cF_87, cF_88, cF_89]
theorem allR : ∀ i, i < 8 → chkR (min 1500 (11241 - 1500 * i)) (RJW.getD i 0) (RKW.getD i 0) = true := by
  intro i hi; interval_cases i
  exacts [cR_0, cR_1, cR_2, cR_3, cR_4, cR_5, cR_6, cR_7]
theorem allO : ∀ i, i < 29 → chkO (min 1500 (43106 - 1500 * i)) (OJW.getD i 0) (OFW.getD i 0) = true := by
  intro i hi; interval_cases i
  exacts [cO_0, cO_1, cO_2, cO_3, cO_4, cO_5, cO_6, cO_7, cO_8, cO_9, cO_10, cO_11, cO_12, cO_13, cO_14, cO_15, cO_16, cO_17, cO_18, cO_19, cO_20, cO_21, cO_22, cO_23, cO_24, cO_25, cO_26, cO_27, cO_28]

theorem termF (t : ℕ) (ht : t < 134078) : cg FFW 11 t < 1262 ∧ cg FBW 13 t < 5746 ∧
    sl FAK 11 (cg FFW 11 t) = sl BSK 11 (cg FBW 13 t) := by
  have h := List.all_eq_true.1 (allF (t / 1500) (by omega)) (t % 1500) (List.mem_range.2 (by omega))
  simp only [chkF, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at h
  exact ⟨h.1.1, h.1.2, h.2⟩
theorem termR (t : ℕ) (ht : t < 11241) : cg RJW 13 t < cg RKW 13 t ∧ cg RKW 13 t < 5746 ∧
    sl BTK 11 (cg RJW 13 t) = sl BSK 11 (cg RKW 13 t) := by
  have h := List.all_eq_true.1 (allR (t / 1500) (by omega)) (t % 1500) (List.mem_range.2 (by omega))
  simp only [chkR, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at h
  exact ⟨h.1.1, h.1.2, h.2⟩
theorem termO (t : ℕ) (ht : t < 43106) : cg OJW 13 t < 5746 ∧ cg OFW 11 t < 1262 ∧
    sl BTK 11 (cg OJW 13 t) = sl FBK 11 (cg OFW 11 t) := by
  have h := List.all_eq_true.1 (allO (t / 1500) (by omega)) (t % 1500) (List.mem_range.2 (by omega))
  simp only [chkO, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at h
  exact ⟨h.1.1, h.1.2, h.2⟩

theorem fin5746_val (x : ℕ) (h : x < 5746) : (fin5746 x : ℕ) = x := Nat.mod_eq_of_lt h
theorem fin1262_val (x : ℕ) (h : x < 1262) : (fin1262 x : ℕ) = x := Nat.mod_eq_of_lt h

theorem sc_fld7761 (k : Fin 5746) (p : ℚ × Fin 1262) (hp : p ∈ Recipe7761.fld k) :
    ChA7761 p.2 = chartOf (srcId k) := by
  simp only [Recipe7761, List.mem_map, List.mem_filter, List.mem_range, beq_iff_eq] at hp
  obtain ⟨t, ⟨ht, hk⟩, rfl⟩ := hp
  obtain ⟨h1, h2, h3⟩ := termF t ht
  have hk' : cg FBW 13 t = k := by have := congrArg Fin.val hk; rwa [fin5746_val _ h2] at this
  unfold ChA7761 srcId
  simp only [fin1262_val _ h1, h3, hk']

theorem sc_ref7761 (k : Fin 5746) (p : ℚ × Fin 5746) (hp : p ∈ Recipe7761.ref k) :
    p.2 < k ∧ chartOf (dstId p.2) = chartOf (srcId k) := by
  simp only [Recipe7761, List.mem_map, List.mem_filter, List.mem_range, beq_iff_eq] at hp
  obtain ⟨t, ⟨ht, hk⟩, rfl⟩ := hp
  obtain ⟨h1, h2, h3⟩ := termR t ht
  have hk' : cg RKW 13 t = k := by have := congrArg Fin.val hk; rwa [fin5746_val _ h2] at this
  refine ⟨?_, ?_⟩
  · show fin5746 (cg RJW 13 t) < k
    rw [Fin.lt_def, fin5746_val _ (by omega), ← hk']; exact h1
  · unfold dstId srcId
    simp only [fin5746_val _ (show cg RJW 13 t < 5746 by omega), h3, hk']

theorem sc_out7761 (f : Fin 1262) (p : ℚ × Fin 5746) (hp : p ∈ oref7761 f) :
    chartOf (dstId p.2) = ChB7761 f := by
  simp only [oref7761, List.mem_map, List.mem_filter, List.mem_range, beq_iff_eq] at hp
  obtain ⟨t, ⟨ht, hk⟩, rfl⟩ := hp
  obtain ⟨h1, h2, h3⟩ := termO t ht
  have hk' : cg OFW 11 t = f := by have := congrArg Fin.val hk; rwa [fin1262_val _ h2] at this
  unfold dstId ChB7761
  simp only [fin5746_val _ h1, h3, hk']

end Bridge7761
#print axioms Bridge7761.sc_fld7761
#print axioms Bridge7761.sc_ref7761
#print axioms Bridge7761.sc_out7761
