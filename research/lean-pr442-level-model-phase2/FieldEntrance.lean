import LevelFrameJoins
import FrameGeometry
import PortGeometry
import Mathlib.LinearAlgebra.Span.Defs

/-!
Field-general interpretation of the pinned PR370/PR386-to-PR442 endpoint
joins. The local matrices are read from the literal frame IDs, independently
of the pending-coordinate comparison target.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
-/

namespace PR442LevelModel.Phase2
open scoped Matrix BigOperators

/-- The unnormalized literal E8 root, cast directly from integers. -/
def q (K : Type*) [Field K] (port : Fin 120) : Fin 8 → K :=
  fun i => (rootVector port i : K)

/-- The literal root-line projector; no map from the rational numbers is used. -/
def rootProjector (K : Type*) [Field K] (port : Fin 120) :
    Matrix (Fin 8) (Fin 8) K :=
  fun i j => q K port i * q K port j / 4

theorem projector_entry (K : Type*) [Field K] (frame : Fin 944)
    (i j : Fin 8) :
    FrameGeometry.projector K frame i j =
      (FrameGeometry.scaled frame i j : K) / 4 := by
  simp only [FrameGeometry.projector, Matrix.smul_apply, smul_eq_mul,
    FrameGeometry.castMatrix, Matrix.map_apply, FrameGeometry.scaledMatrix,
    Matrix.of_apply, Int.coe_castRingHom]
  ring

theorem source_entrance_projector_entry (K : Type*) [Field K]
    (port : Fin 120) (i j : Fin 8) :
    FrameGeometry.projector K (sourceEntrance port) i j =
      q K port i * q K port j / 4 := by
  rw [projector_entry, entrance_scaled]
  simp only [Int.cast_mul]
  unfold q
  ring

theorem source_entrance_projector (K : Type*) [Field K] (port : Fin 120) :
    FrameGeometry.projector K (sourceEntrance port) = rootProjector K port := by
  ext i j
  exact source_entrance_projector_entry K port i j

theorem target_entrance_projector (K : Type*) [Field K] (port : Fin 120) :
    FrameGeometry.projector K (targetEntrance port) = 0 := by
  rw [(endpoint_label_values port).2.1]
  exact FrameGeometry.projector_zero K

