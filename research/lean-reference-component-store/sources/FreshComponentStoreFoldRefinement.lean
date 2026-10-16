import IndependentEntryUpdates
import FreshScalarPrefixNorm

/-!
Source-only component-store refinement of the existing independent-update fold.
Each visited scalar slot reads its own current value. A duplicate-free schedule
therefore reads that slot's original value, without a full-vector saved buffer.
The resulting real/imaginary masks are derived from the schedule, not assumed.

This does not define the selected physical executor. The current1094 archive
contains macro SCALE(-1/2), but no component trace or store implementation.
Actual address projection, write order, rounding and executor refinement remain
separate. General complex multiplication can mix the two components and is not
covered by the component-local hypothesis below.

Reuse: CurrentMain.IndependentEntryFold (unchanged generic proof body), and
Gareth Davidson/bitplane PR1309 PrefixNorm.components (unchanged definition).
Prepared with OpenAI assistance. Apache-2.0. Uncompiled proposal.
-/

noncomputable section
namespace CurrentMain.ComponentStoreFoldRefinement

open IndependentEntryFold

variable {Coord : Type*} [hfin : Fintype Coord] [hdec : DecidableEq Coord]

/-- Left tags are real components; right tags are imaginary components. -/
abbrev Slot (Coord : Type*) := Coord ⊕ Coord

def encode (old : EuclideanSpace ℂ Coord) : Slot Coord → ℝ
  | .inl i => (old i).re
  | .inr i => (old i).im

def decode (s : Slot Coord → ℝ) : EuclideanSpace ℂ Coord :=
  WithLp.toLp 2 (fun i => ⟨s (.inl i), s (.inr i)⟩)

def realDone (order : List (Slot Coord)) : Finset Coord := by
  letI : BEq (Slot Coord) := instBEqOfDecidableEq
  letI : LawfulBEq (Slot Coord) := inferInstance
  exact @Finset.filter Coord (fun i : Coord => (Sum.inl i : Slot Coord) ∈ order)
    (fun i => inferInstanceAs (Decidable ((Sum.inl i : Slot Coord) ∈ order)))
    Finset.univ

def imagDone (order : List (Slot Coord)) : Finset Coord := by
  letI : BEq (Slot Coord) := instBEqOfDecidableEq
  letI : LawfulBEq (Slot Coord) := inferInstance
  exact @Finset.filter Coord (fun i : Coord => (Sum.inr i : Slot Coord) ∈ order)
    (fun i => inferInstanceAs (Decidable ((Sum.inr i : Slot Coord) ∈ order)))
    Finset.univ

/-- The all-component endpoint determined by the component-local operations. -/
def endpoint (act : Slot Coord → ℝ → ℝ) (old : EuclideanSpace ℂ Coord) :
    EuclideanSpace ℂ Coord := decode (fun s => act s (encode old s))

/-- Every visited component is at its new endpoint and every unvisited component
is at its old endpoint. This is derived from the fold, with no hstore premise. -/
theorem run_components (act : Slot Coord → ℝ → ℝ)
    (order : List (Slot Coord)) (hnd : order.Nodup)
    (old : EuclideanSpace ℂ Coord) :
    decode (runUpdates act order (encode old)) =
      PrefixNorm.components (realDone order) (imagDone order) old (endpoint act old) := by
  letI : BEq (Slot Coord) := instBEqOfDecidableEq
  letI : LawfulBEq (Slot Coord) := inferInstance
  apply PiLp.ext
  intro i
  apply Complex.ext
  · change runUpdates act order (encode old) (.inl i) =
      if i ∈ realDone order then act (.inl i) ((old i).re) else (old i).re
    split_ifs with hi
    · exact runUpdates_of_mem act order hnd (.inl i)
        (Finset.mem_filter.mp hi).2 (encode old)
    · exact runUpdates_of_not_mem act order (.inl i)
        (fun h => hi (Finset.mem_filter.mpr ⟨Finset.mem_univ i, h⟩)) (encode old)
  · change runUpdates act order (encode old) (.inr i) =
      if i ∈ imagDone order then act (.inr i) ((old i).im) else (old i).im
    split_ifs with hi
    · exact runUpdates_of_mem act order hnd (.inr i)
        (Finset.mem_filter.mp hi).2 (encode old)
    · exact runUpdates_of_not_mem act order (.inr i)
        (fun h => hi (Finset.mem_filter.mpr ⟨Finset.mem_univ i, h⟩)) (encode old)

