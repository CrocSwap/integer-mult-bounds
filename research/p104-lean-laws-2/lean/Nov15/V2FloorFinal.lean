/-
V2FloorFinal: the certified V2-FLOOR numbers (lane LEAN-NEXT20, Nov 16). See V2FloorCert.md.

  joint α+β (θ = 22257/2^19, JB):  1,839,727,178,682 / 2^30 = 1,713.38… ≤ cost(E)
  β only    (θ = 1, JB):           1,536,575,200,417 / 2^30 = 1,431.05… ≤ cost(E)

for every plan E (strict containments between subspaces of F₂⁹, dims 1..8 priced by w_θ) that realises every pair,
GIVEN `IntFeasible` for the certificate (check.c's per-edge inequality). Everything else — weak duality, the
data-dependent side conditions, the sums, and the log arithmetic in the thresholds — is proved here or in the imports.
-/
import Nov15.V2FloorChk_j_0
import Nov15.V2FloorChk_sj_0
import Nov15.V2FloorChk_j_250
import Nov15.V2FloorChk_sj_250
import Nov15.V2FloorChk_j_500
import Nov15.V2FloorChk_sj_500
import Nov15.V2FloorChk_j_750
import Nov15.V2FloorChk_sj_750
import Nov15.V2FloorChk_j_1000
import Nov15.V2FloorChk_sj_1000
import Nov15.V2FloorChk_j_1250
import Nov15.V2FloorChk_sj_1250
import Nov15.V2FloorChk_j_1500
import Nov15.V2FloorChk_sj_1500
import Nov15.V2FloorChk_j_1750
import Nov15.V2FloorChk_sj_1750
import Nov15.V2FloorChk_j_2000
import Nov15.V2FloorChk_sj_2000
import Nov15.V2FloorChk_j_2250
import Nov15.V2FloorChk_sj_2250
import Nov15.V2FloorChk_j_2500
import Nov15.V2FloorChk_sj_2500
import Nov15.V2FloorChk_b_0
import Nov15.V2FloorChk_sb_0
import Nov15.V2FloorChk_b_250
import Nov15.V2FloorChk_sb_250
import Nov15.V2FloorChk_b_500
import Nov15.V2FloorChk_sb_500
import Nov15.V2FloorChk_b_750
import Nov15.V2FloorChk_sb_750
import Nov15.V2FloorChk_b_1000
import Nov15.V2FloorChk_sb_1000
import Nov15.V2FloorChk_b_1250
import Nov15.V2FloorChk_sb_1250
import Nov15.V2FloorChk_b_1500
import Nov15.V2FloorChk_sb_1500
import Nov15.V2FloorChk_b_1750
import Nov15.V2FloorChk_sb_1750

set_option maxRecDepth 100000
set_option maxHeartbeats 0

namespace V2Floor
open Finset


theorem Lsub_ne_bot (B : List ℕ) (hB : B ≠ []) (h : vec (B.headD 0) ≠ 0) : Lsub B ≠ ⊥ := by
  intro hb; apply h
  have hm : vec (B.headD 0) ∈ Lsub B := by
    apply Submodule.subset_span
    obtain ⟨a, t, rfl⟩ := List.exists_cons_of_ne_nil hB
    simp
  rw [hb] at hm; simpa using hm

theorem Usub_ne_top (H : List ℕ) (hH : H ≠ []) (j : Fin 9) (hj : vec (H.headD 0) j = 1) : Usub H ≠ ⊤ := by
  intro ht
  have hm : (Pi.single j 1 : Vec) ∈ Usub H := ht ▸ Submodule.mem_top
  obtain ⟨a, t, rfl⟩ := List.exists_cons_of_ne_nil hH
  rw [Usub, LinearMap.mem_ker] at hm
  have h0 := congrFun hm ⟨0, by simp⟩
  simp [Matrix.mulVecLin_apply, Matrix.mulVec, dotProduct, Pi.single_apply] at h0
  simp at hj
  rw [hj] at h0; exact one_ne_zero h0

section joint

theorem ok_all_j : ∀ i < N_joint, okj i = true := by
  intro i hi
  unfold N_joint at hi

  by_cases h0 : i < 250
  · have := ok_j_0 (i - 0) (by omega); rwa [show 0 + (i - 0) = i by omega] at this

  by_cases h1 : i < 500
  · have := ok_j_250 (i - 250) (by omega); rwa [show 250 + (i - 250) = i by omega] at this

  by_cases h2 : i < 750
  · have := ok_j_500 (i - 500) (by omega); rwa [show 500 + (i - 500) = i by omega] at this

  by_cases h3 : i < 1000
  · have := ok_j_750 (i - 750) (by omega); rwa [show 750 + (i - 750) = i by omega] at this

  by_cases h4 : i < 1250
  · have := ok_j_1000 (i - 1000) (by omega); rwa [show 1000 + (i - 1000) = i by omega] at this

  by_cases h5 : i < 1500
  · have := ok_j_1250 (i - 1250) (by omega); rwa [show 1250 + (i - 1250) = i by omega] at this

  by_cases h6 : i < 1750
  · have := ok_j_1500 (i - 1500) (by omega); rwa [show 1500 + (i - 1500) = i by omega] at this

  by_cases h7 : i < 2000
  · have := ok_j_1750 (i - 1750) (by omega); rwa [show 1750 + (i - 1750) = i by omega] at this

  by_cases h8 : i < 2250
  · have := ok_j_2000 (i - 2000) (by omega); rwa [show 2000 + (i - 2000) = i by omega] at this

  by_cases h9 : i < 2500
  · have := ok_j_2250 (i - 2250) (by omega); rwa [show 2250 + (i - 2250) = i by omega] at this

  have := ok_j_2500 (i - 2500) (by omega); rwa [show 2500 + (i - 2500) = i by omega] at this

theorem okj_spec (i : ℕ) (h : okj i = true) :
    (D_joint.get i).1 ≠ [] ∧ vec ((D_joint.get i).1.headD 0) ≠ 0 ∧ (D_joint.get i).2.1 ≠ [] ∧
    (∃ j : Fin 9, vec ((D_joint.get i).2.1.headD 0) j = 1) ∧ (D_joint.get i).2.2.length = 9 ∧
    ∀ k < 9, (D_joint.get i).2.2.getD k 0 = 0 ∨ ((D_joint.get i).1.length ≤ k ∧ k < 9 - (D_joint.get i).2.1.length) := by
  simp only [okj, Bool.and_eq_true, bne_iff_ne, ne_eq, decide_eq_true_eq, List.any_eq_true, List.mem_finRange,
    true_and, beq_iff_eq, List.all_eq_true, List.mem_range, Bool.or_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, h5⟩, h6⟩ := h
  exact ⟨h1, h2, h3, h4, h5, fun k hk => by have := h6 k hk; simpa using this⟩

theorem tsumj_add (lo m : ℕ) : ∀ n, tsumj lo (m + n) = tsumj lo m + tsumj (lo + m) n
  | 0 => rfl
  | n + 1 => by
    show tsumj lo (m + n) + _ = tsumj lo m + (tsumj (lo + m) n + _)
    rw [tsumj_add lo m n, Nat.add_assoc, Nat.add_assoc lo m n]; rfl

theorem tsumj_eq (n : ℕ) : (∑ i ∈ range n, ∑ k ∈ range 9, (D_joint.get i).2.2.getD k 0) = tsumj 0 n := by
  induction n with
  | zero => rfl
  | succ n ih => rw [Finset.sum_range_succ, ih]; show _ = tsumj 0 n + _; rw [Nat.zero_add]

theorem totj : tsumj 0 N_joint = 1839727178682 := by
  have e0 : tsumj 0 250 = 104621675572 := sum_j_0
  have e1 : tsumj 0 500 = 182007046432 := by
    rw [show (500 : ℕ) = 250 + 250 from rfl, tsumj_add, e0, show (0 + 250 : ℕ) = 250 from rfl, sum_j_250]
  have e2 : tsumj 0 750 = 253624075526 := by
    rw [show (750 : ℕ) = 500 + 250 from rfl, tsumj_add, e1, show (0 + 500 : ℕ) = 500 from rfl, sum_j_500]
  have e3 : tsumj 0 1000 = 318110314338 := by
    rw [show (1000 : ℕ) = 750 + 250 from rfl, tsumj_add, e2, show (0 + 750 : ℕ) = 750 from rfl, sum_j_750]
  have e4 : tsumj 0 1250 = 380459795092 := by
    rw [show (1250 : ℕ) = 1000 + 250 from rfl, tsumj_add, e3, show (0 + 1000 : ℕ) = 1000 from rfl, sum_j_1000]
  have e5 : tsumj 0 1500 = 763285491633 := by
    rw [show (1500 : ℕ) = 1250 + 250 from rfl, tsumj_add, e4, show (0 + 1250 : ℕ) = 1250 from rfl, sum_j_1250]
  have e6 : tsumj 0 1750 = 1017053286584 := by
    rw [show (1750 : ℕ) = 1500 + 250 from rfl, tsumj_add, e5, show (0 + 1500 : ℕ) = 1500 from rfl, sum_j_1500]
  have e7 : tsumj 0 2000 = 1296020790892 := by
    rw [show (2000 : ℕ) = 1750 + 250 from rfl, tsumj_add, e6, show (0 + 1750 : ℕ) = 1750 from rfl, sum_j_1750]
  have e8 : tsumj 0 2250 = 1492308852917 := by
    rw [show (2250 : ℕ) = 2000 + 250 from rfl, tsumj_add, e7, show (0 + 2000 : ℕ) = 2000 from rfl, sum_j_2000]
  have e9 : tsumj 0 2500 = 1731513690868 := by
    rw [show (2500 : ℕ) = 2250 + 250 from rfl, tsumj_add, e8, show (0 + 2250 : ℕ) = 2250 from rfl, sum_j_2250]
  have e10 : tsumj 0 2625 = 1839727178682 := by
    rw [show (2625 : ℕ) = 2500 + 125 from rfl, tsumj_add, e9, show (0 + 2500 : ℕ) = 2500 from rfl, sum_j_2500]
  exact e10


/-- **V2-FLOOR, joint α+β (JB): every plan realising all 2,625 pairs costs ≥ 1839727178682 / 2^30**, given the certificate's
edge feasibility `IntFeasible` (what check.c verifies). -/
theorem floor_joint (hfeas : IntFeasible (fun p => Lsub (LBj p)) (fun p => Usub (UHj p)) numj T_joint)
    (E : Finset (Sub × Sub)) (hE : ∀ e ∈ E, e.1 < e.2) (hreal : ∀ p, Reach E (Lsub (LBj p)) (Usub (UHj p))) :
    (1839727178682 : ℝ) / 2 ^ 30 ≤ ∑ e ∈ E, wcut (22257 / 524288) (fdim e.1) (fdim e.2) := by
  have sp := fun (p : Fin N_joint) => okj_spec p.val (ok_all_j p.val p.isLt)
  have h := floor_F2 LBj UHj numj (22257 / 524288) T_joint (fun a b h1 hab h8 => T_joint_le a b h1 hab h8)
    (fun p => Lsub_ne_bot _ (sp p).1 (sp p).2.1)
    (fun p => by obtain ⟨j, hj⟩ := (sp p).2.2.2.1; exact Usub_ne_top _ (sp p).2.2.1 j hj)
    (fun p k hk => by
      by_cases k9 : k < 9
      · rcases (sp p).2.2.2.2.2 k k9 with h0 | h0
        · exact absurd h0 hk
        · exact h0
      · exfalso; apply hk; unfold numj
        have hl := (sp p).2.2.2.2.1
        rw [List.getD_eq_getElem?_getD, List.getElem?_eq_none (by omega)]; rfl)
    (fun p k hk => by
      unfold numj; have hl := (sp p).2.2.2.2.1
      rw [List.getD_eq_getElem?_getD, List.getElem?_eq_none (by omega)]; rfl)
    hfeas E hE hreal
  have ht : (∑ p : Fin N_joint, ∑ k ∈ range 9, (numj p k : ℝ)) = 1839727178682 := by
    have e1 := Fin.sum_univ_eq_sum_range (fun i => ∑ k ∈ range 9, (D_joint.get i).2.2.getD k 0) N_joint
    rw [tsumj_eq, totj] at e1
    have e2 : (∑ p : Fin N_joint, ∑ k ∈ range 9, numj p k) = 1839727178682 := e1
    exact_mod_cast e2
  rwa [ht] at h

end joint

section beta

theorem ok_all_b : ∀ i < N_beta, okb i = true := by
  intro i hi
  unfold N_beta at hi

  by_cases h0 : i < 250
  · have := ok_b_0 (i - 0) (by omega); rwa [show 0 + (i - 0) = i by omega] at this

  by_cases h1 : i < 500
  · have := ok_b_250 (i - 250) (by omega); rwa [show 250 + (i - 250) = i by omega] at this

  by_cases h2 : i < 750
  · have := ok_b_500 (i - 500) (by omega); rwa [show 500 + (i - 500) = i by omega] at this

  by_cases h3 : i < 1000
  · have := ok_b_750 (i - 750) (by omega); rwa [show 750 + (i - 750) = i by omega] at this

  by_cases h4 : i < 1250
  · have := ok_b_1000 (i - 1000) (by omega); rwa [show 1000 + (i - 1000) = i by omega] at this

  by_cases h5 : i < 1500
  · have := ok_b_1250 (i - 1250) (by omega); rwa [show 1250 + (i - 1250) = i by omega] at this

  by_cases h6 : i < 1750
  · have := ok_b_1500 (i - 1500) (by omega); rwa [show 1500 + (i - 1500) = i by omega] at this

  have := ok_b_1750 (i - 1750) (by omega); rwa [show 1750 + (i - 1750) = i by omega] at this

theorem okb_spec (i : ℕ) (h : okb i = true) :
    (D_beta.get i).1 ≠ [] ∧ vec ((D_beta.get i).1.headD 0) ≠ 0 ∧ (D_beta.get i).2.1 ≠ [] ∧
    (∃ j : Fin 9, vec ((D_beta.get i).2.1.headD 0) j = 1) ∧ (D_beta.get i).2.2.length = 9 ∧
    ∀ k < 9, (D_beta.get i).2.2.getD k 0 = 0 ∨ ((D_beta.get i).1.length ≤ k ∧ k < 9 - (D_beta.get i).2.1.length) := by
  simp only [okb, Bool.and_eq_true, bne_iff_ne, ne_eq, decide_eq_true_eq, List.any_eq_true, List.mem_finRange,
    true_and, beq_iff_eq, List.all_eq_true, List.mem_range, Bool.or_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, h5⟩, h6⟩ := h
  exact ⟨h1, h2, h3, h4, h5, fun k hk => by have := h6 k hk; simpa using this⟩

theorem tsumb_add (lo m : ℕ) : ∀ n, tsumb lo (m + n) = tsumb lo m + tsumb (lo + m) n
  | 0 => rfl
  | n + 1 => by
    show tsumb lo (m + n) + _ = tsumb lo m + (tsumb (lo + m) n + _)
    rw [tsumb_add lo m n, Nat.add_assoc, Nat.add_assoc lo m n]; rfl

theorem tsumb_eq (n : ℕ) : (∑ i ∈ range n, ∑ k ∈ range 9, (D_beta.get i).2.2.getD k 0) = tsumb 0 n := by
  induction n with
  | zero => rfl
  | succ n ih => rw [Finset.sum_range_succ, ih]; show _ = tsumb 0 n + _; rw [Nat.zero_add]

theorem totb : tsumb 0 N_beta = 1536575200417 := by
  have e0 : tsumb 0 250 = 132262509117 := sum_b_0
  have e1 : tsumb 0 500 = 285529914416 := by
    rw [show (500 : ℕ) = 250 + 250 from rfl, tsumb_add, e0, show (0 + 250 : ℕ) = 250 from rfl, sum_b_250]
  have e2 : tsumb 0 750 = 441898805549 := by
    rw [show (750 : ℕ) = 500 + 250 from rfl, tsumb_add, e1, show (0 + 500 : ℕ) = 500 from rfl, sum_b_500]
  have e3 : tsumb 0 1000 = 623684717551 := by
    rw [show (1000 : ℕ) = 750 + 250 from rfl, tsumb_add, e2, show (0 + 750 : ℕ) = 750 from rfl, sum_b_750]
  have e4 : tsumb 0 1250 = 842726768012 := by
    rw [show (1250 : ℕ) = 1000 + 250 from rfl, tsumb_add, e3, show (0 + 1000 : ℕ) = 1000 from rfl, sum_b_1000]
  have e5 : tsumb 0 1500 = 1116368096105 := by
    rw [show (1500 : ℕ) = 1250 + 250 from rfl, tsumb_add, e4, show (0 + 1250 : ℕ) = 1250 from rfl, sum_b_1250]
  have e6 : tsumb 0 1750 = 1404262609562 := by
    rw [show (1750 : ℕ) = 1500 + 250 from rfl, tsumb_add, e5, show (0 + 1500 : ℕ) = 1500 from rfl, sum_b_1500]
  have e7 : tsumb 0 1822 = 1536575200417 := by
    rw [show (1822 : ℕ) = 1750 + 72 from rfl, tsumb_add, e6, show (0 + 1750 : ℕ) = 1750 from rfl, sum_b_1750]
  exact e7


/-- **V2-FLOOR, β only (JB): every plan realising all 1,822 pairs costs ≥ 1536575200417 / 2^30**, given the certificate's
edge feasibility `IntFeasible` (what check.c verifies). -/
theorem floor_beta (hfeas : IntFeasible (fun p => Lsub (LBb p)) (fun p => Usub (UHb p)) numb T_beta)
    (E : Finset (Sub × Sub)) (hE : ∀ e ∈ E, e.1 < e.2) (hreal : ∀ p, Reach E (Lsub (LBb p)) (Usub (UHb p))) :
    (1536575200417 : ℝ) / 2 ^ 30 ≤ ∑ e ∈ E, wcut 1 (fdim e.1) (fdim e.2) := by
  have sp := fun (p : Fin N_beta) => okb_spec p.val (ok_all_b p.val p.isLt)
  have h := floor_F2 LBb UHb numb 1 T_beta (fun a b h1 hab h8 => T_beta_le a b h1 hab h8)
    (fun p => Lsub_ne_bot _ (sp p).1 (sp p).2.1)
    (fun p => by obtain ⟨j, hj⟩ := (sp p).2.2.2.1; exact Usub_ne_top _ (sp p).2.2.1 j hj)
    (fun p k hk => by
      by_cases k9 : k < 9
      · rcases (sp p).2.2.2.2.2 k k9 with h0 | h0
        · exact absurd h0 hk
        · exact h0
      · exfalso; apply hk; unfold numb
        have hl := (sp p).2.2.2.2.1
        rw [List.getD_eq_getElem?_getD, List.getElem?_eq_none (by omega)]; rfl)
    (fun p k hk => by
      unfold numb; have hl := (sp p).2.2.2.2.1
      rw [List.getD_eq_getElem?_getD, List.getElem?_eq_none (by omega)]; rfl)
    hfeas E hE hreal
  have ht : (∑ p : Fin N_beta, ∑ k ∈ range 9, (numb p k : ℝ)) = 1536575200417 := by
    have e1 := Fin.sum_univ_eq_sum_range (fun i => ∑ k ∈ range 9, (D_beta.get i).2.2.getD k 0) N_beta
    rw [tsumb_eq, totb] at e1
    have e2 : (∑ p : Fin N_beta, ∑ k ∈ range 9, numb p k) = 1536575200417 := e1
    exact_mod_cast e2
  rwa [ht] at h

end beta

end V2Floor
