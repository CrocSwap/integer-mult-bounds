import SplitProjectors

/-! Concrete coordinate partitions, including the selected 18×4 and 3×24 banks. -/
namespace CurrentMain.CoordinatePartitions
open Lean.Grind CurrentMain.SplitProjectors
attribute [local instance] Semiring.natCast Ring.intCast

universe u v w

/-- Coordinate vectors use pointwise ring structure; projectors remain merely additive. -/
instance pointwiseRing {I : Type u} {F : Type v} [CommRing F] : CommRing (I → F) where
  add f g i := f i + g i
  mul f g i := f i * g i
  hPow f n i := f i ^ n
  ofNat n := ⟨fun _ => OfNat.ofNat n⟩
  natCast := ⟨fun n _ => (n : F)⟩
  neg f i := -f i
  sub f g i := f i - g i
  intCast := ⟨fun n _ => (n : F)⟩
  add_assoc _ _ _ := by funext i; exact Semiring.add_assoc _ _ _
  add_comm _ _ := by funext i; exact Semiring.add_comm _ _
  add_zero _ := by funext i; exact Semiring.add_zero _
  mul_assoc _ _ _ := by funext i; exact Semiring.mul_assoc _ _ _
  mul_one _ := by funext i; exact Semiring.mul_one _
  one_mul _ := by funext i; exact Semiring.one_mul _
  left_distrib _ _ _ := by funext i; exact Semiring.left_distrib _ _ _
  right_distrib _ _ _ := by funext i; exact Semiring.right_distrib _ _ _
  zero_mul _ := by funext i; exact Semiring.zero_mul _
  mul_zero _ := by funext i; exact Semiring.mul_zero _
  pow_zero _ := by funext i; exact Semiring.pow_zero _
  pow_succ _ _ := by funext i; exact Semiring.pow_succ _ _
  ofNat_succ _ := by funext i; exact Semiring.ofNat_succ _
  ofNat_eq_natCast _ := by funext i; exact Semiring.ofNat_eq_natCast _
  neg_add_cancel _ := by funext i; exact Ring.neg_add_cancel _
  sub_eq_add_neg _ _ := by funext i; exact Ring.sub_eq_add_neg _ _
  intCast_ofNat _ := by funext i; exact Ring.intCast_ofNat _
  intCast_neg _ := by funext i; exact Ring.intCast_neg _
  mul_comm _ _ := by funext i; exact CommSemiring.mul_comm _ _

variable {I : Type u} {F : Type v} [CommRing F] {Role : Type w} [DecidableEq Role]

/-- Every coordinate belongs to exactly the role supplied by owner. -/
def block (owner : I → Role) (s : Role) : AdditiveEnd (I → F) where
  map x i := if owner i = s then x i else 0
  map_add x y := by
    funext i
    change (if owner i = s then x i + y i else 0) =
      (if owner i = s then x i else 0) + (if owner i = s then y i else 0)
    split <;> simp_all [Semiring.add_zero]
  map_sub x y := by
    funext i
    change (if owner i = s then x i - y i else 0) =
      (if owner i = s then x i else 0) - (if owner i = s then y i else 0)
    split <;> simp_all [Ring.sub_self]

theorem block_idempotent (owner : I → Role) (s : Role) (x : I → F) :
    (block owner s).map ((block owner s).map x) = (block owner s).map x := by
  funext i
  simp only [block]
  split <;> simp_all

theorem block_disjoint (owner : I → Role) (s t : Role) (different : s ≠ t)
    (x : I → F) : (block owner s).map ((block owner t).map x) = 0 := by
  funext i
  change (if owner i = s then (if owner i = t then x i else 0) else 0) = 0
  by_cases hs : owner i = s
  · have ht : owner i ≠ t := by intro ht; exact different (hs.symm.trans ht)
    simp only [hs, different, if_true, if_false]
  · simp only [hs, if_false]

theorem blocks_disjoint (owner : I → Role) (roles : List Role) (hn : roles.Nodup) :
    DisjointList (roles.map (block (F := F) owner)) := by
  induction roles with
  | nil => trivial
  | cons s rest ih =>
    simp only [List.map_cons, DisjointList]
    have hnd := List.nodup_cons.mp hn
    refine ⟨?_, ih hnd.2⟩
    intro q hq x
    obtain ⟨t, ht, rfl⟩ := List.mem_map.mp hq
    exact block_disjoint owner s t (fun he => hnd.1 (he ▸ ht)) x

theorem sum_blocks (owner : I → Role) (roles : List Role) (hn : roles.Nodup)
    (x : I → F) (i : I) :
    (sumEnds (roles.map (block owner))).map x i =
      if owner i ∈ roles then x i else 0 := by
  induction roles with
  | nil => rfl
  | cons s rest ih =>
    have hnd := List.nodup_cons.mp hn
    change (if owner i = s then x i else 0) +
      (sumEnds (rest.map (block owner))).map x i = _
    rw [ih hnd.2]
    by_cases hs : owner i = s
    · have hr : owner i ∉ rest := by simpa only [hs] using hnd.1
      simp [hs, hnd.1, Semiring.add_zero]
    · simp only [List.mem_cons, hs, false_or, if_false]
      exact Semiring.zero_add _

/-- This derives the partition endpoint from role completeness and no duplicates. -/
theorem coordinate_partition_endpoint (owner : I → Role) (roles : List Role)
    (hn : roles.Nodup) (complete : ∀ i, owner i ∈ roles)
    (z : (I → F) × (I → F)) :
    runSwaps (roles.map (block owner)) z = (z.2, z.1) := by
  apply complete_partition_endpoint _ (blocks_disjoint owner roles hn)
  intro x
  funext i
  rw [sum_blocks owner roles hn x i]
  simp only [complete i, if_true]

/-- The selected surviving-entrance partition: 18 blocks of four coordinates. -/
def ownerFour (i : Fin 72) : Nat := i.val / 4

/-- The selected undeferred partition: three blocks of 24 coordinates. -/
def ownerTwentyFour (i : Fin 72) : Nat := i.val / 24

theorem eighteen_by_four_endpoint (z : (Fin 72 → F) × (Fin 72 → F)) :
    runSwaps ((List.range 18).map (block ownerFour)) z = (z.2, z.1) := by
  apply coordinate_partition_endpoint ownerFour (List.range 18) List.nodup_range
  intro i
  simp only [List.mem_range, ownerFour]
  have hi := i.isLt
  omega

theorem three_by_twentyfour_endpoint (z : (Fin 72 → F) × (Fin 72 → F)) :
    runSwaps ((List.range 3).map (block ownerTwentyFour)) z = (z.2, z.1) := by
  apply coordinate_partition_endpoint ownerTwentyFour (List.range 3) List.nodup_range
  intro i
  simp only [List.mem_range, ownerTwentyFour]
  have hi := i.isLt
  omega

end CurrentMain.CoordinatePartitions

#print axioms CurrentMain.CoordinatePartitions.block_idempotent
#print axioms CurrentMain.CoordinatePartitions.block_disjoint
#print axioms CurrentMain.CoordinatePartitions.blocks_disjoint
#print axioms CurrentMain.CoordinatePartitions.sum_blocks
#print axioms CurrentMain.CoordinatePartitions.coordinate_partition_endpoint
#print axioms CurrentMain.CoordinatePartitions.eighteen_by_four_endpoint
#print axioms CurrentMain.CoordinatePartitions.three_by_twentyfour_endpoint