/-- Every prefix, including cuts after the end of the schedule. No particular
ordering of real versus imaginary writes is imposed. -/
theorem prefix_components (act : Slot Coord → ℝ → ℝ)
    (order : List (Slot Coord)) (hnd : order.Nodup)
    (old : EuclideanSpace ℂ Coord) (k : ℕ) :
    decode (runUpdates act (order.take k) (encode old)) =
      PrefixNorm.components (realDone (order.take k)) (imagDone (order.take k))
        old (endpoint act old) := by
  exact run_components act (order.take k)
    (List.Nodup.sublist (List.take_sublist k order) hnd) old

/-- Complete slot coverage yields the endpoint; schedule order is unrestricted. -/
theorem run_complete {Coord : Type*} [Fintype Coord] [DecidableEq Coord]
    (act : Slot Coord → ℝ → ℝ)
    (order : List (Slot Coord)) (hnd : order.Nodup)
    (hcover : ∀ s, s ∈ order) (old : EuclideanSpace ℂ Coord) :
    decode (runUpdates act order (encode old)) = endpoint act old := by
  apply PiLp.ext
  intro i
  apply Complex.ext
  · exact runUpdates_of_mem act order hnd (.inl i) (hcover _) (encode old)
  · exact runUpdates_of_mem act order hnd (.inr i) (hcover _) (encode old)

/-- A real coefficient scales both components independently. This equality is
exact field arithmetic; it is not a floating-point or rounded-store assertion. -/
theorem real_scale_endpoint {Coord : Type*} [Fintype Coord] [DecidableEq Coord]
    (c : ℝ) (old : EuclideanSpace ℂ Coord) :
    endpoint (fun _ v => c * v) old = (c : ℂ) • old := by
  apply PiLp.ext
  intro i
  apply Complex.ext
  · change c * (old i).re = ((c : ℂ) * old i).re
    simp only [Complex.mul_re, Complex.ofReal_re, Complex.ofReal_im,
      zero_mul, sub_zero]
  · change c * (old i).im = ((c : ℂ) * old i).im
    simp only [Complex.mul_im, Complex.ofReal_re, Complex.ofReal_im,
      zero_mul, add_zero]

theorem real_scale_prefix_components (c : ℝ)
    (order : List (Slot Coord)) (hnd : order.Nodup)
    (old : EuclideanSpace ℂ Coord) (k : ℕ) :
    decode (runUpdates (fun _ v => c * v) (order.take k) (encode old)) =
      PrefixNorm.components (realDone (order.take k)) (imagDone (order.take k))
        old ((c : ℂ) • old) := by
  rw [prefix_components (fun _ v => c * v) order hnd old k, real_scale_endpoint]

/-- The coefficient in selected call000 forward raw row1 is exactly -1/2.
This instantiates arithmetic only; order remains an abstract nodup slot list. -/
theorem selected_minus_half_prefix
    (order : List (Slot Coord)) (hnd : order.Nodup)
    (old : EuclideanSpace ℂ Coord) (k : ℕ) :
    decode (runUpdates (fun _ v => (-1 / 2 : ℝ) * v)
      (order.take k) (encode old)) =
      PrefixNorm.components (realDone (order.take k)) (imagDone (order.take k))
        old (((-1 / 2 : ℝ) : ℂ) • old) := by
  exact real_scale_prefix_components (-1 / 2) order hnd old k

end CurrentMain.ComponentStoreFoldRefinement

#print axioms CurrentMain.ComponentStoreFoldRefinement.run_components
#print axioms CurrentMain.ComponentStoreFoldRefinement.prefix_components
#print axioms CurrentMain.ComponentStoreFoldRefinement.run_complete
#print axioms CurrentMain.ComponentStoreFoldRefinement.real_scale_endpoint
#print axioms CurrentMain.ComponentStoreFoldRefinement.real_scale_prefix_components
#print axioms CurrentMain.ComponentStoreFoldRefinement.selected_minus_half_prefix
#check @CurrentMain.ComponentStoreFoldRefinement.run_components
#check @CurrentMain.ComponentStoreFoldRefinement.selected_minus_half_prefix
