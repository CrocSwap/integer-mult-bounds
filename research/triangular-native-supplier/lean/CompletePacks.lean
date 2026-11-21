import MeanPack
import PackedGrid
import TensorMasks

namespace CompletePacks

open TriangularSupplier MixedRankRecovery MixedRankPublicGrid
open CirculantGridBridge CirculantTraceProduct PackedPublicGrid
open scoped BigOperators

variable {d D : ℕ} (s t : Fin d → ℕ)
  (hs : Pairwise fun i j ↦ Nat.Coprime (s i) (s j))
  [∀ i, NeZero (s i)] (ht : ∀ i, s i ≤ t i) [NeZero (∏ i, s i)]

/-- Each boundary is the whole represented physical field, including its holes. -/
structure TapePacks (D : ℕ) where
  count : Bool → ℕ
  action : Bool → ℕ → Field t → Field t
  state : Bool → GridSignal (∏ i, s i) D → ℕ → Field t

def after (a : ℕ → Field t → Field t) (x : Field t) : ℕ → Field t
  | 0 => x
  | j+1 => a j (after a x j)

/-- These conditions concern only the initial state and local, reached word defects. -/
structure TraceBudget (w : TapePacks s t D) (δ : Bool → ℝ) : Prop where
  nonneg : ∀ p, 0 ≤ δ p
  budget : ∀ p, (w.count p : ℝ)*δ p ≤ (1/8 : ℝ)/D
  entry : ∀ p x, disk x.val (1/2) → w.state p x 0 = zeroFill s t hs ht x.val
  local_error : ∀ p x, disk x.val (1/2) → ∀ j, j < w.count p →
    (∀ i, ‖w.state p x j i‖ ≤ 2) →
    Close (δ p) (w.state p x (j+1)) (w.action p j (w.state p x j))

structure LocalFacts (w : TapePacks s t D) (δ : Bool → ℝ) : Prop
    extends TraceBudget s t hs ht w δ where
  zero : ∀ p j, j < w.count p → w.action p j 0 = 0
  contract : ∀ p j, j < w.count p → ∀ {r x y}, 0 ≤ r → Close r x y →
    Close r (w.action p j x) (w.action p j y)
  exact_schedule : ∀ p z, after t (w.action p) z (w.count p) = paddedMean s t p z

/-- The controller dispatches one complete transform along each axis exactly once. -/
structure MaskSchedule (w : TapePacks s t D) (mask : Bool → ℕ → Finset (Fin d)) : Prop where
  disjoint : ∀ p j, j < w.count p → Disjoint (TriangularPaddedTensor.seenAxes (mask p) j) (mask p j)
  covers : ∀ p, TriangularPaddedTensor.seenAxes (mask p) (w.count p) = Finset.univ
  at_mask : ∀ p j, j < w.count p → w.action p j = TriangularPaddedTensor.step s t p (mask p j)

open TriangularPaddedTensor in
omit [NeZero (∏ i, s i)] in
theorem bind_masks (w : TapePacks s t D) (δ : Bool → ℝ) (mask : Bool → ℕ → Finset (Fin d))
    (local_steps : TraceBudget s t hs ht w δ) (schedule : MaskSchedule s t w mask) :
    LocalFacts s t hs ht w δ := by
  refine {local_steps with zero := ?_, contract := ?_, exact_schedule := ?_}
  · intro p j hj
    rw [schedule.at_mask p j hj]
    funext i
    simp [TriangularPaddedTensor.step]
  · intro p j hj r x y _ hxy
    rw [schedule.at_mask p j hj]
    exact step_contracts s t p (mask p j) ht hxy
  · intro p z
    have fold (j : ℕ) (hj : j ≤ w.count p) : after t (w.action p) z j =
        step s t p (seenAxes (mask p) j) z := by
      induction j with
      | zero => exact (empty_step s t p z).symm
      | succ j ih =>
        have hlt : j < w.count p := hj
        rw [after, ih (Nat.le_of_lt hlt), schedule.at_mask p j hlt]
        exact disjoint_steps s t p _ _ (schedule.disjoint p j hlt) z
    rw [fold _ le_rfl, schedule.covers, full_step]

noncomputable def read (w : TapePacks s t D) (p : Bool)
    (x : GridSignal (∏ i, s i) D) (k : ZMod (∏ i, s i)) : ℂ :=
  w.state p x (w.count p) (paddedAddress s t hs ht k)

