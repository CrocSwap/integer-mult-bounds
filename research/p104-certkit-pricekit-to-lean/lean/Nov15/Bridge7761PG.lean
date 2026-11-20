/-
Bridge7761PG (lane BRIDGE-HO, Nov 18).  hO for #7761, kernel-checked:
  hO7761 : ∀ f, outVec Recipe7761 (ofld7761 f) (oref7761 f) = O7761 f
Method (BRIDGE-OUT design): bank k is scaled by an integer D_k (PD table dk); for each of 5 column blocks of 256
the packed integer Q_k = D_k * E_b(dRec k) (E_b = sum_i v(b0+i) 2^(72 i)) is a straight-line constant (PQ_b);
  * fld_slice / ref_slice / out_slice : Recipe7761's List.filter's ARE contiguous slices (start tables + per-term checks, PS);
  * chkB (PB)     : all multipliers D_k c, D_k c / D_j are integers, l-inf bound recursion beta_k;
  * chkBank (PC_b): Q_k = sum fld + sum (D_k c/D_j) Q_j  => packed_ind: D_k * E_b(dRec k) = Q_k;
  * chkOut (PO_b) : sum (D_f c/D_j) Q_j = D_f * E_b(O f), chkOB: output bound < 2^72  => digits_zero: equal on the block.
Kernel only (decide +kernel on data; no sorry / native_decide / new axioms).
-/
import Nov15.Bridge7761R5
import Nov15.Bridge7761P0
import Nov15.Bridge7761PH

namespace Bridge7761
open BridgeP BankNC0 Finset

theorem sx_eq (P w i : ℕ) : sx P w i = sl P w i := rfl

theorem FFT_get : (List.range 90).all (fun i => FFT.get i == FFW.getD i 0) = true := by decide +kernel
theorem FCT_get : (List.range 90).all (fun i => FCT.get i == FCW.getD i 0) = true := by decide +kernel
theorem RJT_get : (List.range 8).all (fun i => RJT.get i == RJW.getD i 0) = true := by decide +kernel
theorem RCT_get : (List.range 8).all (fun i => RCT.get i == RCW.getD i 0) = true := by decide +kernel
theorem OJT_get : (List.range 29).all (fun i => OJT.get i == OJW.getD i 0) = true := by decide +kernel
theorem OCT_get : (List.range 29).all (fun i => OCT.get i == OCW.getD i 0) = true := by decide +kernel

theorem cgT_eq' (tw : BT ℕ) (ws : List ℕ) (n w t : ℕ)
    (h : (List.range n).all (fun i => tw.get i == ws.getD i 0) = true) (ht : t / 1500 < n) :
    cgT tw w t = cg ws w t := by
  have := List.all_eq_true.1 h (t / 1500) (List.mem_range.2 ht)
  simp only [beq_iff_eq] at this
  unfold cgT cg; rw [this, sx_eq]

theorem fF_eq (t : ℕ) (ht : t < 134078) : fF t = cg FFW 11 t := cgT_eq' _ _ 90 _ t FFT_get (by omega)
theorem fC_eq (t : ℕ) (ht : t < 134078) : fC t = cg FCW 32 t := cgT_eq' _ _ 90 _ t FCT_get (by omega)
theorem rJ_eq (t : ℕ) (ht : t < 11241) : rJ t = cg RJW 13 t := cgT_eq' _ _ 8 _ t RJT_get (by omega)
theorem rC_eq (t : ℕ) (ht : t < 11241) : rC t = cg RCW 32 t := cgT_eq' _ _ 8 _ t RCT_get (by omega)
theorem oJ_eq (t : ℕ) (ht : t < 43106) : oJ t = cg OJW 13 t := cgT_eq' _ _ 29 _ t OJT_get (by omega)
theorem oC_eq (t : ℕ) (ht : t < 43106) : oC t = cg OCW 32 t := cgT_eq' _ _ 29 _ t OCT_get (by omega)

/-! ### slices -/

theorem chkSF_spec {n base w : ℕ} (h : chkSF n base w = true) (u : ℕ) (hu : u < n) :
    sF (sx w 13 u) ≤ base + u ∧ base + u < sF (sx w 13 u + 1) := by
  unfold chkSF at h; have := List.all_eq_true.1 h u (List.mem_range.2 hu)
  simp only [Bool.and_eq_true, decide_eq_true_eq] at this; exact this
theorem chkSR_spec {n base w : ℕ} (h : chkSR n base w = true) (u : ℕ) (hu : u < n) :
    sR (sx w 13 u) ≤ base + u ∧ base + u < sR (sx w 13 u + 1) := by
  unfold chkSR at h; have := List.all_eq_true.1 h u (List.mem_range.2 hu)
  simp only [Bool.and_eq_true, decide_eq_true_eq] at this; exact this
