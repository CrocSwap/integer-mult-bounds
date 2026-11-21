import Nov15.DataIdA
import Nov15.DataIdF
import Nov15.BlockComplete
import Nov15.LinP104FreeInst
/-!
DATAID part B: thin wrappers.  Restates the P104 headline theorems in terms of the DEFINED objects
(E8 roots `rootAt`, pattern `Qroot` from the roots, coordinates `coordAt` of the roots in the Z-basis beta,
frames = orthogonal 8-subsets).  Each wrapper rewrites the embedded data by the equalities proved in
DataIdA / DataIdF and applies the existing theorem.
-/
set_option Elab.async false
open Matrix Finset LinCore LinFinal
namespace DataId

/-- the embedded pattern Qlab (from labels.txt) IS the pattern of the roots: Q_ts = 1 iff <r_t,r_s> even -/
theorem Qlab_eq_Qroot (t s : Fin 104) : P104.Qlab t s = Qroot t s := by
  have h := Qlab_eq_Qroot_all t.1 t.2
  unfold rowQOK at h
  rw [List.all_eq_true] at h
  have h2 := h s.1 (List.mem_range.2 s.2)
  simp only [beq_iff_eq] at h2
  exact h2

theorem Qlab_funext : P104.Qlab = Qroot := funext fun t => funext fun s => Qlab_eq_Qroot t s

/-- the embedded F2^8 labels ARE the coordinates of the port roots in the Z-basis beta, mod 2 -/
theorem lab_eq_coord (t : Fin 104) (i : Fin 8) : P104.lab t i = ((coordAt t.1 i.1 : ℤ) : ZMod 2) := by
  have h := xMasks_is_coord_mod2
  rw [List.all_eq_true] at h
  have h1 := h t.1 (List.mem_range.2 t.2)
  rw [List.all_eq_true] at h1
  have h2 := h1 i.1 (List.mem_range.2 i.2)
  simp only [beq_iff_eq] at h2
  have hc : ((coordAt t.1 i.1 : ℤ) : ZMod 2) = (((coordAt t.1 i.1 % 2 : ℤ)) : ZMod 2) :=
    (ZMod.intCast_mod _ 2).symm
  have hr : coordAt t.1 i.1 % 2 = 0 ∨ coordAt t.1 i.1 % 2 = 1 := by omega
  unfold P104.lab P104.cm
  rcases hr with hr | hr
  · have hb : (P104Data.xMasks.getD t.1 0).testBit i.1 = false := by
      rw [h2]; simp [hr]
    rw [hc, hr, hb]; simp
  · have hb : (P104Data.xMasks.getD t.1 0).testBit i.1 = true := by
      rw [h2]; simp [hr]
    rw [hc, hr, hb]; simp

/-- HEADLINE (E8 form).  Every Z/4-linear half-integer decoder for the P104 ports has cost >= 56.
    P104 = the 104 E8 root lines `rootAt t` (standard coordinates, see DataIdA); Q_ts = [<r_t, r_s> even];
    the integer lift `ct` of the labels is any lift of the coordinates of r_t in the Z-basis beta of E8
    (reduced mod 2).  Unconditional on the data tables: they are proved above to be these objects. -/
theorem p104_linear_cost_ge_E8 {κ : Type*} [DecidableEq κ] {J : Finset κ} {w v : κ → Fin 104 → ℤ}
    {x y : κ → Fin 8 → ℤ} {ct : Fin 104 → Fin 8 → ℤ}
    (hct : ∀ (t : Fin 104) (i : Fin 8), ((ct t i : ℤ) : ZMod 2) = ((coordAt t.1 i.1 : ℤ) : ZMod 2))
    (hw : ∀ k ∈ J, ∀ t, w k t ≡ ∑ i, x k i * ct t i [ZMOD 4])
    (hv : ∀ k ∈ J, ∀ t, v k t ≡ ∑ i, y k i * ct t i [ZMOD 4])
    (hdec : ∀ t s, ∑ k ∈ J, w k t * v k s * Qroot t s = if t = s then 2 else 0) :
    56 ≤ ∑ k ∈ J, (Doubling.Qk Qroot (w k) (v k)).rank := by
  have Z : P104.Z4Lin J w v x y ct :=
    { hct := fun t i => by rw [hct, lab_eq_coord]
      hw := hw
      hv := hv }
  have := P104.p104_linear_cost_ge_free Z (by simpa only [Qlab_funext] using hdec)
  simpa only [Qlab_funext] using this