/-- A local budget gives the required accuracy on every physical output wire. -/
theorem all_wires (hD : 0 < D) (w : TapePacks s t D) (δ : Bool → ℝ)
    (facts : LocalFacts s t hs ht w δ) (p : Bool) (x : GridSignal (∏ i, s i) D)
    (hx : disk x.val (1/2)) :
    Close ((1/8 : ℝ)/D) (w.state p x (w.count p))
      (zeroFill s t hs ht (fromAxes s hs p x.val)) := by
  let start := zeroFill s t hs ht x.val
  let ideal := after t (w.action p) start
  have inside : ∀ j, j ≤ w.count p → ∀ i, ‖ideal j i‖ ≤ 1 := by
    intro j
    induction j with
    | zero =>
      intro _ i
      change ‖zeroFill s t hs ht x.val i‖ ≤ 1
      by_cases h : ∃ k, paddedAddress s t hs ht k = i
      · obtain ⟨k,rfl⟩ := h
        rw [zeroFill_true]
        exact (hx k).trans (by norm_num)
      · rw [zeroFill_hole _ _ _ _ _ _ h]; norm_num
    | succ j ih =>
      intro hj
      have hlt : j < w.count p := hj
      have prev : Close 1 (ideal j) (0 : Field t) := by
        intro i
        simpa using ih (Nat.le_of_lt hlt) i
      have applied := facts.contract p j hlt (by norm_num) prev
      rw [facts.zero p j hlt] at applied
      intro i
      simpa [ideal, after] using applied i
  have cap : (1/8 : ℝ)/D ≤ 1 := by
    have h1 : 1 ≤ (D:ℝ) := by exact_mod_cast hD
    rw [div_le_iff₀ (by positivity : 0 < (D:ℝ))]
    nlinarith
  have bound := pack_error ideal (w.state p x) (w.action p) (w.count p) (δ p)
    (facts.nonneg p) ((facts.budget p).trans cap) (facts.entry p x hx)
    (fun _ _ ↦ rfl) inside (facts.contract p) (facts.local_error p x hx)
    (w.count p) le_rfl
  have end_eq : ideal (w.count p) = zeroFill s t hs ht (fromAxes s hs p x.val) :=
    (facts.exact_schedule p start).trans (physical_zero_fill s t hs ht p x.val)
  rw [end_eq] at bound
  exact fun i ↦ (bound i).trans (facts.budget p)

/-- The actual forward pair produces zeros on the whole complement of the original CRT set. -/
theorem pointwise_packet (hD : 0 < D) (w : TapePacks s t D) (δ : Bool → ℝ)
    (facts : LocalFacts s t hs ht w δ) (x y : GridSignal (∏ i, s i) D)
    (hx : disk x.val (1/2)) :
    (fun i ↦ snap D (snap D (w.state false x (w.count false) i) *
      snap D (w.state false y (w.count false) i))) =
      zeroFill s t hs ht (fun k ↦ snap D (snap D (read s t hs ht w false x k) *
        snap D (read s t hs ht w false y k))) :=
  physical_packet_eighth s t hs ht hD _ _ _ (all_wires s t hs ht hD w δ facts false x hx)

/-- The per-pack hypotheses suffice for the integer result with both source factors and carry. -/
theorem recovered_bits (B : ℕ) (hB : 32 ≤ B) (hEven : Even B) (hsize : ∏ i, s i ≤ B)
    (w : TapePacks s t (B^6)) (δ : Bool → ℝ) (facts : LocalFacts s t hs ht w δ)
    (a b : ZMod (∏ i, s i) → ℕ) (ha : ∀ j, a j ≤ B) (hb : ∀ j, b j ≤ B)
    (hspan : ∀ i j, a i ≠ 0 → b j ≠ 0 → i.val+j.val < ∏ i, s i) :
    pack B (carry B 0 (ordered (wordDecode (by omega : 0 < B) hEven
      (read s t hs ht w false) (read s t hs ht w true) a b))) =
      radixValue B a * radixValue B b := by
  apply product_on_the_public_grid s hs B hB hEven hsize (read s t hs ht w) _ a b ha hb hspan
  intro p x hx k
  have Dpos : 0 < B^6 := pow_pos (by omega) _
  have h := all_wires s t hs ht Dpos w δ facts p x hx (paddedAddress s t hs ht k)
  rw [zeroFill_true] at h
  exact h

#print axioms all_wires
#print axioms pointwise_packet
#print axioms recovered_bits

/-- A coordinate partition and measured local defects imply the full radix product. -/
theorem recovered_from_partition (B : ℕ) (hB : 32 ≤ B) (hEven : Even B) (hsize : ∏ i, s i ≤ B)
    (w : TapePacks s t (B^6)) (δ : Bool → ℝ) (mask : Bool → ℕ → Finset (Fin d))
    (local_steps : TraceBudget s t hs ht w δ) (schedule : MaskSchedule s t w mask)
    (a b : ZMod (∏ i, s i) → ℕ) (ha : ∀ j, a j ≤ B) (hb : ∀ j, b j ≤ B)
    (hspan : ∀ i j, a i ≠ 0 → b j ≠ 0 → i.val+j.val < ∏ i, s i) :
    pack B (carry B 0 (ordered (wordDecode (by omega : 0 < B) hEven
      (read s t hs ht w false) (read s t hs ht w true) a b))) =
      radixValue B a * radixValue B b :=
  recovered_bits s t hs ht B hB hEven hsize w δ (bind_masks s t hs ht w δ mask local_steps schedule)
    a b ha hb hspan

#print axioms bind_masks
#print axioms recovered_from_partition

end CompletePacks