theorem chkSO_spec {n base w : ℕ} (h : chkSO n base w = true) (u : ℕ) (hu : u < n) :
    sO (sg (sx w 11 u)) ≤ base + u ∧ base + u < sO (sg (sx w 11 u) + 1) := by
  unfold chkSO at h; have := List.all_eq_true.1 h u (List.mem_range.2 hu)
  simp only [Bool.and_eq_true, decide_eq_true_eq] at this; exact this

theorem termSF (t : ℕ) (ht : t < 134078) : sF (cg FBW 13 t) ≤ t ∧ t < sF (cg FBW 13 t + 1) := by
  have h := chkSF_spec (allSF (t / 1500) (by omega)) (t % 1500) (by omega)
  have e : cg FBW 13 t = sx (FBW.getD (t / 1500) 0) 13 (t % 1500) := rfl
  rw [e]; omega
theorem termSR (t : ℕ) (ht : t < 11241) : sR (cg RKW 13 t) ≤ t ∧ t < sR (cg RKW 13 t + 1) := by
  have h := chkSR_spec (allSR (t / 1500) (by omega)) (t % 1500) (by omega)
  have e : cg RKW 13 t = sx (RKW.getD (t / 1500) 0) 13 (t % 1500) := rfl
  rw [e]; omega
theorem termSO (t : ℕ) (ht : t < 43106) : sO (sg (cg OFW 11 t)) ≤ t ∧ t < sO (sg (cg OFW 11 t) + 1) := by
  have h := chkSO_spec (allSO (t / 1500) (by omega)) (t % 1500) (by omega)
  have e : cg OFW 11 t = sx (OFW.getD (t / 1500) 0) 11 (t % 1500) := rfl
  rw [e]; omega

theorem monoF : ∀ i < 5746, sF i ≤ sF (i+1) := fun i hi => by
  simpa using List.all_eq_true.1 sF_mono i (List.mem_range.2 hi)
theorem monoR : ∀ i < 5746, sR i ≤ sR (i+1) := fun i hi => by
  simpa using List.all_eq_true.1 sR_mono i (List.mem_range.2 hi)
theorem monoO : ∀ i < 1262, sO i ≤ sO (i+1) := fun i hi => by
  simpa using List.all_eq_true.1 sO_mono i (List.mem_range.2 hi)
theorem sgtu (x : ℕ) (hx : x < 1262) : sg x < 1262 ∧ tu (sg x) = x := by
  simpa using List.all_eq_true.1 sg_tu x (List.mem_range.2 hx)

theorem beq_fin5746 (x : ℕ) (hx : x < 5746) (k : Fin 5746) : (fin5746 x == k) = decide (x = k.val) := by
  rw [Bool.eq_iff_iff, beq_iff_eq, decide_eq_true_eq, Fin.ext_iff, fin5746_val x hx]
theorem beq_fin1262 (x : ℕ) (hx : x < 1262) (k : Fin 1262) : (fin1262 x == k) = decide (x = k.val) := by
  rw [Bool.eq_iff_iff, beq_iff_eq, decide_eq_true_eq, Fin.ext_iff, fin1262_val x hx]

theorem fld_slice (k : Fin 5746) :
    Recipe7761.fld k = (fsl k).map (fun t => (cq FCW t, fin1262 (cg FFW 11 t))) := by
  dsimp only [Recipe7761]
  rw [List.filter_congr (q := fun t => decide ((fun t => cg FBW 13 t) t = k.val))
    (fun t ht => beq_fin5746 _ (termF t (List.mem_range.1 ht)).2.1 k),
    filter_slice 134078 5746 (fun t => cg FBW 13 t) sF monoF sF_end (fun t ht => ⟨(termF t ht).2.1, termSF t ht⟩) k.val k.isLt]
  rfl

theorem ref_slice (k : Fin 5746) :
    Recipe7761.ref k = (rsl k).map (fun t => (cq RCW t, fin5746 (cg RJW 13 t))) := by
  dsimp only [Recipe7761]
  rw [List.filter_congr (q := fun t => decide ((fun t => cg RKW 13 t) t = k.val))
    (fun t ht => beq_fin5746 _ (termR t (List.mem_range.1 ht)).2.1 k),
    filter_slice 11241 5746 (fun t => cg RKW 13 t) sR monoR sR_end (fun t ht => ⟨(termR t ht).2.1, termSR t ht⟩) k.val k.isLt]
  rfl

