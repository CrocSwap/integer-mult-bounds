import GridBridge
import TensorStability
import Mathlib.Analysis.Normed.Group.Constructions

/-! The data field contains the padded coordinates. Local error is
measured on the whole field. Extraction reads the original CRT coordinates. -/
namespace CirculantTraceProduct

open Finset
open scoped BigOperators
open CirculantGridBridge MixedRankPublicGrid MixedRankRecovery

variable {d : ℕ}
abbrev Carrier (t : Fin d → ℕ) := (i : Fin d) → Fin (t i)
abbrev Field (t : Fin d → ℕ) := Carrier t → ℂ

variable (s t : Fin d → ℕ) (hs : Pairwise fun i j ↦ Nat.Coprime (s i) (s j))
  [∀ i, NeZero (s i)] (ht : ∀ i, s i ≤ t i)

noncomputable def paddedAddress (k : ZMod (∏ i, s i)) : Carrier t :=
  fun i ↦ ⟨(addresses s hs k i).val, (ZMod.val_lt _).trans_le (ht i)⟩

theorem paddedAddress_injective : Function.Injective (paddedAddress s t hs ht) := by
  intro j k h
  apply (addresses s hs).injective
  funext i
  have hv := congrArg (fun v : Carrier t ↦ (v i).val) h
  change (addresses s hs j i).val = (addresses s hs k i).val at hv
  simpa only [ZMod.natCast_zmod_val] using congrArg (fun n : ℕ ↦ (n : ZMod (s i))) hv

/-- The two arrays at time j are the ideal rational-word field and the
actual computed field. The initial value is the same physical input. -/
structure Trace (S D : ℕ) (t : Fin d → ℕ) where
  steps : ℕ
  stage : ℕ → Field t → Field t
  state : GridSignal S D → ℕ → Field t

noncomputable def exactPrefix {S D : ℕ} (w : Trace S D t) (x : GridSignal S D) (j : ℕ) :=
  DirectTensorStability.run w.stage 0 j (w.state x 0)

noncomputable def readRaw {D : ℕ} (w : Trace (∏ i, s i) D t) (x : GridSignal (∏ i, s i) D)
    (k : ZMod (∏ i, s i)) := w.state x w.steps (paddedAddress s t hs ht k)

variable [NeZero (∏ i, s i)]

/-- The small absolute term β bounds the error of coefficient synthesis at
the exact endpoint. The state-relative term ε is charged at every fused stage.
The statement permits different stage counts and bounds on the two signs. -/
theorem product_from_fused_stages
    (B : ℕ) (hB : 32 ≤ B) (hEven : Even B) (hsize : ∏ i, s i ≤ B)
    (w : Bool → Trace (∏ i, s i) (B^6) t) (M ε R β : Bool → ℝ)
    (hpos : ∀ p, 0 ≤ M p ∧ 0 ≤ ε p ∧ 0 ≤ R p)
    (hboot : ∀ p, ((w p).steps:ℝ) * M p * ε p ≤ 1/2)
    (hpublic : ∀ p, ((w p).steps:ℝ) * M p * ε p * (2+2*R p) + β p ≤
      1 / ((B^6 : ℕ) : ℝ)^4)
    (hinterval : ∀ p i k, i+k ≤ (w p).steps → ∀ u v : Field t,
      dist (DirectTensorStability.run (w p).stage i k u)
        (DirectTensorStability.run (w p).stage i k v) ≤ M p * dist u v)
    (hradius : ∀ p x, disk x.val (1/2) → ∀ j, j ≤ (w p).steps →
      ‖exactPrefix t (w p) x j‖ ≤ R p)
    (hlocal : ∀ p x, disk x.val (1/2) → ∀ j, j < (w p).steps →
      dist ((w p).state x (j+1)) ((w p).stage j ((w p).state x j)) ≤
        ε p * (1 + ‖(w p).state x j‖))
    (hbias : ∀ p x, disk x.val (1/2) → ∀ k,
      ‖exactPrefix t (w p) x (w p).steps (paddedAddress s t hs ht k) -
        fromAxes s hs p x.val k‖ ≤ β p)
    (a b : ZMod (∏ i, s i) → ℕ) (ha : ∀ j, a j ≤ B) (hb : ∀ j, b j ≤ B)
    (hspan : ∀ i j, a i ≠ 0 → b j ≠ 0 → i.val+j.val < ∏ i, s i) :
    pack B (carry B 0 (ordered (wordDecode (by omega : 0 < B) hEven
      (readRaw s t hs ht (w false)) (readRaw s t hs ht (w true)) a b))) =
      radixValue B a * radixValue B b := by
  apply fused_grid_product s hs B hB hEven hsize
    (fun p ↦ readRaw s t hs ht (w p)) _ a b ha hb hspan
  intro p x hx k
  let y := exactPrefix t (w p) x (w p).steps
  let coord := paddedAddress s t hs ht k
  obtain ⟨hM, hε, hR⟩ := hpos p
  have hrun := (DirectTensorStability.bounded_computation (w p).stage ((w p).state x)
    (w p).steps (M p) (ε p) (R p) hM hε hR (hboot p) (hinterval p) (hradius p x hx)
    (hlocal p x hx) (w p).steps le_rfl).2
  have hentry : ‖(w p).state x (w p).steps coord - y coord‖ ≤
      ((w p).steps:ℝ)*M p*ε p*(2+2*R p) :=
    (show ‖(w p).state x (w p).steps coord - y coord‖ ≤ dist ((w p).state x (w p).steps) y by
      simpa only [dist_eq_norm] using dist_le_pi_dist ((w p).state x (w p).steps) y coord).trans hrun
  have h := norm_sub_le_norm_sub_add_norm_sub ((w p).state x (w p).steps coord) (y coord)
    (fromAxes s hs p x.val k)
  exact (h.trans (add_le_add hentry (hbias p x hx k))).trans (hpublic p)

#print axioms paddedAddress_injective
#print axioms product_from_fused_stages

end CirculantTraceProduct
