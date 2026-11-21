/-
CallerPiecePart (lane DISCHARGE, Nov 20).  The piece-partition = stage-form objective equality that CallerRC2 / CallerHP left unformalised.

For a role with mask `M` whose pieces `pc s` (s in M) form a PARTITION of M (s in pc s, pc s ⊆ M, and t in pc s -> pc t = pc s):
   sum over the DISTINCT pieces q of f |q|   =   sum over stages s in M of  f |pc s| / |pc s|          (any f : ℕ → ℝ)
hence   roleValPiece σ M pc := (8|M|+1)^σ - sum_q (8|q|)^σ   =   CallerHP.roleVal σ M (|pc ·|)    (the stage form used by HPDual / CallerHP).
Consequently CallerHP.frame_bound / reduced_bound bound the PIECE-form caller value (sum over roles of (8D+1)^σ - sum_pieces (8L)^σ),
not only the stage-form one.  `frame_bound_piece` states this for a CallerRC2 frame given the partition property.
Kernel only.
-/
import Nov15.CallerHP

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerPiecePart
open Finset

section
variable {k : ℕ}

/-- the pieces of a role: its distinct blocks. -/
def pieces (M : Finset (Fin k)) (pc : Fin k → Finset (Fin k)) : Finset (Finset (Fin k)) := M.image pc

theorem piece_stage_eq (M : Finset (Fin k)) (pc : Fin k → Finset (Fin k))
    (hmem : ∀ s ∈ M, s ∈ pc s) (hsub : ∀ s ∈ M, pc s ⊆ M)
    (hpart : ∀ s ∈ M, ∀ t ∈ M, t ∈ pc s → pc t = pc s) (f : ℕ → ℝ) :
    ∑ q ∈ pieces M pc, f q.card = ∑ s ∈ M, f (pc s).card / ((pc s).card : ℝ) := by
  classical
  have hmaps : ∀ s ∈ M, pc s ∈ pieces M pc := fun s hs => Finset.mem_image_of_mem pc hs
  rw [← Finset.sum_fiberwise_of_maps_to hmaps]
  refine Finset.sum_congr rfl ?_
  intro q hq
  obtain ⟨s0, hs0, rfl⟩ := Finset.mem_image.mp hq
  have hfib : M.filter (fun s => pc s = pc s0) = pc s0 := by
    ext s
    simp only [Finset.mem_filter]
    constructor
    · rintro ⟨hs, h⟩
      rw [← h]; exact hmem s hs
    · intro hs
      have hsM : s ∈ M := hsub s0 hs0 hs
      exact ⟨hsM, hpart s0 hs0 s hsM hs⟩
  have hpos : 0 < (pc s0).card := Finset.card_pos.mpr ⟨s0, hmem s0 hs0⟩
  have hc : ∀ s ∈ M.filter (fun s => pc s = pc s0), f (pc s).card / ((pc s).card : ℝ)
      = f (pc s0).card / ((pc s0).card : ℝ) := by
    intro s hs; rw [(Finset.mem_filter.mp hs).2]
  rw [Finset.sum_congr rfl hc, Finset.sum_const, hfib, nsmul_eq_mul]
  have : ((pc s0).card : ℝ) ≠ 0 := by exact_mod_cast hpos.ne'
  field_simp

end

section
variable {k : ℕ}

noncomputable def roleValPiece (σ : ℝ) (M : Finset (Fin k)) (pc : Fin k → Finset (Fin k)) : ℝ :=
  (8 * (M.card : ℝ) + 1) ^ σ - ∑ q ∈ pieces M pc, (8 * (q.card : ℝ)) ^ σ

/-- the piece form of a role's value equals the stage form of CallerHP. -/
theorem roleValPiece_eq (σ : ℝ) (M : Finset (Fin k)) (pc : Fin k → Finset (Fin k))
    (hmem : ∀ s ∈ M, s ∈ pc s) (hsub : ∀ s ∈ M, pc s ⊆ M)
    (hpart : ∀ s ∈ M, ∀ t ∈ M, t ∈ pc s → pc t = pc s) :
    roleValPiece σ M pc = CallerHP.roleVal σ M (fun s => (pc s).card) := by
  unfold roleValPiece CallerHP.roleVal
  rw [piece_stage_eq M pc hmem hsub hpart (fun n => (8 * (n : ℝ)) ^ σ)]

end


section frame
open CallerSign
variable {K : Type*} [Field K] {k : ℕ}

/-- KASYM's caller law in PIECE form: the same hypotheses as `CallerHP.frame_bound` plus the partition property of each role's pieces
(the pieces of a role partition its mask); the conclusion is the objective  sum_roles ((8D+1)^s - sum_{pieces q} (8|q|)^s). -/
theorem frame_bound_piece {R : Type} [Fintype R] [DecidableEq R] (hk : 3 ≤ k) (M : R → Finset (Fin k))
    (bh ah : R → Fin k → Fin 2 → K)
    (hbh : ∀ r s, s ∉ M r → ∀ a, bh r s a = 0) (hah : ∀ r s, s ∉ M r → ∀ a, ah r s a = 0)
    (P : Pieces M bh) (hG : ∀ s t, s ≠ t → IsUnit (gBlk bh ah s t).det)
    (main : R → Fin k → Bool) (hn : Fintype.card R + 2 = 2 * k) (hdeg : ∀ r, 2 ≤ (M r).card)
    (hmain1 : ∀ r s, s ∈ M r → main r s = true → (P.pc r s).card = 1)
    (hmains : 2 * k ≤ ∑ r, ((M r).filter (fun s => main r s = true)).card)
    (hpart : ∀ r, ∀ s ∈ M r, ∀ t ∈ M r, t ∈ P.pc r s → P.pc r t = P.pc r s) :
    104 / (k : ℝ) * ∑ r, roleValPiece CallerHP.σ0 (M r) (P.pc r) ≤ CallerHP.HPr k := by
  have h := CallerHP.frame_bound hk M bh ah hbh hah P hG main hn hdeg hmain1 hmains
  have e : ∀ r, roleValPiece CallerHP.σ0 (M r) (P.pc r) = CallerHP.roleVal CallerHP.σ0 (M r) (fun s => (P.pc r s).card) :=
    fun r => roleValPiece_eq _ _ _ (P.pc_mem r) (P.pc_sub r) (hpart r)
  simp only [e]
  exact h

end frame


/-! non-vacuity: M = Fin 3, pieces {0,1} | {2} (a genuine partition); the hypotheses hold and the identity is exercised. -/
def pc3 : Fin 3 → Finset (Fin 3) := fun s => if s.val < 2 then {0, 1} else {2}

theorem nonvac_partition (f : ℕ → ℝ) :
    ∑ q ∈ pieces (Finset.univ : Finset (Fin 3)) pc3, f q.card
      = ∑ s ∈ (Finset.univ : Finset (Fin 3)), f (pc3 s).card / ((pc3 s).card : ℝ) :=
  piece_stage_eq _ pc3 (by decide) (by decide) (by decide) f

theorem nonvac_card : (pieces (Finset.univ : Finset (Fin 3)) pc3).card = 2 := by decide

end CallerPiecePart

#print axioms CallerPiecePart.piece_stage_eq
#print axioms CallerPiecePart.roleValPiece_eq
#print axioms CallerPiecePart.frame_bound_piece