theorem out_slice (f : Fin 1262) :
    oref7761 f = (osl (sg f)).map (fun t => (cq OCW t, fin5746 (cg OJW 13 t))) := by
  have hq : ∀ t ∈ List.range 43106, (fin1262 (cg OFW 11 t) == f) = decide ((fun t => sg (cg OFW 11 t)) t = sg f.val) := by
    intro t ht
    have hx := (termO t (List.mem_range.1 ht)).2.1
    rw [beq_fin1262 _ hx f]
    simp only [decide_eq_decide]
    constructor
    · intro h; rw [h]
    · intro h; have := congrArg tu h; rwa [(sgtu _ hx).2, (sgtu _ f.isLt).2] at this
  unfold oref7761
  rw [List.filter_congr hq, filter_slice 43106 1262 (fun t => sg (cg OFW 11 t)) sO monoO sO_end
      (fun t ht => ⟨(sgtu _ (termO t ht).2.1).1, termSO t ht⟩) (sg f.val) (sgtu _ f.isLt).1]
  rfl

theorem fsl_lt (k : ℕ) (hk : k < 5746) (t : ℕ) (ht : t ∈ fsl k) : t < 134078 := by
  unfold fsl at ht; rw [List.mem_range'_1] at ht
  have := mono_le sF 5746 monoF (k+1) 5746 (by omega) le_rfl; have := sF_end; omega
theorem rsl_lt (k : ℕ) (hk : k < 5746) (t : ℕ) (ht : t ∈ rsl k) : t < 11241 := by
  unfold rsl at ht; rw [List.mem_range'_1] at ht
  have := mono_le sR 5746 monoR (k+1) 5746 (by omega) le_rfl; have := sR_end; omega
theorem osl_lt (p : ℕ) (hp : p < 1262) (t : ℕ) (ht : t ∈ osl p) : t < 43106 := by
  unfold osl at ht; rw [List.mem_range'_1] at ht
  have := mono_le sO 1262 monoO (p+1) 1262 (by omega) le_rfl; have := sO_end; omega

/-! ### rational facts from the once-checks -/

theorem qdec_eq (s : ℕ) : qdec s = (nz s : ℚ) / (dz s : ℚ) := rfl

theorem div_cast (a : ℤ) (d : ℕ) (hd : 0 < d) (h : a % (d : ℤ) = 0) : ((a / (d : ℤ) : ℤ) : ℚ) = (a : ℚ) / (d : ℚ) := by
  rw [Int.cast_div (Int.dvd_of_emod_eq_zero h) (by exact_mod_cast hd.ne')]; norm_cast

theorem chkB_spec (k : ℕ) (hk : k < 5746) :
    0 < dk k ∧ (∀ t ∈ fsl k, 0 < dz (fC t) ∧ ((dk k : ℤ) * nz (fC t)) % ((dz (fC t) : ℕ) : ℤ) = 0) ∧
    (∀ t ∈ rsl k, 0 < dz (rC t) * dk (rJ t) ∧ ((dk k : ℤ) * nz (rC t)) % ((dz (rC t) * dk (rJ t) : ℕ) : ℤ) = 0) ∧
    ((fsl k).map (fun t => (mfz k t).natAbs)).sum + ((rsl k).map (fun t => (mrz k t).natAbs * bk (rJ t))).sum ≤ bk k := by
  have h := allB k hk
  simp only [chkB, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, beq_iff_eq] at h
  exact ⟨h.1.1.1, h.1.1.2, h.1.2, h.2⟩

theorem fq (k : ℕ) (hk : k < 5746) (t : ℕ) (ht : t ∈ fsl k) : (dk k : ℚ) * cq FCW t = (mfz k t : ℚ) := by
  obtain ⟨-, hf, -, -⟩ := chkB_spec k hk
  obtain ⟨h1, h2⟩ := hf t ht
  unfold cq mfz; rw [← fC_eq t (fsl_lt k hk t ht), qdec_eq, div_cast _ _ h1 h2]; push_cast; ring

theorem rq (k : ℕ) (hk : k < 5746) (t : ℕ) (ht : t ∈ rsl k) :
    (dk k : ℚ) * cq RCW t / (dk (cg RJW 13 t) : ℚ) = (mrz k t : ℚ) := by
  obtain ⟨-, -, hr, -⟩ := chkB_spec k hk
  obtain ⟨h1, h2⟩ := hr t ht
  have hlt := rsl_lt k hk t ht
  unfold cq mrz; rw [← rC_eq t hlt, ← rJ_eq t hlt, qdec_eq, div_cast _ _ h1 h2]; push_cast
  have : (0:ℚ) < dz (rC t) := by exact_mod_cast Nat.pos_of_mul_pos_right h1
  have : (0:ℚ) < dk (rJ t) := by exact_mod_cast Nat.pos_of_mul_pos_left h1
  field_simp

theorem dk_pos (k : ℕ) (hk : k < 5746) : 0 < dk k := (chkB_spec k hk).1

theorem chkOB_spec (f : ℕ) (hf : f < 1262) :
    0 < df f ∧ 0 < dz (sx ODK 32 f) ∧ 0 < dz (sx OPK 32 f) ∧
    ((df f : ℤ) * nz (sx ODK 32 f)) % ((dz (sx ODK 32 f) : ℕ) : ℤ) = 0 ∧
    ((df f : ℤ) * nz (sx OPK 32 f)) % ((dz (sx OPK 32 f) : ℕ) : ℤ) = 0 ∧
    (∀ t ∈ osl (sg f), 0 < dz (oC t) * dk (oJ t) ∧ ((df f : ℤ) * nz (oC t)) % ((dz (oC t) * dk (oJ t) : ℕ) : ℤ) = 0) ∧
    ((osl (sg f)).map (fun t => (moz f t).natAbs * bk (oJ t))).sum + (mdd f).natAbs + (mop f).natAbs < 2 ^ 72 := by
  have h := allOB (sg f) (sgtu f hf).1
  simp only [chkOB, (sgtu f hf).2, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, beq_iff_eq] at h
  exact ⟨h.1.1.1.1.1.1, h.1.1.1.1.1.2, h.1.1.1.1.2, h.1.1.1.2, h.1.1.2, h.1.2, h.2⟩

theorem oq (f : ℕ) (hf : f < 1262) (t : ℕ) (ht : t ∈ osl (sg f)) :
    (df f : ℚ) * cq OCW t / (dk (cg OJW 13 t) : ℚ) = (moz f t : ℚ) := by
  obtain ⟨-, -, -, -, -, ho, -⟩ := chkOB_spec f hf
  obtain ⟨h1, h2⟩ := ho t ht
  have hlt := osl_lt (sg f) (sgtu f hf).1 t ht
  unfold cq moz; rw [← oC_eq t hlt, ← oJ_eq t hlt, qdec_eq, div_cast _ _ h1 h2]; push_cast
  have : (0:ℚ) < dz (oC t) := by exact_mod_cast Nat.pos_of_mul_pos_right h1
  have : (0:ℚ) < dk (oJ t) := by exact_mod_cast Nat.pos_of_mul_pos_left h1
  field_simp

theorem ddq (f : ℕ) (hf : f < 1262) : (df f : ℚ) * ddv f = (mdd f : ℚ) := by
  obtain ⟨-, h1, -, h2, -⟩ := chkOB_spec f hf
  unfold ddv mdd; rw [← sx_eq, qdec_eq, div_cast _ _ h1 h2]; push_cast; ring
theorem opq (f : ℕ) (hf : f < 1262) : (df f : ℚ) * oov f = (mop f : ℚ) := by
  obtain ⟨-, -, h1, -, h2, -⟩ := chkOB_spec f hf
  unfold oov mop; rw [← sx_eq, qdec_eq, div_cast _ _ h1 h2]; push_cast; ring
theorem oov_ne (f : ℕ) (hf : f < 1262) : oov f ≠ 0 ↔ nz (sx OPK 32 f) ≠ 0 := by
  obtain ⟨-, -, h1, -⟩ := chkOB_spec f hf
  unfold oov; rw [← sx_eq, qdec_eq]
  have : (dz (sx OPK 32 f) : ℚ) ≠ 0 := by exact_mod_cast h1.ne'
  rw [ne_eq, div_eq_zero_iff, not_or, ne_eq, Int.cast_eq_zero]; tauto

/-! ### the row of O as a short vector -/

theorem O_row (f : Fin 1262) : (O7761 f : Fin 1262 → ℚ) =
    ddv f • Pi.single f 1 + (if oov f ≠ 0 then oov f • Pi.single (fin1262 (pip f)) 1 else 0) := by
  funext g
  unfold O7761 funcMat pOpt
  by_cases ho : oov f ≠ 0
  · obtain ⟨hp, hne, -⟩ := chkP f f.isLt ho
    have hne' : fin1262 (pip f) ≠ f := fun e => hne (by have := congrArg Fin.val e; rw [fin1262_val _ hp] at this; exact this)
    simp only [if_pos ho, Pi.add_apply, Pi.smul_apply, smul_eq_mul]
    by_cases hg : g = f
    · subst hg; rw [if_pos rfl, Pi.single_eq_same, Pi.single_eq_of_ne (Ne.symm hne')]; ring
    · rw [if_neg hg, Pi.single_eq_of_ne hg]
      by_cases hg2 : g = fin1262 (pip f)
      · subst hg2; rw [if_pos rfl, Pi.single_eq_same]; ring
      · rw [if_neg (fun e => hg2 (Option.some_injective _ e).symm), Pi.single_eq_of_ne hg2]; ring
  · simp only [if_neg ho, Pi.add_apply, Pi.smul_apply, smul_eq_mul, Pi.zero_apply]
    by_cases hg : g = f
    · subst hg; rw [if_pos rfl, Pi.single_eq_same]; ring
    · rw [if_neg hg, Pi.single_eq_of_ne hg, if_neg (by simp)]; ring

/-! ### one block -/

theorem pw_cast (e : ℕ) : ((pw e : ℤ) : ℚ) = ((2:ℚ) ^ 72) ^ e := by
  unfold pw; push_cast; rw [← pow_mul]

theorem hlt7761 : ∀ k p, p ∈ Recipe7761.ref k → p.2 < k := fun k p hp => (sc_ref7761 k p hp).1

theorem hstep_blk (b0 : ℕ) (qt : BT ℤ) (hC : ∀ k, k < 5746 → chkBank b0 qt k = true) (k : Fin 5746) :
    ((fun k : Fin 5746 => dk k.val) k : ℚ) * ((Recipe7761.fld k).map fun p => p.1 * EB 1262 b0 256 ((2:ℚ) ^ 72) (Pi.single p.2 1)).sum +
      ((Recipe7761.ref k).map fun p => (((fun k : Fin 5746 => dk k.val) k : ℚ) * p.1 /
        ((fun k : Fin 5746 => dk k.val) p.2 : ℚ)) * ((qt.get p.2.val : ℤ) : ℚ)).sum = ((qt.get k.val : ℤ) : ℚ) := by
  have h := hC k.val k.isLt
  simp only [chkBank, beq_iff_eq] at h
  rw [h, fld_slice, ref_slice, List.map_map, List.map_map, Int.cast_add, Int.cast_list_sum, Int.cast_list_sum,
    List.map_map, List.map_map, ← List.sum_map_mul_left]
  congr 1
  · congr 1; apply List.map_congr_left; intro t ht
    have hlt := fsl_lt k.val k.isLt t ht
    have hg := (termF t hlt).1
    simp only [Function.comp, EB_single, fin1262_val _ hg, fterm]
    rw [fF_eq t hlt]
    split_ifs with hb
    · rw [Int.cast_mul, pw_cast, ← fq k.val k.isLt t ht]; ring
    · simp
  · congr 1; apply List.map_congr_left; intro t ht
    have hlt := rsl_lt k.val k.isLt t ht
    have hj := (termR t hlt).2.1
    have hj' : cg RJW 13 t < 5746 := by have := termR t hlt; omega
    simp only [Function.comp, rterm, Int.cast_mul]
    rw [fin5746_val _ hj', rJ_eq t hlt, rq k.val k.isLt t ht]

theorem packed_blk (b0 : ℕ) (qt : BT ℤ) (hC : ∀ k, k < 5746 → chkBank b0 qt k = true) (k : Fin 5746) :
    (dk k.val : ℚ) * EB 1262 b0 256 ((2:ℚ) ^ 72) (dRec Recipe7761 k) = ((qt.get k.val : ℤ) : ℚ) :=
  packed_ind Recipe7761 (EB 1262 b0 256 ((2:ℚ) ^ 72)) (fun k => dk k.val) (fun k => ((qt.get k.val : ℤ) : ℚ))
    (fun k => (dk_pos k.val k.isLt).ne') hlt7761 (hstep_blk b0 qt hC) k


theorem bound7761 (k : Fin 5746) (g : Fin 1262) : IB ((dk k.val : ℚ) * dRec Recipe7761 k g) (bk k.val) := by
  refine bound_ind Recipe7761 (fun k => dk k.val) (fun k => (bk k.val : ℤ)) (fun k => (dk_pos k.val k.isLt).ne')
    hlt7761 (fun k p => ((dk k.val : ℚ) * p.1).num) (fun k p => ((dk k.val : ℚ) * p.1 / (dk p.2.val : ℚ)).num) ?_ ?_ ?_ k g
  · intro k p hp
    rw [fld_slice, List.mem_map] at hp; obtain ⟨t, ht, rfl⟩ := hp
    rw [fq k.val k.isLt t ht, Rat.num_intCast]
  · intro k p hp
    rw [ref_slice, List.mem_map] at hp; obtain ⟨t, ht, rfl⟩ := hp
    have hlt := rsl_lt k.val k.isLt t ht
    have hj' : cg RJW 13 t < 5746 := by have := termR t hlt; omega
    simp only [fin5746_val _ hj']; rw [rq k.val k.isLt t ht, Rat.num_intCast]
  · intro k
    have hb := (chkB_spec k.val k.isLt).2.2.2
    have hb' : ((((fsl k).map (fun t => (mfz k t).natAbs)).sum +
        ((rsl k).map (fun t => (mrz k t).natAbs * bk (rJ t))).sum : ℕ) : ℤ) ≤ (bk k.val : ℤ) := by exact_mod_cast hb
    refine le_trans (le_of_eq ?_) hb'
    rw [fld_slice, ref_slice, List.map_map, List.map_map, Nat.cast_add, Nat.cast_list_sum, Nat.cast_list_sum,
      List.map_map, List.map_map]
    congr 1
    · congr 1; apply List.map_congr_left; intro t ht
      simp only [Function.comp]; rw [fq k.val k.isLt t ht, Rat.num_intCast, Int.natCast_natAbs]
    · congr 1; apply List.map_congr_left; intro t ht
      have hlt := rsl_lt k.val k.isLt t ht
      have hj' : cg RJW 13 t < 5746 := by have := termR t hlt; omega
      simp only [Function.comp, fin5746_val _ hj']
      rw [rq k.val k.isLt t ht, Rat.num_intCast, Nat.cast_mul, Int.natCast_natAbs, rJ_eq t hlt]

theorem outVec_eq (f : Fin 1262) : outVec Recipe7761 (ofld7761 f) (oref7761 f) =
    ((oref7761 f).map fun p => p.1 • dRec Recipe7761 p.2).sum := by
  simp [outVec, ofld7761]

/-- the output side in one block: D_f * outVec f and D_f * O f are equal on columns b0..b0+255. -/
theorem block_ok (b0 : ℕ) (qt : BT ℤ) (hC : ∀ k, k < 5746 → chkBank b0 qt k = true)
    (hOut : ∀ p, p < 1262 → chkOut b0 qt p = true) (f : Fin 1262) (g : Fin 1262)
    (hg : b0 ≤ g.val ∧ g.val < b0 + 256) :
    outVec Recipe7761 (ofld7761 f) (oref7761 f) g = O7761 f g := by
  have hdf := (chkOB_spec f.val f.isLt).1
  -- (1) D_f * E(outVec f) = tgt
  have h1 : (df f.val : ℚ) * EB 1262 b0 256 ((2:ℚ) ^ 72) (outVec Recipe7761 (ofld7761 f) (oref7761 f)) = (tgt b0 f.val : ℚ) := by
    have h := hOut (sg f.val) (sgtu _ f.isLt).1
    simp only [chkOut, beq_iff_eq, (sgtu _ f.isLt).2] at h
    rw [← h, outVec_eq, map_list_sum, out_slice, List.map_map, List.map_map, ← List.sum_map_mul_left,
      Int.cast_list_sum, List.map_map]
    congr 1; apply List.map_congr_left; intro t ht
    have hlt := osl_lt (sg f.val) (sgtu _ f.isLt).1 t ht
    have hj' : cg OJW 13 t < 5746 := (termO t hlt).1
    simp only [Function.comp, map_smul, smul_eq_mul, oterm, Int.cast_mul]
    have hp := packed_blk b0 qt hC (fin5746 (cg OJW 13 t))
    rw [fin5746_val _ hj'] at hp
    have hd : (0:ℚ) < dk (cg OJW 13 t) := by exact_mod_cast dk_pos _ hj'
    rw [← oq f.val f.isLt t ht, oJ_eq t hlt, ← hp]; field_simp
  -- (2) D_f * E(O f) = tgt
  have h2 : (df f.val : ℚ) * EB 1262 b0 256 ((2:ℚ) ^ 72) (O7761 f) = (tgt b0 f.val : ℚ) := by
    rw [O_row, map_add, map_smul, smul_eq_mul, EB_single]
    unfold tgt
    rw [Int.cast_add, mul_add]
    congr 1
    · split_ifs with hb
      · rw [Int.cast_mul, pw_cast, ← ddq f.val f.isLt]; ring
      · simp
    · by_cases ho : oov f ≠ 0
      · obtain ⟨hp, -, -⟩ := chkP f f.isLt ho
        rw [if_pos ho, map_smul, smul_eq_mul, EB_single, fin1262_val _ hp]
        have ho' := (oov_ne f.val f.isLt).1 ho
        show _ = ((if nz (sx OPK 32 f.val) ≠ 0 ∧ b0 ≤ pip f.val ∧ pip f.val < b0 + 256 then
          mop f.val * pw (pip f.val - b0) else 0 : ℤ) : ℚ)
        by_cases hb : b0 ≤ pip f.val ∧ pip f.val < b0 + 256
        · rw [if_pos hb, if_pos ⟨ho', hb⟩, Int.cast_mul, pw_cast, ← opq f.val f.isLt]; ring
        · rw [if_neg hb, if_neg (fun h => hb h.2)]; simp
      · rw [if_neg ho, map_zero, mul_zero]
        have ho' : ¬ nz (sx OPK 32 f.val) ≠ 0 := fun h => ho ((oov_ne f.val f.isLt).2 h)
        show (0:ℚ) = ((if nz (sx OPK 32 f.val) ≠ 0 ∧ b0 ≤ pip f.val ∧ pip f.val < b0 + 256 then
          mop f.val * pw (pip f.val - b0) else 0 : ℤ) : ℚ)
        rw [if_neg (fun h => ho' h.1)]; simp
  -- (3) integer digits with bound < 2^72
  set u : Fin 1262 → ℚ := fun g => (df f.val : ℚ) * (outVec Recipe7761 (ofld7761 f) (oref7761 f) g - O7761 f g)
  have hu0 : EB 1262 b0 256 ((2:ℚ) ^ 72) u = 0 := by
    have : u = (df f.val : ℚ) • (outVec Recipe7761 (ofld7761 f) (oref7761 f) - O7761 f) := by
      funext g; simp [u]
    rw [this, map_smul, map_sub, smul_eq_mul, mul_sub, h1, h2, sub_self]
  have hB := (chkOB_spec f.val f.isLt).2.2.2.2.2.2
  have hIB : ∀ g, IB (u g) ((((osl (sg f.val)).map (fun t => (moz f.val t).natAbs * bk (oJ t))).sum +
      (mdd f.val).natAbs + (mop f.val).natAbs : ℕ) : ℤ) := by
    intro g
    have hA : IB ((df f.val : ℚ) * outVec Recipe7761 (ofld7761 f) (oref7761 f) g)
        (((osl (sg f.val)).map (fun t => (((moz f.val t).natAbs * bk (oJ t) : ℕ) : ℤ))).sum) := by
      rw [outVec_eq, lsum_apply, ← List.sum_map_mul_left, out_slice, List.map_map]
      refine IB_sum _ _ _ (fun t ht => ?_)
      have hlt := osl_lt (sg f.val) (sgtu _ f.isLt).1 t ht
      have hj' : cg OJW 13 t < 5746 := (termO t hlt).1
      simp only [Function.comp, Pi.smul_apply, smul_eq_mul]
      have hd : (0:ℚ) < dk (cg OJW 13 t) := by exact_mod_cast dk_pos _ hj'
      have e : (df f.val : ℚ) * (cq OCW t * dRec Recipe7761 (fin5746 (cg OJW 13 t)) g) =
          (moz f.val t : ℚ) * ((dk (cg OJW 13 t) : ℚ) * dRec Recipe7761 (fin5746 (cg OJW 13 t)) g) := by
        rw [← oq f.val f.isLt t ht]; field_simp
      rw [e]
      have := IB_mul (bound7761 (fin5746 (cg OJW 13 t)) g) (moz f.val t)
      rw [fin5746_val _ hj'] at this
      refine IB_mono this (le_of_eq ?_)
      rw [oJ_eq t hlt]; push_cast; ring
    have hO : IB ((df f.val : ℚ) * O7761 f g) (((mdd f.val).natAbs + (mop f.val).natAbs : ℕ) : ℤ) := by
      rw [O_row]
      simp only [Pi.add_apply, Pi.smul_apply, smul_eq_mul]
      have hm : 0 ≤ (((mop f.val).natAbs : ℕ) : ℤ) := by positivity
      have hd0 : 0 ≤ (((mdd f.val).natAbs : ℕ) : ℤ) := by positivity
      by_cases hg1 : g = f
      · rw [hg1, Pi.single_eq_same]
        by_cases ho : oov f ≠ 0
        · obtain ⟨hp, hne, -⟩ := chkP f f.isLt ho
          have hne' : f ≠ fin1262 (pip f) := fun e => hne (by have := congrArg Fin.val e; rw [fin1262_val _ hp] at this; exact this.symm)
          rw [if_pos ho, Pi.smul_apply, Pi.single_eq_of_ne hne', smul_zero, add_zero, mul_one, ddq f.val f.isLt]
          exact ⟨mdd f.val, rfl, by push_cast; linarith [abs_nonneg (mop f.val)]⟩
        · rw [if_neg ho, Pi.zero_apply, add_zero, mul_one, ddq f.val f.isLt]
          exact ⟨mdd f.val, rfl, by push_cast; linarith [abs_nonneg (mop f.val)]⟩
      · rw [Pi.single_eq_of_ne hg1, mul_zero, zero_add]
        by_cases ho : oov f ≠ 0
        · rw [if_pos ho, Pi.smul_apply, smul_eq_mul]
          by_cases hg2 : g = fin1262 (pip f)
          · subst hg2; rw [Pi.single_eq_same, mul_one, opq f.val f.isLt]
            exact ⟨mop f.val, rfl, by push_cast; linarith [abs_nonneg (mdd f.val)]⟩
          · rw [Pi.single_eq_of_ne hg2, mul_zero, mul_zero]; exact ⟨0, by simp, by push_cast; positivity⟩
        · rw [if_neg ho, Pi.zero_apply, mul_zero]; exact ⟨0, by simp, by push_cast; positivity⟩
    obtain ⟨z1, hz1, hb1⟩ := hA
    obtain ⟨z2, hz2, hb2⟩ := hO
    refine ⟨z1 - z2, ?_, ?_⟩
    · simp only [u]; rw [mul_sub, hz1, hz2]; push_cast; ring
    · refine (abs_sub _ _).trans ?_
      have : ((osl (sg f.val)).map (fun t => (((moz f.val t).natAbs * bk (oJ t) : ℕ) : ℤ))).sum =
          ((((osl (sg f.val)).map (fun t => (moz f.val t).natAbs * bk (oJ t))).sum : ℕ) : ℤ) := by
        rw [Nat.cast_list_sum, List.map_map]; rfl
      rw [this] at hb1; push_cast at hb1 hb2 ⊢; linarith
  -- (4) digits
  choose z hz hzb using hIB
  have hzX : ∀ g, |z g| < 2 ^ 72 := fun g => lt_of_le_of_lt (hzb g) (by exact_mod_cast hB)
  set v : ℕ → ℤ := fun i => if h : b0 + i < 1262 then z ⟨b0 + i, h⟩ else 0
  have hv : ∀ i < 256, |v i| < 2 ^ 72 := by
    intro i _; simp only [v]; split_ifs
    · exact hzX _
    · simp
  have hsum : ∑ i ∈ range 256, v i * (2 ^ 72 : ℤ) ^ i = 0 := by
    have : EB 1262 b0 256 ((2:ℚ) ^ 72) u = ((∑ i ∈ range 256, v i * (2 ^ 72 : ℤ) ^ i : ℤ) : ℚ) := by
      rw [EB_apply]; push_cast
      refine Finset.sum_congr rfl fun i _ => ?_
      simp only [v]; split_ifs with h
      · rw [hz]; norm_num
      · simp
    rw [hu0] at this; exact_mod_cast this.symm
  have hz0 := digits_zero (2 ^ 72) (by positivity) 256 v hv hsum (g.val - b0) (by omega)
  have hgv : v (g.val - b0) = z g := by
    simp only [v]; rw [dif_pos (by omega)]; congr 1; ext; simp; omega
  rw [hgv] at hz0
  have hug : u g = 0 := by rw [hz, hz0]; simp
  simp only [u] at hug
  have : (df f.val : ℚ) ≠ 0 := by exact_mod_cast hdf.ne'
  have := (mul_eq_zero.1 hug).resolve_left this
  linarith

/-- **hO for #7761** (BRIDGE-OUT's goal): the single remaining hypothesis of `Net7761`. -/
theorem hO7761 : ∀ f, outVec Recipe7761 (ofld7761 f) (oref7761 f) = O7761 f := by
  intro f; funext g
  have hg := g.isLt
  rcases (show g.val < 256 ∨ (256 ≤ g.val ∧ g.val < 512) ∨ (512 ≤ g.val ∧ g.val < 768) ∨
      (768 ≤ g.val ∧ g.val < 1024) ∨ 1024 ≤ g.val by omega) with h | h | h | h | h
  · exact block_ok 0 QT0 allC0 allO0 f g ⟨by omega, by omega⟩
  · exact block_ok 256 QT1 allC1 allO1 f g ⟨by omega, by omega⟩
  · exact block_ok 512 QT2 allC2 allO2 f g ⟨by omega, by omega⟩
  · exact block_ok 768 QT3 allC3 allO3 f g ⟨by omega, by omega⟩
  · exact block_ok 1024 QT4 allC4 allO4 f g ⟨by omega, by omega⟩

/-- the #7761 Net, unconditional. -/
noncomputable def Net7761' := Net7761 hO7761

end Bridge7761
#print axioms Bridge7761.hO7761