/-- non-vacuity: the honest E8 linear decoder (LinP104FreeInst) satisfies every hypothesis of the E8 form -/
theorem nonvac_E8 :
    56 ≤ ∑ k : Fin 8, (Doubling.Qk Qroot (P104.wI k) (P104.vI k)).rank := by
  refine p104_linear_cost_ge_E8 (J := Finset.univ) (x := P104.xE) (y := P104.yG) (ct := P104.ctI) ?_ ?_ ?_ ?_
  · intro t i; rw [← lab_eq_coord]; exact P104.Z4_I.hct t i
  · exact P104.Z4_I.hw
  · exact P104.Z4_I.hv
  · intro t s; rw [← Qlab_funext]; exact P104.hdec_I t s

/-! ### frames -/
open FrameCert in
/-- F^perp (vectors even on every one of the 759 packed frames) = vectors even on every orthogonal 8-frame
    of the defined P104 (increasing index lists of 8 ports with pairwise orthogonal roots) -/
theorem Fperp_iff_orth (x : Fin 104 → ZMod 2) :
    x ∈ Fperp ↔ ∀ l : List Nat, (l.length = 8 ∧ l.Sublist (List.range 104) ∧
        l.Pairwise (fun a b => dot (rootAt a) (rootAt b) = 0)) →
      ∑ i : Fin 104, (if l.contains i.val then x i else 0) = 0 := by
  unfold Fperp
  simp only [Set.mem_ofPred_eq]
  constructor
  · intro h l hl
    have hm : maskOfList l ∈ FrameCert.frames := (frames_mask_iff _).2 ⟨l, (frames_exact l).1 hl, rfl⟩
    have := h _ hm
    unfold FrameCert.dot at this
    simpa only [maskOfList_testBit] using this
  · intro h m hm
    obtain ⟨l, hl, rfl⟩ := (frames_mask_iff m).1 hm
    have := h l ((frames_exact l).2 hl)
    unfold FrameCert.dot
    simpa only [maskOfList_testBit] using this

open FrameCert in
/-- all_or_nothing_real, with the frame hypothesis stated on the defined orthogonal frames -/
theorem all_or_nothing_E8 (c : List Nat) (hc : c ∈ certs) (A B : Finset (Fin 104))
    (H_FS4 : ∀ l : List Nat, (l.length = 8 ∧ l.Sublist (List.range 104) ∧
        l.Pairwise (fun a b => dot (rootAt a) (rootAt b) = 0)) →
      ∑ i : Fin 104, (if l.contains i.val then ind (A ∩ B) i else 0) = 0)
    (H_supp : A ⊆ lamSet (lamMask (cu1 c) (cu2 c))) :
    A ∩ B = ∅ ∨ (A = lamSet (lamMask (cu1 c) (cu2 c)) ∧ lamSet (lamMask (cu1 c) (cu2 c)) ⊆ B) :=
  all_or_nothing_real c hc A B ((Fperp_iff_orth _).2 H_FS4) H_supp

/-! ### the Lam sections: lamMask u1 u2 = ports whose 9-bit label is orthogonal to both normals -/
open FrameCert in
/-- F2 inner product of a 9-bit label with a normal -/
def dot9 (lab u : Nat) : Bool :=
  (List.range 9).foldl (fun b j => if u.testBit j then xor b (lab.testBit j) else b) false

