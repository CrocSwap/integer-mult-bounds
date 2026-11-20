/-
WordModelYCard (lane WM-Y): finite fact |q^perp| = 256 for 0 < q < 512, split in chunks to bound kernel memory.
Kernel only (decide +kernel), no sorry/native_decide/axioms.
-/
import Nov15.WordModelDefs
import Mathlib.Tactic.IntervalCases

namespace WordModel
open Finset SafeRungsClique

theorem Hq_card_c0 : ∀ i < 32, 32 * 0 + i ≠ 0 → (Hq (32 * 0 + i)).card = 256 := by
  unfold Hq; decide +kernel
theorem Hq_card_c1 : ∀ i < 32, 32 * 1 + i ≠ 0 → (Hq (32 * 1 + i)).card = 256 := by
  unfold Hq; decide +kernel
theorem Hq_card_c2 : ∀ i < 32, 32 * 2 + i ≠ 0 → (Hq (32 * 2 + i)).card = 256 := by
  unfold Hq; decide +kernel
theorem Hq_card_c3 : ∀ i < 32, 32 * 3 + i ≠ 0 → (Hq (32 * 3 + i)).card = 256 := by
  unfold Hq; decide +kernel
theorem Hq_card_c4 : ∀ i < 32, 32 * 4 + i ≠ 0 → (Hq (32 * 4 + i)).card = 256 := by
  unfold Hq; decide +kernel
theorem Hq_card_c5 : ∀ i < 32, 32 * 5 + i ≠ 0 → (Hq (32 * 5 + i)).card = 256 := by
  unfold Hq; decide +kernel
theorem Hq_card_c6 : ∀ i < 32, 32 * 6 + i ≠ 0 → (Hq (32 * 6 + i)).card = 256 := by
  unfold Hq; decide +kernel
theorem Hq_card_c7 : ∀ i < 32, 32 * 7 + i ≠ 0 → (Hq (32 * 7 + i)).card = 256 := by
  unfold Hq; decide +kernel
theorem Hq_card_c8 : ∀ i < 32, 32 * 8 + i ≠ 0 → (Hq (32 * 8 + i)).card = 256 := by
  unfold Hq; decide +kernel
theorem Hq_card_c9 : ∀ i < 32, 32 * 9 + i ≠ 0 → (Hq (32 * 9 + i)).card = 256 := by
  unfold Hq; decide +kernel
theorem Hq_card_c10 : ∀ i < 32, 32 * 10 + i ≠ 0 → (Hq (32 * 10 + i)).card = 256 := by
  unfold Hq; decide +kernel
theorem Hq_card_c11 : ∀ i < 32, 32 * 11 + i ≠ 0 → (Hq (32 * 11 + i)).card = 256 := by
  unfold Hq; decide +kernel
theorem Hq_card_c12 : ∀ i < 32, 32 * 12 + i ≠ 0 → (Hq (32 * 12 + i)).card = 256 := by
  unfold Hq; decide +kernel
theorem Hq_card_c13 : ∀ i < 32, 32 * 13 + i ≠ 0 → (Hq (32 * 13 + i)).card = 256 := by
  unfold Hq; decide +kernel
theorem Hq_card_c14 : ∀ i < 32, 32 * 14 + i ≠ 0 → (Hq (32 * 14 + i)).card = 256 := by
  unfold Hq; decide +kernel
theorem Hq_card_c15 : ∀ i < 32, 32 * 15 + i ≠ 0 → (Hq (32 * 15 + i)).card = 256 := by
  unfold Hq; decide +kernel

end WordModel