theorem source_exit_projector (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    FrameGeometry.projector K (sourceExit port) = 1 := by
  rw [(endpoint_label_values port).2.2.1]
  exact FrameGeometry.projector_full K h2

theorem target_exit_projector (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    FrameGeometry.projector K (targetExit port) = 1 - rootProjector K port := by
  ext i j
  simp only [Matrix.sub_apply, Matrix.one_apply, rootProjector]
  rw [projector_entry, target_exit_scaled]
  simp only [Int.cast_sub, Int.cast_mul]
  by_cases hij : i = j
  · subst j
    simp only [if_pos rfl, Int.cast_ofNat, q]
    field_simp [FrameGeometry.four_ne_zero K h2]
  · simp only [if_neg hij, Int.cast_zero, q]
    ring

/-- The PR370/PR386 source label and root table interpret as the same
PR442 entrance operator, through both pinned literal provenance joins. -/
theorem old_source_entrance_projector (K : Type*) [Field K]
    (port : Fin 120) :
    FrameGeometry.projector K (oldSourceEntrance port) =
      (fun i j => (oldRootVector port i : K) *
        (oldRootVector port j : K) / 4 : Matrix (Fin 8) (Fin 8) K) := by
  rw [(old_endpoint_labels_join port).1, source_entrance_projector]
  ext i j
  simp only [rootProjector, q, old_roots_join]

/-- The complementary old target exit retains its label and root joins
when interpreted over an arbitrary admissible field. -/
theorem old_target_exit_projector (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    FrameGeometry.projector K (oldTargetExit port) =
      1 - Matrix.of (fun i j : Fin 8 => (oldRootVector port i : K) *
        (oldRootVector port j : K) / 4) := by
  rw [(old_endpoint_labels_join port).2.2.2, target_exit_projector K h2]
  apply congrArg (fun A : Matrix (Fin 8) (Fin 8) K => 1 - A)
  ext i j
  simp only [rootProjector, q, old_roots_join, Matrix.of_apply]

/-- The certified integer port chart gives squared length four in every field. -/
theorem root_square_sum (K : Type*) [Field K] (port : Fin 120) :
    (∑ i : Fin 8, q K port i * q K port i) = 4 := by
  have h := congrArg (fun m : Matrix (Fin 8) (Fin 8) K => m 0 0)
    (PortGeometry.cast_orthogonal K port)
  simpa [Matrix.mul_apply, Matrix.transpose_apply, Matrix.smul_apply,
    Matrix.one_apply, PortGeometry.castBasis, PortGeometry.integerBasis,
    Matrix.map, q, root_eq_basis, smul_eq_mul] using h

theorem source_entrance_mulVec (K : Type*) [Field K] (port : Fin 120)
    (v : Fin 8 → K) :
    FrameGeometry.projector K (sourceEntrance port) *ᵥ v =
      ((q K port ⬝ᵥ v) / 4) • q K port := by
  funext i
  change (∑ j : Fin 8,
      FrameGeometry.projector K (sourceEntrance port) i j * v j) =
    ((∑ j : Fin 8, q K port j * v j) / 4) * q K port i
  calc
    (∑ j : Fin 8,
        FrameGeometry.projector K (sourceEntrance port) i j * v j) =
        ∑ j : Fin 8, (q K port j * v j / 4) * q K port i := by
      apply Finset.sum_congr rfl
      intro j _
      rw [source_entrance_projector_entry]
      ring
    _ = (∑ j : Fin 8, q K port j * v j / 4) * q K port i := by
      rw [Finset.sum_mul]
    _ = ((∑ j : Fin 8, q K port j * v j) / 4) * q K port i := by
      simp only [div_eq_mul_inv, Finset.sum_mul]

theorem source_entrance_fixes_root (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    FrameGeometry.projector K (sourceEntrance port) *ᵥ q K port = q K port := by
  rw [source_entrance_mulVec]
  have h : q K port ⬝ᵥ q K port = 4 := root_square_sum K port
  rw [h]
  simp [FrameGeometry.four_ne_zero K h2]

theorem root_ne_zero (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) : q K port ≠ 0 := by
  intro hq
  have h := root_square_sum K port
  rw [hq] at h
  simp only [Pi.zero_apply, zero_mul, Finset.sum_const_zero] at h
  exact FrameGeometry.four_ne_zero K h2 h.symm

theorem rootProjector_ne_zero (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) : rootProjector K port ≠ 0 := by
  intro hp
  have h := source_entrance_fixes_root K h2 port
  rw [source_entrance_projector K port, hp, Matrix.zero_mulVec] at h
  exact root_ne_zero K h2 port h.symm

theorem entrance_projectors_differ (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    FrameGeometry.projector K (sourceEntrance port) ≠
      FrameGeometry.projector K (targetEntrance port) := by
  rw [source_entrance_projector, target_entrance_projector]
  exact rootProjector_ne_zero K h2 port

theorem exit_projectors_differ (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    FrameGeometry.projector K (sourceExit port) ≠
      FrameGeometry.projector K (targetExit port) := by
  rw [source_exit_projector K h2, target_exit_projector K h2]
  intro heq
  have h : (1 : Matrix (Fin 8) (Fin 8) K) - (1 - rootProjector K port) = 0 := by
    rw [← heq, sub_self]
  rw [sub_sub_cancel] at h
  exact rootProjector_ne_zero K h2 port h

theorem source_entrance_range (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    Set.range (fun v : Fin 8 → K =>
      FrameGeometry.projector K (sourceEntrance port) *ᵥ v) =
    (Submodule.span K ({q K port} : Set (Fin 8 → K)) : Set (Fin 8 → K)) := by
  ext v
  constructor
  · rintro ⟨w, rfl⟩
    apply Submodule.mem_span_singleton.mpr
    exact ⟨(q K port ⬝ᵥ w) / 4, (source_entrance_mulVec K port w).symm⟩
  · intro hv
    obtain ⟨c, hc⟩ := Submodule.mem_span_singleton.mp hv
    refine ⟨c • q K port, ?_⟩
    change FrameGeometry.projector K (sourceEntrance port) *ᵥ (c • q K port) = v
    rw [Matrix.mulVec_smul, source_entrance_fixes_root K h2]
    exact hc

theorem rootProjector_idempotent (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    rootProjector K port * rootProjector K port = rootProjector K port := by
  simpa only [source_entrance_projector K port] using
    FrameGeometry.projector_idempotent K h2 (sourceEntrance port)

/-- The joined root line is the first coordinate of the literal port chart. -/
theorem rootProjector_chart (K : Type*) [Field K] (port : Fin 120) :
    rootProjector K port =
      PortGeometry.basis K port *
        Matrix.diagonal (fun i : Fin 8 => if i = 0 then (1 : K) else 0) *
        (PortGeometry.basis K port).transpose := by
  ext i j
  rw [Matrix.mul_apply]
  simp only [Matrix.mul_diagonal, Matrix.transpose_apply]
  simp only [mul_ite, mul_one, mul_zero, ite_mul, zero_mul]
  simp only [Finset.sum_ite_eq', Finset.mem_univ, if_true]
  simp only [PortGeometry.basis_entry, ← root_eq_basis]
  unfold rootProjector q
  rw [div_mul_div_comm]
  norm_num

theorem root_chart_mulVec (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) (v : Fin 8 → K) :
    rootProjector K port *ᵥ (PortGeometry.basis K port *ᵥ v) =
      PortGeometry.basis K port *ᵥ
        (fun i : Fin 8 => if i = 0 then v i else 0) := by
  rw [rootProjector_chart, ← Matrix.mulVec_mulVec, ← Matrix.mulVec_mulVec,
    Matrix.mulVec_mulVec v (PortGeometry.basis K port).transpose
      (PortGeometry.basis K port), PortGeometry.basis_transpose_mul K h2,
    Matrix.one_mulVec]
  apply congrArg (fun w : Fin 8 → K => PortGeometry.basis K port *ᵥ w)
  funext i
  simp only [Matrix.mulVec_diagonal, ite_mul, one_mul, zero_mul]

/-- The source-side literal exit-minus-entrance difference is proved from
the endpoint tables; it is not a level-projector equality assumption. -/
theorem source_projector_difference (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    FrameGeometry.projector K (sourceExit port) -
      FrameGeometry.projector K (sourceEntrance port) = 1 - rootProjector K port := by
  rw [source_exit_projector K h2, source_entrance_projector]

/-- The target has different entrance and exit projectors; its difference
is derived separately, rather than identified by rank. -/
theorem target_projector_difference (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    FrameGeometry.projector K (targetExit port) -
      FrameGeometry.projector K (targetEntrance port) = 1 - rootProjector K port := by
  rw [target_exit_projector K h2, target_entrance_projector, sub_zero]

theorem endpoint_difference_cancels (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    (FrameGeometry.projector K (sourceExit port) -
      FrameGeometry.projector K (sourceEntrance port)) -
    (FrameGeometry.projector K (targetExit port) -
      FrameGeometry.projector K (targetEntrance port)) = 0 := by
  rw [source_projector_difference K h2, target_projector_difference K h2,
    sub_self]

theorem root_complement_left (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    rootProjector K port * (1 - rootProjector K port) = 0 := by
  rw [mul_sub, mul_one, rootProjector_idempotent K h2, sub_self]

theorem root_complement_right (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (port : Fin 120) :
    (1 - rootProjector K port) * rootProjector K port = 0 := by
  rw [sub_mul, one_mul, rootProjector_idempotent K h2, sub_self]

end PR442LevelModel.Phase2