theorem foldl_col (j : Nat) : ∀ (L : List Nat) (init t : Nat),
    (L.foldl (fun a t' => if (FrameCert.labelAt t').testBit j then a ||| 2 ^ t' else a) init).testBit t =
      (init.testBit t || (L.contains t && (FrameCert.labelAt t).testBit j)) := by
  intro L
  induction L with
  | nil => intro init t; simp
  | cons t0 L ih =>
    intro init t
    simp only [List.foldl_cons]
    by_cases hl : (FrameCert.labelAt t0).testBit j = true
    · rw [if_pos hl, ih, Nat.testBit_or, Nat.testBit_two_pow]
      by_cases ht : t0 = t
      · subst ht; simp [hl, List.contains_cons]
      · have ht' : ¬ t = t0 := fun h => ht h.symm
        simp [ht, ht', List.contains_cons]
    · rw [if_neg hl, ih]
      by_cases ht : t0 = t
      · subst ht; simp [hl, List.contains_cons]
      · have ht' : ¬ t = t0 := fun h => ht h.symm
        simp [ht, ht', List.contains_cons]

theorem colMask_testBit (j t : Nat) (ht : t < 104) :
    (FrameCert.colMask j).testBit t = (FrameCert.labelAt t).testBit j := by
  unfold FrameCert.colMask
  rw [foldl_col]
  simp [List.contains_iff_mem, List.mem_range, ht]

theorem foldl_par (u t : Nat) (ht : t < 104) : ∀ (L : List Nat) (init : Nat),
    (L.foldl (fun a j => if u.testBit j then a ^^^ FrameCert.colMask j else a) init).testBit t =
      L.foldl (fun b j => if u.testBit j then xor b ((FrameCert.labelAt t).testBit j) else b) (init.testBit t) := by
  intro L
  induction L with
  | nil => intro init; simp
  | cons j L ih =>
    intro init
    simp only [List.foldl_cons]
    by_cases hu : u.testBit j = true
    · rw [if_pos hu, if_pos hu, ih, Nat.testBit_xor, colMask_testBit j t ht]
    · rw [if_neg hu, if_neg hu, ih]

theorem lamMask_testBit (u1 u2 t : Nat) (ht : t < 104) :
    (FrameCert.lamMask u1 u2).testBit t =
      (!(dot9 (FrameCert.labelAt t) u1) && !(dot9 (FrameCert.labelAt t) u2)) := by
  unfold FrameCert.lamMask FrameCert.parMask
  rw [Nat.testBit_xor, Nat.testBit_or, Nat.testBit_two_pow_sub_one, foldl_par u1 t ht, foldl_par u2 t ht]
  simp [ht, dot9]

/-- Lam(u1,u2) = ports whose label (= labels.txt) is orthogonal to both normals -/
theorem mem_lamSet_iff (u1 u2 : Nat) (i : Fin 104) :
    i ∈ FrameCert.lamSet (FrameCert.lamMask u1 u2) ↔
      (dot9 (P104Data.labMasks.getD i.1 0) u1 = false ∧ dot9 (P104Data.labMasks.getD i.1 0) u2 = false) := by
  have hl : FrameCert.labelAt i.1 = P104Data.labMasks.getD i.1 0 := by
    have h := labels_agree
    rw [List.all_eq_true] at h
    simpa using h i.1 (List.mem_range.2 i.2)
  unfold FrameCert.lamSet
  rw [Finset.mem_filter, lamMask_testBit u1 u2 i.1 i.2, hl]
  simp

open FrameCert in
/-- block_complete, with the blocking hypothesis stated on the defined orthogonal frames and the label
    orthogonality (labels.txt) spelled out: every 7-dim section (two distinct nonzero normals) meeting every
    orthogonal 8-frame of the ports has the Lam of one of the 1152 certified ones. -/
theorem block_complete_E8 (u1 u2 : Nat) (h1 : 0 < u1) (h2 : 0 < u2) (hne : u1 ≠ u2)
    (h1' : u1 < 512) (h2' : u2 < 512)
    (hb : ∀ l : List Nat, (l.length = 8 ∧ l.Sublist (List.range 104) ∧
        l.Pairwise (fun a b => dot (rootAt a) (rootAt b) = 0)) →
      ∃ j ∈ l, dot9 (P104Data.labMasks.getD j 0) u1 = false ∧ dot9 (P104Data.labMasks.getD j 0) u2 = false) :
    ∃ c ∈ certs, lamMask (cu1 c) (cu2 c) = lamMask u1 u2 := by
  refine BlockComplete.block_complete u1 u2 h1 h2 hne h1' h2' ?_
  intro i hi
  have hm : frameAt i ∈ FrameCert.frames := by
    unfold FrameCert.frames; exact List.mem_map.2 ⟨i, List.mem_range.2 hi, rfl⟩
  obtain ⟨l, hl, hml⟩ := (frames_mask_iff _).1 hm
  obtain ⟨j, hj, hj1, hj2⟩ := hb l ((frames_exact l).2 hl)
  have hjl : j < 104 := List.mem_range.1 ((((frames_exact l).2 hl).2.1).subset hj)
  intro h0
  have hbit : (frameAt i &&& lamMask u1 u2).testBit j = true := by
    rw [Nat.testBit_and, ← hml, maskOfList_testBit]
    have hlam : (lamMask u1 u2).testBit j = true := by
      have := (mem_lamSet_iff u1 u2 ⟨j, hjl⟩).2 ⟨hj1, hj2⟩
      unfold FrameCert.lamSet at this
      exact (Finset.mem_filter.1 this).2
    rw [hlam]; simpa using hj
  rw [h0] at hbit
  simp at hbit

#print axioms DataId.block_complete_E8
#print axioms DataId.mem_lamSet_iff

/-- binvMasks is the F2-inverse of bmMasks (= Gram of beta mod 2): already kernel-proved in LinP104Base -/
theorem binv_is_inverse : P104.Binv * P104.Bm = 1 := P104.Binv_mul

#print axioms DataId.binv_is_inverse
#print axioms DataId.p104_linear_cost_ge_E8
#print axioms DataId.nonvac_E8
#print axioms DataId.Fperp_iff_orth
#print axioms DataId.all_or_nothing_E8
#print axioms DataId.lab_eq_coord
#print axioms DataId.Qlab_eq_Qroot
end DataId
