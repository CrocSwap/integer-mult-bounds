import Current1094PrivateCentreHosting
import FreshReferenceMinusHalfStore

/-!
Exact reference refinement for selected current1094 call000 forward raw row1:
SCALE(L119, -1/2), with source frame annotation 0. This is a source-bound
specialization, not an implementation or parser of the selected runtime.

A scalar multiplication commutes with every linear Hosting chart. Consequently
the realized event has a chart-independent whole-family action. The explicit
read/halve/negate/write reference routine reaches that action after a complete
duplicate-free component traversal. Its endpoint is derived, not a premise.

The reference result retains the dirty accumulator separately. The equality
proved here concerns the family-memory projection, not cleanup of that scratch.
Actual selected physical addresses, component order, scratch allocation,
rounding and primitive execution remain separate implementation obligations.

Reuse: PR509 Stream and PR516 Realize (DreamingOfClouds / Claude Opus 5.5),
PR1309 PrefixNorm (Gareth Davidson / OpenAI Codex), and the existing component
fold and reference routine. Exact import-only aliases keep one Stream namespace.
Prepared with OpenAI assistance. Apache-2.0. Uncompiled source proposal.
-/
set_option Elab.async false

noncomputable section
namespace CurrentMain.Current1094Row1ScalarRealization

open ComponentStoreFoldRefinement ReferenceMinusHalfStore

section ScalarChart

variable {I Φ Λ K W M : Type*} [DecidableEq I] [DecidableEq Φ]
  [Semiring K] [AddCommMonoid W] [Module K W]
  [AddCommMonoid M] [Module K M]

/-- Scalar chart cancellation requires no owner injection, label condition,
recipe exactness, isometry or assumed endpoint equation. -/
theorem realize_scale (σ : LemmaA.Hosting I Φ K W M)
    (rec : Λ → Λ → M → M) (i : I) (q : K) (y : Φ → W) :
    LemmaA.realize σ rec (.scale i q) y =
      Function.update y (σ.own i) (q • y (σ.own i)) := by
  simp only [LemmaA.realize, LemmaA.dst, LemmaG.Event.phys,
    Function.update_self, LemmaA.view, LinearEquiv.map_smul,
    LinearEquiv.symm_apply_apply]

end ScalarChart

section ComponentReference

variable {Coord Φ : Type*} [Fintype Coord] [DecidableEq Coord] [DecidableEq Φ]

/-- A reference execution on the components of one chosen family. Both memory
and the final accumulator are returned; no saved whole-vector buffer is used. -/
def referenceFamilyStep (order : List (Slot Coord)) (f : Φ)
    (y : Φ → EuclideanSpace ℂ Coord) (scratch : ℝ) :
    (Φ → EuclideanSpace ℂ Coord) × ℝ :=
  let result := referenceRun order
    (⟨encode (y f), scratch⟩ : RefState (Slot Coord))
  (Function.update y f (decode result.memory), result.accumulator)

/-- The exact reference operations and the existing own-component fold derive
the complete family-memory result. Other families are preserved by the update. -/
theorem referenceFamilyStep_complete (order : List (Slot Coord))
    (hnd : order.Nodup) (hcover : ∀ s, s ∈ order) (f : Φ)
    (y : Φ → EuclideanSpace ℂ Coord) (scratch : ℝ) :
    (referenceFamilyStep order f y scratch).1 =
      Function.update y f (((-1 / 2 : ℝ) : ℂ) • y f) := by
  change Function.update y f
    (decode (referenceRun order
      (⟨encode (y f), scratch⟩ : RefState (Slot Coord))).memory) = _
  rw [referenceRun_memory, run_complete _ order hnd hcover, real_scale_endpoint]

end ComponentReference

/-- The ordinary L119 tag in the selected 712-register invocation. -/
def selectedRegister : Current1094PrivateCentreHosting.Register := .inl 119

/-- Exact complex interpretation of the source rational coefficient -1/2.
The provider has 1004 frames. SCALE has no recipe or label operand in Event;
the raw source's frame-zero annotation is retained in the source binding. -/
def selectedRow1 :
    LemmaG.Event Current1094PrivateCentreHosting.Register (Fin 1004) ℂ :=
  .scale selectedRegister ((-1 / 2 : ℝ) : ℂ)

/-- Selected raw1's realized event is supplied by the explicit reference
component routine under complete traversal, without assuming that equality.
This is an equality of the reference memory projection, not the selected runtime. -/
theorem selected_row1_refines_realize {Coord Φ M : Type*}
    [Fintype Coord] [DecidableEq Coord] [DecidableEq Φ]
    [AddCommMonoid M] [Module ℂ M]
    (σ : LemmaA.Hosting Current1094PrivateCentreHosting.Register Φ ℂ
      (EuclideanSpace ℂ Coord) M)
    (rec : Fin 1004 → Fin 1004 → M → M)
    (order : List (Slot Coord)) (hnd : order.Nodup) (hcover : ∀ s, s ∈ order)
    (y : Φ → EuclideanSpace ℂ Coord) (scratch : ℝ) :
    (referenceFamilyStep order (σ.own selectedRegister) y scratch).1 =
      LemmaA.realize σ rec selectedRow1 y := by
  rw [referenceFamilyStep_complete order hnd hcover]
  exact (realize_scale σ rec selectedRegister ((-1 / 2 : ℝ) : ℂ) y).symm

end CurrentMain.Current1094Row1ScalarRealization

#print axioms CurrentMain.Current1094Row1ScalarRealization.realize_scale
#print axioms CurrentMain.Current1094Row1ScalarRealization.referenceFamilyStep_complete
#print axioms CurrentMain.Current1094Row1ScalarRealization.selected_row1_refines_realize
#check @CurrentMain.Current1094Row1ScalarRealization.realize_scale
#check @CurrentMain.Current1094Row1ScalarRealization.selected_row1_refines_realize
